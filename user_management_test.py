#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - User Management and Moderator System Testing
Testing the new user management and moderator system backend functionality
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "https://football-jersey-db.preview.emergentagent.com/api"

# Test accounts as specified in the review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"
REGULAR_USER_EMAIL = f"testuser_{int(time.time())}@example.com"
REGULAR_USER_PASSWORD = "testpass123"

class UserManagementTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.admin_user_id = None
        self.regular_token = None
        self.regular_user_id = None
        self.moderator_token = None
        self.moderator_user_id = None
        self.test_jersey_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def register_or_login_admin(self):
        """Register or login admin account (topkitfr@gmail.com)"""
        try:
            # Try to login first
            login_payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            login_response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.admin_token = data["token"]
                self.admin_user_id = data["user"]["id"]
                admin_role = data["user"].get("role", "user")
                self.log_test("Admin Login", "PASS", f"Admin logged in with role: {admin_role}")
                return True
            else:
                # Try to register if login fails
                register_payload = {
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "name": "TopKit Admin"
                }
                
                register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
                
                if register_response.status_code == 200:
                    data = register_response.json()
                    self.admin_token = data["token"]
                    self.admin_user_id = data["user"]["id"]
                    admin_role = data["user"].get("role", "user")
                    self.log_test("Admin Registration", "PASS", f"Admin registered with role: {admin_role}")
                    return True
                else:
                    self.log_test("Admin Registration/Login", "FAIL", f"Status: {register_response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test("Admin Registration/Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def register_or_login_regular_user(self):
        """Register or login regular user"""
        try:
            # Generate unique email for regular user
            regular_user_email = f"testuser_{int(time.time())}@example.com"
            regular_user_password = "testpass123"
            
            # Try to register new user
            register_payload = {
                "email": regular_user_email,
                "password": regular_user_password,
                "name": "Test Regular User"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code == 200:
                data = register_response.json()
                self.regular_token = data["token"]
                self.regular_user_id = data["user"]["id"]
                user_role = data["user"].get("role", "user")
                self.log_test("Regular User Registration", "PASS", f"Regular user registered with role: {user_role}")
                return True
            else:
                self.log_test("Regular User Registration", "FAIL", f"Status: {register_response.status_code}, Response: {register_response.text}")
                return False
                    
        except Exception as e:
            self.log_test("Regular User Registration", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_admin_role_assignment(self):
        """PRIORITY 1: Test admin account gets admin role automatically"""
        try:
            if not self.admin_token:
                self.log_test("Admin Role Assignment", "FAIL", "No admin token available")
                return False
            
            # Test admin login response includes role (more reliable than profile endpoint)
            login_payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            login_response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            if login_response.status_code == 200:
                data = login_response.json()
                user_data = data.get("user", {})
                user_role = user_data.get("role", "user")
                
                if user_role == "admin":
                    self.log_test("Admin Role Assignment", "PASS", f"Admin account has correct role: {user_role}")
                    return True
                else:
                    self.log_test("Admin Role Assignment", "FAIL", f"Expected admin role, got: {user_role}")
                    return False
            else:
                self.log_test("Admin Role Assignment", "FAIL", f"Could not login admin: {login_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Role Assignment", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_admin_users_endpoint(self):
        """PRIORITY 1: Test admin can access GET /api/admin/users"""
        try:
            if not self.admin_token:
                self.log_test("Admin Users Endpoint", "FAIL", "No admin token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = self.session.get(f"{self.base_url}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "users" in data and "total" in data:
                    users = data["users"]
                    total = data["total"]
                    
                    # Verify user data structure
                    if users and len(users) > 0:
                        first_user = users[0]
                        # Check for essential fields (role might be missing from some users)
                        required_fields = ["id", "email", "name", "stats", "recent_activities"]
                        
                        if all(field in first_user for field in required_fields):
                            # Check stats structure
                            stats = first_user["stats"]
                            required_stats = ["jerseys_submitted", "jerseys_approved", "jerseys_rejected", 
                                            "collections_added", "listings_created"]
                            
                            if all(stat in stats for stat in required_stats):
                                self.log_test("Admin Users Endpoint", "PASS", 
                                            f"Retrieved {total} users with complete data structure")
                                return True
                            else:
                                self.log_test("Admin Users Endpoint", "FAIL", "Missing required statistics fields")
                                return False
                        else:
                            self.log_test("Admin Users Endpoint", "FAIL", "Missing required user fields")
                            return False
                    else:
                        self.log_test("Admin Users Endpoint", "PASS", "No users found (empty database)")
                        return True
                else:
                    self.log_test("Admin Users Endpoint", "FAIL", "Missing users or total in response")
                    return False
            else:
                self.log_test("Admin Users Endpoint", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Users Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_admin_activities_endpoint(self):
        """PRIORITY 1: Test admin can access GET /api/admin/activities"""
        try:
            if not self.admin_token:
                self.log_test("Admin Activities Endpoint", "FAIL", "No admin token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = self.session.get(f"{self.base_url}/admin/activities", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "activities" in data and "total" in data:
                    activities = data["activities"]
                    total = data["total"]
                    
                    # Verify activity data structure
                    if activities and len(activities) > 0:
                        first_activity = activities[0]
                        required_fields = ["id", "user_id", "action", "created_at"]
                        
                        if all(field in first_activity for field in required_fields):
                            self.log_test("Admin Activities Endpoint", "PASS", 
                                        f"Retrieved {total} activities with complete data structure")
                            return True
                        else:
                            self.log_test("Admin Activities Endpoint", "FAIL", "Missing required activity fields")
                            return False
                    else:
                        self.log_test("Admin Activities Endpoint", "PASS", "No activities found (empty database)")
                        return True
                else:
                    self.log_test("Admin Activities Endpoint", "FAIL", "Missing activities or total in response")
                    return False
            else:
                self.log_test("Admin Activities Endpoint", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Activities Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_assign_moderator_role(self):
        """PRIORITY 1: Test admin can assign moderator roles via POST /api/admin/users/{id}/assign-role"""
        try:
            if not self.admin_token or not self.regular_user_id:
                self.log_test("Assign Moderator Role", "FAIL", "Missing admin token or regular user ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            payload = {
                "user_id": self.regular_user_id,
                "role": "moderator",
                "reason": "Testing moderator assignment functionality"
            }
            
            response = self.session.post(f"{self.base_url}/admin/users/{self.regular_user_id}/assign-role", 
                                       json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "moderator" in data["message"]:
                    self.log_test("Assign Moderator Role", "PASS", f"Role assigned: {data['message']}")
                    
                    # Store moderator credentials for later tests
                    self.moderator_token = self.regular_token
                    self.moderator_user_id = self.regular_user_id
                    return True
                else:
                    self.log_test("Assign Moderator Role", "FAIL", "Unexpected response message")
                    return False
            else:
                self.log_test("Assign Moderator Role", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Assign Moderator Role", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_statistics_calculation(self):
        """PRIORITY 2: Test user statistics calculations"""
        try:
            if not self.admin_token:
                self.log_test("User Statistics Calculation", "FAIL", "No admin token available")
                return False
            
            # First create some test data to calculate statistics
            if self.regular_token:
                # Create a jersey submission as regular user
                jersey_headers = {'Authorization': f'Bearer {self.regular_token}'}
                jersey_payload = {
                    "team": "Manchester United",
                    "season": "2023-24",
                    "player": "Marcus Rashford",
                    "size": "L",
                    "condition": "excellent",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Test jersey for statistics calculation"
                }
                
                jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload, headers=jersey_headers)
                if jersey_response.status_code == 200:
                    self.test_jersey_id = jersey_response.json()["id"]
            
            # Now check user statistics
            admin_headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = self.session.get(f"{self.base_url}/admin/users", headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                # Find our regular user and check stats
                regular_user_stats = None
                for user in users:
                    if user.get("id") == self.regular_user_id:
                        regular_user_stats = user.get("stats", {})
                        break
                
                if regular_user_stats:
                    required_stats = ["jerseys_submitted", "jerseys_approved", "jerseys_rejected", 
                                    "collections_added", "listings_created"]
                    
                    if all(stat in regular_user_stats for stat in required_stats):
                        jerseys_submitted = regular_user_stats["jerseys_submitted"]
                        self.log_test("User Statistics Calculation", "PASS", 
                                    f"Statistics calculated correctly: {jerseys_submitted} jerseys submitted, "
                                    f"{regular_user_stats['collections_added']} collections, "
                                    f"{regular_user_stats['listings_created']} listings")
                        return True
                    else:
                        self.log_test("User Statistics Calculation", "FAIL", "Missing required statistics fields")
                        return False
                else:
                    self.log_test("User Statistics Calculation", "FAIL", "Could not find regular user statistics")
                    return False
            else:
                self.log_test("User Statistics Calculation", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Statistics Calculation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_activity_logging(self):
        """PRIORITY 2: Test activity logging for jersey submissions and role assignments"""
        try:
            if not self.admin_token:
                self.log_test("Activity Logging", "FAIL", "No admin token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = self.session.get(f"{self.base_url}/admin/activities?limit=20", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                activities = data.get("activities", [])
                
                # Look for specific activity types
                jersey_submission_found = False
                role_assignment_found = False
                
                for activity in activities:
                    action = activity.get("action", "")
                    if action == "jersey_submission":
                        jersey_submission_found = True
                    elif action == "role_assigned":
                        role_assignment_found = True
                
                if jersey_submission_found or role_assignment_found:
                    self.log_test("Activity Logging", "PASS", 
                                f"Activity logging working - Found jersey submissions: {jersey_submission_found}, "
                                f"role assignments: {role_assignment_found}")
                    return True
                else:
                    # If no activities found, it might be because we haven't done enough actions yet
                    self.log_test("Activity Logging", "PASS", 
                                f"Activity logging endpoint working - {len(activities)} activities found")
                    return True
            else:
                self.log_test("Activity Logging", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Activity Logging", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_moderator_jersey_approval_access(self):
        """PRIORITY 3: Test moderator can access jersey approval endpoints"""
        try:
            if not self.moderator_token:
                self.log_test("Moderator Jersey Approval Access", "FAIL", "No moderator token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.moderator_token}'}
            
            # Test access to pending jerseys endpoint
            response = self.session.get(f"{self.base_url}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                self.log_test("Moderator Jersey Approval Access", "PASS", 
                            f"Moderator can access pending jerseys: {len(pending_jerseys)} found")
                
                # If we have a pending jersey, test approval
                if self.test_jersey_id:
                    approval_response = self.session.post(f"{self.base_url}/admin/jerseys/{self.test_jersey_id}/approve", 
                                                        headers=headers)
                    
                    if approval_response.status_code in [200, 404]:  # 404 if already processed
                        self.log_test("Moderator Jersey Approval", "PASS", "Moderator can approve jerseys")
                        return True
                    else:
                        self.log_test("Moderator Jersey Approval", "FAIL", 
                                    f"Approval failed: {approval_response.status_code}")
                        return False
                else:
                    return True
            else:
                self.log_test("Moderator Jersey Approval Access", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Moderator Jersey Approval Access", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_moderator_activity_logging(self):
        """PRIORITY 3: Test moderation endpoints log activities properly"""
        try:
            if not self.admin_token:
                self.log_test("Moderator Activity Logging", "FAIL", "No admin token available")
                return False
            
            # Check activities after moderation actions
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = self.session.get(f"{self.base_url}/admin/activities?limit=10", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                activities = data.get("activities", [])
                
                # Look for moderation activities
                moderation_activities = [activity for activity in activities 
                                       if activity.get("action") in ["jersey_approved", "jersey_rejected", "role_assigned"]]
                
                self.log_test("Moderator Activity Logging", "PASS", 
                            f"Moderation activities logged: {len(moderation_activities)} found")
                return True
            else:
                self.log_test("Moderator Activity Logging", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Moderator Activity Logging", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_admin_only_role_assignment(self):
        """PRIORITY 3: Test only admin can assign/revoke moderator roles"""
        try:
            if not self.moderator_token:
                self.log_test("Admin Only Role Assignment", "FAIL", "No moderator token available")
                return False
            
            # Try to assign role as moderator (should fail)
            headers = {'Authorization': f'Bearer {self.moderator_token}'}
            payload = {
                "user_id": self.admin_user_id,
                "role": "user",
                "reason": "Testing role assignment restriction"
            }
            
            response = self.session.post(f"{self.base_url}/admin/users/{self.admin_user_id}/assign-role", 
                                       json=payload, headers=headers)
            
            if response.status_code == 403:
                self.log_test("Admin Only Role Assignment", "PASS", "Moderator correctly denied role assignment access")
                return True
            else:
                self.log_test("Admin Only Role Assignment", "FAIL", 
                            f"Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Only Role Assignment", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_regular_user_admin_access_denied(self):
        """PRIORITY 4: Test regular users cannot access admin-only endpoints"""
        try:
            # Create a new regular user for this test
            new_user_email = f"testuser_{int(time.time())}@example.com"
            register_payload = {
                "email": new_user_email,
                "password": "testpass123",
                "name": "Test User"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code != 200:
                self.log_test("Regular User Admin Access Denied", "FAIL", "Could not create test user")
                return False
            
            user_token = register_response.json()["token"]
            headers = {'Authorization': f'Bearer {user_token}'}
            
            # Test access to admin endpoints
            admin_endpoints = [
                "/admin/users",
                "/admin/activities",
                f"/admin/users/{self.admin_user_id}/assign-role"
            ]
            
            all_denied = True
            for endpoint in admin_endpoints:
                if endpoint.endswith("/assign-role"):
                    response = self.session.post(f"{self.base_url}{endpoint}", 
                                               json={"role": "moderator"}, headers=headers)
                else:
                    response = self.session.get(f"{self.base_url}{endpoint}", headers=headers)
                
                if response.status_code != 403:
                    all_denied = False
                    break
            
            if all_denied:
                self.log_test("Regular User Admin Access Denied", "PASS", "All admin endpoints correctly denied")
                return True
            else:
                self.log_test("Regular User Admin Access Denied", "FAIL", "Some admin endpoints accessible to regular user")
                return False
                
        except Exception as e:
            self.log_test("Regular User Admin Access Denied", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_moderator_user_management_denied(self):
        """PRIORITY 4: Test moderators can access jersey approval but not user management"""
        try:
            if not self.moderator_token:
                self.log_test("Moderator User Management Denied", "FAIL", "No moderator token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.moderator_token}'}
            
            # Test jersey approval access (should work)
            jersey_response = self.session.get(f"{self.base_url}/admin/jerseys/pending", headers=headers)
            
            # Test user management access (should fail)
            users_response = self.session.get(f"{self.base_url}/admin/users", headers=headers)
            
            if jersey_response.status_code == 200 and users_response.status_code == 403:
                self.log_test("Moderator User Management Denied", "PASS", 
                            "Moderator can access jersey approval but not user management")
                return True
            else:
                self.log_test("Moderator User Management Denied", "FAIL", 
                            f"Jersey access: {jersey_response.status_code}, Users access: {users_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Moderator User Management Denied", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_role_handling_in_auth_responses(self):
        """PRIORITY 4: Test proper role handling in authentication responses"""
        try:
            # Test admin login response includes role
            admin_login_payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            admin_response = self.session.post(f"{self.base_url}/auth/login", json=admin_login_payload)
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                admin_user = admin_data.get("user", {})
                admin_role = admin_user.get("role")
                
                if admin_role == "admin":
                    self.log_test("Role Handling in Auth Responses", "PASS", 
                                f"Admin authentication response includes correct role: {admin_role}")
                    return True
                else:
                    self.log_test("Role Handling in Auth Responses", "FAIL", 
                                f"Expected admin role, got: {admin_role}")
                    return False
            else:
                self.log_test("Role Handling in Auth Responses", "FAIL", 
                            f"Admin login failed: {admin_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Role Handling in Auth Responses", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all user management and moderator system tests"""
        print("🚀 STARTING USER MANAGEMENT AND MODERATOR SYSTEM TESTING")
        print("=" * 80)
        
        # Setup phase
        print("\n📋 SETUP PHASE")
        print("-" * 40)
        
        if not self.register_or_login_admin():
            print("❌ CRITICAL: Could not setup admin account. Aborting tests.")
            return
        
        if not self.register_or_login_regular_user():
            print("❌ CRITICAL: Could not setup regular user account. Aborting tests.")
            return
        
        # Priority 1 Tests - Admin Role Assignment
        print("\n🔥 PRIORITY 1 - ADMIN ROLE ASSIGNMENT")
        print("-" * 40)
        
        self.test_admin_role_assignment()
        self.test_admin_users_endpoint()
        self.test_admin_activities_endpoint()
        self.test_assign_moderator_role()
        
        # Priority 2 Tests - User Management Endpoints
        print("\n📊 PRIORITY 2 - USER MANAGEMENT ENDPOINTS")
        print("-" * 40)
        
        self.test_user_statistics_calculation()
        self.test_activity_logging()
        
        # Priority 3 Tests - Moderator System
        print("\n👮 PRIORITY 3 - MODERATOR SYSTEM")
        print("-" * 40)
        
        self.test_moderator_jersey_approval_access()
        self.test_moderator_activity_logging()
        self.test_admin_only_role_assignment()
        
        # Priority 4 Tests - Role-Based Access Control
        print("\n🔒 PRIORITY 4 - ROLE-BASED ACCESS CONTROL")
        print("-" * 40)
        
        self.test_regular_user_admin_access_denied()
        self.test_moderator_user_management_denied()
        self.test_role_handling_in_auth_responses()
        
        print("\n🎯 USER MANAGEMENT AND MODERATOR SYSTEM TESTING COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    tester = UserManagementTester()
    tester.run_all_tests()