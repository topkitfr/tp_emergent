#!/usr/bin/env python3
"""
Investigate Team and Brand Logo URL Issues
==========================================

The test shows that team and brand logos are failing to load.
Let's investigate the actual logo_url values in the database.
"""

import asyncio
import aiohttp
import json
import os

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-levels.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

async def investigate_logos():
    """Investigate team and brand logo URLs"""
    
    async with aiohttp.ClientSession() as session:
        # Authenticate
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
            if response.status != 200:
                print("❌ Authentication failed")
                return
            data = await response.json()
            auth_token = data.get("token")
            headers = {"Authorization": f"Bearer {auth_token}"}
            
        print("✅ Authenticated successfully")
        
        # Get teams with logos
        print("\n🔍 INVESTIGATING TEAM LOGOS")
        print("=" * 40)
        async with session.get(f"{API_BASE}/teams", headers=headers) as response:
            if response.status == 200:
                teams = await response.json()
                for team in teams:
                    if team.get("logo_url"):
                        print(f"Team: {team.get('name', 'Unknown')}")
                        print(f"  Logo URL: {team['logo_url']}")
                        print(f"  Full URL patterns to test:")
                        print(f"    - {BACKEND_URL}/api/{team['logo_url']}")
                        print(f"    - {BACKEND_URL}/api/uploads/{team['logo_url']}")
                        print(f"    - {BACKEND_URL}/{team['logo_url']}")
                        print()
                        
        # Get brands with logos  
        print("\n🔍 INVESTIGATING BRAND LOGOS")
        print("=" * 40)
        async with session.get(f"{API_BASE}/brands", headers=headers) as response:
            if response.status == 200:
                brands = await response.json()
                for brand in brands:
                    if brand.get("logo_url"):
                        print(f"Brand: {brand.get('name', 'Unknown')}")
                        print(f"  Logo URL: {brand['logo_url']}")
                        print(f"  Full URL patterns to test:")
                        print(f"    - {BACKEND_URL}/api/{brand['logo_url']}")
                        print(f"    - {BACKEND_URL}/api/uploads/{brand['logo_url']}")
                        print(f"    - {BACKEND_URL}/{brand['logo_url']}")
                        print()

if __name__ == "__main__":
    asyncio.run(investigate_logos())