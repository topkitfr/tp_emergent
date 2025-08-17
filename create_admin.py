#!/usr/bin/env python3

import asyncio
import os
import uuid
import bcrypt
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def create_admin_user():
    """Create admin user for Private Beta Mode testing"""
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Admin user data
        admin_email = "topkitfr@gmail.com"
        admin_password = "adminpass123"
        
        # Check if admin already exists
        existing_admin = await db.users.find_one({"email": admin_email})
        if existing_admin:
            print(f"✅ Admin user already exists: {existing_admin.get('name')}")
            return
        
        # Hash password
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "password_hash": password_hash,
            "name": "TopKit Admin",
            "role": "admin",
            "email_verified": True,  # Admin bypasses email verification
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "profile": {
                "bio": "TopKit Administrator",
                "location": "France",
                "joined": datetime.utcnow().isoformat()
            }
        }
        
        # Insert admin user
        await db.users.insert_one(admin_user)
        print(f"✅ Created admin user: {admin_user['name']} ({admin_user['email']})")
        
        # Also create test user for testing
        test_user = {
            "id": str(uuid.uuid4()),
            "email": "steinmetzlivio@gmail.com",
            "password_hash": bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "name": "Livio",
            "role": "user",
            "email_verified": True,  # For testing purposes
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "profile": {
                "bio": "Test user",
                "location": "France",
                "joined": datetime.utcnow().isoformat()
            }
        }
        
        await db.users.insert_one(test_user)
        print(f"✅ Created test user: {test_user['name']} ({test_user['email']})")
        
        # Initialize site configuration as private for testing
        site_config = {
            "id": str(uuid.uuid4()),
            "site_mode": "private",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.site_config.insert_one(site_config)
        print(f"✅ Initialized site config: mode = {site_config['site_mode']}")
        
        print(f"\n🎉 Successfully created admin and test users for Private Beta Mode testing!")
        print(f"Admin: {admin_email} / {admin_password}")
        print(f"User: steinmetzlivio@gmail.com / 123")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())