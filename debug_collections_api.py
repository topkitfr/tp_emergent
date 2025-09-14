#!/usr/bin/env python3
"""
DEBUG COLLECTIONS API RESPONSE FORMAT
====================================

Quick debug script to understand the actual API response format
"""

import requests
import json

# Configuration
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

def debug_api():
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
    
    # Test owned collections
    print("\n📦 Testing owned collections...")
    owned_response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/owned", headers=headers)
    print(f"Status: {owned_response.status_code}")
    
    if owned_response.status_code == 200:
        owned_data = owned_response.json()
        print("Response structure:")
        print(f"Type: {type(owned_data)}")
        print(f"Keys: {list(owned_data.keys()) if isinstance(owned_data, dict) else 'Not a dict'}")
        print("Raw response:")
        print(json.dumps(owned_data, indent=2)[:1000] + "..." if len(str(owned_data)) > 1000 else json.dumps(owned_data, indent=2))
    else:
        print(f"Error: {owned_response.text}")
    
    # Test wanted collections
    print("\n🎯 Testing wanted collections...")
    wanted_response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/wanted", headers=headers)
    print(f"Status: {wanted_response.status_code}")
    
    if wanted_response.status_code == 200:
        wanted_data = wanted_response.json()
        print("Response structure:")
        print(f"Type: {type(wanted_data)}")
        print(f"Keys: {list(wanted_data.keys()) if isinstance(wanted_data, dict) else 'Not a dict'}")
        print("Raw response:")
        print(json.dumps(wanted_data, indent=2)[:1000] + "..." if len(str(wanted_data)) > 1000 else json.dumps(wanted_data, indent=2))
    else:
        print(f"Error: {wanted_response.text}")

if __name__ == "__main__":
    debug_api()