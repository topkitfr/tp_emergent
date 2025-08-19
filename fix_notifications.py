#!/usr/bin/env python3
import asyncio
import os
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def force_create_notifications():
    """Force create notifications for all users"""
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'topkit')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔔 FIXING NOTIFICATIONS SYSTEM")
    
    try:
        # Get all users
        users = await db.users.find({}).to_list(None)
        print(f"👥 Found {len(users)} users")
        
        # Create test notification for each user
        for user in users:
            notification = {
                "id": str(uuid.uuid4()),
                "user_id": user['id'],
                "type": "system_announcement",
                "title": "🎉 Notifications Restored!",
                "message": "Le système de notifications a été restauré et fonctionne maintenant correctement.",
                "related_id": None,
                "is_read": False,
                "created_at": datetime.utcnow().isoformat(),
                "read_at": None
            }
            
            await db.notifications.insert_one(notification)
            print(f"✅ Created notification for {user['name']}")
        
        print("🎯 Notifications system fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(force_create_notifications())