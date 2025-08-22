#!/usr/bin/env python3
"""
Script pour mettre à jour les données manquantes des équipes depuis le CSV
"""

import asyncio
import csv
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Configuration MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

def parse_team_colors(colors_str: str) -> list:
    """Parse team colors string into list"""
    if not colors_str or colors_str.strip() == "":
        return []
    
    colors = [color.strip().lower() for color in colors_str.split()]
    return [color for color in colors if color]

def map_country_name(country: str) -> str:
    """Map French country names to English"""
    country_mapping = {
        "France": "France",
        "Angleterre": "England", 
        "Espagne": "Spain",
        "Allemagne": "Germany",
        "Italie": "Italy",
        "Portugal": "Portugal",
        "Pays-Bas": "Netherlands",
        "Belgique": "Belgium",
        "Brésil": "Brazil",
        "Argentine": "Argentina",
        "États-Unis": "United States",
        "Japon": "Japan",
        "Chine": "China"
    }
    return country_mapping.get(country, country)

async def load_teams_from_csv(csv_file_path: str) -> dict:
    """Load teams from CSV file and return as dictionary keyed by team name"""
    teams_data = {}
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                team_name = row.get("Team Name", "").strip()
                short_name = row.get("Short Name", "").strip()
                country = row.get("Country", "").strip()
                city = row.get("City", "").strip()
                founded_str = row.get("Year of Foundation", "").strip()
                colors_str = row.get("Team Colors", "").strip()
                
                if not team_name:
                    continue
                
                founded_year = None
                if founded_str and founded_str.isdigit():
                    founded_year = int(founded_str)
                
                teams_data[team_name] = {
                    'name': team_name,
                    'short_name': short_name if short_name else None,
                    'country': map_country_name(country),
                    'city': city if city else None,
                    'founded_year': founded_year,
                    'colors': parse_team_colors(colors_str)
                }
    
    except Exception as e:
        print(f"❌ Erreur lors du chargement du CSV: {str(e)}")
        return {}
    
    return teams_data

async def find_missing_data_teams():
    """Find teams with missing data"""
    teams = await db.teams.find({}).to_list(length=None)
    
    missing_data_teams = []
    
    for team in teams:
        missing_fields = []
        
        if not team.get('short_name'):
            missing_fields.append('short_name')
        if not team.get('founded_year'):
            missing_fields.append('founded_year')
        if not team.get('city'):
            missing_fields.append('city')
        if not team.get('colors') or len(team.get('colors', [])) == 0:
            missing_fields.append('colors')
        
        if missing_fields:
            missing_data_teams.append({
                'team': team,
                'missing_fields': missing_fields
            })
    
    return missing_data_teams

