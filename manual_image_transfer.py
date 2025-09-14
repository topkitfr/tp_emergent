#!/usr/bin/env python
"""
Manually trace through image transfer logic to debug
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import shutil
from datetime import datetime

async def manual_image_transfer():
    """Manually perform image transfer with debug output"""
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.topkit_db
    
    print("🔧 Manual Image Transfer Debug")
    print("=" * 40)
    
    # Get the contribution
    contrib = await db.contributions.find_one({'topkit_reference': 'TK-CONTRIB-5AC6A8'})
    entity_id = contrib['entity_id']
    entity_type = contrib['entity_type']
    
    print(f"Contribution: {contrib['topkit_reference']}")
    print(f"Entity ID: {entity_id}")
    print(f"Entity Type: {entity_type}")
    print()
    
    # Find all images associated with this contribution
    contribution_images = []
    
    # Check for uploaded images stored in contribution document
    if "uploaded_images" in contrib:
        for img_info in contrib["uploaded_images"]:
            field_name = img_info.get("field_name", "logo")
            file_path = img_info.get("file_path", "")
            if file_path:
                contribution_images.append((field_name, file_path))
                print(f"Found image: {field_name} -> {file_path}")
    
    if not contribution_images:
        print("❌ No images found")
        return
        
    # Get master kit
    master_kit = await db.master_kits.find_one({"id": entity_id})
    if not master_kit:
        print("❌ Master kit not found")
        return
        
    print(f"Master kit: {master_kit.get('topkit_reference')}")
    print(f"Current front_photo_url: {master_kit.get('front_photo_url')}")
    print()
    
    # Process each image
    for field_name, source_path in contribution_images:
        print(f"Processing image: {field_name} -> {source_path}")
        
        # Construct full source path
        if source_path.startswith("/"):
            full_source_path = source_path
        elif source_path.startswith("uploads/"):
            full_source_path = f"/app/backend/{source_path}"
        elif source_path.startswith("contributions/"):
            full_source_path = f"/app/backend/uploads/{source_path}"
        else:
            full_source_path = f"/app/backend/uploads/contributions/{source_path}"
        
        print(f"   Full source path: {full_source_path}")
        print(f"   Source exists: {os.path.exists(full_source_path)}")
        
        if not os.path.exists(full_source_path):
            print("   ❌ Source file not found, skipping")
            continue
            
        # Get the legacy filename from the entity's current front_photo_url
        legacy_filename = None
        if field_name in ["logo", "logo_url", "uploaded_file"] or field_name.endswith("_logo"):
            legacy_filename = master_kit.get("logo_url", "")
            print(f"   Field type: logo, looking for logo_url")
        elif field_name in ["photo", "photo_url", "primary_photo", "front_photo"]:
            if entity_type == "player":
                legacy_filename = master_kit.get("photo_url", "")
                print(f"   Field type: photo (player), looking for photo_url")
            elif entity_type == "master_kit":
                legacy_filename = master_kit.get("front_photo_url", "")
                print(f"   Field type: photo (master_kit), looking for front_photo_url")
        else:
            print(f"   ❌ Unknown field type: {field_name}")
            
        print(f"   Legacy filename: {legacy_filename}")
        
        if not legacy_filename or not legacy_filename.startswith("image_uploaded_"):
            print(f"   ❌ No valid legacy filename found")
            continue
            
        # Determine file extension from source file
        file_extension = os.path.splitext(source_path)[1] or '.png'
        
        # Create new filename using legacy name + extension
        new_filename = f"{legacy_filename}{file_extension}"
        target_path = f"/app/backend/uploads/master_kits/{new_filename}"
        
        print(f"   New filename: {new_filename}")
        print(f"   Target path: {target_path}")
        
        # Create target directory if it doesn't exist
        os.makedirs("/app/backend/uploads/master_kits", exist_ok=True)
        
        try:
            # Copy the file
            shutil.copy2(full_source_path, target_path)
            print(f"   ✅ File copied successfully")
            
            # Update master kit with new path
            new_url = f"uploads/master_kits/{new_filename}"
            result = await db.master_kits.update_one(
                {"id": entity_id},
                {"$set": {
                    "front_photo_url": new_url,
                    "last_modified_at": datetime.utcnow()
                }}
            )
            
            print(f"   ✅ Master kit updated: {result.modified_count} documents")
            print(f"   New URL: {new_url}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(manual_image_transfer())