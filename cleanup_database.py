#!/usr/bin/env python3
"""
Database cleanup script to remove master kits, reference kits, and extra competitions
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def cleanup_database():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.topkit
    
    print("🧹 Starting database cleanup...")
    
    # 1. Delete all master_kits
    master_kits_result = await db.master_kits.delete_many({})
    print(f"✅ Deleted {master_kits_result.deleted_count} master_kits")
    
    # 2. Delete all master_jerseys
    master_jerseys_result = await db.master_jerseys.delete_many({})
    print(f"✅ Deleted {master_jerseys_result.deleted_count} master_jerseys")
    
    # 3. Delete all reference_kits
    reference_kits_result = await db.reference_kits.delete_many({})
    print(f"✅ Deleted {reference_kits_result.deleted_count} reference_kits")
    
    # 4. Delete all competitions except TK-COMP-E0A5C8E6
    competitions_to_delete = await db.competitions.delete_many({
        "topkit_reference": {"$ne": "TK-COMP-E0A5C8E6"}
    })
    print(f"✅ Deleted {competitions_to_delete.deleted_count} competitions (kept TK-COMP-E0A5C8E6)")
    
    # 5. Verify what's left
    remaining_competitions = await db.competitions.find({}).to_list(length=None)
    print(f"\n📊 Remaining competitions: {len(remaining_competitions)}")
    for comp in remaining_competitions:
        print(f"  - {comp.get('name')} (TopKit Ref: {comp.get('topkit_reference')})")
    
    # 6. Check final counts
    print(f"\n📈 Final counts:")
    print(f"  - master_kits: {await db.master_kits.count_documents({})}")
    print(f"  - master_jerseys: {await db.master_jerseys.count_documents({})}")
    print(f"  - reference_kits: {await db.reference_kits.count_documents({})}")
    print(f"  - competitions: {await db.competitions.count_documents({})}")
    
    client.close()
    print("\n🎉 Database cleanup completed!")

if __name__ == "__main__":
    asyncio.run(cleanup_database())