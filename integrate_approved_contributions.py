#!/usr/bin/env python3
"""
Integration system to move approved V2 contributions to main catalogue
This creates the bridge between the community submission system and the main catalogue
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('backend/.env')
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def integrate_approved_contributions():
    """
    Move approved contributions from contributions_v2 to main entity collections
    and create proper references in the catalogue system
    """
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Starting integration of approved contributions...")
    
    # Get all approved contributions that haven't been integrated yet
    approved_contributions = await db.contributions_v2.find({
        "status": "approved",
        "integrated": {"$ne": True}  # Not yet integrated
    }).to_list(None)
    
    print(f"Found {len(approved_contributions)} approved contributions to integrate")
    
    integrated_count = 0
    
    for contrib in approved_contributions:
        try:
            entity_type = contrib.get('entity_type')
            data = contrib.get('data', {})
            contrib_id = contrib.get('id')
            
            print(f"\n📝 Integrating {entity_type}: {contrib.get('title')}")
            
            # Generate new entity ID
            entity_id = str(uuid.uuid4())
            
            # Prepare common fields
            common_fields = {
                "id": entity_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "verified_level": "community_verified",
                "verified_at": contrib.get('reviewed_at', datetime.utcnow()),
                "verified_by": contrib.get('reviewed_by'),
                "source_contribution_id": contrib_id,
                "topkit_reference": contrib.get('topkit_reference')
            }
            
            # Process different entity types
            if entity_type == 'team':
                team_doc = {
                    **common_fields,
                    "name": data.get('name'),
                    "country": data.get('country'),
                    "city": data.get('city', ''),
                    "founded_year": data.get('founded_year'),
                    "short_name": data.get('short_name', ''),
                    "official_name": data.get('official_name', ''),
                    "alternative_names": data.get('alternative_names', []),
                    "colors": data.get('colors', []),
                    "logo_url": data.get('logo_url', ''),
                    "stadium": data.get('stadium', ''),
                    "league_info": data.get('league_info', {}),
                    "current_competitions": data.get('current_competitions', []),
                    "primary_competition_id": data.get('primary_competition_id', '')
                }
                
                result = await db.teams.insert_one(team_doc)
                print(f"✅ Created team: {data.get('name')} (ID: {entity_id})")
                
            elif entity_type == 'brand':
                brand_doc = {
                    **common_fields,
                    "name": data.get('name'),
                    "official_name": data.get('official_name', ''),
                    "country": data.get('country'),
                    "founded_year": data.get('founded_year'),
                    "website": data.get('website', ''),
                    "alternative_names": data.get('alternative_names', []),
                    "logo_url": data.get('logo_url', ''),
                    "description": data.get('description', '')
                }
                
                result = await db.brands.insert_one(brand_doc)
                print(f"✅ Created brand: {data.get('name')} (ID: {entity_id})")
                
            elif entity_type == 'player':
                player_doc = {
                    **common_fields,
                    "name": data.get('name'),
                    "common_name": data.get('common_name', ''),
                    "nationality": data.get('nationality'),
                    "birth_date": data.get('birth_date', ''),
                    "position": data.get('position', ''),
                    "current_team": data.get('current_team', ''),
                    "jersey_number": data.get('jersey_number'),
                    "alternative_names": data.get('alternative_names', []),
                    "height": data.get('height', ''),
                    "weight": data.get('weight', ''),
                    "foot": data.get('foot', ''),
                    "market_value": data.get('market_value', ''),
                    "profile_picture_url": data.get('profile_picture_url', '')
                }
                
                result = await db.players.insert_one(player_doc)
                print(f"✅ Created player: {data.get('name')} (ID: {entity_id})")
                
            elif entity_type == 'competition':
                competition_doc = {
                    **common_fields,
                    "competition_name": data.get('competition_name'),
                    "official_name": data.get('official_name', ''),
                    "type": data.get('type'),
                    "country": data.get('country'),
                    "level": data.get('level', 1),
                    "confederations_federations": data.get('confederations_federations', []),
                    "alternative_names": data.get('alternative_names', []),
                    "season_format": data.get('season_format', ''),
                    "current_season": data.get('current_season', ''),
                    "logo_url": data.get('logo_url', '')
                }
                
                result = await db.competitions.insert_one(competition_doc)
                print(f"✅ Created competition: {data.get('competition_name')} (ID: {entity_id})")
                
            elif entity_type == 'master_kit':
                # For master kits, we need to create both master_jerseys and potentially reference_kits
                master_jersey_doc = {
                    **common_fields,
                    "team_id": data.get('team_id', ''),
                    "brand_id": data.get('brand_id', ''),
                    "season": data.get('season'),
                    "jersey_type": data.get('jersey_type', 'home'),
                    "model": data.get('model', ''),
                    "primary_color": data.get('primary_color', ''),
                    "secondary_colors": data.get('secondary_colors', []),
                    "pattern": data.get('pattern', ''),
                    "main_image_url": data.get('main_image_url', ''),
                    "additional_images": data.get('additional_images', []),
                    "description": data.get('description', ''),
                    "material": data.get('material', ''),
                    "manufacturer_code": data.get('manufacturer_code', ''),
                    "release_date": data.get('release_date', ''),
                    "discontinued_date": data.get('discontinued_date', '')
                }
                
                result = await db.master_jerseys.insert_one(master_jersey_doc)
                print(f"✅ Created master jersey: {data.get('season')} {data.get('jersey_type')} (ID: {entity_id})")
                
            elif entity_type == 'reference_kit':
                # For reference kits, create in reference_kits collection for Kit Store
                reference_kit_doc = {
                    **common_fields,
                    "master_kit_id": data.get('master_kit_id', ''),
                    "model_name": data.get('model_name', ''),
                    "release_type": data.get('release_type', 'replica'),
                    "original_retail_price": data.get('original_retail_price', 0.0),
                    "current_market_price": data.get('current_market_price', 0.0),
                    "release_date": data.get('release_date', ''),
                    "sku_code": data.get('sku_code', ''),
                    "barcode": data.get('barcode', ''),
                    "is_limited_edition": data.get('is_limited_edition', False),
                    "production_run": data.get('production_run', None),
                    "league_competition": data.get('league_competition', ''),
                    "product_images": data.get('product_images', []),
                    "main_photo": data.get('main_photo', ''),
                    "secondary_photos": data.get('secondary_photos', []),
                    "description": data.get('description', ''),
                    "sizes_available": data.get('sizes_available', []),
                    "material_composition": data.get('material_composition', ''),
                    "care_instructions": data.get('care_instructions', ''),
                    "authenticity_features": data.get('authenticity_features', [])
                }
                
                result = await db.reference_kits.insert_one(reference_kit_doc)
                print(f"✅ Created reference kit: {data.get('model_name')} {data.get('release_type')} (ID: {entity_id})")
            
            # Mark contribution as integrated
            await db.contributions_v2.update_one(
                {"id": contrib_id},
                {
                    "$set": {
                        "integrated": True,
                        "integrated_at": datetime.utcnow(),
                        "integrated_entity_id": entity_id,
                        "integrated_entity_type": entity_type
                    }
                }
            )
            
            integrated_count += 1
            
        except Exception as e:
            print(f"❌ Error integrating contribution {contrib_id}: {e}")
            continue
    
    print(f"\n🎉 Integration complete! Successfully integrated {integrated_count} contributions")
    
    # Show final statistics
    total_entities = {}
    for entity_type in ['teams', 'brands', 'players', 'competitions', 'master_jerseys', 'reference_kits']:
        count = await db[entity_type].count_documents({})
        total_entities[entity_type] = count
        print(f"📊 {entity_type.replace('_', ' ').title()}: {count} total")
    
    return integrated_count

if __name__ == "__main__":
    asyncio.run(integrate_approved_contributions())