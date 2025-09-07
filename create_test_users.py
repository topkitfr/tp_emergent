#!/usr/bin/env python3
"""
Create test users for voting system testing
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import bcrypt
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('backend/.env')
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def create_test_users():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    test_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "test1@topkit.com",
            "password": "TestUser123!",
            "name": "Test User 1",
            "role": "user"
        },
        {
            "id": str(uuid.uuid4()),
            "email": "test2@topkit.com", 
            "password": "TestUser123!",
            "name": "Test User 2",
            "role": "user"
        },
        {
            "id": str(uuid.uuid4()),
            "email": "test3@topkit.com",
            "password": "TestUser123!", 
            "name": "Test User 3",
            "role": "user"
        }
    ]
    
    print("Creating test users...")
    
    for user_data in test_users:
        # Check if user already exists
        existing = await db.users.find_one({"email": user_data["email"]})
        if existing:
            print(f"User {user_data['email']} already exists, skipping...")
            continue
            
        # Hash password
        password_bytes = user_data["password"].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        
        # Prepare user document
        user_doc = {
            "id": user_data["id"],
            "email": user_data["email"],
            "password": hashed_password.decode('utf-8'),
            "name": user_data["name"],
            "role": user_data["role"],
            "created_at": datetime.utcnow(),
            "is_verified": True,
            "verification_token": None,
            "reset_token": None,
            "reset_token_expires": None,
            "profile_picture": None,
            "two_factor_enabled": False,
            "two_factor_secret": None
        }
        
        # Insert user
        result = await db.users.insert_one(user_doc)
        print(f"✅ Created user: {user_data['email']} with ID: {user_data['id']}")
    
    # Verify created users
    print("\n=== VERIFICATION ===")
    all_users = await db.users.find({}).to_list(None)
    print(f"Total users in database: {len(all_users)}")
    
    test_emails = ["test1@topkit.com", "test2@topkit.com", "test3@topkit.com"]
    for email in test_emails:
        user = await db.users.find_one({"email": email})
        if user:
            print(f"✅ {email} - ID: {user['id']}, Name: {user['name']}")
        else:
            print(f"❌ {email} - NOT FOUND")
    
    print(f"\n🎉 Test users created successfully!")
    print("Login credentials for all test users:")
    print("Password: TestUser123!")
    print("Emails: test1@topkit.com, test2@topkit.com, test3@topkit.com")

if __name__ == "__main__":
    asyncio.run(create_test_users())