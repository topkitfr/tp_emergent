#!/usr/bin/env python3
"""
Script de réorganisation des références des équipes TopKit
Corriger l'ordre pour respecter l'importance et ajouter les nouvelles équipes
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

from collaborative_models import Team

# Charger les variables d'environnement
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Configuration MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# ID d'utilisateur système pour l'importation
SYSTEM_USER_ID = "system-reorganize-teams"

# Ordre prioritaire des équipes (les plus importantes en premier)
PRIORITY_TEAMS_ORDER = [
    # Top 10 clubs mondiaux par prestige (ordre historique et actuel)
    ("Real Madrid", "Espagne", "La Liga", 1),
    ("FC Barcelone", "Espagne", "La Liga", 1), 
    ("Manchester United", "Angleterre", "Premier League", 1),
    ("Bayern Munich", "Allemagne", "Bundesliga", 1),
    ("Liverpool", "Angleterre", "Premier League", 1),
    ("AC Milan", "Italie", "Serie A", 1),
    ("Juventus", "Italie", "Serie A", 1),
    ("Arsenal", "Angleterre", "Premier League", 1),
    ("Chelsea", "Angleterre", "Premier League", 1),
    ("Inter Milan", "Italie", "Serie A", 1),
    
    # Suite des grands clubs européens
    ("Paris Saint-Germain", "France", "Ligue 1", 1),
    ("Manchester City", "Angleterre", "Premier League", 1),
    ("Atlético Madrid", "Espagne", "La Liga", 1),
    ("Borussia Dortmund", "Allemagne", "Bundesliga", 1),
    ("Ajax", "Pays-Bas", "Eredivisie", 1),
    ("PSV Eindhoven", "Pays-Bas", "Eredivisie", 1),
    ("Feyenoord", "Pays-Bas", "Eredivisie", 1),
    ("FC Porto", "Portugal", "Primeira Liga", 1),
    ("Sporting CP", "Portugal", "Primeira Liga", 1),
    ("SL Benfica", "Portugal", "Primeira Liga", 1),
]

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

def map_league_name(league: str) -> str:
    """Map French league names to English"""
    league_mapping = {
        "Ligue 1": "Ligue 1",
        "Ligue 2": "Ligue 2",
        "Premier League": "Premier League",
        "Championship": "Championship",
        "La Liga": "La Liga",
        "Segunda División": "Segunda Division",
        "Bundesliga": "Bundesliga",
        "2. Bundesliga": "2. Bundesliga",
        "Serie A": "Serie A",
        "Serie B": "Serie B",
        "Primeira Liga": "Primeira Liga",
        "Liga Portugal 2": "Liga Portugal 2",
        "Eredivisie": "Eredivisie",
        "Eerste Divisie": "Eerste Divisie",
        "Jupiler Pro League": "Belgian Pro League",
        "Challenger Pro League": "Belgian Second Division",
        "Série A": "Serie A",
        "Série B": "Serie B",
        "Primera División": "Primera Division",
        "Primera B Nacional": "Primera B Nacional",
        "MLS": "MLS",
        "USL Championship": "USL Championship",
        "J1 League": "J1 League",
        "J2 League": "J2 League",
        "Super League": "Chinese Super League",
        "China League One": "China League One"
    }
    return league_mapping.get(league, league)

def parse_team_colors(colors_str: str) -> list:
    """Parse team colors string into list"""
    if not colors_str or colors_str.strip() == "":
        return []
    
    colors = [color.strip() for color in colors_str.split()]
    return [color for color in colors if color]

async def load_teams_from_csv(csv_file_path: str) -> list:
    """Load teams from CSV file"""
    teams_data = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                team_name = row.get("Team Name", "").strip()
                short_name = row.get("Short Name", "").strip()
                country = row.get("Country", "").strip()
                league = row.get("League", "").strip()
                tier = row.get("Tier", "").strip()
                city = row.get("City", "").strip()
                founded_str = row.get("Year of Foundation", "").strip()
                colors_str = row.get("Team Colors", "").strip()
                
                if not team_name:
                    continue
                
                founded_year = None
                if founded_str and founded_str.isdigit():
                    founded_year = int(founded_str)
                
                tier_int = None
                if tier and tier.isdigit():
                    tier_int = int(tier)
                
                team_data = {
                    'name': team_name,
                    'short_name': short_name if short_name else None,
                    'country': map_country_name(country),
                    'league': map_league_name(league),
                    'tier': tier_int,
                    'city': city if city else None,
                    'founded_year': founded_year,
                    'primary_colors': parse_team_colors(colors_str)
                }
                
                teams_data.append(team_data)
    
    except Exception as e:
        print(f"❌ Erreur lors du chargement du CSV: {str(e)}")
        return []
    
    return teams_data

async def get_existing_teams():
    """Get all existing teams from database"""
    teams = await db.teams.find({}).to_list(length=None)
    return {team['name']: team for team in teams}

async def create_priority_ordered_teams(teams_data: list, dry_run: bool = False):
    """Create teams with priority order for references"""
    
    print(f"🚀 RÉORGANISATION DES RÉFÉRENCES D'ÉQUIPES")
    print(f"📊 Mode: {'Simulation (dry-run)' if dry_run else 'Mise à jour réelle'}")
    print("-" * 60)
    
    existing_teams = await get_existing_teams()
    teams_by_name = {team['name']: team for team in teams_data}
    
    # Stats
    stats = {
        "teams_updated": 0,
        "teams_created": 0,
        "teams_reordered": 0,
        "priority_teams_fixed": 0,
        "errors": []
    }
    
    # Phase 1: Créer/Updater les équipes prioritaires avec les bonnes références
    print(f"\n📋 PHASE 1: ÉQUIPES PRIORITAIRES (Top {len(PRIORITY_TEAMS_ORDER)})")
    print("=" * 50)
    
    for index, (team_name, expected_country, expected_league, expected_tier) in enumerate(PRIORITY_TEAMS_ORDER, 1):
        reference = f"TK-TEAM-{index:06d}"
        
        print(f"\n🎯 {reference} - {team_name}")
        
        # Chercher l'équipe dans les données CSV
        team_data = None
        for team in teams_data:
            if (team['name'].lower() == team_name.lower() or 
                (team_name == "FC Barcelone" and team['name'] == "FC Barcelona")):
                team_data = team
                break
        
        if not team_data:
            print(f"   ⚠️  Équipe non trouvée dans le CSV")
            continue
        
        # Vérifier si référence actuelle est occupée par autre équipe
        current_holder = await db.teams.find_one({"topkit_reference": reference})
        
        if current_holder and current_holder['name'] != team_name:
            print(f"   🔄 Référence {reference} occupée par {current_holder['name']}")
            if not dry_run:
                # Assigner référence temporaire
                temp_ref = f"TK-TEMP-{int(datetime.now().timestamp())}"
                await db.teams.update_one(
                    {"_id": current_holder["_id"]},
                    {"$set": {"topkit_reference": temp_ref}}
                )
                print(f"      ↳ Référence temporaire assignée: {temp_ref}")
        
        # Créer/Updater l'équipe prioritaire
        existing_team = existing_teams.get(team_name)
        
        team_obj_data = {
            "name": team_data['name'],
            "short_name": team_data['short_name'],
            "country": team_data['country'],
            "city": team_data['city'],
            "founded_year": team_data['founded_year'],
            "primary_colors": team_data['primary_colors'],
            "league": team_data['league'],
            "tier": team_data['tier'],
            "topkit_reference": reference,
            "created_by": SYSTEM_USER_ID if not existing_team else existing_team.get('created_by'),
        }
        
        if not dry_run:
            if existing_team:
                # Update existing team
                await db.teams.update_one(
                    {"name": team_name},
                    {"$set": team_obj_data}
                )
                print(f"   ✅ Équipe mise à jour avec référence {reference}")
                stats["teams_updated"] += 1
            else:
                # Create new team
                team_obj_data["created_at"] = datetime.utcnow()
                team = Team(**team_obj_data)
                await db.teams.insert_one(team.dict())
                print(f"   ✅ Équipe créée avec référence {reference}")
                stats["teams_created"] += 1
        else:
            print(f"   🔍 [DRY-RUN] Équipe {'mise à jour' if existing_team else 'créée'} avec référence {reference}")
        
        stats["priority_teams_fixed"] += 1
    
    # Phase 2: Traiter les autres équipes
    print(f"\n📋 PHASE 2: AUTRES ÉQUIPES")
    print("=" * 30)
    
    priority_team_names = {name.lower() for name, _, _, _ in PRIORITY_TEAMS_ORDER}
    next_reference_num = len(PRIORITY_TEAMS_ORDER) + 1
    
    for team_data in teams_data:
        team_name = team_data['name']
        
        # Skip priority teams (already processed)
        if (team_name.lower() in priority_team_names or 
            (team_name == "FC Barcelona" and "fc barcelone" in priority_team_names)):
            continue
        
        existing_team = existing_teams.get(team_name)
        
        if existing_team:
            # Si l'équipe existe mais n'a pas une référence dans les priorités, la garder
            if existing_team.get('topkit_reference', '').startswith('TK-TEAM-'):
                current_num = int(existing_team['topkit_reference'].split('-')[-1])
                if current_num <= len(PRIORITY_TEAMS_ORDER):
                    # Cette équipe occupe une place prioritaire, la déplacer
                    new_reference = f"TK-TEAM-{next_reference_num:06d}"
                    next_reference_num += 1
                    
                    if not dry_run:
                        await db.teams.update_one(
                            {"name": team_name},
                            {"$set": {"topkit_reference": new_reference}}
                        )
                    
                    print(f"   🔄 {team_name}: {existing_team['topkit_reference']} → {new_reference}")
                    stats["teams_reordered"] += 1
                else:
                    print(f"   ✅ {team_name}: conserve {existing_team['topkit_reference']}")
        else:
            # Nouvelle équipe
            reference = f"TK-TEAM-{next_reference_num:06d}"
            next_reference_num += 1
            
            team_obj_data = {
                "name": team_data['name'],
                "short_name": team_data['short_name'],
                "country": team_data['country'],
                "city": team_data['city'],
                "founded_year": team_data['founded_year'],
                "primary_colors": team_data['primary_colors'],
                "league": team_data['league'],
                "tier": team_data['tier'],
                "topkit_reference": reference,
                "created_by": SYSTEM_USER_ID,
                "created_at": datetime.utcnow()
            }
            
            if not dry_run:
                team = Team(**team_obj_data)
                await db.teams.insert_one(team.dict())
            
            print(f"   ✅ {team_name}: créée avec {reference}")
            stats["teams_created"] += 1
    
    # Nettoyer les références temporaires
    if not dry_run:
        temp_teams = await db.teams.find({"topkit_reference": {"$regex": "^TK-TEMP-"}}).to_list(length=None)
        for team in temp_teams:
            reference = f"TK-TEAM-{next_reference_num:06d}"
            next_reference_num += 1
            await db.teams.update_one(
                {"_id": team["_id"]},
                {"$set": {"topkit_reference": reference}}
            )
            print(f"   🔧 {team['name']}: référence temporaire → {reference}")
    
    # Afficher les statistiques finales
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA RÉORGANISATION")
    print("=" * 60)
    print(f"Équipes prioritaires corrigées: {stats['priority_teams_fixed']}")
    print(f"Équipes mises à jour: {stats['teams_updated']}")
    print(f"Nouvelles équipes créées: {stats['teams_created']}")
    print(f"Équipes réordonnées: {stats['teams_reordered']}")
    
    if stats["errors"]:
        print("\n❌ ERREURS:")
        for error in stats["errors"]:
            print(f"   - {error}")
    
    print(f"\n✅ Réorganisation {'simulée' if dry_run else 'terminée'} avec succès!")
    
    return True

async def verify_priority_order():
    """Verify priority teams have correct order"""
    print("\n🔍 VÉRIFICATION DE L'ORDRE DES ÉQUIPES PRIORITAIRES")
    print("-" * 50)
    
    for index, (expected_name, _, _, _) in enumerate(PRIORITY_TEAMS_ORDER, 1):
        reference = f"TK-TEAM-{index:06d}"
        team = await db.teams.find_one({"topkit_reference": reference})
        
        if team:
            actual_name = team['name']
            if (actual_name.lower() == expected_name.lower() or 
                (expected_name == "FC Barcelone" and actual_name == "FC Barcelona")):
                print(f"   ✅ {reference}: {actual_name}")
            else:
                print(f"   ❌ {reference}: {actual_name} (attendu: {expected_name})")
        else:
            print(f"   ❌ {reference}: VIDE (attendu: {expected_name})")

async def main():
    """Main function"""
    csv_file = "/app/clubs_complets.txt"
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        await verify_priority_order()
        return
    
    print("🏈 RÉORGANISATION DES RÉFÉRENCES D'ÉQUIPES TOPKIT")
    print("=" * 60)
    print(f"Fichier source: {csv_file}")
    print("Mode: Réorganisation réelle")
    
    confirm = input("\n⚠️  Voulez-vous continuer avec la réorganisation? (oui/non): ").lower().strip()
    
    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("❌ Réorganisation annulée par l'utilisateur")
        return
    
    # Charger les équipes du CSV
    print("📂 Chargement des équipes depuis le CSV...")
    teams_data = await load_teams_from_csv(csv_file)
    
    if not teams_data:
        print("❌ Aucune équipe chargée depuis le CSV")
        return
    
    print(f"✅ {len(teams_data)} équipes chargées depuis le CSV")
    
    # Exécuter la réorganisation
    success = await create_priority_ordered_teams(teams_data, dry_run=False)
    
    if success:
        print(f"\n🎉 Réorganisation réussie! Utilisez --verify pour vérifier l'ordre.")
    else:
        print(f"\n💥 Échec de la réorganisation")

if __name__ == "__main__":
    asyncio.run(main())