async def update_teams_data(csv_teams_data: dict, dry_run: bool = False):
    """Update teams with missing data from CSV"""
    
    print(f"🔧 MISE À JOUR DES DONNÉES D'ÉQUIPES MANQUANTES")
    print(f"📊 Mode: {'Simulation (dry-run)' if dry_run else 'Mise à jour réelle'}")
    print("=" * 60)
    
    # Trouver les équipes avec des données manquantes
    missing_data_teams = await find_missing_data_teams()
    
    print(f"📊 {len(missing_data_teams)} équipes avec des données incomplètes")
    
    stats = {
        "teams_updated": 0,
        "fields_updated": 0,
        "teams_not_found_in_csv": 0,
        "errors": []
    }
    
    for missing_info in missing_data_teams:
        team = missing_info['team']
        missing_fields = missing_info['missing_fields']
        team_name = team['name']
        
        print(f"\n🔍 {team_name} ({team['topkit_reference']})")
        print(f"   Champs manquants: {', '.join(missing_fields)}")
        
        # Chercher l'équipe dans les données CSV
        csv_team = csv_teams_data.get(team_name)
        
        if not csv_team:
            # Essayer des variantes de noms
            csv_team = None
            for csv_name, csv_data in csv_teams_data.items():
                if (csv_name.lower() == team_name.lower() or
                    csv_name.lower().replace(' ', '') == team_name.lower().replace(' ', '') or
                    (csv_data['short_name'] and csv_data['short_name'].lower() == team_name.lower())):
                    csv_team = csv_data
                    print(f"   📝 Trouvé via variante: {csv_name}")
                    break
        
        if not csv_team:
            print(f"   ❌ Équipe non trouvée dans le CSV")
            stats["teams_not_found_in_csv"] += 1
            continue
        
        # Préparer les mises à jour
        updates = {}
        
        if 'short_name' in missing_fields and csv_team['short_name']:
            updates['short_name'] = csv_team['short_name']
            print(f"   ✅ Nom court: {csv_team['short_name']}")
        
        if 'founded_year' in missing_fields and csv_team['founded_year']:
            updates['founded_year'] = csv_team['founded_year']
            print(f"   ✅ Année de fondation: {csv_team['founded_year']}")
        
        if 'city' in missing_fields and csv_team['city']:
            updates['city'] = csv_team['city']
            print(f"   ✅ Ville: {csv_team['city']}")
        
        if 'colors' in missing_fields and csv_team['colors']:
            updates['colors'] = csv_team['colors']
            print(f"   ✅ Couleurs: {', '.join(csv_team['colors'])}")
        
        if updates:
            if not dry_run:
                try:
                    await db.teams.update_one(
                        {"_id": team["_id"]},
                        {"$set": updates}
                    )
                    stats["teams_updated"] += 1
                    stats["fields_updated"] += len(updates)
                    print(f"   💾 Équipe mise à jour avec {len(updates)} champs")
                except Exception as e:
                    error_msg = f"Erreur lors de la mise à jour de {team_name}: {str(e)}"
                    stats["errors"].append(error_msg)
                    print(f"   ❌ {error_msg}")
            else:
                print(f"   🔍 [DRY-RUN] {len(updates)} champs seraient mis à jour")
                stats["teams_updated"] += 1
                stats["fields_updated"] += len(updates)
        else:
            print(f"   ⚠️  Aucune donnée utile trouvée dans le CSV")
    
    # Afficher les statistiques finales
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA MISE À JOUR")
    print("=" * 60)
    print(f"Équipes mises à jour: {stats['teams_updated']}")
    print(f"Champs mis à jour: {stats['fields_updated']}")
    print(f"Équipes non trouvées dans CSV: {stats['teams_not_found_in_csv']}")
    
    if stats["errors"]:
        print(f"\n❌ ERREURS ({len(stats['errors'])}):")
        for error in stats["errors"]:
            print(f"   - {error}")
    
    print(f"\n✅ Mise à jour {'simulée' if dry_run else 'terminée'} avec succès!")
    
    return len(stats["errors"]) == 0

async def main():
    """Fonction principale"""
    csv_file = "/app/clubs_complets.txt"
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Afficher les équipes avec des données manquantes
        missing_data_teams = await find_missing_data_teams()
        print(f"📊 {len(missing_data_teams)} équipes avec des données incomplètes:")
        
        for missing_info in missing_data_teams[:10]:  # Limiter à 10 pour l'affichage
            team = missing_info['team']
            missing_fields = missing_info['missing_fields']
            print(f"   - {team['name']} ({team['topkit_reference']}): {', '.join(missing_fields)}")
        
        if len(missing_data_teams) > 10:
            print(f"   ... et {len(missing_data_teams) - 10} autres équipes")
        
        return
    
    print("🏈 MISE À JOUR DES DONNÉES D'ÉQUIPES MANQUANTES")
    print("=" * 60)
    
    # Charger les données du CSV
    print("📂 Chargement des équipes depuis le CSV...")
    csv_teams_data = await load_teams_from_csv(csv_file)
    
    if not csv_teams_data:
        print("❌ Aucune équipe chargée depuis le CSV")
        return
    
    print(f"✅ {len(csv_teams_data)} équipes chargées depuis le CSV")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("🧪 MODE SIMULATION")
        success = await update_teams_data(csv_teams_data, dry_run=True)
    else:
        confirm = input(f"\n⚠️  Mettre à jour les données manquantes des équipes? (oui/non): ").lower().strip()
        
        if confirm not in ['oui', 'o', 'yes', 'y']:
            print("❌ Mise à jour annulée par l'utilisateur")
            return
        
        success = await update_teams_data(csv_teams_data, dry_run=False)
    
    if success:
        print(f"\n🎉 Mise à jour réussie!")
    else:
        print(f"\n💥 Mise à jour terminée avec des erreurs")

if __name__ == "__main__":
    asyncio.run(main())