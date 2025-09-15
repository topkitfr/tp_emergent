#!/usr/bin/env python3
"""
Cleanup Bilateral Violations Script
Remove TK-MASTER-E096BE from wanted collection to resolve bilateral logic violation
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def authenticate():
    """Authenticate and return session"""
    session = requests.Session()
    
    print(f"🔐 Authenticating as {ADMIN_EMAIL}...")
    response = session.post(f"{API_BASE}/auth/login", json={
        "email": ADMIN_EMAIL,  
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        user_info = data.get('user', {})
        
        session.headers.update({'Authorization': f'Bearer {token}'})
        print(f"✅ Authenticated as {user_info.get('name')} ({user_info.get('role')})")
        return session
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None

def cleanup_bilateral_violations():
    """Clean up bilateral violations"""
    session = authenticate()
    if not session:
        return
    
    print("\n" + "="*80)
    print("🧹 CLEANING UP BILATERAL VIOLATIONS")
    print("="*80)
    
    # Get collection
    print("\n📋 Getting current collection...")
    response = session.get(f"{API_BASE}/my-collection")
    if response.status_code != 200:
        print(f"❌ Failed to get collection: {response.status_code}")
        return
    
    collection = response.json()
    print(f"✅ Retrieved {len(collection)} collection items")
    
    # Find TK-MASTER-E096BE entries
    target_entries = []
    for item in collection:
        master_kit = item.get('master_kit', {})
        topkit_ref = master_kit.get('topkit_reference', '')
        
        if 'TK-MASTER-E096BE' in topkit_ref:
            target_entries.append({
                'item_id': item.get('id'),
                'master_kit_id': item.get('master_kit_id'),
                'collection_type': item.get('collection_type'),
                'created_at': item.get('created_at'),
                'topkit_reference': topkit_ref,
                'kit_name': f"{master_kit.get('club', 'Unknown')} {master_kit.get('season', 'Unknown')} {master_kit.get('kit_type', 'Unknown')}"
            })
    
    print(f"\n🎯 Found {len(target_entries)} entries for TK-MASTER-E096BE:")
    for i, entry in enumerate(target_entries, 1):
        print(f"   [{i}] ID: {entry['item_id']}")
        print(f"       Type: {entry['collection_type']}")
        print(f"       Created: {entry['created_at']}")
        print(f"       Kit: {entry['kit_name']}")
    
    # Check for bilateral violation
    owned_entries = [e for e in target_entries if e['collection_type'] == 'owned']
    wanted_entries = [e for e in target_entries if e['collection_type'] == 'wanted']
    
    if len(owned_entries) > 0 and len(wanted_entries) > 0:
        print(f"\n🚨 BILATERAL VIOLATION CONFIRMED!")
        print(f"   • Found in OWNED collection: {len(owned_entries)} entries")
        print(f"   • Found in WANTED collection: {len(wanted_entries)} entries")
        
        # Remove from wanted collection (keep the older owned entry)
        if wanted_entries:
            wanted_entry = wanted_entries[0]  # Take first wanted entry
            item_id_to_remove = wanted_entry['item_id']
            
            print(f"\n🗑️  Removing from WANTED collection...")
            print(f"   Item ID to remove: {item_id_to_remove}")
            print(f"   Reason: Bilateral logic violation - keeping older OWNED entry")
            
            # DELETE the item
            delete_response = session.delete(f"{API_BASE}/my-collection/{item_id_to_remove}")
            
            if delete_response.status_code == 200:
                print(f"✅ Successfully removed TK-MASTER-E096BE from wanted collection")
                print(f"   Response: {delete_response.json().get('message', 'Item removed')}")
                
                # Verify the fix
                print(f"\n🔍 Verifying bilateral violation is resolved...")
                verify_response = session.get(f"{API_BASE}/my-collection")
                if verify_response.status_code == 200:
                    verify_collection = verify_response.json()
                    
                    # Check if TK-MASTER-E096BE still exists in both types
                    verify_owned = []
                    verify_wanted = []
                    
                    for item in verify_collection:
                        master_kit = item.get('master_kit', {})
                        topkit_ref = master_kit.get('topkit_reference', '')
                        
                        if 'TK-MASTER-E096BE' in topkit_ref:
                            if item.get('collection_type') == 'owned':
                                verify_owned.append(item)
                            elif item.get('collection_type') == 'wanted':
                                verify_wanted.append(item)
                    
                    print(f"   • TK-MASTER-E096BE in OWNED: {len(verify_owned)} entries")
                    print(f"   • TK-MASTER-E096BE in WANTED: {len(verify_wanted)} entries")
                    
                    if len(verify_owned) > 0 and len(verify_wanted) == 0:
                        print(f"✅ BILATERAL VIOLATION RESOLVED!")
                        print(f"   TK-MASTER-E096BE now exists only in OWNED collection")
                    elif len(verify_owned) == 0 and len(verify_wanted) > 0:
                        print(f"✅ BILATERAL VIOLATION RESOLVED!")
                        print(f"   TK-MASTER-E096BE now exists only in WANTED collection")
                    else:
                        print(f"⚠️  Bilateral violation may still exist")
                
            else:
                print(f"❌ Failed to remove item: {delete_response.status_code}")
                print(f"   Response: {delete_response.text}")
                
    elif len(target_entries) == 0:
        print(f"ℹ️  TK-MASTER-E096BE not found in user's collection")
    else:
        print(f"ℹ️  No bilateral violation found for TK-MASTER-E096BE")
        if owned_entries:
            print(f"   Exists only in OWNED collection")
        if wanted_entries:
            print(f"   Exists only in WANTED collection")
    
    print(f"\n✅ CLEANUP COMPLETE")

if __name__ == "__main__":
    cleanup_bilateral_violations()