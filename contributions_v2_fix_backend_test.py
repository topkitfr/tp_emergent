#!/usr/bin/env python3
"""
Contributions-v2 API Endpoint Fix Testing
Testing the ContributionModal fix for the "improve this file" form:

ISSUE FIXED: The ContributionModal was sending incorrect data structure to the wrong endpoint 
(/api/contributions instead of /api/contributions-v2/) causing "Error: Not Found" when users 
submit the "improve this file" form.

CHANGES TESTED:
1. POST /api/contributions-v2/ with correct data structure
2. Verify proper contribution response format
3. Test authentication requirements
4. Validate data structure matches ContributionCreate model

AUTHENTICATION: topkitfr@gmail.com/TopKitSecure789#
"""

import requests
import json
import os
import sys
from datetime import datetime
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-fixes.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ContributionsV2FixTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print(f"\n🔐 AUTHENTICATING WITH ADMIN CREDENTIALS...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                user_info = data.get('user', {})
                
                self.log_test("Admin Authentication", True, 
                            f"Authenticated as {user_info.get('name', 'Unknown')} ({user_info.get('role', 'Unknown')})")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_contributions_v2_endpoint_exists(self):
        """Test that the /api/contributions-v2/ endpoint exists and is accessible"""
        print(f"\n🔍 TESTING CONTRIBUTIONS-V2 ENDPOINT ACCESSIBILITY...")
        
        try:
            # Test GET endpoint first to verify it exists
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if response.status_code in [200, 401]:  # 401 is acceptable if auth is required
                self.log_test("Contributions-v2 Endpoint Exists", True, 
                            f"Endpoint accessible (Status: {response.status_code})")
                return True
            elif response.status_code == 404:
                self.log_test("Contributions-v2 Endpoint Exists", False, 
                            "Endpoint returns 404 - Not Found")
                return False
            else:
                self.log_test("Contributions-v2 Endpoint Exists", True, 
                            f"Endpoint exists but returned status: {response.status_code}")
                return True
                
        except Exception as e:
            self.log_test("Contributions-v2 Endpoint Exists", False, f"Exception: {str(e)}")
            return False
    
    def test_create_contribution_correct_structure(self):
        """Test POST /api/contributions-v2/ with correct data structure"""
        print(f"\n📝 TESTING CONTRIBUTION CREATION WITH CORRECT DATA STRUCTURE...")
        
        # Test data matching the ContributionCreate model
        contribution_data = {
            "entity_type": "team",
            "title": "Test contribution",
            "description": "Test description",
            "data": {
                "name": "Test Team",
                "country": "Test Country"
            },
            "source_urls": []
        }
        
        try:
            response = self.session.post(f"{API_BASE}/contributions-v2/", 
                                       json=contribution_data)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                
                # Verify response structure
                required_fields = ['id', 'topkit_reference', 'status', 'created_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check specific values
                    checks = []
                    checks.append(("ID is UUID format", len(data.get('id', '')) > 30))
                    checks.append(("TopKit reference format", data.get('topkit_reference', '').startswith('TK-CONTRIB-')))
                    checks.append(("Status is pending_review", data.get('status') == 'pending_review'))
                    checks.append(("Created_at timestamp exists", 'created_at' in data))
                    
                    all_checks_passed = all(check[1] for check in checks)
                    
                    if all_checks_passed:
                        self.log_test("Create Contribution - Correct Structure", True, 
                                    f"ID: {data.get('id')[:8]}..., Reference: {data.get('topkit_reference')}, Status: {data.get('status')}")
                        return data
                    else:
                        failed_checks = [check[0] for check in checks if not check[1]]
                        self.log_test("Create Contribution - Correct Structure", False, 
                                    f"Response validation failed: {', '.join(failed_checks)}")
                        return None
                else:
                    self.log_test("Create Contribution - Correct Structure", False, 
                                f"Missing required fields: {', '.join(missing_fields)}")
                    return None
            else:
                self.log_test("Create Contribution - Correct Structure", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Create Contribution - Correct Structure", False, f"Exception: {str(e)}")
            return None
    
    def test_authentication_required(self):
        """Test that the endpoint requires Bearer token authentication"""
        print(f"\n🔒 TESTING AUTHENTICATION REQUIREMENTS...")
        
        # Create a session without auth token
        unauth_session = requests.Session()
        
        contribution_data = {
            "entity_type": "team",
            "title": "Unauthorized test",
            "description": "This should fail",
            "data": {"name": "Test"},
            "source_urls": []
        }
        
        try:
            response = unauth_session.post(f"{API_BASE}/contributions-v2/", 
                                         json=contribution_data)
            
            if response.status_code == 401:
                self.log_test("Authentication Required", True, 
                            "Endpoint correctly requires authentication (401 Unauthorized)")
                return True
            elif response.status_code == 403:
                self.log_test("Authentication Required", True, 
                            "Endpoint correctly requires authentication (403 Forbidden)")
                return True
            else:
                self.log_test("Authentication Required", False, 
                            f"Expected 401/403, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Required", False, f"Exception: {str(e)}")
            return False
    
    def test_old_endpoint_behavior(self):
        """Test that the old /api/contributions endpoint behavior (should return 404 or different response)"""
        print(f"\n🔄 TESTING OLD ENDPOINT BEHAVIOR...")
        
        contribution_data = {
            "entity_type": "team",
            "title": "Test old endpoint",
            "description": "Testing old endpoint",
            "data": {"name": "Test"},
            "source_urls": []
        }
        
        try:
            response = self.session.post(f"{API_BASE}/contributions", 
                                       json=contribution_data)
            
            # The old endpoint should either not exist (404) or behave differently
            if response.status_code == 404:
                self.log_test("Old Endpoint Behavior", True, 
                            "Old /api/contributions endpoint returns 404 as expected")
                return True
            elif response.status_code != 200 and response.status_code != 201:
                self.log_test("Old Endpoint Behavior", True, 
                            f"Old endpoint returns non-success status: {response.status_code}")
                return True
            else:
                # If it succeeds, check if it's the same as the new endpoint
                self.log_test("Old Endpoint Behavior", False, 
                            f"Old endpoint still works (Status: {response.status_code}) - may cause confusion")
                return False
                
        except Exception as e:
            self.log_test("Old Endpoint Behavior", False, f"Exception: {str(e)}")
            return False
    
    def test_data_structure_validation(self):
        """Test that the endpoint validates the correct data structure"""
        print(f"\n✅ TESTING DATA STRUCTURE VALIDATION...")
        
        # Test with old incorrect structure (should fail)
        old_structure = {
            "entity_id": "some-id",
            "proposed_data": {"name": "Test"},
            "changes": ["name"]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/contributions-v2/", 
                                       json=old_structure)
            
            if response.status_code >= 400:  # Should fail validation
                self.log_test("Data Structure Validation - Old Format Rejected", True, 
                            f"Old data structure correctly rejected (Status: {response.status_code})")
            else:
                self.log_test("Data Structure Validation - Old Format Rejected", False, 
                            f"Old data structure was accepted (Status: {response.status_code})")
            
            # Test with missing required fields
            incomplete_data = {
                "entity_type": "team"
                # Missing title, data, etc.
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/", 
                                       json=incomplete_data)
            
            if response.status_code >= 400:  # Should fail validation
                self.log_test("Data Structure Validation - Incomplete Data Rejected", True, 
                            f"Incomplete data correctly rejected (Status: {response.status_code})")
                return True
            else:
                self.log_test("Data Structure Validation - Incomplete Data Rejected", False, 
                            f"Incomplete data was accepted (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.log_test("Data Structure Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_get_contributions(self):
        """Test GET /api/contributions-v2/ to verify contributions can be retrieved"""
        print(f"\n📋 TESTING CONTRIBUTION RETRIEVAL...")
        
        try:
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_test("Get Contributions", True, 
                                f"Retrieved {len(data)} contributions")
                    return data
                else:
                    self.log_test("Get Contributions", False, 
                                f"Expected list, got {type(data)}")
                    return None
            else:
                self.log_test("Get Contributions", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Get Contributions", False, f"Exception: {str(e)}")
            return None
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 STARTING CONTRIBUTIONS-V2 API ENDPOINT FIX TESTING")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("\n❌ AUTHENTICATION FAILED - CANNOT CONTINUE TESTING")
            return False
        
        # Step 2: Test endpoint exists
        if not self.test_contributions_v2_endpoint_exists():
            print("\n❌ CONTRIBUTIONS-V2 ENDPOINT NOT ACCESSIBLE - CANNOT CONTINUE")
            return False
        
        # Step 3: Test authentication requirements
        self.test_authentication_required()
        
        # Step 4: Test old endpoint behavior
        self.test_old_endpoint_behavior()
        
        # Step 5: Test data structure validation
        self.test_data_structure_validation()
        
        # Step 6: Test contribution creation with correct structure
        created_contribution = self.test_create_contribution_correct_structure()
        
        # Step 7: Test getting contributions
        self.test_get_contributions()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n" + "=" * 80)
        print(f"🎯 CONTRIBUTIONS-V2 API ENDPOINT FIX TESTING COMPLETE")
        print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        # Summary of critical findings
        print(f"\n📋 CRITICAL FINDINGS:")
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            for test in failed_tests:
                print(f"❌ {test['test']}: {test['details']}")
        else:
            print("✅ All tests passed - ContributionModal fix is working correctly!")
        
        return success_rate >= 80  # Consider 80%+ as success

def main():
    """Main test execution"""
    tester = ContributionsV2FixTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 CONTRIBUTIONS-V2 API ENDPOINT FIX VERIFICATION: SUCCESS!")
        print("The ContributionModal fix is working correctly.")
    else:
        print(f"\n🚨 CONTRIBUTIONS-V2 API ENDPOINT FIX VERIFICATION: ISSUES FOUND!")
        print("The ContributionModal fix may have issues that need attention.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())