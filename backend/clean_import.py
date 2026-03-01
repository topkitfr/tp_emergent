# clean_import.py
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

async def clean():
    result = await db['kits'].delete_many({})
    print(f"Supprime {result.deleted_count} docs de kits")
    client.close()

asyncio.run(clean())
