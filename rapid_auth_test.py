#!/usr/bin/env python3
"""
TopKit - Rapid Authentication Testing
Focus on diagnosing authentication issues causing frontend signup failures
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"

class RapidAuthTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_server_health(self):
        """PRIORITY 3: Test basic server connectivity"""
        try:
            # Test if server is responding
            response = self.session.get(f"{self.base_url.replace('/api', '')}")
            
            if response.status_code in [200, 404, 405]:  # Any response means server is up
                self.log_test("Server Health Check", "PASS", f"Server responding (Status: {response.status_code})")
                return True
            else:
                self.log_test("Server Health Check", "FAIL", f"Server not responding properly (Status: {response.status_code})")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test("Server Health Check", "FAIL", "Connection refused - server may be down")
            return False
        except Exception as e:
            self.log_test("Server Health Check", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_api_base_endpoint(self):
        """Test API base endpoint accessibility"""
        try:
            response = self.session.get(f"{self.base_url}")
            
            # API base might return 404 or 405, but should not be connection error
            if response.status_code in [200, 404, 405, 422]:
                self.log_test("API Base Endpoint", "PASS", f"API accessible (Status: {response.status_code})")
                return True
            else:
                self.log_test("API Base Endpoint", "FAIL", f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("API Base Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_registration_endpoint(self):
        """PRIORITY 1: Test registration endpoint with realistic data"""
        try:
            # Use realistic test data as requested
            unique_email = f"quicktest@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": "password123",
                "name": "Quick Test"
            }
            
            print(f"Testing registration with: {payload}")
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            print(f"Registration response status: {response.status_code}")
            print(f"Registration response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Registration response data: {json.dumps(data, indent=2)}")
                    
                    if "token" in data and "user" in data:
                        user_data = data["user"]
                        if "id" in user_data and "email" in user_data and "name" in user_data:
                            self.log_test("Registration Endpoint", "PASS", 
                                        f"User registered successfully - ID: {user_data['id']}, Email: {user_data['email']}")
                            return {"success": True, "token": data["token"], "user": user_data}
                        else:
                            self.log_test("Registration Endpoint", "FAIL", "Missing required user fields in response")
                            return {"success": False, "error": "Missing user fields"}
                    else:
                        self.log_test("Registration Endpoint", "FAIL", "Missing token or user in response")
                        return {"success": False, "error": "Missing token/user"}
                        
                except json.JSONDecodeError:
                    self.log_test("Registration Endpoint", "FAIL", f"Invalid JSON response: {response.text}")
                    return {"success": False, "error": "Invalid JSON"}
                    
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    self.log_test("Registration Endpoint", "FAIL", f"Bad Request: {error_data}")
                    return {"success": False, "error": f"Bad Request: {error_data}"}
                except:
                    self.log_test("Registration Endpoint", "FAIL", f"Bad Request: {response.text}")
                    return {"success": False, "error": f"Bad Request: {response.text}"}
            else:
                self.log_test("Registration Endpoint", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.ConnectionError:
            self.log_test("Registration Endpoint", "FAIL", "Connection error - cannot reach server")
            return {"success": False, "error": "Connection error"}
        except Exception as e:
            self.log_test("Registration Endpoint", "FAIL", f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_login_endpoint(self, email="quicktest@topkit.com", password="password123"):
        """PRIORITY 2: Test login endpoint with same credentials"""
        try:
            payload = {
                "email": email,
                "password": password
            }
            
            print(f"Testing login with: {payload}")
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            print(f"Login response status: {response.status_code}")
            print(f"Login response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Login response data: {json.dumps(data, indent=2)}")
                    
                    if "token" in data and "user" in data:
                        user_data = data["user"]
                        if "id" in user_data and "email" in user_data and "name" in user_data:
                            self.log_test("Login Endpoint", "PASS", 
                                        f"Login successful - User: {user_data['email']}")
                            return {"success": True, "token": data["token"], "user": user_data}
                        else:
                            self.log_test("Login Endpoint", "FAIL", "Missing required user fields in response")
                            return {"success": False, "error": "Missing user fields"}
                    else:
                        self.log_test("Login Endpoint", "FAIL", "Missing token or user in response")
                        return {"success": False, "error": "Missing token/user"}
                        
                except json.JSONDecodeError:
                    self.log_test("Login Endpoint", "FAIL", f"Invalid JSON response: {response.text}")
                    return {"success": False, "error": "Invalid JSON"}
                    
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    self.log_test("Login Endpoint", "FAIL", f"Bad Request: {error_data}")
                    return {"success": False, "error": f"Bad Request: {error_data}"}
                except:
                    self.log_test("Login Endpoint", "FAIL", f"Bad Request: {response.text}")
                    return {"success": False, "error": f"Bad Request: {response.text}"}
            else:
                self.log_test("Login Endpoint", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.ConnectionError:
            self.log_test("Login Endpoint", "FAIL", "Connection error - cannot reach server")
            return {"success": False, "error": "Connection error"}
        except Exception as e:
            self.log_test("Login Endpoint", "FAIL", f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_token_validation(self, token):
        """Test if the returned token works for protected endpoints"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = self.session.get(f"{self.base_url}/profile", headers=headers)
            
            if response.status_code == 200:
                self.log_test("Token Validation", "PASS", "Token works for protected endpoints")
                return True
            elif response.status_code in [401, 403]:
                self.log_test("Token Validation", "FAIL", f"Token rejected: {response.status_code}")
                return False
            else:
                self.log_test("Token Validation", "FAIL", f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token Validation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test if database is accessible by checking jerseys endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=1")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log_test("Database Connectivity", "PASS", f"Database accessible, found {len(data)} jerseys")
                    return True
                except:
                    self.log_test("Database Connectivity", "FAIL", "Invalid JSON response from database query")
                    return False
            else:
                self.log_test("Database Connectivity", "FAIL", f"Database query failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_rapid_diagnosis(self):
        """Run rapid diagnosis of authentication issues"""
        print("=" * 60)
        print("TOPKIT RAPID AUTHENTICATION DIAGNOSIS")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {}
        
        # PRIORITY 3: Basic connectivity
        print("🔍 PRIORITY 3: TESTING SERVER STATUS")
        print("-" * 40)
        results['server_health'] = self.test_server_health()
        results['api_base'] = self.test_api_base_endpoint()
        results['database'] = self.test_database_connectivity()
        
        # PRIORITY 1: Registration
        print("🔍 PRIORITY 1: TESTING REGISTRATION")
        print("-" * 40)
        reg_result = self.test_registration_endpoint()
        results['registration'] = reg_result
        
        # PRIORITY 2: Login (only if registration worked or we have existing user)
        print("🔍 PRIORITY 2: TESTING LOGIN")
        print("-" * 40)
        if reg_result.get('success'):
            # Use the registered user for login test
            login_result = self.test_login_endpoint()
            results['login'] = login_result
            
            # Test token validation if login worked
            if login_result.get('success'):
                results['token_validation'] = self.test_token_validation(login_result['token'])
        else:
            # Try login anyway in case user already exists
            login_result = self.test_login_endpoint()
            results['login'] = login_result
            
            if login_result.get('success'):
                results['token_validation'] = self.test_token_validation(login_result['token'])
        
        # Summary
        print("=" * 60)
        print("DIAGNOSIS SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if 
                          (isinstance(result, bool) and result) or 
                          (isinstance(result, dict) and result.get('success')))
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print()
        
        # Identify the root cause
        if not results.get('server_health'):
            print("🚨 ROOT CAUSE: Server is not responding")
            print("   SOLUTION: Check if backend server is running")
        elif not results.get('api_base'):
            print("🚨 ROOT CAUSE: API endpoints not accessible")
            print("   SOLUTION: Check API routing and CORS configuration")
        elif not results.get('database'):
            print("🚨 ROOT CAUSE: Database connectivity issues")
            print("   SOLUTION: Check MongoDB connection and database status")
        elif not (results.get('registration', {}).get('success', False)):
            reg_error = results.get('registration', {}).get('error', 'Unknown error')
            print(f"🚨 ROOT CAUSE: Registration endpoint failing - {reg_error}")
            print("   SOLUTION: Check user registration logic and database writes")
        elif not (results.get('login', {}).get('success', False)):
            login_error = results.get('login', {}).get('error', 'Unknown error')
            print(f"🚨 ROOT CAUSE: Login endpoint failing - {login_error}")
            print("   SOLUTION: Check authentication logic and password verification")
        elif not results.get('token_validation'):
            print("🚨 ROOT CAUSE: JWT token validation failing")
            print("   SOLUTION: Check JWT secret key and token generation logic")
        else:
            print("✅ ALL TESTS PASSED: Authentication system appears to be working")
            print("   The frontend 'Authentication failed' error may be due to:")
            print("   - Frontend not sending correct request format")
            print("   - CORS issues")
            print("   - Frontend error handling")
        
        print()
        print(f"Diagnosis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results

def main():
    tester = RapidAuthTester()
    results = tester.run_rapid_diagnosis()
    
    # Return exit code based on results
    if all(isinstance(result, bool) and result or 
           isinstance(result, dict) and result.get('success') 
           for result in results.values()):
        exit(0)  # All tests passed
    else:
        exit(1)  # Some tests failed

if __name__ == "__main__":
    main()