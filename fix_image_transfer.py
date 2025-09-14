#!/usr/bin/env python
"""
Fix image transfer for existing contributions that have images but weren't transferred
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from server import transfer_contribution_images_to_entity

async def fix_image_transfers():
    """Fix image transfers for contributions with uploaded images"""
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.topkit_db
    
    print("🔧 Fixing Image Transfers for Existing Contributions")
    print("=" * 60)
    
    # Find contributions with uploaded_images but placeholder front_photo_url in master_kits
    contribs = await db.contributions.find({
        "entity_type": "master_kit",
        "status": "approved",
        "uploaded_images": {"$exists": True, "$ne": []}
    }).to_list(length=None)
    
    print(f"Found {len(contribs)} contributions with uploaded images")
    
    for contrib in contribs:
        contrib_ref = contrib.get('topkit_reference', 'Unknown')
        entity_id = contrib.get('entity_id')
        
        if not entity_id:
            print(f"⚠️  {contrib_ref}: No entity_id")
            continue
            
        # Check if master_kit has placeholder front_photo_url
        master_kit = await db.master_kits.find_one({'id': entity_id})
        if not master_kit:
            print(f"⚠️  {contrib_ref}: Master kit not found")
            continue
            
        front_photo_url = master_kit.get('front_photo_url', '')
        if front_photo_url and front_photo_url.startswith('image_uploaded_'):
            print(f"🔄 {contrib_ref}: Fixing image transfer...")
            print(f"   Current front_photo_url: {front_photo_url}")
            print(f"   Images to transfer: {len(contrib.get('uploaded_images', []))}")
            
            # Trigger image transfer
            success = await transfer_contribution_images_to_entity(contrib, entity_id)
            
            if success:
                # Check result
                updated_master_kit = await db.master_kits.find_one({'id': entity_id})
                new_front_photo_url = updated_master_kit.get('front_photo_url', '')
                
                if new_front_photo_url != front_photo_url:
                    print(f"   ✅ SUCCESS: Updated to {new_front_photo_url}")
                else:
                    print(f"   ❌ FAILED: Still {front_photo_url}")
            else:
                print(f"   ❌ FAILED: transfer_contribution_images_to_entity returned False")
        else:
            print(f"✅ {contrib_ref}: Already has real image path ({front_photo_url})")
        print()
    
    client.close()
    print("🎯 Image transfer fix completed!")

if __name__ == "__main__":
    asyncio.run(fix_image_transfers())