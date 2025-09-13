#!/usr/bin/env python3
"""
Test server to verify backward compatibility endpoints work
"""
import os
import sys
sys.path.append('/app/backend')

from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.topkit

@app.get("/health")
async def health_check():
    return {"status": "ok", "server": "test_server"}

@app.get("/api/test-stats")
async def test_stats():
    """Test endpoint with hardcoded values"""
    return {
        "master_kits": 999,
        "collections": 888,  
        "users": 777,
        "system": "test_server_working"
    }

@app.get("/api/reference-kits")
async def get_reference_kits_compatibility():
    """Backward compatibility endpoint for reference kits"""
    return []

@app.get("/api/master-jerseys/{master_jersey_id}")
async def get_master_jersey_backward_compat(master_jersey_id: str):
    """Backward compatibility endpoint - redirects master-jerseys to master-kits"""
    try:
        master_kit = await db.master_kits.find_one({"id": master_jersey_id})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master Kit not found")
        
        # Remove MongoDB ObjectId to avoid serialization issues
        if "_id" in master_kit:
            del master_kit["_id"]
            
        return master_kit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in master-jerseys compatibility endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)