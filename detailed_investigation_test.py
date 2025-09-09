#!/usr/bin/env python3
"""
DETAILED INVESTIGATION - MA COLLECTION ENDPOINT ISSUE
====================================================

Deep dive investigation to understand the exact state of:
1. What Jersey Releases exist in vestiaire
2. What collections the user actually has
3. What the general collections endpoint is returning
4. Why TK-RELEASE-000001 is not found
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class DetailedInvestigator:
    def __init__(self):
        self.user_token = None
        self.user_user_id = None
        
    def authenticate_user(self):
        """Authenticate user and get token"""
        print("🔐 AUTHENTICATING USER...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_data = data.get('user', {})
                self.user_user_id = user_data.get('id')
                
                print(f"✅ Authentication successful")
                print(f"   User: {user_data.get('name')}")
                print(f"   ID: {self.user_user_id}")
                print(f"   Email: {user_data.get('email')}")
                return True
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False

    def investigate_vestiaire(self):
        """Detailed investigation of vestiaire endpoint"""
        print("\n🏪 INVESTIGATING VESTIAIRE ENDPOINT...")
        print("-" * 50)
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                jersey_releases = response.json()
                print(f"Response Type: {type(jersey_releases)}")
                print(f"Number of Jersey Releases: {len(jersey_releases) if isinstance(jersey_releases, list) else 'Not a list'}")
                
                if isinstance(jersey_releases, list):
                    for i, release in enumerate(jersey_releases):
                        print(f"\nJersey Release {i+1}:")
                        print(f"  ID: {release.get('id')}")
                        print(f"  Reference: {release.get('reference')}")
                        print(f"  Player Name: {release.get('player_name')}")
                        print(f"  Price: {release.get('price')}")
                        print(f"  Master Jersey ID: {release.get('master_jersey_id')}")
                        
                        # Check if this is TK-RELEASE-000001
                        if release.get('reference') == 'TK-RELEASE-000001':
                            print(f"  🎯 FOUND TK-RELEASE-000001!")
                else:
                    print(f"Unexpected response format: {jersey_releases}")
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")

    def investigate_general_collections(self):
        """Detailed investigation of general collections endpoint"""
        print("\n📋 INVESTIGATING GENERAL COLLECTIONS ENDPOINT...")
        print("-" * 50)
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections", headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print(f"URL: {BACKEND_URL}/users/{self.user_user_id}/collections")
            
            if response.status_code == 200:
                collections = response.json()
                print(f"Response Type: {type(collections)}")
                
                if isinstance(collections, list):
                    print(f"Number of Collections: {len(collections)}")
                    
                    for i, collection in enumerate(collections):
                        print(f"\nCollection {i+1}:")
                        print(f"  ID: {collection.get('id')}")
                        print(f"  Type: {collection.get('collection_type')}")
                        print(f"  Jersey Release ID: {collection.get('jersey_release_id')}")
                        print(f"  Added At: {collection.get('added_at')}")
                        
                        # Check jersey_release data
                        jersey_release = collection.get('jersey_release', {})
                        print(f"  Jersey Release Data: {len(jersey_release)} fields")
                        if jersey_release:
                            print(f"    Reference: {jersey_release.get('reference')}")
                            print(f"    Player Name: {jersey_release.get('player_name')}")
                        
                        # Check master_jersey data
                        master_jersey = collection.get('master_jersey', {})
                        print(f"  Master Jersey Data: {len(master_jersey)} fields")
                        if master_jersey:
                            print(f"    Season: {master_jersey.get('season')}")
                            print(f"    Jersey Type: {master_jersey.get('jersey_type')}")
                else:
                    print(f"Response is not a list: {collections}")
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")

    def investigate_specific_collections(self):
        """Detailed investigation of specific collections endpoints"""
        print("\n📊 INVESTIGATING SPECIFIC COLLECTIONS ENDPOINTS...")
        print("-" * 50)
        
        for collection_type in ['owned', 'wanted']:
            print(f"\n{collection_type.upper()} COLLECTIONS:")
            
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/{collection_type}", headers=headers)
                
                print(f"  Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    collections = response.json()
                    print(f"  Number of Collections: {len(collections) if isinstance(collections, list) else 'Not a list'}")
                    
                    if isinstance(collections, list):
                        for i, collection in enumerate(collections):
                            print(f"\n  Collection {i+1}:")
                            print(f"    ID: {collection.get('id')}")
                            print(f"    Jersey Release ID: {collection.get('jersey_release_id')}")
                            
                            # Check jersey_release data
                            jersey_release = collection.get('jersey_release', {})
                            if jersey_release:
                                print(f"    Jersey Release Reference: {jersey_release.get('reference')}")
                                print(f"    Jersey Release Player: {jersey_release.get('player_name')}")
                            else:
                                print(f"    Jersey Release Data: Empty or missing")
                else:
                    print(f"  Error response: {response.text}")
                    
            except Exception as e:
                print(f"  Exception: {str(e)}")

    def check_jersey_releases_directly(self):
        """Check jersey releases directly from the database endpoint"""
        print("\n🔍 CHECKING JERSEY RELEASES DIRECTLY...")
        print("-" * 50)
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Try to get all jersey releases
            response = requests.get(f"{BACKEND_URL}/jersey-releases", headers=headers)
            
            print(f"Jersey Releases Endpoint Status: {response.status_code}")
            
            if response.status_code == 200:
                releases = response.json()
                print(f"Total Jersey Releases: {len(releases) if isinstance(releases, list) else 'Not a list'}")
                
                if isinstance(releases, list):
                    tk_release = None
                    for release in releases:
                        if release.get('reference') == 'TK-RELEASE-000001':
                            tk_release = release
                            break
                    
                    if tk_release:
                        print(f"\n🎯 FOUND TK-RELEASE-000001 IN JERSEY RELEASES:")
                        print(f"  ID: {tk_release.get('id')}")
                        print(f"  Reference: {tk_release.get('reference')}")
                        print(f"  Player Name: {tk_release.get('player_name')}")
                        print(f"  Master Jersey ID: {tk_release.get('master_jersey_id')}")
                        print(f"  Price: {tk_release.get('price')}")
                        return tk_release.get('id')
                    else:
                        print("❌ TK-RELEASE-000001 NOT FOUND in jersey releases")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")
        
        return None

    def run_investigation(self):
        """Run comprehensive investigation"""
        print("🔍 STARTING DETAILED INVESTIGATION")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot proceed")
            return False
        
        # Step 2: Investigate vestiaire
        self.investigate_vestiaire()
        
        # Step 3: Check jersey releases directly
        tk_release_id = self.check_jersey_releases_directly()
        
        # Step 4: Investigate general collections
        self.investigate_general_collections()
        
        # Step 5: Investigate specific collections
        self.investigate_specific_collections()
        
        print("\n" + "=" * 60)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        if tk_release_id:
            print(f"✅ TK-RELEASE-000001 exists with ID: {tk_release_id}")
        else:
            print("❌ TK-RELEASE-000001 not found in system")
        
        return True

if __name__ == "__main__":
    investigator = DetailedInvestigator()
    investigator.run_investigation()