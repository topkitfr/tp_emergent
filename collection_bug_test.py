#!/usr/bin/env python3
"""
TopKit Collection Bug Debug Test
Testing the specific user complaint: "le bug n'est toujours pas résolu, je ne le vois toujours pas dans ma collection, ni dans les statistiques. C'est pareil avec le bouton 'je le veux'"

This test focuses on debugging the complete end-to-end collection workflow for steinmetzlivio@gmail.com
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "https://kit-fixes.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class CollectionBugTester:
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
    
    def test_user_authentication(self):
        """Test authentication with the specific user steinmetzlivio@gmail.com"""
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("User Authentication", "PASS", f"Logged in as {TEST_USER_EMAIL}, User ID: {self.user_id}")
                    return True
                else:
                    self.log_test("User Authentication", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("User Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_approved_jerseys(self):
        """Find approved jerseys in the database"""
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=50")
            
            if response.status_code == 200:
                jerseys = response.json()
                approved_jerseys = [j for j in jerseys if j.get('status') == 'approved']
                
                if approved_jerseys:
                    # Use the first approved jersey for testing
                    self.test_jersey_id = approved_jerseys[0]['id']
                    jersey_info = f"{approved_jerseys[0].get('team', 'Unknown')} {approved_jerseys[0].get('season', 'Unknown')}"
                    if approved_jerseys[0].get('player'):
                        jersey_info += f" - {approved_jerseys[0]['player']}"
                    
                    self.log_test("Get Approved Jerseys", "PASS", 
                                f"Found {len(approved_jerseys)} approved jerseys. Using: {jersey_info} (ID: {self.test_jersey_id})")
                    return True
                else:
                    self.log_test("Get Approved Jerseys", "FAIL", f"No approved jerseys found. Total jerseys: {len(jerseys)}")
                    return False
            else:
                self.log_test("Get Approved Jerseys", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Approved Jerseys", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_add_jersey_to_owned_collection(self):
        """Test adding jersey to owned collection"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Add to Owned Collection", "FAIL", "Missing auth token or jersey ID")
                return False
            
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Add to Owned Collection", "PASS", f"Response: {data}")
                return True
            elif response.status_code == 400 and "already in collection" in response.text.lower():
                self.log_test("Add to Owned Collection", "PASS", "Jersey already in owned collection")
                return True
            else:
                self.log_test("Add to Owned Collection", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add to Owned Collection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_add_jersey_to_wanted_collection(self):
        """Test adding jersey to wanted collection"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Add to Wanted Collection", "FAIL", "Missing auth token or jersey ID")
                return False
            
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Add to Wanted Collection", "PASS", f"Response: {data}")
                return True
            elif response.status_code == 400 and "already in collection" in response.text.lower():
                self.log_test("Add to Wanted Collection", "PASS", "Jersey already in wanted collection")
                return True
            else:
                self.log_test("Add to Wanted Collection", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add to Wanted Collection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_retrieve_owned_collection(self):
        """Test retrieving user's owned collection"""
        try:
            if not self.auth_token:
                self.log_test("Retrieve Owned Collection", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/collections/owned")
            
            if response.status_code == 200:
                collection = response.json()
                
                # Check if our test jersey is in the collection
                jersey_found = False
                jersey_details = None
                
                for item in collection:
                    if item.get('jersey_id') == self.test_jersey_id:
                        jersey_found = True
                        jersey_details = item.get('jersey', {})
                        break
                
                if jersey_found:
                    jersey_info = f"{jersey_details.get('team', 'Unknown')} {jersey_details.get('season', 'Unknown')}"
                    if jersey_details.get('player'):
                        jersey_info += f" - {jersey_details['player']}"
                    
                    self.log_test("Retrieve Owned Collection", "PASS", 
                                f"Found {len(collection)} owned jerseys. Test jersey found: {jersey_info}")
                    return True
                else:
                    self.log_test("Retrieve Owned Collection", "FAIL", 
                                f"Test jersey NOT found in owned collection. Total items: {len(collection)}")
                    
                    # Debug: Show what's in the collection
                    if collection:
                        print("   DEBUG - Items in owned collection:")
                        for i, item in enumerate(collection[:3]):  # Show first 3 items
                            jersey = item.get('jersey', {})
                            print(f"     {i+1}. {jersey.get('team', 'Unknown')} {jersey.get('season', 'Unknown')} (ID: {item.get('jersey_id', 'Unknown')})")
                    
                    return False
            else:
                self.log_test("Retrieve Owned Collection", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Retrieve Owned Collection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_retrieve_wanted_collection(self):
        """Test retrieving user's wanted collection"""
        try:
            if not self.auth_token:
                self.log_test("Retrieve Wanted Collection", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if response.status_code == 200:
                collection = response.json()
                
                # Check if our test jersey is in the collection
                jersey_found = False
                jersey_details = None
                
                for item in collection:
                    if item.get('jersey_id') == self.test_jersey_id:
                        jersey_found = True
                        jersey_details = item.get('jersey', {})
                        break
                
                if jersey_found:
                    jersey_info = f"{jersey_details.get('team', 'Unknown')} {jersey_details.get('season', 'Unknown')}"
                    if jersey_details.get('player'):
                        jersey_info += f" - {jersey_details['player']}"
                    
                    self.log_test("Retrieve Wanted Collection", "PASS", 
                                f"Found {len(collection)} wanted jerseys. Test jersey found: {jersey_info}")
                    return True
                else:
                    self.log_test("Retrieve Wanted Collection", "FAIL", 
                                f"Test jersey NOT found in wanted collection. Total items: {len(collection)}")
                    
                    # Debug: Show what's in the collection
                    if collection:
                        print("   DEBUG - Items in wanted collection:")
                        for i, item in enumerate(collection[:3]):  # Show first 3 items
                            jersey = item.get('jersey', {})
                            print(f"     {i+1}. {jersey.get('team', 'Unknown')} {jersey.get('season', 'Unknown')} (ID: {item.get('jersey_id', 'Unknown')})")
                    
                    return False
            else:
                self.log_test("Retrieve Wanted Collection", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Retrieve Wanted Collection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_profile_statistics(self):
        """Test user profile statistics to see if collection counts are correct"""
        try:
            if not self.auth_token:
                self.log_test("User Profile Statistics", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                
                if "stats" in profile:
                    stats = profile["stats"]
                    owned_count = stats.get("owned_jerseys", 0)
                    wanted_count = stats.get("wanted_jerseys", 0)
                    listings_count = stats.get("active_listings", 0)
                    
                    self.log_test("User Profile Statistics", "PASS", 
                                f"Stats - Owned: {owned_count}, Wanted: {wanted_count}, Listings: {listings_count}")
                    
                    # Check if stats match what we expect
                    if owned_count == 0 and wanted_count == 0:
                        print("   ⚠️  WARNING: Both owned and wanted counts are 0 - this might indicate the collection bug!")
                    
                    return True
                else:
                    self.log_test("User Profile Statistics", "FAIL", "Missing stats in profile response")
                    return False
            else:
                self.log_test("User Profile Statistics", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Profile Statistics", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_status_filtering(self):
        """Test if only approved jerseys appear in collections"""
        try:
            if not self.auth_token:
                self.log_test("Jersey Status Filtering", "FAIL", "No auth token available")
                return False
            
            # Get all jerseys to check their statuses
            all_jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=100")
            
            if all_jerseys_response.status_code == 200:
                all_jerseys = all_jerseys_response.json()
                
                # Count jerseys by status
                status_counts = {}
                for jersey in all_jerseys:
                    status = jersey.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Get collections
                owned_response = self.session.get(f"{self.base_url}/collections/owned")
                wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
                
                if owned_response.status_code == 200 and wanted_response.status_code == 200:
                    owned_collection = owned_response.json()
                    wanted_collection = wanted_response.json()
                    
                    # Check if all jerseys in collections are approved
                    all_approved = True
                    non_approved_found = []
                    
                    for item in owned_collection + wanted_collection:
                        jersey = item.get('jersey', {})
                        if jersey.get('status') != 'approved':
                            all_approved = False
                            non_approved_found.append(f"{jersey.get('team', 'Unknown')} - Status: {jersey.get('status', 'Unknown')}")
                    
                    if all_approved:
                        self.log_test("Jersey Status Filtering", "PASS", 
                                    f"All jerseys in collections are approved. Jersey statuses in DB: {status_counts}")
                        return True
                    else:
                        self.log_test("Jersey Status Filtering", "FAIL", 
                                    f"Non-approved jerseys found in collections: {non_approved_found}")
                        return False
                else:
                    self.log_test("Jersey Status Filtering", "FAIL", "Could not retrieve collections for filtering test")
                    return False
            else:
                self.log_test("Jersey Status Filtering", "FAIL", f"Could not retrieve all jerseys: {all_jerseys_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Status Filtering", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_mongodb_aggregation_pipeline(self):
        """Test if MongoDB aggregation pipeline is working correctly"""
        try:
            if not self.auth_token:
                self.log_test("MongoDB Aggregation Pipeline", "FAIL", "No auth token available")
                return False
            
            # Test both collection endpoints
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if owned_response.status_code == 200 and wanted_response.status_code == 200:
                owned_collection = owned_response.json()
                wanted_collection = wanted_response.json()
                
                # Check if jersey data is properly populated via aggregation
                aggregation_working = True
                issues = []
                
                for collection_type, collection in [("owned", owned_collection), ("wanted", wanted_collection)]:
                    for item in collection:
                        if 'jersey' not in item:
                            aggregation_working = False
                            issues.append(f"Missing jersey data in {collection_type} collection item")
                        elif not item['jersey'].get('team'):
                            aggregation_working = False
                            issues.append(f"Incomplete jersey data in {collection_type} collection")
                
                if aggregation_working:
                    self.log_test("MongoDB Aggregation Pipeline", "PASS", 
                                f"Aggregation working correctly. Owned: {len(owned_collection)}, Wanted: {len(wanted_collection)}")
                    return True
                else:
                    self.log_test("MongoDB Aggregation Pipeline", "FAIL", f"Aggregation issues: {issues}")
                    return False
            else:
                self.log_test("MongoDB Aggregation Pipeline", "FAIL", 
                            f"Collection endpoints failed. Owned: {owned_response.status_code}, Wanted: {wanted_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("MongoDB Aggregation Pipeline", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_duplicate_prevention(self):
        """Test duplicate prevention when adding same jersey to same collection"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Duplicate Prevention", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Try to add the same jersey to owned collection again
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 400 and "already in collection" in response.text.lower():
                self.log_test("Duplicate Prevention", "PASS", "Duplicate addition correctly prevented")
                return True
            elif response.status_code == 200:
                # This might indicate the jersey wasn't actually in the collection before
                self.log_test("Duplicate Prevention", "FAIL", "Jersey was added again - might not have been in collection initially")
                return False
            else:
                self.log_test("Duplicate Prevention", "FAIL", f"Unexpected response: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Prevention", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_complete_collection_workflow_test(self):
        """Run the complete collection workflow test"""
        print("🔍 COLLECTION BUG DEBUG TEST - COMPLETE WORKFLOW")
        print("=" * 60)
        print(f"Testing with user: {TEST_USER_EMAIL}")
        print(f"Backend URL: {BASE_URL}")
        print("=" * 60)
        print()
        
        # Test sequence
        tests = [
            self.test_user_authentication,
            self.test_get_approved_jerseys,
            self.test_add_jersey_to_owned_collection,
            self.test_add_jersey_to_wanted_collection,
            self.test_retrieve_owned_collection,
            self.test_retrieve_wanted_collection,
            self.test_user_profile_statistics,
            self.test_jersey_status_filtering,
            self.test_mongodb_aggregation_pipeline,
            self.test_duplicate_prevention
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            if test():
                passed += 1
            else:
                failed += 1
            time.sleep(0.5)  # Small delay between tests
        
        print("=" * 60)
        print(f"🎯 COLLECTION WORKFLOW TEST RESULTS")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print("=" * 60)
        
        if failed > 0:
            print("🚨 COLLECTION BUG CONFIRMED - Issues found in the workflow!")
            print("   The user's complaint appears to be valid.")
        else:
            print("✅ COLLECTION WORKFLOW WORKING - No issues found!")
            print("   The bug might be frontend-related or user-specific.")

if __name__ == "__main__":
    tester = CollectionBugTester()
    tester.run_complete_collection_workflow_test()