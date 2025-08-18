#!/usr/bin/env python3
"""
Script to add test friends for user testing
"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
import bcrypt

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.topkit

async def add_test_friends():
    """Add two test friends and friend requests for steinmetzlivio@gmail.com"""
    
    target_email = "steinmetzlivio@gmail.com"
    
    try:
        # Find the target user
        target_user = await db.users.find_one({"email": target_email})
        if not target_user:
            # Try to find by name pattern
            target_user = await db.users.find_one({"name": {"$regex": "Livio", "$options": "i"}})
        if not target_user:
            # Show all users to debug
            users = await db.users.find({}).to_list(10)
            print("Available users:")
            for user in users:
                print(f"  - {user.get('name', 'No name')} ({user.get('email', 'No email')}) - ID: {user.get('id', 'No ID')}")
            print(f"❌ User {target_email} not found")
            return False
            
        print(f"✅ Found target user: {target_user['name']} ({target_email})")
        
        # Create test friend 1
        friend1_email = "ami1@test.com"
        friend1_password = "TestFriend123!"
        friend1_salt = bcrypt.gensalt()
        friend1_hash = bcrypt.hashpw(friend1_password.encode('utf-8'), friend1_salt)
        
        friend1_id = str(uuid.uuid4())
        friend1 = {
            "id": friend1_id,
            "name": "Jean Dupont",
            "email": friend1_email,
            "password_hash": friend1_hash.decode('utf-8'),
            "role": "user",
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "profile": {
                "bio": "Amateur de maillots de foot",
                "location": "Paris, France"
            },
            "security_features": {
                "two_factor_enabled": False,
                "failed_login_attempts": 0,
                "account_locked": False,
                "last_login": datetime.utcnow()
            }
        }
        
        # Create test friend 2
        friend2_email = "ami2@test.com"
        friend2_password = "TestFriend123!"
        friend2_salt = bcrypt.gensalt()
        friend2_hash = bcrypt.hashpw(friend2_password.encode('utf-8'), friend2_salt)
        
        friend2_id = str(uuid.uuid4())
        friend2 = {
            "id": friend2_id,
            "name": "Marie Martin",
            "email": friend2_email,
            "password_hash": friend2_hash.decode('utf-8'),
            "role": "user",
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "profile": {
                "bio": "Collectionneuse de maillots vintage",
                "location": "Lyon, France"
            },
            "security_features": {
                "two_factor_enabled": False,
                "failed_login_attempts": 0,
                "account_locked": False,
                "last_login": datetime.utcnow()
            }
        }
        
        # Insert test friends
        await db.users.insert_one(friend1)
        await db.users.insert_one(friend2)
        print(f"✅ Created test friend 1: {friend1['name']} ({friend1_email})")
        print(f"✅ Created test friend 2: {friend2['name']} ({friend2_email})")
        
        # Create friend relationship 1 (accepted)
        friendship_id1 = str(uuid.uuid4())
        friendship1 = {
            "id": friendship_id1,
            "user_id": target_user["id"],
            "friend_id": friend1_id,
            "status": "accepted",
            "created_at": datetime.utcnow(),
            "accepted_at": datetime.utcnow()
        }
        
        # Reciprocal friendship
        friendship_id1_reverse = str(uuid.uuid4())
        friendship1_reverse = {
            "id": friendship_id1_reverse,
            "user_id": friend1_id,
            "friend_id": target_user["id"],
            "status": "accepted",
            "created_at": datetime.utcnow(),
            "accepted_at": datetime.utcnow()
        }
        
        # Create friend request from friend2 (pending)
        request_id = str(uuid.uuid4())
        friend_request = {
            "id": request_id,
            "user_id": friend2_id,
            "friend_id": target_user["id"],
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        # Insert relationships
        await db.friendships.insert_one(friendship1)
        await db.friendships.insert_one(friendship1_reverse)
        await db.friendships.insert_one(friend_request)
        
        print(f"✅ Created accepted friendship with {friend1['name']}")
        print(f"✅ Created pending friend request from {friend2['name']}")
        
        print("\n🎯 TEST SETUP COMPLETE!")
        print(f"💡 You can now test:")
        print(f"   - 'Supprimer' ami: {friend1['name']}")
        print(f"   - 'Refuser' demande: {friend2['name']}")
        print(f"   - Messagerie with friends list integration")
        
        print(f"\n🔑 Test friend credentials:")
        print(f"   Friend 1: {friend1_email} / {friend1_password}")
        print(f"   Friend 2: {friend2_email} / {friend2_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding test friends: {e}")
        return False

async def main():
    try:
        success = await add_test_friends()
        if success:
            print("\n✅ Test friends added successfully!")
        else:
            print("\n❌ Failed to add test friends")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())