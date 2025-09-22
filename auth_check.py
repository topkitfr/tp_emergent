#!/usr/bin/env python3
"""
Quick authentication check to find working credentials
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://xp-tracking.preview.emergentagent.com/api"

async def test_credentials():
    async with aiohttp.ClientSession() as session:
        
        # Test admin credentials
        admin_passwords = ["adminpass123", "TopKitSecure789#"]
        print("Testing admin credentials...")
        
        for password in admin_passwords:
            try:
                creds = {"email": "topkitfr@gmail.com", "password": password}
                async with session.post(f"{BACKEND_URL}/auth/login", json=creds) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Admin login SUCCESS: topkitfr@gmail.com / {password}")
                        print(f"   User: {data.get('user', {}).get('name')}, Role: {data.get('user', {}).get('role')}")
                        break
                    else:
                        print(f"❌ Admin login FAILED: topkitfr@gmail.com / {password} - Status: {response.status}")
            except Exception as e:
                print(f"❌ Admin login ERROR: {password} - {str(e)}")
        
        # Test user credentials
        user_passwords = ["123", "TopKit123!", "T0p_Mdp_1288*"]
        print("\nTesting user credentials...")
        
        for password in user_passwords:
            try:
                creds = {"email": "steinmetzlivio@gmail.com", "password": password}
                async with session.post(f"{BACKEND_URL}/auth/login", json=creds) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ User login SUCCESS: steinmetzlivio@gmail.com / {password}")
                        print(f"   User: {data.get('user', {}).get('name')}, Role: {data.get('user', {}).get('role')}")
                        break
                    else:
                        print(f"❌ User login FAILED: steinmetzlivio@gmail.com / {password} - Status: {response.status}")
            except Exception as e:
                print(f"❌ User login ERROR: {password} - {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_credentials())