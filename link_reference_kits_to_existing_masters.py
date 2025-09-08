#!/usr/bin/env python3
"""
Link existing reference kits to current master jerseys for testing
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "topkitfr@gmail.com"  
ADMIN_PASSWORD = "TopKitSecure789#"

def authenticate_admin():
    """Authenticate and get token"""
    try:
        auth_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Admin authenticated")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def get_current_master_jerseys(token):
    """Get current master jerseys"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE}/master-jerseys", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Found {len(data)} master jerseys")
            return data
        else:
            print(f"❌ Failed to get master jerseys")
            return []
            
    except Exception as e:
        print(f"❌ Error getting master jerseys: {e}")
        return []

def get_current_reference_kits(token):
    """Get current reference kits"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE}/reference-kits", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Found {len(data)} reference kits")
            return data
        else:
            print(f"❌ Failed to get reference kits")
            return []
            
    except Exception as e:
        print(f"❌ Error getting reference kits: {e}")
        return []

def update_reference_kit_master_id(token, kit_id, new_master_id):
    """Update a reference kit's master_kit_id"""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Create update data
        update_data = {
            "master_kit_id": new_master_id
        }
        
        response = requests.put(f"{API_BASE}/reference-kits/{kit_id}", json=update_data, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Updated reference kit {kit_id} to link to master {new_master_id}")
            return True
        else:
            print(f"❌ Failed to update reference kit {kit_id}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating reference kit: {e}")
        return False

def main():
    print("🔗 Linking Reference Kits to Existing Master Jerseys")
    print("="*60)
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        return
    
    # Get current data
    master_jerseys = get_current_master_jerseys(token)
    reference_kits = get_current_reference_kits(token)
    
    if not master_jerseys:
        print("❌ No master jerseys found")
        return
    
    if not reference_kits:
        print("❌ No reference kits found")
        return
    
    # Take the first master jersey and link all reference kits to it
    target_master = master_jerseys[0]
    target_master_id = target_master['id']
    team_name = target_master.get('team_info', {}).get('name', 'Unknown Team')
    season = target_master.get('season', 'Unknown')
    
    print(f"\n🎯 Linking all reference kits to: {team_name} {season} (ID: {target_master_id})")
    
    # Update each reference kit
    updated_count = 0
    for kit in reference_kits:
        kit_id = kit['id']
        current_master_id = kit.get('master_kit_id')
        
        if current_master_id != target_master_id:
            success = update_reference_kit_master_id(token, kit_id, target_master_id)
            if success:
                updated_count += 1
        else:
            print(f"✅ Reference kit {kit_id} already linked to correct master")
    
    print(f"\n🎉 Successfully updated {updated_count} reference kits!")
    
    # Test the linking
    print(f"\n🔍 Testing reference kits for master {target_master_id}...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE}/reference-kits?master_kit_id={target_master_id}", headers=headers)
        
        if response.status_code == 200:
            linked_kits = response.json()
            print(f"✅ Found {len(linked_kits)} reference kits linked to the master jersey")
            
            if linked_kits:
                print("\n📋 Linked reference kits:")
                for kit in linked_kits:
                    player_name = kit.get('available_prints', [{}])[0].get('player_name', 'No Player')  
                    reference = kit.get('topkit_reference', 'No Reference')
                    print(f"   - {reference}: {player_name}")
        else:
            print(f"❌ Failed to test reference kits: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing reference kits: {e}")
    
    print(f"\n🎉 Reference kits are now linked!")
    print("Now you can test:")
    print(f"1. Go to Kit Area and click on '{team_name} {season}'")
    print("2. You should see 'Other Versions' section with the linked reference kits")
    print("3. Test 'View All Versions' and individual version pages")

if __name__ == "__main__":
    main()