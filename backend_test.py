#!/usr/bin/env python3
"""
TopKit Backend Testing - Unified Form System and Community DB Functionality
Testing the contributions-v2 endpoints, form dependencies, voting system, and authentication
"""

import requests
import json
import base64
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://football-collab.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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

    def test_contributions_v2_get(self):
        """Test GET /api/contributions-v2/ endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if response.status_code == 200:
                data = response.json()
                contributions_count = len(data) if isinstance(data, list) else len(data.get('contributions', []))
                self.log_result(
                    "GET /api/contributions-v2/",
                    True,
                    f"Retrieved {contributions_count} contributions successfully"
                )
                return data
            else:
                self.log_result(
                    "GET /api/contributions-v2/",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("GET /api/contributions-v2/", False, "", str(e))
            return None

    def test_contributions_v2_post(self):
        """Test POST /api/contributions-v2/ endpoint with unified form fields"""
        try:
            # Create a test contribution with unified form fields
            contribution_data = {
                "entity_type": "team",
                "entity_id": None,  # New entity
                "title": "Test Team Contribution - Backend Testing",
                "description": "Testing unified form system with comprehensive team data",
                "changes": {
                    "name": "Test Football Club Backend",
                    "short_name": "TFC-BE",
                    "country": "France",
                    "city": "Paris",
                    "founded_year": 2024,
                    "team_colors": ["Blue", "White", "Red"]
                },
                "source_urls": ["https://example.com/test-team"],
                "images": []  # Will add image in separate test
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                contribution_id = data.get('id') or data.get('contribution_id')
                self.log_result(
                    "POST /api/contributions-v2/ - Create Contribution",
                    True,
                    f"Created contribution with ID: {contribution_id}"
                )
                return contribution_id
            else:
                self.log_result(
                    "POST /api/contributions-v2/ - Create Contribution",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("POST /api/contributions-v2/ - Create Contribution", False, "", str(e))
            return None

    def test_image_upload_for_contributions(self):
        """Test image upload functionality for contributions"""
        try:
            # Create a simple test image (1x1 pixel PNG in base64)
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            # Test contribution with image
            contribution_data = {
                "entity_type": "BRAND",
                "entity_id": None,
                "title": "Test Brand Logo Upload",
                "description": "Testing image upload functionality in unified form",
                "changes": {
                    "name": "Test Brand Backend",
                    "country": "France",
                    "founded_year": 2024
                },
                "images": [
                    {
                        "type": "logo",
                        "data": test_image_base64,
                        "filename": "test_logo.png"
                    }
                ]
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                contribution_id = data.get('id') or data.get('contribution_id')
                self.log_result(
                    "Image Upload for Contributions",
                    True,
                    f"Successfully uploaded image with contribution ID: {contribution_id}"
                )
                return contribution_id
            else:
                self.log_result(
                    "Image Upload for Contributions",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Image Upload for Contributions", False, "", str(e))
            return None

    def test_form_dependency_endpoints(self):
        """Test form dependency endpoints for unified forms"""
        endpoints_to_test = [
            ("/teams", "Teams for dropdowns"),
            ("/brands", "Brands for dropdowns"),
            ("/competitions", "Competitions for dropdowns"),
            ("/master-jerseys", "Master kits for dropdowns")
        ]
        
        all_success = True
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else len(data.get('items', []))
                    self.log_result(
                        f"GET {endpoint}",
                        True,
                        f"{description}: Retrieved {count} items"
                    )
                else:
                    self.log_result(
                        f"GET {endpoint}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_success = False
                    
            except Exception as e:
                self.log_result(f"GET {endpoint}", False, "", str(e))
                all_success = False
        
        return all_success

    def test_voting_system(self, contribution_id):
        """Test voting system for contributions"""
        if not contribution_id:
            self.log_result("Voting System Test", False, "", "No contribution ID provided")
            return False
            
        try:
            # Test upvote
            vote_data = {
                "vote_type": "UPVOTE"
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/{contribution_id}/vote", json=vote_data)
            
            if response.status_code in [200, 201]:
                self.log_result(
                    "Voting System - Upvote",
                    True,
                    f"Successfully cast upvote for contribution {contribution_id}"
                )
                
                # Test downvote (should replace previous vote)
                vote_data["vote_type"] = "DOWNVOTE"
                response = self.session.post(f"{API_BASE}/contributions-v2/{contribution_id}/vote", json=vote_data)
                
                if response.status_code in [200, 201]:
                    self.log_result(
                        "Voting System - Downvote",
                        True,
                        f"Successfully cast downvote for contribution {contribution_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Voting System - Downvote",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Voting System - Upvote",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Voting System Test", False, "", str(e))
            return False

    def test_authentication_requirements(self):
        """Test that endpoints require proper JWT tokens"""
        # Create a session without authentication
        unauth_session = requests.Session()
        
        protected_endpoints = [
            ("/contributions-v2/", "POST", "Create contribution"),
            ("/admin/settings", "GET", "Admin settings"),
            ("/admin/users", "GET", "Admin users")
        ]
        
        all_protected = True
        
        for endpoint, method, description in protected_endpoints:
            try:
                if method == "GET":
                    response = unauth_session.get(f"{API_BASE}{endpoint}")
                elif method == "POST":
                    response = unauth_session.post(f"{API_BASE}{endpoint}", json={})
                
                if response.status_code == 401:
                    self.log_result(
                        f"Authentication Required - {description}",
                        True,
                        f"Endpoint properly protected (HTTP 401)"
                    )
                else:
                    self.log_result(
                        f"Authentication Required - {description}",
                        False,
                        "",
                        f"Expected HTTP 401, got {response.status_code}"
                    )
                    all_protected = False
                    
            except Exception as e:
                self.log_result(f"Authentication Required - {description}", False, "", str(e))
                all_protected = False
        
        return all_protected

    def test_admin_specific_endpoints(self):
        """Test admin-specific endpoints with admin credentials"""
        admin_endpoints = [
            ("/admin/settings", "GET", "Admin settings"),
            ("/admin/dashboard-stats", "GET", "Dashboard statistics"),
            ("/admin/users", "GET", "User management")
        ]
        
        all_success = True
        
        for endpoint, method, description in admin_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        f"Admin Endpoint - {description}",
                        True,
                        f"Successfully accessed admin endpoint"
                    )
                else:
                    self.log_result(
                        f"Admin Endpoint - {description}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_success = False
                    
            except Exception as e:
                self.log_result(f"Admin Endpoint - {description}", False, "", str(e))
                all_success = False
        
        return all_success

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting TopKit Backend Testing - Unified Form System and Community DB")
        print("=" * 80)
        
        # Step 1: Authenticate admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test contributions-v2 GET endpoint
        contributions = self.test_contributions_v2_get()
        
        # Step 3: Test contributions-v2 POST endpoint
        contribution_id = self.test_contributions_v2_post()
        
        # Step 4: Test image upload for contributions
        image_contribution_id = self.test_image_upload_for_contributions()
        
        # Step 5: Test form dependency endpoints
        self.test_form_dependency_endpoints()
        
        # Step 6: Test voting system
        if contribution_id:
            self.test_voting_system(contribution_id)
        
        # Step 7: Test authentication requirements
        self.test_authentication_requirements()
        
        # Step 8: Test admin-specific endpoints
        self.test_admin_specific_endpoints()
        
        # Generate summary
        self.generate_summary()
        
        return True

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: Backend system is working excellently with {success_rate:.1f}% success rate!")
        elif success_rate >= 70:
            print(f"\n✅ GOOD: Backend system is working well with {success_rate:.1f}% success rate.")
        elif success_rate >= 50:
            print(f"\n⚠️ PARTIAL: Backend system has issues but core functionality works ({success_rate:.1f}% success rate).")
        else:
            print(f"\n❌ CRITICAL: Backend system has major issues ({success_rate:.1f}% success rate).")

if __name__ == "__main__":
    tester = TopKitBackendTester()
    tester.run_all_tests()