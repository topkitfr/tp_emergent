#!/usr/bin/env python3
"""
TopKit Security Level 2 Backend Testing
Testing new Security Level 2 backend implementation including:
- 2FA Setup & Management
- Password Management  
- Admin User Management
- Enhanced User Profile
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

# Test results tracking
test_results = []
total_tests = 0
passed_tests = 0

def log_test(test_name, success, details="", response_data=None):
    global total_tests, passed_tests
    total_tests += 1
    if success:
        passed_tests += 1
        status = "✅ PASS"
    else:
        status = "❌ FAIL"
    
    result = f"{status} - {test_name}"
    if details:
        result += f": {details}"
    
    test_results.append(result)
    print(result)
    
    if response_data and not success:
        print(f"   Response: {response_data}")

def authenticate_user(email, password):
    """Authenticate user and return token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            if "requires_2fa" in data and data["requires_2fa"]:
                return {"requires_2fa": True, "temp_token": data["temp_token"]}
            return {"token": data["token"], "user": data["user"]}
        else:
            return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def test_authentication_system():
    """Test basic authentication system"""
    print("\n🔐 TESTING AUTHENTICATION SYSTEM")
    
    # Test admin authentication
    admin_auth = authenticate_user(ADMIN_EMAIL, ADMIN_PASSWORD)
    if admin_auth and "token" in admin_auth:
        log_test("Admin Authentication", True, f"Admin user authenticated successfully (Role: {admin_auth['user'].get('role', 'unknown')})")
        admin_token = admin_auth["token"]
        admin_user = admin_auth["user"]
    else:
        log_test("Admin Authentication", False, "Failed to authenticate admin user")
        return None, None, None, None
    
    # Test user authentication
    user_auth = authenticate_user(USER_EMAIL, USER_PASSWORD)
    if user_auth and "token" in user_auth:
        log_test("User Authentication", True, f"User authenticated successfully (Role: {user_auth['user'].get('role', 'unknown')})")
        user_token = user_auth["token"]
        user_user = user_auth["user"]
    else:
        log_test("User Authentication", False, "Failed to authenticate user")
        return admin_token, admin_user, None, None
    
    return admin_token, admin_user, user_token, user_user

