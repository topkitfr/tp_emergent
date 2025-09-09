#!/usr/bin/env python3
"""
TopKit Jersey Reference System Testing
Focused test to verify jersey reference_number field functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "https://football-kit-ui.preview.emergentagent.com/api"

class JerseyReferenceSystemTester:
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
    
    def authenticate(self):
        """Authenticate to get access token"""
        try:
            # Use unique email to avoid conflicts
            unique_email = f"reftest_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": "password123",
                "name": "Reference Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("Authentication", "PASS", f"User registered with ID: {self.user_id}")
                    return True
                else:
                    self.log_test("Authentication", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_existing_jerseys_have_reference_numbers(self):
        """Test 1: Check if existing jerseys in database have reference_number fields"""
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=50")
            
            if response.status_code == 200:
                jerseys = response.json()
                total_jerseys = len(jerseys)
                
                if total_jerseys == 0:
                    self.log_test("Existing Jerseys Reference Check", "INFO", "No jerseys found in database")
                    return True
                
                # Check how many have reference_number field
                jerseys_with_ref = 0
                jerseys_without_ref = 0
                sample_references = []
                
                for jersey in jerseys:
                    if 'reference_number' in jersey and jersey['reference_number']:
                        jerseys_with_ref += 1
                        if len(sample_references) < 5:  # Collect first 5 as samples
                            sample_references.append({
                                'team': jersey.get('team', 'Unknown'),
                                'season': jersey.get('season', 'Unknown'),
                                'reference_number': jersey['reference_number']
                            })
                    else:
                        jerseys_without_ref += 1
                
                # Report findings
                if jerseys_with_ref > 0:
                    sample_text = ", ".join([f"{ref['team']} {ref['season']} ({ref['reference_number']})" for ref in sample_references])
                    self.log_test("Existing Jerseys Reference Check", "PASS", 
                                f"Found {jerseys_with_ref}/{total_jerseys} jerseys with reference numbers. Samples: {sample_text}")
                else:
                    self.log_test("Existing Jerseys Reference Check", "FAIL", 
                                f"No jerseys have reference_number field out of {total_jerseys} jerseys")
                
                return jerseys_with_ref > 0
                
            else:
                self.log_test("Existing Jerseys Reference Check", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Existing Jerseys Reference Check", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_jersey_reference_generation(self):
        """Test 2: Create a new jersey and verify automatic reference generation"""
        try:
            if not self.auth_token:
                self.log_test("New Jersey Reference Generation", "FAIL", "No auth token available")
                return False
            
            payload = {
                "team": "Test FC Reference",
                "season": "2024-25",
                "player": "Reference Test Player",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Test Brand",
                "home_away": "home",
                "league": "Test League",
                "description": "Test jersey for reference number generation verification",
                "images": []
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if jersey has reference_number field
                if 'reference_number' in data and data['reference_number']:
                    reference_number = data['reference_number']
                    self.test_jersey_id = data['id']
                    
                    # Verify TK-000001 format
                    if reference_number.startswith('TK-') and len(reference_number) == 9:
                        try:
                            # Extract number part and verify it's numeric
                            number_part = reference_number[3:]  # Remove 'TK-'
                            int(number_part)  # Should be convertible to int
                            
                            self.log_test("New Jersey Reference Generation", "PASS", 
                                        f"Jersey created with reference: {reference_number}")
                            return True
                        except ValueError:
                            self.log_test("New Jersey Reference Generation", "FAIL", 
                                        f"Reference number format invalid: {reference_number}")
                            return False
                    else:
                        self.log_test("New Jersey Reference Generation", "FAIL", 
                                    f"Reference number doesn't match TK-XXXXXX format: {reference_number}")
                        return False
                else:
                    self.log_test("New Jersey Reference Generation", "FAIL", 
                                "New jersey missing reference_number field")
                    return False
            else:
                self.log_test("New Jersey Reference Generation", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("New Jersey Reference Generation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_reference_field_in_get_jersey_response(self):
        """Test 3: Verify reference_number field appears in GET jersey response"""
        try:
            if not self.test_jersey_id:
                self.log_test("Reference Field in GET Response", "FAIL", "No test jersey ID available")
                return False
            
            response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}")
            
            if response.status_code == 200:
                jersey = response.json()
                
                if 'reference_number' in jersey and jersey['reference_number']:
                    reference_number = jersey['reference_number']
                    self.log_test("Reference Field in GET Response", "PASS", 
                                f"GET /api/jerseys/{{id}} includes reference_number: {reference_number}")
                    return True
                else:
                    self.log_test("Reference Field in GET Response", "FAIL", 
                                "reference_number field missing or empty in GET response")
                    return False
            else:
                self.log_test("Reference Field in GET Response", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Reference Field in GET Response", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_reference_field_in_jerseys_list(self):
        """Test 4: Verify reference_number field appears in GET /api/jerseys list"""
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=10")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                if len(jerseys) == 0:
                    self.log_test("Reference Field in Jerseys List", "INFO", "No jerseys in list to check")
                    return True
                
                # Check if any jerseys have reference_number field
                jerseys_with_ref = 0
                sample_refs = []
                
                for jersey in jerseys:
                    if 'reference_number' in jersey and jersey['reference_number']:
                        jerseys_with_ref += 1
                        if len(sample_refs) < 3:
                            sample_refs.append(jersey['reference_number'])
                
                if jerseys_with_ref > 0:
                    self.log_test("Reference Field in Jerseys List", "PASS", 
                                f"GET /api/jerseys includes reference_number field in {jerseys_with_ref}/{len(jerseys)} jerseys. Samples: {', '.join(sample_refs)}")
                    return True
                else:
                    self.log_test("Reference Field in Jerseys List", "FAIL", 
                                f"No jerseys in list have reference_number field (checked {len(jerseys)} jerseys)")
                    return False
            else:
                self.log_test("Reference Field in Jerseys List", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Reference Field in Jerseys List", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_reference_field_in_collection_endpoints(self):
        """Test 5: Verify reference_number field appears in collection-related endpoints"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Reference Field in Collection Endpoints", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # First add jersey to collection
            add_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
            
            if add_response.status_code != 200:
                self.log_test("Reference Field in Collection Endpoints", "FAIL", "Could not add jersey to collection")
                return False
            
            # Now check if reference_number appears in collection endpoint
            collection_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if collection_response.status_code == 200:
                collections = collection_response.json()
                
                # Find our test jersey in the collection
                test_jersey_in_collection = None
                for item in collections:
                    if item.get('jersey_id') == self.test_jersey_id and 'jersey' in item:
                        test_jersey_in_collection = item['jersey']
                        break
                
                if test_jersey_in_collection:
                    if 'reference_number' in test_jersey_in_collection and test_jersey_in_collection['reference_number']:
                        reference_number = test_jersey_in_collection['reference_number']
                        self.log_test("Reference Field in Collection Endpoints", "PASS", 
                                    f"GET /api/collections/owned includes reference_number: {reference_number}")
                        return True
                    else:
                        self.log_test("Reference Field in Collection Endpoints", "FAIL", 
                                    "reference_number field missing in collection jersey data")
                        return False
                else:
                    self.log_test("Reference Field in Collection Endpoints", "FAIL", 
                                "Test jersey not found in collection")
                    return False
            else:
                self.log_test("Reference Field in Collection Endpoints", "FAIL", 
                            f"Collection endpoint failed: {collection_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Reference Field in Collection Endpoints", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_reference_field_in_listing_endpoints(self):
        """Test 6: Verify reference_number field appears in listing-related endpoints"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Reference Field in Listing Endpoints", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Create a listing for our test jersey
            listing_payload = {
                "jersey_id": self.test_jersey_id,
                "price": 99.99,
                "description": "Test listing for reference number verification",
                "images": []
            }
            
            listing_response = self.session.post(f"{self.base_url}/listings", json=listing_payload)
            
            if listing_response.status_code == 200:
                listing_data = listing_response.json()
                listing_id = listing_data['id']
                
                # Check if reference_number appears in listing detail endpoint
                listing_detail_response = self.session.get(f"{self.base_url}/listings/{listing_id}")
                
                if listing_detail_response.status_code == 200:
                    listing_detail = listing_detail_response.json()
                    
                    if 'jersey' in listing_detail and 'reference_number' in listing_detail['jersey']:
                        reference_number = listing_detail['jersey']['reference_number']
                        if reference_number:
                            self.log_test("Reference Field in Listing Endpoints", "PASS", 
                                        f"GET /api/listings/{{id}} includes reference_number: {reference_number}")
                            return True
                        else:
                            self.log_test("Reference Field in Listing Endpoints", "FAIL", 
                                        "reference_number field is empty in listing jersey data")
                            return False
                    else:
                        self.log_test("Reference Field in Listing Endpoints", "FAIL", 
                                    "reference_number field missing in listing jersey data")
                        return False
                else:
                    self.log_test("Reference Field in Listing Endpoints", "FAIL", 
                                f"Listing detail endpoint failed: {listing_detail_response.status_code}")
                    return False
            else:
                self.log_test("Reference Field in Listing Endpoints", "FAIL", 
                            f"Listing creation failed: {listing_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Reference Field in Listing Endpoints", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all jersey reference system tests"""
        print("🔍 JERSEY REFERENCE SYSTEM TESTING")
        print("=" * 50)
        print(f"Backend URL: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Run all tests
        tests = [
            self.test_existing_jerseys_have_reference_numbers,
            self.test_new_jersey_reference_generation,
            self.test_reference_field_in_get_jersey_response,
            self.test_reference_field_in_jerseys_list,
            self.test_reference_field_in_collection_endpoints,
            self.test_reference_field_in_listing_endpoints
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
                failed += 1
        
        # Summary
        print("=" * 50)
        print("🏁 JERSEY REFERENCE SYSTEM TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "0%")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED - Jersey reference system is working correctly!")
        else:
            print("⚠️  Some tests failed - Jersey reference system needs attention")
        
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    tester = JerseyReferenceSystemTester()
    tester.run_all_tests()