#!/usr/bin/env python3

import asyncio
import os
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def add_sample_listings():
    """Add sample listings to help with cart testing"""
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Get user IDs (we'll use steinmetzlivio for sample listings)
        user = await db.users.find_one({"email": "steinmetzlivio@gmail.com"})
        if not user:
            print("❌ User steinmetzlivio@gmail.com not found")
            return
            
        user_id = user["id"]
        print(f"✅ Found user: {user['name']} ({user_id})")
        
        # Sample jersey data
        sample_jerseys = [
            {
                "id": str(uuid.uuid4()),
                "team": "FC Barcelona",
                "season": "24/25",
                "player": "Lewandowski",
                "size": "L",
                "condition": "new",
                "description": "Official FC Barcelona home jersey 24/25 season with Lewandowski #9",
                "league": "La Liga",
                "status": "approved",
                "submitted_by": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "reference": f"TK-{str(uuid.uuid4())[:6].upper()}",
                "images": ["https://dummyimage.com/300x400/1a56db/ffffff.png&text=Barcelona+Home"]
            },
            {
                "id": str(uuid.uuid4()),
                "team": "Real Madrid",
                "season": "24/25", 
                "player": "Vinicius Jr",
                "size": "M",
                "condition": "excellent",
                "description": "Real Madrid home jersey 24/25 with Vinicius Jr #7",
                "league": "La Liga",
                "status": "approved",
                "submitted_by": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "reference": f"TK-{str(uuid.uuid4())[:6].upper()}",
                "images": ["https://dummyimage.com/300x400/ffffff/000000.png&text=Real+Madrid+Home"]
            },
            {
                "id": str(uuid.uuid4()),
                "team": "Manchester City",
                "season": "24/25",
                "player": "Haaland",
                "size": "L",
                "condition": "good",
                "description": "Manchester City home jersey 24/25 with Haaland #9",
                "league": "Premier League",
                "status": "approved",
                "submitted_by": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "reference": f"TK-{str(uuid.uuid4())[:6].upper()}",
                "images": ["https://dummyimage.com/300x400/6cabdd/ffffff.png&text=Man+City+Home"]
            }
        ]
        
        # Insert sample jerseys
        for jersey in sample_jerseys:
            await db.jerseys.insert_one(jersey)
            print(f"✅ Added jersey: {jersey['team']} - {jersey['player']}")
        
        # Sample listings
        sample_listings = []
        for i, jersey in enumerate(sample_jerseys):
            listing = {
                "id": str(uuid.uuid4()),
                "jersey_id": jersey["id"],
                "seller_id": user_id,
                "price": [89.99, 119.99, 94.99][i],  # Different prices
                "condition": jersey["condition"],
                "size": jersey["size"],
                "description": f"Selling {jersey['team']} jersey in {jersey['condition']} condition",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "jersey": jersey  # Embed jersey data for easier querying
            }
            sample_listings.append(listing)
        
        # Insert sample listings
        for listing in sample_listings:
            await db.listings.insert_one(listing)
            print(f"✅ Added listing: {listing['jersey']['team']} - €{listing['price']}")
        
        print(f"\n🎉 Successfully added {len(sample_jerseys)} jerseys and {len(sample_listings)} listings for cart testing!")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_sample_listings())