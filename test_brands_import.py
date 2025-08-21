#!/usr/bin/env python3
"""
Test script pour l'importation des équipementiers - DRY RUN uniquement
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

def parse_common_names(names_str: str) -> list:
    """Parse common names string into list"""
    if not names_str or names_str.strip() == "":
        return []
    
    names = [name.strip() for name in names_str.split(',')]
    return [name for name in names if name]

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

async def test_csv_parsing():
    """Test CSV parsing without database insertion"""
    csv_file_path = "/app/equipementiers_football.csv"
    
    print("🧪 TEST DE PARSING DU FICHIER CSV")
    print("=" * 50)
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            
            for row_num, row in enumerate(csv_reader, start=2):
                # Extraire les données
                brand_name = row.get("Nom de la marque", "").strip()
                official_name = row.get("Nom officiel", "").strip()
                country = row.get("Pays", "").strip()
                founded_year_str = row.get("Année de fondation", "").strip()
                website = row.get("Site web", "").strip()
                common_names_str = row.get("Noms alternatifs", "").strip()
                
                print(f"\n📦 Ligne {row_num}: {brand_name}")
                print(f"   Raw data: {dict(row)}")
                
                # Validation des données obligatoires
                if not brand_name:
                    print(f"   ❌ Nom de marque manquant")
                    continue
                
                # Traitement des données
                founded_year = None
                if founded_year_str and founded_year_str.isdigit():
                    founded_year = int(founded_year_str)
                
                country_standardized = map_country_name(country) if country else None
                website_validated = await validate_website_url(website)
                common_names = parse_common_names(common_names_str)
                
                print(f"   ✅ Données traitées:")
                print(f"      - Nom: {brand_name}")
                print(f"      - Nom officiel: {official_name if official_name and official_name != brand_name else 'N/A'}")
                print(f"      - Pays: {country_standardized or 'N/A'}")
                print(f"      - Fondée en: {founded_year or 'N/A'}")
                print(f"      - Site web: {website_validated or 'N/A'}")
                print(f"      - Noms alternatifs: {', '.join(common_names) if common_names else 'Aucun'}")
                
                # Test de création du modèle Brand
                try:
                    brand_data = {
                        "name": brand_name,
                        "official_name": official_name if official_name and official_name != brand_name else None,
                        "common_names": common_names,
                        "country": country_standardized,
                        "founded_year": founded_year,
                        "website": website_validated,
                        "created_by": "test-user",
                        "topkit_reference": f"TK-BRAND-{row_num-1:06d}"
                    }
                    
                    brand = Brand(**brand_data)
                    print(f"      ✅ Modèle Brand créé avec succès")
                    
                except Exception as e:
                    print(f"      ❌ Erreur lors de la création du modèle Brand: {str(e)}")
                    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_csv_parsing())