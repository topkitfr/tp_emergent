#!/usr/bin/env python3
"""
Test script to approve a master kit contribution and check integration
"""

import requests
import json
import os
import time
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

def test_master_kit_integration():
    """Test the complete master kit integration workflow"""
    session = authenticate_admin()
    if not session:
        return
    
    print("\n🧪 Testing Master Kit Integration Workflow")
    print("=" * 50)
    
    # Get the most recent master kit contribution  
    response = session.get(f"{API_BASE}/contributions-v2/", params={"entity_type": "master_kit"})
    if response.status_code != 200:
        print(f"❌ Failed to get contributions: {response.status_code}")
        return
    
    contributions = response.json()
    pending_contributions = [c for c in contributions if c.get('status') == 'pending_review']
    
    if not pending_contributions:
        print("❌ No pending master kit contributions found")
        return
    
    # Get the most recent one
    contribution = pending_contributions[0]
    contribution_id = contribution['id']
    
    print(f"📝 Found pending contribution: {contribution_id}")
    print(f"  - Title: {contribution.get('title')}")
    print(f"  - Status: {contribution.get('status')}")
    
    # Get full contribution details
    response = session.get(f"{API_BASE}/contributions-v2/{contribution_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get contribution details: {response.status_code}")
        return
    
    full_contribution = response.json()
    data = full_contribution.get('data', {})
    
    print(f"📊 Contribution data before approval:")
    if data:
        for key, value in data.items():
            print(f"  - {key}: {value}")
    else:
        print("  ❌ No data found in contribution!")
        return
    
    # Check current master jerseys count
    response = session.get(f"{API_BASE}/master-jerseys")
    if response.status_code == 200:
        before_count = len(response.json())
        print(f"📈 Master jerseys before approval: {before_count}")
    else:
        print(f"⚠️ Master jerseys endpoint error: {response.status_code}")
        before_count = "unknown"
    
    # Approve the contribution
    print(f"\n✅ Approving contribution...")
    moderation_data = {
        "action": "approve",
        "reason": "Test approval for integration workflow debugging",
        "internal_notes": "Testing master kit integration",
        "notify_contributor": False
    }
    
    response = session.post(f"{API_BASE}/contributions-v2/{contribution_id}/moderate", json=moderation_data)
    if response.status_code != 200:
        print(f"❌ Failed to approve contribution: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    print(f"✅ Contribution approved successfully")
    
    # Wait a moment for integration
    time.sleep(2)
    
    # Check if master jersey was created
    print(f"\n🔍 Checking master jerseys after approval...")
    response = session.get(f"{API_BASE}/master-jerseys")
    if response.status_code == 200:
        after_count = len(response.json())
        print(f"📈 Master jerseys after approval: {after_count}")
        
        if after_count > before_count:
            print(f"✅ New master jersey created! ({after_count - before_count} added)")
            
            # Find the new jersey
            jerseys = response.json()
            for jersey in jerseys[-3:]:  # Check last 3 jerseys
                print(f"  📄 Jersey: {jersey.get('topkit_reference', 'No ref')}")
                print(f"    - Team ID: {jersey.get('team_id')}")
                print(f"    - Brand ID: {jersey.get('brand_id')}")
                print(f"    - Season: {jersey.get('season')}")
                print(f"    - Type: {jersey.get('jersey_type')}")
        else:
            print(f"❌ No new master jersey created (count unchanged)")
    else:
        print(f"❌ Master jerseys endpoint still failing: {response.status_code}")
        print(f"Error: {response.text}")
        
        # Let's try to directly check the database
        print(f"\n🔍 Checking if integration happened despite endpoint error...")
        
        # Check contribution status
        response = session.get(f"{API_BASE}/contributions-v2/{contribution_id}")
        if response.status_code == 200:
            updated_contribution = response.json()
            integrated = updated_contribution.get('integrated', False)
            integrated_at = updated_contribution.get('integrated_at')
            integrated_entity_id = updated_contribution.get('integrated_entity_id')
            
            print(f"  - Integrated flag: {integrated}")
            print(f"  - Integrated at: {integrated_at}")
            print(f"  - Integrated entity ID: {integrated_entity_id}")
            
            if integrated:
                print(f"✅ Integration completed successfully")
            else:
                print(f"❌ Integration not completed")

if __name__ == "__main__":
    print("🚀 Master Kit Integration Test")
    print("=" * 40)
    
    test_master_kit_integration()
    
    print(f"\n🎯 Integration test complete!")