#!/usr/bin/env python3
"""
Test script to create a master kit contribution and check data storage
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-collection-5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def authenticate_admin():
    """Authenticate admin user and get JWT token"""
    session = requests.Session()
    
    auth_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = session.post(f"{API_BASE}/auth/login", json=auth_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        if token:
            session.headers.update({
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            })
            print(f"✅ Admin authenticated successfully")
            return session
    
    print(f"❌ Authentication failed: {response.status_code}")
    return None

def test_master_kit_contribution():
    """Test creating a master kit contribution with proper data"""
    session = authenticate_admin()
    if not session:
        return
    
    print("\n🧪 Testing Master Kit Contribution Data Storage")
    print("=" * 50)
    
    # Create a master kit contribution with detailed data
    test_contribution = {
        "entity_type": "master_kit",
        "entity_id": None,
        "title": "Debug Test Master Kit 2024",
        "description": "Testing master kit data storage and integration",
        "data": {
            "team_name": "Debug FC",
            "brand_name": "Test Brand Nike",
            "season": "2024-25",
            "jersey_type": "home",
            "model": "authentic",
            "primary_color": "#FF0000",
            "secondary_colors": ["#FFFFFF", "#000000"],
            "pattern": "solid",
            "main_sponsor": "Debug Sponsor"
        },
        "source_urls": ["https://example.com/debug-test-kit"]
    }
    
    print("📝 Creating contribution with data:")
    print(json.dumps(test_contribution, indent=2))
    
    response = session.post(f"{API_BASE}/contributions-v2/", json=test_contribution)
    
    if response.status_code in [200, 201]:
        data = response.json()
        contribution_id = data.get('id')
        print(f"✅ Created contribution: {contribution_id}")
        
        # Check the stored data immediately
        print(f"\n🔍 Checking stored contribution data:")
        response = session.get(f"{API_BASE}/contributions-v2/{contribution_id}")
        if response.status_code == 200:
            contrib_data = response.json()
            print(f"✅ Retrieved contribution successfully")
            print(f"  - ID: {contrib_data.get('id')}")
            print(f"  - Entity Type: {contrib_data.get('entity_type')}")
            print(f"  - Title: {contrib_data.get('title')}")
            print(f"  - Status: {contrib_data.get('status')}")
            
            stored_data = contrib_data.get('data', {})
            print(f"  - Data field content: {stored_data}")
            print(f"  - Data field is empty: {len(stored_data) == 0}")
            
            if stored_data:
                print(f"  - Data keys: {list(stored_data.keys())}")
                for key, value in stored_data.items():
                    print(f"    {key}: {value}")
            else:
                print("  ❌ DATA FIELD IS EMPTY!")
                
        return contribution_id
    else:
        print(f"❌ Failed to create contribution: {response.status_code}")
        print(f"Response: {response.text}")
        return None

if __name__ == "__main__":
    print("🚀 Master Kit Contribution Data Test")
    print("=" * 40)
    
    contribution_id = test_master_kit_contribution()
    
    if contribution_id:
        print(f"\n🎯 Test contribution created: {contribution_id}")
        print("Check the backend logs for DEBUG messages showing the received data")
    else:
        print("\n❌ Test failed")