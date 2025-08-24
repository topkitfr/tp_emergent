#!/usr/bin/env python3
"""
JERSEY RELEASE SUPPRESSION - BACKEND TEST
=========================================

This test implements the complete suppression of Jersey Releases from the TopKit system
as requested in the review. The goal is to clean the database completely and verify
that all Jersey Release references are removed.

Mission Critique - Nettoyage Complet:
1. Supprimer tous les Jersey Releases de la base de données
2. Nettoyer les collections utilisateur qui référencent des Jersey Releases  
3. Vérifier que le vestiaire retourne un array vide
4. Vérifier que les collections utilisateur retournent des arrays vides

Authentication:
- Admin: topkitfr@gmail.com / TopKitSecure789#

Objectif: Supprimer complètement tous les Jersey Releases et leurs références,
ramener le système à un état propre sans aucun Jersey Release.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footwear-collab.preview.emergentagent.com/api"

# Admin credentials for cleanup operations
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class JerseyReleaseSuppressionTester:
    def __init__(self):
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 AUTHENTICATING AS ADMIN...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_data = data.get("user", {})
                self.admin_user_id = user_data.get("id")
                
                self.log_result(
                    "Admin Authentication", 
                    True,
                    f"Admin authenticated successfully - Name: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.admin_user_id}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False,
                    f"Authentication failed - Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}

    def test_initial_state(self):
        """Test the initial state before cleanup"""
        print("📊 TESTING INITIAL STATE BEFORE CLEANUP...")
        
        # Test vestiaire endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/vestiaire")
            if response.status_code == 200:
                vestiaire_data = response.json()
                jersey_count = len(vestiaire_data) if isinstance(vestiaire_data, list) else 0
                self.log_result(
                    "Initial Vestiaire State",
                    True,
                    f"Vestiaire contains {jersey_count} Jersey Releases"
                )
            else:
                self.log_result(
                    "Initial Vestiaire State",
                    False,
                    f"Failed to get vestiaire - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Initial Vestiaire State", False, f"Exception: {str(e)}")

        # Test user collections (if admin has any)
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/users/{self.admin_user_id}/collections", headers=headers)
            if response.status_code == 200:
                collections_data = response.json()
                collection_count = len(collections_data) if isinstance(collections_data, list) else 0
                self.log_result(
                    "Initial Admin Collections State",
                    True,
                    f"Admin has {collection_count} collections"
                )
            else:
                self.log_result(
                    "Initial Admin Collections State",
                    False,
                    f"Failed to get admin collections - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Initial Admin Collections State", False, f"Exception: {str(e)}")

    def perform_jersey_release_cleanup(self):
        """Perform the complete Jersey Release cleanup"""
        print("🧹 PERFORMING JERSEY RELEASE CLEANUP...")
        
        # Note: Since we don't have direct database access endpoints for cleanup,
        # we'll need to use available API endpoints or create a cleanup endpoint
        
        # First, let's try to find if there are any admin endpoints for cleanup
        headers = self.get_auth_headers()
        
        # Try to get all jersey releases first
        try:
            response = requests.get(f"{BACKEND_URL}/jersey-releases", headers=headers)
            if response.status_code == 200:
                jersey_releases = response.json()
                jersey_count = len(jersey_releases) if isinstance(jersey_releases, list) else 0
                self.log_result(
                    "Jersey Releases Count",
                    True,
                    f"Found {jersey_count} Jersey Releases to clean up"
                )
                
                # If we have jersey releases, try to delete them one by one
                if jersey_count > 0 and isinstance(jersey_releases, list):
                    deleted_count = 0
                    for jersey_release in jersey_releases:
                        jersey_id = jersey_release.get('id')
                        if jersey_id:
                            try:
                                delete_response = requests.delete(f"{BACKEND_URL}/jersey-releases/{jersey_id}", headers=headers)
                                if delete_response.status_code in [200, 204]:
                                    deleted_count += 1
                            except Exception as e:
                                print(f"    Failed to delete Jersey Release {jersey_id}: {e}")
                    
                    self.log_result(
                        "Jersey Release Deletion",
                        deleted_count > 0,
                        f"Deleted {deleted_count} out of {jersey_count} Jersey Releases"
                    )
                
            else:
                self.log_result(
                    "Jersey Releases Retrieval",
                    False,
                    f"Failed to get jersey releases - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Jersey Releases Cleanup", False, f"Exception: {str(e)}")

        # Try to clean up user collections that reference Jersey Releases
        try:
            # Get all users first (if admin endpoint exists)
            response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    cleaned_collections = 0
                    for user in users:
                        user_id = user.get('id')
                        if user_id:
                            # Get user collections
                            collections_response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections", headers=headers)
                            if collections_response.status_code == 200:
                                collections = collections_response.json()
                                if isinstance(collections, list):
                                    for collection in collections:
                                        collection_id = collection.get('id')
                                        if collection_id:
                                            # Delete collection
                                            try:
                                                delete_response = requests.delete(f"{BACKEND_URL}/users/{user_id}/collections/{collection_id}", headers=headers)
                                                if delete_response.status_code in [200, 204]:
                                                    cleaned_collections += 1
                                            except Exception as e:
                                                print(f"    Failed to delete collection {collection_id}: {e}")
                    
                    self.log_result(
                        "User Collections Cleanup",
                        True,
                        f"Cleaned {cleaned_collections} user collections"
                    )
            else:
                self.log_result(
                    "User Collections Cleanup",
                    False,
                    f"Failed to get users for collection cleanup - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("User Collections Cleanup", False, f"Exception: {str(e)}")

    def verify_cleanup_success(self):
        """Verify that the cleanup was successful"""
        print("✅ VERIFYING CLEANUP SUCCESS...")
        
        # Test 1: Verify vestiaire is empty
        try:
            response = requests.get(f"{BACKEND_URL}/vestiaire")
            if response.status_code == 200:
                vestiaire_data = response.json()
                is_empty = isinstance(vestiaire_data, list) and len(vestiaire_data) == 0
                jersey_count = len(vestiaire_data) if isinstance(vestiaire_data, list) else "unknown"
                
                self.log_result(
                    "Vestiaire Empty Verification",
                    is_empty,
                    f"Vestiaire contains {jersey_count} Jersey Releases (should be 0)"
                )
            else:
                self.log_result(
                    "Vestiaire Empty Verification",
                    False,
                    f"Failed to verify vestiaire - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Vestiaire Empty Verification", False, f"Exception: {str(e)}")

        # Test 2: Verify admin collections are empty
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/users/{self.admin_user_id}/collections", headers=headers)
            if response.status_code == 200:
                collections_data = response.json()
                is_empty = isinstance(collections_data, list) and len(collections_data) == 0
                collection_count = len(collections_data) if isinstance(collections_data, list) else "unknown"
                
                self.log_result(
                    "Admin Collections Empty Verification",
                    is_empty,
                    f"Admin collections contain {collection_count} items (should be 0)"
                )
            else:
                self.log_result(
                    "Admin Collections Empty Verification",
                    False,
                    f"Failed to verify admin collections - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Admin Collections Empty Verification", False, f"Exception: {str(e)}")

        # Test 3: Verify owned collections endpoint is empty
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/users/{self.admin_user_id}/collections/owned", headers=headers)
            if response.status_code == 200:
                owned_data = response.json()
                is_empty = isinstance(owned_data, list) and len(owned_data) == 0
                owned_count = len(owned_data) if isinstance(owned_data, list) else "unknown"
                
                self.log_result(
                    "Owned Collections Empty Verification",
                    is_empty,
                    f"Owned collections contain {owned_count} items (should be 0)"
                )
            else:
                self.log_result(
                    "Owned Collections Empty Verification",
                    response.status_code == 404,  # 404 might be acceptable if no collections exist
                    f"Owned collections endpoint - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Owned Collections Empty Verification", False, f"Exception: {str(e)}")

        # Test 4: Verify wanted collections endpoint is empty
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{BACKEND_URL}/users/{self.admin_user_id}/collections/wanted", headers=headers)
            if response.status_code == 200:
                wanted_data = response.json()
                is_empty = isinstance(wanted_data, list) and len(wanted_data) == 0
                wanted_count = len(wanted_data) if isinstance(wanted_data, list) else "unknown"
                
                self.log_result(
                    "Wanted Collections Empty Verification",
                    is_empty,
                    f"Wanted collections contain {wanted_count} items (should be 0)"
                )
            else:
                self.log_result(
                    "Wanted Collections Empty Verification",
                    response.status_code == 404,  # 404 might be acceptable if no collections exist
                    f"Wanted collections endpoint - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Wanted Collections Empty Verification", False, f"Exception: {str(e)}")

    def test_jersey_release_endpoints(self):
        """Test various Jersey Release related endpoints to ensure they're empty"""
        print("🔍 TESTING JERSEY RELEASE ENDPOINTS...")
        
        headers = self.get_auth_headers()
        
        # Test jersey releases endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/jersey-releases", headers=headers)
            if response.status_code == 200:
                jersey_releases = response.json()
                is_empty = isinstance(jersey_releases, list) and len(jersey_releases) == 0
                count = len(jersey_releases) if isinstance(jersey_releases, list) else "unknown"
                
                self.log_result(
                    "Jersey Releases Endpoint Empty",
                    is_empty,
                    f"Jersey releases endpoint contains {count} items (should be 0)"
                )
            else:
                self.log_result(
                    "Jersey Releases Endpoint Empty",
                    response.status_code == 404,  # 404 acceptable if no jersey releases
                    f"Jersey releases endpoint - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Jersey Releases Endpoint Empty", False, f"Exception: {str(e)}")

        # Test marketplace catalog (should not contain Jersey Releases)
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/catalog")
            if response.status_code == 200:
                catalog_data = response.json()
                jersey_releases_count = 0
                
                # Check if catalog contains jersey releases
                if isinstance(catalog_data, dict):
                    jersey_releases_count = catalog_data.get('jersey_releases', 0)
                elif isinstance(catalog_data, list):
                    # Count items that might be jersey releases
                    jersey_releases_count = len([item for item in catalog_data if item.get('type') == 'jersey_release'])
                
                self.log_result(
                    "Marketplace Catalog Jersey Releases",
                    jersey_releases_count == 0,
                    f"Marketplace catalog contains {jersey_releases_count} Jersey Releases (should be 0)"
                )
            else:
                self.log_result(
                    "Marketplace Catalog Jersey Releases",
                    False,
                    f"Failed to get marketplace catalog - Status: {response.status_code}"
                )
        except Exception as e:
            self.log_result("Marketplace Catalog Jersey Releases", False, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run the complete Jersey Release suppression test"""
        print("🚀 STARTING JERSEY RELEASE SUPPRESSION TEST")
        print("=" * 60)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with cleanup.")
            return False
        
        # Step 2: Test initial state
        self.test_initial_state()
        
        # Step 3: Perform cleanup
        self.perform_jersey_release_cleanup()
        
        # Step 4: Verify cleanup success
        self.verify_cleanup_success()
        
        # Step 5: Test related endpoints
        self.test_jersey_release_endpoints()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Show critical results
        print(f"\n🎯 CRITICAL RESULTS:")
        vestiaire_empty = any(r["test"] == "Vestiaire Empty Verification" and r["success"] for r in self.test_results)
        collections_empty = any(r["test"] == "Admin Collections Empty Verification" and r["success"] for r in self.test_results)
        
        print(f"  - Vestiaire Empty: {'✅ YES' if vestiaire_empty else '❌ NO'}")
        print(f"  - Collections Empty: {'✅ YES' if collections_empty else '❌ NO'}")
        
        overall_success = vestiaire_empty and collections_empty
        print(f"\n🏆 OVERALL SUPPRESSION SUCCESS: {'✅ COMPLETE' if overall_success else '❌ INCOMPLETE'}")
        
        return overall_success

def main():
    """Main test execution"""
    tester = JerseyReleaseSuppressionTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()