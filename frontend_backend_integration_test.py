#!/usr/bin/env python3

"""
Frontend-Backend Integration Test for Personal Kit Edit Issue

This test simulates the exact frontend workflow to identify where the data loss occurs:
1. Frontend adds jersey from Kit Store (POST /api/personal-kits)
2. Frontend retrieves collections for "Ma Collection" page (GET /api/personal-kits?collection_type=owned)
3. Frontend opens edit modal and loads existing data
4. Check if there's any data transformation or field mapping issue

Focus on testing the exact API calls and data structures the frontend expects.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class FrontendBackendIntegrationTester:
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

    def test_vestiaire_endpoint(self):
        """Test vestiaire endpoint that frontend uses to display kits"""
        print("🏪 TESTING VESTIAIRE ENDPOINT...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                kits = response.json()
                
                if kits and len(kits) > 0:
                    sample_kit = kits[0]
                    required_fields = ["id", "team_info", "master_kit_info"]
                    missing_fields = [field for field in required_fields if field not in sample_kit]
                    
                    self.log_result(
                        "Vestiaire Endpoint Structure",
                        len(missing_fields) == 0,
                        f"Vestiaire returns {len(kits)} kits. Missing required fields: {len(missing_fields)}",
                        {
                            "total_kits": len(kits),
                            "missing_fields": missing_fields,
                            "sample_kit_keys": list(sample_kit.keys()),
                            "sample_kit_id": sample_kit.get("id")
                        }
                    )
                    return kits[0] if kits else None
                else:
                    self.log_result(
                        "Vestiaire Endpoint Structure",
                        False,
                        "No kits available in vestiaire"
                    )
                    return None
            else:
                self.log_result(
                    "Vestiaire Endpoint Structure",
                    False,
                    f"Vestiaire endpoint failed: {response.status_code}",
                    {"response": response.text}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Vestiaire Endpoint Structure",
                False,
                f"Error testing vestiaire: {str(e)}"
            )
            return None

    def test_ma_collection_endpoint(self):
        """Test the exact endpoint frontend uses for 'Ma Collection' page"""
        print("📱 TESTING MA COLLECTION ENDPOINT...")
        
        try:
            # Test the endpoint that MyCollectionPage.js uses
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                owned_kits = response.json()
                
                # Analyze the data structure for edit form compatibility
                edit_form_analysis = {}
                if owned_kits and len(owned_kits) > 0:
                    sample_kit = owned_kits[0]
                    
                    # Fields that edit form expects
                    expected_fields = [
                        "id", "size", "condition", "purchase_price", "purchase_date",
                        "is_signed", "signed_by", "has_printing", "printed_name", 
                        "printed_number", "is_worn", "personal_notes"
                    ]
                    
                    for field in expected_fields:
                        edit_form_analysis[field] = {
                            "present": field in sample_kit,
                            "value": sample_kit.get(field),
                            "type": type(sample_kit.get(field)).__name__ if field in sample_kit else "missing",
                            "is_null": sample_kit.get(field) is None if field in sample_kit else True
                        }
                    
                    # Check for potential frontend issues
                    potential_issues = []
                    
                    # Check for null values that might cause frontend issues
                    null_fields = [field for field, data in edit_form_analysis.items() 
                                 if data["is_null"] and field in ["size", "condition"]]
                    if null_fields:
                        potential_issues.append(f"Critical fields are null: {null_fields}")
                    
                    # Check for type mismatches
                    if "printed_number" in sample_kit and not isinstance(sample_kit["printed_number"], (int, type(None))):
                        potential_issues.append(f"printed_number should be int, got {type(sample_kit['printed_number'])}")
                    
                    # Check for date format issues
                    if "purchase_date" in sample_kit and sample_kit["purchase_date"]:
                        date_value = sample_kit["purchase_date"]
                        if not isinstance(date_value, str) or "T" not in date_value:
                            potential_issues.append(f"purchase_date format issue: {date_value}")
                
                self.log_result(
                    "Ma Collection Endpoint Analysis",
                    len(potential_issues) == 0,
                    f"Ma Collection returns {len(owned_kits)} owned kits. Potential issues: {len(potential_issues)}",
                    {
                        "total_owned_kits": len(owned_kits),
                        "edit_form_analysis": edit_form_analysis,
                        "potential_issues": potential_issues,
                        "sample_kit_id": owned_kits[0].get("id") if owned_kits else None
                    }
                )
                return owned_kits[0] if owned_kits else None
            else:
                self.log_result(
                    "Ma Collection Endpoint Analysis",
                    False,
                    f"Ma Collection endpoint failed: {response.status_code}",
                    {"response": response.text}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Ma Collection Endpoint Analysis",
                False,
                f"Error testing Ma Collection endpoint: {str(e)}"
            )
            return None

    def test_edit_form_data_simulation(self, kit_data):
        """Simulate how frontend edit form would process the kit data"""
        print("🖥️ SIMULATING FRONTEND EDIT FORM DATA PROCESSING...")
        
        try:
            # Simulate frontend form field mapping
            form_fields = {
                "size": kit_data.get("size", ""),
                "condition": kit_data.get("condition", ""),
                "purchase_price": kit_data.get("purchase_price", ""),
                "purchase_date": kit_data.get("purchase_date", ""),
                "is_signed": kit_data.get("is_signed", False),
                "signed_by": kit_data.get("signed_by", ""),
                "has_printing": kit_data.get("has_printing", False),
                "printed_name": kit_data.get("printed_name", ""),
                "printed_number": kit_data.get("printed_number", ""),
                "is_worn": kit_data.get("is_worn", False),
                "personal_notes": kit_data.get("personal_notes", "")
            }
            
            # Check for frontend display issues
            display_issues = []
            empty_fields = []
            
            for field, value in form_fields.items():
                if value is None:
                    display_issues.append(f"{field} is null (might display as empty)")
                elif value == "":
                    empty_fields.append(field)
                elif field == "purchase_date" and value and isinstance(value, str):
                    # Check if date needs formatting for frontend
                    if "T" in value:
                        # ISO format - frontend might need to convert this
                        display_issues.append(f"purchase_date in ISO format: {value} (frontend might need conversion)")
            
            # Simulate form population success
            populated_fields = sum(1 for value in form_fields.values() if value not in [None, "", 0, False])
            total_fields = len(form_fields)
            
            form_population_success = populated_fields > 0
            
            self.log_result(
                "Frontend Edit Form Simulation",
                form_population_success,
                f"Form population simulation. Populated fields: {populated_fields}/{total_fields}",
                {
                    "form_fields": form_fields,
                    "populated_fields_count": populated_fields,
                    "empty_fields": empty_fields,
                    "display_issues": display_issues,
                    "form_population_success": form_population_success
                }
            )
            return form_population_success
            
        except Exception as e:
            self.log_result(
                "Frontend Edit Form Simulation",
                False,
                f"Error simulating frontend form: {str(e)}"
            )
            return False

    def test_specific_field_types(self, kit_data):
        """Test specific field types that might cause frontend issues"""
        print("🔍 TESTING SPECIFIC FIELD TYPES...")
        
        try:
            field_type_analysis = {}
            
            # Test boolean fields
            boolean_fields = ["is_signed", "has_printing", "is_worn"]
            for field in boolean_fields:
                value = kit_data.get(field)
                field_type_analysis[field] = {
                    "value": value,
                    "type": type(value).__name__,
                    "is_boolean": isinstance(value, bool),
                    "frontend_safe": isinstance(value, bool) or value is None
                }
            
            # Test numeric fields
            numeric_fields = ["purchase_price", "printed_number"]
            for field in numeric_fields:
                value = kit_data.get(field)
                field_type_analysis[field] = {
                    "value": value,
                    "type": type(value).__name__,
                    "is_numeric": isinstance(value, (int, float)),
                    "frontend_safe": isinstance(value, (int, float)) or value is None
                }
            
            # Test string fields
            string_fields = ["size", "condition", "signed_by", "printed_name", "personal_notes"]
            for field in string_fields:
                value = kit_data.get(field)
                field_type_analysis[field] = {
                    "value": value,
                    "type": type(value).__name__,
                    "is_string": isinstance(value, str),
                    "frontend_safe": isinstance(value, str) or value is None
                }
            
            # Check for type issues
            type_issues = []
            for field, analysis in field_type_analysis.items():
                if not analysis["frontend_safe"]:
                    type_issues.append(f"{field}: expected safe type, got {analysis['type']}")
            
            all_types_safe = len(type_issues) == 0
            
            self.log_result(
                "Field Type Analysis",
                all_types_safe,
                f"Field type safety check. Type issues: {len(type_issues)}",
                {
                    "field_type_analysis": field_type_analysis,
                    "type_issues": type_issues,
                    "all_types_safe": all_types_safe
                }
            )
            return all_types_safe
            
        except Exception as e:
            self.log_result(
                "Field Type Analysis",
                False,
                f"Error analyzing field types: {str(e)}"
            )
            return False

    def run_comprehensive_test(self):
        """Run the complete frontend-backend integration test"""
        print("🚀 STARTING FRONTEND-BACKEND INTEGRATION TEST")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test vestiaire endpoint
        vestiaire_kit = self.test_vestiaire_endpoint()
        if not vestiaire_kit:
            print("⚠️ No vestiaire kits available, but continuing with existing data...")
        
        # Step 3: Test Ma Collection endpoint
        owned_kit = self.test_ma_collection_endpoint()
        if not owned_kit:
            print("❌ No owned kits found. Cannot test edit form integration.")
            return False
        
        # Step 4: Simulate frontend edit form processing
        form_simulation_ok = self.test_edit_form_data_simulation(owned_kit)
        
        # Step 5: Test specific field types
        field_types_ok = self.test_specific_field_types(owned_kit)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FRONTEND-BACKEND INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Root cause analysis
        print("\n🔍 INTEGRATION ANALYSIS:")
        if not form_simulation_ok:
            print("❌ ISSUE IDENTIFIED: Frontend form simulation failed - data not suitable for edit form")
        elif not field_types_ok:
            print("❌ ISSUE IDENTIFIED: Field type issues detected - frontend might have trouble with data types")
        else:
            print("✅ NO INTEGRATION ISSUES FOUND: Backend data is fully compatible with frontend edit form")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = FrontendBackendIntegrationTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)