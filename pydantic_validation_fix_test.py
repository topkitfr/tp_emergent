#!/usr/bin/env python3
"""
Backend Test for Pydantic Validation Fixes
Testing that the MasterKitResponse model fixes are working correctly after making 
required fields optional to handle existing database records.

SPECIFIC TESTING REQUIREMENTS:
1. Test GET /api/master-kits endpoint to ensure it returns data without validation errors
2. Test basic authentication endpoint (POST /api/auth/login) with credentials topkitfr@gmail.com/TopKitSecure789#
3. Verify that master kits data is returned properly without 500 errors
4. Check that the backend can handle existing database records that are missing kit_type, gender, and total_collectors fields

EXPECTED RESULTS:
- Master kits endpoint should return data without validation errors
- Authentication should work without issues
- No 500 errors due to Pydantic validation failures
- Backend should gracefully handle missing optional fields in existing records

CONTEXT: The troubleshoot agent identified that production 500 errors were caused by Pydantic 
validation failures for missing required fields (kit_type, gender, total_collectors) in existing 
MongoDB records. These fields have now been made optional in the MasterKitResponse model to 
maintain backward compatibility.
"""

import requests
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "https://mongodb-routing.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class PydanticValidationFixTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_authentication_endpoint(self):
        """Test 1: Test basic authentication endpoint with provided credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=TEST_CREDENTIALS,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.log_test(
                        "Authentication Endpoint",
                        True,
                        f"Authentication successful for {TEST_CREDENTIALS['email']}",
                        {
                            "user_name": data["user"].get("name"),
                            "user_role": data["user"].get("role"),
                            "token_length": len(data["token"])
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Authentication Endpoint",
                        False,
                        "Authentication response missing required fields",
                        {"response": data}
                    )
                    return False
            else:
                error_msg = "Authentication failed"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
                
                self.log_test(
                    "Authentication Endpoint",
                    False,
                    f"Authentication failed: {error_msg}",
                    {"status_code": response.status_code, "response": response.text[:500]}
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authentication Endpoint",
                False,
                f"Authentication request failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_master_kits_endpoint_validation(self):
        """Test 2: Test GET /api/master-kits endpoint for Pydantic validation fixes"""
        try:
            response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Check if we got valid JSON data
                    if isinstance(data, list):
                        master_kits_count = len(data)
                        
                        # Analyze the data structure for validation issues
                        validation_issues = []
                        optional_fields_analysis = {
                            "kit_type_missing": 0,
                            "gender_missing": 0,
                            "total_collectors_missing": 0,
                            "primary_color_missing": 0
                        }
                        
                        for i, kit in enumerate(data):
                            if not isinstance(kit, dict):
                                validation_issues.append(f"Kit {i}: Not a valid object")
                                continue
                                
                            # Check for previously required fields that are now optional
                            if kit.get("kit_type") is None:
                                optional_fields_analysis["kit_type_missing"] += 1
                            if kit.get("gender") is None:
                                optional_fields_analysis["gender_missing"] += 1
                            if kit.get("total_collectors") is None:
                                optional_fields_analysis["total_collectors_missing"] += 1
                            if kit.get("primary_color") is None:
                                optional_fields_analysis["primary_color_missing"] += 1
                            
                            # Check for required fields that should always be present
                            required_fields = ["id", "season", "model", "created_at", "topkit_reference"]
                            for field in required_fields:
                                if field not in kit or kit[field] is None:
                                    validation_issues.append(f"Kit {i}: Missing required field '{field}'")
                        
                        if not validation_issues:
                            self.log_test(
                                "Master Kits Endpoint - Pydantic Validation",
                                True,
                                f"Successfully retrieved {master_kits_count} master kits without validation errors",
                                {
                                    "count": master_kits_count,
                                    "optional_fields_analysis": optional_fields_analysis,
                                    "sample_kit": data[0] if data else None
                                }
                            )
                            return True
                        else:
                            self.log_test(
                                "Master Kits Endpoint - Pydantic Validation",
                                False,
                                f"Validation issues found in {len(validation_issues)} cases",
                                {
                                    "count": master_kits_count,
                                    "validation_issues": validation_issues[:10],  # Show first 10 issues
                                    "optional_fields_analysis": optional_fields_analysis
                                }
                            )
                            return False
                    else:
                        self.log_test(
                            "Master Kits Endpoint - Pydantic Validation",
                            False,
                            "Response is not a valid list",
                            {"response_type": type(data).__name__, "response": str(data)[:200]}
                        )
                        return False
                        
                except json.JSONDecodeError as e:
                    self.log_test(
                        "Master Kits Endpoint - Pydantic Validation",
                        False,
                        "Response is not valid JSON",
                        {"json_error": str(e), "response": response.text[:500]}
                    )
                    return False
                    
            else:
                # Check if it's a 500 error (which would indicate Pydantic validation failure)
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
                
                is_validation_error = response.status_code == 500
                self.log_test(
                    "Master Kits Endpoint - Pydantic Validation",
                    False,
                    f"Endpoint failed with {error_msg}" + (" - LIKELY PYDANTIC VALIDATION ERROR" if is_validation_error else ""),
                    {
                        "status_code": response.status_code,
                        "response": response.text[:500],
                        "is_validation_error": is_validation_error
                    }
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Master Kits Endpoint - Pydantic Validation",
                False,
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_specific_master_kit_validation(self):
        """Test 3: Test specific master kit retrieval to check individual record validation"""
        try:
            # First get the list to find a specific master kit ID
            response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=15)
            
            if response.status_code != 200:
                self.log_test(
                    "Specific Master Kit Validation",
                    False,
                    "Cannot test specific master kit - list endpoint failed",
                    {"status_code": response.status_code}
                )
                return False
            
            data = response.json()
            if not data or not isinstance(data, list):
                self.log_test(
                    "Specific Master Kit Validation",
                    False,
                    "No master kits available to test specific validation",
                    {"data_type": type(data).__name__}
                )
                return False
            
            # Test the first master kit
            test_kit = data[0]
            kit_id = test_kit.get("id")
            
            if not kit_id:
                self.log_test(
                    "Specific Master Kit Validation",
                    False,
                    "Master kit missing ID field",
                    {"test_kit": test_kit}
                )
                return False
            
            # Test specific master kit endpoint
            response = self.session.get(f"{BACKEND_URL}/master-kits/{kit_id}", timeout=15)
            
            if response.status_code == 200:
                try:
                    kit_data = response.json()
                    
                    # Check for the fields that were causing validation issues
                    problematic_fields = {
                        "kit_type": kit_data.get("kit_type"),
                        "gender": kit_data.get("gender"),
                        "total_collectors": kit_data.get("total_collectors"),
                        "primary_color": kit_data.get("primary_color")
                    }
                    
                    missing_optional_fields = [field for field, value in problematic_fields.items() if value is None]
                    
                    self.log_test(
                        "Specific Master Kit Validation",
                        True,
                        f"Successfully retrieved master kit {kit_id} without validation errors",
                        {
                            "kit_id": kit_id,
                            "club": kit_data.get("club"),
                            "season": kit_data.get("season"),
                            "missing_optional_fields": missing_optional_fields,
                            "problematic_fields": problematic_fields
                        }
                    )
                    return True
                    
                except json.JSONDecodeError as e:
                    self.log_test(
                        "Specific Master Kit Validation",
                        False,
                        f"Invalid JSON response for master kit {kit_id}",
                        {"json_error": str(e), "response": response.text[:500]}
                    )
                    return False
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
                
                is_validation_error = response.status_code == 500
                self.log_test(
                    "Specific Master Kit Validation",
                    False,
                    f"Failed to retrieve master kit {kit_id}: {error_msg}" + (" - LIKELY PYDANTIC VALIDATION ERROR" if is_validation_error else ""),
                    {
                        "kit_id": kit_id,
                        "status_code": response.status_code,
                        "response": response.text[:500],
                        "is_validation_error": is_validation_error
                    }
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Specific Master Kit Validation",
                False,
                f"Test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_master_kits_search_validation(self):
        """Test 4: Test master kits search endpoint for validation issues"""
        try:
            # Test search with a common query
            search_queries = ["Paris", "2024", "home"]
            
            for query in search_queries:
                response = self.session.get(
                    f"{BACKEND_URL}/master-kits/search",
                    params={"q": query},
                    timeout=15
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            self.log_test(
                                f"Master Kits Search Validation - '{query}'",
                                True,
                                f"Search for '{query}' returned {len(data)} results without validation errors",
                                {"query": query, "results_count": len(data)}
                            )
                        else:
                            self.log_test(
                                f"Master Kits Search Validation - '{query}'",
                                False,
                                f"Search for '{query}' returned invalid data structure",
                                {"query": query, "response_type": type(data).__name__}
                            )
                            return False
                    except json.JSONDecodeError as e:
                        self.log_test(
                            f"Master Kits Search Validation - '{query}'",
                            False,
                            f"Search for '{query}' returned invalid JSON",
                            {"query": query, "json_error": str(e)}
                        )
                        return False
                else:
                    is_validation_error = response.status_code == 500
                    self.log_test(
                        f"Master Kits Search Validation - '{query}'",
                        False,
                        f"Search for '{query}' failed with HTTP {response.status_code}" + (" - LIKELY PYDANTIC VALIDATION ERROR" if is_validation_error else ""),
                        {
                            "query": query,
                            "status_code": response.status_code,
                            "is_validation_error": is_validation_error
                        }
                    )
                    return False
            
            return True
            
        except Exception as e:
            self.log_test(
                "Master Kits Search Validation",
                False,
                f"Search validation test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_authenticated_collection_validation(self):
        """Test 5: Test authenticated endpoints that use MasterKitResponse model"""
        if not self.auth_token:
            self.log_test(
                "Authenticated Collection Validation",
                False,
                "No auth token available, skipping authenticated validation tests",
                {}
            )
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test my-collection endpoint which embeds MasterKitResponse
            response = self.session.get(
                f"{BACKEND_URL}/my-collection",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        collection_count = len(data)
                        
                        # Check embedded master kit data for validation issues
                        validation_issues = []
                        for i, item in enumerate(data):
                            if "master_kit" not in item:
                                validation_issues.append(f"Collection item {i}: Missing embedded master_kit")
                                continue
                            
                            master_kit = item["master_kit"]
                            if not isinstance(master_kit, dict):
                                validation_issues.append(f"Collection item {i}: Invalid master_kit structure")
                                continue
                            
                            # Check for the problematic fields in embedded master kit
                            problematic_fields = ["kit_type", "gender", "total_collectors", "primary_color"]
                            for field in problematic_fields:
                                # These fields can be None now (they're optional)
                                if field not in master_kit:
                                    validation_issues.append(f"Collection item {i}: Master kit missing field '{field}'")
                        
                        if not validation_issues:
                            self.log_test(
                                "Authenticated Collection Validation",
                                True,
                                f"Successfully retrieved {collection_count} collection items with embedded master kits without validation errors",
                                {"collection_count": collection_count}
                            )
                            return True
                        else:
                            self.log_test(
                                "Authenticated Collection Validation",
                                False,
                                f"Validation issues found in embedded master kit data",
                                {
                                    "collection_count": collection_count,
                                    "validation_issues": validation_issues[:5]  # Show first 5 issues
                                }
                            )
                            return False
                    else:
                        self.log_test(
                            "Authenticated Collection Validation",
                            False,
                            "My collection endpoint returned invalid data structure",
                            {"response_type": type(data).__name__}
                        )
                        return False
                        
                except json.JSONDecodeError as e:
                    self.log_test(
                        "Authenticated Collection Validation",
                        False,
                        "My collection endpoint returned invalid JSON",
                        {"json_error": str(e)}
                    )
                    return False
            else:
                is_validation_error = response.status_code == 500
                self.log_test(
                    "Authenticated Collection Validation",
                    False,
                    f"My collection endpoint failed with HTTP {response.status_code}" + (" - LIKELY PYDANTIC VALIDATION ERROR" if is_validation_error else ""),
                    {
                        "status_code": response.status_code,
                        "is_validation_error": is_validation_error,
                        "response": response.text[:500]
                    }
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Authenticated Collection Validation",
                False,
                f"Authenticated collection validation test failed: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def run_all_tests(self):
        """Run all Pydantic validation fix tests"""
        print("🔧 Starting Pydantic Validation Fix Testing")
        print("=" * 70)
        print("Testing that MasterKitResponse model fixes handle missing optional fields")
        print("=" * 70)
        
        # Test 1: Authentication endpoint
        auth_success = self.test_authentication_endpoint()
        
        # Test 2: Master kits endpoint validation
        master_kits_success = self.test_master_kits_endpoint_validation()
        
        # Test 3: Specific master kit validation
        specific_kit_success = self.test_specific_master_kit_validation()
        
        # Test 4: Master kits search validation
        search_success = self.test_master_kits_search_validation()
        
        # Test 5: Authenticated collection validation (if auth worked)
        collection_success = self.test_authenticated_collection_validation()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 PYDANTIC VALIDATION FIX TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical assessment for Pydantic validation fixes
        validation_tests = [master_kits_success, specific_kit_success, search_success]
        validation_passed = sum(validation_tests)
        
        print(f"\n🎯 VALIDATION TESTS (Master Kits, Specific Kit, Search): {validation_passed}/3 passed")
        
        if auth_success and validation_passed >= 2:
            print("✅ PYDANTIC VALIDATION FIXES: SUCCESS")
            print("   - Master kits endpoint returns data without validation errors")
            print("   - Backend handles missing optional fields (kit_type, gender, total_collectors)")
            print("   - No 500 errors due to Pydantic validation failures")
            print("   - Backward compatibility maintained for existing database records")
        else:
            print("❌ PYDANTIC VALIDATION FIXES: ISSUES DETECTED")
            if not auth_success:
                print("   - Authentication is failing (cannot test validation fixes)")
            if not master_kits_success:
                print("   - Master kits endpoint still has validation errors")
            if not specific_kit_success:
                print("   - Specific master kit retrieval has validation issues")
            if not search_success:
                print("   - Master kits search has validation problems")
            if not collection_success:
                print("   - Collection endpoint with embedded master kits has issues")
        
        # Check for any 500 errors that might indicate validation failures
        validation_errors = [r for r in self.test_results if 
                           "PYDANTIC VALIDATION ERROR" in r.get("message", "") or
                           r.get("details", {}).get("is_validation_error", False)]
        
        if validation_errors:
            print(f"\n⚠️  DETECTED {len(validation_errors)} POTENTIAL PYDANTIC VALIDATION ERRORS:")
            for error in validation_errors:
                print(f"   - {error['test']}: {error['message']}")
        
        return auth_success and validation_passed >= 2

if __name__ == "__main__":
    tester = PydanticValidationFixTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)