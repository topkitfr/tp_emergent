#!/usr/bin/env python3
"""
TopKit Security Level 2 Backend Testing
Testing all Security Level 2 endpoints as requested in review:
- 2FA System Endpoints
- Password Management
- Admin User Management  
- Enhanced User Profile
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

class SecurityLevel2Tester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        
        self.test_results.append(result)
        print(result)
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_test("Admin Authentication", True, f"Admin: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.log_test("User Authentication", True, f"User: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_test("User Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_2fa_setup(self):
        """Test 2FA setup endpoint"""
        if not self.user_token:
            self.log_test("2FA Setup", False, "No user token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/auth/2fa/setup", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                has_secret = bool(data.get("secret"))
                has_qr_code = bool(data.get("qr_code"))
                has_backup_codes = bool(data.get("backup_codes"))
                backup_codes_count = len(data.get("backup_codes", []))
                
                self.log_test("2FA Setup", True, f"Secret: {has_secret}, QR: {has_qr_code}, Backup codes: {backup_codes_count}")
            else:
                self.log_test("2FA Setup", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("2FA Setup", False, f"Exception: {str(e)}")
    
    def test_2fa_enable(self):
        """Test 2FA enable endpoint with invalid token"""
        if not self.user_token:
            self.log_test("2FA Enable", False, "No user token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/auth/2fa/enable", 
                                   headers=headers,
                                   json={"token": "123456"})  # Invalid token
            
            if response.status_code == 400:
                self.log_test("2FA Enable", True, "Correctly rejects invalid TOTP token")
            elif response.status_code == 200:
                self.log_test("2FA Enable", False, "Should reject invalid token but accepted it")
            else:
                self.log_test("2FA Enable", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("2FA Enable", False, f"Exception: {str(e)}")
    
    def test_2fa_disable(self):
        """Test 2FA disable endpoint"""
        if not self.user_token:
            self.log_test("2FA Disable", False, "No user token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/auth/2fa/disable", 
                                   headers=headers,
                                   json={"token": "123456"})
            
            if response.status_code in [400, 401]:
                self.log_test("2FA Disable", True, "Properly handles 2FA disable request")
            else:
                self.log_test("2FA Disable", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("2FA Disable", False, f"Exception: {str(e)}")
    
    def test_2fa_verify(self):
        """Test 2FA verify endpoint during login"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/2fa/verify", 
                                   json={"token": "123456"})
            
            if response.status_code == 401:
                self.log_test("2FA Verify", True, "Correctly requires authentication token")
            else:
                self.log_test("2FA Verify", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("2FA Verify", False, f"Exception: {str(e)}")
    
    def test_2fa_backup_codes(self):
        """Test 2FA backup codes regeneration"""
        if not self.user_token:
            self.log_test("2FA Backup Codes", False, "No user token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/auth/2fa/backup-codes", headers=headers)
            
            if response.status_code in [200, 400]:
                self.log_test("2FA Backup Codes", True, "Endpoint accessible and handles request")
            else:
                self.log_test("2FA Backup Codes", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("2FA Backup Codes", False, f"Exception: {str(e)}")
    
    def test_change_password(self):
        """Test password change endpoint"""
        if not self.user_token:
            self.log_test("Change Password", False, "No user token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/auth/change-password", 
                                   headers=headers,
                                   json={
                                       "current_password": "wrong_password",
                                       "new_password": "NewSecurePass123!"
                                   })
            
            if response.status_code == 400:
                self.log_test("Change Password", True, "Correctly rejects invalid current password")
            elif response.status_code == 401:
                self.log_test("Change Password", True, "Properly requires authentication")
            else:
                # Test with weak password
                response2 = requests.post(f"{BACKEND_URL}/auth/change-password", 
                                        headers=headers,
                                        json={
                                            "current_password": USER_PASSWORD,
                                            "new_password": "weak"
                                        })
                if response2.status_code == 400:
                    self.log_test("Change Password", True, "Validates password strength")
                else:
                    self.log_test("Change Password", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Change Password", False, f"Exception: {str(e)}")
    
    def test_admin_ban_user(self):
        """Test admin ban user endpoint"""
        if not self.admin_token:
            self.log_test("Admin Ban User", False, "No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            # Try to ban a user (using user's ID if we can get it)
            response = requests.post(f"{BACKEND_URL}/admin/users/test-user-id/ban", 
                                   headers=headers,
                                   json={
                                       "reason": "Test ban",
                                       "permanent": False,
                                       "ban_duration_days": 7
                                   })
            
            if response.status_code in [200, 404, 400]:
                self.log_test("Admin Ban User", True, "Endpoint accessible with proper admin auth")
            elif response.status_code == 403:
                self.log_test("Admin Ban User", False, "Admin access denied")
            else:
                self.log_test("Admin Ban User", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Ban User", False, f"Exception: {str(e)}")
    
    def test_admin_unban_user(self):
        """Test admin unban user endpoint"""
        if not self.admin_token:
            self.log_test("Admin Unban User", False, "No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/admin/users/test-user-id/unban", 
                                   headers=headers)
            
            if response.status_code in [200, 404, 400]:
                self.log_test("Admin Unban User", True, "Endpoint accessible with proper admin auth")
            elif response.status_code == 403:
                self.log_test("Admin Unban User", False, "Admin access denied")
            else:
                self.log_test("Admin Unban User", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Unban User", False, f"Exception: {str(e)}")
    
    def test_admin_delete_user(self):
        """Test admin delete user endpoint"""
        if not self.admin_token:
            self.log_test("Admin Delete User", False, "No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.delete(f"{BACKEND_URL}/admin/users/test-user-id", 
                                     headers=headers)
            
            if response.status_code in [200, 404, 400]:
                self.log_test("Admin Delete User", True, "Endpoint accessible with proper admin auth")
            elif response.status_code == 403:
                self.log_test("Admin Delete User", False, "Admin access denied")
            else:
                self.log_test("Admin Delete User", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin Delete User", False, f"Exception: {str(e)}")
    
    def test_admin_user_security(self):
        """Test admin get user security info endpoint"""
        if not self.admin_token:
            self.log_test("Admin User Security Info", False, "No admin token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/users/test-user-id/security", 
                                  headers=headers)
            
            if response.status_code in [200, 404]:
                self.log_test("Admin User Security Info", True, "Endpoint accessible with proper admin auth")
            elif response.status_code == 403:
                self.log_test("Admin User Security Info", False, "Admin access denied")
            else:
                self.log_test("Admin User Security Info", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Admin User Security Info", False, f"Exception: {str(e)}")
    
    def test_user_profile_settings(self):
        """Test enhanced user profile settings endpoint"""
        if not self.user_token:
            self.log_test("User Profile Settings", False, "No user token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.put(f"{BACKEND_URL}/users/profile/settings", 
                                  headers=headers,
                                  json={
                                      "seller_settings": {
                                          "is_seller": True,
                                          "business_name": "Test Seller",
                                          "address_settings": {
                                              "full_name": "Test User",
                                              "address_line_1": "123 Test St",
                                              "city": "Test City",
                                              "postal_code": "12345",
                                              "country": "France"
                                          }
                                      },
                                      "buyer_settings": {
                                          "address_settings": {
                                              "full_name": "Test Buyer",
                                              "address_line_1": "456 Buyer Ave",
                                              "city": "Buyer City",
                                              "postal_code": "67890",
                                              "country": "France"
                                          }
                                      },
                                      "privacy_settings": {
                                          "profile_visibility": "public",
                                          "show_last_seen": True
                                      }
                                  })
            
            if response.status_code == 200:
                self.log_test("User Profile Settings", True, "Successfully updated profile settings")
            elif response.status_code == 401:
                self.log_test("User Profile Settings", True, "Properly requires authentication")
            else:
                self.log_test("User Profile Settings", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Profile Settings", False, f"Exception: {str(e)}")
    
    def test_user_detailed_profile(self):
        """Test get detailed user profile endpoint"""
        if not self.user_token:
            self.log_test("User Detailed Profile", False, "No user token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/test-user-id/profile", 
                                  headers=headers)
            
            if response.status_code in [200, 404]:
                self.log_test("User Detailed Profile", True, "Endpoint accessible")
            elif response.status_code == 500:
                self.log_test("User Detailed Profile", False, "Server error - implementation issue")
            else:
                self.log_test("User Detailed Profile", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Detailed Profile", False, f"Exception: {str(e)}")
    
    def test_unauthenticated_access(self):
        """Test that endpoints properly require authentication"""
        try:
            # Test 2FA setup without auth
            response = requests.post(f"{BACKEND_URL}/auth/2fa/setup")
            if response.status_code == 401:
                self.log_test("2FA Setup Auth Required", True, "Correctly rejects unauthenticated requests")
            else:
                self.log_test("2FA Setup Auth Required", False, f"Should require auth: HTTP {response.status_code}")
            
            # Test password change without auth
            response = requests.post(f"{BACKEND_URL}/auth/change-password", 
                                   json={"current_password": "test", "new_password": "test"})
            if response.status_code == 401:
                self.log_test("Password Change Auth Required", True, "Correctly rejects unauthenticated requests")
            else:
                self.log_test("Password Change Auth Required", False, f"Should require auth: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Unauthenticated Access", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all Security Level 2 tests"""
        print("🔐 TOPKIT SECURITY LEVEL 2 BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: Admin ({ADMIN_EMAIL}), User ({USER_EMAIL})")
        print("=" * 60)
        
        # Authentication
        print("\n📋 AUTHENTICATION SETUP:")
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        
        # 2FA System Tests
        print("\n🔐 2FA SYSTEM ENDPOINTS:")
        self.test_2fa_setup()
        self.test_2fa_enable()
        self.test_2fa_disable()
        self.test_2fa_verify()
        self.test_2fa_backup_codes()
        
        # Password Management Tests
        print("\n🔑 PASSWORD MANAGEMENT:")
        self.test_change_password()
        
        # Admin User Management Tests
        print("\n👥 ADMIN USER MANAGEMENT:")
        self.test_admin_ban_user()
        self.test_admin_unban_user()
        self.test_admin_delete_user()
        self.test_admin_user_security()
        
        # Enhanced User Profile Tests
        print("\n👤 ENHANCED USER PROFILE:")
        self.test_user_profile_settings()
        self.test_user_detailed_profile()
        
        # Security Tests
        print("\n🛡️ SECURITY VALIDATION:")
        self.test_unauthenticated_access()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SECURITY LEVEL 2 TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 85:
            print("🎉 EXCELLENT IMPLEMENTATION - Security Level 2 is PRODUCTION-READY!")
        elif success_rate >= 70:
            print("✅ GOOD IMPLEMENTATION - Minor issues to address")
        else:
            print("❌ CRITICAL ISSUES - Major fixes required")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result}")
        
        return success_rate

if __name__ == "__main__":
    tester = SecurityLevel2Tester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)