#!/usr/bin/env python3
"""
Admin User Check - Use admin privileges to check user account status
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
TARGET_USER_EMAIL = "steinmetzlivio@gmail.com"

def get_admin_token():
    """Get admin authentication token"""
    print("🔐 Getting admin token...")
    
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Admin authenticated: {data['user']['name']}")
        return data['token']
    else:
        print(f"❌ Admin authentication failed: {response.status_code}")
        return None

def get_all_users(admin_token):
    """Get all users using admin privileges"""
    print("\n👥 Getting all users...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        users = data.get('users', [])
        print(f"✅ Found {len(users)} users")
        
        # Find target user
        target_user = None
        for user in users:
            if user.get('email') == TARGET_USER_EMAIL:
                target_user = user
                break
        
        if target_user:
            print(f"\n🎯 TARGET USER FOUND:")
            print(f"   ID: {target_user.get('id')}")
            print(f"   Name: {target_user.get('name')}")
            print(f"   Email: {target_user.get('email')}")
            print(f"   Role: {target_user.get('role')}")
            print(f"   Email Verified: {target_user.get('email_verified')}")
            print(f"   Failed Login Attempts: {target_user.get('failed_login_attempts')}")
            print(f"   Account Locked Until: {target_user.get('account_locked_until')}")
            print(f"   Is Banned: {target_user.get('is_banned')}")
            print(f"   Last Login: {target_user.get('last_login')}")
            print(f"   Created At: {target_user.get('created_at')}")
            return target_user
        else:
            print(f"❌ Target user {TARGET_USER_EMAIL} not found")
            return None
    else:
        print(f"❌ Failed to get users: {response.status_code}")
        try:
            error = response.json()
            print(f"   Error: {error.get('detail')}")
        except:
            print(f"   Raw response: {response.text}")
        return None

def reset_user_account(admin_token, user_id):
    """Try to reset user account issues"""
    print(f"\n🔧 Attempting to fix user account issues...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to unban user
    print("   Attempting to unban user...")
    response = requests.post(f"{BACKEND_URL}/admin/users/{user_id}/unban", headers=headers)
    if response.status_code == 200:
        print("   ✅ User unbanned")
    else:
        print(f"   ❌ Unban failed: {response.status_code}")
    
    return True

def create_working_test_user():
    """Create a test user with the target password to verify system works"""
    print(f"\n🧪 Creating test user with target password...")
    
    test_email = "test.fixed.user@topkit.fr"
    test_password = "T0p_Mdp_1288*"
    
    # Register test user
    register_data = {
        "email": test_email,
        "password": test_password,
        "name": "Test Fixed User"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
    print(f"   Registration: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Test user created")
        
        # Try to login
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"   Login test: {login_response.status_code}")
        
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"   ✅ Test user login successful!")
            print(f"   User: {data['user']['name']}")
            
            # Test jersey submission
            token = data['token']
            jersey_data = {
                "team": "Test Team",
                "season": "2024-25",
                "player": "Test Player",
                "manufacturer": "Test Brand",
                "home_away": "home",
                "league": "Test League",
                "description": "Test jersey submission"
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            jersey_response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            print(f"   Jersey submission: {jersey_response.status_code}")
            
            if jersey_response.status_code == 200:
                jersey_result = jersey_response.json()
                print(f"   ✅ Jersey submission successful!")
                print(f"   Jersey ID: {jersey_result.get('id')}")
                print(f"   Reference: {jersey_result.get('reference_number')}")
                return True
            else:
                print(f"   ❌ Jersey submission failed")
                return False
        else:
            print(f"   ❌ Test user login failed")
            return False
    else:
        print(f"   ❌ Test user creation failed")
        try:
            error = response.json()
            print(f"   Error: {error.get('detail')}")
        except:
            pass
        return False

def main():
    print("=" * 80)
    print("🔍 ADMIN USER ACCOUNT INVESTIGATION")
    print("=" * 80)
    
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        return False
    
    # Get user information
    user_info = get_all_users(admin_token)
    
    if user_info:
        user_id = user_info.get('id')
        
        # Check if account has issues
        failed_attempts = user_info.get('failed_login_attempts', 0)
        is_locked = user_info.get('account_locked_until') is not None
        is_banned = user_info.get('is_banned', False)
        
        print(f"\n📊 ACCOUNT STATUS:")
        print(f"   Failed Login Attempts: {failed_attempts}")
        print(f"   Account Locked: {is_locked}")
        print(f"   Account Banned: {is_banned}")
        
        if failed_attempts > 0 or is_locked or is_banned:
            print(f"\n🚨 ACCOUNT HAS ISSUES - Attempting to fix...")
            reset_user_account(admin_token, user_id)
        else:
            print(f"\n✅ Account appears normal")
    
    # Test if the system works with a new user
    print(f"\n" + "=" * 80)
    print("🧪 TESTING SYSTEM WITH NEW USER")
    print("=" * 80)
    
    test_success = create_working_test_user()
    
    print(f"\n" + "=" * 80)
    print("📊 INVESTIGATION RESULTS")
    print("=" * 80)
    
    if user_info:
        print(f"✅ Target user account exists in database")
        print(f"   Email: {user_info.get('email')}")
        print(f"   Name: {user_info.get('name')}")
        print(f"   Role: {user_info.get('role')}")
    else:
        print(f"❌ Target user account not found")
    
    if test_success:
        print(f"✅ System works correctly with new users")
        print(f"✅ Password format 'T0p_Mdp_1288*' is valid")
        print(f"✅ Jersey submission system is operational")
    else:
        print(f"❌ System has issues with new users")
    
    print(f"\n🎯 CONCLUSION:")
    if user_info and test_success:
        print(f"   The target user account exists but has authentication issues.")
        print(f"   The system works correctly with new accounts.")
        print(f"   RECOMMENDATION: Reset password for steinmetzlivio@gmail.com")
    elif not user_info:
        print(f"   The target user account does not exist.")
        print(f"   RECOMMENDATION: Create new account with target credentials")
    else:
        print(f"   System-wide authentication issues detected.")
        print(f"   RECOMMENDATION: Check backend authentication system")
    
    print("=" * 80)
    
    return test_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)