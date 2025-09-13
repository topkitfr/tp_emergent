#!/usr/bin/env python3
"""
Friends Endpoint Debug Test - Check database for test friends
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

def authenticate_user():
    """Authenticate user and return token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=USER_CREDENTIALS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User authenticated: {data['user']['name']} (ID: {data['user']['id']})")
            return data['token'], data['user']['id']
        else:
            print(f"❌ User authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None, None

def authenticate_admin():
    """Authenticate admin and return token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=ADMIN_CREDENTIALS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Admin authenticated: {data['user']['name']} (ID: {data['user']['id']})")
            return data['token']
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Admin authentication error: {e}")
        return None

def check_users_in_database(admin_token):
    """Check if Jean Dupont and Marie Martin exist in database"""
    print("\n🔍 CHECKING USERS IN DATABASE...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/admin/users",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            users_data = response.json()
            
            # Handle different response formats
            if isinstance(users_data, list):
                users = users_data
            elif isinstance(users_data, dict) and 'users' in users_data:
                users = users_data['users']
            else:
                print(f"❌ Unexpected response format: {type(users_data)}")
                print(f"Response: {users_data}")
                return False, False
            
            print(f"📊 Total users in database: {len(users)}")
            
            jean_found = False
            marie_found = False
            
            print("\n👥 All users in database:")
            for user in users:
                if isinstance(user, dict):
                    name = user.get('name', 'Unknown')
                    email = user.get('email', 'Unknown')
                    user_id = user.get('id', 'Unknown')
                else:
                    # Handle string or other formats
                    name = str(user)
                    email = 'Unknown'
                    user_id = 'Unknown'
                
                print(f"  - {name} ({email}) - ID: {user_id}")
                
                if 'jean' in name.lower() and 'dupont' in name.lower():
                    jean_found = True
                    print(f"    ✅ Found Jean Dupont!")
                
                if 'marie' in name.lower() and 'martin' in name.lower():
                    marie_found = True
                    print(f"    ✅ Found Marie Martin!")
            
            print(f"\n📋 Test Friends Status:")
            print(f"  Jean Dupont: {'✅ Found' if jean_found else '❌ Not Found'}")
            print(f"  Marie Martin: {'✅ Found' if marie_found else '❌ Not Found'}")
            
            return jean_found, marie_found
            
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            return False, False
            
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return False, False

def check_friendships_in_database(user_token, user_id):
    """Check friendships for the user"""
    print(f"\n🤝 CHECKING FRIENDSHIPS FOR USER ID: {user_id}...")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/friends",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            friends_data = response.json()
            print(f"📊 Friends API Response:")
            print(json.dumps(friends_data, indent=2, default=str))
            
            # Check stats
            stats = friends_data.get('stats', {})
            print(f"\n📈 Friends Statistics:")
            print(f"  Total Friends: {stats.get('total_friends', 0)}")
            print(f"  Pending Received: {stats.get('pending_received', 0)}")
            print(f"  Pending Sent: {stats.get('pending_sent', 0)}")
            
            return friends_data
            
        else:
            print(f"❌ Failed to get friends: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking friends: {e}")
        return None

def main():
    print("🚀 FRIENDS ENDPOINT DEBUG TEST")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Authenticate user
    user_token, user_id = authenticate_user()
    if not user_token:
        print("❌ Cannot proceed without user authentication")
        return
    
    # Authenticate admin
    admin_token = authenticate_admin()
    if not admin_token:
        print("❌ Cannot check database without admin authentication")
        return
    
    # Check if test friends exist in database
    jean_found, marie_found = check_users_in_database(admin_token)
    
    # Check current friendships
    friends_data = check_friendships_in_database(user_token, user_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    print(f"User: steinmetzlivio@gmail.com (ID: {user_id})")
    print(f"Jean Dupont in database: {'✅ Yes' if jean_found else '❌ No'}")
    print(f"Marie Martin in database: {'✅ Yes' if marie_found else '❌ No'}")
    
    if friends_data:
        stats = friends_data.get('stats', {})
        print(f"Current friends count: {stats.get('total_friends', 0)}")
        print(f"Pending requests received: {stats.get('pending_received', 0)}")
        print(f"Pending requests sent: {stats.get('pending_sent', 0)}")
    
    print("\n🔍 ROOT CAUSE ANALYSIS:")
    if not jean_found and not marie_found:
        print("❌ ISSUE IDENTIFIED: Test friends Jean Dupont and Marie Martin do not exist in the database")
        print("   This explains why the frontend shows all zeros for friends counts")
        print("   The friends endpoint is working correctly, but there's no test data")
    elif jean_found and marie_found:
        if friends_data and friends_data.get('stats', {}).get('total_friends', 0) == 0:
            print("❌ ISSUE IDENTIFIED: Test friends exist but no friendship relationships are established")
            print("   Need to create friendship records between users")
        else:
            print("✅ Test friends exist and friendships are established")
    else:
        print("⚠️ PARTIAL ISSUE: Some test friends exist but not all")
    
    print("\n🏁 DEBUG TEST COMPLETE")

if __name__ == "__main__":
    main()