#!/usr/bin/env python3
"""
Collection Synchronization Backend Test
Testing the collection synchronization fixes as requested in the review:

ISSUES FIXED:
1. Collection authentication dependency mismatch between add and view operations
2. AttributeError in jersey valuation function when size/condition are None
3. Incorrect parameter types in collection endpoints (expecting user_id string vs user dict)

SPECIFIC TESTS:
- Test login with steinmetzlivio@gmail.com account (Password: T0p_Mdp_1288*)
- Test adding jersey to "owned" collection via POST /api/collections
- Test viewing "owned" collection via GET /api/collections/owned
- Test viewing "owned" collection via GET /api/collections/my-owned
- Verify added jerseys appear in both collection endpoints
- Test collection operations as admin user (should now work)
- Test jersey valuation function with jerseys that have null size/condition
- Verify generate_jersey_signature handles None values properly
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://mongodb-routing.preview.emergentagent.com/api"

# Test credentials from review request
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class CollectionSyncTester:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.user_id = None
        self.admin_id = None
        self.test_jersey_id = None
        self.results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_user(self):
        """Test user authentication with steinmetzlivio@gmail.com"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_data = data.get('user', {})
                self.user_id = user_data.get('id')
                
                self.log_result(
                    "User Authentication (steinmetzlivio@gmail.com)",
                    True,
                    f"User: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "User Authentication (steinmetzlivio@gmail.com)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "User Authentication (steinmetzlivio@gmail.com)",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_id = user_data.get('id')
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Admin: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.admin_id}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def create_test_jersey(self):
        """Create a test jersey for collection testing"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            jersey_data = {
                "team": "FC Barcelona",
                "season": "2024-25",
                "player": "Pedri",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for collection synchronization testing"
            }
            
            response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_jersey_id = data.get('id')
                
                self.log_result(
                    "Test Jersey Creation",
                    True,
                    f"Jersey ID: {self.test_jersey_id}, Status: {data.get('status')}"
                )
                return True
            else:
                self.log_result(
                    "Test Jersey Creation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Test Jersey Creation",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def approve_test_jersey(self):
        """Approve the test jersey as admin so it can be added to collections"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.post(f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}/approve", headers=headers)
            
            if response.status_code == 200:
                self.log_result(
                    "Test Jersey Approval (Admin)",
                    True,
                    f"Jersey {self.test_jersey_id} approved successfully"
                )
                return True
            else:
                self.log_result(
                    "Test Jersey Approval (Admin)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Test Jersey Approval (Admin)",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_add_to_owned_collection(self):
        """Test adding jersey to owned collection via POST /api/collections"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "very_good",
                "personal_description": "Test collection item for synchronization testing"
            }
            
            response = requests.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Add Jersey to Owned Collection (POST /api/collections)",
                    True,
                    f"Collection ID: {data.get('id')}, Type: {data.get('collection_type')}, Size: {data.get('size')}, Condition: {data.get('condition')}"
                )
                return True
            else:
                self.log_result(
                    "Add Jersey to Owned Collection (POST /api/collections)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Add Jersey to Owned Collection (POST /api/collections)",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_view_owned_collection_endpoint1(self):
        """Test viewing owned collection via GET /api/collections/owned"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.get(f"{BACKEND_URL}/collections/owned", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                collections = data if isinstance(data, list) else data.get('collections', [])
                
                # Check if our test jersey appears in the collection
                found_jersey = False
                for collection in collections:
                    if collection.get('jersey_id') == self.test_jersey_id:
                        found_jersey = True
                        break
                
                self.log_result(
                    "View Owned Collection (GET /api/collections/owned)",
                    found_jersey,
                    f"Found {len(collections)} owned items, Test jersey found: {found_jersey}"
                )
                return found_jersey
            else:
                self.log_result(
                    "View Owned Collection (GET /api/collections/owned)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "View Owned Collection (GET /api/collections/owned)",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_view_owned_collection_endpoint2(self):
        """Test viewing owned collection via GET /api/collections/my-owned"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.get(f"{BACKEND_URL}/collections/my-owned", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                collections = data if isinstance(data, list) else data.get('collections', [])
                
                # Check if our test jersey appears in the collection
                found_jersey = False
                for collection in collections:
                    if collection.get('jersey_id') == self.test_jersey_id:
                        found_jersey = True
                        break
                
                self.log_result(
                    "View Owned Collection (GET /api/collections/my-owned)",
                    found_jersey,
                    f"Found {len(collections)} owned items, Test jersey found: {found_jersey}"
                )
                return found_jersey
            else:
                self.log_result(
                    "View Owned Collection (GET /api/collections/my-owned)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "View Owned Collection (GET /api/collections/my-owned)",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_admin_collection_operations(self):
        """Test that admin users can now perform collection operations (should work after fix)"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted",
                "size": "M",
                "condition": "new",
                "personal_description": "Admin test collection item"
            }
            
            response = requests.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Admin Collection Operations (POST /api/collections)",
                    True,
                    f"Admin successfully added to collection: {data.get('collection_type')}, Size: {data.get('size')}"
                )
                return True
            else:
                self.log_result(
                    "Admin Collection Operations (POST /api/collections)",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Collection Operations (POST /api/collections)",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_jersey_valuation_with_none_values(self):
        """Test jersey valuation function with jerseys that have null size/condition"""
        try:
            # Create a jersey without size/condition to test valuation handling
            headers = {"Authorization": f"Bearer {self.user_token}"}
            jersey_data = {
                "team": "Real Madrid",
                "season": "2024-25",
                "player": "Vinicius Jr",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey with no size/condition for valuation testing"
                # Note: size and condition are intentionally omitted (None values)
            }
            
            response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                jersey_id = data.get('id')
                
                # Approve the jersey
                admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
                approve_response = requests.post(f"{BACKEND_URL}/admin/jerseys/{jersey_id}/approve", headers=admin_headers)
                
                if approve_response.status_code == 200:
                    # Try to add to collection with None size/condition to test valuation
                    collection_data = {
                        "jersey_id": jersey_id,
                        "collection_type": "owned"
                        # Note: size and condition are intentionally omitted (None values)
                    }
                    
                    collection_response = requests.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
                    
                    if collection_response.status_code == 200:
                        self.log_result(
                            "Jersey Valuation with None Size/Condition",
                            True,
                            f"Successfully handled jersey with None size/condition values in valuation function"
                        )
                        return True
                    else:
                        self.log_result(
                            "Jersey Valuation with None Size/Condition",
                            False,
                            f"Collection creation failed: HTTP {collection_response.status_code}: {collection_response.text}"
                        )
                        return False
                else:
                    self.log_result(
                        "Jersey Valuation with None Size/Condition",
                        False,
                        f"Jersey approval failed: HTTP {approve_response.status_code}: {approve_response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Jersey Valuation with None Size/Condition",
                    False,
                    f"Jersey creation failed: HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Jersey Valuation with None Size/Condition",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_authentication_consistency(self):
        """Test that collection endpoints use consistent authentication (get_current_user)"""
        try:
            # Test that both POST and GET endpoints work with the same authentication
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test POST /api/collections (should use get_current_user)
            post_response = requests.post(f"{BACKEND_URL}/collections", json={
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted",
                "size": "S",
                "condition": "good"
            }, headers=headers)
            
            # Test GET /api/collections/owned (should use get_current_user)
            get_response = requests.get(f"{BACKEND_URL}/collections/owned", headers=headers)
            
            post_success = post_response.status_code == 200
            get_success = get_response.status_code == 200
            
            self.log_result(
                "Authentication Consistency Between Collection Endpoints",
                post_success and get_success,
                f"POST /api/collections: HTTP {post_response.status_code}, GET /api/collections/owned: HTTP {get_response.status_code}"
            )
            
            return post_success and get_success
                
        except Exception as e:
            self.log_result(
                "Authentication Consistency Between Collection Endpoints",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_collection_synchronization(self):
        """Test that jerseys added via POST appear in both GET endpoints immediately"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Add a unique jersey to collection
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned",
                "size": "XL",
                "condition": "near_mint",
                "personal_description": "Synchronization test item"
            }
            
            # First, remove any existing collection item to ensure clean test
            try:
                requests.post(f"{BACKEND_URL}/collections/remove", json={
                    "jersey_id": self.test_jersey_id,
                    "collection_type": "owned"
                }, headers=headers)
            except:
                pass  # Ignore errors if item doesn't exist
            
            # Add to collection
            add_response = requests.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
            
            if add_response.status_code == 200:
                # Immediately check both endpoints
                owned_response = requests.get(f"{BACKEND_URL}/collections/owned", headers=headers)
                my_owned_response = requests.get(f"{BACKEND_URL}/collections/my-owned", headers=headers)
                
                owned_success = owned_response.status_code == 200
                my_owned_success = my_owned_response.status_code == 200
                
                # Check if jersey appears in both endpoints
                found_in_owned = False
                found_in_my_owned = False
                
                if owned_success:
                    owned_data = owned_response.json()
                    owned_collections = owned_data if isinstance(owned_data, list) else owned_data.get('collections', [])
                    for item in owned_collections:
                        if item.get('jersey_id') == self.test_jersey_id and item.get('size') == 'XL':
                            found_in_owned = True
                            break
                
                if my_owned_success:
                    my_owned_data = my_owned_response.json()
                    my_owned_collections = my_owned_data if isinstance(my_owned_data, list) else my_owned_data.get('collections', [])
                    for item in my_owned_collections:
                        if item.get('jersey_id') == self.test_jersey_id and item.get('size') == 'XL':
                            found_in_my_owned = True
                            break
                
                sync_success = found_in_owned and found_in_my_owned
                
                self.log_result(
                    "Collection Synchronization Verification",
                    sync_success,
                    f"Added jersey appears in /owned: {found_in_owned}, appears in /my-owned: {found_in_my_owned}"
                )
                
                return sync_success
            else:
                self.log_result(
                    "Collection Synchronization Verification",
                    False,
                    f"Failed to add to collection: HTTP {add_response.status_code}: {add_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Collection Synchronization Verification",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all collection synchronization tests"""
        print("🎯 COLLECTION SYNCHRONIZATION BACKEND TESTING STARTED")
        print("=" * 80)
        print()
        
        # Authentication tests
        if not self.authenticate_user():
            print("❌ CRITICAL: User authentication failed. Cannot proceed with collection tests.")
            return False
            
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with admin tests.")
            return False
        
        # Create and approve test jersey
        if not self.create_test_jersey():
            print("❌ CRITICAL: Test jersey creation failed. Cannot proceed with collection tests.")
            return False
            
        if not self.approve_test_jersey():
            print("❌ CRITICAL: Test jersey approval failed. Cannot proceed with collection tests.")
            return False
        
        # Core collection synchronization tests
        self.test_add_to_owned_collection()
        self.test_view_owned_collection_endpoint1()
        self.test_view_owned_collection_endpoint2()
        self.test_collection_synchronization()
        
        # Authentication consistency tests
        self.test_authentication_consistency()
        self.test_admin_collection_operations()
        
        # Data integrity tests
        self.test_jersey_valuation_with_none_values()
        
        # Generate summary
        self.generate_summary()
        
        return True

    def generate_summary(self):
        """Generate test summary"""
        print()
        print("=" * 80)
        print("🎯 COLLECTION SYNCHRONIZATION TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical issues
        critical_issues = []
        for result in self.results:
            if not result['success']:
                if any(keyword in result['test'].lower() for keyword in ['authentication', 'synchronization', 'collection']):
                    critical_issues.append(result['test'])
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   - {issue}")
            print()
        
        # Test results by category
        print("📊 DETAILED RESULTS:")
        for result in self.results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"   {status}: {result['test']}")
            if result['details']:
                print(f"      {result['details']}")
        
        print()
        print("=" * 80)
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 COLLECTION SYNCHRONIZATION FIXES: EXCELLENT - Production Ready!")
        elif success_rate >= 75:
            print("✅ COLLECTION SYNCHRONIZATION FIXES: GOOD - Minor issues to address")
        elif success_rate >= 50:
            print("⚠️ COLLECTION SYNCHRONIZATION FIXES: MODERATE - Several issues need fixing")
        else:
            print("🚨 COLLECTION SYNCHRONIZATION FIXES: CRITICAL - Major issues require immediate attention")

if __name__ == "__main__":
    tester = CollectionSyncTester()
    tester.run_all_tests()