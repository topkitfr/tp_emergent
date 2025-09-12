#!/usr/bin/env python3
"""
TopKit Collection Workflow Bug Fix Testing
Testing the specific issue: "depuis la page dédiée à un maillot, je peux enfin cliquer sur le bouton 'j'ai ce maillot', 
le problème c'est que je ne le vois toujours pas dans 'ma collection'"

COMPLETE WORKFLOW TO TEST:
1. Jersey Creation & Approval Workflow
2. Collection Add Workflow  
3. Collection Retrieval Workflow
4. Collection Filtering (only approved jerseys)
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "https://footkit-admin.preview.emergentagent.com/api"

class CollectionWorkflowTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.admin_token = None
        self.admin_user_id = None
        self.test_jersey_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def setup_test_user(self):
        """Create a test user for collection testing"""
        try:
            unique_email = f"collectiontest_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "Collection Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("Setup Test User", "PASS", f"User created: {unique_email}")
                    return True
                else:
                    self.log_test("Setup Test User", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Setup Test User", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Setup Test User", "FAIL", f"Exception: {str(e)}")
            return False
    
    def setup_admin_user(self):
        """Setup admin user for jersey approval"""
        try:
            # Try to login with the known admin account
            admin_payload = {
                "email": "topkitfr@gmail.com",
                "password": "adminpass123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=admin_payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.admin_token = data["token"]
                    self.admin_user_id = data["user"]["id"]
                    self.log_test("Setup Admin User", "PASS", f"Admin logged in: {data['user']['email']}")
                    return True
                else:
                    self.log_test("Setup Admin User", "FAIL", "Missing token or user in admin response")
                    return False
            else:
                # Try to register admin if login fails
                admin_register_payload = {
                    "email": "topkitfr@gmail.com",
                    "password": "adminpass123",
                    "name": "TopKit Admin"
                }
                
                register_response = self.session.post(f"{self.base_url}/auth/register", json=admin_register_payload)
                
                if register_response.status_code == 200:
                    data = register_response.json()
                    self.admin_token = data["token"]
                    self.admin_user_id = data["user"]["id"]
                    self.log_test("Setup Admin User", "PASS", f"Admin registered: {data['user']['email']}")
                    return True
                else:
                    self.log_test("Setup Admin User", "FAIL", f"Admin setup failed: {register_response.status_code}")
                    return False
                
        except Exception as e:
            self.log_test("Setup Admin User", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_creation_workflow(self):
        """Test Step 1: Create a new jersey as regular user"""
        try:
            if not self.auth_token:
                self.log_test("Jersey Creation Workflow", "FAIL", "No auth token available")
                return False
            
            # Create a jersey with realistic data
            payload = {
                "team": "Paris Saint-Germain",
                "season": "2023-24",
                "player": "Kylian Mbappé",
                "size": "L",
                "condition": "very_good",  # Use valid condition from enum
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Ligue 1",
                "description": "Maillot PSG domicile 2023-24 avec flocage Mbappé #7, excellent état",
                "images": ["https://example.com/psg-mbappe-home.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_jersey_id = data["id"]
                    jersey_status = data.get("status", "unknown")
                    self.log_test("Jersey Creation Workflow", "PASS", 
                                f"Jersey created with ID: {self.test_jersey_id}, Status: {jersey_status}")
                    return True
                else:
                    self.log_test("Jersey Creation Workflow", "FAIL", "Missing jersey ID in response")
                    return False
            else:
                self.log_test("Jersey Creation Workflow", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Creation Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_approval_workflow(self):
        """Test Step 2: Approve the jersey as admin (crucial for collection visibility)"""
        try:
            if not self.admin_token or not self.test_jersey_id:
                self.log_test("Jersey Approval Workflow", "FAIL", "Missing admin token or jersey ID")
                return False
            
            # Switch to admin session
            admin_session = requests.Session()
            admin_session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.admin_token}'
            })
            
            # Approve the jersey
            response = admin_session.post(f"{self.base_url}/admin/jerseys/{self.test_jersey_id}/approve")
            
            if response.status_code == 200:
                # Verify jersey status is now "approved"
                jersey_response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}")
                
                if jersey_response.status_code == 200:
                    jersey_data = jersey_response.json()
                    jersey_status = jersey_data.get("status", "unknown")
                    approved_at = jersey_data.get("approved_at")
                    
                    if jersey_status == "approved" and approved_at:
                        self.log_test("Jersey Approval Workflow", "PASS", 
                                    f"Jersey approved successfully, Status: {jersey_status}, Approved at: {approved_at}")
                        return True
                    else:
                        self.log_test("Jersey Approval Workflow", "FAIL", 
                                    f"Jersey status not updated correctly: {jersey_status}")
                        return False
                else:
                    self.log_test("Jersey Approval Workflow", "FAIL", "Could not verify jersey status after approval")
                    return False
            else:
                self.log_test("Jersey Approval Workflow", "FAIL", f"Approval failed: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Approval Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_add_workflow(self):
        """Test Step 3: Add the approved jersey to user's 'owned' collection"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Collection Add Workflow", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Add jersey to owned collection
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                self.log_test("Collection Add Workflow", "PASS", 
                            f"Jersey added to collection: {response_data.get('message', 'Success')}")
                return True
            else:
                self.log_test("Collection Add Workflow", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collection Add Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_retrieval_workflow(self):
        """Test Step 4: CRITICAL - Verify the jersey appears in user's owned collection"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Collection Retrieval Workflow", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Fetch user's owned collection
            response = self.session.get(f"{self.base_url}/collections/owned")
            
            if response.status_code == 200:
                collections = response.json()
                
                # Look for our test jersey in the collection
                jersey_found = False
                jersey_data = None
                
                for collection_item in collections:
                    if collection_item.get("jersey_id") == self.test_jersey_id:
                        jersey_found = True
                        jersey_data = collection_item.get("jersey", {})
                        break
                
                if jersey_found:
                    # Verify the jersey data is complete
                    required_fields = ["team", "season", "player", "size", "condition", "status"]
                    missing_fields = [field for field in required_fields if not jersey_data.get(field)]
                    
                    if not missing_fields:
                        self.log_test("Collection Retrieval Workflow", "PASS", 
                                    f"✅ CRITICAL SUCCESS: Jersey found in collection! Team: {jersey_data.get('team')}, "
                                    f"Player: {jersey_data.get('player')}, Status: {jersey_data.get('status')}")
                        return True
                    else:
                        self.log_test("Collection Retrieval Workflow", "FAIL", 
                                    f"Jersey found but missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Collection Retrieval Workflow", "FAIL", 
                                f"❌ CRITICAL ISSUE: Jersey NOT found in collection! "
                                f"Collection has {len(collections)} items, but our jersey {self.test_jersey_id} is missing")
                    
                    # Debug: Show what's in the collection
                    if collections:
                        print("   DEBUG: Collection contents:")
                        for i, item in enumerate(collections[:3]):  # Show first 3 items
                            print(f"     Item {i+1}: jersey_id={item.get('jersey_id')}, team={item.get('jersey', {}).get('team', 'N/A')}")
                    else:
                        print("   DEBUG: Collection is empty")
                    
                    return False
            else:
                self.log_test("Collection Retrieval Workflow", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collection Retrieval Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_filtering_approved_only(self):
        """Test Step 5: Verify only approved jerseys appear in collections"""
        try:
            if not self.auth_token:
                self.log_test("Collection Filtering (Approved Only)", "FAIL", "No auth token available")
                return False
            
            # Create a pending jersey (not approved)
            pending_payload = {
                "team": "Manchester City",
                "season": "2023-24",
                "player": "Erling Haaland",
                "size": "M",
                "condition": "new",
                "manufacturer": "Puma",
                "home_away": "home",
                "league": "Premier League",
                "description": "Maillot Manchester City domicile avec Haaland #9",
                "images": ["https://example.com/city-haaland.jpg"]
            }
            
            pending_response = self.session.post(f"{self.base_url}/jerseys", json=pending_payload)
            
            if pending_response.status_code == 200:
                pending_jersey_id = pending_response.json()["id"]
                
                # Try to add pending jersey to collection
                collection_payload = {
                    "jersey_id": pending_jersey_id,
                    "collection_type": "owned"
                }
                
                add_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
                
                if add_response.status_code == 200:
                    # Check if pending jersey appears in collection (it shouldn't)
                    collection_response = self.session.get(f"{self.base_url}/collections/owned")
                    
                    if collection_response.status_code == 200:
                        collections = collection_response.json()
                        
                        # Check if pending jersey is in collection
                        pending_in_collection = any(
                            item.get("jersey_id") == pending_jersey_id 
                            for item in collections
                        )
                        
                        if not pending_in_collection:
                            self.log_test("Collection Filtering (Approved Only)", "PASS", 
                                        "✅ Pending jersey correctly excluded from collection view")
                            return True
                        else:
                            self.log_test("Collection Filtering (Approved Only)", "FAIL", 
                                        "❌ Pending jersey incorrectly appears in collection")
                            return False
                    else:
                        self.log_test("Collection Filtering (Approved Only)", "FAIL", "Could not fetch collection")
                        return False
                else:
                    self.log_test("Collection Filtering (Approved Only)", "FAIL", "Could not add pending jersey to collection")
                    return False
            else:
                self.log_test("Collection Filtering (Approved Only)", "FAIL", "Could not create pending jersey")
                return False
                
        except Exception as e:
            self.log_test("Collection Filtering (Approved Only)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_mongodb_aggregation_pipeline(self):
        """Test Step 6: Verify MongoDB aggregation pipeline works correctly"""
        try:
            if not self.auth_token:
                self.log_test("MongoDB Aggregation Pipeline", "FAIL", "No auth token available")
                return False
            
            # Test both collection types
            for collection_type in ["owned", "wanted"]:
                response = self.session.get(f"{self.base_url}/collections/{collection_type}")
                
                if response.status_code == 200:
                    collections = response.json()
                    
                    # Verify each collection item has proper jersey data
                    for collection_item in collections:
                        if "jersey" not in collection_item:
                            self.log_test("MongoDB Aggregation Pipeline", "FAIL", 
                                        f"Missing jersey data in {collection_type} collection item")
                            return False
                        
                        jersey = collection_item["jersey"]
                        if not jersey.get("id") or not jersey.get("team"):
                            self.log_test("MongoDB Aggregation Pipeline", "FAIL", 
                                        f"Incomplete jersey data in {collection_type} collection")
                            return False
                    
                    self.log_test(f"MongoDB Aggregation Pipeline ({collection_type})", "PASS", 
                                f"✅ {len(collections)} items with complete jersey data")
                else:
                    self.log_test("MongoDB Aggregation Pipeline", "FAIL", 
                                f"Failed to fetch {collection_type} collection: {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("MongoDB Aggregation Pipeline", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_id_matching(self):
        """Test Step 7: Verify jersey_id matching works between collections and jerseys tables"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Jersey ID Matching", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Get the jersey directly
            jersey_response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}")
            
            if jersey_response.status_code == 200:
                direct_jersey = jersey_response.json()
                
                # Get the jersey from collection
                collection_response = self.session.get(f"{self.base_url}/collections/owned")
                
                if collection_response.status_code == 200:
                    collections = collection_response.json()
                    
                    # Find our jersey in collection
                    collection_jersey = None
                    for item in collections:
                        if item.get("jersey_id") == self.test_jersey_id:
                            collection_jersey = item.get("jersey")
                            break
                    
                    if collection_jersey:
                        # Compare key fields
                        fields_to_compare = ["id", "team", "season", "player", "size", "condition"]
                        
                        for field in fields_to_compare:
                            direct_value = direct_jersey.get(field)
                            collection_value = collection_jersey.get(field)
                            
                            if direct_value != collection_value:
                                self.log_test("Jersey ID Matching", "FAIL", 
                                            f"Field mismatch for {field}: direct={direct_value}, collection={collection_value}")
                                return False
                        
                        self.log_test("Jersey ID Matching", "PASS", 
                                    "✅ Jersey data matches perfectly between direct fetch and collection lookup")
                        return True
                    else:
                        self.log_test("Jersey ID Matching", "FAIL", "Jersey not found in collection for comparison")
                        return False
                else:
                    self.log_test("Jersey ID Matching", "FAIL", "Could not fetch collection for comparison")
                    return False
            else:
                self.log_test("Jersey ID Matching", "FAIL", "Could not fetch jersey directly")
                return False
                
        except Exception as e:
            self.log_test("Jersey ID Matching", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_complete_collection_workflow_test(self):
        """Run the complete collection workflow test"""
        print("🧪 COLLECTION WORKFLOW BUG FIX TESTING")
        print("=" * 60)
        print("Testing the specific issue: User can click 'j'ai ce maillot' but doesn't see it in 'ma collection'")
        print()
        
        # Setup
        if not self.setup_test_user():
            return False
        
        if not self.setup_admin_user():
            return False
        
        # Test the complete workflow
        tests = [
            ("Step 1: Jersey Creation", self.test_jersey_creation_workflow),
            ("Step 2: Jersey Approval (Admin)", self.test_jersey_approval_workflow),
            ("Step 3: Collection Add", self.test_collection_add_workflow),
            ("Step 4: Collection Retrieval (CRITICAL)", self.test_collection_retrieval_workflow),
            ("Step 5: Collection Filtering", self.test_collection_filtering_approved_only),
            ("Step 6: MongoDB Pipeline", self.test_mongodb_aggregation_pipeline),
            ("Step 7: Jersey ID Matching", self.test_jersey_id_matching),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            if test_func():
                passed_tests += 1
            print()
        
        # Summary
        print("=" * 60)
        print(f"COLLECTION WORKFLOW TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Collection workflow bug fix is working correctly!")
            return True
        else:
            print(f"❌ {total_tests - passed_tests} tests failed - Collection workflow needs attention")
            return False

def main():
    """Main test execution"""
    tester = CollectionWorkflowTester()
    success = tester.run_complete_collection_workflow_test()
    
    if success:
        print("\n✅ CONCLUSION: The collection workflow bug fix is working correctly.")
        print("Users should now be able to see jerseys in their collection after adding them.")
    else:
        print("\n❌ CONCLUSION: Collection workflow issues detected.")
        print("The bug fix may need additional work to resolve the collection visibility issue.")

if __name__ == "__main__":
    main()