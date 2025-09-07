#!/usr/bin/env python3
"""
Fix existing approved contributions by re-integrating them with proper image data
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import uuid

# Load environment variables from backend directory
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def integrate_approved_contribution_with_images(contribution_id: str, contribution: dict, user_id: str):
    """Re-integrate approved contribution data with proper image handling"""
    try:
        entity_type = contribution.get('entity_type')
        data = contribution.get('data', {})
        images = contribution.get('images', [])
        
        # Extract logo/image URL from contribution images (first image becomes logo)
        logo_url = ""
        if images and len(images) > 0:
            logo_url = images[0].get('url', '') if isinstance(images[0], dict) else str(images[0])
        
        # Get existing integrated entity
        existing_entity_id = contribution.get('integrated_entity_id')
        if not existing_entity_id:
            print(f"❌ Contribution {contribution_id} has no integrated entity ID")
            return False
        
        # Update existing entity with image data
        if entity_type == 'team':
            update_result = await db.teams.update_one(
                {"id": existing_entity_id},
                {"$set": {"logo_url": logo_url, "updated_at": datetime.utcnow()}}
            )
            if update_result.modified_count > 0:
                print(f"✅ Updated team {data.get('name')} with logo: {logo_url}")
                return True
                
        elif entity_type == 'brand':
            update_result = await db.brands.update_one(
                {"id": existing_entity_id},
                {"$set": {"logo_url": logo_url, "updated_at": datetime.utcnow()}}
            )
            if update_result.modified_count > 0:
                print(f"✅ Updated brand {data.get('name')} with logo: {logo_url}")
                return True
                
        elif entity_type == 'player':
            update_result = await db.players.update_one(
                {"id": existing_entity_id},
                {"$set": {"profile_picture_url": logo_url, "updated_at": datetime.utcnow()}}
            )
            if update_result.modified_count > 0:
                print(f"✅ Updated player {data.get('name')} with photo: {logo_url}")
                return True
                
        elif entity_type == 'competition':
            update_result = await db.competitions.update_one(
                {"id": existing_entity_id},
                {"$set": {"logo_url": logo_url, "updated_at": datetime.utcnow()}}
            )
            if update_result.modified_count > 0:
                print(f"✅ Updated competition {data.get('competition_name')} with logo: {logo_url}")
                return True
                
        elif entity_type == 'master_kit':
            update_result = await db.master_jerseys.update_one(
                {"id": existing_entity_id},
                {"$set": {"main_image_url": logo_url, "updated_at": datetime.utcnow()}}
            )
            if update_result.modified_count > 0:
                print(f"✅ Updated master kit with image: {logo_url}")
                return True
            
        elif entity_type == 'reference_kit':
            # For reference kits, extract multiple images
            product_images = []
            main_photo = logo_url
            secondary_photos = []
            
            for i, img in enumerate(images):
                img_url = img.get('url', '') if isinstance(img, dict) else str(img)
                if i == 0:
                    main_photo = img_url
                else:
                    secondary_photos.append(img_url)
                product_images.append(img_url)
            
            update_result = await db.reference_kits.update_one(
                {"id": existing_entity_id},
                {
                    "$set": {
                        "product_images": product_images,
                        "main_photo": main_photo,
                        "secondary_photos": secondary_photos,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            if update_result.modified_count > 0:
                print(f"✅ Updated reference kit with {len(product_images)} images")
                return True
        
        print(f"⚠️ No entity found to update for {entity_type} contribution {contribution_id}")
        return False
        
    except Exception as e:
        print(f"❌ Error updating contribution {contribution_id}: {e}")
        return False

async def fix_existing_contributions():
    """Fix all approved contributions that have images but missing image data in entities"""
    try:
        print("🔍 Finding approved contributions with images...")
        
        # Get all approved and integrated contributions that have images
        contributions = await db.contributions_v2.find({
            "status": "approved",
            "integrated": True,
            "images": {"$exists": True, "$ne": []},
            "integrated_entity_id": {"$exists": True, "$ne": None}
        }).to_list(1000)
        
        print(f"📊 Found {len(contributions)} approved contributions with images")
        
        if not contributions:
            print("✅ No contributions to fix")
            return
        
        fixed_count = 0
        for contrib in contributions:
            print(f"\n🔧 Processing contribution {contrib['topkit_reference']} ({contrib['entity_type']})")
            success = await integrate_approved_contribution_with_images(
                contrib['id'], 
                contrib, 
                contrib['created_by']
            )
            if success:
                fixed_count += 1
        
        print(f"\n🎉 Successfully fixed {fixed_count}/{len(contributions)} contributions!")
        
    except Exception as e:
        print(f"❌ Error fixing contributions: {e}")

if __name__ == "__main__":
    print("🚀 Starting image fix for existing approved contributions...")
    asyncio.run(fix_existing_contributions())
    print("✅ Image fix completed!")