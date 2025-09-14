#!/usr/bin/env python
"""
Test selective update functionality for the improve workflow
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import json

async def test_selective_update():
    """Test that selective updates work correctly"""
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.topkit_db
    
    print("🔍 Testing Selective Update Logic")
    print("=" * 50)
    
    # Find the team that had issues
    team = await db.teams.find_one({'topkit_reference': 'TK-TEAM-616469'})
    if team:
        print(f"✅ Found test team: {team['topkit_reference']}")
        print(f"   Current name: '{team['name']}'")
        print(f"   Logo URL: '{team.get('logo_url', 'None')}'")
        print(f"   Modification count: {team.get('modification_count', 0)}")
        print()
        
        # Simulate selective update (only logo change)
        from server import create_or_update_entity_from_contribution
        
        # Create mock contribution with only logo change
        mock_contribution = {
            "id": "test-contribution-123",
            "entity_type": "team",
            "entity_id": team["id"],
            "data": {
                "logo_url": "image_uploaded_test_selective_update"
            },
            "created_by": "test-user"
        }
        
        print("🧪 Testing selective update with only logo change...")
        print(f"   Original data: {{'logo_url': '{team.get('logo_url')}', 'name': '{team['name']}'}}")
        print(f"   Update data: {json.dumps(mock_contribution['data'])}")
        
        # Apply the update
        result = await create_or_update_entity_from_contribution(mock_contribution)
        
        if result:
            # Check the updated team
            updated_team = await db.teams.find_one({'id': team['id']})
            print(f"   Updated data: {{'logo_url': '{updated_team.get('logo_url')}', 'name': '{updated_team['name']}'}}")
            
            # Verify only logo changed
            if updated_team['name'] == team['name'] and updated_team['logo_url'] != team['logo_url']:
                print("✅ SUCCESS: Only logo was updated, name remained unchanged!")
            else:
                print("❌ FAILURE: Unintended field changes detected!")
                print(f"   Name changed: {team['name']} -> {updated_team['name']}")
                print(f"   Logo changed: {team.get('logo_url')} -> {updated_team.get('logo_url')}")
        else:
            print("❌ FAILURE: Update function returned None")
            
    else:
        print("❌ Test team TK-TEAM-616469 not found")
    
    print()
    print("🔍 Testing with multiple entity types...")
    print("=" * 50)
    
    # Test with other entity types
    entity_tests = [
        ("brand", "brands", "logo_url"),
        ("player", "players", "photo_url"), 
        ("competition", "competitions", "logo_url")
    ]
    
    for entity_type, collection_name, image_field in entity_tests:
        collection = getattr(db, collection_name)
        entity = await collection.find_one({})
        
        if entity:
            print(f"✅ Testing {entity_type}: {entity.get('name', 'Unknown')}")
            
            # Create mock contribution
            mock_contribution = {
                "id": f"test-{entity_type}-123",
                "entity_type": entity_type,
                "entity_id": entity["id"],
                "data": {
                    image_field: f"image_uploaded_test_{entity_type}"
                },
                "created_by": "test-user"
            }
            
            original_name = entity.get('name', '')
            print(f"   Original name: '{original_name}'")
            
            # Apply selective update
            from server import create_or_update_entity_from_contribution
            result = await create_or_update_entity_from_contribution(mock_contribution)
            
            if result:
                updated_entity = await collection.find_one({'id': entity['id']})
                updated_name = updated_entity.get('name', '')
                
                if updated_name == original_name:
                    print(f"   ✅ SUCCESS: Name preserved: '{updated_name}'")
                else:
                    print(f"   ❌ FAILURE: Name changed: '{original_name}' -> '{updated_name}'")
            else:
                print(f"   ❌ FAILURE: Update failed")
        else:
            print(f"⚠️  No {entity_type} found for testing")
    
    client.close()
    print("\n🎯 Selective update test completed!")

if __name__ == "__main__":
    asyncio.run(test_selective_update())