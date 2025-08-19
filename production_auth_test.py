#!/usr/bin/env python3
"""
Production Authentication Testing for TopKit Beta Users
Testing authentication for 4 specific production accounts at https://topkit-beta.emergent.host/
"""

import requests
import json
import jwt
from datetime import datetime
import sys

# Production backend URL
BACKEND_URL = "https://topkit-beta.emergent.host/api"

# Test accounts with shared password
TEST_ACCOUNTS = [
    "beltramopierre@gmail.com",
    "Bacquet.florent@gmail.com", 
    "steinmetzpierre@gmail.com",
    "thomasteinmetz@gmail.com"
]

PASSWORD = "TopKitBeta2025!"

# Known working accounts for endpoint verification
KNOWN_ACCOUNTS = [
    {"email": "topkitfr@gmail.com", "password": "TopKitSecure789#"},
    {"email": "steinmetzlivio@gmail.com", "password": "TopKit123!"}
]

class ProductionAuthTester:
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_user_existence(self, admin_token):
        """Check if the requested users exist in the production database"""
        self.log("🔍 Checking if requested users exist in production database")
        
        try:
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            # Try to get user list from admin endpoint
            response = requests.get(
                f"{BACKEND_URL}/admin/users",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json()
                self.log(f"✅ Retrieved users from production database")
                self.log(f"Raw response: {users}")
                self.log(f"Response type: {type(users)}")
                
                # Check if our requested users exist
                existing_emails = []
                
                # Handle different response formats
                if isinstance(users, dict) and 'users' in users:
                    # Extract users from nested structure
                    user_list = users['users']
                    for user in user_list:
                        if isinstance(user, dict):
                            email = user.get('email', '').lower()
                            existing_emails.append(email)
                elif isinstance(users, list):
                    for user in users:
                        if isinstance(user, dict):
                            email = user.get('email', '').lower()
                            existing_emails.append(email)
                
                self.log(f"Found emails: {existing_emails}")
                
                for email in TEST_ACCOUNTS:
                    if email.lower() in existing_emails:
                        self.log(f"✅ User {email} exists in production database")
                    else:
                        self.log(f"❌ User {email} NOT found in production database")
                
                # Show all users for debugging
                self.log("📋 All users in production database:")
                if isinstance(users, dict) and 'users' in users:
                    user_list = users['users']
                    for i, user in enumerate(user_list):
                        email = user.get('email', 'N/A')
                        name = user.get('name', 'N/A')
                        role = user.get('role', 'N/A')
                        beta_access = user.get('beta_access', False)
                        self.log(f"   {i+1}. {email} ({name}) - Role: {role}, Beta Access: {beta_access}")
                    
            else:
                self.log(f"❌ Failed to retrieve users: HTTP {response.status_code}")
                self.log(f"   Response: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error checking user existence: {e}", "ERROR")
            import traceback
            self.log(f"   Traceback: {traceback.format_exc()}", "ERROR")
    
    def test_endpoint_connectivity(self):
        """Test if the production endpoint is working with known accounts"""
        self.log("🔍 Testing production endpoint connectivity with known accounts")
        
        for account in KNOWN_ACCOUNTS:
            email = account["email"]
            password = account["password"]
            
            try:
                login_data = {
                    "email": email,
                    "password": password
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.log(f"✅ Production endpoint working - {email} authenticated successfully")
                    
                    # Get admin token for user existence check
                    if email == "topkitfr@gmail.com":
                        data = response.json()
                        admin_token = data.get('token')
                        if admin_token:
                            self.check_user_existence(admin_token)
                    
                    return True
                else:
                    self.log(f"⚠️  Known account {email} failed: HTTP {response.status_code}")
                    
            except Exception as e:
                self.log(f"❌ Error testing known account {email}: {e}", "ERROR")
        
        self.log("❌ Production endpoint connectivity test failed", "ERROR")
        return False
    
    def test_login_authentication(self, email):
        """Test POST /api/auth/login for specific account"""
        self.log(f"Testing authentication for {email}")
        
        try:
            # Test login endpoint
            login_data = {
                "email": email,
                "password": PASSWORD
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            self.total_tests += 1
            
            if response.status_code == 200:
                self.log(f"✅ Login successful for {email} (HTTP 200)")
                self.passed_tests += 1
                
                # Parse response
                data = response.json()
                token = data.get('token')
                user_data = data.get('user', {})
                
                if token:
                    self.log(f"✅ JWT token received for {email}")
                    self.passed_tests += 1
                    
                    # Decode token to check contents (without verification for inspection)
                    try:
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        self.log(f"✅ Token decoded successfully for {email}")
                        self.log(f"   Token user_id: {decoded.get('user_id')}")
                        self.log(f"   Token exp: {decoded.get('exp')}")
                        self.passed_tests += 1
                    except Exception as e:
                        self.log(f"❌ Failed to decode token for {email}: {e}", "ERROR")
                    
                    # Check user data in response
                    self.log(f"User data for {email}:")
                    self.log(f"   Name: {user_data.get('name', 'N/A')}")
                    self.log(f"   Email: {user_data.get('email', 'N/A')}")
                    self.log(f"   Role: {user_data.get('role', 'N/A')}")
                    self.log(f"   Beta Access: {user_data.get('beta_access', 'N/A')}")
                    
                    # Check if beta_access is true
                    if user_data.get('beta_access') == True:
                        self.log(f"✅ Beta access confirmed for {email}")
                        self.passed_tests += 1
                    else:
                        self.log(f"❌ Beta access not found or false for {email}", "ERROR")
                    
                    # Test token validation with protected endpoint
                    self.test_protected_endpoint(email, token)
                    
                else:
                    self.log(f"❌ No token received for {email}", "ERROR")
                    
                self.results[email] = {
                    "login_success": True,
                    "token_received": bool(token),
                    "user_data": user_data,
                    "beta_access": user_data.get('beta_access', False)
                }
                
            else:
                self.log(f"❌ Login failed for {email} (HTTP {response.status_code})", "ERROR")
                self.log(f"   Response: {response.text}")
                self.results[email] = {
                    "login_success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Network error testing {email}: {e}", "ERROR")
            self.results[email] = {
                "login_success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            self.log(f"❌ Unexpected error testing {email}: {e}", "ERROR")
            self.results[email] = {
                "login_success": False,
                "error": f"Unexpected error: {str(e)}"
            }
            
        self.total_tests += 3  # login, token, beta_access checks
        
    def test_protected_endpoint(self, email, token):
        """Test token validation against /api/profile endpoint"""
        self.log(f"Testing protected endpoint access for {email}")
        
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{BACKEND_URL}/profile",
                headers=headers,
                timeout=10
            )
            
            self.total_tests += 1
            
            if response.status_code == 200:
                self.log(f"✅ Protected endpoint access successful for {email}")
                self.passed_tests += 1
                
                profile_data = response.json()
                self.log(f"   Profile ID: {profile_data.get('id', 'N/A')}")
                self.log(f"   Profile Email: {profile_data.get('email', 'N/A')}")
                
            else:
                self.log(f"❌ Protected endpoint access failed for {email} (HTTP {response.status_code})", "ERROR")
                self.log(f"   Response: {response.text}")
                
        except Exception as e:
            self.log(f"❌ Error testing protected endpoint for {email}: {e}", "ERROR")
    
    def run_all_tests(self):
        """Run authentication tests for all production accounts"""
        self.log("🚀 Starting Production Authentication Testing")
        self.log(f"Backend URL: {BACKEND_URL}")
        self.log(f"Testing {len(TEST_ACCOUNTS)} accounts")
        self.log("-" * 60)
        
        # First test endpoint connectivity
        if not self.test_endpoint_connectivity():
            self.log("🚨 Production endpoint not accessible - aborting tests", "ERROR")
            return 0
        
        self.log("-" * 60)
        
        for email in TEST_ACCOUNTS:
            self.test_login_authentication(email)
            self.log("-" * 60)
        
        # Summary
        self.log("📊 PRODUCTION AUTHENTICATION TEST SUMMARY")
        self.log(f"Total Tests: {self.total_tests}")
        self.log(f"Passed: {self.passed_tests}")
        self.log(f"Failed: {self.total_tests - self.passed_tests}")
        self.log(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        self.log("\n📋 ACCOUNT STATUS SUMMARY:")
        for email, result in self.results.items():
            if result.get('login_success'):
                beta_status = "✅ Beta Access" if result.get('beta_access') else "❌ No Beta Access"
                self.log(f"✅ {email}: Login OK, {beta_status}")
            else:
                self.log(f"❌ {email}: Login Failed - {result.get('error', 'Unknown error')}")
        
        return self.passed_tests / self.total_tests if self.total_tests > 0 else 0

def main():
    """Main test execution"""
    tester = ProductionAuthTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    if success_rate >= 0.8:  # 80% success rate threshold
        print("\n🎉 Production authentication testing completed successfully!")
        sys.exit(0)
    else:
        print(f"\n🚨 Production authentication testing failed (success rate: {success_rate:.1f}%)")
        sys.exit(1)

if __name__ == "__main__":
    main()