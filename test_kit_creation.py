#!/usr/bin/env python3
"""
Script to create test master kits and reference kits for testing inheritance functionality
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment
load_dotenv('/app/backend/.env')

async def create_test_data():
    # Connect to database
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🔄 Creating test master kits and reference kits...")
    
    # Check if we have teams and brands
    teams = await db.teams.find().to_list(10)
    brands = await db.brands.find().to_list(10)
    
    if not teams:
        print("❌ No teams found. Creating a test team...")
        team_data = {
            "id": str(uuid.uuid4()),
            "name": "Paris Saint-Germain",
            "short_name": "PSG", 
            "country": "France",
            "city": "Paris",
            "colors": ["navy", "red", "white"],
            "created_at": datetime.utcnow(),
            "created_by": "system",
            "verified_level": "community_verified",
            "verified_at": datetime.utcnow(),
            "topkit_reference": "TK-TEAM-000001"
        }
        await db.teams.insert_one(team_data)
        teams = [team_data]
        print("✅ Created test team: PSG")
    
    if not brands:
        print("❌ No brands found. Creating a test brand...")
        brand_data = {
            "id": str(uuid.uuid4()),
            "name": "Nike",
            "country": "USA",
            "founded_year": 1964,
            "created_at": datetime.utcnow(),
            "created_by": "system",
            "verified_level": "community_verified",
            "verified_at": datetime.utcnow(),
            "topkit_reference": "TK-BRAND-000001"
        }
        await db.brands.insert_one(brand_data)
        brands = [brand_data]
        print("✅ Created test brand: Nike")
    
    # Create master kit
    master_kit_data = {
        "id": str(uuid.uuid4()),
        "team_id": teams[0]["id"],
        "brand_id": brands[0]["id"],
        "season": "2024-25",
        "jersey_type": "home",
        "model": "authentic",
        "primary_color": "#001F5B",
        "secondary_colors": ["#FF0000", "#FFFFFF"],
        "pattern": "solid",
        "main_sponsor": "Qatar Airways",
        "description": "PSG 2024-25 Home Kit",
        "created_at": datetime.utcnow(),
        "created_by": "system",
        "verified_level": "community_verified",
        "verified_at": datetime.utcnow(),
        "topkit_reference": "TK-MASTER-000001"
    }
    
    # Check if master kit already exists
    existing_master = await db.master_kits.find_one({"topkit_reference": master_kit_data["topkit_reference"]})
    if not existing_master:
        await db.master_kits.insert_one(master_kit_data)
        print("✅ Created test master kit: PSG 2024-25 Home")
    else:
        master_kit_data = existing_master
        print("ℹ️  Master kit already exists: PSG 2024-25 Home")
    
    # Create reference kit
    reference_kit_data = {
        "id": str(uuid.uuid4()),
        "master_kit_id": master_kit_data["id"],
        "model_name": "PSG 2024-25 Home Authentic",
        "release_type": "authentic",
        "available_sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "original_retail_price": 140.0,
        "current_market_estimate": 120.0,
        "official_product_code": "DV1199-411",
        "is_limited_edition": False,
        "main_photo_url": "/api/uploads/test-psg-kit.jpg",
        "product_images": ["/api/uploads/test-psg-kit.jpg", "/api/uploads/test-psg-kit-back.jpg"],
        "created_at": datetime.utcnow(),
        "created_by": "system",
        "verified_level": "community_verified",
        "verified_at": datetime.utcnow(),
        "topkit_reference": "TK-REF-000001"
    }
    
    # Check if reference kit already exists
    existing_ref = await db.reference_kits.find_one({"topkit_reference": reference_kit_data["topkit_reference"]})
    if not existing_ref:
        await db.reference_kits.insert_one(reference_kit_data)
        print("✅ Created test reference kit: PSG 2024-25 Home Authentic")
    else:
        print("ℹ️  Reference kit already exists: PSG 2024-25 Home Authentic")
    
    print("\n📊 Database summary:")
    teams_count = await db.teams.count_documents({})
    brands_count = await db.brands.count_documents({})
    master_kits_count = await db.master_kits.count_documents({})
    reference_kits_count = await db.reference_kits.count_documents({})
    personal_kits_count = await db.personal_kits.count_documents({})
    wanted_kits_count = await db.wanted_kits.count_documents({})
    
    print(f"Teams: {teams_count}")
    print(f"Brands: {brands_count}") 
    print(f"Master Kits: {master_kits_count}")
    print(f"Reference Kits: {reference_kits_count}")
    print(f"Personal Kits: {personal_kits_count}")
    print(f"Wanted Kits: {wanted_kits_count}")
    
    print("\n✅ Test data creation complete!")

if __name__ == "__main__":
    asyncio.run(create_test_data())