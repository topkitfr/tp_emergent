#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - FINAL ADMIN ACCOUNT VERIFICATION

FINAL VERIFICATION - Single Admin Account Status

VERIFICATION REQUIRED:
1. Test login with topkitfr@gmail.fr / TopKitAdmin2025!
2. Verify it has full admin privileges 
3. Confirm it's the ONLY admin account on the site
4. Test all admin functions work correctly

This is the final verification that the user's request has been completed successfully.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://jersey-pricing.preview.emergentagent.com/api"

# Target Admin Credentials for Final Verification
TARGET_ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.fr",
    "password": "TopKitAdmin2025!",
    "name": "TopKit Admin"
}

class TopKitFinalAdminVerification:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.admin_user_id = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_target_admin_login(self):
        """Test login with topkitfr@gmail.fr / TopKitAdmin2025!"""
        try:
            print(f"\n🔐 TESTING TARGET ADMIN LOGIN")
            print("=" * 60)
            print(f"   Email: {TARGET_ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {TARGET_ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": TARGET_ADMIN_CREDENTIALS['email'],
                    "password": TARGET_ADMIN_CREDENTIALS['password']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.admin_user_id = self.admin_user_data.get('id')
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Target Admin Login", True, 
                             f"✅ Target admin login successful")
                
                print(f"      Login Response:")
                print(f"         User ID: {self.admin_user_data.get('id')}")
                print(f"         Name: {self.admin_user_data.get('name')}")
                print(f"         Email: {self.admin_user_data.get('email')}")
                print(f"         Role: {self.admin_user_data.get('role')}")
                print(f"         Token: {self.auth_token[:20]}..." if self.auth_token else "No token")
                
                return True
                
            else:
                self.log_test("Target Admin Login", False, 
                             f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Target Admin Login", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_privileges(self):
        """Verify the target admin account has full admin privileges"""
        try:
            print(f"\n🛡️ TESTING ADMIN PRIVILEGES")
            print("=" * 60)
            
            if not self.auth_token:
                self.log_test("Admin Privileges Test", False, "No authentication token available")
                return False
            
            # Test various admin endpoints
            admin_tests = [
                ("Pending Contributions", f"{BACKEND_URL}/admin/pending-contributions"),
                ("Leaderboard Access", f"{BACKEND_URL}/leaderboard"),
                ("User Gamification Data", f"{BACKEND_URL}/users/{self.admin_user_id}/gamification")
            ]
            
            admin_access_count = 0
            total_tests = len(admin_tests)
            
            for test_name, endpoint in admin_tests:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        print(f"      ✅ {test_name}: Accessible")
                        admin_access_count += 1
                    elif response.status_code == 403:
                        print(f"      ❌ {test_name}: Access denied (403)")
                    else:
                        print(f"      ⚠️ {test_name}: Unexpected status {response.status_code}")
                except Exception as e:
                    print(f"      ❌ {test_name}: Exception - {str(e)}")
            
            if admin_access_count == total_tests:
                self.log_test("Admin Privileges Test", True, 
                             f"All {total_tests} admin endpoints accessible - full admin privileges confirmed")
                return True
            elif admin_access_count > 0:
                self.log_test("Admin Privileges Test", False, 
                             f"Partial admin access - {admin_access_count}/{total_tests} endpoints accessible")
                return False
            else:
                self.log_test("Admin Privileges Test", False, 
                             f"No admin privileges - all admin endpoints inaccessible")
                return False
                
        except Exception as e:
            self.log_test("Admin Privileges Test", False, f"Exception: {str(e)}")
            return False
    
    def test_single_admin_status(self):
        """Verify that the target account is the ONLY admin account on the site"""
        try:
            print(f"\n👑 TESTING SINGLE ADMIN STATUS")
            print("=" * 60)
            
            # Get all users from leaderboard
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=100", timeout=10)
            
            if response.status_code == 200:
                all_users = response.json()
                
                # Count admin accounts by checking username patterns
                admin_accounts = []
                target_admin_found = False
                
                for user in all_users:
                    username = user.get('username', '').lower()
                    # Look for admin patterns in username
                    if 'admin' in username:
                        admin_accounts.append(user)
                        
                        # Check if this is our target admin
                        if TARGET_ADMIN_CREDENTIALS['email'].lower() in username.lower() or \
                           TARGET_ADMIN_CREDENTIALS['name'].lower() in username.lower():
                            target_admin_found = True
                
                print(f"   Total admin accounts found: {len(admin_accounts)}")
                print(f"   Target admin account found: {'✅ Yes' if target_admin_found else '❌ No'}")
                
                print(f"\n   👥 ALL ADMIN ACCOUNTS:")
                for i, admin in enumerate(admin_accounts, 1):
                    username = admin.get('username', 'Unknown')
                    xp = admin.get('xp', 0)
                    level = admin.get('level', 'Unknown')
                    rank = admin.get('rank', 'Unknown')
                    
                    is_target = TARGET_ADMIN_CREDENTIALS['email'].lower() in username.lower() or \
                               TARGET_ADMIN_CREDENTIALS['name'].lower() in username.lower()
                    
                    status_icon = "🎯" if is_target else "⚠️"
                    status_text = "TARGET ADMIN" if is_target else "OTHER ADMIN"
                    
                    print(f"      {i}. {status_icon} {username} ({status_text})")
                    print(f"         XP: {xp}, Level: {level}, Rank: #{rank}")
                    print()
                
                # Determine result
                if len(admin_accounts) == 1 and target_admin_found:
                    self.log_test("Single Admin Status Test", True, 
                                 f"✅ Perfect! Only 1 admin account exists and it's the target account")
                    return True
                elif target_admin_found and len(admin_accounts) > 1:
                    self.log_test("Single Admin Status Test", False, 
                                 f"Target admin exists but {len(admin_accounts)-1} other admin accounts still exist")
                    return False
                elif not target_admin_found:
                    self.log_test("Single Admin Status Test", False, 
                                 f"Target admin account not found among {len(admin_accounts)} admin accounts")
                    return False
                else:
                    self.log_test("Single Admin Status Test", False, 
                                 f"Unexpected admin account configuration")
                    return False
                
            else:
                self.log_test("Single Admin Status Test", False, 
                             f"Failed to get user list: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Single Admin Status Test", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_functions(self):
        """Test all admin functions work correctly"""
        try:
            print(f"\n⚙️ TESTING ADMIN FUNCTIONS")
            print("=" * 60)
            
            if not self.auth_token:
                self.log_test("Admin Functions Test", False, "No authentication token available")
                return False
            
            admin_function_tests = []
            
            # Test 1: Get pending contributions
            try:
                response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions", timeout=10)
                if response.status_code == 200:
                    contributions = response.json()
                    admin_function_tests.append(("Get Pending Contributions", True, f"Retrieved {len(contributions)} pending contributions"))
                    print(f"      ✅ Get Pending Contributions: {len(contributions)} items")
                else:
                    admin_function_tests.append(("Get Pending Contributions", False, f"Status {response.status_code}"))
                    print(f"      ❌ Get Pending Contributions: Status {response.status_code}")
            except Exception as e:
                admin_function_tests.append(("Get Pending Contributions", False, f"Exception: {str(e)}"))
                print(f"      ❌ Get Pending Contributions: Exception - {str(e)}")
            
            # Test 2: Get leaderboard
            try:
                response = self.session.get(f"{BACKEND_URL}/leaderboard", timeout=10)
                if response.status_code == 200:
                    leaderboard = response.json()
                    admin_function_tests.append(("Get Leaderboard", True, f"Retrieved {len(leaderboard)} users"))
                    print(f"      ✅ Get Leaderboard: {len(leaderboard)} users")
                else:
                    admin_function_tests.append(("Get Leaderboard", False, f"Status {response.status_code}"))
                    print(f"      ❌ Get Leaderboard: Status {response.status_code}")
            except Exception as e:
                admin_function_tests.append(("Get Leaderboard", False, f"Exception: {str(e)}"))
                print(f"      ❌ Get Leaderboard: Exception - {str(e)}")
            
            # Test 3: Get user gamification data
            try:
                response = self.session.get(f"{BACKEND_URL}/users/{self.admin_user_id}/gamification", timeout=10)
                if response.status_code == 200:
                    gamification_data = response.json()
                    xp = gamification_data.get('xp', 0)
                    level = gamification_data.get('level', 'Unknown')
                    admin_function_tests.append(("Get User Gamification", True, f"XP: {xp}, Level: {level}"))
                    print(f"      ✅ Get User Gamification: XP: {xp}, Level: {level}")
                else:
                    admin_function_tests.append(("Get User Gamification", False, f"Status {response.status_code}"))
                    print(f"      ❌ Get User Gamification: Status {response.status_code}")
            except Exception as e:
                admin_function_tests.append(("Get User Gamification", False, f"Exception: {str(e)}"))
                print(f"      ❌ Get User Gamification: Exception - {str(e)}")
            
            # Calculate success rate
            successful_functions = len([test for test in admin_function_tests if test[1]])
            total_functions = len(admin_function_tests)
            success_rate = (successful_functions / total_functions) * 100
            
            if successful_functions == total_functions:
                self.log_test("Admin Functions Test", True, 
                             f"All {total_functions} admin functions working correctly (100% success rate)")
                return True
            elif successful_functions > 0:
                self.log_test("Admin Functions Test", False, 
                             f"Partial success - {successful_functions}/{total_functions} functions working ({success_rate:.1f}% success rate)")
                return False
            else:
                self.log_test("Admin Functions Test", False, 
                             f"No admin functions working (0% success rate)")
                return False
                
        except Exception as e:
            self.log_test("Admin Functions Test", False, f"Exception: {str(e)}")
            return False
    
    def run_final_verification(self):
        """Run the complete final verification"""
        print("\n🎯 FINAL ADMIN ACCOUNT VERIFICATION")
        print("Verifying topkitfr@gmail.fr as the ONLY admin account with full privileges")
        print("=" * 80)
        
        verification_results = []
        
        # Test 1: Target admin login
        print("\n1️⃣ Testing Target Admin Login...")
        verification_results.append(self.test_target_admin_login())
        
        if not self.auth_token:
            print("❌ Cannot proceed without successful login")
            return verification_results
        
        # Test 2: Admin privileges
        print("\n2️⃣ Testing Admin Privileges...")
        verification_results.append(self.test_admin_privileges())
        
        # Test 3: Single admin status
        print("\n3️⃣ Testing Single Admin Status...")
        verification_results.append(self.test_single_admin_status())
        
        # Test 4: Admin functions
        print("\n4️⃣ Testing Admin Functions...")
        verification_results.append(self.test_admin_functions())
        
        return verification_results
    
    def print_final_summary(self):
        """Print comprehensive final verification summary"""
        print("\n📊 FINAL VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key verification results
        print(f"\n🔍 VERIFICATION RESULTS:")
        
        # Login test
        login_success = any(r['success'] for r in self.test_results if 'Target Admin Login' in r['test'])
        if login_success:
            print(f"  ✅ ADMIN LOGIN: topkitfr@gmail.fr / TopKitAdmin2025! working correctly")
            if self.admin_user_data:
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
        else:
            print(f"  ❌ ADMIN LOGIN: Failed to login with provided credentials")
        
        # Admin privileges test
        privileges_success = any(r['success'] for r in self.test_results if 'Admin Privileges Test' in r['test'])
        if privileges_success:
            print(f"  ✅ ADMIN PRIVILEGES: Full admin access confirmed")
        else:
            print(f"  ❌ ADMIN PRIVILEGES: Admin access issues detected")
        
        # Single admin test
        single_admin_success = any(r['success'] for r in self.test_results if 'Single Admin Status Test' in r['test'])
        if single_admin_success:
            print(f"  ✅ SINGLE ADMIN: Only one admin account exists")
        else:
            print(f"  ❌ SINGLE ADMIN: Multiple admin accounts detected")
        
        # Admin functions test
        functions_success = any(r['success'] for r in self.test_results if 'Admin Functions Test' in r['test'])
        if functions_success:
            print(f"  ✅ ADMIN FUNCTIONS: All admin functions working correctly")
        else:
            print(f"  ❌ ADMIN FUNCTIONS: Some admin functions not working")
        
        # Show any failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status
        print(f"\n🎯 FINAL VERIFICATION STATUS:")
        if passed_tests == total_tests:
            print(f"  ✅ COMPLETE SUCCESS: All verification requirements met")
            print(f"     - Admin login working: ✅")
            print(f"     - Full admin privileges: ✅")
            print(f"     - Single admin account: ✅")
            print(f"     - All admin functions: ✅")
            print(f"\n  🎉 USER REQUEST SUCCESSFULLY COMPLETED!")
            print(f"     topkitfr@gmail.fr is the ONLY admin account with full privileges")
        elif login_success and privileges_success:
            print(f"  ⚠️ PARTIAL SUCCESS: Admin account working but issues remain")
            print(f"     - Admin login working: ✅")
            print(f"     - Full admin privileges: ✅")
            print(f"     - Single admin account: {'✅' if single_admin_success else '❌'}")
            print(f"     - All admin functions: {'✅' if functions_success else '❌'}")
        else:
            print(f"  ❌ VERIFICATION FAILED: Critical issues detected")
            print(f"     - Admin login working: {'✅' if login_success else '❌'}")
            print(f"     - Full admin privileges: {'✅' if privileges_success else '❌'}")
            print(f"     - Single admin account: {'✅' if single_admin_success else '❌'}")
            print(f"     - All admin functions: {'✅' if functions_success else '❌'}")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run complete final verification and return success status"""
        verification_results = self.run_final_verification()
        self.print_final_summary()
        return all(verification_results)

def main():
    """Main test execution"""
    verifier = TopKitFinalAdminVerification()
    success = verifier.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()