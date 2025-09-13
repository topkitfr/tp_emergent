#!/usr/bin/env python3

"""
API Endpoints Debug Test
Testing specific API endpoints that are reported as not being registered.

Test Requirements from Review Request:
1. Test `/api/master-jerseys/{master_jersey_id}` - backward compatibility endpoint 
2. Test `/api/reference-kits` - backward compatibility endpoint
3. Verify working endpoints like `/api/master-kits` and `/api/stats`
4. Test specific master kit: 7274ceb6-45d1-47fa-8ce2-a79675a977ea
5. Check for import/syntax errors preventing route registration
6. Verify backend server is loading routes properly
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
SPECIFIC_MASTER_KIT_ID = "7274ceb6-45d1-47fa-8ce2-a79675a977ea"

class APIEndpointsDebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} - {test_name}: {details}")

    def authenticate_admin(self):
        """Test admin authentication"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    
                    self.log_test(
                        "Admin Authentication", 
                        True, 
                        f"Successfully authenticated. Token length: {len(self.admin_token)}, Role: {user_data.get('role')}"
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token received")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_working_endpoints(self):
        """Test endpoints that should be working"""
        print("\n✅ TESTING KNOWN WORKING ENDPOINTS")
        
        working_endpoints = [
            ("/stats", "Stats endpoint"),
            ("/master-kits", "Master Kits list endpoint"),
            ("/teams", "Teams endpoint"),
            ("/brands", "Brands endpoint"),
            ("/competitions", "Competitions endpoint")
        ]
        
        for endpoint, description in working_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Working Endpoint - {description}", 
                        True, 
                        f"Status: {response.status_code}, Response type: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                    )
                else:
                    self.log_test(
                        f"Working Endpoint - {description}", 
                        False, 
                        f"Unexpected status: {response.status_code} - {response.text[:200]}"
                    )
                    
            except Exception as e:
                self.log_test(f"Working Endpoint - {description}", False, f"Exception: {str(e)}")

    def test_problematic_endpoints(self):
        """Test the endpoints that are reported as not working"""
        print("\n🔍 TESTING PROBLEMATIC ENDPOINTS")
        
        # Test 1: /api/reference-kits endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/reference-kits")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Reference Kits Endpoint", 
                    True, 
                    f"Status: {response.status_code}, Response type: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                )
            else:
                self.log_test(
                    "Reference Kits Endpoint", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_test("Reference Kits Endpoint", False, f"Exception: {str(e)}")
        
        # Test 2: /api/reference-kits with master_kit_id parameter
        try:
            response = self.session.get(f"{BACKEND_URL}/reference-kits?master_kit_id={SPECIFIC_MASTER_KIT_ID}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Reference Kits with Master Kit ID", 
                    True, 
                    f"Status: {response.status_code}, Response type: {type(data)}, Length: {len(data) if isinstance(data, list) else 'N/A'}"
                )
            else:
                self.log_test(
                    "Reference Kits with Master Kit ID", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_test("Reference Kits with Master Kit ID", False, f"Exception: {str(e)}")

    def test_master_jersey_backward_compatibility(self):
        """Test the master-jerseys backward compatibility endpoint"""
        print("\n🔄 TESTING MASTER-JERSEYS BACKWARD COMPATIBILITY")
        
        # First, get a list of master kits to find valid IDs
        try:
            response = self.session.get(f"{BACKEND_URL}/master-kits")
            
            if response.status_code == 200:
                master_kits = response.json()
                
                if master_kits:
                    # Test with the first available master kit ID
                    first_kit_id = master_kits[0].get('id')
                    
                    if first_kit_id:
                        # Test master-jerseys endpoint with valid ID
                        jersey_response = self.session.get(f"{BACKEND_URL}/master-jerseys/{first_kit_id}")
                        
                        if jersey_response.status_code == 200:
                            jersey_data = jersey_response.json()
                            self.log_test(
                                "Master Jersey Backward Compatibility - Valid ID", 
                                True, 
                                f"Status: {jersey_response.status_code}, Kit ID: {first_kit_id}, Kit name: {jersey_data.get('club', 'Unknown')}"
                            )
                        else:
                            self.log_test(
                                "Master Jersey Backward Compatibility - Valid ID", 
                                False, 
                                f"Status: {jersey_response.status_code}, Response: {jersey_response.text[:200]}"
                            )
                    
                    # Test with the specific master kit ID from the review request
                    specific_response = self.session.get(f"{BACKEND_URL}/master-jerseys/{SPECIFIC_MASTER_KIT_ID}")
                    
                    if specific_response.status_code == 200:
                        specific_data = specific_response.json()
                        self.log_test(
                            "Master Jersey Backward Compatibility - Specific ID", 
                            True, 
                            f"Status: {specific_response.status_code}, Kit ID: {SPECIFIC_MASTER_KIT_ID}, Kit name: {specific_data.get('club', 'Unknown')}"
                        )
                    elif specific_response.status_code == 404:
                        self.log_test(
                            "Master Jersey Backward Compatibility - Specific ID", 
                            False, 
                            f"Master kit {SPECIFIC_MASTER_KIT_ID} not found (404). This may be expected if the kit doesn't exist in the database."
                        )
                    else:
                        self.log_test(
                            "Master Jersey Backward Compatibility - Specific ID", 
                            False, 
                            f"Status: {specific_response.status_code}, Response: {specific_response.text[:200]}"
                        )
                        
                else:
                    self.log_test(
                        "Master Jersey Backward Compatibility", 
                        False, 
                        "No master kits found to test backward compatibility"
                    )
                    
            else:
                self.log_test(
                    "Master Jersey Backward Compatibility Setup", 
                    False, 
                    f"Failed to get master kits list: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Master Jersey Backward Compatibility", False, f"Exception: {str(e)}")

    def test_route_registration_health(self):
        """Test if the server is properly loading routes"""
        print("\n🏥 TESTING ROUTE REGISTRATION HEALTH")
        
        # Test root endpoint
        try:
            response = self.session.get(f"{BACKEND_URL.replace('/api', '')}/")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Root Endpoint Health", 
                    True, 
                    f"Status: {response.status_code}, Message: {data.get('message', 'No message')}, Version: {data.get('version', 'Unknown')}"
                )
            else:
                self.log_test(
                    "Root Endpoint Health", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_test("Root Endpoint Health", False, f"Exception: {str(e)}")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{BACKEND_URL.replace('/api', '')}/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Endpoint", 
                    True, 
                    f"Status: {response.status_code}, Health status: {data.get('status', 'Unknown')}"
                )
            else:
                self.log_test(
                    "Health Endpoint", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Exception: {str(e)}")

    def test_master_kits_detailed(self):
        """Test master-kits endpoint in detail to understand the data structure"""
        print("\n🔍 TESTING MASTER-KITS ENDPOINT IN DETAIL")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/master-kits")
            
            if response.status_code == 200:
                master_kits = response.json()
                
                self.log_test(
                    "Master Kits List", 
                    True, 
                    f"Found {len(master_kits)} master kits"
                )
                
                # Check if the specific master kit exists
                specific_kit = None
                for kit in master_kits:
                    if kit.get('id') == SPECIFIC_MASTER_KIT_ID:
                        specific_kit = kit
                        break
                
                if specific_kit:
                    self.log_test(
                        "Specific Master Kit Exists", 
                        True, 
                        f"Found master kit {SPECIFIC_MASTER_KIT_ID}: {specific_kit.get('club', 'Unknown')} {specific_kit.get('season', 'Unknown')}"
                    )
                else:
                    self.log_test(
                        "Specific Master Kit Exists", 
                        False, 
                        f"Master kit {SPECIFIC_MASTER_KIT_ID} not found in the database"
                    )
                
                # Show sample of available master kits
                if master_kits:
                    sample_kits = master_kits[:3]  # Show first 3 kits
                    kit_info = []
                    for kit in sample_kits:
                        kit_info.append(f"ID: {kit.get('id', 'Unknown')}, Club: {kit.get('club', 'Unknown')}, Season: {kit.get('season', 'Unknown')}")
                    
                    self.log_test(
                        "Available Master Kits Sample", 
                        True, 
                        f"Sample kits: {'; '.join(kit_info)}"
                    )
                    
            else:
                self.log_test(
                    "Master Kits List", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_test("Master Kits Detailed", False, f"Exception: {str(e)}")

    def test_individual_master_kit_access(self):
        """Test accessing individual master kits by ID"""
        print("\n🎯 TESTING INDIVIDUAL MASTER KIT ACCESS")
        
        try:
            # First get the list of master kits
            response = self.session.get(f"{BACKEND_URL}/master-kits")
            
            if response.status_code == 200:
                master_kits = response.json()
                
                if master_kits:
                    # Test with the first available master kit
                    first_kit_id = master_kits[0].get('id')
                    
                    if first_kit_id:
                        kit_response = self.session.get(f"{BACKEND_URL}/master-kits/{first_kit_id}")
                        
                        if kit_response.status_code == 200:
                            kit_data = kit_response.json()
                            self.log_test(
                                "Individual Master Kit Access - Valid ID", 
                                True, 
                                f"Successfully accessed master kit {first_kit_id}: {kit_data.get('club', 'Unknown')}"
                            )
                        else:
                            self.log_test(
                                "Individual Master Kit Access - Valid ID", 
                                False, 
                                f"Status: {kit_response.status_code}, Response: {kit_response.text[:200]}"
                            )
                    
                    # Test with the specific master kit ID
                    specific_response = self.session.get(f"{BACKEND_URL}/master-kits/{SPECIFIC_MASTER_KIT_ID}")
                    
                    if specific_response.status_code == 200:
                        specific_data = specific_response.json()
                        self.log_test(
                            "Individual Master Kit Access - Specific ID", 
                            True, 
                            f"Successfully accessed specific master kit {SPECIFIC_MASTER_KIT_ID}: {specific_data.get('club', 'Unknown')}"
                        )
                    elif specific_response.status_code == 404:
                        self.log_test(
                            "Individual Master Kit Access - Specific ID", 
                            False, 
                            f"Master kit {SPECIFIC_MASTER_KIT_ID} not found (404)"
                        )
                    else:
                        self.log_test(
                            "Individual Master Kit Access - Specific ID", 
                            False, 
                            f"Status: {specific_response.status_code}, Response: {specific_response.text[:200]}"
                        )
                        
                else:
                    self.log_test(
                        "Individual Master Kit Access", 
                        False, 
                        "No master kits available to test individual access"
                    )
                    
            else:
                self.log_test(
                    "Individual Master Kit Access Setup", 
                    False, 
                    f"Failed to get master kits list: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Individual Master Kit Access", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all API endpoint debug tests"""
        print("🚀 STARTING API ENDPOINTS DEBUG TESTS")
        print("=" * 80)
        
        # Test 1: Admin Authentication (optional for some endpoints)
        self.authenticate_admin()
        
        # Test 2: Known Working Endpoints
        self.test_working_endpoints()
        
        # Test 3: Route Registration Health
        self.test_route_registration_health()
        
        # Test 4: Master Kits Detailed Analysis
        self.test_master_kits_detailed()
        
        # Test 5: Individual Master Kit Access
        self.test_individual_master_kit_access()
        
        # Test 6: Problematic Endpoints
        self.test_problematic_endpoints()
        
        # Test 7: Master Jersey Backward Compatibility
        self.test_master_jersey_backward_compatibility()
        
        # Print summary
        self.print_test_summary()
        
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 API ENDPOINTS DEBUG TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        
        # Specific analysis for the review request
        print(f"\n🔍 SPECIFIC ANALYSIS FOR REVIEW REQUEST:")
        
        # Check reference-kits endpoint
        ref_kits_test = next((r for r in self.test_results if 'Reference Kits Endpoint' in r['test']), None)
        if ref_kits_test:
            if ref_kits_test['success']:
                print(f"   ✅ /api/reference-kits endpoint is working correctly")
            else:
                print(f"   ❌ /api/reference-kits endpoint has issues: {ref_kits_test['details']}")
        
        # Check master-jerseys backward compatibility
        master_jersey_test = next((r for r in self.test_results if 'Master Jersey Backward Compatibility' in r['test']), None)
        if master_jersey_test:
            if master_jersey_test['success']:
                print(f"   ✅ /api/master-jerseys/{{id}} endpoint is working correctly")
            else:
                print(f"   ❌ /api/master-jerseys/{{id}} endpoint has issues: {master_jersey_test['details']}")
        
        # Check specific master kit
        specific_kit_test = next((r for r in self.test_results if 'Specific Master Kit' in r['test']), None)
        if specific_kit_test:
            if specific_kit_test['success']:
                print(f"   ✅ Master kit {SPECIFIC_MASTER_KIT_ID} exists and is accessible")
            else:
                print(f"   ❌ Master kit {SPECIFIC_MASTER_KIT_ID} is not accessible: {specific_kit_test['details']}")

def main():
    """Main test execution"""
    tester = APIEndpointsDebugTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n🏁 TESTING COMPLETED")
        else:
            print(f"\n💥 TESTING FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()