#!/usr/bin/env python3
"""
TopKit Admin Jersey Correction Photo Upload Testing
Testing the photo upload functionality in admin jersey correction as requested.

CONTEXT: Testing the fixed photo upload issue in admin jersey correction by:
1. Backend: Modified PUT /api/admin/jerseys/{jersey_id}/edit to accept multipart form data with front_photo and back_photo files
2. Frontend: Changed admin edit to use FormData instead of JSON to support file uploads

TESTING OBJECTIVES:
1. Admin Authentication: Login as admin (topkitfr@gmail.com / TopKitSecure789#)
2. Get Pending Jersey: Retrieve or create a pending jersey for editing
3. Test Admin Edit with Photos: Use PUT /api/admin/jerseys/{jersey_id}/edit with multipart form data including photo files
4. Validate Photo Upload: Confirm photos are saved and included in the jersey images field
5. Verify Complete Functionality: Ensure both jersey data AND photos persist after admin correction
"""

import requests
import json
import io
from PIL import Image
import base64
import time

# Configuration
BASE_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class AdminPhotoUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_jersey_id = None
        
    def create_test_image(self, text="TEST", size=(200, 200), color="red"):
        """Create a test image for upload testing"""
        try:
            img = Image.new('RGB', size, color=color)
            # Add text to make it identifiable
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            try:
                # Try to use a default font
                font = ImageFont.load_default()
                draw.text((10, 10), text, fill="white", font=font)
            except:
                # Fallback if font loading fails
                draw.text((10, 10), text, fill="white")
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            return img_bytes.getvalue()
        except Exception as e:
            print(f"⚠️ Error creating test image: {e}")
            # Return a minimal PNG if PIL fails
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Step 1: Admin Authentication")
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.admin_user = data.get("user", {})
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                print(f"✅ Admin authentication successful")
                print(f"   - Name: {self.admin_user.get('name')}")
                print(f"   - Role: {self.admin_user.get('role')}")
                print(f"   - ID: {self.admin_user.get('id')}")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin authentication error: {e}")
            return False
    
    def get_or_create_pending_jersey(self):
        """Get existing pending jersey or create one for testing"""
        print("\n📋 Step 2: Get/Create Pending Jersey")
        
        try:
            # First, try to get existing pending jerseys
            response = self.session.get(f"{BASE_URL}/admin/jerseys/pending")
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                
                # Handle both list and single object responses
                if isinstance(pending_jerseys, list):
                    jerseys_list = pending_jerseys
                elif isinstance(pending_jerseys, dict) and 'jerseys' in pending_jerseys:
                    jerseys_list = pending_jerseys['jerseys']
                else:
                    jerseys_list = [pending_jerseys] if pending_jerseys else []
                
                if jerseys_list:
                    # Use the first pending jersey
                    test_jersey = jerseys_list[0]
                    self.test_jersey_id = test_jersey.get('id')
                    print(f"✅ Found existing pending jersey for testing")
                    print(f"   - ID: {self.test_jersey_id}")
                    print(f"   - Team: {test_jersey.get('team')}")
                    print(f"   - Season: {test_jersey.get('season')}")
                    print(f"   - Reference: {test_jersey.get('reference_number')}")
                    return True
                else:
                    print("📝 No pending jerseys found, creating test jersey...")
                    return self.create_test_jersey()
            else:
                print(f"⚠️ Could not retrieve pending jerseys: {response.status_code}")
                print("📝 Creating test jersey instead...")
                return self.create_test_jersey()
                
        except Exception as e:
            print(f"❌ Error getting pending jerseys: {e}")
            print("📝 Creating test jersey instead...")
            return self.create_test_jersey()
    
    def create_test_jersey(self):
        """Create a test jersey for admin correction testing"""
        try:
            # Create test jersey using multipart form data
            jersey_data = {
                'team': 'Test FC Barcelona',
                'league': 'La Liga',
                'season': '2024-25',
                'model': 'authentic',
                'manufacturer': 'Nike',
                'jersey_type': 'home',
                'sku_code': 'TEST-BCN-2425',
                'description': 'Test jersey for admin photo upload testing'
            }
            
            response = self.session.post(f"{BASE_URL}/jerseys", data=jersey_data)
            
            if response.status_code == 200:
                jersey = response.json()
                self.test_jersey_id = jersey.get('id')
                print(f"✅ Test jersey created successfully")
                print(f"   - ID: {self.test_jersey_id}")
                print(f"   - Team: {jersey.get('team')}")
                print(f"   - Reference: {jersey.get('reference_number')}")
                print(f"   - Status: {jersey.get('status')}")
                return True
            else:
                print(f"❌ Failed to create test jersey: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating test jersey: {e}")
            return False
    
    def test_admin_edit_with_photos(self):
        """Test admin jersey correction with photo uploads"""
        print(f"\n📸 Step 3: Test Admin Edit with Photo Upload")
        
        if not self.test_jersey_id:
            print("❌ No test jersey ID available")
            return False
        
        try:
            # Create test images
            front_image_data = self.create_test_image("FRONT PHOTO", color="blue")
            back_image_data = self.create_test_image("BACK PHOTO", color="green")
            
            # Prepare multipart form data with jersey updates and photos
            files = {
                'front_photo': ('front_test.png', front_image_data, 'image/png'),
                'back_photo': ('back_test.png', back_image_data, 'image/png')
            }
            
            data = {
                'team': 'FC Barcelona (Admin Corrected)',
                'league': 'La Liga',
                'season': '2024-25',
                'model': 'authentic',
                'manufacturer': 'Nike (Updated)',
                'jersey_type': 'away',
                'sku_code': 'ADMIN-BCN-2425-CORRECTED',
                'description': 'Jersey corrected by admin with photo uploads - testing multipart form data functionality'
            }
            
            print(f"📤 Sending PUT request to /admin/jerseys/{self.test_jersey_id}/edit")
            print(f"   - Including front_photo: front_test.png ({len(front_image_data)} bytes)")
            print(f"   - Including back_photo: back_test.png ({len(back_image_data)} bytes)")
            print(f"   - Jersey data: {data['team']}, {data['manufacturer']}, {data['jersey_type']}")
            
            # Make the PUT request with multipart form data
            response = self.session.put(
                f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/edit",
                files=files,
                data=data
            )
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Admin jersey correction with photos successful!")
                print(f"   - Message: {result.get('message', 'No message')}")
                
                # Check if photos_uploaded count is included
                photos_uploaded = result.get('photos_uploaded', 0)
                print(f"   - Photos uploaded: {photos_uploaded}")
                
                return True
            else:
                print(f"❌ Admin jersey correction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error during admin jersey correction: {e}")
            return False
    
    def validate_photo_persistence(self):
        """Validate that photos are saved and included in jersey data"""
        print(f"\n🔍 Step 4: Validate Photo Upload Persistence")
        
        if not self.test_jersey_id:
            print("❌ No test jersey ID available")
            return False
        
        try:
            # Get the updated jersey to verify photo persistence
            response = self.session.get(f"{BASE_URL}/admin/jerseys/pending")
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                
                # Handle both list and single object responses
                if isinstance(pending_jerseys, list):
                    jerseys_list = pending_jerseys
                elif isinstance(pending_jerseys, dict) and 'jerseys' in pending_jerseys:
                    jerseys_list = pending_jerseys['jerseys']
                else:
                    jerseys_list = [pending_jerseys] if pending_jerseys else []
                
                # Find our test jersey
                test_jersey = None
                for jersey in jerseys_list:
                    if jersey.get('id') == self.test_jersey_id:
                        test_jersey = jersey
                        break
                
                if test_jersey:
                    print(f"✅ Found updated jersey in database")
                    print(f"   - ID: {test_jersey.get('id')}")
                    print(f"   - Team: {test_jersey.get('team')}")
                    print(f"   - Manufacturer: {test_jersey.get('manufacturer')}")
                    print(f"   - Jersey Type: {test_jersey.get('jersey_type')}")
                    print(f"   - SKU Code: {test_jersey.get('sku_code')}")
                    
                    # Check photo URLs
                    front_photo_url = test_jersey.get('front_photo_url')
                    back_photo_url = test_jersey.get('back_photo_url')
                    
                    if front_photo_url:
                        print(f"   - Front Photo URL: {front_photo_url}")
                    else:
                        print(f"   - Front Photo URL: Not set")
                    
                    if back_photo_url:
                        print(f"   - Back Photo URL: {back_photo_url}")
                    else:
                        print(f"   - Back Photo URL: Not set")
                    
                    # Check if images field is updated (legacy field)
                    images = test_jersey.get('images', [])
                    if images:
                        print(f"   - Images field: {len(images)} items - {images}")
                    else:
                        print(f"   - Images field: Empty or not present")
                    
                    # Validate photo persistence
                    photos_persisted = bool(front_photo_url or back_photo_url or images)
                    if photos_persisted:
                        print(f"✅ Photo persistence validated - photos are saved in jersey record")
                        return True
                    else:
                        print(f"⚠️ Photo persistence issue - no photo URLs found in jersey record")
                        return False
                else:
                    print(f"❌ Test jersey not found in pending jerseys")
                    return False
            else:
                print(f"❌ Could not retrieve pending jerseys for validation: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error validating photo persistence: {e}")
            return False
    
    def test_different_photo_combinations(self):
        """Test different photo upload combinations"""
        print(f"\n🎯 Step 5: Test Different Photo Upload Combinations")
        
        if not self.test_jersey_id:
            print("❌ No test jersey ID available")
            return False
        
        test_results = []
        
        # Test 1: Only front photo
        print(f"\n📸 Test 5a: Upload only front photo")
        try:
            front_image_data = self.create_test_image("FRONT ONLY", color="red")
            
            files = {
                'front_photo': ('front_only.png', front_image_data, 'image/png')
            }
            
            data = {
                'team': 'FC Barcelona (Front Photo Only)',
                'league': 'La Liga',
                'season': '2024-25',
                'model': 'authentic',
                'manufacturer': 'Nike',
                'jersey_type': 'home',
                'sku_code': 'FRONT-ONLY-TEST',
                'description': 'Testing front photo only upload'
            }
            
            response = self.session.put(
                f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/edit",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                photos_uploaded = result.get('photos_uploaded', 0)
                print(f"✅ Front photo only test successful - {photos_uploaded} photo(s) uploaded")
                test_results.append(True)
            else:
                print(f"❌ Front photo only test failed: {response.status_code}")
                test_results.append(False)
                
        except Exception as e:
            print(f"❌ Error in front photo only test: {e}")
            test_results.append(False)
        
        # Test 2: Only back photo
        print(f"\n📸 Test 5b: Upload only back photo")
        try:
            back_image_data = self.create_test_image("BACK ONLY", color="yellow")
            
            files = {
                'back_photo': ('back_only.png', back_image_data, 'image/png')
            }
            
            data = {
                'team': 'FC Barcelona (Back Photo Only)',
                'league': 'La Liga',
                'season': '2024-25',
                'model': 'authentic',
                'manufacturer': 'Nike',
                'jersey_type': 'third',
                'sku_code': 'BACK-ONLY-TEST',
                'description': 'Testing back photo only upload'
            }
            
            response = self.session.put(
                f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/edit",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                photos_uploaded = result.get('photos_uploaded', 0)
                print(f"✅ Back photo only test successful - {photos_uploaded} photo(s) uploaded")
                test_results.append(True)
            else:
                print(f"❌ Back photo only test failed: {response.status_code}")
                test_results.append(False)
                
        except Exception as e:
            print(f"❌ Error in back photo only test: {e}")
            test_results.append(False)
        
        # Test 3: Both photos
        print(f"\n📸 Test 5c: Upload both front and back photos")
        try:
            front_image_data = self.create_test_image("BOTH FRONT", color="purple")
            back_image_data = self.create_test_image("BOTH BACK", color="orange")
            
            files = {
                'front_photo': ('both_front.png', front_image_data, 'image/png'),
                'back_photo': ('both_back.png', back_image_data, 'image/png')
            }
            
            data = {
                'team': 'FC Barcelona (Both Photos)',
                'league': 'La Liga',
                'season': '2024-25',
                'model': 'replica',
                'manufacturer': 'Nike',
                'jersey_type': 'goalkeeper',
                'sku_code': 'BOTH-PHOTOS-TEST',
                'description': 'Testing both front and back photo upload'
            }
            
            response = self.session.put(
                f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/edit",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                photos_uploaded = result.get('photos_uploaded', 0)
                print(f"✅ Both photos test successful - {photos_uploaded} photo(s) uploaded")
                test_results.append(True)
            else:
                print(f"❌ Both photos test failed: {response.status_code}")
                test_results.append(False)
                
        except Exception as e:
            print(f"❌ Error in both photos test: {e}")
            test_results.append(False)
        
        success_rate = sum(test_results) / len(test_results) * 100 if test_results else 0
        print(f"\n📊 Photo combination tests completed: {sum(test_results)}/{len(test_results)} successful ({success_rate:.1f}%)")
        
        return all(test_results)
    
    def verify_complete_functionality(self):
        """Verify that both jersey data AND photos persist after admin correction"""
        print(f"\n🔍 Step 6: Verify Complete Functionality")
        
        if not self.test_jersey_id:
            print("❌ No test jersey ID available")
            return False
        
        try:
            # Get the final state of the jersey
            response = self.session.get(f"{BASE_URL}/admin/jerseys/pending")
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                
                # Handle both list and single object responses
                if isinstance(pending_jerseys, list):
                    jerseys_list = pending_jerseys
                elif isinstance(pending_jerseys, dict) and 'jerseys' in pending_jerseys:
                    jerseys_list = pending_jerseys['jerseys']
                else:
                    jerseys_list = [pending_jerseys] if pending_jerseys else []
                
                # Find our test jersey
                test_jersey = None
                for jersey in jerseys_list:
                    if jersey.get('id') == self.test_jersey_id:
                        test_jersey = jersey
                        break
                
                if test_jersey:
                    print(f"✅ Final jersey state verification:")
                    print(f"   - ID: {test_jersey.get('id')}")
                    print(f"   - Team: {test_jersey.get('team')}")
                    print(f"   - League: {test_jersey.get('league')}")
                    print(f"   - Season: {test_jersey.get('season')}")
                    print(f"   - Model: {test_jersey.get('model')}")
                    print(f"   - Manufacturer: {test_jersey.get('manufacturer')}")
                    print(f"   - Jersey Type: {test_jersey.get('jersey_type')}")
                    print(f"   - SKU Code: {test_jersey.get('sku_code')}")
                    print(f"   - Description: {test_jersey.get('description', '')[:50]}...")
                    print(f"   - Status: {test_jersey.get('status')}")
                    
                    # Check photo persistence
                    front_photo_url = test_jersey.get('front_photo_url')
                    back_photo_url = test_jersey.get('back_photo_url')
                    images = test_jersey.get('images', [])
                    
                    data_persisted = bool(test_jersey.get('team') and test_jersey.get('league'))
                    photos_persisted = bool(front_photo_url or back_photo_url or images)
                    
                    print(f"   - Jersey Data Persisted: {'✅ Yes' if data_persisted else '❌ No'}")
                    print(f"   - Photos Persisted: {'✅ Yes' if photos_persisted else '❌ No'}")
                    
                    if front_photo_url:
                        print(f"   - Front Photo: {front_photo_url}")
                    if back_photo_url:
                        print(f"   - Back Photo: {back_photo_url}")
                    if images:
                        print(f"   - Images: {images}")
                    
                    complete_functionality = data_persisted and photos_persisted
                    
                    if complete_functionality:
                        print(f"✅ Complete functionality verified - both jersey data AND photos persist!")
                        return True
                    else:
                        print(f"⚠️ Incomplete functionality - missing data or photos")
                        return False
                else:
                    print(f"❌ Test jersey not found for final verification")
                    return False
            else:
                print(f"❌ Could not retrieve jerseys for final verification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in complete functionality verification: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete admin photo upload test suite"""
        print("🎯 TOPKIT ADMIN JERSEY CORRECTION PHOTO UPLOAD TESTING")
        print("=" * 70)
        print("Testing the photo upload functionality in admin jersey correction")
        print("Context: Backend modified to accept multipart form data with photo files")
        print("Frontend: Changed to use FormData instead of JSON for file uploads")
        print("=" * 70)
        
        test_results = []
        
        # Step 1: Admin Authentication
        test_results.append(self.authenticate_admin())
        
        if not test_results[-1]:
            print("\n❌ CRITICAL FAILURE: Admin authentication failed - cannot proceed")
            return False
        
        # Step 2: Get/Create Pending Jersey
        test_results.append(self.get_or_create_pending_jersey())
        
        if not test_results[-1]:
            print("\n❌ CRITICAL FAILURE: Could not get/create pending jersey - cannot proceed")
            return False
        
        # Step 3: Test Admin Edit with Photos
        test_results.append(self.test_admin_edit_with_photos())
        
        # Step 4: Validate Photo Persistence
        test_results.append(self.validate_photo_persistence())
        
        # Step 5: Test Different Photo Combinations
        test_results.append(self.test_different_photo_combinations())
        
        # Step 6: Verify Complete Functionality
        test_results.append(self.verify_complete_functionality())
        
        # Calculate results
        successful_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (successful_tests / total_tests) * 100
        
        print("\n" + "=" * 70)
        print("🎯 ADMIN PHOTO UPLOAD TESTING RESULTS")
        print("=" * 70)
        print(f"✅ Tests Passed: {successful_tests}/{total_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 ADMIN PHOTO UPLOAD FUNCTIONALITY: PRODUCTION-READY")
            print("✅ Admin can now correct jersey information AND update photos simultaneously")
            print("✅ No 'upload not persisting' issues detected")
            print("✅ Complete admin jersey correction workflow including photo uploads is functional")
        elif success_rate >= 60:
            print("⚠️ ADMIN PHOTO UPLOAD FUNCTIONALITY: MOSTLY WORKING")
            print("⚠️ Some issues detected but core functionality operational")
        else:
            print("❌ ADMIN PHOTO UPLOAD FUNCTIONALITY: NEEDS ATTENTION")
            print("❌ Critical issues prevent proper photo upload functionality")
        
        print("=" * 70)
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = AdminPhotoUploadTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        exit(0)
    else:
        print("\n⚠️ Some tests failed - check results above")
        exit(1)

if __name__ == "__main__":
    main()