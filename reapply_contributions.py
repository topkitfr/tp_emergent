#!/usr/bin/env python3
"""
Script to re-apply all approved contributions using the corrected logic
This will properly apply images from contributions to entities
"""

import asyncio
import motor.motor_asyncio
import os
from datetime import datetime

# MongoDB configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/topkit')

async def reapply_approved_contributions():
    """Re-apply all approved contributions with the corrected image logic"""
    
    # Connect to MongoDB
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client.topkit
    
    print("🔍 Searching for approved contributions to re-apply...")
    
    # Find all approved contributions
    approved_contributions = await db.contributions.find({"status": {"$in": ["approved", "auto_approved"]}}).to_list(length=None)
    
    print(f"📋 Found {len(approved_contributions)} approved contributions")
    
    if not approved_contributions:
        print("✅ No approved contributions found")
        return
    
    # Re-apply each contribution using the corrected logic
    applied_count = 0
    for contrib in approved_contributions:
        try:
            contrib_id = contrib['id']
            entity_type = contrib.get('entity_type')
            entity_id = contrib.get('entity_id')
            proposed_data = contrib.get('proposed_data', {})
            images = contrib.get('images', {})
            
            print(f"\n🔄 Re-applying contribution {contrib_id} ({entity_type})")
            
            if images:
                print(f"   Images found: {list(images.keys())}")
            
            # Apply the corrected logic
            success = await apply_contribution_corrected(db, contrib)
            if success:
                applied_count += 1
            else:
                print(f"   ❌ Failed to re-apply contribution")
                
        except Exception as e:
            print(f"❌ Error processing contribution {contrib_id}: {str(e)}")
    
    print(f"\n🎉 COMPLETED: {applied_count}/{len(approved_contributions)} contributions re-applied")
    
    # Close connection
    client.close()

async def apply_contribution_corrected(db, contribution):
    """Apply contribution using the corrected logic from server.py"""
    
    entity_type = contribution["entity_type"]
    entity_id = contribution["entity_id"]
    proposed_data = contribution.get("proposed_data", {})
    images = contribution.get("images", {})
    
    # Déterminer la collection MongoDB
    collection_map = {
        "team": "teams",
        "brand": "brands",
        "player": "players", 
        "competition": "competitions",
        "master_jersey": "master_jerseys"
    }
    
    collection_name = collection_map.get(entity_type)
    if not collection_name:
        print(f"⚠️ Unknown entity type: {entity_type}")
        return False
    
    collection = getattr(db, collection_name)
    
    try:
        # Préparer les données de mise à jour
        update_data = {
            **proposed_data,
            "last_modified_at": datetime.utcnow(),
            "last_modified_by": contribution["contributor_id"],
        }
        
        # CORRECTION: Appliquer les images de la contribution
        if images:
            print(f"🖼️ Applying images from contribution to {entity_type} {entity_id}")
            
            # Mapper les champs d'images selon le type d'entité
            if entity_type in ["team", "brand", "competition"]:
                # Pour teams, brands, competitions -> logo_url
                if "logo" in images:
                    # Gérer le cas où logo est une liste ou une chaîne
                    logo_data = images["logo"]
                    if isinstance(logo_data, list) and len(logo_data) > 0:
                        update_data["logo_url"] = logo_data[0]
                    elif isinstance(logo_data, str):
                        update_data["logo_url"] = logo_data
                
                # Gérer team_photos pour les équipes
                if entity_type == "team" and "team_photos" in images and "logo_url" not in update_data:
                    team_photos = images["team_photos"]
                    if isinstance(team_photos, list) and len(team_photos) > 0:
                        update_data["logo_url"] = team_photos[0]
            
            elif entity_type == "player":
                # Pour players -> photo_url
                if "photo" in images:
                    photo_data = images["photo"]
                    if isinstance(photo_data, list) and len(photo_data) > 0:
                        update_data["photo_url"] = photo_data[0]
                    elif isinstance(photo_data, str):
                        update_data["photo_url"] = photo_data
                elif "profile_photo" in images:
                    profile_data = images["profile_photo"]
                    if isinstance(profile_data, list) and len(profile_data) > 0:
                        update_data["photo_url"] = profile_data[0]
                    elif isinstance(profile_data, str):
                        update_data["photo_url"] = profile_data
            
            elif entity_type == "master_jersey":
                # Pour master jerseys -> front_photo_url, back_photo_url
                if "front_image" in images:
                    front_data = images["front_image"]
                    if isinstance(front_data, list) and len(front_data) > 0:
                        update_data["front_photo_url"] = front_data[0]
                    elif isinstance(front_data, str):
                        update_data["front_photo_url"] = front_data
                
                if "back_image" in images:
                    back_data = images["back_image"]
                    if isinstance(back_data, list) and len(back_data) > 0:
                        update_data["back_photo_url"] = back_data[0]
                    elif isinstance(back_data, str):
                        update_data["back_photo_url"] = back_data
            
            image_fields = [k for k in update_data.keys() if 'url' in k or 'photo' in k]
            if image_fields:
                print(f"✅ Image fields to apply: {image_fields}")
        
        # Mettre à jour l'entité avec les données proposées ET les images
        result = await collection.update_one(
            {"id": entity_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully re-applied contribution to {entity_type} {entity_id}")
            
            # Show what was updated
            for key, value in update_data.items():
                if 'url' in key or 'photo' in key:
                    print(f"   🖼️ {key}: Applied!")
                elif key not in ["last_modified_at", "last_modified_by"]:
                    print(f"   📝 {key}: {value}")
            
            return True
        else:
            print(f"⚠️ No changes applied to {entity_type} {entity_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error applying contribution to {entity_type} {entity_id}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting re-application of approved contributions with corrected logic...")
    asyncio.run(reapply_approved_contributions())
    print("✅ Re-application script completed!")