#!/usr/bin/env python3
"""
TopKit Profile Picture Upload Functionality Testing - Simplified Version
Testing the newly implemented profile picture upload endpoints without PIL dependency
"""

import requests
import json
import os
import io

# Configuration
API_BASE = "http://localhost:8001/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class SimpleProfilePictureUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def authenticate(self):
        """Authenticate test user"""
        try:
            print("🔐 Attempting authentication...")
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.user_id = data.get('user', {}).get('id')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                self.log_result("Authentication", True, f"Successfully authenticated user {TEST_USER_EMAIL}")
                return True
            else:
                self.log_result("Authentication", False, f"Failed to authenticate: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def create_simple_test_file(self, content_type='image/jpeg', filename='test.jpg'):
        """Create a simple test file"""
        # Create a minimal JPEG header for testing
        if content_type == 'image/jpeg':
            # Minimal JPEG file header
            jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'
            test_data = jpeg_header + b'\x00' * 100  # Add some padding
        elif content_type == 'image/png':
            # Minimal PNG file header
            png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
            test_data = png_header + b'\x00' * 50
        else:
            test_data = b"This is a test file content"
        
        return io.BytesIO(test_data)
    
    def test_authentication_required(self):
        """Test that upload/delete endpoints require authentication"""
        try:
            print("🔒 Testing authentication requirements...")
            
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Try to upload without auth
            test_file = self.create_simple_test_file()
            files = {'file': ('unauth_test.jpg', test_file, 'image/jpeg')}
            upload_response = self.session.post(f"{API_BASE}/users/profile/picture", files=files, timeout=30)
            
            # Try to delete without auth
            delete_response = self.session.delete(f"{API_BASE}/users/profile/picture", timeout=30)
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            # Both should return 401
            upload_auth_required = upload_response.status_code == 401
            delete_auth_required = delete_response.status_code == 401
            
            if upload_auth_required and delete_auth_required:
                self.log_result("Authentication Required", True, 
                              "Both upload and delete correctly require authentication")
                return True
            else:
                self.log_result("Authentication Required", False, 
                              f"Auth check failed - Upload: {upload_response.status_code}, Delete: {delete_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Required", False, f"Auth test error: {str(e)}")
            return False
    
    def test_upload_profile_picture_success(self):
        """Test successful profile picture upload"""
        try:
            print("📤 Testing profile picture upload...")
            
            # Create test file
            test_file = self.create_simple_test_file('image/jpeg', 'test_profile.jpg')
            
            # Upload file
            files = {'file': ('test_profile.jpg', test_file, 'image/jpeg')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'profile_picture_url' in data:
                    self.log_result("Upload Profile Picture - Success", True, 
                                  f"Successfully uploaded profile picture: {data['profile_picture_url']}")
                    return True
                else:
                    self.log_result("Upload Profile Picture - Success", False, 
                                  "Response missing profile_picture_url field")
                    return False
            else:
                self.log_result("Upload Profile Picture - Success", False, 
                              f"Upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Upload Profile Picture - Success", False, f"Upload error: {str(e)}")
            return False
    
    def test_upload_png_format(self):
        """Test PNG format upload"""
        try:
            print("🖼️ Testing PNG format upload...")
            
            test_file = self.create_simple_test_file('image/png', 'test_profile.png')
            files = {'file': ('test_profile.png', test_file, 'image/png')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files, timeout=30)
            
            success = response.status_code == 200
            details = f"PNG upload: {response.status_code}" + (f" - {response.json().get('message', '')}" if success else f" - {response.text}")
            self.log_result("Upload PNG Format", success, details)
            return success
            
        except Exception as e:
            self.log_result("Upload PNG Format", False, f"PNG upload error: {str(e)}")
            return False
    
    def test_file_type_validation_reject_unsupported(self):
        """Test file type validation - reject unsupported formats"""
        try:
            print("🚫 Testing unsupported file type rejection...")
            
            # Create a text file disguised as image
            fake_file = io.BytesIO(b"This is not an image file")
            
            files = {'file': ('fake_image.txt', fake_file, 'text/plain')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files, timeout=30)
            
            # Should be rejected with 400 status
            if response.status_code == 400:
                self.log_result("File Type Validation - Reject Unsupported", True, 
                              f"Correctly rejected unsupported file type: {response.json().get('detail', '')}")
                return True
            else:
                self.log_result("File Type Validation - Reject Unsupported", False, 
                              f"Unsupported file not rejected: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("File Type Validation - Reject Unsupported", False, f"Unsupported file test error: {str(e)}")
            return False
    
    def test_get_profile_picture_url(self):
        """Test GET /api/users/profile/picture/{user_id}"""
        try:
            print("📥 Testing profile picture URL retrieval...")
            
            if not self.user_id:
                self.log_result("Get Profile Picture URL", False, "No user_id available")
                return False
            
            response = self.session.get(f"{API_BASE}/users/profile/picture/{self.user_id}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'profile_picture_url' in data:
                    picture_url = data['profile_picture_url']
                    if picture_url:
                        self.log_result("Get Profile Picture URL", True, 
                                      f"Successfully retrieved profile picture URL: {picture_url}")
                    else:
                        self.log_result("Get Profile Picture URL", True, 
                                      "Successfully retrieved null profile picture URL (no picture uploaded)")
                    return True
                else:
                    self.log_result("Get Profile Picture URL", False, 
                                  "Response missing profile_picture_url field")
                    return False
            else:
                self.log_result("Get Profile Picture URL", False, 
                              f"Failed to get profile picture: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Get Profile Picture URL", False, f"Get profile picture error: {str(e)}")
            return False
    
    def test_get_profile_picture_nonexistent_user(self):
        """Test GET profile picture for non-existent user"""
        try:
            print("👻 Testing nonexistent user profile picture...")
            
            fake_user_id = "nonexistent-user-id-12345"
            response = self.session.get(f"{API_BASE}/users/profile/picture/{fake_user_id}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('profile_picture_url') is None:
                    self.log_result("Get Profile Picture - Nonexistent User", True, 
                                  "Correctly returned null for nonexistent user")
                    return True
                else:
                    self.log_result("Get Profile Picture - Nonexistent User", False, 
                                  "Should return null for nonexistent user")
                    return False
            else:
                self.log_result("Get Profile Picture - Nonexistent User", False, 
                              f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Get Profile Picture - Nonexistent User", False, f"Nonexistent user test error: {str(e)}")
            return False
    
    def test_profile_integration(self):
        """Test that profile endpoint includes profile_picture_url"""
        try:
            print("🔗 Testing profile integration...")
            
            if not self.user_id:
                self.log_result("Profile Integration", False, "No user_id available")
                return False
            
            # First upload a picture
            test_file = self.create_simple_test_file('image/jpeg', 'integration_test.jpg')
            files = {'file': ('integration_test.jpg', test_file, 'image/jpeg')}
            upload_response = self.session.post(f"{API_BASE}/users/profile/picture", files=files, timeout=30)
            
            if upload_response.status_code == 200:
                # Now check if profile endpoint includes the picture URL
                profile_response = self.session.get(f"{API_BASE}/users/{self.user_id}/profile", timeout=30)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    if 'profile_picture_url' in profile_data:
                        self.log_result("Profile Integration", True, 
                                      f"Profile endpoint includes profile_picture_url: {profile_data['profile_picture_url']}")
                        return True
                    else:
                        self.log_result("Profile Integration", False, 
                                      "Profile endpoint missing profile_picture_url field")
                        return False
                else:
                    self.log_result("Profile Integration", False, 
                                  f"Failed to get profile: {profile_response.status_code}")
                    return False
            else:
                self.log_result("Profile Integration", False, 
                              f"Failed to upload test image for integration test: {upload_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Profile Integration", False, f"Profile integration error: {str(e)}")
            return False
    
    def test_delete_profile_picture(self):
        """Test DELETE /api/users/profile/picture"""
        try:
            print("🗑️ Testing profile picture deletion...")
            
            response = self.session.delete(f"{API_BASE}/users/profile/picture", timeout=30)
            
            if response.status_code == 200:
                self.log_result("Delete Profile Picture", True, 
                              f"Successfully deleted profile picture: {response.json().get('message', '')}")
                return True
            elif response.status_code == 404:
                self.log_result("Delete Profile Picture", True, 
                              "No profile picture to delete (404 expected if no picture exists)")
                return True
            else:
                self.log_result("Delete Profile Picture", False, 
                              f"Delete failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Delete Profile Picture", False, f"Delete error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all profile picture upload tests"""
        print("🎯 STARTING TOPKIT PROFILE PICTURE UPLOAD FUNCTIONALITY TESTING")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run all tests
        tests = [
            self.test_authentication_required,
            self.test_upload_profile_picture_success,
            self.test_upload_png_format,
            self.test_file_type_validation_reject_unsupported,
            self.test_get_profile_picture_url,
            self.test_get_profile_picture_nonexistent_user,
            self.test_profile_integration,
            self.test_delete_profile_picture,
        ]
        
        print(f"\n🔄 Running {len(tests)} tests...")
        print("-" * 80)
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Profile picture upload functionality is working perfectly!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Review the details above.")
        
        return success_rate >= 80  # Consider 80%+ as success

if __name__ == "__main__":
    tester = SimpleProfilePictureUploadTester()
    tester.run_all_tests()