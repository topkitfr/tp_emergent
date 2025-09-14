#!/usr/bin/env python3
"""
Focused Jersey Valuation System Testing
"""

import requests
import json
import time

BASE_URL = "https://jersey-collab-1.preview.emergentagent.com/api"

def test_valuation_system():
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Register user
    unique_email = f"valtest_{int(time.time())}@topkit.com"
    register_payload = {
        "email": unique_email,
        "password": "TestPass123!",
        "name": "Valuation Tester"
    }
    
    register_response = session.post(f"{BASE_URL}/auth/register", json=register_payload)
    if register_response.status_code != 200:
        print("❌ Registration failed")
        return
    
    auth_data = register_response.json()
    token = auth_data["token"]
    session.headers.update({'Authorization': f'Bearer {token}'})
    
    print("✅ User registered and authenticated")
    
    # Create test jersey
    jersey_payload = {
        "team": "Manchester United",
        "season": "2023-24",
        "player": "Bruno Fernandes",
        "size": "L",
        "condition": "excellent",
        "manufacturer": "Adidas",
        "home_away": "home",
        "league": "Premier League",
        "description": "Test jersey for valuation",
        "images": []
    }
    
    jersey_response = session.post(f"{BASE_URL}/jerseys", json=jersey_payload)
    if jersey_response.status_code != 200:
        print("❌ Jersey creation failed")
        return
    
    jersey_id = jersey_response.json()["id"]
    print(f"✅ Jersey created: {jersey_id}")
    
    # Create listing to generate valuation data
    listing_payload = {
        "jersey_id": jersey_id,
        "price": 95.00,
        "description": "Test listing for valuation",
        "images": []
    }
    
    listing_response = session.post(f"{BASE_URL}/listings", json=listing_payload)
    if listing_response.status_code != 200:
        print("❌ Listing creation failed")
        return
    
    print("✅ Listing created")
    
    # Wait for valuation calculation
    time.sleep(2)
    
    # Test jersey valuation endpoint
    valuation_response = session.get(f"{BASE_URL}/jerseys/{jersey_id}/valuation")
    print(f"Jersey valuation status: {valuation_response.status_code}")
    if valuation_response.status_code == 200:
        valuation_data = valuation_response.json()
        print(f"✅ Jersey valuation: {json.dumps(valuation_data, indent=2)}")
    else:
        print(f"❌ Jersey valuation failed: {valuation_response.text}")
    
    # Add to collection
    collection_payload = {
        "jersey_id": jersey_id,
        "collection_type": "owned"
    }
    
    collection_response = session.post(f"{BASE_URL}/collections", json=collection_payload)
    if collection_response.status_code == 200:
        print("✅ Added to collection")
    else:
        print(f"❌ Collection add failed: {collection_response.text}")
    
    # Test collection valuations endpoint
    collection_val_response = session.get(f"{BASE_URL}/collections/valuations")
    print(f"Collection valuations status: {collection_val_response.status_code}")
    if collection_val_response.status_code == 200:
        collection_data = collection_val_response.json()
        print(f"✅ Collection valuations: {json.dumps(collection_data, indent=2)}")
    else:
        print(f"❌ Collection valuations failed: {collection_val_response.text}")
    
    # Test profile with valuations
    profile_response = session.get(f"{BASE_URL}/profile")
    print(f"Profile status: {profile_response.status_code}")
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print(f"✅ Profile with valuations: {json.dumps(profile_data, indent=2)}")
    else:
        print(f"❌ Profile failed: {profile_response.text}")
    
    # Test market trending
    trending_response = session.get(f"{BASE_URL}/market/trending")
    print(f"Market trending status: {trending_response.status_code}")
    if trending_response.status_code == 200:
        trending_data = trending_response.json()
        print(f"✅ Market trending: {len(trending_data.get('trending_jerseys', []))} trending jerseys")
    else:
        print(f"❌ Market trending failed: {trending_response.text}")

if __name__ == "__main__":
    test_valuation_system()