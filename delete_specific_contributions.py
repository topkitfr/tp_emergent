#!/usr/bin/env python3
"""
Delete Specific Contributions
============================

Script to delete specific contributions that are awaiting approval:
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

async def delete_specific_contributions():
    """Delete the specified contributions"""
    
    # Items to delete
    items_to_delete = [
        'TK-TEAM-D6685AF4',
        'TK-TEAM-2F94B5F5', 
        'TK-RKIT-C2110564',
        'TK-MKIT-D9FF6273',
        'TK-COMP-E3A38BB5',
        'TK-PLAYER-7F915C33'
    ]
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    
    try:
        # Use topkit database
        db = client['topkit']
        
        print(f"🎯 Searching for contributions to delete...")
        
        # Check contributions_v2 collection
        contributions_collection = db['contributions_v2']
        
        deletion_summary = {}
        
        # Find and delete each contribution
        for item_id in items_to_delete:
            print(f"\n🔍 Searching for contribution: {item_id}")
            
            # Look for contributions that reference this ID
            # Check both direct ID matches and data field references
            contributions_found = []
            
            # Search by ID field
            contrib_by_id = await contributions_collection.find_one({'id': item_id})
            if contrib_by_id:
                contributions_found.append(contrib_by_id)
            
            # Search in data fields for references to this ID
            async for contrib in contributions_collection.find():
                contrib_data = contrib.get('data', {})
                # Check if any data field contains this ID
                for field_name, field_value in contrib_data.items():
                    if field_value == item_id:
                        if contrib not in contributions_found:
                            contributions_found.append(contrib)
                        break
            
            if not contributions_found:
                print(f"   ⚠️  No contributions found for {item_id}")
                deletion_summary[item_id] = {'status': 'not_found', 'contributions': 0}
                continue
            
            print(f"   📍 Found {len(contributions_found)} contribution(s) for {item_id}")
            
            deleted_count = 0
            for contrib in contributions_found:
                contrib_id = contrib.get('id')
                contrib_title = contrib.get('title', 'Unknown Title')
                contrib_status = contrib.get('status', 'Unknown Status')
                
                print(f"   🗑️  Deleting contribution: {contrib_id}")
                print(f"       Title: {contrib_title}")
                print(f"       Status: {contrib_status}")
                
                # Delete this contribution
                delete_result = await contributions_collection.delete_one({'_id': contrib['_id']})
                
                if delete_result.deleted_count > 0:
                    print(f"       ✅ Successfully deleted contribution {contrib_id}")
                    deleted_count += 1
                else:
                    print(f"       ❌ Failed to delete contribution {contrib_id}")
            
            deletion_summary[item_id] = {
                'status': 'processed',
                'contributions': len(contributions_found),
                'deleted': deleted_count
            }
        
        # Summary
        print(f"\n📊 DELETION SUMMARY:")
        total_found = sum(item['contributions'] for item in deletion_summary.values() if item['status'] == 'processed')
        total_deleted = sum(item['deleted'] for item in deletion_summary.values() if item['status'] == 'processed')
        
        print(f"   📍 Total contributions found: {total_found}")
        print(f"   ✅ Total contributions deleted: {total_deleted}")
        
        for item_id, info in deletion_summary.items():
            if info['status'] == 'not_found':
                print(f"   ⚠️  {item_id}: Not found")
            else:
                print(f"   ✅ {item_id}: Found {info['contributions']}, Deleted {info['deleted']}")
        
        print(f"\n🎉 Contribution cleanup complete!")
        
    except Exception as e:
        print(f"❌ Error during deletion: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(delete_specific_contributions())