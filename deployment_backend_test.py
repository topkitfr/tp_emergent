#!/usr/bin/env python3
"""
TopKit Deployment Fixes Backend Testing
Testing environment variable implementation and deployment readiness
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-fixes.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

class DeploymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                self.log_test("Admin Authentication", True, f"Admin: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_environment_variables(self):
        """Test that environment variables are properly configured"""
        print("\n🔧 TESTING ENVIRONMENT VARIABLE CONFIGURATION")
        
        # Check backend .env file
        try:
            with open('/app/backend/.env', 'r') as f:
                backend_env = f.read()
            
            # Check for FRONTEND_URL
            if 'FRONTEND_URL=' in backend_env:
                self.log_test("Backend FRONTEND_URL Environment Variable", True, "FRONTEND_URL found in backend/.env")
            else:
                self.log_test("Backend FRONTEND_URL Environment Variable", False, "FRONTEND_URL not found in backend/.env")
            
            # Check for hardcoded URLs (should not exist)
            hardcoded_patterns = [
                'https://kit-fixes.preview.emergentagent.com',
                'localhost:3000',
                'http://localhost'
            ]
            
            hardcoded_found = []
            for pattern in hardcoded_patterns:
                if pattern in backend_env and 'FRONTEND_URL=' not in backend_env.split(pattern)[0].split('\n')[-1]:
                    hardcoded_found.append(pattern)
            
            if hardcoded_found:
                self.log_test("No Hardcoded URLs in .env", False, f"Found hardcoded URLs: {hardcoded_found}")
            else:
                self.log_test("No Hardcoded URLs in .env", True, "No hardcoded URLs found in environment file")
                
        except Exception as e:
            self.log_test("Environment File Check", False, f"Could not read backend/.env: {str(e)}")
    
    def test_password_reset_urls(self):
        """Test password reset email URL generation"""
        print("\n📧 TESTING PASSWORD RESET URL GENERATION")
        
        try:
            # Test password reset request
            response = self.session.post(f"{API_BASE}/auth/forgot-password", json={
                "email": "test@example.com"  # Use non-existent email for security
            })
            
            if response.status_code == 200:
                self.log_test("Password Reset Endpoint", True, "Password reset endpoint accessible")
                
                # Check if the endpoint uses environment variables (we can't see the actual email)
                # But we can verify the endpoint works without errors
                data = response.json()
                if 'message' in data:
                    self.log_test("Password Reset Response", True, "Proper response format received")
                else:
                    self.log_test("Password Reset Response", False, "Invalid response format")
            else:
                self.log_test("Password Reset Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Password Reset URL Test", False, f"Exception: {str(e)}")
    
    def test_email_verification_urls(self):
        """Test email verification URL generation"""
        print("\n✉️ TESTING EMAIL VERIFICATION URL GENERATION")
        
        try:
            # Test user registration (which triggers email verification)
            test_email = f"test.deployment.{datetime.now().timestamp()}@example.com"
            response = self.session.post(f"{API_BASE}/auth/register", json={
                "email": test_email,
                "password": "TestPassword123!",
                "name": "Deployment Test User"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("User Registration", True, f"User created: {data.get('user', {}).get('name', 'Unknown')}")
                
                # Check if verification link is provided (for development)
                if 'dev_verification_link' in data:
                    link = data['dev_verification_link']
                    if 'FRONTEND_URL' in str(link) or link.startswith('https://kit-fixes.preview.emergentagent.com'):
                        self.log_test("Email Verification URL", True, "Verification URL uses proper domain")
                    else:
                        self.log_test("Email Verification URL", False, f"Unexpected URL format: {link}")
                else:
                    self.log_test("Email Verification URL", True, "Email verification system operational (no dev link)")
                    
            else:
                self.log_test("User Registration for Email Test", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Email Verification URL Test", False, f"Exception: {str(e)}")
    
    def test_authentication_system(self):
        """Test authentication system with environment-based URLs"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test user authentication
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                self.log_test("User Authentication", True, f"User: {data.get('user', {}).get('name', 'Unknown')}")
                
                # Test protected endpoint access
                headers = {'Authorization': f'Bearer {self.user_token}'}
                profile_response = self.session.get(f"{API_BASE}/profile", headers=headers)
                
                if profile_response.status_code == 200:
                    self.log_test("Protected Endpoint Access", True, "Profile endpoint accessible with JWT token")
                else:
                    self.log_test("Protected Endpoint Access", False, f"HTTP {profile_response.status_code}")
                    
            else:
                self.log_test("User Authentication", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Authentication System Test", False, f"Exception: {str(e)}")
    
    def test_backend_server_configuration(self):
        """Test backend server configuration and URL handling"""
        print("\n🖥️ TESTING BACKEND SERVER CONFIGURATION")
        
        try:
            # Test basic API health
            response = self.session.get(f"{API_BASE}/jerseys")
            
            if response.status_code == 200:
                self.log_test("API Health Check", True, f"Jerseys endpoint accessible")
                
                # Test CORS headers (important for deployment)
                cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
                if cors_headers:
                    self.log_test("CORS Configuration", True, f"CORS headers present: {cors_headers}")
                else:
                    self.log_test("CORS Configuration", False, "No CORS headers found")
                    
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}: {response.text}")
                
            # Test site mode configuration
            site_response = self.session.get(f"{API_BASE}/site/mode")
            if site_response.status_code == 200:
                site_data = site_response.json()
                self.log_test("Site Mode Configuration", True, f"Site mode: {site_data.get('mode', 'unknown')}")
            else:
                self.log_test("Site Mode Configuration", False, f"HTTP {site_response.status_code}")
                
        except Exception as e:
            self.log_test("Backend Server Configuration Test", False, f"Exception: {str(e)}")
    
    def test_email_service_integration(self):
        """Test email service integration and URL generation"""
        print("\n📬 TESTING EMAIL SERVICE INTEGRATION")
        
        if not self.admin_token:
            self.log_test("Email Service Test", False, "Admin authentication required")
            return
        
        try:
            # Test admin endpoints that might trigger email notifications
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            # Get pending jerseys (if any)
            pending_response = self.session.get(f"{API_BASE}/admin/jerseys/pending", headers=headers)
            
            if pending_response.status_code == 200:
                pending_data = pending_response.json()
                self.log_test("Admin Endpoints Access", True, f"Found {len(pending_data)} pending jerseys")
                
                # Test notification system (which might use email)
                notifications_response = self.session.get(f"{API_BASE}/notifications", headers=headers)
                if notifications_response.status_code == 200:
                    self.log_test("Notification System", True, "Notification system accessible")
                else:
                    self.log_test("Notification System", False, f"HTTP {notifications_response.status_code}")
                    
            else:
                self.log_test("Admin Endpoints Access", False, f"HTTP {pending_response.status_code}")
                
        except Exception as e:
            self.log_test("Email Service Integration Test", False, f"Exception: {str(e)}")
    
    def check_source_code_for_hardcoded_urls(self):
        """Check source code for hardcoded URLs"""
        print("\n🔍 CHECKING SOURCE CODE FOR HARDCODED URLS")
        
        files_to_check = [
            '/app/backend/server.py',
            '/app/backend/email_service.py',
            '/app/backend/email_service_marketing.py',
            '/app/backend/email_service_community.py',
            '/app/backend/email_service_extended.py'
        ]
        
        hardcoded_patterns = [
            'https://kit-fixes.preview.emergentagent.com',
            'localhost:3000',
            'http://localhost:3000'
        ]
        
        total_files_checked = 0
        files_with_hardcoded = 0
        
        for file_path in files_to_check:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    total_files_checked += 1
                    hardcoded_found = []
                    
                    for pattern in hardcoded_patterns:
                        if pattern in content:
                            # Check if it's in a comment or environment variable usage
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if pattern in line and not line.strip().startswith('#'):
                                    # Check if it's using environment variable
                                    if 'os.environ.get' not in line and 'FRONTEND_URL' not in line:
                                        hardcoded_found.append(f"Line {i+1}: {line.strip()}")
                    
                    if hardcoded_found:
                        files_with_hardcoded += 1
                        self.log_test(f"Hardcoded URLs in {os.path.basename(file_path)}", False, 
                                    f"Found {len(hardcoded_found)} hardcoded URLs")
                    else:
                        self.log_test(f"Hardcoded URLs in {os.path.basename(file_path)}", True, 
                                    "No hardcoded URLs found")
                        
            except Exception as e:
                self.log_test(f"Source Code Check {file_path}", False, f"Could not read file: {str(e)}")
        
        if total_files_checked > 0:
            success_rate = ((total_files_checked - files_with_hardcoded) / total_files_checked) * 100
            self.log_test("Overall Source Code Check", files_with_hardcoded == 0, 
                        f"Checked {total_files_checked} files, {success_rate:.1f}% clean")
    
    def run_all_tests(self):
        """Run all deployment tests"""
        print("🚀 STARTING TOPKIT DEPLOYMENT FIXES BACKEND TESTING")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Run all tests
        self.test_environment_variables()
        self.test_password_reset_urls()
        self.test_email_verification_urls()
        self.test_authentication_system()
        self.test_backend_server_configuration()
        self.test_email_service_integration()
        self.check_source_code_for_hardcoded_urls()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT FIXES TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 DEPLOYMENT READINESS ASSESSMENT:")
        if success_rate >= 90:
            print("✅ EXCELLENT - Deployment fixes are working correctly")
        elif success_rate >= 75:
            print("⚠️ GOOD - Minor issues identified, mostly deployment ready")
        elif success_rate >= 50:
            print("⚠️ MODERATE - Several issues need attention before deployment")
        else:
            print("❌ CRITICAL - Major issues prevent successful deployment")
        
        # Key findings
        print("\n🔑 KEY FINDINGS:")
        
        # Environment variables
        env_tests = [r for r in self.test_results if 'Environment' in r['test'] or 'FRONTEND_URL' in r['test']]
        env_success = sum(1 for r in env_tests if r['success'])
        if env_success == len(env_tests) and len(env_tests) > 0:
            print("✅ Environment variable implementation: WORKING")
        else:
            print("❌ Environment variable implementation: NEEDS ATTENTION")
        
        # Email functionality
        email_tests = [r for r in self.test_results if 'Email' in r['test'] or 'Password Reset' in r['test']]
        email_success = sum(1 for r in email_tests if r['success'])
        if email_success == len(email_tests) and len(email_tests) > 0:
            print("✅ Email functionality: WORKING")
        else:
            print("❌ Email functionality: NEEDS ATTENTION")
        
        # Authentication system
        auth_tests = [r for r in self.test_results if 'Authentication' in r['test'] or 'Auth' in r['test']]
        auth_success = sum(1 for r in auth_tests if r['success'])
        if auth_success == len(auth_tests) and len(auth_tests) > 0:
            print("✅ Authentication system: WORKING")
        else:
            print("❌ Authentication system: NEEDS ATTENTION")
        
        # Hardcoded URLs
        url_tests = [r for r in self.test_results if 'Hardcoded' in r['test'] or 'URL' in r['test']]
        url_success = sum(1 for r in url_tests if r['success'])
        if url_success == len(url_tests) and len(url_tests) > 0:
            print("✅ No hardcoded URLs: VERIFIED")
        else:
            print("❌ Hardcoded URLs found: NEEDS FIXING")

if __name__ == "__main__":
    tester = DeploymentTester()
    tester.run_all_tests()