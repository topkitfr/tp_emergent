"""
Script to assign all database entities to Topkitfr@gmail.com user
Assigns teams, brands, players, competitions, and master kits to specific user
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

# Load environment variables from the backend directory
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'topkit')

# Target user email
TARGET_USER_EMAIL = "topkitfr@gmail.com"

async def assign_data_to_user():
    """Main function to assign all data to target user"""
    try:
        # Connect to database
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        logger.info(f"Connected to database: {db.name}")
        
        # Step 1: Find the target user
        user = await db.users.find_one({"email": TARGET_USER_EMAIL})
        if not user:
            logger.error(f"❌ User {TARGET_USER_EMAIL} not found in database")
            return
        
        user_id = user["id"]
        logger.info(f"✅ Found target user: {user['name']} (ID: {user_id})")
        
        # Step 2: Get current counts and check existing assignments
        collections_to_update = [
            ("teams", "teams"),
            ("brands", "brands"), 
            ("players", "players"),
            ("competitions", "competitions"),
            ("master_kits", "master kits")
        ]
        
        results = {}
        
        for collection_name, display_name in collections_to_update:
            collection = db[collection_name]
            
            # Get total count
            total_count = await collection.count_documents({})
            
            # Get count already assigned to this user
            assigned_count = await collection.count_documents({"created_by": user_id})
            
            # Get count with system or other creators
            other_creators_count = await collection.count_documents({"created_by": {"$ne": user_id}})
            
            logger.info(f"📊 {display_name.title()}: Total={total_count}, Already assigned to user={assigned_count}, Others={other_creators_count}")
            
            # Update all entities to be created by target user
            if other_creators_count > 0:
                update_result = await collection.update_many(
                    {"created_by": {"$ne": user_id}},
                    {"$set": {"created_by": user_id}}
                )
                logger.info(f"✅ Updated {update_result.modified_count} {display_name} to be created by {TARGET_USER_EMAIL}")
                results[collection_name] = {
                    "total": total_count,
                    "updated": update_result.modified_count,
                    "already_assigned": assigned_count
                }
            else:
                logger.info(f"ℹ️ All {display_name} already assigned to {TARGET_USER_EMAIL}")
                results[collection_name] = {
                    "total": total_count,
                    "updated": 0,
                    "already_assigned": assigned_count
                }
        
        # Step 3: Verify the assignments
        logger.info("\n📋 FINAL VERIFICATION:")
        total_entities = 0
        total_assigned = 0
        
        for collection_name, display_name in collections_to_update:
            collection = db[collection_name]
            
            # Final count check
            final_total = await collection.count_documents({})
            final_assigned = await collection.count_documents({"created_by": user_id})
            
            total_entities += final_total
            total_assigned += final_assigned
            
            logger.info(f"✅ {display_name.title()}: {final_assigned}/{final_total} assigned to {TARGET_USER_EMAIL}")
        
        # Step 4: Summary
        logger.info(f"\n🎉 ASSIGNMENT COMPLETE!")
        logger.info(f"📊 Total entities: {total_entities}")
        logger.info(f"📊 Assigned to {TARGET_USER_EMAIL}: {total_assigned}")
        logger.info(f"📊 Assignment rate: {(total_assigned/total_entities)*100:.1f}%")
        
        # Step 5: Update user's contribution count (optional)
        user_contributions = await db.contributions_gamification.count_documents({"user_id": user_id})
        logger.info(f"📊 User has {user_contributions} contribution entries for XP tracking")
        
        if total_assigned > user_contributions:
            logger.info(f"💡 Consider creating contribution entries for XP system (missing {total_assigned - user_contributions} entries)")
        
    except Exception as e:
        logger.error(f"❌ Error in assignment process: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(assign_data_to_user())