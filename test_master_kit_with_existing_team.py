#!/usr/bin/env python3
"""
Test creating master kit with existing team/brand names
"""

import requests
import json
import os
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
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

def test_master_kit_with_existing_data():
    """Test creating master kit with existing team/brand"""
    session = authenticate_admin()
    if not session:
        return
    
    print("\n🧪 Testing Master Kit with Existing Team/Brand")
    print("=" * 50)
    
    # First get existing teams and brands
    teams_response = session.get(f"{API_BASE}/teams")
    brands_response = session.get(f"{API_BASE}/brands")
    
    if teams_response.status_code != 200 or brands_response.status_code != 200:
        print("❌ Failed to get teams or brands")
        return
    
    teams = teams_response.json()
    brands = brands_response.json()
    
    if not teams or not brands:
        print("❌ No teams or brands found")
        return
    
    # Use first team and brand
    team = teams[0]
    brand = brands[0]
    
    print(f"📋 Using existing data:")
    print(f"  - Team: {team['name']} (ID: {team['id']})")
    print(f"  - Brand: {brand['name']} (ID: {brand['id']})")
    
    # Create master kit contribution
    test_contribution = {
        "entity_type": "master_kit",
        "entity_id": None,
        "title": "Working Master Kit Test 2024",
        "description": "Testing master kit with existing team/brand",
        "data": {
            "team_name": team['name'],  # Use exact team name
            "brand_name": brand['name'],  # Use exact brand name
            "season": "2024-25",
            "jersey_type": "home",
            "model": "authentic",
            "primary_color": "#FF0000",
            "secondary_colors": ["#FFFFFF", "#000000"],
            "pattern": "solid",
            "main_sponsor": "Working Sponsor"
        },
        "source_urls": ["https://example.com/working-test-kit"]
    }
    
    print(f"\n📝 Creating contribution...")
    response = session.post(f"{API_BASE}/contributions-v2/", json=test_contribution)
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create contribution: {response.status_code}")
        return
    
    contribution = response.json()
    contribution_id = contribution['id']
    print(f"✅ Created contribution: {contribution_id}")
    
    # Approve it immediately
    print(f"\n✅ Approving contribution...")
    moderation_data = {
        "action": "approve",
        "reason": "Test approval with existing team/brand",
        "notify_contributor": False
    }
    
    response = session.post(f"{API_BASE}/contributions-v2/{contribution_id}/moderate", json=moderation_data)
    if response.status_code != 200:
        print(f"❌ Failed to approve: {response.status_code}")
        return
    
    print(f"✅ Contribution approved successfully")
    
    # Wait for integration
    time.sleep(3)
    
    # Check master jerseys
    print(f"\n🔍 Checking master jerseys...")
    response = session.get(f"{API_BASE}/master-jerseys")
    if response.status_code == 200:
        jerseys = response.json()
        print(f"📈 Total master jerseys: {len(jerseys)}")
        
        # Find our new jersey
        new_jersey = None
        for jersey in jerseys:
            if jersey.get('season') == '2024-25' and jersey.get('jersey_type') == 'home':
                if jersey.get('team_info', {}).get('name') == team['name']:
                    new_jersey = jersey
                    break
        
        if new_jersey:
            print(f"✅ Found integrated master jersey:")
            print(f"  - Reference: {new_jersey.get('topkit_reference')}")
            print(f"  - Season: {new_jersey.get('season')}")
            print(f"  - Team: {new_jersey.get('team_info', {}).get('name')} (ID: {new_jersey.get('team_id')})")
            print(f"  - Brand: {new_jersey.get('brand_info', {}).get('name')} (ID: {new_jersey.get('brand_id')})")
            print(f"  - Created By: {new_jersey.get('created_by')}")
            return True
        else:
            print(f"❌ Could not find integrated master jersey")
            return False
    else:
        print(f"❌ Master jerseys endpoint error: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 Master Kit Integration Test with Existing Data")
    print("=" * 50)
    
    success = test_master_kit_with_existing_data()
    
    if success:
        print(f"\n🎉 SUCCESS! Master kit integration is working correctly!")
    else:
        print(f"\n❌ FAILED! Integration issue persists.")