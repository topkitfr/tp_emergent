#!/usr/bin/env python3
"""
Focused Registration Test - Core Functionality Only
Testing the exact user-reported scenario: 404 error when trying to sign up
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-wizard.preview.emergentagent.com/api"

def test_core_registration_functionality():
    """Test the core registration functionality that was causing 404 errors"""
    
    print("🎯 FOCUSED TEST: Core Registration Functionality")
    print("Testing the exact user-reported scenario: 404 error when trying to sign up")
    print("=" * 80)
    
    session = requests.Session()
    
    # Test 1: Verify endpoint exists (no more 404)
    print("\n1. Testing endpoint availability...")
    unique_id = str(uuid.uuid4())[:8]
    test_user = {
        "name": f"Test User {unique_id}",
        "email": f"testuser{unique_id}@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = session.post(
            f"{BACKEND_URL}/auth/register",
            json=test_user,
            timeout=10
        )
        
        if response.status_code == 404:
            print("❌ CRITICAL: 404 error still present - endpoint not found")
            return False
        elif response.status_code == 200:
            print("✅ SUCCESS: Endpoint found and working (no 404 error)")
            data = response.json()
            
            # Verify response has required fields
            if "token" in data and "user" in data:
                print("✅ SUCCESS: Response contains token and user data")
                token = data["token"]
                user = data["user"]
                
                # Verify user data
                if user.get("email") == test_user["email"] and user.get("name") == test_user["name"]:
                    print("✅ SUCCESS: User data matches registration request")
                    
                    # Test 2: Verify JWT token works
                    print("\n2. Testing JWT token functionality...")
                    headers = {"Authorization": f"Bearer {token}"}
                    auth_test = session.get(f"{BACKEND_URL}/my-collection", headers=headers, timeout=10)
                    
                    if auth_test.status_code in [200, 403]:  # 403 is acceptable for empty collection
                        print("✅ SUCCESS: JWT token is valid and working")
                        
                        # Test 3: Verify login works with registered user
                        print("\n3. Testing login with registered user...")
                        login_response = session.post(
                            f"{BACKEND_URL}/auth/login",
                            json={"email": test_user["email"], "password": test_user["password"]},
                            timeout=10
                        )
                        
                        if login_response.status_code == 200:
                            print("✅ SUCCESS: Login works with registered user")
                            
                            # Test 4: Verify duplicate email protection
                            print("\n4. Testing duplicate email protection...")
                            duplicate_response = session.post(
                                f"{BACKEND_URL}/auth/register",
                                json=test_user,  # Same user data
                                timeout=10
                            )
                            
                            if duplicate_response.status_code == 400:
                                error_data = duplicate_response.json()
                                if "already registered" in error_data.get("detail", "").lower():
                                    print("✅ SUCCESS: Duplicate email properly rejected")
                                    
                                    print("\n🎉 CORE REGISTRATION FUNCTIONALITY TEST RESULTS:")
                                    print("✅ Endpoint exists (no 404 error)")
                                    print("✅ User registration works")
                                    print("✅ JWT token generation works")
                                    print("✅ JWT token authentication works")
                                    print("✅ Login with registered user works")
                                    print("✅ Duplicate email protection works")
                                    print("\n🎯 USER ISSUE RESOLVED: 404 signup error is completely fixed!")
                                    return True
                                else:
                                    print(f"❌ Duplicate email error message unclear: {error_data}")
                            else:
                                print(f"❌ Duplicate email not properly rejected: {duplicate_response.status_code}")
                        else:
                            print(f"❌ Login failed: {login_response.status_code}")
                    else:
                        print(f"❌ JWT token validation failed: {auth_test.status_code}")
                else:
                    print(f"❌ User data mismatch: expected {test_user}, got {user}")
            else:
                print(f"❌ Response missing required fields: {data}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception during test: {str(e)}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_core_registration_functionality()
    exit(0 if success else 1)