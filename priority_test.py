#!/usr/bin/env python3
"""
TopKit Priority Testing - Focus on Collection Delete and Jersey Update
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://footkit-admin.preview.emergentagent.com/api"
TEST_USER_EMAIL = "prioritytest@topkit.com"
TEST_USER_PASSWORD = "SecurePass123!"
TEST_USER_NAME = "Priority Test User"

class PriorityTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
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
    
    def setup_auth(self):
        """Setup authentication for testing"""
        try:
            # Use unique email to avoid conflicts
            unique_email = f"prioritytest_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("Setup Authentication", "PASS", f"User registered with ID: {self.user_id}")
                    return True
                else:
                    self.log_test("Setup Authentication", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Setup Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Setup Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def setup_test_jersey(self):
        """Create a test jersey for testing"""
        try:
            if not self.auth_token:
                self.log_test("Setup Test Jersey", "FAIL", "No auth token available")
                return False
            
            payload = {
                "team": "Chelsea FC",
                "season": "2023-24",
                "player": "Enzo Fernandez",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Chelsea FC home jersey with Enzo Fernandez #5",
                "images": ["https://example.com/chelsea-enzo.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_jersey_id = data["id"]
                    self.log_test("Setup Test Jersey", "PASS", f"Jersey created with ID: {self.test_jersey_id}")
                    return True
                else:
                    self.log_test("Setup Test Jersey", "FAIL", "Missing jersey ID in response")
                    return False
            else:
                self.log_test("Setup Test Jersey", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Setup Test Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_delete_functionality(self):
        """Test PRIORITY 1: Collection Delete Functionality"""
        print("🎯 PRIORITY 1: COLLECTION DELETE FUNCTIONALITY TESTING")
        print("=" * 60)
        
        if not self.auth_token or not self.test_jersey_id:
            self.log_test("Collection Delete Setup", "FAIL", "Missing auth token or jersey ID")
            return False
        
        # Step 1: Add jersey to collection first
        add_payload = {
            "jersey_id": self.test_jersey_id,
            "collection_type": "owned"
        }
        
        add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
        
        if add_response.status_code != 200:
            self.log_test("Collection Delete - Add Setup", "FAIL", f"Could not add jersey to collection: {add_response.status_code}")
            return False
        
        self.log_test("Collection Delete - Add Setup", "PASS", "Jersey added to collection for testing")
        
        # Step 2: Verify jersey is in collection
        collection_response = self.session.get(f"{self.base_url}/collections/owned")
        
        if collection_response.status_code == 200:
            collections = collection_response.json()
            jersey_in_collection = any(item.get('jersey_id') == self.test_jersey_id for item in collections)
            
            if jersey_in_collection:
                self.log_test("Collection Delete - Verify Setup", "PASS", "Jersey confirmed in collection")
            else:
                self.log_test("Collection Delete - Verify Setup", "FAIL", "Jersey not found in collection")
                return False
        else:
            self.log_test("Collection Delete - Verify Setup", "FAIL", "Could not verify collection")
            return False
        
        # Step 3: Test DELETE endpoint
        delete_response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
        
        if delete_response.status_code == 200:
            delete_data = delete_response.json()
            if "message" in delete_data and "removed" in delete_data["message"].lower():
                self.log_test("Collection Delete - DELETE Endpoint", "PASS", 
                            f"DELETE /api/collections/{self.test_jersey_id} successful")
            else:
                self.log_test("Collection Delete - DELETE Endpoint", "FAIL", "Unexpected response message")
                return False
        else:
            self.log_test("Collection Delete - DELETE Endpoint", "FAIL", 
                        f"DELETE failed with status {delete_response.status_code}: {delete_response.text}")
            return False
        
        # Step 4: Verify jersey was removed
        verify_response = self.session.get(f"{self.base_url}/collections/owned")
        
        if verify_response.status_code == 200:
            collections_after = verify_response.json()
            jersey_still_in_collection = any(item.get('jersey_id') == self.test_jersey_id for item in collections_after)
            
            if not jersey_still_in_collection:
                self.log_test("Collection Delete - Verify Removal", "PASS", "Jersey successfully removed from collection")
                return True
            else:
                self.log_test("Collection Delete - Verify Removal", "FAIL", "Jersey still in collection after delete")
                return False
        else:
            self.log_test("Collection Delete - Verify Removal", "FAIL", "Could not verify removal")
            return False
    
    def test_jersey_update_functionality(self):
        """Test PRIORITY 2: Jersey Update Functionality"""
        print("🎯 PRIORITY 2: JERSEY UPDATE FUNCTIONALITY TESTING")
        print("=" * 60)
        
        if not self.auth_token or not self.test_jersey_id:
            self.log_test("Jersey Update Setup", "FAIL", "Missing auth token or jersey ID")
            return False
        
        # Step 1: Get original jersey data
        original_response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}")
        
        if original_response.status_code != 200:
            self.log_test("Jersey Update - Get Original", "FAIL", "Could not get original jersey data")
            return False
        
        original_jersey = original_response.json()
        self.log_test("Jersey Update - Get Original", "PASS", 
                    f"Original: {original_jersey.get('team')} {original_jersey.get('size')} {original_jersey.get('condition')}")
        
        # Step 2: Test PUT endpoint with updates
        update_payload = {
            "team": "Chelsea FC",
            "season": "2023-24",
            "player": "Enzo Fernandez",
            "size": "XL",  # Changed from L to XL
            "condition": "mint",  # Changed from excellent to mint
            "manufacturer": "Nike",
            "home_away": "home",
            "league": "Premier League",
            "description": "UPDATED: Official Chelsea FC home jersey with Enzo Fernandez #5 - now in mint condition",
            "images": ["https://example.com/chelsea-enzo-updated.jpg"]
        }
        
        update_response = self.session.put(f"{self.base_url}/jerseys/{self.test_jersey_id}", json=update_payload)
        
        if update_response.status_code == 200:
            updated_jersey = update_response.json()
            
            # Verify the updates were applied
            if (updated_jersey.get("size") == "XL" and 
                updated_jersey.get("condition") == "mint" and
                "UPDATED:" in updated_jersey.get("description", "")):
                
                self.log_test("Jersey Update - PUT Endpoint", "PASS", 
                            f"PUT /api/jerseys/{self.test_jersey_id} successful: Size L→XL, Condition excellent→mint")
            else:
                self.log_test("Jersey Update - PUT Endpoint", "FAIL", "Updates not reflected in response")
                return False
        else:
            self.log_test("Jersey Update - PUT Endpoint", "FAIL", 
                        f"PUT failed with status {update_response.status_code}: {update_response.text}")
            return False
        
        # Step 3: Verify updates persisted by getting jersey again
        verify_response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}")
        
        if verify_response.status_code == 200:
            verified_jersey = verify_response.json()
            
            if (verified_jersey.get("size") == "XL" and 
                verified_jersey.get("condition") == "mint"):
                
                self.log_test("Jersey Update - Verify Persistence", "PASS", "Updates persisted in database")
                return True
            else:
                self.log_test("Jersey Update - Verify Persistence", "FAIL", "Updates not persisted")
                return False
        else:
            self.log_test("Jersey Update - Verify Persistence", "FAIL", "Could not verify persistence")
            return False
    
    def test_authorization_checks(self):
        """Test authorization for jersey updates"""
        print("🔒 AUTHORIZATION TESTING")
        print("=" * 30)
        
        # Create a second user to test authorization
        try:
            unique_email = f"testuser2_{int(time.time())}@topkit.com"
            
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "name": "Test User 2"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code != 200:
                self.log_test("Authorization - Create Second User", "FAIL", "Could not create second user")
                return False
            
            # Get the second user's token
            second_user_data = register_response.json()
            second_user_token = second_user_data["token"]
            
            self.log_test("Authorization - Create Second User", "PASS", "Second user created")
            
            # Try to update the first user's jersey with second user's token
            update_payload = {
                "team": "Chelsea FC",
                "season": "2023-24",
                "player": "Enzo Fernandez",
                "size": "S",
                "condition": "good",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Unauthorized update attempt",
                "images": []
            }
            
            # Use second user's token
            unauthorized_headers = {'Authorization': f'Bearer {second_user_token}'}
            response = self.session.put(f"{self.base_url}/jerseys/{self.test_jersey_id}", 
                                      json=update_payload, headers=unauthorized_headers)
            
            if response.status_code == 403:
                self.log_test("Authorization - Unauthorized Update", "PASS", "Unauthorized update correctly rejected with 403")
                return True
            else:
                self.log_test("Authorization - Unauthorized Update", "FAIL", f"Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authorization Testing", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_priority_tests(self):
        """Run all priority tests"""
        print("🚀 TopKit Priority Testing - Collection Delete & Jersey Update")
        print("=" * 70)
        
        results = {}
        
        # Setup
        if not self.setup_auth():
            print("❌ Cannot proceed without authentication")
            return results
        
        if not self.setup_test_jersey():
            print("❌ Cannot proceed without test jersey")
            return results
        
        # Priority Tests
        results['collection_delete'] = self.test_collection_delete_functionality()
        results['jersey_update'] = self.test_jersey_update_functionality()
        results['authorization'] = self.test_authorization_checks()
        
        # Summary
        print("📊 PRIORITY TEST SUMMARY")
        print("=" * 40)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        print(f"Total Priority Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        return results

if __name__ == "__main__":
    tester = PriorityTester()
    results = tester.run_priority_tests()