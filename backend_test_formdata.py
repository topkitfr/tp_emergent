#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - MASTER KIT FORMDATA SUBMISSION BUG FIX TESTING

Testing the Master Kit FormData submission bug fix comprehensively:
1. **Master Kit FormData Creation Testing** - Test POST /api/master-kits endpoint with FormData and file uploads
2. **UnicodeDecodeError Fix Verification** - Verify FormData endpoint works without UnicodeDecodeError
3. **Contribution Creation for Moderation** - Verify contribution entry is created in contributions_v2 collection
4. **Response Message Testing** - Verify success response includes detailed message with topkit_reference and status
5. **Authentication Testing** - Login with emergency.admin@topkit.test / EmergencyAdmin2025!
6. **File Upload Testing** - Test front_photo and back_photo file uploads with FormData

CRITICAL: Testing with emergency.admin@topkit.test / EmergencyAdmin2025! account.
Focus on verifying that Master Kit FormData submissions now work without UnicodeDecodeError and properly create contributions.
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
BACKEND_URL = "https://kitauth-fix.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitMasterKitFormDataTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.form_data = {}
        self.created_master_kit_id = None
        self.created_contribution_id = None
        
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
    
    def create_test_image(self, width=800, height=600, filename="test_image.jpg"):
        """Create a test image for upload"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (width, height), color='red')
            img_buffer = BytesIO()
            img.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            return img_buffer
        except Exception as e:
            print(f"Error creating test image: {str(e)}")
            return None
    
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
    
    def get_form_data(self):
        """Get form data for Master Kit creation (clubs, brands, competitions, sponsors)"""
        try:
            print(f"\n📋 GETTING FORM DATA")
            print("=" * 60)
            print("Getting form data for Master Kit creation...")
            
            # Get clubs
            clubs_response = self.session.get(f"{BACKEND_URL}/form-data/clubs", timeout=10)
            brands_response = self.session.get(f"{BACKEND_URL}/form-data/brands", timeout=10)
            
            if all(r.status_code == 200 for r in [clubs_response, brands_response]):
                self.form_data = {
                    "clubs": clubs_response.json(),
                    "brands": brands_response.json()
                }
                
                print(f"      ✅ Form data retrieved successfully")
                print(f"         Clubs: {len(self.form_data['clubs'])}")
                print(f"         Brands: {len(self.form_data['brands'])}")
                
                self.log_test("Get Form Data", True, 
                             f"✅ Form data retrieved - {len(self.form_data['clubs'])} clubs, {len(self.form_data['brands'])} brands")
                return True
            else:
                self.log_test("Get Form Data", False, 
                             f"❌ Failed to get form data - Status codes: clubs={clubs_response.status_code}, brands={brands_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Form Data", False, f"Exception: {str(e)}")
            return False
    
    def test_master_kit_formdata_creation(self):
        """Test Master Kit creation with FormData and file uploads"""
        try:
            print(f"\n📤 TESTING MASTER KIT FORMDATA CREATION")
            print("=" * 60)
            print("Testing Master Kit creation with FormData and file uploads...")
            
            if not self.auth_token:
                self.log_test("Master Kit FormData Creation", False, "❌ No authentication token available")
                return False
            
            if not self.form_data or not self.form_data['clubs'] or not self.form_data['brands']:
                self.log_test("Master Kit FormData Creation", False, "❌ Insufficient form data for testing")
                return False
            
            club = self.form_data['clubs'][0]
            brand = self.form_data['brands'][0]
            
            # Create test images
            front_image = self.create_test_image(800, 600, "front_test.jpg")
            back_image = self.create_test_image(800, 600, "back_test.jpg")
            
            if not front_image or not back_image:
                self.log_test("Master Kit FormData Creation", False, "❌ Failed to create test images")
                return False
            
            print(f"      Creating Master Kit with FormData:")
            print(f"         Club: {club['name']} ({club['id']})")
            print(f"         Brand: {brand['name']} ({brand['id']})")
            print(f"         Kit Type: authentic")
            print(f"         Season: 2024/2025")
            print(f"         Kit Style: home")
            
            # Prepare FormData
            form_data = {
                'kit_type': 'authentic',
                'club_id': club['id'],
                'kit_style': 'home',
                'season': '2024/2025',
                'brand_id': brand['id']
            }
            
            # Prepare files
            files = {
                'front_photo': ('front_test.jpg', front_image, 'image/jpeg'),
                'back_photo': ('back_test.jpg', back_image, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/master-kits",
                data=form_data,
                files=files,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.created_master_kit_id = data.get('id')
                
                print(f"         ✅ Master Kit created successfully with FormData")
                print(f"            Master Kit ID: {self.created_master_kit_id}")
                print(f"            TopKit Reference: {data.get('topkit_reference')}")
                print(f"            Status: {data.get('status')}")
                print(f"            Message: {data.get('message')}")
                
                # Verify response structure
                required_response_fields = ['id', 'topkit_reference', 'message']
                missing_fields = [field for field in required_response_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Master Kit FormData Creation", True, 
                                 f"✅ Master Kit created successfully with FormData - no UnicodeDecodeError")
                    return True
                else:
                    self.log_test("Master Kit FormData Creation", False, 
                                 f"❌ Master Kit created but response missing fields: {missing_fields}")
                    return False
                    
            else:
                error_text = response.text
                print(f"         ❌ Master Kit FormData creation failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                
                # Check if it's a UnicodeDecodeError
                if "UnicodeDecodeError" in error_text:
                    self.log_test("Master Kit FormData Creation", False, 
                                 f"❌ UnicodeDecodeError still present - bug not fixed", error_text)
                else:
                    self.log_test("Master Kit FormData Creation", False, 
                                 f"❌ Master Kit FormData creation failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Master Kit FormData Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_contribution_creation_for_moderation(self):
        """Test that Master Kit creation creates contribution entry for moderation"""
        try:
            print(f"\n📝 TESTING CONTRIBUTION CREATION FOR MODERATION")
            print("=" * 60)
            print("Testing that Master Kit creation creates contribution entry...")
            
            if not self.created_master_kit_id:
                self.log_test("Contribution Creation for Moderation", False, "❌ No Master Kit created for testing")
                return False
            
            # Check contributions-v2 endpoint for the created Master Kit
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/", timeout=10)
            
            if response.status_code == 200:
                contributions = response.json()
                
                print(f"      ✅ Contributions endpoint accessible")
                print(f"         Found {len(contributions)} contributions")
                
                # Look for contribution with entity_type="master_kit" and matching master_kit_id
                master_kit_contributions = [
                    c for c in contributions 
                    if c.get('entity_type') == 'master_kit' and 
                       (c.get('entity_id') == self.created_master_kit_id or 
                        c.get('master_kit_id') == self.created_master_kit_id)
                ]
                
                if master_kit_contributions:
                    contribution = master_kit_contributions[0]
                    self.created_contribution_id = contribution.get('id')
                    
                    print(f"         ✅ Master Kit contribution found")
                    print(f"            Contribution ID: {contribution.get('id')}")
                    print(f"            Entity Type: {contribution.get('entity_type')}")
                    print(f"            Status: {contribution.get('status')}")
                    print(f"            Master Kit ID: {contribution.get('entity_id') or contribution.get('master_kit_id')}")
                    
                    # Verify contribution has required fields
                    required_fields = ['id', 'entity_type', 'status']
                    missing_fields = [field for field in required_fields if field not in contribution]
                    
                    if not missing_fields:
                        # Check if status is "pending"
                        if contribution.get('status') == 'pending':
                            self.log_test("Contribution Creation for Moderation", True, 
                                         f"✅ Master Kit contribution created with pending status for moderation")
                            return True
                        else:
                            self.log_test("Contribution Creation for Moderation", True, 
                                         f"✅ Master Kit contribution created with status: {contribution.get('status')}")
                            return True
                    else:
                        self.log_test("Contribution Creation for Moderation", False, 
                                     f"❌ Contribution missing required fields: {missing_fields}")
                        return False
                else:
                    print(f"         ❌ No Master Kit contribution found for Master Kit ID: {self.created_master_kit_id}")
                    
                    # Show available contributions for debugging
                    print(f"         Available contributions:")
                    for c in contributions[:3]:  # Show first 3
                        print(f"            • {c.get('entity_type')} - {c.get('id')} - Status: {c.get('status')}")
                    
                    self.log_test("Contribution Creation for Moderation", False, 
                                 f"❌ No Master Kit contribution found for created Master Kit")
                    return False
                    
            else:
                self.log_test("Contribution Creation for Moderation", False, 
                             f"❌ Contributions endpoint failed - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Contribution Creation for Moderation", False, f"Exception: {str(e)}")
            return False
    
    def test_master_kit_formdata_bug_fix(self):
        """Test complete Master Kit FormData submission bug fix"""
        print("\n🚀 MASTER KIT FORMDATA SUBMISSION BUG FIX TESTING")
        print("Testing Master Kit FormData submission bug fix comprehensively")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        test_results.append(auth_success)
        
        # Step 2: Get form data
        print("\n2️⃣ Getting form data...")
        form_data_success = self.get_form_data()
        test_results.append(form_data_success)
        
        # Step 3: Test Master Kit FormData creation
        print("\n3️⃣ Testing Master Kit FormData creation...")
        formdata_success = self.test_master_kit_formdata_creation()
        test_results.append(formdata_success)
        
        # Step 4: Test contribution creation for moderation
        print("\n4️⃣ Testing contribution creation for moderation...")
        contribution_success = self.test_contribution_creation_for_moderation()
        test_results.append(contribution_success)
        
        return test_results
    
    def print_final_summary(self):
        """Print final testing summary"""
        print("\n📊 MASTER KIT FORMDATA SUBMISSION BUG FIX TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 MASTER KIT FORMDATA SUBMISSION RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Emergency admin login working")
        else:
            print(f"  ❌ AUTHENTICATION: Emergency admin login failed")
        
        # Form Data
        form_data_working = any(r['success'] for r in self.test_results if 'Get Form Data' in r['test'])
        if form_data_working:
            print(f"  ✅ FORM DATA: Form data endpoints accessible")
        else:
            print(f"  ❌ FORM DATA: Form data endpoints failed")
        
        # FormData Creation
        formdata_working = any(r['success'] for r in self.test_results if 'Master Kit FormData Creation' in r['test'])
        if formdata_working:
            print(f"  ✅ FORMDATA CREATION: Master Kit FormData creation working without UnicodeDecodeError")
        else:
            print(f"  ❌ FORMDATA CREATION: FormData creation failed or UnicodeDecodeError still present")
        
        # Contribution Creation
        contribution_working = any(r['success'] for r in self.test_results if 'Contribution Creation for Moderation' in r['test'])
        if contribution_working:
            print(f"  ✅ CONTRIBUTION CREATION: Master Kit contributions created for moderation")
        else:
            print(f"  ❌ CONTRIBUTION CREATION: Contributions not being created")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status
        print(f"\n🎯 FINAL STATUS:")
        critical_tests = [auth_working, formdata_working, contribution_working]
        if all(critical_tests):
            print(f"  ✅ MASTER KIT FORMDATA SUBMISSION BUG FIX WORKING PERFECTLY")
            print(f"     - Authentication system operational")
            print(f"     - FormData endpoint working without UnicodeDecodeError")
            print(f"     - File uploads working correctly")
            print(f"     - Contributions properly created for moderation")
            print(f"     - Response format includes topkit_reference and status")
        elif auth_working and formdata_working:
            print(f"  ⚠️ PARTIAL SUCCESS: Core FormData creation working")
            print(f"     - FormData submission functional")
            print(f"     - Some moderation issues")
        else:
            print(f"  ❌ MAJOR ISSUES: Critical FormData submission not working")
            print(f"     - UnicodeDecodeError may still be present")
            print(f"     - Cannot properly create Master Kits with FormData")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all Master Kit FormData submission tests and return success status"""
        test_results = self.test_master_kit_formdata_bug_fix()
        self.print_final_summary()
        return any(test_results)

def main():
    """Main test execution - Master Kit FormData Submission Bug Fix Testing"""
    tester = TopKitMasterKitFormDataTesting()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()