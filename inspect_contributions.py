#!/usr/bin/env python3
"""
Script to inspect the structure of contributions with images
"""

import asyncio
import motor.motor_asyncio
import os
import json

# MongoDB configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/topkit')

async def inspect_contributions():
    """Inspect the structure of contributions"""
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.topkit
    
    print("🔍 Inspecting contributions structure...")
    
    # Find all contributions
    contributions = await db.contributions.find({}).to_list(length=None)
    
    print(f"📊 Found {len(contributions)} total contributions")
    
    # Focus on contributions with images
    contributions_with_images = []
    for contrib in contributions:
        has_images = (
            contrib.get('images') or 
            contrib.get('logo') or 
            contrib.get('secondary_photos') or
            contrib.get('photo_url') or
            contrib.get('logo_url') or
            contrib.get('changes', {}).get('logo_url') or
            contrib.get('changes', {}).get('photo_url')
        )
        if has_images:
            contributions_with_images.append(contrib)
    
    print(f"📸 Found {len(contributions_with_images)} contributions with images")
    
    # Show structure of first few contributions with images
    for i, contrib in enumerate(contributions_with_images[:3]):
        print(f"\n📋 CONTRIBUTION {i+1}:")
        print(f"   ID: {contrib.get('id')}")
        print(f"   Entity Type: {contrib.get('entity_type')}")
        print(f"   Entity ID: {contrib.get('entity_id')}")
        print(f"   Status: {contrib.get('status')}")
        print(f"   Vote Score: {contrib.get('vote_score', 0)}")
        
        # Show image-related fields
        print("   📸 Image fields:")
        for field in ['images', 'logo', 'logo_url', 'photo_url', 'secondary_photos']:
            if contrib.get(field):
                print(f"      {field}: {contrib[field]}")
        
        # Show changes
        changes = contrib.get('changes', {})
        if changes:
            print("   🔄 Changes:")
            for key, value in changes.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"      {key}: {value[:100]}...")
                else:
                    print(f"      {key}: {value}")
        else:
            print("   🔄 Changes: None")
        
        print("   " + "="*50)
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_contributions())