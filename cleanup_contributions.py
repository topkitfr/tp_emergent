#!/usr/bin/env python3
"""
Contributions cleanup script - keep only contributions for items still in catalog
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def cleanup_contributions():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.topkit
    
    print("🧹 Starting contributions cleanup...")
    
    # Get current catalog items
    catalog_items = {
        'teams': [],
        'brands': [],
        'players': [],
        'competitions': []
    }
    
    # Fetch existing catalog items with their names
    teams = await db.teams.find({}).to_list(length=None)
    catalog_items['teams'] = [team.get('name') for team in teams if team.get('name')]
    
    brands = await db.brands.find({}).to_list(length=None)
    catalog_items['brands'] = [brand.get('name') for brand in brands if brand.get('name')]
    
    players = await db.players.find({}).to_list(length=None)
    catalog_items['players'] = [player.get('name') for player in players if player.get('name')]
    
    competitions = await db.competitions.find({}).to_list(length=None)
    catalog_items['competitions'] = [comp.get('name') for comp in competitions if comp.get('name')]
    
    print("📊 Catalog items to keep contributions for:")
    for entity_type, names in catalog_items.items():
        print(f"  {entity_type}: {names}")
    
    # Process each contribution collection
    contribution_collections = ['contributions_v2', 'enhanced_contributions']
    
    total_deleted = 0
    total_kept = 0
    
    for collection_name in contribution_collections:
        contributions = await db[collection_name].find({}).to_list(length=None)
        
        if not contributions:
            print(f"\\n📋 {collection_name}: No contributions found")
            continue
            
        print(f"\\n📋 Processing {collection_name} ({len(contributions)} contributions):")
        
        deleted_count = 0
        kept_count = 0
        
        for contrib in contributions:
            contrib_id = contrib.get('id')
            entity_type = contrib.get('entity_type')
            data = contrib.get('data', {})
            
            should_delete = False
            reason = ""
            
            # Rule 1: Delete all master_kit and reference_kit contributions
            if entity_type in ['master_kit', 'reference_kit']:
                should_delete = True
                reason = f"Entity type '{entity_type}' no longer exists in catalog"
            
            # Rule 2: For other entity types, check if the item exists in catalog
            elif entity_type in ['team', 'brand', 'player', 'competition']:
                entity_name = data.get('name') or data.get('team_name') or data.get('competition_name')
                
                if not entity_name:
                    should_delete = True
                    reason = "No name found in contribution data"
                elif entity_name not in catalog_items.get(entity_type + 's', []):
                    should_delete = True
                    reason = f"'{entity_name}' not found in {entity_type}s catalog"
                else:
                    reason = f"Keeping '{entity_name}' - exists in catalog"
            
            # Rule 3: Delete unknown entity types
            else:
                should_delete = True
                reason = f"Unknown entity type '{entity_type}'"
            
            if should_delete:
                await db[collection_name].delete_one({"id": contrib_id})
                deleted_count += 1
                print(f"    ❌ Deleted {contrib_id}: {reason}")
            else:
                kept_count += 1
                print(f"    ✅ Kept {contrib_id}: {reason}")
        
        print(f"  → {collection_name}: Deleted {deleted_count}, Kept {kept_count}")
        total_deleted += deleted_count
        total_kept += kept_count
    
    # Also clean up the old 'contributions' collection if it exists
    old_contributions_count = await db.contributions.count_documents({})
    if old_contributions_count > 0:
        await db.contributions.delete_many({})
        print(f"\\n🧹 Cleaned up old 'contributions' collection: {old_contributions_count} deleted")
        total_deleted += old_contributions_count
    
    print(f"\\n🎉 Contributions cleanup completed!")
    print(f"  📊 Total: Deleted {total_deleted}, Kept {total_kept}")
    
    # Verify final state
    print(f"\\n📈 Final contribution counts:")
    for collection_name in contribution_collections:
        count = await db[collection_name].count_documents({})
        print(f"  {collection_name}: {count} contributions")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_contributions())