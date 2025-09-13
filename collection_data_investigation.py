#!/usr/bin/env python3
"""
COLLECTION DATA INVESTIGATION - DETAILED ANALYSIS
================================================

This script investigates the exact data structure returned by collection endpoints
to understand why jersey_release and master_jersey are still empty objects.
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"

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

def investigate_owned_collections(token, user_id):
    """Investigate owned collections data structure"""
    print("\n📦 INVESTIGATING OWNED COLLECTIONS...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/owned", headers=headers)
        
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ Found {len(collections)} owned collections")
            
            if collections:
                print("\n🔍 FIRST COLLECTION DETAILED ANALYSIS:")
                first_collection = collections[0]
                print(json.dumps(first_collection, indent=2, default=str))
                
                print("\n📊 COLLECTION STRUCTURE ANALYSIS:")
                print(f"- Collection ID: {first_collection.get('id', 'Missing')}")
                print(f"- Jersey Release ID: {first_collection.get('jersey_release_id', 'Missing')}")
                print(f"- Jersey Release Object: {type(first_collection.get('jersey_release', {}))}")
                print(f"- Jersey Release Keys: {list(first_collection.get('jersey_release', {}).keys())}")
                print(f"- Master Jersey Object: {type(first_collection.get('master_jersey', {}))}")
                print(f"- Master Jersey Keys: {list(first_collection.get('master_jersey', {}).keys())}")
                
                # Check if jersey_release_id exists but jersey_release is empty
                jersey_release_id = first_collection.get('jersey_release_id')
                jersey_release_obj = first_collection.get('jersey_release', {})
                
                if jersey_release_id and not jersey_release_obj:
                    print(f"⚠️  ISSUE IDENTIFIED: jersey_release_id exists ({jersey_release_id}) but jersey_release object is empty")
                elif not jersey_release_id:
                    print(f"⚠️  ISSUE IDENTIFIED: jersey_release_id is missing from collection")
                
            return collections
        else:
            print(f"❌ Failed to get owned collections: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error investigating owned collections: {str(e)}")
        return []

def investigate_wanted_collections(token, user_id):
    """Investigate wanted collections data structure"""
    print("\n🎯 INVESTIGATING WANTED COLLECTIONS...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/wanted", headers=headers)
        
        if response.status_code == 200:
            collections = response.json()
            print(f"✅ Found {len(collections)} wanted collections")
            
            if collections:
                print("\n🔍 FIRST COLLECTION DETAILED ANALYSIS:")
                first_collection = collections[0]
                print(json.dumps(first_collection, indent=2, default=str))
                
            return collections
        else:
            print(f"❌ Failed to get wanted collections: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error investigating wanted collections: {str(e)}")
        return []

def investigate_vestiaire_data():
    """Investigate vestiaire data structure"""
    print("\n🏪 INVESTIGATING VESTIAIRE DATA...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/vestiaire")
        
        if response.status_code == 200:
            vestiaire_data = response.json()
            print(f"✅ Found {len(vestiaire_data)} Jersey Releases in vestiaire")
            
            if vestiaire_data:
                print("\n🔍 FIRST JERSEY RELEASE DETAILED ANALYSIS:")
                first_jersey = vestiaire_data[0]
                print(json.dumps(first_jersey, indent=2, default=str))
                
                print("\n📊 JERSEY RELEASE STRUCTURE ANALYSIS:")
                print(f"- Jersey Release ID: {first_jersey.get('id', 'Missing')}")
                print(f"- Master Jersey ID: {first_jersey.get('master_jersey_id', 'Missing')}")
                print(f"- Master Jersey Info: {type(first_jersey.get('master_jersey_info', {}))}")
                print(f"- Master Jersey Info Keys: {list(first_jersey.get('master_jersey_info', {}).keys())}")
                
                master_jersey_info = first_jersey.get('master_jersey_info', {})
                if master_jersey_info:
                    print(f"- Player Name: {master_jersey_info.get('player_name', 'Missing')}")
                    print(f"- Team Info: {master_jersey_info.get('team_info', 'Missing')}")
                    print(f"- Season: {master_jersey_info.get('season', 'Missing')}")
                
            return vestiaire_data
        else:
            print(f"❌ Failed to get vestiaire data: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error investigating vestiaire data: {str(e)}")
        return []

def compare_data_structures(collections, vestiaire_data):
    """Compare collection and vestiaire data structures"""
    print("\n🔄 COMPARING DATA STRUCTURES...")
    
    if not collections or not vestiaire_data:
        print("❌ Cannot compare - missing data")
        return
    
    collection = collections[0]
    jersey_release = vestiaire_data[0]
    
    collection_jersey_id = collection.get('jersey_release_id')
    vestiaire_jersey_id = jersey_release.get('id')
    
    print(f"Collection Jersey Release ID: {collection_jersey_id}")
    print(f"Vestiaire Jersey Release ID: {vestiaire_jersey_id}")
    
    if collection_jersey_id == vestiaire_jersey_id:
        print("✅ IDs match - aggregation should work")
    else:
        print("⚠️  IDs don't match - checking if collection references existing jersey release")
        
        # Check if collection's jersey_release_id exists in vestiaire
        vestiaire_ids = [jr.get('id') for jr in vestiaire_data]
        if collection_jersey_id in vestiaire_ids:
            print("✅ Collection references valid Jersey Release from vestiaire")
        else:
            print("❌ Collection references Jersey Release not found in vestiaire")
            print(f"Available vestiaire IDs: {vestiaire_ids[:3]}...")

def main():
    print("🔍 COLLECTION DATA INVESTIGATION")
    print("=" * 50)
    
    # Authenticate
    token, user_id = authenticate_user()
    if not token:
        return
    
    # Investigate data structures
    owned_collections = investigate_owned_collections(token, user_id)
    wanted_collections = investigate_wanted_collections(token, user_id)
    vestiaire_data = investigate_vestiaire_data()
    
    # Compare structures
    if owned_collections:
        compare_data_structures(owned_collections, vestiaire_data)
    
    print("\n" + "=" * 50)
    print("🎯 INVESTIGATION COMPLETE")
    
    # Summary
    if owned_collections or wanted_collections:
        has_empty_jersey_release = False
        has_empty_master_jersey = False
        
        for collection in (owned_collections + wanted_collections):
            if not collection.get('jersey_release') or collection.get('jersey_release') == {}:
                has_empty_jersey_release = True
            if not collection.get('master_jersey') or collection.get('master_jersey') == {}:
                has_empty_master_jersey = True
        
        if has_empty_jersey_release or has_empty_master_jersey:
            print("❌ AGGREGATION PIPELINE ISSUE CONFIRMED:")
            print(f"   - Empty jersey_release objects: {has_empty_jersey_release}")
            print(f"   - Empty master_jersey objects: {has_empty_master_jersey}")
            print("   - Collections cannot display proper data in 'Ma Collection'")
        else:
            print("✅ AGGREGATION PIPELINE WORKING:")
            print("   - Jersey Release and Master Jersey data properly populated")
    else:
        print("ℹ️  No collections found to analyze")

if __name__ == "__main__":
    main()