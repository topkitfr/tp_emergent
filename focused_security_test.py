#!/usr/bin/env python3
"""
Rate Limiting Focused Test - Testing account creation rate limiting more precisely
"""

import requests
import json
import time
import uuid
from datetime import datetime

BASE_URL = "https://image-fix-10.preview.emergentagent.com/api"

def test_rate_limiting_focused():
    """Test rate limiting with proper timing and fresh session"""
    print("🔍 FOCUSED RATE LIMITING TEST")
    print("Testing 3 accounts per hour per IP limit...")
    
    session = requests.Session()
    accounts_created = 0
    rate_limit_hit = False
    
    for i in range(5):  # Try to create 5 accounts
        test_email = f"ratelimit_focused_{i}_{uuid.uuid4().hex[:8]}@test.com"
        
        try:
            print(f"\nAttempt {i+1}: Creating account {test_email}")
            
            response = session.post(f"{BASE_URL}/auth/register", json={
                "email": test_email,
                "password": "ValidPass456!",
                "name": f"Rate Limit Test {i+1}"
            })
            
            print(f"Response: HTTP {response.status_code}")
            
            if response.status_code == 200:
                accounts_created += 1
                print(f"✅ Account {i+1} created successfully")
                data = response.json()
                print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
                
            elif response.status_code == 429:
                rate_limit_hit = True
                print(f"🚫 Rate limit hit after {accounts_created} accounts")
                print(f"   Response: {response.text}")
                break
                
            elif response.status_code == 400:
                print(f"❌ Validation error: {response.text}")
                # This might be due to duplicate email or other validation
                
            else:
                print(f"❓ Unexpected response: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
            # Small delay between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error creating account {i+1}: {e}")
    
    print(f"\n📊 RATE LIMITING TEST RESULTS:")
    print(f"   Accounts successfully created: {accounts_created}")
    print(f"   Rate limit triggered: {'Yes' if rate_limit_hit else 'No'}")
    
    if rate_limit_hit and accounts_created <= 3:
        print("✅ Rate limiting is working correctly!")
        return True
    elif accounts_created > 3 and not rate_limit_hit:
        print("❌ Rate limiting is NOT working - too many accounts created")
        return False
    else:
        print("⚠️ Rate limiting test results are inconclusive")
        return False

def test_email_verification_workflow():
    """Test complete email verification workflow"""
    print("\n📧 FOCUSED EMAIL VERIFICATION TEST")
    
    session = requests.Session()
    test_email = f"emailtest_{uuid.uuid4().hex[:8]}@test.com"
    
    try:
        # Step 1: Register account
        print(f"Step 1: Registering account {test_email}")
        response = session.post(f"{BASE_URL}/auth/register", json={
            "email": test_email,
            "password": "ValidPass456!",
            "name": "Email Test User"
        })
        
        if response.status_code != 200:
            print(f"❌ Registration failed: HTTP {response.status_code}: {response.text}")
            return False
        
        data = response.json()
        user_data = data.get("user", {})
        
        print(f"✅ Account registered successfully")
        print(f"   Email verified: {user_data.get('email_verified')}")
        print(f"   User ID: {user_data.get('id')}")
        
        # Step 2: Try to login before verification
        print(f"\nStep 2: Attempting login before email verification")
        login_response = session.post(f"{BASE_URL}/auth/login", json={
            "email": test_email,
            "password": "ValidPass456!"
        })
        
        if login_response.status_code == 403:
            print("✅ Login correctly blocked for unverified email")
        else:
            print(f"❌ Login should be blocked but got: HTTP {login_response.status_code}")
            return False
        
        # Step 3: Verify email if token available
        verification_link = data.get("dev_verification_link")
        if verification_link and "token=" in verification_link:
            token = verification_link.split("token=")[1]
            print(f"\nStep 3: Verifying email with token")
            
            verify_response = session.post(f"{BASE_URL}/auth/verify-email", params={"token": token})
            
            if verify_response.status_code == 200:
                print("✅ Email verification successful")
                verify_data = verify_response.json()
                print(f"   JWT token received: {verify_data.get('token', 'N/A')[:20]}...")
                
                # Step 4: Try login after verification
                print(f"\nStep 4: Attempting login after email verification")
                login_after_verify = session.post(f"{BASE_URL}/auth/login", json={
                    "email": test_email,
                    "password": "ValidPass456!"
                })
                
                if login_after_verify.status_code == 200:
                    print("✅ Login successful after email verification")
                    return True
                else:
                    print(f"❌ Login failed after verification: HTTP {login_after_verify.status_code}")
                    return False
            else:
                print(f"❌ Email verification failed: HTTP {verify_response.status_code}")
                return False
        else:
            print("⚠️ No verification token available for testing")
            return False
            
    except Exception as e:
        print(f"❌ Email verification test error: {e}")
        return False

if __name__ == "__main__":
    print("🔐 TOPKIT SECURITY FOCUSED TESTING")
    print("="*50)
    
    # Test rate limiting
    rate_limit_success = test_rate_limiting_focused()
    
    # Test email verification
    email_verify_success = test_email_verification_workflow()
    
    print("\n" + "="*50)
    print("📋 FOCUSED TEST SUMMARY:")
    print(f"   Rate Limiting: {'✅ PASS' if rate_limit_success else '❌ FAIL'}")
    print(f"   Email Verification: {'✅ PASS' if email_verify_success else '❌ FAIL'}")
    
    if rate_limit_success and email_verify_success:
        print("\n🎉 All focused security tests PASSED!")
    else:
        print("\n⚠️ Some focused security tests FAILED!")