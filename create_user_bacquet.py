#!/usr/bin/env python3
"""
Create a user account for Bacquet.florent@gmail.com with beta access
"""

import asyncio
import os
import uuid
import bcrypt
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def create_bacquet_user():
    """Create user account for Bacquet.florent@gmail.com with beta access"""
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # User data
        user_email = "Bacquet.florent@gmail.com"
        user_password = "TopKitBeta2025!"  # Temporary password
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_email})
        if existing_user:
            print(f"✅ User already exists: {existing_user.get('name')}")
            print(f"   Email: {user_email}")
            print(f"   ID: {existing_user.get('id')}")
            print(f"   Role: {existing_user.get('role', 'user')}")
            return
        
        # Hash password
        password_hash = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        new_user = {
            "id": str(uuid.uuid4()),
            "email": user_email,
            "password_hash": password_hash,
            "name": "Florent Bacquet",
            "role": "user",
            "email_verified": True,  # Beta access bypasses email verification
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "beta_access": True,  # Grant beta access
            "profile": {
                "bio": "Beta tester",
                "location": "France",
                "joined": datetime.utcnow().isoformat()
            },
            "failed_login_attempts": 0,
            "is_banned": False,
            "two_factor_enabled": False,
            "account_locked_until": None
        }
        
        # Insert user
        await db.users.insert_one(new_user)
        print(f"✅ Created user account: {new_user['name']} ({new_user['email']})")
        print(f"   ID: {new_user['id']}")
        print(f"   Password: {user_password}")
        print(f"   Beta Access: {new_user['beta_access']}")
        print(f"   Email Verified: {new_user['email_verified']}")
        
        print(f"\n🎉 Successfully created user account for beta access!")
        print(f"📧 Email: {user_email}")
        print(f"🔑 Temporary Password: {user_password}")
        print(f"🚀 Beta Access: Enabled")
        print(f"\n📝 Instructions:")
        print(f"1. User can log in immediately with these credentials")
        print(f"2. User has beta access and can use all features")
        print(f"3. Recommend user changes password after first login")
        
    except Exception as e:
        print(f"❌ Error creating user account: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_bacquet_user())