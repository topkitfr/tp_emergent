#!/usr/bin/env python3
"""
Script to apply contribution images to main entities
This will fix the image display issue in TopKit cards
"""

import asyncio
import motor.motor_asyncio
import os
import base64
import uuid
from datetime import datetime

# MongoDB configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/topkit')

async def apply_contribution_images():
    """Apply approved contribution images to main entities"""
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.topkit
    
    print("🔍 Searching for approved contributions with images...")
    
    # Find all approved contributions with images
    approved_contributions = await db.contributions.find({"status": "approved"}).to_list(length=None)
    
    contributions_with_images = []
    for contrib in approved_contributions:
        has_images = contrib.get('images')
        if has_images:
            contributions_with_images.append(contrib)
    
    print(f"📸 Found {len(contributions_with_images)} approved contributions with images")
    
    if not contributions_with_images:
        print("✅ No approved contributions with images found")
        return
    
    # Apply images to entities
    applied_count = 0
    for contrib in contributions_with_images:
        try:
            contrib_id = contrib['id']
            entity_type = contrib.get('entity_type')
            entity_id = contrib.get('entity_id')
            images = contrib.get('images', {})
            
            print(f"\n🔄 Processing contribution {contrib_id} ({entity_type})")
            print(f"   Images found: {list(images.keys())}")
            
            # Apply the images to the main entity
            success = await apply_images_to_entity(db, entity_type, entity_id, images)
            if success:
                applied_count += 1
                
        except Exception as e:
            print(f"❌ Error processing contribution {contrib_id}: {str(e)}")
    
    print(f"\n🎉 COMPLETED: {applied_count}/{len(contributions_with_images)} contributions processed")
    
    # Verify results by checking a few entities
    await verify_image_application(db)
    
    # Close connection
    client.close()

async def apply_images_to_entity(db, entity_type, entity_id, images):
    """Apply images to a specific entity"""
    
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
        # Prepare update data based on image types
        update_data = {}
        
        # Handle different image types
        for image_key, image_data in images.items():
            if image_key == 'logo' and image_data:
                # For logos, save as logo_url
                update_data['logo_url'] = image_data
            elif image_key == 'photo' and image_data:
                # For photos, save as photo_url
                update_data['photo_url'] = image_data
            elif image_key in ['test_image', 'secondary_photos']:
                # Skip test images and secondary photos for now
                continue
            else:
                # For any other image, try to apply it appropriately
                if entity_type in ['brand', 'team', 'competition']:
                    update_data['logo_url'] = image_data
                elif entity_type == 'player':
                    update_data['photo_url'] = image_data
                elif entity_type == 'master_jersey':
                    update_data['front_photo_url'] = image_data
        
        if update_data:
            result = await collection.update_one(
                {"id": entity_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ Applied images to {entity_type} {entity_id}")
                for key, value in update_data.items():
                    print(f"   🖼️ {key}: {value[:50]}...")
                return True
            else:
                print(f"⚠️ No changes applied to {entity_type} {entity_id}")
                return False
        else:
            print(f"⚠️ No valid images found for {entity_type} {entity_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error applying images to {entity_type} {entity_id}: {str(e)}")
        return False

async def verify_image_application(db):
    """Verify that images have been applied to entities"""
    
    print(f"\n🔍 VERIFICATION: Checking entities for applied images...")
    
    # Check teams for logo_url
    teams_with_images = await db.teams.find({"logo_url": {"$exists": True, "$ne": None}}).to_list(length=10)
    print(f"📊 Teams with logo_url: {len(teams_with_images)}")
    
    # Check brands for logo_url
    brands_with_images = await db.brands.find({"logo_url": {"$exists": True, "$ne": None}}).to_list(length=10)
    print(f"📊 Brands with logo_url: {len(brands_with_images)}")
    
    # Check competitions for logo_url
    competitions_with_images = await db.competitions.find({"logo_url": {"$exists": True, "$ne": None}}).to_list(length=10)
    print(f"📊 Competitions with logo_url: {len(competitions_with_images)}")
    
    # Check players for photo_url
    players_with_images = await db.players.find({"photo_url": {"$exists": True, "$ne": None}}).to_list(length=10)
    print(f"📊 Players with photo_url: {len(players_with_images)}")
    
    # Show examples
    if teams_with_images:
        team = teams_with_images[0]
        print(f"✅ Example team with image: {team.get('name')} has logo_url")
    
    if brands_with_images:
        brand = brands_with_images[0] 
        print(f"✅ Example brand with image: {brand.get('name')} has logo_url")

if __name__ == "__main__":
    print("🚀 Starting application of contribution images...")
    asyncio.run(apply_contribution_images())
    print("✅ Image application script completed!")