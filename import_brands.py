#!/usr/bin/env python3
"""
Script d'importation des équipementiers de football depuis CSV
Intègre les marques dans la base de données TopKit collaborative
"""

import asyncio
import csv
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Ajouter le répertoire backend au path pour importer les modèles
sys.path.append(str(Path(__file__).parent / 'backend'))

from collaborative_models import Brand

# Charger les variables d'environnement
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Configuration MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# ID d'utilisateur système pour l'importation
SYSTEM_USER_ID = "system-import-brands"

async def generate_reference(entity_type: str) -> str:
    """Generate unique reference for entities"""
    prefixes = {
        "brand": "TK-BRAND-"
    }
    
    prefix = prefixes.get(entity_type, "TK-UNKNOWN-")
    
    # Compter les entités existantes
    count = await db.brands.count_documents({}) + 1
    
    # Générer référence avec padding de 6 chiffres
    reference = f"{prefix}{count:06d}"
    
    # Vérifier l'unicité
    while await db.brands.find_one({"topkit_reference": reference}):
        count += 1
        reference = f"{prefix}{count:06d}"
    
    return reference

def parse_common_names(names_str: str) -> list:
    """Parse common names string into list"""
    if not names_str or names_str.strip() == "":
        return []
    
    # Séparer par des virgules et nettoyer
    names = [name.strip() for name in names_str.split(',')]
    return [name for name in names if name]  # Enlever les chaînes vides

def map_country_name(country: str) -> str:
    """Map French country names to standardized format"""
    country_mapping = {
        "États-Unis": "United States",
        "Allemagne": "Germany", 
        "Royaume-Uni": "United Kingdom",
        "Italie": "Italy",
        "France": "France",
        "Danemark": "Denmark",
        "Espagne": "Spain"
    }
    return country_mapping.get(country, country)

async def validate_website_url(url: str) -> str:
    """Validate and format website URL"""
    if not url or url.strip() == "":
        return None
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url

async def check_existing_brand(name: str, official_name: str = None) -> dict:
    """Check if brand already exists in database"""
    # Recherche par nom principal
    existing = await db.brands.find_one({
        "$or": [
            {"name": {"$regex": f"^{name}$", "$options": "i"}},
            {"official_name": {"$regex": f"^{name}$", "$options": "i"}} if official_name else {}
        ]
    })
    
    if existing:
        return existing
    
    # Recherche par nom officiel si fourni
    if official_name and official_name != name:
        existing = await db.brands.find_one({
            "$or": [
                {"name": {"$regex": f"^{official_name}$", "$options": "i"}},
                {"official_name": {"$regex": f"^{official_name}$", "$options": "i"}}
            ]
        })
    
    return existing

