#!/usr/bin/env python
"""
Debug image transfer to understand what's failing
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient

async def debug_image_transfer():
    """Debug the image transfer process step by step"""
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.topkit_db
    
    print("🔍 Debugging Image Transfer Process")
    print("=" * 50)
    
    # Get a specific contribution that should have images
    contrib = await db.contributions.find_one({'topkit_reference': 'TK-CONTRIB-5AC6A8'})
    
    if not contrib:
        print("❌ Contribution not found")
        return
        
    print(f"✅ Found contribution: {contrib['topkit_reference']}")
    print(f"   Entity Type: {contrib['entity_type']}")
    print(f"   Entity ID: {contrib['entity_id']}")
    print(f"   Status: {contrib['status']}")
    print()
    
    # Check uploaded_images
    uploaded_images = contrib.get('uploaded_images', [])
    print(f"📁 Uploaded Images: {len(uploaded_images)}")
    for i, img in enumerate(uploaded_images):
        print(f"   {i+1}. Field: {img.get('field_name')}")
        print(f"      Path: {img.get('file_path')}")
        print(f"      Primary: {img.get('is_primary')}")
        
        # Check if file exists
        file_path = img.get('file_path', '')
        if file_path.startswith('uploads/'):
            full_path = f"/app/backend/{file_path}"
        else:
            full_path = f"/app/backend/uploads/contributions/{file_path}"
            
        exists = os.path.exists(full_path)
        print(f"      File exists: {exists} ({full_path})")
        
        if exists:
            file_size = os.path.getsize(full_path)
            print(f"      File size: {file_size} bytes")
        print()
    
    # Check master kit
    if contrib.get('entity_id'):
        master_kit = await db.master_kits.find_one({'id': contrib['entity_id']})
        if master_kit:
            print(f"🎯 Master Kit: {master_kit.get('topkit_reference')}")
            print(f"   Current front_photo_url: {master_kit.get('front_photo_url')}")
            
            # Check if front_photo_url file exists
            front_photo = master_kit.get('front_photo_url', '')
            if front_photo and not front_photo.startswith('image_uploaded_'):
                if front_photo.startswith('uploads/'):
                    master_path = f"/app/backend/{front_photo}"
                else:
                    master_path = f"/app/backend/uploads/master_kits/{front_photo}"
                    
                exists = os.path.exists(master_path)
                print(f"   Master kit image exists: {exists} ({master_path})")
            else:
                print(f"   Master kit has placeholder: {front_photo}")
        else:
            print("❌ Master kit not found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_image_transfer())