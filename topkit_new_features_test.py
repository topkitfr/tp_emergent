#!/usr/bin/env python3
"""
TopKit New Features Testing - Moderator Roles, Dynamic Stats & Database Cleanup
Testing the newly implemented features as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-jersey-db.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

class TopKitNewFeaturesTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.test_user_id = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
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
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                admin_info = data["user"]
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Admin logged in successfully - Name: {admin_info['name']}, Role: {admin_info['role']}, ID: {admin_info['id']}"
                )
                return True
            else:
                self.log_result("Admin Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
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
                self.user_token = data["token"]
                user_info = data["user"]
                self.test_user_id = user_info["id"]
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"User logged in successfully - Name: {user_info['name']}, Role: {user_info['role']}, ID: {user_info['id']}"
                )
                return True
            else:
                self.log_result("User Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, "", str(e))
            return False
    
    def test_moderator_role_assignment(self):
        """Test POST /api/admin/users/{user_id}/make-moderator"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Make User Moderator", False, "", "Missing admin token or user ID")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/make-moderator",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Make User Moderator", 
                    True, 
                    f"User successfully made moderator: {data.get('message', 'Success')}"
                )
                return True
            else:
                self.log_result("Make User Moderator", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Make User Moderator", False, "", str(e))
            return False
    
    def test_moderator_role_removal(self):
        """Test POST /api/admin/users/{user_id}/remove-moderator"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Remove User Moderator", False, "", "Missing admin token or user ID")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/remove-moderator",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Remove User Moderator", 
                    True, 
                    f"User moderator role removed: {data.get('message', 'Success')}"
                )
                return True
            else:
                self.log_result("Remove User Moderator", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Remove User Moderator", False, "", str(e))
            return False
    
    def test_admin_users_list(self):
        """Test GET /api/admin/users (liste des utilisateurs avec rôles)"""
        if not self.admin_token:
            self.log_result("Admin Users List", False, "", "Missing admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users_count = len(data) if isinstance(data, list) else len(data.get('users', []))
                self.log_result(
                    "Admin Users List", 
                    True, 
                    f"Retrieved {users_count} users with roles information"
                )
                return True
            else:
                self.log_result("Admin Users List", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Users List", False, "", str(e))
            return False
    
    def test_dynamic_stats_before_cleanup(self):
        """Test GET /api/stats/dynamic (before cleanup)"""
        try:
            response = requests.get(f"{BACKEND_URL}/stats/dynamic")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Dynamic Stats (Before Cleanup)", 
                    True, 
                    f"Stats retrieved - Users: {data.get('users', 'N/A')}, Jerseys: {data.get('jerseys', 'N/A')}, Collections: {data.get('collections', 'N/A')}, Listings: {data.get('listings', 'N/A')}, Messages: {data.get('messages', 'N/A')}"
                )
                return data
            else:
                self.log_result("Dynamic Stats (Before Cleanup)", False, "", f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Dynamic Stats (Before Cleanup)", False, "", str(e))
            return None
    
    def test_database_cleanup(self):
        """Test POST /api/admin/cleanup/database (avec credentials admin)"""
        if not self.admin_token:
            self.log_result("Database Cleanup", False, "", "Missing admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/admin/cleanup/database", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Database Cleanup", 
                    True, 
                    f"Database cleaned successfully: {data.get('message', 'Success')} - Details: {data.get('details', 'N/A')}"
                )
                return True
            else:
                self.log_result("Database Cleanup", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Database Cleanup", False, "", str(e))
            return False
    
    def test_dynamic_stats_after_cleanup(self):
        """Test GET /api/stats/dynamic (after cleanup)"""
        try:
            response = requests.get(f"{BACKEND_URL}/stats/dynamic")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Dynamic Stats (After Cleanup)", 
                    True, 
                    f"Stats after cleanup - Users: {data.get('users', 'N/A')}, Jerseys: {data.get('jerseys', 'N/A')}, Collections: {data.get('collections', 'N/A')}, Listings: {data.get('listings', 'N/A')}, Messages: {data.get('messages', 'N/A')}"
                )
                return data
            else:
                self.log_result("Dynamic Stats (After Cleanup)", False, "", f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Dynamic Stats (After Cleanup)", False, "", str(e))
            return None
    
    def verify_preserved_accounts(self):
        """Verify that only the 2 specified accounts are preserved after cleanup"""
        if not self.admin_token:
            self.log_result("Verify Preserved Accounts", False, "", "Missing admin token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data if isinstance(data, list) else data.get('users', [])
                
                preserved_emails = [user.get('email') for user in users]
                expected_emails = [ADMIN_EMAIL, USER_EMAIL]
                
                if len(users) == 2 and all(email in preserved_emails for email in expected_emails):
                    self.log_result(
                        "Verify Preserved Accounts", 
                        True, 
                        f"Correct accounts preserved: {preserved_emails}"
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Preserved Accounts", 
                        False, 
                        f"Expected 2 accounts ({expected_emails}), found {len(users)}: {preserved_emails}"
                    )
                    return False
            else:
                self.log_result("Verify Preserved Accounts", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Verify Preserved Accounts", False, "", str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests in the correct sequence"""
        print("🧹 TOPKIT - TEST DES NOUVELLES FONCTIONNALITÉS ET NETTOYAGE DE BASE DE DONNÉES")
        print("=" * 80)
        print()
        
        # Phase 1: Authentication
        print("📋 PHASE 1: AUTHENTICATION")
        print("-" * 40)
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return self.generate_summary()
        
        if not self.authenticate_user():
            print("⚠️ User authentication failed, some tests will be skipped")
        
        print()
        
        # Phase 2: Test Moderator Role Management
        print("👥 PHASE 2: MODERATOR ROLE MANAGEMENT")
        print("-" * 40)
        self.test_admin_users_list()
        if self.test_user_id:
            self.test_moderator_role_assignment()
            self.test_moderator_role_removal()
        print()
        
        # Phase 3: Test Dynamic Statistics (Before Cleanup)
        print("📊 PHASE 3: DYNAMIC STATISTICS (BEFORE CLEANUP)")
        print("-" * 40)
        stats_before = self.test_dynamic_stats_before_cleanup()
        print()
        
        # Phase 4: Database Cleanup
        print("🧹 PHASE 4: DATABASE CLEANUP")
        print("-" * 40)
        print("⚠️  WARNING: This will permanently delete data from the database!")
        print("   Only preserving: topkitfr@gmail.com and steinmetzlivio@gmail.com")
        print()
        
        cleanup_success = self.test_database_cleanup()
        print()
        
        # Phase 5: Verify Results
        print("✅ PHASE 5: VERIFICATION")
        print("-" * 40)
        if cleanup_success:
            self.test_dynamic_stats_after_cleanup()
            self.verify_preserved_accounts()
        print()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
            print()
        
        print("🎯 CONCLUSION:")
        if success_rate >= 90:
            print("✅ All new features are working excellently!")
        elif success_rate >= 70:
            print("⚠️  Most features working, some issues need attention")
        else:
            print("❌ Multiple critical issues identified")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = TopKitNewFeaturesTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["success_rate"] >= 70 else 1)

if __name__ == "__main__":
    main()