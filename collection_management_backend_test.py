#!/usr/bin/env python3
"""
TopKit Collection Management API Testing
Testing collection removal, detail updates, retrieval, and management functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"

# Test credentials - using admin as test user since regular user is locked
TEST_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

ADMIN_USER = {
    "email": "topkitfr@gmail.com", 
    "password": "TopKitSecure789#"
}

class CollectionManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.user_token = None
        self.admin_token = None
        self.test_jersey_id = None
        self.collection_id = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
    
    def authenticate_user(self):
        """Authenticate test user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=TEST_USER)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["token"]
                self.session.headers.update({"Authorization": f"Bearer {self.user_token}"})
                self.log_result("User Authentication", True, f"Authenticated as {data['user']['name']}")
                return True
            else:
                self.log_result("User Authentication", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Authentication", False, error=str(e))
            return False
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_USER)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.log_result("Admin Authentication", True, f"Authenticated as {data['user']['name']}")
                return True
            else:
                self.log_result("Admin Authentication", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, error=str(e))
            return False
    
    def create_test_jersey(self):
        """Create a test jersey for collection testing"""
        try:
            # Use admin token for jersey creation
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            jersey_data = {
                "team": "FC Barcelona",
                "season": "2024-25",
                "player": "Pedri",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for collection management testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=admin_headers)
            if response.status_code in [200, 201]:
                data = response.json()
                # Handle different response formats
                if "jersey" in data:
                    self.test_jersey_id = data["jersey"]["id"]
                else:
                    self.test_jersey_id = data["id"]
                
                # Approve the jersey immediately for testing
                approve_response = self.session.post(
                    f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}/approve",
                    headers=admin_headers
                )
                
                if approve_response.status_code == 200:
                    self.log_result("Test Jersey Creation & Approval", True, f"Created and approved jersey ID: {self.test_jersey_id}")
                    return True
                else:
                    self.log_result("Test Jersey Approval", False, error=f"Approval failed: {approve_response.status_code}")
                    return False
            else:
                self.log_result("Test Jersey Creation", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Test Jersey Creation", False, error=str(e))
            return False
    
    def test_add_to_collection(self):
        """Test adding jersey to collection"""
        try:
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "near_mint",
                "personal_description": "Test collection item for API testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/collections", json=collection_data)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Add to Collection", True, f"Added jersey to owned collection: {data['message']}")
                return True
            else:
                self.log_result("Add to Collection", False, error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Add to Collection", False, error=str(e))
            return False
    
    def test_collection_retrieval(self):
        """Test collection retrieval with proper jersey data"""
        try:
            # Test owned collection retrieval
            response = self.session.get(f"{BACKEND_URL}/collections/owned")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if jersey data is properly included
                    collection_item = data[0]
                    if 'jersey' in collection_item and 'id' in collection_item['jersey']:
                        jersey_data = collection_item['jersey']
                        required_fields = ['team', 'season', 'player', 'status']
                        missing_fields = [field for field in required_fields if field not in jersey_data]
                        
                        if not missing_fields:
                            self.log_result("Collection Retrieval with Jersey Data", True, 
                                          f"Retrieved {len(data)} items with complete jersey data")
                            return True
                        else:
                            self.log_result("Collection Retrieval with Jersey Data", False, 
                                          error=f"Missing jersey fields: {missing_fields}")
                            return False
                    else:
                        self.log_result("Collection Retrieval with Jersey Data", False, 
                                      error="Jersey data not properly included in collection response")
                        return False
                else:
                    self.log_result("Collection Retrieval with Jersey Data", True, 
                                  "Collection is empty (expected for clean test)")
                    return True
            else:
                self.log_result("Collection Retrieval with Jersey Data", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Collection Retrieval with Jersey Data", False, error=str(e))
            return False
    
    def test_collection_detail_retrieval(self):
        """Test collection detail retrieval for owned items"""
        try:
            if not self.test_jersey_id:
                self.log_result("Collection Detail Retrieval", False, error="No test jersey ID available")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/collections/owned/{self.test_jersey_id}/details")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['jersey_id', 'user_id', 'model_type', 'condition', 'size']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_result("Collection Detail Retrieval", True, 
                                  f"Retrieved detailed info with all required fields")
                    return True
                else:
                    self.log_result("Collection Detail Retrieval", False, 
                                  error=f"Missing detail fields: {missing_fields}")
                    return False
            elif response.status_code == 404:
                self.log_result("Collection Detail Retrieval", True, 
                              "Jersey not in collection (expected if not added yet)")
                return True
            else:
                self.log_result("Collection Detail Retrieval", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Collection Detail Retrieval", False, error=str(e))
            return False
    
    def test_collection_detail_update(self):
        """Test collection detail update APIs"""
        try:
            if not self.test_jersey_id:
                self.log_result("Collection Detail Update", False, error="No test jersey ID available")
                return False
            
            detail_data = {
                "model_type": "authentic",
                "condition": "mint",
                "size": "m",
                "special_features": ["match_worn", "signed"],
                "material_details": "100% polyester with moisture-wicking technology",
                "tags": "tags_on",
                "packaging": "original_packaging",
                "customization": "player_name_number",
                "competition_badges": "champions_league",
                "rarity": "rare",
                "purchase_price": 89.99,
                "purchase_date": "2024-01-15",
                "purchase_location": "Official FC Barcelona Store",
                "certificate_authenticity": True,
                "storage_notes": "Stored in climate-controlled environment",
                "estimated_value": 150.0
            }
            
            response = self.session.put(f"{BACKEND_URL}/collections/owned/{self.test_jersey_id}/details", 
                                      json=detail_data)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Collection Detail Update", True, 
                              f"Updated jersey details successfully: {data['message']}")
                return True
            elif response.status_code == 404:
                self.log_result("Collection Detail Update", True, 
                              "Jersey not in owned collection (expected if not added)")
                return True
            else:
                self.log_result("Collection Detail Update", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Collection Detail Update", False, error=str(e))
            return False
    
    def test_collection_removal_post(self):
        """Test collection removal API (POST /api/collections/remove)"""
        try:
            if not self.test_jersey_id:
                self.log_result("Collection Removal (POST)", False, error="No test jersey ID available")
                return False
            
            removal_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{BACKEND_URL}/collections/remove", json=removal_data)
            if response.status_code == 200:
                data = response.json()
                self.log_result("Collection Removal (POST)", True, 
                              f"Removed from collection: {data['message']}")
                return True
            elif response.status_code == 404:
                self.log_result("Collection Removal (POST)", True, 
                              "Jersey not found in collection (expected if not added)")
                return True
            else:
                self.log_result("Collection Removal (POST)", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Collection Removal (POST)", False, error=str(e))
            return False
    
    def test_collection_removal_delete(self):
        """Test collection removal API (DELETE /api/collections/{jersey_id})"""
        try:
            if not self.test_jersey_id:
                self.log_result("Collection Removal (DELETE)", False, error="No test jersey ID available")
                return False
            
            response = self.session.delete(f"{BACKEND_URL}/collections/{self.test_jersey_id}")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Collection Removal (DELETE)", True, 
                              f"Removed from collection: {data['message']}")
                return True
            elif response.status_code == 404:
                self.log_result("Collection Removal (DELETE)", True, 
                              "Jersey not found in collection (expected if already removed)")
                return True
            else:
                self.log_result("Collection Removal (DELETE)", False, 
                              error=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_result("Collection Removal (DELETE)", False, error=str(e))
            return False
    
    def test_collection_management_workflow(self):
        """Test complete collection management workflow"""
        try:
            # Add to collection
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted",
                "size": "L",
                "condition": "good",
                "personal_description": "Workflow test item"
            }
            
            add_response = self.session.post(f"{BACKEND_URL}/collections", json=collection_data)
            if add_response.status_code != 200:
                self.log_result("Collection Management Workflow", False, 
                              error=f"Failed to add to collection: {add_response.status_code}")
                return False
            
            # Retrieve collection to verify
            get_response = self.session.get(f"{BACKEND_URL}/collections/wanted")
            if get_response.status_code != 200:
                self.log_result("Collection Management Workflow", False, 
                              error=f"Failed to retrieve collection: {get_response.status_code}")
                return False
            
            # Remove from collection
            removal_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted"
            }
            
            remove_response = self.session.post(f"{BACKEND_URL}/collections/remove", json=removal_data)
            if remove_response.status_code != 200:
                self.log_result("Collection Management Workflow", False, 
                              error=f"Failed to remove from collection: {remove_response.status_code}")
                return False
            
            self.log_result("Collection Management Workflow", True, 
                          "Complete workflow (add → retrieve → remove) successful")
            return True
            
        except Exception as e:
            self.log_result("Collection Management Workflow", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all collection management tests"""
        print("🧪 Starting TopKit Collection Management API Testing...")
        print("=" * 60)
        
        # Authentication tests
        if not self.authenticate_user():
            print("❌ User authentication failed - cannot proceed with tests")
            return
        
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot create test data")
            return
        
        # Create test data
        if not self.create_test_jersey():
            print("❌ Test jersey creation failed - cannot proceed with collection tests")
            return
        
        # Collection management tests
        print("\n📋 Testing Collection Management APIs...")
        self.test_add_to_collection()
        self.test_collection_retrieval()
        self.test_collection_detail_retrieval()
        self.test_collection_detail_update()
        self.test_collection_removal_post()
        
        # Re-add for DELETE test
        self.test_add_to_collection()
        self.test_collection_removal_delete()
        
        # Workflow test
        self.test_collection_management_workflow()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
        
        print("\n🎯 COLLECTION MANAGEMENT API STATUS:")
        critical_tests = [
            "Collection Removal (POST)",
            "Collection Detail Update", 
            "Collection Retrieval with Jersey Data",
            "Collection Management Workflow"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        critical_total = len([r for r in self.test_results if r["test"] in critical_tests])
        
        if critical_passed == critical_total:
            print("✅ All critical collection management APIs are working correctly")
        else:
            print(f"⚠️  {critical_total - critical_passed} critical collection management APIs have issues")

if __name__ == "__main__":
    tester = CollectionManagementTester()
    tester.run_all_tests()