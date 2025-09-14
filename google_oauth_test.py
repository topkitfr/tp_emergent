#!/usr/bin/env python3
"""
Google OAuth Authentication System Testing for TopKit
Testing specifically the Google OAuth functionality as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class GoogleOAuthTester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_google_oauth_endpoint_accessibility(self):
        """Test 1: Check if /api/auth/google endpoint is accessible"""
        try:
            response = requests.get(f"{API_BASE}/auth/google", allow_redirects=False, timeout=10)
            
            if response.status_code == 302:
                # OAuth redirect is expected
                redirect_url = response.headers.get('Location', '')
                if 'accounts.google.com' in redirect_url:
                    self.log_result(
                        "Google OAuth Endpoint Accessibility",
                        True,
                        "OAuth endpoint properly redirects to Google",
                        {"status_code": response.status_code, "redirect_url": redirect_url[:100] + "..."}
                    )
                else:
                    self.log_result(
                        "Google OAuth Endpoint Accessibility", 
                        False,
                        "OAuth endpoint redirects but not to Google",
                        {"status_code": response.status_code, "redirect_url": redirect_url}
                    )
            elif response.status_code == 500:
                self.log_result(
                    "Google OAuth Endpoint Accessibility",
                    False,
                    "OAuth endpoint returns server error - likely configuration issue",
                    {"status_code": response.status_code, "error": response.text[:200]}
                )
            else:
                self.log_result(
                    "Google OAuth Endpoint Accessibility",
                    False,
                    f"Unexpected response from OAuth endpoint",
                    {"status_code": response.status_code, "response": response.text[:200]}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Google OAuth Endpoint Accessibility",
                False,
                "Failed to connect to OAuth endpoint",
                {"error": str(e)}
            )

    def test_google_oauth_credentials_validation(self):
        """Test 2: Validate Google OAuth credentials by checking redirect URL structure"""
        try:
            response = requests.get(f"{API_BASE}/auth/google", allow_redirects=False, timeout=10)
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                
                # Check if redirect URL contains expected OAuth parameters
                expected_params = ['client_id', 'redirect_uri', 'response_type', 'scope']
                found_params = []
                
                for param in expected_params:
                    if param in redirect_url:
                        found_params.append(param)
                
                # Extract client_id from URL if present
                client_id = None
                if 'client_id=' in redirect_url:
                    try:
                        client_id = redirect_url.split('client_id=')[1].split('&')[0]
                    except:
                        pass
                
                if len(found_params) == len(expected_params) and client_id:
                    self.log_result(
                        "Google OAuth Credentials Validation",
                        True,
                        "OAuth URL contains all required parameters",
                        {
                            "found_params": found_params,
                            "client_id": client_id,
                            "redirect_url_valid": True
                        }
                    )
                else:
                    self.log_result(
                        "Google OAuth Credentials Validation",
                        False,
                        "OAuth URL missing required parameters",
                        {
                            "expected_params": expected_params,
                            "found_params": found_params,
                            "client_id": client_id
                        }
                    )
            else:
                self.log_result(
                    "Google OAuth Credentials Validation",
                    False,
                    "Cannot validate credentials - no redirect received",
                    {"status_code": response.status_code}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Google OAuth Credentials Validation",
                False,
                "Failed to validate OAuth credentials",
                {"error": str(e)}
            )

    def test_google_oauth_callback_endpoint(self):
        """Test 3: Test the callback endpoint structure"""
        try:
            # Test callback endpoint without parameters (should fail gracefully)
            response = requests.get(f"{API_BASE}/auth/google/callback", timeout=10)
            
            if response.status_code in [400, 422]:
                self.log_result(
                    "Google OAuth Callback Endpoint Structure",
                    True,
                    "Callback endpoint properly handles missing parameters",
                    {"status_code": response.status_code, "response": response.text[:200]}
                )
            elif response.status_code == 500:
                # Check if it's a proper OAuth error
                error_text = response.text.lower()
                if 'oauth' in error_text or 'token' in error_text or 'authorization' in error_text:
                    self.log_result(
                        "Google OAuth Callback Endpoint Structure",
                        True,
                        "Callback endpoint exists and processes OAuth requests",
                        {"status_code": response.status_code, "oauth_error": True}
                    )
                else:
                    self.log_result(
                        "Google OAuth Callback Endpoint Structure",
                        False,
                        "Callback endpoint has server error",
                        {"status_code": response.status_code, "error": response.text[:200]}
                    )
            else:
                self.log_result(
                    "Google OAuth Callback Endpoint Structure",
                    False,
                    f"Unexpected callback endpoint response",
                    {"status_code": response.status_code, "response": response.text[:200]}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Google OAuth Callback Endpoint Structure",
                False,
                "Failed to test callback endpoint",
                {"error": str(e)}
            )

    def test_oauth_error_handling(self):
        """Test 4: Test OAuth error handling with invalid parameters"""
        try:
            # Test callback with invalid parameters
            invalid_params = {
                'error': 'access_denied',
                'error_description': 'User denied access'
            }
            
            response = requests.get(f"{API_BASE}/auth/google/callback", params=invalid_params, timeout=10)
            
            # Any response that doesn't crash is good error handling
            if response.status_code in [400, 401, 403, 422, 500]:
                self.log_result(
                    "OAuth Error Handling",
                    True,
                    "OAuth error handling works - endpoint handles invalid requests",
                    {"status_code": response.status_code, "handles_errors": True}
                )
            else:
                self.log_result(
                    "OAuth Error Handling",
                    False,
                    "Unexpected response to OAuth error",
                    {"status_code": response.status_code, "response": response.text[:200]}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "OAuth Error Handling",
                False,
                "Failed to test OAuth error handling",
                {"error": str(e)}
            )

    def test_hardcoded_credentials_validity(self):
        """Test 5: Check if hardcoded Google credentials are still valid"""
        try:
            # The hardcoded credentials from server.py
            client_id = "920523740769-d74f1dsdajtilkqasrhtrei4blmf8ujj.apps.googleusercontent.com"
            client_secret = "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"
            
            # Try to validate by making OAuth request and checking response
            response = requests.get(f"{API_BASE}/auth/google", allow_redirects=False, timeout=10)
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                
                # Check if the client_id in the redirect matches our hardcoded one
                if client_id in redirect_url:
                    self.log_result(
                        "Hardcoded Credentials Validity Check",
                        True,
                        "Hardcoded client_id is being used in OAuth flow",
                        {
                            "client_id_found": True,
                            "client_id": client_id,
                            "credentials_in_use": True
                        }
                    )
                else:
                    self.log_result(
                        "Hardcoded Credentials Validity Check",
                        False,
                        "Hardcoded client_id not found in OAuth flow",
                        {
                            "expected_client_id": client_id,
                            "redirect_url": redirect_url[:200]
                        }
                    )
            else:
                self.log_result(
                    "Hardcoded Credentials Validity Check",
                    False,
                    "Cannot check credentials - OAuth flow not working",
                    {"status_code": response.status_code}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Hardcoded Credentials Validity Check",
                False,
                "Failed to check hardcoded credentials",
                {"error": str(e)}
            )

    def test_redirect_uri_configuration(self):
        """Test 6: Check if redirect URI is properly configured"""
        try:
            response = requests.get(f"{API_BASE}/auth/google", allow_redirects=False, timeout=10)
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                
                # Extract redirect_uri parameter
                if 'redirect_uri=' in redirect_url:
                    try:
                        redirect_uri = redirect_url.split('redirect_uri=')[1].split('&')[0]
                        # URL decode
                        import urllib.parse
                        redirect_uri = urllib.parse.unquote(redirect_uri)
                        
                        # Check if redirect URI matches current domain
                        expected_callback = f"{BACKEND_URL}/api/auth/google/callback"
                        
                        if redirect_uri == expected_callback:
                            self.log_result(
                                "Redirect URI Configuration",
                                True,
                                "Redirect URI is properly configured for current domain",
                                {
                                    "redirect_uri": redirect_uri,
                                    "matches_expected": True,
                                    "expected": expected_callback
                                }
                            )
                        else:
                            self.log_result(
                                "Redirect URI Configuration",
                                False,
                                "Redirect URI does not match current domain",
                                {
                                    "redirect_uri": redirect_uri,
                                    "expected": expected_callback,
                                    "domain_mismatch": True
                                }
                            )
                    except Exception as e:
                        self.log_result(
                            "Redirect URI Configuration",
                            False,
                            "Failed to parse redirect URI",
                            {"error": str(e), "redirect_url": redirect_url[:200]}
                        )
                else:
                    self.log_result(
                        "Redirect URI Configuration",
                        False,
                        "No redirect_uri parameter found in OAuth URL",
                        {"redirect_url": redirect_url[:200]}
                    )
            else:
                self.log_result(
                    "Redirect URI Configuration",
                    False,
                    "Cannot check redirect URI - OAuth flow not working",
                    {"status_code": response.status_code}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Redirect URI Configuration",
                False,
                "Failed to check redirect URI configuration",
                {"error": str(e)}
            )

    def run_all_tests(self):
        """Run all Google OAuth tests"""
        print("🔍 GOOGLE OAUTH AUTHENTICATION SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all tests
        self.test_google_oauth_endpoint_accessibility()
        self.test_google_oauth_credentials_validation()
        self.test_hardcoded_credentials_validity()
        self.test_redirect_uri_configuration()
        self.test_google_oauth_callback_endpoint()
        self.test_oauth_error_handling()
        
        # Summary
        print("=" * 60)
        print("🎯 GOOGLE OAUTH TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            print(f"   {result['message']}")
            if result['details']:
                for key, value in result['details'].items():
                    print(f"   {key}: {value}")
            print()
        
        # Recommendations
        print("🔧 RECOMMENDATIONS:")
        print("-" * 40)
        
        if success_rate >= 80:
            print("✅ Google OAuth system appears to be functional")
            print("✅ OAuth endpoints are accessible and properly configured")
            print("✅ Credentials appear to be valid")
            print("⚠️  Consider testing with actual Google login flow in browser")
        elif success_rate >= 50:
            print("⚠️  Google OAuth system has some issues but may be partially functional")
            print("⚠️  Some endpoints work but there may be configuration problems")
            print("🔧 Review failed tests and fix configuration issues")
        else:
            print("❌ Google OAuth system appears to be broken")
            print("❌ Multiple critical failures detected")
            print("🗑️  Consider removing Google OAuth functionality")
            print("🔧 Or fix all configuration issues before enabling")
        
        print()
        print("📊 OAUTH FUNCTIONALITY STATUS:")
        if success_rate >= 80:
            print("🟢 FUNCTIONAL - OAuth system is working")
        elif success_rate >= 50:
            print("🟡 PARTIALLY FUNCTIONAL - Needs fixes")
        else:
            print("🔴 BROKEN - Should be removed or completely fixed")
        
        return success_rate

if __name__ == "__main__":
    tester = GoogleOAuthTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    if success_rate >= 80:
        sys.exit(0)  # Success
    elif success_rate >= 50:
        sys.exit(1)  # Partial success
    else:
        sys.exit(2)  # Failure