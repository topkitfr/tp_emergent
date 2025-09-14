#!/usr/bin/env python3
"""
Test the team creation and contributions fix
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://footkit-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_system():
    print("🧪 Testing Team Creation and Contributions Fix\n")
    
    # Step 1: Authenticate as user
    print("1. Authenticating as user...")
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "steinmetzlivio@gmail.com",
        "password": "T0p_Mdp_1288*"
    })
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.text}")
        return
    
    token = response.json()['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Step 2: Create a new team
    print("\n2. Creating a new team...")
    team_name = f"FC Test {datetime.now().strftime('%H%M%S')}"
    team_data = {
        "name": team_name,
        "country": "France",
        "city": "Test City",
        "founded_year": 2024,
        "short_name": "FCT",
        "team_colors": ["blue", "white"]
    }
    
    response = requests.post(f"{API_BASE}/teams", json=team_data, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"❌ Team creation failed: {response.text}")
        return
    
    team = response.json()
    team_id = team['id']
    print(f"✅ Team created successfully: {team_name} (ID: {team_id})")
    
    # Step 3: Check if team appears in contributions
    print("\n3. Checking if team appears in contributions...")
    response = requests.get(f"{API_BASE}/contributions", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch contributions: {response.text}")
        return
    
    contributions = response.json()
    team_contributions = [c for c in contributions if c.get('entity_type') == 'team' and c.get('entity_id') == team_id]
    
    if team_contributions:
        print(f"✅ Team found in contributions! Found {len(team_contributions)} contribution(s)")
        for contrib in team_contributions:
            print(f"   - {contrib['title']} (Status: {contrib['status']})")
    else:
        print(f"❌ Team NOT found in contributions")
        print(f"   Total contributions: {len(contributions)}")
        print(f"   Team contributions: {len([c for c in contributions if c.get('entity_type') == 'team'])}")
    
    # Step 4: Test image upload endpoint
    print("\n4. Testing image upload endpoint...")
    
    # Create a simple test image data (1x1 pixel PNG)
    import base64
    test_image_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==')
    
    files = {
        'file': ('test_logo.png', test_image_data, 'image/png'),
        'entity_type': (None, 'team')
    }
    
    response = requests.post(f"{API_BASE}/upload/image", files=files, headers=headers)
    
    if response.status_code in [200, 201]:
        upload_result = response.json()
        print(f"✅ Image upload successful!")
        print(f"   Image URL: {upload_result['image_url']}")
        print(f"   Filename: {upload_result['filename']}")
    else:
        print(f"❌ Image upload failed: {response.text}")
    
    print(f"\n🎯 Test Summary:")
    print(f"   - Team Creation: ✅ Working")
    print(f"   - Auto-Contribution: {'✅ Working' if team_contributions else '❌ Failed'}")
    print(f"   - Image Upload: {'✅ Working' if response.status_code in [200, 201] else '❌ Failed'}")

if __name__ == "__main__":
    test_system()