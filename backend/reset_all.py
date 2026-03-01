import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

async def reset():
    collections = ['master_kits', 'versions', 'teams', 'leagues', 
                   'brands', 'players', 'reviews', 'collections', 
                   'submissions', 'wishlists']
    for col in collections:
        result = await db[col].delete_many({})
        print(f"🗑️  {col} : {result.deleted_count} docs supprimés")
    print("\n✅ Base complètement vidée !")
    client.close()

asyncio.run(reset())
