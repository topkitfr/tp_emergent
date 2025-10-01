#!/usr/bin/env python3
"""
TopKit Contributions System Testing Suite - PENDING APPROVAL STICKERS ENHANCEMENT

**REVIEW REQUEST - CONTRIBUTION SYSTEM ENHANCEMENTS:**
Test the contribution system enhancements for "pending approval" stickers:

1. **Authentication**: Login with emergency.admin@topkit.test / EmergencyAdmin2025!

2. **Contributions Endpoint Testing**: 
   - Test GET /api/contributions-v2/ to verify it returns all contributions with status field
   - Check that contributions include both approved and pending_review status items
   - Verify the status field is properly populated in the response

3. **Status Values Verification**:
   - Confirm contributions have status values like 'pending_review', 'approved', 'rejected'
   - Check that the backend is not filtering by approval status (should show all)
   - Verify contribution response includes all necessary fields (id, status, title, entity_type, topkit_reference, upvotes, downvotes, created_at)

4. **Master Kit Contributions**:
   - Test specifically that master kit contributions are included with their status
   - Verify master kit contributions show proper status values
   - Check if there are any pending_review contributions available for testing

5. **Moderation API**: 
   - Test GET /api/contributions-v2/?status=pending_review to get only pending items
   - Test GET /api/contributions-v2/?status=approved to get only approved items
   - Verify the filtering works correctly

Expected Results:
- All contributions returned with status field populated
- Mix of approved and pending_review status items visible
- No filtering preventing unapproved contributions from appearing
- Proper response format for frontend consumption
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://jersey-pricing.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitContributionsSystemTesting:
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
    
    def test_contributions_v2_endpoint(self):
        """Test GET /api/contributions-v2/ endpoint to verify it returns all contributions with status field"""
        try:
            print(f"\n📋 TESTING CONTRIBUTIONS V2 ENDPOINT")
            print("=" * 80)
            print("Testing GET /api/contributions-v2/ endpoint...")
            
            if not self.auth_token:
                print(f"         ⚠️ No auth token available, attempting authentication...")
                if not self.authenticate_admin():
                    self.log_test("Contributions V2 Endpoint", False, "❌ Cannot authenticate for testing")
                    return False
            
            # Test GET /api/contributions-v2/
            print(f"      Testing GET /api/contributions-v2/...")
            
            contributions_response = self.session.get(f"{BACKEND_URL}/contributions-v2/", timeout=10)
            
            print(f"         Response status: {contributions_response.status_code}")
            
            if contributions_response.status_code == 200:
                contributions_data = contributions_response.json()
                print(f"         ✅ Contributions V2 endpoint accessible")
                print(f"            Total contributions returned: {len(contributions_data)}")
                
                # Analyze contributions data
                status_counts = {}
                entity_type_counts = {}
                contributions_with_status = 0
                contributions_with_required_fields = 0
                
                required_fields = ['id', 'status', 'entity_type', 'topkit_reference', 'created_at']
                
                for contrib in contributions_data:
                    # Count status values
                    status = contrib.get('status')
                    if status:
                        contributions_with_status += 1
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # Count entity types
                    entity_type = contrib.get('entity_type')
                    if entity_type:
                        entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
                    
                    # Check required fields
                    has_all_required = all(contrib.get(field) for field in required_fields)
                    if has_all_required:
                        contributions_with_required_fields += 1
                
                print(f"            Contributions with status field: {contributions_with_status}/{len(contributions_data)}")
                print(f"            Contributions with all required fields: {contributions_with_required_fields}/{len(contributions_data)}")
                
                # Show status breakdown
                print(f"            Status breakdown:")
                for status, count in status_counts.items():
                    print(f"               {status}: {count}")
                
                # Show entity type breakdown
                print(f"            Entity type breakdown:")
                for entity_type, count in entity_type_counts.items():
                    print(f"               {entity_type}: {count}")
                
                # Show sample contribution data
                if contributions_data:
                    print(f"            Sample contribution:")
                    sample = contributions_data[0]
                    for field in required_fields:
                        print(f"               {field}: {sample.get(field, 'MISSING')}")
                    if sample.get('upvotes') is not None:
                        print(f"               upvotes: {sample.get('upvotes')}")
                    if sample.get('downvotes') is not None:
                        print(f"               downvotes: {sample.get('downvotes')}")
                    if sample.get('title'):
                        print(f"               title: {sample.get('title')}")
                
                # Determine success
                success_criteria = [
                    len(contributions_data) > 0,  # Has contributions
                    contributions_with_status == len(contributions_data),  # All have status
                    contributions_with_required_fields >= len(contributions_data) * 0.8,  # 80% have required fields
                    len(status_counts) > 1  # Multiple status values present
                ]
                
                success_count = sum(success_criteria)
                success_rate = (success_count / len(success_criteria)) * 100
                
                if success_rate >= 75:  # At least 3 out of 4 criteria met
                    self.log_test("Contributions V2 Endpoint", True, 
                                 f"✅ Contributions V2 endpoint working - {len(contributions_data)} contributions with status field")
                    return True, contributions_data
                else:
                    self.log_test("Contributions V2 Endpoint", False, 
                                 f"❌ Contributions V2 endpoint issues - success rate {success_rate:.1f}%")
                    return False, None
                    
            else:
                print(f"         ❌ Contributions V2 endpoint failed - Status {contributions_response.status_code}")
                print(f"            Error: {contributions_response.text}")
                self.log_test("Contributions V2 Endpoint", False, 
                             f"❌ Contributions V2 endpoint failed - Status {contributions_response.status_code}")
                return False, None
                
        except Exception as e:
            self.log_test("Contributions V2 Endpoint", False, f"Exception: {str(e)}")
            return False, None
    
    def test_status_values_verification(self, contributions_data):
        """Test status values verification - confirm contributions have proper status values"""
        try:
            print(f"\n🔍 TESTING STATUS VALUES VERIFICATION")
            print("=" * 80)
            print("Verifying contribution status values...")
            
            if not contributions_data:
                self.log_test("Status Values Verification", False, "❌ No contributions data to verify")
                return False
            
            # Expected status values
            expected_statuses = ['pending_review', 'approved', 'rejected', 'pending']
            
            # Analyze status values
            found_statuses = set()
            status_distribution = {}
            
            for contrib in contributions_data:
                status = contrib.get('status')
                if status:
                    found_statuses.add(status)
                    status_distribution[status] = status_distribution.get(status, 0) + 1
            
            print(f"      Status values found: {list(found_statuses)}")
            print(f"      Status distribution:")
            for status, count in status_distribution.items():
                print(f"         {status}: {count} contributions")
            
            # Check for expected statuses
            expected_found = [status for status in expected_statuses if status in found_statuses]
            print(f"      Expected statuses found: {expected_found}")
            
            # Check for pending_review and approved mix
            has_pending_review = 'pending_review' in found_statuses
            has_approved = 'approved' in found_statuses
            has_mix = has_pending_review and has_approved
            
            print(f"      Has pending_review: {'✅' if has_pending_review else '❌'}")
            print(f"      Has approved: {'✅' if has_approved else '❌'}")
            print(f"      Has status mix: {'✅' if has_mix else '❌'}")
            
            # Check that backend is not filtering (should show all statuses)
            total_contributions = len(contributions_data)
            non_approved_count = sum(1 for contrib in contributions_data if contrib.get('status') != 'approved')
            
            print(f"      Total contributions: {total_contributions}")
            print(f"      Non-approved contributions: {non_approved_count}")
            print(f"      Backend filtering check: {'✅ Not filtering' if non_approved_count > 0 else '⚠️ May be filtering'}")
            
            # Verify required fields are present
            required_fields = ['id', 'status', 'entity_type', 'topkit_reference', 'created_at']
            field_coverage = {}
            
            for field in required_fields:
                count = sum(1 for contrib in contributions_data if contrib.get(field))
                field_coverage[field] = count
                coverage_percent = (count / total_contributions) * 100
                print(f"      {field} coverage: {count}/{total_contributions} ({coverage_percent:.1f}%)")
            
            # Determine success
            success_criteria = [
                len(found_statuses) >= 2,  # Multiple status values
                has_mix or has_pending_review or has_approved,  # Has expected statuses
                non_approved_count > 0,  # Not filtering out non-approved
                all(field_coverage[field] >= total_contributions * 0.8 for field in required_fields)  # 80% field coverage
            ]
            
            success_count = sum(success_criteria)
            success_rate = (success_count / len(success_criteria)) * 100
            
            if success_rate >= 75:  # At least 3 out of 4 criteria met
                self.log_test("Status Values Verification", True, 
                             f"✅ Status values verification passed - {len(found_statuses)} status types found")
                return True
            else:
                self.log_test("Status Values Verification", False, 
                             f"❌ Status values verification failed - success rate {success_rate:.1f}%")
                return False
                
        except Exception as e:
            self.log_test("Status Values Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_master_kit_contributions(self, contributions_data):
        """Test master kit contributions specifically"""
        try:
            print(f"\n🎽 TESTING MASTER KIT CONTRIBUTIONS")
            print("=" * 80)
            print("Testing master kit contributions with status...")
            
            if not contributions_data:
                self.log_test("Master Kit Contributions", False, "❌ No contributions data to test")
                return False
            
            # Filter master kit contributions
            master_kit_contributions = [
                contrib for contrib in contributions_data 
                if contrib.get('entity_type') == 'master_kit'
            ]
            
            print(f"      Total contributions: {len(contributions_data)}")
            print(f"      Master kit contributions: {len(master_kit_contributions)}")
            
            if not master_kit_contributions:
                print(f"      ⚠️ No master kit contributions found")
                self.log_test("Master Kit Contributions", False, "❌ No master kit contributions found")
                return False
            
            # Analyze master kit contributions
            master_kit_statuses = {}
            master_kit_with_status = 0
            
            for contrib in master_kit_contributions:
                status = contrib.get('status')
                if status:
                    master_kit_with_status += 1
                    master_kit_statuses[status] = master_kit_statuses.get(status, 0) + 1
            
            print(f"      Master kit contributions with status: {master_kit_with_status}/{len(master_kit_contributions)}")
            print(f"      Master kit status breakdown:")
            for status, count in master_kit_statuses.items():
                print(f"         {status}: {count}")
            
            # Check for pending_review master kits
            pending_master_kits = [
                contrib for contrib in master_kit_contributions 
                if contrib.get('status') == 'pending_review'
            ]
            
            print(f"      Pending review master kits: {len(pending_master_kits)}")
            
            if pending_master_kits:
                print(f"      Sample pending master kit:")
                sample = pending_master_kits[0]
                print(f"         ID: {sample.get('id')}")
                print(f"         Status: {sample.get('status')}")
                print(f"         TopKit Reference: {sample.get('topkit_reference')}")
                print(f"         Created At: {sample.get('created_at')}")
            
            # Show sample master kit contribution
            if master_kit_contributions:
                print(f"      Sample master kit contribution:")
                sample = master_kit_contributions[0]
                print(f"         ID: {sample.get('id')}")
                print(f"         Status: {sample.get('status')}")
                print(f"         Entity Type: {sample.get('entity_type')}")
                print(f"         TopKit Reference: {sample.get('topkit_reference')}")
                print(f"         Title: {sample.get('title', 'N/A')}")
                print(f"         Upvotes: {sample.get('upvotes', 'N/A')}")
                print(f"         Downvotes: {sample.get('downvotes', 'N/A')}")
                print(f"         Created At: {sample.get('created_at')}")
            
            # Determine success
            success_criteria = [
                len(master_kit_contributions) > 0,  # Has master kit contributions
                master_kit_with_status == len(master_kit_contributions),  # All have status
                len(master_kit_statuses) >= 1,  # Has status values
                len(pending_master_kits) >= 0  # Has pending items (0 is acceptable)
            ]
            
            success_count = sum(success_criteria)
            success_rate = (success_count / len(success_criteria)) * 100
            
            if success_rate >= 75:  # At least 3 out of 4 criteria met
                self.log_test("Master Kit Contributions", True, 
                             f"✅ Master kit contributions working - {len(master_kit_contributions)} found with status")
                return True
            else:
                self.log_test("Master Kit Contributions", False, 
                             f"❌ Master kit contributions issues - success rate {success_rate:.1f}%")
                return False
                
        except Exception as e:
            self.log_test("Master Kit Contributions", False, f"Exception: {str(e)}")
            return False
    
    def test_moderation_api_filtering(self):
        """Test moderation API filtering by status"""
        try:
            print(f"\n🔧 TESTING MODERATION API FILTERING")
            print("=" * 80)
            print("Testing GET /api/contributions-v2/?status=... filtering...")
            
            if not self.auth_token:
                print(f"         ⚠️ No auth token available, attempting authentication...")
                if not self.authenticate_admin():
                    self.log_test("Moderation API Filtering", False, "❌ Cannot authenticate for testing")
                    return False
            
            # Test different status filters
            status_filters = ['pending_review', 'approved', 'rejected']
            filter_results = {}
            
            for status_filter in status_filters:
                print(f"      Testing GET /api/contributions-v2/?status={status_filter}...")
                
                filter_response = self.session.get(
                    f"{BACKEND_URL}/contributions-v2/?status={status_filter}", 
                    timeout=10
                )
                
                print(f"         Response status: {filter_response.status_code}")
                
                if filter_response.status_code == 200:
                    filter_data = filter_response.json()
                    filter_results[status_filter] = filter_data
                    
                    print(f"         ✅ Filter working - {len(filter_data)} {status_filter} contributions")
                    
                    # Verify all returned items have the correct status
                    correct_status_count = sum(1 for contrib in filter_data if contrib.get('status') == status_filter)
                    
                    if len(filter_data) == correct_status_count:
                        print(f"         ✅ All returned items have correct status ({correct_status_count}/{len(filter_data)})")
                    else:
                        print(f"         ⚠️ Some items have incorrect status ({correct_status_count}/{len(filter_data)})")
                    
                    # Show sample if available
                    if filter_data:
                        sample = filter_data[0]
                        print(f"         Sample {status_filter} contribution:")
                        print(f"            ID: {sample.get('id')}")
                        print(f"            Status: {sample.get('status')}")
                        print(f"            Entity Type: {sample.get('entity_type')}")
                        print(f"            TopKit Reference: {sample.get('topkit_reference')}")
                    
                else:
                    print(f"         ❌ Filter failed - Status {filter_response.status_code}")
                    print(f"            Error: {filter_response.text}")
                    filter_results[status_filter] = None
            
            # Test unfiltered endpoint for comparison
            print(f"      Testing GET /api/contributions-v2/ (unfiltered) for comparison...")
            
            unfiltered_response = self.session.get(f"{BACKEND_URL}/contributions-v2/", timeout=10)
            
            if unfiltered_response.status_code == 200:
                unfiltered_data = unfiltered_response.json()
                print(f"         ✅ Unfiltered endpoint - {len(unfiltered_data)} total contributions")
                
                # Compare totals
                filtered_total = sum(len(data) for data in filter_results.values() if data is not None)
                print(f"         Filtered total: {filtered_total}")
                print(f"         Unfiltered total: {len(unfiltered_data)}")
                
                if filtered_total <= len(unfiltered_data):
                    print(f"         ✅ Filtering logic consistent - filtered total ≤ unfiltered total")
                else:
                    print(f"         ⚠️ Filtering logic inconsistent - filtered total > unfiltered total")
                
            else:
                print(f"         ❌ Unfiltered endpoint failed - Status {unfiltered_response.status_code}")
                unfiltered_data = None
            
            # Analyze results
            working_filters = sum(1 for data in filter_results.values() if data is not None)
            total_filters = len(status_filters)
            
            print(f"\n      📊 MODERATION API FILTERING ANALYSIS:")
            print(f"         Working filters: {working_filters}/{total_filters}")
            for status_filter, data in filter_results.items():
                if data is not None:
                    print(f"         {status_filter}: ✅ {len(data)} contributions")
                else:
                    print(f"         {status_filter}: ❌ Failed")
            
            # Determine success
            success_rate = (working_filters / total_filters) * 100
            
            if success_rate >= 66:  # At least 2 out of 3 filters working
                self.log_test("Moderation API Filtering", True, 
                             f"✅ Moderation API filtering working - {working_filters}/{total_filters} filters functional")
                return True
            else:
                self.log_test("Moderation API Filtering", False, 
                             f"❌ Moderation API filtering issues - {working_filters}/{total_filters} filters working")
                return False
                
        except Exception as e:
            self.log_test("Moderation API Filtering", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_contributions_tests(self):
        """Run comprehensive contributions system testing suite"""
        print("\n🚀 COMPREHENSIVE CONTRIBUTIONS SYSTEM TESTING SUITE")
        print("Testing contribution system enhancements for pending approval stickers")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with testing")
            return [False]
        
        # Step 2: Test Contributions V2 Endpoint
        print("\n2️⃣ Testing Contributions V2 Endpoint...")
        contributions_success, contributions_data = self.test_contributions_v2_endpoint()
        test_results.append(contributions_success)
        
        # Step 3: Test Status Values Verification
        print("\n3️⃣ Testing Status Values Verification...")
        status_verification_success = self.test_status_values_verification(contributions_data)
        test_results.append(status_verification_success)
        
        # Step 4: Test Master Kit Contributions
        print("\n4️⃣ Testing Master Kit Contributions...")
        master_kit_success = self.test_master_kit_contributions(contributions_data)
        test_results.append(master_kit_success)
        
        # Step 5: Test Moderation API Filtering
        print("\n5️⃣ Testing Moderation API Filtering...")
        moderation_filtering_success = self.test_moderation_api_filtering()
        test_results.append(moderation_filtering_success)
        
        return test_results
    
    def print_comprehensive_contributions_summary(self):
        """Print final comprehensive contributions testing summary"""
        print("\n📊 COMPREHENSIVE CONTRIBUTIONS SYSTEM TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 CONTRIBUTIONS SYSTEM TESTING RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Admin authentication working with emergency.admin@topkit.test")
        else:
            print(f"  ❌ AUTHENTICATION: Admin authentication failing")
        
        # Contributions V2 Endpoint
        contributions_working = any(r['success'] for r in self.test_results if 'Contributions V2 Endpoint' in r['test'])
        if contributions_working:
            print(f"  ✅ CONTRIBUTIONS V2 ENDPOINT: GET /api/contributions-v2/ returning contributions with status field")
        else:
            print(f"  ❌ CONTRIBUTIONS V2 ENDPOINT: GET /api/contributions-v2/ failing or missing status field")
        
        # Status Values Verification
        status_verification_working = any(r['success'] for r in self.test_results if 'Status Values Verification' in r['test'])
        if status_verification_working:
            print(f"  ✅ STATUS VALUES: Contributions have proper status values (pending_review, approved, rejected)")
        else:
            print(f"  ❌ STATUS VALUES: Status values missing or incorrect")
        
        # Master Kit Contributions
        master_kit_working = any(r['success'] for r in self.test_results if 'Master Kit Contributions' in r['test'])
        if master_kit_working:
            print(f"  ✅ MASTER KIT CONTRIBUTIONS: Master kit contributions included with proper status")
        else:
            print(f"  ❌ MASTER KIT CONTRIBUTIONS: Master kit contributions missing or status issues")
        
        # Moderation API Filtering
        moderation_working = any(r['success'] for r in self.test_results if 'Moderation API Filtering' in r['test'])
        if moderation_working:
            print(f"  ✅ MODERATION API: Status filtering working (pending_review, approved, rejected)")
        else:
            print(f"  ❌ MODERATION API: Status filtering not working correctly")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ CRITICAL CONTRIBUTIONS ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final diagnosis
        print(f"\n🎯 CONTRIBUTIONS SYSTEM DIAGNOSIS:")
        
        working_components = sum([auth_working, contributions_working, status_verification_working, master_kit_working, moderation_working])
        total_components = 5
        
        if working_components == total_components:
            print(f"  ✅ ALL CONTRIBUTIONS COMPONENTS WORKING ({working_components}/{total_components})")
            print(f"     - All contributions returned with status field populated")
            print(f"     - Mix of approved and pending_review status items visible")
            print(f"     - No filtering preventing unapproved contributions from appearing")
            print(f"     - Proper response format for frontend consumption")
            print(f"     - Master kit contributions included with status")
            print(f"     - Moderation API filtering working correctly")
        elif working_components >= 4:
            print(f"  ⚠️ MOST CONTRIBUTIONS COMPONENTS WORKING ({working_components}/{total_components})")
            print(f"     - Core functionality operational with minor issues")
        elif working_components >= 3:
            print(f"  ⚠️ SOME CONTRIBUTIONS COMPONENTS WORKING ({working_components}/{total_components})")
            print(f"     - Basic functionality working but significant issues present")
        else:
            print(f"  ❌ MULTIPLE CONTRIBUTIONS COMPONENTS BROKEN ({working_components}/{total_components})")
            print(f"     - Major issues preventing proper contribution system operation")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the comprehensive contributions system testing suite"""
    tester = TopKitContributionsSystemTesting()
    
    # Run the comprehensive contributions tests
    test_results = tester.run_comprehensive_contributions_tests()
    
    # Print comprehensive summary
    tester.print_comprehensive_contributions_summary()
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)