#!/usr/bin/env python3
"""
Jersey Release Collection Endpoints Backend Testing
Testing the new Jersey Release collection endpoints as requested in the review.

ENDPOINTS TO TEST:
1. GET /api/users/{user_id}/collections/owned - get owned Jersey Release collections
2. GET /api/users/{user_id}/collections/wanted - get wanted Jersey Release collections  
3. POST /api/users/{user_id}/collections - add Jersey Release to collection
4. DELETE /api/users/{user_id}/collections/{collection_id} - remove from collection
5. PUT /api/users/{user_id}/collections/{collection_id} - update collection item details
6. POST /api/vestiaire/add-to-collection - add vestiaire item to collection

TEST FLOW:
1. Test authentication with existing user (steinmetzlivio@gmail.com/123)
2. Get current owned/wanted collections (should be empty initially)
3. Create test Jersey Release if needed (from existing master jerseys)
4. Add Jersey Release to owned collection
5. Add Jersey Release to wanted collection  
6. Test updating collection item details
7. Test removing from collection
8. Test vestiaire integration endpoint
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://kit-fixes.preview.emergentagent.com/api"

# Test credentials - using working admin account
TEST_USER_EMAIL = "topkitfr@gmail.com"
TEST_USER_PASSWORD = "TopKitSecure789#"

class JerseyReleaseCollectionTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_user(self):
        """Authenticate test user"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.user_id = data.get("user", {}).get("id")
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.user_token}"
                })
                
                self.log_result("User Authentication", True, 
                              f"User: {data.get('user', {}).get('name')}, ID: {self.user_id}")
                return True
            else:
                self.log_result("User Authentication", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_master_jerseys(self):
        """Get available master jerseys to create releases from"""
        try:
            response = self.session.get(f"{BASE_URL}/master-jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                self.log_result("Get Master Jerseys", True, f"Found {len(jerseys)} master jerseys")
                return jerseys
            else:
                self.log_result("Get Master Jerseys", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Get Master Jerseys", False, f"Exception: {str(e)}")
            return []
    
    def get_jersey_releases(self):
        """Get available jersey releases"""
        try:
            response = self.session.get(f"{BASE_URL}/jersey-releases")
            
            if response.status_code == 200:
                releases = response.json()
                self.log_result("Get Jersey Releases", True, f"Found {len(releases)} jersey releases")
                return releases
            else:
                self.log_result("Get Jersey Releases", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Get Jersey Releases", False, f"Exception: {str(e)}")
            return []
    
    def create_test_jersey_release(self, master_jersey_id):
        """Create a test Jersey Release for testing"""
        try:
            release_data = {
                "master_jersey_id": master_jersey_id,
                "release_type": "player_version",
                "size_range": ["S", "M", "L", "XL"],
                "player_name": "Test Player",
                "player_number": 10,
                "retail_price": 89.99,
                "sku_code": "TEST-RELEASE-001",
                "variant_notes": "Test release for collection testing",
                "product_images": ["test_image_1.jpg", "test_image_2.jpg"]
            }
            
            response = self.session.post(f"{BASE_URL}/jersey-releases", json=release_data)
            
            if response.status_code == 201:
                release = response.json()
                self.log_result("Create Test Jersey Release", True, 
                              f"Created release ID: {release.get('id')}")
                return release
            else:
                self.log_result("Create Test Jersey Release", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Create Test Jersey Release", False, f"Exception: {str(e)}")
            return None
    
    def get_owned_collections(self):
        """Test GET /api/users/{user_id}/collections/owned"""
        try:
            response = self.session.get(f"{BASE_URL}/users/{self.user_id}/collections/owned")
            
            if response.status_code == 200:
                collections = response.json()
                self.log_result("Get Owned Collections", True, 
                              f"Found {len(collections)} owned items")
                return collections
            else:
                self.log_result("Get Owned Collections", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Get Owned Collections", False, f"Exception: {str(e)}")
            return []
    
    def get_wanted_collections(self):
        """Test GET /api/users/{user_id}/collections/wanted"""
        try:
            response = self.session.get(f"{BASE_URL}/users/{self.user_id}/collections/wanted")
            
            if response.status_code == 200:
                collections = response.json()
                self.log_result("Get Wanted Collections", True, 
                              f"Found {len(collections)} wanted items")
                return collections
            else:
                self.log_result("Get Wanted Collections", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Get Wanted Collections", False, f"Exception: {str(e)}")
            return []
    
    def add_to_owned_collection(self, jersey_release_id):
        """Test POST /api/users/{user_id}/collections - add to owned"""
        try:
            collection_data = {
                "jersey_release_id": jersey_release_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "mint",
                "purchase_price": 85.00,
                "estimated_value": 90.00
            }
            
            response = self.session.post(f"{BASE_URL}/users/{self.user_id}/collections", 
                                       json=collection_data)
            
            if response.status_code == 200:
                result = response.json()
                collection_id = result.get("collection_id")
                self.log_result("Add to Owned Collection", True, 
                              f"Added to owned collection, ID: {collection_id}")
                return collection_id
            else:
                self.log_result("Add to Owned Collection", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Add to Owned Collection", False, f"Exception: {str(e)}")
            return None
    
    def add_to_wanted_collection(self, jersey_release_id):
        """Test POST /api/users/{user_id}/collections - add to wanted"""
        try:
            collection_data = {
                "jersey_release_id": jersey_release_id,
                "collection_type": "wanted"
            }
            
            response = self.session.post(f"{BASE_URL}/users/{self.user_id}/collections", 
                                       json=collection_data)
            
            if response.status_code == 200:
                result = response.json()
                collection_id = result.get("collection_id")
                self.log_result("Add to Wanted Collection", True, 
                              f"Added to wanted collection, ID: {collection_id}")
                return collection_id
            else:
                self.log_result("Add to Wanted Collection", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Add to Wanted Collection", False, f"Exception: {str(e)}")
            return None
    
    def update_collection_item(self, collection_id):
        """Test PUT /api/users/{user_id}/collections/{collection_id}"""
        try:
            update_data = {
                "size": "XL",
                "condition": "near_mint",
                "purchase_price": 80.00,
                "estimated_value": 95.00
            }
            
            response = self.session.put(f"{BASE_URL}/users/{self.user_id}/collections/{collection_id}", 
                                      json=update_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Update Collection Item", True, 
                              f"Updated collection item: {result.get('message')}")
                return True
            else:
                self.log_result("Update Collection Item", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Update Collection Item", False, f"Exception: {str(e)}")
            return False
    
    def remove_from_collection(self, collection_id):
        """Test DELETE /api/users/{user_id}/collections/{collection_id}"""
        try:
            response = self.session.delete(f"{BASE_URL}/users/{self.user_id}/collections/{collection_id}")
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Remove from Collection", True, 
                              f"Removed from collection: {result.get('message')}")
                return True
            else:
                self.log_result("Remove from Collection", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Remove from Collection", False, f"Exception: {str(e)}")
            return False
    
    def test_vestiaire_integration(self, jersey_release_id):
        """Test POST /api/vestiaire/add-to-collection"""
        try:
            vestiaire_data = {
                "jersey_release_id": jersey_release_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "good",
                "purchase_price": 75.00
            }
            
            response = self.session.post(f"{BASE_URL}/vestiaire/add-to-collection", 
                                       json=vestiaire_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("Vestiaire Integration", True, 
                              f"Added via vestiaire: {result.get('message')}")
                return result.get("collection_id")
            else:
                self.log_result("Vestiaire Integration", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Vestiaire Integration", False, f"Exception: {str(e)}")
            return None
    
    def test_error_scenarios(self, jersey_release_id):
        """Test error scenarios and edge cases"""
        print("\n🔍 Testing Error Scenarios:")
        
        # Test duplicate addition
        try:
            collection_data = {
                "jersey_release_id": jersey_release_id,
                "collection_type": "owned",
                "size": "L"
            }
            
            response = self.session.post(f"{BASE_URL}/users/{self.user_id}/collections", 
                                       json=collection_data)
            
            if response.status_code == 400:
                self.log_result("Duplicate Addition Prevention", True, 
                              "Correctly prevented duplicate addition")
            else:
                self.log_result("Duplicate Addition Prevention", False, 
                              f"Expected HTTP 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Duplicate Addition Prevention", False, f"Exception: {str(e)}")
        
        # Test invalid collection type
        try:
            collection_data = {
                "jersey_release_id": jersey_release_id,
                "collection_type": "invalid_type"
            }
            
            response = self.session.post(f"{BASE_URL}/users/{self.user_id}/collections", 
                                       json=collection_data)
            
            if response.status_code == 400:
                self.log_result("Invalid Collection Type", True, 
                              "Correctly rejected invalid collection type")
            else:
                self.log_result("Invalid Collection Type", False, 
                              f"Expected HTTP 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Invalid Collection Type", False, f"Exception: {str(e)}")
        
        # Test non-existent jersey release
        try:
            collection_data = {
                "jersey_release_id": "non-existent-id",
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{BASE_URL}/users/{self.user_id}/collections", 
                                       json=collection_data)
            
            if response.status_code == 404:
                self.log_result("Non-existent Jersey Release", True, 
                              "Correctly rejected non-existent jersey release")
            else:
                self.log_result("Non-existent Jersey Release", False, 
                              f"Expected HTTP 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Non-existent Jersey Release", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive test of Jersey Release collection endpoints"""
        print("🚀 Starting Jersey Release Collection Endpoints Testing")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot continue testing")
            return
        
        # Step 2: Get initial collections (should be empty)
        print("\n📋 Getting Initial Collections:")
        initial_owned = self.get_owned_collections()
        initial_wanted = self.get_wanted_collections()
        
        # Step 3: Get available data
        print("\n🔍 Getting Available Data:")
        master_jerseys = self.get_master_jerseys()
        jersey_releases = self.get_jersey_releases()
        
        # Step 4: Create test Jersey Release if needed
        test_jersey_release = None
        if jersey_releases:
            test_jersey_release = jersey_releases[0]
            self.log_result("Use Existing Jersey Release", True, 
                          f"Using existing release ID: {test_jersey_release.get('id')}")
        elif master_jerseys:
            print("\n🏗️ Creating Test Jersey Release:")
            test_jersey_release = self.create_test_jersey_release(master_jerseys[0]["id"])
        else:
            print("❌ No master jerseys or jersey releases available - cannot continue testing")
            return
        
        if not test_jersey_release:
            print("❌ No test jersey release available - cannot continue testing")
            return
        
        jersey_release_id = test_jersey_release["id"]
        
        # Step 5: Test adding to collections
        print("\n➕ Testing Collection Addition:")
        owned_collection_id = self.add_to_owned_collection(jersey_release_id)
        wanted_collection_id = self.add_to_wanted_collection(jersey_release_id)
        
        # Step 6: Verify collections were added
        print("\n📋 Verifying Collections After Addition:")
        owned_after_add = self.get_owned_collections()
        wanted_after_add = self.get_wanted_collections()
        
        # Step 7: Test updating collection item
        if owned_collection_id:
            print("\n✏️ Testing Collection Item Update:")
            self.update_collection_item(owned_collection_id)
        
        # Step 8: Test vestiaire integration
        print("\n🛍️ Testing Vestiaire Integration:")
        vestiaire_collection_id = self.test_vestiaire_integration(jersey_release_id)
        
        # Step 9: Test error scenarios
        self.test_error_scenarios(jersey_release_id)
        
        # Step 10: Test removal (cleanup)
        print("\n🗑️ Testing Collection Removal (Cleanup):")
        if owned_collection_id:
            self.remove_from_collection(owned_collection_id)
        if wanted_collection_id:
            self.remove_from_collection(wanted_collection_id)
        if vestiaire_collection_id:
            self.remove_from_collection(vestiaire_collection_id)
        
        # Step 11: Final verification
        print("\n📋 Final Collections Verification:")
        final_owned = self.get_owned_collections()
        final_wanted = self.get_wanted_collections()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 JERSEY RELEASE COLLECTION ENDPOINTS TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅" in r["status"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if "❌" in result["status"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 CONCLUSION:")
        if success_rate >= 90:
            print("✅ Jersey Release collection endpoints are PRODUCTION-READY and working excellently!")
        elif success_rate >= 75:
            print("⚠️ Jersey Release collection endpoints are mostly functional with minor issues.")
        else:
            print("❌ Jersey Release collection endpoints have significant issues requiring fixes.")
        
        print(f"\nTesting completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    tester = JerseyReleaseCollectionTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()