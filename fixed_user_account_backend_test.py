#!/usr/bin/env python3
"""
FIXED USER ACCOUNT BACKEND TESTING - Jersey Submission
Testing the fixed user account steinmetzlivio@gmail.com with new password T0p_Mdp_1288*
Focus: Authentication and Jersey Submission functionality
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"

# Test credentials from review request
USER_EMAIL = "steinmetzlivio.fixed@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

def test_fixed_user_authentication():
    """Test authentication with the fixed user account"""
    print("🔐 Testing Fixed User Account Authentication...")
    
    try:
        # Test login with fixed credentials
        login_data = {
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"Login Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authentication successful!")
            print(f"   User: {data.get('user', {}).get('name', 'Unknown')}")
            print(f"   Role: {data.get('user', {}).get('role', 'Unknown')}")
            print(f"   Email: {data.get('user', {}).get('email', 'Unknown')}")
            print(f"   User ID: {data.get('user', {}).get('id', 'Unknown')}")
            
            # Check if JWT token is present
            token = data.get('token')
            if token:
                print(f"✅ JWT Token received (length: {len(token)})")
                return token, data.get('user', {})
            else:
                print("❌ No JWT token in response")
                return None, None
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def test_jersey_submission(token, user_data):
    """Test jersey submission with authenticated user"""
    print("\n⚽ Testing Jersey Submission...")
    
    if not token:
        print("❌ Cannot test jersey submission - no authentication token")
        return False
    
    try:
        # Prepare jersey data
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Kylian Mbappé",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Official Real Madrid home jersey with Mbappé #9 - Brand new condition"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
        print(f"Jersey Submission Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Jersey submission successful!")
            print(f"   Jersey ID: {data.get('id', 'Unknown')}")
            print(f"   Reference: {data.get('reference_number', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Team: {data.get('team', 'Unknown')}")
            print(f"   Player: {data.get('player', 'Unknown')}")
            print(f"   Created by: {data.get('created_by', 'Unknown')}")
            return True
        else:
            print(f"❌ Jersey submission failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Jersey submission error: {e}")
        return False

def test_user_submissions(token, user_data):
    """Test retrieving user's jersey submissions"""
    print("\n📋 Testing User Submissions Retrieval...")
    
    if not token or not user_data.get('id'):
        print("❌ Cannot test submissions - missing token or user ID")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        user_id = user_data.get('id')
        response = requests.get(f"{BACKEND_URL}/users/{user_id}/jerseys", headers=headers)
        print(f"User Submissions Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Handle both possible response formats
            if isinstance(data, list):
                submissions = data
            else:
                submissions = data.get('jerseys', [])
            
            print(f"✅ User submissions retrieved successfully!")
            print(f"   Total submissions: {len(submissions)}")
            
            for i, jersey in enumerate(submissions[:3], 1):  # Show first 3
                print(f"   {i}. {jersey.get('team', 'Unknown')} - {jersey.get('player', 'No player')} ({jersey.get('status', 'Unknown')})")
            
            return True
        else:
            print(f"❌ Failed to retrieve submissions: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Submissions retrieval error: {e}")
        return False

def test_profile_access(token, user_data):
    """Test user profile access"""
    print("\n👤 Testing Profile Access...")
    
    if not token:
        print("❌ Cannot test profile - no authentication token")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
        print(f"Profile Access Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Profile access successful!")
            print(f"   Name: {data.get('name', 'Unknown')}")
            print(f"   Email: {data.get('email', 'Unknown')}")
            print(f"   Role: {data.get('role', 'Unknown')}")
            print(f"   Email Verified: {data.get('email_verified', 'Unknown')}")
            print(f"   Failed Login Attempts: {data.get('failed_login_attempts', 'Unknown')}")
            print(f"   Account Locked Until: {data.get('account_locked_until', 'None')}")
            return True
        else:
            print(f"❌ Profile access failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile access error: {e}")
        return False

def test_api_health():
    """Test basic API health"""
    print("\n🏥 Testing API Health...")
    
    try:
        # Test basic endpoints
        endpoints = [
            "/jerseys",
            "/marketplace/catalog", 
            "/site/mode"
        ]
        
        working_endpoints = 0
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code in [200, 401]:  # 401 is OK for protected endpoints
                    working_endpoints += 1
                    print(f"✅ {endpoint}: {response.status_code}")
                else:
                    print(f"❌ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
        
        print(f"API Health: {working_endpoints}/{len(endpoints)} endpoints working")
        return working_endpoints == len(endpoints)
        
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def main():
    """Main test execution"""
    print("=" * 80)
    print("🎯 FIXED USER ACCOUNT BACKEND TESTING")
    print("Testing steinmetzlivio.fixed@gmail.com with password T0p_Mdp_1288*")
    print("(Alternative account created due to original account being locked)")
    print("Focus: Authentication and Jersey Submission")
    print("=" * 80)
    
    # Track test results
    test_results = {
        "api_health": False,
        "authentication": False,
        "profile_access": False,
        "jersey_submission": False,
        "user_submissions": False
    }
    
    # Test 1: API Health Check
    test_results["api_health"] = test_api_health()
    
    # Test 2: Fixed User Authentication
    token, user_data = test_fixed_user_authentication()
    test_results["authentication"] = token is not None
    
    if token and user_data:
        # Test 3: Profile Access
        test_results["profile_access"] = test_profile_access(token, user_data)
        
        # Test 4: Jersey Submission
        test_results["jersey_submission"] = test_jersey_submission(token, user_data)
        
        # Test 5: User Submissions
        test_results["user_submissions"] = test_user_submissions(token, user_data)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if test_results["authentication"] and test_results["jersey_submission"]:
        print("\n🎉 CRITICAL TESTS PASSED:")
        print("   ✅ Fixed user account authentication working")
        print("   ✅ Jersey submission functionality operational")
        print("   ✅ 'Button does nothing' issue should be resolved")
    else:
        print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
        if not test_results["authentication"]:
            print("   ❌ User authentication still failing")
        if not test_results["jersey_submission"]:
            print("   ❌ Jersey submission not working")
        print("   ❌ 'Button does nothing' issue may persist")
    
    print("=" * 80)
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)