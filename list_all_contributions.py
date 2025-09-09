#!/usr/bin/env python3
"""
List All Current Contributions
==============================

Script to list all current contributions to see what exists
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Get MongoDB URL from environment
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

async def list_all_contributions():
    """List all current contributions"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    
    try:
        # Use topkit database
        db = client['topkit']
        
        print(f"📋 Listing all contributions...")
        
        # Check contributions_v2 collection
        contributions_collection = db['contributions_v2']
        
        # Count total contributions
        total_count = await contributions_collection.count_documents({})
        print(f"📊 Total contributions: {total_count}")
        
        if total_count == 0:
            print("   ℹ️  No contributions found")
            return
        
        # List all contributions
        print(f"\n📝 CONTRIBUTIONS LIST:")
        contributions_by_type = {}
        
        async for contrib in contributions_collection.find().sort('created_at', -1):
            contrib_id = contrib.get('id', 'No ID')
            contrib_title = contrib.get('title', 'No Title')
            contrib_type = contrib.get('entity_type', 'Unknown Type')
            contrib_status = contrib.get('status', 'Unknown Status')
            created_at = contrib.get('created_at', 'Unknown Date')
            created_by = contrib.get('created_by', {})
            creator_name = created_by.get('name', 'Unknown User') if isinstance(created_by, dict) else str(created_by)
            
            # Group by type
            if contrib_type not in contributions_by_type:
                contributions_by_type[contrib_type] = []
            
            contributions_by_type[contrib_type].append({
                'id': contrib_id,
                'title': contrib_title,
                'status': contrib_status,
                'created_at': created_at,
                'creator': creator_name
            })
        
        # Display by type
        for entity_type, contribs in contributions_by_type.items():
            print(f"\n🏷️  {entity_type.upper()} ({len(contribs)} contributions):")
            for contrib in contribs:
                status_emoji = "⏳" if contrib['status'] == 'pending' else "✅" if contrib['status'] == 'approved' else "❌"
                print(f"   {status_emoji} {contrib['id']} - {contrib['title']}")
                print(f"       Status: {contrib['status']} | Creator: {contrib['creator']}")
                print(f"       Created: {contrib['created_at']}")
        
        print(f"\n📊 SUMMARY BY TYPE:")
        for entity_type, contribs in contributions_by_type.items():
            pending_count = sum(1 for c in contribs if c['status'] == 'pending')
            approved_count = sum(1 for c in contribs if c['status'] == 'approved')
            other_count = len(contribs) - pending_count - approved_count
            
            print(f"   {entity_type}: {len(contribs)} total (⏳ {pending_count} pending, ✅ {approved_count} approved, ❓ {other_count} other)")
        
    except Exception as e:
        print(f"❌ Error during listing: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(list_all_contributions())