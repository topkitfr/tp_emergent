#!/usr/bin/env python3
"""
Test to verify admin endpoint issue and create a fix
"""

import requests
import json

BACKEND_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def test_admin_endpoints():
    print("🔧 TESTING ADMIN ENDPOINTS WITH DETAILED DEBUGGING")
    print("=" * 50)
    
    # Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.status_code}")
        return
    
    data = response.json()
    token = data.get("token")
    user_data = data.get("user")
    
    print(f"✅ Admin login successful")
    print(f"Admin role: {user_data.get('role')}")
    print(f"Admin email: {user_data.get('email')}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different admin endpoints to see which ones work
    test_endpoints = [
        ("/admin/users", "GET"),
        ("/admin/traffic-stats", "GET"),
        ("/admin/jerseys/pending", "GET"),
        ("/admin/activities", "GET"),
        ("/admin/beta/requests", "GET"),
        ("/site/mode", "POST", {"mode": "private"}),
        ("/admin/cleanup/database", "POST", {}),
    ]
    
    working_endpoints = []
    failing_endpoints = []
    
    for endpoint_info in test_endpoints:
        endpoint = endpoint_info[0]
        method = endpoint_info[1]
        data = endpoint_info[2] if len(endpoint_info) > 2 else None
        
        print(f"\nTesting {method} {endpoint}:")
        
        try:
            if method == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{BACKEND_URL}{endpoint}", json=data, headers=headers)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                working_endpoints.append(endpoint)
                try:
                    resp_data = response.json()
                    if isinstance(resp_data, list):
                        print(f"✅ Success: {len(resp_data)} items")
                    else:
                        print(f"✅ Success: {resp_data}")
                except:
                    print(f"✅ Success: {response.text[:100]}")
            else:
                failing_endpoints.append((endpoint, response.status_code, response.text))
                print(f"❌ Failed: {response.text}")
                
        except Exception as e:
            failing_endpoints.append((endpoint, "ERROR", str(e)))
            print(f"❌ Exception: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"Working endpoints: {len(working_endpoints)}")
    for endpoint in working_endpoints:
        print(f"  ✅ {endpoint}")
    
    print(f"\nFailing endpoints: {len(failing_endpoints)}")
    for endpoint, status, error in failing_endpoints:
        print(f"  ❌ {endpoint} - {status}: {error[:100]}")

if __name__ == "__main__":
    test_admin_endpoints()