#!/usr/bin/env python3
"""
URGENT ADMIN CONNECTION DIAGNOSIS TEST
Diagnostic rapide du problème de connexion admin avec topkitfr@gmail.com
"""

import requests
import json
import sys
from datetime import datetime

# Configuration from .env files
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"

# Possible passwords to test
POSSIBLE_PASSWORDS = [
    "TopKitSecure789#",
    "adminpass123", 
    "TopKit123!",
    "admin123",
    "topkit123",
    "password123"
]

def test_api_health():
    """Test if backend API is accessible"""
    print("🔍 TESTING API HEALTH...")
    try:
        response = requests.get(f"{BACKEND_URL}/jerseys", timeout=10)
        print(f"✅ API Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Health Failed: {e}")
        return False

def test_admin_login(email, password):
    """Test admin login with specific credentials"""
    try:
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                user_info = data.get("user", {})
                print(f"✅ LOGIN SUCCESS with {password}")
                print(f"   User: {user_info.get('name', 'Unknown')}")
                print(f"   Role: {user_info.get('role', 'Unknown')}")
                print(f"   ID: {user_info.get('id', 'Unknown')}")
                return True, data["token"], user_info
            elif data.get("requires_2fa"):
                print(f"🔐 2FA REQUIRED with {password}")
                return "2fa", data.get("temp_token"), {}
        else:
            print(f"❌ LOGIN FAILED with {password}: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ LOGIN ERROR with {password}: {e}")
    
    return False, None, {}

def test_database_admin_account():
    """Check if admin account exists in database via API"""
    print("\n🔍 CHECKING DATABASE FOR ADMIN ACCOUNT...")
    
    # Try to get user info through different endpoints
    endpoints_to_test = [
        "/users/search?query=topkit",
        "/admin/users",  # Requires auth but might give info about existence
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

def test_with_valid_token(token):
    """Test protected endpoints with valid token"""
    print(f"\n🔍 TESTING PROTECTED ENDPOINTS WITH TOKEN...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/auth/profile",
        "/admin/users", 
        "/admin/traffic-stats",
        "/notifications"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if endpoint == "/auth/profile":
                    print(f"      Profile: {data.get('name')} ({data.get('role')})")
                elif endpoint == "/admin/users":
                    print(f"      Users found: {len(data) if isinstance(data, list) else 'N/A'}")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

def main():
    print("🚨 URGENT ADMIN CONNECTION DIAGNOSIS")
    print("=" * 50)
    print(f"Testing admin connection for: {ADMIN_EMAIL}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Time: {datetime.now()}")
    print("=" * 50)
    
    # 1. Test API Health
    if not test_api_health():
        print("❌ CRITICAL: Backend API is not accessible!")
        return
    
    # 2. Test database for admin account
    test_database_admin_account()
    
    # 3. Test admin login with different passwords
    print(f"\n🔍 TESTING ADMIN LOGIN WITH DIFFERENT PASSWORDS...")
    successful_login = False
    valid_token = None
    user_info = {}
    
    for password in POSSIBLE_PASSWORDS:
        print(f"\n   Testing password: {password}")
        success, token, user = test_admin_login(ADMIN_EMAIL, password)
        
        if success == True:
            successful_login = True
            valid_token = token
            user_info = user
            break
        elif success == "2fa":
            print(f"   🔐 2FA enabled - would need TOTP code")
            successful_login = "2fa"
            break
    
    # 4. If login successful, test protected endpoints
    if successful_login == True and valid_token:
        test_with_valid_token(valid_token)
    
    # 5. Summary
    print("\n" + "=" * 50)
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if successful_login == True:
        print("✅ ADMIN LOGIN: SUCCESS")
        print(f"   Working password found")
        print(f"   User: {user_info.get('name', 'Unknown')}")
        print(f"   Role: {user_info.get('role', 'Unknown')}")
        print("   🎯 SOLUTION: User can connect with working password")
    elif successful_login == "2fa":
        print("🔐 ADMIN LOGIN: 2FA REQUIRED")
        print("   Password is correct but 2FA code needed")
        print("   🎯 SOLUTION: User needs to provide TOTP code")
    else:
        print("❌ ADMIN LOGIN: FAILED")
        print("   None of the tested passwords work")
        print("   🎯 POSSIBLE ISSUES:")
        print("     - Password changed recently")
        print("     - Account doesn't exist")
        print("     - Database connection issues")
        print("     - Environment mismatch (preview vs production)")
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    if successful_login != True:
        print("1. Check if admin account exists in database")
        print("2. Verify correct backend URL is being used")
        print("3. Check for recent password changes")
        print("4. Consider password reset if needed")
    else:
        print("1. Admin connection is working properly")
        print("2. User should use the working password")

if __name__ == "__main__":
    main()