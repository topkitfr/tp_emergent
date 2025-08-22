#!/usr/bin/env python3
"""
Script de correction robuste pour les références d'équipes TopKit
Corriger les références dupliquées et assigner les bonnes références aux équipes prioritaires
"""

import asyncio
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

# Ordre prioritaire des équipes (les 20 plus importantes au monde)
PRIORITY_TEAMS_ORDER = [
    "Real Madrid",           # TK-TEAM-000001
    "FC Barcelona",          # TK-TEAM-000002 (sera mappé sur "FC Barcelone")
    "Manchester United",     # TK-TEAM-000003
    "Bayern Munich",         # TK-TEAM-000004
    "Liverpool",            # TK-TEAM-000005
    "AC Milan",             # TK-TEAM-000006
    "Juventus",             # TK-TEAM-000007
    "Arsenal",              # TK-TEAM-000008
    "Chelsea",              # TK-TEAM-000009
    "Inter Milan",          # TK-TEAM-000010
    "Paris Saint-Germain",  # TK-TEAM-000011
    "Manchester City",      # TK-TEAM-000012
    "Atlético Madrid",      # TK-TEAM-000013
    "Borussia Dortmund",    # TK-TEAM-000014
    "Ajax",                 # TK-TEAM-000015
    "PSV Eindhoven",        # TK-TEAM-000016
    "Feyenoord",            # TK-TEAM-000017
    "FC Porto",             # TK-TEAM-000018
    "Sporting CP",          # TK-TEAM-000019
    "SL Benfica"            # TK-TEAM-000020
]

def normalize_team_name(name: str) -> str:
    """Normaliser le nom d'équipe pour la comparaison"""
    # Mappings pour les variations de noms
    name_mappings = {
        "fc barcelone": "fc barcelona",
        "fc barcelona": "fc barcelona",
        "barcelona": "fc barcelona",
        "real madrid cf": "real madrid",
        "manchester utd": "manchester united",
        "man united": "manchester united",
        "man city": "manchester city",
        "manchester city fc": "manchester city",
        "fc bayern munich": "bayern munich",
        "bayern": "bayern munich",
        "ac milan": "ac milan",
        "milan": "ac milan",
        "internazionale": "inter milan",
        "inter": "inter milan",
        "fc inter milan": "inter milan",
        "paris sg": "paris saint-germain",
        "psg": "paris saint-germain",
        "atletico de madrid": "atlético madrid",
        "atletico madrid": "atlético madrid",
        "bvb": "borussia dortmund",
        "dortmund": "borussia dortmund",
        "ajax amsterdam": "ajax",
        "afc ajax": "ajax",
        "fc porto": "fc porto",
        "porto": "fc porto",
        "sporting lisbon": "sporting cp",
        "sporting lisboa": "sporting cp",
        "benfica": "sl benfica",
        "sl benfica": "sl benfica"
    }
    
    normalized = name.lower().strip()
    return name_mappings.get(normalized, normalized)

async def backup_teams_collection():
    """Créer une sauvegarde de la collection teams"""
    print("💾 Création d'une sauvegarde de la collection teams...")
    
    teams = await db.teams.find({}).to_list(length=None)
    backup_collection = f"teams_backup_{int(datetime.now().timestamp())}"
    
    if teams:
        await db[backup_collection].insert_many(teams)
        print(f"   ✅ Sauvegarde créée: {backup_collection} ({len(teams)} équipes)")
        return backup_collection
    else:
        print("   ⚠️  Aucune équipe trouvée pour la sauvegarde")
        return None

async def find_duplicate_references():
    """Identifier les références dupliquées"""
    print("🔍 Identification des références dupliquées...")
    
    pipeline = [
        {"$group": {
            "_id": "$topkit_reference",
            "count": {"$sum": 1},
            "teams": {"$push": {"name": "$name", "id": "$_id"}}
        }},
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"_id": 1}}
    ]
    
    duplicates = await db.teams.aggregate(pipeline).to_list(length=None)
    
    print(f"   🔍 Trouvé {len(duplicates)} références dupliquées:")
    for dup in duplicates:
        reference = dup["_id"]
        teams_list = [team["name"] for team in dup["teams"]]
        print(f"      - {reference}: {', '.join(teams_list)}")
    
    return duplicates

