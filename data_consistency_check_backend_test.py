#!/usr/bin/env python3
"""
DATA CONSISTENCY CHECK - BACKEND TEST
====================================

Final investigation to check data consistency between collections and vestiaire.
We found that some Jersey Release IDs in collections don't exist in vestiaire.
This test will identify which Jersey Releases are missing and why.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class DataConsistencyChecker:
    def __init__(self):
        self.user_token = None
        self.user_user_id = None
        
    def authenticate_user(self):
        """Authenticate user and get token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_data = data.get("user", {})
                self.user_user_id = user_data.get("id")
                print(f"✅ Authenticated as: {user_data.get('name')}")
                return True
            else:
                print(f"❌ Authentication failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def check_data_consistency(self):
        """Check data consistency between collections and vestiaire"""
        print("\n🔍 DATA CONSISTENCY CHECK")
        print("=" * 40)
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Get all collections
            owned_response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            wanted_response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/wanted", headers=headers)
            vestiaire_response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if owned_response.status_code == 200 and wanted_response.status_code == 200 and vestiaire_response.status_code == 200:
                owned_collections = owned_response.json()
                wanted_collections = wanted_response.json()
                vestiaire_data = vestiaire_response.json()
                
                # Create sets for comparison
                collection_jersey_ids = set()
                vestiaire_jersey_ids = set()
                
                # Collect all Jersey Release IDs from collections
                for collection in owned_collections + wanted_collections:
                    jersey_release_id = collection.get('jersey_release_id')
                    if jersey_release_id:
                        collection_jersey_ids.add(jersey_release_id)
                
                # Collect all Jersey Release IDs from vestiaire
                for jersey_release in vestiaire_data:
                    jersey_id = jersey_release.get('id')
                    if jersey_id:
                        vestiaire_jersey_ids.add(jersey_id)
                
                # Find missing Jersey Releases
                missing_in_vestiaire = collection_jersey_ids - vestiaire_jersey_ids
                extra_in_vestiaire = vestiaire_jersey_ids - collection_jersey_ids
                
                print(f"📊 CONSISTENCY ANALYSIS:")
                print(f"   Collections reference {len(collection_jersey_ids)} unique Jersey Releases")
                print(f"   Vestiaire contains {len(vestiaire_jersey_ids)} Jersey Releases")
                print(f"   Missing in vestiaire: {len(missing_in_vestiaire)}")
                print(f"   Extra in vestiaire: {len(extra_in_vestiaire)}")
                print()
                
                if missing_in_vestiaire:
                    print("❌ MISSING JERSEY RELEASES IN VESTIAIRE:")
                    for missing_id in missing_in_vestiaire:
                        print(f"   • {missing_id}")
                        
                        # Find which collections reference this missing Jersey Release
                        referencing_collections = []
                        for collection in owned_collections + wanted_collections:
                            if collection.get('jersey_release_id') == missing_id:
                                referencing_collections.append({
                                    'id': collection.get('id'),
                                    'type': 'owned' if collection in owned_collections else 'wanted',
                                    'created_at': collection.get('created_at')
                                })
                        
                        print(f"     Referenced by {len(referencing_collections)} collections:")
                        for ref in referencing_collections:
                            print(f"       - {ref['type']} collection {ref['id']} (created: {ref['created_at']})")
                    print()
                
                if extra_in_vestiaire:
                    print("ℹ️  JERSEY RELEASES ONLY IN VESTIAIRE (not in user's collections):")
                    for extra_id in list(extra_in_vestiaire)[:5]:  # Show first 5
                        jersey_release = next((jr for jr in vestiaire_data if jr.get('id') == extra_id), None)
                        if jersey_release:
                            player_name = jersey_release.get('player_name', 'Unknown')
                            print(f"   • {extra_id} - {player_name}")
                    if len(extra_in_vestiaire) > 5:
                        print(f"   ... and {len(extra_in_vestiaire) - 5} more")
                    print()
                
                # Summary
                consistency_percentage = ((len(collection_jersey_ids) - len(missing_in_vestiaire)) / len(collection_jersey_ids) * 100) if collection_jersey_ids else 100
                print(f"📈 DATA CONSISTENCY: {consistency_percentage:.1f}%")
                
                if missing_in_vestiaire:
                    print("🔧 ISSUE IDENTIFIED: Some Jersey Releases referenced in collections no longer exist in vestiaire")
                    print("   This could be due to:")
                    print("   • Jersey Releases being deleted from the system")
                    print("   • Data migration issues")
                    print("   • Inconsistent data cleanup")
                else:
                    print("✅ All Jersey Releases in collections exist in vestiaire")
                
                return len(missing_in_vestiaire) == 0
                
            else:
                print("❌ Failed to retrieve data for consistency check")
                return False
                
        except Exception as e:
            print(f"❌ Data consistency check error: {str(e)}")
            return False

    def run_check(self):
        """Run the complete data consistency check"""
        print("🔍 DATA CONSISTENCY CHECK")
        print("=" * 50)
        print("Checking consistency between user collections and vestiaire data")
        print()
        
        if not self.authenticate_user():
            return False
        
        return self.check_data_consistency()

def main():
    """Main execution function"""
    checker = DataConsistencyChecker()
    success = checker.run_check()
    
    if success:
        print("\n🎉 Data consistency check completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Data consistency issues found")
        sys.exit(1)

if __name__ == "__main__":
    main()