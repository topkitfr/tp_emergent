#!/usr/bin/env python3
"""
CSV Kit Import Script
Cleans existing master_kits and my_collection data and imports new kit data from CSV
"""

import asyncio
import csv
import uuid
import requests
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'topkit')

# CSV URL
CSV_URL = "https://customer-assets.emergentagent.com/job_jersey-pricing/artifacts/ygicn3vf_20_kit.csv"

# Team name mappings (CSV name -> potential database variations)
TEAM_MAPPINGS = {
    "Real Madrid": ["Real Madrid", "Real Madrid CF", "Real Madrid Club de Fútbol"],
    "FC Barcelone": ["Barcelona", "FC Barcelona", "FC Barcelone", "Futbol Club Barcelona"],
    "Bayern Munich": ["Bayern Munich", "FC Bayern Munich", "Bayern München"],
    "Liverpool": ["Liverpool", "Liverpool FC", "Liverpool Football Club"]
}

# Brand name mappings
BRAND_MAPPINGS = {
    "Adidas": ["Adidas", "adidas"],
    "Nike": ["Nike", "NIKE"]
}

async def get_csv_data():
    """Download and parse CSV data"""
    print(f"Downloading CSV from: {CSV_URL}")
    response = requests.get(CSV_URL)
    response.raise_for_status()
    
    # Parse CSV
    csv_data = []
    csv_text = response.text
    reader = csv.DictReader(csv_text.splitlines())
    
    for row in reader:
        csv_data.append({
            'kit_type': row['Kit Type'].lower(),  # replica/authentic
            'team': row['Team'],
            'kit_style': row['Kit Style'].lower(),  # home/away/third/gk
            'brand': row['Brand'],
            'season': row['Season/Year'],
            'photo_front': row['Photo Front'],
            'photo_back': row['Photo Back'] or None
        })
    
    print(f"Parsed {len(csv_data)} kits from CSV")
    return csv_data

async def find_or_create_team(db, team_name):
    """Find existing team in database or create new one"""
    
    # First try exact match
    team = await db.teams.find_one({"name": team_name})
    if team:
        print(f"Found exact team match: {team_name}")
        return team["id"]
    
    # Try mapped variations
    if team_name in TEAM_MAPPINGS:
        for variation in TEAM_MAPPINGS[team_name]:
            team = await db.teams.find_one({"name": {"$regex": f"^{variation}$", "$options": "i"}})
            if team:
                print(f"Found team variation match: {team_name} -> {team['name']}")
                return team["id"]
    
    # Try partial match
    team = await db.teams.find_one({"name": {"$regex": team_name, "$options": "i"}})
    if team:
        print(f"Found team partial match: {team_name} -> {team['name']}")
        return team["id"]
    
    # Create new team
    team_id = str(uuid.uuid4())
    new_team = {
        "id": team_id,
        "name": team_name,
        "short_name": team_name[:10],
        "country": "Unknown",
        "founded_year": None,
        "logo_url": None,
        "created_at": datetime.now(timezone.utc)
    }
    await db.teams.insert_one(new_team)
    print(f"Created new team: {team_name} (ID: {team_id})")
    return team_id

async def find_or_create_brand(db, brand_name):
    """Find existing brand in database or create new one"""
    
    # Try exact match
    brand = await db.brands.find_one({"name": brand_name, "type": "brand"})
    if brand:
        print(f"Found exact brand match: {brand_name}")
        return brand["id"]
    
    # Try mapped variations
    if brand_name in BRAND_MAPPINGS:
        for variation in BRAND_MAPPINGS[brand_name]:
            brand = await db.brands.find_one({"name": {"$regex": f"^{variation}$", "$options": "i"}, "type": "brand"})
            if brand:
                print(f"Found brand variation match: {brand_name} -> {brand['name']}")
                return brand["id"]
    
    # Try partial match
    brand = await db.brands.find_one({"name": {"$regex": brand_name, "$options": "i"}, "type": "brand"})
    if brand:
        print(f"Found brand partial match: {brand_name} -> {brand['name']}")
        return brand["id"]
    
    # Create new brand
    brand_id = str(uuid.uuid4())
    new_brand = {
        "id": brand_id,
        "name": brand_name,
        "type": "brand",
        "country": "Unknown",
        "founded_year": None,
        "logo_url": None,
        "created_at": datetime.now(timezone.utc)
    }
    await db.brands.insert_one(new_brand)
    print(f"Created new brand: {brand_name} (ID: {brand_id})")
    return brand_id

