#!/usr/bin/env python3
"""
Process approved contributions that don't have corresponding entities created
"""
import os
import asyncio
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

async def process_approved_contributions():
    """Process approved contributions and create missing entities"""
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.topkit_db
    
    print("=== PROCESSING APPROVED CONTRIBUTIONS ===\n")
    
    # Find approved contributions without entity_id
    approved_contributions = await db.contributions.find({
        "status": "approved",
        "entity_id": None
    }).to_list(length=None)
    
    print(f"Found {len(approved_contributions)} approved contributions without entities")
    
    for contrib in approved_contributions:
        try:
            print(f"\nProcessing: {contrib['title']} (TK-CONTRIB: {contrib['topkit_reference']})")
            
            entity_type = contrib["entity_type"]
            entity_data = contrib["data"]
            entity_id = str(uuid.uuid4())
            
            # Prepare common fields
            entity = {
                "id": entity_id,
                "created_at": datetime.utcnow(),
                "created_from_contribution": contrib["id"],
                "topkit_reference": f"TK-{entity_type.upper()}-{uuid.uuid4().hex[:6].upper()}"
            }
            
            # Add entity-specific data
            if entity_type == "team":
                entity.update({
                    "name": entity_data.get("name", ""),
                    "short_name": entity_data.get("short_name", ""),
                    "country": entity_data.get("country", ""),
                    "city": entity_data.get("city", ""),
                    "founded_year": entity_data.get("founded_year", 0),
                    "colors": entity_data.get("colors", []),
                    "logo_url": entity_data.get("logo_url", ""),
                    "secondary_photos": entity_data.get("secondary_photos", "")
                })
                await db.teams.insert_one(entity)
                print(f"  ✅ Created team: {entity['name']} (TK-TEAM: {entity['topkit_reference']})")
                
            elif entity_type == "brand":
                entity.update({
                    "name": entity_data.get("name", ""),
                    "country": entity_data.get("country", ""),
                    "founded_year": entity_data.get("founded_year", 0),
                    "logo_url": entity_data.get("logo_url", ""),
                    "description": entity_data.get("description", "")
                })
                await db.brands.insert_one(entity)
                print(f"  ✅ Created brand: {entity['name']} (TK-BRAND: {entity['topkit_reference']})")
                
            elif entity_type == "player":
                entity.update({
                    "name": entity_data.get("name", ""),
                    "nationality": entity_data.get("nationality", ""),
                    "position": entity_data.get("position", ""),
                    "birth_date": entity_data.get("birth_date", ""),
                    "photo_url": entity_data.get("photo_url", "")
                })
                await db.players.insert_one(entity)
                print(f"  ✅ Created player: {entity['name']} (TK-PLAYER: {entity['topkit_reference']})")
                
            elif entity_type == "competition":
                entity.update({
                    "name": entity_data.get("name", ""),
                    "competition_name": entity_data.get("competition_name", entity_data.get("name", "")),
                    "country": entity_data.get("country", ""),
                    "level": entity_data.get("level", ""),
                    "format": entity_data.get("format", ""),
                    "logo_url": entity_data.get("logo_url", "")
                })
                await db.competitions.insert_one(entity)
                print(f"  ✅ Created competition: {entity['name']} (TK-COMPETITION: {entity['topkit_reference']})")
            
            # Update contribution with entity_id
            await db.contributions.update_one(
                {"id": contrib["id"]},
                {"$set": {"entity_id": entity_id}}
            )
            print(f"  ✅ Updated contribution with entity_id: {entity_id}")
            
        except Exception as e:
            print(f"  ❌ Error processing contribution {contrib['id']}: {str(e)}")
    
    print("\n=== SUMMARY ===")
    teams_count = await db.teams.count_documents({})
    brands_count = await db.brands.count_documents({})
    players_count = await db.players.count_documents({})
    competitions_count = await db.competitions.count_documents({})
    
    print(f"Total entities in database:")
    print(f"  Teams: {teams_count}")
    print(f"  Brands: {brands_count}")
    print(f"  Players: {players_count}")
    print(f"  Competitions: {competitions_count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(process_approved_contributions())