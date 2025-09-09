#!/usr/bin/env python3
"""
Find Specific Player Reference
==============================

Search for TK-PLAYER-7F915C33 specifically
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Get MongoDB URL from environment
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

async def find_specific_player():
    """Search for TK-PLAYER-7F915C33 in all possible locations"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    
    try:
        # Use topkit database
        db = client['topkit']
        
        target_id = 'TK-PLAYER-7F915C33'
        print(f"🔍 Searching for {target_id} in all collections...")
        
        # Get all collection names
        collections = await db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        found_items = []
        
        # Search in each collection
        for collection_name in collections:
            collection = db[collection_name]
            
            # Search by id field
            item_by_id = await collection.find_one({'id': target_id})
            if item_by_id:
                found_items.append({
                    'collection': collection_name,
                    'search_type': 'direct_id',
                    'item': item_by_id
                })
            
            # Search in data fields
            async for doc in collection.find():
                doc_data = doc.get('data', {})
                if isinstance(doc_data, dict):
                    for field_name, field_value in doc_data.items():
                        if field_value == target_id:
                            found_items.append({
                                'collection': collection_name,
                                'search_type': 'data_reference',
                                'field': field_name,
                                'item': doc
                            })
                            break
                
                # Also check if any field directly contains the ID
                for field_name, field_value in doc.items():
                    if isinstance(field_value, str) and target_id in field_value:
                        found_items.append({
                            'collection': collection_name,
                            'search_type': 'field_contains',
                            'field': field_name,
                            'item': doc
                        })
                        break
        
        if not found_items:
            print(f"❌ {target_id} not found in any collection")
            
            # Let's also check what player IDs actually exist
            print(f"\n📋 EXISTING PLAYER IDs:")
            players_collection = db['players']
            async for player in players_collection.find():
                player_id = player.get('id', 'No ID')
                player_name = player.get('name', 'No Name')
                print(f"   - {player_id}: {player_name}")
            
            # Check contributions for players
            print(f"\n📋 PLAYER CONTRIBUTIONS:")
            contributions_collection = db['contributions_v2']
            async for contrib in contributions_collection.find({'entity_type': 'player'}):
                contrib_id = contrib.get('id', 'No ID')
                contrib_title = contrib.get('title', 'No Title')
                contrib_data = contrib.get('data', {})
                player_name = contrib_data.get('name', 'No Name')
                print(f"   - {contrib_id}: {contrib_title} (Player: {player_name})")
        else:
            print(f"✅ Found {len(found_items)} references to {target_id}:")
            
            for item in found_items:
                print(f"\n📍 Found in {item['collection']} collection ({item['search_type']}):")
                if item['search_type'] == 'direct_id':
                    item_data = item['item']
                    print(f"   ID: {item_data.get('id', 'No ID')}")
                    print(f"   Name: {item_data.get('name', 'No Name')}")
                    print(f"   Title: {item_data.get('title', 'No Title')}")
                    print(f"   Status: {item_data.get('status', 'No Status')}")
                elif item['search_type'] == 'data_reference':
                    print(f"   Referenced in field: {item['field']}")
                    print(f"   Parent document ID: {item['item'].get('id', 'No ID')}")
                    print(f"   Parent document title: {item['item'].get('title', 'No Title')}")
                elif item['search_type'] == 'field_contains':
                    print(f"   Contains ID in field: {item['field']}")
                    print(f"   Document ID: {item['item'].get('id', 'No ID')}")
                    print(f"   Document title: {item['item'].get('title', 'No Title')}")
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(find_specific_player())