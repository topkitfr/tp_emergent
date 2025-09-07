#!/usr/bin/env python3
"""
Create Admin User - topkitfr@gmail.com
Creates the admin user with proper credentials for the clean database
"""

import asyncio
import os
import bcrypt
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = 'topkit_collaborative'

# Admin user details
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
ADMIN_NAME = "TopKit Admin"

async def create_admin_user():
    """Create the admin user in the clean database"""
    
    print("👤 Creating Admin User")
    print("=" * 25)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    try:
        users_collection = db['users']
        
        # Check if admin already exists
        existing_admin = await users_collection.find_one({"email": ADMIN_EMAIL})
        
        if existing_admin:
            print(f"✅ Admin user already exists: {existing_admin.get('name')} ({existing_admin.get('email')})")
            return True
        
        # Hash the password
        password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user document
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": ADMIN_EMAIL,
            "password_hash": password_hash,
            "name": ADMIN_NAME,
            "role": "admin",
            "is_verified": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "profile": {
                "bio": "TopKit Platform Administrator",
                "location": "France",
                "website": "",
                "avatar_url": ""
            },
            "preferences": {
                "language": "en",
                "timezone": "Europe/Paris",
                "email_notifications": True
            },
            "stats": {
                "contributions_count": 0,
                "votes_cast": 0,
                "collections_count": 0
            }
        }
        
        # Insert admin user
        result = await users_collection.insert_one(admin_user)
        
        if result.inserted_id:
            print(f"✅ Admin user created successfully!")
            print(f"   📧 Email: {ADMIN_EMAIL}")
            print(f"   👤 Name: {ADMIN_NAME}")
            print(f"   🔑 Role: admin")
            print(f"   🆔 ID: {admin_user['id']}")
            
            # Verify creation
            verification = await users_collection.find_one({"email": ADMIN_EMAIL})
            if verification:
                print(f"✅ Verification successful - admin user is in database")
                return True
            else:
                print(f"❌ Verification failed - admin user not found after creation")
                return False
        else:
            print(f"❌ Failed to create admin user")
            return False
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
        
    finally:
        client.close()

async def main():
    """Main function"""
    print(f"🕐 Creating admin user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await create_admin_user()
    
    if success:
        print("\n🎉 Admin user setup completed!")
        print(f"💡 You can now login with:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
    else:
        print("\n❌ Admin user creation failed")

if __name__ == "__main__":
    asyncio.run(main())