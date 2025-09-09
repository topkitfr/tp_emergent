#!/usr/bin/env python3

"""
DELETE Functionality Critical Bug Testing

CRITICAL BUG REPORT: User reports they can't remove items from either collection (owned or wanted) 
after recent fixes. This is a regression bug that was introduced.

**Issue**: Delete functionality is completely broken for both collections

**What Changed:**
1. Updated `handleDeleteItem` function to use different endpoints based on `activeTab`
2. Added new DELETE endpoints: `/api/wanted-kits/{kit_id}` and updated `/api/personal-kits/{kit_id}`
3. Changed function to pass entire `item` object instead of just `item.id`

**Potential Problems:**
1. The `activeTab` logic might not be working correctly in frontend
2. The item IDs might not match what backend expects
3. The new DELETE endpoints might not be working properly
4. Authentication issues with the DELETE requests

**Testing Focus:**
1. Test DELETE /api/personal-kits/{kit_id} - Verify this endpoint works
2. Test DELETE /api/wanted-kits/{kit_id} - Verify this new endpoint works  
3. Test with real item IDs - Check if the IDs being sent match database records
4. Check authentication - Ensure DELETE requests have proper authorization
5. Test both collection types - Verify delete works for both owned and wanted items

Authentication: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class DeleteFunctionalityTester:
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
                    {
                        "email": TEST_USER_EMAIL, 
                        "token_length": len(self.user_token) if self.user_token else 0,
                        "user_role": user_info.get("role", "unknown")
                    }
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

    def get_user_collections(self):
        """Get user's current collections to identify items for deletion testing"""
        print("📋 GETTING USER COLLECTIONS...")
        
        try:
            # Get owned collections
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            wanted_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            owned_data = []
            wanted_data = []
            
            if owned_response.status_code == 200:
                owned_data = owned_response.json()
                if not isinstance(owned_data, list):
                    owned_data = []
            
            if wanted_response.status_code == 200:
                wanted_data = wanted_response.json()
                if not isinstance(wanted_data, list):
                    wanted_data = []
            
            self.log_result(
                "Get User Collections",
                True,
                f"Retrieved collections - Owned: {len(owned_data)} items, Wanted: {len(wanted_data)} items",
                {
                    "owned_count": len(owned_data),
                    "wanted_count": len(wanted_data),
                    "owned_endpoint_status": owned_response.status_code,
                    "wanted_endpoint_status": wanted_response.status_code,
                    "owned_sample_ids": [item.get("id") for item in owned_data[:3]] if owned_data else [],
                    "wanted_sample_ids": [item.get("id") for item in wanted_data[:3]] if wanted_data else []
                }
            )
            
            return True, owned_data, wanted_data
            
        except Exception as e:
            self.log_result(
                "Get User Collections",
                False,
                f"Error getting collections: {str(e)}"
            )
            return False, [], []

    def test_delete_owned_item(self, owned_data):
        """Test DELETE /api/personal-kits/{kit_id} endpoint"""
        print("🗑️ TESTING DELETE OWNED ITEM...")
        
        if not owned_data or len(owned_data) == 0:
            self.log_result(
                "Delete Owned Item",
                False,
                "No owned items available for deletion testing",
                {"owned_count": 0}
            )
            return False
        
        try:
            # Get the first owned item for testing
            test_item = owned_data[0]
            item_id = test_item.get("id")
            
            if not item_id:
                self.log_result(
                    "Delete Owned Item",
                    False,
                    "No valid item ID found in owned collection",
                    {"test_item_keys": list(test_item.keys()) if test_item else []}
                )
                return False
            
            # Get initial count
            initial_count = len(owned_data)
            
            # Attempt to delete the item
            delete_response = self.session.delete(f"{BACKEND_URL}/personal-kits/{item_id}")
            
            # Check response
            if delete_response.status_code in [200, 204]:
                # Verify deletion by checking collection again
                verify_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
                
                if verify_response.status_code == 200:
                    updated_data = verify_response.json()
                    if not isinstance(updated_data, list):
                        updated_data = []
                    
                    final_count = len(updated_data)
                    deletion_successful = final_count < initial_count
                    
                    # Check if the specific item is gone
                    item_still_exists = any(item.get("id") == item_id for item in updated_data)
                    
                    self.log_result(
                        "Delete Owned Item",
                        deletion_successful and not item_still_exists,
                        f"DELETE /api/personal-kits/{item_id} - Status: {delete_response.status_code}, Count: {initial_count}→{final_count}, Item removed: {not item_still_exists}",
                        {
                            "item_id": item_id,
                            "delete_status": delete_response.status_code,
                            "initial_count": initial_count,
                            "final_count": final_count,
                            "item_still_exists": item_still_exists,
                            "deletion_successful": deletion_successful,
                            "item_info": {
                                "team_name": test_item.get("team_info", {}).get("name", "Unknown"),
                                "season": test_item.get("master_kit_info", {}).get("season", "Unknown")
                            }
                        }
                    )
                    return deletion_successful and not item_still_exists
                else:
                    self.log_result(
                        "Delete Owned Item",
                        False,
                        f"Failed to verify deletion - verification request failed with status {verify_response.status_code}",
                        {"verify_error": verify_response.text}
                    )
                    return False
            else:
                self.log_result(
                    "Delete Owned Item",
                    False,
                    f"DELETE request failed with status {delete_response.status_code}",
                    {
                        "item_id": item_id,
                        "delete_status": delete_response.status_code,
                        "error_response": delete_response.text,
                        "endpoint": f"/api/personal-kits/{item_id}"
                    }
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Delete Owned Item",
                False,
                f"Error testing delete owned item: {str(e)}"
            )
            return False

    def test_delete_wanted_item(self, wanted_data):
        """Test DELETE /api/wanted-kits/{kit_id} endpoint"""
        print("🗑️ TESTING DELETE WANTED ITEM...")
        
        if not wanted_data or len(wanted_data) == 0:
            self.log_result(
                "Delete Wanted Item",
                False,
                "No wanted items available for deletion testing",
                {"wanted_count": 0}
            )
            return False
        
        try:
            # Get the first wanted item for testing
            test_item = wanted_data[0]
            item_id = test_item.get("id")
            
            if not item_id:
                self.log_result(
                    "Delete Wanted Item",
                    False,
                    "No valid item ID found in wanted collection",
                    {"test_item_keys": list(test_item.keys()) if test_item else []}
                )
                return False
            
            # Get initial count
            initial_count = len(wanted_data)
            
            # Attempt to delete the item
            delete_response = self.session.delete(f"{BACKEND_URL}/wanted-kits/{item_id}")
            
            # Check response
            if delete_response.status_code in [200, 204]:
                # Verify deletion by checking collection again
                verify_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
                
                if verify_response.status_code == 200:
                    updated_data = verify_response.json()
                    if not isinstance(updated_data, list):
                        updated_data = []
                    
                    final_count = len(updated_data)
                    deletion_successful = final_count < initial_count
                    
                    # Check if the specific item is gone
                    item_still_exists = any(item.get("id") == item_id for item in updated_data)
                    
                    self.log_result(
                        "Delete Wanted Item",
                        deletion_successful and not item_still_exists,
                        f"DELETE /api/wanted-kits/{item_id} - Status: {delete_response.status_code}, Count: {initial_count}→{final_count}, Item removed: {not item_still_exists}",
                        {
                            "item_id": item_id,
                            "delete_status": delete_response.status_code,
                            "initial_count": initial_count,
                            "final_count": final_count,
                            "item_still_exists": item_still_exists,
                            "deletion_successful": deletion_successful,
                            "item_info": {
                                "team_name": test_item.get("team_info", {}).get("name", "Unknown"),
                                "season": test_item.get("master_kit_info", {}).get("season", "Unknown")
                            }
                        }
                    )
                    return deletion_successful and not item_still_exists
                else:
                    self.log_result(
                        "Delete Wanted Item",
                        False,
                        f"Failed to verify deletion - verification request failed with status {verify_response.status_code}",
                        {"verify_error": verify_response.text}
                    )
                    return False
            else:
                self.log_result(
                    "Delete Wanted Item",
                    False,
                    f"DELETE request failed with status {delete_response.status_code}",
                    {
                        "item_id": item_id,
                        "delete_status": delete_response.status_code,
                        "error_response": delete_response.text,
                        "endpoint": f"/api/wanted-kits/{item_id}"
                    }
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Delete Wanted Item",
                False,
                f"Error testing delete wanted item: {str(e)}"
            )
            return False

    def test_authentication_on_delete_endpoints(self):
        """Test that DELETE endpoints require proper authentication"""
        print("🔐 TESTING AUTHENTICATION ON DELETE ENDPOINTS...")
        
        try:
            # Create a session without authentication
            unauth_session = requests.Session()
            
            # Test DELETE endpoints without authentication
            fake_id = "test-id-12345"
            
            # Test DELETE /api/personal-kits/{id} without auth
            owned_response = unauth_session.delete(f"{BACKEND_URL}/personal-kits/{fake_id}")
            
            # Test DELETE /api/wanted-kits/{id} without auth
            wanted_response = unauth_session.delete(f"{BACKEND_URL}/wanted-kits/{fake_id}")
            
            # Both should return 401 Unauthorized
            owned_auth_required = owned_response.status_code == 401
            wanted_auth_required = wanted_response.status_code == 401
            
            auth_working = owned_auth_required and wanted_auth_required
            
            self.log_result(
                "Authentication on Delete Endpoints",
                auth_working,
                f"Authentication requirement {'working correctly' if auth_working else 'NOT working'} - Owned: {owned_response.status_code}, Wanted: {wanted_response.status_code}",
                {
                    "owned_delete_status": owned_response.status_code,
                    "wanted_delete_status": wanted_response.status_code,
                    "owned_auth_required": owned_auth_required,
                    "wanted_auth_required": wanted_auth_required,
                    "test_id": fake_id
                }
            )
            
            return auth_working
            
        except Exception as e:
            self.log_result(
                "Authentication on Delete Endpoints",
                False,
                f"Error testing authentication: {str(e)}"
            )
            return False

    def test_invalid_id_handling(self):
        """Test how DELETE endpoints handle invalid/non-existent IDs"""
        print("🚫 TESTING INVALID ID HANDLING...")
        
        try:
            # Test with various invalid IDs
            invalid_ids = [
                "non-existent-id-12345",
                "invalid-uuid-format",
                "",
                "null"
            ]
            
            results = []
            
            for invalid_id in invalid_ids:
                if invalid_id == "":
                    # Skip empty ID as it would change the endpoint structure
                    continue
                    
                # Test DELETE /api/personal-kits/{invalid_id}
                owned_response = self.session.delete(f"{BACKEND_URL}/personal-kits/{invalid_id}")
                
                # Test DELETE /api/wanted-kits/{invalid_id}
                wanted_response = self.session.delete(f"{BACKEND_URL}/wanted-kits/{invalid_id}")
                
                # Should return 404 Not Found for non-existent items
                owned_handled = owned_response.status_code in [404, 400]
                wanted_handled = wanted_response.status_code in [404, 400]
                
                results.append({
                    "id": invalid_id,
                    "owned_status": owned_response.status_code,
                    "wanted_status": wanted_response.status_code,
                    "owned_handled": owned_handled,
                    "wanted_handled": wanted_handled
                })
            
            all_handled = all(r["owned_handled"] and r["wanted_handled"] for r in results)
            
            self.log_result(
                "Invalid ID Handling",
                all_handled,
                f"Invalid ID handling {'working correctly' if all_handled else 'needs improvement'} - {len([r for r in results if r['owned_handled'] and r['wanted_handled']])}/{len(results)} tests passed",
                {
                    "test_results": results,
                    "all_handled_correctly": all_handled
                }
            )
            
            return all_handled
            
        except Exception as e:
            self.log_result(
                "Invalid ID Handling",
                False,
                f"Error testing invalid ID handling: {str(e)}"
            )
            return False

    def add_test_items_for_deletion(self):
        """Add test items to collections so we have items to delete"""
        print("➕ ADDING TEST ITEMS FOR DELETION TESTING...")
        
        try:
            # First, get available reference kits from vestiaire
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if vestiaire_response.status_code != 200:
                self.log_result(
                    "Add Test Items",
                    False,
                    f"Failed to get vestiaire data - Status: {vestiaire_response.status_code}",
                    {"vestiaire_error": vestiaire_response.text}
                )
                return False
            
            vestiaire_data = vestiaire_response.json()
            if not isinstance(vestiaire_data, list) or len(vestiaire_data) == 0:
                self.log_result(
                    "Add Test Items",
                    False,
                    "No reference kits available in vestiaire for testing",
                    {"vestiaire_count": len(vestiaire_data) if isinstance(vestiaire_data, list) else 0}
                )
                return False
            
            # Get first available reference kit
            test_kit = vestiaire_data[0]
            reference_kit_id = test_kit.get("id") or test_kit.get("reference_kit_id")
            
            if not reference_kit_id:
                self.log_result(
                    "Add Test Items",
                    False,
                    "No valid reference kit ID found in vestiaire data"
                )
                return False
            
            items_added = 0
            
            # Add to wanted collection
            try:
                wanted_data = {
                    "reference_kit_id": reference_kit_id,
                    "preferred_size": "Any",
                    "notes": "Test item for DELETE functionality testing"
                }
                
                wanted_response = self.session.post(f"{BACKEND_URL}/wanted-kits", json=wanted_data)
                if wanted_response.status_code in [200, 201]:
                    items_added += 1
                elif "already" in wanted_response.text.lower():
                    items_added += 1  # Already exists, which is fine
            except Exception as e:
                print(f"   Warning: Could not add to wanted collection: {e}")
            
            # Add to owned collection
            try:
                owned_data = {
                    "reference_kit_id": reference_kit_id,
                    "collection_type": "owned",
                    "size": "L",
                    "condition": "mint",
                    "purchase_price": 99.99,
                    "personal_notes": "Test item for DELETE functionality testing"
                }
                
                owned_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=owned_data)
                if owned_response.status_code in [200, 201]:
                    items_added += 1
                elif "already" in owned_response.text.lower():
                    items_added += 1  # Already exists, which is fine
            except Exception as e:
                print(f"   Warning: Could not add to owned collection: {e}")
            
            success = items_added > 0
            
            self.log_result(
                "Add Test Items",
                success,
                f"Added {items_added} test items for deletion testing",
                {
                    "reference_kit_id": reference_kit_id,
                    "items_added": items_added,
                    "team_name": test_kit.get("team_info", {}).get("name", "Unknown")
                }
            )
            
            return success
            
        except Exception as e:
            self.log_result(
                "Add Test Items",
                False,
                f"Error adding test items: {str(e)}"
            )
            return False

    def run_comprehensive_delete_test(self):
        """Run comprehensive DELETE functionality testing"""
        print("🚀 STARTING COMPREHENSIVE DELETE FUNCTIONALITY TESTING")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: Test authentication on DELETE endpoints
        self.test_authentication_on_delete_endpoints()
        
        # Step 3: Test invalid ID handling
        self.test_invalid_id_handling()
        
        # Step 4: Add test items if needed
        self.add_test_items_for_deletion()
        
        # Step 5: Get current collections
        success, owned_data, wanted_data = self.get_user_collections()
        if not success:
            print("❌ CRITICAL: Failed to get user collections")
            return False
        
        # Step 6: Test DELETE owned items
        if owned_data and len(owned_data) > 0:
            self.test_delete_owned_item(owned_data)
        else:
            self.log_result(
                "Delete Owned Item",
                False,
                "No owned items available for deletion testing - user may need to add items first",
                {"owned_count": 0}
            )
        
        # Step 7: Test DELETE wanted items
        if wanted_data and len(wanted_data) > 0:
            self.test_delete_wanted_item(wanted_data)
        else:
            self.log_result(
                "Delete Wanted Item",
                False,
                "No wanted items available for deletion testing - user may need to add items first",
                {"wanted_count": 0}
            )
        
        # Generate summary
        self.generate_test_summary()
        
        return True

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 DELETE FUNCTIONALITY TEST SUMMARY")
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
        
        # Critical DELETE functionality issues
        delete_issues = []
        for result in self.test_results:
            if not result["success"] and ("delete" in result["test"].lower() or "Delete" in result["test"]):
                delete_issues.append(result["test"])
        
        if delete_issues:
            print("🚨 CRITICAL DELETE FUNCTIONALITY ISSUES:")
            for issue in delete_issues:
                print(f"   - {issue}")
            print()
        
        # Test results by category
        print("📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status}: {result['test']}")
            if not result["success"]:
                print(f"      Issue: {result['message']}")
        
        print("\n" + "=" * 80)
        
        # Overall assessment for DELETE functionality
        if success_rate >= 90:
            print("🎉 EXCELLENT: DELETE functionality is working correctly!")
        elif success_rate >= 70:
            print("✅ GOOD: Most DELETE operations working, minor issues may need attention")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Some DELETE functionality issues found, needs review")
        else:
            print("❌ CRITICAL: Major DELETE functionality issues found - user report confirmed!")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = DeleteFunctionalityTester()
    
    try:
        success = tester.run_comprehensive_delete_test()
        
        if success:
            print("\n✅ DELETE functionality testing completed")
            return 0
        else:
            print("\n❌ DELETE functionality testing failed")
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