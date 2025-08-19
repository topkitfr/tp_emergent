#!/usr/bin/env python3
"""
Enhanced notifications test to debug user-specific notification issues
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-beta.emergent.host/api"

# Admin credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

def test_notifications_detailed():
    """Test notifications with detailed analysis"""
    
    session = requests.Session()
    session.timeout = 30
    
    # Authenticate as admin
    response = session.post(
        f"{BACKEND_URL}/auth/login",
        json=ADMIN_CREDENTIALS,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return False
    
    token = response.json().get("token")
    admin_user_id = response.json().get("user", {}).get("id")
    
    print(f"✅ Authenticated as admin: {admin_user_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get initial notifications count
    response = session.get(f"{BACKEND_URL}/notifications", headers=headers)
    if response.status_code == 200:
        initial_notifications = response.json()
        initial_count = len(initial_notifications) if isinstance(initial_notifications, list) else 0
        print(f"📊 Initial notifications count: {initial_count}")
        
        if initial_notifications and isinstance(initial_notifications, list):
            print("📋 Existing notifications:")
            for i, notif in enumerate(initial_notifications):
                print(f"  {i+1}. {notif.get('title', 'No title')} - Type: {notif.get('type', 'No type')} - User: {notif.get('user_id', 'No user')}")
    else:
        print(f"❌ Failed to get initial notifications: {response.status_code}")
        return False
    
    # Submit a test jersey
    jersey_data = {
        "team": "FC Barcelona",
        "season": "2024-25",
        "player": "Pedri",
        "manufacturer": "Nike",
        "home_away": "home",
        "league": "La Liga",
        "description": "Test jersey for detailed notification debugging"
    }
    
    print(f"\n🏈 Submitting test jersey...")
    response = session.post(
        f"{BACKEND_URL}/jerseys",
        json=jersey_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        jersey = response.json()
        jersey_id = jersey.get("id")
        jersey_ref = jersey.get("reference_number")
        print(f"✅ Jersey submitted successfully: {jersey_id} ({jersey_ref})")
    else:
        print(f"❌ Jersey submission failed: {response.status_code} - {response.text}")
        return False
    
    # Wait for notification to be created
    print(f"\n⏳ Waiting 3 seconds for notification creation...")
    time.sleep(3)
    
    # Check notifications again
    response = session.get(f"{BACKEND_URL}/notifications", headers=headers)
    if response.status_code == 200:
        new_notifications = response.json()
        new_count = len(new_notifications) if isinstance(new_notifications, list) else 0
        print(f"📊 New notifications count: {new_count}")
        
        if new_count > initial_count:
            print(f"🎉 SUCCESS: {new_count - initial_count} new notification(s) created!")
            
            # Show new notifications
            if isinstance(new_notifications, list):
                print("📋 All notifications (newest first):")
                for i, notif in enumerate(reversed(new_notifications)):
                    created_at = notif.get('created_at', 'Unknown time')
                    print(f"  {i+1}. {notif.get('title', 'No title')}")
                    print(f"     Type: {notif.get('type', 'No type')}")
                    print(f"     User: {notif.get('user_id', 'No user')}")
                    print(f"     Created: {created_at}")
                    print(f"     Related ID: {notif.get('related_id', 'None')}")
                    print()
        else:
            print(f"❌ FAILURE: No new notifications created (count remained {new_count})")
            
            # Check if there are any notifications for the admin user specifically
            admin_notifications = [n for n in new_notifications if n.get('user_id') == admin_user_id] if isinstance(new_notifications, list) else []
            print(f"📊 Notifications for admin user ({admin_user_id}): {len(admin_notifications)}")
            
            # Check if there are notifications for any user
            if isinstance(new_notifications, list) and new_notifications:
                user_ids = set(n.get('user_id') for n in new_notifications)
                print(f"📊 Notifications exist for users: {user_ids}")
    else:
        print(f"❌ Failed to get updated notifications: {response.status_code}")
        return False
    
    return new_count > initial_count

if __name__ == "__main__":
    success = test_notifications_detailed()
    if success:
        print("\n✅ CONCLUSION: Notifications system is working!")
    else:
        print("\n❌ CONCLUSION: Notifications system has issues.")