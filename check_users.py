#!/usr/bin/env python3
"""
Check what users exist in the database
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"

async def check_users():
    async with aiohttp.ClientSession() as session:
        
        # First authenticate with working user credentials
        user_creds = {"email": "steinmetzlivio@gmail.com", "password": "T0p_Mdp_1288*"}
        user_token = None
        
        try:
            async with session.post(f"{BACKEND_URL}/auth/login", json=user_creds) as response:
                if response.status == 200:
                    data = await response.json()
                    user_token = data.get("token")
                    print(f"✅ User authenticated: {data.get('user', {}).get('name')}")
                else:
                    print(f"❌ User authentication failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ User authentication error: {str(e)}")
            return
        
        # Try to register a new admin account for testing
        print("\nTrying to create a test admin account...")
        admin_reg_data = {
            "email": "testadmin@topkit.com",
            "password": "StrongP@ssw0rd2024!",
            "name": "Test Admin"
        }
        
        try:
            async with session.post(f"{BACKEND_URL}/auth/register", json=admin_reg_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Test admin account created: {data.get('user', {}).get('email')}")
                    
                    # Try to login with new admin account
                    admin_creds = {"email": "testadmin@topkit.com", "password": "StrongP@ssw0rd2024!"}
                    async with session.post(f"{BACKEND_URL}/auth/login", json=admin_creds) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ Test admin login successful: {data.get('user', {}).get('name')}, Role: {data.get('user', {}).get('role')}")
                            return data.get("token")
                        else:
                            print(f"❌ Test admin login failed: {response.status}")
                else:
                    error_text = await response.text()
                    print(f"❌ Test admin registration failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Test admin registration error: {str(e)}")
        
        return None

if __name__ == "__main__":
    asyncio.run(check_users())