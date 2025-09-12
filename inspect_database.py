#!/usr/bin/env python3
"""
Inspect current database structure to understand the schema mismatch
"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def inspect_database():
    """Inspect database structure"""
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.topkit_db
    
    print("=== DATABASE INSPECTION ===\n")
    
    # Check master_kits collection
    master_kits_count = await db.master_kits.count_documents({})
    print(f"Master Kits Count: {master_kits_count}")
    
    if master_kits_count > 0:
        # Get a sample document
        sample = await db.master_kits.find_one()
        print("\n=== SAMPLE MASTER KIT STRUCTURE ===")
        for key, value in sample.items():
            print(f"{key}: {value} ({type(value).__name__})")
        
        # Check all unique gender values
        print("\n=== UNIQUE GENDER VALUES ===")
        gender_values = await db.master_kits.distinct("gender")
        print(f"Gender values found: {gender_values}")
        
        # Check for required fields in new schema
        print("\n=== CHECKING REQUIRED FIELDS ===")
        required_fields = ['club_id', 'competition_id', 'brand_id', 'primary_color']
        for field in required_fields:
            count_with_field = await db.master_kits.count_documents({field: {"$exists": True, "$ne": None}})
            print(f"'{field}' exists and not null: {count_with_field}/{master_kits_count}")
    
    # Check other related collections
    print("\n=== OTHER COLLECTIONS ===")
    collections = ['teams', 'brands', 'competitions', 'players']
    for collection_name in collections:
        count = await db[collection_name].count_documents({})
        print(f"{collection_name}: {count} documents")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_database())