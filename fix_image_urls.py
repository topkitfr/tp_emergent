#!/usr/bin/env python3
"""
Fix existing image URLs to include /api prefix
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from backend directory
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def fix_image_urls():
    print('🔧 Fixing existing image URLs to include /api prefix...')
    
    # Update teams
    teams = await db.teams.find({'logo_url': {'$regex': '^uploads/'}}).to_list(1000)
    for team in teams:
        new_logo_url = f"api/{team['logo_url']}"
        await db.teams.update_one(
            {'id': team['id']},
            {'$set': {'logo_url': new_logo_url}}
        )
        print(f'✅ Updated team {team["name"]} logo URL to {new_logo_url}')
    
    # Update brands
    brands = await db.brands.find({'logo_url': {'$regex': '^uploads/'}}).to_list(1000)
    for brand in brands:
        new_logo_url = f"api/{brand['logo_url']}"
        await db.brands.update_one(
            {'id': brand['id']},
            {'$set': {'logo_url': new_logo_url}}
        )
        print(f'✅ Updated brand {brand["name"]} logo URL to {new_logo_url}')
    
    # Update players
    players = await db.players.find({'profile_picture_url': {'$regex': '^uploads/'}}).to_list(1000)
    for player in players:
        new_pic_url = f"api/{player['profile_picture_url']}"
        await db.players.update_one(
            {'id': player['id']},
            {'$set': {'profile_picture_url': new_pic_url}}
        )
        print(f'✅ Updated player {player["name"]} picture URL to {new_pic_url}')
    
    # Update competitions
    competitions = await db.competitions.find({'logo_url': {'$regex': '^uploads/'}}).to_list(1000)
    for comp in competitions:
        new_logo_url = f"api/{comp['logo_url']}"
        await db.competitions.update_one(
            {'id': comp['id']},
            {'$set': {'logo_url': new_logo_url}}
        )
        print(f'✅ Updated competition {comp["competition_name"]} logo URL to {new_logo_url}')
    
    # Update master jerseys
    master_jerseys = await db.master_jerseys.find({'main_image_url': {'$regex': '^uploads/'}}).to_list(1000)
    for jersey in master_jerseys:
        new_image_url = f"api/{jersey['main_image_url']}"
        await db.master_jerseys.update_one(
            {'id': jersey['id']},
            {'$set': {'main_image_url': new_image_url}}
        )
        print(f'✅ Updated master jersey {jersey.get("season", "unknown")} image URL to {new_image_url}')
    
    # Update reference kits
    reference_kits = await db.reference_kits.find({
        '$or': [
            {'main_photo': {'$regex': '^uploads/'}},
            {'product_images': {'$regex': '^uploads/'}}
        ]
    }).to_list(1000)
    for kit in reference_kits:
        update_data = {}
        if kit.get('main_photo', '').startswith('uploads/'):
            update_data['main_photo'] = f"api/{kit['main_photo']}"
        
        if kit.get('product_images'):
            updated_images = []
            for img in kit['product_images']:
                if img.startswith('uploads/'):
                    updated_images.append(f"api/{img}")
                else:
                    updated_images.append(img)
            update_data['product_images'] = updated_images
        
        if kit.get('secondary_photos'):
            updated_secondary = []
            for img in kit['secondary_photos']:
                if img.startswith('uploads/'):
                    updated_secondary.append(f"api/{img}")
                else:
                    updated_secondary.append(img)
            update_data['secondary_photos'] = updated_secondary
        
        if update_data:
            await db.reference_kits.update_one(
                {'id': kit['id']},
                {'$set': update_data}
            )
            print(f'✅ Updated reference kit {kit.get("model_name", "unknown")} image URLs')
    
    print('✅ All image URLs updated with /api prefix!')

if __name__ == "__main__":
    asyncio.run(fix_image_urls())