#!/usr/bin/env python3
"""
Script to unlock steinmetzlivio@gmail.com account and update password
"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def unlock_account():
    """Unlock the account steinmetzlivio@gmail.com and update password"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client["topkit"]
    users_collection = db["users"]
    
    email = "steinmetzlivio@gmail.com"
    new_password = "T0p_Mdp_1288*"
    
    print(f"🔍 Searching for user: {email}")
    
    # Find the user
    user = await users_collection.find_one({"email": email})
    
    if not user:
        print(f"❌ User {email} not found!")
        return
    
    print(f"✅ User found: {user.get('name', 'Unknown')} (ID: {user['id']})")
    print(f"📊 Current status:")
    print(f"   - Banned: {user.get('is_banned', False)}")
    print(f"   - Account locked until: {user.get('account_locked_until', 'None')}")
    print(f"   - Failed login attempts: {user.get('failed_login_attempts', 0)}")
    
    # Hash the new password
    hashed_password = pwd_context.hash(new_password)
    
    # Update the user - unlock account and update password
    update_data = {
        "password": hashed_password,
        "account_locked_until": None,  # Unlock the account
        "is_banned": False,           # Ensure not banned
        "failed_login_attempts": 0,   # Reset failed attempts
        "updated_at": datetime.utcnow()
    }
    
    result = await users_collection.update_one(
        {"email": email},
        {"$set": update_data}
    )
    
    if result.modified_count > 0:
        print(f"✅ Account unlocked successfully!")
        print(f"🔑 Password updated to: {new_password}")
        print(f"🔓 Account lock removed")
        print(f"⚡ Failed login attempts reset to 0")
        print(f"✨ Account is now accessible for testing")
    else:
        print(f"❌ Failed to update account")
    
    # Verify the changes
    updated_user = await users_collection.find_one({"email": email})
    print(f"\n📋 Verification:")
    print(f"   - Banned: {updated_user.get('is_banned', False)}")
    print(f"   - Account locked until: {updated_user.get('account_locked_until', 'None')}")
    print(f"   - Failed login attempts: {updated_user.get('failed_login_attempts', 0)}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(unlock_account())