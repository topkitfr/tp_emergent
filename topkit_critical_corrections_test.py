#!/usr/bin/env python3
"""
TopKit Critical Corrections Testing - Focus on User-Reported Issues
Testing the critical corrections implemented for TopKit based on user feedback:

PRIORITY 1 - API Collection Delete (stuck_count: 2)
PRIORITY 2 - API Listing avec Prix  
PRIORITY 3 - Intégration complète
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://mongodb-routing.preview.emergentagent.com/api"

class TopKitCriticalTester:
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
    
    def setup_test_user(self):
        """Create a test user for authentication"""
        try:
            unique_email = f"topkit_test_{int(time.time())}@example.com"
            
            payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "TopKit Test User"
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
    
    def create_test_jersey(self):
        """Create a test jersey for collection testing"""
        try:
            if not self.auth_token:
                self.log_test("Create Test Jersey", "FAIL", "No auth token available")
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
                "images": ["https://example.com/chelsea-enzo.jpg"],
                "reference_code": "CHE-2324-ENZ-L"
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_jersey_id = data["id"]
                    self.log_test("Create Test Jersey", "PASS", f"Jersey created: {data['team']} {data['season']} {data.get('player', 'N/A')}")
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
    
    # PRIORITY 1 - API Collection Delete Testing (stuck_count: 2)
    def test_priority1_collection_delete_authenticated(self):
        """PRIORITY 1: Test DELETE /api/collections/{jersey_id} with authenticated user"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Step 1: Add jersey to collection first
            add_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
            
            if add_response.status_code != 200:
                self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", "Could not add jersey to collection for testing")
                return False
            
            # Step 2: Verify jersey is in collection
            collection_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if collection_response.status_code == 200:
                collections = collection_response.json()
                jersey_found = any(item.get('jersey_id') == self.test_jersey_id for item in collections)
                
                if not jersey_found:
                    self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", "Jersey not found in collection after adding")
                    return False
            else:
                self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", "Could not verify jersey in collection")
                return False
            
            # Step 3: Test DELETE endpoint
            delete_response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            if delete_response.status_code == 200:
                data = delete_response.json()
                if "message" in data and "removed" in data["message"].lower():
                    # Step 4: Verify jersey is actually removed
                    verify_response = self.session.get(f"{self.base_url}/collections/owned")
                    
                    if verify_response.status_code == 200:
                        updated_collections = verify_response.json()
                        jersey_still_exists = any(item.get('jersey_id') == self.test_jersey_id for item in updated_collections)
                        
                        if not jersey_still_exists:
                            self.log_test("PRIORITY 1 - Collection Delete (Auth)", "PASS", "Jersey successfully removed from collection")
                            return True
                        else:
                            self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", "Jersey still exists in collection after delete")
                            return False
                    else:
                        self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", "Could not verify removal")
                        return False
                else:
                    self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", f"Unexpected response message: {data}")
                    return False
            else:
                self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", f"Status: {delete_response.status_code}, Response: {delete_response.text}")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 1 - Collection Delete (Auth)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority1_collection_delete_unauthenticated(self):
        """PRIORITY 1: Test DELETE /api/collections/{jersey_id} without authentication"""
        try:
            if not self.test_jersey_id:
                self.log_test("PRIORITY 1 - Collection Delete (Unauth)", "FAIL", "No test jersey ID available")
                return False
            
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                self.log_test("PRIORITY 1 - Collection Delete (Unauth)", "PASS", f"Correctly rejected unauthenticated request with status {response.status_code}")
                return True
            else:
                self.log_test("PRIORITY 1 - Collection Delete (Unauth)", "FAIL", f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 1 - Collection Delete (Unauth)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority1_collection_delete_nonexistent_jersey(self):
        """PRIORITY 1: Test DELETE /api/collections/{jersey_id} with non-existent jersey"""
        try:
            if not self.auth_token:
                self.log_test("PRIORITY 1 - Collection Delete (Nonexistent)", "FAIL", "No auth token available")
                return False
            
            # Use a fake jersey ID
            fake_jersey_id = str(uuid.uuid4())
            
            response = self.session.delete(f"{self.base_url}/collections/{fake_jersey_id}")
            
            if response.status_code == 404:
                self.log_test("PRIORITY 1 - Collection Delete (Nonexistent)", "PASS", "Correctly returned 404 for non-existent jersey")
                return True
            else:
                self.log_test("PRIORITY 1 - Collection Delete (Nonexistent)", "FAIL", f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 1 - Collection Delete (Nonexistent)", "FAIL", f"Exception: {str(e)}")
            return False
    
    # PRIORITY 2 - API Listing avec Prix Testing
    def test_priority2_listing_with_price(self):
        """PRIORITY 2: Test POST /api/listings with price field"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("PRIORITY 2 - Listing with Price", "FAIL", "Missing auth token or jersey ID")
                return False
            
            payload = {
                "jersey_id": self.test_jersey_id,
                "price": 99.99,
                "description": "Excellent condition Chelsea FC jersey with Enzo Fernandez. Perfect for collectors!",
                "images": ["https://example.com/chelsea-listing1.jpg", "https://example.com/chelsea-listing2.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/listings", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("price") == 99.99:
                    self.test_listing_id = data["id"]
                    self.log_test("PRIORITY 2 - Listing with Price", "PASS", f"Listing created with price: €{data['price']}")
                    return True
                else:
                    self.log_test("PRIORITY 2 - Listing with Price", "FAIL", "Missing listing ID or incorrect price in response")
                    return False
            else:
                self.log_test("PRIORITY 2 - Listing with Price", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 2 - Listing with Price", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority2_listing_without_price(self):
        """PRIORITY 2: Test POST /api/listings without price (null) for compatibility"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("PRIORITY 2 - Listing without Price", "FAIL", "Missing auth token or jersey ID")
                return False
            
            payload = {
                "jersey_id": self.test_jersey_id,
                "price": None,  # Explicitly null
                "description": "Chelsea FC jersey - price to be determined by market demand (Discogs-style)",
                "images": ["https://example.com/chelsea-no-price.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/listings", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("price") is None:
                    self.log_test("PRIORITY 2 - Listing without Price", "PASS", "Listing created without price (market-determined)")
                    return True
                else:
                    self.log_test("PRIORITY 2 - Listing without Price", "FAIL", "Unexpected price value in response")
                    return False
            else:
                self.log_test("PRIORITY 2 - Listing without Price", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 2 - Listing without Price", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority2_listing_price_retrieval(self):
        """PRIORITY 2: Test GET /api/listings to verify price is stored and retrieved correctly"""
        try:
            if not self.test_listing_id:
                self.log_test("PRIORITY 2 - Listing Price Retrieval", "FAIL", "No test listing ID available")
                return False
            
            response = self.session.get(f"{self.base_url}/listings/{self.test_listing_id}")
            
            if response.status_code == 200:
                listing = response.json()
                if listing.get("id") == self.test_listing_id and listing.get("price") == 99.99:
                    self.log_test("PRIORITY 2 - Listing Price Retrieval", "PASS", f"Price correctly stored and retrieved: €{listing['price']}")
                    return True
                else:
                    self.log_test("PRIORITY 2 - Listing Price Retrieval", "FAIL", f"Price mismatch or missing data. Expected: €99.99, Got: {listing.get('price')}")
                    return False
            else:
                self.log_test("PRIORITY 2 - Listing Price Retrieval", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 2 - Listing Price Retrieval", "FAIL", f"Exception: {str(e)}")
            return False
    
    # PRIORITY 3 - Intégration complète Testing
    def test_priority3_complete_workflow(self):
        """PRIORITY 3: Test complete workflow - Create jersey → Add to collection → Create listing with price → Delete from collection"""
        try:
            if not self.auth_token:
                self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "No auth token available")
                return False
            
            # Step 1: Create a new jersey for complete workflow test
            jersey_payload = {
                "team": "Real Madrid",
                "season": "2023-24",
                "player": "Vinicius Jr",
                "size": "M",
                "condition": "mint",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Official Real Madrid home jersey with Vinicius Jr #7 - mint condition",
                "images": ["https://example.com/real-madrid-vinicius.jpg"],
                "reference_code": "RM-2324-VIN-M"
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if jersey_response.status_code != 200:
                self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "Step 1: Jersey creation failed")
                return False
            
            workflow_jersey_id = jersey_response.json()["id"]
            
            # Step 2: Add to collection
            collection_payload = {
                "jersey_id": workflow_jersey_id,
                "collection_type": "owned"
            }
            
            collection_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
            
            if collection_response.status_code != 200:
                self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "Step 2: Collection add failed")
                return False
            
            # Step 3: Create listing with price
            listing_payload = {
                "jersey_id": workflow_jersey_id,
                "price": 149.99,
                "description": "Mint condition Real Madrid jersey from my personal collection. Vinicius Jr #7, never worn.",
                "images": ["https://example.com/real-madrid-listing.jpg"]
            }
            
            listing_response = self.session.post(f"{self.base_url}/listings", json=listing_payload)
            
            if listing_response.status_code != 200:
                self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "Step 3: Listing creation failed")
                return False
            
            workflow_listing_id = listing_response.json()["id"]
            
            # Step 4: Verify listing has correct price and jersey data
            listing_detail_response = self.session.get(f"{self.base_url}/listings/{workflow_listing_id}")
            
            if listing_detail_response.status_code != 200:
                self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "Step 4: Could not retrieve listing details")
                return False
            
            listing_detail = listing_detail_response.json()
            
            if (listing_detail.get("price") != 149.99 or 
                listing_detail.get("jersey_id") != workflow_jersey_id or
                "jersey" not in listing_detail):
                self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "Step 4: Listing data integrity check failed")
                return False
            
            # Step 5: Delete from collection
            delete_response = self.session.delete(f"{self.base_url}/collections/{workflow_jersey_id}")
            
            if delete_response.status_code != 200:
                self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "Step 5: Collection delete failed")
                return False
            
            # Step 6: Verify removal
            verify_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if verify_response.status_code == 200:
                collections = verify_response.json()
                jersey_still_exists = any(item.get('jersey_id') == workflow_jersey_id for item in collections)
                
                if not jersey_still_exists:
                    self.log_test("PRIORITY 3 - Complete Workflow", "PASS", 
                                f"Complete workflow successful: Jersey → Collection → Listing (€{listing_detail['price']}) → Delete")
                    return True
                else:
                    self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "Step 6: Jersey not removed from collection")
                    return False
            else:
                self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", "Step 6: Could not verify collection removal")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 3 - Complete Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_critical_tests(self):
        """Run all critical correction tests"""
        print("🎯 TOPKIT CRITICAL CORRECTIONS TESTING")
        print("=" * 60)
        print("Testing critical corrections based on user feedback:")
        print("- PRIORITY 1: API Collection Delete (stuck_count: 2)")
        print("- PRIORITY 2: API Listing avec Prix")
        print("- PRIORITY 3: Intégration complète")
        print("=" * 60)
        print()
        
        # Setup
        if not self.setup_test_user():
            print("❌ CRITICAL: Could not setup test user. Aborting tests.")
            return
        
        if not self.create_test_jersey():
            print("❌ CRITICAL: Could not create test jersey. Aborting tests.")
            return
        
        print("🔧 SETUP COMPLETE - Starting critical tests...")
        print()
        
        # Track results
        results = {
            "priority1": [],
            "priority2": [],
            "priority3": []
        }
        
        # PRIORITY 1 Tests - Collection Delete (Most Critical - stuck_count: 2)
        print("🚨 PRIORITY 1 - COLLECTION DELETE TESTING (STUCK_COUNT: 2)")
        print("-" * 50)
        
        results["priority1"].append(self.test_priority1_collection_delete_authenticated())
        results["priority1"].append(self.test_priority1_collection_delete_unauthenticated())
        results["priority1"].append(self.test_priority1_collection_delete_nonexistent_jersey())
        
        # PRIORITY 2 Tests - Listing with Price
        print("💰 PRIORITY 2 - LISTING WITH PRICE TESTING")
        print("-" * 50)
        
        results["priority2"].append(self.test_priority2_listing_with_price())
        results["priority2"].append(self.test_priority2_listing_without_price())
        results["priority2"].append(self.test_priority2_listing_price_retrieval())
        
        # PRIORITY 3 Tests - Complete Integration
        print("🔄 PRIORITY 3 - COMPLETE INTEGRATION TESTING")
        print("-" * 50)
        
        results["priority3"].append(self.test_priority3_complete_workflow())
        
        # Summary
        print("📊 CRITICAL CORRECTIONS TEST SUMMARY")
        print("=" * 60)
        
        priority1_passed = sum(results["priority1"])
        priority1_total = len(results["priority1"])
        
        priority2_passed = sum(results["priority2"])
        priority2_total = len(results["priority2"])
        
        priority3_passed = sum(results["priority3"])
        priority3_total = len(results["priority3"])
        
        total_passed = priority1_passed + priority2_passed + priority3_passed
        total_tests = priority1_total + priority2_total + priority3_total
        
        print(f"🚨 PRIORITY 1 (Collection Delete - stuck_count: 2): {priority1_passed}/{priority1_total} PASSED")
        print(f"💰 PRIORITY 2 (Listing with Price): {priority2_passed}/{priority2_total} PASSED")
        print(f"🔄 PRIORITY 3 (Complete Integration): {priority3_passed}/{priority3_total} PASSED")
        print()
        print(f"🎯 OVERALL CRITICAL CORRECTIONS: {total_passed}/{total_tests} PASSED ({(total_passed/total_tests)*100:.1f}%)")
        
        if priority1_passed == priority1_total:
            print("✅ PRIORITY 1 SUCCESS: Collection delete functionality is working correctly!")
        else:
            print("❌ PRIORITY 1 CRITICAL ISSUE: Collection delete has problems - user complaint is valid!")
        
        if priority2_passed == priority2_total:
            print("✅ PRIORITY 2 SUCCESS: Listing with price functionality is working correctly!")
        else:
            print("❌ PRIORITY 2 ISSUE: Listing with price has problems!")
        
        if priority3_passed == priority3_total:
            print("✅ PRIORITY 3 SUCCESS: Complete integration workflow is working correctly!")
        else:
            print("❌ PRIORITY 3 ISSUE: Complete integration workflow has problems!")

if __name__ == "__main__":
    tester = TopKitCriticalTester()
    tester.run_all_critical_tests()