#!/usr/bin/env python3
"""
Clean Up Test Contributions
===========================

Script to delete test contributions with pending_review status
keeping only the approved real contributions
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Get MongoDB URL from environment
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

async def cleanup_test_contributions():
    """Delete test contributions with pending_review status"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    
    try:
        # Use topkit database
        db = client['topkit']
        
        print(f"🧹 Cleaning up test contributions...")
        
        # Check contributions_v2 collection
        contributions_collection = db['contributions_v2']
        
        # Find all contributions with pending_review status (these are test data)
        # Also find the specific contribution containing TK-PLAYER-7F915C33
        test_contributions = []
        
        # Find pending_review contributions
        async for contrib in contributions_collection.find({'status': 'pending_review'}):
            test_contributions.append({
                'id': contrib.get('id'),
                'title': contrib.get('title'),
                'entity_type': contrib.get('entity_type'),
                'created_at': contrib.get('created_at'),
                'status': contrib.get('status'),
                'topkit_reference': contrib.get('topkit_reference', 'None')
            })
        
        # Also find the specific contribution with TK-PLAYER-7F915C33
        specific_contrib = await contributions_collection.find_one({'topkit_reference': 'TK-PLAYER-7F915C33'})
        if specific_contrib and specific_contrib not in [tc for tc in test_contributions if tc['id'] == specific_contrib.get('id')]:
            test_contributions.append({
                'id': specific_contrib.get('id'),
                'title': specific_contrib.get('title'),
                'entity_type': specific_contrib.get('entity_type'),
                'created_at': specific_contrib.get('created_at'),
                'status': specific_contrib.get('status'),
                'topkit_reference': specific_contrib.get('topkit_reference', 'None')
            })
        
        print(f"📊 Found {len(test_contributions)} test contributions with pending_review status")
        
        if len(test_contributions) == 0:
            print("✅ No test contributions to clean up")
            return
        
        # Show what will be deleted
        print(f"\n🗑️  CONTRIBUTIONS TO DELETE:")
        for contrib in test_contributions:
            ref_info = f" [Ref: {contrib['topkit_reference']}]" if contrib['topkit_reference'] != 'None' else ""
            print(f"   - {contrib['entity_type']}: {contrib['title']} ({contrib['id']}){ref_info}")
        
        # Ask for confirmation in the script (for safety)
        print(f"\n⚠️  About to delete {len(test_contributions)} test contributions...")
        print("   This will keep only the approved real contributions:")
        print("   ✅ Teams: AC Milan, Paris Saint-Germain")
        print("   ✅ Brands: Nike, Puma") 
        print("   ✅ Players: Leao, Dembele, Maldini")
        
        # Delete all test contributions
        delete_result = await contributions_collection.delete_many({'status': 'pending_review'})
        
        print(f"\n✅ Successfully deleted {delete_result.deleted_count} test contributions")
        
        # Show what's left
        remaining_count = await contributions_collection.count_documents({})
        print(f"📊 Remaining contributions: {remaining_count}")
        
        print(f"\n📋 REMAINING CONTRIBUTIONS:")
        async for contrib in contributions_collection.find().sort('entity_type', 1):
            contrib_id = contrib.get('id', 'No ID')
            contrib_title = contrib.get('title', 'No Title')
            contrib_type = contrib.get('entity_type', 'Unknown Type')
            contrib_status = contrib.get('status', 'Unknown Status')
            
            status_emoji = "✅" if contrib_status == 'approved' else "⏳"
            print(f"   {status_emoji} {contrib_type}: {contrib_title} ({contrib_id})")
        
        print(f"\n🎉 Test contribution cleanup complete!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_test_contributions())