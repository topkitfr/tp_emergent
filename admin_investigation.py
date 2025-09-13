#!/usr/bin/env python3
"""
Admin Investigation - Check existing users and create test account if needed
"""

import requests
import json

# Configuration
BACKEND_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"

# Admin credentials (confirmed working)
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

# Target user from review request
TARGET_USER_EMAIL = "steinmetzlivio@gmail.com"
TARGET_USER_PASSWORD = "T0p_Mdp_1288*"

def get_admin_token():
    """Get admin authentication token"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            return response.json().get("token")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return None

def check_existing_users(admin_token):
    """Check what users exist in the system"""
    print("🔍 CHECKING EXISTING USERS")
    print("=" * 50)
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
        
        if response.status_code == 200:
            users = response.json()
            print(f"Found {len(users)} users in system:")
            
            target_user_found = False
            for user in users:
                email = user.get("email", "N/A")
                name = user.get("name", "N/A")
                role = user.get("role", "N/A")
                user_id = user.get("id", "N/A")
                is_banned = user.get("is_banned", False)
                email_verified = user.get("email_verified", False)
                
                print(f"   • {email} - {name} (Role: {role}, ID: {user_id[:8]}...)")
                print(f"     Banned: {is_banned}, Email Verified: {email_verified}")
                
                if email == TARGET_USER_EMAIL:
                    target_user_found = True
                    print(f"     🎯 TARGET USER FOUND!")
                    
                    # Check if account is locked
                    if user.get("account_locked_until"):
                        print(f"     ⚠️  Account locked until: {user.get('account_locked_until')}")
                    
                    failed_attempts = user.get("failed_login_attempts", 0)
                    if failed_attempts > 0:
                        print(f"     ⚠️  Failed login attempts: {failed_attempts}")
                
                print()
            
            return target_user_found
            
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
            print(f"❌ Failed to get users: {error_detail}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking users: {str(e)}")
        return False

def create_test_user():
    """Create the target user account for testing"""
    print("🔧 CREATING TEST USER ACCOUNT")
    print("=" * 50)
    
    user_data = {
        "email": TARGET_USER_EMAIL,
        "password": TARGET_USER_PASSWORD,
        "name": "Livio Steinmetz"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ User account created successfully!")
            print(f"   Email: {TARGET_USER_EMAIL}")
            print(f"   Name: {data.get('user', {}).get('name', 'N/A')}")
            print(f"   ID: {data.get('user', {}).get('id', 'N/A')}")
            print(f"   Email Verified: {data.get('user', {}).get('email_verified', False)}")
            
            # If email verification is required, we might need to handle that
            if not data.get('user', {}).get('email_verified', True):
                print("   ⚠️  Email verification may be required")
            
            return True
            
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
            print(f"❌ Failed to create user: {error_detail}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        return False

def test_user_login_after_creation():
    """Test login with the target user credentials"""
    print("🔍 TESTING USER LOGIN AFTER CREATION")
    print("=" * 50)
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "email": TARGET_USER_EMAIL,
            "password": TARGET_USER_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get("user", {})
            print("✅ User login successful!")
            print(f"   User: {user_info.get('name')} (Role: {user_info.get('role')}, ID: {user_info.get('id')})")
            return data.get("token")
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
            print(f"❌ User login failed: {error_detail}")
            return None
            
    except Exception as e:
        print(f"❌ User login error: {str(e)}")
        return None

def test_jersey_submission_with_working_user(user_token):
    """Test jersey submission with working user token"""
    if not user_token:
        print("❌ No user token available for jersey submission test")
        return False
    
    print("🔍 TESTING JERSEY SUBMISSION")
    print("=" * 50)
    
    # Test jersey data from review request
    test_jersey = {
        "team": "Test Team",
        "season": "2024/25", 
        "league": "Test League",
        "manufacturer": "Nike",
        "home_away": "Home",
        "description": "Test jersey submission for bug investigation"
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(f"{BACKEND_URL}/jerseys", json=test_jersey, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            jersey_data = response.json()
            print("✅ Jersey submission successful!")
            print(f"   Jersey ID: {jersey_data.get('id', 'N/A')}")
            print(f"   Reference: {jersey_data.get('reference_number', 'N/A')}")
            print(f"   Status: {jersey_data.get('status', 'N/A')}")
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
            print(f"❌ Jersey submission failed: {error_detail}")
            return False
            
    except Exception as e:
        print(f"❌ Jersey submission error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚨 ADMIN INVESTIGATION - USER ACCOUNT & JERSEY SUBMISSION")
    print("=" * 70)
    print()
    
    # Get admin token
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Cannot proceed without admin access")
        exit(1)
    
    print("✅ Admin authentication successful")
    print()
    
    # Check existing users
    target_user_exists = check_existing_users(admin_token)
    
    # Create user if doesn't exist
    if not target_user_exists:
        print(f"🎯 Target user {TARGET_USER_EMAIL} not found. Creating account...")
        user_created = create_test_user()
        
        if not user_created:
            print("❌ Cannot proceed without target user account")
            exit(1)
    else:
        print(f"🎯 Target user {TARGET_USER_EMAIL} already exists")
    
    print()
    
    # Test user login
    user_token = test_user_login_after_creation()
    
    if user_token:
        print()
        # Test jersey submission
        jersey_success = test_jersey_submission_with_working_user(user_token)
        
        print()
        print("=" * 70)
        print("🎯 FINAL INVESTIGATION RESULTS")
        print("=" * 70)
        
        if jersey_success:
            print("✅ JERSEY SUBMISSION WORKING: The backend jersey submission system is operational")
            print("   Root cause of original issue: User account didn't exist or had wrong password")
            print("   Solution: User account is now created and jersey submission works")
        else:
            print("❌ JERSEY SUBMISSION BROKEN: Backend has issues with jersey submission")
            print("   Root cause: Jersey submission API endpoint has problems")
            print("   This requires backend code investigation")
    else:
        print()
        print("=" * 70)
        print("🎯 FINAL INVESTIGATION RESULTS")
        print("=" * 70)
        print("❌ USER AUTHENTICATION BROKEN: Cannot authenticate user even after account creation")
        print("   This indicates a deeper backend authentication issue")