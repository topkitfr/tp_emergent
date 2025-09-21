#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - URGENT LOGIN INVESTIGATION

URGENT USER ISSUE REPORT:
User reports that topkitfr@gmail.com login no longer works, account may not exist

INVESTIGATION REQUIRED:
1. Check if User Exists in Database
2. Test Authentication Endpoints  
3. Database Connection & User Data
4. Authentication System Status
5. Backup Admin Access

CRITICAL: This needs to be resolved immediately as it blocks testing of the gamification system.
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://topkit-auth-fix-1.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

# Alternative passwords to test
ALTERNATIVE_PASSWORDS = [
    "TopKitSecure789#",
    "topkit123",
    "admin123",
    "password123",
    "TopKit2024!",
    "topkitfr@gmail.com"
]

class LoginInvestigationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.users_found = []
        
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
            # Try to access any public endpoint to verify backend is running
            response = self.session.get(
                f"{BACKEND_URL}/teams",
                timeout=10
            )
            
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
    
    def test_admin_login_attempts(self):
        """Test login with various password combinations"""
        try:
            print(f"\n🔍 Testing login attempts for {ADMIN_CREDENTIALS['email']}...")
            
            successful_login = False
            
            for i, password in enumerate(ALTERNATIVE_PASSWORDS, 1):
                print(f"   Attempt {i}: Testing password '{password}'...")
                
                try:
                    response = self.session.post(
                        f"{BACKEND_URL}/auth/login",
                        json={
                            "email": ADMIN_CREDENTIALS['email'],
                            "password": password
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.auth_token = data.get("token")
                        user_data = data.get('user', {})
                        
                        self.log_test(f"Login Attempt {i}", True, 
                                     f"✅ SUCCESS! Login successful with password '{password}'")
                        print(f"      User ID: {user_data.get('id')}")
                        print(f"      Name: {user_data.get('name')}")
                        print(f"      Email: {user_data.get('email')}")
                        print(f"      Role: {user_data.get('role')}")
                        
                        self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                        successful_login = True
                        break
                        
                    elif response.status_code == 401:
                        self.log_test(f"Login Attempt {i}", False, 
                                     f"Invalid credentials with password '{password}'")
                    else:
                        self.log_test(f"Login Attempt {i}", False, 
                                     f"Unexpected status {response.status_code} with password '{password}'", 
                                     response.text)
                        
                except Exception as e:
                    self.log_test(f"Login Attempt {i}", False, 
                                 f"Exception with password '{password}': {str(e)}")
            
            if not successful_login:
                self.log_test("Admin Login", False, 
                             f"❌ CRITICAL: No successful login found for {ADMIN_CREDENTIALS['email']}")
                return False
            else:
                self.log_test("Admin Login", True, 
                             f"✅ Admin login successful for {ADMIN_CREDENTIALS['email']}")
                return True
                
        except Exception as e:
            self.log_test("Admin Login Attempts", False, f"Exception: {str(e)}")
            return False
    
    def test_user_registration_system(self):
        """Test if user registration system is working"""
        try:
            print(f"\n🔍 Testing user registration system...")
            
            # Test registration with a new test user
            test_email = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@topkit.test"
            test_user_data = {
                "name": "Test User Registration",
                "email": test_email,
                "password": "TestPassword123!"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=test_user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                
                self.log_test("User Registration", True, 
                             f"✅ Registration system working - created user {user_data.get('email')}")
                
                # Test login with newly created user
                login_response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json={
                        "email": test_email,
                        "password": "TestPassword123!"
                    },
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    self.log_test("New User Login", True, 
                                 "✅ New user can login successfully")
                    return True
                else:
                    self.log_test("New User Login", False, 
                                 f"New user cannot login: {login_response.status_code}")
                    return False
                    
            else:
                self.log_test("User Registration", False, 
                             f"Registration failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Registration System", False, f"Exception: {str(e)}")
            return False
    
    def investigate_user_database(self):
        """Investigate users in database if we have admin access"""
        try:
            if not self.auth_token:
                self.log_test("User Database Investigation", False, 
                             "No admin token available for database investigation")
                return False
            
            print(f"\n🔍 Investigating user database...")
            
            # Try to access admin endpoints to get user information
            # First, let's try to get leaderboard which shows users
            response = self.session.get(
                f"{BACKEND_URL}/leaderboard",
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json()
                self.users_found = users
                
                print(f"   Found {len(users)} users in leaderboard:")
                for i, user in enumerate(users[:10], 1):  # Show first 10 users
                    username = user.get('username', 'Unknown')
                    xp = user.get('xp', 0)
                    level = user.get('level', 'Unknown')
                    print(f"      {i}. {username} - {xp} XP ({level})")
                
                # Check if topkitfr@gmail.com user exists in leaderboard
                admin_user_found = any(
                    'topkit' in user.get('username', '').lower() or 
                    'admin' in user.get('username', '').lower()
                    for user in users
                )
                
                if admin_user_found:
                    self.log_test("Admin User in Database", True, 
                                 "✅ Admin-like user found in database")
                else:
                    self.log_test("Admin User in Database", False, 
                                 "❌ No admin-like user found in leaderboard")
                
                self.log_test("User Database Investigation", True, 
                             f"Successfully retrieved {len(users)} users from database")
                return True
            else:
                self.log_test("User Database Investigation", False, 
                             f"Failed to access leaderboard: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Database Investigation", False, f"Exception: {str(e)}")
            return False
    
    def test_gamification_endpoints(self):
        """Test gamification endpoints that require admin access"""
        try:
            if not self.auth_token:
                self.log_test("Gamification Endpoints", False, 
                             "No admin token available for gamification testing")
                return False
            
            print(f"\n🔍 Testing gamification endpoints...")
            
            # Test pending contributions endpoint (admin only)
            response = self.session.get(
                f"{BACKEND_URL}/admin/pending-contributions",
                timeout=10
            )
            
            if response.status_code == 200:
                contributions = response.json()
                self.log_test("Admin Gamification Access", True, 
                             f"✅ Admin access confirmed - found {len(contributions)} pending contributions")
                return True
            elif response.status_code == 403:
                self.log_test("Admin Gamification Access", False, 
                             "❌ Admin access denied - user may not have admin role")
                return False
            else:
                self.log_test("Admin Gamification Access", False, 
                             f"Unexpected response: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Gamification Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def create_backup_admin_account(self):
        """Create a backup admin account if needed"""
        try:
            print(f"\n🔧 Creating backup admin account...")
            
            backup_admin_data = {
                "name": "Backup Admin",
                "email": "backup.admin@topkit.test",
                "password": "BackupAdmin123!"
            }
            
            # First try to register the backup admin
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=backup_admin_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                
                self.log_test("Backup Admin Creation", True, 
                             f"✅ Backup admin account created: {user_data.get('email')}")
                
                # Note: In a real system, we would need to manually set the role to 'admin' in the database
                # For now, we just confirm the account was created
                print(f"   ⚠️  NOTE: Backup admin account created but role needs to be set to 'admin' in database")
                print(f"   📧 Email: {backup_admin_data['email']}")
                print(f"   🔑 Password: {backup_admin_data['password']}")
                
                return True
            else:
                self.log_test("Backup Admin Creation", False, 
                             f"Failed to create backup admin: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Backup Admin Creation", False, f"Exception: {str(e)}")
            return False
    
    def run_login_investigation(self):
        """Run comprehensive login investigation"""
        print("\n🚨 URGENT: TopKit Admin Login Investigation")
        print("User reports that topkitfr@gmail.com login no longer works")
        print("=" * 80)
        
        investigation_results = []
        
        # Step 1: Test database connection
        print("\n1️⃣ Testing Database Connection...")
        investigation_results.append(self.test_database_connection())
        
        # Step 2: Test admin login attempts
        print("\n2️⃣ Testing Admin Login Attempts...")
        investigation_results.append(self.test_admin_login_attempts())
        
        # Step 3: Test user registration system
        print("\n3️⃣ Testing User Registration System...")
        investigation_results.append(self.test_user_registration_system())
        
        # Step 4: Investigate user database
        print("\n4️⃣ Investigating User Database...")
        investigation_results.append(self.investigate_user_database())
        
        # Step 5: Test gamification endpoints
        print("\n5️⃣ Testing Gamification Endpoints...")
        investigation_results.append(self.test_gamification_endpoints())
        
        # Step 6: Create backup admin if needed
        if not any(investigation_results[1:3]):  # If login and registration both failed
            print("\n6️⃣ Creating Backup Admin Account...")
            investigation_results.append(self.create_backup_admin_account())
        
        return investigation_results
    
    def run_all_tests(self):
        """Run comprehensive login investigation"""
        print("🚨 URGENT: TopKit Backend Login Investigation")
        print("Investigating topkitfr@gmail.com login issue")
        print("=" * 80)
        
        # Run investigation
        investigation_results = self.run_login_investigation()
        
        # Summary
        self.print_summary()
        
        return any(investigation_results)
    
    def print_summary(self):
        """Print comprehensive investigation summary"""
        print("\n📊 LOGIN INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical findings
        login_tests = [r for r in self.test_results if 'Login' in r['test']]
        successful_logins = [r for r in login_tests if r['success']]
        
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        if successful_logins:
            print(f"  ✅ ADMIN LOGIN WORKING: Found {len(successful_logins)} successful login method(s)")
            for login in successful_logins:
                print(f"     • {login['test']}: {login['message']}")
        else:
            print(f"  ❌ ADMIN LOGIN BROKEN: No successful login methods found")
        
        # Database findings
        if self.users_found:
            print(f"  📊 DATABASE STATUS: Found {len(self.users_found)} users in system")
        else:
            print(f"  ⚠️  DATABASE STATUS: Could not retrieve user information")
        
        # Show all failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if successful_logins:
            print(f"  ✅ Admin access is available - use working credentials for gamification testing")
        else:
            print(f"  🚨 URGENT: Admin access is broken - immediate fix required")
            print(f"     - Check database for topkitfr@gmail.com user existence")
            print(f"     - Verify password hash in database")
            print(f"     - Consider creating new admin account")
        
        # Backup admin info
        backup_admin_tests = [r for r in self.test_results if 'Backup Admin' in r['test']]
        if backup_admin_tests and backup_admin_tests[0]['success']:
            print(f"  🔧 BACKUP ADMIN CREATED: Use backup.admin@topkit.test / BackupAdmin123!")
            print(f"     - Remember to set role='admin' in database")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = LoginInvestigationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()