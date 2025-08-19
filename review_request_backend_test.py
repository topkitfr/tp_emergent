#!/usr/bin/env python3
"""
TopKit Review Request Backend Testing
Testing basic functionality after UI modifications to verify system is working properly
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://profile-friends.preview.emergentagent.com/api"

# Test credentials as requested
TEST_USER = {
    "email": "friendstest2@example.com",
    "password": "TopKit123!"
}

ADMIN_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class ReviewRequestTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.admin_token = None
        
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
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
    
    def test_user_authentication(self):
        """Test basic authentication with friendstest2@example.com / TopKit123!"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_token = data['token']
                    user_info = data.get('user', {})
                    self.log_result(
                        "User Authentication", 
                        True, 
                        f"Login successful - Name: {user_info.get('name', 'N/A')}, Role: {user_info.get('role', 'N/A')}, ID: {user_info.get('id', 'N/A')}"
                    )
                    return True
                else:
                    self.log_result("User Authentication", False, "", "No token in response")
                    return False
            else:
                self.log_result("User Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, "", str(e))
            return False
    
    def test_admin_authentication(self):
        """Test admin authentication"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_USER)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.admin_token = data['token']
                    user_info = data.get('user', {})
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Admin login successful - Name: {user_info.get('name', 'N/A')}, Role: {user_info.get('role', 'N/A')}, ID: {user_info.get('id', 'N/A')}"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, "", "No token in response")
                    return False
            else:
                self.log_result("Admin Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False
    
    def test_jerseys_endpoint(self):
        """Test jerseys API endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                data = response.json()
                jersey_count = len(data) if isinstance(data, list) else 0
                self.log_result(
                    "Jerseys Endpoint", 
                    True, 
                    f"Jerseys endpoint accessible - Found {jersey_count} jerseys"
                )
                return True
            else:
                self.log_result("Jerseys Endpoint", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Jerseys Endpoint", False, "", str(e))
            return False
    
    def test_marketplace_endpoint(self):
        """Test marketplace API endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/marketplace/catalog")
            
            if response.status_code == 200:
                data = response.json()
                catalog_count = len(data) if isinstance(data, list) else 0
                self.log_result(
                    "Marketplace Endpoint", 
                    True, 
                    f"Marketplace catalog accessible - Found {catalog_count} items"
                )
                return True
            else:
                self.log_result("Marketplace Endpoint", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Marketplace Endpoint", False, "", str(e))
            return False
    
    def test_authenticated_endpoints(self):
        """Test authenticated endpoints with user token"""
        if not self.auth_token:
            self.log_result("Authenticated Endpoints", False, "", "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        endpoints_tested = 0
        endpoints_passed = 0
        
        # Test profile endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
                data = response.json()
                print(f"    Profile endpoint: ✅ - User: {data.get('name', 'N/A')}")
            else:
                print(f"    Profile endpoint: ❌ - HTTP {response.status_code}")
        except Exception as e:
            endpoints_tested += 1
            print(f"    Profile endpoint: ❌ - Error: {e}")
        
        # Test notifications endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers)
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
                data = response.json()
                notification_count = len(data) if isinstance(data, list) else 0
                print(f"    Notifications endpoint: ✅ - {notification_count} notifications")
            else:
                print(f"    Notifications endpoint: ❌ - HTTP {response.status_code}")
        except Exception as e:
            endpoints_tested += 1
            print(f"    Notifications endpoint: ❌ - Error: {e}")
        
        success = endpoints_passed > 0
        self.log_result(
            "Authenticated Endpoints", 
            success, 
            f"{endpoints_passed}/{endpoints_tested} authenticated endpoints working"
        )
        return success
    
    def test_site_configuration(self):
        """Test site configuration endpoints"""
        try:
            response = self.session.get(f"{BACKEND_URL}/site/mode")
            
            if response.status_code == 200:
                data = response.json()
                mode = data.get('mode', 'unknown')
                self.log_result(
                    "Site Configuration", 
                    True, 
                    f"Site mode endpoint accessible - Current mode: {mode}"
                )
                return True
            else:
                self.log_result("Site Configuration", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Site Configuration", False, "", str(e))
            return False
    
    def test_explorer_endpoints(self):
        """Test explorer API endpoints"""
        try:
            response = self.session.get(f"{BACKEND_URL}/explorer/leagues")
            
            if response.status_code == 200:
                data = response.json()
                league_count = len(data) if isinstance(data, list) else 0
                self.log_result(
                    "Explorer Endpoints", 
                    True, 
                    f"Explorer leagues endpoint accessible - Found {league_count} leagues"
                )
                return True
            else:
                self.log_result("Explorer Endpoints", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Explorer Endpoints", False, "", str(e))
            return False
    
    def test_backend_health(self):
        """Test overall backend health"""
        try:
            # Test a simple endpoint to verify backend is responding
            response = self.session.get(f"{BACKEND_URL}/stats/dynamic")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Backend Health", 
                    True, 
                    f"Backend responding correctly - Stats endpoint operational"
                )
                return True
            else:
                self.log_result("Backend Health", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Backend Health", False, "", str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests for the review request"""
        print("🎯 TOPKIT REVIEW REQUEST BACKEND TESTING")
        print("=" * 50)
        print(f"Testing backend functionality after UI modifications")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER['email']}")
        print()
        
        # Test basic authentication
        print("1. Testing Basic Authentication...")
        auth_success = self.test_user_authentication()
        
        # Test admin authentication
        print("\n2. Testing Admin Authentication...")
        admin_success = self.test_admin_authentication()
        
        # Test basic API endpoints
        print("\n3. Testing Basic API Endpoints...")
        jerseys_success = self.test_jerseys_endpoint()
        marketplace_success = self.test_marketplace_endpoint()
        explorer_success = self.test_explorer_endpoints()
        
        # Test authenticated endpoints
        print("\n4. Testing Authenticated Endpoints...")
        auth_endpoints_success = self.test_authenticated_endpoints()
        
        # Test site configuration
        print("\n5. Testing Site Configuration...")
        site_config_success = self.test_site_configuration()
        
        # Test backend health
        print("\n6. Testing Backend Health...")
        health_success = self.test_backend_health()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("🎉 TESTING COMPLETE")
        print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Summary of critical areas
        critical_tests = {
            "Authentication": auth_success,
            "Basic API Endpoints": jerseys_success and marketplace_success,
            "Backend Health": health_success
        }
        
        print("\nCritical Areas Status:")
        for area, status in critical_tests.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {area}")
        
        # Detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            print(f"  {status_icon} {result['test']}")
            if result['details']:
                print(f"      {result['details']}")
            if result['error']:
                print(f"      Error: {result['error']}")
        
        return success_rate >= 80  # Consider 80%+ as successful

if __name__ == "__main__":
    tester = ReviewRequestTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 BACKEND TESTING SUCCESSFUL - System is working properly after UI modifications")
    else:
        print("\n🚨 BACKEND TESTING IDENTIFIED ISSUES - Some functionality may be affected")