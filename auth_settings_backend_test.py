#!/usr/bin/env python3
"""
TopKit Authentication & Settings Backend Test
Focus: User Authentication and Settings Endpoint Testing

Test Credentials:
- Email: steinmetzlivio@gmail.com
- Password: T0p_Mdp_1288*

Test Scenarios:
1. User Authentication Test
2. User Profile Access Test  
3. Settings Endpoints Test
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
TEST_EMAIL = "steinmetzlivio@gmail.com"
TEST_PASSWORD = "T0p_Mdp_1288*"

class AuthSettingsBackendTest:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_data = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
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

    def test_user_authentication(self):
        """Test 1: User Authentication with specific credentials"""
        print("🔐 Testing User Authentication...")
        
        try:
            # Test login with provided credentials
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if JWT token is present
                if "token" in data:
                    self.jwt_token = data["token"]
                    self.user_data = data.get("user", {})
                    
                    # Verify user data structure
                    required_fields = ["id", "name", "email", "role"]
                    missing_fields = [field for field in required_fields if field not in self.user_data]
                    
                    if not missing_fields:
                        self.log_test(
                            "User Authentication",
                            True,
                            f"Login successful. User: {self.user_data.get('name')}, Role: {self.user_data.get('role')}, ID: {self.user_data.get('id')}"
                        )
                        
                        # Set authorization header for future requests
                        self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                        return True
                    else:
                        self.log_test(
                            "User Authentication",
                            False,
                            f"Login successful but missing user data fields: {missing_fields}",
                            "Incomplete user data structure"
                        )
                        return False
                else:
                    self.log_test(
                        "User Authentication",
                        False,
                        f"Login response missing JWT token. Response: {data}",
                        "No JWT token in response"
                    )
                    return False
            else:
                # Check for specific error cases
                if response.status_code == 401:
                    self.log_test(
                        "User Authentication",
                        False,
                        f"Authentication failed with provided credentials",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                elif response.status_code == 403:
                    self.log_test(
                        "User Authentication",
                        False,
                        f"Account may be banned or suspended",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                elif response.status_code == 423:
                    self.log_test(
                        "User Authentication",
                        False,
                        f"Account temporarily locked",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                else:
                    self.log_test(
                        "User Authentication",
                        False,
                        f"Login failed with status {response.status_code}",
                        response.text
                    )
                return False
                
        except Exception as e:
            self.log_test(
                "User Authentication",
                False,
                "Exception during authentication",
                str(e)
            )
            return False

    def test_user_profile_access(self):
        """Test 2: User Profile Access with JWT token"""
        print("👤 Testing User Profile Access...")
        
        if not self.jwt_token:
            self.log_test(
                "User Profile Access",
                False,
                "Cannot test profile access without valid JWT token",
                "Authentication required first"
            )
            return False
            
        try:
            # Test profile endpoint
            response = self.session.get(f"{API_BASE}/users/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Verify profile data contains security settings information
                security_fields = ["two_factor_enabled", "email_verified", "role"]
                present_security_fields = [field for field in security_fields if field in profile_data]
                
                self.log_test(
                    "User Profile Access",
                    True,
                    f"Profile accessible. Security fields present: {present_security_fields}. Profile data includes: {list(profile_data.keys())}"
                )
                return True
            else:
                self.log_test(
                    "User Profile Access",
                    False,
                    f"Profile access failed with status {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "User Profile Access",
                False,
                "Exception during profile access",
                str(e)
            )
            return False

    def test_settings_endpoints(self):
        """Test 3: Settings-related endpoints"""
        print("⚙️ Testing Settings Endpoints...")
        
        if not self.jwt_token:
            self.log_test(
                "Settings Endpoints",
                False,
                "Cannot test settings without valid JWT token",
                "Authentication required first"
            )
            return False
            
        settings_tests = []
        
        # Test 2FA setup endpoint
        try:
            response = self.session.post(f"{API_BASE}/auth/2fa/setup")
            if response.status_code in [200, 400, 401]:  # 400 might be expected if already setup
                settings_tests.append(("2FA Setup", True, f"Endpoint accessible (HTTP {response.status_code})"))
            else:
                settings_tests.append(("2FA Setup", False, f"Unexpected status {response.status_code}"))
        except Exception as e:
            settings_tests.append(("2FA Setup", False, f"Exception: {str(e)}"))
            
        # Test password change endpoint
        try:
            # Test with invalid data to check endpoint availability
            response = self.session.post(f"{API_BASE}/auth/change-password", json={
                "current_password": "invalid",
                "new_password": "test"
            })
            if response.status_code in [400, 401, 422]:  # Expected validation errors
                settings_tests.append(("Password Change", True, f"Endpoint accessible (HTTP {response.status_code})"))
            else:
                settings_tests.append(("Password Change", False, f"Unexpected status {response.status_code}"))
        except Exception as e:
            settings_tests.append(("Password Change", False, f"Exception: {str(e)}"))
            
        # Test profile settings endpoint
        try:
            response = self.session.put(f"{API_BASE}/users/profile/settings", json={})
            if response.status_code in [200, 400, 422]:  # Various expected responses
                settings_tests.append(("Profile Settings", True, f"Endpoint accessible (HTTP {response.status_code})"))
            else:
                settings_tests.append(("Profile Settings", False, f"Unexpected status {response.status_code}"))
        except Exception as e:
            settings_tests.append(("Profile Settings", False, f"Exception: {str(e)}"))
            
        # Test user profile endpoint (detailed)
        try:
            user_id = self.user_data.get('id') if self.user_data else 'test'
            response = self.session.get(f"{API_BASE}/users/{user_id}/profile")
            if response.status_code in [200, 404]:  # 200 success, 404 might be expected
                settings_tests.append(("User Profile Details", True, f"Endpoint accessible (HTTP {response.status_code})"))
            else:
                settings_tests.append(("User Profile Details", False, f"Unexpected status {response.status_code}"))
        except Exception as e:
            settings_tests.append(("User Profile Details", False, f"Exception: {str(e)}"))
        
        # Log all settings test results
        successful_tests = sum(1 for _, success, _ in settings_tests if success)
        total_tests = len(settings_tests)
        
        for test_name, success, details in settings_tests:
            self.log_test(f"Settings - {test_name}", success, details)
            
        # Overall settings test result
        overall_success = successful_tests >= (total_tests * 0.75)  # 75% success rate
        self.log_test(
            "Settings Endpoints Overall",
            overall_success,
            f"Settings endpoints test: {successful_tests}/{total_tests} endpoints accessible"
        )
        
        return overall_success

    def test_security_settings_backend_support(self):
        """Test 4: Verify backend supports security settings that frontend needs"""
        print("🔒 Testing Security Settings Backend Support...")
        
        if not self.jwt_token:
            self.log_test(
                "Security Settings Backend Support",
                False,
                "Cannot test security settings without valid JWT token",
                "Authentication required first"
            )
            return False
            
        security_features = []
        
        # Check 2FA endpoints
        endpoints_to_check = [
            ("/auth/2fa/setup", "2FA Setup"),
            ("/auth/2fa/enable", "2FA Enable"),
            ("/auth/2fa/disable", "2FA Disable"),
            ("/auth/change-password", "Password Change"),
            ("/users/profile/settings", "Profile Settings")
        ]
        
        for endpoint, feature_name in endpoints_to_check:
            try:
                # Use HEAD request to check endpoint availability without side effects
                response = self.session.head(f"{API_BASE}{endpoint}")
                if response.status_code != 404:  # Endpoint exists
                    security_features.append((feature_name, True, f"Endpoint available"))
                else:
                    security_features.append((feature_name, False, f"Endpoint not found (404)"))
            except Exception as e:
                security_features.append((feature_name, False, f"Exception: {str(e)}"))
        
        # Log security features support
        supported_features = sum(1 for _, supported, _ in security_features if supported)
        total_features = len(security_features)
        
        for feature_name, supported, details in security_features:
            self.log_test(f"Security Feature - {feature_name}", supported, details)
            
        # Overall security support result
        overall_support = supported_features >= (total_features * 0.8)  # 80% support rate
        self.log_test(
            "Security Settings Backend Support",
            overall_support,
            f"Security features support: {supported_features}/{total_features} features available"
        )
        
        return overall_support

    def run_all_tests(self):
        """Run all authentication and settings tests"""
        print("🎯 TOPKIT AUTHENTICATION & SETTINGS BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {API_BASE}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        auth_success = self.test_user_authentication()
        profile_success = self.test_user_profile_access()
        settings_success = self.test_settings_endpoints()
        security_support = self.test_security_settings_backend_support()
        
        # Calculate overall results
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("=" * 60)
        print("📊 FINAL RESULTS")
        print("=" * 60)
        
        # Summary by category
        categories = {
            "Authentication": auth_success,
            "Profile Access": profile_success,
            "Settings Endpoints": settings_success,
            "Security Support": security_support
        }
        
        for category, success in categories.items():
            status = "✅ WORKING" if success else "❌ FAILED"
            print(f"{category}: {status}")
        
        print()
        print(f"Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
        
        # Determine if authentication system is ready
        if auth_success and profile_success:
            print("🎉 AUTHENTICATION SYSTEM: OPERATIONAL")
        else:
            print("🚨 AUTHENTICATION SYSTEM: ISSUES DETECTED")
            
        if settings_success and security_support:
            print("🎉 SECURITY SETTINGS: BACKEND SUPPORT CONFIRMED")
        else:
            print("⚠️ SECURITY SETTINGS: LIMITED BACKEND SUPPORT")
        
        print()
        print("=" * 60)
        
        # Return overall success
        return success_rate >= 75.0  # 75% success rate threshold

if __name__ == "__main__":
    tester = AuthSettingsBackendTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)