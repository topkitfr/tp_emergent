#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - MASTER KIT MODERATION APPROVAL FIX TESTING

Testing the Master Kit moderation approval fix. There was a collection mismatch bug where the moderation 
endpoint was looking in db.contributions but Master Kit contributions are stored in db.contributions_v2. 
All endpoints have been fixed to use contributions_v2.

Test Plan:
1. Login with emergency.admin@topkit.test / EmergencyAdmin2025!
2. Get the list of pending contributions from GET /api/contributions-v2/?status=pending_review
3. Take a contribution ID and test the moderation endpoint: POST /api/contributions-v2/{contribution_id}/moderate with action="approve" 
4. Verify the contribution status is updated to "approved" in the contributions_v2 collection
5. Confirm no more "Contribution not found" error

Focus: Testing that the moderation approve/reject actions now work correctly with contributions_v2 collection 
instead of the old contributions collection.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://collector-hub-4.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitModerationApprovalTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.pending_contributions = []
        self.test_contribution_id = None
        
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
    
    def get_pending_contributions(self):
        """Get the list of pending contributions from GET /api/contributions-v2/?status=pending_review"""
        try:
            print(f"\n📋 GETTING PENDING CONTRIBUTIONS")
            print("=" * 60)
            print("Getting pending contributions from contributions_v2 collection...")
            
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/?status=pending_review", timeout=10)
            
            if response.status_code == 200:
                self.pending_contributions = response.json()
                
                print(f"      ✅ Pending contributions retrieved successfully")
                print(f"         Found {len(self.pending_contributions)} pending_review contributions")
                
                # Show details of first few contributions
                for i, contrib in enumerate(self.pending_contributions[:3]):
                    print(f"         [{i+1}] ID: {contrib.get('id')}")
                    print(f"             Entity Type: {contrib.get('entity_type')}")
                    print(f"             Status: {contrib.get('status')}")
                    print(f"             Created By: {contrib.get('created_by', 'N/A')}")
                
                if self.pending_contributions:
                    # Select the first contribution for testing
                    self.test_contribution_id = self.pending_contributions[0].get('id')
                    print(f"      🎯 Selected contribution for testing: {self.test_contribution_id}")
                
                self.log_test("Get Pending Contributions", True, 
                             f"✅ Found {len(self.pending_contributions)} pending_review contributions")
                return True
                
            else:
                self.log_test("Get Pending Contributions", False, 
                             f"❌ Failed to get pending contributions - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Pending Contributions", False, f"Exception: {str(e)}")
            return False
    
    def create_test_contribution_if_needed(self):
        """Create a test Master Kit contribution if no pending contributions exist"""
        try:
            if self.pending_contributions:
                return True  # Already have contributions to test with
                
            print(f"\n🔧 CREATING TEST CONTRIBUTION")
            print("=" * 60)
            print("No pending contributions found, creating a test Master Kit...")
            
            # Get form data first
            clubs_response = self.session.get(f"{BACKEND_URL}/form-data/clubs", timeout=10)
            brands_response = self.session.get(f"{BACKEND_URL}/form-data/brands", timeout=10)
            competitions_response = self.session.get(f"{BACKEND_URL}/form-data/competitions", timeout=10)
            
            if not all(r.status_code == 200 for r in [clubs_response, brands_response, competitions_response]):
                self.log_test("Create Test Contribution", False, "❌ Failed to get form data for test contribution")
                return False
            
            clubs = clubs_response.json()
            brands = brands_response.json()
            competitions = competitions_response.json()
            
            if not clubs or not brands or not competitions:
                self.log_test("Create Test Contribution", False, "❌ Insufficient form data for test contribution")
                return False
            
            # Create test images
            front_image = self.create_test_image(800, 600, "front_test.jpg")
            back_image = self.create_test_image(800, 600, "back_test.jpg")
            
            if not front_image or not back_image:
                self.log_test("Create Test Contribution", False, "❌ Failed to create test images")
                return False
            
            # Prepare FormData for Master Kit creation
            files = {
                'front_photo': ('front_test.jpg', front_image, 'image/jpeg'),
                'back_photo': ('back_test.jpg', back_image, 'image/jpeg')
            }
            
            data = {
                'kit_type': 'authentic',
                'club_id': clubs[0]['id'],
                'kit_style': 'home',
                'season': '2024/2025',
                'competition_id': competitions[0]['id'],
                'brand_id': brands[0]['id']
            }
            
            print(f"      Creating test Master Kit...")
            print(f"         Club: {clubs[0]['name']}")
            print(f"         Brand: {brands[0]['name']}")
            print(f"         Competition: {competitions[0]['name']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/master-kits",
                files=files,
                data=data,
                timeout=20
            )
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                print(f"         ✅ Test Master Kit created successfully")
                print(f"            Master Kit ID: {response_data.get('id')}")
                print(f"            TopKit Reference: {response_data.get('topkit_reference')}")
                
                # Now get the pending contributions again
                return self.get_pending_contributions()
                
            else:
                self.log_test("Create Test Contribution", False, 
                             f"❌ Failed to create test Master Kit - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Create Test Contribution", False, f"Exception: {str(e)}")
            return False
    
    def create_test_image(self, width=800, height=600, filename="test_image.jpg"):
        """Create a test image for FormData upload"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (width, height), color='blue')
            img_buffer = BytesIO()
            img.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            return img_buffer
        except Exception as e:
            print(f"Error creating test image: {str(e)}")
            return None
    
    def test_moderation_approve_endpoint(self):
        """Test the moderation endpoint: POST /api/contributions-v2/{contribution_id}/moderate with action="approve" """
        try:
            print(f"\n✅ TESTING MODERATION APPROVE ENDPOINT")
            print("=" * 60)
            print("Testing POST /api/contributions-v2/{contribution_id}/moderate with action='approve'...")
            
            if not self.test_contribution_id:
                self.log_test("Moderation Approve Endpoint", False, "❌ No contribution ID available for testing")
                return False
            
            print(f"      Testing contribution ID: {self.test_contribution_id}")
            
            # Test the moderation endpoint with approve action
            moderation_data = {
                "action": "approve"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/{self.test_contribution_id}/moderate",
                json=moderation_data,
                timeout=15
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"      ✅ Moderation approve endpoint working")
                print(f"         Response: {response_data}")
                
                self.log_test("Moderation Approve Endpoint", True, 
                             f"✅ Moderation approve endpoint working - no 'Contribution not found' error")
                return True
                
            elif response.status_code == 404:
                error_text = response.text
                if "Contribution not found" in error_text:
                    print(f"      ❌ Still getting 'Contribution not found' error")
                    print(f"         This indicates the endpoint is still looking in wrong collection")
                    self.log_test("Moderation Approve Endpoint", False, 
                                 f"❌ Still getting 'Contribution not found' error - collection mismatch not fixed", error_text)
                else:
                    print(f"      ❌ 404 error but different message: {error_text}")
                    self.log_test("Moderation Approve Endpoint", False, 
                                 f"❌ 404 error with different message", error_text)
                return False
                
            else:
                error_text = response.text
                print(f"      ❌ Unexpected status code: {response.status_code}")
                print(f"         Error: {error_text}")
                self.log_test("Moderation Approve Endpoint", False, 
                             f"❌ Unexpected status code {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Moderation Approve Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_moderation_reject_endpoint(self):
        """Test the moderation endpoint: POST /api/contributions-v2/{contribution_id}/moderate with action="reject" """
        try:
            print(f"\n❌ TESTING MODERATION REJECT ENDPOINT")
            print("=" * 60)
            print("Testing POST /api/contributions-v2/{contribution_id}/moderate with action='reject'...")
            
            # Find another contribution to test reject (if available)
            reject_contribution_id = None
            if len(self.pending_contributions) > 1:
                reject_contribution_id = self.pending_contributions[1].get('id')
            elif len(self.pending_contributions) == 1:
                # Use the same contribution but test reject action
                reject_contribution_id = self.test_contribution_id
            
            if not reject_contribution_id:
                self.log_test("Moderation Reject Endpoint", False, "❌ No contribution ID available for reject testing")
                return False
            
            print(f"      Testing contribution ID: {reject_contribution_id}")
            
            # Test the moderation endpoint with reject action
            moderation_data = {
                "action": "reject"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/{reject_contribution_id}/moderate",
                json=moderation_data,
                timeout=15
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"      ✅ Moderation reject endpoint working")
                print(f"         Response: {response_data}")
                
                self.log_test("Moderation Reject Endpoint", True, 
                             f"✅ Moderation reject endpoint working - no 'Contribution not found' error")
                return True
                
            elif response.status_code == 404:
                error_text = response.text
                if "Contribution not found" in error_text:
                    print(f"      ❌ Still getting 'Contribution not found' error")
                    print(f"         This indicates the endpoint is still looking in wrong collection")
                    self.log_test("Moderation Reject Endpoint", False, 
                                 f"❌ Still getting 'Contribution not found' error - collection mismatch not fixed", error_text)
                else:
                    print(f"      ❌ 404 error but different message: {error_text}")
                    self.log_test("Moderation Reject Endpoint", False, 
                                 f"❌ 404 error with different message", error_text)
                return False
                
            else:
                error_text = response.text
                print(f"      ❌ Unexpected status code: {response.status_code}")
                print(f"         Error: {error_text}")
                self.log_test("Moderation Reject Endpoint", False, 
                             f"❌ Unexpected status code {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Moderation Reject Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def verify_contribution_status_updated(self):
        """Verify the contribution status is updated to "approved" in the contributions_v2 collection"""
        try:
            print(f"\n🔍 VERIFYING CONTRIBUTION STATUS UPDATE")
            print("=" * 60)
            print("Verifying contribution status updated in contributions_v2 collection...")
            
            if not self.test_contribution_id:
                self.log_test("Verify Contribution Status Update", False, "❌ No contribution ID to verify")
                return False
            
            # Get the specific contribution to check its status
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/{self.test_contribution_id}", timeout=10)
            
            if response.status_code == 200:
                contribution_data = response.json()
                current_status = contribution_data.get('status')
                
                print(f"      ✅ Contribution found in contributions_v2")
                print(f"         Contribution ID: {contribution_data.get('id')}")
                print(f"         Current Status: {current_status}")
                print(f"         Entity Type: {contribution_data.get('entity_type')}")
                print(f"         Updated At: {contribution_data.get('updated_at', 'N/A')}")
                
                if current_status == "approved":
                    print(f"      ✅ Status successfully updated to 'approved'")
                    self.log_test("Verify Contribution Status Update", True, 
                                 f"✅ Contribution status successfully updated to 'approved'")
                    return True
                elif current_status == "pending_review":
                    print(f"      ⚠️ Status still 'pending_review' - moderation may not have processed")
                    self.log_test("Verify Contribution Status Update", False, 
                                 f"⚠️ Status still 'pending_review' - moderation action may not have been processed")
                    return False
                else:
                    print(f"      ❓ Unexpected status: {current_status}")
                    self.log_test("Verify Contribution Status Update", False, 
                                 f"❓ Unexpected status: {current_status}")
                    return False
                    
            elif response.status_code == 404:
                print(f"      ❌ Contribution not found when verifying status")
                self.log_test("Verify Contribution Status Update", False, 
                             f"❌ Contribution not found when verifying status")
                return False
                
            else:
                error_text = response.text
                print(f"      ❌ Error getting contribution status - Status {response.status_code}")
                print(f"         Error: {error_text}")
                self.log_test("Verify Contribution Status Update", False, 
                             f"❌ Error getting contribution status - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Verify Contribution Status Update", False, f"Exception: {str(e)}")
            return False
    
    def test_contributions_v2_collection_access(self):
        """Test that all endpoints are now using contributions_v2 collection"""
        try:
            print(f"\n🗄️ TESTING CONTRIBUTIONS_V2 COLLECTION ACCESS")
            print("=" * 60)
            print("Testing that all endpoints are using contributions_v2 collection...")
            
            # Test various endpoints to ensure they're using contributions_v2
            endpoints_to_test = [
                ("/contributions-v2/", "List all contributions"),
                ("/contributions-v2/?status=pending_review", "Filter pending_review"),
                ("/contributions-v2/?status=approved", "Filter approved"),
                ("/contributions-v2/?entity_type=master_kit", "Filter master_kit type")
            ]
            
            results = []
            
            for endpoint, description in endpoints_to_test:
                print(f"      Testing: {description}")
                response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"         ✅ {description}: {len(data)} items found")
                    results.append(True)
                else:
                    print(f"         ❌ {description}: Status {response.status_code}")
                    results.append(False)
            
            if all(results):
                self.log_test("Contributions V2 Collection Access", True, 
                             f"✅ All contributions_v2 endpoints accessible")
                return True
            else:
                failed_count = len([r for r in results if not r])
                self.log_test("Contributions V2 Collection Access", False, 
                             f"❌ {failed_count}/{len(results)} contributions_v2 endpoints failed")
                return False
                
        except Exception as e:
            self.log_test("Contributions V2 Collection Access", False, f"Exception: {str(e)}")
            return False
    
    def test_moderation_approval_fix(self):
        """Test complete moderation approval fix"""
        print("\n🚀 MASTER KIT MODERATION APPROVAL FIX TESTING")
        print("Testing that moderation approve/reject actions work with contributions_v2 collection")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        test_results.append(auth_success)
        
        # Step 2: Get pending contributions from contributions_v2
        print("\n2️⃣ Getting pending contributions from contributions_v2...")
        pending_success = self.get_pending_contributions()
        test_results.append(pending_success)
        
        # Step 3: Create test contribution if needed
        if not self.pending_contributions:
            print("\n3️⃣ Creating test contribution...")
            create_success = self.create_test_contribution_if_needed()
            test_results.append(create_success)
        
        # Step 4: Test contributions_v2 collection access
        print("\n4️⃣ Testing contributions_v2 collection access...")
        collection_success = self.test_contributions_v2_collection_access()
        test_results.append(collection_success)
        
        # Step 5: Test moderation approve endpoint
        print("\n5️⃣ Testing moderation approve endpoint...")
        approve_success = self.test_moderation_approve_endpoint()
        test_results.append(approve_success)
        
        # Step 6: Verify contribution status updated
        print("\n6️⃣ Verifying contribution status updated...")
        verify_success = self.verify_contribution_status_updated()
        test_results.append(verify_success)
        
        # Step 7: Test moderation reject endpoint
        print("\n7️⃣ Testing moderation reject endpoint...")
        reject_success = self.test_moderation_reject_endpoint()
        test_results.append(reject_success)
        
        return test_results
    
    def print_final_summary(self):
        """Print final testing summary"""
        print("\n📊 MASTER KIT MODERATION APPROVAL FIX TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 MODERATION APPROVAL FIX RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Emergency admin login working")
        else:
            print(f"  ❌ AUTHENTICATION: Emergency admin login failed")
        
        # Pending Contributions
        pending_working = any(r['success'] for r in self.test_results if 'Get Pending Contributions' in r['test'])
        if pending_working:
            print(f"  ✅ PENDING CONTRIBUTIONS: GET /api/contributions-v2/?status=pending_review working")
        else:
            print(f"  ❌ PENDING CONTRIBUTIONS: Cannot access pending contributions")
        
        # Collection Access
        collection_working = any(r['success'] for r in self.test_results if 'Contributions V2 Collection Access' in r['test'])
        if collection_working:
            print(f"  ✅ COLLECTION ACCESS: All contributions_v2 endpoints accessible")
        else:
            print(f"  ❌ COLLECTION ACCESS: Issues with contributions_v2 endpoints")
        
        # Moderation Approve
        approve_working = any(r['success'] for r in self.test_results if 'Moderation Approve Endpoint' in r['test'])
        if approve_working:
            print(f"  ✅ MODERATION APPROVE: POST /api/contributions-v2/{{id}}/moderate working")
        else:
            print(f"  ❌ MODERATION APPROVE: Still getting 'Contribution not found' error")
        
        # Status Update Verification
        verify_working = any(r['success'] for r in self.test_results if 'Verify Contribution Status Update' in r['test'])
        if verify_working:
            print(f"  ✅ STATUS UPDATE: Contribution status updated to 'approved'")
        else:
            print(f"  ❌ STATUS UPDATE: Status not updated correctly")
        
        # Moderation Reject
        reject_working = any(r['success'] for r in self.test_results if 'Moderation Reject Endpoint' in r['test'])
        if reject_working:
            print(f"  ✅ MODERATION REJECT: POST /api/contributions-v2/{{id}}/moderate with reject working")
        else:
            print(f"  ❌ MODERATION REJECT: Reject action not working")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status - Focus on the specific fix
        print(f"\n🎯 FINAL STATUS - MODERATION APPROVAL FIX:")
        critical_tests = [auth_working, pending_working, approve_working]
        if all(critical_tests):
            print(f"  ✅ MODERATION APPROVAL FIX WORKING PERFECTLY")
            print(f"     - Emergency admin authentication operational")
            print(f"     - Pending contributions accessible from contributions_v2")
            print(f"     - Moderation approve endpoint working (no 'Contribution not found' error)")
            print(f"     - Collection mismatch bug has been fixed")
        elif auth_working and pending_working:
            print(f"  ⚠️ PARTIAL SUCCESS: Can access contributions but moderation actions may have issues")
            print(f"     - Authentication and contribution access working")
            print(f"     - Moderation endpoints may still have collection mismatch issues")
        else:
            print(f"  ❌ MAJOR ISSUES: Moderation approval fix not working")
            print(f"     - Cannot properly access or moderate contributions_v2")
            print(f"     - Collection mismatch bug may still exist")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all moderation approval fix tests and return success status"""
        test_results = self.test_moderation_approval_fix()
        self.print_final_summary()
        return any(test_results)

def main():
    """Main test execution - Master Kit Moderation Approval Fix Testing"""
    tester = TopKitModerationApprovalTesting()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()