async def find_priority_team_by_name(name: str):
    """Trouver une équipe prioritaire par nom avec variations"""
    normalized_target = normalize_team_name(name)
    
    all_teams = await db.teams.find({}).to_list(length=None)
    
    for team in all_teams:
        team_name = team.get("name", "")
        normalized_team = normalize_team_name(team_name)
        
        if normalized_team == normalized_target:
            return team
        
        # Vérifications supplémentaires pour des cas spéciaux
        if normalized_target == "fc barcelona" and "barcelona" in normalized_team:
            return team
        if normalized_target == "ac milan" and "milan" in normalized_team and "inter" not in normalized_team:
            return team
        if normalized_target == "inter milan" and "inter" in normalized_team:
            return team
    
    return None

async def fix_team_references(dry_run: bool = False):
    """Corriger les références d'équipes de manière atomique"""
    
    print(f"🛠️  CORRECTION DES RÉFÉRENCES D'ÉQUIPES")
    print(f"📊 Mode: {'Simulation (dry-run)' if dry_run else 'Correction réelle'}")
    print("=" * 60)
    
    # Statistiques
    stats = {
        "duplicates_fixed": 0,
        "priority_teams_fixed": 0,
        "references_reassigned": 0,
        "errors": []
    }
    
    # Étape 1: Sauvegarde
    if not dry_run:
        backup_name = await backup_teams_collection()
        if not backup_name:
            print("❌ Impossible de créer une sauvegarde. Arrêt du processus.")
            return False
    
    # Étape 2: Identifier les doublons
    duplicates = await find_duplicate_references()
    
    # Étape 3: Nettoyer les références temporaires
    print("\n🧹 Nettoyage des références temporaires...")
    temp_teams = await db.teams.find({"topkit_reference": {"$regex": "^TK-TEMP-"}}).to_list(length=None)
    
    for team in temp_teams:
        temp_ref = f"TK-CLEANUP-{int(datetime.now().timestamp())}-{team['_id']}"
        if not dry_run:
            await db.teams.update_one(
                {"_id": team["_id"]},
                {"$set": {"topkit_reference": temp_ref}}
            )
        print(f"   🔧 {team['name']}: {team['topkit_reference']} → {temp_ref}")
        stats["references_reassigned"] += 1
    
    # Étape 4: Assigner les équipes prioritaires avec les bonnes références
    print(f"\n🎯 ASSIGNATION DES ÉQUIPES PRIORITAIRES")
    print("=" * 40)
    
    for index, priority_name in enumerate(PRIORITY_TEAMS_ORDER, 1):
        target_reference = f"TK-TEAM-{index:06d}"
        
        print(f"\n{target_reference} - {priority_name}")
        
        # Trouver l'équipe prioritaire
        priority_team = await find_priority_team_by_name(priority_name)
        
        if not priority_team:
            error_msg = f"Équipe prioritaire non trouvée: {priority_name}"
            stats["errors"].append(error_msg)
            print(f"   ❌ {error_msg}")
            continue
        
        current_reference = priority_team.get("topkit_reference", "")
        
        # Vérifier si la référence cible est occupée par une autre équipe
        current_holder = await db.teams.find_one({
            "topkit_reference": target_reference,
            "_id": {"$ne": priority_team["_id"]}
        })
        
        if current_holder:
            # Assigner une référence temporaire au détenteur actuel
            temp_ref = f"TK-DISPLACED-{int(datetime.now().timestamp())}-{current_holder['_id']}"
            if not dry_run:
                await db.teams.update_one(
                    {"_id": current_holder["_id"]},
                    {"$set": {"topkit_reference": temp_ref}}
                )
            print(f"   🔄 Déplacer {current_holder['name']}: {target_reference} → {temp_ref}")
            stats["references_reassigned"] += 1
        
        # Assigner la référence cible à l'équipe prioritaire
        if not dry_run:
            await db.teams.update_one(
                {"_id": priority_team["_id"]},
                {"$set": {"topkit_reference": target_reference}}
            )
        
        print(f"   ✅ {priority_team['name']}: {current_reference} → {target_reference}")
        stats["priority_teams_fixed"] += 1
    
    # Étape 5: Réassigner les équipes déplacées et temporaires
    print(f"\n🔀 RÉASSIGNATION DES ÉQUIPES DÉPLACÉES")
    print("=" * 35)
    
    # Trouver toutes les équipes avec des références temporaires
    temp_pattern_teams = await db.teams.find({
        "topkit_reference": {"$regex": "^TK-(CLEANUP|DISPLACED|TEMP)-"}
    }).to_list(length=None)
    
    # Commencer après les équipes prioritaires
    next_available = len(PRIORITY_TEAMS_ORDER) + 1
    
    # Trouver le prochain numéro disponible
    all_teams = await db.teams.find({}).to_list(length=None)
    used_numbers = set()
    
    for team in all_teams:
        ref = team.get("topkit_reference", "")
        if ref.startswith("TK-TEAM-"):
            try:
                num = int(ref.split("-")[-1])
                used_numbers.add(num)
            except ValueError:
                pass
    
    # Réassigner les équipes temporaires
    for team in temp_pattern_teams:
        # Trouver le prochain numéro disponible
        while next_available in used_numbers:
            next_available += 1
        
        new_reference = f"TK-TEAM-{next_available:06d}"
        used_numbers.add(next_available)
        
        if not dry_run:
            await db.teams.update_one(
                {"_id": team["_id"]},
                {"$set": {"topkit_reference": new_reference}}
            )
        
        print(f"   ✅ {team['name']}: {team['topkit_reference']} → {new_reference}")
        stats["references_reassigned"] += 1
        next_available += 1
    
    # Étape 6: Vérification finale
    print(f"\n🔍 VÉRIFICATION FINALE")
    print("=" * 20)
    
    if not dry_run:
        # Vérifier qu'il n'y a plus de doublons
        final_duplicates = await find_duplicate_references()
        if final_duplicates:
            print(f"   ❌ {len(final_duplicates)} références dupliquées restantes!")
            for dup in final_duplicates:
                stats["errors"].append(f"Référence dupliquée restante: {dup['_id']}")
        else:
            print("   ✅ Aucune référence dupliquée détectée")
        
        # Vérifier les équipes prioritaires
        priority_check_passed = 0
        for index, priority_name in enumerate(PRIORITY_TEAMS_ORDER, 1):
            target_reference = f"TK-TEAM-{index:06d}"
            team = await db.teams.find_one({"topkit_reference": target_reference})
            
            if team:
                team_normalized = normalize_team_name(team["name"])
                expected_normalized = normalize_team_name(priority_name)
                
                if team_normalized == expected_normalized:
                    priority_check_passed += 1
                    print(f"   ✅ {target_reference}: {team['name']}")
                else:
                    print(f"   ❌ {target_reference}: {team['name']} (attendu: {priority_name})")
            else:
                print(f"   ❌ {target_reference}: VIDE (attendu: {priority_name})")
        
        print(f"\nÉquipes prioritaires correctement assignées: {priority_check_passed}/{len(PRIORITY_TEAMS_ORDER)}")
    
    # Afficher les statistiques finales
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA CORRECTION")
    print("=" * 60)
    print(f"Doublons corrigés: {stats['duplicates_fixed']}")
    print(f"Équipes prioritaires assignées: {stats['priority_teams_fixed']}")
    print(f"Références réassignées: {stats['references_reassigned']}")
    
    if stats["errors"]:
        print(f"\n❌ ERREURS ({len(stats['errors'])}):")
        for error in stats["errors"]:
            print(f"   - {error}")
    
    print(f"\n✅ Correction {'simulée' if dry_run else 'terminée'} avec succès!")
    
    return len(stats["errors"]) == 0

async def main():
    """Fonction principale"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        print("🧪 MODE SIMULATION (DRY-RUN)")
        success = await fix_team_references(dry_run=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "--check":
        print("🔍 VÉRIFICATION DES DOUBLONS")
        await find_duplicate_references()
        return
    else:
        print("🏈 CORRECTION RÉELLE DES RÉFÉRENCES D'ÉQUIPES TOPKIT")
        print("=" * 60)
        
        confirm = input("\n⚠️  ATTENTION: Cette opération va modifier la base de données.\nUne sauvegarde sera créée automatiquement.\nVoulez-vous continuer? (oui/non): ").lower().strip()
        
        if confirm not in ['oui', 'o', 'yes', 'y']:
            print("❌ Correction annulée par l'utilisateur")
            return
        
        success = await fix_team_references(dry_run=False)
        
        if success:
            print(f"\n🎉 Correction réussie!")
        else:
            print(f"\n💥 Correction terminée avec des erreurs")

if __name__ == "__main__":
    asyncio.run(main())