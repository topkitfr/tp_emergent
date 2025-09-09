#!/usr/bin/env python3
"""
Admin Authorization Diagnostic Test
"""

import requests
import json
import jwt

BACKEND_URL = "https://jersey-tracker.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def decode_jwt_token(token):
    """Decode JWT token to inspect contents"""
    try:
        # Decode without verification to inspect contents
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        return f"Error decoding token: {e}"

def test_admin_auth():
    print("🔍 ADMIN AUTHORIZATION DIAGNOSTIC")
    print("=" * 40)
    
    # Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    data = response.json()
    token = data.get("token")
    user_data = data.get("user")
    
    print(f"✅ Admin login successful")
    print(f"User data: {json.dumps(user_data, indent=2)}")
    print(f"Token: {token[:50]}...")
    
    # Decode token
    decoded_token = decode_jwt_token(token)
    print(f"Decoded token: {decoded_token}")
    
    # Test profile endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
    print(f"\nProfile endpoint: {response.status_code}")
    if response.status_code == 200:
        profile_data = response.json()
        print(f"Profile data: {json.dumps(profile_data, indent=2)}")
    else:
        print(f"Profile error: {response.text}")
    
    # Test admin endpoints with detailed error info
    admin_endpoints = [
        "/admin/users",
        "/admin/traffic-stats", 
        "/admin/jerseys/pending",
        "/site/mode"
    ]
    
    for endpoint in admin_endpoints:
        print(f"\nTesting {endpoint}:")
        if endpoint == "/site/mode" and "POST" in endpoint:
            response = requests.post(f"{BACKEND_URL}{endpoint}", 
                                   json={"mode": "private"}, headers=headers)
        else:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            try:
                data = response.json()
                print(f"Success: {len(data) if isinstance(data, list) else 'OK'}")
            except:
                print(f"Success: {response.text[:100]}")

if __name__ == "__main__":
    test_admin_auth()