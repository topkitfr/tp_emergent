#!/usr/bin/env python3
"""
Production Authentication Backend Test for TopKit
Testing specific production accounts after database configuration fix
"""

import requests
import json
import jwt
from datetime import datetime
import sys

# Production backend URL from frontend/.env
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"

# Test accounts as specified in review request
TEST_ACCOUNTS = [
    {
        "email": "Bacquet.florent@gmail.com",
        "password": "TopKitBeta2025!",
        "description": "Main requested account"
    },
    {
        "email": "beltramopierre@gmail.com", 
        "password": "TopKitBeta2025!",
        "description": "Secondary test account"
    }
]

class ProductionAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TopKit-Production-Auth-Test/1.0'
        })
        self.results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    def test_authentication(self, account):
        """Test authentication for a specific account"""
        print(f"\n🔐 Testing authentication for {account['email']} ({account['description']})")
        
        try:
            # Test login endpoint
            login_data = {
                "email": account['email'],
                "password": account['password']
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code != 200:
                self.log_result(
                    f"Login {account['email']}", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
            login_response = response.json()
            
            # Verify response structure
            if 'token' not in login_response:
                self.log_result(
                    f"Login Response {account['email']}", 
                    False, 
                    "No JWT token in response"
                )
                return None
                
            token = login_response['token']
            user_data = login_response.get('user', {})
            
            self.log_result(
                f"Login {account['email']}", 
                True, 
                f"HTTP 200 with JWT token received"
            )
            
            # Decode and verify JWT token structure
            try:
                # Decode without verification to inspect contents
                decoded_token = jwt.decode(token, options={"verify_signature": False})
                self.log_result(
                    f"JWT Structure {account['email']}", 
                    True, 
                    f"Token contains user_id: {decoded_token.get('user_id', 'N/A')}"
                )
            except Exception as e:
                self.log_result(
                    f"JWT Structure {account['email']}", 
                    False, 
                    f"Failed to decode JWT: {str(e)}"
                )
                
            # Verify user data in response
            expected_fields = ['id', 'name', 'email', 'role']
            missing_fields = [field for field in expected_fields if field not in user_data]
            
            if missing_fields:
                self.log_result(
                    f"User Data {account['email']}", 
                    False, 
                    f"Missing fields: {missing_fields}"
                )
            else:
                # Check for beta_access field specifically mentioned in requirements
                beta_access = user_data.get('beta_access', False)
                self.log_result(
                    f"User Data {account['email']}", 
                    True, 
                    f"Name: {user_data.get('name')}, Email: {user_data.get('email')}, Role: {user_data.get('role')}, Beta Access: {beta_access}"
                )
                
            # Test token validation against protected endpoint
            self.test_protected_endpoint(account['email'], token)
            
            return token
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                f"Login {account['email']}", 
                False, 
                f"Network error: {str(e)}"
            )
            return None
        except Exception as e:
            self.log_result(
                f"Login {account['email']}", 
                False, 
                f"Unexpected error: {str(e)}"
            )
            return None
            
    def test_protected_endpoint(self, email, token):
        """Test token validation against protected endpoints"""
        try:
            # Test /api/profile endpoint
            headers = {'Authorization': f'Bearer {token}'}
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                self.log_result(
                    f"Protected Endpoint {email}", 
                    True, 
                    f"Profile access successful - User: {profile_data.get('name', 'N/A')}"
                )
            else:
                self.log_result(
                    f"Protected Endpoint {email}", 
                    False, 
                    f"Profile access failed - HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                f"Protected Endpoint {email}", 
                False, 
                f"Error accessing protected endpoint: {str(e)}"
            )
            
    def test_backend_health(self):
        """Test basic backend connectivity"""
        print("🏥 Testing backend health and connectivity")
        
        try:
            # Test basic endpoint
            response = self.session.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                self.log_result(
                    "Backend Health", 
                    True, 
                    f"Backend accessible - Found {len(jerseys)} jerseys"
                )
            else:
                self.log_result(
                    "Backend Health", 
                    False, 
                    f"Backend not accessible - HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Backend Health", 
                False, 
                f"Backend connection failed: {str(e)}"
            )
            
    def run_comprehensive_test(self):
        """Run comprehensive production authentication test"""
        print("🚀 Starting Production Authentication Test for TopKit")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Testing {len(TEST_ACCOUNTS)} production accounts")
        
        # Test backend health first
        self.test_backend_health()
        
        # Test each account
        successful_logins = 0
        for account in TEST_ACCOUNTS:
            token = self.test_authentication(account)
            if token:
                successful_logins += 1
                
        # Summary
        print(f"\n📊 PRODUCTION AUTHENTICATION TEST SUMMARY")
        print(f"Total accounts tested: {len(TEST_ACCOUNTS)}")
        print(f"Successful authentications: {successful_logins}")
        print(f"Success rate: {(successful_logins/len(TEST_ACCOUNTS)*100):.1f}%")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        passed_tests = sum(1 for r in self.results if r['success'])
        total_tests = len(self.results)
        
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
            
        print(f"\nOverall Test Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}%)")
        
        return successful_logins == len(TEST_ACCOUNTS)

def main():
    """Main test execution"""
    tester = ProductionAuthTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All production authentication tests PASSED!")
        sys.exit(0)
    else:
        print("\n🚨 Some production authentication tests FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()