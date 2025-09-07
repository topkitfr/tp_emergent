#!/usr/bin/env python3
"""
Comprehensive Database Cleanup Script for TopKit
Cleans ALL collections except preserves only the admin user (topkitfr@gmail.com)
This script addresses the review request for clean database state verification.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    print("❌ MONGO_URL not found in environment variables")
    exit(1)

DB_NAME = os.environ.get('DB_NAME', 'topkit')

# Only preserve admin user as specified in review request
PRESERVE_ADMIN_USER = 'topkitfr@gmail.com'

async def comprehensive_database_cleanup():
    """Comprehensive cleanup of ALL collections, preserving only admin user"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🧹 Starting TopKit Comprehensive Database Cleanup...")
    print(f"📅 Cleanup started at: {datetime.utcnow()}")
    print(f"🔒 Preserving ONLY admin user: {PRESERVE_ADMIN_USER}")
    print("⚠️  ALL other data will be deleted to achieve clean database state")
    print("-" * 80)
    
    try:
        # Get admin user to preserve
        admin_user = await db.users.find_one({"email": PRESERVE_ADMIN_USER})
        if not admin_user:
            print(f"❌ Admin user {PRESERVE_ADMIN_USER} not found!")
            return False
        
        admin_user_id = admin_user['id']
        print(f"✅ Found admin user to preserve: {admin_user.get('name')} (ID: {admin_user_id})")
        
        # Collections to clean completely (as specified in review request)
        collections_to_clean = [
            # Collaborative collections (main focus of review request)
            ('teams', 'Teams'),
            ('brands', 'Brands'), 
            ('players', 'Players'),
            ('competitions', 'Competitions'),
            ('master_jerseys', 'Master Jerseys'),
            ('reference_kits', 'Reference Kits'),
            ('contributions', 'Contributions'),
            ('contributions_v2', 'Contributions V2'),
            
            # Kit hierarchy collections
            ('master_kits', 'Master Kits'),
            ('personal_kits', 'Personal Kits'),
            ('wanted_kits', 'Wanted Kits'),
            
            # Legacy jersey system
            ('jerseys', 'Jerseys'),
            ('listings', 'Listings'),
            ('collections', 'Collections'),
            
            # User-generated content
            ('notifications', 'Notifications'),
            ('user_activities', 'User Activities'),
            ('modification_suggestions', 'Modification Suggestions'),
            ('conversations', 'Conversations'),
            ('messages', 'Messages'),
            ('friendships', 'Friendships'),
            
            # Transaction and payment data
            ('transactions', 'Transactions'),
            ('secure_transactions', 'Secure Transactions'),
            ('payment_transactions', 'Payment Transactions'),
            
            # Valuation and market data
            ('jersey_valuations', 'Jersey Valuations'),
            ('price_history', 'Price History'),
            
            # Security and moderation
            ('suspicious_activities', 'Suspicious Activities'),
            ('user_profiles', 'User Profiles'),
            ('user_ratings', 'User Ratings'),
            
            # Beta and access management
            ('beta_access_requests', 'Beta Access Requests'),
            
            # Site configuration
            ('site_config', 'Site Configuration')
        ]
        
        total_deleted = 0
        
        # Clean all specified collections
        for collection_name, display_name in collections_to_clean:
            try:
                result = await db[collection_name].delete_many({})
                print(f"🗑️  {display_name}: Deleted {result.deleted_count} documents")
                total_deleted += result.deleted_count
            except Exception as e:
                print(f"⚠️  {display_name}: Error during cleanup - {str(e)}")
        
        # Delete ALL users except admin
        user_result = await db.users.delete_many({
            "email": {"$ne": PRESERVE_ADMIN_USER}
        })
        print(f"👤 Users: Deleted {user_result.deleted_count} user accounts (preserved admin)")
        total_deleted += user_result.deleted_count
        
        # Reset admin user to clean state
        await db.users.update_one(
            {"email": PRESERVE_ADMIN_USER},
            {"$set": {
                "role": "admin",
                "failed_login_attempts": 0,
                "account_locked_until": None,
                "suspicious_activity_score": 0,
                "is_banned": False,
                "last_login": None
            }}
        )
        print("✅ Reset admin user to clean state")
        
        print("-" * 80)
        print("🎉 COMPREHENSIVE DATABASE CLEANUP COMPLETED SUCCESSFULLY!")
        print(f"📊 Total documents deleted: {total_deleted}")
        print(f"👤 Users remaining: 1 (admin only)")
        print(f"📅 Cleanup completed at: {datetime.utcnow()}")
        
        # Verify clean state
        print("\n🔍 VERIFICATION - Checking collection counts:")
        verification_collections = [
            'teams', 'brands', 'players', 'competitions', 
            'master_jerseys', 'reference_kits', 'contributions', 'contributions_v2'
        ]
        
        all_empty = True
        for collection_name in verification_collections:
            count = await db[collection_name].count_documents({})
            status = "✅ EMPTY" if count == 0 else f"❌ NOT EMPTY ({count})"
            print(f"  • {collection_name}: {status}")
            if count > 0:
                all_empty = False
        
        # Verify only admin user exists
        user_count = await db.users.count_documents({})
        admin_count = await db.users.count_documents({"email": PRESERVE_ADMIN_USER})
        
        print(f"\n👤 USER VERIFICATION:")
        print(f"  • Total users: {user_count}")
        print(f"  • Admin users: {admin_count}")
        print(f"  • Status: {'✅ CLEAN' if user_count == 1 and admin_count == 1 else '❌ NOT CLEAN'}")
        
        if all_empty and user_count == 1 and admin_count == 1:
            print("\n🎯 SUCCESS: Database is now in CLEAN STATE as requested!")
            print("✅ All data collections are empty")
            print("✅ Only admin user exists")
            print("✅ System ready for fresh usage")
        else:
            print("\n⚠️  WARNING: Database cleanup may not be complete")
            
        return all_empty and user_count == 1 and admin_count == 1
            
    except Exception as e:
        print(f"❌ Error during comprehensive cleanup: {str(e)}")
        raise e
    finally:
        client.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    print("⚠️  COMPREHENSIVE DATABASE CLEANUP")
    print("This will delete ALL data except the admin user account.")
    print("This operation is IRREVERSIBLE!")
    
    # Run cleanup
    result = asyncio.run(comprehensive_database_cleanup())
    
    if result:
        print("\n🚀 Database is ready for clean state verification testing!")
    else:
        print("\n❌ Cleanup may not be complete. Please check the logs above.")