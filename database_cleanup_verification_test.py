#!/usr/bin/env python3
"""
Database Cleanup Verification Test
Testing clean database state and admin user functionality as specified in review request:

1. Database State Verification - Check that all data collections are empty
2. Admin Authentication Test - Test login with topkitfr@gmail.com / TopKitSecure789#
3. Clean Slate Confirmation - GET endpoints should return empty arrays
4. System Readiness - Verify all endpoints are functional
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-collab-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class DatabaseCleanupVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
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
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Test admin authentication with specified credentials"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                
                if self.admin_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    
                    # Verify admin role
                    admin_role = user_data.get('role') == 'admin'
                    admin_name = user_data.get('name', 'Unknown')
                    
                    self.log_result(
                        "Admin Authentication Test", 
                        True, 
                        f"Successfully authenticated admin user: {admin_name} (Role: {user_data.get('role')}, Token length: {len(self.admin_token)})"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication Test", False, "", "No token in response")
                    return False
            else:
                self.log_result(
                    "Admin Authentication Test", 
                    False, 
                    "", 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication Test", False, "", str(e))
            return False

    def verify_database_collections_empty(self):
        """Verify that all specified data collections are empty"""
        collections_to_check = [
            ("/teams", "teams"),
            ("/brands", "brands"), 
            ("/players", "players"),
            ("/competitions", "competitions"),
            ("/master-jerseys", "master_jerseys"),
            ("/reference-kits", "reference_kits"),
            ("/contributions", "contributions"),
            ("/contributions-v2/", "contributions_v2")
        ]
        
        all_empty = True
        collection_status = {}
        
        for endpoint, collection_name in collections_to_check:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different response formats
                    if isinstance(data, list):
                        count = len(data)
                    elif isinstance(data, dict):
                        # Check for common array keys
                        count = len(data.get('items', data.get('data', data.get(collection_name, []))))
                    else:
                        count = 0
                    
                    is_empty = count == 0
                    collection_status[collection_name] = {"count": count, "empty": is_empty}
                    
                    if not is_empty:
                        all_empty = False
                    
                    self.log_result(
                        f"Database Collection Check - {collection_name}",
                        is_empty,
                        f"Collection has {count} items ({'EMPTY' if is_empty else 'NOT EMPTY'})",
                        "" if is_empty else f"Expected empty collection but found {count} items"
                    )
                else:
                    self.log_result(
                        f"Database Collection Check - {collection_name}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_empty = False
                    
            except Exception as e:
                self.log_result(f"Database Collection Check - {collection_name}", False, "", str(e))
                all_empty = False
        
        # Summary of database state
        empty_collections = [name for name, status in collection_status.items() if status["empty"]]
        non_empty_collections = [f"{name}({status['count']})" for name, status in collection_status.items() if not status["empty"]]
        
        self.log_result(
            "Overall Database State Verification",
            all_empty,
            f"Empty collections: {len(empty_collections)}/{len(collection_status)} - {', '.join(empty_collections) if empty_collections else 'None'}",
            f"Non-empty collections: {', '.join(non_empty_collections)}" if non_empty_collections else ""
        )
        
        return all_empty, collection_status

    def verify_only_admin_user_exists(self):
        """Verify only the admin user exists in users collection"""
        try:
            response = self.session.get(f"{API_BASE}/admin/users")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                total_users = len(users)
                
                # Check if only admin user exists
                admin_users = [user for user in users if user.get('email') == ADMIN_EMAIL]
                other_users = [user for user in users if user.get('email') != ADMIN_EMAIL]
                
                only_admin_exists = total_users == 1 and len(admin_users) == 1
                
                if only_admin_exists:
                    admin_user = admin_users[0]
                    self.log_result(
                        "Admin User Verification",
                        True,
                        f"Only admin user exists: {admin_user.get('name')} ({admin_user.get('email')}) with role: {admin_user.get('role')}"
                    )
                else:
                    other_user_details = [f"{user.get('name')} ({user.get('email')})" for user in other_users]
                    self.log_result(
                        "Admin User Verification",
                        False,
                        f"Found {total_users} total users, {len(admin_users)} admin users, {len(other_users)} other users",
                        f"Expected only admin user but found: {', '.join(other_user_details)}" if other_users else "Admin user not found"
                    )
                
                return only_admin_exists, users
            else:
                self.log_result(
                    "Admin User Verification",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False, []
                
        except Exception as e:
            self.log_result("Admin User Verification", False, "", str(e))
            return False, []

    def test_clean_slate_endpoints(self):
        """Test that specified endpoints return empty arrays"""
        endpoints_to_test = [
            ("/teams", "GET /api/teams"),
            ("/brands", "GET /api/brands"),
            ("/contributions-v2/", "GET /api/contributions-v2/"),
            ("/vestiaire", "GET /api/vestiaire")
        ]
        
        all_empty = True
        endpoint_results = {}
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different response formats
                    if isinstance(data, list):
                        count = len(data)
                        is_empty = count == 0
                    elif isinstance(data, dict):
                        # Check for common array keys
                        items = data.get('items', data.get('data', data.get('results', [])))
                        count = len(items) if isinstance(items, list) else 0
                        is_empty = count == 0
                    else:
                        count = 0
                        is_empty = True
                    
                    endpoint_results[endpoint] = {"count": count, "empty": is_empty}
                    
                    if not is_empty:
                        all_empty = False
                    
                    self.log_result(
                        f"Clean Slate Confirmation - {description}",
                        is_empty,
                        f"Returned {count} items ({'empty array' if is_empty else 'NOT EMPTY'})",
                        "" if is_empty else f"Expected empty array but got {count} items"
                    )
                else:
                    self.log_result(
                        f"Clean Slate Confirmation - {description}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_empty = False
                    
            except Exception as e:
                self.log_result(f"Clean Slate Confirmation - {description}", False, "", str(e))
                all_empty = False
        
        return all_empty, endpoint_results

    def test_system_readiness(self):
        """Verify all endpoints are functional and ready for new data"""
        system_endpoints = [
            ("/teams", "GET", "Teams endpoint"),
            ("/brands", "GET", "Brands endpoint"),
            ("/players", "GET", "Players endpoint"),
            ("/competitions", "GET", "Competitions endpoint"),
            ("/master-jerseys", "GET", "Master jerseys endpoint"),
            ("/vestiaire", "GET", "Vestiaire/Kit Store endpoint"),
            ("/contributions-v2/", "GET", "Community DB endpoint"),
            ("/admin/settings", "GET", "Admin settings endpoint"),
            ("/admin/dashboard-stats", "GET", "Admin dashboard stats")
        ]
        
        all_functional = True
        functional_count = 0
        
        for endpoint, method, description in system_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    functional_count += 1
                    self.log_result(
                        f"System Readiness - {description}",
                        True,
                        f"Endpoint functional and ready (HTTP 200)"
                    )
                else:
                    self.log_result(
                        f"System Readiness - {description}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_functional = False
                    
            except Exception as e:
                self.log_result(f"System Readiness - {description}", False, "", str(e))
                all_functional = False
        
        # Overall system readiness summary
        total_endpoints = len(system_endpoints)
        readiness_percentage = (functional_count / total_endpoints * 100) if total_endpoints > 0 else 0
        
        self.log_result(
            "Overall System Readiness",
            all_functional,
            f"{functional_count}/{total_endpoints} endpoints functional ({readiness_percentage:.1f}%)",
            f"{total_endpoints - functional_count} endpoints not functional" if not all_functional else ""
        )
        
        return all_functional, functional_count, total_endpoints

    def test_enhanced_topkit_system_with_clean_database(self):
        """Test that the enhanced TopKit system works with clean database"""
        try:
            # Test admin settings access
            settings_response = self.session.get(f"{API_BASE}/admin/settings")
            settings_working = settings_response.status_code == 200
            
            # Test dashboard stats
            stats_response = self.session.get(f"{API_BASE}/admin/dashboard-stats")
            stats_working = stats_response.status_code == 200
            
            if stats_working:
                stats_data = stats_response.json()
                content_stats = stats_data.get('content', {})
                
                # Verify all content counts are 0 (clean database)
                expected_zero_counts = {
                    'teams': content_stats.get('teams', -1),
                    'competitions': content_stats.get('competitions', -1),
                    'brands': content_stats.get('brands', -1),
                    'master_jerseys': content_stats.get('master_jerseys', -1),
                    'reference_kits': content_stats.get('reference_kits', -1),
                    'personal_kits': content_stats.get('personal_kits', -1),
                    'wanted_kits': content_stats.get('wanted_kits', -1)
                }
                
                all_zero = all(count == 0 for count in expected_zero_counts.values())
                non_zero_items = [f"{key}:{count}" for key, count in expected_zero_counts.items() if count != 0]
                
                self.log_result(
                    "Enhanced TopKit System - Clean Database Stats",
                    all_zero,
                    f"All content counts are zero: {all_zero}",
                    f"Non-zero counts: {', '.join(non_zero_items)}" if non_zero_items else ""
                )
            
            # Test that system is ready for new contributions
            test_contribution = {
                "entity_type": "team",
                "entity_id": None,
                "title": "Clean Database Test Team",
                "description": "Testing system readiness with clean database",
                "changes": {
                    "name": "Clean Test FC",
                    "short_name": "CTC",
                    "country": "France",
                    "city": "Paris",
                    "founded_year": 2024,
                    "team_colors": ["Blue", "White"]
                }
            }
            
            # Test contribution creation (should work with clean database)
            contrib_response = self.session.post(f"{API_BASE}/contributions-v2/", json=test_contribution)
            contrib_working = contrib_response.status_code in [200, 201]
            
            if contrib_working:
                contrib_data = contrib_response.json()
                contribution_id = contrib_data.get('id')
                
                self.log_result(
                    "Enhanced TopKit System - New Data Creation",
                    True,
                    f"Successfully created test contribution with clean database (ID: {contribution_id})"
                )
            else:
                self.log_result(
                    "Enhanced TopKit System - New Data Creation",
                    False,
                    "",
                    f"Failed to create contribution: HTTP {contrib_response.status_code}: {contrib_response.text}"
                )
            
            system_working = settings_working and stats_working and contrib_working
            
            self.log_result(
                "Enhanced TopKit System Compatibility",
                system_working,
                f"System components working: Settings({settings_working}), Stats({stats_working}), Contributions({contrib_working})",
                "Some system components not working with clean database" if not system_working else ""
            )
            
            return system_working
            
        except Exception as e:
            self.log_result("Enhanced TopKit System Test", False, "", str(e))
            return False

    def run_database_cleanup_verification(self):
        """Run complete database cleanup verification as specified in review request"""
        print("🧹 Starting Database Cleanup Verification Test")
        print("Verifying clean database state and admin user functionality")
        print("=" * 80)
        
        # Step 1: Admin Authentication Test
        print("\n🔐 STEP 1: Admin Authentication Test")
        print("-" * 50)
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Database State Verification
        print("\n🗄️ STEP 2: Database State Verification")
        print("-" * 50)
        all_empty, collection_status = self.verify_database_collections_empty()
        
        # Step 3: Admin User Verification
        print("\n👤 STEP 3: Admin User Verification")
        print("-" * 50)
        only_admin, users = self.verify_only_admin_user_exists()
        
        # Step 4: Clean Slate Confirmation
        print("\n✨ STEP 4: Clean Slate Confirmation")
        print("-" * 50)
        endpoints_empty, endpoint_results = self.test_clean_slate_endpoints()
        
        # Step 5: System Readiness
        print("\n🚀 STEP 5: System Readiness")
        print("-" * 50)
        system_ready, functional_count, total_endpoints = self.test_system_readiness()
        
        # Step 6: Enhanced TopKit System Test
        print("\n⚡ STEP 6: Enhanced TopKit System Test")
        print("-" * 50)
        enhanced_system_working = self.test_enhanced_topkit_system_with_clean_database()
        
        # Generate comprehensive summary
        self.generate_cleanup_verification_summary(
            all_empty, only_admin, endpoints_empty, system_ready, enhanced_system_working,
            collection_status, users, endpoint_results, functional_count, total_endpoints
        )
        
        return True

    def generate_cleanup_verification_summary(self, all_empty, only_admin, endpoints_empty, 
                                            system_ready, enhanced_system_working,
                                            collection_status, users, endpoint_results, 
                                            functional_count, total_endpoints):
        """Generate comprehensive summary for database cleanup verification"""
        print("\n" + "=" * 80)
        print("📊 DATABASE CLEANUP VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Review Request Requirements Status
        print(f"\n📋 REVIEW REQUEST REQUIREMENTS STATUS:")
        print("-" * 50)
        
        requirements = [
            ("1. Database State Verification", all_empty, "All data collections are empty"),
            ("2. Admin Authentication Test", True, "Admin login working with topkitfr@gmail.com"),
            ("3. Clean Slate Confirmation", endpoints_empty, "GET endpoints return empty arrays"),
            ("4. System Readiness", system_ready, "All endpoints functional and ready"),
            ("5. Enhanced TopKit System", enhanced_system_working, "System works with clean database")
        ]
        
        for req_name, status, description in requirements:
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {req_name}: {description}")
        
        # Detailed Results
        print(f"\n📈 DETAILED RESULTS:")
        print("-" * 50)
        
        # Database Collections Status
        if collection_status:
            empty_collections = [name for name, status in collection_status.items() if status["empty"]]
            non_empty_collections = [(name, status["count"]) for name, status in collection_status.items() if not status["empty"]]
            
            print(f"Database Collections:")
            print(f"  ✅ Empty: {len(empty_collections)}/{len(collection_status)} ({', '.join(empty_collections) if empty_collections else 'None'})")
            if non_empty_collections:
                print(f"  ❌ Non-empty: {', '.join([f'{name}({count})' for name, count in non_empty_collections])}")
        
        # User Status
        if users:
            admin_users = [user for user in users if user.get('email') == ADMIN_EMAIL]
            other_users = [user for user in users if user.get('email') != ADMIN_EMAIL]
            print(f"Users:")
            print(f"  ✅ Admin users: {len(admin_users)} (Expected: 1)")
            print(f"  {'✅' if len(other_users) == 0 else '❌'} Other users: {len(other_users)} (Expected: 0)")
        
        # System Readiness
        print(f"System Readiness:")
        print(f"  {'✅' if system_ready else '❌'} Functional endpoints: {functional_count}/{total_endpoints} ({(functional_count/total_endpoints*100):.1f}%)")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        print("-" * 50)
        
        all_requirements_met = all_empty and only_admin and endpoints_empty and system_ready and enhanced_system_working
        
        if all_requirements_met and success_rate >= 95:
            print("🎉 EXCELLENT: Database cleanup verification SUCCESSFUL!")
            print("   ✅ All data collections are empty")
            print("   ✅ Only admin user exists")
            print("   ✅ All endpoints return empty arrays")
            print("   ✅ System is ready for fresh usage")
            print("   ✅ Enhanced TopKit system works with clean database")
            print("\n✅ CONCLUSION: Database cleanup was successful and system is ready for fresh usage!")
        elif success_rate >= 80:
            print("⚠️ MOSTLY SUCCESSFUL: Database cleanup mostly verified with minor issues")
            print("   Most requirements met but some issues detected")
        else:
            print("❌ ISSUES DETECTED: Database cleanup verification found problems")
            print("   Significant issues need attention")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if not all_empty:
            print("   🧹 Some collections are not empty - consider additional cleanup")
        if not only_admin:
            print("   👤 Multiple users exist - verify if this is intended")
        if not endpoints_empty:
            print("   📡 Some endpoints return non-empty data - check data consistency")
        if not system_ready:
            print("   🔧 Some endpoints not functional - check system health")
        if not enhanced_system_working:
            print("   ⚡ Enhanced TopKit system issues - verify system configuration")
        
        if all_requirements_met:
            print("   🚀 System is ready for production use with clean database!")

if __name__ == "__main__":
    tester = DatabaseCleanupVerificationTester()
    tester.run_database_cleanup_verification()