async def create_master_kit(db, kit_data, club_id, brand_id):
    """Create a master kit from CSV data"""
    
    kit_id = str(uuid.uuid4())
    
    # Map kit_style to proper values
    kit_style_map = {
        'home': 'home',
        'away': 'away', 
        'third': 'third',
        'gk': 'goalkeeper'
    }
    
    master_kit = {
        "id": kit_id,
        "topkit_reference": f"TK-MASTER-{kit_id[:6].upper()}",
        
        # Core identification
        "club_id": club_id,
        "club": kit_data['team'],  # For backward compatibility
        "club_name": kit_data['team'],
        
        "brand_id": brand_id,  
        "brand": kit_data['brand'],  # For backward compatibility
        "brand_name": kit_data['brand'],
        
        "season": kit_data['season'],
        "kit_style": kit_style_map.get(kit_data['kit_style'], kit_data['kit_style']),
        "kit_type": kit_data['kit_type'],
        
        # Visual details
        "front_photo_url": kit_data['photo_front'],
        "back_photo_url": kit_data['photo_back'],
        "primary_color": "Unknown",
        "secondary_color": None,
        
        # Default values
        "competition_id": None,
        "competition": None,
        "competition_name": None,
        "main_sponsor_id": None,
        "main_sponsor": None,
        "main_sponsor_name": None,
        "gender": "man",
        "model": kit_data['kit_type'],
        
        # Stats
        "total_collectors": 0,
        "total_wanted": 0,
        "price_estimate": 50.0,
        
        # Metadata
        "created_at": datetime.now(timezone.utc),
        "created_by": "system_import",
        "is_approved": True
    }
    
    await db.master_kits.insert_one(master_kit)
    print(f"Created master kit: {kit_data['team']} {kit_data['season']} {kit_data['kit_style']} (ID: {kit_id})")
    return kit_id

async def main():
    """Main import process"""
    print("Starting CSV kit import process...")
    
    # Connect to database
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Step 1: Clean existing data
        print("\n=== CLEANING EXISTING DATA ===")
        
        master_kits_count = await db.master_kits.count_documents({})
        collection_count = await db.my_collection.count_documents({})
        
        print(f"Found {master_kits_count} existing master kits")
        print(f"Found {collection_count} existing collection items")
        
        # Delete existing data
        if master_kits_count > 0:
            await db.master_kits.delete_many({})
            print(f"✅ Deleted {master_kits_count} master kits")
        
        if collection_count > 0:
            await db.my_collection.delete_many({})
            print(f"✅ Deleted {collection_count} collection items")
        
        # Step 2: Download and parse CSV
        print("\n=== DOWNLOADING CSV DATA ===")
        csv_data = await get_csv_data()
        
        # Step 3: Import new data
        print("\n=== IMPORTING NEW KITS ===")
        
        imported_count = 0
        for kit_data in csv_data:
            print(f"\nProcessing: {kit_data['team']} {kit_data['season']} {kit_data['kit_style']}")
            
            # Find or create team
            club_id = await find_or_create_team(db, kit_data['team'])
            
            # Find or create brand
            brand_id = await find_or_create_brand(db, kit_data['brand'])
            
            # Create master kit
            kit_id = await create_master_kit(db, kit_data, club_id, brand_id)
            
            imported_count += 1
        
        # Step 4: Summary
        print(f"\n=== IMPORT COMPLETE ===")
        print(f"✅ Successfully imported {imported_count} master kits")
        
        # Verify final counts
        new_master_kits_count = await db.master_kits.count_documents({})
        new_teams_count = await db.teams.count_documents({})
        new_brands_count = await db.brands.count_documents({})
        
        print(f"📊 Final database state:")
        print(f"  - Master kits: {new_master_kits_count}")
        print(f"  - Teams: {new_teams_count}")  
        print(f"  - Brands: {new_brands_count}")
        
    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        raise
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())