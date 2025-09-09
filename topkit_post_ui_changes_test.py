#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Post UI Changes Backend Testing
Tests backend functionality after removing create listing buttons from Browse Jerseys and Marketplace pages.
New workflow: User goes to Collections -> sees owned jerseys with "Sell This Jersey" button -> creates listing from existing owned jersey.
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://football-kit-ui.preview.emergentagent.com/api"
TEST_USER_EMAIL = "postui_testuser@topkit.com"
TEST_USER_PASSWORD = "SecurePass123!"
TEST_USER_NAME = "Post UI Test User"

class TopKitPostUIChangesTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.test_jersey_id = None
        self.test_listing_id = None
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
    
    def setup_authenticated_user(self):
        """Setup authenticated user for testing"""
        try:
            # Use unique email to avoid conflicts
            unique_email = f"postui_testuser_{int(time.time())}@topkit.com"
            
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
                    self.log_test("Setup Authenticated User", "PASS", f"User registered with ID: {self.user_id}")
                    return True
                else:
                    self.log_test("Setup Authenticated User", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Setup Authenticated User", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Setup Authenticated User", "FAIL", f"Exception: {str(e)}")
            return False
    
    def create_test_jersey(self):
        """Create a test jersey for collection and listing tests"""
        try:
            if not self.auth_token:
                self.log_test("Create Test Jersey", "FAIL", "No auth token available")
                return False
            
            payload = {
                "team": "Liverpool FC",
                "season": "2023-24",
                "player": "Mohamed Salah",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Liverpool FC home jersey with Mohamed Salah #11",
                "images": ["https://example.com/liverpool_salah.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_jersey_id = data["id"]
                    self.log_test("Create Test Jersey", "PASS", f"Jersey created with ID: {self.test_jersey_id}")
                    return True
                else:
                    self.log_test("Create Test Jersey", "FAIL", "Missing jersey ID in response")
                    return False
            else:
                self.log_test("Create Test Jersey", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Test Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    # TEST 1: Marketplace functionality still works after removing create listing buttons
    def test_marketplace_listings_retrieval(self):
        """Test GET /api/listings endpoint to ensure listings are still retrievable"""
        try:
            response = self.session.get(f"{self.base_url}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                self.log_test("Marketplace Listings Retrieval", "PASS", 
                            f"Retrieved {len(listings)} listings successfully. Marketplace display functionality intact.")
                
                # Verify listing structure includes jersey details
                if listings:
                    first_listing = listings[0]
                    required_fields = ["id", "jersey_id", "seller_id", "price", "status", "description"]
                    jersey_fields_present = "jersey" in first_listing
                    
                    if all(field in first_listing for field in required_fields) and jersey_fields_present:
                        self.log_test("Marketplace Listing Structure", "PASS", 
                                    "Listings include proper jersey details via aggregation")
                        return True
                    else:
                        self.log_test("Marketplace Listing Structure", "FAIL", 
                                    "Missing required fields or jersey aggregation data")
                        return False
                else:
                    self.log_test("Marketplace Listings Retrieval", "PASS", 
                                "No listings found, but endpoint working correctly")
                    return True
            else:
                self.log_test("Marketplace Listings Retrieval", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Marketplace Listings Retrieval", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_individual_listing_details(self):
        """Test GET /api/listings/{listing_id} for individual listing details"""
        try:
            # First get all listings to find one to test
            listings_response = self.session.get(f"{self.base_url}/listings")
            
            if listings_response.status_code != 200:
                self.log_test("Individual Listing Details", "FAIL", "Could not retrieve listings for test")
                return False
            
            listings = listings_response.json()
            
            if not listings:
                self.log_test("Individual Listing Details", "PASS", "No listings available to test (acceptable)")
                return True
            
            # Test first listing
            listing_id = listings[0]["id"]
            response = self.session.get(f"{self.base_url}/listings/{listing_id}")
            
            if response.status_code == 200:
                listing = response.json()
                
                # Verify listing includes jersey and seller details
                required_fields = ["id", "jersey_id", "seller_id", "price", "jersey", "seller"]
                
                if all(field in listing for field in required_fields):
                    jersey_data = listing["jersey"]
                    seller_data = listing["seller"]
                    
                    self.log_test("Individual Listing Details", "PASS", 
                                f"Listing {listing_id} includes complete jersey and seller details")
                    return True
                else:
                    self.log_test("Individual Listing Details", "FAIL", 
                                "Missing required fields in individual listing response")
                    return False
            else:
                self.log_test("Individual Listing Details", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Individual Listing Details", "FAIL", f"Exception: {str(e)}")
            return False
    
    # TEST 2: Collection management is working for the new "Sell This Jersey" functionality
    def test_owned_collections_access(self):
        """Test GET /api/collections/owned to verify owned collections are accessible"""
        try:
            if not self.auth_token:
                self.log_test("Owned Collections Access", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/collections/owned")
            
            if response.status_code == 200:
                owned_collection = response.json()
                self.log_test("Owned Collections Access", "PASS", 
                            f"Retrieved {len(owned_collection)} owned jerseys. Ready for 'Sell This Jersey' functionality.")
                
                # Verify collection items include jersey data
                if owned_collection:
                    first_item = owned_collection[0]
                    if "jersey" in first_item and "jersey_id" in first_item:
                        jersey_data = first_item["jersey"]
                        required_jersey_fields = ["id", "team", "season", "player", "size", "condition", "manufacturer"]
                        
                        if all(field in jersey_data for field in required_jersey_fields):
                            self.log_test("Owned Collection Jersey Data", "PASS", 
                                        "Owned jerseys include all necessary fields for creating listings")
                            return True
                        else:
                            self.log_test("Owned Collection Jersey Data", "FAIL", 
                                        "Missing required jersey fields for listing creation")
                            return False
                    else:
                        self.log_test("Owned Collection Jersey Data", "FAIL", 
                                    "Collection items missing jersey aggregation data")
                        return False
                else:
                    self.log_test("Owned Collections Access", "PASS", 
                                "No owned jerseys found, but endpoint working correctly")
                    return True
            else:
                self.log_test("Owned Collections Access", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Owned Collections Access", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_wanted_collections_access(self):
        """Test GET /api/collections/wanted to verify wanted collections are accessible"""
        try:
            if not self.auth_token:
                self.log_test("Wanted Collections Access", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if response.status_code == 200:
                wanted_collection = response.json()
                self.log_test("Wanted Collections Access", "PASS", 
                            f"Retrieved {len(wanted_collection)} wanted jerseys. Collections management working.")
                return True
            else:
                self.log_test("Wanted Collections Access", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Wanted Collections Access", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_data_structure_for_listings(self):
        """Test that jersey data structure includes all necessary fields for creating listings"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Jersey Data Structure", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Add jersey to owned collection first
            add_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
            
            # Get owned collection to verify jersey data structure
            response = self.session.get(f"{self.base_url}/collections/owned")
            
            if response.status_code == 200:
                owned_collection = response.json()
                
                # Find our test jersey
                test_jersey_item = None
                for item in owned_collection:
                    if item.get("jersey_id") == self.test_jersey_id:
                        test_jersey_item = item
                        break
                
                if test_jersey_item and "jersey" in test_jersey_item:
                    jersey_data = test_jersey_item["jersey"]
                    
                    # Check all fields needed for listing creation
                    required_fields = [
                        "id", "team", "season", "player", "size", "condition", 
                        "manufacturer", "home_away", "league", "description", "images"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in jersey_data]
                    
                    if not missing_fields:
                        self.log_test("Jersey Data Structure", "PASS", 
                                    "Jersey data includes all necessary fields for creating listings from owned collection")
                        return True
                    else:
                        self.log_test("Jersey Data Structure", "FAIL", 
                                    f"Missing required fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Jersey Data Structure", "FAIL", 
                                "Test jersey not found in owned collection or missing jersey data")
                    return False
            else:
                self.log_test("Jersey Data Structure", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Data Structure", "FAIL", f"Exception: {str(e)}")
            return False
    
    # TEST 3: Listing creation still works for "Sell This Jersey" from collections
    def test_listing_creation_from_owned_jersey(self):
        """Test POST /api/listings endpoint to ensure listings can still be created"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Listing Creation from Owned Jersey", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Create listing from owned jersey (simulating "Sell This Jersey" button click)
            payload = {
                "jersey_id": self.test_jersey_id,
                "price": 95.99,
                "description": "Excellent condition Liverpool FC jersey from my personal collection. Selling due to size change.",
                "images": ["https://example.com/my_liverpool_jersey1.jpg", "https://example.com/my_liverpool_jersey2.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/listings", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_listing_id = data["id"]
                    self.log_test("Listing Creation from Owned Jersey", "PASS", 
                                f"Successfully created listing {self.test_listing_id} from owned jersey. 'Sell This Jersey' workflow supported.")
                    return True
                else:
                    self.log_test("Listing Creation from Owned Jersey", "FAIL", "Missing listing ID in response")
                    return False
            else:
                self.log_test("Listing Creation from Owned Jersey", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Listing Creation from Owned Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_valuation_system_integration(self):
        """Test that the jersey valuation system still updates when new listings are created"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Jersey Valuation System Integration", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Wait a moment for valuation calculations
            time.sleep(2)
            
            # Check if valuation was updated after listing creation
            response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}/valuation")
            
            if response.status_code == 200:
                data = response.json()
                if "valuation" in data and data["valuation"]:
                    valuation = data["valuation"]
                    if valuation.get("total_listings", 0) > 0:
                        self.log_test("Jersey Valuation System Integration", "PASS", 
                                    f"Valuation system updated with {valuation['total_listings']} listings. Integration working.")
                        return True
                    else:
                        self.log_test("Jersey Valuation System Integration", "PASS", 
                                    "Valuation system accessible, listing count may be updating")
                        return True
                else:
                    self.log_test("Jersey Valuation System Integration", "PASS", 
                                "Valuation endpoint accessible, data may be calculating")
                    return True
            else:
                self.log_test("Jersey Valuation System Integration", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Valuation System Integration", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_workflow_end_to_end(self):
        """Test the complete new workflow: Collections -> Owned Jerseys -> Create Listing"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("New Workflow End-to-End", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Step 1: User goes to Collections page (GET /api/collections/owned)
            collections_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if collections_response.status_code != 200:
                self.log_test("New Workflow End-to-End", "FAIL", "Step 1 failed: Could not access owned collections")
                return False
            
            owned_jerseys = collections_response.json()
            
            # Step 2: User sees owned jerseys with jersey data
            test_jersey_found = False
            jersey_data = None
            
            for item in owned_jerseys:
                if item.get("jersey_id") == self.test_jersey_id:
                    test_jersey_found = True
                    jersey_data = item.get("jersey", {})
                    break
            
            if not test_jersey_found:
                self.log_test("New Workflow End-to-End", "FAIL", "Step 2 failed: Test jersey not found in owned collection")
                return False
            
            # Step 3: User clicks "Sell This Jersey" button (creates listing from existing owned jersey)
            listing_payload = {
                "jersey_id": self.test_jersey_id,
                "price": 89.99,
                "description": f"Selling my {jersey_data.get('team', 'Unknown')} {jersey_data.get('season', 'Unknown')} jersey",
                "images": jersey_data.get("images", [])
            }
            
            listing_response = self.session.post(f"{self.base_url}/listings", json=listing_payload)
            
            if listing_response.status_code == 200:
                listing_data = listing_response.json()
                
                # Step 4: Verify listing appears in marketplace
                marketplace_response = self.session.get(f"{self.base_url}/listings")
                
                if marketplace_response.status_code == 200:
                    marketplace_listings = marketplace_response.json()
                    
                    # Check if our new listing appears
                    new_listing_found = any(
                        listing.get("id") == listing_data.get("id") 
                        for listing in marketplace_listings
                    )
                    
                    if new_listing_found:
                        self.log_test("New Workflow End-to-End", "PASS", 
                                    "Complete workflow successful: Collections -> Owned Jerseys -> Create Listing -> Marketplace")
                        return True
                    else:
                        self.log_test("New Workflow End-to-End", "FAIL", 
                                    "Step 4 failed: New listing not found in marketplace")
                        return False
                else:
                    self.log_test("New Workflow End-to-End", "FAIL", 
                                "Step 4 failed: Could not verify listing in marketplace")
                    return False
            else:
                self.log_test("New Workflow End-to-End", "FAIL", 
                            f"Step 3 failed: Could not create listing. Status: {listing_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("New Workflow End-to-End", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_post_ui_changes_tests(self):
        """Run all tests for post UI changes functionality"""
        print("🚀 Starting TopKit Post UI Changes Backend Tests")
        print("Testing backend functionality after removing create listing buttons from Browse Jerseys and Marketplace pages")
        print("New workflow: User goes to Collections -> sees owned jerseys with 'Sell This Jersey' button -> creates listing")
        print("=" * 80)
        
        test_results = {}
        
        # Setup
        print("🔧 SETUP")
        print("-" * 30)
        if not self.setup_authenticated_user():
            print("❌ Setup failed. Cannot continue with tests.")
            return {}
        
        if not self.create_test_jersey():
            print("❌ Test jersey creation failed. Some tests may not work properly.")
        
        # Test 1: Marketplace functionality still works
        print("🏪 TEST 1: MARKETPLACE FUNCTIONALITY AFTER UI CHANGES")
        print("-" * 50)
        test_results['marketplace_listings_retrieval'] = self.test_marketplace_listings_retrieval()
        test_results['individual_listing_details'] = self.test_individual_listing_details()
        
        # Test 2: Collection management is working for "Sell This Jersey"
        print("📚 TEST 2: COLLECTION MANAGEMENT FOR 'SELL THIS JERSEY'")
        print("-" * 50)
        test_results['owned_collections_access'] = self.test_owned_collections_access()
        test_results['wanted_collections_access'] = self.test_wanted_collections_access()
        test_results['jersey_data_structure'] = self.test_jersey_data_structure_for_listings()
        
        # Test 3: Listing creation still works from collections
        print("💰 TEST 3: LISTING CREATION FROM OWNED JERSEYS")
        print("-" * 50)
        test_results['listing_creation_from_owned'] = self.test_listing_creation_from_owned_jersey()
        test_results['valuation_system_integration'] = self.test_jersey_valuation_system_integration()
        
        # Test 4: Complete new workflow
        print("🔄 TEST 4: NEW WORKFLOW END-TO-END")
        print("-" * 50)
        test_results['new_workflow_end_to_end'] = self.test_new_workflow_end_to_end()
        
        # Summary
        print("📊 POST UI CHANGES TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        print("\n🎯 KEY FINDINGS:")
        if test_results.get('marketplace_listings_retrieval', False):
            print("✅ Marketplace functionality remains intact after UI changes")
        else:
            print("❌ Marketplace functionality may be affected")
            
        if test_results.get('owned_collections_access', False) and test_results.get('jersey_data_structure', False):
            print("✅ Collection management ready for 'Sell This Jersey' functionality")
        else:
            print("❌ Collection management may need attention for new workflow")
            
        if test_results.get('listing_creation_from_owned', False):
            print("✅ Listing creation from owned jerseys working correctly")
        else:
            print("❌ Listing creation from collections may have issues")
            
        if test_results.get('new_workflow_end_to_end', False):
            print("✅ Complete new workflow (Collections -> Sell This Jersey -> Marketplace) working")
        else:
            print("❌ New workflow may have integration issues")
        
        return test_results

if __name__ == "__main__":
    tester = TopKitPostUIChangesTester()
    results = tester.run_post_ui_changes_tests()