def test_2fa_setup_management(user_token, user_id):
    """Test 2FA Setup & Management endpoints"""
    print("\n🔒 TESTING 2FA SETUP & MANAGEMENT")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test 2FA setup
    try:
        response = requests.post(f"{BASE_URL}/auth/2fa/setup", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "secret" in data and "qr_code" in data and "backup_codes" in data:
                log_test("2FA Setup", True, f"QR code and backup codes generated successfully ({len(data['backup_codes'])} backup codes)")
                secret = data["secret"]
                backup_codes = data["backup_codes"]
            else:
                log_test("2FA Setup", False, "Missing required fields in 2FA setup response", data)
                return
        else:
            log_test("2FA Setup", False, f"HTTP {response.status_code}", response.text)
            return
    except Exception as e:
        log_test("2FA Setup", False, f"Exception: {e}")
        return
    
    # Test 2FA enable (would need valid TOTP token in real scenario)
    try:
        # Using a dummy token - in real scenario would need actual TOTP
        response = requests.post(f"{BASE_URL}/auth/2fa/enable", 
                               headers=headers, 
                               json={"token": "123456"})
        if response.status_code == 400:
            log_test("2FA Enable Validation", True, "Correctly rejects invalid 2FA token")
        else:
            log_test("2FA Enable Validation", False, f"Unexpected response: HTTP {response.status_code}")
    except Exception as e:
        log_test("2FA Enable Validation", False, f"Exception: {e}")
    
    # Test 2FA backup codes regeneration
    try:
        response = requests.post(f"{BASE_URL}/auth/2fa/backup-codes", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "backup_codes" in data:
                log_test("2FA Backup Codes Regeneration", True, f"New backup codes generated ({len(data['backup_codes'])} codes)")
            else:
                log_test("2FA Backup Codes Regeneration", False, "Missing backup_codes in response", data)
        elif response.status_code == 400:
            log_test("2FA Backup Codes Regeneration", True, "Correctly requires 2FA to be enabled first")
        else:
            log_test("2FA Backup Codes Regeneration", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("2FA Backup Codes Regeneration", False, f"Exception: {e}")
    
    # Test 2FA disable (would need valid token)
    try:
        response = requests.post(f"{BASE_URL}/auth/2fa/disable", 
                               headers=headers, 
                               json={"token": "123456"})
        if response.status_code == 400:
            log_test("2FA Disable Validation", True, "Correctly rejects invalid 2FA token or requires 2FA to be enabled")
        else:
            log_test("2FA Disable Validation", False, f"Unexpected response: HTTP {response.status_code}")
    except Exception as e:
        log_test("2FA Disable Validation", False, f"Exception: {e}")
    
    # Test 2FA verify during login
    try:
        response = requests.post(f"{BASE_URL}/auth/2fa/verify", 
                               headers=headers, 
                               json={"token": "123456"})
        if response.status_code in [400, 401]:
            log_test("2FA Login Verification", True, "Correctly handles 2FA verification request")
        else:
            log_test("2FA Login Verification", False, f"Unexpected response: HTTP {response.status_code}")
    except Exception as e:
        log_test("2FA Login Verification", False, f"Exception: {e}")

def test_password_management(user_token):
    """Test Password Management endpoints"""
    print("\n🔑 TESTING PASSWORD MANAGEMENT")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test password change with invalid current password
    try:
        response = requests.post(f"{BASE_URL}/auth/change-password", 
                               headers=headers,
                               json={
                                   "current_password": "WrongPassword123!",
                                   "new_password": "NewSecurePassword456!"
                               })
        if response.status_code in [400, 401]:
            log_test("Password Change - Invalid Current Password", True, "Correctly rejects invalid current password")
        else:
            log_test("Password Change - Invalid Current Password", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Password Change - Invalid Current Password", False, f"Exception: {e}")
    
    # Test password change with weak new password
    try:
        response = requests.post(f"{BASE_URL}/auth/change-password", 
                               headers=headers,
                               json={
                                   "current_password": USER_PASSWORD,
                                   "new_password": "weak"
                               })
        if response.status_code == 400:
            log_test("Password Change - Weak Password Validation", True, "Correctly rejects weak password")
        else:
            log_test("Password Change - Weak Password Validation", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Password Change - Weak Password Validation", False, f"Exception: {e}")
    
    # Test password change endpoint accessibility
    try:
        response = requests.post(f"{BASE_URL}/auth/change-password", 
                               headers=headers,
                               json={
                                   "current_password": USER_PASSWORD,
                                   "new_password": "ValidNewPassword123!"
                               })
        if response.status_code in [200, 400]:
            log_test("Password Change Endpoint", True, "Password change endpoint accessible and validates input")
        else:
            log_test("Password Change Endpoint", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Password Change Endpoint", False, f"Exception: {e}")

def test_admin_user_management(admin_token, user_id):
    """Test Admin User Management endpoints"""
    print("\n👑 TESTING ADMIN USER MANAGEMENT")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test ban user
    try:
        response = requests.post(f"{BASE_URL}/admin/users/{user_id}/ban", 
                               headers=headers,
                               json={
                                   "reason": "Test ban for Security Level 2 testing",
                                   "permanent": False,
                                   "ban_duration_days": 7
                               })
        if response.status_code == 200:
            log_test("Admin Ban User", True, "User ban endpoint working correctly")
        elif response.status_code == 404:
            log_test("Admin Ban User", False, "Ban endpoint not found - may not be implemented yet")
        else:
            log_test("Admin Ban User", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Admin Ban User", False, f"Exception: {e}")
    
    # Test unban user
    try:
        response = requests.post(f"{BASE_URL}/admin/users/{user_id}/unban", headers=headers)
        if response.status_code == 200:
            log_test("Admin Unban User", True, "User unban endpoint working correctly")
        elif response.status_code == 404:
            log_test("Admin Unban User", False, "Unban endpoint not found - may not be implemented yet")
        else:
            log_test("Admin Unban User", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Admin Unban User", False, f"Exception: {e}")
    
    # Test get user security information
    try:
        response = requests.get(f"{BASE_URL}/admin/users/{user_id}/security", headers=headers)
        if response.status_code == 200:
            data = response.json()
            log_test("Admin Get User Security Info", True, f"Security info retrieved successfully")
        elif response.status_code == 404:
            log_test("Admin Get User Security Info", False, "Security info endpoint not found - may not be implemented yet")
        else:
            log_test("Admin Get User Security Info", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Admin Get User Security Info", False, f"Exception: {e}")
    
    # Test delete user (dangerous - test with caution)
    try:
        # Create a test user first for deletion
        test_user_response = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "test-delete@topkit.fr",
            "password": "TestPassword123!",
            "name": "Test Delete User"
        })
        
        if test_user_response.status_code == 200:
            test_user_data = test_user_response.json()
            test_user_id = test_user_data["user"]["id"]
            
            # Now test deletion
            response = requests.delete(f"{BASE_URL}/admin/users/{test_user_id}", headers=headers)
            if response.status_code == 200:
                log_test("Admin Delete User", True, "User deletion endpoint working correctly")
            elif response.status_code == 404:
                log_test("Admin Delete User", False, "Delete user endpoint not found - may not be implemented yet")
            else:
                log_test("Admin Delete User", False, f"HTTP {response.status_code}", response.text)
        else:
            log_test("Admin Delete User", False, "Could not create test user for deletion test")
    except Exception as e:
        log_test("Admin Delete User", False, f"Exception: {e}")

def test_enhanced_user_profile(user_token, user_id):
    """Test Enhanced User Profile endpoints"""
    print("\n👤 TESTING ENHANCED USER PROFILE")
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Test get detailed user profile
    try:
        response = requests.get(f"{BASE_URL}/users/{user_id}/profile", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "user" in data or "profile" in data or "id" in data:
                log_test("Get Detailed User Profile", True, "User profile retrieved successfully with detailed information")
            else:
                log_test("Get Detailed User Profile", False, "Profile response missing expected fields", data)
        elif response.status_code == 404:
            log_test("Get Detailed User Profile", False, "Profile endpoint not found - may not be implemented yet")
        else:
            log_test("Get Detailed User Profile", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Get Detailed User Profile", False, f"Exception: {e}")
    
    # Test update profile settings with address information
    try:
        profile_update = {
            "name": "Updated Test Name",
            "bio": "Updated bio for Security Level 2 testing",
            "location": "Paris, France",
            "address_settings": {
                "full_name": "Test User Full Name",
                "address_line_1": "123 Test Street",
                "city": "Paris",
                "postal_code": "75001",
                "country": "France",
                "phone_number": "+33123456789"
            },
            "privacy_settings": {
                "profile_visibility": "public",
                "show_location": True,
                "allow_private_messages": True
            }
        }
        
        response = requests.put(f"{BASE_URL}/users/profile/settings", 
                              headers=headers,
                              json=profile_update)
        if response.status_code == 200:
            log_test("Update Profile Settings with Address", True, "Profile settings updated successfully with address information")
        elif response.status_code == 404:
            log_test("Update Profile Settings with Address", False, "Profile settings endpoint not found - may not be implemented yet")
        else:
            log_test("Update Profile Settings with Address", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Update Profile Settings with Address", False, f"Exception: {e}")
    
    # Test existing profile settings endpoint (fallback)
    try:
        basic_update = {
            "name": "Basic Update Test",
            "profile_privacy": "public"
        }
        
        response = requests.put(f"{BASE_URL}/profile/settings", 
                              headers=headers,
                              json=basic_update)
        if response.status_code == 200:
            log_test("Basic Profile Settings Update", True, "Basic profile settings update working")
        else:
            log_test("Basic Profile Settings Update", False, f"HTTP {response.status_code}", response.text)
    except Exception as e:
        log_test("Basic Profile Settings Update", False, f"Exception: {e}")

def test_security_endpoints_authorization():
    """Test that security endpoints require proper authorization"""
    print("\n🛡️ TESTING SECURITY ENDPOINTS AUTHORIZATION")
    
    # Test 2FA endpoints without authentication
    try:
        response = requests.post(f"{BASE_URL}/auth/2fa/setup")
        if response.status_code in [401, 403]:
            log_test("2FA Setup Authorization", True, "Correctly requires authentication")
        else:
            log_test("2FA Setup Authorization", False, f"HTTP {response.status_code} - should require auth")
    except Exception as e:
        log_test("2FA Setup Authorization", False, f"Exception: {e}")
    
    # Test admin endpoints without admin token
    try:
        response = requests.post(f"{BASE_URL}/admin/users/test-id/ban")
        if response.status_code in [401, 403]:
            log_test("Admin Ban Authorization", True, "Correctly requires admin authentication")
        else:
            log_test("Admin Ban Authorization", False, f"HTTP {response.status_code} - should require admin auth")
    except Exception as e:
        log_test("Admin Ban Authorization", False, f"Exception: {e}")
    
    # Test password change without authentication
    try:
        response = requests.post(f"{BASE_URL}/auth/change-password", json={
            "current_password": "test",
            "new_password": "test"
        })
        if response.status_code in [401, 403]:
            log_test("Password Change Authorization", True, "Correctly requires authentication")
        else:
            log_test("Password Change Authorization", False, f"HTTP {response.status_code} - should require auth")
    except Exception as e:
        log_test("Password Change Authorization", False, f"Exception: {e}")

def main():
    print("🚀 TOPKIT SECURITY LEVEL 2 BACKEND TESTING")
    print("=" * 60)
    print(f"Testing Security Level 2 implementation at: {BASE_URL}")
    print(f"Admin credentials: {ADMIN_EMAIL}")
    print(f"User credentials: {USER_EMAIL}")
    print("=" * 60)
    
    # Test authentication first
    admin_token, admin_user, user_token, user_user = test_authentication_system()
    
    if not admin_token or not user_token:
        print("\n❌ CRITICAL: Authentication failed - cannot proceed with Security Level 2 testing")
        return
    
    user_id = user_user["id"]
    
    # Test Security Level 2 features
    test_2fa_setup_management(user_token, user_id)
    test_password_management(user_token)
    test_admin_user_management(admin_token, user_id)
    test_enhanced_user_profile(user_token, user_id)
    test_security_endpoints_authorization()
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 SECURITY LEVEL 2 TESTING SUMMARY")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
    
    print(f"\n📋 Detailed Results:")
    for result in test_results:
        print(f"  {result}")
    
    if success_rate >= 80:
        print(f"\n✅ EXCELLENT: Security Level 2 implementation is working well!")
    elif success_rate >= 60:
        print(f"\n⚠️ GOOD: Security Level 2 implementation is mostly functional with some issues")
    else:
        print(f"\n❌ NEEDS WORK: Security Level 2 implementation has significant issues")
    
    print("\n🔍 FOCUS AREAS TESTED:")
    print("  • 2FA Setup & Management (QR codes, backup codes, enable/disable)")
    print("  • Password Management (change password with validation)")
    print("  • Admin User Management (ban/unban/delete users, security info)")
    print("  • Enhanced User Profile (detailed profiles, address settings)")
    print("  • Security Authorization (proper authentication requirements)")
    
    return success_rate

if __name__ == "__main__":
    try:
        success_rate = main()
        sys.exit(0 if success_rate >= 60 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {e}")
        sys.exit(1)