#!/usr/bin/env python3
"""
TopKit Backend Testing - Image Saving Functionality
Testing the new image saving feature for jersey submissions
"""

import requests
import json
import os
import time
from pathlib import Path
import tempfile
from PIL import Image
import io

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"
TEST_USER_EMAIL = "topkitfr@gmail.com"
TEST_USER_PASSWORD = "TopKitSecure789#"

class TopKitImageSavingTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_data = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def authenticate_user(self):
        """Authenticate test user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data["token"]
                self.user_data = data["user"]
                self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                
                self.log_result(
                    "User Authentication",
                    True,
                    f"Successfully authenticated user {self.user_data['name']}",
                    {
                        "user_id": self.user_data["id"],
                        "email": self.user_data["email"],
                        "role": self.user_data["role"]
                    }
                )
                return True
            else:
                self.log_result(
                    "User Authentication",
                    False,
                    f"Authentication failed: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def create_test_image(self, filename, color=(255, 0, 0), size=(200, 200)):
        """Create a test image file"""
        try:
            # Create a simple colored image
            image = Image.new('RGB', size, color)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}")
            image.save(temp_file.name, 'JPEG')
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None
    
    def test_jersey_submission_with_images(self):
        """Test jersey submission with front and back images"""
        try:
            # Create test images
            front_image_path = self.create_test_image("front_test.jpg", color=(255, 0, 0))  # Red
            back_image_path = self.create_test_image("back_test.jpg", color=(0, 0, 255))   # Blue
            
            if not front_image_path or not back_image_path:
                self.log_result(
                    "Jersey Submission with Images",
                    False,
                    "Failed to create test images"
                )
                return None
            
            # Prepare form data
            form_data = {
                'team': 'Real Madrid CF',
                'league': 'La Liga',
                'season': '2024-25',
                'model': 'authentic',
                'manufacturer': 'Adidas',
                'jersey_type': 'home',
                'sku_code': 'RM-HOME-2425',
                'description': 'Test jersey submission with image saving functionality'
            }
            
            # Prepare files
            files = {}
            with open(front_image_path, 'rb') as f:
                front_content = f.read()
            with open(back_image_path, 'rb') as f:
                back_content = f.read()
            
            files['front_photo'] = ('front_test.jpg', front_content, 'image/jpeg')
            files['back_photo'] = ('back_test.jpg', back_content, 'image/jpeg')
            
            # Submit jersey
            response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                data=form_data,
                files=files
            )
            
            # Clean up temporary files
            os.unlink(front_image_path)
            os.unlink(back_image_path)
            
            if response.status_code == 200:
                jersey_data = response.json()
                jersey_id = jersey_data.get('id')
                
                self.log_result(
                    "Jersey Submission with Images",
                    True,
                    f"Jersey submitted successfully with ID: {jersey_id}",
                    {
                        "jersey_id": jersey_id,
                        "reference_number": jersey_data.get('reference_number'),
                        "status": jersey_data.get('status'),
                        "front_photo_url": jersey_data.get('front_photo_url'),
                        "back_photo_url": jersey_data.get('back_photo_url')
                    }
                )
                return jersey_data
            else:
                self.log_result(
                    "Jersey Submission with Images",
                    False,
                    f"Jersey submission failed: {response.status_code}",
                    {"response": response.text}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Jersey Submission with Images",
                False,
                f"Jersey submission error: {str(e)}"
            )
            return None
    
    def verify_image_files_created(self, jersey_data):
        """Verify that image files were actually created on disk"""
        if not jersey_data:
            return False
            
        jersey_id = jersey_data.get('id')
        front_photo_url = jersey_data.get('front_photo_url')
        back_photo_url = jersey_data.get('back_photo_url')
        
        if not jersey_id:
            self.log_result(
                "Image Files Creation Verification",
                False,
                "No jersey ID provided for verification"
            )
            return False
        
        # Expected directory path
        expected_dir = f"/app/frontend/public/uploads/jerseys/{jersey_id}"
        
        try:
            # Check if directory exists
            if os.path.exists(expected_dir):
                dir_exists = True
                files_in_dir = os.listdir(expected_dir)
            else:
                dir_exists = False
                files_in_dir = []
            
            # Check for front photo file
            front_file_exists = False
            front_file_path = None
            if front_photo_url:
                # Extract filename from URL
                front_filename = front_photo_url.split('/')[-1]
                front_file_path = os.path.join(expected_dir, front_filename)
                front_file_exists = os.path.exists(front_file_path)
            
            # Check for back photo file
            back_file_exists = False
            back_file_path = None
            if back_photo_url:
                # Extract filename from URL
                back_filename = back_photo_url.split('/')[-1]
                back_file_path = os.path.join(expected_dir, back_filename)
                back_file_exists = os.path.exists(back_file_path)
            
            # Verify file sizes (should be > 0)
            front_file_size = 0
            back_file_size = 0
            if front_file_exists and front_file_path:
                front_file_size = os.path.getsize(front_file_path)
            if back_file_exists and back_file_path:
                back_file_size = os.path.getsize(back_file_path)
            
            success = dir_exists and front_file_exists and back_file_exists and front_file_size > 0 and back_file_size > 0
            
            self.log_result(
                "Image Files Creation Verification",
                success,
                f"Image files verification: {'SUCCESS' if success else 'FAILED'}",
                {
                    "expected_directory": expected_dir,
                    "directory_exists": dir_exists,
                    "files_in_directory": files_in_dir,
                    "front_photo_url": front_photo_url,
                    "front_file_exists": front_file_exists,
                    "front_file_size": f"{front_file_size} bytes",
                    "back_photo_url": back_photo_url,
                    "back_file_exists": back_file_exists,
                    "back_file_size": f"{back_file_size} bytes"
                }
            )
            
            return success
            
        except Exception as e:
            self.log_result(
                "Image Files Creation Verification",
                False,
                f"Error verifying image files: {str(e)}"
            )
            return False
    
    def verify_image_urls_format(self, jersey_data):
        """Verify that returned URLs point to correct paths"""
        if not jersey_data:
            return False
            
        jersey_id = jersey_data.get('id')
        front_photo_url = jersey_data.get('front_photo_url')
        back_photo_url = jersey_data.get('back_photo_url')
        
        # Expected URL format: uploads/jerseys/{jersey_id}/{filename}
        expected_front_pattern = f"uploads/jerseys/{jersey_id}/front_"
        expected_back_pattern = f"uploads/jerseys/{jersey_id}/back_"
        
        front_url_correct = front_photo_url and front_photo_url.startswith(expected_front_pattern)
        back_url_correct = back_photo_url and back_photo_url.startswith(expected_back_pattern)
        
        success = front_url_correct and back_url_correct
        
        self.log_result(
            "Image URLs Format Verification",
            success,
            f"URL format verification: {'SUCCESS' if success else 'FAILED'}",
            {
                "jersey_id": jersey_id,
                "front_photo_url": front_photo_url,
                "front_url_correct": front_url_correct,
                "expected_front_pattern": expected_front_pattern,
                "back_photo_url": back_photo_url,
                "back_url_correct": back_url_correct,
                "expected_back_pattern": expected_back_pattern
            }
        )
        
        return success
    
    def test_jersey_submission_without_images(self):
        """Test jersey submission without images (should still work)"""
        try:
            # Prepare form data without images
            form_data = {
                'team': 'FC Barcelona',
                'league': 'La Liga',
                'season': '2024-25',
                'model': 'replica',
                'manufacturer': 'Nike',
                'jersey_type': 'away',
                'description': 'Test jersey submission without images'
            }
            
            # Submit jersey without files
            response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                data=form_data
            )
            
            if response.status_code == 200:
                jersey_data = response.json()
                jersey_id = jersey_data.get('id')
                
                # Should have no photo URLs
                front_photo_url = jersey_data.get('front_photo_url')
                back_photo_url = jersey_data.get('back_photo_url')
                
                success = not front_photo_url and not back_photo_url
                
                self.log_result(
                    "Jersey Submission without Images",
                    success,
                    f"Jersey submitted without images: {'SUCCESS' if success else 'FAILED'}",
                    {
                        "jersey_id": jersey_id,
                        "reference_number": jersey_data.get('reference_number'),
                        "status": jersey_data.get('status'),
                        "front_photo_url": front_photo_url,
                        "back_photo_url": back_photo_url
                    }
                )
                return success
            else:
                self.log_result(
                    "Jersey Submission without Images",
                    False,
                    f"Jersey submission failed: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Jersey Submission without Images",
                False,
                f"Jersey submission error: {str(e)}"
            )
            return False
    
    def check_uploads_directory_structure(self):
        """Check the overall uploads directory structure"""
        try:
            base_uploads_dir = "/app/frontend/public/uploads"
            jerseys_uploads_dir = "/app/frontend/public/uploads/jerseys"
            
            base_exists = os.path.exists(base_uploads_dir)
            jerseys_exists = os.path.exists(jerseys_uploads_dir)
            
            jersey_dirs = []
            if jerseys_exists:
                try:
                    jersey_dirs = [d for d in os.listdir(jerseys_uploads_dir) 
                                 if os.path.isdir(os.path.join(jerseys_uploads_dir, d))]
                except:
                    jersey_dirs = []
            
            self.log_result(
                "Uploads Directory Structure Check",
                base_exists and jerseys_exists,
                f"Directory structure check: {'SUCCESS' if base_exists and jerseys_exists else 'PARTIAL'}",
                {
                    "base_uploads_dir": base_uploads_dir,
                    "base_exists": base_exists,
                    "jerseys_uploads_dir": jerseys_uploads_dir,
                    "jerseys_exists": jerseys_exists,
                    "jersey_directories_count": len(jersey_dirs),
                    "jersey_directories": jersey_dirs[:5] if len(jersey_dirs) <= 5 else jersey_dirs[:5] + ["..."]
                }
            )
            
            return base_exists and jerseys_exists
            
        except Exception as e:
            self.log_result(
                "Uploads Directory Structure Check",
                False,
                f"Error checking directory structure: {str(e)}"
            )
            return False
    
    def run_comprehensive_test(self):
        """Run all image saving tests"""
        print("🚀 Starting TopKit Image Saving Functionality Tests")
        print("=" * 60)
        
        # Step 1: Authenticate user
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Check directory structure
        self.check_uploads_directory_structure()
        
        # Step 3: Test jersey submission with images
        jersey_data = self.test_jersey_submission_with_images()
        
        # Step 4: Verify image files were created
        if jersey_data:
            self.verify_image_files_created(jersey_data)
            self.verify_image_urls_format(jersey_data)
        
        # Step 5: Test jersey submission without images
        self.test_jersey_submission_without_images()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        # Overall assessment
        critical_tests = [
            "User Authentication",
            "Jersey Submission with Images", 
            "Image Files Creation Verification",
            "Image URLs Format Verification"
        ]
        
        critical_success = all(
            result["success"] for result in self.test_results 
            if result["test"] in critical_tests
        )
        
        print(f"\n🎯 CRITICAL FUNCTIONALITY: {'✅ WORKING' if critical_success else '❌ FAILED'}")
        
        if critical_success:
            print("🎉 Image saving functionality is working correctly!")
            print("✅ Images are being saved to disk in the correct directory structure")
            print("✅ URLs are being generated with the correct format")
            print("✅ File system integration is operational")
        else:
            print("🚨 Image saving functionality has issues that need attention")
            
        return critical_success

def main():
    """Main test execution"""
    tester = TopKitImageSavingTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 ALL CRITICAL TESTS PASSED - Image saving functionality is working!")
    else:
        print("\n🚨 SOME CRITICAL TESTS FAILED - Image saving functionality needs fixes")
    
    return success

if __name__ == "__main__":
    main()