async def import_brands_from_csv(csv_file_path: str, dry_run: bool = False):
    """Import brands from CSV file"""
    
    print(f"🚀 Début de l'importation des équipementiers depuis {csv_file_path}")
    print(f"📊 Mode: {'Simulation (dry-run)' if dry_run else 'Importation réelle'}")
    print("-" * 60)
    
    # Statistiques
    stats = {
        "total_rows": 0,
        "brands_created": 0,
        "brands_updated": 0,
        "brands_skipped": 0,
        "errors": []
    }
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Utiliser le point-virgule comme délimiteur
            csv_reader = csv.DictReader(file, delimiter=';')
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 car première ligne = headers
                stats["total_rows"] += 1
                
                try:
                    # Extraire les données
                    brand_name = row.get("Nom de la marque", "").strip()
                    official_name = row.get("Nom officiel", "").strip()
                    country = row.get("Pays", "").strip()
                    founded_year_str = row.get("Année de fondation", "").strip()
                    website = row.get("Site web", "").strip()
                    common_names_str = row.get("Noms alternatifs", "").strip()
                    
                    # Validation des données obligatoires
                    if not brand_name:
                        stats["errors"].append(f"Ligne {row_num}: Nom de marque manquant")
                        continue
                    
                    print(f"\n📦 Traitement: {brand_name}")
                    
                    # Vérifier si la marque existe déjà
                    existing_brand = await check_existing_brand(brand_name, official_name)
                    
                    if existing_brand:
                        print(f"   ⚠️  Marque déjà existante: {existing_brand['name']} (Référence: {existing_brand.get('topkit_reference', 'N/A')})")
                        stats["brands_skipped"] += 1
                        continue
                    
                    # Traitement des données
                    founded_year = None
                    if founded_year_str and founded_year_str.isdigit():
                        founded_year = int(founded_year_str)
                    
                    country_standardized = map_country_name(country) if country else None
                    website_validated = await validate_website_url(website)
                    common_names = parse_common_names(common_names_str)
                    
                    # Créer l'objet Brand
                    brand_data = {
                        "name": brand_name,
                        "official_name": official_name if official_name and official_name != brand_name else None,
                        "common_names": common_names,
                        "country": country_standardized,
                        "founded_year": founded_year,
                        "website": website_validated,
                        "created_by": SYSTEM_USER_ID,
                        "topkit_reference": await generate_reference("brand") if not dry_run else f"TK-BRAND-{stats['total_rows']:06d}"
                    }
                    
                    brand = Brand(**brand_data)
                    
                    print(f"   ✅ Données traitées:")
                    print(f"      - Nom: {brand.name}")
                    print(f"      - Nom officiel: {brand.official_name or 'N/A'}")
                    print(f"      - Pays: {brand.country or 'N/A'}")
                    print(f"      - Fondée en: {brand.founded_year or 'N/A'}")
                    print(f"      - Site web: {brand.website or 'N/A'}")
                    print(f"      - Noms alternatifs: {', '.join(brand.common_names) if brand.common_names else 'Aucun'}")
                    print(f"      - Référence TopKit: {brand.topkit_reference}")
                    
                    if not dry_run:
                        # Insérer en base de données
                        await db.brands.insert_one(brand.dict())
                        print(f"   💾 Marque créée en base de données")
                    else:
                        print(f"   🔍 [DRY-RUN] Marque non créée (simulation)")
                    
                    stats["brands_created"] += 1
                    
                except Exception as e:
                    error_msg = f"Ligne {row_num}: Erreur lors du traitement de {brand_name}: {str(e)}"
                    stats["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
                    continue
    
    except FileNotFoundError:
        print(f"❌ Fichier CSV non trouvé: {csv_file_path}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier CSV: {str(e)}")
        return False
    
    # Afficher les statistiques finales
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE L'IMPORTATION")
    print("=" * 60)
    print(f"Lignes traitées: {stats['total_rows']}")
    print(f"Marques créées: {stats['brands_created']}")
    print(f"Marques ignorées (déjà existantes): {stats['brands_skipped']}")
    print(f"Erreurs: {len(stats['errors'])}")
    
    if stats["errors"]:
        print("\n❌ ERREURS DÉTECTÉES:")
        for error in stats["errors"]:
            print(f"   - {error}")
    
    print(f"\n✅ Importation {'simulée' if dry_run else 'terminée'} avec succès!")
    
    return True

async def verify_imported_brands():
    """Verify imported brands in database"""
    print("\n🔍 VÉRIFICATION DES MARQUES IMPORTÉES")
    print("-" * 40)
    
    brands = await db.brands.find({"created_by": SYSTEM_USER_ID}).to_list(length=None)
    
    print(f"Nombre de marques importées trouvées: {len(brands)}")
    
    for brand in brands:
        brand.pop('_id', None)  # Remove MongoDB ObjectId
        print(f"\n📦 {brand['name']} ({brand['topkit_reference']})")
        print(f"   - Officiel: {brand.get('official_name', 'N/A')}")
        print(f"   - Pays: {brand.get('country', 'N/A')}")
        print(f"   - Fondée: {brand.get('founded_year', 'N/A')}")
        print(f"   - Site: {brand.get('website', 'N/A')}")
        if brand.get('common_names'):
            print(f"   - Autres noms: {', '.join(brand['common_names'])}")

async def main():
    """Main function"""
    csv_file = "/app/equipementiers_football.csv"
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        await verify_imported_brands()
        return
    
    # Demander confirmation avant importation
    print("🏈 IMPORTATION DES ÉQUIPEMENTIERS DE FOOTBALL")
    print("=" * 50)
    print(f"Fichier source: {csv_file}")
    print("Mode: Importation réelle (pas de simulation)")
    
    confirm = input("\n⚠️  Voulez-vous continuer avec l'importation? (oui/non): ").lower().strip()
    
    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("❌ Importation annulée par l'utilisateur")
        return
    
    # Exécuter l'importation
    success = await import_brands_from_csv(csv_file, dry_run=False)
    
    if success:
        print(f"\n🎉 Importation réussie! Utilisez --verify pour vérifier les données.")
    else:
        print(f"\n💥 Échec de l'importation")

if __name__ == "__main__":
    asyncio.run(main())