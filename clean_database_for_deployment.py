#!/usr/bin/env python3
"""
TopKit Database Cleanup Script for Clean Deployment
Conserve uniquement le compte admin topkitfr@gmail.com
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_database_for_deployment():
    """
    Nettoie la base de données en conservant uniquement le compte admin
    """
    # Get MongoDB connection
    mongo_url = os.getenv('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment variables")
        return False
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_url)
        db = client.get_default_database()
        
        print("🧹 Starting database cleanup for deployment...")
        print("📧 Preserving admin account: topkitfr@gmail.com")
        
        # 1. Keep only admin user
        users_result = db.users.delete_many({
            "email": {"$ne": "topkitfr@gmail.com"}
        })
        print(f"👥 Removed {users_result.deleted_count} non-admin users")
        
        # 2. Clear all jerseys (fresh start for submissions)
        jerseys_result = db.jerseys.delete_many({})
        print(f"👕 Removed {jerseys_result.deleted_count} jerseys")
        
        # 3. Clear all collections
        collections_result = db.collections.delete_many({})
        print(f"📚 Removed {collections_result.deleted_count} collections")
        
        # 4. Clear all listings
        listings_result = db.listings.delete_many({})
        print(f"🏪 Removed {listings_result.deleted_count} listings")
        
        # 5. Clear all conversations and messages
        conversations_result = db.conversations.delete_many({})
        messages_result = db.messages.delete_many({})
        print(f"💬 Removed {conversations_result.deleted_count} conversations and {messages_result.deleted_count} messages")
        
        # 6. Clear all notifications
        notifications_result = db.notifications.delete_many({})
        print(f"🔔 Removed {notifications_result.deleted_count} notifications")
        
        # 7. Clear all friends/relationships
        friends_result = db.friends.delete_many({})
        print(f"👥 Removed {friends_result.deleted_count} friend relationships")
        
        # 8. Clear all beta access requests
        beta_result = db.beta_access_requests.delete_many({})
        print(f"🔒 Removed {beta_result.deleted_count} beta access requests")
        
        # 9. Clear all activities
        activities_result = db.activities.delete_many({})
        print(f"📊 Removed {activities_result.deleted_count} activities")
        
        # 10. Clear all transactions/payments
        transactions_result = db.transactions.delete_many({})
        secure_transactions_result = db.secure_transactions.delete_many({})
        print(f"💳 Removed {transactions_result.deleted_count} transactions and {secure_transactions_result.deleted_count} secure transactions")
        
        # Verify admin user still exists
        admin_user = db.users.find_one({"email": "topkitfr@gmail.com"})
        if admin_user:
            print(f"✅ Admin account preserved: {admin_user.get('name')} ({admin_user.get('email')})")
        else:
            print("❌ WARNING: Admin account not found!")
            return False
        
        # Reset site mode to private for clean deployment
        db.site_config.update_one(
            {},
            {"$set": {"mode": "private"}},
            upsert=True
        )
        print("🔒 Site mode set to private")
        
        print("\n✅ Database cleanup completed successfully!")
        print("🚀 Ready for clean deployment with only admin account")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database cleanup: {str(e)}")
        return False
    
    finally:
        client.close()

if __name__ == "__main__":
    print("🧹 TopKit Database Cleanup for Deployment")
    print("=" * 50)
    
    # Confirmation
    confirm = input("⚠️  This will remove ALL data except the admin account. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cleanup cancelled")
        sys.exit(1)
    
    success = clean_database_for_deployment()
    
    if success:
        print("\n🎉 Database is now clean and ready for deployment!")
        print("\n📋 Next steps:")
        print("1. Test your application locally with the cleaned database")
        print("2. Verify admin login works: topkitfr@gmail.com")
        print("3. Deploy to production using the Deploy button")
        print("4. Test admin access on the deployed application")
    else:
        print("\n❌ Cleanup failed. Please check the errors above.")
        sys.exit(1)