#!/usr/bin/env python3
"""
Script spécialisé pour corriger les références dupliquées restantes
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

async def find_duplicate_references():
    """Identifier les références dupliquées"""
    pipeline = [
        {"$group": {
            "_id": "$topkit_reference",
            "count": {"$sum": 1},
            "teams": {"$push": {"name": "$name", "id": "$_id", "country": "$country"}}
        }},
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"_id": 1}}
    ]
    
    duplicates = await db.teams.aggregate(pipeline).to_list(length=None)
    return duplicates

async def get_next_available_reference():
    """Trouver la prochaine référence disponible"""
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
    
    # Trouver le prochain numéro disponible
    next_num = 1
    while next_num in used_numbers:
        next_num += 1
    
    return f"TK-TEAM-{next_num:06d}"

async def fix_duplicates_smart():
    """Corriger les doublons en gardant l'équipe la plus importante"""
    
    print("🔧 CORRECTION INTELLIGENTE DES DOUBLONS")
    print("=" * 50)
    
    duplicates = await find_duplicate_references()
    
    if not duplicates:
        print("✅ Aucun doublon détecté!")
        return True
    
    print(f"📊 {len(duplicates)} références dupliquées à corriger")
    
    stats = {"fixed": 0, "errors": []}
    
    # Ordre de priorité par pays/ligue (pour décider quelle équipe garder)
    priority_order = {
        "Spain": 1, "England": 2, "Germany": 3, "Italy": 4, "France": 5,
        "Portugal": 6, "Netherlands": 7, "Brazil": 8, "Argentina": 9
    }
    
    for duplicate_info in duplicates:
        reference = duplicate_info["_id"]
        teams = duplicate_info["teams"]
        
        print(f"\n🔍 Traitement de {reference}")
        print(f"   Équipes: {[t['name'] for t in teams]}")
        
        # Trier les équipes par priorité (pays) et par nom
        def team_priority(team):
            country = team.get("country", "Unknown")
            country_priority = priority_order.get(country, 999)
            # Les équipes de Ligue 1 sont prioritaires pour la France
            name_lower = team["name"].lower()
            
            # Bonus de priorité pour certaines équipes importantes
            if any(keyword in name_lower for keyword in ["marseille", "monaco", "lyon", "saint-etienne"]):
                country_priority -= 0.5
            
            return (country_priority, team["name"])
        
        sorted_teams = sorted(teams, key=team_priority)
        
        # La première équipe garde la référence, les autres sont déplacées
        team_to_keep = sorted_teams[0]
        teams_to_move = sorted_teams[1:]
        
        print(f"   ✅ Garde: {team_to_keep['name']} ({team_to_keep.get('country', 'Unknown')})")
        
        for team_to_move in teams_to_move:
            new_reference = await get_next_available_reference()
            
            try:
                await db.teams.update_one(
                    {"_id": team_to_move["id"]},
                    {"$set": {"topkit_reference": new_reference}}
                )
                
                print(f"   🔄 Déplace: {team_to_move['name']} → {new_reference}")
                stats["fixed"] += 1
                
            except Exception as e:
                error_msg = f"Erreur lors du déplacement de {team_to_move['name']}: {str(e)}"
                stats["errors"].append(error_msg)
                print(f"   ❌ {error_msg}")
    
    # Vérification finale
    print(f"\n🔍 VÉRIFICATION FINALE")
    remaining_duplicates = await find_duplicate_references()
    
    if remaining_duplicates:
        print(f"   ❌ {len(remaining_duplicates)} doublons restants!")
        for dup in remaining_duplicates:
            print(f"      - {dup['_id']}: {[t['name'] for t in dup['teams']]}")
        return False
    else:
        print("   ✅ Tous les doublons ont été corrigés!")
        
    print(f"\n📊 RÉSUMÉ:")
    print(f"   Équipes déplacées: {stats['fixed']}")
    print(f"   Erreurs: {len(stats['errors'])}")
    
    for error in stats["errors"]:
        print(f"   ❌ {error}")
    
    return len(stats["errors"]) == 0

async def main():
    """Fonction principale"""
    
    print("🏈 CORRECTION DES DOUBLONS DE RÉFÉRENCES D'ÉQUIPES")
    print("=" * 60)
    
    # Vérifier d'abord l'état actuel
    duplicates = await find_duplicate_references()
    
    if not duplicates:
        print("✅ Aucun doublon détecté dans la base de données!")
        return
    
    print(f"📊 {len(duplicates)} références dupliquées détectées")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        print("\n🔍 DÉTAIL DES DOUBLONS:")
        for dup in duplicates:
            teams_list = [f"{t['name']} ({t.get('country', 'Unknown')})" for t in dup['teams']]
            print(f"   - {dup['_id']}: {', '.join(teams_list)}")
        return
    
    confirm = input(f"\n⚠️  Corriger {len(duplicates)} références dupliquées? (oui/non): ").lower().strip()
    
    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("❌ Correction annulée par l'utilisateur")
        return
    
    success = await fix_duplicates_smart()
    
    if success:
        print(f"\n🎉 Tous les doublons ont été corrigés avec succès!")
    else:
        print(f"\n💥 Correction terminée mais avec des problèmes restants")

if __name__ == "__main__":
    asyncio.run(main())