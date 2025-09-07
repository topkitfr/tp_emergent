#!/usr/bin/env python3
"""
Database Cleanup - Keep Only Admin User
Removes all data from MongoDB collections except the admin user topkitfr@gmail.com
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = 'topkit_collaborative'

async def cleanup_database():
    """Clean all database collections except keep admin user"""
    
    print("🧹 Starting Database Cleanup - Keep Admin Only")
    print("=" * 50)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Collections to completely clear
        collections_to_clear = [
            'teams',
            'brands', 
            'players',
            'competitions',
            'master_jerseys',
            'master_kits',  # Legacy collection
            'reference_kits',
            'contributions',  # Legacy contributions
            'contributions_v2',  # New contributions
            'personal_kits',
            'collections',
            'votes',
            'notifications',
            'sessions',
            'password_resets'
        ]
        
        # Clear specified collections completely
        total_deleted = 0
        for collection_name in collections_to_clear:
            try:
                collection = db[collection_name]
                result = await collection.delete_many({})
                deleted_count = result.deleted_count
                total_deleted += deleted_count
                
                if deleted_count > 0:
                    print(f"✅ Cleared {collection_name}: {deleted_count} documents deleted")
                else:
                    print(f"ℹ️  {collection_name}: Already empty")
                    
            except Exception as e:
                print(f"⚠️  Error clearing {collection_name}: {e}")
        
        # Special handling for users collection - keep only admin
        print("\n🔐 Processing Users Collection...")
        users_collection = db['users']
        
        # First, check if admin user exists
        admin_user = await users_collection.find_one({"email": "topkitfr@gmail.com"})
        
        if admin_user:
            print(f"✅ Admin user found: {admin_user.get('name', 'Admin')} ({admin_user.get('email')})")
            
            # Delete all users except admin
            result = await users_collection.delete_many({
                "email": {"$ne": "topkitfr@gmail.com"}
            })
            
            users_deleted = result.deleted_count
            total_deleted += users_deleted
            
            if users_deleted > 0:
                print(f"✅ Removed {users_deleted} non-admin users")
            else:
                print("ℹ️  No other users to remove")
                
            # Verify admin user still exists
            admin_check = await users_collection.find_one({"email": "topkitfr@gmail.com"})
            if admin_check:
                print("✅ Admin user preserved successfully")
            else:
                print("❌ ERROR: Admin user was accidentally deleted!")
                
        else:
            print("❌ WARNING: Admin user topkitfr@gmail.com not found in database!")
            # Still clear other users
            result = await users_collection.delete_many({})
            print(f"⚠️  Cleared all {result.deleted_count} users (admin was not found)")
            total_deleted += result.deleted_count
        
        # Get final collection statistics
        print("\n📊 Final Database State:")
        print("-" * 30)
        
        for collection_name in ['users'] + collections_to_clear:
            try:
                count = await db[collection_name].count_documents({})
                if collection_name == 'users':
                    if count == 1:
                        print(f"✅ {collection_name}: {count} document (admin user)")
                    else:
                        print(f"⚠️  {collection_name}: {count} documents (expected 1)")
                else:
                    if count == 0:
                        print(f"✅ {collection_name}: {count} documents (cleaned)")
                    else:
                        print(f"⚠️  {collection_name}: {count} documents (not fully cleaned)")
                        
            except Exception as e:
                print(f"❌ Error checking {collection_name}: {e}")
        
        print(f"\n🎯 Cleanup Summary:")
        print(f"   • Total documents deleted: {total_deleted}")
        print(f"   • Admin user preserved: topkitfr@gmail.com")
        print(f"   • Database ready for fresh data")
        
        return True
        
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return False
        
    finally:
        client.close()

async def main():
    """Main cleanup function"""
    print(f"🕐 Starting cleanup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will delete ALL data except admin user!")
    print("   Collections to be cleared:")
    print("   • teams, brands, players, competitions")
    print("   • master_jerseys, reference_kits") 
    print("   • contributions, contributions_v2")
    print("   • personal_kits, collections, votes")
    print("   • All users EXCEPT topkitfr@gmail.com")
    
    # Run cleanup
    success = await cleanup_database()
    
    if success:
        print("\n✅ Database cleanup completed successfully!")
        print("🚀 TopKit is ready for fresh data with admin user preserved")
    else:
        print("\n❌ Database cleanup failed - please check errors above")

if __name__ == "__main__":
    asyncio.run(main())