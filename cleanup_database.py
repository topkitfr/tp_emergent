#!/usr/bin/env python3
"""
Database Cleanup Script for TopKit
Removes all jerseys, listings, collections, notifications, and user activities.
Keeps only specified user accounts: topkitfr@gmail.com and steinmetzlivio@gmail.com
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

# Users to preserve
PRESERVE_USERS = [
    'topkitfr@gmail.com',
    'steinmetzlivio@gmail.com'
]

async def cleanup_database():
    """Clean up the database while preserving specified user accounts"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_default_database()
    
    print("🧹 Starting TopKit Database Cleanup...")
    print(f"📅 Cleanup started at: {datetime.utcnow()}")
    print(f"🔒 Preserving user accounts: {', '.join(PRESERVE_USERS)}")
    print("-" * 60)
    
    try:
        # Get user IDs for preserved accounts
        preserved_user_docs = await db.users.find(
            {"email": {"$in": PRESERVE_USERS}}
        ).to_list(None)
        
        preserved_user_ids = [user['id'] for user in preserved_user_docs]
        print(f"✅ Found {len(preserved_user_ids)} user accounts to preserve")
        
        # 1. Delete all jerseys
        jersey_result = await db.jerseys.delete_many({})
        print(f"🗑️  Deleted {jersey_result.deleted_count} jerseys")
        
        # 2. Delete all listings
        listing_result = await db.listings.delete_many({})
        print(f"🗑️  Deleted {listing_result.deleted_count} listings")
        
        # 3. Delete all collections
        collection_result = await db.collections.delete_many({})
        print(f"🗑️  Deleted {collection_result.deleted_count} collection entries")
        
        # 4. Delete all notifications
        notification_result = await db.notifications.delete_many({})
        print(f"🗑️  Deleted {notification_result.deleted_count} notifications")
        
        # 5. Delete all user activities
        activity_result = await db.user_activities.delete_many({})
        print(f"🗑️  Deleted {activity_result.deleted_count} user activities")
        
        # 6. Delete all modification suggestions
        suggestion_result = await db.modification_suggestions.delete_many({})
        print(f"🗑️  Deleted {suggestion_result.deleted_count} modification suggestions")
        
        # 7. Delete all users except preserved ones
        user_result = await db.users.delete_many({
            "email": {"$nin": PRESERVE_USERS}
        })
        print(f"🗑️  Deleted {user_result.deleted_count} user accounts")
        
        # 8. Reset preserved users' roles (ensure admin role for topkitfr@gmail.com)
        await db.users.update_one(
            {"email": "topkitfr@gmail.com"},
            {"$set": {"role": "admin"}}
        )
        
        await db.users.update_one(
            {"email": "steinmetzlivio@gmail.com"},
            {"$set": {"role": "user"}}
        )
        print("✅ Updated preserved user roles")
        
        print("-" * 60)
        print("✅ Database cleanup completed successfully!")
        print(f"📊 Summary:")
        print(f"  • Jerseys deleted: {jersey_result.deleted_count}")
        print(f"  • Listings deleted: {listing_result.deleted_count}")
        print(f"  • Collections deleted: {collection_result.deleted_count}")
        print(f"  • Notifications deleted: {notification_result.deleted_count}")
        print(f"  • User activities deleted: {activity_result.deleted_count}")
        print(f"  • Modification suggestions deleted: {suggestion_result.deleted_count}")
        print(f"  • User accounts deleted: {user_result.deleted_count}")
        print(f"  • User accounts preserved: {len(preserved_user_ids)}")
        print(f"📅 Cleanup completed at: {datetime.utcnow()}")
        
        # Verify remaining users
        remaining_users = await db.users.find({}).to_list(None)
        print(f"\n👥 Remaining user accounts:")
        for user in remaining_users:
            print(f"  • {user.get('email', 'Unknown')} - Role: {user.get('role', 'user')} - ID: {user.get('id', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        raise e
    finally:
        client.close()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    asyncio.run(cleanup_database())