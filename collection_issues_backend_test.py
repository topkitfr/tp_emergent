#!/usr/bin/env python3
"""
TopKit Collection Issues Testing
Testing the collection problems identified by user:
- PROBLÈME 1: Les références ajoutées à la collection ne sont pas visibles
- PROBLÈME 2: Pas de message de confirmation lors de l'ajout
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"

# Test credentials as specified in review request
TEST_USER = {
    "email": "friendstest2@example.com",
    "password": "TestFriends9!$"
}

class CollectionIssuesTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.user_id = None
        self.test_jersey_id = None
        
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
                self.auth_token = data.get('token')
                user_data = data.get('user', {})
                self.user_id = user_data.get('id')
                
                self.log_result(
                    "User Authentication",
                    True,
                    f"Successfully authenticated user: {user_data.get('name')} (ID: {self.user_id})"
                )
                
                # Set authorization header for future requests
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                return True
            else:
                self.log_result(
                    "User Authentication", 
                    False, 
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, "", str(e))
            return False
    
    def get_or_create_test_jersey(self):
        """Get existing jersey or create one for testing"""
        try:
            # First, try to get existing jerseys
            response = self.session.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                if jerseys and len(jerseys) > 0:
                    # Use first available jersey
                    self.test_jersey_id = jerseys[0]['id']
                    jersey_info = f"{jerseys[0].get('team', 'Unknown')} - {jerseys[0].get('season', 'Unknown')}"
                    self.log_result(
                        "Get Test Jersey",
                        True,
                        f"Using existing jersey: {jersey_info} (ID: {self.test_jersey_id})"
                    )
                    return True
                else:
                    # Create a test jersey if none exist
                    return self.create_test_jersey()
            else:
                self.log_result(
                    "Get Test Jersey",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Get Test Jersey", False, "", str(e))
            return False
    
    def create_test_jersey(self):
        """Create a test jersey for collection testing"""
        try:
            jersey_data = {
                "team": "FC Barcelona",
                "season": "2024-25",
                "player": "Pedri",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for collection functionality"
            }
            
            response = self.session.post(f"{BACKEND_URL}/jerseys", json=jersey_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_jersey_id = data.get('id')
                self.log_result(
                    "Create Test Jersey",
                    True,
                    f"Created test jersey: {jersey_data['team']} - {jersey_data['season']} (ID: {self.test_jersey_id})"
                )
                return True
            else:
                self.log_result(
                    "Create Test Jersey",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Create Test Jersey", False, "", str(e))
            return False
    
    def test_add_to_collection_owned(self):
        """Test adding jersey to 'owned' collection - PROBLÈME 1 & 2"""
        try:
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "very_good",
                "personal_description": "Test jersey added to owned collection"
            }
            
            response = self.session.post(f"{BACKEND_URL}/collections", json=collection_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for confirmation message (PROBLÈME 2)
                message = data.get('message', '')
                has_confirmation = bool(message and 'ajouté' in message.lower())
                
                self.log_result(
                    "Add to Owned Collection - API Response",
                    True,
                    f"Jersey added successfully. Response: {json.dumps(data, indent=2)}"
                )
                
                self.log_result(
                    "Add to Collection - Confirmation Message",
                    has_confirmation,
                    f"Confirmation message: '{message}'" if message else "No confirmation message found",
                    "Missing confirmation message" if not has_confirmation else ""
                )
                
                return True
            else:
                self.log_result(
                    "Add to Owned Collection - API Response",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Add to Owned Collection - API Response", False, "", str(e))
            return False
    
    def test_add_to_collection_wanted(self):
        """Test adding jersey to 'wanted' collection"""
        try:
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted",
                "size": "L",
                "condition": "new",
                "personal_description": "Test jersey added to wanted collection"
            }
            
            response = self.session.post(f"{BACKEND_URL}/collections", json=collection_data)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                has_confirmation = bool(message and 'ajouté' in message.lower())
                
                self.log_result(
                    "Add to Wanted Collection - API Response",
                    True,
                    f"Jersey added to wanted collection. Response: {json.dumps(data, indent=2)}"
                )
                
                self.log_result(
                    "Add to Wanted Collection - Confirmation Message",
                    has_confirmation,
                    f"Confirmation message: '{message}'" if message else "No confirmation message found",
                    "Missing confirmation message" if not has_confirmation else ""
                )
                
                return True
            else:
                self.log_result(
                    "Add to Wanted Collection - API Response",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Add to Wanted Collection - API Response", False, "", str(e))
            return False
    
    def test_retrieve_user_collections(self):
        """Test retrieving user collections - PROBLÈME 1"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{self.user_id}/collections")
            
            if response.status_code == 200:
                collections = response.json()
                
                self.log_result(
                    "Retrieve User Collections - API Response",
                    True,
                    f"Retrieved {len(collections)} collection items"
                )
                
                # Check if added jerseys are visible (PROBLÈME 1)
                owned_items = [item for item in collections if item.get('collection_type') == 'owned']
                wanted_items = [item for item in collections if item.get('collection_type') == 'wanted']
                
                # Check for our test jersey in collections
                test_jersey_in_owned = any(item.get('jersey_id') == self.test_jersey_id for item in owned_items)
                test_jersey_in_wanted = any(item.get('jersey_id') == self.test_jersey_id for item in wanted_items)
                
                self.log_result(
                    "Collection Visibility - Owned Items",
                    test_jersey_in_owned,
                    f"Found {len(owned_items)} owned items. Test jersey visible: {test_jersey_in_owned}",
                    "Test jersey not found in owned collection" if not test_jersey_in_owned else ""
                )
                
                self.log_result(
                    "Collection Visibility - Wanted Items", 
                    test_jersey_in_wanted,
                    f"Found {len(wanted_items)} wanted items. Test jersey visible: {test_jersey_in_wanted}",
                    "Test jersey not found in wanted collection" if not test_jersey_in_wanted else ""
                )
                
                # Verify data structure for frontend compatibility
                self.verify_collection_data_structure(collections)
                
                return True
            else:
                self.log_result(
                    "Retrieve User Collections - API Response",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Retrieve User Collections - API Response", False, "", str(e))
            return False
    
    def verify_collection_data_structure(self, collections):
        """Verify that collection data structure matches frontend expectations"""
        try:
            structure_issues = []
            
            for i, item in enumerate(collections):
                # Check required fields
                required_fields = ['id', 'user_id', 'jersey_id', 'collection_type', 'added_at']
                missing_fields = [field for field in required_fields if field not in item]
                
                if missing_fields:
                    structure_issues.append(f"Item {i}: Missing fields {missing_fields}")
                
                # Check jersey data structure if present
                if 'jersey' in item:
                    jersey = item['jersey']
                    jersey_required_fields = ['team', 'league', 'season']
                    jersey_missing_fields = [field for field in jersey_required_fields if field not in jersey]
                    
                    if jersey_missing_fields:
                        structure_issues.append(f"Item {i} jersey: Missing fields {jersey_missing_fields}")
                else:
                    structure_issues.append(f"Item {i}: No jersey data populated")
            
            if structure_issues:
                self.log_result(
                    "Collection Data Structure Verification",
                    False,
                    f"Found {len(structure_issues)} structure issues",
                    "; ".join(structure_issues)
                )
            else:
                self.log_result(
                    "Collection Data Structure Verification",
                    True,
                    f"All {len(collections)} collection items have proper data structure"
                )
                
        except Exception as e:
            self.log_result("Collection Data Structure Verification", False, "", str(e))
    
    def test_collection_with_jersey_details(self):
        """Test collection endpoint that includes jersey details"""
        try:
            # Try different collection endpoints to find one with jersey details
            endpoints_to_test = [
                f"/users/{self.user_id}/collections",
                f"/collections/my-owned",
                f"/collections/my-wanted"
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if jersey details are populated
                        has_jersey_details = False
                        if isinstance(data, list) and data:
                            for item in data:
                                if 'jersey' in item and isinstance(item['jersey'], dict):
                                    jersey = item['jersey']
                                    if jersey.get('team') and jersey.get('league') and jersey.get('season'):
                                        has_jersey_details = True
                                        break
                        
                        self.log_result(
                            f"Collection with Jersey Details - {endpoint}",
                            has_jersey_details,
                            f"Endpoint returned {len(data) if isinstance(data, list) else 'non-list'} items. Jersey details populated: {has_jersey_details}",
                            "Jersey details not properly populated" if not has_jersey_details else ""
                        )
                        
                        if has_jersey_details:
                            # Log sample jersey data structure
                            sample_jersey = next((item['jersey'] for item in data if 'jersey' in item), {})
                            self.log_result(
                                "Sample Jersey Data Structure",
                                True,
                                f"Sample jersey fields: {list(sample_jersey.keys())}"
                            )
                    else:
                        self.log_result(
                            f"Collection with Jersey Details - {endpoint}",
                            False,
                            f"HTTP {response.status_code}",
                            response.text
                        )
                        
                except Exception as e:
                    self.log_result(f"Collection with Jersey Details - {endpoint}", False, "", str(e))
                    
        except Exception as e:
            self.log_result("Collection with Jersey Details", False, "", str(e))
    
    def run_all_tests(self):
        """Run all collection issue tests"""
        print("🧪 Starting TopKit Collection Issues Testing")
        print("=" * 60)
        
        # Step 1: Authenticate user
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Step 2: Get or create test jersey
        if not self.get_or_create_test_jersey():
            print("❌ Could not get test jersey - cannot proceed with collection tests")
            return
        
        # Step 3: Test adding to owned collection (PROBLÈME 1 & 2)
        print("\n📝 Testing Add to Owned Collection...")
        self.test_add_to_collection_owned()
        
        # Step 4: Test adding to wanted collection
        print("\n📝 Testing Add to Wanted Collection...")
        self.test_add_to_collection_wanted()
        
        # Step 5: Test retrieving collections (PROBLÈME 1)
        print("\n📝 Testing Collection Retrieval...")
        self.test_retrieve_user_collections()
        
        # Step 6: Test collection endpoints with jersey details
        print("\n📝 Testing Collection Endpoints with Jersey Details...")
        self.test_collection_with_jersey_details()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 COLLECTION ISSUES TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Highlight critical issues
        print("\n🔍 CRITICAL FINDINGS:")
        
        # PROBLÈME 1: Collection visibility
        visibility_tests = [r for r in self.test_results if 'Collection Visibility' in r['test']]
        if any(not r['success'] for r in visibility_tests):
            print("❌ PROBLÈME 1 CONFIRMED: Les références ajoutées à la collection ne sont pas visibles")
        else:
            print("✅ PROBLÈME 1 RESOLVED: Collection items are visible")
        
        # PROBLÈME 2: Confirmation messages
        confirmation_tests = [r for r in self.test_results if 'Confirmation Message' in r['test']]
        if any(not r['success'] for r in confirmation_tests):
            print("❌ PROBLÈME 2 CONFIRMED: Pas de message de confirmation lors de l'ajout")
        else:
            print("✅ PROBLÈME 2 RESOLVED: Confirmation messages are present")
        
        # Data structure issues
        structure_tests = [r for r in self.test_results if 'Data Structure' in r['test']]
        if any(not r['success'] for r in structure_tests):
            print("❌ DATA STRUCTURE ISSUE: Collection data structure problems detected")
        else:
            print("✅ DATA STRUCTURE OK: Collection data structure is correct")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['error']:
                print(f"   Error: {result['error']}")

if __name__ == "__main__":
    tester = CollectionIssuesTester()
    tester.run_all_tests()