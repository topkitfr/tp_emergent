#!/usr/bin/env python3

"""
Frontend DELETE Simulation Test

This test simulates the exact frontend behavior to identify why the user
reports they can't remove items from collections. We'll test:

1. The exact API calls the frontend makes
2. Different item ID formats that might be sent
3. Authentication token issues
4. Response handling that might cause frontend errors

Based on the review request, the issue might be:
- Frontend sending wrong item ID format
- Frontend not handling the activeTab logic correctly
- Authentication issues with DELETE requests
- Item object vs item.id confusion
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class FrontendSimulationTester:
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

    def setup_test_collections(self):
        """Setup test collections with items to delete"""
        print("🏗️ SETTING UP TEST COLLECTIONS...")
        
        try:
            # Get vestiaire data
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            if vestiaire_response.status_code != 200:
                self.log_result(
                    "Setup Test Collections",
                    False,
                    f"Failed to get vestiaire data: {vestiaire_response.status_code}"
                )
                return False, None, None
            
            vestiaire_data = vestiaire_response.json()
            if len(vestiaire_data) < 2:
                self.log_result(
                    "Setup Test Collections",
                    False,
                    f"Not enough reference kits in vestiaire: {len(vestiaire_data)}"
                )
                return False, None, None
            
            # Add items to both collections
            kit1 = vestiaire_data[0]
            kit2 = vestiaire_data[1] if len(vestiaire_data) > 1 else vestiaire_data[0]
            
            # Add to wanted collection
            wanted_data = {
                "reference_kit_id": kit1.get("id"),
                "preferred_size": "L",
                "notes": "Test wanted item for frontend simulation"
            }
            wanted_response = self.session.post(f"{BACKEND_URL}/wanted-kits", json=wanted_data)
            
            # Add to owned collection  
            owned_data = {
                "reference_kit_id": kit2.get("id"),
                "collection_type": "owned",
                "size": "M",
                "condition": "good",
                "purchase_price": 85.00,
                "personal_notes": "Test owned item for frontend simulation"
            }
            owned_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=owned_data)
            
            # Get the created items
            owned_items_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            wanted_items_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            owned_items = owned_items_response.json() if owned_items_response.status_code == 200 else []
            wanted_items = wanted_items_response.json() if wanted_items_response.status_code == 200 else []
            
            self.log_result(
                "Setup Test Collections",
                True,
                f"Setup complete - Owned: {len(owned_items)} items, Wanted: {len(wanted_items)} items",
                {
                    "owned_add_status": owned_response.status_code,
                    "wanted_add_status": wanted_response.status_code,
                    "owned_count": len(owned_items),
                    "wanted_count": len(wanted_items)
                }
            )
            
            return True, owned_items, wanted_items
            
        except Exception as e:
            self.log_result(
                "Setup Test Collections",
                False,
                f"Error setting up collections: {str(e)}"
            )
            return False, None, None

    def test_frontend_delete_simulation(self, owned_items, wanted_items):
        """Simulate exact frontend DELETE behavior"""
        print("🎭 SIMULATING FRONTEND DELETE BEHAVIOR...")
        
        test_scenarios = []
        
        # Test 1: Delete from owned collection (activeTab = 'owned')
        if owned_items and len(owned_items) > 0:
            owned_item = owned_items[0]
            
            # Scenario 1a: Correct endpoint with item.id
            test_scenarios.append({
                "name": "Owned Collection - Correct ID",
                "method": "DELETE",
                "url": f"{BACKEND_URL}/personal-kits/{owned_item.get('id')}",
                "expected_success": True,
                "item_type": "owned",
                "item_id": owned_item.get('id')
            })
            
            # Scenario 1b: Wrong endpoint (using wanted endpoint for owned item)
            test_scenarios.append({
                "name": "Owned Collection - Wrong Endpoint",
                "method": "DELETE", 
                "url": f"{BACKEND_URL}/wanted-kits/{owned_item.get('id')}",
                "expected_success": False,
                "item_type": "owned",
                "item_id": owned_item.get('id')
            })
        
        # Test 2: Delete from wanted collection (activeTab = 'wanted')
        if wanted_items and len(wanted_items) > 0:
            wanted_item = wanted_items[0]
            
            # Scenario 2a: Correct endpoint with item.id
            test_scenarios.append({
                "name": "Wanted Collection - Correct ID",
                "method": "DELETE",
                "url": f"{BACKEND_URL}/wanted-kits/{wanted_item.get('id')}",
                "expected_success": True,
                "item_type": "wanted",
                "item_id": wanted_item.get('id')
            })
            
            # Scenario 2b: Wrong endpoint (using owned endpoint for wanted item)
            test_scenarios.append({
                "name": "Wanted Collection - Wrong Endpoint",
                "method": "DELETE",
                "url": f"{BACKEND_URL}/personal-kits/{wanted_item.get('id')}",
                "expected_success": False,
                "item_type": "wanted", 
                "item_id": wanted_item.get('id')
            })
        
        # Test 3: Common frontend mistakes
        if owned_items and len(owned_items) > 0:
            owned_item = owned_items[0]
            
            # Scenario 3a: Sending entire item object instead of just ID
            test_scenarios.append({
                "name": "Owned Collection - Entire Object as ID",
                "method": "DELETE",
                "url": f"{BACKEND_URL}/personal-kits/{json.dumps(owned_item)}",
                "expected_success": False,
                "item_type": "owned",
                "item_id": json.dumps(owned_item)
            })
            
            # Scenario 3b: Using reference_kit_id instead of item id
            ref_kit_id = owned_item.get('reference_kit_id')
            if ref_kit_id:
                test_scenarios.append({
                    "name": "Owned Collection - Reference Kit ID",
                    "method": "DELETE",
                    "url": f"{BACKEND_URL}/personal-kits/{ref_kit_id}",
                    "expected_success": False,
                    "item_type": "owned",
                    "item_id": ref_kit_id
                })
        
        # Execute test scenarios
        results = []
        for scenario in test_scenarios:
            try:
                print(f"   Testing: {scenario['name']}")
                
                response = self.session.delete(scenario['url'])
                
                success = (response.status_code in [200, 204]) == scenario['expected_success']
                
                result = {
                    "scenario": scenario['name'],
                    "success": success,
                    "status_code": response.status_code,
                    "expected_success": scenario['expected_success'],
                    "actual_success": response.status_code in [200, 204],
                    "response_text": response.text[:100],
                    "item_type": scenario['item_type'],
                    "item_id": scenario['item_id'][:50] if isinstance(scenario['item_id'], str) else str(scenario['item_id'])[:50]
                }
                
                results.append(result)
                
                status = "✅" if success else "❌"
                print(f"     {status} Status: {response.status_code}, Expected success: {scenario['expected_success']}")
                
            except Exception as e:
                results.append({
                    "scenario": scenario['name'],
                    "success": False,
                    "error": str(e),
                    "item_type": scenario['item_type']
                })
                print(f"     ❌ Error: {str(e)}")
        
        # Analyze results
        total_scenarios = len(results)
        correct_behaviors = sum(1 for r in results if r.get('success', False))
        
        self.log_result(
            "Frontend DELETE Simulation",
            correct_behaviors == total_scenarios,
            f"Frontend simulation results: {correct_behaviors}/{total_scenarios} scenarios behaved as expected",
            {
                "total_scenarios": total_scenarios,
                "correct_behaviors": correct_behaviors,
                "detailed_results": results
            }
        )
        
        return results

    def test_authentication_edge_cases(self):
        """Test authentication edge cases that might cause frontend issues"""
        print("🔐 TESTING AUTHENTICATION EDGE CASES...")
        
        try:
            # Test 1: Expired token simulation
            old_auth = self.session.headers.get('Authorization', '')
            
            # Test with malformed token
            self.session.headers.update({'Authorization': 'Bearer invalid-token-12345'})
            
            response = self.session.delete(f"{BACKEND_URL}/personal-kits/test-id")
            malformed_token_handled = response.status_code == 401
            
            # Test with missing Bearer prefix
            self.session.headers.update({'Authorization': self.user_token})
            
            response = self.session.delete(f"{BACKEND_URL}/personal-kits/test-id")
            missing_bearer_handled = response.status_code == 401
            
            # Restore correct auth
            self.session.headers.update({'Authorization': old_auth})
            
            auth_edge_cases_working = malformed_token_handled and missing_bearer_handled
            
            self.log_result(
                "Authentication Edge Cases",
                auth_edge_cases_working,
                f"Authentication edge cases {'handled correctly' if auth_edge_cases_working else 'need attention'}",
                {
                    "malformed_token_handled": malformed_token_handled,
                    "missing_bearer_handled": missing_bearer_handled
                }
            )
            
            return auth_edge_cases_working
            
        except Exception as e:
            self.log_result(
                "Authentication Edge Cases",
                False,
                f"Error testing authentication edge cases: {str(e)}"
            )
            return False

    def test_cors_and_headers(self):
        """Test CORS and header issues that might affect frontend"""
        print("🌐 TESTING CORS AND HEADERS...")
        
        try:
            # Test with different headers that frontend might send
            test_headers = [
                {'Content-Type': 'application/json'},
                {'Content-Type': 'application/json', 'Accept': 'application/json'},
                {'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'},
            ]
            
            results = []
            
            for headers in test_headers:
                # Create a new session with test headers
                test_session = requests.Session()
                test_session.headers.update({'Authorization': f'Bearer {self.user_token}'})
                test_session.headers.update(headers)
                
                # Test DELETE request
                response = test_session.delete(f"{BACKEND_URL}/personal-kits/non-existent-id")
                
                # Should get 404 (not CORS error)
                cors_working = response.status_code == 404
                
                results.append({
                    "headers": headers,
                    "status_code": response.status_code,
                    "cors_working": cors_working
                })
            
            all_cors_working = all(r['cors_working'] for r in results)
            
            self.log_result(
                "CORS and Headers",
                all_cors_working,
                f"CORS and headers {'working correctly' if all_cors_working else 'may have issues'}",
                {"test_results": results}
            )
            
            return all_cors_working
            
        except Exception as e:
            self.log_result(
                "CORS and Headers",
                False,
                f"Error testing CORS and headers: {str(e)}"
            )
            return False

    def run_comprehensive_frontend_simulation(self):
        """Run comprehensive frontend simulation testing"""
        print("🚀 STARTING COMPREHENSIVE FRONTEND DELETE SIMULATION")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: Setup test collections
        success, owned_items, wanted_items = self.setup_test_collections()
        if not success:
            print("❌ CRITICAL: Failed to setup test collections")
            return False
        
        # Step 3: Test frontend DELETE simulation
        self.test_frontend_delete_simulation(owned_items, wanted_items)
        
        # Step 4: Test authentication edge cases
        self.test_authentication_edge_cases()
        
        # Step 5: Test CORS and headers
        self.test_cors_and_headers()
        
        # Generate summary
        self.generate_test_summary()
        
        return True

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 FRONTEND DELETE SIMULATION SUMMARY")
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
        
        # Identify potential frontend issues
        frontend_issues = []
        for result in self.test_results:
            if not result["success"]:
                frontend_issues.append(result["test"])
        
        if frontend_issues:
            print("🚨 POTENTIAL FRONTEND ISSUES IDENTIFIED:")
            for issue in frontend_issues:
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
        
        # Root cause analysis
        print("🔍 ROOT CAUSE ANALYSIS:")
        
        # Check if DELETE endpoints are working
        delete_simulation_result = next((r for r in self.test_results if "Frontend DELETE Simulation" in r["test"]), None)
        if delete_simulation_result and delete_simulation_result.get("details", {}).get("detailed_results"):
            correct_scenarios = [r for r in delete_simulation_result["details"]["detailed_results"] if r.get("success")]
            incorrect_scenarios = [r for r in delete_simulation_result["details"]["detailed_results"] if not r.get("success")]
            
            print(f"   ✅ Correct DELETE operations: {len(correct_scenarios)}")
            print(f"   ❌ Incorrect DELETE operations: {len(incorrect_scenarios)}")
            
            if incorrect_scenarios:
                print("   🔍 Common frontend mistakes detected:")
                for scenario in incorrect_scenarios:
                    if "Wrong Endpoint" in scenario.get("scenario", ""):
                        print("      - Frontend using wrong endpoint for collection type")
                    elif "Entire Object" in scenario.get("scenario", ""):
                        print("      - Frontend sending entire object instead of ID")
                    elif "Reference Kit ID" in scenario.get("scenario", ""):
                        print("      - Frontend using reference_kit_id instead of item ID")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = FrontendSimulationTester()
    
    try:
        success = tester.run_comprehensive_frontend_simulation()
        
        if success:
            print("\n✅ Frontend simulation testing completed")
            return 0
        else:
            print("\n❌ Frontend simulation testing failed")
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