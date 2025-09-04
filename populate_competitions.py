#!/usr/bin/env python3
"""
Script to populate the database with competitions from the CSV file
"""

import asyncio
import csv
import io
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# CSV data from the uploaded file
CSV_DATA = """id,competition_name,official_name,alternative_names,type,confederations_federations,country,level,year_created,logo,trophy_photo
1,Ligue 1,Ligue 1 Uber Eats,"L1;French Championship",National league,UEFA,France,1,1932,links/ligue1_logo.png,links/ligue1_trophy.png
2,Premier League,Premier League,"PL;English Premier League",National league,UEFA,United Kingdom,1,1992,links/pl_logo.png,links/pl_trophy.png
3,UEFA Champions League,UEFA Champions League,"UCL;European Cup",Continental competition,UEFA,,1,1955,links/uefa_cl_logo.png,links/uefa_cl_trophy.png
4,UEFA Europa League,UEFA Europa League,"UEL;UEFA Cup",Continental competition,UEFA,,1,1971,links/uefa_el_logo.png,links/uefa_el_trophy.png
5,Coupe de France,Coupe de France,"French Cup;Coupe Charles Simon",National cup,UEFA,France,3,1917,links/cdf_logo.png,links/cdf_trophy.png
6,FIFA World Cup,FIFA World Cup,"World Cup;WC",International competition,FIFA,,1,1930,links/fifa_wc_logo.png,links/fifa_wc_trophy.png
7,UEFA European Championship,UEFA European Championship,"Euros;EURO",International competition,UEFA,,1,1960,links/euro_logo.png,links/euro_trophy.png
8,Copa Libertadores,CONMEBOL Libertadores,"Copa Lib;Libertadores",Continental competition,CONMEBOL,,1,1960,links/libertadores_logo.png,links/libertadores_trophy.png
9,Finalissima,CONMEBOL–UEFA Cup of Champions,,Intercontinental competition,UEFA;CONMEBOL,,1,2022,links/finalissima_logo.png,links/finalissima_trophy.png
10,Bundesliga,Bundesliga,,National league,UEFA,Germany,1,1963,links/bundesliga_logo.png,links/bundesliga_trophy.png
11,Serie A,Serie A,"Calcio;Italian Championship",National league,UEFA,Italy,1,1898,links/seriea_logo.png,links/seriea_trophy.png
12,La Liga,La Liga,"Primera División;Spanish Championship",National league,UEFA,Spain,1,1929,links/laliga_logo.png,links/laliga_trophy.png
13,FIFA Club World Cup,FIFA Club World Cup,"Club World Cup",Intercontinental competition,FIFA,,1,2000,links/fifa_club_wc_logo.png,links/fifa_club_wc_trophy.png
14,Ligue 2,Ligue 2 BKT,,National league,UEFA,France,2,1933,links/ligue2_logo.png,links/ligue2_trophy.png
15,UEFA Super Cup,UEFA Super Cup,,Continental super cup,UEFA,,1,1973,links/uefa_supercup_logo.png,links/uefa_supercup_trophy.png
16,Copa América,Copa América,"South American Cup",International competition,CONMEBOL,,1,1916,links/copa_america_logo.png,links/copa_america_trophy.png
17,Africa Cup of Nations,Africa Cup of Nations,"AFCON;CAN",International competition,CAF,,1,1957,links/can_logo.png,links/can_trophy.png
18,CONCACAF Gold Cup,CONCACAF Gold Cup,,International competition,CONCACAF,,1,1963,links/gold_cup_logo.png,links/gold_cup_trophy.png
19,CAF Champions League,CAF Champions League,"African Champions League",Continental competition,CAF,,1,1964,links/caf_cl_logo.png,links/caf_cl_trophy.png
20,UEFA Europa Conference League,UEFA Europa Conference League,"UECL;C4",Continental competition,UEFA,,1,2021,links/uefa_ecl_logo.png,links/uefa_ecl_trophy.png"""

async def populate_competitions():
    """Populate competitions from CSV data"""
    
    print("Starting competition population from CSV data...")
    
    # Parse CSV data
    csv_reader = csv.DictReader(io.StringIO(CSV_DATA))
    
    # Clear existing competitions if any
    await db.competitions.delete_many({})
    print("Cleared existing competitions")
    
    # Generate a fake admin user ID for created_by field
    admin_user_id = "admin-system-import"
    
    competitions_added = 0
    
    for row in csv_reader:
        try:
            # Parse alternative names
            alternative_names = []
            if row['alternative_names']:
                alternative_names = [name.strip() for name in row['alternative_names'].split(';')]
            
            # Parse confederations/federations
            confederations = []
            if row['confederations_federations']:
                confederations = [conf.strip() for conf in row['confederations_federations'].split(';')]
            
            # Generate TopKit reference
            topkit_ref = f"TK-COMP-{str(int(row['id'])).zfill(6)}"
            
            # Create competition document
            competition = {
                "id": str(uuid.uuid4()),
                "competition_name": row['competition_name'],
                "official_name": row['official_name'] if row['official_name'] else None,
                "alternative_names": alternative_names,
                "type": row['type'],
                "confederations_federations": confederations,
                "country": row['country'] if row['country'] else None,
                "level": int(row['level']) if row['level'] else None,
                "year_created": int(row['year_created']) if row['year_created'] else None,
                "logo": row['logo'] if row['logo'] else None,
                "trophy_photo": row['trophy_photo'] if row['trophy_photo'] else None,
                "secondary_images": [],
                "primary_color": None,
                "is_recurring": True,
                "current_season": None,
                "created_at": datetime.utcnow(),
                "created_by": admin_user_id,
                "verified_level": "community_verified",  # Pre-verified since from official source
                "verified_at": datetime.utcnow(),
                "verified_by": admin_user_id,
                "modification_count": 0,
                "last_modified_at": None,
                "last_modified_by": None,
                "topkit_reference": topkit_ref
            }
            
            # Insert into database
            await db.competitions.insert_one(competition)
            competitions_added += 1
            
            print(f"Added: {row['competition_name']} ({topkit_ref})")
            
        except Exception as e:
            print(f"Error adding competition {row.get('competition_name', 'Unknown')}: {e}")
            continue
    
    print(f"\n✅ Successfully added {competitions_added} competitions to the database!")
    
    # Verify the insertion
    total_competitions = await db.competitions.count_documents({})
    print(f"Total competitions in database: {total_competitions}")
    
    # List some examples
    print("\nSample competitions added:")
    async for comp in db.competitions.find({}).limit(5):
        print(f"- {comp['competition_name']} ({comp['topkit_reference']}) - {comp['type']}")

if __name__ == "__main__":
    asyncio.run(populate_competitions())