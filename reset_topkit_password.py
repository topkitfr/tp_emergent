"""
Script to reset password for topkitfr@gmail.com account
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from passlib.context import CryptContext

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
NEW_PASSWORD = "TopKitAdmin2024!"

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_password():
    """Reset password for topkitfr@gmail.com"""
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        logger.info(f"Connected to database: {db.name}")
        
        # Find the user
        user = await db.users.find_one({"email": TARGET_USER_EMAIL})
        if not user:
            logger.error(f"❌ User {TARGET_USER_EMAIL} not found")
            return
        
        logger.info(f"✅ Found user: {user['name']} (ID: {user['id']})")
        
        # Hash the new password
        hashed_password = pwd_context.hash(NEW_PASSWORD)
        
        # Update the password
        result = await db.users.update_one(
            {"email": TARGET_USER_EMAIL},
            {"$set": {"password_hash": hashed_password}}
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ Password updated successfully for {TARGET_USER_EMAIL}")
            logger.info(f"📋 New login credentials:")
            logger.info(f"  Email: {TARGET_USER_EMAIL}")
            logger.info(f"  Password: {NEW_PASSWORD}")
        else:
            logger.error(f"❌ Failed to update password")
            
        # Verify the password works
        updated_user = await db.users.find_one({"email": TARGET_USER_EMAIL})
        if pwd_context.verify(NEW_PASSWORD, updated_user["password_hash"]):
            logger.info(f"✅ Password verification successful")
        else:
            logger.error(f"❌ Password verification failed")
        
    except Exception as e:
        logger.error(f"❌ Error resetting password: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(reset_password())