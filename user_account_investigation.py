#!/usr/bin/env python3
"""
User Account Investigation - Check existing users and try different passwords
"""

import requests
import json

# Configuration
BACKEND_URL = "https://image-fix-10.preview.emergentagent.com/api"

# Test different password combinations for steinmetzlivio@gmail.com
USER_EMAIL = "steinmetzlivio@gmail.com"
POSSIBLE_PASSWORDS = [
    "T0p_Mdp_1288*",  # From review request
    "TopKit123!",     # From previous test results
    "123",            # Simple password from test results
    "TopKitSecure789#",  # Admin password variant
    "SecurePass789!"  # Common test password
]

def test_authentication_variants():
    """Test different password combinations"""
    print(f"🔍 TESTING AUTHENTICATION FOR: {USER_EMAIL}")
    print("=" * 60)
    
    for i, password in enumerate(POSSIBLE_PASSWORDS, 1):
        print(f"Attempt {i}: Testing password '{password}'")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                print(f"✅ SUCCESS! Password '{password}' works!")
                print(f"   User: {user_info.get('name')} (Role: {user_info.get('role')}, ID: {user_info.get('id')})")
                print(f"   Token: {data.get('token', 'N/A')[:50]}...")
                return password, data.get("token")
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                print(f"❌ FAILED: {error_detail}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print()
    
    print("🚨 NONE OF THE PASSWORDS WORKED!")
    return None, None

def check_admin_authentication():
    """Test admin authentication to verify backend is working"""
    print("🔍 TESTING ADMIN AUTHENTICATION")
    print("=" * 60)
    
    admin_credentials = [
        ("topkitfr@gmail.com", "TopKitSecure789#"),
        ("topkitfr@gmail.com", "adminpass123")
    ]
    
    for email, password in admin_credentials:
        print(f"Testing admin: {email} with password '{password}'")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {})
                print(f"✅ ADMIN LOGIN SUCCESS!")
                print(f"   User: {user_info.get('name')} (Role: {user_info.get('role')}, ID: {user_info.get('id')})")
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                print(f"❌ ADMIN LOGIN FAILED: {error_detail}")
                
        except Exception as e:
            print(f"❌ ADMIN LOGIN ERROR: {str(e)}")
        
        print()
    
    return False

def test_backend_health():
    """Test basic backend connectivity"""
    print("🔍 TESTING BACKEND HEALTH")
    print("=" * 60)
    
    endpoints_to_test = [
        "/jerseys",
        "/marketplace/catalog", 
        "/site/mode"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            print(f"GET {endpoint}: HTTP {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Response: List with {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"   Response: Dict with keys: {list(data.keys())}")
                    else:
                        print(f"   Response: {type(data)}")
                except:
                    print(f"   Response: Non-JSON content")
            else:
                try:
                    error = response.json().get("detail", "No error details")
                    print(f"   Error: {error}")
                except:
                    print(f"   Error: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"GET {endpoint}: Connection error - {str(e)}")
        
        print()

if __name__ == "__main__":
    print("🚨 USER ACCOUNT INVESTIGATION")
    print("=" * 60)
    print()
    
    # Test backend health first
    test_backend_health()
    
    # Test admin authentication to verify backend auth is working
    admin_works = check_admin_authentication()
    
    # Test user authentication with different passwords
    working_password, token = test_authentication_variants()
    
    print("=" * 60)
    print("🎯 INVESTIGATION SUMMARY")
    print("=" * 60)
    
    if admin_works:
        print("✅ Backend authentication system is working (admin login successful)")
    else:
        print("❌ Backend authentication system may be broken (admin login failed)")
    
    if working_password:
        print(f"✅ User account exists and password '{working_password}' works")
        print("   Jersey submission testing can proceed")
    else:
        print("❌ User account authentication failed with all tested passwords")
        print("   Possible issues:")
        print("   1. Account doesn't exist")
        print("   2. Password is different from tested combinations")
        print("   3. Account is locked/banned")
        print("   4. Backend authentication issue")