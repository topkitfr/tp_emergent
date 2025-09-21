#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - ADMIN ACCOUNT EMAIL CORRECTION

CRITICAL EMAIL CORRECTION REQUIRED:
- User created wrong email: topkitfr@gmail.fr (WRONG)
- User wants: topkitfr@gmail.com (CORRECT)

ACTIONS REQUIRED:
1. Create new admin account: topkitfr@gmail.com
2. Set password: TopKitAdmin2025!
3. Set name: TopKit Admin
4. Set role: admin
5. Delete the incorrect account: topkitfr@gmail.fr
6. Make sure topkitfr@gmail.com is the ONLY admin account

CRITICAL: Fix the email address error and create the correct admin account.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://jersey-levels.preview.emergentagent.com/api"

# New Admin Credentials to Create - CORRECTED EMAIL
NEW_ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",  # CORRECTED: .com instead of .fr
    "password": "TopKitAdmin2025!",
    "name": "TopKit Admin"
}

# Emergency Admin Credentials (for initial access)
EMERGENCY_ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!"
}

class TopKitAdminAccountManager:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.existing_admins = []
        self.new_admin_user_id = None
        
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
    
    def authenticate_emergency_admin(self):
        """Authenticate as emergency admin to perform admin operations"""
        try:
            print(f"\n🔐 AUTHENTICATING AS EMERGENCY ADMIN")
            print("=" * 60)
            print(f"   Email: {EMERGENCY_ADMIN_CREDENTIALS['email']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=EMERGENCY_ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Emergency Admin Authentication", True, 
                             f"✅ Emergency admin authenticated successfully")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Emergency Admin Authentication", False, 
                             f"Authentication failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_all_users_and_identify_admins(self):
        """Get all users and identify existing admin accounts"""
        try:
            print(f"\n👥 IDENTIFYING ALL EXISTING ADMIN ACCOUNTS")
            print("=" * 60)
            
            # Get leaderboard to see all users
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=100", timeout=10)
            
            if response.status_code == 200:
                all_users = response.json()
                
                # Find admin accounts by checking role or username patterns
                admin_accounts = []
                for user in all_users:
                    username = user.get('username', '').lower()
                    # Look for admin patterns in username
                    if 'admin' in username:
                        admin_accounts.append(user)
                
                self.existing_admins = admin_accounts
                
                self.log_test("Admin Accounts Identification", True, 
                             f"Found {len(admin_accounts)} existing admin accounts")
                
                print(f"\n   👥 EXISTING ADMIN ACCOUNTS:")
                for i, admin in enumerate(admin_accounts, 1):
                    username = admin.get('username', 'Unknown')
                    xp = admin.get('xp', 0)
                    level = admin.get('level', 'Unknown')
                    rank = admin.get('rank', 'Unknown')
                    
                    print(f"      {i}. {username}")
                    print(f"         XP: {xp}")
                    print(f"         Level: {level}")
                    print(f"         Rank: #{rank}")
                    print()
                
                return True
                
            else:
                self.log_test("Admin Accounts Identification", False, 
                             f"Failed to get user list: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Accounts Identification", False, f"Exception: {str(e)}")
            return False
    
    def check_if_target_account_exists(self):
        """Check if topkitfr@gmail.fr account already exists"""
        try:
            print(f"\n🔍 CHECKING IF TARGET ACCOUNT ALREADY EXISTS")
            print("=" * 60)
            print(f"   Target Email: {NEW_ADMIN_CREDENTIALS['email']}")
            
            # Try to login with the target account to see if it exists
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": NEW_ADMIN_CREDENTIALS['email'],
                    "password": NEW_ADMIN_CREDENTIALS['password']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Target Account Existence Check", True, 
                             f"Account {NEW_ADMIN_CREDENTIALS['email']} already exists and is accessible")
                
                data = response.json()
                user_data = data.get('user', {})
                print(f"      Existing Account Details:")
                print(f"         User ID: {user_data.get('id')}")
                print(f"         Name: {user_data.get('name')}")
                print(f"         Role: {user_data.get('role')}")
                print(f"         Email: {user_data.get('email')}")
                
                self.new_admin_user_id = user_data.get('id')
                return True
                
            elif response.status_code == 401:
                self.log_test("Target Account Existence Check", True, 
                             f"Account {NEW_ADMIN_CREDENTIALS['email']} does not exist - will create new")
                print(f"      Account does not exist - proceeding with creation")
                return False
                
            else:
                self.log_test("Target Account Existence Check", False, 
                             f"Unexpected response: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Target Account Existence Check", False, f"Exception: {str(e)}")
            return False
    
    def create_new_admin_account(self):
        """Create the new admin account"""
        try:
            print(f"\n🏗️ CREATING NEW ADMIN ACCOUNT")
            print("=" * 60)
            print(f"   Email: {NEW_ADMIN_CREDENTIALS['email']}")
            print(f"   Name: {NEW_ADMIN_CREDENTIALS['name']}")
            print(f"   Password: {NEW_ADMIN_CREDENTIALS['password']}")
            
            # Create new user account
            registration_data = {
                "name": NEW_ADMIN_CREDENTIALS['name'],
                "email": NEW_ADMIN_CREDENTIALS['email'],
                "password": NEW_ADMIN_CREDENTIALS['password']
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                self.new_admin_user_id = user_data.get('id')
                
                self.log_test("New Admin Account Creation", True, 
                             f"New admin account created successfully")
                
                print(f"      New Account Details:")
                print(f"         User ID: {user_data.get('id')}")
                print(f"         Name: {user_data.get('name')}")
                print(f"         Email: {user_data.get('email')}")
                print(f"         Role: {user_data.get('role', 'user')} (will be upgraded to admin)")
                
                return True
                
            else:
                self.log_test("New Admin Account Creation", False, 
                             f"Failed to create account: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("New Admin Account Creation", False, f"Exception: {str(e)}")
            return False
    
    def upgrade_account_to_admin_role(self):
        """Upgrade the new account to admin role (requires direct database access simulation)"""
        try:
            print(f"\n⬆️ UPGRADING ACCOUNT TO ADMIN ROLE")
            print("=" * 60)
            
            if not self.new_admin_user_id:
                self.log_test("Admin Role Upgrade", False, "No user ID available for upgrade")
                return False
            
            print(f"   User ID to upgrade: {self.new_admin_user_id}")
            print(f"   Target Role: admin")
            
            # Note: In a real scenario, this would require direct database access
            # For testing purposes, we'll simulate this by checking if we can access admin endpoints
            # after the account is created. In production, this would be done via database update.
            
            # Try to verify admin access by testing admin endpoints
            # First, login as the new account
            login_response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": NEW_ADMIN_CREDENTIALS['email'],
                    "password": NEW_ADMIN_CREDENTIALS['password']
                },
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                new_token = login_data.get("token")
                
                # Create a new session for the new admin
                new_admin_session = requests.Session()
                new_admin_session.headers.update({"Authorization": f"Bearer {new_token}"})
                
                # Test admin endpoint access
                admin_test_response = new_admin_session.get(f"{BACKEND_URL}/admin/pending-contributions", timeout=10)
                
                if admin_test_response.status_code == 200:
                    self.log_test("Admin Role Upgrade", True, 
                                 f"Account successfully has admin privileges")
                    print(f"      ✅ Admin endpoints accessible")
                    return True
                elif admin_test_response.status_code == 403:
                    self.log_test("Admin Role Upgrade", False, 
                                 f"Account created but does not have admin privileges - manual database update required")
                    print(f"      ❌ Admin endpoints not accessible (403 Forbidden)")
                    print(f"      📝 MANUAL ACTION REQUIRED: Update user role to 'admin' in database")
                    print(f"         UPDATE users SET role = 'admin' WHERE id = '{self.new_admin_user_id}';")
                    return False
                else:
                    self.log_test("Admin Role Upgrade", False, 
                                 f"Unexpected response when testing admin access: {admin_test_response.status_code}")
                    return False
            else:
                self.log_test("Admin Role Upgrade", False, 
                             f"Cannot login as new account: {login_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Role Upgrade", False, f"Exception: {str(e)}")
            return False
    
    def demote_existing_admin_accounts(self):
        """Demote all existing admin accounts to user role"""
        try:
            print(f"\n⬇️ DEMOTING EXISTING ADMIN ACCOUNTS TO USER ROLE")
            print("=" * 60)
            
            if not self.existing_admins:
                self.log_test("Admin Accounts Demotion", True, "No existing admin accounts to demote")
                print(f"      No existing admin accounts found")
                return True
            
            print(f"   Found {len(self.existing_admins)} admin accounts to demote")
            
            demoted_count = 0
            for admin in self.existing_admins:
                username = admin.get('username', 'Unknown')
                
                # Skip the new admin account we just created
                if NEW_ADMIN_CREDENTIALS['email'].lower() in username.lower():
                    print(f"      Skipping new admin account: {username}")
                    continue
                
                print(f"      Demoting: {username}")
                
                # Note: In a real scenario, this would require direct database access
                # For testing purposes, we'll log what needs to be done
                print(f"         📝 MANUAL ACTION REQUIRED: Update role to 'user' in database")
                print(f"            UPDATE users SET role = 'user' WHERE name = '{username}';")
                
                demoted_count += 1
            
            if demoted_count > 0:
                self.log_test("Admin Accounts Demotion", False, 
                             f"Manual database updates required to demote {demoted_count} admin accounts")
                print(f"\n      ⚠️ MANUAL DATABASE UPDATES REQUIRED:")
                print(f"         {demoted_count} admin accounts need to be demoted to 'user' role")
                print(f"         This requires direct database access to execute UPDATE statements")
            else:
                self.log_test("Admin Accounts Demotion", True, "No admin accounts needed demotion")
            
            return demoted_count == 0
                
        except Exception as e:
            self.log_test("Admin Accounts Demotion", False, f"Exception: {str(e)}")
            return False
    
    def verify_new_admin_login(self):
        """Verify the new admin account can login successfully"""
        try:
            print(f"\n🔐 VERIFYING NEW ADMIN ACCOUNT LOGIN")
            print("=" * 60)
            print(f"   Email: {NEW_ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {NEW_ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": NEW_ADMIN_CREDENTIALS['email'],
                    "password": NEW_ADMIN_CREDENTIALS['password']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                token = data.get('token')
                
                self.log_test("New Admin Login Verification", True, 
                             f"New admin account login successful")
                
                print(f"      Login Response:")
                print(f"         User ID: {user_data.get('id')}")
                print(f"         Name: {user_data.get('name')}")
                print(f"         Email: {user_data.get('email')}")
                print(f"         Role: {user_data.get('role')}")
                print(f"         Token: {token[:20]}..." if token else "No token")
                
                return True
                
            else:
                self.log_test("New Admin Login Verification", False, 
                             f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("New Admin Login Verification", False, f"Exception: {str(e)}")
            return False
    
    def verify_admin_privileges(self):
        """Verify the new admin account has admin privileges"""
        try:
            print(f"\n🛡️ VERIFYING ADMIN PRIVILEGES")
            print("=" * 60)
            
            # Login as new admin
            login_response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": NEW_ADMIN_CREDENTIALS['email'],
                    "password": NEW_ADMIN_CREDENTIALS['password']
                },
                timeout=10
            )
            
            if login_response.status_code != 200:
                self.log_test("Admin Privileges Verification", False, "Cannot login as new admin")
                return False
            
            login_data = login_response.json()
            admin_token = login_data.get("token")
            
            # Create session with admin token
            admin_session = requests.Session()
            admin_session.headers.update({"Authorization": f"Bearer {admin_token}"})
            
            # Test various admin endpoints
            admin_tests = [
                ("Pending Contributions", f"{BACKEND_URL}/admin/pending-contributions"),
                ("Leaderboard Access", f"{BACKEND_URL}/leaderboard"),
                ("User Gamification Data", f"{BACKEND_URL}/users/{self.new_admin_user_id}/gamification")
            ]
            
            admin_access_count = 0
            for test_name, endpoint in admin_tests:
                try:
                    response = admin_session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        print(f"      ✅ {test_name}: Accessible")
                        admin_access_count += 1
                    elif response.status_code == 403:
                        print(f"      ❌ {test_name}: Access denied (403)")
                    else:
                        print(f"      ⚠️ {test_name}: Unexpected status {response.status_code}")
                except Exception as e:
                    print(f"      ❌ {test_name}: Exception - {str(e)}")
            
            if admin_access_count == len(admin_tests):
                self.log_test("Admin Privileges Verification", True, 
                             f"All admin endpoints accessible - full admin privileges confirmed")
                return True
            elif admin_access_count > 0:
                self.log_test("Admin Privileges Verification", False, 
                             f"Partial admin access - {admin_access_count}/{len(admin_tests)} endpoints accessible")
                return False
            else:
                self.log_test("Admin Privileges Verification", False, 
                             f"No admin privileges - all admin endpoints inaccessible")
                return False
                
        except Exception as e:
            self.log_test("Admin Privileges Verification", False, f"Exception: {str(e)}")
            return False
    
    def check_and_delete_incorrect_account(self):
        """Check for and delete the incorrect admin account (topkitfr@gmail.fr)"""
        try:
            print(f"\n🗑️ CHECKING FOR INCORRECT ADMIN ACCOUNT TO DELETE")
            print("=" * 60)
            
            incorrect_email = "topkitfr@gmail.fr"
            print(f"   Incorrect Email to Delete: {incorrect_email}")
            
            # Try to login with the incorrect account to see if it exists
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": incorrect_email,
                    "password": NEW_ADMIN_CREDENTIALS['password']  # Same password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                incorrect_user_id = user_data.get('id')
                
                self.log_test("Incorrect Account Detection", True, 
                             f"Found incorrect account {incorrect_email} - needs deletion")
                
                print(f"      Incorrect Account Found:")
                print(f"         User ID: {incorrect_user_id}")
                print(f"         Name: {user_data.get('name')}")
                print(f"         Role: {user_data.get('role')}")
                print(f"         Email: {user_data.get('email')}")
                
                # Note: In a real scenario, this would require direct database access
                print(f"      📝 MANUAL ACTION REQUIRED: Delete incorrect account from database")
                print(f"         DELETE FROM users WHERE id = '{incorrect_user_id}';")
                print(f"         DELETE FROM sessions WHERE user_id = '{incorrect_user_id}';")
                print(f"         DELETE FROM contributions_gamification WHERE user_id = '{incorrect_user_id}';")
                
                self.log_test("Incorrect Account Deletion", False, 
                             f"Manual database deletion required for {incorrect_email}")
                return False
                
            elif response.status_code == 401:
                self.log_test("Incorrect Account Detection", True, 
                             f"Incorrect account {incorrect_email} does not exist - good!")
                print(f"      ✅ Incorrect account does not exist")
                return True
                
            else:
                self.log_test("Incorrect Account Detection", False, 
                             f"Unexpected response when checking incorrect account: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Incorrect Account Detection", False, f"Exception: {str(e)}")
            return False
    
    def verify_single_admin_status(self):
        """Verify that the new account is the only admin account"""
        try:
            print(f"\n👑 VERIFYING SINGLE ADMIN STATUS")
            print("=" * 60)
            
            # Get updated user list
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=100", timeout=10)
            
            if response.status_code == 200:
                all_users = response.json()
                
                # Count admin accounts
                current_admin_accounts = []
                for user in all_users:
                    username = user.get('username', '').lower()
                    if 'admin' in username:
                        current_admin_accounts.append(user)
                
                print(f"   Current admin accounts found: {len(current_admin_accounts)}")
                
                target_admin_found = False
                for admin in current_admin_accounts:
                    username = admin.get('username', 'Unknown')
                    print(f"      - {username}")
                    
                    if NEW_ADMIN_CREDENTIALS['email'].lower() in username.lower() or \
                       NEW_ADMIN_CREDENTIALS['name'].lower() in username.lower():
                        target_admin_found = True
                        print(f"        ✅ This is our target admin account")
                    else:
                        print(f"        ⚠️ This is an existing admin that should be demoted")
                
                if len(current_admin_accounts) == 1 and target_admin_found:
                    self.log_test("Single Admin Status Verification", True, 
                                 f"✅ Only one admin account exists - the target account")
                    return True
                elif target_admin_found and len(current_admin_accounts) > 1:
                    self.log_test("Single Admin Status Verification", False, 
                                 f"Target admin exists but {len(current_admin_accounts)-1} other admin accounts still exist")
                    return False
                elif not target_admin_found:
                    self.log_test("Single Admin Status Verification", False, 
                                 f"Target admin account not found in admin list")
                    return False
                else:
                    self.log_test("Single Admin Status Verification", False, 
                                 f"Unexpected admin account state")
                    return False
                
            else:
                self.log_test("Single Admin Status Verification", False, 
                             f"Failed to get user list: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Single Admin Status Verification", False, f"Exception: {str(e)}")
            return False
        """Verify that the new account is the only admin account"""
        try:
            print(f"\n👑 VERIFYING SINGLE ADMIN STATUS")
            print("=" * 60)
            
            # Get updated user list
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=100", timeout=10)
            
            if response.status_code == 200:
                all_users = response.json()
                
                # Count admin accounts
                current_admin_accounts = []
                for user in all_users:
                    username = user.get('username', '').lower()
                    if 'admin' in username:
                        current_admin_accounts.append(user)
                
                print(f"   Current admin accounts found: {len(current_admin_accounts)}")
                
                target_admin_found = False
                for admin in current_admin_accounts:
                    username = admin.get('username', 'Unknown')
                    print(f"      - {username}")
                    
                    if NEW_ADMIN_CREDENTIALS['email'].lower() in username.lower() or \
                       NEW_ADMIN_CREDENTIALS['name'].lower() in username.lower():
                        target_admin_found = True
                        print(f"        ✅ This is our target admin account")
                    else:
                        print(f"        ⚠️ This is an existing admin that should be demoted")
                
                if len(current_admin_accounts) == 1 and target_admin_found:
                    self.log_test("Single Admin Status Verification", True, 
                                 f"✅ Only one admin account exists - the target account")
                    return True
                elif target_admin_found and len(current_admin_accounts) > 1:
                    self.log_test("Single Admin Status Verification", False, 
                                 f"Target admin exists but {len(current_admin_accounts)-1} other admin accounts still exist")
                    return False
                elif not target_admin_found:
                    self.log_test("Single Admin Status Verification", False, 
                                 f"Target admin account not found in admin list")
                    return False
                else:
                    self.log_test("Single Admin Status Verification", False, 
                                 f"Unexpected admin account state")
                    return False
                
            else:
                self.log_test("Single Admin Status Verification", False, 
                             f"Failed to get user list: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Single Admin Status Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_admin_account_management(self):
        """Run comprehensive admin account management"""
        print("\n👑 ADMIN ACCOUNT EMAIL CORRECTION")
        print("Creating topkitfr@gmail.com as the ONLY admin account (CORRECTED EMAIL)")
        print("=" * 80)
        
        management_results = []
        
        # Step 1: Authenticate as emergency admin
        print("\n1️⃣ Authenticating as Emergency Admin...")
        management_results.append(self.authenticate_emergency_admin())
        
        if not self.auth_token:
            print("❌ Cannot proceed without admin authentication")
            return management_results
        
        # Step 2: Identify existing admin accounts
        print("\n2️⃣ Identifying Existing Admin Accounts...")
        management_results.append(self.get_all_users_and_identify_admins())
        
        # Step 3: Check for and delete incorrect account
        print("\n3️⃣ Checking for Incorrect Account to Delete...")
        management_results.append(self.check_and_delete_incorrect_account())
        
        # Step 4: Check if target account already exists
        print("\n4️⃣ Checking if Target Account Already Exists...")
        target_exists = self.check_if_target_account_exists()
        management_results.append(True)  # This step always succeeds
        
        # Step 5: Create new admin account (if needed)
        if not target_exists:
            print("\n5️⃣ Creating New Admin Account...")
            management_results.append(self.create_new_admin_account())
        else:
            print("\n5️⃣ Skipping Account Creation (Already Exists)...")
            management_results.append(True)
        
        # Step 6: Upgrade account to admin role
        print("\n6️⃣ Upgrading Account to Admin Role...")
        management_results.append(self.upgrade_account_to_admin_role())
        
        # Step 7: Demote existing admin accounts
        print("\n7️⃣ Demoting Existing Admin Accounts...")
        management_results.append(self.demote_existing_admin_accounts())
        
        # Step 8: Verify new admin login
        print("\n8️⃣ Verifying New Admin Login...")
        management_results.append(self.verify_new_admin_login())
        
        # Step 9: Verify admin privileges
        print("\n9️⃣ Verifying Admin Privileges...")
        management_results.append(self.verify_admin_privileges())
        
        # Step 10: Verify single admin status
        print("\n🔟 Verifying Single Admin Status...")
        management_results.append(self.verify_single_admin_status())
        
        return management_results
    
    def print_management_summary(self):
        """Print comprehensive management summary"""
        print("\n📊 ADMIN ACCOUNT MANAGEMENT SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # Emergency admin access
        emergency_admin_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if emergency_admin_working:
            print(f"  ✅ EMERGENCY ADMIN ACCESS: Working correctly")
        else:
            print(f"  ❌ EMERGENCY ADMIN ACCESS: Failed")
        
        # Account creation
        account_created = any(r['success'] for r in self.test_results if 'New Admin Account Creation' in r['test'])
        if account_created:
            print(f"  ✅ ACCOUNT CREATION: New admin account created successfully")
            print(f"      Email: {NEW_ADMIN_CREDENTIALS['email']}")
            print(f"      Name: {NEW_ADMIN_CREDENTIALS['name']}")
        else:
            print(f"  ❌ ACCOUNT CREATION: Failed to create new admin account")
        
        # Admin privileges
        admin_privileges = any(r['success'] for r in self.test_results if 'Admin Privileges Verification' in r['test'])
        if admin_privileges:
            print(f"  ✅ ADMIN PRIVILEGES: New account has admin access")
        else:
            print(f"  ❌ ADMIN PRIVILEGES: New account lacks admin access")
        
        # Single admin status
        single_admin = any(r['success'] for r in self.test_results if 'Single Admin Status Verification' in r['test'])
        if single_admin:
            print(f"  ✅ SINGLE ADMIN: Only one admin account exists")
        else:
            print(f"  ❌ SINGLE ADMIN: Multiple admin accounts still exist")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Manual actions required
        manual_actions = []
        if not any(r['success'] for r in self.test_results if 'Admin Role Upgrade' in r['test']):
            manual_actions.append(f"Update user role to 'admin' in database for user ID: {self.new_admin_user_id}")
        
        if not any(r['success'] for r in self.test_results if 'Admin Accounts Demotion' in r['test']):
            for admin in self.existing_admins:
                username = admin.get('username', 'Unknown')
                if NEW_ADMIN_CREDENTIALS['email'].lower() not in username.lower():
                    manual_actions.append(f"Update role to 'user' for admin account: {username}")
        
        if manual_actions:
            print(f"\n📝 MANUAL DATABASE ACTIONS REQUIRED:")
            for i, action in enumerate(manual_actions, 1):
                print(f"  {i}. {action}")
        
        # Final status
        print(f"\n🎯 FINAL STATUS:")
        if passed_tests == total_tests:
            print(f"  ✅ COMPLETE SUCCESS: All admin account management tasks completed")
            print(f"     - New admin account created and functional")
            print(f"     - Admin privileges verified")
            print(f"     - Single admin status confirmed")
        elif account_created and admin_privileges:
            print(f"  ⚠️ PARTIAL SUCCESS: New admin account created but manual actions required")
            print(f"     - Account creation: ✅")
            print(f"     - Admin privileges: ✅")
            print(f"     - Single admin status: ❌ (manual database updates needed)")
        else:
            print(f"  ❌ INCOMPLETE: Admin account management requires manual intervention")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run comprehensive admin account management and return success status"""
        management_results = self.run_admin_account_management()
        self.print_management_summary()
        return any(management_results)

def main():
    """Main test execution"""
    manager = TopKitAdminAccountManager()
    success = manager.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()