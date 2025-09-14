#!/usr/bin/env python3
"""
TopKit Collection Fresh Jersey Test
Test the specific scenario: Create a new jersey, approve it, then add to collection
This simulates the exact user workflow that might be causing issues
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://image-fix-10.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"

class FreshJerseyCollectionTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.user_token = None
        self.admin_token = None
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
    
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["token"]
                self.user_id = data["user"]["id"]
                self.log_test("User Authentication", "PASS", f"Logged in as {TEST_USER_EMAIL}")
                return True
            else:
                self.log_test("User Authentication", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.log_test("Admin Authentication", "PASS", f"Logged in as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Admin Authentication", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def create_fresh_jersey(self):
        """Create a new jersey as regular user"""
        try:
            if not self.user_token:
                self.log_test("Create Fresh Jersey", "FAIL", "No user token")
                return False
            
            # Set user auth
            self.session.headers.update({'Authorization': f'Bearer {self.user_token}'})
            
            # Create unique jersey
            timestamp = int(time.time())
            payload = {
                "team": f"Test Team {timestamp}",
                "season": "2024-25",
                "player": "Test Player",
                "size": "L",
                "condition": "very_good",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Test League",
                "description": f"Fresh jersey test created at {datetime.now().isoformat()}",
                "images": []
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.test_jersey_id = data["id"]
                jersey_name = f"{data.get('team')} {data.get('season')}"
                self.log_test("Create Fresh Jersey", "PASS", 
                            f"Created jersey: {jersey_name} (ID: {self.test_jersey_id}, Status: {data.get('status')})")
                return True
            else:
                self.log_test("Create Fresh Jersey", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Fresh Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def verify_jersey_pending(self):
        """Verify jersey is in pending status and not visible in public list"""
        try:
            # Check that jersey is NOT in public jersey list
            public_response = self.session.get(f"{self.base_url}/jerseys?limit=100")
            
            if public_response.status_code == 200:
                public_jerseys = public_response.json()
                jersey_in_public = any(j.get('id') == self.test_jersey_id for j in public_jerseys)
                
                if not jersey_in_public:
                    self.log_test("Verify Jersey Pending", "PASS", "Jersey correctly hidden from public list (pending status)")
                    return True
                else:
                    self.log_test("Verify Jersey Pending", "FAIL", "Jersey visible in public list despite pending status")
                    return False
            else:
                self.log_test("Verify Jersey Pending", "FAIL", f"Could not get public jerseys: {public_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Verify Jersey Pending", "FAIL", f"Exception: {str(e)}")
            return False
    
    def approve_jersey_as_admin(self):
        """Approve the jersey as admin"""
        try:
            if not self.admin_token or not self.test_jersey_id:
                self.log_test("Approve Jersey", "FAIL", "Missing admin token or jersey ID")
                return False
            
            # Set admin auth
            self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
            
            response = self.session.post(f"{self.base_url}/admin/jerseys/{self.test_jersey_id}/approve")
            
            if response.status_code == 200:
                self.log_test("Approve Jersey", "PASS", "Jersey approved successfully")
                return True
            else:
                self.log_test("Approve Jersey", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Approve Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def verify_jersey_approved_and_public(self):
        """Verify jersey is now approved and visible in public list"""
        try:
            # Check that jersey is NOW in public jersey list
            public_response = self.session.get(f"{self.base_url}/jerseys?limit=100")
            
            if public_response.status_code == 200:
                public_jerseys = public_response.json()
                jersey_in_public = None
                
                for jersey in public_jerseys:
                    if jersey.get('id') == self.test_jersey_id:
                        jersey_in_public = jersey
                        break
                
                if jersey_in_public:
                    status = jersey_in_public.get('status')
                    if status == 'approved':
                        self.log_test("Verify Jersey Approved", "PASS", 
                                    f"Jersey now visible in public list with approved status")
                        return True
                    else:
                        self.log_test("Verify Jersey Approved", "FAIL", 
                                    f"Jersey visible but status is {status}, not approved")
                        return False
                else:
                    self.log_test("Verify Jersey Approved", "FAIL", "Jersey still not visible in public list after approval")
                    return False
            else:
                self.log_test("Verify Jersey Approved", "FAIL", f"Could not get public jerseys: {public_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Verify Jersey Approved", "FAIL", f"Exception: {str(e)}")
            return False
    
    def add_approved_jersey_to_collection(self):
        """Add the newly approved jersey to user's collection"""
        try:
            if not self.user_token or not self.test_jersey_id:
                self.log_test("Add to Collection", "FAIL", "Missing user token or jersey ID")
                return False
            
            # Switch back to user auth
            self.session.headers.update({'Authorization': f'Bearer {self.user_token}'})
            
            # Add to owned collection
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 200:
                self.log_test("Add to Collection", "PASS", "Jersey added to owned collection")
                return True
            else:
                self.log_test("Add to Collection", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add to Collection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def verify_jersey_in_collection(self):
        """Verify jersey appears in user's collection"""
        try:
            if not self.user_token:
                self.log_test("Verify in Collection", "FAIL", "No user token")
                return False
            
            # Get owned collection
            response = self.session.get(f"{self.base_url}/collections/owned")
            
            if response.status_code == 200:
                collection = response.json()
                
                # Look for our test jersey
                jersey_found = False
                jersey_details = None
                
                for item in collection:
                    if item.get('jersey_id') == self.test_jersey_id:
                        jersey_found = True
                        jersey_details = item.get('jersey', {})
                        break
                
                if jersey_found:
                    jersey_name = f"{jersey_details.get('team', 'Unknown')} {jersey_details.get('season', 'Unknown')}"
                    self.log_test("Verify in Collection", "PASS", 
                                f"Jersey found in collection: {jersey_name}")
                    return True
                else:
                    self.log_test("Verify in Collection", "FAIL", 
                                f"Jersey NOT found in collection. Total items: {len(collection)}")
                    return False
            else:
                self.log_test("Verify in Collection", "FAIL", f"Could not get collection: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Verify in Collection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def verify_profile_stats_updated(self):
        """Verify profile statistics reflect the collection addition"""
        try:
            if not self.user_token:
                self.log_test("Verify Profile Stats", "FAIL", "No user token")
                return False
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                stats = profile.get("stats", {})
                owned_count = stats.get("owned_jerseys", 0)
                
                if owned_count > 0:
                    self.log_test("Verify Profile Stats", "PASS", 
                                f"Profile stats show {owned_count} owned jerseys")
                    return True
                else:
                    self.log_test("Verify Profile Stats", "FAIL", 
                                f"Profile stats show 0 owned jerseys despite collection addition")
                    return False
            else:
                self.log_test("Verify Profile Stats", "FAIL", f"Could not get profile: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Verify Profile Stats", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_timing_issues(self):
        """Test if there are any timing/synchronization issues"""
        try:
            if not self.user_token or not self.test_jersey_id:
                self.log_test("Test Timing Issues", "FAIL", "Missing requirements")
                return False
            
            # Add jersey to wanted collection
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if add_response.status_code == 200:
                # Immediately check if it appears in collection (no delay)
                immediate_response = self.session.get(f"{self.base_url}/collections/wanted")
                
                if immediate_response.status_code == 200:
                    immediate_collection = immediate_response.json()
                    immediate_found = any(item.get('jersey_id') == self.test_jersey_id for item in immediate_collection)
                    
                    # Wait 1 second and check again
                    time.sleep(1)
                    delayed_response = self.session.get(f"{self.base_url}/collections/wanted")
                    
                    if delayed_response.status_code == 200:
                        delayed_collection = delayed_response.json()
                        delayed_found = any(item.get('jersey_id') == self.test_jersey_id for item in delayed_collection)
                        
                        if immediate_found and delayed_found:
                            self.log_test("Test Timing Issues", "PASS", 
                                        "No timing issues - jersey appears immediately and consistently")
                            return True
                        elif not immediate_found and delayed_found:
                            self.log_test("Test Timing Issues", "FAIL", 
                                        "Timing issue detected - jersey appears only after delay")
                            return False
                        elif immediate_found and not delayed_found:
                            self.log_test("Test Timing Issues", "FAIL", 
                                        "Consistency issue - jersey disappears after delay")
                            return False
                        else:
                            self.log_test("Test Timing Issues", "FAIL", 
                                        "Jersey not found in either immediate or delayed check")
                            return False
                    else:
                        self.log_test("Test Timing Issues", "FAIL", "Delayed check failed")
                        return False
                else:
                    self.log_test("Test Timing Issues", "FAIL", "Immediate check failed")
                    return False
            else:
                self.log_test("Test Timing Issues", "FAIL", f"Could not add to wanted collection: {add_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test Timing Issues", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_fresh_jersey_workflow_test(self):
        """Run the complete fresh jersey workflow test"""
        print("🔍 FRESH JERSEY COLLECTION WORKFLOW TEST")
        print("=" * 60)
        print("Testing the complete workflow: Create → Approve → Add to Collection")
        print("=" * 60)
        print()
        
        tests = [
            self.authenticate_user,
            self.authenticate_admin,
            self.create_fresh_jersey,
            self.verify_jersey_pending,
            self.approve_jersey_as_admin,
            self.verify_jersey_approved_and_public,
            self.add_approved_jersey_to_collection,
            self.verify_jersey_in_collection,
            self.verify_profile_stats_updated,
            self.test_timing_issues
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            if test():
                passed += 1
            else:
                failed += 1
            time.sleep(0.5)
        
        print("=" * 60)
        print(f"🎯 FRESH JERSEY WORKFLOW TEST RESULTS")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print("=" * 60)
        
        if failed == 0:
            print("✅ COMPLETE WORKFLOW WORKING PERFECTLY!")
            print("   The collection system handles fresh jersey creation and approval correctly.")
        else:
            print("🚨 ISSUES FOUND IN WORKFLOW!")
            print("   There may be problems with the jersey approval or collection process.")

if __name__ == "__main__":
    tester = FreshJerseyCollectionTester()
    tester.run_fresh_jersey_workflow_test()