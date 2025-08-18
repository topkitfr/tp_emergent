#!/usr/bin/env python3
"""
Database Cleanup Script for TopKit
Complètement vide la base de données - 0 maillot, 0 user
Ne garde que les profils de steinmetzlivio@gmail.com et topkitfr@gmail.com
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

DB_NAME = os.environ.get('DB_NAME', 'test_database')

# Users to preserve
PRESERVE_USERS = [
    'topkitfr@gmail.com',
    'steinmetzlivio@gmail.com'
]

async def cleanup_database():
    """Nettoie complètement la base de données en ne gardant que les comptes spécifiés"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🧹 Starting TopKit Complete Database Cleanup...")
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
        
        # 1. Delete ALL jerseys
        jersey_result = await db.jerseys.delete_many({})
        print(f"👕 Deleted {jersey_result.deleted_count} jerseys")
        
        # 2. Delete ALL listings
        listing_result = await db.listings.delete_many({})
        print(f"🏪 Deleted {listing_result.deleted_count} listings")
        
        # 3. Delete ALL collections
        collection_result = await db.collections.delete_many({})
        print(f"📚 Deleted {collection_result.deleted_count} collection entries")
        
        # 4. Delete ALL notifications
        notification_result = await db.notifications.delete_many({})
        print(f"🔔 Deleted {notification_result.deleted_count} notifications")
        
        # 5. Delete ALL user activities
        activity_result = await db.user_activities.delete_many({})
        print(f"📊 Deleted {activity_result.deleted_count} user activities")
        
        # 6. Delete ALL modification suggestions
        suggestion_result = await db.modification_suggestions.delete_many({})
        print(f"💡 Deleted {suggestion_result.deleted_count} modification suggestions")
        
        # 7. Delete ALL conversations and messages
        conversations_result = await db.conversations.delete_many({})
        messages_result = await db.messages.delete_many({})
        print(f"💬 Deleted {conversations_result.deleted_count} conversations and {messages_result.deleted_count} messages")
        
        # 8. Delete ALL friends/relationships
        friends_result = await db.friends.delete_many({})
        print(f"👥 Deleted {friends_result.deleted_count} friend relationships")
        
        # 9. Delete ALL beta access requests
        beta_result = await db.beta_access_requests.delete_many({})
        print(f"🔒 Deleted {beta_result.deleted_count} beta access requests")
        
        # 10. Delete ALL transactions/payments
        transactions_result = await db.transactions.delete_many({})
        secure_transactions_result = await db.secure_transactions.delete_many({})
        payment_transactions_result = await db.payment_transactions.delete_many({})
        print(f"💳 Deleted {transactions_result.deleted_count} transactions, {secure_transactions_result.deleted_count} secure transactions, {payment_transactions_result.deleted_count} payment transactions")
        
        # 11. Delete ALL jersey valuations and price history
        valuations_result = await db.jersey_valuations.delete_many({})
        price_history_result = await db.price_history.delete_many({})
        print(f"💰 Deleted {valuations_result.deleted_count} jersey valuations and {price_history_result.deleted_count} price history entries")
        
        # 12. Delete ALL suspicious activities
        suspicious_result = await db.suspicious_activities.delete_many({})
        print(f"🚨 Deleted {suspicious_result.deleted_count} suspicious activity records")
        
        # 13. Delete ALL user profiles (extended profiles)
        profiles_result = await db.user_profiles.delete_many({})
        print(f"👤 Deleted {profiles_result.deleted_count} user profiles")
        
        # 14. Delete ALL user ratings
        ratings_result = await db.user_ratings.delete_many({})
        print(f"⭐ Deleted {ratings_result.deleted_count} user ratings")
        
        # 15. Delete ALL users except preserved ones
        user_result = await db.users.delete_many({
            "email": {"$nin": PRESERVE_USERS}
        })
        print(f"👤 Deleted {user_result.deleted_count} user accounts")
        
        # 16. Reset preserved users' roles and clean their data
        await db.users.update_one(
            {"email": "topkitfr@gmail.com"},
            {"$set": {
                "role": "admin",
                "failed_login_attempts": 0,
                "account_locked_until": None,
                "suspicious_activity_score": 0,
                "is_banned": False
            }}
        )
        
        await db.users.update_one(
            {"email": "steinmetzlivio@gmail.com"},
            {"$set": {
                "role": "user",
                "failed_login_attempts": 0,
                "account_locked_until": None,
                "suspicious_activity_score": 0,
                "is_banned": False
            }}
        )
        print("✅ Updated preserved user roles and cleaned their data")
        
        # 17. Reset site mode to private for clean deployment
        site_config_result = await db.site_config.delete_many({})
        await db.site_config.insert_one({"mode": "private"})
        print(f"🔒 Reset site mode to private (cleared {site_config_result.deleted_count} old config entries)")
        
        print("-" * 60)
        print("✅ Complete database cleanup completed successfully!")
        print(f"📊 Summary:")
        print(f"  • Jerseys deleted: {jersey_result.deleted_count}")
        print(f"  • Listings deleted: {listing_result.deleted_count}")
        print(f"  • Collections deleted: {collection_result.deleted_count}")
        print(f"  • Notifications deleted: {notification_result.deleted_count}")
        print(f"  • User activities deleted: {activity_result.deleted_count}")
        print(f"  • Modification suggestions deleted: {suggestion_result.deleted_count}")
        print(f"  • Conversations deleted: {conversations_result.deleted_count}")
        print(f"  • Messages deleted: {messages_result.deleted_count}")
        print(f"  • Friend relationships deleted: {friends_result.deleted_count}")
        print(f"  • Beta access requests deleted: {beta_result.deleted_count}")
        print(f"  • All transactions deleted: {transactions_result.deleted_count + secure_transactions_result.deleted_count + payment_transactions_result.deleted_count}")
        print(f"  • Jersey valuations deleted: {valuations_result.deleted_count}")
        print(f"  • Price history deleted: {price_history_result.deleted_count}")
        print(f"  • Suspicious activities deleted: {suspicious_result.deleted_count}")
        print(f"  • User profiles deleted: {profiles_result.deleted_count}")
        print(f"  • User ratings deleted: {ratings_result.deleted_count}")
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