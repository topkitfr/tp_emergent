#!/usr/bin/env python3
"""
Create test data for Vestiaire system testing
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import uuid

API_BASE = "https://topkit-workflow-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

async def create_test_data():
    """Create test data for Vestiaire system"""
    
    async with aiohttp.ClientSession() as session:
        # Authenticate admin
        print("🔐 Authenticating admin...")
        async with session.post(f"{API_BASE}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }) as response:
            if response.status != 200:
                print(f"❌ Admin authentication failed: {response.status}")
                return
            
            data = await response.json()
            admin_token = data.get('token')
            print(f"✅ Admin authenticated: {data.get('user', {}).get('name', 'Unknown')}")
        
        headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        
        # Create sample teams
        print("\n🏟️ Creating sample teams...")
        teams_data = [
            {"name": "FC Barcelona", "country": "Spain", "league": "La Liga", "topkit_reference": "TK-TEAM-001"},
            {"name": "Real Madrid", "country": "Spain", "league": "La Liga", "topkit_reference": "TK-TEAM-002"},
            {"name": "Manchester United", "country": "England", "league": "Premier League", "topkit_reference": "TK-TEAM-003"}
        ]
        
        team_ids = []
        for team_data in teams_data:
            try:
                async with session.post(f"{API_BASE}/teams", json=team_data, headers=headers) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        team_ids.append(result.get('id', str(uuid.uuid4())))
                        print(f"✅ Created team: {team_data['name']}")
                    else:
                        # Team might already exist
                        team_ids.append(str(uuid.uuid4()))
                        print(f"⚠️ Team {team_data['name']} might already exist")
            except Exception as e:
                team_ids.append(str(uuid.uuid4()))
                print(f"⚠️ Error creating team {team_data['name']}: {e}")
        
        # Create sample master jerseys
        print("\n👕 Creating sample master jerseys...")
        master_jerseys_data = [
            {
                "team_id": team_ids[0],
                "season": "2024/25",
                "jersey_type": "home",
                "manufacturer": "Nike",
                "topkit_reference": "TK-MASTER-001"
            },
            {
                "team_id": team_ids[1], 
                "season": "2024/25",
                "jersey_type": "away",
                "manufacturer": "Adidas",
                "topkit_reference": "TK-MASTER-002"
            },
            {
                "team_id": team_ids[2],
                "season": "2023/24", 
                "jersey_type": "home",
                "manufacturer": "TeamViewer",
                "topkit_reference": "TK-MASTER-003"
            }
        ]
        
        master_jersey_ids = []
        for master_data in master_jerseys_data:
            try:
                async with session.post(f"{API_BASE}/master-jerseys", json=master_data, headers=headers) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        master_jersey_ids.append(result.get('id', str(uuid.uuid4())))
                        print(f"✅ Created master jersey: {master_data['topkit_reference']}")
                    else:
                        master_jersey_ids.append(str(uuid.uuid4()))
                        print(f"⚠️ Master jersey might already exist")
            except Exception as e:
                master_jersey_ids.append(str(uuid.uuid4()))
                print(f"⚠️ Error creating master jersey: {e}")
        
        # Create sample jersey releases
        print("\n🎽 Creating sample jersey releases...")
        jersey_releases_data = [
            {
                "master_jersey_id": master_jersey_ids[0],
                "player_name": "Lionel Messi",
                "player_id": "messi-001",
                "release_type": "player_version",
                "retail_price": 89.99,
                "season": "2024/25",
                "team_id": team_ids[0],
                "topkit_reference": "TK-RELEASE-001"
            },
            {
                "master_jersey_id": master_jersey_ids[1],
                "player_name": "Vinicius Jr",
                "player_id": "vinicius-001", 
                "release_type": "player_version",
                "retail_price": 94.99,
                "season": "2024/25",
                "team_id": team_ids[1],
                "topkit_reference": "TK-RELEASE-002"
            },
            {
                "master_jersey_id": master_jersey_ids[2],
                "player_name": "Marcus Rashford",
                "player_id": "rashford-001",
                "release_type": "player_version", 
                "retail_price": 84.99,
                "season": "2023/24",
                "team_id": team_ids[2],
                "topkit_reference": "TK-RELEASE-003"
            }
        ]
        
        for release_data in jersey_releases_data:
            try:
                async with session.post(f"{API_BASE}/jersey-releases", json=release_data, headers=headers) as response:
                    if response.status in [200, 201]:
                        print(f"✅ Created jersey release: {release_data['topkit_reference']} - {release_data['player_name']}")
                    else:
                        error_text = await response.text()
                        print(f"⚠️ Error creating jersey release {release_data['topkit_reference']}: {response.status} - {error_text}")
            except Exception as e:
                print(f"⚠️ Exception creating jersey release: {e}")
        
        print("\n🎯 Test data creation completed!")
        print("You can now run the Vestiaire backend test to verify the system.")

if __name__ == "__main__":
    asyncio.run(create_test_data())