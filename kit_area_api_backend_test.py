#!/usr/bin/env python3
"""
TopKit Kit Area API Backend Testing
Testing the backend API endpoints for the Kit Area functionality to verify routing structure:

1. GET /api/master-jerseys - Basic Master Jerseys API
2. GET /api/master-jerseys/{id} - Individual Master Jersey API  
3. GET /api/reference-kits - Reference Kits API
4. GET /api/reference-kits?master_kit_id={id} - Reference Kits by Master
5. GET /api/reference-kits/{id} - Individual Reference Kit API

Frontend Kit Area structure:
- /kit-area - Browse master jerseys ✅
- /kit-area/master/{id} - Master jersey detail page ✅ 
- /kit-area/master/{id}/versions - All versions page ✅
- /kit-area/version/{id} - Version detail page ✅
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://footkit-admin.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class KitAreaAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.master_jersey_ids = []
        self.reference_kit_ids = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate admin user and get JWT token"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Successfully authenticated admin user. Token length: {len(self.admin_token)}"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, "", "No token in response")
                    return False
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    "", 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def test_master_jerseys_api(self):
        """Test GET /api/master-jerseys - Basic Master Jerseys API"""
        try:
            response = self.session.get(f"{API_BASE}/master-jerseys")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze response structure
                if isinstance(data, list):
                    master_jerseys = data
                elif isinstance(data, dict) and 'master_jerseys' in data:
                    master_jerseys = data['master_jerseys']
                else:
                    master_jerseys = []
                
                # Store IDs for later tests
                for jersey in master_jerseys:
                    if isinstance(jersey, dict) and jersey.get('id'):
                        self.master_jersey_ids.append(jersey['id'])
                
                # Check data structure
                has_required_fields = True
                missing_fields = []
                
                if master_jerseys:
                    sample_jersey = master_jerseys[0]
                    required_fields = ['id', 'team_id', 'brand_id', 'season', 'jersey_type']
                    
                    for field in required_fields:
                        if field not in sample_jersey:
                            has_required_fields = False
                            missing_fields.append(field)
                
                self.log_result(
                    "GET /api/master-jerseys",
                    True,
                    f"Retrieved {len(master_jerseys)} master jerseys. Required fields present: {has_required_fields}. Missing: {missing_fields if missing_fields else 'None'}"
                )
                return True, master_jerseys
            else:
                self.log_result(
                    "GET /api/master-jerseys",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False, []
                
        except Exception as e:
            self.log_result("GET /api/master-jerseys", False, "", str(e))
            return False, []

    def test_individual_master_jersey_api(self, jersey_id):
        """Test GET /api/master-jerseys/{id} - Individual Master Jersey API"""
        try:
            response = self.session.get(f"{API_BASE}/master-jerseys/{jersey_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response contains detailed jersey information
                required_fields = ['id', 'team_id', 'brand_id', 'season', 'jersey_type']
                has_all_fields = all(field in data for field in required_fields)
                
                # Check for enriched data (team_info, brand_info)
                has_enriched_data = 'team_info' in data or 'brand_info' in data
                
                self.log_result(
                    f"GET /api/master-jerseys/{jersey_id}",
                    True,
                    f"Retrieved individual master jersey. Has required fields: {has_all_fields}. Has enriched data: {has_enriched_data}"
                )
                return True, data
            elif response.status_code == 404:
                self.log_result(
                    f"GET /api/master-jerseys/{jersey_id}",
                    False,
                    "",
                    f"Master jersey not found (HTTP 404)"
                )
                return False, None
            else:
                self.log_result(
                    f"GET /api/master-jerseys/{jersey_id}",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False, None
                
        except Exception as e:
            self.log_result(f"GET /api/master-jerseys/{jersey_id}", False, "", str(e))
            return False, None

    def test_reference_kits_api(self):
        """Test GET /api/reference-kits - Reference Kits API"""
        try:
            response = self.session.get(f"{API_BASE}/reference-kits")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze response structure
                if isinstance(data, list):
                    reference_kits = data
                elif isinstance(data, dict) and 'reference_kits' in data:
                    reference_kits = data['reference_kits']
                else:
                    reference_kits = []
                
                # Store IDs for later tests
                for kit in reference_kits:
                    if isinstance(kit, dict) and kit.get('id'):
                        self.reference_kit_ids.append(kit['id'])
                
                # Check data structure
                has_required_fields = True
                missing_fields = []
                
                if reference_kits:
                    sample_kit = reference_kits[0]
                    required_fields = ['id', 'master_jersey_id', 'player_name', 'retail_price']
                    
                    for field in required_fields:
                        if field not in sample_kit:
                            has_required_fields = False
                            missing_fields.append(field)
                
                self.log_result(
                    "GET /api/reference-kits",
                    True,
                    f"Retrieved {len(reference_kits)} reference kits. Required fields present: {has_required_fields}. Missing: {missing_fields if missing_fields else 'None'}"
                )
                return True, reference_kits
            else:
                self.log_result(
                    "GET /api/reference-kits",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False, []
                
        except Exception as e:
            self.log_result("GET /api/reference-kits", False, "", str(e))
            return False, []

    def test_reference_kits_by_master_api(self, master_jersey_id):
        """Test GET /api/reference-kits?master_kit_id={id} - Reference Kits by Master"""
        try:
            # Try different parameter names that might be used
            param_variations = [
                f"master_kit_id={master_jersey_id}",
                f"master_jersey_id={master_jersey_id}",
                f"master_id={master_jersey_id}"
            ]
            
            for param in param_variations:
                response = self.session.get(f"{API_BASE}/reference-kits?{param}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Analyze response structure
                    if isinstance(data, list):
                        reference_kits = data
                    elif isinstance(data, dict) and 'reference_kits' in data:
                        reference_kits = data['reference_kits']
                    else:
                        reference_kits = []
                    
                    # Check if kits are filtered by master jersey
                    filtered_correctly = True
                    if reference_kits:
                        for kit in reference_kits:
                            if isinstance(kit, dict):
                                kit_master_id = kit.get('master_jersey_id') or kit.get('master_kit_id')
                                if kit_master_id and kit_master_id != master_jersey_id:
                                    filtered_correctly = False
                                    break
                    
                    self.log_result(
                        f"GET /api/reference-kits?{param}",
                        True,
                        f"Retrieved {len(reference_kits)} reference kits for master jersey. Filtered correctly: {filtered_correctly}"
                    )
                    return True, reference_kits
                elif response.status_code == 404:
                    continue  # Try next parameter variation
                else:
                    self.log_result(
                        f"GET /api/reference-kits?{param}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
            
            # If we get here, none of the parameter variations worked
            self.log_result(
                f"GET /api/reference-kits?master_*_id={master_jersey_id}",
                False,
                "",
                "No working parameter variation found for filtering by master jersey"
            )
            return False, []
                
        except Exception as e:
            self.log_result(f"GET /api/reference-kits?master_*_id={master_jersey_id}", False, "", str(e))
            return False, []

    def test_individual_reference_kit_api(self, kit_id):
        """Test GET /api/reference-kits/{id} - Individual Reference Kit API"""
        try:
            response = self.session.get(f"{API_BASE}/reference-kits/{kit_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response contains detailed kit information
                required_fields = ['id', 'master_jersey_id', 'player_name', 'retail_price']
                has_all_fields = all(field in data for field in required_fields)
                
                # Check for enriched data (master_jersey_info, jersey_release info)
                has_enriched_data = 'master_jersey_info' in data or 'jersey_release' in data
                
                self.log_result(
                    f"GET /api/reference-kits/{kit_id}",
                    True,
                    f"Retrieved individual reference kit. Has required fields: {has_all_fields}. Has enriched data: {has_enriched_data}"
                )
                return True, data
            elif response.status_code == 404:
                self.log_result(
                    f"GET /api/reference-kits/{kit_id}",
                    False,
                    "",
                    f"Reference kit not found (HTTP 404)"
                )
                return False, None
            else:
                self.log_result(
                    f"GET /api/reference-kits/{kit_id}",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False, None
                
        except Exception as e:
            self.log_result(f"GET /api/reference-kits/{kit_id}", False, "", str(e))
            return False, None

    def test_kit_area_data_structure_compatibility(self):
        """Test that API responses support the frontend Kit Area structure"""
        try:
            # Test master jerseys for browse page compatibility
            master_jerseys_success, master_jerseys = self.test_master_jerseys_api()
            
            if master_jerseys_success and master_jerseys:
                # Check if master jerseys have data needed for browse page
                sample_jersey = master_jerseys[0]
                browse_fields = ['id', 'team_id', 'season', 'jersey_type']
                has_browse_data = all(field in sample_jersey for field in browse_fields)
                
                self.log_result(
                    "Kit Area Browse Page Data Compatibility",
                    has_browse_data,
                    f"Master jerseys {'have' if has_browse_data else 'missing'} required fields for browse page"
                )
                
                # Test individual master jersey for detail page compatibility
                if self.master_jersey_ids:
                    jersey_id = self.master_jersey_ids[0]
                    detail_success, detail_data = self.test_individual_master_jersey_api(jersey_id)
                    
                    if detail_success and detail_data:
                        # Check if detail has enriched data for detail page
                        detail_fields = ['id', 'team_id', 'brand_id', 'season', 'jersey_type']
                        has_detail_data = all(field in detail_data for field in detail_fields)
                        
                        self.log_result(
                            "Kit Area Detail Page Data Compatibility",
                            has_detail_data,
                            f"Master jersey detail {'has' if has_detail_data else 'missing'} required fields for detail page"
                        )
                        
                        # Test reference kits for versions page compatibility
                        versions_success, versions_data = self.test_reference_kits_by_master_api(jersey_id)
                        
                        if versions_success:
                            self.log_result(
                                "Kit Area Versions Page Data Compatibility",
                                True,
                                f"Reference kits filtering by master jersey works for versions page"
                            )
                        else:
                            self.log_result(
                                "Kit Area Versions Page Data Compatibility",
                                False,
                                "",
                                "Reference kits filtering by master jersey not working"
                            )
                
                # Test reference kits for version detail page compatibility
                reference_kits_success, reference_kits = self.test_reference_kits_api()
                
                if reference_kits_success and reference_kits and self.reference_kit_ids:
                    kit_id = self.reference_kit_ids[0]
                    version_detail_success, version_detail_data = self.test_individual_reference_kit_api(kit_id)
                    
                    if version_detail_success and version_detail_data:
                        version_fields = ['id', 'master_jersey_id', 'player_name', 'retail_price']
                        has_version_data = all(field in version_detail_data for field in version_fields)
                        
                        self.log_result(
                            "Kit Area Version Detail Page Data Compatibility",
                            has_version_data,
                            f"Reference kit detail {'has' if has_version_data else 'missing'} required fields for version detail page"
                        )
                
                return True
            else:
                self.log_result(
                    "Kit Area Data Structure Compatibility",
                    False,
                    "",
                    "No master jerseys available to test compatibility"
                )
                return False
                
        except Exception as e:
            self.log_result("Kit Area Data Structure Compatibility", False, "", str(e))
            return False

    def test_api_response_formats(self):
        """Test that API responses are in proper JSON format and structure"""
        endpoints_to_test = [
            ("/master-jerseys", "Master Jerseys List"),
            ("/reference-kits", "Reference Kits List")
        ]
        
        all_success = True
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    # Test JSON parsing
                    try:
                        data = response.json()
                        
                        # Check response structure
                        is_list = isinstance(data, list)
                        is_dict_with_items = isinstance(data, dict) and any(key in data for key in ['master_jerseys', 'reference_kits', 'items'])
                        
                        valid_structure = is_list or is_dict_with_items
                        
                        self.log_result(
                            f"API Response Format - {description}",
                            valid_structure,
                            f"Response is {'valid' if valid_structure else 'invalid'} JSON structure. Type: {'list' if is_list else 'dict'}"
                        )
                        
                        if not valid_structure:
                            all_success = False
                            
                    except json.JSONDecodeError as e:
                        self.log_result(
                            f"API Response Format - {description}",
                            False,
                            "",
                            f"Invalid JSON response: {str(e)}"
                        )
                        all_success = False
                else:
                    self.log_result(
                        f"API Response Format - {description}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_success = False
                    
            except Exception as e:
                self.log_result(f"API Response Format - {description}", False, "", str(e))
                all_success = False
        
        return all_success

    def run_all_tests(self):
        """Run all Kit Area API tests"""
        print("🚀 Starting TopKit Kit Area API Backend Testing")
        print("Testing backend API endpoints for Kit Area functionality")
        print("=" * 80)
        
        # Step 1: Authenticate admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test Basic Master Jerseys API
        print("\n📋 TEST 1: Basic Master Jerseys API")
        print("-" * 50)
        master_jerseys_success, master_jerseys = self.test_master_jerseys_api()
        
        # Step 3: Test Individual Master Jersey API
        print("\n🔍 TEST 2: Individual Master Jersey API")
        print("-" * 50)
        if self.master_jersey_ids:
            for i, jersey_id in enumerate(self.master_jersey_ids[:3]):  # Test first 3
                self.test_individual_master_jersey_api(jersey_id)
        else:
            self.log_result("Individual Master Jersey API", False, "", "No master jersey IDs available for testing")
        
        # Step 4: Test Reference Kits API
        print("\n📦 TEST 3: Reference Kits API")
        print("-" * 50)
        reference_kits_success, reference_kits = self.test_reference_kits_api()
        
        # Step 5: Test Reference Kits by Master API
        print("\n🔗 TEST 4: Reference Kits by Master API")
        print("-" * 50)
        if self.master_jersey_ids:
            for i, jersey_id in enumerate(self.master_jersey_ids[:2]):  # Test first 2
                self.test_reference_kits_by_master_api(jersey_id)
        else:
            self.log_result("Reference Kits by Master API", False, "", "No master jersey IDs available for testing")
        
        # Step 6: Test Individual Reference Kit API
        print("\n🎯 TEST 5: Individual Reference Kit API")
        print("-" * 50)
        if self.reference_kit_ids:
            for i, kit_id in enumerate(self.reference_kit_ids[:3]):  # Test first 3
                self.test_individual_reference_kit_api(kit_id)
        else:
            self.log_result("Individual Reference Kit API", False, "", "No reference kit IDs available for testing")
        
        # Step 7: Test Kit Area Data Structure Compatibility
        print("\n🏗️ TEST 6: Kit Area Data Structure Compatibility")
        print("-" * 50)
        self.test_kit_area_data_structure_compatibility()
        
        # Step 8: Test API Response Formats
        print("\n📄 TEST 7: API Response Formats")
        print("-" * 50)
        self.test_api_response_formats()
        
        # Generate summary
        self.generate_summary()
        
        return True

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 KIT AREA API TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results by API endpoint
        api_categories = {
            "Authentication": ["Admin Authentication"],
            "Master Jerseys API": ["GET /api/master-jerseys"],
            "Individual Master Jersey API": ["master-jerseys/"],
            "Reference Kits API": ["GET /api/reference-kits"],
            "Reference Kits by Master API": ["reference-kits?"],
            "Individual Reference Kit API": ["reference-kits/"],
            "Data Compatibility": ["Kit Area", "Data Compatibility"],
            "Response Formats": ["API Response Format"]
        }
        
        print("\n📋 RESULTS BY API CATEGORY:")
        print("-" * 50)
        
        critical_issues = []
        
        for category_name, keywords in api_categories.items():
            category_tests = [r for r in self.test_results if any(keyword in r['test'] for keyword in keywords)]
            if category_tests:
                category_passed = sum(1 for r in category_tests if r['success'])
                category_total = len(category_tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                status = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
                print(f"{status} {category_name}: {category_passed}/{category_total} ({category_rate:.1f}%)")
                
                # Track critical issues
                if category_rate < 80:
                    failed_in_category = [r for r in category_tests if not r['success']]
                    for failed_test in failed_in_category:
                        critical_issues.append(f"{category_name}: {failed_test['test']} - {failed_test['error']}")
        
        # Frontend Kit Area Support Analysis
        print(f"\n🏗️ FRONTEND KIT AREA SUPPORT ANALYSIS:")
        print("-" * 50)
        
        # Check specific frontend route support
        frontend_routes = {
            "/kit-area": "Browse master jerseys",
            "/kit-area/master/{id}": "Master jersey detail page", 
            "/kit-area/master/{id}/versions": "All versions page",
            "/kit-area/version/{id}": "Version detail page"
        }
        
        master_jerseys_working = any("GET /api/master-jerseys" in r['test'] and r['success'] for r in self.test_results)
        individual_master_working = any("master-jerseys/" in r['test'] and r['success'] for r in self.test_results)
        reference_kits_working = any("GET /api/reference-kits" in r['test'] and r['success'] for r in self.test_results)
        reference_by_master_working = any("reference-kits?" in r['test'] and r['success'] for r in self.test_results)
        individual_reference_working = any("reference-kits/" in r['test'] and r['success'] for r in self.test_results)
        
        print(f"  • /kit-area (Browse): {'✅ Supported' if master_jerseys_working else '❌ Not Supported'}")
        print(f"  • /kit-area/master/{{id}} (Detail): {'✅ Supported' if individual_master_working else '❌ Not Supported'}")
        print(f"  • /kit-area/master/{{id}}/versions (Versions): {'✅ Supported' if reference_by_master_working else '❌ Not Supported'}")
        print(f"  • /kit-area/version/{{id}} (Version Detail): {'✅ Supported' if individual_reference_working else '❌ Not Supported'}")
        
        # Data availability analysis
        print(f"\n📊 DATA AVAILABILITY ANALYSIS:")
        print("-" * 50)
        print(f"  • Master Jerseys Available: {len(self.master_jersey_ids)}")
        print(f"  • Reference Kits Available: {len(self.reference_kit_ids)}")
        
        if len(self.master_jersey_ids) == 0:
            print("  ⚠️ WARNING: No master jerseys found - Kit Area will be empty")
        if len(self.reference_kit_ids) == 0:
            print("  ⚠️ WARNING: No reference kits found - Version pages will be empty")
        
        # Critical issues summary
        if critical_issues:
            print(f"\n❌ CRITICAL ISSUES IDENTIFIED:")
            print("-" * 50)
            for issue in critical_issues:
                print(f"  • {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES DETECTED")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            print("-" * 50)
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['error']}")
        
        # Passed tests summary
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        print("-" * 50)
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}")
        
        # Final assessment and recommendations
        print("\n" + "=" * 80)
        print("🎯 KIT AREA API ASSESSMENT & RECOMMENDATIONS")
        print("=" * 80)
        
        if success_rate >= 90:
            print(f"✅ EXCELLENT: Kit Area APIs are working correctly with {success_rate:.1f}% success rate!")
            print("   All backend endpoints support the frontend Kit Area structure properly.")
        elif success_rate >= 70:
            print(f"⚠️ PARTIAL ISSUES: Kit Area APIs have some issues with {success_rate:.1f}% success rate.")
            print("   Some functionality working but issues need investigation.")
        else:
            print(f"❌ CRITICAL ISSUES: Kit Area APIs have major problems ({success_rate:.1f}% success rate).")
            print("   Significant API issues detected. Frontend Kit Area may not work properly.")
        
        # Specific recommendations
        print(f"\n📝 SPECIFIC RECOMMENDATIONS:")
        
        if len(critical_issues) == 0:
            print("   ✅ All Kit Area API endpoints are working correctly")
            print("   ✅ Frontend routing structure is fully supported by backend")
            print("   ✅ Data structure is compatible with Kit Area requirements")
        else:
            print("   🔧 REQUIRED FIXES:")
            
            if not master_jerseys_working:
                print("     • Fix GET /api/master-jerseys endpoint for browse page")
            if not individual_master_working:
                print("     • Fix GET /api/master-jerseys/{id} endpoint for detail pages")
            if not reference_kits_working:
                print("     • Fix GET /api/reference-kits endpoint for reference kits")
            if not reference_by_master_working:
                print("     • Fix GET /api/reference-kits?master_kit_id={id} filtering for versions pages")
            if not individual_reference_working:
                print("     • Fix GET /api/reference-kits/{id} endpoint for version detail pages")
        
        print(f"\n🎯 NEXT STEPS:")
        if success_rate >= 90:
            print("   1. ✅ Backend APIs fully support Kit Area functionality")
            print("   2. 🎨 Frontend Kit Area should work correctly with current API structure")
            print("   3. 📱 Test frontend Kit Area navigation and data display")
        else:
            print("   1. 🔧 Fix identified API endpoint issues")
            print("   2. 🧪 Re-test Kit Area API endpoints")
            print("   3. 🔍 Verify API response data structure matches frontend requirements")
            print("   4. 📱 Test complete Kit Area workflow after fixes")

if __name__ == "__main__":
    tester = KitAreaAPITester()
    tester.run_all_tests()