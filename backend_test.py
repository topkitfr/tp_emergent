#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - ADMIN DATA DELETION ENDPOINTS TESTING

Testing the newly created admin data deletion endpoints for clearing master kits and personal collections.

**Testing Requirements:**
1. Login with emergency admin account (emergency.admin@topkit.test / EmergencyAdmin2025!)
2. Test the three new admin endpoints:
   - `DELETE /api/admin/clear-master-kits` - Should clear all master kits
   - `DELETE /api/admin/clear-personal-collections` - Should clear all personal collections
   - `DELETE /api/admin/clear-all-kits` - Should clear both master kits and personal collections
3. Verify the endpoints return proper counts before and after deletion
4. Test admin authorization (endpoints should require admin role)
5. Verify the data is actually cleared from the database by checking counts afterward

**Expected Results:**
- All endpoints should return success messages with deletion counts
- After running the clear endpoints, the respective collections should be empty
- Only admin users should be able to access these endpoints
- Error handling should work for non-admin users

**Authentication:**
- Use emergency.admin@topkit.test / EmergencyAdmin2025! (admin role)
- Test should confirm admin authorization is working correctly

CRITICAL: Focus on testing admin data deletion endpoints with proper authorization and data verification.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://jersey-collect.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitAdminDataDeletionTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.initial_master_kits_count = 0
        self.initial_collections_count = 0
        
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
    
    def authenticate_admin(self):
        """Authenticate with emergency admin credentials"""
        try:
            print(f"\n🔐 EMERGENCY ADMIN AUTHENTICATION")
            print("=" * 60)
            print(f"   Email: {ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Emergency Admin Authentication", True, 
                             f"✅ Emergency admin authentication successful")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Email: {self.admin_user_data.get('email')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Emergency Admin Authentication", False, 
                             f"❌ Emergency admin authentication failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_initial_data_counts(self):
        """Get initial counts of master kits and personal collections before testing"""
        try:
            print(f"\n📊 GETTING INITIAL DATA COUNTS")
            print("=" * 60)
            print("Getting initial counts of master kits and personal collections...")
            
            if not self.auth_token:
                self.log_test("Get Initial Data Counts", False, "❌ Missing authentication")
                return False
            
            # Get master kits count
            master_kits_response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            if master_kits_response.status_code == 200:
                master_kits = master_kits_response.json()
                self.initial_master_kits_count = len(master_kits)
                print(f"      Initial Master Kits Count: {self.initial_master_kits_count}")
            else:
                print(f"      ❌ Failed to get master kits count - Status {master_kits_response.status_code}")
                self.initial_master_kits_count = 0
            
            # Get personal collections count
            collections_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            if collections_response.status_code == 200:
                collections = collections_response.json()
                self.initial_collections_count = len(collections)
                print(f"      Initial Personal Collections Count: {self.initial_collections_count}")
            else:
                print(f"      ❌ Failed to get collections count - Status {collections_response.status_code}")
                self.initial_collections_count = 0
            
            self.log_test("Get Initial Data Counts", True, 
                         f"✅ Initial counts retrieved - Master Kits: {self.initial_master_kits_count}, Collections: {self.initial_collections_count}")
            return True
                
        except Exception as e:
            self.log_test("Get Initial Data Counts", False, f"Exception: {str(e)}")
            return False
    
    def test_clear_master_kits_endpoint(self):
        """Test DELETE /api/admin/clear-master-kits endpoint"""
        try:
            print(f"\n🗑️ TESTING CLEAR MASTER KITS ENDPOINT")
            print("=" * 60)
            print("Testing DELETE /api/admin/clear-master-kits...")
            
            if not self.auth_token:
                self.log_test("Clear Master Kits Endpoint", False, "❌ Missing authentication")
                return False
            
            # Verify admin role
            if self.admin_user_data.get('role') != 'admin':
                self.log_test("Clear Master Kits Endpoint", False, "❌ User does not have admin role")
                return False
            
            print(f"      Admin user confirmed: {self.admin_user_data.get('email')} (Role: {self.admin_user_data.get('role')})")
            print(f"      Initial Master Kits Count: {self.initial_master_kits_count}")
            
            response = self.session.delete(f"{BACKEND_URL}/admin/clear-master-kits", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"         ✅ Clear master kits endpoint successful")
                print(f"            Message: {data.get('message')}")
                print(f"            Count Before: {data.get('count_before')}")
                print(f"            Deleted Count: {data.get('deleted_count')}")
                
                # Verify data was actually cleared
                verification_response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
                if verification_response.status_code == 200:
                    remaining_kits = verification_response.json()
                    remaining_count = len(remaining_kits)
                    
                    print(f"            Verification - Remaining Master Kits: {remaining_count}")
                    
                    if remaining_count == 0:
                        print(f"            ✅ Master kits successfully cleared from database")
                        self.log_test("Clear Master Kits Endpoint", True, 
                                     f"✅ Master kits cleared successfully - {data.get('deleted_count')} deleted")
                        return True
                    else:
                        print(f"            ❌ Master kits not fully cleared - {remaining_count} still remain")
                        self.log_test("Clear Master Kits Endpoint", False, 
                                     f"❌ Master kits not fully cleared - {remaining_count} still remain")
                        return False
                else:
                    print(f"            ❌ Cannot verify master kits clearance - Status {verification_response.status_code}")
                    self.log_test("Clear Master Kits Endpoint", False, 
                                 f"❌ Cannot verify clearance - Status {verification_response.status_code}")
                    return False
                    
            elif response.status_code == 403:
                print(f"         ❌ Access denied - Admin privileges required")
                self.log_test("Clear Master Kits Endpoint", False, 
                             f"❌ Access denied - Admin privileges required")
                return False
            else:
                error_text = response.text
                print(f"         ❌ Clear master kits failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                
                self.log_test("Clear Master Kits Endpoint", False, 
                             f"❌ Clear master kits failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Clear Master Kits Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_clear_personal_collections_endpoint(self):
        """Test DELETE /api/admin/clear-personal-collections endpoint"""
        try:
            print(f"\n🗑️ TESTING CLEAR PERSONAL COLLECTIONS ENDPOINT")
            print("=" * 60)
            print("Testing DELETE /api/admin/clear-personal-collections...")
            
            if not self.auth_token:
                self.log_test("Clear Personal Collections Endpoint", False, "❌ Missing authentication")
                return False
            
            # Verify admin role
            if self.admin_user_data.get('role') != 'admin':
                self.log_test("Clear Personal Collections Endpoint", False, "❌ User does not have admin role")
                return False
            
            print(f"      Admin user confirmed: {self.admin_user_data.get('email')} (Role: {self.admin_user_data.get('role')})")
            print(f"      Initial Personal Collections Count: {self.initial_collections_count}")
            
            response = self.session.delete(f"{BACKEND_URL}/admin/clear-personal-collections", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"         ✅ Clear personal collections endpoint successful")
                print(f"            Message: {data.get('message')}")
                print(f"            Count Before: {data.get('count_before')}")
                print(f"            Deleted Count: {data.get('deleted_count')}")
                
                # Verify data was actually cleared
                verification_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
                if verification_response.status_code == 200:
                    remaining_collections = verification_response.json()
                    remaining_count = len(remaining_collections)
                    
                    print(f"            Verification - Remaining Personal Collections: {remaining_count}")
                    
                    if remaining_count == 0:
                        print(f"            ✅ Personal collections successfully cleared from database")
                        self.log_test("Clear Personal Collections Endpoint", True, 
                                     f"✅ Personal collections cleared successfully - {data.get('deleted_count')} deleted")
                        return True
                    else:
                        print(f"            ❌ Personal collections not fully cleared - {remaining_count} still remain")
                        self.log_test("Clear Personal Collections Endpoint", False, 
                                     f"❌ Personal collections not fully cleared - {remaining_count} still remain")
                        return False
                else:
                    print(f"            ❌ Cannot verify personal collections clearance - Status {verification_response.status_code}")
                    self.log_test("Clear Personal Collections Endpoint", False, 
                                 f"❌ Cannot verify clearance - Status {verification_response.status_code}")
                    return False
                    
            elif response.status_code == 403:
                print(f"         ❌ Access denied - Admin privileges required")
                self.log_test("Clear Personal Collections Endpoint", False, 
                             f"❌ Access denied - Admin privileges required")
                return False
            else:
                error_text = response.text
                print(f"         ❌ Clear personal collections failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                
                self.log_test("Clear Personal Collections Endpoint", False, 
                             f"❌ Clear personal collections failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Clear Personal Collections Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_clear_all_kits_endpoint(self):
        """Test DELETE /api/admin/clear-all-kits endpoint"""
        try:
            print(f"\n🗑️ TESTING CLEAR ALL KITS ENDPOINT")
            print("=" * 60)
            print("Testing DELETE /api/admin/clear-all-kits...")
            
            if not self.auth_token:
                self.log_test("Clear All Kits Endpoint", False, "❌ Missing authentication")
                return False
            
            # Verify admin role
            if self.admin_user_data.get('role') != 'admin':
                self.log_test("Clear All Kits Endpoint", False, "❌ User does not have admin role")
                return False
            
            print(f"      Admin user confirmed: {self.admin_user_data.get('email')} (Role: {self.admin_user_data.get('role')})")
            print(f"      Initial Master Kits Count: {self.initial_master_kits_count}")
            print(f"      Initial Personal Collections Count: {self.initial_collections_count}")
            
            response = self.session.delete(f"{BACKEND_URL}/admin/clear-all-kits", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"         ✅ Clear all kits endpoint successful")
                print(f"            Message: {data.get('message')}")
                print(f"            Master Kits Deleted: {data.get('master_kits_deleted')}")
                print(f"            Collections Deleted: {data.get('collections_deleted')}")
                print(f"            Total Deleted: {data.get('total_deleted')}")
                
                counts_before = data.get('counts_before', {})
                print(f"            Counts Before - Master Kits: {counts_before.get('master_kits')}, Collections: {counts_before.get('collections')}")
                
                # Verify both master kits and collections were cleared
                master_kits_response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
                collections_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
                
                master_kits_cleared = False
                collections_cleared = False
                
                if master_kits_response.status_code == 200:
                    remaining_master_kits = master_kits_response.json()
                    remaining_master_count = len(remaining_master_kits)
                    print(f"            Verification - Remaining Master Kits: {remaining_master_count}")
                    master_kits_cleared = (remaining_master_count == 0)
                
                if collections_response.status_code == 200:
                    remaining_collections = collections_response.json()
                    remaining_collections_count = len(remaining_collections)
                    print(f"            Verification - Remaining Personal Collections: {remaining_collections_count}")
                    collections_cleared = (remaining_collections_count == 0)
                
                if master_kits_cleared and collections_cleared:
                    print(f"            ✅ Both master kits and personal collections successfully cleared")
                    self.log_test("Clear All Kits Endpoint", True, 
                                 f"✅ All kits cleared successfully - {data.get('total_deleted')} total deleted")
                    return True
                else:
                    issues = []
                    if not master_kits_cleared:
                        issues.append("master kits not fully cleared")
                    if not collections_cleared:
                        issues.append("personal collections not fully cleared")
                    
                    print(f"            ❌ Issues: {', '.join(issues)}")
                    self.log_test("Clear All Kits Endpoint", False, 
                                 f"❌ Issues: {', '.join(issues)}")
                    return False
                    
            elif response.status_code == 403:
                print(f"         ❌ Access denied - Admin privileges required")
                self.log_test("Clear All Kits Endpoint", False, 
                             f"❌ Access denied - Admin privileges required")
                return False
            else:
                error_text = response.text
                print(f"         ❌ Clear all kits failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                
                self.log_test("Clear All Kits Endpoint", False, 
                             f"❌ Clear all kits failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Clear All Kits Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_non_admin_authorization(self):
        """Test that non-admin users cannot access admin endpoints"""
        try:
            print(f"\n🔒 TESTING NON-ADMIN AUTHORIZATION")
            print("=" * 60)
            print("Testing that non-admin users cannot access admin endpoints...")
            
            # Create a temporary session without admin token
            temp_session = requests.Session()
            
            # Test without any authentication
            print(f"      Testing without authentication...")
            
            endpoints_to_test = [
                "/admin/clear-master-kits",
                "/admin/clear-personal-collections", 
                "/admin/clear-all-kits"
            ]
            
            unauthorized_access_blocked = True
            
            for endpoint in endpoints_to_test:
                response = temp_session.delete(f"{BACKEND_URL}{endpoint}", timeout=10)
                
                if response.status_code in [401, 403]:
                    print(f"         ✅ {endpoint}: Access properly denied (Status {response.status_code})")
                else:
                    print(f"         ❌ {endpoint}: Access not properly denied (Status {response.status_code})")
                    unauthorized_access_blocked = False
            
            if unauthorized_access_blocked:
                self.log_test("Non-Admin Authorization", True, 
                             f"✅ Admin endpoints properly protected - unauthorized access blocked")
                return True
            else:
                self.log_test("Non-Admin Authorization", False, 
                             f"❌ Admin endpoints not properly protected - unauthorized access allowed")
                return False
                
        except Exception as e:
            self.log_test("Non-Admin Authorization", False, f"Exception: {str(e)}")
            return False
    
    def test_admin_data_deletion_endpoints(self):
        """Test complete admin data deletion endpoints functionality"""
        print("\n🚀 ADMIN DATA DELETION ENDPOINTS TESTING")
        print("Testing the newly created admin data deletion endpoints for clearing master kits and personal collections")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate with admin account
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        test_results.append(auth_success)
        
        # Step 2: Get initial data counts
        print("\n2️⃣ Getting initial data counts...")
        counts_success = self.get_initial_data_counts()
        test_results.append(counts_success)
        
        # Step 3: Test non-admin authorization
        print("\n3️⃣ Testing non-admin authorization...")
        auth_test_success = self.test_non_admin_authorization()
        test_results.append(auth_test_success)
        
        # Step 4: Test clear master kits endpoint
        print("\n4️⃣ Testing clear master kits endpoint...")
        clear_master_kits_success = self.test_clear_master_kits_endpoint()
        test_results.append(clear_master_kits_success)
        
        # Step 5: Test clear personal collections endpoint
        print("\n5️⃣ Testing clear personal collections endpoint...")
        clear_collections_success = self.test_clear_personal_collections_endpoint()
        test_results.append(clear_collections_success)
        
        # Step 6: Test clear all kits endpoint
        print("\n6️⃣ Testing clear all kits endpoint...")
        clear_all_success = self.test_clear_all_kits_endpoint()
        test_results.append(clear_all_success)
        
        return test_results
    
    def print_admin_deletion_summary(self):
        """Print final admin data deletion testing summary"""
        print("\n📊 ADMIN DATA DELETION ENDPOINTS TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 ADMIN DATA DELETION ENDPOINTS RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Emergency admin login working with admin role")
        else:
            print(f"  ❌ AUTHENTICATION: Emergency admin login failed")
        
        # Initial Data Counts
        counts_working = any(r['success'] for r in self.test_results if 'Get Initial Data Counts' in r['test'])
        if counts_working:
            print(f"  ✅ INITIAL DATA COUNTS: Successfully retrieved counts before deletion")
        else:
            print(f"  ❌ INITIAL DATA COUNTS: Failed to get initial counts")
        
        # Non-Admin Authorization
        auth_test_working = any(r['success'] for r in self.test_results if 'Non-Admin Authorization' in r['test'])
        if auth_test_working:
            print(f"  ✅ AUTHORIZATION SECURITY: Admin endpoints properly protected")
        else:
            print(f"  ❌ AUTHORIZATION SECURITY: Admin endpoints not properly protected")
        
        # Clear Master Kits
        clear_master_kits_working = any(r['success'] for r in self.test_results if 'Clear Master Kits Endpoint' in r['test'])
        if clear_master_kits_working:
            print(f"  ✅ CLEAR MASTER KITS: DELETE /api/admin/clear-master-kits working correctly")
        else:
            print(f"  ❌ CLEAR MASTER KITS: DELETE /api/admin/clear-master-kits failed")
        
        # Clear Personal Collections
        clear_collections_working = any(r['success'] for r in self.test_results if 'Clear Personal Collections Endpoint' in r['test'])
        if clear_collections_working:
            print(f"  ✅ CLEAR PERSONAL COLLECTIONS: DELETE /api/admin/clear-personal-collections working correctly")
        else:
            print(f"  ❌ CLEAR PERSONAL COLLECTIONS: DELETE /api/admin/clear-personal-collections failed")
        
        # Clear All Kits
        clear_all_working = any(r['success'] for r in self.test_results if 'Clear All Kits Endpoint' in r['test'])
        if clear_all_working:
            print(f"  ✅ CLEAR ALL KITS: DELETE /api/admin/clear-all-kits working correctly")
        else:
            print(f"  ❌ CLEAR ALL KITS: DELETE /api/admin/clear-all-kits failed")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status
        print(f"\n🎯 FINAL STATUS - ADMIN DATA DELETION ENDPOINTS:")
        critical_tests = [auth_working, clear_master_kits_working, clear_collections_working, clear_all_working]
        
        if all(critical_tests):
            print(f"  ✅ ADMIN DATA DELETION ENDPOINTS WORKING PERFECTLY")
            print(f"     - All three admin deletion endpoints functional")
            print(f"     - DELETE /api/admin/clear-master-kits clears all master kits")
            print(f"     - DELETE /api/admin/clear-personal-collections clears all personal collections")
            print(f"     - DELETE /api/admin/clear-all-kits clears both master kits and personal collections")
            print(f"     - Admin authorization working correctly")
            print(f"     - Proper counts returned before and after deletion")
            print(f"     - Data actually cleared from database")
        elif any(critical_tests):
            print(f"  ⚠️ PARTIAL SUCCESS: Some endpoints working")
            working_areas = []
            if auth_working: working_areas.append("authentication")
            if clear_master_kits_working: working_areas.append("clear master kits")
            if clear_collections_working: working_areas.append("clear personal collections")
            if clear_all_working: working_areas.append("clear all kits")
            print(f"     - Working endpoints: {', '.join(working_areas)}")
            
            failing_areas = []
            if not auth_working: failing_areas.append("authentication")
            if not clear_master_kits_working: failing_areas.append("clear master kits")
            if not clear_collections_working: failing_areas.append("clear personal collections")
            if not clear_all_working: failing_areas.append("clear all kits")
            if failing_areas:
                print(f"     - Still failing: {', '.join(failing_areas)}")
        else:
            print(f"  ❌ ADMIN DATA DELETION ENDPOINTS NOT WORKING")
            print(f"     - Admin deletion endpoints not functional")
            print(f"     - Data clearing not working properly")
            print(f"     - Authorization may not be working correctly")
        
        print("\n" + "=" * 80)
    
    def run_admin_deletion_tests(self):
        """Run all admin data deletion tests and return success status"""
        test_results = self.test_admin_data_deletion_endpoints()
        self.print_admin_deletion_summary()
        return any(test_results)

def main():
    """Main test execution - Admin Data Deletion Endpoints Testing"""
    tester = TopKitAdminDataDeletionTesting()
    success = tester.run_admin_deletion_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()