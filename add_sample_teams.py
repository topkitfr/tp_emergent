#!/usr/bin/env python3
"""
Script to add sample teams with competition relationships for testing interconnected forms
"""

import asyncio
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def add_sample_teams():
    """Add sample teams with competition relationships"""
    
    print("Adding sample teams with competition relationships...")
    
    # Get some competitions from the database
    competitions = await db.competitions.find({}).to_list(length=None)
    
    # Find specific competitions
    ligue1 = next((c for c in competitions if c['competition_name'] == 'Ligue 1'), None)
    premier_league = next((c for c in competitions if c['competition_name'] == 'Premier League'), None)
    la_liga = next((c for c in competitions if c['competition_name'] == 'La Liga'), None)
    champions_league = next((c for c in competitions if c['competition_name'] == 'UEFA Champions League'), None)
    
    if not all([ligue1, premier_league, la_liga, champions_league]):
        print("Required competitions not found in database")
        return
    
    # Sample teams data
    sample_teams = [
        {
            "name": "Paris Saint-Germain",
            "short_name": "PSG",
            "common_names": ["PSG", "Paris SG", "Paris Saint-Germain"],
            "country": "France",
            "city": "Paris",
            "founded_year": 1970,
            "primary_competition_id": ligue1['id'],
            "current_competitions": [ligue1['id'], champions_league['id']],
            "colors": ["navy", "red", "white"]
        },
        {
            "name": "FC Barcelona",
            "short_name": "Barça",
            "common_names": ["Barça", "Barcelona", "FC Barcelona"],
            "country": "Spain", 
            "city": "Barcelona",
            "founded_year": 1899,
            "primary_competition_id": la_liga['id'],
            "current_competitions": [la_liga['id'], champions_league['id']],
            "colors": ["blue", "red"]
        },
        {
            "name": "Manchester United",
            "short_name": "Man Utd",
            "common_names": ["Man Utd", "Manchester United", "United"],
            "country": "United Kingdom",
            "city": "Manchester",
            "founded_year": 1878,
            "primary_competition_id": premier_league['id'],
            "current_competitions": [premier_league['id']],
            "colors": ["red", "white"]
        },
        {
            "name": "Olympique Lyonnais",
            "short_name": "OL",
            "common_names": ["OL", "Lyon", "Olympique Lyonnais"],
            "country": "France",
            "city": "Lyon",
            "founded_year": 1950,
            "primary_competition_id": ligue1['id'],
            "current_competitions": [ligue1['id']],
            "colors": ["blue", "white", "red"]
        }
    ]
    
    # Generate fake admin user ID for created_by field
    admin_user_id = "admin-system-import"
    
    teams_added = 0
    
    for team_data in sample_teams:
        try:
            # Check if team already exists
            existing_team = await db.teams.find_one({"name": team_data["name"]})
            if existing_team:
                print(f"Team {team_data['name']} already exists, skipping...")
                continue
            
            # Generate TopKit reference
            team_count = await db.teams.count_documents({})
            topkit_ref = f"TK-TEAM-{str(team_count + 1).zfill(6)}"
            
            # Create team document
            team = {
                "id": str(uuid.uuid4()),
                **team_data,
                "logo_url": None,
                "competition_history": [],
                "external_ids": {},
                "created_at": datetime.utcnow(),
                "created_by": admin_user_id,
                "verified_level": "community_verified",
                "verified_at": datetime.utcnow(),
                "verified_by": admin_user_id,
                "modification_count": 0,
                "last_modified_at": None,
                "last_modified_by": None,
                "topkit_reference": topkit_ref
            }
            
            # Insert into database
            await db.teams.insert_one(team)
            teams_added += 1
            
            print(f"Added: {team_data['name']} ({topkit_ref}) - Primary: {team_data.get('primary_competition_id', 'None')[:8]}...")
            
        except Exception as e:
            print(f"Error adding team {team_data.get('name', 'Unknown')}: {e}")
            continue
    
    print(f"\n✅ Successfully added {teams_added} teams to the database!")
    
    # Verify the insertion
    total_teams = await db.teams.count_documents({})
    print(f"Total teams in database: {total_teams}")
    
    # List teams with their competitions
    print("\nTeams with competition relationships:")
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
    asyncio.run(add_sample_teams())