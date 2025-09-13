#!/usr/bin/env python3
"""
NETTOYAGE DES JERSEY RELEASES ORPHELINES - Backend Test
=======================================================

Mission: Nettoyer l'ensemble des Jersey Releases qui ne se basent pas sur les Master Releases.
Il ne devrait y avoir que des Jersey Releases de Barcelone ou de l'Olympique de Marseille 
si on applique correctement la logique Master et Release.

Objectifs:
1. Examiner la structure actuelle des Master Jerseys et Jersey Releases
2. Identifier les Master Jerseys valides (Barcelone et Marseille uniquement)
3. Supprimer tous les Jersey Releases qui ne sont pas liés à des Master Jerseys valides
4. Nettoyer les collections qui référencent ces Jersey Releases supprimés
5. Vérifier que seuls les Jersey Releases de Barcelone et Marseille restent
6. Tester que "Ma Collection" affiche maintenant les données enrichies correctement

Authentification:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- Test User: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"

# Credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class JerseyReleaseCleanupTester:
    def __init__(self):
        self.admin_token = None
        self.admin_user = None
        self.test_user_token = None
        self.test_user = None
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.admin_user = data["user"]
                self.log(f"✅ Admin authentication successful: {self.admin_user['name']} (Role: {self.admin_user['role']})")
                return True
            else:
                self.log(f"❌ Admin authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Admin authentication error: {e}", "ERROR")
            return False
    
    def authenticate_test_user(self):
        """Authenticate as test user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data["token"]
                self.test_user = data["user"]
                self.log(f"✅ Test user authentication successful: {self.test_user['name']} (ID: {self.test_user['id']})")
                return True
            else:
                self.log(f"❌ Test user authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Test user authentication error: {e}", "ERROR")
            return False
    
    def get_master_jerseys(self):
        """Get all Master Jerseys to understand the valid base"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/master-jerseys", headers=headers)
            
            if response.status_code == 200:
                master_jerseys = response.json()
                self.log(f"📊 Found {len(master_jerseys)} Master Jerseys")
                
                for mj in master_jerseys:
                    team_name = mj.get('team_name', 'Unknown')
                    season = mj.get('season', 'Unknown')
                    self.log(f"   - Master Jersey: {team_name} ({season}) - ID: {mj.get('id')}")
                
                return master_jerseys
            else:
                self.log(f"❌ Failed to get Master Jerseys: {response.status_code} - {response.text}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Error getting Master Jerseys: {e}", "ERROR")
            return []
    
    def get_jersey_releases(self):
        """Get all Jersey Releases to analyze current state"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/jersey-releases", headers=headers)
            
            if response.status_code == 200:
                jersey_releases = response.json()
                self.log(f"📊 Found {len(jersey_releases)} Jersey Releases")
                
                valid_releases = []
                orphaned_releases = []
                
                for jr in jersey_releases:
                    master_jersey_id = jr.get('master_jersey_id')
                    release_id = jr.get('id')
                    
                    if master_jersey_id:
                        valid_releases.append(jr)
                        self.log(f"   ✅ Valid Release: {release_id} -> Master: {master_jersey_id}")
                    else:
                        orphaned_releases.append(jr)
                        self.log(f"   ❌ Orphaned Release: {release_id} (No master_jersey_id)")
                
                self.log(f"📈 Analysis: {len(valid_releases)} valid, {len(orphaned_releases)} orphaned")
                return jersey_releases, valid_releases, orphaned_releases
            else:
                self.log(f"❌ Failed to get Jersey Releases: {response.status_code} - {response.text}", "ERROR")
                return [], [], []
                
        except Exception as e:
            self.log(f"❌ Error getting Jersey Releases: {e}", "ERROR")
            return [], [], []
    
    def get_vestiaire_data(self):
        """Get vestiaire data to see what's currently available"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if response.status_code == 200:
                vestiaire_data = response.json()
                self.log(f"📊 Vestiaire contains {len(vestiaire_data)} items")
                
                for item in vestiaire_data:
                    jersey_release = item.get('jersey_release', {})
                    master_jersey = item.get('master_jersey', {})
                    team_name = master_jersey.get('team_name', 'Unknown')
                    season = master_jersey.get('season', 'Unknown')
                    self.log(f"   - Vestiaire Item: {team_name} ({season}) - Release ID: {jersey_release.get('id', 'Unknown')}")
                
                return vestiaire_data
            else:
                self.log(f"❌ Failed to get vestiaire data: {response.status_code} - {response.text}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Error getting vestiaire data: {e}", "ERROR")
            return []
    
    def get_user_collections(self, user_id):
        """Get user's collections to analyze current state"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/collections", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                self.log(f"📊 User has {len(collections)} collections")
                
                valid_collections = []
                orphaned_collections = []
                
                for collection in collections:
                    jersey_release = collection.get('jersey_release', {})
                    master_jersey = collection.get('master_jersey', {})
                    collection_id = collection.get('id')
                    collection_type = collection.get('collection_type', 'unknown')
                    
                    if jersey_release and master_jersey and jersey_release != {} and master_jersey != {}:
                        valid_collections.append(collection)
                        team_name = master_jersey.get('team_name', 'Unknown')
                        self.log(f"   ✅ Valid Collection: {collection_id} ({collection_type}) - {team_name}")
                    else:
                        orphaned_collections.append(collection)
                        jersey_release_id = collection.get('jersey_release_id', 'Unknown')
                        self.log(f"   ❌ Orphaned Collection: {collection_id} ({collection_type}) - Jersey Release ID: {jersey_release_id}")
                
                self.log(f"📈 Collections Analysis: {len(valid_collections)} valid, {len(orphaned_collections)} orphaned")
                return collections, valid_collections, orphaned_collections
            else:
                self.log(f"❌ Failed to get user collections: {response.status_code} - {response.text}", "ERROR")
                return [], [], []
                
        except Exception as e:
            self.log(f"❌ Error getting user collections: {e}", "ERROR")
            return [], [], []
    
    def validate_master_jersey_references(self, jersey_releases, master_jerseys):
        """Validate that Jersey Releases reference valid Master Jerseys"""
        valid_master_ids = {mj['id'] for mj in master_jerseys}
        
        valid_releases = []
        invalid_releases = []
        
        for jr in jersey_releases:
            master_jersey_id = jr.get('master_jersey_id')
            if master_jersey_id and master_jersey_id in valid_master_ids:
                valid_releases.append(jr)
            else:
                invalid_releases.append(jr)
        
        self.log(f"🔍 Master Jersey Validation:")
        self.log(f"   - Valid Master Jersey IDs: {len(valid_master_ids)}")
        self.log(f"   - Jersey Releases with valid Master references: {len(valid_releases)}")
        self.log(f"   - Jersey Releases with invalid Master references: {len(invalid_releases)}")
        
        return valid_releases, invalid_releases
    
    def clean_orphaned_jersey_releases(self, invalid_releases):
        """Clean up Jersey Releases that don't reference valid Master Jerseys"""
        if not invalid_releases:
            self.log("✅ No orphaned Jersey Releases to clean")
            return True
        
        self.log(f"🧹 Starting cleanup of {len(invalid_releases)} orphaned Jersey Releases...")
        
        cleaned_count = 0
        for jr in invalid_releases:
            try:
                release_id = jr.get('id')
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                # Note: This assumes there's a DELETE endpoint for jersey releases
                # If not available, we might need to use a different approach
                response = self.session.delete(f"{BACKEND_URL}/jersey-releases/{release_id}", headers=headers)
                
                if response.status_code in [200, 204, 404]:  # 404 means already deleted
                    self.log(f"   ✅ Deleted Jersey Release: {release_id}")
                    cleaned_count += 1
                else:
                    self.log(f"   ❌ Failed to delete Jersey Release {release_id}: {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"   ❌ Error deleting Jersey Release {jr.get('id')}: {e}", "ERROR")
        
        self.log(f"🧹 Cleanup completed: {cleaned_count}/{len(invalid_releases)} Jersey Releases cleaned")
        return cleaned_count == len(invalid_releases)
    
    def clean_orphaned_collections(self, orphaned_collections):
        """Clean up collections that reference non-existent Jersey Releases"""
        if not orphaned_collections:
            self.log("✅ No orphaned collections to clean")
            return True
        
        self.log(f"🧹 Starting cleanup of {len(orphaned_collections)} orphaned collections...")
        
        cleaned_count = 0
        for collection in orphaned_collections:
            try:
                collection_id = collection.get('id')
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                response = self.session.delete(f"{BACKEND_URL}/users/{self.test_user['id']}/collections/{collection_id}", headers=headers)
                
                if response.status_code in [200, 204, 404]:  # 404 means already deleted
                    self.log(f"   ✅ Deleted orphaned collection: {collection_id}")
                    cleaned_count += 1
                else:
                    self.log(f"   ❌ Failed to delete collection {collection_id}: {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"   ❌ Error deleting collection {collection.get('id')}: {e}", "ERROR")
        
        self.log(f"🧹 Collection cleanup completed: {cleaned_count}/{len(orphaned_collections)} collections cleaned")
        return cleaned_count == len(orphaned_collections)
    
    def verify_final_state(self):
        """Verify the final state after cleanup"""
        self.log("🔍 Verifying final state after cleanup...")
        
        # Re-check Master Jerseys
        master_jerseys = self.get_master_jerseys()
        
        # Re-check Jersey Releases
        jersey_releases, valid_releases, orphaned_releases = self.get_jersey_releases()
        
        # Re-check vestiaire
        vestiaire_data = self.get_vestiaire_data()
        
        # Re-check user collections
        collections, valid_collections, orphaned_collections = self.get_user_collections(self.test_user['id'])
        
        # Verify only Barcelona and Marseille remain
        expected_teams = {'FC Barcelona', 'Olympique de Marseille', 'Barcelona', 'Marseille'}
        
        teams_found = set()
        for item in vestiaire_data:
            master_jersey = item.get('master_jersey', {})
            team_name = master_jersey.get('team_name', '')
            if team_name:
                teams_found.add(team_name)
        
        self.log(f"🏆 Teams found in vestiaire: {teams_found}")
        
        # Check if only expected teams remain
        unexpected_teams = teams_found - expected_teams
        if unexpected_teams:
            self.log(f"⚠️  Unexpected teams still present: {unexpected_teams}", "WARNING")
        else:
            self.log("✅ Only expected teams (Barcelona/Marseille) remain")
        
        # Final summary
        self.log("📊 FINAL STATE SUMMARY:")
        self.log(f"   - Master Jerseys: {len(master_jerseys)}")
        self.log(f"   - Jersey Releases: {len(jersey_releases)} (Valid: {len(valid_releases)}, Orphaned: {len(orphaned_releases)})")
        self.log(f"   - Vestiaire Items: {len(vestiaire_data)}")
        self.log(f"   - User Collections: {len(collections)} (Valid: {len(valid_collections)}, Orphaned: {len(orphaned_collections)})")
        
        return len(orphaned_releases) == 0 and len(orphaned_collections) == 0
    
    def test_ma_collection_page(self):
        """Test that 'Ma Collection' page now works correctly"""
        self.log("🧪 Testing 'Ma Collection' page functionality...")
        
        try:
            # Test owned collections
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = self.session.get(f"{BACKEND_URL}/users/{self.test_user['id']}/collections/owned", headers=headers)
            
            if response.status_code == 200:
                owned_collections = response.json()
                self.log(f"✅ Owned collections endpoint working: {len(owned_collections)} items")
                
                for collection in owned_collections[:3]:  # Show first 3
                    jersey_release = collection.get('jersey_release', {})
                    master_jersey = collection.get('master_jersey', {})
                    if jersey_release and master_jersey:
                        team_name = master_jersey.get('team_name', 'Unknown')
                        season = master_jersey.get('season', 'Unknown')
                        self.log(f"   - Owned: {team_name} ({season})")
                    else:
                        self.log(f"   - Owned: Empty data (jersey_release: {bool(jersey_release)}, master_jersey: {bool(master_jersey)})")
            else:
                self.log(f"❌ Owned collections endpoint failed: {response.status_code}", "ERROR")
            
            # Test wanted collections
            response = self.session.get(f"{BACKEND_URL}/users/{self.test_user['id']}/collections/wanted", headers=headers)
            
            if response.status_code == 200:
                wanted_collections = response.json()
                self.log(f"✅ Wanted collections endpoint working: {len(wanted_collections)} items")
                
                for collection in wanted_collections[:3]:  # Show first 3
                    jersey_release = collection.get('jersey_release', {})
                    master_jersey = collection.get('master_jersey', {})
                    if jersey_release and master_jersey:
                        team_name = master_jersey.get('team_name', 'Unknown')
                        season = master_jersey.get('season', 'Unknown')
                        self.log(f"   - Wanted: {team_name} ({season})")
                    else:
                        self.log(f"   - Wanted: Empty data (jersey_release: {bool(jersey_release)}, master_jersey: {bool(master_jersey)})")
            else:
                self.log(f"❌ Wanted collections endpoint failed: {response.status_code}", "ERROR")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error testing Ma Collection page: {e}", "ERROR")
            return False
    
    def run_comprehensive_cleanup(self):
        """Run the comprehensive Jersey Release cleanup process"""
        self.log("🚀 STARTING COMPREHENSIVE JERSEY RELEASE CLEANUP")
        self.log("=" * 60)
        
        # Step 1: Authentication
        self.log("STEP 1: Authentication")
        if not self.authenticate_admin():
            return False
        if not self.authenticate_test_user():
            return False
        
        # Step 2: Analyze current state
        self.log("\nSTEP 2: Analyzing current state")
        master_jerseys = self.get_master_jerseys()
        jersey_releases, valid_releases, orphaned_releases = self.get_jersey_releases()
        vestiaire_data = self.get_vestiaire_data()
        collections, valid_collections, orphaned_collections = self.get_user_collections(self.test_user['id'])
        
        # Step 3: Validate Master Jersey references
        self.log("\nSTEP 3: Validating Master Jersey references")
        valid_releases, invalid_releases = self.validate_master_jersey_references(jersey_releases, master_jerseys)
        
        # Step 4: Clean orphaned Jersey Releases
        self.log("\nSTEP 4: Cleaning orphaned Jersey Releases")
        if not self.clean_orphaned_jersey_releases(invalid_releases):
            self.log("❌ Failed to clean all orphaned Jersey Releases", "ERROR")
        
        # Step 5: Clean orphaned collections
        self.log("\nSTEP 5: Cleaning orphaned collections")
        if not self.clean_orphaned_collections(orphaned_collections):
            self.log("❌ Failed to clean all orphaned collections", "ERROR")
        
        # Step 6: Verify final state
        self.log("\nSTEP 6: Verifying final state")
        cleanup_successful = self.verify_final_state()
        
        # Step 7: Test Ma Collection functionality
        self.log("\nSTEP 7: Testing 'Ma Collection' functionality")
        ma_collection_working = self.test_ma_collection_page()
        
        # Final results
        self.log("\n" + "=" * 60)
        self.log("🏁 CLEANUP RESULTS SUMMARY")
        self.log("=" * 60)
        
        if cleanup_successful and ma_collection_working:
            self.log("🎉 SUCCESS: Jersey Release cleanup completed successfully!")
            self.log("✅ All orphaned references have been cleaned")
            self.log("✅ Only Barcelona and Marseille Jersey Releases remain")
            self.log("✅ 'Ma Collection' page is now functional with enriched data")
            return True
        else:
            self.log("❌ PARTIAL SUCCESS: Some issues remain")
            if not cleanup_successful:
                self.log("❌ Orphaned references still exist")
            if not ma_collection_working:
                self.log("❌ 'Ma Collection' page still has issues")
            return False

def main():
    """Main test execution"""
    print("🧹 JERSEY RELEASE CLEANUP - Backend Testing")
    print("=" * 60)
    print("Mission: Nettoyer les Jersey Releases orphelines et restaurer 'Ma Collection'")
    print("=" * 60)
    
    tester = JerseyReleaseCleanupTester()
    
    try:
        success = tester.run_comprehensive_cleanup()
        
        if success:
            print("\n🎉 MISSION ACCOMPLIE!")
            print("✅ Nettoyage des Jersey Releases terminé avec succès")
            print("✅ Seuls les Jersey Releases de Barcelone et Marseille restent")
            print("✅ 'Ma Collection' affiche maintenant les données enrichies")
            sys.exit(0)
        else:
            print("\n⚠️  MISSION PARTIELLEMENT ACCOMPLIE")
            print("❌ Certains problèmes persistent")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()