"""
Script to create contribution entries for XP system
Creates gamification entries for all entities assigned to topkitfr@gmail.com
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import uuid
from datetime import datetime, timezone

# Load environment variables
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'topkit')
TARGET_USER_EMAIL = "topkitfr@gmail.com"

async def create_contribution_entries():
    """Create contribution entries for XP system"""
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        logger.info(f"Connected to database: {db.name}")
        
        # Find target user
        user = await db.users.find_one({"email": TARGET_USER_EMAIL})
        if not user:
            logger.error(f"❌ User {TARGET_USER_EMAIL} not found")
            return
        
        user_id = user["id"]
        logger.info(f"✅ Found user: {user['name']} (ID: {user_id})")
        
        # Collections to process with their XP mapping
        collections_info = [
            ("teams", "team", 10),
            ("brands", "brand", 10),
            ("players", "player", 10),
            ("competitions", "competition", 10),
            ("master_kits", "jersey", 20)  # Master kit = jersey in XP system
        ]
        
        total_created = 0
        total_xp = 0
        
        for collection_name, item_type, xp_value in collections_info:
            collection = db[collection_name]
            
            # Get all entities created by this user
            entities = await collection.find({"created_by": user_id}).to_list(length=None)
            
            logger.info(f"📊 Processing {len(entities)} {collection_name}...")
            
            # Create contribution entries
            for entity in entities:
                entity_id = entity["id"]
                
                # Check if contribution entry already exists
                existing = await db.contributions_gamification.find_one({
                    "user_id": user_id,
                    "item_type": item_type,
                    "item_id": entity_id
                })
                
                if not existing:
                    # Create new contribution entry
                    contribution_entry = {
                        "id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "item_type": item_type,
                        "item_id": entity_id,
                        "is_approved": True,  # Pre-approved since user is admin
                        "xp_awarded": xp_value,
                        "created_at": datetime.now(timezone.utc),
                        "approved_at": datetime.now(timezone.utc),
                        "approved_by": "system"  # System approval
                    }
                    
                    await db.contributions_gamification.insert_one(contribution_entry)
                    total_created += 1
                    total_xp += xp_value
                    
                    logger.info(f"  ✅ Created contribution entry for {item_type}: {entity.get('name', entity_id)[:30]}...")
        
        # Update user XP
        current_user = await db.users.find_one({"id": user_id})
        current_xp = current_user.get('xp', 0)
        new_xp = current_xp + total_xp
        
        # Calculate new level
        if new_xp >= 2000:
            new_level = "Ballon d'Or"
        elif new_xp >= 500:
            new_level = "Légende"
        elif new_xp >= 100:
            new_level = "Titulaire"
        else:
            new_level = "Remplaçant"
        
        # Update user XP and level
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "xp": new_xp,
                "level": new_level
            }}
        )
        
        logger.info(f"\n🎉 CONTRIBUTION ENTRIES CREATED!")
        logger.info(f"📊 Created entries: {total_created}")
        logger.info(f"📊 Total XP awarded: {total_xp}")
        logger.info(f"📊 User XP: {current_xp} → {new_xp}")
        logger.info(f"📊 User Level: {new_level}")
        
        # Final verification
        final_entries = await db.contributions_gamification.count_documents({"user_id": user_id})
        logger.info(f"📊 Total contribution entries for user: {final_entries}")
        
    except Exception as e:
        logger.error(f"❌ Error creating contribution entries: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_contribution_entries())