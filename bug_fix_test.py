#!/usr/bin/env python3
"""
TopKit Bug Fix Testing - Specific tests for recent bug fixes
Testing jersey condition bug fix and collection management bug fix
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "https://footkit-admin.preview.emergentagent.com/api"

# Test accounts as specified in review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"
# Use unique email for test user to avoid conflicts
TEST_EMAIL = f"testuser_{int(time.time())}@example.com"
TEST_PASSWORD = "testpass123"

class BugFixTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.test_token = None
        self.admin_user_id = None
        self.test_user_id = None
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
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.admin_token = data["token"]
                    self.admin_user_id = data["user"]["id"]
                    self.log_test("Admin Authentication", "PASS", f"Admin logged in: {ADMIN_EMAIL}")
                    return True
                else:
                    self.log_test("Admin Authentication", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Admin Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def authenticate_test_user(self):
        """Authenticate as test user - register new user"""
        try:
            # Register a new test user
            register_payload = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "Bug Fix Test User"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code == 200:
                data = register_response.json()
                if "token" in data and "user" in data:
                    self.test_token = data["token"]
                    self.test_user_id = data["user"]["id"]
                    self.log_test("Test User Authentication", "PASS", f"Test user registered: {TEST_EMAIL}")
                    return True
                else:
                    self.log_test("Test User Authentication", "FAIL", "Missing token or user in registration response")
                    return False
            else:
                self.log_test("Test User Authentication", "FAIL", f"Registration failed: {register_response.status_code}, Response: {register_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test User Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_condition_new(self):
        """Test jersey submission with condition 'new' - should now work"""
        try:
            if not self.test_token:
                self.log_test("Jersey Condition 'new'", "FAIL", "No test user token available")
                return False
            
            # Set auth header for test user
            headers = {'Authorization': f'Bearer {self.test_token}'}
            
            payload = {
                "team": "Real Madrid",
                "season": "2024-25",
                "player": "Kylian Mbappé",
                "size": "L",
                "condition": "new",  # This should now work
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Brand new Real Madrid home jersey with Mbappé #9, still with tags",
                "images": ["https://example.com/realmadrid-mbappe.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("condition") == "new":
                    self.test_jersey_id = data["id"]
                    self.log_test("Jersey Condition 'new'", "PASS", f"Jersey created with 'new' condition: {data['id']}")
                    return True
                else:
                    self.log_test("Jersey Condition 'new'", "FAIL", "Jersey created but condition not set correctly")
                    return False
            else:
                self.log_test("Jersey Condition 'new'", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Condition 'new'", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_condition_all_values(self):
        """Test all jersey condition values: new, near_mint, very_good, good, poor"""
        try:
            if not self.test_token:
                self.log_test("All Jersey Conditions", "FAIL", "No test user token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.test_token}'}
            conditions = ["new", "near_mint", "very_good", "good", "poor"]
            results = []
            
            for condition in conditions:
                payload = {
                    "team": "Manchester City",
                    "season": "2024-25",
                    "player": "Erling Haaland",
                    "size": "M",
                    "condition": condition,
                    "manufacturer": "Puma",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": f"Manchester City jersey in {condition} condition",
                    "images": ["https://example.com/mancity-haaland.jpg"]
                }
                
                response = self.session.post(f"{self.base_url}/jerseys", json=payload, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("condition") == condition:
                        results.append(f"✅ {condition}")
                    else:
                        results.append(f"❌ {condition} (wrong value returned)")
                else:
                    results.append(f"❌ {condition} (status: {response.status_code})")
            
            success_count = len([r for r in results if r.startswith("✅")])
            
            if success_count == len(conditions):
                self.log_test("All Jersey Conditions", "PASS", f"All conditions accepted: {', '.join(results)}")
                return True
            else:
                self.log_test("All Jersey Conditions", "FAIL", f"Some conditions failed: {', '.join(results)}")
                return False
                
        except Exception as e:
            self.log_test("All Jersey Conditions", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_add_endpoint(self):
        """Test adding to collection using POST /api/collections"""
        try:
            if not self.test_token or not self.test_jersey_id:
                self.log_test("Collection Add Endpoint", "FAIL", "Missing test token or jersey ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.test_token}'}
            
            # Test adding to owned collection
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "added" in data["message"].lower():
                    self.log_test("Collection Add Endpoint (Owned)", "PASS", "Jersey added to owned collection")
                    
                    # Test adding to wanted collection
                    payload["collection_type"] = "wanted"
                    wanted_response = self.session.post(f"{self.base_url}/collections", json=payload, headers=headers)
                    
                    if wanted_response.status_code == 200:
                        wanted_data = wanted_response.json()
                        if "message" in wanted_data and "added" in wanted_data["message"].lower():
                            self.log_test("Collection Add Endpoint (Wanted)", "PASS", "Jersey added to wanted collection")
                            return True
                        else:
                            self.log_test("Collection Add Endpoint (Wanted)", "FAIL", f"Unexpected response: {wanted_data}")
                            return False
                    else:
                        self.log_test("Collection Add Endpoint (Wanted)", "FAIL", f"Status: {wanted_response.status_code}")
                        return False
                else:
                    self.log_test("Collection Add Endpoint (Owned)", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Collection Add Endpoint (Owned)", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collection Add Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_remove_endpoint(self):
        """Test the new POST /api/collections/remove endpoint"""
        try:
            if not self.test_token or not self.test_jersey_id:
                self.log_test("Collection Remove Endpoint", "FAIL", "Missing test token or jersey ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.test_token}'}
            
            # Test removing from owned collection
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections/remove", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "removed" in data["message"].lower():
                    self.log_test("Collection Remove Endpoint (Owned)", "PASS", "Jersey removed from owned collection")
                    
                    # Test removing from wanted collection
                    payload["collection_type"] = "wanted"
                    wanted_response = self.session.post(f"{self.base_url}/collections/remove", json=payload, headers=headers)
                    
                    if wanted_response.status_code == 200:
                        wanted_data = wanted_response.json()
                        if "message" in wanted_data and "removed" in wanted_data["message"].lower():
                            self.log_test("Collection Remove Endpoint (Wanted)", "PASS", "Jersey removed from wanted collection")
                            return True
                        else:
                            self.log_test("Collection Remove Endpoint (Wanted)", "FAIL", f"Unexpected response: {wanted_data}")
                            return False
                    else:
                        self.log_test("Collection Remove Endpoint (Wanted)", "FAIL", f"Status: {wanted_response.status_code}")
                        return False
                else:
                    self.log_test("Collection Remove Endpoint (Owned)", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Collection Remove Endpoint (Owned)", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collection Remove Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_management_workflow(self):
        """Test complete collection add/remove workflow"""
        try:
            if not self.test_token or not self.test_jersey_id:
                self.log_test("Collection Management Workflow", "FAIL", "Missing test token or jersey ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.test_token}'}
            
            # Step 1: Add to owned collection
            add_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=add_payload, headers=headers)
            
            if add_response.status_code != 200:
                self.log_test("Collection Management Workflow", "FAIL", f"Add failed: {add_response.status_code}")
                return False
            
            # Step 2: Verify it's in collection
            owned_response = self.session.get(f"{self.base_url}/collections/owned", headers=headers)
            
            if owned_response.status_code != 200:
                self.log_test("Collection Management Workflow", "FAIL", f"Get owned failed: {owned_response.status_code}")
                return False
            
            owned_collection = owned_response.json()
            jersey_in_owned = any(item.get('jersey_id') == self.test_jersey_id for item in owned_collection)
            
            if not jersey_in_owned:
                self.log_test("Collection Management Workflow", "FAIL", "Jersey not found in owned collection after adding")
                return False
            
            # Step 3: Remove using new endpoint
            remove_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            remove_response = self.session.post(f"{self.base_url}/collections/remove", json=remove_payload, headers=headers)
            
            if remove_response.status_code != 200:
                self.log_test("Collection Management Workflow", "FAIL", f"Remove failed: {remove_response.status_code}")
                return False
            
            # Step 4: Verify it's removed
            owned_after_response = self.session.get(f"{self.base_url}/collections/owned", headers=headers)
            
            if owned_after_response.status_code != 200:
                self.log_test("Collection Management Workflow", "FAIL", f"Get owned after remove failed: {owned_after_response.status_code}")
                return False
            
            owned_after = owned_after_response.json()
            jersey_still_in_owned = any(item.get('jersey_id') == self.test_jersey_id for item in owned_after)
            
            if jersey_still_in_owned:
                self.log_test("Collection Management Workflow", "FAIL", "Jersey still in owned collection after removal")
                return False
            
            self.log_test("Collection Management Workflow", "PASS", "Complete add/remove workflow successful")
            return True
                
        except Exception as e:
            self.log_test("Collection Management Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_existing_endpoints_still_work(self):
        """Test that existing endpoints still work correctly"""
        try:
            # Test GET /api/jerseys
            jerseys_response = self.session.get(f"{self.base_url}/jerseys")
            
            if jerseys_response.status_code != 200:
                self.log_test("Existing Endpoints - Get Jerseys", "FAIL", f"Status: {jerseys_response.status_code}")
                return False
            
            jerseys = jerseys_response.json()
            self.log_test("Existing Endpoints - Get Jerseys", "PASS", f"Retrieved {len(jerseys)} jerseys")
            
            # Test GET /api/listings
            listings_response = self.session.get(f"{self.base_url}/listings")
            
            if listings_response.status_code != 200:
                self.log_test("Existing Endpoints - Get Listings", "FAIL", f"Status: {listings_response.status_code}")
                return False
            
            listings = listings_response.json()
            self.log_test("Existing Endpoints - Get Listings", "PASS", f"Retrieved {len(listings)} listings")
            
            return True
                
        except Exception as e:
            self.log_test("Existing Endpoints", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_approval_workflow(self):
        """Test jersey creation and approval workflow"""
        try:
            if not self.admin_token or not self.test_jersey_id:
                self.log_test("Jersey Approval Workflow", "FAIL", "Missing admin token or jersey ID")
                return False
            
            admin_headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            # Step 1: Get pending jerseys
            pending_response = self.session.get(f"{self.base_url}/admin/jerseys/pending", headers=admin_headers)
            
            if pending_response.status_code != 200:
                self.log_test("Jersey Approval Workflow", "FAIL", f"Get pending failed: {pending_response.status_code}")
                return False
            
            pending_jerseys = pending_response.json()
            
            # Find our test jersey
            test_jersey = None
            for jersey in pending_jerseys:
                if jersey.get('id') == self.test_jersey_id:
                    test_jersey = jersey
                    break
            
            if not test_jersey:
                self.log_test("Jersey Approval Workflow", "FAIL", "Test jersey not found in pending list")
                return False
            
            # Step 2: Approve the jersey
            approve_response = self.session.post(f"{self.base_url}/admin/jerseys/{self.test_jersey_id}/approve", headers=admin_headers)
            
            if approve_response.status_code != 200:
                self.log_test("Jersey Approval Workflow", "FAIL", f"Approval failed: {approve_response.status_code}")
                return False
            
            # Step 3: Verify jersey is now in public list
            public_response = self.session.get(f"{self.base_url}/jerseys")
            
            if public_response.status_code != 200:
                self.log_test("Jersey Approval Workflow", "FAIL", f"Get public jerseys failed: {public_response.status_code}")
                return False
            
            public_jerseys = public_response.json()
            approved_jersey = None
            for jersey in public_jerseys:
                if jersey.get('id') == self.test_jersey_id:
                    approved_jersey = jersey
                    break
            
            if approved_jersey:
                self.log_test("Jersey Approval Workflow", "PASS", "Jersey successfully approved and visible publicly")
                return True
            else:
                self.log_test("Jersey Approval Workflow", "FAIL", "Approved jersey not found in public list")
                return False
                
        except Exception as e:
            self.log_test("Jersey Approval Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all bug fix tests"""
        print("🧪 TOPKIT BUG FIX TESTING - SPECIFIC FIXES VERIFICATION")
        print("=" * 60)
        print()
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        if not self.authenticate_test_user():
            print("❌ Cannot proceed without test user authentication")
            return
        
        print("🔧 TESTING BUG FIX #1: Jersey Condition 'new' Support")
        print("-" * 50)
        
        # Test jersey condition bug fix
        self.test_jersey_condition_new()
        self.test_jersey_condition_all_values()
        
        print()
        print("🔧 TESTING BUG FIX #2: Collection Management Endpoints")
        print("-" * 50)
        
        # Test collection management bug fix
        self.test_collection_add_endpoint()
        self.test_collection_remove_endpoint()
        self.test_collection_management_workflow()
        
        print()
        print("🔧 TESTING BUG FIX #3: General API Health")
        print("-" * 50)
        
        # Test general API health
        self.test_existing_endpoints_still_work()
        self.test_jersey_approval_workflow()
        
        print()
        print("✅ BUG FIX TESTING COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    tester = BugFixTester()
    tester.run_all_tests()