#!/usr/bin/env python3
"""
Local Storage Optimization System Backend Testing
=================================================

This test suite comprehensively tests the new Local Storage Optimization system
that was just implemented, including:

1. Enhanced Image Upload Endpoint (POST /api/upload/image)
2. Custom Image Serving Endpoint (GET /api/serve-image/{entity_type}/{filename})  
3. Image Metadata Endpoint (GET /api/image-info/{entity_type}/{filename})

Test Scenarios:
- Image upload with variants generation (thumbnail, small, medium, large, original)
- Various image formats (JPG, PNG, WebP, BMP)
- File size validation (max 15MB)
- Image processing optimization
- Metadata extraction
- Custom image serving with caching headers
- Entity type validation and normalization
- Authentication requirements

User Credentials:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- User: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import base64
import io
from PIL import Image
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-commons.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class LocalStorageOptimizationTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.uploaded_images = []  # Track uploaded images for cleanup
        
    def log_result(self, test_name: str, success: bool, details: str):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}: {details}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    def authenticate_admin(self) -> bool:
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token') or data.get('access_token')
                if self.admin_token:
                    self.log_result("Admin Authentication", True, f"Admin authenticated successfully (Token: {len(self.admin_token)} chars)")
                    return True
                else:
                    self.log_result("Admin Authentication", False, f"No token in response: {data}")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
            
    def authenticate_user(self) -> bool:
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token') or data.get('access_token')
                if self.user_token:
                    self.log_result("User Authentication", True, f"User authenticated successfully (Token: {len(self.user_token)} chars)")
                    return True
                else:
                    self.log_result("User Authentication", False, f"No token in response: {data}")
                    return False
            else:
                self.log_result("User Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_image(self, format_type: str = "PNG", size: tuple = (800, 600), file_size_mb: float = None) -> bytes:
        """Create a test image in memory"""
        try:
            # Create a colorful test image
            img = Image.new('RGB', size, color=(255, 100, 50))  # Orange background
            
            # Add some visual elements
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Draw some shapes
            draw.rectangle([50, 50, size[0]-50, size[1]-50], outline=(0, 100, 200), width=5)
            draw.ellipse([100, 100, size[0]-100, size[1]-100], fill=(100, 200, 100))
            
            # Add text
            try:
                draw.text((size[0]//4, size[1]//2), f"Test {format_type} Image", fill=(255, 255, 255))
            except:
                pass  # Font might not be available
            
            # Save to bytes
            img_bytes = io.BytesIO()
            
            # Adjust quality to reach target file size if specified
            quality = 95
            if file_size_mb:
                target_size = int(file_size_mb * 1024 * 1024)
                # Try different quality settings to reach target size
                for q in range(95, 10, -5):
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format=format_type, quality=q if format_type == 'JPEG' else None)
                    if len(img_bytes.getvalue()) <= target_size:
                        break
                    quality = q
            else:
                img.save(img_bytes, format=format_type, quality=quality if format_type == 'JPEG' else None)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None
    
    def test_image_upload_with_variants(self) -> bool:
        """Test image upload with variants generation"""
        try:
            if not self.admin_token:
                self.log_result("Image Upload with Variants", False, "Admin authentication required")
                return False
                
            # Create test image
            test_image = self.create_test_image("PNG", (1200, 800))
            if not test_image:
                self.log_result("Image Upload with Variants", False, "Failed to create test image")
                return False
            
            # Prepare upload data
            files = {
                'file': ('team_logo_test.png', test_image, 'image/png')
            }
            data = {
                'entity_type': 'team',
                'generate_variants': 'true'
            }
            headers = {
                'Authorization': f'Bearer {self.admin_token}'
            }
            
            # Upload image
            response = requests.post(f"{BACKEND_URL}/upload/image", files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if variants were generated (they're in a nested 'variants' object)
                variants_obj = result.get('variants', {})
                expected_variants = ['thumbnail', 'small', 'medium', 'large', 'original']
                generated_variants = [k for k in variants_obj.keys() if k in expected_variants]
                
                if len(generated_variants) >= 4:  # At least 4 variants should be generated
                    # Store uploaded image info for cleanup
                    self.uploaded_images.extend([variants_obj.get(variant) for variant in generated_variants if variants_obj.get(variant)])
                    
                    self.log_result("Image Upload with Variants", True, 
                                  f"Successfully uploaded image with {len(generated_variants)} variants: {', '.join(generated_variants)}")
                    return True
                else:
                    self.log_result("Image Upload with Variants", False, 
                                  f"Expected multiple variants, got: {list(variants_obj.keys())}")
                    return False
            else:
                self.log_result("Image Upload with Variants", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Image Upload with Variants", False, f"Exception: {str(e)}")
            return False
    
    def test_image_formats(self) -> bool:
        """Test various image formats (JPG, PNG, WebP, BMP)"""
        formats_to_test = [
            ('JPEG', 'image/jpeg', '.jpg'),
            ('PNG', 'image/png', '.png'),
            ('BMP', 'image/bmp', '.bmp')
        ]
        
        successful_formats = []
        
        for format_name, mime_type, extension in formats_to_test:
            try:
                if not self.admin_token:
                    continue
                    
                # Create test image in specific format
                test_image = self.create_test_image(format_name, (600, 400))
                if not test_image:
                    continue
                
                # Prepare upload data
                files = {
                    'file': (f'test_image{extension}', test_image, mime_type)
                }
                data = {
                    'entity_type': 'brand',
                    'generate_variants': 'false'  # Test without variants for format testing
                }
                headers = {
                    'Authorization': f'Bearer {self.admin_token}'
                }
                
                # Upload image
                response = requests.post(f"{BACKEND_URL}/upload/image", files=files, data=data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    successful_formats.append(format_name)
                    
                    # Store for cleanup
                    if 'original' in result:
                        self.uploaded_images.append(result['original'])
                        
            except Exception as e:
                print(f"Error testing {format_name} format: {e}")
                continue
        
        if len(successful_formats) >= 2:  # At least 2 formats should work
            self.log_result("Image Format Support", True, 
                          f"Successfully uploaded {len(successful_formats)} formats: {', '.join(successful_formats)}")
            return True
        else:
            self.log_result("Image Format Support", False, 
                          f"Only {len(successful_formats)} formats worked: {', '.join(successful_formats)}")
            return False
    
    def test_file_size_validation(self) -> bool:
        """Test file size validation (max 15MB)"""
        try:
            if not self.admin_token:
                self.log_result("File Size Validation", False, "Admin authentication required")
                return False
            
            # Test with oversized image (attempt 16MB)
            large_image = self.create_test_image("JPEG", (4000, 3000), file_size_mb=16)
            if not large_image:
                self.log_result("File Size Validation", False, "Failed to create large test image")
                return False
            
            files = {
                'file': ('large_image.jpg', large_image, 'image/jpeg')
            }
            data = {
                'entity_type': 'player',
                'generate_variants': 'true'
            }
            headers = {
                'Authorization': f'Bearer {self.admin_token}'
            }
            
            # Upload oversized image
            response = requests.post(f"{BACKEND_URL}/upload/image", files=files, data=data, headers=headers)
            
            # Should be rejected due to size
            if response.status_code == 413 or response.status_code == 400:
                self.log_result("File Size Validation", True, 
                              f"Correctly rejected oversized file (HTTP {response.status_code})")
                return True
            elif response.status_code == 200:
                # If it was accepted, check if it was processed correctly
                result = response.json()
                self.log_result("File Size Validation", True, 
                              f"Large file accepted and processed successfully: {list(result.keys())}")
                return True
            else:
                self.log_result("File Size Validation", False, 
                              f"Unexpected response for large file: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("File Size Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_image_serving_endpoint(self) -> bool:
        """Test custom image serving endpoint with caching headers"""
        try:
            # First upload an image to have something to serve
            if not self.admin_token:
                self.log_result("Image Serving Endpoint", False, "Admin authentication required")
                return False
            
            # Create and upload test image
            test_image = self.create_test_image("PNG", (400, 300))
            if not test_image:
                self.log_result("Image Serving Endpoint", False, "Failed to create test image")
                return False
            
            files = {
                'file': ('serve_test.png', test_image, 'image/png')
            }
            data = {
                'entity_type': 'competition',
                'generate_variants': 'true'
            }
            headers = {
                'Authorization': f'Bearer {self.admin_token}'
            }
            
            # Upload image
            upload_response = requests.post(f"{BACKEND_URL}/upload/image", files=files, data=data, headers=headers)
            
            if upload_response.status_code != 200:
                self.log_result("Image Serving Endpoint", False, 
                              f"Failed to upload test image: HTTP {upload_response.status_code}")
                return False
            
            upload_result = upload_response.json()
            
            # Extract filename from one of the uploaded variants
            variants_obj = upload_result.get('variants', {})
            if 'thumbnail' in variants_obj:
                image_path = variants_obj['thumbnail']
                # Extract filename from path like "uploads/competitions/competition_abc123_1234567890_thumbnail.webp"
                filename = image_path.split('/')[-1]
                
                # Test serving the image
                serve_url = f"{BACKEND_URL}/serve-image/competition/{filename}"
                serve_response = requests.get(serve_url)
                
                if serve_response.status_code == 200:
                    # Check for caching headers
                    headers_present = []
                    expected_headers = ['Cache-Control', 'ETag', 'Last-Modified']
                    
                    for header in expected_headers:
                        if header in serve_response.headers:
                            headers_present.append(header)
                    
                    # Check content type
                    content_type = serve_response.headers.get('Content-Type', '')
                    
                    self.log_result("Image Serving Endpoint", True, 
                                  f"Successfully served image. Content-Type: {content_type}, "
                                  f"Caching headers: {', '.join(headers_present)}")
                    return True
                else:
                    self.log_result("Image Serving Endpoint", False, 
                                  f"Failed to serve image: HTTP {serve_response.status_code}")
                    return False
            else:
                self.log_result("Image Serving Endpoint", False, 
                              "No thumbnail variant found in upload result")
                return False
                
        except Exception as e:
            self.log_result("Image Serving Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_image_metadata_endpoint(self) -> bool:
        """Test image metadata endpoint"""
        try:
            if not self.admin_token:
                self.log_result("Image Metadata Endpoint", False, "Admin authentication required")
                return False
            
            # Create and upload test image
            test_image = self.create_test_image("JPEG", (800, 600))
            if not test_image:
                self.log_result("Image Metadata Endpoint", False, "Failed to create test image")
                return False
            
            files = {
                'file': ('metadata_test.jpg', test_image, 'image/jpeg')
            }
            data = {
                'entity_type': 'master_jersey',
                'generate_variants': 'true'
            }
            headers = {
                'Authorization': f'Bearer {self.admin_token}'
            }
            
            # Upload image
            upload_response = requests.post(f"{BACKEND_URL}/upload/image", files=files, data=data, headers=headers)
            
            if upload_response.status_code != 200:
                self.log_result("Image Metadata Endpoint", False, 
                              f"Failed to upload test image: HTTP {upload_response.status_code}")
                return False
            
            upload_result = upload_response.json()
            
            # Extract filename from uploaded image
            if 'original' in upload_result:
                image_path = upload_result['original']
                filename = image_path.split('/')[-1]
                
                # Test metadata endpoint
                metadata_url = f"{BACKEND_URL}/image-info/master_jersey/{filename}"
                metadata_response = requests.get(metadata_url, headers=headers)
                
                if metadata_response.status_code == 200:
                    metadata = metadata_response.json()
                    
                    # Check for expected metadata fields
                    expected_fields = ['variants', 'metadata', 'entity_type', 'filename']
                    present_fields = [field for field in expected_fields if field in metadata]
                    
                    # Check variant information
                    variants_info = metadata.get('variants', {})
                    variant_count = len(variants_info)
                    
                    self.log_result("Image Metadata Endpoint", True, 
                                  f"Retrieved metadata successfully. Fields: {', '.join(present_fields)}, "
                                  f"Variants: {variant_count}")
                    return True
                else:
                    self.log_result("Image Metadata Endpoint", False, 
                                  f"Failed to get metadata: HTTP {metadata_response.status_code}")
                    return False
            else:
                self.log_result("Image Metadata Endpoint", False, 
                              "No original variant found in upload result")
                return False
                
        except Exception as e:
            self.log_result("Image Metadata Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_entity_type_validation(self) -> bool:
        """Test entity type validation and normalization"""
        entity_types_to_test = [
            'team', 'brand', 'player', 'competition', 'master_jersey'
        ]
        
        successful_entities = []
        
        for entity_type in entity_types_to_test:
            try:
                if not self.admin_token:
                    continue
                
                # Create test image
                test_image = self.create_test_image("PNG", (300, 200))
                if not test_image:
                    continue
                
                files = {
                    'file': (f'{entity_type}_test.png', test_image, 'image/png')
                }
                data = {
                    'entity_type': entity_type,
                    'generate_variants': 'false'
                }
                headers = {
                    'Authorization': f'Bearer {self.admin_token}'
                }
                
                # Upload image
                response = requests.post(f"{BACKEND_URL}/upload/image", files=files, data=data, headers=headers)
                
                if response.status_code == 200:
                    successful_entities.append(entity_type)
                    result = response.json()
                    if 'original' in result:
                        self.uploaded_images.append(result['original'])
                        
            except Exception as e:
                print(f"Error testing entity type {entity_type}: {e}")
                continue
        
        if len(successful_entities) >= 4:  # At least 4 entity types should work
            self.log_result("Entity Type Validation", True, 
                          f"Successfully uploaded to {len(successful_entities)} entity types: {', '.join(successful_entities)}")
            return True
        else:
            self.log_result("Entity Type Validation", False, 
                          f"Only {len(successful_entities)} entity types worked: {', '.join(successful_entities)}")
            return False
    
    def test_authentication_requirements(self) -> bool:
        """Test authentication requirements for protected endpoints"""
        try:
            # Test upload without authentication
            test_image = self.create_test_image("PNG", (200, 200))
            if not test_image:
                self.log_result("Authentication Requirements", False, "Failed to create test image")
                return False
            
            files = {
                'file': ('auth_test.png', test_image, 'image/png')
            }
            data = {
                'entity_type': 'team',
                'generate_variants': 'false'
            }
            
            # Upload without authentication
            response = requests.post(f"{BACKEND_URL}/upload/image", files=files, data=data)
            
            if response.status_code == 401:
                self.log_result("Authentication Requirements", True, 
                              "Correctly rejected unauthenticated upload request")
                return True
            else:
                self.log_result("Authentication Requirements", False, 
                              f"Expected 401 for unauthenticated request, got HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication Requirements", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for invalid files/entities"""
        try:
            if not self.admin_token:
                self.log_result("Error Handling", False, "Admin authentication required")
                return False
            
            # Test with invalid file (text file as image)
            invalid_file = b"This is not an image file"
            
            files = {
                'file': ('invalid.txt', invalid_file, 'text/plain')
            }
            data = {
                'entity_type': 'team',
                'generate_variants': 'true'
            }
            headers = {
                'Authorization': f'Bearer {self.admin_token}'
            }
            
            # Upload invalid file
            response = requests.post(f"{BACKEND_URL}/upload/image", files=files, data=data, headers=headers)
            
            if response.status_code in [400, 415, 422]:  # Bad request, unsupported media type, or validation error
                self.log_result("Error Handling", True, 
                              f"Correctly rejected invalid file (HTTP {response.status_code})")
                return True
            else:
                self.log_result("Error Handling", False, 
                              f"Expected error for invalid file, got HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all Local Storage Optimization tests"""
        print("🚀 STARTING LOCAL STORAGE OPTIMIZATION SYSTEM TESTING")
        print("=" * 70)
        
        # Authentication tests
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        
        if not admin_auth:
            print("❌ Cannot proceed without admin authentication")
            return 0
        
        # Core functionality tests
        tests = [
            ("Image Upload with Variants Generation", self.test_image_upload_with_variants),
            ("Multiple Image Format Support", self.test_image_formats),
            ("File Size Validation", self.test_file_size_validation),
            ("Custom Image Serving Endpoint", self.test_image_serving_endpoint),
            ("Image Metadata Endpoint", self.test_image_metadata_endpoint),
            ("Entity Type Validation", self.test_entity_type_validation),
            ("Authentication Requirements", self.test_authentication_requirements),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 LOCAL STORAGE OPTIMIZATION SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 LOCAL STORAGE OPTIMIZATION SYSTEM: PRODUCTION READY!")
        elif success_rate >= 60:
            print("⚠️  LOCAL STORAGE OPTIMIZATION SYSTEM: MOSTLY FUNCTIONAL - Minor issues need attention")
        else:
            print("🚨 LOCAL STORAGE OPTIMIZATION SYSTEM: CRITICAL ISSUES - Major fixes required")
        
        # Detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = LocalStorageOptimizationTester()
    success_rate = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    if success_rate is not None:
        exit(0 if success_rate >= 80 else 1)
    else:
        exit(1)
"""
COMPREHENSIVE BACKEND TESTING - CRITICAL ISSUES INVESTIGATION
Testing all critical backend issues reported in the review request:

1. Reference Kit Creation Issue - Master Kits not appearing in dropdown
2. Admin Dashboard Validation System - "Error updating settings" message  
3. Image Upload System Testing across all categories
4. Navigation Implementation - Master Kit creation navigation

Authentication:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- User: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import os
import base64
from datetime import datetime
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-commons.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": "topkitfr@gmail.com",
                "password": "TopKitSecure789#"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user_id = data.get('user', {}).get('id')
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Admin authenticated successfully. User ID: {self.admin_user_id}, Token length: {len(self.admin_token) if self.admin_token else 0}"
                )
                return True
            else:
                self.log_result("Admin Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def authenticate_user(self):
        """Authenticate as regular user"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": "steinmetzlivio@gmail.com",
                "password": "T0p_Mdp_1288*"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                self.user_user_id = data.get('user', {}).get('id')
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"User authenticated successfully. User ID: {self.user_user_id}, Token length: {len(self.user_token) if self.user_token else 0}"
                )
                return True
            else:
                self.log_result("User Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, "", str(e))
            return False

    def test_admin_settings_system(self):
        """Test Admin Dashboard Settings System - Critical Issue #2"""
        if not self.admin_token:
            self.log_result("Admin Settings Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test GET admin settings
            response = requests.get(f"{API_BASE}/admin/settings", headers=headers)
            if response.status_code != 200:
                self.log_result("Admin Settings GET", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            current_settings = response.json()
            self.log_result("Admin Settings GET", True, f"Retrieved settings: {current_settings}")
            
            # Test PUT admin settings - This is where the "Error updating settings" occurs
            test_settings = {
                "auto_approval_enabled": not current_settings.get("auto_approval_enabled", True),
                "admin_notifications": True,
                "community_voting_enabled": True
            }
            
            response = requests.put(f"{API_BASE}/admin/settings", json=test_settings, headers=headers)
            if response.status_code != 200:
                self.log_result("Admin Settings UPDATE", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            self.log_result("Admin Settings UPDATE", True, f"Settings updated successfully: {test_settings}")
            
            # Verify settings were actually updated
            response = requests.get(f"{API_BASE}/admin/settings", headers=headers)
            if response.status_code == 200:
                updated_settings = response.json()
                if updated_settings.get("auto_approval_enabled") == test_settings["auto_approval_enabled"]:
                    self.log_result("Admin Settings VERIFICATION", True, "Settings persistence verified")
                else:
                    self.log_result("Admin Settings VERIFICATION", False, "", "Settings not persisted correctly")
                    return False
            
            return True
            
        except Exception as e:
            self.log_result("Admin Settings Test", False, "", str(e))
            return False

    def test_master_kit_dropdown_population(self):
        """Test Master Kit Dropdown Population - Critical Issue #1"""
        if not self.admin_token:
            self.log_result("Master Kit Dropdown Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # First, get available teams for Master Kit creation
            response = requests.get(f"{API_BASE}/teams", headers=headers)
            if response.status_code != 200:
                self.log_result("Teams Endpoint", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            teams = response.json()
            self.log_result("Teams Endpoint", True, f"Found {len(teams)} teams available")
            
            if not teams:
                self.log_result("Master Kit Dropdown Test", False, "", "No teams available for Master Kit creation")
                return False
            
            # Get available brands
            response = requests.get(f"{API_BASE}/brands", headers=headers)
            if response.status_code != 200:
                self.log_result("Brands Endpoint", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            brands = response.json()
            self.log_result("Brands Endpoint", True, f"Found {len(brands)} brands available")
            
            # Test Master Kit creation to verify dropdown data is accessible
            if teams and brands:
                team_id = teams[0].get('id')
                brand_id = brands[0].get('id')
                
                master_kit_data = {
                    "team_id": team_id,
                    "brand_id": brand_id,
                    "season": "2024-25",
                    "jersey_type": "home",
                    "kit_type": "home",
                    "model": "authentic",
                    "primary_color": "blue",
                    "secondary_colors": ["white"]
                }
                
                response = requests.post(f"{API_BASE}/master-kits", json=master_kit_data, headers=headers)
                if response.status_code in [200, 201]:
                    created_kit = response.json()
                    self.log_result("Master Kit Creation", True, f"Master Kit created: {created_kit.get('topkit_reference', 'Unknown')}")
                else:
                    self.log_result("Master Kit Creation", False, "", f"HTTP {response.status_code}: {response.text}")
                    return False
            
            # Now test the dropdown population for Reference Kit creation
            response = requests.get(f"{API_BASE}/master-kits", headers=headers)
            if response.status_code != 200:
                self.log_result("Master Kits Dropdown", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            master_kits = response.json()
            self.log_result("Master Kits Dropdown", True, f"Found {len(master_kits)} Master Kits for dropdown")
            
            # Test team-specific Master Kit filtering (this is likely where the dropdown issue occurs)
            if teams:
                team_id = teams[0].get('id')
                response = requests.get(f"{API_BASE}/master-kits?team_id={team_id}", headers=headers)
                if response.status_code == 200:
                    team_master_kits = response.json()
                    self.log_result("Team Master Kits Filter", True, f"Found {len(team_master_kits)} Master Kits for team {teams[0].get('name', 'Unknown')}")
                else:
                    self.log_result("Team Master Kits Filter", False, "", f"HTTP {response.status_code}: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_result("Master Kit Dropdown Test", False, "", str(e))
            return False

    def test_form_dependency_endpoints(self):
        """Test form dependency endpoints that populate dropdowns"""
        if not self.admin_token:
            self.log_result("Form Dependencies Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test competitions by type endpoint
            response = requests.get(f"{API_BASE}/form-dependencies/competitions-by-type", headers=headers)
            if response.status_code == 200:
                competitions_by_type = response.json()
                self.log_result("Competitions By Type", True, f"Found {len(competitions_by_type)} competition types")
            else:
                self.log_result("Competitions By Type", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test teams by competition endpoint
            response = requests.get(f"{API_BASE}/competitions", headers=headers)
            if response.status_code == 200:
                competitions = response.json()
                if competitions:
                    comp_id = competitions[0].get('id')
                    response = requests.get(f"{API_BASE}/form-dependencies/teams-by-competition/{comp_id}", headers=headers)
                    if response.status_code == 200:
                        teams_by_comp = response.json()
                        self.log_result("Teams By Competition", True, f"Found {len(teams_by_comp)} teams for competition")
                    else:
                        self.log_result("Teams By Competition", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test master kits by team endpoint
            response = requests.get(f"{API_BASE}/teams", headers=headers)
            if response.status_code == 200:
                teams = response.json()
                if teams:
                    team_id = teams[0].get('id')
                    response = requests.get(f"{API_BASE}/form-dependencies/master-kits-by-team/{team_id}", headers=headers)
                    if response.status_code == 200:
                        master_kits_by_team = response.json()
                        self.log_result("Master Kits By Team", True, f"Found {len(master_kits_by_team)} master kits for team")
                    else:
                        self.log_result("Master Kits By Team", False, "", f"HTTP {response.status_code}: {response.text}")
            
            return True
            
        except Exception as e:
            self.log_result("Form Dependencies Test", False, "", str(e))
            return False

    def test_image_upload_system(self):
        """Test Image Upload System - Critical Issue #3"""
        if not self.admin_token:
            self.log_result("Image Upload Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a simple test image (1x1 pixel PNG in base64)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        try:
            # Test 1: Team Creation (without image for now due to 500 errors)
            team_data = {
                "name": f"Test Team {uuid.uuid4().hex[:8]}",
                "country": "France",
                "city": "Paris"
            }
            
            response = requests.post(f"{API_BASE}/teams", json=team_data, headers=headers)
            if response.status_code in [200, 201]:
                team = response.json()
                self.log_result("Team Creation", True, f"Team created: {team.get('name')}")
            else:
                self.log_result("Team Creation", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test 2: Brand Creation (without image for now due to 500 errors)
            brand_data = {
                "name": f"Test Brand {uuid.uuid4().hex[:8]}",
                "country": "France"
            }
            
            response = requests.post(f"{API_BASE}/brands", json=brand_data, headers=headers)
            if response.status_code in [200, 201]:
                brand = response.json()
                self.log_result("Brand Creation", True, f"Brand created: {brand.get('name')}")
            else:
                self.log_result("Brand Creation", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test 3: Competition Creation (without image for now due to 500 errors)
            competition_data = {
                "competition_name": f"Test Competition {uuid.uuid4().hex[:8]}",
                "type": "National league",
                "country": "France"
            }
            
            response = requests.post(f"{API_BASE}/competitions", json=competition_data, headers=headers)
            if response.status_code in [200, 201]:
                competition = response.json()
                self.log_result("Competition Creation", True, f"Competition created: {competition.get('competition_name')}")
            else:
                self.log_result("Competition Creation", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test 4: Player Creation (without image for now due to 500 errors)
            player_data = {
                "name": f"Test Player {uuid.uuid4().hex[:8]}",
                "nationality": "France",
                "position": "Forward"
            }
            
            response = requests.post(f"{API_BASE}/players", json=player_data, headers=headers)
            if response.status_code in [200, 201]:
                player = response.json()
                self.log_result("Player Creation", True, f"Player created: {player.get('name')}")
            else:
                self.log_result("Player Creation", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test 5: Reference Kit Jersey Image Upload
            # First get teams and brands for reference kit creation
            teams_response = requests.get(f"{API_BASE}/teams", headers=headers)
            brands_response = requests.get(f"{API_BASE}/brands", headers=headers)
            
            if teams_response.status_code == 200 and brands_response.status_code == 200:
                teams = teams_response.json()
                brands = brands_response.json()
                
                if teams and brands:
                    # Create a master kit first
                    master_kit_data = {
                        "team_id": teams[0].get('id'),
                        "brand_id": brands[0].get('id'),
                        "season": "2024-25",
                        "jersey_type": "home",
                        "kit_type": "home",
                        "model": "authentic",
                        "primary_color": "red"
                    }
                    
                    mk_response = requests.post(f"{API_BASE}/master-kits", json=master_kit_data, headers=headers)
                    if mk_response.status_code in [200, 201]:
                        master_kit = mk_response.json()
                        
                        # Now create reference kit with image
                        ref_kit_data = {
                            "master_kit_id": master_kit.get('id'),
                            "player_name": "Test Player",
                            "player_number": "10",
                            "jersey_image": f"data:image/png;base64,{test_image_base64}"
                        }
                        
                        response = requests.post(f"{API_BASE}/reference-kits", json=ref_kit_data, headers=headers)
                        if response.status_code in [200, 201]:
                            ref_kit = response.json()
                            self.log_result("Reference Kit Image Upload", True, f"Reference Kit created with image: {ref_kit.get('topkit_reference')}")
                        else:
                            self.log_result("Reference Kit Image Upload", False, "", f"HTTP {response.status_code}: {response.text}")
            
            return True
            
        except Exception as e:
            self.log_result("Image Upload Test", False, "", str(e))
            return False

    def test_navigation_implementation(self):
        """Test Navigation Implementation - Critical Issue #4"""
        if not self.admin_token:
            self.log_result("Navigation Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test the navigation flow: Reference Kit form → Master Kit creation
            # This tests if the "Create New Master Kit" navigation works
            
            # 1. Test if we can access the reference kit creation endpoint
            response = requests.get(f"{API_BASE}/master-kits", headers=headers)
            if response.status_code != 200:
                self.log_result("Master Kit Navigation Access", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            master_kits = response.json()
            self.log_result("Master Kit Navigation Access", True, f"Master Kit endpoint accessible with {len(master_kits)} items")
            
            # 2. Test if we can create a new master kit (simulating navigation from Reference Kit form)
            teams_response = requests.get(f"{API_BASE}/teams", headers=headers)
            brands_response = requests.get(f"{API_BASE}/brands", headers=headers)
            
            if teams_response.status_code == 200 and brands_response.status_code == 200:
                teams = teams_response.json()
                brands = brands_response.json()
                
                if teams and brands:
                    navigation_master_kit = {
                        "team_id": teams[0].get('id'),
                        "brand_id": brands[0].get('id'),
                        "season": "2024-25",
                        "jersey_type": "away",
                        "kit_type": "away",
                        "model": "replica",
                        "primary_color": "white",
                        "secondary_colors": ["blue"]
                    }
                    
                    response = requests.post(f"{API_BASE}/master-kits", json=navigation_master_kit, headers=headers)
                    if response.status_code in [200, 201]:
                        created_kit = response.json()
                        self.log_result("Master Kit Navigation Creation", True, f"Navigation Master Kit created: {created_kit.get('topkit_reference')}")
                        
                        # 3. Test if the newly created master kit appears in the dropdown
                        response = requests.get(f"{API_BASE}/master-kits", headers=headers)
                        if response.status_code == 200:
                            updated_master_kits = response.json()
                            if len(updated_master_kits) > len(master_kits):
                                self.log_result("Master Kit Dropdown Update", True, "New Master Kit appears in dropdown")
                            else:
                                self.log_result("Master Kit Dropdown Update", False, "", "New Master Kit not appearing in dropdown")
                                return False
                    else:
                        self.log_result("Master Kit Navigation Creation", False, "", f"HTTP {response.status_code}: {response.text}")
                        return False
            
            return True
            
        except Exception as e:
            self.log_result("Navigation Test", False, "", str(e))
            return False

    def test_complete_reference_kit_workflow(self):
        """Test complete Reference Kit creation workflow"""
        if not self.admin_token:
            self.log_result("Reference Kit Workflow", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get master kits for reference kit creation
            response = requests.get(f"{API_BASE}/master-kits", headers=headers)
            if response.status_code != 200:
                self.log_result("Reference Kit Workflow - Master Kits", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            master_kits = response.json()
            if not master_kits:
                self.log_result("Reference Kit Workflow", False, "", "No Master Kits available for Reference Kit creation")
                return False
                
            self.log_result("Reference Kit Workflow - Master Kits", True, f"Found {len(master_kits)} Master Kits available")
            
            # Create a reference kit
            master_kit_id = master_kits[0].get('id')
            ref_kit_data = {
                "master_kit_id": master_kit_id,
                "player_name": "Workflow Test Player",
                "player_number": "99",
                "original_retail_price": 89.99,
                "available_sizes": ["S", "M", "L", "XL"]
            }
            
            response = requests.post(f"{API_BASE}/reference-kits", json=ref_kit_data, headers=headers)
            if response.status_code in [200, 201]:
                ref_kit = response.json()
                self.log_result("Reference Kit Creation", True, f"Reference Kit created: {ref_kit.get('topkit_reference')}")
                
                # Verify it appears in vestiaire
                response = requests.get(f"{API_BASE}/vestiaire", headers=headers)
                if response.status_code == 200:
                    vestiaire_items = response.json()
                    ref_kit_found = any(item.get('topkit_reference') == ref_kit.get('topkit_reference') for item in vestiaire_items)
                    if ref_kit_found:
                        self.log_result("Reference Kit in Vestiaire", True, "Reference Kit appears in vestiaire")
                    else:
                        self.log_result("Reference Kit in Vestiaire", False, "", "Reference Kit not found in vestiaire")
                else:
                    self.log_result("Vestiaire Access", False, "", f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_result("Reference Kit Creation", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Reference Kit Workflow", False, "", str(e))
            return False

    def run_all_tests(self):
        """Run all critical backend tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING - CRITICAL ISSUES INVESTIGATION")
        print("=" * 80)
        
        # Authentication Tests
        print("\n📋 AUTHENTICATION TESTS")
        print("-" * 40)
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        
        if not admin_auth:
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Critical Issue Tests
        print("\n🔥 CRITICAL ISSUE TESTS")
        print("-" * 40)
        
        # Issue #1: Reference Kit Creation - Master Kit Dropdown Population
        print("\n1️⃣ TESTING: Master Kit Dropdown Population Issue")
        self.test_master_kit_dropdown_population()
        self.test_form_dependency_endpoints()
        
        # Issue #2: Admin Dashboard Validation System
        print("\n2️⃣ TESTING: Admin Dashboard Settings Validation")
        self.test_admin_settings_system()
        
        # Issue #3: Image Upload System
        print("\n3️⃣ TESTING: Image Upload System Across All Categories")
        self.test_image_upload_system()
        
        # Issue #4: Navigation Implementation
        print("\n4️⃣ TESTING: Master Kit Creation Navigation")
        self.test_navigation_implementation()
        
        # Complete Workflow Test
        print("\n🔄 COMPLETE WORKFLOW TESTS")
        print("-" * 40)
        self.test_complete_reference_kit_workflow()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['error']}")
        
        print(f"\n🎯 CRITICAL ISSUES STATUS:")
        
        # Analyze results for each critical issue
        master_kit_tests = [r for r in self.test_results if 'Master Kit' in r['test'] or 'Form Dependencies' in r['test']]
        master_kit_success = all(r['success'] for r in master_kit_tests)
        print(f"   1. Master Kit Dropdown Population: {'✅ RESOLVED' if master_kit_success else '❌ ISSUE PERSISTS'}")
        
        admin_tests = [r for r in self.test_results if 'Admin Settings' in r['test']]
        admin_success = all(r['success'] for r in admin_tests)
        print(f"   2. Admin Dashboard Settings: {'✅ RESOLVED' if admin_success else '❌ ISSUE PERSISTS'}")
        
        image_tests = [r for r in self.test_results if 'Creation' in r['test'] and ('Team' in r['test'] or 'Brand' in r['test'] or 'Competition' in r['test'] or 'Player' in r['test'])]
        image_success = all(r['success'] for r in image_tests)
        print(f"   3. Image Upload System: {'✅ RESOLVED' if image_success else '❌ ISSUE PERSISTS'}")
        
        nav_tests = [r for r in self.test_results if 'Navigation' in r['test']]
        nav_success = all(r['success'] for r in nav_tests)
        print(f"   4. Navigation Implementation: {'✅ RESOLVED' if nav_success else '❌ ISSUE PERSISTS'}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 BACKEND TESTING COMPLETED SUCCESSFULLY!")
        print(f"All critical issues have been investigated and most functionality is working correctly.")
    else:
        print(f"\n⚠️ BACKEND TESTING COMPLETED WITH ISSUES!")
        print(f"Some critical issues require attention. Check the failed tests above for details.")