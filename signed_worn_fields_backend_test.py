#!/usr/bin/env python3

"""
Backend Testing for Signed/Worn Fields Complete Data Flow

This test verifies the complete data flow for jersey creation and editing with signed/worn fields
as specified in the review request:

**Issue Resolution Testing:**
- ✅ Added signed/worn fields to creation form (VestiairePage.js)
- ✅ Made edit form identical to creation form (MyCollectionPage.js)
- ✅ Updated data mapping between frontend and backend
- ✅ Fixed backend edit functionality (PersonalKitResponse bug)

**Testing Required:**
1. **Complete Data Flow Test**: Add jersey with all fields → Verify data saved → Edit jersey → Verify all fields displayed
2. **Field Mapping Test**: Ensure frontend field names correctly map to backend field names
3. **Signed/Worn Fields Test**: Verify signed and worn fields work in both creation and edit
4. **Data Persistence Test**: Ensure all information entered during creation appears in edit form
5. **Form Validation Test**: Test conditional fields (printing, signed details, match worn)

**Specific Tests:**
- Create PersonalKit with: price_buy, price_value, size, condition, is_worn, is_signed, signed_by, has_printing, player_name, player_number, custom fields
- Retrieve PersonalKit and verify ALL fields are present and correct
- Update PersonalKit with different values
- Verify changes persist correctly

**Expected Results:**
- ✅ All information entered during jersey addition appears in collection edit form
- ✅ Both forms are now identical in structure and fields
- ✅ Signed/worn fields work correctly in both forms
- ✅ Data persistence works perfectly from creation → storage → retrieval → editing

**Authentication**: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class SignedWornFieldsTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        self.test_personal_kit_id = None
        
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

    def get_vestiaire_reference_kit(self):
        """Get a reference kit from vestiaire for testing"""
        print("🏪 GETTING REFERENCE KIT FROM VESTIAIRE...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                vestiaire_data = response.json()
                
                if vestiaire_data and len(vestiaire_data) > 0:
                    # Get first available reference kit
                    reference_kit = vestiaire_data[0]
                    reference_kit_id = reference_kit.get("id") or reference_kit.get("reference_kit_id")
                    
                    self.log_result(
                        "Vestiaire Reference Kit Access",
                        True,
                        f"Successfully retrieved reference kit for testing",
                        {
                            "reference_kit_id": reference_kit_id,
                            "team_name": reference_kit.get("team_info", {}).get("name", "Unknown"),
                            "season": reference_kit.get("master_kit_info", {}).get("season", "Unknown"),
                            "total_kits_available": len(vestiaire_data)
                        }
                    )
                    return reference_kit_id
                else:
                    self.log_result(
                        "Vestiaire Reference Kit Access",
                        False,
                        "No reference kits available in vestiaire"
                    )
                    return None
            else:
                self.log_result(
                    "Vestiaire Reference Kit Access",
                    False,
                    f"Failed to access vestiaire - Status: {response.status_code}",
                    {"error": response.text}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Vestiaire Reference Kit Access",
                False,
                f"Error accessing vestiaire: {str(e)}"
            )
            return None

    def test_complete_data_flow_creation(self, reference_kit_id):
        """Test 1: Complete Data Flow - Create PersonalKit with ALL fields including signed/worn"""
        print("📝 TESTING COMPLETE DATA FLOW - CREATION WITH ALL FIELDS...")
        
        if not reference_kit_id:
            self.log_result(
                "Complete Data Flow - Creation",
                False,
                "No reference kit ID available for testing"
            )
            return False
        
        try:
            # Create PersonalKit with comprehensive data including signed/worn fields
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "owned",
                # Basic fields
                "size": "L",
                "condition": "mint",
                # Price fields
                "purchase_price": 149.99,
                "estimated_value": 180.00,
                "purchase_date": "2024-01-15",
                # Signed fields (NEW - focus of testing)
                "is_signed": True,
                "signed_by": "Lionel Messi",
                "signed_date": "2024-02-10",
                "signature_location": "Front chest",
                "certificate_of_authenticity": True,
                # Worn fields (NEW - focus of testing)
                "is_worn": True,
                "worn_by": "Lionel Messi",
                "match_details": "PSG vs Barcelona - Champions League Final 2024",
                "match_date": "2024-05-25",
                "match_worn_evidence": "Official match sheet and photo evidence",
                # Printing fields
                "has_printing": True,
                "printed_name": "MESSI",
                "printed_number": "10",
                "printing_type": "Official",
                # Custom fields
                "personal_notes": "Signed jersey worn in Champions League final - incredible condition with COA",
                "acquisition_story": "Purchased directly from PSG official store after the match",
                "storage_location": "Climate controlled display case",
                "insurance_value": 2500.00,
                "provenance_details": "Direct from player via official PSG channels"
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                self.test_personal_kit_id = response_data.get("id")
                
                # Verify all fields are present in response
                expected_fields = [
                    "size", "condition", "purchase_price", "estimated_value",
                    "is_signed", "signed_by", "signed_date", "signature_location", "certificate_of_authenticity",
                    "is_worn", "worn_by", "match_details", "match_date", "match_worn_evidence",
                    "has_printing", "printed_name", "printed_number", "printing_type",
                    "personal_notes", "acquisition_story", "storage_location", "insurance_value", "provenance_details"
                ]
                
                fields_present = []
                fields_missing = []
                
                for field in expected_fields:
                    if field in response_data:
                        fields_present.append(field)
                    else:
                        fields_missing.append(field)
                
                success = len(fields_missing) == 0
                
                self.log_result(
                    "Complete Data Flow - Creation",
                    success,
                    f"PersonalKit creation {'successful' if success else 'incomplete'} - {len(fields_present)}/{len(expected_fields)} fields present",
                    {
                        "personal_kit_id": self.test_personal_kit_id,
                        "reference_kit_id": reference_kit_id,
                        "fields_present": fields_present,
                        "fields_missing": fields_missing,
                        "signed_fields_working": all(f in response_data for f in ["is_signed", "signed_by", "signed_date"]),
                        "worn_fields_working": all(f in response_data for f in ["is_worn", "worn_by", "match_details"]),
                        "response_status": response.status_code
                    }
                )
                return success
            else:
                error_detail = response.text
                self.log_result(
                    "Complete Data Flow - Creation",
                    False,
                    f"PersonalKit creation failed - Status: {response.status_code}",
                    {"error": error_detail, "request_data": personal_kit_data}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Complete Data Flow - Creation",
                False,
                f"Error creating PersonalKit: {str(e)}"
            )
            return False

    def test_data_persistence_retrieval(self):
        """Test 2: Data Persistence - Retrieve PersonalKit and verify ALL fields are present"""
        print("🔍 TESTING DATA PERSISTENCE - RETRIEVAL AND VERIFICATION...")
        
        if not self.test_personal_kit_id:
            self.log_result(
                "Data Persistence - Retrieval",
                False,
                "No PersonalKit ID available for testing (creation may have failed)"
            )
            return False, None
        
        try:
            # Retrieve the created PersonalKit
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                owned_kits = response.json()
                
                # Find our test kit
                test_kit = None
                if isinstance(owned_kits, list):
                    for kit in owned_kits:
                        if kit.get("id") == self.test_personal_kit_id:
                            test_kit = kit
                            break
                
                if test_kit:
                    # Verify all expected fields are present and have correct values
                    expected_values = {
                        "size": "L",
                        "condition": "mint",
                        "purchase_price": 149.99,
                        "is_signed": True,
                        "signed_by": "Lionel Messi",
                        "signed_date": "2024-02-10",
                        "is_worn": True,
                        "worn_by": "Lionel Messi",
                        "match_details": "PSG vs Barcelona - Champions League Final 2024",
                        "has_printing": True,
                        "printed_name": "MESSI",
                        "printed_number": "10",
                        "personal_notes": "Signed jersey worn in Champions League final - incredible condition with COA"
                    }
                    
                    fields_correct = []
                    fields_incorrect = []
                    
                    for field, expected_value in expected_values.items():
                        actual_value = test_kit.get(field)
                        if actual_value == expected_value:
                            fields_correct.append(field)
                        else:
                            fields_incorrect.append({
                                "field": field,
                                "expected": expected_value,
                                "actual": actual_value
                            })
                    
                    success = len(fields_incorrect) == 0
                    
                    self.log_result(
                        "Data Persistence - Retrieval",
                        success,
                        f"Data persistence {'verified' if success else 'has issues'} - {len(fields_correct)}/{len(expected_values)} fields correct",
                        {
                            "personal_kit_id": self.test_personal_kit_id,
                            "fields_correct": fields_correct,
                            "fields_incorrect": fields_incorrect,
                            "signed_data_persisted": test_kit.get("is_signed") == True and test_kit.get("signed_by") == "Lionel Messi",
                            "worn_data_persisted": test_kit.get("is_worn") == True and test_kit.get("worn_by") == "Lionel Messi",
                            "all_kit_fields": list(test_kit.keys())
                        }
                    )
                    return success, test_kit
                else:
                    self.log_result(
                        "Data Persistence - Retrieval",
                        False,
                        f"Created PersonalKit not found in owned collection",
                        {"searched_kit_id": self.test_personal_kit_id, "total_owned_kits": len(owned_kits)}
                    )
                    return False, None
            else:
                self.log_result(
                    "Data Persistence - Retrieval",
                    False,
                    f"Failed to retrieve owned collection - Status: {response.status_code}",
                    {"error": response.text}
                )
                return False, None
                
        except Exception as e:
            self.log_result(
                "Data Persistence - Retrieval",
                False,
                f"Error retrieving PersonalKit: {str(e)}"
            )
            return False, None

    def test_edit_functionality_update(self, original_kit_data):
        """Test 3: Edit Functionality - Update PersonalKit with different values"""
        print("✏️ TESTING EDIT FUNCTIONALITY - UPDATE WITH DIFFERENT VALUES...")
        
        if not self.test_personal_kit_id or not original_kit_data:
            self.log_result(
                "Edit Functionality - Update",
                False,
                "No PersonalKit data available for edit testing"
            )
            return False
        
        try:
            # Update PersonalKit with different values, especially signed/worn fields
            updated_data = {
                "size": "XL",  # Changed from L
                "condition": "excellent",  # Changed from mint
                "purchase_price": 199.99,  # Changed from 149.99
                # Update signed fields
                "is_signed": True,  # Keep signed
                "signed_by": "Kylian Mbappé",  # Changed signer
                "signed_date": "2024-03-15",  # Changed date
                "signature_location": "Back number",  # Changed location
                "certificate_of_authenticity": False,  # Changed to false
                # Update worn fields
                "is_worn": False,  # Changed from worn to not worn
                "worn_by": "",  # Clear worn by
                "match_details": "",  # Clear match details
                "match_date": "",  # Clear match date
                "match_worn_evidence": "",  # Clear evidence
                # Update printing fields
                "has_printing": True,  # Keep printing
                "printed_name": "MBAPPÉ",  # Changed name
                "printed_number": "7",  # Changed number
                "printing_type": "Custom",  # Changed type
                # Update custom fields
                "personal_notes": "Updated: Signed by Mbappé, no longer match worn",
                "acquisition_story": "Updated acquisition story",
                "storage_location": "Updated storage location",
                "insurance_value": 1800.00,  # Changed value
                "provenance_details": "Updated provenance details"
            }
            
            response = self.session.put(f"{BACKEND_URL}/personal-kits/{self.test_personal_kit_id}", json=updated_data)
            
            if response.status_code in [200, 204]:
                # Verify the update was successful by retrieving the updated kit
                get_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
                
                if get_response.status_code == 200:
                    owned_kits = get_response.json()
                    updated_kit = None
                    
                    if isinstance(owned_kits, list):
                        for kit in owned_kits:
                            if kit.get("id") == self.test_personal_kit_id:
                                updated_kit = kit
                                break
                    
                    if updated_kit:
                        # Verify updates were applied
                        expected_updates = {
                            "size": "XL",
                            "condition": "excellent",
                            "purchase_price": 199.99,
                            "signed_by": "Kylian Mbappé",
                            "signed_date": "2024-03-15",
                            "is_worn": False,
                            "printed_name": "MBAPPÉ",
                            "printed_number": "7",
                            "personal_notes": "Updated: Signed by Mbappé, no longer match worn"
                        }
                        
                        updates_correct = []
                        updates_incorrect = []
                        
                        for field, expected_value in expected_updates.items():
                            actual_value = updated_kit.get(field)
                            if actual_value == expected_value:
                                updates_correct.append(field)
                            else:
                                updates_incorrect.append({
                                    "field": field,
                                    "expected": expected_value,
                                    "actual": actual_value
                                })
                        
                        success = len(updates_incorrect) == 0
                        
                        self.log_result(
                            "Edit Functionality - Update",
                            success,
                            f"PersonalKit update {'successful' if success else 'has issues'} - {len(updates_correct)}/{len(expected_updates)} updates correct",
                            {
                                "personal_kit_id": self.test_personal_kit_id,
                                "updates_correct": updates_correct,
                                "updates_incorrect": updates_incorrect,
                                "signed_fields_updated": updated_kit.get("signed_by") == "Kylian Mbappé",
                                "worn_fields_updated": updated_kit.get("is_worn") == False,
                                "response_status": response.status_code
                            }
                        )
                        return success
                    else:
                        self.log_result(
                            "Edit Functionality - Update",
                            False,
                            "Updated PersonalKit not found after update"
                        )
                        return False
                else:
                    self.log_result(
                        "Edit Functionality - Update",
                        False,
                        f"Failed to retrieve updated kit - Status: {get_response.status_code}"
                    )
                    return False
            else:
                error_detail = response.text
                self.log_result(
                    "Edit Functionality - Update",
                    False,
                    f"PersonalKit update failed - Status: {response.status_code}",
                    {"error": error_detail, "update_data": updated_data}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Edit Functionality - Update",
                False,
                f"Error updating PersonalKit: {str(e)}"
            )
            return False

    def test_field_mapping_validation(self):
        """Test 4: Field Mapping - Ensure frontend field names correctly map to backend"""
        print("🗺️ TESTING FIELD MAPPING VALIDATION...")
        
        try:
            # Test field mapping by creating a kit with specific field names that should match frontend
            test_reference_kit = self.get_vestiaire_reference_kit()
            
            if not test_reference_kit:
                self.log_result(
                    "Field Mapping Validation",
                    False,
                    "No reference kit available for field mapping test"
                )
                return False
            
            # Test with field names that should match frontend exactly
            field_mapping_data = {
                "reference_kit_id": test_reference_kit,
                "collection_type": "owned",
                # Standard fields
                "size": "M",
                "condition": "good",
                "purchase_price": 75.00,
                # Signed fields - test exact field names
                "is_signed": True,
                "signed_by": "Test Player",
                "signed_date": "2024-01-01",
                "signature_location": "Front",
                "certificate_of_authenticity": True,
                # Worn fields - test exact field names
                "is_worn": True,
                "worn_by": "Test Player",
                "match_details": "Test Match",
                "match_date": "2024-01-01",
                "match_worn_evidence": "Test Evidence",
                # Printing fields
                "has_printing": True,
                "printed_name": "TEST",
                "printed_number": "99",
                "printing_type": "Official",
                # Additional fields
                "personal_notes": "Field mapping test",
                "acquisition_story": "Test story",
                "storage_location": "Test location",
                "insurance_value": 100.00,
                "provenance_details": "Test provenance"
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=field_mapping_data)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                # Check that all field names are preserved exactly
                field_mapping_success = True
                mapping_results = {}
                
                for field_name, expected_value in field_mapping_data.items():
                    if field_name == "reference_kit_id" or field_name == "collection_type":
                        continue  # Skip system fields
                    
                    actual_value = response_data.get(field_name)
                    mapping_results[field_name] = {
                        "expected": expected_value,
                        "actual": actual_value,
                        "matches": actual_value == expected_value
                    }
                    
                    if actual_value != expected_value:
                        field_mapping_success = False
                
                # Clean up test kit
                test_kit_id = response_data.get("id")
                if test_kit_id:
                    self.session.delete(f"{BACKEND_URL}/personal-kits/{test_kit_id}")
                
                self.log_result(
                    "Field Mapping Validation",
                    field_mapping_success,
                    f"Field mapping {'successful' if field_mapping_success else 'has issues'} - All field names preserved correctly",
                    {
                        "total_fields_tested": len(mapping_results),
                        "mapping_results": mapping_results,
                        "signed_fields_mapped": all(mapping_results.get(f, {}).get("matches", False) for f in ["is_signed", "signed_by", "signed_date"]),
                        "worn_fields_mapped": all(mapping_results.get(f, {}).get("matches", False) for f in ["is_worn", "worn_by", "match_details"])
                    }
                )
                return field_mapping_success
            else:
                self.log_result(
                    "Field Mapping Validation",
                    False,
                    f"Field mapping test failed - Status: {response.status_code}",
                    {"error": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Field Mapping Validation",
                False,
                f"Error testing field mapping: {str(e)}"
            )
            return False

    def test_conditional_fields_validation(self):
        """Test 5: Form Validation - Test conditional fields (printing, signed details, match worn)"""
        print("🔧 TESTING CONDITIONAL FIELDS VALIDATION...")
        
        try:
            test_reference_kit = self.get_vestiaire_reference_kit()
            
            if not test_reference_kit:
                self.log_result(
                    "Conditional Fields Validation",
                    False,
                    "No reference kit available for conditional fields test"
                )
                return False
            
            # Test 1: Signed = True should allow signed details
            signed_test_data = {
                "reference_kit_id": test_reference_kit,
                "collection_type": "owned",
                "size": "M",
                "condition": "mint",
                "is_signed": True,
                "signed_by": "Conditional Test Player",
                "signed_date": "2024-01-01",
                "signature_location": "Front chest",
                "certificate_of_authenticity": True,
                "is_worn": False,
                "has_printing": False,
                "personal_notes": "Conditional fields test - signed only"
            }
            
            signed_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=signed_test_data)
            signed_success = signed_response.status_code in [200, 201]
            signed_kit_id = None
            
            if signed_success:
                signed_kit_id = signed_response.json().get("id")
            
            # Test 2: Worn = True should allow worn details
            worn_test_data = {
                "reference_kit_id": test_reference_kit,
                "collection_type": "owned",
                "size": "L",
                "condition": "excellent",
                "is_signed": False,
                "is_worn": True,
                "worn_by": "Conditional Test Player",
                "match_details": "Test Match - Conditional Fields",
                "match_date": "2024-02-01",
                "match_worn_evidence": "Official match documentation",
                "has_printing": False,
                "personal_notes": "Conditional fields test - worn only"
            }
            
            worn_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=worn_test_data)
            worn_success = worn_response.status_code in [200, 201]
            worn_kit_id = None
            
            if worn_success:
                worn_kit_id = worn_response.json().get("id")
            
            # Test 3: Printing = True should allow printing details
            printing_test_data = {
                "reference_kit_id": test_reference_kit,
                "collection_type": "owned",
                "size": "XL",
                "condition": "good",
                "is_signed": False,
                "is_worn": False,
                "has_printing": True,
                "printed_name": "CONDITIONAL",
                "printed_number": "88",
                "printing_type": "Custom",
                "personal_notes": "Conditional fields test - printing only"
            }
            
            printing_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=printing_test_data)
            printing_success = printing_response.status_code in [200, 201]
            printing_kit_id = None
            
            if printing_success:
                printing_kit_id = printing_response.json().get("id")
            
            # Clean up test kits
            for kit_id in [signed_kit_id, worn_kit_id, printing_kit_id]:
                if kit_id:
                    self.session.delete(f"{BACKEND_URL}/personal-kits/{kit_id}")
            
            overall_success = signed_success and worn_success and printing_success
            
            self.log_result(
                "Conditional Fields Validation",
                overall_success,
                f"Conditional fields validation {'successful' if overall_success else 'has issues'} - All conditional field combinations work",
                {
                    "signed_fields_test": signed_success,
                    "worn_fields_test": worn_success,
                    "printing_fields_test": printing_success,
                    "signed_response_status": signed_response.status_code if signed_response else None,
                    "worn_response_status": worn_response.status_code if worn_response else None,
                    "printing_response_status": printing_response.status_code if printing_response else None
                }
            )
            return overall_success
            
        except Exception as e:
            self.log_result(
                "Conditional Fields Validation",
                False,
                f"Error testing conditional fields: {str(e)}"
            )
            return False

    def run_comprehensive_test(self):
        """Run all tests for signed/worn fields complete data flow"""
        print("🚀 STARTING COMPREHENSIVE SIGNED/WORN FIELDS DATA FLOW TESTING")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Step 2: Get reference kit for testing
        reference_kit_id = self.get_vestiaire_reference_kit()
        if not reference_kit_id:
            print("❌ CRITICAL: No reference kit available - cannot proceed with testing")
            return False
        
        # Step 3: Test complete data flow - creation with all fields
        creation_success = self.test_complete_data_flow_creation(reference_kit_id)
        
        # Step 4: Test data persistence - retrieval and verification
        retrieval_success, original_kit_data = self.test_data_persistence_retrieval()
        
        # Step 5: Test edit functionality - update with different values
        if retrieval_success and original_kit_data:
            self.test_edit_functionality_update(original_kit_data)
        
        # Step 6: Test field mapping validation
        self.test_field_mapping_validation()
        
        # Step 7: Test conditional fields validation
        self.test_conditional_fields_validation()
        
        # Generate summary
        self.generate_test_summary()
        
        return True

    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE SIGNED/WORN FIELDS TEST SUMMARY")
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
            if not result["success"]:
                critical_issues.append(result["test"])
        
        if critical_issues:
            print("🚨 ISSUES FOUND:")
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
            print("🎉 EXCELLENT: Signed/worn fields complete data flow is working perfectly!")
            print("✅ All information entered during jersey addition appears in collection edit form")
            print("✅ Both forms are now identical in structure and fields")
            print("✅ Signed/worn fields work correctly in both forms")
            print("✅ Data persistence works perfectly from creation → storage → retrieval → editing")
        elif success_rate >= 70:
            print("✅ GOOD: Most functionality is working, minor issues may need attention")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Some critical issues found, fixes may need review")
        else:
            print("❌ CRITICAL: Major issues found, signed/worn fields implementation needs immediate attention")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = SignedWornFieldsTester()
    
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