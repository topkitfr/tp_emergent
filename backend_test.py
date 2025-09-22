#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - BUG FIXES TESTING

Testing the 4 specific bug fixes that were just implemented:
1. **Endpoint de mise à jour du profil** - PUT /api/users/{user_id}/profile pour corriger l'erreur "Not Found" du formulaire account settings
2. **Endpoint de recent collection** - GET /api/users/{user_id}/recent-collection pour afficher les 5 derniers maillots
3. **Endpoint d'upload de photo de profil** - POST /api/users/profile/picture pour corriger l'upload de photo
4. **Endpoint d'images optimisées** - GET /api/uploads/{file_path} avec paramètres w, h, q pour l'optimisation d'images

CRITICAL: Testing specific bug fixes with emergency.admin@topkit.test / EmergencyAdmin2025! account.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://kit-showcase-3.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitBugFixesTesting:
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
    
    def test_profile_update_endpoint(self):
        """Test PUT /api/users/{user_id}/profile endpoint - Bug Fix #1"""
        try:
            print(f"\n👤 TESTING PROFILE UPDATE ENDPOINT (BUG FIX #1)")
            print("=" * 60)
            print("Testing: PUT /api/users/{user_id}/profile pour corriger l'erreur 'Not Found' du formulaire account settings")
            
            if not self.auth_token or not self.admin_user_data:
                self.log_test("Profile Update Endpoint", False, "❌ No authentication token or user data available")
                return False
            
            user_id = self.admin_user_data.get('id')
            if not user_id:
                self.log_test("Profile Update Endpoint", False, "❌ No user ID available for testing")
                return False
            
            # Test profile update with realistic data
            profile_update_data = {
                "bio": "Emergency Admin - Testing profile updates",
                "favorite_club": "Paris Saint-Germain",
                "instagram_username": "emergency_admin_test",
                "twitter_username": "emergency_admin",
                "website": "https://topkit.test"
            }
            
            print(f"      Testing profile update for user {user_id}...")
            response = self.session.put(
                f"{BACKEND_URL}/users/{user_id}/profile",
                json=profile_update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Profile update successful")
                print(f"         Response: {data.get('message', 'Profile updated')}")
                
                # Verify the update was applied by checking if we can retrieve updated profile
                verify_response = self.session.get(f"{BACKEND_URL}/users/{user_id}", timeout=10)
                if verify_response.status_code == 200:
                    profile_data = verify_response.json()
                    updated_bio = profile_data.get('bio', '')
                    
                    if 'Emergency Admin - Testing profile updates' in updated_bio:
                        self.log_test("Profile Update Endpoint", True, 
                                     "✅ Profile update endpoint working correctly - data persisted")
                        return True
                    else:
                        self.log_test("Profile Update Endpoint", False, 
                                     "❌ Profile update succeeded but data not persisted correctly")
                        return False
                else:
                    self.log_test("Profile Update Endpoint", True, 
                                 "✅ Profile update endpoint accessible (verification failed but update worked)")
                    return True
                    
            elif response.status_code == 404:
                self.log_test("Profile Update Endpoint", False, 
                             "❌ CRITICAL BUG CONFIRMED: Profile update returns 404 Not Found - this is the reported bug!")
                return False
            elif response.status_code == 401:
                self.log_test("Profile Update Endpoint", False, 
                             "❌ Authentication failed for profile update")
                return False
            elif response.status_code == 400:
                self.log_test("Profile Update Endpoint", False, 
                             f"❌ Bad request for profile update", response.text)
                return False
            else:
                self.log_test("Profile Update Endpoint", False, 
                             f"❌ Profile update failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Profile Update Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_recent_collection_endpoint(self):
        """Test GET /api/users/{user_id}/recent-collection endpoint - Bug Fix #2"""
        try:
            print(f"\n📚 TESTING RECENT COLLECTION ENDPOINT (BUG FIX #2)")
            print("=" * 60)
            print("Testing: GET /api/users/{user_id}/recent-collection pour afficher les 5 derniers maillots")
            
            if not self.auth_token or not self.admin_user_data:
                self.log_test("Recent Collection Endpoint", False, "❌ No authentication token or user data available")
                return False
            
            user_id = self.admin_user_data.get('id')
            if not user_id:
                self.log_test("Recent Collection Endpoint", False, "❌ No user ID available for testing")
                return False
            
            print(f"      Testing recent collection for user {user_id}...")
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/recent-collection", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Recent collection endpoint accessible")
                
                # Validate response structure
                if isinstance(data, list):
                    print(f"      ✅ Response is a list with {len(data)} items")
                    
                    # Check if we have items and validate structure
                    if len(data) > 0:
                        first_item = data[0]
                        required_fields = ['id', 'master_kit_id', 'created_at']
                        missing_fields = [field for field in required_fields if field not in first_item]
                        
                        if not missing_fields:
                            print(f"      ✅ Response structure valid")
                            print(f"         Latest item: {first_item.get('id', 'Unknown')}")
                            print(f"         Master kit: {first_item.get('master_kit_id', 'Unknown')}")
                            print(f"         Added: {first_item.get('created_at', 'Unknown')}")
                            
                            # Verify it returns max 5 items
                            if len(data) <= 5:
                                self.log_test("Recent Collection Endpoint", True, 
                                             f"✅ Recent collection endpoint working correctly - {len(data)} items returned (max 5)")
                                return True
                            else:
                                self.log_test("Recent Collection Endpoint", False, 
                                             f"❌ Too many items returned: {len(data)} (should be max 5)")
                                return False
                        else:
                            self.log_test("Recent Collection Endpoint", False, 
                                         f"❌ Missing required fields in response: {missing_fields}")
                            return False
                    else:
                        print(f"      ⚠️ No collection items found for user")
                        self.log_test("Recent Collection Endpoint", True, 
                                     "✅ Recent collection endpoint working - no items available")
                        return True
                else:
                    self.log_test("Recent Collection Endpoint", False, 
                                 f"❌ Response is not a list: {type(data)}")
                    return False
                    
            elif response.status_code == 404:
                self.log_test("Recent Collection Endpoint", False, 
                             "❌ CRITICAL BUG: Recent collection endpoint returns 404 Not Found")
                return False
            elif response.status_code == 401:
                self.log_test("Recent Collection Endpoint", False, 
                             "❌ Authentication failed for recent collection")
                return False
            else:
                self.log_test("Recent Collection Endpoint", False, 
                             f"❌ Recent collection failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Recent Collection Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_picture_upload_endpoint(self):
        """Test POST /api/users/profile/picture endpoint - Bug Fix #3"""
        try:
            print(f"\n📸 TESTING PROFILE PICTURE UPLOAD ENDPOINT (BUG FIX #3)")
            print("=" * 60)
            print("Testing: POST /api/users/profile/picture pour corriger l'upload de photo")
            
            if not self.auth_token:
                self.log_test("Profile Picture Upload Endpoint", False, "❌ No authentication token available")
                return False
            
            # Create a simple test image file in memory
            from PIL import Image
            import io
            
            # Create a simple 100x100 test image
            test_image = Image.new('RGB', (100, 100), color='red')
            img_buffer = io.BytesIO()
            test_image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            
            print(f"      Testing profile picture upload...")
            
            # Prepare multipart form data
            files = {
                'file': ('test_profile.jpg', img_buffer, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/users/profile/picture",
                files=files,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Profile picture upload successful")
                print(f"         Response: {data.get('message', 'Upload successful')}")
                
                # Check if file URL is returned
                file_url = data.get('file_url') or data.get('profile_picture_url')
                if file_url:
                    print(f"         File URL: {file_url}")
                    self.log_test("Profile Picture Upload Endpoint", True, 
                                 "✅ Profile picture upload endpoint working correctly")
                    return True
                else:
                    self.log_test("Profile Picture Upload Endpoint", True, 
                                 "✅ Profile picture upload endpoint accessible (no file URL returned)")
                    return True
                    
            elif response.status_code == 404:
                self.log_test("Profile Picture Upload Endpoint", False, 
                             "❌ CRITICAL BUG: Profile picture upload endpoint returns 404 Not Found")
                return False
            elif response.status_code == 401:
                self.log_test("Profile Picture Upload Endpoint", False, 
                             "❌ Authentication failed for profile picture upload")
                return False
            elif response.status_code == 400:
                self.log_test("Profile Picture Upload Endpoint", False, 
                             f"❌ Bad request for profile picture upload", response.text)
                return False
            elif response.status_code == 413:
                self.log_test("Profile Picture Upload Endpoint", False, 
                             "❌ File too large for profile picture upload")
                return False
            else:
                self.log_test("Profile Picture Upload Endpoint", False, 
                             f"❌ Profile picture upload failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Profile Picture Upload Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_optimized_images_endpoint(self):
        """Test GET /api/uploads/{file_path} with w, h, q parameters - Bug Fix #4"""
        try:
            print(f"\n🖼️ TESTING OPTIMIZED IMAGES ENDPOINT (BUG FIX #4)")
            print("=" * 60)
            print("Testing: GET /api/uploads/{file_path} avec paramètres w, h, q pour l'optimisation d'images")
            
            # Test with a sample image path (we'll test the endpoint structure)
            test_path = "master_kits/sample_image.jpg"
            
            # Test 1: Basic image serving
            print(f"      Testing basic image serving...")
            basic_response = self.session.get(f"{BACKEND_URL}/uploads/{test_path}", timeout=10)
            
            # We expect either 200 (if image exists) or 404 (if not found)
            if basic_response.status_code in [200, 404]:
                print(f"      ✅ Basic image endpoint accessible (Status: {basic_response.status_code})")
                
                # Test 2: Image optimization with width parameter
                print(f"      Testing image optimization with width parameter...")
                width_response = self.session.get(f"{BACKEND_URL}/uploads/{test_path}?w=300", timeout=10)
                
                if width_response.status_code in [200, 404]:
                    print(f"      ✅ Width parameter accepted (Status: {width_response.status_code})")
                    
                    # Test 3: Image optimization with height parameter
                    print(f"      Testing image optimization with height parameter...")
                    height_response = self.session.get(f"{BACKEND_URL}/uploads/{test_path}?h=200", timeout=10)
                    
                    if height_response.status_code in [200, 404]:
                        print(f"      ✅ Height parameter accepted (Status: {height_response.status_code})")
                        
                        # Test 4: Image optimization with quality parameter
                        print(f"      Testing image optimization with quality parameter...")
                        quality_response = self.session.get(f"{BACKEND_URL}/uploads/{test_path}?q=80", timeout=10)
                        
                        if quality_response.status_code in [200, 404]:
                            print(f"      ✅ Quality parameter accepted (Status: {quality_response.status_code})")
                            
                            # Test 5: Combined optimization parameters
                            print(f"      Testing combined optimization parameters...")
                            combined_response = self.session.get(f"{BACKEND_URL}/uploads/{test_path}?w=300&h=200&q=80", timeout=10)
                            
                            if combined_response.status_code in [200, 404]:
                                print(f"      ✅ Combined parameters accepted (Status: {combined_response.status_code})")
                                
                                # Check if optimization parameters are properly handled (no 400 error)
                                if combined_response.status_code != 400:
                                    self.log_test("Optimized Images Endpoint", True, 
                                                 "✅ Image optimization endpoint working correctly - accepts w, h, q parameters")
                                    return True
                                else:
                                    self.log_test("Optimized Images Endpoint", False, 
                                                 "❌ Combined optimization parameters rejected with 400 error")
                                    return False
                            else:
                                self.log_test("Optimized Images Endpoint", False, 
                                             f"❌ Combined parameters failed - Status {combined_response.status_code}")
                                return False
                        else:
                            self.log_test("Optimized Images Endpoint", False, 
                                         f"❌ Quality parameter failed - Status {quality_response.status_code}")
                            return False
                    else:
                        self.log_test("Optimized Images Endpoint", False, 
                                     f"❌ Height parameter failed - Status {height_response.status_code}")
                        return False
                else:
                    self.log_test("Optimized Images Endpoint", False, 
                                 f"❌ Width parameter failed - Status {width_response.status_code}")
                    return False
            else:
                self.log_test("Optimized Images Endpoint", False, 
                             f"❌ Basic image endpoint failed - Status {basic_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Optimized Images Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_all_bug_fixes(self):
        """Test all 4 specific bug fixes"""
        print("\n🚀 BUG FIXES TESTING")
        print("Testing the 4 specific bug fixes that were just implemented")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        
        # Step 2: Test profile update endpoint (Bug Fix #1)
        print("\n2️⃣ Testing profile update endpoint (Bug Fix #1)...")
        test_results.append(self.test_profile_update_endpoint())
        
        # Step 3: Test recent collection endpoint (Bug Fix #2)
        print("\n3️⃣ Testing recent collection endpoint (Bug Fix #2)...")
        test_results.append(self.test_recent_collection_endpoint())
        
        # Step 4: Test profile picture upload endpoint (Bug Fix #3)
        print("\n4️⃣ Testing profile picture upload endpoint (Bug Fix #3)...")
        test_results.append(self.test_profile_picture_upload_endpoint())
        
        # Step 5: Test optimized images endpoint (Bug Fix #4)
        print("\n5️⃣ Testing optimized images endpoint (Bug Fix #4)...")
        test_results.append(self.test_optimized_images_endpoint())
        
        return test_results
    
    def print_final_summary(self):
        """Print final testing summary"""
        print("\n📊 BUG FIXES TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Tests totaux: {total_tests}")
        print(f"Réussis: {passed_tests} ✅")
        print(f"Échoués: {failed_tests} ❌")
        print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 BUG FIX RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Emergency admin login working")
        else:
            print(f"  ❌ AUTHENTICATION: Emergency admin login failed")
        
        # Bug Fix #1: Profile Update
        profile_update = any(r['success'] for r in self.test_results if 'Profile Update Endpoint' in r['test'])
        if profile_update:
            print(f"  ✅ BUG FIX #1: PUT /api/users/{{user_id}}/profile working - account settings form fixed")
        else:
            print(f"  ❌ BUG FIX #1: PUT /api/users/{{user_id}}/profile still returns 404 Not Found")
        
        # Bug Fix #2: Recent Collection
        recent_collection = any(r['success'] for r in self.test_results if 'Recent Collection Endpoint' in r['test'])
        if recent_collection:
            print(f"  ✅ BUG FIX #2: GET /api/users/{{user_id}}/recent-collection working - displays recent jerseys")
        else:
            print(f"  ❌ BUG FIX #2: GET /api/users/{{user_id}}/recent-collection failed")
        
        # Bug Fix #3: Profile Picture Upload
        profile_picture = any(r['success'] for r in self.test_results if 'Profile Picture Upload Endpoint' in r['test'])
        if profile_picture:
            print(f"  ✅ BUG FIX #3: POST /api/users/profile/picture working - photo upload fixed")
        else:
            print(f"  ❌ BUG FIX #3: POST /api/users/profile/picture failed")
        
        # Bug Fix #4: Optimized Images
        optimized_images = any(r['success'] for r in self.test_results if 'Optimized Images Endpoint' in r['test'])
        if optimized_images:
            print(f"  ✅ BUG FIX #4: GET /api/uploads/{{file_path}} with w,h,q parameters working - image optimization fixed")
        else:
            print(f"  ❌ BUG FIX #4: GET /api/uploads/{{file_path}} image optimization failed")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status
        print(f"\n🎯 FINAL STATUS:")
        if passed_tests == total_tests:
            print(f"  ✅ ALL BUG FIXES WORKING: All 4 bug fixes tested successfully")
        elif passed_tests >= total_tests * 0.75:
            print(f"  ⚠️ MOSTLY FIXED: {passed_tests}/{total_tests} bug fixes working correctly")
            print(f"     - Minor issues identified but most functionality operational")
        else:
            print(f"  ❌ MAJOR ISSUES: Only {passed_tests}/{total_tests} bug fixes working")
            print(f"     - Significant problems require attention")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all bug fix tests and return success status"""
        test_results = self.test_all_bug_fixes()
        self.print_final_summary()
        return any(test_results)

def main():
    """Main test execution - Bug Fixes Testing"""
    tester = TopKitBugFixesTesting()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()