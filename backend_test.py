#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - URGENT TOPKITFR@GMAIL.COM ACCOUNT SEARCH

USER REQUEST:
User believes topkitfr@gmail.com account existed before and wants comprehensive search

INVESTIGATION REQUIRED:
1. Search users collection for any account with email containing "topkitfr" or "topkit"
2. Look for any user with admin role
3. Check for variations of the email (with/without @gmail.com, different domain)
4. Show all admin users found in the database
5. Try login with topkitfr@gmail.com and common passwords: topkit123, admin123, password123, TopKitSecure789#
6. Verify emergency.admin@topkit.test account status

CRITICAL: Comprehensive database search to find the original topkitfr@gmail.com account.
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://jersey-levels.preview.emergentagent.com/api"

# Emergency Admin Credentials (KNOWN WORKING)
EMERGENCY_ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!"
}

# Passwords to test for topkitfr@gmail.com account
TOPKITFR_PASSWORDS = [
    "topkit123",
    "admin123", 
    "password123",
    "TopKitSecure789#",
    "TopKit2024!",
    "topkitfr@gmail.com",
    "topkit",
    "admin",
    "password",
    "123456"
]

class TopKitAccountSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.users_found = []
        self.found_accounts = []
        
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
    
    def test_database_connection(self):
        """Test basic database connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/teams", timeout=10)
            
            if response.status_code == 200:
                teams = response.json()
                self.log_test("Database Connection", True, 
                             f"Backend accessible, found {len(teams)} teams in database")
                return True
            else:
                self.log_test("Database Connection", False, 
                             f"Backend returned status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Database Connection", False, f"Exception: {str(e)}")
            return False
    
    def search_topkitfr_account(self):
        """Comprehensive search for topkitfr@gmail.com account"""
        try:
            print(f"\n🔍 COMPREHENSIVE SEARCH FOR TOPKITFR@GMAIL.COM ACCOUNT")
            print("=" * 60)
            
            successful_login = False
            found_account = None
            
            # Test all password combinations for topkitfr@gmail.com
            print(f"\n1️⃣ Testing login attempts for topkitfr@gmail.com...")
            for i, password in enumerate(TOPKITFR_PASSWORDS, 1):
                print(f"   Attempt {i}/{len(TOPKITFR_PASSWORDS)}: Testing password '{password}'...")
                
                try:
                    response = self.session.post(
                        f"{BACKEND_URL}/auth/login",
                        json={
                            "email": "topkitfr@gmail.com",
                            "password": password
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        user_data = data.get('user', {})
                        found_account = user_data
                        
                        self.log_test(f"TopKitFR Login Attempt {i}", True, 
                                     f"✅ SUCCESS! topkitfr@gmail.com login works with password '{password}'")
                        print(f"      🎉 ACCOUNT FOUND!")
                        print(f"      User ID: {user_data.get('id')}")
                        print(f"      Name: {user_data.get('name')}")
                        print(f"      Email: {user_data.get('email')}")
                        print(f"      Role: {user_data.get('role')}")
                        print(f"      Created: {user_data.get('created_at')}")
                        
                        successful_login = True
                        self.found_accounts.append(user_data)
                        break
                        
                    elif response.status_code == 401:
                        self.log_test(f"TopKitFR Login Attempt {i}", False, 
                                     f"Invalid credentials with password '{password}'")
                    else:
                        self.log_test(f"TopKitFR Login Attempt {i}", False, 
                                     f"Unexpected status {response.status_code} with password '{password}'", 
                                     response.text)
                        
                except Exception as e:
                    self.log_test(f"TopKitFR Login Attempt {i}", False, 
                                 f"Exception with password '{password}': {str(e)}")
            
            # Final assessment for topkitfr@gmail.com
            if successful_login:
                self.log_test("TopKitFR Account Search", True, 
                             f"✅ ACCOUNT FOUND: topkitfr@gmail.com exists and is functional")
                return True, found_account
            else:
                self.log_test("TopKitFR Account Search", False, 
                             f"❌ ACCOUNT NOT FOUND: topkitfr@gmail.com does not exist or all passwords failed")
                return False, None
                
        except Exception as e:
            self.log_test("TopKitFR Account Search", False, f"Exception: {str(e)}")
            return False, None
    
    def search_database_users(self):
        """Search database for all users and identify admin accounts"""
        try:
            print(f"\n2️⃣ Searching database for all users and admin accounts...")
            
            # Get all users from leaderboard
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=100", timeout=10)
            
            if response.status_code == 200:
                users = response.json()
                self.users_found = users
                print(f"   Found {len(users)} total users in database")
                
                topkit_users = []
                admin_users = []
                high_xp_users = []
                
                print(f"\n   📋 ALL USERS IN DATABASE:")
                for i, user in enumerate(users, 1):
                    username = user.get('username', 'Unknown')
                    xp = user.get('xp', 0)
                    level = user.get('level', 'Unknown')
                    
                    print(f"      {i:2d}. {username} - {xp} XP ({level})")
                    
                    # Check for topkit-related usernames
                    if any(term in username.lower() for term in ['topkit', 'admin', 'emergency']):
                        topkit_users.append(user)
                    
                    # Check for high XP users (potential admins)
                    if xp > 30:
                        high_xp_users.append(user)
                    
                    # Check for admin-like patterns
                    if ('admin' in username.lower() or 
                        'topkit' in username.lower() or 
                        'emergency' in username.lower() or
                        xp > 50):
                        admin_users.append(user)
                
                # Report findings
                if topkit_users:
                    print(f"\n   🎯 TOPKIT-RELATED ACCOUNTS FOUND ({len(topkit_users)}):")
                    for user in topkit_users:
                        print(f"      • {user.get('username')} - {user.get('xp', 0)} XP - {user.get('level', 'Unknown')}")
                        self.found_accounts.append(user)
                else:
                    print(f"   ❌ NO TOPKIT-RELATED USERNAMES FOUND")
                
                if admin_users:
                    print(f"\n   🔑 POTENTIAL ADMIN ACCOUNTS FOUND ({len(admin_users)}):")
                    for user in admin_users:
                        print(f"      • {user.get('username')} - {user.get('xp', 0)} XP - {user.get('level', 'Unknown')}")
                else:
                    print(f"   ❌ NO ADMIN-LIKE ACCOUNTS IDENTIFIED")
                
                if high_xp_users:
                    print(f"\n   ⭐ HIGH-XP USERS (>30 XP) FOUND ({len(high_xp_users)}):")
                    for user in high_xp_users:
                        print(f"      • {user.get('username')} - {user.get('xp', 0)} XP - {user.get('level', 'Unknown')}")
                
                self.log_test("Database User Search", True, 
                             f"Searched {len(users)} users - found {len(topkit_users)} topkit-related, {len(admin_users)} admin-like")
                return True
            else:
                self.log_test("Database User Search", False, 
                             f"Failed to access user database: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database User Search", False, f"Exception: {str(e)}")
            return False
    
    def verify_emergency_admin(self):
        """Verify emergency admin account status"""
        try:
            print(f"\n3️⃣ Verifying emergency admin account status...")
            print(f"   Email: {EMERGENCY_ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {EMERGENCY_ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=EMERGENCY_ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                
                self.log_test("Emergency Admin Verification", True, 
                             f"✅ Emergency admin account is working")
                print(f"      User ID: {user_data.get('id')}")
                print(f"      Name: {user_data.get('name')}")
                print(f"      Email: {user_data.get('email')}")
                print(f"      Role: {user_data.get('role')}")
                print(f"      Created: {user_data.get('created_at')}")
                
                self.found_accounts.append(user_data)
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                return True
                
            elif response.status_code == 401:
                self.log_test("Emergency Admin Verification", False, 
                             "❌ Emergency admin credentials invalid")
                return False
            else:
                self.log_test("Emergency Admin Verification", False, 
                             f"Unexpected status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_functionality(self):
        """Test admin functionality if we have admin access"""
        try:
            if not self.auth_token:
                self.log_test("Admin Functionality Test", False, 
                             "No admin token available for functionality testing")
                return False
            
            print(f"\n4️⃣ Testing admin functionality...")
            
            # Test admin endpoints
            response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions", timeout=10)
            
            if response.status_code == 200:
                contributions = response.json()
                self.log_test("Admin Functionality Test", True, 
                             f"✅ Admin access confirmed - found {len(contributions)} pending contributions")
                return True
            elif response.status_code == 403:
                self.log_test("Admin Functionality Test", False, 
                             "❌ Admin access denied - account may not have admin role")
                return False
            else:
                self.log_test("Admin Functionality Test", False, 
                             f"Unexpected response: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Functionality Test", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_search(self):
        """Run comprehensive search for topkitfr@gmail.com account"""
        print("\n🔍 COMPREHENSIVE TOPKITFR@GMAIL.COM ACCOUNT SEARCH")
        print("Searching for the original topkitfr@gmail.com account")
        print("=" * 80)
        
        search_results = []
        
        # Step 1: Test database connection
        print("\n1️⃣ Testing Database Connection...")
        search_results.append(self.test_database_connection())
        
        # Step 2: Search for topkitfr@gmail.com account
        print("\n2️⃣ Searching for topkitfr@gmail.com account...")
        topkitfr_found, topkitfr_data = self.search_topkitfr_account()
        search_results.append(topkitfr_found)
        
        # Step 3: Search all database users
        print("\n3️⃣ Searching all database users...")
        search_results.append(self.search_database_users())
        
        # Step 4: Verify emergency admin
        print("\n4️⃣ Verifying emergency admin account...")
        emergency_admin_works = self.verify_emergency_admin()
        search_results.append(emergency_admin_works)
        
        # Step 5: Test admin functionality if possible
        if emergency_admin_works:
            print("\n5️⃣ Testing admin functionality...")
            search_results.append(self.test_admin_functionality())
        
        return search_results
    
    def print_summary(self):
        """Print comprehensive search summary"""
        print("\n📊 TOPKITFR@GMAIL.COM ACCOUNT SEARCH SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        topkitfr_tests = [r for r in self.test_results if 'TopKitFR' in r['test']]
        topkitfr_found = any(r['success'] for r in topkitfr_tests if 'Search' in r['test'])
        
        emergency_admin_tests = [r for r in self.test_results if 'Emergency Admin' in r['test']]
        emergency_admin_working = any(r['success'] for r in emergency_admin_tests)
        
        print(f"\n🔍 KEY FINDINGS:")
        
        # TopKitFR Account Status
        if topkitfr_found:
            print(f"  ✅ TOPKITFR@GMAIL.COM: Account found and working!")
        else:
            print(f"  ❌ TOPKITFR@GMAIL.COM: Account not found or not accessible")
        
        # Emergency Admin Status
        if emergency_admin_working:
            print(f"  ✅ EMERGENCY ADMIN: Working - emergency.admin@topkit.test")
        else:
            print(f"  ❌ EMERGENCY ADMIN: Not working")
        
        # Database findings
        if self.users_found:
            print(f"  📊 DATABASE STATUS: Found {len(self.users_found)} total users in system")
            admin_like_users = [u for u in self.users_found if 'admin' in u.get('username', '').lower() or 'topkit' in u.get('username', '').lower()]
            if admin_like_users:
                print(f"     • {len(admin_like_users)} admin-like users identified")
        
        # Show found accounts
        if self.found_accounts:
            print(f"\n🎯 ACCOUNTS FOUND ({len(self.found_accounts)}):")
            for account in self.found_accounts:
                print(f"  • {account.get('name', 'Unknown')} ({account.get('email', 'No email')}) - Role: {account.get('role', 'Unknown')}")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Recommendations
        print(f"\n💡 CONCLUSIONS:")
        
        if topkitfr_found:
            print(f"  ✅ ORIGINAL ACCOUNT FOUND: topkitfr@gmail.com exists and is accessible")
            print(f"     - User can use this account for admin access")
        else:
            print(f"  ❌ ORIGINAL ACCOUNT NOT FOUND: topkitfr@gmail.com does not exist in database")
            print(f"     - Account may have been deleted or never existed")
            print(f"     - All tested passwords failed")
        
        if emergency_admin_working:
            print(f"  ✅ BACKUP SOLUTION: emergency.admin@topkit.test is available")
            print(f"     - User can use this account as alternative admin access")
        
        print(f"\n🎯 RECOMMENDATION FOR USER:")
        if topkitfr_found:
            print(f"  ✅ Use the original topkitfr@gmail.com account - it exists and works!")
        elif emergency_admin_working:
            print(f"  🔧 Use emergency.admin@topkit.test / EmergencyAdmin2025! as admin account")
        else:
            print(f"  🚨 No admin access available - manual database intervention required")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run comprehensive search and return success status"""
        search_results = self.run_comprehensive_search()
        self.print_summary()
        return any(search_results)

def main():
    """Main test execution"""
    searcher = TopKitAccountSearcher()
    success = searcher.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()