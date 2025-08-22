#!/usr/bin/env python3
"""
Debug script to inspect the actual base64 image data stored in database
"""

import asyncio
import motor.motor_asyncio
import os

# MongoDB configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/topkit')

async def debug_image_data():
    """Debug the actual image data stored in entities"""
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.topkit
    
    print("🔍 DEBUGGING IMAGE DATA IN ENTITIES")
    print("=" * 50)
    
    # Check FC Barcelona specifically
    fc_barcelona = await db.teams.find_one({"name": {"$regex": "barcelona", "$options": "i"}})
    
    if fc_barcelona:
        print(f"📋 FC BARCELONA FOUND:")
        print(f"   Name: {fc_barcelona.get('name')}")
        print(f"   ID: {fc_barcelona.get('id')}")
        
        logo_url = fc_barcelona.get('logo_url')
        if logo_url:
            print(f"   Logo URL exists: {type(logo_url)}")
            if isinstance(logo_url, str):
                print(f"   Logo URL starts with: {logo_url[:50]}...")
                print(f"   Logo URL length: {len(logo_url)} characters")
                
                # Check if it's valid base64
                if logo_url.startswith('data:image/'):
                    print(f"   ✅ Valid data URL format")
                    # Extract the actual base64 part
                    if ',' in logo_url:
                        header, base64_part = logo_url.split(',', 1)
                        print(f"   Header: {header}")
                        print(f"   Base64 part length: {len(base64_part)}")
                        
                        # Try to decode base64
                        try:
                            import base64
                            decoded = base64.b64decode(base64_part)
                            print(f"   ✅ Valid base64 - decoded size: {len(decoded)} bytes")
                            
                            # Check if it's a valid image format
                            if decoded.startswith(b'\x89PNG'):
                                print(f"   ✅ Valid PNG image")
                            elif decoded.startswith(b'\xff\xd8\xff'):
                                print(f"   ✅ Valid JPEG image")
                            elif decoded.startswith(b'RIFF') and b'WEBP' in decoded[:20]:
                                print(f"   ✅ Valid WEBP image")
                            else:
                                print(f"   ❌ Unknown image format - first 20 bytes: {decoded[:20]}")
                        except Exception as e:
                            print(f"   ❌ Invalid base64: {str(e)}")
                    else:
                        print(f"   ❌ No comma found in data URL")
                else:
                    print(f"   ❌ Not a valid data URL format")
            else:
                print(f"   ❌ Logo URL is not a string: {logo_url}")
        else:
            print(f"   ❌ No logo_url field found")
    else:
        print("❌ FC Barcelona not found")
    
    print("\n" + "=" * 50)
    
    # Check all teams with logo_url
    teams_with_logos = await db.teams.find({"logo_url": {"$exists": True, "$ne": None}}).to_list(length=10)
    
    print(f"📊 TEAMS WITH LOGO_URL: {len(teams_with_logos)}")
    for i, team in enumerate(teams_with_logos):
        logo_url = team.get('logo_url')
        logo_status = "❌ Invalid"
        if isinstance(logo_url, str) and logo_url.startswith('data:image/'):
            logo_status = "✅ Valid"
        
        print(f"   {i+1}. {team.get('name')}: {logo_status}")
        if isinstance(logo_url, str):
            print(f"      Type: {type(logo_url)}, Length: {len(logo_url)}, Starts with: {logo_url[:30]}...")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_image_data())