"""
Script to upload CSV data to TopKit database
Handles team, competition, player, and brand data
"""
import asyncio
import csv
import aiohttp
import uuid
from datetime import datetime, timezone
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

# CSV file URLs
CSV_URLS = {
    'team': 'https://customer-assets.emergentagent.com/job_d48e1460-a6f0-4846-8ff9-5b30d211f65a/artifacts/zer2mfel_team.csv',
    'competition': 'https://customer-assets.emergentagent.com/job_d48e1460-a6f0-4846-8ff9-5b30d211f65a/artifacts/do23njgh_competition.csv',
    'player': 'https://customer-assets.emergentagent.com/job_d48e1460-a6f0-4846-8ff9-5b30d211f65a/artifacts/fvs625ah_player.csv',
    'brand': 'https://customer-assets.emergentagent.com/job_d48e1460-a6f0-4846-8ff9-5b30d211f65a/artifacts/u7pm51yn_brand.csv'
}

def generate_topkit_reference(entity_type: str, count: int) -> str:
    """Generate TopKit reference in format TK-{TYPE}-{6-digit-number}"""
    type_codes = {
        'team': 'TEAM',
        'competition': 'COMP',
        'player': 'PLAY',
        'brand': 'BRND'
    }
    return f"TK-{type_codes.get(entity_type, 'UNKN')}-{count:06d}"

async def download_csv(session, url: str) -> str:
    """Download CSV file and return content as string"""
    async with session.get(url) as response:
        if response.status == 200:
            return await response.text()
        else:
            raise Exception(f"Failed to download CSV from {url}, status: {response.status}")

def parse_team_csv(csv_content: str) -> list:
    """Parse team CSV and return list of team documents"""
    teams = []
    reader = csv.DictReader(csv_content.splitlines())
    
    for i, row in enumerate(reader, 1):
        team = {
            'id': str(uuid.uuid4()),
            'name': row['Team Name'].strip(),
            'short_name': row['Short Name'].strip() if row['Short Name'] else None,
            'country': row['Country'].strip(),
            'city': row['City'].strip() if row['City'] else None,
            'founded_year': int(row['Founded Year']) if row['Founded Year'] and row['Founded Year'].isdigit() else None,
            'colors': [color.strip() for color in row['Team Colors'].split(',') if color.strip()] if row['Team Colors'] else [],
            'common_names': [name.strip() for name in row['Alternative Names'].split(',') if name.strip()] if row['Alternative Names'] else [],
            'logo_url': row['Logo'].strip() if row['Logo'] else None,
            'current_competitions': [],
            'primary_competition_id': None,
            'competition_history': [],
            'created_at': datetime.now(timezone.utc),
            'created_by': 'system',
            'verified_level': 'unverified',
            'verified_at': None,
            'verified_by': None,
            'modification_count': 0,
            'last_modified_at': None,
            'last_modified_by': None,
            'external_ids': {},
            'topkit_reference': generate_topkit_reference('team', i)
        }
        teams.append(team)
        
    return teams

def parse_competition_csv(csv_content: str) -> list:
    """Parse competition CSV and return list of competition documents"""
    competitions = []
    reader = csv.DictReader(csv_content.splitlines())
    
    for i, row in enumerate(reader, 1):
        competition = {
            'id': str(uuid.uuid4()),
            'competition_name': row['Competition Name'].strip(),
            'short_name': row['Competition Name'].strip(),  # Use competition name as short name
            'common_names': [row['Official Name'].strip()] if row['Official Name'] else [],
            'type': row['Competition Type'].strip() if row['Competition Type'] else 'unknown',
            'country': row['Country/Continent'].strip() if row['Country/Continent'] else None,
            'confederations_federations': [row['Federation/Confederation'].strip()] if row['Federation/Confederation'] else [],
            'level': row['Level'].strip() if row['Level'] else 'unknown',
            'current_season': None,
            'logo_url': row['Logo'].strip() if row['Logo'] else None,
            'created_at': datetime.now(timezone.utc),
            'created_by': 'system',
            'verified_level': 'unverified',
            'verified_at': None,
            'verified_by': None,
            'modification_count': 0,
            'last_modified_at': None,
            'last_modified_by': None,
            'topkit_reference': generate_topkit_reference('competition', i)
        }
        competitions.append(competition)
        
    return competitions

