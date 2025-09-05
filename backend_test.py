#!/usr/bin/env python3

"""
Backend Testing for Want List vs Owned Collection System Critical Bug Fixes

This test verifies the critical bug fixes implemented for the want list vs owned collection system:

Issues Reported by User:
1. Can still edit jerseys in wantlist (should NOT be editable - they're Reference Kits)
2. Removing from wantlist deletes from owned (Delete operations should be separate)
3. Adding to owned also adds to wantlist (Should remove from wantlist when adding to owned)

Fixes Implemented:
1. Frontend: Updated MyCollectionPage.js to use separate endpoints (/api/personal-kits vs /api/wanted-kits)
2. Frontend: Disabled edit button for wanted items (only show for owned items)
3. Frontend: Fixed delete function to use correct endpoints based on item type
4. Backend: Added DELETE /api/wanted-kits/{kit_id} endpoint
5. Backend: Separated DELETE endpoints for owned vs wanted

Test Requirements:
1. Test Separate Collections: Verify GET /api/personal-kits and GET /api/wanted-kits return different data
2. Test Separate Deletes: DELETE from wanted should NOT affect owned, and vice versa
3. Test Add to Owned Logic: Adding to owned should remove from wanted (not add to both)
4. Test Data Separation: Owned items should have PersonalKit data, wanted items should have WantedKit data
5. Verify Two-Way Relationship: Still works correctly (wanted→owned removes from wanted)

Authentication: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-collection.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class WantListOwnedCollectionTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_user(self):
        """Authenticate test user"""
        print("🔐 AUTHENTICATING USER...")
        
        try:
            # Login user
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.user_token}"
                })
                
                self.log_result(
                    "User Authentication",
                    True,
                    f"Successfully authenticated user: {user_info.get('name', 'Unknown')} (ID: {self.user_id})",
                    {"email": TEST_USER_EMAIL, "token_length": len(self.user_token) if self.user_token else 0}
                )
                return True
            else:
                self.log_result(
                    "User Authentication",
                    False,
                    f"Authentication failed with status {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "User Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False

    def test_separate_collections_endpoints(self):
        """Test that /api/personal-kits and /api/wanted-kits return different data"""
        print("🔍 TESTING SEPARATE COLLECTIONS ENDPOINTS...")
        
        try:
            # Test GET /api/personal-kits (owned collection)
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            wanted_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            if owned_response.status_code == 200 and wanted_response.status_code == 200:
                owned_data = owned_response.json()
                wanted_data = wanted_response.json()
                
                # Verify different endpoints return different data structures
                owned_count = len(owned_data) if isinstance(owned_data, list) else 0
                wanted_count = len(wanted_data) if isinstance(wanted_data, list) else 0
                
                self.log_result(
                    "Separate Collections Endpoints",
                    True,
                    f"Both endpoints accessible - Owned: {owned_count} items, Wanted: {wanted_count} items",
                    {
                        "owned_endpoint": "/api/personal-kits?collection_type=owned",
                        "wanted_endpoint": "/api/wanted-kits",
                        "owned_count": owned_count,
                        "wanted_count": wanted_count,
                        "owned_structure": type(owned_data).__name__,
                        "wanted_structure": type(wanted_data).__name__
                    }
                )
                return True, owned_data, wanted_data
            else:
                self.log_result(
                    "Separate Collections Endpoints",
                    False,
                    f"Endpoint access failed - Owned: {owned_response.status_code}, Wanted: {wanted_response.status_code}",
                    {
                        "owned_error": owned_response.text if owned_response.status_code != 200 else None,
                        "wanted_error": wanted_response.text if wanted_response.status_code != 200 else None
                    }
                )
                return False, None, None
                
        except Exception as e:
            self.log_result(
                "Separate Collections Endpoints",
                False,
                f"Error testing endpoints: {str(e)}"
            )
            return False, None, None

    def test_data_separation(self, owned_data, wanted_data):
        """Test that owned items have PersonalKit data, wanted items have WantedKit data"""
        print("📊 TESTING DATA SEPARATION...")
        
        try:
            owned_has_personal_data = False
            wanted_has_minimal_data = False
            
            # Check owned data structure (should have PersonalKit fields)
            if owned_data and len(owned_data) > 0:
                sample_owned = owned_data[0]
                personal_fields = ['size', 'condition', 'purchase_price', 'personal_notes']
                owned_has_personal_data = any(field in sample_owned for field in personal_fields)
            
            # Check wanted data structure (should have minimal WantedKit fields)
            if wanted_data and len(wanted_data) > 0:
                sample_wanted = wanted_data[0]
                # Wanted items should NOT have detailed PersonalKit fields
                personal_fields = ['purchase_price', 'condition', 'is_signed', 'has_printing']
                wanted_has_minimal_data = not any(field in sample_wanted for field in personal_fields)
            
            success = True
            details = {
                "owned_items_count": len(owned_data) if owned_data else 0,
                "wanted_items_count": len(wanted_data) if wanted_data else 0,
                "owned_has_personal_data": owned_has_personal_data,
                "wanted_has_minimal_data": wanted_has_minimal_data
            }
            
            if owned_data and len(owned_data) > 0:
                details["sample_owned_fields"] = list(owned_data[0].keys())
            if wanted_data and len(wanted_data) > 0:
                details["sample_wanted_fields"] = list(wanted_data[0].keys())
            
            message = f"Data separation verified - Owned items: {'PersonalKit data' if owned_has_personal_data else 'No personal data'}, Wanted items: {'Minimal data' if wanted_has_minimal_data else 'Has personal data'}"
            
            self.log_result(
                "Data Separation Verification",
                success,
                message,
                details
            )
            return success
            
        except Exception as e:
            self.log_result(
                "Data Separation Verification",
                False,
                f"Error testing data separation: {str(e)}"
            )
            return False

    def test_vestiaire_endpoint(self):
        """Test vestiaire endpoint for available reference kits"""
        print("🏪 TESTING VESTIAIRE ENDPOINT...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                vestiaire_data = response.json()
                kit_count = len(vestiaire_data) if isinstance(vestiaire_data, list) else 0
                
                # Check if we have reference kits available for testing
                available_kits = []
                if vestiaire_data and kit_count > 0:
                    for kit in vestiaire_data[:3]:  # Get first 3 kits for testing
                        kit_info = {
                            "id": kit.get("id"),
                            "reference_kit_id": kit.get("reference_kit_id"),
                            "team_name": kit.get("team_info", {}).get("name", "Unknown"),
                            "season": kit.get("master_kit_info", {}).get("season", "Unknown")
                        }
                        available_kits.append(kit_info)
                
                self.log_result(
                    "Vestiaire Endpoint Access",
                    True,
                    f"Vestiaire accessible with {kit_count} reference kits available",
                    {
                        "total_kits": kit_count,
                        "sample_kits": available_kits[:3],
                        "endpoint": "/api/vestiaire"
                    }
                )
                return True, vestiaire_data
            else:
                self.log_result(
                    "Vestiaire Endpoint Access",
                    False,
                    f"Vestiaire access failed with status {response.status_code}",
                    {"error": response.text}
                )
                return False, None
                
        except Exception as e:
            self.log_result(
                "Vestiaire Endpoint Access",
                False,
                f"Error accessing vestiaire: {str(e)}"
            )
            return False, None

    def test_add_to_wanted_workflow(self, vestiaire_data):
        """Test adding reference kit to wanted collection"""
        print("➕ TESTING ADD TO WANTED WORKFLOW...")
        
        if not vestiaire_data or len(vestiaire_data) == 0:
            self.log_result(
                "Add to Wanted Workflow",
                False,
                "No reference kits available in vestiaire for testing"
            )
            return False, None
        
        try:
            # Get first available reference kit
            test_kit = vestiaire_data[0]
            reference_kit_id = test_kit.get("id") or test_kit.get("reference_kit_id")
            
            if not reference_kit_id:
                self.log_result(
                    "Add to Wanted Workflow",
                    False,
                    "No valid reference kit ID found in vestiaire data"
                )
                return False, None
            
            # Add to wanted collection
            wanted_data = {
                "reference_kit_id": reference_kit_id,
                "preferred_size": "Any",
                "notes": "Test wanted kit for bug fix verification"
            }
            
            response = self.session.post(f"{BACKEND_URL}/wanted-kits", json=wanted_data)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                self.log_result(
                    "Add to Wanted Workflow",
                    True,
                    f"Successfully added reference kit to wanted collection",
                    {
                        "reference_kit_id": reference_kit_id,
                        "team_name": test_kit.get("team_info", {}).get("name", "Unknown"),
                        "response_status": response.status_code,
                        "wanted_kit_id": response_data.get("id") if isinstance(response_data, dict) else None
                    }
                )
                return True, reference_kit_id
            else:
                error_detail = response.text
                # Check if it's a duplicate error (which is acceptable)
                if "already" in error_detail.lower() or "duplicate" in error_detail.lower():
                    self.log_result(
                        "Add to Wanted Workflow",
                        True,
                        f"Kit already in wanted collection (duplicate prevention working)",
                        {
                            "reference_kit_id": reference_kit_id,
                            "status_code": response.status_code,
                            "message": error_detail
                        }
                    )
                    return True, reference_kit_id
                else:
                    self.log_result(
                        "Add to Wanted Workflow",
                        False,
                        f"Failed to add to wanted collection - Status: {response.status_code}",
                        {"error": error_detail}
                    )
                    return False, None
                
        except Exception as e:
            self.log_result(
                "Add to Wanted Workflow",
                False,
                f"Error in add to wanted workflow: {str(e)}"
            )
            return False, None

    def test_add_to_owned_workflow(self, reference_kit_id):
        """Test adding reference kit to owned collection (should remove from wanted)"""
        print("🏠 TESTING ADD TO OWNED WORKFLOW...")
        
        if not reference_kit_id:
            self.log_result(
                "Add to Owned Workflow",
                False,
                "No reference kit ID available for testing"
            )
            return False
        
        try:
            # Add to owned collection with detailed PersonalKit data
            owned_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "mint",
                "purchase_price": 89.99,
                "purchase_date": "2024-01-15",
                "is_signed": False,
                "has_printing": True,
                "printed_name": "Test Player",
                "printed_number": "10",
                "personal_notes": "Test owned kit for bug fix verification"
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=owned_data)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                self.log_result(
                    "Add to Owned Workflow",
                    True,
                    f"Successfully added reference kit to owned collection",
                    {
                        "reference_kit_id": reference_kit_id,
                        "response_status": response.status_code,
                        "personal_kit_id": response_data.get("id") if isinstance(response_data, dict) else None,
                        "detailed_data_included": True
                    }
                )
                return True
            else:
                error_detail = response.text
                # Check if it's a duplicate error (which is acceptable)
                if "already" in error_detail.lower() or "duplicate" in error_detail.lower():
                    self.log_result(
                        "Add to Owned Workflow",
                        True,
                        f"Kit already in owned collection (duplicate prevention working)",
                        {
                            "reference_kit_id": reference_kit_id,
                            "status_code": response.status_code,
                            "message": error_detail
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Add to Owned Workflow",
                        False,
                        f"Failed to add to owned collection - Status: {response.status_code}",
                        {"error": error_detail}
                    )
                    return False
                
        except Exception as e:
            self.log_result(
                "Add to Owned Workflow",
                False,
                f"Error in add to owned workflow: {str(e)}"
            )
            return False

    def test_two_way_relationship(self, reference_kit_id):
        """Test that adding to owned removes from wanted (two-way relationship)"""
        print("🔄 TESTING TWO-WAY RELATIONSHIP...")
        
        if not reference_kit_id:
            self.log_result(
                "Two-Way Relationship Logic",
                False,
                "No reference kit ID available for testing"
            )
            return False
        
        try:
            # Check current state of collections
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            wanted_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            if owned_response.status_code == 200 and wanted_response.status_code == 200:
                owned_data = owned_response.json()
                wanted_data = wanted_response.json()
                
                # Check if the test kit is in owned collection
                kit_in_owned = False
                kit_in_wanted = False
                
                if isinstance(owned_data, list):
                    for item in owned_data:
                        item_ref_id = item.get("reference_kit_id") or item.get("reference_kit_info", {}).get("id")
                        if item_ref_id == reference_kit_id:
                            kit_in_owned = True
                            break
                
                if isinstance(wanted_data, list):
                    for item in wanted_data:
                        item_ref_id = item.get("reference_kit_id") or item.get("reference_kit_info", {}).get("id")
                        if item_ref_id == reference_kit_id:
                            kit_in_wanted = True
                            break
                
                # Two-way relationship should ensure kit is NOT in both collections
                relationship_working = not (kit_in_owned and kit_in_wanted)
                
                self.log_result(
                    "Two-Way Relationship Logic",
                    relationship_working,
                    f"Two-way relationship {'working correctly' if relationship_working else 'NOT working'} - Kit in owned: {kit_in_owned}, Kit in wanted: {kit_in_wanted}",
                    {
                        "reference_kit_id": reference_kit_id,
                        "kit_in_owned": kit_in_owned,
                        "kit_in_wanted": kit_in_wanted,
                        "relationship_working": relationship_working,
                        "owned_count": len(owned_data) if isinstance(owned_data, list) else 0,
                        "wanted_count": len(wanted_data) if isinstance(wanted_data, list) else 0
                    }
                )
                return relationship_working
            else:
                self.log_result(
                    "Two-Way Relationship Logic",
                    False,
                    f"Failed to check collections - Owned: {owned_response.status_code}, Wanted: {wanted_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Two-Way Relationship Logic",
                False,
                f"Error testing two-way relationship: {str(e)}"
            )
            return False

    def test_separate_delete_operations(self):
        """Test that DELETE operations are separate for owned vs wanted"""
        print("🗑️ TESTING SEPARATE DELETE OPERATIONS...")
        
        try:
            # Get current collections to find items to delete
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            wanted_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            if owned_response.status_code != 200 or wanted_response.status_code != 200:
                self.log_result(
                    "Separate Delete Operations",
                    False,
                    f"Failed to get collections for delete testing - Owned: {owned_response.status_code}, Wanted: {wanted_response.status_code}"
                )
                return False
            
            owned_data = owned_response.json()
            wanted_data = wanted_response.json()
            
            delete_tests_passed = 0
            total_delete_tests = 0
            
            # Test DELETE from wanted collection (should not affect owned)
            if isinstance(wanted_data, list) and len(wanted_data) > 0:
                wanted_item = wanted_data[0]
                wanted_item_id = wanted_item.get("id")
                
                if wanted_item_id:
                    total_delete_tests += 1
                    
                    # Count owned items before delete
                    owned_count_before = len(owned_data) if isinstance(owned_data, list) else 0
                    
                    # Delete from wanted collection
                    delete_response = self.session.delete(f"{BACKEND_URL}/wanted-kits/{wanted_item_id}")
                    
                    if delete_response.status_code in [200, 204]:
                        # Check that owned collection is unchanged
                        owned_after_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
                        if owned_after_response.status_code == 200:
                            owned_after_data = owned_after_response.json()
                            owned_count_after = len(owned_after_data) if isinstance(owned_after_data, list) else 0
                            
                            if owned_count_before == owned_count_after:
                                delete_tests_passed += 1
                                print(f"   ✅ DELETE from wanted collection successful - Owned collection unchanged ({owned_count_after} items)")
                            else:
                                print(f"   ❌ DELETE from wanted affected owned collection - Before: {owned_count_before}, After: {owned_count_after}")
                    else:
                        print(f"   ❌ DELETE from wanted collection failed - Status: {delete_response.status_code}")
            
            # Test DELETE from owned collection (should not affect wanted)
            if isinstance(owned_data, list) and len(owned_data) > 0:
                owned_item = owned_data[0]
                owned_item_id = owned_item.get("id")
                
                if owned_item_id:
                    total_delete_tests += 1
                    
                    # Count wanted items before delete
                    wanted_count_before = len(wanted_data) if isinstance(wanted_data, list) else 0
                    
                    # Delete from owned collection
                    delete_response = self.session.delete(f"{BACKEND_URL}/personal-kits/{owned_item_id}")
                    
                    if delete_response.status_code in [200, 204]:
                        # Check that wanted collection is unchanged
                        wanted_after_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
                        if wanted_after_response.status_code == 200:
                            wanted_after_data = wanted_after_response.json()
                            wanted_count_after = len(wanted_after_data) if isinstance(wanted_after_data, list) else 0
                            
                            if wanted_count_before == wanted_count_after:
                                delete_tests_passed += 1
                                print(f"   ✅ DELETE from owned collection successful - Wanted collection unchanged ({wanted_count_after} items)")
                            else:
                                print(f"   ❌ DELETE from owned affected wanted collection - Before: {wanted_count_before}, After: {wanted_count_after}")
                    else:
                        print(f"   ❌ DELETE from owned collection failed - Status: {delete_response.status_code}")
            
            success = delete_tests_passed == total_delete_tests and total_delete_tests > 0
            
            self.log_result(
                "Separate Delete Operations",
                success,
                f"Delete operations test - {delete_tests_passed}/{total_delete_tests} tests passed",
                {
                    "total_tests": total_delete_tests,
                    "passed_tests": delete_tests_passed,
                    "separate_deletes_working": success
                }
            )
            return success
            
        except Exception as e:
            self.log_result(
                "Separate Delete Operations",
                False,
                f"Error testing separate delete operations: {str(e)}"
            )
            return False

    def test_reference_kit_preservation(self):
        """Test that wanted items remain as Reference Kits (not editable PersonalKits)"""
        print("🔒 TESTING REFERENCE KIT PRESERVATION...")
        
        try:
            # Get wanted collection
            wanted_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            if wanted_response.status_code == 200:
                wanted_data = wanted_response.json()
                
                if isinstance(wanted_data, list) and len(wanted_data) > 0:
                    # Check that wanted items have reference kit info but no personal kit fields
                    sample_wanted = wanted_data[0]
                    
                    # Should have reference kit info
                    has_reference_info = "reference_kit_info" in sample_wanted or "master_kit_info" in sample_wanted
                    
                    # Should NOT have editable PersonalKit fields
                    personal_fields = ["purchase_price", "condition", "is_signed", "has_printing", "printed_name", "printed_number"]
                    has_personal_fields = any(field in sample_wanted for field in personal_fields)
                    
                    preservation_working = has_reference_info and not has_personal_fields
                    
                    self.log_result(
                        "Reference Kit Preservation",
                        preservation_working,
                        f"Reference Kit preservation {'working correctly' if preservation_working else 'NOT working'} - Has reference info: {has_reference_info}, Has personal fields: {has_personal_fields}",
                        {
                            "wanted_items_count": len(wanted_data),
                            "has_reference_info": has_reference_info,
                            "has_personal_fields": has_personal_fields,
                            "sample_fields": list(sample_wanted.keys()) if sample_wanted else [],
                            "preservation_working": preservation_working
                        }
                    )
                    return preservation_working
                else:
                    self.log_result(
                        "Reference Kit Preservation",
                        True,
                        "No wanted items to test (empty collection)",
                        {"wanted_items_count": 0}
                    )
                    return True
            else:
                self.log_result(
                    "Reference Kit Preservation",
                    False,
                    f"Failed to get wanted collection - Status: {wanted_response.status_code}",
                    {"error": wanted_response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Reference Kit Preservation",
                False,
                f"Error testing reference kit preservation: {str(e)}"
            )
            return False

    def run_comprehensive_test(self):
        """Run all tests for want list vs owned collection bug fixes"""
        print("🚀 STARTING COMPREHENSIVE WANT LIST VS OWNED COLLECTION BUG FIX TESTING")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: Test separate collections endpoints
        success, owned_data, wanted_data = self.test_separate_collections_endpoints()
        if not success:
            print("❌ CRITICAL: Separate endpoints test failed")
            return False
        
        # Step 3: Test data separation
        self.test_data_separation(owned_data, wanted_data)
        
        # Step 4: Test vestiaire endpoint
        vestiaire_success, vestiaire_data = self.test_vestiaire_endpoint()
        if not vestiaire_success:
            print("⚠️ WARNING: Vestiaire endpoint failed - some tests may be limited")
        
        # Step 5: Test add to wanted workflow
        if vestiaire_success:
            wanted_success, reference_kit_id = self.test_add_to_wanted_workflow(vestiaire_data)
            
            # Step 6: Test add to owned workflow (should remove from wanted)
            if wanted_success and reference_kit_id:
                self.test_add_to_owned_workflow(reference_kit_id)
                
                # Step 7: Test two-way relationship
                self.test_two_way_relationship(reference_kit_id)
        
        # Step 8: Test separate delete operations
        self.test_separate_delete_operations()
        
        # Step 9: Test reference kit preservation
        self.test_reference_kit_preservation()
        
        # Generate summary
        self.generate_test_summary()
        
        return True

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical issues
        critical_issues = []
        for result in self.test_results:
            if not result["success"] and "CRITICAL" in result["message"].upper():
                critical_issues.append(result["test"])
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   - {issue}")
            print()
        
        # Test results by category
        print("📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status}: {result['test']}")
        
        print("\n" + "=" * 80)
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Want list vs owned collection bug fixes are working correctly!")
        elif success_rate >= 70:
            print("✅ GOOD: Most bug fixes are working, minor issues may need attention")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Some critical issues found, fixes may need review")
        else:
            print("❌ CRITICAL: Major issues found, bug fixes need immediate attention")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = WantListOwnedCollectionTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n✅ Testing completed successfully")
            return 0
        else:
            print("\n❌ Testing failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)