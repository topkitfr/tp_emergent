#!/usr/bin/env python3
"""
Script to manually approve all pending contributions with images
This will fix the image display issue in TopKit cards
"""

import asyncio
import motor.motor_asyncio
import os
from datetime import datetime

# MongoDB configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/topkit')

async def approve_contributions_with_images():
    """Approve all pending contributions that have images"""
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.topkit
    
    print("🔍 Searching for pending contributions with images...")
    
    # Find all pending contributions with images
    pending_contributions = await db.contributions.find({"status": "pending"}).to_list(length=None)
    
    contributions_with_images = []
    for contrib in pending_contributions:
        has_images = (
            contrib.get('images') or 
            contrib.get('logo') or 
            contrib.get('secondary_photos') or
            contrib.get('photo_url') or
            contrib.get('logo_url')
        )
        if has_images:
            contributions_with_images.append(contrib)
    
    print(f"📸 Found {len(contributions_with_images)} pending contributions with images")
    
    if not contributions_with_images:
        print("✅ No pending contributions with images found")
        return
    
    # Approve each contribution with images
    approved_count = 0
    for contrib in contributions_with_images:
        try:
            contrib_id = contrib['id']
            entity_type = contrib.get('entity_type')
            entity_id = contrib.get('entity_id')
            
            print(f"\n🔄 Processing contribution {contrib_id} ({entity_type})")
            
            # Mark contribution as approved
            result = await db.contributions.update_one(
                {"id": contrib_id},
                {"$set": {
                    "status": "approved",
                    "reviewed_at": datetime.utcnow(),
                    "moderator_notes": "Auto-approved for image display fix",
                    "vote_score": 3  # Set score to trigger approval logic
                }}
            )
            
            if result.modified_count > 0:
                print(f"✅ Contribution {contrib_id} marked as approved")
                
                # Apply the changes to the main entity
                await apply_contribution_to_entity(db, contrib)
                approved_count += 1
            else:
                print(f"❌ Failed to approve contribution {contrib_id}")
                
        except Exception as e:
            print(f"❌ Error processing contribution {contrib_id}: {str(e)}")
    
    print(f"\n🎉 COMPLETED: {approved_count}/{len(contributions_with_images)} contributions approved")
    
    # Close connection
    client.close()

async def apply_contribution_to_entity(db, contribution):
    """Apply approved contribution changes to the main entity"""
    
    entity_type = contribution.get('entity_type')
    entity_id = contribution.get('entity_id')
    changes = contribution.get('changes', {})
    
    if not entity_type or not entity_id:
        print(f"⚠️ Missing entity_type or entity_id in contribution")
        return False
    
    # Map entity types to collections
    collection_map = {
        'team': 'teams',
        'brand': 'brands',
        'competition': 'competitions', 
        'player': 'players',
        'master_jersey': 'master_jerseys'
    }
    
    collection_name = collection_map.get(entity_type)
    if not collection_name:
        print(f"⚠️ Unknown entity type: {entity_type}")
        return False
    
    collection = getattr(db, collection_name)
    
    try:
        # Prepare update data from contribution changes
        update_data = {}
        
        # Handle image fields specifically
        image_fields = ['logo', 'logo_url', 'photo_url', 'images', 'secondary_photos']
        for field in image_fields:
            if field in changes and changes[field]:
                if field == 'logo' and 'logo_url' not in update_data:
                    update_data['logo_url'] = changes[field]
                elif field in ['photo_url', 'logo_url', 'images']:
                    update_data[field] = changes[field]
        
        # Handle other changes
        for key, value in changes.items():
            if key not in image_fields and value is not None:
                update_data[key] = value
        
        if update_data:
            result = await collection.update_one(
                {"id": entity_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ Applied changes to {entity_type} {entity_id}")
                
                # Show what was updated
                for key, value in update_data.items():
                    if 'url' in key or 'photo' in key or 'image' in key:
                        print(f"   🖼️ {key}: {value[:50]}...")
                    else:
                        print(f"   📝 {key}: {value}")
                        
                return True
            else:
                print(f"⚠️ No changes applied to {entity_type} {entity_id}")
                return False
        else:
            print(f"⚠️ No update data found for {entity_type} {entity_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error applying changes to {entity_type} {entity_id}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting approval of pending contributions with images...")
    asyncio.run(approve_contributions_with_images())
    print("✅ Approval script completed!")