#!/usr/bin/env python3
"""
Bilateral Data Integrity Check
Check for TK-MASTER-E096BE and identify all Master Kits that violate bilateral logic
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-collect.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def authenticate():
    """Authenticate and return session"""
    session = requests.Session()
    
    response = session.post(f"{API_BASE}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        session.headers.update({'Authorization': f'Bearer {token}'})
        print(f"✅ Authenticated as {data.get('user', {}).get('name', 'Unknown')}")
        return session
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None

def check_data_integrity():
    """Check data integrity and identify bilateral violations"""
    session = authenticate()
    if not session:
        return
    
    print("\n" + "="*80)
    print("🔍 BILATERAL DATA INTEGRITY CHECK")
    print("="*80)
    
    # Get collection
    response = session.get(f"{API_BASE}/my-collection")
    if response.status_code != 200:
        print(f"❌ Failed to get collection: {response.status_code}")
        return
    
    collection = response.json()
    print(f"📋 Total collection items: {len(collection)}")
    
    # Separate by type
    owned_items = [item for item in collection if item.get('collection_type') == 'owned']
    wanted_items = [item for item in collection if item.get('collection_type') == 'wanted']
    
    print(f"   • Owned items: {len(owned_items)}")
    print(f"   • Wanted items: {len(wanted_items)}")
    
    # Create lookup dictionaries
    owned_kits = {}
    wanted_kits = {}
    
    for item in owned_items:
        kit_id = item['master_kit_id']
        owned_kits[kit_id] = item
    
    for item in wanted_items:
        kit_id = item['master_kit_id']
        wanted_kits[kit_id] = item
    
    # Find bilateral violations
    bilateral_violations = []
    for kit_id in owned_kits.keys():
        if kit_id in wanted_kits:
            bilateral_violations.append({
                'master_kit_id': kit_id,
                'owned_item': owned_kits[kit_id],
                'wanted_item': wanted_kits[kit_id]
            })
    
    print(f"\n🚨 BILATERAL VIOLATIONS FOUND: {len(bilateral_violations)}")
    
    if bilateral_violations:
        print("\nDetailed violation analysis:")
        for i, violation in enumerate(bilateral_violations, 1):
            kit_id = violation['master_kit_id']
            owned_item = violation['owned_item']
            wanted_item = violation['wanted_item']
            
            print(f"\n{i}. Master Kit ID: {kit_id}")
            
            # Get Master Kit details if available
            master_kit = owned_item.get('master_kit') or wanted_item.get('master_kit')
            if master_kit:
                topkit_ref = master_kit.get('topkit_reference', 'Unknown')
                club = master_kit.get('club', 'Unknown')
                season = master_kit.get('season', 'Unknown')
                kit_type = master_kit.get('kit_type', 'Unknown')
                
                print(f"   TopKit Reference: {topkit_ref}")
                print(f"   Kit: {club} {season} {kit_type}")
                
                # Check for TK-MASTER-E096BE specifically
                if 'TK-MASTER-E096BE' in topkit_ref:
                    print(f"   🎯 TARGET KIT FOUND: TK-MASTER-E096BE")
            
            print(f"   Owned item ID: {owned_item.get('id', 'Unknown')}")
            print(f"   Wanted item ID: {wanted_item.get('id', 'Unknown')}")
            print(f"   Owned created: {owned_item.get('created_at', 'Unknown')}")
            print(f"   Wanted created: {wanted_item.get('created_at', 'Unknown')}")
    
    # Check specifically for TK-MASTER-E096BE
    print(f"\n🎯 CHECKING FOR TK-MASTER-E096BE SPECIFICALLY:")
    
    target_found_owned = False
    target_found_wanted = False
    
    for item in collection:
        master_kit = item.get('master_kit', {})
        topkit_ref = master_kit.get('topkit_reference', '')
        
        if 'TK-MASTER-E096BE' in topkit_ref:
            collection_type = item.get('collection_type', 'unknown')
            if collection_type == 'owned':
                target_found_owned = True
                print(f"   ✅ Found in OWNED collection (Item ID: {item.get('id')})")
            elif collection_type == 'wanted':
                target_found_wanted = True
                print(f"   ✅ Found in WANTED collection (Item ID: {item.get('id')})")
    
    if target_found_owned and target_found_wanted:
        print(f"   🚨 CONFIRMED: TK-MASTER-E096BE exists in BOTH collections (bilateral violation)")
    elif target_found_owned:
        print(f"   ℹ️  TK-MASTER-E096BE exists only in OWNED collection")
    elif target_found_wanted:
        print(f"   ℹ️  TK-MASTER-E096BE exists only in WANTED collection")
    else:
        print(f"   ❌ TK-MASTER-E096BE not found in any collection")
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Total bilateral violations: {len(bilateral_violations)}")
    print(f"   • TK-MASTER-E096BE bilateral violation: {'YES' if target_found_owned and target_found_wanted else 'NO'}")
    
    if bilateral_violations:
        print(f"\n💡 CLEANUP NEEDED:")
        print(f"   These {len(bilateral_violations)} Master Kits need manual cleanup to resolve bilateral violations.")
        print(f"   Users should remove from one collection before adding to the other.")

if __name__ == "__main__":
    check_data_integrity()