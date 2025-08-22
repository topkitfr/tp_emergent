#!/usr/bin/env python3
"""
Apply images from approved contributions to main entities
This script will process all approved contributions and apply their images to the corresponding entities
"""

import os
import pymongo
from datetime import datetime
from urllib.parse import quote_plus

def main():
    # Get MongoDB connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/topkit')
    client = pymongo.MongoClient(mongo_url)
    db = client.get_default_database()
    
    print("🖼️ APPLYING IMAGES FROM APPROVED CONTRIBUTIONS")
    print("=" * 60)
    
    # Find all approved contributions with images
    approved_contributions = list(db.contributions.find({
        'status': {'$in': ['approved', 'auto_approved']},
        '$or': [
            {'images': {'$ne': None, '$exists': True}},
            {'logo': {'$ne': None, '$exists': True}},
            {'secondary_photos': {'$ne': None, '$exists': True}}
        ]
    }))
    
    print(f"Found {len(approved_contributions)} approved contributions with images")
    
    applied_count = 0
    
    for i, contribution in enumerate(approved_contributions):
        print(f"\n--- Processing Contribution {i+1}/{len(approved_contributions)} ---")
        contribution_id = contribution['id']
        entity_type = contribution['entity_type']
        entity_id = contribution['entity_id']
        
        print(f"Contribution ID: {contribution_id}")
        print(f"Entity Type: {entity_type}")
        print(f"Entity ID: {entity_id}")
        
        # Get images from contribution
        images = contribution.get('images', {})
        if not images:
            # Try legacy fields
            if 'logo' in contribution and contribution['logo']:
                images['logo'] = contribution['logo']
            if 'secondary_photos' in contribution and contribution['secondary_photos']:
                images['secondary_photos'] = contribution['secondary_photos']
        
        if not images:
            print("⚠️ No images found in contribution")
            continue
        
        print(f"Images keys: {list(images.keys())}")
        
        # Determine the collection
        collection_map = {
            "team": "teams",
            "brand": "brands", 
            "player": "players",
            "competition": "competitions",
            "master_jersey": "master_jerseys"
        }
        
        collection_name = collection_map.get(entity_type)
        if not collection_name:
            print(f"❌ Unknown entity type: {entity_type}")
            continue
        
        # Find the entity
        entity = db[collection_name].find_one({"id": entity_id})
        if not entity:
            print(f"❌ Entity not found: {entity_type} {entity_id}")
            continue
        
        print(f"Entity found: {entity.get('name', 'Unknown')}")
        
        # Prepare update data
        update_data = {}
        
        # Map images to correct fields based on entity type
        if entity_type in ["team", "brand", "competition"]:
            # For teams, brands, competitions -> logo_url
            if "logo" in images:
                logo_data = images["logo"]
                if isinstance(logo_data, list) and len(logo_data) > 0:
                    update_data["logo_url"] = logo_data[0]
                elif isinstance(logo_data, str):
                    update_data["logo_url"] = logo_data
                print(f"✅ Setting logo_url from 'logo' field")
            
            # Handle team_photos for teams
            if entity_type == "team" and "team_photos" in images and "logo_url" not in update_data:
                team_photos = images["team_photos"]
                if isinstance(team_photos, list) and len(team_photos) > 0:
                    update_data["logo_url"] = team_photos[0]
                elif isinstance(team_photos, str):
                    update_data["logo_url"] = team_photos
                print(f"✅ Setting logo_url from 'team_photos' field")
            
            # Handle test_image or other generic image fields
            if "logo_url" not in update_data:
                for key, value in images.items():
                    if key in ['test_image', 'banner', 'image']:
                        if isinstance(value, list) and len(value) > 0:
                            update_data["logo_url"] = value[0]
                        elif isinstance(value, str):
                            update_data["logo_url"] = value
                        print(f"✅ Setting logo_url from '{key}' field")
                        break
        
        elif entity_type == "player":
            # For players -> photo_url
            if "photo" in images:
                photo_data = images["photo"]
                if isinstance(photo_data, list) and len(photo_data) > 0:
                    update_data["photo_url"] = photo_data[0]
                elif isinstance(photo_data, str):
                    update_data["photo_url"] = photo_data
                print(f"✅ Setting photo_url from 'photo' field")
            elif "profile_photo" in images:
                profile_data = images["profile_photo"]
                if isinstance(profile_data, list) and len(profile_data) > 0:
                    update_data["photo_url"] = profile_data[0]
                elif isinstance(profile_data, str):
                    update_data["photo_url"] = profile_data
                print(f"✅ Setting photo_url from 'profile_photo' field")
        
        elif entity_type == "master_jersey":
            # For master jerseys -> front_photo_url, back_photo_url
            if "front_image" in images:
                front_data = images["front_image"]
                if isinstance(front_data, list) and len(front_data) > 0:
                    update_data["front_photo_url"] = front_data[0]
                elif isinstance(front_data, str):
                    update_data["front_photo_url"] = front_data
                print(f"✅ Setting front_photo_url")
            
            if "back_image" in images:
                back_data = images["back_image"]
                if isinstance(back_data, list) and len(back_data) > 0:
                    update_data["back_photo_url"] = back_data[0]
                elif isinstance(back_data, str):
                    update_data["back_photo_url"] = back_data
                print(f"✅ Setting back_photo_url")
        
        if not update_data:
            print("⚠️ No image fields to update")
            continue
        
        # Add metadata
        update_data.update({
            "last_modified_at": datetime.utcnow(),
            "last_modified_by": contribution.get("contributor_id", "system"),
            "images_applied_from_contribution": contribution_id
        })
        
        print(f"Update fields: {list(update_data.keys())}")
        
        # Apply the update
        try:
            result = db[collection_name].update_one(
                {"id": entity_id},
                {"$set": update_data}
            )
        except Exception as e:
            print(f"❌ Update error: {e}")
            continue
        
        if result.modified_count > 0:
            print(f"✅ Successfully applied images to {entity_type} {entity_id}")
            applied_count += 1
        else:
            print(f"⚠️ No changes applied to {entity_type} {entity_id}")
    
    print(f"\n🎉 COMPLETED! Applied images to {applied_count}/{len(approved_contributions)} entities")
    
    # Show summary
    print("\n📊 SUMMARY OF ENTITIES WITH IMAGES:")
    for entity_type, collection_name in collection_map.items():
        image_field = "logo_url"
        if entity_type == "player":
            image_field = "photo_url" 
        elif entity_type == "master_jersey":
            image_field = "front_photo_url"
        
        count = db[collection_name].count_documents({image_field: {"$ne": None, "$exists": True}})
        print(f"- {entity_type.capitalize()}s with images: {count}")
    
    client.close()

if __name__ == "__main__":
    main()