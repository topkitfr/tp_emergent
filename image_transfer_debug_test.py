#!/usr/bin/env python3
"""
Debug test to understand the image transfer issue
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

async def debug_image_transfer():
    """Debug the image transfer issue"""
    
    async with aiohttp.ClientSession() as session:
        # Authenticate
        login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
            if response.status != 200:
                print("❌ Authentication failed")
                return
            
            data = await response.json()
            token = data.get("token")
            headers = {"Authorization": f"Bearer {token}"}
        
        # Get the contribution we just created
        contribution_id = "b932eebf-1e7e-421c-8754-527385b0063c"
        
        async with session.get(f"{API_BASE}/contributions-v2/{contribution_id}", headers=headers) as response:
            if response.status == 200:
                contribution = await response.json()
                print("📋 Contribution Details:")
                print(f"  ID: {contribution.get('id')}")
                print(f"  Entity Type: {contribution.get('entity_type')}")
                print(f"  Entity ID: {contribution.get('entity_id')}")
                print(f"  Images Count: {contribution.get('images_count')}")
                print(f"  Status: {contribution.get('status')}")
                print(f"  Data: {json.dumps(contribution.get('data', {}), indent=2)}")
                
                # Check if the team was updated
                team_id = contribution.get('entity_id')
                if team_id:
                    async with session.get(f"{API_BASE}/teams") as team_response:
                        if team_response.status == 200:
                            teams = await team_response.json()
                            for team in teams:
                                if team.get('id') == team_id:
                                    print(f"\n🏆 Team Details (ID: {team_id}):")
                                    print(f"  Name: {team.get('name')}")
                                    print(f"  Logo URL: {team.get('logo_url')}")
                                    
                                    # Test if the logo is accessible
                                    logo_url = team.get('logo_url')
                                    if logo_url:
                                        async with session.get(f"{API_BASE}/legacy-image/{logo_url}") as img_response:
                                            print(f"  Logo Accessible: {img_response.status == 200}")
                                            if img_response.status != 200:
                                                print(f"    Error: {img_response.status}")
                                    break
            else:
                print(f"❌ Failed to get contribution: {response.status}")

if __name__ == "__main__":
    asyncio.run(debug_image_transfer())