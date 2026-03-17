import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def run():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.topkit
    result = await db.users.update_one(
        {'email': 'dev@topkit.fr'},
        {'$set': {'role': 'moderator'}}
    )
    print('Modified:', result.modified_count)
    client.close()

asyncio.run(run())
