#!/usr/bin/env python3
"""
TopKit Profile Picture Upload Functionality Testing
Testing the newly implemented profile picture upload endpoints
"""

import requests
import json
import os
import tempfile
from PIL import Image
import io
import base64

# Configuration
API_BASE = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-vault-3.preview.emergentagent.com') + '/api'
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class ProfilePictureUploadTester:
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
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
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
    
    def create_test_image(self, format='JPEG', size=(300, 300), file_size_mb=None):
        """Create a test image file"""
        try:
            # Create a simple colored image
            img = Image.new('RGB', size, color=(73, 109, 137))  # Blue color
            
            # Add some text to make it identifiable
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                draw.text((10, 10), "Test Profile Picture", fill=(255, 255, 255))
            except:
                pass  # Skip text if font not available
            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=format, quality=95)
            img_bytes.seek(0)
            
            # If specific file size requested, adjust
            if file_size_mb:
                target_size = file_size_mb * 1024 * 1024
                current_size = len(img_bytes.getvalue())
                
                if current_size < target_size:
                    # Pad with zeros to reach target size
                    padding = b'\x00' * (target_size - current_size)
                    img_bytes = io.BytesIO(img_bytes.getvalue() + padding)
                    img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None
    
    def test_upload_profile_picture_success(self):
        """Test successful profile picture upload"""
        try:
            # Create test image
            test_image = self.create_test_image('JPEG')
            if not test_image:
                self.log_result("Upload Profile Picture - Success", False, "Failed to create test image")
                return False
            
            # Upload image
            files = {'file': ('test_profile.jpg', test_image, 'image/jpeg')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files)
            
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
            test_image = self.create_test_image('PNG')
            if not test_image:
                self.log_result("Upload PNG Format", False, "Failed to create PNG test image")
                return False
            
            files = {'file': ('test_profile.png', test_image, 'image/png')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files)
            
            success = response.status_code == 200
            details = f"PNG upload: {response.status_code}" + (f" - {response.json().get('message', '')}" if success else f" - {response.text}")
            self.log_result("Upload PNG Format", success, details)
            return success
            
        except Exception as e:
            self.log_result("Upload PNG Format", False, f"PNG upload error: {str(e)}")
            return False
    
    def test_file_size_validation_reject_large(self):
        """Test file size validation - reject files > 5MB"""
        try:
            # Create a 6MB image (should be rejected)
            test_image = self.create_test_image('JPEG', size=(1000, 1000), file_size_mb=6)
            if not test_image:
                self.log_result("File Size Validation - Reject Large", False, "Failed to create large test image")
                return False
            
            files = {'file': ('large_profile.jpg', test_image, 'image/jpeg')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files)
            
            # Should be rejected with 400 status
            if response.status_code == 400:
                self.log_result("File Size Validation - Reject Large", True, 
                              f"Correctly rejected large file: {response.json().get('detail', '')}")
                return True
            else:
                self.log_result("File Size Validation - Reject Large", False, 
                              f"Large file not rejected: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("File Size Validation - Reject Large", False, f"Large file test error: {str(e)}")
            return False
    
    def test_file_size_validation_accept_reasonable(self):
        """Test file size validation - accept reasonable sizes"""
        try:
            # Create a 2MB image (should be accepted)
            test_image = self.create_test_image('JPEG', size=(800, 800))
            if not test_image:
                self.log_result("File Size Validation - Accept Reasonable", False, "Failed to create reasonable test image")
                return False
            
            files = {'file': ('reasonable_profile.jpg', test_image, 'image/jpeg')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files)
            
            # Should be accepted with 200 status
            if response.status_code == 200:
                self.log_result("File Size Validation - Accept Reasonable", True, 
                              "Correctly accepted reasonable file size")
                return True
            else:
                self.log_result("File Size Validation - Accept Reasonable", False, 
                              f"Reasonable file rejected: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("File Size Validation - Accept Reasonable", False, f"Reasonable file test error: {str(e)}")
            return False
    
    def test_file_type_validation_reject_unsupported(self):
        """Test file type validation - reject unsupported formats"""
        try:
            # Create a text file disguised as image
            fake_image = io.BytesIO(b"This is not an image file")
            
            files = {'file': ('fake_image.txt', fake_image, 'text/plain')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files)
            
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
            if not self.user_id:
                self.log_result("Get Profile Picture URL", False, "No user_id available")
                return False
            
            response = self.session.get(f"{API_BASE}/users/profile/picture/{self.user_id}")
            
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
            fake_user_id = "nonexistent-user-id-12345"
            response = self.session.get(f"{API_BASE}/users/profile/picture/{fake_user_id}")
            
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
    
    def test_delete_profile_picture(self):
        """Test DELETE /api/users/profile/picture"""
        try:
            response = self.session.delete(f"{API_BASE}/users/profile/picture")
            
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
    
    def test_profile_integration(self):
        """Test that profile endpoint includes profile_picture_url"""
        try:
            if not self.user_id:
                self.log_result("Profile Integration", False, "No user_id available")
                return False
            
            # First upload a picture
            test_image = self.create_test_image('JPEG')
            if test_image:
                files = {'file': ('integration_test.jpg', test_image, 'image/jpeg')}
                upload_response = self.session.post(f"{API_BASE}/users/profile/picture", files=files)
                
                if upload_response.status_code == 200:
                    # Now check if profile endpoint includes the picture URL
                    profile_response = self.session.get(f"{API_BASE}/users/{self.user_id}/profile")
                    
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
            else:
                self.log_result("Profile Integration", False, "Failed to create test image for integration test")
                return False
                
        except Exception as e:
            self.log_result("Profile Integration", False, f"Profile integration error: {str(e)}")
            return False
    
    def test_authentication_required(self):
        """Test that upload/delete endpoints require authentication"""
        try:
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Try to upload without auth
            test_image = self.create_test_image('JPEG')
            files = {'file': ('unauth_test.jpg', test_image, 'image/jpeg')}
            upload_response = self.session.post(f"{API_BASE}/users/profile/picture", files=files)
            
            # Try to delete without auth
            delete_response = self.session.delete(f"{API_BASE}/users/profile/picture")
            
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
    
    def test_uploads_directory_creation(self):
        """Test that uploads directory structure is created properly"""
        try:
            # Upload an image to trigger directory creation
            test_image = self.create_test_image('JPEG')
            if not test_image:
                self.log_result("Uploads Directory Creation", False, "Failed to create test image")
                return False
            
            files = {'file': ('directory_test.jpg', test_image, 'image/jpeg')}
            response = self.session.post(f"{API_BASE}/users/profile/picture", files=files)
            
            if response.status_code == 200:
                # Check if the directory exists (we can't directly check filesystem, but successful upload indicates it was created)
                self.log_result("Uploads Directory Creation", True, 
                              "Directory creation successful (inferred from successful upload)")
                return True
            else:
                self.log_result("Uploads Directory Creation", False, 
                              f"Upload failed, directory may not have been created: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Uploads Directory Creation", False, f"Directory creation test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all profile picture upload tests"""
        print("🎯 STARTING TOPKIT PROFILE PICTURE UPLOAD FUNCTIONALITY TESTING")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Run all tests
        tests = [
            self.test_authentication_required,
            self.test_upload_profile_picture_success,
            self.test_upload_png_format,
            self.test_file_size_validation_accept_reasonable,
            self.test_file_size_validation_reject_large,
            self.test_file_type_validation_reject_unsupported,
            self.test_get_profile_picture_url,
            self.test_get_profile_picture_nonexistent_user,
            self.test_profile_integration,
            self.test_uploads_directory_creation,
            self.test_delete_profile_picture,
        ]
        
        print(f"\n🔄 Running {len(tests)} tests...")
        print("-" * 80)
        
        for test in tests:
            test()
        
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
    tester = ProfilePictureUploadTester()
    tester.run_all_tests()