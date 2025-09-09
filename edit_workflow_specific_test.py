#!/usr/bin/env python3

"""
Edit Workflow Specific Test - Testing the exact edit workflow

This test focuses on the specific workflow mentioned in the bug report:
1. User adds jersey from Kit Store → Fills form with details
2. Jersey gets added to owned collection 
3. User clicks edit button on the jersey
4. Edit form is empty/doesn't show the previously entered data

We'll test if there's a specific issue with:
- Different reference kits
- Edge case data values
- Specific field combinations that might cause issues
- Update operations (PUT/PATCH endpoints)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class EditWorkflowTester:
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
            print(f"   Details: {json.dumps(details, indent=2)}")
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
                    f"Successfully authenticated: {user_info.get('name')} (ID: {self.user_id})",
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

    def test_edge_case_data_scenarios(self):
        """Test edge cases that might cause frontend display issues"""
        print("🧪 TESTING EDGE CASE DATA SCENARIOS...")
        
        try:
            # Get existing kit to test edge cases
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                owned_kits = response.json()
                if not owned_kits:
                    self.log_result(
                        "Edge Case Data Scenarios",
                        False,
                        "No owned kits found for edge case testing"
                    )
                    return False
                
                kit = owned_kits[0]
                
                # Test various edge cases that might cause frontend issues
                edge_cases = {
                    "empty_strings": {
                        "signed_by": "",
                        "printed_name": "",
                        "personal_notes": ""
                    },
                    "null_values": {
                        "signed_by": None,
                        "printed_name": None,
                        "personal_notes": None
                    },
                    "special_characters": {
                        "signed_by": "Mbappé & Neymar Jr.",
                        "printed_name": "MBAPPÉ",
                        "personal_notes": "Special chars: àáâãäåæçèéêë & symbols: €$£¥"
                    },
                    "long_text": {
                        "personal_notes": "A" * 1000  # Very long text
                    },
                    "numeric_edge_cases": {
                        "purchase_price": 0.01,  # Very small price
                        "printed_number": 99  # High number
                    }
                }
                
                edge_case_results = {}
                
                for case_name, test_data in edge_cases.items():
                    # Test if these values would cause issues in retrieval
                    simulated_kit = kit.copy()
                    simulated_kit.update(test_data)
                    
                    # Check for potential frontend issues
                    issues = []
                    
                    for field, value in test_data.items():
                        if value == "":
                            issues.append(f"{field} is empty string (might display as blank)")
                        elif value is None:
                            issues.append(f"{field} is null (might cause undefined errors)")
                        elif isinstance(value, str) and len(value) > 500:
                            issues.append(f"{field} is very long ({len(value)} chars)")
                        elif field == "purchase_price" and isinstance(value, (int, float)) and value < 1:
                            issues.append(f"{field} is very small value: {value}")
                    
                    edge_case_results[case_name] = {
                        "test_data": test_data,
                        "potential_issues": issues,
                        "issue_count": len(issues)
                    }
                
                total_issues = sum(result["issue_count"] for result in edge_case_results.values())
                
                self.log_result(
                    "Edge Case Data Scenarios",
                    total_issues == 0,
                    f"Edge case testing completed. Total potential issues: {total_issues}",
                    {
                        "edge_case_results": edge_case_results,
                        "total_potential_issues": total_issues
                    }
                )
                return total_issues == 0
            else:
                self.log_result(
                    "Edge Case Data Scenarios",
                    False,
                    f"Failed to get owned kits: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Edge Case Data Scenarios",
                False,
                f"Error testing edge cases: {str(e)}"
            )
            return False

    def test_individual_kit_retrieval(self):
        """Test retrieving individual kit by ID (what edit form might do)"""
        print("🔍 TESTING INDIVIDUAL KIT RETRIEVAL...")
        
        try:
            # Get list of owned kits first
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                owned_kits = response.json()
                if not owned_kits:
                    self.log_result(
                        "Individual Kit Retrieval",
                        False,
                        "No owned kits found for individual retrieval testing"
                    )
                    return False
                
                kit_id = owned_kits[0]["id"]
                
                # Test if there's a specific endpoint for individual kit retrieval
                # This might be what the edit form uses
                individual_endpoints_to_test = [
                    f"/personal-kits/{kit_id}",
                    f"/users/{self.user_id}/personal-kits/{kit_id}",
                    f"/collections/{kit_id}"
                ]
                
                retrieval_results = {}
                
                for endpoint in individual_endpoints_to_test:
                    try:
                        response = self.session.get(f"{BACKEND_URL}{endpoint}")
                        
                        retrieval_results[endpoint] = {
                            "status_code": response.status_code,
                            "success": response.status_code == 200,
                            "response_size": len(response.text) if response.text else 0
                        }
                        
                        if response.status_code == 200:
                            data = response.json()
                            retrieval_results[endpoint]["data_keys"] = list(data.keys()) if isinstance(data, dict) else "not_dict"
                            retrieval_results[endpoint]["has_edit_fields"] = all(
                                field in data for field in ["id", "size", "condition", "personal_notes"]
                            ) if isinstance(data, dict) else False
                        else:
                            retrieval_results[endpoint]["error"] = response.text
                            
                    except Exception as e:
                        retrieval_results[endpoint] = {
                            "status_code": "error",
                            "success": False,
                            "error": str(e)
                        }
                
                # Check if any individual retrieval endpoint works
                working_endpoints = [ep for ep, result in retrieval_results.items() if result["success"]]
                
                self.log_result(
                    "Individual Kit Retrieval",
                    len(working_endpoints) > 0,
                    f"Individual kit retrieval test. Working endpoints: {len(working_endpoints)}",
                    {
                        "kit_id_tested": kit_id,
                        "retrieval_results": retrieval_results,
                        "working_endpoints": working_endpoints
                    }
                )
                return len(working_endpoints) > 0
            else:
                self.log_result(
                    "Individual Kit Retrieval",
                    False,
                    f"Failed to get owned kits list: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Individual Kit Retrieval",
                False,
                f"Error testing individual kit retrieval: {str(e)}"
            )
            return False

    def test_update_endpoints(self):
        """Test if there are update endpoints that might be used for editing"""
        print("✏️ TESTING UPDATE ENDPOINTS...")
        
        try:
            # Get existing kit
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                owned_kits = response.json()
                if not owned_kits:
                    self.log_result(
                        "Update Endpoints Test",
                        False,
                        "No owned kits found for update testing"
                    )
                    return False
                
                kit = owned_kits[0]
                kit_id = kit["id"]
                
                # Test update data
                update_data = {
                    "personal_notes": "Updated notes for testing edit functionality",
                    "condition": "good",
                    "purchase_price": 95.00
                }
                
                # Test various update endpoints
                update_endpoints_to_test = [
                    {"method": "PUT", "url": f"/personal-kits/{kit_id}"},
                    {"method": "PATCH", "url": f"/personal-kits/{kit_id}"},
                    {"method": "PUT", "url": f"/users/{self.user_id}/personal-kits/{kit_id}"},
                    {"method": "PATCH", "url": f"/users/{self.user_id}/personal-kits/{kit_id}"}
                ]
                
                update_results = {}
                
                for endpoint_info in update_endpoints_to_test:
                    method = endpoint_info["method"]
                    url = endpoint_info["url"]
                    
                    try:
                        if method == "PUT":
                            response = self.session.put(f"{BACKEND_URL}{url}", json=update_data)
                        elif method == "PATCH":
                            response = self.session.patch(f"{BACKEND_URL}{url}", json=update_data)
                        
                        update_results[f"{method} {url}"] = {
                            "status_code": response.status_code,
                            "success": response.status_code in [200, 204],
                            "response": response.text[:200] if response.text else ""
                        }
                        
                    except Exception as e:
                        update_results[f"{method} {url}"] = {
                            "status_code": "error",
                            "success": False,
                            "error": str(e)
                        }
                
                # Check if any update endpoint works
                working_updates = [ep for ep, result in update_results.items() if result["success"]]
                
                self.log_result(
                    "Update Endpoints Test",
                    len(working_updates) > 0,
                    f"Update endpoints test. Working endpoints: {len(working_updates)}",
                    {
                        "kit_id_tested": kit_id,
                        "update_data": update_data,
                        "update_results": update_results,
                        "working_update_endpoints": working_updates
                    }
                )
                return len(working_updates) > 0
            else:
                self.log_result(
                    "Update Endpoints Test",
                    False,
                    f"Failed to get owned kits: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Update Endpoints Test",
                False,
                f"Error testing update endpoints: {str(e)}"
            )
            return False

    def test_date_format_compatibility(self):
        """Test if date formats might cause frontend issues"""
        print("📅 TESTING DATE FORMAT COMPATIBILITY...")
        
        try:
            # Get existing kit
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                owned_kits = response.json()
                if not owned_kits:
                    self.log_result(
                        "Date Format Compatibility",
                        False,
                        "No owned kits found for date format testing"
                    )
                    return False
                
                kit = owned_kits[0]
                purchase_date = kit.get("purchase_date")
                
                date_analysis = {
                    "original_date": purchase_date,
                    "date_type": type(purchase_date).__name__,
                    "is_iso_format": isinstance(purchase_date, str) and "T" in purchase_date,
                    "frontend_compatible": True
                }
                
                # Check for potential date issues
                date_issues = []
                
                if purchase_date:
                    if isinstance(purchase_date, str):
                        if "T" in purchase_date:
                            # ISO format - might need conversion for HTML date input
                            date_issues.append("ISO format might need conversion for HTML date input (YYYY-MM-DD)")
                        
                        # Check if it's a valid date format
                        try:
                            from datetime import datetime
                            if "T" in purchase_date:
                                datetime.fromisoformat(purchase_date.replace("Z", "+00:00"))
                            else:
                                datetime.strptime(purchase_date, "%Y-%m-%d")
                        except ValueError:
                            date_issues.append(f"Invalid date format: {purchase_date}")
                    else:
                        date_issues.append(f"Date is not string type: {type(purchase_date)}")
                
                date_analysis["issues"] = date_issues
                date_analysis["issue_count"] = len(date_issues)
                
                # Test date conversion for frontend
                if purchase_date and isinstance(purchase_date, str) and "T" in purchase_date:
                    try:
                        # Convert ISO to date-only format for HTML input
                        date_only = purchase_date.split("T")[0]
                        date_analysis["converted_for_frontend"] = date_only
                        date_analysis["conversion_successful"] = True
                    except Exception as e:
                        date_analysis["conversion_error"] = str(e)
                        date_analysis["conversion_successful"] = False
                
                all_dates_compatible = len(date_issues) == 0
                
                self.log_result(
                    "Date Format Compatibility",
                    all_dates_compatible,
                    f"Date format analysis. Issues found: {len(date_issues)}",
                    date_analysis
                )
                return all_dates_compatible
            else:
                self.log_result(
                    "Date Format Compatibility",
                    False,
                    f"Failed to get owned kits: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Date Format Compatibility",
                False,
                f"Error testing date format: {str(e)}"
            )
            return False

    def run_comprehensive_test(self):
        """Run the complete edit workflow test"""
        print("🚀 STARTING EDIT WORKFLOW SPECIFIC TEST")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test edge case data scenarios
        edge_cases_ok = self.test_edge_case_data_scenarios()
        
        # Step 3: Test individual kit retrieval
        individual_retrieval_ok = self.test_individual_kit_retrieval()
        
        # Step 4: Test update endpoints
        update_endpoints_ok = self.test_update_endpoints()
        
        # Step 5: Test date format compatibility
        date_format_ok = self.test_date_format_compatibility()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 EDIT WORKFLOW TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Root cause analysis
        print("\n🔍 EDIT WORKFLOW ANALYSIS:")
        if not edge_cases_ok:
            print("❌ ISSUE IDENTIFIED: Edge case data scenarios might cause frontend display issues")
        elif not individual_retrieval_ok:
            print("⚠️ POTENTIAL ISSUE: No individual kit retrieval endpoints found (edit form might use collection list)")
        elif not update_endpoints_ok:
            print("⚠️ POTENTIAL ISSUE: No update endpoints found (edit functionality might be limited)")
        elif not date_format_ok:
            print("⚠️ POTENTIAL ISSUE: Date format compatibility issues detected")
        else:
            print("✅ NO EDIT WORKFLOW ISSUES FOUND: All edit-related functionality appears to work correctly")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = EditWorkflowTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)