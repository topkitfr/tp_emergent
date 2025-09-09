#!/usr/bin/env python3
"""
Test only the endpoints that should work based on correct dependency injection
"""

import requests
import json

BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

def test_working_endpoints():
    print("🧪 TESTING CORRECTLY IMPLEMENTED ENDPOINTS")
    print("=" * 50)
    
    # Login as admin and user
    admin_token = None
    user_token = None
    user_id = None
    
    # Admin login
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        admin_token = data.get("token")
        print(f"✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {response.status_code}")
    
    # User login
    login_data = {"email": USER_EMAIL, "password": USER_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        user_token = data.get("token")
        user_id = data.get("user", {}).get("id")
        print(f"✅ User login successful")
    else:
        print(f"❌ User login failed: {response.status_code}")
    
    if not admin_token or not user_token:
        print("❌ Cannot proceed without tokens")
        return
    
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    print(f"\n🔒 TESTING SECURITY LEVEL 2 ENDPOINTS (Should work)")
    print("-" * 40)
    
    # Test 2FA setup (user)
    response = requests.post(f"{BACKEND_URL}/auth/2fa/setup", headers=user_headers)
    print(f"2FA Setup: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Test password change (user)
    password_data = {"current_password": "wrong", "new_password": "NewPass123!"}
    response = requests.post(f"{BACKEND_URL}/auth/change-password", json=password_data, headers=user_headers)
    print(f"Password Change: {response.status_code} {'✅' if response.status_code == 400 else '❌'} (400 expected for wrong password)")
    
    # Test admin user management (admin)
    if user_id:
        ban_data = {"reason": "Test", "permanent": False}
        response = requests.post(f"{BACKEND_URL}/admin/users/{user_id}/ban", json=ban_data, headers=admin_headers)
        print(f"Admin Ban User: {response.status_code} {'✅' if response.status_code in [200, 400] else '❌'}")
        
        response = requests.post(f"{BACKEND_URL}/admin/users/{user_id}/unban", headers=admin_headers)
        print(f"Admin Unban User: {response.status_code} {'✅' if response.status_code in [200, 400] else '❌'}")
        
        response = requests.get(f"{BACKEND_URL}/admin/users/{user_id}/security", headers=admin_headers)
        print(f"Admin User Security: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    print(f"\n🌐 TESTING BASIC ENDPOINTS")
    print("-" * 40)
    
    # Test basic endpoints that don't require admin
    response = requests.get(f"{BACKEND_URL}/jerseys")
    print(f"Jerseys List: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    response = requests.get(f"{BACKEND_URL}/marketplace/catalog")
    print(f"Marketplace Catalog: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    response = requests.get(f"{BACKEND_URL}/site/mode")
    print(f"Site Mode: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    response = requests.get(f"{BACKEND_URL}/site/access-check")
    print(f"Site Access Check: {response.status_code} {'✅' if response.status_code in [200, 403] else '❌'}")
    
    # Test beta access
    beta_data = {"email": "test@example.com", "first_name": "Test", "last_name": "User"}
    response = requests.post(f"{BACKEND_URL}/beta/request-access", json=beta_data)
    print(f"Beta Request: {response.status_code} {'✅' if response.status_code in [200, 400] else '❌'}")
    
    print(f"\n🚨 TESTING BROKEN ADMIN ENDPOINTS (Expected to fail)")
    print("-" * 40)
    
    # These should fail due to dependency injection issues
    broken_endpoints = [
        "/admin/users",
        "/admin/traffic-stats", 
        "/admin/jerseys/pending",
        "/admin/activities"
    ]
    
    for endpoint in broken_endpoints:
        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=admin_headers)
        print(f"{endpoint}: {response.status_code} {'❌ (Expected)' if response.status_code == 403 else '⚠️ Unexpected'}")

if __name__ == "__main__":
    test_working_endpoints()