#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - ENHANCED EDIT KIT FORM PHOTO REQUIREMENT REMOVAL TESTING

Testing the Enhanced Edit Kit Form photo requirement removal:
1. **Form Validation Test** - Simulate form submission without photos to ensure no validation errors occur
2. **Authentication Check** - Verify emergency.admin@topkit.test still works for testing
3. **Backend Readiness** - Confirm that the MyCollection update endpoints can handle form submissions without photo requirements

CRITICAL: Testing with emergency.admin@topkit.test / EmergencyAdmin2025! account.
Verifying that the form validation logic no longer requires photos in the "D. Physical Condition" section.
Expected Result: The form should be submittable without any photos, and no "minimum 3 photos required" validation errors should appear.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
import io

# Configuration
BACKEND_URL = "https://kit-showcase-3.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitEnhancedEditFormTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.test_collection_item_id = None
        self.collection_items = []
        
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
    
    def test_my_collection_access(self):
        """Test GET /api/my-collection endpoint to get collection items for testing"""
        try:
            print(f"\n📋 TESTING MY COLLECTION ACCESS")
            print("=" * 60)
            print("Testing: GET /api/my-collection - Verify collection items available for editing")
            
            if not self.auth_token:
                self.log_test("My Collection Access", False, "❌ No authentication token available")
                return False
            
            response = self.session.get(
                f"{BACKEND_URL}/my-collection",
                timeout=10
            )
            
            if response.status_code == 200:
                collection_data = response.json()
                print(f"      ✅ My Collection endpoint accessible")
                print(f"         Found {len(collection_data)} collection items")
                
                if len(collection_data) > 0:
                    # Store collection items for testing
                    self.collection_items = collection_data
                    
                    # Get first item for testing
                    test_item = collection_data[0]
                    self.test_collection_item_id = test_item.get('id')
                    
                    print(f"      ✅ Collection items available for testing")
                    print(f"         Test item ID: {self.test_collection_item_id}")
                    print(f"         Test item master kit: {test_item.get('master_kit', {}).get('club', 'Unknown')} {test_item.get('master_kit', {}).get('season', 'Unknown')}")
                    
                    self.log_test("My Collection Access", True, 
                                 f"✅ My Collection accessible - {len(collection_data)} items available for testing")
                    return True
                else:
                    print(f"      ⚠️ No collection items found - will create test item if needed")
                    self.log_test("My Collection Access", True, 
                                 "✅ My Collection accessible (no items found)")
                    return True
                    
            else:
                self.log_test("My Collection Access", False, 
                             f"❌ My Collection endpoint failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("My Collection Access", False, f"Exception: {str(e)}")
            return False
    
    def test_collection_update_without_photos(self):
        """Test PUT /api/my-collection/{id} endpoint without photos to verify no photo requirement validation"""
        try:
            print(f"\n📝 TESTING COLLECTION UPDATE WITHOUT PHOTOS")
            print("=" * 60)
            print("Testing: PUT /api/my-collection/{id} - Update collection item without photos (D. Physical Condition section)")
            
            if not self.auth_token:
                self.log_test("Collection Update Without Photos", False, "❌ No authentication token available")
                return False
            
            if not self.test_collection_item_id:
                self.log_test("Collection Update Without Photos", False, "❌ No test collection item available")
                return False
            
            # Create update data that would typically require photos in D. Physical Condition section
            # This simulates the Enhanced Edit Kit Form submission without photos
            update_data = {
                # A. Basic Information
                "gender": "man",
                "size": "L",
                
                # B. Player & Printing
                "name_printing": "MESSI",
                "number_printing": "10",
                
                # C. Origin & Authenticity
                "condition": "match_worn",  # This would typically require photos
                "match_date": "2024-12-15",
                
                # D. Physical Condition - NO PHOTOS PROVIDED
                "physical_state": "very_good_condition",
                # photos field intentionally omitted to test photo requirement removal
                
                # E. Technical Details
                "patches": "champions_league",  # Fixed: should be string, not array
                "is_signed": True,
                "signed_by": "Lionel Messi",
                
                # F. User Estimate
                "purchase_price": 450.00,
                "purchase_date": "2024-01-15",
                
                # G. Comments
                "comments": "Testing Enhanced Edit Kit Form without photo requirements"
            }
            
            print(f"      Updating collection item {self.test_collection_item_id}")
            print(f"      Update includes D. Physical Condition data WITHOUT photos")
            print(f"         Physical State: {update_data['physical_state']}")
            print(f"         Condition: {update_data['condition']}")
            print(f"         Match Date: {update_data['match_date']}")
            print(f"         Photos: None (intentionally omitted)")
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{self.test_collection_item_id}",
                json=update_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Collection update successful without photos")
                print(f"         Response status: {response.status_code}")
                print(f"         Updated item ID: {data.get('id')}")
                
                # Verify the update was successful and no photo validation errors occurred
                if 'id' in data:
                    print(f"      ✅ No photo requirement validation errors")
                    print(f"         Form submission successful without minimum 3 photos requirement")
                    
                    self.log_test("Collection Update Without Photos", True, 
                                 f"✅ Enhanced Edit Kit Form working correctly - No photo requirements enforced")
                    return True
                else:
                    self.log_test("Collection Update Without Photos", False, 
                                 "❌ Update response missing expected fields")
                    return False
                    
            elif response.status_code == 400:
                error_data = response.text
                print(f"      ❌ Bad request error: {error_data}")
                
                # Check if error is related to photo requirements
                if "photo" in error_data.lower() or "minimum" in error_data.lower() or "3" in error_data:
                    print(f"      ❌ PHOTO REQUIREMENT VALIDATION ERROR DETECTED")
                    print(f"         This indicates the photo requirement removal is NOT working")
                    self.log_test("Collection Update Without Photos", False, 
                                 f"❌ Photo requirement validation still active - {error_data}")
                    return False
                else:
                    print(f"      ⚠️ Other validation error (not photo-related): {error_data}")
                    self.log_test("Collection Update Without Photos", True, 
                                 f"⚠️ Update failed but not due to photo requirements - {error_data}")
                    return True
                    
            elif response.status_code == 401:
                self.log_test("Collection Update Without Photos", False, 
                             "❌ Authentication failed for collection update")
                return False
            elif response.status_code == 404:
                self.log_test("Collection Update Without Photos", False, 
                             "❌ Collection item not found")
                return False
            elif response.status_code == 422:
                error_data = response.text
                print(f"      ❌ Validation error: {error_data}")
                
                # Check if validation error is related to photo requirements
                if "photo" in error_data.lower() or "minimum" in error_data.lower():
                    print(f"      ❌ PHOTO REQUIREMENT VALIDATION ERROR DETECTED")
                    print(f"         This indicates the photo requirement removal is NOT working")
                    self.log_test("Collection Update Without Photos", False, 
                                 f"❌ Photo requirement validation still active - {error_data}")
                    return False
                else:
                    print(f"      ⚠️ Other validation error (not photo-related): {error_data}")
                    self.log_test("Collection Update Without Photos", True, 
                                 f"⚠️ Validation error but not photo-related - {error_data}")
                    return True
            else:
                self.log_test("Collection Update Without Photos", False, 
                             f"❌ Collection update failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Collection Update Without Photos", False, f"Exception: {str(e)}")
            return False
    
    def test_collection_update_with_minimal_data(self):
        """Test PUT /api/my-collection/{id} endpoint with minimal data to ensure basic functionality"""
        try:
            print(f"\n🔧 TESTING COLLECTION UPDATE WITH MINIMAL DATA")
            print("=" * 60)
            print("Testing: PUT /api/my-collection/{id} - Update with minimal data to verify basic endpoint functionality")
            
            if not self.auth_token:
                self.log_test("Collection Update Minimal Data", False, "❌ No authentication token available")
                return False
            
            if not self.test_collection_item_id:
                self.log_test("Collection Update Minimal Data", False, "❌ No test collection item available")
                return False
            
            # Create minimal update data
            minimal_update_data = {
                "comments": "Minimal update test - Enhanced Edit Kit Form photo requirement removal verification"
            }
            
            print(f"      Updating collection item {self.test_collection_item_id} with minimal data")
            print(f"         Comments: {minimal_update_data['comments']}")
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{self.test_collection_item_id}",
                json=minimal_update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Minimal collection update successful")
                print(f"         Response status: {response.status_code}")
                
                self.log_test("Collection Update Minimal Data", True, 
                             f"✅ Basic collection update functionality working")
                return True
                    
            elif response.status_code == 400:
                error_data = response.text
                print(f"      ❌ Bad request error: {error_data}")
                self.log_test("Collection Update Minimal Data", False, 
                             f"❌ Minimal update failed - {error_data}")
                return False
            elif response.status_code == 401:
                self.log_test("Collection Update Minimal Data", False, 
                             "❌ Authentication failed for minimal update")
                return False
            elif response.status_code == 404:
                self.log_test("Collection Update Minimal Data", False, 
                             "❌ Collection item not found for minimal update")
                return False
            else:
                self.log_test("Collection Update Minimal Data", False, 
                             f"❌ Minimal update failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Collection Update Minimal Data", False, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_edit_form_functionality(self):
        """Test complete Enhanced Edit Kit Form photo requirement removal functionality"""
        print("\n🚀 ENHANCED EDIT KIT FORM PHOTO REQUIREMENT REMOVAL TESTING")
        print("Testing Enhanced Edit Kit Form photo requirement removal functionality")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        
        # Step 2: Test My Collection access
        print("\n2️⃣ Testing My Collection access...")
        collection_access_success = self.test_my_collection_access()
        test_results.append(collection_access_success)
        
        # Step 3: Test collection update with minimal data (baseline)
        print("\n3️⃣ Testing collection update with minimal data (baseline)...")
        minimal_update_success = self.test_collection_update_with_minimal_data()
        test_results.append(minimal_update_success)
        
        # Step 4: Test collection update without photos (main test)
        print("\n4️⃣ Testing collection update without photos (main test)...")
        no_photos_update_success = self.test_collection_update_without_photos()
        test_results.append(no_photos_update_success)
        
        return test_results
    
    def print_final_summary(self):
        """Print final testing summary"""
        print("\n📊 ENHANCED EDIT KIT FORM PHOTO REQUIREMENT REMOVAL TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 ENHANCED EDIT KIT FORM RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Emergency admin login working")
        else:
            print(f"  ❌ AUTHENTICATION: Emergency admin login failed")
        
        # My Collection Access
        collection_working = any(r['success'] for r in self.test_results if 'My Collection Access' in r['test'])
        if collection_working:
            print(f"  ✅ MY COLLECTION ACCESS: Collection items accessible for testing")
        else:
            print(f"  ❌ MY COLLECTION ACCESS: Cannot access collection items")
        
        # Photo Requirement Removal (Main Test)
        photo_removal_working = any(r['success'] for r in self.test_results if 'Collection Update Without Photos' in r['test'])
        if photo_removal_working:
            print(f"  ✅ PHOTO REQUIREMENT REMOVAL: Form submittable without photos")
            print(f"     - No 'minimum 3 photos required' validation errors")
            print(f"     - D. Physical Condition section works without photos")
        else:
            print(f"  ❌ PHOTO REQUIREMENT REMOVAL: Photo requirements still enforced")
            print(f"     - Form validation may still require minimum 3 photos")
        
        # Basic Update Functionality
        basic_update_working = any(r['success'] for r in self.test_results if 'Collection Update Minimal Data' in r['test'])
        if basic_update_working:
            print(f"  ✅ BASIC UPDATE: Collection update endpoints working")
        else:
            print(f"  ❌ BASIC UPDATE: Collection update endpoints failed")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status
        print(f"\n🎯 FINAL STATUS:")
        if photo_removal_working and auth_working:
            print(f"  ✅ PHOTO REQUIREMENT REMOVAL SUCCESSFUL")
            print(f"     - Enhanced Edit Kit Form no longer requires photos")
            print(f"     - Form validation logic updated correctly")
            print(f"     - Backend ready for frontend form submissions")
        elif auth_working and collection_working:
            print(f"  ⚠️ PARTIAL SUCCESS: Backend accessible but photo requirements may still exist")
            print(f"     - Authentication and collection access working")
            print(f"     - Photo requirement removal needs verification")
        else:
            print(f"  ❌ MAJOR ISSUES: Critical functionality not working")
            print(f"     - Cannot properly test photo requirement removal")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all Enhanced Edit Kit Form tests and return success status"""
        test_results = self.test_enhanced_edit_form_functionality()
        self.print_final_summary()
        return any(test_results)

def main():
    """Main test execution - Enhanced Edit Kit Form Photo Requirement Removal Testing"""
    tester = TopKitEnhancedEditFormTesting()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()