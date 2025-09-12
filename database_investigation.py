#!/usr/bin/env python3
"""
DATABASE INVESTIGATION - JERSEY RELEASES AND COLLECTIONS
========================================================

This script investigates the database to understand the mismatch between
collection jersey_release_id references and actual Jersey Releases.
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"

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

def get_all_jersey_releases():
    """Get all Jersey Releases from vestiaire endpoint"""
    print("\n🏪 GETTING ALL JERSEY RELEASES...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vestiaire")
        
        if response.status_code == 200:
            jersey_releases = response.json()
            print(f"✅ Found {len(jersey_releases)} Jersey Releases")
            
            jersey_ids = [jr.get('id') for jr in jersey_releases]
            print(f"Jersey Release IDs: {jersey_ids}")
            
            return jersey_releases, jersey_ids
        else:
            print(f"❌ Failed to get Jersey Releases: HTTP {response.status_code}")
            return [], []
            
    except Exception as e:
        print(f"❌ Error getting Jersey Releases: {str(e)}")
        return [], []

def get_user_collections(token, user_id):
    """Get user's collections (raw data without aggregation)"""
    print(f"\n📦 GETTING USER COLLECTIONS (Raw Data)...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get collections using a different endpoint or direct database query
        # Let's check if there's a general collections endpoint
        response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections", headers=headers)
        
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ Found {len(collections)} total collections")
            
            collection_jersey_ids = []
            for collection in collections:
                jersey_id = collection.get('jersey_release_id')
                if jersey_id:
                    collection_jersey_ids.append(jersey_id)
            
            print(f"Collection Jersey Release IDs: {collection_jersey_ids}")
            return collections, collection_jersey_ids
        else:
            print(f"❌ Failed to get collections: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return [], []
            
    except Exception as e:
        print(f"❌ Error getting collections: {str(e)}")
        return [], []

def analyze_id_mismatch(collection_ids, jersey_ids):
    """Analyze the mismatch between collection and jersey release IDs"""
    print(f"\n🔍 ANALYZING ID MISMATCH...")
    
    print(f"Collection Jersey Release IDs: {len(collection_ids)} unique IDs")
    print(f"Available Jersey Release IDs: {len(jersey_ids)} unique IDs")
    
    # Find orphaned collections (referencing non-existent Jersey Releases)
    orphaned_ids = [cid for cid in collection_ids if cid not in jersey_ids]
    valid_ids = [cid for cid in collection_ids if cid in jersey_ids]
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"✅ Valid references: {len(valid_ids)} collections")
    print(f"❌ Orphaned references: {len(orphaned_ids)} collections")
    
    if orphaned_ids:
        print(f"\n⚠️  ORPHANED JERSEY RELEASE IDs:")
        for orphaned_id in orphaned_ids:
            print(f"   - {orphaned_id}")
        
        print(f"\n💡 SOLUTION NEEDED:")
        print(f"   - Clean up orphaned collection references")
        print(f"   - OR restore missing Jersey Releases")
        print(f"   - OR update collection references to valid Jersey Release IDs")
    
    if valid_ids:
        print(f"\n✅ VALID JERSEY RELEASE IDs:")
        for valid_id in valid_ids:
            print(f"   - {valid_id}")

def test_aggregation_with_valid_id(token, user_id, valid_jersey_ids):
    """Test if aggregation works with a valid Jersey Release ID"""
    print(f"\n🧪 TESTING AGGREGATION WITH VALID ID...")
    
    if not valid_jersey_ids:
        print("❌ No valid Jersey Release IDs to test with")
        return
    
    # Try to add a valid Jersey Release to collection and test aggregation
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Use first valid Jersey Release ID
        test_jersey_id = valid_jersey_ids[0]
        print(f"Testing with Jersey Release ID: {test_jersey_id}")
        
        # Try to add to collection (might fail if already exists)
        collection_data = {
            "jersey_release_id": test_jersey_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "mint"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/users/{user_id}/collections", 
            headers=headers,
            json=collection_data
        )
        
        if response.status_code == 201:
            print("✅ Successfully added Jersey Release to collection")
        elif response.status_code == 400 and "already in collection" in response.text.lower():
            print("ℹ️  Jersey Release already in collection (expected)")
        else:
            print(f"⚠️  Add to collection response: HTTP {response.status_code}")
        
        # Now test the aggregation
        owned_response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/owned", headers=headers)
        
        if owned_response.status_code == 200:
            owned_collections = owned_response.json()
            
            # Find collection with our test Jersey Release ID
            test_collection = None
            for collection in owned_collections:
                if collection.get('jersey_release_id') == test_jersey_id:
                    test_collection = collection
                    break
            
            if test_collection:
                jersey_release = test_collection.get('jersey_release', {})
                master_jersey = test_collection.get('master_jersey', {})
                
                jersey_populated = bool(jersey_release and jersey_release != {})
                master_populated = bool(master_jersey and master_jersey != {})
                
                print(f"🔍 AGGREGATION TEST RESULTS:")
                print(f"   - Jersey Release populated: {jersey_populated}")
                print(f"   - Master Jersey populated: {master_populated}")
                
                if jersey_populated and master_populated:
                    print("✅ AGGREGATION WORKING for valid Jersey Release IDs!")
                    print(f"   - Player: {jersey_release.get('player_name', 'Unknown')}")
                    print(f"   - Season: {master_jersey.get('season', 'Unknown')}")
                else:
                    print("❌ AGGREGATION STILL NOT WORKING even with valid IDs")
            else:
                print("⚠️  Test collection not found in owned collections")
        else:
            print(f"❌ Failed to get owned collections: HTTP {owned_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing aggregation: {str(e)}")

def main():
    print("🔍 DATABASE INVESTIGATION - JERSEY RELEASES AND COLLECTIONS")
    print("=" * 70)
    
    # Authenticate
    token, user_id = authenticate_user()
    if not token:
        return
    
    # Get all Jersey Releases
    jersey_releases, jersey_ids = get_all_jersey_releases()
    
    # Get user collections
    collections, collection_ids = get_user_collections(token, user_id)
    
    # Analyze mismatch
    if collection_ids and jersey_ids:
        analyze_id_mismatch(collection_ids, jersey_ids)
        
        # Test aggregation with valid ID
        valid_ids = [cid for cid in collection_ids if cid in jersey_ids]
        if valid_ids:
            test_aggregation_with_valid_id(token, user_id, jersey_ids)
    
    print("\n" + "=" * 70)
    print("🎯 INVESTIGATION COMPLETE")
    
    # Summary and recommendations
    orphaned_count = len([cid for cid in collection_ids if cid not in jersey_ids]) if collection_ids and jersey_ids else 0
    
    if orphaned_count > 0:
        print(f"❌ CRITICAL ISSUE: {orphaned_count} collections reference non-existent Jersey Releases")
        print("🔧 RECOMMENDED ACTIONS:")
        print("   1. Clean up orphaned collection references")
        print("   2. Update aggregation pipeline to handle missing references gracefully")
        print("   3. Add data validation to prevent orphaned references")
    else:
        print("✅ All collection references are valid")

if __name__ == "__main__":
    main()