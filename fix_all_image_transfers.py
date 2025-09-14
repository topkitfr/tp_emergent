#!/usr/bin/env python
"""
Fix all existing contributions that have images but weren't transferred properly
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import shutil
from datetime import datetime

async def fix_all_image_transfers():
    """Fix image transfers for all contributions that need it"""
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.topkit_db
    
    print("🔧 Fixing All Image Transfers")
    print("=" * 40)
    
    # Find contributions with uploaded_images but placeholder front_photo_url in master_kits
    contribs = await db.contributions.find({
        "entity_type": "master_kit",
        "status": "approved",
        "uploaded_images": {"$exists": True, "$ne": []}
    }).to_list(length=None)
    
    print(f"Found {len(contribs)} contributions with uploaded images")
    fixed_count = 0
    
    for contrib in contribs:
        contrib_ref = contrib.get('topkit_reference', 'Unknown')
        entity_id = contrib.get('entity_id')
        
        if not entity_id:
            continue
            
        # Check if master_kit has placeholder front_photo_url
        master_kit = await db.master_kits.find_one({'id': entity_id})
        if not master_kit:
            continue
            
        front_photo_url = master_kit.get('front_photo_url', '')
        if not front_photo_url or not front_photo_url.startswith('image_uploaded_'):
            print(f"✅ {contrib_ref}: Already has real image path")
            continue
            
        print(f"🔄 {contrib_ref}: Fixing image transfer...")
        
        # Process uploaded images
        success = False
        for img_info in contrib.get("uploaded_images", []):
            field_name = img_info.get("field_name", "logo")
            source_path = img_info.get("file_path", "")
            
            if not source_path:
                continue
                
            # Construct full source path
            if source_path.startswith("uploads/"):
                full_source_path = f"/app/backend/{source_path}"
            else:
                full_source_path = f"/app/backend/uploads/contributions/{source_path}"
            
            if not os.path.exists(full_source_path):
                print(f"   ⚠️  Source file not found: {full_source_path}")
                continue
                
            # Get legacy filename and create target path
            legacy_filename = master_kit.get("front_photo_url", "")
            if not legacy_filename.startswith("image_uploaded_"):
                continue
                
            file_extension = os.path.splitext(source_path)[1] or '.jpg'
            new_filename = f"{legacy_filename}{file_extension}"
            target_path = f"/app/backend/uploads/master_kits/{new_filename}"
            
            try:
                # Create target directory
                os.makedirs("/app/backend/uploads/master_kits", exist_ok=True)
                
                # Copy the file
                shutil.copy2(full_source_path, target_path)
                
                # Update master kit
                new_url = f"uploads/master_kits/{new_filename}"
                result = await db.master_kits.update_one(
                    {"id": entity_id},
                    {"$set": {
                        "front_photo_url": new_url,
                        "last_modified_at": datetime.utcnow()
                    }}
                )
                
                if result.modified_count > 0:
                    print(f"   ✅ SUCCESS: {new_url}")
                    success = True
                    break
                else:
                    print(f"   ❌ Failed to update database")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        if success:
            fixed_count += 1
    
    print(f"\n🎯 Fixed {fixed_count} master kits with images!")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_all_image_transfers())