#!/usr/bin/env python3
"""
Verify Bacquet account exists and can authenticate
"""

import asyncio
import os
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv('/app/backend/.env')

async def verify_bacquet_account():
    """Verify the Bacquet account exists and test authentication"""
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test different email variations
        email_variations = [
            "Bacquet.florent@gmail.com",
            "bacquet.florent@gmail.com",
            "Bacquet.florent@gmail.com".lower()
        ]
        
        print("🔍 Searching for Bacquet account...")
        
        # Check each variation
        for email in email_variations:
            user = await db.users.find_one({"email": email})
            if user:
                print(f"✅ Found user with email: {email}")
                print(f"   Name: {user.get('name')}")
                print(f"   ID: {user.get('id')}")
                print(f"   Role: {user.get('role')}")
                print(f"   Email Verified: {user.get('email_verified')}")
                print(f"   Beta Access: {user.get('beta_access')}")
                print(f"   Is Banned: {user.get('is_banned')}")
                print(f"   Failed Login Attempts: {user.get('failed_login_attempts')}")
                
                # Check password hash
                if user.get('password_hash'):
                    print(f"   ✅ Password hash exists: {user['password_hash'][:20]}...")
                else:
                    print(f"   ❌ No password_hash field found!")
                
                # Test password verification
                test_password = "TopKitBeta2025!"
                if user.get('password_hash'):
                    try:
                        password_valid = bcrypt.checkpw(
                            test_password.encode('utf-8'), 
                            user['password_hash'].encode('utf-8')
                        )
                        print(f"   Password validation: {'✅ Valid' if password_valid else '❌ Invalid'}")
                    except Exception as e:
                        print(f"   Password validation error: {e}")
                
                print(f"\n📋 Full user document:")
                for key, value in user.items():
                    if key != 'password_hash':  # Don't print full password hash
                        print(f"   {key}: {value}")
                
                return user
        
        print("❌ User not found with any email variation")
        
        # Show all users in database
        all_users = await db.users.find({}).to_list(None)
        print(f"\n👥 All users in database ({len(all_users)} total):")
        for user in all_users:
            print(f"  • {user.get('email', 'No email')} - {user.get('name', 'No name')} - Role: {user.get('role', 'user')}")
        
        return None
        
    except Exception as e:
        print(f"❌ Error verifying account: {e}")
        return None
    finally:
        client.close()

async def test_backend_auth():
    """Test backend authentication API directly"""
    
    print("\n🧪 Testing backend authentication API...")
    
    # Get backend URL from environment
    backend_url = "http://localhost:8001"  # Internal backend URL
    
    auth_data = {
        "email": "Bacquet.florent@gmail.com",
        "password": "TopKitBeta2025!"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/auth/login",
            json=auth_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authentication successful!")
            print(f"   Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User: {data.get('user', {})}")
        else:
            print(f"❌ Authentication failed!")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
    except Exception as e:
        print(f"❌ Authentication test error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_bacquet_account())
    asyncio.run(test_backend_auth())