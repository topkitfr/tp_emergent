#!/usr/bin/env python3
"""
Kit Store Comprehensive Validation - Master Jerseys Fix
Final validation of the Kit Store after master_kits → master_jerseys migration
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-tracker.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def authenticate():
    """Authenticate and return session with token"""
    session = requests.Session()
    auth_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{API_BASE}/auth/login", json=auth_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })
        return session
    return None

def main():
    print("🔍 Kit Store Comprehensive Validation - Master Jerseys Fix")
    print("=" * 65)
    
    session = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # 1. Verify Kit Store endpoint works
    print("\n1️⃣ Testing Kit Store Endpoint (GET /api/vestiaire)")
    vestiaire_response = session.get(f"{API_BASE}/vestiaire")
    
    if vestiaire_response.status_code != 200:
        print(f"❌ Kit Store endpoint failed: {vestiaire_response.status_code}")
        return
    
    reference_kits = vestiaire_response.json()
    print(f"✅ Kit Store endpoint working - Found {len(reference_kits)} reference kits")
    
    if not reference_kits:
        print("⚠️  No reference kits found in Kit Store")
        return
    
    # 2. Analyze reference kit data structure
    print("\n2️⃣ Analyzing Reference Kit Data Structure")
    kit = reference_kits[0]
    
    print(f"   TopKit Reference: {kit.get('topkit_reference', 'Missing')}")
    print(f"   Master Kit ID: {kit.get('master_kit_id', 'Missing')}")
    
    # Check for master jersey information (could be master_jersey_info or master_kit_info)
    master_jersey_data = None
    field_name = None
    
    if 'master_jersey_info' in kit and kit['master_jersey_info']:
        master_jersey_data = kit['master_jersey_info']
        field_name = 'master_jersey_info'
    elif 'master_kit_info' in kit and kit['master_kit_info']:
        master_jersey_data = kit['master_kit_info']
        field_name = 'master_kit_info'
    
    if master_jersey_data:
        print(f"✅ Master jersey data found (field: {field_name})")
        print(f"   Season: {master_jersey_data.get('season', 'Missing')}")
        print(f"   Jersey Type: {master_jersey_data.get('jersey_type', 'Missing')}")
        print(f"   Team ID: {master_jersey_data.get('team_id', 'Missing')}")
    else:
        print("❌ No master jersey data found")
        return
    
    # 3. Verify master jersey exists in master-jerseys collection
    print("\n3️⃣ Verifying Master Jersey Collection Integration")
    master_kit_id = kit.get('master_kit_id')
    
    if master_kit_id:
        # Check if this ID exists in master-jerseys collection
        jerseys_response = session.get(f"{API_BASE}/master-jerseys")
        if jerseys_response.status_code == 200:
            master_jerseys = jerseys_response.json()
            matching_jersey = None
            
            for jersey in master_jerseys:
                if jersey['id'] == master_kit_id:
                    matching_jersey = jersey
                    break
            
            if matching_jersey:
                print(f"✅ Reference kit properly linked to master jersey")
                print(f"   Master Jersey ID: {matching_jersey['id']}")
                print(f"   Season: {matching_jersey.get('season')}")
                print(f"   Type: {matching_jersey.get('jersey_type')}")
                
                # Check team information
                team_info = matching_jersey.get('team_info', {})
                if team_info and team_info.get('name'):
                    print(f"   Team: {team_info['name']}")
                    print("✅ Team information properly populated")
                else:
                    print("⚠️  Team information missing in master jersey")
            else:
                print(f"❌ Reference kit master_kit_id ({master_kit_id}) not found in master-jerseys collection")
        else:
            print(f"❌ Failed to fetch master-jerseys: {jerseys_response.status_code}")
    
    # 4. Verify data consistency
    print("\n4️⃣ Data Consistency Validation")
    
    # Check if master_kits collection is empty (should be after migration)
    master_kits_response = session.get(f"{API_BASE}/master-kits")
    if master_kits_response.status_code == 200:
        master_kits = master_kits_response.json()
        master_kits_count = len(master_kits) if isinstance(master_kits, list) else len(master_kits.get('master_kits', []))
        
        if master_kits_count == 0:
            print("✅ Master kits collection is empty (migration completed)")
        else:
            print(f"⚠️  Master kits collection still has {master_kits_count} items")
    
    # Check master-jerseys collection
    if jerseys_response.status_code == 200:
        master_jerseys_count = len(master_jerseys)
        print(f"✅ Master jerseys collection has {master_jerseys_count} items")
    
    # 5. Final assessment
    print("\n🎯 Final Assessment")
    print("=" * 30)
    
    issues = []
    successes = []
    
    # Check what we found
    if len(reference_kits) > 0:
        successes.append("Reference kits appear in Kit Store")
    else:
        issues.append("No reference kits in Kit Store")
    
    if master_jersey_data:
        successes.append("Reference kits have master jersey data")
        if field_name == 'master_kit_info':
            issues.append("Using legacy field name 'master_kit_info' instead of 'master_jersey_info'")
    else:
        issues.append("Reference kits missing master jersey data")
    
    if matching_jersey:
        successes.append("Reference kits properly linked to master jerseys collection")
    else:
        issues.append("Reference kits not properly linked to master jerseys")
    
    if team_info and team_info.get('name'):
        successes.append("Team information properly populated")
    else:
        issues.append("Team information missing or incomplete")
    
    print("✅ Successes:")
    for success in successes:
        print(f"   • {success}")
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"   • {issue}")
    
    # Overall status
    success_rate = len(successes) / (len(successes) + len(issues)) * 100
    
    if success_rate >= 90:
        print(f"\n🎉 EXCELLENT: Kit Store master jerseys fix is working great! ({success_rate:.0f}% success)")
    elif success_rate >= 75:
        print(f"\n✅ GOOD: Kit Store fix is mostly working with minor issues ({success_rate:.0f}% success)")
    else:
        print(f"\n❌ NEEDS ATTENTION: Kit Store fix has significant issues ({success_rate:.0f}% success)")

if __name__ == "__main__":
    main()