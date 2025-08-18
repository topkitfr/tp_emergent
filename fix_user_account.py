#!/usr/bin/env python3
"""
Fix user account issues for steinmetzlivio@gmail.com
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def fix_user_account():
    """Fix or create user account"""
    # Get MongoDB connection
    mongo_url = os.getenv('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return False
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_url)
        db = client.get_default_database()
        
        email = "steinmetzlivio@gmail.com"
        password = "T0p_Mdp_1288*"
        
        print(f"🔍 Checking user account: {email}")
        
        # Check if user exists
        existing_user = db.users.find_one({"email": email})
        
        if existing_user:
            print("✅ User found in database")
            print(f"   Name: {existing_user.get('name', 'N/A')}")
            print(f"   ID: {existing_user.get('id', 'N/A')}")
            print(f"   Role: {existing_user.get('role', 'N/A')}")
            print(f"   Email Verified: {existing_user.get('email_verified', False)}")
            print(f"   Banned: {existing_user.get('is_banned', False)}")
            print(f"   Failed Login Attempts: {existing_user.get('failed_login_attempts', 0)}")
            
            # Check if account is locked
            if existing_user.get('account_locked_until'):
                print(f"   🔒 Account locked until: {existing_user.get('account_locked_until')}")
            
            # Update password and reset account locks
            hashed_password = hash_password(password)
            
            update_result = db.users.update_one(
                {"email": email},
                {
                    "$set": {
                        "password": hashed_password,
                        "email_verified": True,
                        "is_banned": False,
                        "failed_login_attempts": 0
                    },
                    "$unset": {
                        "account_locked_until": ""
                    }
                }
            )
            
            if update_result.modified_count > 0:
                print("✅ User account updated successfully")
                print("   - Password reset to provided password")
                print("   - Email verified: True")
                print("   - Account unlocked")
                print("   - Failed login attempts reset")
            else:
                print("⚠️  No changes needed")
            
        else:
            print("❌ User not found. Creating new account...")
            
            # Create new user
            user_id = str(uuid.uuid4())
            hashed_password = hash_password(password)
            
            new_user = {
                "id": user_id,
                "email": email,
                "password": hashed_password,
                "name": "Livio Steinmetz",
                "role": "user",
                "created_at": datetime.utcnow(),
                "email_verified": True,
                "is_banned": False,
                "failed_login_attempts": 0,
                "profile_picture": None,
                "bio": "",
                "location": "",
                "two_factor_enabled": False,
                "beta_access": True  # Give beta access
            }
            
            insert_result = db.users.insert_one(new_user)
            
            if insert_result.inserted_id:
                print("✅ User account created successfully")
                print(f"   Email: {email}")
                print(f"   Name: Livio Steinmetz")
                print(f"   ID: {user_id}")
                print(f"   Beta Access: True")
            else:
                print("❌ Failed to create user account")
                return False
        
        print(f"\n🎯 User {email} is now ready to use the application")
        print(f"   Password: {password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing user account: {str(e)}")
        return False
    
    finally:
        client.close()

if __name__ == "__main__":
    print("🔧 Fixing User Account Issues")
    print("=" * 50)
    
    success = fix_user_account()
    
    if success:
        print("\n✅ User account fix completed successfully!")
        print("\nUser can now:")
        print("1. Login with email: steinmetzlivio@gmail.com")
        print("2. Password: T0p_Mdp_1288*")
        print("3. Submit jerseys")
        print("4. Access security settings (password change, 2FA)")
    else:
        print("\n❌ User account fix failed")
        sys.exit(1)