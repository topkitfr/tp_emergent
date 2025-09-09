#!/usr/bin/env python3
"""
Delete Specific Awaiting Approval Items
======================================

Script to delete specific catalog items that are awaiting approval:
- TK-TEAM-D6685AF4 (team)
- TK-TEAM-2F94B5F5 (team)
- TK-RKIT-C2110564 (reference kit)
- TK-MKIT-D9FF6273 (master kit)
- TK-COMP-E3A38BB5 (competition)
- TK-PLAYER-7F915C33 (player)
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Get MongoDB URL from environment
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

async def delete_specific_items():
    """Delete the specified catalog items and related data"""
    
    # Items to delete
    items_to_delete = [
        {'id': 'TK-TEAM-D6685AF4', 'type': 'team', 'collection': 'teams'},
        {'id': 'TK-TEAM-2F94B5F5', 'type': 'team', 'collection': 'teams'},
        {'id': 'TK-RKIT-C2110564', 'type': 'reference_kit', 'collection': 'reference_kits'},
        {'id': 'TK-MKIT-D9FF6273', 'type': 'master_kit', 'collection': 'master_kits'},
        {'id': 'TK-COMP-E3A38BB5', 'type': 'competition', 'collection': 'competitions'},
        {'id': 'TK-PLAYER-7F915C33', 'type': 'player', 'collection': 'players'}
    ]
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    
    try:
        # List all databases
        databases = await client.list_database_names()
        print(f"📋 Available databases: {databases}")
        
        # Find the topkit database
        db_name = None
        for db in databases:
            if 'topkit' in db.lower() or 'jersey' in db.lower():
                db_name = db
                break
        
        if not db_name:
            # Default to common database names
            for common_name in ['topkit', 'jersey_catalog', 'collaborative_platform']:
                if common_name in databases:
                    db_name = common_name
                    break
        
        if not db_name:
            print("❌ Could not find the appropriate database. Available databases:")
            for db in databases:
                print(f"  - {db}")
            return
        
        print(f"🎯 Using database: {db_name}")
        db = client[db_name]
        
        # Get all collection names
        collections = await db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        deletion_summary = {}
        
        # Delete each item
        for item in items_to_delete:
            item_id = item['id']
            item_type = item['type']
            collection_name = item['collection']
            
            print(f"\n🗑️  Deleting {item_type}: {item_id}")
            
            if collection_name not in collections:
                print(f"   ⚠️  Collection '{collection_name}' not found, skipping...")
                continue
            
            collection = db[collection_name]
            
            # Check if item exists
            existing_item = await collection.find_one({'id': item_id})
            if not existing_item:
                print(f"   ⚠️  Item {item_id} not found in {collection_name}")
                continue
            
            print(f"   📍 Found item: {existing_item.get('name', existing_item.get('competition_name', 'Unknown Name'))}")
            
            # Delete the item
            delete_result = await collection.delete_one({'id': item_id})
            
            if delete_result.deleted_count > 0:
                print(f"   ✅ Successfully deleted {item_id} from {collection_name}")
                deletion_summary[item_id] = {'status': 'deleted', 'type': item_type}
            else:
                print(f"   ❌ Failed to delete {item_id} from {collection_name}")
                deletion_summary[item_id] = {'status': 'failed', 'type': item_type}
        
        # Now clean up related data
        print(f"\n🧹 Cleaning up related data...")
        
        # Clean up personal_kits that might reference deleted reference_kits or master_kits
        if 'personal_kits' in collections:
            deleted_reference_kits = [item['id'] for item in items_to_delete if item['type'] == 'reference_kit']
            if deleted_reference_kits:
                personal_kits_result = await db.personal_kits.delete_many({
                    'reference_kit_id': {'$in': deleted_reference_kits}
                })
                print(f"   🗑️  Deleted {personal_kits_result.deleted_count} personal_kits referencing deleted reference_kits")
        
        # Clean up wanted_kits that might reference deleted items
        if 'wanted_kits' in collections:
            deleted_reference_kits = [item['id'] for item in items_to_delete if item['type'] == 'reference_kit']
            if deleted_reference_kits:
                wanted_kits_result = await db.wanted_kits.delete_many({
                    'reference_kit_id': {'$in': deleted_reference_kits}
                })
                print(f"   🗑️  Deleted {wanted_kits_result.deleted_count} wanted_kits referencing deleted reference_kits")
        
        # Clean up contributions that reference deleted items
        if 'contributions_v2' in collections:
            deleted_ids = [item['id'] for item in items_to_delete]
            # Look for contributions that might reference these items in their data
            contributions_to_delete = []
            async for contrib in db.contributions_v2.find():
                contrib_data = contrib.get('data', {})
                # Check if this contribution references any of the deleted items
                for field_value in contrib_data.values():
                    if isinstance(field_value, str) and field_value in deleted_ids:
                        contributions_to_delete.append(contrib['id'])
                        break
            
            if contributions_to_delete:
                contributions_result = await db.contributions_v2.delete_many({
                    'id': {'$in': contributions_to_delete}
                })
                print(f"   🗑️  Deleted {contributions_result.deleted_count} contributions referencing deleted items")
        
        # Summary
        print(f"\n📊 DELETION SUMMARY:")
        successful_deletions = sum(1 for item in deletion_summary.values() if item['status'] == 'deleted')
        failed_deletions = sum(1 for item in deletion_summary.values() if item['status'] == 'failed')
        
        print(f"   ✅ Successfully deleted: {successful_deletions} items")
        print(f"   ❌ Failed to delete: {failed_deletions} items")
        
        for item_id, info in deletion_summary.items():
            status_emoji = "✅" if info['status'] == 'deleted' else "❌"
            print(f"   {status_emoji} {item_id} ({info['type']}): {info['status']}")
        
        print(f"\n🎉 Cleanup complete! All specified awaiting approval items have been processed.")
        
    except Exception as e:
        print(f"❌ Error during deletion: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(delete_specific_items())