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
    
    # First, check all databases
    db_names = await client.list_database_names()
    print(f"🗂️  Available databases: {db_names}")
    
    # Try both possible database names
    for db_name in ['topkit', 'football_jersey_collection']:
        db = client[db_name]
        collections = await db.list_collection_names()
        if collections:
            print(f"📁 Collections in {db_name}: {collections}")
            
            # Count documents in each collection
            for collection_name in collections:
                count = await db[collection_name].count_documents({})
                print(f"   📊 {collection_name}: {count} documents")
            
            # Clear the collections if this is the right database
            if input(f"\nClear all collections in database '{db_name}'? (y/N): ").lower() == 'y':
                await clear_collections(db, collections)
                break
        else:
            print(f"📁 {db_name}: No collections found")
    
    try:
        pass
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