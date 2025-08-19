#!/usr/bin/env python3

import requests
import json
import time

# Production URL
BASE_URL = "https://topkit-beta.emergent.host/api"

# Admin credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def test_notification_creation():
    print("🔍 DEBUGGING NOTIFICATION CREATION")
    print("=" * 50)
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()["token"]
    user_id = response.json()["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Authenticated as {response.json()['user']['name']} (ID: {user_id})")
    
    # Step 2: Get initial notification count
    print("\n2. Getting initial notifications...")
    response = requests.get(f"{BASE_URL}/notifications", headers=headers)
    initial_count = len(response.json()) if response.status_code == 200 else 0
    print(f"📋 Initial notification count: {initial_count}")
    
    # Step 3: Submit jersey
    print("\n3. Submitting jersey...")
    jersey_data = {
        "team": "FC Barcelona",
        "season": "2024-25",
        "player": "Lewandowski",
        "manufacturer": "Nike",
        "home_away": "home",
        "league": "La Liga",
        "description": "Debug test for notification creation - FC Barcelona home jersey"
    }
    
    response = requests.post(f"{BASE_URL}/jerseys", json=jersey_data, headers=headers)
    
    if response.status_code == 200:
        jersey = response.json()
        print(f"✅ Jersey created: {jersey['id']} - {jersey['reference_number']}")
    else:
        print(f"❌ Jersey creation failed: {response.status_code} - {response.text}")
        return
    
    # Step 4: Wait a moment and check notifications again
    print("\n4. Waiting 2 seconds and checking notifications...")
    time.sleep(2)
    
    response = requests.get(f"{BASE_URL}/notifications", headers=headers)
    if response.status_code == 200:
        notifications = response.json()
        new_count = len(notifications)
        print(f"📋 New notification count: {new_count}")
        
        if new_count > initial_count:
            print("✅ NEW NOTIFICATION FOUND!")
            latest = notifications[0]  # Assuming newest first
            print(f"   Title: {latest.get('title')}")
            print(f"   Message: {latest.get('message')}")
            print(f"   Type: {latest.get('type')}")
        else:
            print("❌ NO NEW NOTIFICATION CREATED")
            print("🔍 This confirms the notification creation bug")
    else:
        print(f"❌ Failed to get notifications: {response.status_code}")

if __name__ == "__main__":
    test_notification_creation()