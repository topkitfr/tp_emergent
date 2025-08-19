#!/usr/bin/env python3
"""
Test and fix notifications system
"""

import asyncio
import os
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv('/app/backend/.env')

# Test creating notifications directly in database
async def test_direct_notification_creation():
    """Test creating notifications directly in the database"""
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'topkit')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔧 Testing Direct Notification Creation")
    print("=" * 50)
    
    try:
        # Get a user to create notification for
        user = await db.users.find_one({"email": "steinmetzlivio@gmail.com"})
        if not user:
            print("❌ Test user not found")
            return
            
        user_id = user['id']
        print(f"📧 Target user: {user.get('name')} ({user.get('email')})")
        print(f"🆔 User ID: {user_id}")
        
        # Create test notification directly
        test_notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "system_announcement",
            "title": "🧪 Test Notification",
            "message": "This is a test notification to verify the notifications system is working correctly.",
            "related_id": None,
            "is_read": False,
            "created_at": datetime.utcnow().isoformat(),
            "read_at": None
        }
        
        # Insert notification
        result = await db.notifications.insert_one(test_notification)
        
        if result.inserted_id:
            print("✅ Direct notification creation successful")
            print(f"   Notification ID: {test_notification['id']}")
            print(f"   Title: {test_notification['title']}")
            print(f"   Message: {test_notification['message']}")
        else:
            print("❌ Direct notification creation failed")
            
        # Check if notification exists
        created_notification = await db.notifications.find_one({"id": test_notification['id']})
        if created_notification:
            print("✅ Notification found in database")
            print(f"   Database entry: {created_notification}")
        else:
            print("❌ Notification not found in database")
            
        # Count total notifications for this user
        notification_count = await db.notifications.count_documents({"user_id": user_id})
        print(f"📊 Total notifications for user: {notification_count}")
        
        # List all notifications for this user
        all_notifications = await db.notifications.find({"user_id": user_id}).to_list(None)
        print(f"\n📋 All notifications for user:")
        for i, notif in enumerate(all_notifications):
            print(f"   {i+1}. {notif.get('title', 'No Title')} - {notif.get('type', 'No Type')} - {notif.get('created_at', 'No Date')}")
            
    except Exception as e:
        print(f"❌ Error during direct notification test: {e}")
        
    finally:
        client.close()

async def test_api_notification_creation():
    """Test creating notifications via API"""
    
    print("\n🌐 Testing API Notification Creation")
    print("=" * 50)
    
    # First authenticate
    backend_url = "http://localhost:8001"
    
    try:
        # Login as user
        login_data = {
            "email": "steinmetzlivio@gmail.com", 
            "password": "TopKit123!"
        }
        
        response = requests.post(f"{backend_url}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
        auth_data = response.json()
        token = auth_data.get('token')
        user_data = auth_data.get('user', {})
        
        print(f"✅ Authentication successful")
        print(f"   User: {user_data.get('name')} ({user_data.get('email')})")
        print(f"   Token: {token[:20]}...")
        
        # Test jersey submission (should create notification)
        headers = {"Authorization": f"Bearer {token}"}
        
        jersey_data = {
            "team": "Test Team FC",
            "season": "2024-25",
            "player": "Test Player",
            "type": "home",
            "size": "M",
            "condition": "new",
            "manufacturer": "Nike",
            "description": "Test jersey submission to verify notification creation"
        }
        
        response = requests.post(f"{backend_url}/api/jerseys", json=jersey_data, headers=headers)
        
        if response.status_code == 200:
            jersey_response = response.json()
            print(f"✅ Jersey submission successful")
            print(f"   Jersey ID: {jersey_response.get('id')}")
            print(f"   Reference: {jersey_response.get('reference_number')}")
            
            # Wait a moment for notification to be created
            await asyncio.sleep(2)
            
            # Check if notification was created via API
            response = requests.get(f"{backend_url}/api/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications = response.json()
                print(f"✅ Notifications API accessible")
                print(f"   Total notifications: {len(notifications)}")
                
                if notifications:
                    recent_notification = notifications[0]  # Assuming newest first
                    print(f"   Most recent: {recent_notification.get('title')} - {recent_notification.get('created_at')}")
                else:
                    print("❌ No notifications found via API")
            else:
                print(f"❌ Notifications API failed: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print(f"❌ Jersey submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during API notification test: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_notification_creation())
    asyncio.run(test_api_notification_creation())