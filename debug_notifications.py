#!/usr/bin/env python3
"""
Direct notification creation test to debug the issue
"""

import requests
import json

# Configuration
BACKEND_URL = "https://topkit-beta.emergent.host/api"

# Admin credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

def test_direct_notification():
    """Test creating a notification directly via API"""
    
    # First authenticate
    session = requests.Session()
    response = session.post(
        f"{BACKEND_URL}/auth/login",
        json=ADMIN_CREDENTIALS,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return False
    
    token = response.json().get("token")
    user_id = response.json().get("user", {}).get("id")
    
    print(f"✅ Authenticated as user: {user_id}")
    
    # Check if there's a direct notification creation endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try to create a notification via admin endpoint (if it exists)
    notification_data = {
        "user_id": user_id,
        "type": "system_announcement",
        "title": "Test Notification",
        "message": "This is a test notification to verify the system is working",
        "related_id": None
    }
    
    # Check if admin notifications endpoint exists
    response = session.post(
        f"{BACKEND_URL}/admin/notifications",
        json=notification_data,
        headers=headers
    )
    
    print(f"Direct notification creation attempt: {response.status_code}")
    if response.status_code == 404:
        print("No direct notification creation endpoint found")
    else:
        print(f"Response: {response.text}")
    
    # Now check current notifications count
    response = session.get(f"{BACKEND_URL}/notifications", headers=headers)
    if response.status_code == 200:
        notifications = response.json()
        print(f"Current notifications count: {len(notifications)}")
        if notifications:
            print("Recent notifications:")
            for notif in notifications[-3:]:  # Show last 3
                print(f"  - {notif.get('title', 'No title')} ({notif.get('type', 'No type')})")
    else:
        print(f"❌ Failed to get notifications: {response.status_code}")

if __name__ == "__main__":
    test_direct_notification()