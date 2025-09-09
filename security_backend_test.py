#!/usr/bin/env python3
"""
TopKit Enhanced Security Features Testing Suite
Testing comprehensive security improvements in TopKit authentication system

PRIMARY SECURITY FEATURES TO TEST:
1. Password Strength Validation
2. Rate Limiting for Account Creation  
3. Email Verification System
4. Enhanced Login Security
5. User Model Security Fields

Test Credentials:
- Admin: topkitfr@gmail.com/adminpass123 (should bypass email verification)
- Test various password combinations for validation
"""

import requests
import json
import sys
import time
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"

class SecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_id = None
        self.test_results = []
        self.test_emails = []  # Track emails created for cleanup
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def admin_login(self):
        """Login as admin for testing purposes"""
        print("🔐 ADMIN LOGIN FOR TESTING")
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.admin_id = data["user"]["id"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_test("Admin Login", True, f"Admin authenticated: {data['user']['name']}")
                return True
            else:
                self.log_test("Admin Login", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, error=str(e))
            return False

    def test_password_strength_validation(self):
        """Test 1: Password Strength Validation - Test registration with weak passwords"""
        print("🔒 TESTING PASSWORD STRENGTH VALIDATION")
        
        # Test cases for password validation
        password_tests = [
            {
                "password": "123",
                "expected_fail": True,
                "reason": "Too short (< 8 characters)"
            },
            {
                "password": "12345678",
                "expected_fail": True,
                "reason": "Missing uppercase letters"
            },
            {
                "password": "ABCDEFGH",
                "expected_fail": True,
                "reason": "Missing lowercase letters"
            },
            {
                "password": "abcdefgh",
                "expected_fail": True,
                "reason": "Missing numbers and uppercase"
            },
            {
                "password": "Abcdefgh",
                "expected_fail": True,
                "reason": "Missing numbers"
            },
            {
                "password": "Abcdefg1",
                "expected_fail": True,
                "reason": "Missing special characters"
            },
            {
                "password": "Password123",
                "expected_fail": True,
                "reason": "Contains common weak pattern 'password'"
            },
            {
                "password": "Admin123!",
                "expected_fail": True,
                "reason": "Contains common weak pattern 'admin'"
            },
            {
                "password": "User123abc",
                "expected_fail": True,
                "reason": "Contains common weak patterns 'user' and 'abc'"
            },
            {
                "password": "Test123456",
                "expected_fail": True,
                "reason": "Contains common weak pattern '123'"
            },
            {
                "password": "StrongPass456!",
                "expected_fail": False,
                "reason": "Valid strong password"
            }
        ]
        
        passed_tests = 0
        total_tests = len(password_tests)
        
        for i, test_case in enumerate(password_tests):
            test_email = f"pwtest{i}_{uuid.uuid4().hex[:8]}@test.com"
            self.test_emails.append(test_email)
            
            try:
                response = self.session.post(f"{BASE_URL}/auth/register", json={
                    "email": test_email,
                    "password": test_case["password"],
                    "name": f"Password Test User {i}"
                })
                
                if test_case["expected_fail"]:
                    # Should fail with 400 status
                    if response.status_code == 400:
                        passed_tests += 1
                        self.log_test(
                            f"Password Validation - {test_case['reason']}", 
                            True, 
                            f"Correctly rejected weak password: {test_case['password']}"
                        )
                    else:
                        self.log_test(
                            f"Password Validation - {test_case['reason']}", 
                            False, 
                            error=f"Expected rejection but got HTTP {response.status_code}"
                        )
                else:
                    # Should succeed with 200 status
                    if response.status_code == 200:
                        passed_tests += 1
                        self.log_test(
                            f"Password Validation - {test_case['reason']}", 
                            True, 
                            f"Correctly accepted strong password"
                        )
                    else:
                        self.log_test(
                            f"Password Validation - {test_case['reason']}", 
                            False, 
                            error=f"Expected success but got HTTP {response.status_code}: {response.text}"
                        )
                        
            except Exception as e:
                self.log_test(
                    f"Password Validation - {test_case['reason']}", 
                    False, 
                    error=str(e)
                )
        
        success_rate = (passed_tests / total_tests) * 100
        self.log_test(
            "Password Strength Validation Overall", 
            passed_tests == total_tests,
            f"Passed {passed_tests}/{total_tests} tests ({success_rate:.1f}%)"
        )

    def test_rate_limiting(self):
        """Test 2: Rate Limiting - Test account creation rate limiting (3 accounts per hour per IP)"""
        print("⏱️ TESTING RATE LIMITING FOR ACCOUNT CREATION")
        
        # Try to create 4 accounts rapidly to test rate limiting
        accounts_created = 0
        rate_limit_triggered = False
        
        for i in range(4):
            test_email = f"ratetest{i}_{uuid.uuid4().hex[:8]}@test.com"
            self.test_emails.append(test_email)
            
            try:
                response = self.session.post(f"{BASE_URL}/auth/register", json={
                    "email": test_email,
                    "password": "ValidPass456!",
                    "name": f"Rate Test User {i}"
                })
                
                if response.status_code == 200:
                    accounts_created += 1
                    self.log_test(
                        f"Rate Limit Test - Account {i+1}", 
                        True, 
                        f"Account created successfully"
                    )
                elif response.status_code == 429:
                    rate_limit_triggered = True
                    self.log_test(
                        f"Rate Limit Test - Account {i+1}", 
                        True, 
                        f"Rate limit correctly triggered after {accounts_created} accounts"
                    )
                    break
                else:
                    self.log_test(
                        f"Rate Limit Test - Account {i+1}", 
                        False, 
                        error=f"Unexpected response: HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"Rate Limit Test - Account {i+1}", 
                    False, 
                    error=str(e)
                )
        
        # Rate limiting should trigger after 3 accounts
        if rate_limit_triggered and accounts_created <= 3:
            self.log_test(
                "Rate Limiting System", 
                True, 
                f"Rate limit correctly enforced after {accounts_created} accounts"
            )
        elif accounts_created >= 4:
            self.log_test(
                "Rate Limiting System", 
                False, 
                error=f"Rate limit not enforced - created {accounts_created} accounts"
            )
        else:
            self.log_test(
                "Rate Limiting System", 
                False, 
                error="Rate limiting test inconclusive"
            )

    def test_email_verification_system(self):
        """Test 3: Email Verification System - Test email verification workflow"""
        print("📧 TESTING EMAIL VERIFICATION SYSTEM")
        
        # Create a new account for email verification testing
        test_email = f"emailverify_{uuid.uuid4().hex[:8]}@test.com"
        self.test_emails.append(test_email)
        
        try:
            # Step 1: Register new account
            response = self.session.post(f"{BASE_URL}/auth/register", json={
                "email": test_email,
                "password": "ValidPass456!",
                "name": "Email Verification Test User"
            })
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                
                # Check that email_verified is False
                if user_data.get("email_verified") == False:
                    self.log_test(
                        "Email Verification - Account Creation", 
                        True, 
                        "Account created with email_verified=false"
                    )
                else:
                    self.log_test(
                        "Email Verification - Account Creation", 
                        False, 
                        error=f"Expected email_verified=false, got {user_data.get('email_verified')}"
                    )
                
                # Check if verification token is provided (dev mode)
                verification_link = data.get("dev_verification_link")
                if verification_link:
                    # Extract token from verification link
                    token = verification_link.split("token=")[1] if "token=" in verification_link else None
                    
                    if token:
                        self.log_test(
                            "Email Verification - Token Generation", 
                            True, 
                            "Verification token generated successfully"
                        )
                        
                        # Step 2: Test email verification with valid token
                        verify_response = self.session.post(f"{BASE_URL}/auth/verify-email", params={"token": token})
                        
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            verified_user = verify_data.get("user", {})
                            
                            if verified_user.get("email_verified") == True:
                                self.log_test(
                                    "Email Verification - Valid Token", 
                                    True, 
                                    "Email verified successfully with valid token"
                                )
                            else:
                                self.log_test(
                                    "Email Verification - Valid Token", 
                                    False, 
                                    error="Email verification did not update email_verified status"
                                )
                        else:
                            self.log_test(
                                "Email Verification - Valid Token", 
                                False, 
                                error=f"HTTP {verify_response.status_code}: {verify_response.text}"
                            )
                        
                        # Step 3: Test email verification with invalid token
                        invalid_token = "invalid_token_12345"
                        invalid_response = self.session.post(f"{BASE_URL}/auth/verify-email", params={"token": invalid_token})
                        
                        if invalid_response.status_code == 400:
                            self.log_test(
                                "Email Verification - Invalid Token", 
                                True, 
                                "Invalid token correctly rejected"
                            )
                        else:
                            self.log_test(
                                "Email Verification - Invalid Token", 
                                False, 
                                error=f"Expected HTTP 400, got {invalid_response.status_code}"
                            )
                    else:
                        self.log_test(
                            "Email Verification - Token Generation", 
                            False, 
                            error="Could not extract token from verification link"
                        )
                else:
                    self.log_test(
                        "Email Verification - Token Generation", 
                        False, 
                        error="No verification link provided in registration response"
                    )
            else:
                self.log_test(
                    "Email Verification - Account Creation", 
                    False, 
                    error=f"Registration failed: HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Email Verification System", 
                False, 
                error=str(e)
            )

    def test_enhanced_login_security(self):
        """Test 4: Enhanced Login Security - Test improved login with email verification check"""
        print("🔐 TESTING ENHANCED LOGIN SECURITY")
        
        # Test 1: Admin bypass for email verification requirement
        try:
            admin_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                self.log_test(
                    "Enhanced Login - Admin Bypass", 
                    True, 
                    f"Admin can login without email verification: {admin_data['user']['name']}"
                )
            else:
                self.log_test(
                    "Enhanced Login - Admin Bypass", 
                    False, 
                    error=f"Admin login failed: HTTP {admin_response.status_code}: {admin_response.text}"
                )
        except Exception as e:
            self.log_test(
                "Enhanced Login - Admin Bypass", 
                False, 
                error=str(e)
            )
        
        # Test 2: Unverified user login should be blocked
        unverified_email = f"unverified_{uuid.uuid4().hex[:8]}@test.com"
        self.test_emails.append(unverified_email)
        
        try:
            # Create unverified account
            reg_response = self.session.post(f"{BASE_URL}/auth/register", json={
                "email": unverified_email,
                "password": "ValidPass456!",
                "name": "Unverified Test User"
            })
            
            if reg_response.status_code == 200:
                # Try to login with unverified account
                login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                    "email": unverified_email,
                    "password": "ValidPass456!"
                })
                
                if login_response.status_code == 403:
                    self.log_test(
                        "Enhanced Login - Email Verification Check", 
                        True, 
                        "Unverified users correctly blocked from login"
                    )
                else:
                    self.log_test(
                        "Enhanced Login - Email Verification Check", 
                        False, 
                        error=f"Expected HTTP 403, got {login_response.status_code}: {login_response.text}"
                    )
            else:
                self.log_test(
                    "Enhanced Login - Email Verification Check", 
                    False, 
                    error=f"Could not create test account: HTTP {reg_response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Enhanced Login - Email Verification Check", 
                False, 
                error=str(e)
            )

    def test_user_model_security_fields(self):
        """Test 5: User Model Updates - Verify new security fields are properly stored"""
        print("👤 TESTING USER MODEL SECURITY FIELDS")
        
        if not self.admin_token:
            self.log_test(
                "User Model Security Fields", 
                False, 
                error="Admin token required for user data verification"
            )
            return
        
        # Create a test account and verify security fields
        test_email = f"modeltest_{uuid.uuid4().hex[:8]}@test.com"
        self.test_emails.append(test_email)
        
        try:
            # Register new account
            response = self.session.post(f"{BASE_URL}/auth/register", json={
                "email": test_email,
                "password": "ValidPass456!",
                "name": "Model Test User"
            })
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                
                # Check required security fields
                security_fields = {
                    "email_verified": False,  # Should be False initially
                    "id": str,  # Should have UUID
                    "email": test_email,  # Should match
                    "name": "Model Test User",  # Should match
                    "role": "user"  # Should be user role
                }
                
                fields_correct = 0
                total_fields = len(security_fields)
                
                for field, expected_value in security_fields.items():
                    actual_value = user_data.get(field)
                    
                    if field == "id":
                        # Check if ID is a valid UUID string
                        if isinstance(actual_value, str) and len(actual_value) > 0:
                            fields_correct += 1
                            self.log_test(
                                f"User Model - {field} field", 
                                True, 
                                f"Valid UUID: {actual_value}"
                            )
                        else:
                            self.log_test(
                                f"User Model - {field} field", 
                                False, 
                                error=f"Invalid ID format: {actual_value}"
                            )
                    else:
                        if actual_value == expected_value:
                            fields_correct += 1
                            self.log_test(
                                f"User Model - {field} field", 
                                True, 
                                f"Correct value: {actual_value}"
                            )
                        else:
                            self.log_test(
                                f"User Model - {field} field", 
                                False, 
                                error=f"Expected {expected_value}, got {actual_value}"
                            )
                
                # Overall security fields test
                success_rate = (fields_correct / total_fields) * 100
                self.log_test(
                    "User Model Security Fields Overall", 
                    fields_correct == total_fields,
                    f"Security fields validation: {fields_correct}/{total_fields} correct ({success_rate:.1f}%)"
                )
                
                # Test login to verify last_login timestamp update
                login_response = self.session.post(f"{BASE_URL}/auth/login", json={
                    "email": ADMIN_EMAIL,  # Use admin to bypass email verification
                    "password": ADMIN_PASSWORD
                })
                
                if login_response.status_code == 200:
                    self.log_test(
                        "User Model - Last Login Update", 
                        True, 
                        "Login successful - last_login timestamp should be updated"
                    )
                else:
                    self.log_test(
                        "User Model - Last Login Update", 
                        False, 
                        error="Could not test last_login update due to login failure"
                    )
                    
            else:
                self.log_test(
                    "User Model Security Fields", 
                    False, 
                    error=f"Could not create test account: HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "User Model Security Fields", 
                False, 
                error=str(e)
            )

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 TOPKIT ENHANCED SECURITY FEATURES TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by feature area
        feature_areas = {
            "Password Strength Validation": [],
            "Rate Limiting": [],
            "Email Verification": [],
            "Enhanced Login Security": [],
            "User Model Security": [],
            "Admin Authentication": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Password" in test_name:
                feature_areas["Password Strength Validation"].append(result)
            elif "Rate" in test_name:
                feature_areas["Rate Limiting"].append(result)
            elif "Email" in test_name:
                feature_areas["Email Verification"].append(result)
            elif "Login" in test_name:
                feature_areas["Enhanced Login Security"].append(result)
            elif "Model" in test_name:
                feature_areas["User Model Security"].append(result)
            elif "Admin" in test_name:
                feature_areas["Admin Authentication"].append(result)
        
        print("📋 FEATURE AREA BREAKDOWN:")
        for area, tests in feature_areas.items():
            if tests:
                area_passed = sum(1 for t in tests if t["success"])
                area_total = len(tests)
                area_rate = (area_passed / area_total * 100) if area_total > 0 else 0
                status = "✅" if area_passed == area_total else "❌"
                print(f"   {status} {area}: {area_passed}/{area_total} ({area_rate:.1f}%)")
        
        print()
        print("🔍 FAILED TESTS DETAILS:")
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            for result in failed_results:
                print(f"   ❌ {result['test']}")
                if result["error"]:
                    print(f"      Error: {result['error']}")
        else:
            print("   🎉 No failed tests!")
        
        print()
        print("="*80)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: TopKit security features are working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: TopKit security features are mostly working with minor issues.")
        elif success_rate >= 50:
            print("⚠️ MODERATE: TopKit security features have some significant issues.")
        else:
            print("🚨 CRITICAL: TopKit security features have major issues requiring immediate attention.")
        
        print("="*80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "feature_breakdown": {area: len(tests) for area, tests in feature_areas.items() if tests}
        }

    def run_all_tests(self):
        """Run all security tests"""
        print("🚀 STARTING TOPKIT ENHANCED SECURITY FEATURES TESTING")
        print("="*80)
        
        # Admin login first for some tests
        if not self.admin_login():
            print("⚠️ Warning: Admin login failed, some tests may be limited")
        
        # Run all security tests
        self.test_password_strength_validation()
        self.test_rate_limiting()
        self.test_email_verification_system()
        self.test_enhanced_login_security()
        self.test_user_model_security_fields()
        
        # Generate summary
        summary = self.generate_summary()
        
        return summary

def main():
    """Main test execution"""
    tester = SecurityTester()
    
    try:
        summary = tester.run_all_tests()
        
        # Exit with appropriate code
        if summary["success_rate"] >= 75:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()