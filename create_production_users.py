#!/usr/bin/env python3
"""
Create Production User Accounts for TopKit
Creates multiple user accounts in the production environment with beta access
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

# Production user accounts to create
PRODUCTION_USERS = [
    {
        "email": "beltramopierre@gmail.com",
        "name": "Pierre Beltramo",
        "password": "TopKitBeta2025!"
    },
    {
        "email": "Bacquet.florent@gmail.com", 
        "name": "Florent Bacquet",
        "password": "TopKitBeta2025!"
    },
    {
        "email": "steinmetzpierre@gmail.com",
        "name": "Pierre Steinmetz", 
        "password": "TopKitBeta2025!"
    },
    {
        "email": "thomasteinmetz@gmail.com",
        "name": "Thomas Steinmetz",
        "password": "TopKitBeta2025!"
    }
]

async def create_production_users():
    """Create all production user accounts with beta access"""
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🚀 Creating Production User Accounts for TopKit")
    print("=" * 60)
    print(f"📅 Creation started at: {datetime.utcnow()}")
    print(f"🏭 Environment: Production")
    print(f"📊 Users to create: {len(PRODUCTION_USERS)}")
    print("-" * 60)
    
    created_users = []
    existing_users = []
    errors = []
    
    try:
        for user_data in PRODUCTION_USERS:
            email = user_data["email"]
            name = user_data["name"]
            password = user_data["password"]
            
            print(f"\n👤 Processing user: {email}")
            
            try:
                # Check if user already exists
                existing_user = await db.users.find_one({"email": email})
                if existing_user:
                    print(f"   ✅ User already exists: {existing_user.get('name')}")
                    print(f"      ID: {existing_user.get('id')}")
                    print(f"      Role: {existing_user.get('role', 'user')}")
                    print(f"      Beta Access: {existing_user.get('beta_access', False)}")
                    existing_users.append(email)
                    continue
                
                # Hash password
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Create user account
                new_user = {
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "password_hash": password_hash,
                    "name": name,
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
                
                print(f"   ✅ Created user: {name}")
                print(f"      Email: {email}")
                print(f"      ID: {new_user['id']}")
                print(f"      Password: {password}")
                print(f"      Beta Access: {new_user['beta_access']}")
                print(f"      Email Verified: {new_user['email_verified']}")
                
                created_users.append({
                    "email": email,
                    "name": name,
                    "id": new_user['id'],
                    "password": password
                })
                
            except Exception as user_error:
                print(f"   ❌ Error creating user {email}: {user_error}")
                errors.append(f"{email}: {str(user_error)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PRODUCTION USER CREATION SUMMARY")
        print("=" * 60)
        
        if created_users:
            print(f"✅ Successfully created {len(created_users)} user(s):")
            for user in created_users:
                print(f"   • {user['name']} ({user['email']})")
                print(f"     ID: {user['id']}")
                print(f"     Password: {user['password']}")
        
        if existing_users:
            print(f"\nℹ️  {len(existing_users)} user(s) already existed:")
            for email in existing_users:
                print(f"   • {email}")
        
        if errors:
            print(f"\n❌ {len(errors)} error(s) occurred:")
            for error in errors:
                print(f"   • {error}")
        
        print(f"\n📋 PRODUCTION ACCOUNT DETAILS:")
        print("=" * 60)
        
        all_users = await db.users.find({"email": {"$in": [user["email"] for user in PRODUCTION_USERS]}}).to_list(None)
        
        for user in all_users:
            print(f"📧 {user.get('email')}")
            print(f"   👤 Name: {user.get('name')}")
            print(f"   🆔 ID: {user.get('id')}")
            print(f"   🔑 Password: TopKitBeta2025!")
            print(f"   🚀 Beta Access: {user.get('beta_access', False)}")
            print(f"   ✅ Email Verified: {user.get('email_verified', False)}")
            print(f"   📅 Created: {user.get('created_at', 'Unknown')}")
            print()
        
        print("🎯 INSTRUCTIONS FOR USERS:")
        print("=" * 60)
        print("1. 🌐 Go to: https://topkit-beta.emergent.host/")
        print("2. 🔵 Click: 'Se Connecter à la Bêta'")
        print("3. 📧 Enter your email address")
        print("4. 🔐 Password: TopKitBeta2025!")
        print("5. ✅ You will have full access to all beta features")
        print()
        print("💡 Recommend users change their password after first login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Fatal error during user creation: {str(e)}")
        return False
    finally:
        client.close()
        print(f"\n🔌 Database connection closed")
        print(f"📅 Process completed at: {datetime.utcnow()}")

if __name__ == "__main__":
    asyncio.run(create_production_users())