#!/usr/bin/env python3
"""
Master Kit Approval Test - Test manual approval of master kit contributions
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

def test_master_kit_approval_workflow():
    """Test the complete master kit approval workflow"""
    session = authenticate_admin()
    if not session:
        return
    
    print("\n🧪 Testing Master Kit Approval Workflow")
    print("=" * 50)
    
    # Step 1: Create a master kit contribution
    print("\n📝 Step 1: Creating Master Kit Contribution")
    test_contribution = {
        "entity_type": "master_kit",
        "entity_id": None,
        "title": "Test Master Kit Approval Workflow",
        "description": "Testing master kit approval and integration",
        "data": {
            "team_name": "Test Approval FC",
            "brand_name": "Test Brand",
            "season": "2024-25",
            "jersey_type": "home",
            "model": "authentic",
            "primary_color": "#FF0000"
        },
        "source_urls": ["https://example.com/test-approval-kit"]
    }
    
    response = session.post(f"{API_BASE}/contributions-v2/", json=test_contribution)
    
    if response.status_code in [200, 201]:
        data = response.json()
        contribution_id = data.get('id')
        print(f"✅ Created contribution: {contribution_id}")
        
        # Step 2: Check contribution status
        print(f"\n🔍 Step 2: Checking Contribution Status")
        response = session.get(f"{API_BASE}/contributions-v2/{contribution_id}")
        if response.status_code == 200:
            contrib_data = response.json()
            status = contrib_data.get('status')
            print(f"✅ Contribution status: {status}")
            
            # Step 3: Manually approve the contribution
            print(f"\n✅ Step 3: Manually Approving Contribution")
            moderation_data = {
                "action": "approve",
                "notes": "Test approval for master kit integration workflow",
                "notify_contributor": False
            }
            
            response = session.post(f"{API_BASE}/contributions-v2/{contribution_id}/moderate", json=moderation_data)
            if response.status_code == 200:
                print(f"✅ Contribution approved successfully")
                
                # Step 4: Check if it appears in master jerseys collection
                print(f"\n👕 Step 4: Checking Master Jerseys Collection")
                import time
                time.sleep(2)  # Wait for integration
                
                response = session.get(f"{API_BASE}/master-jerseys")
                if response.status_code == 200:
                    jerseys = response.json()
                    test_jersey_found = any(
                        j.get('season') == '2024-25' and 
                        'Test Approval FC' in str(j.get('team_name', ''))
                        for j in jerseys
                    )
                    
                    if test_jersey_found:
                        print(f"✅ SUCCESS: Master kit integrated to master jerseys collection!")
                        print(f"   Found test jersey in collection")
                        
                        # Show the integrated jersey details
                        for jersey in jerseys:
                            if (jersey.get('season') == '2024-25' and 
                                'Test Approval FC' in str(jersey.get('team_name', ''))):
                                print(f"   Jersey Details:")
                                print(f"     - ID: {jersey.get('id')}")
                                print(f"     - TopKit Ref: {jersey.get('topkit_reference')}")
                                print(f"     - Team: {jersey.get('team_name')}")
                                print(f"     - Season: {jersey.get('season')}")
                                print(f"     - Type: {jersey.get('jersey_type')}")
                                break
                    else:
                        print(f"❌ FAILURE: Master kit NOT found in master jerseys collection")
                        print(f"   Total jerseys in collection: {len(jerseys)}")
                else:
                    print(f"❌ Failed to check master jerseys: {response.status_code}")
                
                # Step 5: Check master kits collection too
                print(f"\n🎽 Step 5: Checking Master Kits Collection")
                response = session.get(f"{API_BASE}/master-kits")
                if response.status_code == 200:
                    kits = response.json()
                    test_kit_found = any(
                        k.get('season') == '2024-25' and 
                        'Test Approval FC' in str(k.get('team_name', ''))
                        for k in kits
                    )
                    
                    if test_kit_found:
                        print(f"✅ Also found in master kits collection")
                    else:
                        print(f"ℹ️ Not found in master kits collection (expected - goes to master jerseys)")
                        print(f"   Total kits in collection: {len(kits)}")
                else:
                    print(f"❌ Failed to check master kits: {response.status_code}")
                    
            else:
                print(f"❌ Failed to approve contribution: {response.status_code} - {response.text}")
        else:
            print(f"❌ Failed to get contribution: {response.status_code}")
    else:
        print(f"❌ Failed to create contribution: {response.status_code} - {response.text}")

def check_existing_contributions():
    """Check existing master kit contributions and their status"""
    session = authenticate_admin()
    if not session:
        return
    
    print("\n🔍 Checking Existing Master Kit Contributions")
    print("=" * 50)
    
    response = session.get(f"{API_BASE}/contributions-v2/", params={"entity_type": "master_kit"})
    
    if response.status_code == 200:
        contributions = response.json()
        master_kit_contribs = [c for c in contributions if c.get('entity_type') == 'master_kit']
        
        print(f"📊 Found {len(master_kit_contribs)} master kit contributions")
        
        status_counts = {}
        for contrib in master_kit_contribs:
            status = contrib.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"📋 Status breakdown:")
        for status, count in status_counts.items():
            print(f"   - {status}: {count}")
        
        # Show details of first few contributions
        print(f"\n📝 Sample Contributions:")
        for i, contrib in enumerate(master_kit_contribs[:3]):
            print(f"   {i+1}. ID: {contrib.get('id')}")
            print(f"      Title: {contrib.get('title')}")
            print(f"      Status: {contrib.get('status')}")
            print(f"      Created: {contrib.get('created_at')}")
            data = contrib.get('data', {})
            print(f"      Team: {data.get('team_name', 'N/A')}")
            print(f"      Season: {data.get('season', 'N/A')}")
            print()
        
        # Try to approve one existing contribution if any are pending
        pending_contribs = [c for c in master_kit_contribs if c.get('status') == 'PENDING_REVIEW']
        if pending_contribs:
            print(f"\n✅ Attempting to approve first pending contribution...")
            contrib_to_approve = pending_contribs[0]
            contrib_id = contrib_to_approve.get('id')
            
            moderation_data = {
                "action": "approve",
                "notes": "Test approval for existing master kit contribution",
                "notify_contributor": False
            }
            
            response = session.post(f"{API_BASE}/contributions-v2/{contrib_id}/moderate", json=moderation_data)
            if response.status_code == 200:
                print(f"✅ Successfully approved existing contribution: {contrib_id}")
                
                # Check if it gets integrated
                import time
                time.sleep(2)
                
                response = session.get(f"{API_BASE}/master-jerseys")
                if response.status_code == 200:
                    jerseys = response.json()
                    data = contrib_to_approve.get('data', {})
                    team_name = data.get('team_name', '')
                    season = data.get('season', '')
                    
                    found_jersey = any(
                        j.get('season') == season and 
                        team_name.lower() in str(j.get('team_name', '')).lower()
                        for j in jerseys
                    )
                    
                    if found_jersey:
                        print(f"✅ SUCCESS: Existing contribution integrated to master jerseys!")
                    else:
                        print(f"❌ FAILURE: Existing contribution NOT integrated")
                        print(f"   Looking for: {team_name} {season}")
                        print(f"   Total jerseys: {len(jerseys)}")
            else:
                print(f"❌ Failed to approve existing contribution: {response.status_code}")
        else:
            print(f"ℹ️ No pending contributions to approve")
    else:
        print(f"❌ Failed to get contributions: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Master Kit Approval and Integration Test")
    print("=" * 60)
    
    # First check existing contributions
    check_existing_contributions()
    
    # Then test the full workflow
    test_master_kit_approval_workflow()
    
    print(f"\n🎯 Test Complete!")