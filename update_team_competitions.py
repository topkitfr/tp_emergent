#!/usr/bin/env python3
"""
Script to update existing teams with competition relationships
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def update_team_competitions():
    """Update existing teams with competition relationships"""
    
    print("Updating existing teams with competition relationships...")
    
    # Get competitions
    competitions = await db.competitions.find({}).to_list(length=None)
    
    # Find specific competitions
    ligue1 = next((c for c in competitions if c['competition_name'] == 'Ligue 1'), None)
    premier_league = next((c for c in competitions if c['competition_name'] == 'Premier League'), None)
    la_liga = next((c for c in competitions if c['competition_name'] == 'La Liga'), None)
    serie_a = next((c for c in competitions if c['competition_name'] == 'Serie A'), None)
    champions_league = next((c for c in competitions if c['competition_name'] == 'UEFA Champions League'), None)
    
    # Team updates mapping
    team_updates = [
        {
            "name": "FC Barcelona",
            "primary_competition_id": la_liga['id'] if la_liga else None,
            "current_competitions": [la_liga['id'], champions_league['id']] if la_liga and champions_league else []
        },
        {
            "name": "Paris Saint-Germain", 
            "primary_competition_id": ligue1['id'] if ligue1 else None,
            "current_competitions": [ligue1['id'], champions_league['id']] if ligue1 and champions_league else []
        },
        {
            "name": "Manchester United",
            "primary_competition_id": premier_league['id'] if premier_league else None,
            "current_competitions": [premier_league['id']] if premier_league else []
        },
        {
            "name": "AC Milan",
            "primary_competition_id": serie_a['id'] if serie_a else None,
            "current_competitions": [serie_a['id'], champions_league['id']] if serie_a and champions_league else []
        }
    ]
    
    updated_count = 0
    
    for update in team_updates:
        try:
            # Find team by name
            team = await db.teams.find_one({"name": update["name"]})
            if not team:
                print(f"Team {update['name']} not found")
                continue
            
            # Update team with competition relationships
            update_data = {
                "primary_competition_id": update["primary_competition_id"],
                "current_competitions": update["current_competitions"]
            }
            
            result = await db.teams.update_one(
                {"id": team["id"]},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                primary_comp_name = "None"
                if update["primary_competition_id"]:
                    comp = await db.competitions.find_one({"id": update["primary_competition_id"]})
                    if comp:
                        primary_comp_name = comp["competition_name"]
                
                current_comp_names = []
                for comp_id in update["current_competitions"]:
                    comp = await db.competitions.find_one({"id": comp_id})
                    if comp:
                        current_comp_names.append(comp["competition_name"])
                
                print(f"✅ Updated {update['name']} - Primary: {primary_comp_name}, Current: {', '.join(current_comp_names)}")
            else:
                print(f"❌ Failed to update {update['name']}")
                
        except Exception as e:
            print(f"Error updating team {update['name']}: {e}")
    
    print(f"\n✅ Successfully updated {updated_count} teams with competition relationships!")
    
    # Verify updates
    print("\nVerification - Teams with competition relationships:")
    async for team in db.teams.find({}):
        primary_comp = "None"
        if team.get("primary_competition_id"):
            comp = await db.competitions.find_one({"id": team["primary_competition_id"]})
            if comp:
                primary_comp = comp["competition_name"]
        
        current_comps = []
        for comp_id in team.get("current_competitions", []):
            comp = await db.competitions.find_one({"id": comp_id})
            if comp:
                current_comps.append(comp["competition_name"])
        
        print(f"- {team['name']} ({team['topkit_reference']}) - Primary: {primary_comp}, Current: {', '.join(current_comps) if current_comps else 'None'}")

if __name__ == "__main__":
    asyncio.run(update_team_competitions())