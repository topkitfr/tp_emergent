#!/usr/bin/env python3
"""
Script to clear database collections for teams, brands, players, competitions, and master kits
Preserves users but clears all content data for fresh testing
"""

import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

async def clear_database():
    """Clear all content collections while preserving users"""
    MONGO_URL = os.environ.get('MONGO_URL')
    if not MONGO_URL:
        print("❌ MONGO_URL not found in environment")
        return
    
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.football_jersey_collection
    
    try:
        # Collections to clear
        collections_to_clear = [
            'teams',
            'brands', 
            'players',
            'competitions',
            'master_kits',
            'master_jerseys',  # Both naming conventions
            'reference_kits',
            'jersey_releases',  # Alternative naming
            'personal_kits',
            'contributions',
            'pending_approvals'
        ]
        
        print("🗑️  Clearing database collections...")
        
        for collection_name in collections_to_clear:
            try:
                result = await db[collection_name].delete_many({})
                print(f"   ✅ Cleared {collection_name}: {result.deleted_count} documents deleted")
            except Exception as e:
                print(f"   ⚠️  {collection_name}: {e}")
        
        # Verify users are preserved
        user_count = await db.users.count_documents({})
        print(f"\n✅ Database cleared successfully!")
        print(f"📊 Users preserved: {user_count}")
        
        # Show remaining collections
        collections = await db.list_collection_names()
        print(f"📁 Remaining collections: {collections}")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
    finally:
        client.close()

async def clear_collections(db, collections):
    """Clear all collections in the database"""
    print("🗑️  Clearing database collections...")
    
    for collection_name in collections:
        if collection_name != 'users':  # Preserve users
            try:
                result = await db[collection_name].delete_many({})
                print(f"   ✅ Cleared {collection_name}: {result.deleted_count} documents deleted")
            except Exception as e:
                print(f"   ⚠️  {collection_name}: {e}")
        else:
            count = await db[collection_name].count_documents({})
            print(f"   🔒 Preserved {collection_name}: {count} users kept")

if __name__ == "__main__":
    asyncio.run(clear_database())