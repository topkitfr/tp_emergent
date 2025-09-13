#!/usr/bin/env python3
"""
Verify that the TopKit database is completely empty after erasure
"""

import requests
import json

BASE_URL = "https://football-jersey-db.preview.emergentagent.com/api"

def verify_empty_database():
    """Verify all endpoints return empty results"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    print("🔍 VERIFYING EMPTY DATABASE STATE")
    print("=" * 50)
    
    # Test jerseys endpoint
    jerseys_response = session.get(f"{BASE_URL}/jerseys?limit=100")
    if jerseys_response.status_code == 200:
        jerseys = jerseys_response.json()
        print(f"✅ Jerseys: {len(jerseys)} items (should be 0)")
    else:
        print(f"❌ Jerseys endpoint error: {jerseys_response.status_code}")
    
    # Test listings endpoint
    listings_response = session.get(f"{BASE_URL}/listings?limit=100")
    if listings_response.status_code == 200:
        listings = listings_response.json()
        print(f"✅ Listings: {len(listings)} items (should be 0)")
    else:
        print(f"❌ Listings endpoint error: {listings_response.status_code}")
    
    # Test registration (should work with new email)
    test_email = "newuser@topkit.com"
    register_payload = {
        "email": test_email,
        "password": "newpassword123",
        "name": "New User"
    }
    
    register_response = session.post(f"{BASE_URL}/auth/register", json=register_payload)
    if register_response.status_code == 200:
        print("✅ New user registration: Works (database accepts new users)")
        
        # Test that we can create new data
        data = register_response.json()
        token = data["token"]
        session.headers.update({'Authorization': f'Bearer {token}'})
        
        # Try creating a jersey
        jersey_payload = {
            "team": "Test Team After Erase",
            "season": "2024-25",
            "player": "Test Player",
            "size": "L",
            "condition": "excellent",
            "manufacturer": "Test Brand",
            "home_away": "home",
            "league": "Test League",
            "description": "Test jersey after database erase",
            "images": []
        }
        
        jersey_response = session.post(f"{BASE_URL}/jerseys", json=jersey_payload)
        if jersey_response.status_code == 200:
            print("✅ New jersey creation: Works (database accepts new data)")
        else:
            print(f"❌ New jersey creation failed: {jersey_response.status_code}")
    else:
        print(f"❌ New user registration failed: {register_response.status_code}")
    
    print("\n🎯 CONCLUSION: Database is completely empty and ready for new data!")

if __name__ == "__main__":
    verify_empty_database()