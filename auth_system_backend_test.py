#!/usr/bin/env python3
"""
TopKit Authentication System Backend Testing
Focus: Debug login issues and test authentication endpoints comprehensively
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"
TEST_USER_EMAIL = "topkitfr@gmail.com"
TEST_USER_PASSWORD = "adminpass123"
NEW_USER_EMAIL = f"testuser_{int(time.time())}@example.com"
NEW_USER_PASSWORD = "SecureAuth789#"
NEW_USER_NAME = "Test User"

class AuthenticationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.jwt_token = None
        self.user_data = None
        
    def log_result(self, test_name, success, details, response_data=None):
        """Log test result with details"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"   Details: {details}")
        if response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
        print()
        
    def test_login_endpoint(self):
        """Test POST /api/auth/login with valid credentials"""
        print("🔐 Testing Login Endpoint...")
        
        try:
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.jwt_token = data["token"]
                    self.user_data = data["user"]
                    self.log_result(
                        "Login with Valid Credentials",
                        True,
                        f"Successfully logged in as {data['user'].get('name', 'Unknown')} (Role: {data['user'].get('role', 'Unknown')})",
                        data
                    )
                    return True
                else:
                    self.log_result(
                        "Login with Valid Credentials",
                        False,
                        "Login response missing token or user data",
                        data
                    )
            else:
                self.log_result(
                    "Login with Valid Credentials",
                    False,
                    f"Login failed with status {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Login with Valid Credentials",
                False,
                f"Login request failed with exception: {str(e)}"
            )
            
        return False
    
    def test_regular_user_login(self):
        """Test login with regular user credentials"""
        print("👤 Testing Regular User Login...")
        
        try:
            payload = {
                "email": "steinmetzlivio@gmail.com",
                "password": "123"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.log_result(
                        "Regular User Login",
                        True,
                        f"Successfully logged in as {data['user'].get('name', 'Unknown')} (Role: {data['user'].get('role', 'Unknown')})",
                        data
                    )
                    return True
                else:
                    self.log_result(
                        "Regular User Login",
                        False,
                        "Login response missing token or user data",
                        data
                    )
            else:
                self.log_result(
                    "Regular User Login",
                    False,
                    f"Regular user login failed with status {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Regular User Login",
                False,
                f"Regular user login request failed with exception: {str(e)}"
            )
            
        return False
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        print("🚫 Testing Invalid Credentials...")
        
        test_cases = [
            {"email": TEST_USER_EMAIL, "password": "wrongpassword", "case": "Wrong Password"},
            {"email": "nonexistent@example.com", "password": TEST_USER_PASSWORD, "case": "Wrong Email"},
            {"email": "invalid-email", "password": TEST_USER_PASSWORD, "case": "Invalid Email Format"},
            {"email": "", "password": TEST_USER_PASSWORD, "case": "Empty Email"},
            {"email": TEST_USER_EMAIL, "password": "", "case": "Empty Password"}
        ]
        
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"email": test_case["email"], "password": test_case["password"]},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code in [400, 401, 422]:
                    self.log_result(
                        f"Invalid Login - {test_case['case']}",
                        True,
                        f"Correctly rejected with status {response.status_code}",
                        {"status_code": response.status_code, "response": response.text}
                    )
                else:
                    self.log_result(
                        f"Invalid Login - {test_case['case']}",
                        False,
                        f"Unexpected status code {response.status_code}, expected 400/401/422",
                        {"status_code": response.status_code, "response": response.text}
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Invalid Login - {test_case['case']}",
                    False,
                    f"Request failed with exception: {str(e)}"
                )
    
    def test_register_endpoint(self):
        """Test POST /api/auth/register with new user registration"""
        print("📝 Testing Registration Endpoint...")
        
        try:
            payload = {
                "email": NEW_USER_EMAIL,
                "password": NEW_USER_PASSWORD,
                "name": NEW_USER_NAME
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "user" in data:
                    self.log_result(
                        "User Registration",
                        True,
                        f"Successfully registered user {data['user'].get('name', 'Unknown')} with email verification requirement",
                        data
                    )
                    return True
                else:
                    self.log_result(
                        "User Registration",
                        False,
                        "Registration response missing user data",
                        data
                    )
            else:
                self.log_result(
                    "User Registration",
                    False,
                    f"Registration failed with status {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "User Registration",
                False,
                f"Registration request failed with exception: {str(e)}"
            )
            
        return False
    
    def test_profile_endpoint(self):
        """Test GET /api/profile endpoint with Bearer token authentication"""
        print("👤 Testing Profile Endpoint...")
        
        if not self.jwt_token:
            self.log_result(
                "Profile Access with Token",
                False,
                "No JWT token available for testing (login may have failed)"
            )
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{BACKEND_URL}/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Profile Access with Token",
                    True,
                    f"Successfully retrieved profile for user {data.get('name', 'Unknown')}",
                    data
                )
                return True
            else:
                self.log_result(
                    "Profile Access with Token",
                    False,
                    f"Profile access failed with status {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Profile Access with Token",
                False,
                f"Profile request failed with exception: {str(e)}"
            )
            
        return False
    
    def test_profile_without_token(self):
        """Test profile endpoint without authentication"""
        print("🚫 Testing Profile Without Token...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/profile",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                self.log_result(
                    "Profile Access Without Token",
                    True,
                    f"Correctly rejected unauthorized access with status {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
            else:
                self.log_result(
                    "Profile Access Without Token",
                    False,
                    f"Unexpected status code {response.status_code}, expected 401/403",
                    {"status_code": response.status_code, "response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Profile Access Without Token",
                False,
                f"Request failed with exception: {str(e)}"
            )
    
    def test_jwt_token_structure(self):
        """Validate JWT token structure and basic properties"""
        print("🔍 Testing JWT Token Structure...")
        
        if not self.jwt_token:
            self.log_result(
                "JWT Token Structure Validation",
                False,
                "No JWT token available for validation"
            )
            return False
            
        try:
            # Basic JWT structure check (should have 3 parts separated by dots)
            token_parts = self.jwt_token.split('.')
            
            if len(token_parts) == 3:
                self.log_result(
                    "JWT Token Structure Validation",
                    True,
                    f"JWT token has correct structure with 3 parts (header.payload.signature)",
                    {"token_length": len(self.jwt_token), "parts_count": len(token_parts)}
                )
                return True
            else:
                self.log_result(
                    "JWT Token Structure Validation",
                    False,
                    f"JWT token has incorrect structure with {len(token_parts)} parts, expected 3",
                    {"token": self.jwt_token[:50] + "...", "parts_count": len(token_parts)}
                )
                
        except Exception as e:
            self.log_result(
                "JWT Token Structure Validation",
                False,
                f"Token validation failed with exception: {str(e)}"
            )
            
        return False
    
    def test_password_strength_validation(self):
        """Test password strength validation during registration"""
        print("🔒 Testing Password Strength Validation...")
        
        weak_passwords = [
            {"password": "123", "case": "Too Short"},
            {"password": "password", "case": "No Uppercase/Numbers/Special"},
            {"password": "PASSWORD", "case": "No Lowercase/Numbers/Special"},
            {"password": "Password", "case": "No Numbers/Special"},
            {"password": "Password123", "case": "No Special Characters"},
            {"password": "admin123", "case": "Contains Common Pattern"}
        ]
        
        for test_case in weak_passwords:
            try:
                payload = {
                    "email": f"weakpass_{int(time.time())}@example.com",
                    "password": test_case["password"],
                    "name": "Test User"
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/auth/register",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 400:
                    self.log_result(
                        f"Password Strength - {test_case['case']}",
                        True,
                        f"Correctly rejected weak password with status 400",
                        {"password_case": test_case['case'], "response": response.text}
                    )
                else:
                    self.log_result(
                        f"Password Strength - {test_case['case']}",
                        False,
                        f"Weak password not rejected, status: {response.status_code}",
                        {"password_case": test_case['case'], "status_code": response.status_code}
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Password Strength - {test_case['case']}",
                    False,
                    f"Request failed with exception: {str(e)}"
                )
    
    def test_rate_limiting(self):
        """Test rate limiting for authentication attempts"""
        print("⏱️ Testing Rate Limiting...")
        
        # Test multiple rapid registration attempts
        rapid_attempts = 0
        blocked_attempts = 0
        
        for i in range(5):
            try:
                payload = {
                    "email": f"ratelimit_{i}_{int(time.time())}@example.com",
                    "password": "RateLimit123!",
                    "name": f"Rate Test {i}"
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/auth/register",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                rapid_attempts += 1
                
                if response.status_code == 429:
                    blocked_attempts += 1
                    
            except Exception as e:
                pass
                
        if blocked_attempts > 0:
            self.log_result(
                "Rate Limiting for Registration",
                True,
                f"Rate limiting active: {blocked_attempts}/{rapid_attempts} attempts blocked",
                {"blocked_attempts": blocked_attempts, "total_attempts": rapid_attempts}
            )
        else:
            self.log_result(
                "Rate Limiting for Registration",
                False,
                f"No rate limiting detected: 0/{rapid_attempts} attempts blocked",
                {"blocked_attempts": blocked_attempts, "total_attempts": rapid_attempts}
            )
    
    def test_database_integration(self):
        """Test database integration by verifying user data persistence"""
        print("🗄️ Testing Database Integration...")
        
        if not self.user_data:
            self.log_result(
                "Database Integration - User Data Persistence",
                False,
                "No user data available to verify database integration"
            )
            return False
            
        try:
            # Test that user data is properly structured and contains expected fields
            required_fields = ["id", "email", "name", "role"]
            missing_fields = [field for field in required_fields if field not in self.user_data]
            
            if not missing_fields:
                self.log_result(
                    "Database Integration - User Data Structure",
                    True,
                    f"User data contains all required fields: {required_fields}",
                    {"user_data": self.user_data}
                )
                
                # Test that user ID is UUID format
                user_id = self.user_data.get("id", "")
                if len(user_id) == 36 and user_id.count("-") == 4:
                    self.log_result(
                        "Database Integration - UUID Format",
                        True,
                        f"User ID follows UUID format: {user_id}",
                        {"user_id": user_id}
                    )
                else:
                    self.log_result(
                        "Database Integration - UUID Format",
                        False,
                        f"User ID does not follow UUID format: {user_id}",
                        {"user_id": user_id}
                    )
                    
                return True
            else:
                self.log_result(
                    "Database Integration - User Data Structure",
                    False,
                    f"User data missing required fields: {missing_fields}",
                    {"user_data": self.user_data, "missing_fields": missing_fields}
                )
                
        except Exception as e:
            self.log_result(
                "Database Integration - User Data Structure",
                False,
                f"Database integration test failed with exception: {str(e)}"
            )
            
        return False
    
    def run_comprehensive_tests(self):
        """Run all authentication system tests"""
        print("🚀 Starting Comprehensive TopKit Authentication System Testing")
        print("=" * 70)
        print()
        
        # Core Authentication Tests
        login_success = self.test_login_endpoint()
        self.test_regular_user_login()
        self.test_login_invalid_credentials()
        
        # Registration Tests
        self.test_register_endpoint()
        self.test_password_strength_validation()
        
        # Profile Access Tests
        if login_success:
            self.test_profile_endpoint()
            self.test_jwt_token_structure()
        self.test_profile_without_token()
        
        # Security Tests
        self.test_rate_limiting()
        
        # Database Integration Tests
        self.test_database_integration()
        
        # Generate Summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 70)
        print("🎯 AUTHENTICATION SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        categories = {
            "Authentication": [],
            "Registration": [],
            "Security": [],
            "Database": [],
            "Error Handling": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Login" in test_name or "Profile" in test_name or "JWT" in test_name:
                categories["Authentication"].append(result)
            elif "Registration" in test_name or "Password" in test_name:
                categories["Registration"].append(result)
            elif "Rate Limiting" in test_name:
                categories["Security"].append(result)
            elif "Database" in test_name:
                categories["Database"].append(result)
            elif "Invalid" in test_name or "Without Token" in test_name:
                categories["Error Handling"].append(result)
        
        for category, results in categories.items():
            if results:
                passed = len([r for r in results if r["success"]])
                total = len(results)
                print(f"{category}: {passed}/{total} passed")
        
        print()
        
        # Critical Issues
        critical_failures = [r for r in self.test_results if not r["success"] and 
                           ("Login with Valid Credentials" in r["test"] or 
                            "Profile Access with Token" in r["test"] or
                            "User Registration" in r["test"])]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   ✅ Authentication system is working excellently!")
        elif success_rate >= 75:
            print("   ⚠️ Authentication system is mostly functional with minor issues")
        else:
            print("   🚨 Authentication system has significant issues requiring immediate attention")
        
        if failed_tests > 0:
            print("   🔧 Review failed tests above for specific issues to address")
        
        print()
        print("🏁 Authentication System Testing Complete!")

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_comprehensive_tests()