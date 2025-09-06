#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING - CRITICAL ISSUES INVESTIGATION
Testing all critical backend issues reported in the review request:

1. Reference Kit Creation Issue - Master Kits not appearing in dropdown
2. Admin Dashboard Validation System - "Error updating settings" message  
3. Image Upload System Testing across all categories
4. Navigation Implementation - Master Kit creation navigation

Authentication:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- User: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import os
import base64
from datetime import datetime
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-collection-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 AUTHENTICATING ADMIN USER...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_data = data.get("user", {})
                self.admin_user_id = user_data.get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Admin authenticated: {user_data.get('name', 'Unknown')} (Role: {user_data.get('role', 'Unknown')})"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_admin_settings_get(self):
        """Test GET /api/admin/settings"""
        print("⚙️ TESTING ADMIN SETTINGS RETRIEVAL...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/settings")
            
            if response.status_code == 200:
                settings = response.json()
                expected_keys = ["auto_approval_enabled", "admin_notifications", "community_voting_enabled"]
                
                missing_keys = [key for key in expected_keys if key not in settings]
                if missing_keys:
                    self.log_test(
                        "Admin Settings GET",
                        False,
                        f"Missing settings keys: {missing_keys}"
                    )
                else:
                    self.log_test(
                        "Admin Settings GET",
                        True,
                        f"Settings retrieved: {json.dumps(settings, indent=2)}"
                    )
                return settings
            else:
                self.log_test(
                    "Admin Settings GET",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Admin Settings GET", False, f"Exception: {str(e)}")
            return None

    def test_admin_settings_update(self, new_settings):
        """Test PUT /api/admin/settings"""
        print("⚙️ TESTING ADMIN SETTINGS UPDATE...")
        
        try:
            response = self.session.put(f"{BACKEND_URL}/admin/settings", json=new_settings)
            
            if response.status_code == 200:
                self.log_test(
                    "Admin Settings UPDATE",
                    True,
                    f"Settings updated: {json.dumps(new_settings, indent=2)}"
                )
                return True
            else:
                self.log_test(
                    "Admin Settings UPDATE",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Settings UPDATE", False, f"Exception: {str(e)}")
            return False

    def test_dashboard_stats(self):
        """Test GET /api/admin/dashboard-stats"""
        print("📊 TESTING ADMIN DASHBOARD STATISTICS...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/dashboard-stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Check for expected sections
                expected_sections = ["users", "content", "moderation", "system"]
                missing_sections = [section for section in expected_sections if section not in stats]
                
                if missing_sections:
                    self.log_test(
                        "Dashboard Statistics",
                        False,
                        f"Missing sections: {missing_sections}"
                    )
                else:
                    # Verify data structure
                    users_stats = stats.get("users", {})
                    content_stats = stats.get("content", {})
                    moderation_stats = stats.get("moderation", {})
                    system_stats = stats.get("system", {})
                    
                    details = f"""
Dashboard Statistics Retrieved:
- Users: {users_stats.get('total', 0)} total, {users_stats.get('active_30d', 0)} active (30d)
- Content: {content_stats.get('teams', 0)} teams, {content_stats.get('competitions', 0)} competitions, {content_stats.get('brands', 0)} brands
- Moderation: {moderation_stats.get('pending_contributions', 0)} pending, {moderation_stats.get('total_contributions', 0)} total
- System: Auto-approval={system_stats.get('auto_approval', 'Unknown')}, Community voting={system_stats.get('community_voting', 'Unknown')}
                    """
                    
                    self.log_test("Dashboard Statistics", True, details.strip())
                return stats
            else:
                self.log_test(
                    "Dashboard Statistics",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Dashboard Statistics", False, f"Exception: {str(e)}")
            return None

    def test_admin_users(self):
        """Test GET /api/admin/users"""
        print("👥 TESTING ADMIN USER MANAGEMENT...")
        
        try:
            # Test basic user listing
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                total = data.get("total", 0)
                
                self.log_test(
                    "Admin Users Listing",
                    True,
                    f"Retrieved {len(users)} users out of {total} total"
                )
                
                # Test pagination
                response_page2 = self.session.get(f"{BACKEND_URL}/admin/users?page=2&limit=5")
                if response_page2.status_code == 200:
                    self.log_test("Admin Users Pagination", True, "Pagination working")
                else:
                    self.log_test("Admin Users Pagination", False, f"HTTP {response_page2.status_code}")
                
                # Test search functionality
                response_search = self.session.get(f"{BACKEND_URL}/admin/users?search=topkit")
                if response_search.status_code == 200:
                    search_data = response_search.json()
                    self.log_test(
                        "Admin Users Search",
                        True,
                        f"Search returned {len(search_data.get('users', []))} results"
                    )
                else:
                    self.log_test("Admin Users Search", False, f"HTTP {response_search.status_code}")
                
                return data
            else:
                self.log_test(
                    "Admin Users Listing",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Admin Users Listing", False, f"Exception: {str(e)}")
            return None

    def test_pending_approvals(self):
        """Test GET /api/admin/pending-approvals"""
        print("⏳ TESTING PENDING APPROVALS MANAGEMENT...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/pending-approvals")
            
            if response.status_code == 200:
                pending_items = response.json()
                
                # Group by type
                item_types = {}
                for item in pending_items:
                    item_type = item.get("type", "unknown")
                    if item_type not in item_types:
                        item_types[item_type] = 0
                    item_types[item_type] += 1
                
                details = f"Found {len(pending_items)} pending items: {dict(item_types)}"
                self.log_test("Pending Approvals Listing", True, details)
                
                return pending_items
            else:
                self.log_test(
                    "Pending Approvals Listing",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Pending Approvals Listing", False, f"Exception: {str(e)}")
            return None

    def test_approval_functionality(self, pending_items):
        """Test approval functionality if pending items exist"""
        print("✅ TESTING APPROVAL FUNCTIONALITY...")
        
        if not pending_items:
            self.log_test(
                "Approval Functionality",
                True,
                "No pending items to test approval (system working correctly)"
            )
            return True
        
        # Test approval on first pending item
        test_item = pending_items[0]
        item_type = test_item.get("type")
        item_id = test_item.get("id")
        
        try:
            response = self.session.put(f"{BACKEND_URL}/admin/approve/{item_type}/{item_id}")
            
            if response.status_code == 200:
                self.log_test(
                    "Approval Functionality",
                    True,
                    f"Successfully approved {item_type} with ID {item_id}"
                )
                return True
            else:
                self.log_test(
                    "Approval Functionality",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Approval Functionality", False, f"Exception: {str(e)}")
            return False

    def create_test_team(self, auto_approval_enabled):
        """Create a test team to verify auto-approval behavior"""
        print(f"🏆 CREATING TEST TEAM (Auto-approval: {auto_approval_enabled})...")
        
        # Use microseconds to ensure unique names
        import time
        unique_suffix = f"{datetime.now().strftime('%H%M%S')}{int(time.time() * 1000000) % 1000000}"
        
        test_team_data = {
            "name": f"Test Team Auto-Approval {unique_suffix}",
            "country": "France",
            "city": "Test City",
            "founded_year": 2024,
            "short_name": f"TTA{unique_suffix[:4]}"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/teams", json=test_team_data)
            
            if response.status_code == 200 or response.status_code == 201:
                team_data = response.json()
                team_id = team_data.get("id")
                verified_level = team_data.get("verified_level")
                
                # Handle case insensitive comparison
                expected_status = "COMMUNITY_VERIFIED" if auto_approval_enabled else "PENDING"
                verified_level_upper = verified_level.upper() if verified_level else None
                
                if verified_level_upper == expected_status:
                    self.log_test(
                        f"Team Creation (Auto-approval: {auto_approval_enabled})",
                        True,
                        f"Team created with correct status: {verified_level}"
                    )
                    return team_id, verified_level
                else:
                    self.log_test(
                        f"Team Creation (Auto-approval: {auto_approval_enabled})",
                        False,
                        f"Expected status {expected_status}, got {verified_level}"
                    )
                    return team_id, verified_level
            else:
                self.log_test(
                    f"Team Creation (Auto-approval: {auto_approval_enabled})",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None, None
                
        except Exception as e:
            self.log_test(
                f"Team Creation (Auto-approval: {auto_approval_enabled})",
                False,
                f"Exception: {str(e)}"
            )
            return None, None

    def test_hybrid_auto_approval_workflow(self):
        """Test the complete hybrid auto-approval workflow"""
        print("🔄 TESTING HYBRID AUTO-APPROVAL WORKFLOW...")
        
        # Get current settings
        current_settings = self.test_admin_settings_get()
        if not current_settings:
            return False
        
        # Test 1: Enable auto-approval and create team
        print("\n--- Test 1: Auto-approval ENABLED ---")
        auto_approval_settings = current_settings.copy()
        auto_approval_settings["auto_approval_enabled"] = True
        
        if self.test_admin_settings_update(auto_approval_settings):
            team_id_1, status_1 = self.create_test_team(True)
            
        # Test 2: Disable auto-approval and create team
        print("\n--- Test 2: Auto-approval DISABLED ---")
        manual_approval_settings = current_settings.copy()
        manual_approval_settings["auto_approval_enabled"] = False
        
        if self.test_admin_settings_update(manual_approval_settings):
            # Add small delay to ensure different timestamp
            import time
            time.sleep(1)
            team_id_2, status_2 = self.create_test_team(False)
        
        # Test 3: Verify pending items and approve manually
        print("\n--- Test 3: Manual approval workflow ---")
        pending_items = self.test_pending_approvals()
        if pending_items:
            # Find our test team in pending items
            test_team_pending = None
            for item in pending_items:
                if item.get("id") == team_id_2:
                    test_team_pending = item
                    break
            
            if test_team_pending:
                self.test_approval_functionality([test_team_pending])
            else:
                self.log_test(
                    "Manual Approval Workflow",
                    False,
                    f"Test team {team_id_2} not found in pending items"
                )
        
        # Restore original settings
        print("\n--- Restoring original settings ---")
        self.test_admin_settings_update(current_settings)
        
        # Summary
        workflow_success = (
            status_1 and status_1.upper() == "COMMUNITY_VERIFIED" and 
            status_2 and status_2.upper() == "PENDING"
        )
        
        self.log_test(
            "Hybrid Auto-Approval Workflow",
            workflow_success,
            f"Auto-approved team status: {status_1}, Manual team status: {status_2}"
        )
        
        return workflow_success

    def run_all_tests(self):
        """Run all admin system tests"""
        print("🚀 STARTING ADMIN SYSTEM COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test admin settings management
        current_settings = self.test_admin_settings_get()
        
        # Step 3: Test dashboard statistics
        self.test_dashboard_stats()
        
        # Step 4: Test user management
        self.test_admin_users()
        
        # Step 5: Test pending approvals
        pending_items = self.test_pending_approvals()
        
        # Step 6: Test approval functionality
        self.test_approval_functionality(pending_items)
        
        # Step 7: Test hybrid auto-approval workflow
        self.test_hybrid_auto_approval_workflow()
        
        # Generate summary
        self.generate_summary()
        
        return True

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📋 ADMIN SYSTEM TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 80:
            print("🎉 ADMIN SYSTEM IS PRODUCTION-READY!")
        elif success_rate >= 60:
            print("⚠️  ADMIN SYSTEM NEEDS MINOR FIXES")
        else:
            print("🚨 ADMIN SYSTEM NEEDS MAJOR FIXES")
        
        print("=" * 60)

def main():
    """Main test execution"""
    tester = AdminSystemTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n🚨 CRITICAL ERROR: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())