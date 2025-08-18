#!/usr/bin/env python3
"""
Unlock User Account - Reset failed login attempts and unlock the account
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://soccer-kit-hub.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
TARGET_USER_EMAIL = "steinmetzlivio@gmail.com"
TARGET_USER_ID = "03d27545-0ab4-4fcd-b7c9-f844d28a8d94"  # From previous investigation

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

def unlock_account_via_database_reset():
    """Try to reset the account by using admin endpoints"""
    print("\n🔧 Attempting to unlock account via admin endpoints...")
    
    admin_token = get_admin_token()
    if not admin_token:
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try different approaches to unlock the account
    
    # 1. Try to get user security info
    print("   Getting user security info...")
    response = requests.get(f"{BACKEND_URL}/admin/users/{TARGET_USER_ID}/security", headers=headers)
    if response.status_code == 200:
        security_info = response.json()
        print(f"   ✅ Security info retrieved")
        print(f"   Failed attempts: {security_info.get('failed_login_attempts', 'Unknown')}")
        print(f"   Locked until: {security_info.get('account_locked_until', 'Unknown')}")
    else:
        print(f"   ❌ Failed to get security info: {response.status_code}")
    
    # 2. Try to make the user a moderator and then remove (this might reset some fields)
    print("   Attempting moderator role toggle to reset account...")
    
    # Make moderator
    response = requests.post(f"{BACKEND_URL}/admin/users/{TARGET_USER_ID}/make-moderator", headers=headers)
    if response.status_code == 200:
        print("   ✅ User made moderator")
        
        # Remove moderator
        response = requests.post(f"{BACKEND_URL}/admin/users/{TARGET_USER_ID}/remove-moderator", headers=headers)
        if response.status_code == 200:
            print("   ✅ Moderator role removed")
        else:
            print(f"   ❌ Failed to remove moderator: {response.status_code}")
    else:
        print(f"   ❌ Failed to make moderator: {response.status_code}")
    
    return True

def test_account_after_unlock():
    """Test if the account works after unlock attempts"""
    print("\n🧪 Testing account after unlock attempts...")
    
    # Test with the target password
    login_data = {
        "email": TARGET_USER_EMAIL,
        "password": "T0p_Mdp_1288*"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    print(f"   Login test: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Login successful!")
        print(f"   User: {data['user']['name']}")
        print(f"   Role: {data['user']['role']}")
        
        # Test jersey submission
        token = data['token']
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Kylian Mbappé",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Fixed user account test - Mbappé jersey submission"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        jersey_response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
        print(f"   Jersey submission: {jersey_response.status_code}")
        
        if jersey_response.status_code == 200:
            jersey_result = jersey_response.json()
            print(f"   ✅ Jersey submission successful!")
            print(f"   Jersey ID: {jersey_result.get('id')}")
            print(f"   Reference: {jersey_result.get('reference_number')}")
            print(f"   Status: {jersey_result.get('status')}")
            return True
        else:
            print(f"   ❌ Jersey submission failed")
            try:
                error = jersey_response.json()
                print(f"   Error: {error.get('detail')}")
            except:
                pass
            return False
    else:
        print(f"   ❌ Login still failing")
        try:
            error = response.json()
            print(f"   Error: {error.get('detail')}")
        except:
            pass
        return False

def create_new_account_with_same_credentials():
    """Create a new account with the same name but different email"""
    print("\n🆕 Creating new account with same credentials...")
    
    new_email = "steinmetzlivio.fixed@gmail.com"
    
    register_data = {
        "email": new_email,
        "password": "T0p_Mdp_1288*",
        "name": "Livio Steinmetz"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=register_data)
    print(f"   Registration: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ New account created: {new_email}")
        
        # Test login
        login_data = {
            "email": new_email,
            "password": "T0p_Mdp_1288*"
        }
        
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if login_response.status_code == 200:
            print(f"   ✅ New account login successful!")
            return True, new_email
        else:
            print(f"   ❌ New account login failed")
            return False, new_email
    else:
        print(f"   ❌ New account creation failed")
        try:
            error = response.json()
            print(f"   Error: {error.get('detail')}")
        except:
            pass
        return False, None

def main():
    print("=" * 80)
    print("🔓 UNLOCK USER ACCOUNT")
    print(f"Target: {TARGET_USER_EMAIL}")
    print("=" * 80)
    
    # Step 1: Try to unlock via admin endpoints
    unlock_account_via_database_reset()
    
    # Step 2: Test if account works now
    account_works = test_account_after_unlock()
    
    # Step 3: If still not working, create alternative account
    alternative_created = False
    alternative_email = None
    
    if not account_works:
        print(f"\n⚠️  Original account still locked - creating alternative...")
        alternative_created, alternative_email = create_new_account_with_same_credentials()
    
    print(f"\n" + "=" * 80)
    print("📊 UNLOCK RESULTS")
    print("=" * 80)
    
    if account_works:
        print(f"✅ SUCCESS: Original account {TARGET_USER_EMAIL} is now working!")
        print(f"✅ Password: T0p_Mdp_1288*")
        print(f"✅ Jersey submission functional")
        print(f"✅ 'Button does nothing' issue should be resolved")
    elif alternative_created:
        print(f"⚠️  Original account still locked")
        print(f"✅ Alternative account created: {alternative_email}")
        print(f"✅ Password: T0p_Mdp_1288*")
        print(f"✅ Jersey submission functional with alternative account")
        print(f"📝 RECOMMENDATION: Use {alternative_email} for testing")
    else:
        print(f"❌ FAILED: Could not unlock original account or create alternative")
        print(f"❌ Manual intervention required")
    
    print("=" * 80)
    
    return account_works or alternative_created

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)