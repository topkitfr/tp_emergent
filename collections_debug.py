#!/usr/bin/env python3
"""
COLLECTIONS DEBUG - DIRECT ENDPOINT TESTING
===========================================

This script tests the collection endpoints directly to understand the data structure.
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

def authenticate_user():
    """Authenticate user and get token"""
    print("🔐 Authenticating user...")
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            user_data = data.get("user", {})
            user_id = user_data.get("id")
            
            print(f"✅ Authenticated: {user_data.get('name')} (ID: {user_id})")
            return token, user_id
        else:
            print(f"❌ Authentication failed: HTTP {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def test_general_collections_endpoint(token, user_id):
    """Test the general collections endpoint"""
    print(f"\n📦 TESTING GENERAL COLLECTIONS ENDPOINT...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                collections = response.json()
                print(f"✅ Found {len(collections)} collections")
                print(f"Response type: {type(collections)}")
                
                if collections and len(collections) > 0:
                    print(f"First collection type: {type(collections[0])}")
                    print(f"First collection: {collections[0]}")
                    
                    # Extract jersey_release_ids
                    jersey_ids = []
                    for i, collection in enumerate(collections):
                        if isinstance(collection, dict):
                            jersey_id = collection.get('jersey_release_id')
                            if jersey_id:
                                jersey_ids.append(jersey_id)
                                print(f"Collection {i}: jersey_release_id = {jersey_id}")
                        else:
                            print(f"Collection {i}: unexpected type {type(collection)}")
                    
                    return collections, jersey_ids
                else:
                    print("Empty collections array")
                    return [], []
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {response.text[:500]}")
                return [], []
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return [], []
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return [], []

def test_owned_collections_raw(token, user_id):
    """Test owned collections endpoint and show raw response"""
    print(f"\n📦 TESTING OWNED COLLECTIONS (Raw Response)...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/owned", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ Found {len(collections)} owned collections")
            
            if collections:
                print(f"\n🔍 FIRST COLLECTION ANALYSIS:")
                first = collections[0]
                print(f"Type: {type(first)}")
                print(f"Keys: {list(first.keys()) if isinstance(first, dict) else 'Not a dict'}")
                
                # Check specific fields
                jersey_release_id = first.get('jersey_release_id')
                jersey_release = first.get('jersey_release')
                master_jersey = first.get('master_jersey')
                
                print(f"jersey_release_id: {jersey_release_id}")
                print(f"jersey_release type: {type(jersey_release)}")
                print(f"jersey_release content: {jersey_release}")
                print(f"master_jersey type: {type(master_jersey)}")
                print(f"master_jersey content: {master_jersey}")
                
                # Check if jersey_release is None vs empty dict
                if jersey_release is None:
                    print("⚠️  jersey_release is None (aggregation lookup failed)")
                elif jersey_release == {}:
                    print("⚠️  jersey_release is empty dict (no data found)")
                elif jersey_release:
                    print("✅ jersey_release has data")
                
                return collections
            else:
                print("No owned collections found")
                return []
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def test_add_valid_jersey_release(token, user_id):
    """Test adding a valid Jersey Release from vestiaire"""
    print(f"\n➕ TESTING ADD VALID JERSEY RELEASE...")
    
    try:
        # First get available Jersey Releases
        vestiaire_response = requests.get(f"{BACKEND_URL}/vestiaire")
        if vestiaire_response.status_code != 200:
            print("❌ Cannot get vestiaire data")
            return False
        
        jersey_releases = vestiaire_response.json()
        if not jersey_releases:
            print("❌ No Jersey Releases available")
            return False
        
        # Use first Jersey Release
        jersey_release = jersey_releases[0]
        jersey_id = jersey_release.get('id')
        player_name = jersey_release.get('player_name', 'Unknown')
        
        print(f"Testing with Jersey Release: {player_name} (ID: {jersey_id})")
        
        # Try to add to collection
        headers = {"Authorization": f"Bearer {token}"}
        collection_data = {
            "jersey_release_id": jersey_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "mint"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/users/{user_id}/collections", 
            headers=headers,
            json=collection_data
        )
        
        print(f"Add to collection response: HTTP {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Successfully added to collection: {result}")
            return True
        elif response.status_code == 400 and "already in collection" in response.text.lower():
            print("ℹ️  Already in collection (expected)")
            return True
        else:
            print(f"❌ Failed to add: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("🔍 COLLECTIONS DEBUG - DIRECT ENDPOINT TESTING")
    print("=" * 60)
    
    # Authenticate
    token, user_id = authenticate_user()
    if not token:
        return
    
    # Test general collections endpoint
    collections, jersey_ids = test_general_collections_endpoint(token, user_id)
    
    # Test owned collections with raw response analysis
    owned_collections = test_owned_collections_raw(token, user_id)
    
    # Test adding a valid Jersey Release
    add_success = test_add_valid_jersey_release(token, user_id)
    
    # If we added successfully, test owned collections again
    if add_success:
        print(f"\n🔄 RETESTING OWNED COLLECTIONS AFTER ADD...")
        owned_collections_after = test_owned_collections_raw(token, user_id)
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG COMPLETE")

if __name__ == "__main__":
    main()