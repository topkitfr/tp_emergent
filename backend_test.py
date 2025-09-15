#!/usr/bin/env python3
"""
Backend Testing Suite for TopKit Application
Tests the application after database fresh start cleanup
"""

import requests
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials for preserved admin user
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if details and not success:
            print(f"    Details: {details}")
        print()
        
    def test_database_connection(self):
        """Test basic database connectivity"""
        try:
            response = self.session.get(f"{API_BASE}/teams", timeout=10)
            if response.status_code == 200:
                self.log_test("Database Connection", True, "Backend can connect to database and return responses")
                return True
            else:
                self.log_test("Database Connection", False, f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Connection", False, f"Connection failed: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test authentication with preserved admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    user_info = data["user"]
                    self.log_test("Authentication", True, 
                                f"Successfully authenticated admin user: {user_info.get('email', 'Unknown')}")
                    return True
                else:
                    self.log_test("Authentication", False, "Login response missing token or user data", data)
                    return False
            else:
                self.log_test("Authentication", False, 
                            f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_empty_endpoints(self):
        """Test that API endpoints return empty arrays instead of errors for empty database"""
        endpoints_to_test = [
            ("teams", "Teams endpoint"),
            ("brands", "Brands endpoint"), 
            ("players", "Players endpoint"),
            ("competitions", "Competitions endpoint"),
            ("master-kits", "Master Kits endpoint"),
            ("master-jerseys", "Master Jerseys endpoint (backward compatibility)")
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}/{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"Empty Database - {description}", True, 
                                    f"Returns empty array with {len(data)} items (expected for clean database)")
                    else:
                        self.log_test(f"Empty Database - {description}", False, 
                                    f"Expected array, got {type(data)}", data)
                        all_passed = False
                else:
                    self.log_test(f"Empty Database - {description}", False, 
                                f"HTTP {response.status_code} instead of 200", response.text)
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Empty Database - {description}", False, f"Request failed: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_form_data_endpoints(self):
        """Test form data endpoints for dropdowns"""
        form_endpoints = [
            ("form-data/clubs", "Clubs form data"),
            ("form-data/competitions", "Competitions form data"),
            ("form-data/brands", "Brands form data")
        ]
        
        all_passed = True
        
        for endpoint, description in form_endpoints:
            try:
                response = self.session.get(f"{API_BASE}/{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"Form Data - {description}", True, 
                                    f"Returns array with {len(data)} items")
                    else:
                        self.log_test(f"Form Data - {description}", False, 
                                    f"Expected array, got {type(data)}", data)
                        all_passed = False
                else:
                    self.log_test(f"Form Data - {description}", False, 
                                f"HTTP {response.status_code}", response.text)
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Form Data - {description}", False, f"Request failed: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_authenticated_endpoints(self):
        """Test endpoints that require authentication"""
        if not self.auth_token:
            self.log_test("Authenticated Endpoints", False, "No auth token available")
            return False
            
        auth_endpoints = [
            ("my-collection", "My Collection endpoint"),
            ("contributions-v2/", "Contributions endpoint")
        ]
        
        all_passed = True
        
        for endpoint, description in auth_endpoints:
            try:
                response = self.session.get(f"{API_BASE}/{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"Authenticated - {description}", True, 
                                    f"Returns array with {len(data)} items")
                    else:
                        self.log_test(f"Authenticated - {description}", False, 
                                    f"Expected array, got {type(data)}", data)
                        all_passed = False
                elif response.status_code == 401:
                    self.log_test(f"Authenticated - {description}", False, 
                                "Authentication failed - token may be invalid", response.text)
                    all_passed = False
                else:
                    self.log_test(f"Authenticated - {description}", False, 
                                f"HTTP {response.status_code}", response.text)
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Authenticated - {description}", False, f"Request failed: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_error_handling(self):
        """Test that the backend handles invalid requests gracefully"""
        error_tests = [
            (f"{API_BASE}/master-kits/nonexistent-id", "Non-existent master kit", 404),
            (f"{API_BASE}/teams/invalid-id", "Non-existent team", 404),
        ]
        
        all_passed = True
        
        for url, description, expected_status in error_tests:
            try:
                response = self.session.get(url, timeout=10)
                
                if response.status_code == expected_status:
                    self.log_test(f"Error Handling - {description}", True, 
                                f"Correctly returns {expected_status}")
                else:
                    self.log_test(f"Error Handling - {description}", False, 
                                f"Expected {expected_status}, got {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Error Handling - {description}", False, f"Request failed: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("TOPKIT BACKEND TESTING SUITE")
        print("Testing application after database fresh start cleanup")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print(f"Test Admin: {ADMIN_EMAIL}")
        print("=" * 80)
        print()
        
        # Test sequence
        tests = [
            ("Database Connection", self.test_database_connection),
            ("Authentication", self.test_authentication),
            ("Empty Database Endpoints", self.test_empty_endpoints),
            ("Form Data Endpoints", self.test_form_data_endpoints),
            ("Authenticated Endpoints", self.test_authenticated_endpoints),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            print("-" * 40)
            try:
                result = test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test suite error: {str(e)}")
            print()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Detailed results
        critical_failures = []
        for result in self.test_results:
            if not result["success"]:
                if any(keyword in result["test"].lower() for keyword in ["authentication", "database", "connection"]):
                    critical_failures.append(result)
        
        if critical_failures:
            print("CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"❌ {failure['test']}: {failure['message']}")
            print()
        
        # Overall assessment
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Application is ready for deployment!")
        elif len(critical_failures) == 0:
            print("⚠️  Some tests failed but no critical issues found")
        else:
            print("🚨 CRITICAL ISSUES FOUND - Application needs attention before deployment")
        
        print("=" * 80)
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()