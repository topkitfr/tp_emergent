#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - URGENT EMERGENCY ADMIN ACCESS INVESTIGATION

URGENT USER ISSUE REPORT:
User reports that topkitfr@gmail.com login no longer works, account may be corrupted
Emergency admin access needed for gamification system testing

INVESTIGATION REQUIRED:
1. Test Emergency Admin Login (emergency.admin@topkit.test / EmergencyAdmin2025!)
2. Investigate Corrupted topkitfr@gmail.com Account
3. Database User Analysis - List all users and their roles
4. Admin Functionality Verification with emergency admin
5. Account Recovery Options

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

# Emergency Admin Credentials (PRIMARY TEST TARGET)
EMERGENCY_ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!"
}

# Corrupted Admin Credentials (INVESTIGATION TARGET)
CORRUPTED_ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

# Alternative passwords to test for corrupted account
ALTERNATIVE_PASSWORDS = [
    "TopKitSecure789#",
    "topkit123",
    "admin123",
    "password123",
    "TopKit2024!",
    "topkitfr@gmail.com"
]

class EmergencyAdminTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.emergency_admin_token = None
        self.test_results = []
        self.users_found = []
        self.admin_user_data = None
        
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
    
    def test_emergency_admin_login(self):
        """Test Emergency Admin Login - PRIMARY OBJECTIVE"""
        try:
            print(f"\n🚨 PRIORITY: Testing Emergency Admin Login...")
            print(f"   Email: {EMERGENCY_ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {EMERGENCY_ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=EMERGENCY_ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.emergency_admin_token = data.get("token")
                user_data = data.get('user', {})
                self.admin_user_data = user_data
                
                self.log_test("Emergency Admin Login", True, 
                             f"✅ SUCCESS! Emergency admin login working")
                print(f"      User ID: {user_data.get('id')}")
                print(f"      Name: {user_data.get('name')}")
                print(f"      Email: {user_data.get('email')}")
                print(f"      Role: {user_data.get('role')}")
                
                # Set auth token for subsequent requests
                self.auth_token = self.emergency_admin_token
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                return True
                
            elif response.status_code == 401:
                self.log_test("Emergency Admin Login", False, 
                             "❌ CRITICAL: Emergency admin credentials invalid")
                return False
            else:
                self.log_test("Emergency Admin Login", False, 
                             f"Unexpected status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Login", False, f"Exception: {str(e)}")
            return False
    
    def investigate_corrupted_admin_account(self):
        """Investigate the corrupted topkitfr@gmail.com account"""
        try:
            print(f"\n🔍 Investigating corrupted admin account: {CORRUPTED_ADMIN_CREDENTIALS['email']}")
            
            successful_login = False
            
            for i, password in enumerate(ALTERNATIVE_PASSWORDS, 1):
                print(f"   Attempt {i}: Testing password '{password}'...")
                
                try:
                    response = self.session.post(
                        f"{BACKEND_URL}/auth/login",
                        json={
                            "email": CORRUPTED_ADMIN_CREDENTIALS['email'],
                            "password": password
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        user_data = data.get('user', {})
                        
                        self.log_test(f"Corrupted Admin Login Attempt {i}", True, 
                                     f"✅ SUCCESS! Corrupted admin login works with password '{password}'")
                        print(f"      User ID: {user_data.get('id')}")
                        print(f"      Name: {user_data.get('name')}")
                        print(f"      Email: {user_data.get('email')}")
                        print(f"      Role: {user_data.get('role')}")
                        
                        successful_login = True
                        break
                        
                    elif response.status_code == 401:
                        self.log_test(f"Corrupted Admin Login Attempt {i}", False, 
                                     f"Invalid credentials with password '{password}'")
                    else:
                        self.log_test(f"Corrupted Admin Login Attempt {i}", False, 
                                     f"Unexpected status {response.status_code} with password '{password}'", 
                                     response.text)
                        
                except Exception as e:
                    self.log_test(f"Corrupted Admin Login Attempt {i}", False, 
                                 f"Exception with password '{password}': {str(e)}")
            
            if not successful_login:
                self.log_test("Corrupted Admin Account Investigation", False, 
                             f"❌ CONFIRMED: topkitfr@gmail.com account is completely broken - no working passwords found")
                return False
            else:
                self.log_test("Corrupted Admin Account Investigation", True, 
                             f"✅ RESOLVED: topkitfr@gmail.com account is working with correct password")
                return True
                
        except Exception as e:
            self.log_test("Corrupted Admin Account Investigation", False, f"Exception: {str(e)}")
            return False
    
    def analyze_database_users(self):
        """Analyze all users in database and their roles"""
        try:
            print(f"\n🔍 Analyzing database users and roles...")
            
            # Try to access leaderboard which shows users
            response = self.session.get(
                f"{BACKEND_URL}/leaderboard",
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json()
                self.users_found = users
                
                print(f"   Found {len(users)} users in database:")
                admin_users = []
                regular_users = []
                
                for i, user in enumerate(users, 1):
                    username = user.get('username', 'Unknown')
                    xp = user.get('xp', 0)
                    level = user.get('level', 'Unknown')
                    
                    # Check if this looks like an admin user
                    if ('admin' in username.lower() or 
                        'topkit' in username.lower() or 
                        'emergency' in username.lower()):
                        admin_users.append(user)
                        print(f"      🔑 ADMIN: {i}. {username} - {xp} XP ({level})")
                    else:
                        regular_users.append(user)
                        print(f"      👤 USER:  {i}. {username} - {xp} XP ({level})")
                
                self.log_test("Database User Analysis", True, 
                             f"Successfully analyzed {len(users)} users - {len(admin_users)} admin-like, {len(regular_users)} regular")
                
                # Report findings
                if admin_users:
                    print(f"\n   🔑 ADMIN ACCOUNTS FOUND ({len(admin_users)}):")
                    for admin in admin_users:
                        print(f"      • {admin.get('username', 'Unknown')} - {admin.get('xp', 0)} XP")
                else:
                    print(f"\n   ⚠️  NO ADMIN ACCOUNTS IDENTIFIED in leaderboard")
                
                return True
            else:
                self.log_test("Database User Analysis", False, 
                             f"Failed to access leaderboard: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Database User Analysis", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_functionality(self):
        """Test admin functionality with emergency admin"""
        try:
            if not self.auth_token:
                self.log_test("Admin Functionality Test", False, 
                             "No admin token available for functionality testing")
                return False
            
            print(f"\n🔍 Testing admin functionality...")
            
            # Test 1: Admin pending contributions endpoint
            print("   Testing GET /api/admin/pending-contributions...")
            response = self.session.get(
                f"{BACKEND_URL}/admin/pending-contributions",
                timeout=10
            )
            
            if response.status_code == 200:
                contributions = response.json()
                self.log_test("Admin Pending Contributions", True, 
                             f"✅ Admin access confirmed - found {len(contributions)} pending contributions")
                
                # Test 2: Leaderboard access
                print("   Testing GET /api/leaderboard...")
                leaderboard_response = self.session.get(
                    f"{BACKEND_URL}/leaderboard",
                    timeout=10
                )
                
                if leaderboard_response.status_code == 200:
                    leaderboard = leaderboard_response.json()
                    self.log_test("Admin Leaderboard Access", True, 
                                 f"✅ Leaderboard accessible - {len(leaderboard)} users")
                    
                    # Test 3: Check if we can access user gamification data
                    if self.admin_user_data and self.admin_user_data.get('id'):
                        print(f"   Testing GET /api/users/{self.admin_user_data['id']}/gamification...")
                        gamification_response = self.session.get(
                            f"{BACKEND_URL}/users/{self.admin_user_data['id']}/gamification",
                            timeout=10
                        )
                        
                        if gamification_response.status_code == 200:
                            gamification_data = gamification_response.json()
                            self.log_test("Admin Gamification Data", True, 
                                         f"✅ Gamification data accessible - XP: {gamification_data.get('xp', 0)}, Level: {gamification_data.get('level', 'Unknown')}")
                        else:
                            self.log_test("Admin Gamification Data", False, 
                                         f"Failed to access gamification data: {gamification_response.status_code}")
                    
                    return True
                else:
                    self.log_test("Admin Leaderboard Access", False, 
                                 f"Failed to access leaderboard: {leaderboard_response.status_code}")
                    return False
                    
            elif response.status_code == 403:
                self.log_test("Admin Functionality Test", False, 
                             "❌ CRITICAL: Admin access denied - emergency admin may not have admin role")
                return False
            else:
                self.log_test("Admin Functionality Test", False, 
                             f"Unexpected response: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Functionality Test", False, f"Exception: {str(e)}")
            return False
    
    def create_emergency_admin_if_needed(self):
        """Create emergency admin account if it doesn't exist"""
        try:
            print(f"\n🔧 Checking if emergency admin account needs to be created...")
            
            # First try to register the emergency admin
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json={
                    "name": "Emergency Admin",
                    "email": EMERGENCY_ADMIN_CREDENTIALS['email'],
                    "password": EMERGENCY_ADMIN_CREDENTIALS['password']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                
                self.log_test("Emergency Admin Creation", True, 
                             f"✅ Emergency admin account created: {user_data.get('email')}")
                
                print(f"   ⚠️  IMPORTANT: Emergency admin account created but role is 'user'")
                print(f"   🔧 MANUAL ACTION REQUIRED: Set role='admin' in database for user ID: {user_data.get('id')}")
                print(f"   📧 Email: {EMERGENCY_ADMIN_CREDENTIALS['email']}")
                print(f"   🔑 Password: {EMERGENCY_ADMIN_CREDENTIALS['password']}")
                
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                self.log_test("Emergency Admin Creation", True, 
                             f"✅ Emergency admin account already exists")
                return True
            else:
                self.log_test("Emergency Admin Creation", False, 
                             f"Failed to create emergency admin: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Creation", False, f"Exception: {str(e)}")
            return False
    
    def run_emergency_admin_investigation(self):
        """Run comprehensive emergency admin investigation"""
        print("\n🚨 URGENT: Emergency Admin Access Investigation")
        print("Testing emergency admin access for gamification system")
        print("=" * 80)
        
        investigation_results = []
        
        # Step 1: Test database connection
        print("\n1️⃣ Testing Database Connection...")
        investigation_results.append(self.test_database_connection())
        
        # Step 2: Test emergency admin login
        print("\n2️⃣ Testing Emergency Admin Login...")
        emergency_admin_works = self.test_emergency_admin_login()
        investigation_results.append(emergency_admin_works)
        
        # Step 3: If emergency admin doesn't work, try to create it
        if not emergency_admin_works:
            print("\n3️⃣ Creating Emergency Admin Account...")
            investigation_results.append(self.create_emergency_admin_if_needed())
            
            # Try login again after creation
            print("\n3️⃣b Re-testing Emergency Admin Login...")
            investigation_results.append(self.test_emergency_admin_login())
        
        # Step 4: Investigate corrupted admin account
        print("\n4️⃣ Investigating Corrupted Admin Account...")
        investigation_results.append(self.investigate_corrupted_admin_account())
        
        # Step 5: Analyze database users
        print("\n5️⃣ Analyzing Database Users...")
        investigation_results.append(self.analyze_database_users())
        
        # Step 6: Test admin functionality
        print("\n6️⃣ Testing Admin Functionality...")
        investigation_results.append(self.test_admin_functionality())
        
        return investigation_results
    
    def run_all_tests(self):
        """Run comprehensive emergency admin investigation"""
        print("🚨 URGENT: TopKit Emergency Admin Access Investigation")
        print("Testing emergency admin access and investigating corrupted account")
        print("=" * 80)
        
        # Run investigation
        investigation_results = self.run_emergency_admin_investigation()
        
        # Summary
        self.print_summary()
        
        return any(investigation_results)
    
    def print_summary(self):
        """Print comprehensive investigation summary"""
        print("\n📊 EMERGENCY ADMIN INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical findings
        emergency_admin_tests = [r for r in self.test_results if 'Emergency Admin' in r['test']]
        emergency_admin_working = any(r['success'] for r in emergency_admin_tests if 'Login' in r['test'])
        
        corrupted_admin_tests = [r for r in self.test_results if 'Corrupted Admin' in r['test']]
        corrupted_admin_working = any(r['success'] for r in corrupted_admin_tests)
        
        admin_functionality_tests = [r for r in self.test_results if 'Admin Functionality' in r['test'] or 'Admin Pending' in r['test']]
        admin_functionality_working = any(r['success'] for r in admin_functionality_tests)
        
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        # Emergency Admin Status
        if emergency_admin_working:
            print(f"  ✅ EMERGENCY ADMIN: Working - emergency.admin@topkit.test / EmergencyAdmin2025!")
            if self.admin_user_data:
                print(f"     • User ID: {self.admin_user_data.get('id')}")
                print(f"     • Name: {self.admin_user_data.get('name')}")
                print(f"     • Role: {self.admin_user_data.get('role')}")
        else:
            print(f"  ❌ EMERGENCY ADMIN: Not working - needs creation or role upgrade")
        
        # Corrupted Admin Status
        if corrupted_admin_working:
            print(f"  ✅ CORRUPTED ADMIN: Actually working - topkitfr@gmail.com is functional")
        else:
            print(f"  ❌ CORRUPTED ADMIN: Confirmed broken - topkitfr@gmail.com account is corrupted")
        
        # Admin Functionality Status
        if admin_functionality_working:
            print(f"  ✅ ADMIN FUNCTIONALITY: Working - gamification endpoints accessible")
        else:
            print(f"  ❌ ADMIN FUNCTIONALITY: Not working - admin role may be missing")
        
        # Database findings
        if self.users_found:
            print(f"  📊 DATABASE STATUS: Found {len(self.users_found)} users in system")
            admin_like_users = [u for u in self.users_found if 'admin' in u.get('username', '').lower() or 'topkit' in u.get('username', '').lower()]
            if admin_like_users:
                print(f"     • {len(admin_like_users)} admin-like users identified")
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
        
        if emergency_admin_working and admin_functionality_working:
            print(f"  ✅ READY FOR TESTING: Use emergency.admin@topkit.test / EmergencyAdmin2025! for gamification testing")
        elif emergency_admin_working and not admin_functionality_working:
            print(f"  🔧 ROLE UPGRADE NEEDED: Emergency admin exists but needs role='admin' in database")
            if self.admin_user_data:
                print(f"     - Update user ID {self.admin_user_data.get('id')} role to 'admin'")
        else:
            print(f"  🚨 URGENT: Emergency admin access not available")
            print(f"     - Create emergency.admin@topkit.test account")
            print(f"     - Set role='admin' in database")
        
        if not corrupted_admin_working:
            print(f"  🔍 CORRUPTED ACCOUNT: topkitfr@gmail.com needs investigation")
            print(f"     - Check if user exists in database")
            print(f"     - Verify password_hash field integrity")
            print(f"     - Compare with working account structure")
        
        print(f"\n🎯 IMMEDIATE ACTION FOR USER:")
        if emergency_admin_working and admin_functionality_working:
            print(f"  ✅ Use emergency.admin@topkit.test / EmergencyAdmin2025! for gamification testing")
        else:
            print(f"  🔧 Manual database update required to set admin role")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = EmergencyAdminTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()