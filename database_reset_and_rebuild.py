#!/usr/bin/env python3
"""
Complete database reset and rebuild with clean interconnected data structure
"""

import asyncio
import uuid
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def complete_database_reset_and_rebuild():
    """Complete database reset and rebuild with interconnected structure"""
    
    print("🚀 Starting complete database reset and rebuild...")
    
    # Step 1: Preserve essential users
    print("\n📥 Step 1: Preserving essential user accounts...")
    
    essential_users = []
    async for user in db.users.find({"email": {"$in": ["topkitfr@gmail.com", "steinmetzlivio@gmail.com"]}}):
        essential_users.append(user)
        print(f"✅ Preserved user: {user['email']} ({user.get('role', 'user')})")
    
    if len(essential_users) == 0:
        print("⚠️ No essential users found, creating admin user...")
        # Create admin user
        hashed_password = bcrypt.hashpw("TopKitSecure789#".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": "topkitfr@gmail.com", 
            "password": hashed_password,
            "name": "TopKit Admin",
            "role": "admin",
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "profile_picture": None,
            "settings": {
                "notifications": True,
                "privacy": "public"
            }
        }
        essential_users.append(admin_user)
        print("✅ Created admin user: topkitfr@gmail.com")
        
        # Create regular user
        hashed_password2 = bcrypt.hashpw("T0p_Mdp_1288*".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        regular_user = {
            "id": str(uuid.uuid4()),
            "email": "steinmetzlivio@gmail.com",
            "password": hashed_password2,
            "name": "Livio Steinmetz",
            "role": "user", 
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "profile_picture": None,
            "settings": {
                "notifications": True,
                "privacy": "public"
            }
        }
        essential_users.append(regular_user)
        print("✅ Created regular user: steinmetzlivio@gmail.com")
    
    # Step 2: Complete database wipe
    print("\n🗑️ Step 2: Complete database wipe...")
    
    # List all collections
    collections = await db.list_collection_names()
    wipe_count = 0
    
    for collection_name in collections:
        if collection_name not in ['users']:  # We'll handle users separately
            count = await db[collection_name].count_documents({})
            if count > 0:
                result = await db[collection_name].delete_many({})
                print(f"✅ Wiped {collection_name}: {result.deleted_count} documents")
                wipe_count += result.deleted_count
    
    # Wipe users and restore essential ones
    await db.users.delete_many({})
    print(f"✅ Wiped users collection")
    
    print(f"🧹 Total documents wiped: {wipe_count}")
    
    # Step 3: Restore essential users
    print("\n👥 Step 3: Restoring essential users...")
    
    if essential_users:
        await db.users.insert_many(essential_users)
        print(f"✅ Restored {len(essential_users)} essential users")
        for user in essential_users:
            print(f"   - {user['email']} ({user.get('role', 'user')})")
    
    # Step 4: Rebuild competitions (from previous CSV data)
    print("\n🏆 Step 4: Rebuilding competitions...")
    
    competitions_data = [
        {"competition_name": "Ligue 1", "official_name": "Ligue 1 Uber Eats", "type": "National league", "confederations_federations": ["UEFA"], "country": "France", "level": 1},
        {"competition_name": "Premier League", "official_name": "Premier League", "type": "National league", "confederations_federations": ["UEFA"], "country": "United Kingdom", "level": 1},
        {"competition_name": "La Liga", "official_name": "La Liga", "type": "National league", "confederations_federations": ["UEFA"], "country": "Spain", "level": 1},
        {"competition_name": "Serie A", "official_name": "Serie A", "type": "National league", "confederations_federations": ["UEFA"], "country": "Italy", "level": 1},
        {"competition_name": "Bundesliga", "official_name": "Bundesliga", "type": "National league", "confederations_federations": ["UEFA"], "country": "Germany", "level": 1},
        {"competition_name": "UEFA Champions League", "official_name": "UEFA Champions League", "type": "Continental competition", "confederations_federations": ["UEFA"], "country": None, "level": 1},
        {"competition_name": "UEFA Europa League", "official_name": "UEFA Europa League", "type": "Continental competition", "confederations_federations": ["UEFA"], "country": None, "level": 1},
        {"competition_name": "FIFA World Cup", "official_name": "FIFA World Cup", "type": "International competition", "confederations_federations": ["FIFA"], "country": None, "level": 1},
    ]
    
    admin_user_id = essential_users[0]["id"]
    competitions = []
    
    for i, comp_data in enumerate(competitions_data):
        competition = {
            "id": str(uuid.uuid4()),
            **comp_data,
            "alternative_names": [],
            "year_created": 1950 + i * 5,
            "logo": None,
            "trophy_photo": None,
            "secondary_images": [],
            "primary_color": None,
            "is_recurring": True,
            "current_season": "2024-25",
            "created_at": datetime.utcnow(),
            "created_by": admin_user_id,
            "verified_level": "community_verified",
            "verified_at": datetime.utcnow(),
            "verified_by": admin_user_id,
            "modification_count": 0,
            "last_modified_at": None,
            "last_modified_by": None,
            "topkit_reference": f"TK-COMP-{str(i+1).zfill(6)}"
        }
        competitions.append(competition)
    
    await db.competitions.insert_many(competitions)
    print(f"✅ Created {len(competitions)} competitions")
    
    # Find key competitions for team relationships
    ligue1 = next(c for c in competitions if c["competition_name"] == "Ligue 1")
    premier_league = next(c for c in competitions if c["competition_name"] == "Premier League")
    la_liga = next(c for c in competitions if c["competition_name"] == "La Liga")
    serie_a = next(c for c in competitions if c["competition_name"] == "Serie A")
    champions_league = next(c for c in competitions if c["competition_name"] == "UEFA Champions League")
    
    # Step 5: Create teams with proper competition relationships
    print("\n⚽ Step 5: Creating teams with competition relationships...")
    
    teams_data = [
        {
            "name": "Paris Saint-Germain",
            "short_name": "PSG",
            "common_names": ["PSG", "Paris SG"],
            "country": "France",
            "city": "Paris",
            "founded_year": 1970,
            "primary_competition_id": ligue1["id"],
            "current_competitions": [ligue1["id"], champions_league["id"]],
            "colors": ["navy", "red", "white"]
        },
        {
            "name": "Olympique Lyonnais",
            "short_name": "OL", 
            "common_names": ["OL", "Lyon"],
            "country": "France",
            "city": "Lyon",
            "founded_year": 1950,
            "primary_competition_id": ligue1["id"],
            "current_competitions": [ligue1["id"]],
            "colors": ["blue", "white", "red"]
        },
        {
            "name": "FC Barcelona",
            "short_name": "Barça",
            "common_names": ["Barça", "Barcelona"],
            "country": "Spain",
            "city": "Barcelona", 
            "founded_year": 1899,
            "primary_competition_id": la_liga["id"],
            "current_competitions": [la_liga["id"], champions_league["id"]],
            "colors": ["blue", "red"]
        },
        {
            "name": "Manchester United",
            "short_name": "Man Utd",
            "common_names": ["Man Utd", "United"],
            "country": "United Kingdom",
            "city": "Manchester",
            "founded_year": 1878,
            "primary_competition_id": premier_league["id"],
            "current_competitions": [premier_league["id"]],
            "colors": ["red", "white"]
        },
        {
            "name": "AC Milan", 
            "short_name": "Milan",
            "common_names": ["Milan", "AC Milan"],
            "country": "Italy",
            "city": "Milan",
            "founded_year": 1899,
            "primary_competition_id": serie_a["id"],
            "current_competitions": [serie_a["id"], champions_league["id"]],
            "colors": ["red", "black"]
        }
    ]
    
    teams = []
    for i, team_data in enumerate(teams_data):
        team = {
            "id": str(uuid.uuid4()),
            **team_data,
            "logo_url": None,
            "competition_history": [],
            "external_ids": {},
            "created_at": datetime.utcnow(),
            "created_by": admin_user_id,
            "verified_level": "community_verified",
            "verified_at": datetime.utcnow(),
            "verified_by": admin_user_id,
            "modification_count": 0,
            "last_modified_at": None,
            "last_modified_by": None,
            "topkit_reference": f"TK-TEAM-{str(i+1).zfill(6)}"
        }
        teams.append(team)
    
    await db.teams.insert_many(teams)
    print(f"✅ Created {len(teams)} teams with competition relationships")
    
    # Step 6: Create brands
    print("\n👕 Step 6: Creating brands...")
    
    brands_data = [
        {"name": "Nike", "official_name": "Nike Inc.", "country": "United States"},
        {"name": "Adidas", "official_name": "Adidas AG", "country": "Germany"},
        {"name": "Puma", "official_name": "Puma SE", "country": "Germany"},
        {"name": "Jordan", "official_name": "Jordan Brand", "country": "United States"},
        {"name": "New Balance", "official_name": "New Balance Athletics", "country": "United States"}
    ]
    
    brands = []
    for i, brand_data in enumerate(brands_data):
        brand = {
            "id": str(uuid.uuid4()),
            **brand_data,
            "logo_url": None,
            "website": None,
            "established_year": 1970 + i * 5,
            "created_at": datetime.utcnow(),
            "created_by": admin_user_id,
            "verified_level": "community_verified",
            "verified_at": datetime.utcnow(),
            "verified_by": admin_user_id,
            "modification_count": 0,
            "last_modified_at": None,
            "last_modified_by": None,
            "topkit_reference": f"TK-BRAND-{str(i+1).zfill(6)}"
        }
        brands.append(brand)
    
    await db.brands.insert_many(brands)
    print(f"✅ Created {len(brands)} brands")
    
    # Step 7: Create sample master kits for testing
    print("\n🏟️ Step 7: Creating sample master kits...")
    
    nike = next(b for b in brands if b["name"] == "Nike")
    adidas = next(b for b in brands if b["name"] == "Adidas")
    psg = next(t for t in teams if t["name"] == "Paris Saint-Germain")
    barcelona = next(t for t in teams if t["name"] == "FC Barcelona")
    
    master_kits_data = [
        {
            "team_id": psg["id"],
            "brand_id": nike["id"],
            "season": "2024-25",
            "kit_type": "home",
            "model": "authentic", 
            "colors": ["navy", "red", "white"],
            "pattern": "solid_navy_with_red_stripe"
        },
        {
            "team_id": psg["id"],
            "brand_id": nike["id"],
            "season": "2024-25", 
            "kit_type": "away",
            "model": "authentic",
            "colors": ["white", "navy"],
            "pattern": "solid_white_with_navy_details"
        },
        {
            "team_id": barcelona["id"],
            "brand_id": nike["id"],
            "season": "2024-25",
            "kit_type": "home",
            "model": "authentic",
            "colors": ["blue", "red"],
            "pattern": "vertical_stripes"
        }
    ]
    
    master_kits = []
    for i, kit_data in enumerate(master_kits_data):
        master_kit = {
            "id": str(uuid.uuid4()),
            **kit_data,
            "design_name": f"{kit_data['kit_type'].title()} Kit",
            "primary_color": kit_data["colors"][0],
            "secondary_colors": kit_data["colors"][1:],
            "created_at": datetime.utcnow(),
            "created_by": admin_user_id,
            "verified_level": "community_verified",
            "verified_at": datetime.utcnow(),
            "verified_by": admin_user_id,
            "modification_count": 0,
            "last_modified_at": None,
            "last_modified_by": None,
            "topkit_reference": f"TK-MKIT-{str(i+1).zfill(6)}"
        }
        master_kits.append(master_kit)
    
    await db.master_kits.insert_many(master_kits)
    print(f"✅ Created {len(master_kits)} sample master kits")
    
    # Step 8: Create players for testing
    print("\n🏃 Step 8: Creating sample players...")
    
    players_data = [
        {"name": "Kylian Mbappé", "team_id": psg["id"], "position": "Forward", "numbers": [7, 10]},
        {"name": "Neymar Jr", "team_id": psg["id"], "position": "Forward", "numbers": [10, 11]},
        {"name": "Robert Lewandowski", "team_id": barcelona["id"], "position": "Forward", "numbers": [9]},
        {"name": "Pedri", "team_id": barcelona["id"], "position": "Midfielder", "numbers": [8, 16]},
    ]
    
    players = []
    for i, player_data in enumerate(players_data):
        player = {
            "id": str(uuid.uuid4()),
            **player_data,
            "nationality": "Various",
            "birth_year": 1995 + i,
            "created_at": datetime.utcnow(),
            "created_by": admin_user_id,
            "verified_level": "community_verified",
            "verified_at": datetime.utcnow(),
            "verified_by": admin_user_id,
            "modification_count": 0,
            "last_modified_at": None,
            "last_modified_by": None,
            "topkit_reference": f"TK-PLAYER-{str(i+1).zfill(6)}"
        }
        players.append(player)
    
    await db.players.insert_many(players)
    print(f"✅ Created {len(players)} sample players")
    
    # Step 9: Verification
    print("\n✅ Step 9: Verification...")
    
    # Count documents in each collection
    collections_to_check = [
        'users', 'competitions', 'teams', 'brands', 'master_kits', 'players'
    ]
    
    print("\n📊 Final database state:")
    for collection_name in collections_to_check:
        count = await db[collection_name].count_documents({})
        print(f"   {collection_name}: {count} documents")
    
    # Verify interconnected relationships
    print("\n🔗 Verifying interconnected relationships:")
    
    # Check teams have competition relationships
    teams_with_competitions = await db.teams.count_documents({"primary_competition_id": {"$exists": True}})
    print(f"   Teams with primary competition: {teams_with_competitions}/{len(teams)}")
    
    # Check master kits have team and brand relationships
    master_kits_with_relationships = await db.master_kits.count_documents({
        "team_id": {"$exists": True},
        "brand_id": {"$exists": True}
    })
    print(f"   Master kits with team/brand relationships: {master_kits_with_relationships}/{len(master_kits)}")
    
    print(f"\n🎉 Database reset and rebuild complete!")
    print(f"📧 Admin user: topkitfr@gmail.com / TopKitSecure789#")
    print(f"📧 Regular user: steinmetzlivio@gmail.com / T0p_Mdp_1288*")
    print(f"🎯 Ready for comprehensive testing!")

if __name__ == "__main__":
    asyncio.run(complete_database_reset_and_rebuild())