def parse_player_csv(csv_content: str) -> list:
    """Parse player CSV and return list of player documents"""
    players = []
    reader = csv.DictReader(csv_content.splitlines())
    
    for i, row in enumerate(reader, 1):
        # Parse birth date
        birth_date = None
        if row['Birth Date']:
            try:
                birth_date = datetime.strptime(row['Birth Date'], '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid birth date for {row['Player Name']}: {row['Birth Date']}")
        
        player = {
            'id': str(uuid.uuid4()),
            'name': row['Player Name'].strip(),
            'full_name': row['Full Name'].strip() if row['Full Name'] else None,
            'common_names': [name.strip() for name in row['Alternative Names'].split(',') if name.strip()] if row['Alternative Names'] else [],
            'birth_date': birth_date,
            'nationality': row['Nationality'].strip() if row['Nationality'] else None,
            'position': row['Position'].strip() if row['Position'] else None,
            'current_team_id': None,
            'team_history': [],
            'profile_picture_url': row['Player Photo'].strip() if row['Player Photo'] else None,
            'player_type': 'none',  # Default player type
            'influence_coefficient': None,
            'created_at': datetime.now(timezone.utc),
            'created_by': 'system',
            'verified_level': 'unverified',
            'verified_at': None,
            'verified_by': None,
            'modification_count': 0,
            'last_modified_at': None,
            'last_modified_by': None,
            'topkit_reference': generate_topkit_reference('player', i)
        }
        players.append(player)
        
    return players

def parse_brand_csv(csv_content: str) -> list:
    """Parse brand CSV and return list of brand documents"""
    brands = []
    reader = csv.DictReader(csv_content.splitlines())
    
    for i, row in enumerate(reader, 1):
        # Parse founded year
        founded_year = None
        if row['Founded Year'] and row['Founded Year'].isdigit():
            founded_year = int(row['Founded Year'])
        
        brand = {
            'id': str(uuid.uuid4()),
            'name': row['Name'].strip(),
            'type': row['Type'].strip().lower() if row['Type'] else 'brand',  # Ensure lowercase
            'country': row['Country of Origin'].strip() if row['Country of Origin'] else None,
            'founded_year': founded_year,
            'website': row['Official Website'].strip() if row['Official Website'] else None,
            'logo_url': row['Brand Logo'].strip() if row['Brand Logo'] else None,
            'created_at': datetime.now(timezone.utc),
            'created_by': 'system',
            'verified_level': 'unverified',
            'verified_at': None,
            'verified_by': None,
            'modification_count': 0,
            'last_modified_at': None,
            'last_modified_by': None,
            'topkit_reference': generate_topkit_reference('brand', i)
        }
        brands.append(brand)
        
    return brands

async def upload_csv_data():
    """Main function to upload all CSV data"""
    try:
        # Connect to database
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        logger.info(f"Connected to database: {db.name}")
        
        # Check existing counts
        existing_teams = await db.teams.count_documents({})
        existing_competitions = await db.competitions.count_documents({})
        existing_players = await db.players.count_documents({})
        existing_brands = await db.brands.count_documents({})
        
        logger.info(f"Existing counts - Teams: {existing_teams}, Competitions: {existing_competitions}, Players: {existing_players}, Brands: {existing_brands}")
        
        async with aiohttp.ClientSession() as session:
            # Download and process each CSV file
            for entity_type, url in CSV_URLS.items():
                logger.info(f"Processing {entity_type} CSV...")
                
                try:
                    # Download CSV content
                    csv_content = await download_csv(session, url)
                    logger.info(f"Downloaded {entity_type} CSV, size: {len(csv_content)} characters")
                    
                    # Parse CSV based on type
                    if entity_type == 'team':
                        documents = parse_team_csv(csv_content)
                        collection = db.teams
                    elif entity_type == 'competition':
                        documents = parse_competition_csv(csv_content)
                        collection = db.competitions
                    elif entity_type == 'player':
                        documents = parse_player_csv(csv_content)
                        collection = db.players
                    elif entity_type == 'brand':
                        documents = parse_brand_csv(csv_content)
                        collection = db.brands
                    else:
                        logger.warning(f"Unknown entity type: {entity_type}")
                        continue
                    
                    if not documents:
                        logger.warning(f"No documents parsed for {entity_type}")
                        continue
                    
                    logger.info(f"Parsed {len(documents)} {entity_type} documents")
                    
                    # Check for duplicates and insert new documents
                    existing_names = set()
                    name_field = 'name' if entity_type in ['team', 'brand'] else ('competition_name' if entity_type == 'competition' else 'name')
                    
                    # Get existing names
                    existing_docs = await collection.find({}, {name_field: 1}).to_list(length=None)
                    existing_names = {doc[name_field] for doc in existing_docs if name_field in doc}
                    
                    # Filter out duplicates
                    new_documents = []
                    for doc in documents:
                        doc_name = doc.get(name_field)
                        if doc_name not in existing_names:
                            new_documents.append(doc)
                        else:
                            logger.info(f"Skipping duplicate {entity_type}: {doc_name}")
                    
                    if new_documents:
                        # Insert new documents
                        result = await collection.insert_many(new_documents)
                        logger.info(f"✅ Inserted {len(result.inserted_ids)} new {entity_type} documents")
                    else:
                        logger.info(f"No new {entity_type} documents to insert (all duplicates)")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing {entity_type}: {str(e)}")
                    continue
        
        # Final counts
        final_teams = await db.teams.count_documents({})
        final_competitions = await db.competitions.count_documents({})
        final_players = await db.players.count_documents({})
        final_brands = await db.brands.count_documents({})
        
        logger.info(f"Final counts - Teams: {final_teams}, Competitions: {final_competitions}, Players: {final_players}, Brands: {final_brands}")
        logger.info("✅ CSV data upload completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in upload process: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(upload_csv_data())