#!/usr/bin/env python3

"""
Personal Kit Edit Data Investigation - Critical Bug Testing

CRITICAL BUG REPORTED:
User reports that when they add a jersey from Kit Store and fill in the form fields, 
the information is not displayed when they edit the jersey later. This suggests a 
data persistence or retrieval issue.

Issue Description:
1. User adds jersey from Kit Store → Fills form with details
2. Jersey gets added to owned collection 
3. User clicks edit button on the jersey
4. Edit form is empty/doesn't show the previously entered data

Potential Causes:
1. Data Not Being Saved: Form data not properly saved during POST /api/personal-kits
2. Data Not Being Retrieved: Edit form not properly loading existing data
3. Field Mismatch: Different field names between creation and editing
4. Database Storage Issue: Data being stored but with wrong field names

Test Process:
1. Create a personal kit with detailed information
2. Retrieve the personal kit and verify all fields are present
3. Check if the data structure matches what the edit form expects
4. Identify missing or incorrectly mapped fields

Authentication: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://mongodb-routing.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class PersonalKitEditDataTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        self.created_kit_id = None
        
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

    def get_available_reference_kits(self):
        """Get available reference kits from vestiaire"""
        print("🏪 GETTING AVAILABLE REFERENCE KITS...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                kits = response.json()
                if kits and len(kits) > 0:
                    self.log_result(
                        "Reference Kits Availability",
                        True,
                        f"Found {len(kits)} reference kits available",
                        {"first_kit_id": kits[0].get("id"), "first_kit_team": kits[0].get("team_info", {}).get("name")}
                    )
                    return kits[0]  # Return first available kit
                else:
                    self.log_result(
                        "Reference Kits Availability",
                        False,
                        "No reference kits available in vestiaire"
                    )
                    return None
            else:
                self.log_result(
                    "Reference Kits Availability",
                    False,
                    f"Failed to get reference kits: {response.status_code}",
                    {"response": response.text}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Reference Kits Availability",
                False,
                f"Error getting reference kits: {str(e)}"
            )
            return None

    def get_existing_personal_kit_or_create(self, reference_kit):
        """Get existing personal kit or create one with comprehensive detailed information"""
        print("📝 GETTING EXISTING PERSONAL KIT OR CREATING NEW ONE...")
        
        try:
            # First, check if user already has personal kits
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                existing_kits = response.json()
                if existing_kits and len(existing_kits) > 0:
                    # Use existing kit for testing
                    existing_kit = existing_kits[0]
                    self.created_kit_id = existing_kit.get("id")
                    
                    self.log_result(
                        "Existing Personal Kit Found",
                        True,
                        f"Using existing personal kit with ID: {self.created_kit_id}",
                        {
                            "existing_kit_id": self.created_kit_id,
                            "total_existing_kits": len(existing_kits),
                            "response_keys": list(existing_kit.keys())
                        }
                    )
                    return existing_kit
            
            # If no existing kits, try to create a new one
            personal_kit_data = {
                "reference_kit_id": reference_kit["id"],
                "collection_type": "owned",
                "size": "L",
                "condition": "excellent",
                "purchase_price": 89.99,
                "purchase_date": "2024-01-15",
                "is_signed": True,
                "signed_by": "Lionel Messi",
                "has_printing": True,
                "printed_name": "MESSI",
                "printed_number": "10",
                "is_worn": False,
                "personal_notes": "Bought from official PSG store during Champions League final. Certificate of authenticity included. Perfect condition, never worn."
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            
            if response.status_code in [200, 201]:
                created_kit = response.json()
                self.created_kit_id = created_kit.get("id")
                
                # Verify all fields were saved in the response
                saved_fields = {}
                for field, expected_value in personal_kit_data.items():
                    if field == "reference_kit_id":
                        continue  # This becomes a relationship, not a direct field
                    actual_value = created_kit.get(field)
                    saved_fields[field] = {
                        "expected": expected_value,
                        "actual": actual_value,
                        "matches": actual_value == expected_value
                    }
                
                all_fields_saved = all(field_data["matches"] for field_data in saved_fields.values())
                
                self.log_result(
                    "Personal Kit Creation with Detailed Data",
                    all_fields_saved,
                    f"Personal kit created with ID: {self.created_kit_id}. All fields saved: {all_fields_saved}",
                    {
                        "created_kit_id": self.created_kit_id,
                        "field_verification": saved_fields,
                        "response_keys": list(created_kit.keys())
                    }
                )
                return created_kit
            else:
                self.log_result(
                    "Personal Kit Creation with Detailed Data",
                    False,
                    f"Failed to create personal kit: {response.status_code}",
                    {"response": response.text, "sent_data": personal_kit_data}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Personal Kit Creation/Retrieval",
                False,
                f"Error getting/creating personal kit: {str(e)}"
            )
            return None

    def retrieve_personal_kit_for_editing(self):
        """Retrieve the created personal kit to verify all data is present for editing"""
        print("🔍 RETRIEVING PERSONAL KIT FOR EDIT VERIFICATION...")
        
        try:
            # Get owned collections (this is what the edit form would call)
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                owned_kits = response.json()
                
                # Find our created kit
                created_kit = None
                for kit in owned_kits:
                    if kit.get("id") == self.created_kit_id:
                        created_kit = kit
                        break
                
                if created_kit:
                    # Check all expected fields for edit form
                    expected_edit_fields = [
                        "id", "size", "condition", "purchase_price", "purchase_date",
                        "is_signed", "signed_by", "has_printing", "printed_name", 
                        "printed_number", "is_worn", "personal_notes"
                    ]
                    
                    field_analysis = {}
                    missing_fields = []
                    present_fields = []
                    
                    for field in expected_edit_fields:
                        if field in created_kit:
                            present_fields.append(field)
                            field_analysis[field] = {
                                "present": True,
                                "value": created_kit[field],
                                "type": type(created_kit[field]).__name__
                            }
                        else:
                            missing_fields.append(field)
                            field_analysis[field] = {
                                "present": False,
                                "value": None,
                                "type": "missing"
                            }
                    
                    # Check for enriched data (reference_kit_info, master_kit_info, etc.)
                    enriched_data = {}
                    for key in created_kit.keys():
                        if "_info" in key:
                            enriched_data[key] = created_kit[key]
                    
                    all_fields_present = len(missing_fields) == 0
                    
                    self.log_result(
                        "Personal Kit Retrieval for Edit",
                        all_fields_present,
                        f"Retrieved kit for editing. Missing fields: {len(missing_fields)}, Present fields: {len(present_fields)}",
                        {
                            "kit_id": self.created_kit_id,
                            "missing_fields": missing_fields,
                            "present_fields": present_fields,
                            "field_analysis": field_analysis,
                            "enriched_data_keys": list(enriched_data.keys()),
                            "total_response_keys": list(created_kit.keys())
                        }
                    )
                    return created_kit, field_analysis
                else:
                    self.log_result(
                        "Personal Kit Retrieval for Edit",
                        False,
                        f"Created kit with ID {self.created_kit_id} not found in owned collections",
                        {"available_kit_ids": [kit.get("id") for kit in owned_kits]}
                    )
                    return None, None
            else:
                self.log_result(
                    "Personal Kit Retrieval for Edit",
                    False,
                    f"Failed to retrieve owned collections: {response.status_code}",
                    {"response": response.text}
                )
                return None, None
                
        except Exception as e:
            self.log_result(
                "Personal Kit Retrieval for Edit",
                False,
                f"Error retrieving personal kit: {str(e)}"
            )
            return None, None

    def test_field_mapping_consistency(self, created_kit, retrieved_kit):
        """Test if field names and values are consistent between creation and retrieval"""
        print("🔄 TESTING FIELD MAPPING CONSISTENCY...")
        
        try:
            # Compare creation response vs retrieval response
            creation_fields = set(created_kit.keys()) if created_kit else set()
            retrieval_fields = set(retrieved_kit.keys()) if retrieved_kit else set()
            
            # Fields that should be identical
            core_fields = ["id", "size", "condition", "purchase_price", "is_signed", 
                          "signed_by", "has_printing", "printed_name", "printed_number", 
                          "is_worn", "personal_notes"]
            
            field_consistency = {}
            inconsistent_fields = []
            
            for field in core_fields:
                creation_value = created_kit.get(field) if created_kit else None
                retrieval_value = retrieved_kit.get(field) if retrieved_kit else None
                
                is_consistent = creation_value == retrieval_value
                field_consistency[field] = {
                    "creation_value": creation_value,
                    "retrieval_value": retrieval_value,
                    "consistent": is_consistent
                }
                
                if not is_consistent:
                    inconsistent_fields.append(field)
            
            all_consistent = len(inconsistent_fields) == 0
            
            self.log_result(
                "Field Mapping Consistency",
                all_consistent,
                f"Field consistency check. Inconsistent fields: {len(inconsistent_fields)}",
                {
                    "inconsistent_fields": inconsistent_fields,
                    "field_consistency": field_consistency,
                    "creation_only_fields": list(creation_fields - retrieval_fields),
                    "retrieval_only_fields": list(retrieval_fields - creation_fields)
                }
            )
            return all_consistent
            
        except Exception as e:
            self.log_result(
                "Field Mapping Consistency",
                False,
                f"Error testing field consistency: {str(e)}"
            )
            return False

    def test_edit_form_data_completeness(self, retrieved_kit, field_analysis):
        """Test if retrieved data has everything needed for edit form"""
        print("📋 TESTING EDIT FORM DATA COMPLETENESS...")
        
        try:
            # Critical fields that MUST be present for edit form to work
            critical_fields = ["id", "size", "condition", "personal_notes"]
            
            # Optional but important fields
            important_fields = ["purchase_price", "is_signed", "signed_by", "has_printing", 
                              "printed_name", "printed_number", "is_worn"]
            
            critical_missing = []
            important_missing = []
            
            for field in critical_fields:
                if not field_analysis.get(field, {}).get("present", False):
                    critical_missing.append(field)
            
            for field in important_fields:
                if not field_analysis.get(field, {}).get("present", False):
                    important_missing.append(field)
            
            # Check for proper data types
            type_issues = []
            if retrieved_kit:
                if "purchase_price" in retrieved_kit and retrieved_kit["purchase_price"] is not None:
                    if not isinstance(retrieved_kit["purchase_price"], (int, float)):
                        type_issues.append(f"purchase_price should be number, got {type(retrieved_kit['purchase_price'])}")
                
                if "is_signed" in retrieved_kit and retrieved_kit["is_signed"] is not None:
                    if not isinstance(retrieved_kit["is_signed"], bool):
                        type_issues.append(f"is_signed should be boolean, got {type(retrieved_kit['is_signed'])}")
            
            edit_form_ready = len(critical_missing) == 0 and len(type_issues) == 0
            
            self.log_result(
                "Edit Form Data Completeness",
                edit_form_ready,
                f"Edit form readiness: {edit_form_ready}. Critical missing: {len(critical_missing)}, Type issues: {len(type_issues)}",
                {
                    "critical_missing_fields": critical_missing,
                    "important_missing_fields": important_missing,
                    "type_issues": type_issues,
                    "edit_form_ready": edit_form_ready
                }
            )
            return edit_form_ready
            
        except Exception as e:
            self.log_result(
                "Edit Form Data Completeness",
                False,
                f"Error testing edit form completeness: {str(e)}"
            )
            return False

    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("🚀 STARTING PERSONAL KIT EDIT DATA INVESTIGATION")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Get reference kit
        reference_kit = self.get_available_reference_kits()
        if not reference_kit:
            print("❌ No reference kits available. Cannot proceed with tests.")
            return False
        
        # Step 3: Get existing personal kit or create new one
        created_kit = self.get_existing_personal_kit_or_create(reference_kit)
        if not created_kit:
            print("❌ Failed to create personal kit. Cannot proceed with tests.")
            return False
        
        # Step 4: Retrieve personal kit for editing
        retrieved_kit, field_analysis = self.retrieve_personal_kit_for_editing()
        if not retrieved_kit:
            print("❌ Failed to retrieve personal kit. Cannot proceed with tests.")
            return False
        
        # Step 5: Test field mapping consistency
        consistency_ok = self.test_field_mapping_consistency(created_kit, retrieved_kit)
        
        # Step 6: Test edit form data completeness
        completeness_ok = self.test_edit_form_data_completeness(retrieved_kit, field_analysis)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Identify root cause
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        if not consistency_ok:
            print("❌ ISSUE IDENTIFIED: Field mapping inconsistency between creation and retrieval")
        elif not completeness_ok:
            print("❌ ISSUE IDENTIFIED: Retrieved data missing critical fields for edit form")
        else:
            print("✅ NO ISSUES FOUND: Personal kit data persistence and retrieval working correctly")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = PersonalKitEditDataTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)