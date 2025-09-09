#!/usr/bin/env python3
"""
Focused test for failing endpoints
"""

import requests
import json

BASE_URL = "https://football-kit-ui.preview.emergentagent.com/api"

def test_failing_endpoints():
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # First register and get token
    print("🔐 Registering user...")
    register_payload = {
        "email": f"focustest_{int(__import__('time').time())}@topkit.com",
        "password": "SecurePass123!",
        "name": "Focus Test User"
    }
    
    register_response = session.post(f"{BASE_URL}/auth/register", json=register_payload)
    if register_response.status_code == 200:
        data = register_response.json()
        auth_token = data["token"]
        session.headers.update({'Authorization': f'Bearer {auth_token}'})
        print(f"✅ User registered with token")
        
        # Create a jersey for testing
        print("⚽ Creating jersey...")
        jersey_payload = {
            "team": "Real Madrid",
            "season": "2023-24",
            "player": "Vinicius Jr",
            "size": "M",
            "condition": "mint",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Official Real Madrid home jersey",
            "images": []
        }
        
        jersey_response = session.post(f"{BASE_URL}/jerseys", json=jersey_payload)
        if jersey_response.status_code == 200:
            jersey_data = jersey_response.json()
            jersey_id = jersey_data["id"]
            print(f"✅ Jersey created: {jersey_id}")
            
            # Create a listing
            print("🏪 Creating listing...")
            listing_payload = {
                "jersey_id": jersey_id,
                "price": 120.00,
                "description": "Mint condition Real Madrid jersey",
                "images": []
            }
            
            listing_response = session.post(f"{BASE_URL}/listings", json=listing_payload)
            if listing_response.status_code == 200:
                listing_data = listing_response.json()
                listing_id = listing_data["id"]
                print(f"✅ Listing created: {listing_id}")
                
                # Test get listings
                print("🔍 Testing get listings...")
                listings_response = session.get(f"{BASE_URL}/listings")
                print(f"Get listings status: {listings_response.status_code}")
                if listings_response.status_code != 200:
                    print(f"Error: {listings_response.text}")
                else:
                    listings = listings_response.json()
                    print(f"✅ Retrieved {len(listings)} listings")
                
                # Test get specific listing
                print("🔍 Testing get specific listing...")
                specific_listing_response = session.get(f"{BASE_URL}/listings/{listing_id}")
                print(f"Get specific listing status: {specific_listing_response.status_code}")
                if specific_listing_response.status_code != 200:
                    print(f"Error: {specific_listing_response.text}")
                else:
                    listing = specific_listing_response.json()
                    print(f"✅ Retrieved listing with jersey and seller")
                
                # Add to collection
                print("📚 Adding to collection...")
                collection_payload = {
                    "jersey_id": jersey_id,
                    "collection_type": "owned"
                }
                
                collection_response = session.post(f"{BASE_URL}/collections", json=collection_payload)
                if collection_response.status_code == 200:
                    print("✅ Added to collection")
                    
                    # Test get collections
                    print("🔍 Testing get collections...")
                    collections_response = session.get(f"{BASE_URL}/collections/owned")
                    print(f"Get collections status: {collections_response.status_code}")
                    if collections_response.status_code != 200:
                        print(f"Error: {collections_response.text}")
                    else:
                        collections = collections_response.json()
                        print(f"✅ Retrieved {len(collections)} collections")
                else:
                    print(f"❌ Failed to add to collection: {collection_response.status_code}")
            else:
                print(f"❌ Failed to create listing: {listing_response.status_code}")
        else:
            print(f"❌ Failed to create jersey: {jersey_response.status_code}")
    else:
        print(f"❌ Failed to register: {register_response.status_code}")
    
    # Test JWT validation without token
    print("🔐 Testing JWT validation without token...")
    no_auth_session = requests.Session()
    no_auth_session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    profile_response = no_auth_session.get(f"{BASE_URL}/profile")
    print(f"Profile without token status: {profile_response.status_code}")
    if profile_response.status_code in [401, 403]:
        print("✅ Correctly rejected request without token")
    else:
        print(f"❌ Should have rejected request without token, got {profile_response.status_code}")

if __name__ == "__main__":
    test_failing_endpoints()