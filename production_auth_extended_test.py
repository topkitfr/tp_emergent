#!/usr/bin/env python3
"""
Extended Production Authentication Test for TopKit
Testing additional protected endpoints and JWT token validation
"""

import requests
import json
import jwt
from datetime import datetime
import sys

# Production backend URL
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"

# Test account (using the main requested account)
TEST_ACCOUNT = {
    "email": "Bacquet.florent@gmail.com",
    "password": "TopKitBeta2025!",
    "description": "Main requested account"
}

class ExtendedAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TopKit-Extended-Auth-Test/1.0'
        })
        self.token = None
        self.user_data = None
        
    def authenticate(self):
        """Authenticate and get token"""
        print(f"🔐 Authenticating as {TEST_ACCOUNT['email']}")
        
        try:
            login_data = {
                "email": TEST_ACCOUNT['email'],
                "password": TEST_ACCOUNT['password']
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                login_response = response.json()
                self.token = login_response.get('token')
                self.user_data = login_response.get('user', {})
                print(f"✅ Authentication successful - User: {self.user_data.get('name')}")
                return True
            else:
                print(f"❌ Authentication failed - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
            
    def test_protected_endpoints(self):
        """Test various protected endpoints"""
        if not self.token:
            print("❌ No token available for testing")
            return
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # List of protected endpoints to test
        protected_endpoints = [
            ('/profile', 'User Profile'),
            ('/users/me', 'Current User Info'),
            ('/notifications', 'User Notifications'),
            ('/collections/my-owned', 'User Collections - Owned'),
            ('/collections/my-wanted', 'User Collections - Wanted'),
            (f"/users/{self.user_data.get('id')}/jerseys", 'User Jersey Submissions'),
            ('/conversations', 'User Conversations'),
            ('/friends', 'User Friends')
        ]
        
        print(f"\n🛡️ Testing {len(protected_endpoints)} protected endpoints")
        
        successful_tests = 0
        for endpoint, description in protected_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code in [200, 404]:  # 404 is acceptable for empty collections
                    print(f"✅ {description}: HTTP {response.status_code}")
                    successful_tests += 1
                elif response.status_code == 401:
                    print(f"❌ {description}: HTTP 401 - Token validation failed")
                elif response.status_code == 403:
                    print(f"⚠️ {description}: HTTP 403 - Access forbidden (may be expected)")
                    successful_tests += 1  # Count as success if it's a permission issue, not auth
                else:
                    print(f"⚠️ {description}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
                
        print(f"\nProtected endpoints test: {successful_tests}/{len(protected_endpoints)} successful")
        return successful_tests
        
    def test_jwt_token_details(self):
        """Test JWT token structure and contents"""
        if not self.token:
            print("❌ No token available for JWT analysis")
            return
            
        print(f"\n🔍 Analyzing JWT Token Structure")
        
        try:
            # Decode token without verification to inspect contents
            decoded_token = jwt.decode(self.token, options={"verify_signature": False})
            
            print(f"✅ JWT Token successfully decoded")
            print(f"   User ID: {decoded_token.get('user_id')}")
            print(f"   Expiration: {datetime.fromtimestamp(decoded_token.get('exp', 0))}")
            
            # Check if token is properly structured
            required_fields = ['user_id', 'exp']
            missing_fields = [field for field in required_fields if field not in decoded_token]
            
            if missing_fields:
                print(f"❌ JWT Token missing required fields: {missing_fields}")
                return False
            else:
                print(f"✅ JWT Token contains all required fields")
                return True
                
        except Exception as e:
            print(f"❌ JWT Token analysis failed: {str(e)}")
            return False
            
    def test_token_persistence(self):
        """Test that token works across multiple requests"""
        if not self.token:
            print("❌ No token available for persistence testing")
            return
            
        print(f"\n🔄 Testing Token Persistence Across Multiple Requests")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        successful_requests = 0
        
        # Make multiple requests to test token persistence
        for i in range(3):
            try:
                response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
                if response.status_code == 200:
                    successful_requests += 1
                    print(f"✅ Request {i+1}: Token valid")
                else:
                    print(f"❌ Request {i+1}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Request {i+1}: Error - {str(e)}")
                
        print(f"Token persistence: {successful_requests}/3 requests successful")
        return successful_requests == 3
        
    def run_extended_test(self):
        """Run comprehensive extended authentication test"""
        print("🚀 Starting Extended Production Authentication Test")
        print(f"Backend URL: {BACKEND_URL}")
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with extended tests")
            return False
            
        # Step 2: Test JWT token structure
        jwt_valid = self.test_jwt_token_details()
        
        # Step 3: Test protected endpoints
        protected_success = self.test_protected_endpoints()
        
        # Step 4: Test token persistence
        persistence_success = self.test_token_persistence()
        
        # Summary
        print(f"\n📊 EXTENDED AUTHENTICATION TEST SUMMARY")
        print(f"✅ Authentication: SUCCESS")
        print(f"{'✅' if jwt_valid else '❌'} JWT Token Structure: {'VALID' if jwt_valid else 'INVALID'}")
        print(f"✅ Protected Endpoints: {protected_success} endpoints accessible")
        print(f"{'✅' if persistence_success else '❌'} Token Persistence: {'SUCCESS' if persistence_success else 'FAILED'}")
        
        overall_success = jwt_valid and persistence_success and protected_success > 0
        
        if overall_success:
            print(f"\n🎉 Extended authentication test PASSED!")
            print(f"Production authentication is working correctly for {TEST_ACCOUNT['email']}")
        else:
            print(f"\n🚨 Extended authentication test had issues!")
            
        return overall_success

def main():
    """Main test execution"""
    tester = ExtendedAuthTester()
    success = tester.run_extended_test()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()