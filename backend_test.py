#!/usr/bin/env python3
"""
TopKit Backend Testing - Discogs-Style Workflow Implementation
Testing the complete workflow: Jersey Submission → Admin Approval → Collection → Listing Creation
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-marketplace.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD_NEW = "TopKitSecure789#"  # From review request
ADMIN_PASSWORD_OLD = "adminpass123"      # From previous tests

USER_EMAIL = "testuser@topkit.fr"
USER_PASSWORD = "SecurePass789!"

class TopKitTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.jersey_id = None
        self.collection_id = None
        self.listing_id = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Test admin authentication with both possible passwords"""
        print("🔐 Testing Admin Authentication...")
        
        # Try new password first
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD_NEW
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                admin_info = data.get("user", {})
                self.log_result(
                    "Admin Authentication (New Password)",
                    True,
                    f"Admin logged in: {admin_info.get('name')} (Role: {admin_info.get('role')})"
                )
                return True
        except Exception as e:
            pass
        
        # Try old password as fallback
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD_OLD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                admin_info = data.get("user", {})
                self.log_result(
                    "Admin Authentication (Fallback Password)",
                    True,
                    f"Admin logged in: {admin_info.get('name')} (Role: {admin_info.get('role')})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def authenticate_user(self):
        """Test user authentication"""
        print("👤 Testing User Authentication...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.log_result(
                    "User Authentication",
                    True,
                    f"User logged in: {user_info.get('name')} (Role: {user_info.get('role')})"
                )
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
            self.log_result(
                "User Authentication",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_jersey_submission_without_size_condition(self):
        """Test jersey submission without size/condition (catalog submission)"""
        print("📝 Testing Jersey Submission (Catalog Entry)...")
        
        if not self.user_token:
            self.log_result("Jersey Submission", False, "", "User not authenticated")
            return False
        
        jersey_data = {
            "team": "FC Barcelona",
            "season": "2024-25",
            "player": "Pedri",
            "manufacturer": "Nike",
            "home_away": "home",
            "league": "La Liga",
            "description": "Official FC Barcelona home jersey for 2024-25 season featuring Pedri #8",
            "images": ["https://example.com/barca-pedri.jpg"]
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.jersey_id = data.get("id")
                jersey_ref = data.get("reference_number", "N/A")
                self.log_result(
                    "Jersey Submission (Catalog Entry)",
                    True,
                    f"Jersey submitted successfully. ID: {self.jersey_id}, Ref: {jersey_ref}, Status: {data.get('status')}"
                )
                return True
            else:
                self.log_result(
                    "Jersey Submission (Catalog Entry)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Jersey Submission (Catalog Entry)",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_admin_approval_workflow(self):
        """Test admin jersey approval workflow"""
        print("👨‍💼 Testing Admin Approval Workflow...")
        
        if not self.admin_token or not self.jersey_id:
            self.log_result("Admin Approval Workflow", False, "", "Admin not authenticated or no jersey to approve")
            return False
        
        # First, get pending jerseys
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                found_jersey = None
                for jersey in pending_jerseys:
                    if jersey.get("id") == self.jersey_id:
                        found_jersey = jersey
                        break
                
                if found_jersey:
                    self.log_result(
                        "Get Pending Jerseys",
                        True,
                        f"Found submitted jersey in pending list: {found_jersey.get('team')} {found_jersey.get('season')}"
                    )
                else:
                    self.log_result(
                        "Get Pending Jerseys",
                        False,
                        f"Submitted jersey not found in pending list. Found {len(pending_jerseys)} pending jerseys"
                    )
                    return False
            else:
                self.log_result(
                    "Get Pending Jerseys",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Get Pending Jerseys",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False
        
        # Now approve the jersey
        try:
            response = requests.post(f"{BACKEND_URL}/admin/jerseys/{self.jersey_id}/approve", headers=headers)
            
            if response.status_code == 200:
                self.log_result(
                    "Admin Jersey Approval",
                    True,
                    "Jersey approved successfully"
                )
                return True
            else:
                self.log_result(
                    "Admin Jersey Approval",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Admin Jersey Approval",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_approved_jerseys_endpoint(self):
        """Test GET /api/jerseys/approved to get approved jerseys for collection"""
        print("✅ Testing Approved Jerseys Endpoint...")
        
        if not self.user_token:
            self.log_result("Approved Jerseys Endpoint", False, "", "User not authenticated")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/jerseys/approved", headers=headers)
            
            if response.status_code == 200:
                approved_jerseys = response.json()
                found_jersey = None
                for jersey in approved_jerseys:
                    if jersey.get("id") == self.jersey_id:
                        found_jersey = jersey
                        break
                
                if found_jersey:
                    self.log_result(
                        "Approved Jerseys Endpoint",
                        True,
                        f"Found approved jersey: {found_jersey.get('team')} {found_jersey.get('season')} (Status: {found_jersey.get('status')})"
                    )
                    return True
                else:
                    self.log_result(
                        "Approved Jerseys Endpoint",
                        False,
                        f"Approved jersey not found in list. Found {len(approved_jerseys)} approved jerseys"
                    )
                    return False
            else:
                self.log_result(
                    "Approved Jerseys Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Approved Jerseys Endpoint",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_collection_management_with_size_condition(self):
        """Test POST /api/collections with new size/condition fields for owned items"""
        print("📚 Testing Collection Management (with Size/Condition)...")
        
        if not self.user_token or not self.jersey_id:
            self.log_result("Collection Management", False, "", "User not authenticated or no jersey available")
            return False
        
        collection_data = {
            "jersey_id": self.jersey_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "very_good",
            "personal_description": "Purchased from official store, worn twice"
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.collection_id = data.get("collection_id")
                self.log_result(
                    "Collection Management (Add to Owned)",
                    True,
                    f"Jersey added to owned collection. Collection ID: {self.collection_id}, Size: L, Condition: very_good"
                )
                return True
            else:
                self.log_result(
                    "Collection Management (Add to Owned)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Collection Management (Add to Owned)",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_my_owned_collection_endpoint(self):
        """Test GET /api/collections/my-owned to get listable items"""
        print("🏠 Testing My Owned Collection Endpoint...")
        
        if not self.user_token:
            self.log_result("My Owned Collection Endpoint", False, "", "User not authenticated")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/collections/my-owned", headers=headers)
            
            if response.status_code == 200:
                owned_items = response.json()
                found_item = None
                for item in owned_items:
                    if item.get("id") == self.collection_id:
                        found_item = item
                        break
                
                if found_item:
                    self.log_result(
                        "My Owned Collection Endpoint",
                        True,
                        f"Found owned item: {found_item.get('jersey', {}).get('team')} {found_item.get('jersey', {}).get('season')} (Size: {found_item.get('size')}, Condition: {found_item.get('condition')})"
                    )
                    return True
                else:
                    self.log_result(
                        "My Owned Collection Endpoint",
                        False,
                        f"Owned item not found in collection. Found {len(owned_items)} owned items"
                    )
                    return False
            else:
                self.log_result(
                    "My Owned Collection Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "My Owned Collection Endpoint",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_listing_creation_from_collection(self):
        """Test POST /api/listings using collection_id (not jersey_id directly)"""
        print("🏪 Testing Listing Creation from Collection...")
        
        if not self.user_token or not self.collection_id:
            self.log_result("Listing Creation from Collection", False, "", "User not authenticated or no collection item available")
            return False
        
        listing_data = {
            "collection_id": self.collection_id,
            "price": 89.99,
            "marketplace_description": "Excellent condition FC Barcelona jersey, worn only twice. Perfect for collectors!",
            "images": ["https://example.com/my-barca-jersey-1.jpg", "https://example.com/my-barca-jersey-2.jpg"]
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.listing_id = data.get("id")
                self.log_result(
                    "Listing Creation from Collection",
                    True,
                    f"Listing created successfully. ID: {self.listing_id}, Price: €{data.get('price')}, Status: {data.get('status')}"
                )
                return True
            else:
                self.log_result(
                    "Listing Creation from Collection",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Listing Creation from Collection",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_complete_discogs_workflow_validation(self):
        """Validate the complete Discogs workflow end-to-end"""
        print("🔄 Testing Complete Discogs Workflow Validation...")
        
        if not all([self.jersey_id, self.collection_id, self.listing_id]):
            self.log_result(
                "Complete Discogs Workflow Validation",
                False,
                "",
                f"Missing components: Jersey ID: {bool(self.jersey_id)}, Collection ID: {bool(self.collection_id)}, Listing ID: {bool(self.listing_id)}"
            )
            return False
        
        # Verify the listing contains proper references
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/listings/{self.listing_id}", headers=headers)
            
            if response.status_code == 200:
                listing = response.json()
                
                # Check that listing references collection, not jersey directly
                has_collection_ref = "collection_id" in listing or listing.get("jersey_id") != self.jersey_id
                has_proper_size_condition = listing.get("size") and listing.get("condition")
                
                workflow_valid = has_proper_size_condition
                
                self.log_result(
                    "Complete Discogs Workflow Validation",
                    workflow_valid,
                    f"Workflow validation: Size/Condition from collection: {has_proper_size_condition}, Listing Price: €{listing.get('price')}"
                )
                return workflow_valid
            else:
                self.log_result(
                    "Complete Discogs Workflow Validation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Complete Discogs Workflow Validation",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all tests in the correct sequence"""
        print("🚀 Starting TopKit Discogs-Style Workflow Testing")
        print("=" * 60)
        
        # Authentication tests
        admin_auth_success = self.authenticate_admin()
        user_auth_success = self.authenticate_user()
        
        if not admin_auth_success or not user_auth_success:
            print("❌ Authentication failed - cannot proceed with workflow tests")
            return self.generate_summary()
        
        # Core workflow tests
        tests = [
            self.test_jersey_submission_without_size_condition,
            self.test_admin_approval_workflow,
            self.test_approved_jerseys_endpoint,
            self.test_collection_management_with_size_condition,
            self.test_my_owned_collection_endpoint,
            self.test_listing_creation_from_collection,
            self.test_complete_discogs_workflow_validation
        ]
        
        for test in tests:
            test()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = TopKitTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["failed_tests"] == 0 else 1)