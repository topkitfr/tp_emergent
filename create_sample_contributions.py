#!/usr/bin/env python3
"""
Create sample enhanced contributions for testing the voting system
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('backend/.env')
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def create_sample_contributions():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Get test users
    test_users = await db.users.find({"email": {"$in": ["test1@topkit.com", "test2@topkit.com", "test3@topkit.com"]}}).to_list(None)
    if len(test_users) < 3:
        print("❌ Need 3 test users. Please run create_test_users.py first.")
        return
    
    print(f"Found {len(test_users)} test users")
    
    # Sample contributions to create
    sample_contributions = [
        {
            "id": str(uuid.uuid4()),
            "title": "New Team: FC Barcelona Youth",
            "entity_type": "team",
            "status": "pending_review",
            "contributor_id": test_users[0]["id"],
            "data": {
                "name": "FC Barcelona Youth",
                "country": "Spain",
                "city": "Barcelona",
                "founded_year": 1995,
                "short_name": "Barça Youth"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "title": "New Brand: Kappa Sport",
            "entity_type": "brand", 
            "status": "pending_review",
            "contributor_id": test_users[1]["id"],
            "data": {
                "name": "Kappa Sport",
                "country": "Italy",
                "founded_year": 1916,
                "website": "https://www.kappa.com"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "title": "New Player: Lionel Messi",
            "entity_type": "player",
            "status": "pending_review", 
            "contributor_id": test_users[2]["id"],
            "data": {
                "name": "Lionel Messi",
                "nationality": "Argentina",
                "position": "Forward",
                "date_of_birth": "1987-06-24"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "title": "New Competition: UEFA Champions League 2025",
            "entity_type": "competition",
            "status": "pending_review",
            "contributor_id": test_users[0]["id"], 
            "data": {
                "competition_name": "UEFA Champions League 2025",
                "type": "Continental competition",
                "country": "Europe",
                "level": 1
            }
        }
    ]
    
    print("Creating sample enhanced contributions...")
    
    for contrib_data in sample_contributions:
        # Check if contribution already exists
        existing = await db.enhanced_contributions.find_one({"title": contrib_data["title"]})
        if existing:
            print(f"Contribution '{contrib_data['title']}' already exists, skipping...")
            continue
        
        # Generate TopKit reference
        entity_abbrev = {
            "team": "TEAM",
            "brand": "BRAND", 
            "player": "PLAYER",
            "competition": "COMP"
        }
        topkit_ref = f"TK-{entity_abbrev.get(contrib_data['entity_type'], 'ENT')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Prepare contribution document
        contrib_doc = {
            "id": contrib_data["id"],
            "title": contrib_data["title"],
            "entity_type": contrib_data["entity_type"],
            "status": contrib_data["status"],
            "contributor_id": contrib_data["contributor_id"],
            "data": contrib_data["data"],
            "topkit_reference": topkit_ref,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "upvotes": 0,
            "downvotes": 0,
            "votes": [],
            "images": [],
            "images_count": 0,
            "history": [
                {
                    "action": "created",
                    "user_id": contrib_data["contributor_id"],
                    "timestamp": datetime.utcnow(),
                    "details": "Initial contribution created"
                }
            ],
            "moderation_history": [],
            "review_notes": [],
            "auto_approved": False,
            "auto_rejected": False
        }
        
        # Insert contribution
        result = await db.enhanced_contributions.insert_one(contrib_doc)
        print(f"✅ Created contribution: {contrib_data['title']} (Ref: {topkit_ref})")
    
    # Verify created contributions
    print("\n=== VERIFICATION ===")
    all_contributions = await db.enhanced_contributions.find({}).to_list(None)
    print(f"Total enhanced contributions: {len(all_contributions)}")
    
    for contrib in all_contributions:
        print(f"- {contrib['title']} ({contrib['entity_type']}) - Status: {contrib['status']} - Ref: {contrib['topkit_reference']}")
    
    print(f"\n🎉 Sample contributions created successfully!")
    print("Users can now:")
    print("1. View contributions on the Community DB page")
    print("2. Vote on pending contributions")
    print("3. Test auto-approval (3 upvotes) and auto-rejection (2 downvotes)")
    print("4. Access individual contribution detail pages")

if __name__ == "__main__":
    asyncio.run(create_sample_contributions())