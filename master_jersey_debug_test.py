#!/usr/bin/env python3
"""
Master Jersey Debug Test - Check the actual data in master_jerseys collection
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://topkit-workflow-fix.preview.emergentagent.com')
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

def debug_master_jerseys_collection():
    """Debug the master_jerseys collection directly"""
    session = authenticate_admin()
    if not session:
        return
    
    print("\n🔍 Debugging Master Jerseys Collection")
    print("=" * 50)
    
    # Try to access the collection directly via MongoDB-style query
    # Since we can't access MongoDB directly, let's check what approved contributions exist
    
    print("\n📋 Step 1: Check Approved Master Kit Contributions")
    response = session.get(f"{API_BASE}/contributions-v2/", params={"entity_type": "master_kit"})
    
    if response.status_code == 200:
        contributions = response.json()
        approved_contribs = [c for c in contributions if c.get('status') == 'approved']
        
        print(f"Found {len(approved_contribs)} approved master kit contributions")
        
        for i, contrib in enumerate(approved_contribs):
            print(f"\n  Contribution {i+1}:")
            print(f"    ID: {contrib.get('id')}")
            print(f"    Title: {contrib.get('title')}")
            print(f"    Status: {contrib.get('status')}")
            
            data = contrib.get('data', {})
            print(f"    Data structure:")
            for key, value in data.items():
                print(f"      {key}: {value}")
            
            # Check if this contribution has team_id/brand_id or team_name/brand_name
            has_ids = data.get('team_id') or data.get('brand_id')
            has_names = data.get('team_name') or data.get('brand_name')
            print(f"    Has IDs: {bool(has_ids)}")
            print(f"    Has Names: {bool(has_names)}")
    
    print(f"\n👕 Step 2: Try Alternative Master Jersey Endpoints")
    
    # Try different approaches to access master jerseys
    endpoints_to_try = [
        "/master-jerseys",
        "/master-jerseys/",
        "/master-kits",
        "/master-kits/"
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n  Trying {endpoint}:")
        try:
            response = session.get(f"{API_BASE}{endpoint}")
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"    Count: {count}")
                
                if count > 0:
                    print(f"    Sample item:")
                    sample = data[0] if isinstance(data, list) else data
                    for key, value in sample.items():
                        if key not in ['_id']:
                            print(f"      {key}: {value}")
            elif response.status_code == 500:
                print(f"    Error: Internal Server Error")
                try:
                    error_text = response.text
                    print(f"    Details: {error_text}")
                except:
                    pass
            else:
                print(f"    Error: {response.text}")
        except Exception as e:
            print(f"    Exception: {e}")

def check_teams_and_brands():
    """Check if teams and brands exist for ID lookup"""
    session = authenticate_admin()
    if not session:
        return
    
    print(f"\n🏢 Step 3: Check Teams and Brands Collections")
    print("-" * 40)
    
    # Check teams
    response = session.get(f"{API_BASE}/teams")
    if response.status_code == 200:
        teams = response.json()
        print(f"Teams collection: {len(teams)} items")
        if teams:
            sample_team = teams[0]
            print(f"  Sample team: {sample_team.get('name')} (ID: {sample_team.get('id')})")
    else:
        print(f"Teams collection error: {response.status_code}")
    
    # Check brands
    response = session.get(f"{API_BASE}/brands")
    if response.status_code == 200:
        brands = response.json()
        print(f"Brands collection: {len(brands)} items")
        if brands:
            sample_brand = brands[0]
            print(f"  Sample brand: {sample_brand.get('name')} (ID: {sample_brand.get('id')})")
    else:
        print(f"Brands collection error: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Master Jersey Debug Test")
    print("=" * 40)
    
    debug_master_jerseys_collection()
    check_teams_and_brands()
    
    print(f"\n🎯 Debug Complete!")