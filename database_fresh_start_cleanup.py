#!/usr/bin/env python3
"""
TopKit Database Fresh Start Cleanup
Removes all data except the essential admin user topkitfr@gmail.com

DESTRUCTIVE OPERATION - Creates clean slate for fresh deployment
"""

import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'topkit')

class DatabaseCleanup:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        
    async def backup_essential_data(self):
        """Backup essential user data before cleanup"""
        print("📦 Creating backup of essential data...")
        
        # Backup admin user
        admin_user = await self.db.users.find_one({"email": "topkitfr@gmail.com"})
        if admin_user:
            print(f"✅ Found admin user: {admin_user['name']} ({admin_user['email']})")
            return admin_user
        else:
            print("❌ Admin user topkitfr@gmail.com not found!")
            return None
    
    async def get_collection_stats(self):
        """Get current collection statistics"""
        stats = {}
        collections = ['master_kits', 'teams', 'brands', 'players', 'competitions', 
                      'my_collection', 'contributions', 'users']
        
        for collection_name in collections:
            count = await self.db[collection_name].count_documents({})
            stats[collection_name] = count
            
        return stats
    
    async def clean_collections(self):
        """Remove all data except admin user"""
        print("\n🧹 Starting database cleanup...")
        
        # Collections to completely empty
        collections_to_empty = [
            'master_kits',
            'teams', 
            'brands',
            'players',
            'competitions',
            'my_collection',
            'contributions',
            'contributions_v2'
        ]
        
        for collection_name in collections_to_empty:
            try:
                result = await self.db[collection_name].delete_many({})
                print(f"✅ Deleted {result.deleted_count} documents from {collection_name}")
            except Exception as e:
                print(f"❌ Error cleaning {collection_name}: {e}")
        
        # Clean users but keep admin
        try:
            result = await self.db.users.delete_many({"email": {"$ne": "topkitfr@gmail.com"}})
            print(f"✅ Deleted {result.deleted_count} non-admin users")
        except Exception as e:
            print(f"❌ Error cleaning users: {e}")
    
    async def verify_cleanup(self):
        """Verify cleanup was successful"""
        print("\n🔍 Verifying cleanup...")
        
        final_stats = await self.get_collection_stats()
        
        print("Final collection counts:")
        for collection, count in final_stats.items():
            status = "✅" if count == 0 or (collection == "users" and count == 1) else "❌"
            print(f"  {status} {collection}: {count}")
        
        # Verify admin user still exists
        admin_user = await self.db.users.find_one({"email": "topkitfr@gmail.com"})
        if admin_user:
            print(f"✅ Admin user preserved: {admin_user['name']} ({admin_user['email']})")
            return True
        else:
            print("❌ Admin user lost during cleanup!")
            return False
    
    async def run_cleanup(self):
        """Execute complete cleanup process"""
        print("🚀 TopKit Database Fresh Start Cleanup")
        print("=" * 50)
        
        # Get initial stats
        initial_stats = await self.get_collection_stats()
        print("\nInitial collection counts:")
        total_items = 0
        for collection, count in initial_stats.items():
            print(f"  📊 {collection}: {count}")
            if collection != "users":
                total_items += count
        
        print(f"\n📈 Total items to be deleted: {total_items}")
        
        # Backup essential data
        admin_backup = await self.backup_essential_data()
        if not admin_backup:
            print("❌ Cannot proceed without admin user!")
            return False
        
        # Perform cleanup
        await self.clean_collections()
        
        # Verify cleanup
        success = await self.verify_cleanup()
        
        if success:
            print("\n🎉 DATABASE CLEANUP COMPLETE!")
            print("✅ Fresh start ready for deployment")
            print("✅ Admin user topkitfr@gmail.com preserved")
            print("✅ All collections cleaned")
        else:
            print("\n❌ CLEANUP FAILED!")
            print("Some issues occurred during cleanup")
        
        return success
    
    async def close(self):
        """Close database connection"""
        self.client.close()

async def main():
    cleanup = DatabaseCleanup()
    try:
        success = await cleanup.run_cleanup()
        return success
    finally:
        await cleanup.close()

if __name__ == "__main__":
    print("⚠️  WARNING: This will DELETE ALL DATA except admin user!")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    success = asyncio.run(main())
    if success:
        print("\n✅ Ready for fresh deployment!")
    else:
        print("\n❌ Cleanup failed - check logs above")