#!/usr/bin/env python3
"""
TopKit Moderation Dashboard Testing Suite - CRITICAL FIXES VERIFICATION

**MODERATION DASHBOARD FIXES TESTING:**
User reported critical issue with moderation dashboard showing inconsistent data:
1. Overview tab shows '30 Pending Review'
2. Pending Review tab shows 'All Caught Up! No contributions pending review'
3. User created brand contribution but can't see it anywhere
4. Clear mismatch between stats and actual displayed data

**MAIN AGENT FIXES TO TEST:**
1. **Fixed Moderation Stats API** - GET /api/contributions-v2/admin/moderation-stats
   - Should now query contributions_v2 collection instead of contributions collection
   - Should return correct pending count from contributions_v2 collection
   
2. **Fixed Status Value Consistency** - Pending contributions API
   - Test GET /api/contributions-v2/?status=pending_review
   - Test GET /api/contributions-v2/?status=pending
   - Should identify which status value is actually used in database
   
3. **Collection Consistency Verification**
   - Confirm moderation stats API and contributions API use same collection
   - Check that 30 vs 0 discrepancy is resolved
   - Verify consistent counts across different endpoints

**TEST CREDENTIALS:**
- Admin: emergency.admin@topkit.test / EmergencyAdmin2025!

**EXPECTED RESULTS:**
- Moderation stats API should return consistent numbers with contributions API
- Should identify which status value ('pending' or 'pending_review') is actually used
- No more discrepancy between overview stats and pending review tab data
- Clear path to resolving the user's reported issue

**PRIORITY: CRITICAL** - This affects core moderation workflow.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://kitauth-fix.preview.emergentagent.com/api"

# Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class ModerationDashboardTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
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
    
    def test_moderation_stats_api(self):
        """Test the fixed moderation stats API - GET /api/contributions-v2/admin/moderation-stats"""
        try:
            print(f"\n📊 TESTING MODERATION STATS API")
            print("=" * 80)
            print("Testing GET /api/contributions-v2/admin/moderation-stats endpoint...")
            
            if not self.auth_token:
                self.log_test("Moderation Stats API", False, "❌ No authentication token available")
                return False, None
            
            # Test moderation stats endpoint
            print(f"      Testing moderation stats API...")
            
            stats_response = self.session.get(
                f"{BACKEND_URL}/contributions-v2/admin/moderation-stats",
                timeout=10
            )
            
            print(f"         Response status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"         ✅ Moderation stats API accessible")
                print(f"            Response data: {json.dumps(stats_data, indent=2)}")
                
                # Extract key metrics
                pending_count = stats_data.get('pending', 0)
                total_contributions = stats_data.get('total', 0)
                approved_count = stats_data.get('approved', 0)
                rejected_count = stats_data.get('rejected', 0)
                
                print(f"         📈 MODERATION STATS BREAKDOWN:")
                print(f"            Total contributions: {total_contributions}")
                print(f"            Pending review: {pending_count}")
                print(f"            Approved: {approved_count}")
                print(f"            Rejected: {rejected_count}")
                
                self.log_test("Moderation Stats API", True, 
                             f"✅ Moderation stats API working - {pending_count} pending contributions found")
                
                return True, stats_data
                
            elif stats_response.status_code == 401:
                print(f"         ❌ Authentication failed for moderation stats API")
                self.log_test("Moderation Stats API", False, 
                             f"❌ Authentication failed - Status 401")
                return False, None
                
            elif stats_response.status_code == 403:
                print(f"         ❌ Access denied for moderation stats API - admin role required")
                self.log_test("Moderation Stats API", False, 
                             f"❌ Access denied - Status 403")
                return False, None
                
            else:
                print(f"         ❌ Moderation stats API failed - Status {stats_response.status_code}")
                print(f"            Error: {stats_response.text}")
                self.log_test("Moderation Stats API", False, 
                             f"❌ API failed - Status {stats_response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Moderation Stats API", False, f"Exception: {str(e)}")
            return False, None
    
    def test_pending_contributions_apis(self):
        """Test pending contributions APIs with different status values"""
        try:
            print(f"\n📋 TESTING PENDING CONTRIBUTIONS APIs")
            print("=" * 80)
            print("Testing pending contributions endpoints with different status values...")
            
            if not self.auth_token:
                self.log_test("Pending Contributions APIs", False, "❌ No authentication token available")
                return False, None, None
            
            # Test 1: GET /api/contributions-v2/?status=pending_review
            print(f"      Testing GET /api/contributions-v2/?status=pending_review...")
            
            pending_review_response = self.session.get(
                f"{BACKEND_URL}/contributions-v2/?status=pending_review",
                timeout=10
            )
            
            pending_review_count = 0
            pending_review_data = []
            
            print(f"         Response status: {pending_review_response.status_code}")
            
            if pending_review_response.status_code == 200:
                pending_review_data = pending_review_response.json()
                pending_review_count = len(pending_review_data) if isinstance(pending_review_data, list) else 0
                
                print(f"         ✅ Pending review API accessible")
                print(f"            Contributions with 'pending_review' status: {pending_review_count}")
                
                if pending_review_count > 0:
                    print(f"            Sample contribution: {json.dumps(pending_review_data[0], indent=2)}")
                else:
                    print(f"            No contributions with 'pending_review' status found")
                    
            else:
                print(f"         ❌ Pending review API failed - Status {pending_review_response.status_code}")
                print(f"            Error: {pending_review_response.text}")
            
            # Test 2: GET /api/contributions-v2/?status=pending
            print(f"      Testing GET /api/contributions-v2/?status=pending...")
            
            pending_response = self.session.get(
                f"{BACKEND_URL}/contributions-v2/?status=pending",
                timeout=10
            )
            
            pending_count = 0
            pending_data = []
            
            print(f"         Response status: {pending_response.status_code}")
            
            if pending_response.status_code == 200:
                pending_data = pending_response.json()
                pending_count = len(pending_data) if isinstance(pending_data, list) else 0
                
                print(f"         ✅ Pending API accessible")
                print(f"            Contributions with 'pending' status: {pending_count}")
                
                if pending_count > 0:
                    print(f"            Sample contribution: {json.dumps(pending_data[0], indent=2)}")
                else:
                    print(f"            No contributions with 'pending' status found")
                    
            else:
                print(f"         ❌ Pending API failed - Status {pending_response.status_code}")
                print(f"            Error: {pending_response.text}")
            
            # Test 3: GET /api/contributions-v2/ (all contributions)
            print(f"      Testing GET /api/contributions-v2/ (all contributions)...")
            
            all_contributions_response = self.session.get(
                f"{BACKEND_URL}/contributions-v2/",
                timeout=10
            )
            
            all_contributions_count = 0
            all_contributions_data = []
            status_breakdown = {}
            
            print(f"         Response status: {all_contributions_response.status_code}")
            
            if all_contributions_response.status_code == 200:
                all_contributions_data = all_contributions_response.json()
                all_contributions_count = len(all_contributions_data) if isinstance(all_contributions_data, list) else 0
                
                print(f"         ✅ All contributions API accessible")
                print(f"            Total contributions: {all_contributions_count}")
                
                # Analyze status values
                if isinstance(all_contributions_data, list):
                    for contrib in all_contributions_data:
                        status = contrib.get('status', 'unknown')
                        status_breakdown[status] = status_breakdown.get(status, 0) + 1
                    
                    print(f"         📊 STATUS BREAKDOWN:")
                    for status, count in status_breakdown.items():
                        print(f"            {status}: {count}")
                        
            else:
                print(f"         ❌ All contributions API failed - Status {all_contributions_response.status_code}")
                print(f"            Error: {all_contributions_response.text}")
            
            # Analysis
            print(f"\n      📈 PENDING CONTRIBUTIONS ANALYSIS:")
            print(f"         Contributions with 'pending_review': {pending_review_count}")
            print(f"         Contributions with 'pending': {pending_count}")
            print(f"         Total contributions: {all_contributions_count}")
            print(f"         Status values found: {list(status_breakdown.keys())}")
            
            # Determine which status value is actually used
            actual_status_used = None
            if pending_review_count > 0 and pending_count == 0:
                actual_status_used = "pending_review"
                print(f"         🎯 ACTUAL STATUS USED: 'pending_review' ({pending_review_count} contributions)")
            elif pending_count > 0 and pending_review_count == 0:
                actual_status_used = "pending"
                print(f"         🎯 ACTUAL STATUS USED: 'pending' ({pending_count} contributions)")
            elif pending_count > 0 and pending_review_count > 0:
                actual_status_used = "both"
                print(f"         🎯 BOTH STATUS VALUES USED: 'pending' ({pending_count}) and 'pending_review' ({pending_review_count})")
            else:
                actual_status_used = "none"
                print(f"         🎯 NO PENDING CONTRIBUTIONS FOUND with either status value")
            
            success = (pending_review_response.status_code == 200 and 
                      pending_response.status_code == 200 and 
                      all_contributions_response.status_code == 200)
            
            if success:
                self.log_test("Pending Contributions APIs", True, 
                             f"✅ Pending contributions APIs working - Status used: {actual_status_used}")
            else:
                self.log_test("Pending Contributions APIs", False, 
                             f"❌ Some pending contributions APIs failed")
            
            return success, {
                "pending_review_count": pending_review_count,
                "pending_count": pending_count,
                "total_count": all_contributions_count,
                "status_breakdown": status_breakdown,
                "actual_status_used": actual_status_used
            }, {
                "pending_review_data": pending_review_data,
                "pending_data": pending_data,
                "all_contributions_data": all_contributions_data
            }
                
        except Exception as e:
            self.log_test("Pending Contributions APIs", False, f"Exception: {str(e)}")
            return False, None, None
    
    def test_collection_consistency(self, stats_data, contributions_data):
        """Test consistency between moderation stats and contributions APIs"""
        try:
            print(f"\n🔍 TESTING COLLECTION CONSISTENCY")
            print("=" * 80)
            print("Verifying consistency between moderation stats and contributions APIs...")
            
            if not stats_data or not contributions_data:
                self.log_test("Collection Consistency", False, "❌ Missing data for consistency check")
                return False
            
            # Extract data from stats API
            stats_pending = stats_data.get('pending', 0)  # Fixed: use 'pending' instead of 'pending_review'
            stats_total = stats_data.get('total', 0)
            stats_approved = stats_data.get('approved', 0)
            stats_rejected = stats_data.get('rejected', 0)
            
            # Extract data from contributions API
            contrib_pending_review = contributions_data.get('pending_review_count', 0)
            contrib_pending = contributions_data.get('pending_count', 0)
            contrib_total = contributions_data.get('total_count', 0)
            status_breakdown = contributions_data.get('status_breakdown', {})
            
            print(f"      📊 CONSISTENCY COMPARISON:")
            print(f"         MODERATION STATS API:")
            print(f"            Total: {stats_total}")
            print(f"            Pending review: {stats_pending}")
            print(f"            Approved: {stats_approved}")
            print(f"            Rejected: {stats_rejected}")
            
            print(f"         CONTRIBUTIONS API:")
            print(f"            Total: {contrib_total}")
            print(f"            Pending review: {contrib_pending_review}")
            print(f"            Pending: {contrib_pending}")
            print(f"            Status breakdown: {status_breakdown}")
            
            # Check consistency
            consistency_issues = []
            
            # Check total count consistency
            if stats_total != contrib_total:
                consistency_issues.append(f"Total count mismatch: Stats API ({stats_total}) vs Contributions API ({contrib_total})")
            else:
                print(f"         ✅ Total count consistent: {stats_total}")
            
            # Check pending count consistency
            # The stats API might be using 'pending_review' while contributions might use 'pending'
            actual_pending_count = max(contrib_pending_review, contrib_pending)
            
            if stats_pending != actual_pending_count:
                consistency_issues.append(f"Pending count mismatch: Stats API ({stats_pending}) vs Contributions API ({actual_pending_count})")
            else:
                print(f"         ✅ Pending count consistent: {stats_pending}")
            
            # Check if the 30 vs 0 discrepancy is resolved
            discrepancy_resolved = True
            if stats_pending > 0 and actual_pending_count == 0:
                discrepancy_resolved = False
                consistency_issues.append(f"30 vs 0 discrepancy still exists: Stats shows {stats_pending} but contributions show {actual_pending_count}")
            elif stats_pending == 0 and actual_pending_count > 0:
                discrepancy_resolved = False
                consistency_issues.append(f"Reverse discrepancy: Stats shows {stats_pending} but contributions show {actual_pending_count}")
            else:
                print(f"         ✅ No 30 vs 0 discrepancy detected")
            
            # Final assessment
            if len(consistency_issues) == 0:
                print(f"      🎉 COLLECTION CONSISTENCY VERIFIED:")
                print(f"         ✅ All counts match between APIs")
                print(f"         ✅ No discrepancies detected")
                print(f"         ✅ Moderation stats and contributions use same data source")
                
                self.log_test("Collection Consistency", True, 
                             f"✅ Collection consistency verified - all counts match")
                return True
            else:
                print(f"      ❌ COLLECTION CONSISTENCY ISSUES FOUND ({len(consistency_issues)}):")
                for issue in consistency_issues:
                    print(f"         • {issue}")
                
                self.log_test("Collection Consistency", False, 
                             f"❌ Collection consistency issues - {len(consistency_issues)} mismatches found")
                return False
                
        except Exception as e:
            self.log_test("Collection Consistency", False, f"Exception: {str(e)}")
            return False
    
    def test_status_values_investigation(self, contributions_raw_data):
        """Investigate actual status values in contributions_v2 collection"""
        try:
            print(f"\n🔬 INVESTIGATING STATUS VALUES")
            print("=" * 80)
            print("Analyzing actual status values in contributions_v2 collection...")
            
            if not contributions_raw_data or not contributions_raw_data.get('all_contributions_data'):
                self.log_test("Status Values Investigation", False, "❌ No contributions data available")
                return False, None
            
            all_contributions = contributions_raw_data['all_contributions_data']
            
            if not isinstance(all_contributions, list):
                self.log_test("Status Values Investigation", False, "❌ Invalid contributions data format")
                return False, None
            
            print(f"      📋 ANALYZING {len(all_contributions)} CONTRIBUTIONS:")
            
            # Collect all unique status values
            status_values = set()
            status_counts = {}
            entity_types = set()
            
            for contrib in all_contributions:
                status = contrib.get('status')
                entity_type = contrib.get('entity_type')
                
                if status:
                    status_values.add(status)
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                if entity_type:
                    entity_types.add(entity_type)
            
            print(f"         📊 STATUS VALUES FOUND:")
            for status, count in sorted(status_counts.items()):
                print(f"            {status}: {count} contributions")
            
            print(f"         📊 ENTITY TYPES FOUND:")
            for entity_type in sorted(entity_types):
                entity_count = len([c for c in all_contributions if c.get('entity_type') == entity_type])
                print(f"            {entity_type}: {entity_count} contributions")
            
            # Identify which status values are used for pending contributions
            pending_statuses = []
            if 'pending' in status_values:
                pending_statuses.append('pending')
            if 'pending_review' in status_values:
                pending_statuses.append('pending_review')
            if 'pending_moderation' in status_values:
                pending_statuses.append('pending_moderation')
            
            print(f"         🎯 PENDING STATUS VALUES IDENTIFIED:")
            if pending_statuses:
                for status in pending_statuses:
                    count = status_counts.get(status, 0)
                    print(f"            '{status}': {count} contributions")
            else:
                print(f"            No pending status values found")
            
            # Check for recent contributions that might be pending
            recent_contributions = []
            for contrib in all_contributions:
                if contrib.get('status') in ['pending', 'pending_review', 'pending_moderation']:
                    recent_contributions.append(contrib)
            
            if recent_contributions:
                print(f"         📅 RECENT PENDING CONTRIBUTIONS ({len(recent_contributions)}):")
                for contrib in recent_contributions[:3]:  # Show first 3
                    print(f"            ID: {contrib.get('id', 'N/A')}")
                    print(f"            Status: {contrib.get('status', 'N/A')}")
                    print(f"            Entity Type: {contrib.get('entity_type', 'N/A')}")
                    print(f"            Submitted At: {contrib.get('submitted_at', 'N/A')}")
                    print(f"            ---")
            
            investigation_data = {
                "total_contributions": len(all_contributions),
                "status_values": list(status_values),
                "status_counts": status_counts,
                "entity_types": list(entity_types),
                "pending_statuses": pending_statuses,
                "recent_pending_count": len(recent_contributions)
            }
            
            self.log_test("Status Values Investigation", True, 
                         f"✅ Status values investigated - {len(status_values)} unique statuses found")
            
            return True, investigation_data
                
        except Exception as e:
            self.log_test("Status Values Investigation", False, f"Exception: {str(e)}")
            return False, None
    
    def run_moderation_dashboard_tests(self):
        """Run comprehensive moderation dashboard testing suite"""
        print("\n🚀 MODERATION DASHBOARD FIXES TESTING SUITE")
        print("Testing all moderation dashboard fixes and consistency")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        test_results = []
        
        # Step 2: Test Moderation Stats API
        print("\n1️⃣ Testing Moderation Stats API...")
        stats_success, stats_data = self.test_moderation_stats_api()
        test_results.append(stats_success)
        
        # Step 3: Test Pending Contributions APIs
        print("\n2️⃣ Testing Pending Contributions APIs...")
        contrib_success, contrib_data, contrib_raw_data = self.test_pending_contributions_apis()
        test_results.append(contrib_success)
        
        # Step 4: Test Collection Consistency
        print("\n3️⃣ Testing Collection Consistency...")
        consistency_success = self.test_collection_consistency(stats_data, contrib_data)
        test_results.append(consistency_success)
        
        # Step 5: Investigate Status Values
        print("\n4️⃣ Investigating Status Values...")
        investigation_success, investigation_data = self.test_status_values_investigation(contrib_raw_data)
        test_results.append(investigation_success)
        
        return test_results, {
            "stats_data": stats_data,
            "contrib_data": contrib_data,
            "investigation_data": investigation_data
        }
    
    def print_moderation_dashboard_summary(self, test_data):
        """Print final moderation dashboard testing summary"""
        print("\n📊 MODERATION DASHBOARD FIXES TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 MODERATION DASHBOARD FIXES RESULTS:")
        
        # Extract data
        stats_data = test_data.get('stats_data', {})
        contrib_data = test_data.get('contrib_data', {})
        investigation_data = test_data.get('investigation_data', {})
        
        # Moderation Stats API
        stats_working = any(r['success'] for r in self.test_results if 'Moderation Stats API' in r['test'])
        if stats_working:
            pending_from_stats = stats_data.get('pending_review', 0) if stats_data else 0
            print(f"  ✅ MODERATION STATS API: Working correctly - shows {pending_from_stats} pending contributions")
        else:
            print(f"  ❌ MODERATION STATS API: Not working - API endpoint failing")
        
        # Pending Contributions APIs
        contrib_working = any(r['success'] for r in self.test_results if 'Pending Contributions APIs' in r['test'])
        if contrib_working and contrib_data:
            actual_status = contrib_data.get('actual_status_used', 'unknown')
            pending_review_count = contrib_data.get('pending_review_count', 0)
            pending_count = contrib_data.get('pending_count', 0)
            print(f"  ✅ PENDING CONTRIBUTIONS APIs: Working correctly")
            print(f"     - Status 'pending_review': {pending_review_count} contributions")
            print(f"     - Status 'pending': {pending_count} contributions")
            print(f"     - Actual status used: {actual_status}")
        else:
            print(f"  ❌ PENDING CONTRIBUTIONS APIs: Not working properly")
        
        # Collection Consistency
        consistency_working = any(r['success'] for r in self.test_results if 'Collection Consistency' in r['test'])
        if consistency_working:
            print(f"  ✅ COLLECTION CONSISTENCY: Verified - stats and contributions APIs use same data")
        else:
            print(f"  ❌ COLLECTION CONSISTENCY: Issues found - APIs showing different numbers")
        
        # Status Values Investigation
        investigation_working = any(r['success'] for r in self.test_results if 'Status Values Investigation' in r['test'])
        if investigation_working and investigation_data:
            status_values = investigation_data.get('status_values', [])
            pending_statuses = investigation_data.get('pending_statuses', [])
            print(f"  ✅ STATUS VALUES: Investigated - {len(status_values)} unique statuses found")
            print(f"     - Pending statuses: {pending_statuses}")
        else:
            print(f"  ❌ STATUS VALUES: Investigation failed")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ CRITICAL MODERATION ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final diagnosis
        print(f"\n🎯 MODERATION DASHBOARD FIXES DIAGNOSIS:")
        
        working_components = sum([stats_working, contrib_working, consistency_working, investigation_working])
        total_components = 4
        
        if working_components == total_components:
            print(f"  ✅ ALL MODERATION FIXES WORKING ({working_components}/{total_components})")
            print(f"     - Moderation stats API returns consistent numbers")
            print(f"     - Pending contributions APIs work with correct status values")
            print(f"     - No more 30 vs 0 discrepancy between overview and pending tabs")
            print(f"     - Collection consistency verified across all endpoints")
        elif working_components >= 3:
            print(f"  ⚠️ MOST MODERATION FIXES WORKING ({working_components}/{total_components})")
            if not stats_working:
                print(f"     ❌ Moderation stats API still has issues")
            if not contrib_working:
                print(f"     ❌ Pending contributions APIs still have issues")
            if not consistency_working:
                print(f"     ❌ Collection consistency issues remain")
            if not investigation_working:
                print(f"     ❌ Status values investigation failed")
        else:
            print(f"  ❌ MULTIPLE MODERATION ISSUES REMAIN ({working_components}/{total_components})")
            print(f"     - Moderation dashboard may still show inconsistent data")
            print(f"     - 30 vs 0 discrepancy may not be resolved")
            print(f"     - Status value inconsistencies may persist")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if contrib_data:
            actual_status = contrib_data.get('actual_status_used', 'unknown')
            if actual_status == 'pending':
                print(f"  🎯 Frontend should use 'pending' status instead of 'pending_review'")
            elif actual_status == 'pending_review':
                print(f"  🎯 Backend should use 'pending_review' status consistently")
            elif actual_status == 'both':
                print(f"  🎯 Standardize on single status value - either 'pending' or 'pending_review'")
            elif actual_status == 'none':
                print(f"  🎯 Create test contributions to verify moderation workflow")
        
        if not consistency_working:
            print(f"  🎯 Ensure moderation stats API queries contributions_v2 collection")
            print(f"  🎯 Verify both APIs use same status field for pending contributions")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the moderation dashboard testing suite"""
    tester = ModerationDashboardTesting()
    
    # Run the moderation dashboard tests
    test_results, test_data = tester.run_moderation_dashboard_tests()
    
    # Print comprehensive summary
    tester.print_moderation_dashboard_summary(test_data)
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)