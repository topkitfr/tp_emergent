#!/usr/bin/env python3
"""
Test the master jerseys endpoint directly
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-collab-1.preview.emergentagent.com')
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

def test_master_jerseys_endpoint():
    """Test the master jerseys endpoint"""
    session = authenticate_admin()
    if not session:
        return
    
    print("\n🧪 Testing Master Jerseys Endpoint")
    print("=" * 50)
    
    response = session.get(f"{API_BASE}/master-jerseys")
    
    print(f"📊 Endpoint response:")
    print(f"  - Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        count = len(data) if isinstance(data, list) else 0
        print(f"  - Master Jerseys Count: {count}")
        
        if count > 0:
            print(f"\n📋 Sample Master Jerseys:")
            for i, jersey in enumerate(data[:3]):  # Show first 3
                print(f"    Jersey {i+1}:")
                print(f"      - ID: {jersey.get('id')}")
                print(f"      - Reference: {jersey.get('topkit_reference')}")
                print(f"      - Season: {jersey.get('season')}")
                print(f"      - Type: {jersey.get('jersey_type')}")
                print(f"      - Team ID: {jersey.get('team_id')}")
                print(f"      - Brand ID: {jersey.get('brand_id')}")
                print(f"      - Created By: {jersey.get('created_by')}")
                print(f"      - Team Info: {jersey.get('team_info', {})}")
                print(f"      - Brand Info: {jersey.get('brand_info', {})}")
        else:
            print("  ❌ No master jerseys found!")
    else:
        print(f"  ❌ Error: {response.text}")

if __name__ == "__main__":
    print("🚀 Master Jerseys Endpoint Test")
    print("=" * 40)
    
    test_master_jerseys_endpoint()
    
    print(f"\n🎯 Test complete!")