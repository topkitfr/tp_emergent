#!/usr/bin/env python3
"""
Upload real images from the provided URLs to replace test placeholders
"""

import asyncio
import motor.motor_asyncio
import os
import requests
import base64

# MongoDB configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/topkit')

# Real images provided by user
REAL_IMAGES = {
    "fc_barcelona_logo": "https://customer-assets.emergentagent.com/job_topkit-vestiaire/artifacts/cw0jhuka_Logo_FC_Barcelona.svg.png",
    "nike_logo": "https://customer-assets.emergentagent.com/job_team-jersey-hub/artifacts/svh03ry5_nike-logo-8.png",
    "messi_photo": "https://customer-assets.emergentagent.com/job_team-jersey-hub/artifacts/m2yol13t_28003-1740766555.jpg",
    "laliga_logo": "https://customer-assets.emergentagent.com/job_team-jersey-hub/artifacts/du7rlyi4_LaLiga-Logo-PNG-Official-Symbol-for-Football-League-Transparent-jpg.webp",
    "barcelona_jersey": "https://customer-assets.emergentagent.com/job_team-jersey-hub/artifacts/50rtfe96_Maillot-Barca-Domicile-2024-2025-New-Sponsor.jpg"
}

async def upload_real_images():
    """Replace test images with real images from provided URLs"""
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.topkit
    
    print("🖼️ UPLOADING REAL IMAGES TO REPLACE TEST PLACEHOLDERS")
    print("=" * 60)
    
    # Download and convert images to base64
    converted_images = {}
    
    for image_key, url in REAL_IMAGES.items():
        try:
            print(f"\n📥 Downloading {image_key} from URL...")
            response = requests.get(url)
            
            if response.status_code == 200:
                # Detect content type
                content_type = response.headers.get('content-type', '')
                if 'png' in content_type.lower():
                    mime_type = 'image/png'
                elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
                    mime_type = 'image/jpeg'
                elif 'webp' in content_type.lower():
                    mime_type = 'image/webp'
                else:
                    # Detect from URL extension
                    if url.endswith('.png'):
                        mime_type = 'image/png'
                    elif url.endswith('.jpg') or url.endswith('.jpeg'):
                        mime_type = 'image/jpeg'
                    elif url.endswith('.webp'):
                        mime_type = 'image/webp'
                    else:
                        mime_type = 'image/png'  # default
                
                # Convert to base64
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                data_url = f"data:{mime_type};base64,{image_base64}"
                
                converted_images[image_key] = data_url
                
                print(f"   ✅ {image_key} converted successfully")
                print(f"      Size: {len(response.content)} bytes")
                print(f"      MIME type: {mime_type}")
                print(f"      Base64 length: {len(data_url)} characters")
            else:
                print(f"   ❌ Failed to download {image_key}: HTTP {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error downloading {image_key}: {str(e)}")
    
    print(f"\n📊 Successfully converted {len(converted_images)}/{len(REAL_IMAGES)} images")
    
    # Apply images to specific entities
    updates_made = 0
    
    # 1. FC Barcelona Logo
    if 'fc_barcelona_logo' in converted_images:
        result = await db.teams.update_one(
            {"name": {"$regex": "barcelona", "$options": "i"}},
            {"$set": {"logo_url": converted_images['fc_barcelona_logo']}}
        )
        if result.modified_count > 0:
            print(f"✅ FC Barcelona logo updated")
            updates_made += 1
    
    # 2. Nike Brand Logo  
    if 'nike_logo' in converted_images:
        result = await db.brands.update_one(
            {"name": {"$regex": "nike", "$options": "i"}},
            {"$set": {"logo_url": converted_images['nike_logo']}}
        )
        if result.modified_count > 0:
            print(f"✅ Nike brand logo updated")
            updates_made += 1
    
    # 3. Lionel Messi Photo
    if 'messi_photo' in converted_images:
        result = await db.players.update_one(
            {"name": {"$regex": "messi", "$options": "i"}},
            {"$set": {"photo_url": converted_images['messi_photo']}}
        )
        if result.modified_count > 0:
            print(f"✅ Lionel Messi photo updated")
            updates_made += 1
    
    # 4. La Liga Competition Logo
    if 'laliga_logo' in converted_images:
        result = await db.competitions.update_one(
            {"name": {"$regex": "la liga", "$options": "i"}},
            {"$set": {"logo_url": converted_images['laliga_logo']}}
        )
        if result.modified_count > 0:
            print(f"✅ La Liga logo updated")
            updates_made += 1
    
    # 5. Barcelona Master Jersey
    if 'barcelona_jersey' in converted_images:
        result = await db.master_jerseys.update_one(
            {"team_info.name": {"$regex": "barcelona", "$options": "i"}},
            {"$set": {"front_photo_url": converted_images['barcelona_jersey']}}
        )
        if result.modified_count > 0:
            print(f"✅ Barcelona master jersey updated")
            updates_made += 1
    
    print(f"\n🎉 COMPLETED: {updates_made} entities updated with real images")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    print("🚀 Starting real image upload process...")
    asyncio.run(upload_real_images())
    print("✅ Real image upload completed!")