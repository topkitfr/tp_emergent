#!/usr/bin/env python
"""
Fix the team name that was corrupted by the previous bug
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def fix_team_name():
    """Fix the team name that was incorrectly changed"""
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.topkit_db
    
    print("🔧 Fixing Team Name Bug")
    print("=" * 30)
    
    # Find the team that had issues
    team = await db.teams.find_one({'topkit_reference': 'TK-TEAM-616469'})
    if team:
        print(f"✅ Found team: {team['topkit_reference']}")
        print(f"   Current name: '{team['name']}'")
        print(f"   Should be: 'paris saint-germain'")
        
        # Update the team name back to original
        result = await db.teams.update_one(
            {'id': team['id']},
            {
                '$set': {
                    'name': 'paris saint-germain',
                    'last_modified_at': datetime.utcnow(),
                    'last_modified_by': 'system-fix'
                },
                '$inc': {'modification_count': 1}
            }
        )
        
        if result.modified_count > 0:
            print("✅ Successfully restored team name to 'paris saint-germain'")
            
            # Verify the fix
            fixed_team = await db.teams.find_one({'id': team['id']})
            print(f"   Verified name: '{fixed_team['name']}'")
        else:
            print("❌ Failed to update team name")
    else:
        print("❌ Team TK-TEAM-616469 not found")
    
    client.close()
    print("\n🎯 Team name fix completed!")

if __name__ == "__main__":
    asyncio.run(fix_team_name())