#!/usr/bin/env python3
"""
DEBUG MASTER JERSEY DATA
========================

Check the master jersey data to see why team_info is empty
"""

import requests
import json

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

def debug_master_jersey():
    # Authenticate
    print("🔐 Authenticating...")
    auth_response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        return
        
    auth_data = auth_response.json()
    token = auth_data.get("token")
    user_id = auth_data.get("user", {}).get("id")
    
    print(f"✅ Authenticated as user ID: {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get the master jersey ID from collections
    print("\n📦 Getting collection to find master jersey ID...")
    owned_response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/owned", headers=headers)
    
    if owned_response.status_code == 200:
        collections = owned_response.json()
        if collections:
            master_jersey_id = collections[0].get("master_jersey", {}).get("id")
            print(f"Master Jersey ID: {master_jersey_id}")
            
            # Try to get master jersey directly
            print(f"\n🎯 Trying to get master jersey {master_jersey_id} directly...")
            master_jersey_response = requests.get(f"{BACKEND_URL}/master-jerseys/{master_jersey_id}", headers=headers)
            
            if master_jersey_response.status_code == 200:
                master_jersey_data = master_jersey_response.json()
                print("Master Jersey Data:")
                print(json.dumps(master_jersey_data, indent=2))
            else:
                print(f"❌ Failed to get master jersey: {master_jersey_response.status_code}")
                print(master_jersey_response.text)
        else:
            print("❌ No collections found")
    else:
        print(f"❌ Failed to get collections: {owned_response.status_code}")

if __name__ == "__main__":
    debug_master_jersey()