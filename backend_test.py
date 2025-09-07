#!/usr/bin/env python3
"""
Complete Image System Integration Backend Testing
Testing the enhanced image upload, optimization, and serving system
"""

import requests
import json
import os
import sys
from pathlib import Path
import time
import io
from PIL import Image
import tempfile

# Configuration
BACKEND_URL = "https://football-collab.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImageSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        
    def authenticate(self):
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating admin user...")
            
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token') or data.get('token')
                self.user_data = data.get('user')
                
                if not self.auth_token:
                    print(f"❌ No token in response: {data}")
                    return False
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                print(f"✅ Authentication successful - User: {self.user_data.get('name') if self.user_data else 'Unknown'}")
                print(f"   Token length: {len(self.auth_token)} characters")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def create_test_image(self, width=800, height=600, format='JPEG'):
        """Create a test image for upload testing"""
        try:
            # Create a simple test image
            image = Image.new('RGB', (width, height), color='red')
            
            # Add some content to make it realistic
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(image)
            
            # Draw some shapes and text
            draw.rectangle([50, 50, width-50, height-50], outline='blue', width=5)
            draw.ellipse([100, 100, width-100, height-100], fill='green')
            
            try:
                # Try to add text (may fail if no font available)
                draw.text((width//2-50, height//2), "TEST IMAGE", fill='white')
            except:
                pass  # Font not available, skip text
            
            # Save to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format=format, quality=90)
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"❌ Error creating test image: {e}")
            return None
    
    def test_image_upload_endpoint(self):
        """Test the /api/upload/image endpoint"""
        print("\n📤 Testing Image Upload Endpoint...")
        
        try:
            # Test different entity types
            entity_types = ['team', 'brand', 'player', 'competition', 'master_jersey']
            results = {}
            
            for entity_type in entity_types:
                print(f"\n  Testing {entity_type} image upload...")
                
                # Create test image
                image_data = self.create_test_image()
                if not image_data:
                    results[entity_type] = {'success': False, 'error': 'Failed to create test image'}
                    continue
                
                # Prepare multipart form data
                files = {
                    'file': ('test_image.jpg', image_data, 'image/jpeg')
                }
                data = {
                    'entity_type': entity_type,
                    'generate_variants': 'true'
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/upload/image",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    results[entity_type] = {
                        'success': True,
                        'image_url': result_data.get('image_url'),
                        'variants_count': result_data.get('variants_count', 0),
                        'optimization_applied': result_data.get('optimization_applied', False),
                        'metadata': result_data.get('metadata', {})
                    }
                    print(f"    ✅ {entity_type}: Upload successful")
                    print(f"       Variants: {result_data.get('variants_count', 0)}")
                    print(f"       Optimized: {result_data.get('optimization_applied', False)}")
                else:
                    results[entity_type] = {
                        'success': False,
                        'status_code': response.status_code,
                        'error': response.text
                    }
                    print(f"    ❌ {entity_type}: Upload failed ({response.status_code})")
            
            # Summary
            successful_uploads = sum(1 for r in results.values() if r.get('success'))
            print(f"\n  📊 Upload Results: {successful_uploads}/{len(entity_types)} successful")
            
            return results
            
        except Exception as e:
            print(f"❌ Image upload test error: {e}")
            return {}
    
    def test_image_serving_endpoint(self, upload_results):
        """Test the /api/serve-image/{entity_type}/{filename} endpoint"""
        print("\n🖼️  Testing Image Serving Endpoint...")
        
        try:
            serving_results = {}
            
            for entity_type, upload_data in upload_results.items():
                if not upload_data.get('success'):
                    continue
                
                print(f"\n  Testing {entity_type} image serving...")
                
                # Extract filename from image_url
                image_url = upload_data.get('image_url', '')
                if not image_url:
                    continue
                
                # Extract filename (assuming format: uploads/teams/filename.jpg)
                filename = image_url.split('/')[-1] if '/' in image_url else image_url
                
                # Test different size variants
                sizes = ['thumbnail', 'small', 'medium', 'large', 'original']
                size_results = {}
                
                for size in sizes:
                    serve_url = f"{BACKEND_URL}/serve-image/{entity_type}/{filename}?size={size}"
                    
                    response = self.session.get(serve_url)
                    
                    if response.status_code == 200:
                        size_results[size] = {
                            'success': True,
                            'content_type': response.headers.get('content-type'),
                            'content_length': len(response.content),
                            'cache_control': response.headers.get('cache-control'),
                            'etag': response.headers.get('etag')
                        }
                        print(f"    ✅ {size}: {len(response.content)} bytes")
                    else:
                        size_results[size] = {
                            'success': False,
                            'status_code': response.status_code,
                            'error': response.text[:100]
                        }
                        print(f"    ❌ {size}: Failed ({response.status_code})")
                
                serving_results[entity_type] = {
                    'filename': filename,
                    'sizes': size_results,
                    'successful_sizes': sum(1 for r in size_results.values() if r.get('success'))
                }
            
            # Summary
            total_tests = sum(len(r.get('sizes', {})) for r in serving_results.values())
            successful_tests = sum(r.get('successful_sizes', 0) for r in serving_results.values())
            print(f"\n  📊 Serving Results: {successful_tests}/{total_tests} size variants successful")
            
            return serving_results
            
        except Exception as e:
            print(f"❌ Image serving test error: {e}")
            return {}
    
    def test_image_info_endpoint(self, upload_results):
        """Test the /api/image-info/{entity_type}/{filename} endpoint"""
        print("\n📋 Testing Image Info Endpoint...")
        
        try:
            info_results = {}
            
            for entity_type, upload_data in upload_results.items():
                if not upload_data.get('success'):
                    continue
                
                print(f"\n  Testing {entity_type} image info...")
                
                # Extract filename from image_url
                image_url = upload_data.get('image_url', '')
                if not image_url:
                    continue
                
                filename = image_url.split('/')[-1] if '/' in image_url else image_url
                
                response = self.session.get(f"{BACKEND_URL}/image-info/{entity_type}/{filename}")
                
                if response.status_code == 200:
                    info_data = response.json()
                    info_results[entity_type] = {
                        'success': True,
                        'filename': info_data.get('filename'),
                        'entity_type': info_data.get('entity_type'),
                        'variant_count': info_data.get('variant_count', 0),
                        'total_size': info_data.get('total_size', 0),
                        'variants': info_data.get('variants', {})
                    }
                    print(f"    ✅ {entity_type}: {info_data.get('variant_count', 0)} variants")
                    print(f"       Total size: {info_data.get('total_size', 0)} bytes")
                else:
                    info_results[entity_type] = {
                        'success': False,
                        'status_code': response.status_code,
                        'error': response.text
                    }
                    print(f"    ❌ {entity_type}: Failed ({response.status_code})")
            
            # Summary
            successful_info = sum(1 for r in info_results.values() if r.get('success'))
            print(f"\n  📊 Info Results: {successful_info}/{len(info_results)} successful")
            
            return info_results
            
        except Exception as e:
            print(f"❌ Image info test error: {e}")
            return {}
    
    def test_image_optimization_features(self):
        """Test image optimization features (WebP conversion, compression)"""
        print("\n⚡ Testing Image Optimization Features...")
        
        try:
            # Create a large test image to test compression
            large_image_data = self.create_test_image(width=2000, height=1500, format='PNG')
            if not large_image_data:
                print("❌ Failed to create large test image")
                return {}
            
            print(f"  Original image size: {len(large_image_data)} bytes")
            
            # Upload with optimization
            files = {
                'file': ('large_test.png', large_image_data, 'image/png')
            }
            data = {
                'entity_type': 'team',
                'generate_variants': 'true'
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/upload/image",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Get image info to check optimization
                filename = result_data.get('image_url', '').split('/')[-1]
                if filename:
                    info_response = self.session.get(f"{BACKEND_URL}/image-info/team/{filename}")
                    
                    if info_response.status_code == 200:
                        info_data = info_response.json()
                        variants = info_data.get('variants', {})
                        
                        optimization_results = {
                            'original_size': len(large_image_data),
                            'variants_generated': len(variants),
                            'compression_ratios': {}
                        }
                        
                        for size_name, variant_info in variants.items():
                            if variant_info.get('exists'):
                                compressed_size = variant_info.get('file_size', 0)
                                ratio = (len(large_image_data) - compressed_size) / len(large_image_data) * 100
                                optimization_results['compression_ratios'][size_name] = {
                                    'compressed_size': compressed_size,
                                    'compression_ratio': round(ratio, 2)
                                }
                                print(f"    ✅ {size_name}: {compressed_size} bytes ({ratio:.1f}% compression)")
                        
                        return optimization_results
                    else:
                        print(f"❌ Failed to get image info: {info_response.status_code}")
                else:
                    print("❌ No filename in upload response")
            else:
                print(f"❌ Optimization test upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
            
            return {}
            
        except Exception as e:
            print(f"❌ Optimization test error: {e}")
            return {}
    
    def test_caching_headers(self, upload_results):
        """Test proper caching headers in image serving"""
        print("\n🗄️  Testing Caching Headers...")
        
        try:
            caching_results = {}
            
            for entity_type, upload_data in upload_results.items():
                if not upload_data.get('success'):
                    continue
                
                image_url = upload_data.get('image_url', '')
                if not image_url:
                    continue
                
                filename = image_url.split('/')[-1]
                serve_url = f"{BACKEND_URL}/serve-image/{entity_type}/{filename}"
                
                response = self.session.get(serve_url)
                
                if response.status_code == 200:
                    headers = response.headers
                    caching_results[entity_type] = {
                        'success': True,
                        'cache_control': headers.get('cache-control'),
                        'etag': headers.get('etag'),
                        'last_modified': headers.get('last-modified'),
                        'content_type': headers.get('content-type')
                    }
                    
                    # Check for proper caching headers
                    has_cache_control = 'cache-control' in headers
                    has_etag = 'etag' in headers
                    has_last_modified = 'last-modified' in headers
                    
                    print(f"    ✅ {entity_type}:")
                    print(f"       Cache-Control: {'✓' if has_cache_control else '✗'} {headers.get('cache-control', 'Missing')}")
                    print(f"       ETag: {'✓' if has_etag else '✗'} {headers.get('etag', 'Missing')}")
                    print(f"       Last-Modified: {'✓' if has_last_modified else '✗'} {headers.get('last-modified', 'Missing')}")
                else:
                    caching_results[entity_type] = {
                        'success': False,
                        'status_code': response.status_code
                    }
                    print(f"    ❌ {entity_type}: Failed to test caching ({response.status_code})")
            
            return caching_results
            
        except Exception as e:
            print(f"❌ Caching test error: {e}")
            return {}
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n🚫 Testing Error Handling...")
        
        try:
            error_tests = {}
            
            # Test 1: Invalid entity type
            print("  Testing invalid entity type...")
            files = {'file': ('test.jpg', self.create_test_image(), 'image/jpeg')}
            data = {'entity_type': 'invalid_type', 'generate_variants': 'true'}
            
            response = self.session.post(f"{BACKEND_URL}/upload/image", files=files, data=data)
            error_tests['invalid_entity_type'] = {
                'expected_status': 400,
                'actual_status': response.status_code,
                'success': response.status_code == 400
            }
            print(f"    {'✅' if response.status_code == 400 else '❌'} Invalid entity type: {response.status_code}")
            
            # Test 2: Invalid file type
            print("  Testing invalid file type...")
            files = {'file': ('test.txt', b'This is not an image', 'text/plain')}
            data = {'entity_type': 'team', 'generate_variants': 'true'}
            
            response = self.session.post(f"{BACKEND_URL}/upload/image", files=files, data=data)
            error_tests['invalid_file_type'] = {
                'expected_status': 400,
                'actual_status': response.status_code,
                'success': response.status_code == 400
            }
            print(f"    {'✅' if response.status_code == 400 else '❌'} Invalid file type: {response.status_code}")
            
            # Test 3: Missing authentication
            print("  Testing missing authentication...")
            temp_session = requests.Session()  # No auth headers
            files = {'file': ('test.jpg', self.create_test_image(), 'image/jpeg')}
            data = {'entity_type': 'team', 'generate_variants': 'true'}
            
            response = temp_session.post(f"{BACKEND_URL}/upload/image", files=files, data=data)
            error_tests['missing_auth'] = {
                'expected_status': 401,
                'actual_status': response.status_code,
                'success': response.status_code == 401
            }
            print(f"    {'✅' if response.status_code == 401 else '❌'} Missing auth: {response.status_code}")
            
            # Test 4: Non-existent image serving
            print("  Testing non-existent image...")
            response = self.session.get(f"{BACKEND_URL}/serve-image/team/nonexistent.jpg")
            error_tests['nonexistent_image'] = {
                'expected_status': 404,
                'actual_status': response.status_code,
                'success': response.status_code == 404
            }
            print(f"    {'✅' if response.status_code == 404 else '❌'} Non-existent image: {response.status_code}")
            
            # Summary
            successful_error_tests = sum(1 for t in error_tests.values() if t.get('success'))
            print(f"\n  📊 Error Handling: {successful_error_tests}/{len(error_tests)} tests passed")
            
            return error_tests
            
        except Exception as e:
            print(f"❌ Error handling test error: {e}")
            return {}
    
    def run_comprehensive_test(self):
        """Run all image system integration tests"""
        print("🎯 COMPLETE IMAGE SYSTEM INTEGRATION TESTING")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Test image upload endpoint
        upload_results = self.test_image_upload_endpoint()
        
        # Step 3: Test image serving endpoint
        serving_results = self.test_image_serving_endpoint(upload_results)
        
        # Step 4: Test image info endpoint
        info_results = self.test_image_info_endpoint(upload_results)
        
        # Step 5: Test optimization features
        optimization_results = self.test_image_optimization_features()
        
        # Step 6: Test caching headers
        caching_results = self.test_caching_headers(upload_results)
        
        # Step 7: Test error handling
        error_results = self.test_error_handling()
        
        # Final Summary
        print("\n" + "=" * 60)
        print("📊 COMPLETE IMAGE SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        # Upload summary
        successful_uploads = sum(1 for r in upload_results.values() if r.get('success'))
        print(f"📤 Image Upload: {successful_uploads}/5 entity types successful")
        
        # Serving summary
        total_serving_tests = sum(len(r.get('sizes', {})) for r in serving_results.values())
        successful_serving = sum(r.get('successful_sizes', 0) for r in serving_results.values())
        print(f"🖼️  Image Serving: {successful_serving}/{total_serving_tests} size variants successful")
        
        # Info summary
        successful_info = sum(1 for r in info_results.values() if r.get('success'))
        print(f"📋 Image Info: {successful_info}/{len(info_results)} successful")
        
        # Optimization summary
        if optimization_results:
            variants_count = optimization_results.get('variants_generated', 0)
            print(f"⚡ Optimization: {variants_count} variants generated with compression")
        
        # Caching summary
        successful_caching = sum(1 for r in caching_results.values() if r.get('success'))
        print(f"🗄️  Caching Headers: {successful_caching}/{len(caching_results)} successful")
        
        # Error handling summary
        successful_errors = sum(1 for t in error_results.values() if t.get('success'))
        print(f"🚫 Error Handling: {successful_errors}/{len(error_results)} tests passed")
        
        # Overall assessment
        total_tests = (
            len(upload_results) + 
            total_serving_tests + 
            len(info_results) + 
            len(caching_results) + 
            len(error_results)
        )
        
        successful_tests = (
            successful_uploads + 
            successful_serving + 
            successful_info + 
            successful_caching + 
            successful_errors
        )
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Image system is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD: Image system is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️  FAIR: Image system has significant issues requiring attention")
        else:
            print("❌ POOR: Image system has critical issues requiring immediate fixes")
        
        return success_rate >= 75

def main():
    """Main test execution"""
    tester = ImageSystemTester()
    
    try:
        success = tester.run_comprehensive_test()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()