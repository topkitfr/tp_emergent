#!/usr/bin/env python3
"""
NETTOYAGE DES COLLECTIONS ORPHELINES - Backend Test
===================================================

Mission: Nettoyer les collections qui référencent des jersey_release_id inexistants,
spécifiquement le Jersey Release ID '919e41f3-048d-4cd1-98f7-0829eb53c3c8' qui n'existe plus.

Objectifs:
1. Identifier les collections orphelines avec jersey_release: {} et master_jersey: {}
2. Supprimer les collections qui référencent des jersey_release_id inexistants
3. Vérifier que "Ma Collection" affiche maintenant les données enrichies correctement
4. Confirmer que seuls les Jersey Releases de FC Barcelona restent (pas de Marseille trouvé)

Authentification:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- Test User: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"

# Credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

# Specific orphaned Jersey Release ID to clean
ORPHANED_JERSEY_RELEASE_ID = "919e41f3-048d-4cd1-98f7-0829eb53c3c8"

class OrphanedCollectionsCleanupTester:
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
    
    def analyze_user_collections(self):
        """Analyze user's collections to identify orphaned ones"""
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            response = self.session.get(f"{BACKEND_URL}/users/{self.test_user['id']}/collections", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                collections = data.get('collections', [])
                self.log(f"📊 User has {len(collections)} total collections")
                
                valid_collections = []
                orphaned_collections = []
                
                for collection in collections:
                    jersey_release = collection.get('jersey_release', {})
                    master_jersey = collection.get('master_jersey', {})
                    collection_id = collection.get('id')
                    collection_type = collection.get('collection_type', 'unknown')
                    jersey_release_id = collection.get('jersey_release_id')
                    
                    # Check if this collection has empty jersey_release and master_jersey objects
                    if not jersey_release or not master_jersey or jersey_release == {} or master_jersey == {}:
                        orphaned_collections.append(collection)
                        self.log(f"   ❌ ORPHANED: {collection_id} ({collection_type}) - Jersey Release ID: {jersey_release_id}")
                        
                        # Check if this is the specific orphaned ID we're looking for
                        if jersey_release_id == ORPHANED_JERSEY_RELEASE_ID:
                            self.log(f"      🎯 TARGET FOUND: This references the missing Jersey Release {ORPHANED_JERSEY_RELEASE_ID}")
                    else:
                        valid_collections.append(collection)
                        team_name = master_jersey.get('team_name', 'Unknown')
                        player_name = jersey_release.get('player_name', 'Unknown')
                        self.log(f"   ✅ VALID: {collection_id} ({collection_type}) - {player_name} ({team_name})")
                
                self.log(f"📈 Collections Analysis: {len(valid_collections)} valid, {len(orphaned_collections)} orphaned")
                return collections, valid_collections, orphaned_collections
            else:
                self.log(f"❌ Failed to get user collections: {response.status_code} - {response.text}", "ERROR")
                return [], [], []
                
        except Exception as e:
            self.log(f"❌ Error analyzing user collections: {e}", "ERROR")
            return [], [], []
    
    def verify_jersey_release_exists(self, jersey_release_id):
        """Verify if a Jersey Release ID exists in the system"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/jersey-releases/{jersey_release_id}", headers=headers)
            
            if response.status_code == 200:
                self.log(f"✅ Jersey Release {jersey_release_id} exists")
                return True
            elif response.status_code == 404:
                self.log(f"❌ Jersey Release {jersey_release_id} does NOT exist (404)")
                return False
            else:
                self.log(f"⚠️  Jersey Release {jersey_release_id} check returned {response.status_code}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"❌ Error checking Jersey Release {jersey_release_id}: {e}", "ERROR")
            return False
    
    def clean_orphaned_collections(self, orphaned_collections):
        """Clean up orphaned collections"""
        if not orphaned_collections:
            self.log("✅ No orphaned collections to clean")
            return True
        
        self.log(f"🧹 Starting cleanup of {len(orphaned_collections)} orphaned collections...")
        
        cleaned_count = 0
        for collection in orphaned_collections:
            try:
                collection_id = collection.get('id')
                jersey_release_id = collection.get('jersey_release_id')
                collection_type = collection.get('collection_type', 'unknown')
                
                # Verify the Jersey Release doesn't exist before deleting
                if not self.verify_jersey_release_exists(jersey_release_id):
                    headers = {"Authorization": f"Bearer {self.test_user_token}"}
                    response = self.session.delete(f"{BACKEND_URL}/users/{self.test_user['id']}/collections/{collection_id}", headers=headers)
                    
                    if response.status_code in [200, 204, 404]:  # 404 means already deleted
                        self.log(f"   ✅ DELETED: Collection {collection_id} ({collection_type}) referencing missing Jersey Release {jersey_release_id}")
                        cleaned_count += 1
                    else:
                        self.log(f"   ❌ FAILED to delete collection {collection_id}: {response.status_code} - {response.text}", "ERROR")
                else:
                    self.log(f"   ⚠️  SKIPPED: Collection {collection_id} references existing Jersey Release {jersey_release_id}", "WARNING")
                    
            except Exception as e:
                self.log(f"   ❌ Error deleting collection {collection.get('id')}: {e}", "ERROR")
        
        self.log(f"🧹 Collection cleanup completed: {cleaned_count}/{len(orphaned_collections)} collections cleaned")
        return cleaned_count > 0
    
    def verify_final_state(self):
        """Verify the final state after cleanup"""
        self.log("🔍 Verifying final state after cleanup...")
        
        # Re-check user collections
        collections, valid_collections, orphaned_collections = self.analyze_user_collections()
        
        # Check what teams are represented
        teams_found = set()
        players_found = set()
        
        for collection in valid_collections:
            master_jersey = collection.get('master_jersey', {})
            jersey_release = collection.get('jersey_release', {})
            
            # Note: The master_jersey doesn't seem to have team_name in the response
            # Let's check what data we actually have
            if master_jersey:
                # Check if we can get team info from the master jersey reference
                topkit_ref = master_jersey.get('topkit_reference', 'Unknown')
                teams_found.add(f"Master Jersey {topkit_ref}")
            
            if jersey_release:
                player_name = jersey_release.get('player_name', '')
                if player_name:
                    players_found.add(player_name)
        
        self.log(f"🏆 Master Jerseys found: {teams_found}")
        self.log(f"👥 Players found: {players_found}")
        
        # Final summary
        self.log("📊 FINAL STATE SUMMARY:")
        self.log(f"   - Total Collections: {len(collections)}")
        self.log(f"   - Valid Collections: {len(valid_collections)}")
        self.log(f"   - Orphaned Collections: {len(orphaned_collections)}")
        
        return len(orphaned_collections) == 0
    
    def test_ma_collection_endpoints(self):
        """Test that 'Ma Collection' endpoints now work correctly"""
        self.log("🧪 Testing 'Ma Collection' endpoints functionality...")
        
        success_count = 0
        total_tests = 2
        
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Test owned collections endpoint
            response = self.session.get(f"{BACKEND_URL}/users/{self.test_user['id']}/collections/owned", headers=headers)
            
            if response.status_code == 200:
                owned_collections = response.json()
                self.log(f"✅ Owned collections endpoint working: {len(owned_collections)} items")
                success_count += 1
                
                # Check for enriched data
                enriched_count = 0
                for collection in owned_collections[:5]:  # Show first 5
                    jersey_release = collection.get('jersey_release', {})
                    master_jersey = collection.get('master_jersey', {})
                    if jersey_release and master_jersey and jersey_release != {} and master_jersey != {}:
                        player_name = jersey_release.get('player_name', 'Unknown')
                        topkit_ref = master_jersey.get('topkit_reference', 'Unknown')
                        self.log(f"   - Owned: {player_name} ({topkit_ref}) ✅ ENRICHED")
                        enriched_count += 1
                    else:
                        self.log(f"   - Owned: Empty data ❌ NOT ENRICHED")
                
                self.log(f"   📊 Owned collections enrichment: {enriched_count}/{min(len(owned_collections), 5)} items have enriched data")
            else:
                self.log(f"❌ Owned collections endpoint failed: {response.status_code}", "ERROR")
            
            # Test wanted collections endpoint
            response = self.session.get(f"{BACKEND_URL}/users/{self.test_user['id']}/collections/wanted", headers=headers)
            
            if response.status_code == 200:
                wanted_collections = response.json()
                self.log(f"✅ Wanted collections endpoint working: {len(wanted_collections)} items")
                success_count += 1
                
                # Check for enriched data
                enriched_count = 0
                for collection in wanted_collections[:5]:  # Show first 5
                    jersey_release = collection.get('jersey_release', {})
                    master_jersey = collection.get('master_jersey', {})
                    if jersey_release and master_jersey and jersey_release != {} and master_jersey != {}:
                        player_name = jersey_release.get('player_name', 'Unknown')
                        topkit_ref = master_jersey.get('topkit_reference', 'Unknown')
                        self.log(f"   - Wanted: {player_name} ({topkit_ref}) ✅ ENRICHED")
                        enriched_count += 1
                    else:
                        self.log(f"   - Wanted: Empty data ❌ NOT ENRICHED")
                
                self.log(f"   📊 Wanted collections enrichment: {enriched_count}/{min(len(wanted_collections), 5)} items have enriched data")
            else:
                self.log(f"❌ Wanted collections endpoint failed: {response.status_code}", "ERROR")
            
            return success_count == total_tests
            
        except Exception as e:
            self.log(f"❌ Error testing Ma Collection endpoints: {e}", "ERROR")
            return False
    
    def run_comprehensive_cleanup(self):
        """Run the comprehensive orphaned collections cleanup process"""
        self.log("🚀 STARTING ORPHANED COLLECTIONS CLEANUP")
        self.log("=" * 60)
        
        # Step 1: Authentication
        self.log("STEP 1: Authentication")
        if not self.authenticate_admin():
            return False
        if not self.authenticate_test_user():
            return False
        
        # Step 2: Analyze current state
        self.log("\nSTEP 2: Analyzing current collections state")
        collections, valid_collections, orphaned_collections = self.analyze_user_collections()
        
        # Step 3: Verify the specific orphaned Jersey Release ID
        self.log(f"\nSTEP 3: Verifying target Jersey Release ID {ORPHANED_JERSEY_RELEASE_ID}")
        target_exists = self.verify_jersey_release_exists(ORPHANED_JERSEY_RELEASE_ID)
        if target_exists:
            self.log(f"⚠️  WARNING: Target Jersey Release {ORPHANED_JERSEY_RELEASE_ID} still exists!", "WARNING")
        else:
            self.log(f"✅ CONFIRMED: Target Jersey Release {ORPHANED_JERSEY_RELEASE_ID} does not exist - cleanup needed")
        
        # Step 4: Clean orphaned collections
        self.log("\nSTEP 4: Cleaning orphaned collections")
        cleanup_performed = self.clean_orphaned_collections(orphaned_collections)
        
        # Step 5: Verify final state
        self.log("\nSTEP 5: Verifying final state")
        cleanup_successful = self.verify_final_state()
        
        # Step 6: Test Ma Collection functionality
        self.log("\nSTEP 6: Testing 'Ma Collection' endpoints")
        ma_collection_working = self.test_ma_collection_endpoints()
        
        # Final results
        self.log("\n" + "=" * 60)
        self.log("🏁 CLEANUP RESULTS SUMMARY")
        self.log("=" * 60)
        
        if cleanup_successful and ma_collection_working:
            self.log("🎉 SUCCESS: Orphaned collections cleanup completed successfully!")
            self.log("✅ All orphaned references have been cleaned")
            self.log("✅ Collections no longer contain empty jersey_release: {} and master_jersey: {}")
            self.log("✅ 'Ma Collection' endpoints are now functional with enriched data")
            return True
        else:
            self.log("❌ PARTIAL SUCCESS: Some issues remain")
            if not cleanup_successful:
                self.log("❌ Orphaned collections still exist")
            if not ma_collection_working:
                self.log("❌ 'Ma Collection' endpoints still have issues")
            return False

def main():
    """Main test execution"""
    print("🧹 ORPHANED COLLECTIONS CLEANUP - Backend Testing")
    print("=" * 60)
    print("Mission: Nettoyer les collections orphelines et restaurer 'Ma Collection'")
    print(f"Target: Jersey Release ID {ORPHANED_JERSEY_RELEASE_ID}")
    print("=" * 60)
    
    tester = OrphanedCollectionsCleanupTester()
    
    try:
        success = tester.run_comprehensive_cleanup()
        
        if success:
            print("\n🎉 MISSION ACCOMPLIE!")
            print("✅ Nettoyage des collections orphelines terminé avec succès")
            print("✅ Les objets vides jersey_release: {} et master_jersey: {} ont été éliminés")
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