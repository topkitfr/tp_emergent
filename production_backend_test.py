#!/usr/bin/env python3
"""
Production Backend Connectivity Test for TopKit
Testing production environment at https://topkit-beta.emergent.host/

This test verifies:
1. Basic API connectivity to https://topkit-beta.emergent.host/api/
2. Health check endpoints if available
3. Database connectivity by testing GET endpoints like /api/jerseys
4. Site configuration endpoints like /api/site/mode
5. Authentication endpoints availability (POST /api/auth/login)
"""

import requests
import json
import sys
from datetime import datetime

# Production backend URL
PRODUCTION_BASE_URL = "https://topkit-beta.emergent.host"
API_BASE_URL = f"{PRODUCTION_BASE_URL}/api"

# Test credentials (if available)
TEST_CREDENTIALS = {
    "admin": {
        "email": "topkitfr@gmail.com",
        "password": "TopKitSecure789#"
    },
    "user": {
        "email": "steinmetzlivio@gmail.com", 
        "password": "TopKit123!"
    }
}

class ProductionBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, success, details, response_code=None):
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
            "details": details,
            "response_code": response_code,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status} - {test_name}: {details}")
        
    def test_basic_connectivity(self):
        """Test 1: Basic API connectivity"""
        print("\n🔗 Testing Basic API Connectivity...")
        
        try:
            # Test root API endpoint
            response = self.session.get(f"{API_BASE_URL}/", timeout=10)
            
            if response.status_code == 200:
                self.log_result(
                    "Basic API Connectivity", 
                    True, 
                    f"API root accessible (HTTP {response.status_code})",
                    response.status_code
                )
            elif response.status_code == 404:
                # Try without trailing slash
                response = self.session.get(API_BASE_URL, timeout=10)
                if response.status_code in [200, 404, 405]:
                    self.log_result(
                        "Basic API Connectivity", 
                        True, 
                        f"API base accessible (HTTP {response.status_code})",
                        response.status_code
                    )
                else:
                    self.log_result(
                        "Basic API Connectivity", 
                        False, 
                        f"API not accessible (HTTP {response.status_code})",
                        response.status_code
                    )
            else:
                self.log_result(
                    "Basic API Connectivity", 
                    True, 
                    f"API responding (HTTP {response.status_code})",
                    response.status_code
                )
                
        except requests.exceptions.ConnectionError as e:
            self.log_result(
                "Basic API Connectivity", 
                False, 
                f"Connection failed: {str(e)}"
            )
        except requests.exceptions.Timeout as e:
            self.log_result(
                "Basic API Connectivity", 
                False, 
                f"Request timeout: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "Basic API Connectivity", 
                False, 
                f"Unexpected error: {str(e)}"
            )
    
    def test_health_endpoints(self):
        """Test 2: Health check endpoints"""
        print("\n🏥 Testing Health Check Endpoints...")
        
        health_endpoints = [
            "/health",
            "/api/health", 
            "/api/status",
            "/ping",
            "/api/ping"
        ]
        
        health_found = False
        
        for endpoint in health_endpoints:
            try:
                url = f"{PRODUCTION_BASE_URL}{endpoint}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log_result(
                            f"Health Check ({endpoint})", 
                            True, 
                            f"Health endpoint found - Status: {data.get('status', 'OK')}",
                            response.status_code
                        )
                        health_found = True
                        break
                    except:
                        self.log_result(
                            f"Health Check ({endpoint})", 
                            True, 
                            f"Health endpoint found - Response: {response.text[:100]}",
                            response.status_code
                        )
                        health_found = True
                        break
                        
            except Exception as e:
                continue
                
        if not health_found:
            self.log_result(
                "Health Check Endpoints", 
                False, 
                "No health check endpoints found"
            )
    
    def test_database_connectivity(self):
        """Test 3: Database connectivity via GET endpoints"""
        print("\n🗄️ Testing Database Connectivity...")
        
        database_endpoints = [
            ("/api/jerseys", "Jerseys endpoint"),
            ("/api/marketplace/catalog", "Marketplace catalog"),
            ("/api/explorer/leagues", "Explorer leagues"),
            ("/api/stats/dynamic", "Dynamic statistics")
        ]
        
        for endpoint, description in database_endpoints:
            try:
                url = f"{PRODUCTION_BASE_URL}{endpoint}"
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            count = len(data)
                            self.log_result(
                                f"Database - {description}", 
                                True, 
                                f"Endpoint accessible - {count} items returned",
                                response.status_code
                            )
                        elif isinstance(data, dict):
                            keys = list(data.keys())[:3]
                            self.log_result(
                                f"Database - {description}", 
                                True, 
                                f"Endpoint accessible - Data keys: {keys}",
                                response.status_code
                            )
                        else:
                            self.log_result(
                                f"Database - {description}", 
                                True, 
                                f"Endpoint accessible - Response type: {type(data)}",
                                response.status_code
                            )
                    except json.JSONDecodeError:
                        self.log_result(
                            f"Database - {description}", 
                            True, 
                            f"Endpoint accessible - Non-JSON response",
                            response.status_code
                        )
                elif response.status_code == 404:
                    self.log_result(
                        f"Database - {description}", 
                        False, 
                        f"Endpoint not found (HTTP 404)",
                        response.status_code
                    )
                elif response.status_code == 500:
                    self.log_result(
                        f"Database - {description}", 
                        False, 
                        f"Server error - possible database issue (HTTP 500)",
                        response.status_code
                    )
                else:
                    self.log_result(
                        f"Database - {description}", 
                        False, 
                        f"Unexpected response (HTTP {response.status_code})",
                        response.status_code
                    )
                    
            except requests.exceptions.ConnectionError as e:
                self.log_result(
                    f"Database - {description}", 
                    False, 
                    f"Connection failed: {str(e)}"
                )
            except requests.exceptions.Timeout as e:
                self.log_result(
                    f"Database - {description}", 
                    False, 
                    f"Request timeout: {str(e)}"
                )
            except Exception as e:
                self.log_result(
                    f"Database - {description}", 
                    False, 
                    f"Error: {str(e)}"
                )
    
    def test_site_configuration(self):
        """Test 4: Site configuration endpoints"""
        print("\n⚙️ Testing Site Configuration...")
        
        try:
            url = f"{API_BASE_URL}/site/mode"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    mode = data.get('mode', 'unknown')
                    self.log_result(
                        "Site Configuration", 
                        True, 
                        f"Site mode endpoint accessible - Mode: {mode}",
                        response.status_code
                    )
                except json.JSONDecodeError:
                    self.log_result(
                        "Site Configuration", 
                        True, 
                        f"Site mode endpoint accessible - Non-JSON response",
                        response.status_code
                    )
            elif response.status_code == 401:
                self.log_result(
                    "Site Configuration", 
                    True, 
                    f"Site mode endpoint exists but requires authentication",
                    response.status_code
                )
            elif response.status_code == 404:
                self.log_result(
                    "Site Configuration", 
                    False, 
                    f"Site mode endpoint not found",
                    response.status_code
                )
            else:
                self.log_result(
                    "Site Configuration", 
                    False, 
                    f"Unexpected response (HTTP {response.status_code})",
                    response.status_code
                )
                
        except Exception as e:
            self.log_result(
                "Site Configuration", 
                False, 
                f"Error accessing site configuration: {str(e)}"
            )
    
    def test_authentication_endpoints(self):
        """Test 5: Authentication endpoints availability"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test login endpoint availability
        try:
            url = f"{API_BASE_URL}/auth/login"
            
            # Test with invalid credentials to check if endpoint exists
            test_payload = {
                "email": "test@example.com",
                "password": "invalid"
            }
            
            response = self.session.post(
                url, 
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [401, 400, 422]:
                self.log_result(
                    "Authentication Endpoint Availability", 
                    True, 
                    f"Login endpoint accessible (HTTP {response.status_code})",
                    response.status_code
                )
                
                # Try with known credentials if available
                self.test_authentication_with_credentials()
                
            elif response.status_code == 404:
                self.log_result(
                    "Authentication Endpoint Availability", 
                    False, 
                    f"Login endpoint not found (HTTP 404)",
                    response.status_code
                )
            elif response.status_code == 500:
                self.log_result(
                    "Authentication Endpoint Availability", 
                    False, 
                    f"Server error on login endpoint (HTTP 500)",
                    response.status_code
                )
            else:
                self.log_result(
                    "Authentication Endpoint Availability", 
                    True, 
                    f"Login endpoint responding (HTTP {response.status_code})",
                    response.status_code
                )
                
        except Exception as e:
            self.log_result(
                "Authentication Endpoint Availability", 
                False, 
                f"Error testing login endpoint: {str(e)}"
            )
    
    def test_authentication_with_credentials(self):
        """Test authentication with known credentials"""
        print("\n🔑 Testing Authentication with Known Credentials...")
        
        for role, creds in TEST_CREDENTIALS.items():
            try:
                url = f"{API_BASE_URL}/auth/login"
                response = self.session.post(
                    url,
                    json=creds,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'token' in data:
                            user_info = data.get('user', {})
                            user_name = user_info.get('name', 'Unknown')
                            user_role = user_info.get('role', 'Unknown')
                            self.log_result(
                                f"Authentication - {role.title()}", 
                                True, 
                                f"Login successful - User: {user_name}, Role: {user_role}",
                                response.status_code
                            )
                        else:
                            self.log_result(
                                f"Authentication - {role.title()}", 
                                False, 
                                f"Login response missing token",
                                response.status_code
                            )
                    except json.JSONDecodeError:
                        self.log_result(
                            f"Authentication - {role.title()}", 
                            False, 
                            f"Invalid JSON response",
                            response.status_code
                        )
                elif response.status_code == 401:
                    self.log_result(
                        f"Authentication - {role.title()}", 
                        False, 
                        f"Invalid credentials (HTTP 401)",
                        response.status_code
                    )
                elif response.status_code == 403:
                    self.log_result(
                        f"Authentication - {role.title()}", 
                        False, 
                        f"Account banned or restricted (HTTP 403)",
                        response.status_code
                    )
                else:
                    self.log_result(
                        f"Authentication - {role.title()}", 
                        False, 
                        f"Unexpected response (HTTP {response.status_code})",
                        response.status_code
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Authentication - {role.title()}", 
                    False, 
                    f"Error: {str(e)}"
                )
    
    def run_all_tests(self):
        """Run all production backend tests"""
        print("🚀 Starting Production Backend Connectivity Tests")
        print(f"Target: {PRODUCTION_BASE_URL}")
        print("=" * 60)
        
        # Run all tests
        self.test_basic_connectivity()
        self.test_health_endpoints()
        self.test_database_connectivity()
        self.test_site_configuration()
        self.test_authentication_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']} {result['test']}: {result['details']}")
            
        # Determine overall status
        if success_rate >= 80:
            print(f"\n🎉 PRODUCTION BACKEND STATUS: OPERATIONAL ({success_rate:.1f}% success rate)")
            return True
        elif success_rate >= 60:
            print(f"\n⚠️ PRODUCTION BACKEND STATUS: PARTIALLY OPERATIONAL ({success_rate:.1f}% success rate)")
            return False
        else:
            print(f"\n🚨 PRODUCTION BACKEND STATUS: CRITICAL ISSUES ({success_rate:.1f}% success rate)")
            return False

if __name__ == "__main__":
    tester = ProductionBackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)