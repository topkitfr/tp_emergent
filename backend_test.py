#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - Contribution Approval System Testing
Testing the contribution approval system specifically for image updates on master kits
to identify the bug where new photos are not showing up after approval.

FOCUS: Testing the specific flow from contribution approval to master kit image update
to identify where the process is failing.
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://topkit-preview.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "password123"
}

class ContributionApprovalTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.contributions = []
        self.master_kits = []
        
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
    
    def authenticate(self):
        """Authenticate with admin credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=TEST_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                user_email = data.get('user', {}).get('email')
                user_role = data.get('user', {}).get('role')
                self.log_test("Admin Authentication", True, 
                             f"Successfully authenticated as {user_email} (role: {user_role})")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                             f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_contributions(self, status=None):
        """Get contributions with optional status filter"""
        try:
            params = {}
            if status:
                params["status"] = status
                
            response = self.session.get(
                f"{BACKEND_URL}/contributions-v2/",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                contributions = response.json()
                self.contributions = contributions
                
                status_filter = f" with status '{status}'" if status else ""
                self.log_test("Get Contributions", True,
                             f"Retrieved {len(contributions)} contributions{status_filter}")
                
                return contributions
            else:
                self.log_test("Get Contributions", False,
                             f"Failed with status {response.status_code}", response.text)
                return []
                
        except Exception as e:
            self.log_test("Get Contributions", False, f"Exception: {str(e)}")
            return []
    
    def get_master_kits(self):
        """Get master kits to check for image updates"""
        try:
            response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            
            if response.status_code == 200:
                master_kits = response.json()
                self.master_kits = master_kits
                
                self.log_test("Get Master Kits", True,
                             f"Retrieved {len(master_kits)} master kits")
                
                return master_kits
            else:
                self.log_test("Get Master Kits", False,
                             f"Failed with status {response.status_code}", response.text)
                return []
                
        except Exception as e:
            self.log_test("Get Master Kits", False, f"Exception: {str(e)}")
            return []
    
    def test_approved_contributions_with_images(self):
        """Test approved contributions that include image uploads"""
        try:
            print("\n🔍 Testing Approved Contributions with Images...")
            
            # Get approved contributions
            approved_contributions = self.get_contributions("approved")
            
            if not approved_contributions:
                self.log_test("Approved Contributions Analysis", False,
                             "No approved contributions found")
                return False
            
            # Analyze ALL approved contributions to find master kit ones
            master_kit_contributions = []
            image_contributions = []
            
            for contrib in approved_contributions:
                print(f"   Contribution: {contrib.get('id')} - Type: {contrib.get('entity_type')} - Images: {contrib.get('images_count', 0)}")
                
                if contrib.get("entity_type") == "master_kit":
                    master_kit_contributions.append(contrib)
                    
                if contrib.get("images_count", 0) > 0 or contrib.get("uploaded_images"):
                    image_contributions.append(contrib)
            
            print(f"   Found {len(master_kit_contributions)} master kit contributions")
            print(f"   Found {len(image_contributions)} contributions with images")
            
            # Test master kit contributions specifically
            if master_kit_contributions:
                self.log_test("Master Kit Contributions Found", True,
                             f"Found {len(master_kit_contributions)} master kit contributions")
                
                for contrib in master_kit_contributions:
                    self.analyze_contribution_approval(contrib)
            else:
                self.log_test("Master Kit Contributions Found", False,
                             "No master kit contributions found")
            
            # Also test image contributions
            if image_contributions:
                self.log_test("Approved Image Contributions", True,
                             f"Found {len(image_contributions)} approved contributions with images")
                
                for contrib in image_contributions:
                    if contrib.get("entity_type") != "master_kit":  # Already tested above
                        self.analyze_contribution_approval(contrib)
            else:
                self.log_test("Approved Image Contributions", False,
                             f"No approved contributions with images found out of {len(approved_contributions)} approved contributions")
            
            return True
            
        except Exception as e:
            self.log_test("Approved Contributions Analysis", False, f"Exception: {str(e)}")
            return False
    
    def analyze_contribution_approval(self, contribution):
        """Analyze a specific contribution's approval process"""
        try:
            contrib_id = contribution.get("id")
            entity_type = contribution.get("entity_type")
            entity_id = contribution.get("entity_id")
            
            print(f"\n📋 Analyzing Contribution: {contrib_id}")
            print(f"   Entity Type: {entity_type}")
            print(f"   Entity ID: {entity_id}")
            print(f"   Images Count: {contribution.get('images_count', 0)}")
            print(f"   Status: {contribution.get('status')}")
            print(f"   Data: {contribution.get('data', {})}")
            print(f"   Uploaded Images: {contribution.get('uploaded_images', [])}")
            
            # Check if this is a master kit contribution
            if entity_type == "master_kit":
                if entity_id:
                    return self.test_master_kit_image_update(contribution, entity_id)
                else:
                    self.log_test(f"Contribution Analysis - {contrib_id}", False,
                                 f"Master kit contribution without entity_id")
                    return False
            else:
                # Still analyze non-master-kit contributions for completeness
                if contribution.get('images_count', 0) > 0:
                    print(f"   Non-master-kit contribution with images - checking image accessibility")
                    return self.test_non_master_kit_images(contribution)
                else:
                    self.log_test(f"Contribution Analysis - {contrib_id}", True,
                                 f"Non-master-kit contribution ({entity_type}) without images")
                    return True
                
        except Exception as e:
            self.log_test(f"Contribution Analysis - {contrib_id}", False, f"Exception: {str(e)}")
            return False
    
    def test_master_kit_image_update(self, contribution, master_kit_id):
        """Test if master kit was properly updated with new image"""
        try:
            contrib_id = contribution.get("id")
            
            print(f"\n🎯 Testing Master Kit Image Update for: {master_kit_id}")
            
            # Get the master kit
            response = self.session.get(f"{BACKEND_URL}/master-kits/{master_kit_id}", timeout=10)
            
            if response.status_code != 200:
                self.log_test(f"Master Kit Retrieval - {master_kit_id}", False,
                             f"Failed to retrieve master kit: {response.status_code}")
                return False
            
            master_kit = response.json()
            
            # Check if master kit has front_photo_url
            front_photo_url = master_kit.get("front_photo_url")
            
            print(f"   Master Kit: {master_kit.get('club')} {master_kit.get('season')}")
            print(f"   Front Photo URL: {front_photo_url}")
            
            if not front_photo_url:
                self.log_test(f"Master Kit Image Check - {master_kit_id}", False,
                             "Master kit has no front_photo_url - image update failed")
                return False
            
            # Check if the image file exists
            image_accessible = self.test_image_accessibility(front_photo_url, master_kit_id)
            
            # Check contribution's uploaded images
            uploaded_images = contribution.get("uploaded_images", [])
            
            print(f"   Contribution uploaded images: {len(uploaded_images)}")
            for img in uploaded_images:
                print(f"     - Field: {img.get('field_name')}, Path: {img.get('file_path')}")
            
            # Test the transfer process
            transfer_success = self.test_image_transfer_process(contribution, master_kit_id)
            
            if image_accessible and transfer_success:
                self.log_test(f"Master Kit Image Update - {master_kit_id}", True,
                             "Master kit image update successful")
                return True
            else:
                self.log_test(f"Master Kit Image Update - {master_kit_id}", False,
                             f"Image update failed - accessible: {image_accessible}, transfer: {transfer_success}")
                return False
                
        except Exception as e:
            self.log_test(f"Master Kit Image Update - {master_kit_id}", False, f"Exception: {str(e)}")
            return False
    
    def test_image_accessibility(self, image_url, master_kit_id):
        """Test if the image is accessible via the API"""
        try:
            if not image_url:
                return False
            
            # Try different URL formats
            test_urls = []
            
            # Direct API access
            if image_url.startswith("uploads/"):
                test_urls.append(f"{BACKEND_URL}/{image_url}")
            elif image_url.startswith("image_uploaded_"):
                # Legacy format - try different extensions and directories
                test_urls.extend([
                    f"{BACKEND_URL}/legacy-image/{image_url}",
                    f"{BACKEND_URL}/uploads/master_kits/{image_url}.jpg",
                    f"{BACKEND_URL}/uploads/master_kits/{image_url}.png",
                    f"{BACKEND_URL}/uploads/master_kits/{image_url}.jpeg"
                ])
            else:
                test_urls.append(f"{BACKEND_URL}/uploads/{image_url}")
            
            for test_url in test_urls:
                try:
                    response = self.session.get(test_url, timeout=5)
                    if response.status_code == 200:
                        self.log_test(f"Image Accessibility - {master_kit_id}", True,
                                     f"Image accessible at: {test_url}")
                        return True
                except:
                    continue
            
            self.log_test(f"Image Accessibility - {master_kit_id}", False,
                         f"Image not accessible at any tested URL: {test_urls}")
            return False
            
        except Exception as e:
            self.log_test(f"Image Accessibility - {master_kit_id}", False, f"Exception: {str(e)}")
            return False
    
    def test_image_transfer_process(self, contribution, master_kit_id):
        """Test the image transfer process from contributions to master_kits directory"""
        try:
            contrib_id = contribution.get("id")
            uploaded_images = contribution.get("uploaded_images", [])
            
            if not uploaded_images:
                self.log_test(f"Image Transfer Process - {contrib_id}", True,
                             "No uploaded images to transfer")
                return True
            
            print(f"\n🔄 Testing Image Transfer Process...")
            print(f"   Contribution ID: {contrib_id}")
            print(f"   Master Kit ID: {master_kit_id}")
            print(f"   Uploaded Images: {len(uploaded_images)}")
            
            # Check if images exist in contributions directory
            contributions_images_found = 0
            master_kit_images_found = 0
            
            for img_info in uploaded_images:
                file_path = img_info.get("file_path", "")
                field_name = img_info.get("field_name", "")
                
                print(f"     Checking image: {field_name} -> {file_path}")
                
                # Check if source image exists (in contributions directory)
                source_urls = [
                    f"{BACKEND_URL}/{file_path}",
                    f"{BACKEND_URL}/uploads/{file_path}",
                    f"{BACKEND_URL}/uploads/contributions/{file_path}"
                ]
                
                source_found = False
                for source_url in source_urls:
                    try:
                        response = self.session.get(source_url, timeout=5)
                        if response.status_code == 200:
                            contributions_images_found += 1
                            source_found = True
                            print(f"       ✅ Source found: {source_url}")
                            break
                    except:
                        continue
                
                if not source_found:
                    print(f"       ❌ Source not found at: {source_urls}")
                
                # Check if image was transferred to master_kits directory
                # This would require knowing the legacy filename format
                master_kit_urls = [
                    f"{BACKEND_URL}/uploads/master_kits/{file_path}",
                    f"{BACKEND_URL}/legacy-image/{file_path.split('/')[-1].split('.')[0]}"
                ]
                
                target_found = False
                for target_url in master_kit_urls:
                    try:
                        response = self.session.get(target_url, timeout=5)
                        if response.status_code == 200:
                            master_kit_images_found += 1
                            target_found = True
                            print(f"       ✅ Target found: {target_url}")
                            break
                    except:
                        continue
                
                if not target_found:
                    print(f"       ❌ Target not found at: {master_kit_urls}")
            
            success = contributions_images_found > 0 and master_kit_images_found > 0
            
            self.log_test(f"Image Transfer Process - {contrib_id}", success,
                         f"Transfer check: {contributions_images_found} source images, {master_kit_images_found} target images",
                         {
                             "source_images_found": contributions_images_found,
                             "target_images_found": master_kit_images_found,
                             "total_uploaded_images": len(uploaded_images)
                         })
            
            return success
            
        except Exception as e:
            self.log_test(f"Image Transfer Process - {contrib_id}", False, f"Exception: {str(e)}")
            return False
    
    def test_pending_contribution_approval(self):
        """Test approving a pending contribution with image upload"""
        try:
            print("\n🔄 Testing Pending Contribution Approval...")
            
            # Get pending contributions
            pending_contributions = self.get_contributions("pending_review")
            
            if not pending_contributions:
                self.log_test("Pending Contribution Approval", True,
                             "No pending contributions found - cannot test approval process")
                return True
            
            # Find a pending contribution with images for master_kit
            target_contribution = None
            for contrib in pending_contributions:
                if (contrib.get("entity_type") == "master_kit" and 
                    contrib.get("images_count", 0) > 0):
                    target_contribution = contrib
                    break
            
            if not target_contribution:
                self.log_test("Pending Contribution Approval", True,
                             "No pending master_kit contributions with images found")
                return True
            
            # Test the approval process
            return self.test_contribution_approval_flow(target_contribution)
            
        except Exception as e:
            self.log_test("Pending Contribution Approval", False, f"Exception: {str(e)}")
            return False
    
    def test_non_master_kit_images(self, contribution):
        """Test image accessibility for non-master-kit contributions"""
        try:
            contrib_id = contribution.get("id")
            entity_type = contribution.get("entity_type")
            
            uploaded_images = contribution.get("uploaded_images", [])
            
            if not uploaded_images:
                self.log_test(f"Non-Master-Kit Images - {contrib_id}", True,
                             "No uploaded images to test")
                return True
            
            accessible_images = 0
            total_images = len(uploaded_images)
            
            for img_info in uploaded_images:
                file_path = img_info.get("file_path", "")
                field_name = img_info.get("field_name", "")
                
                # Test accessibility
                test_urls = [
                    f"{BACKEND_URL}/{file_path}",
                    f"{BACKEND_URL}/uploads/{file_path}",
                    f"{BACKEND_URL}/uploads/{entity_type}s/{file_path}"
                ]
                
                for test_url in test_urls:
                    try:
                        response = self.session.get(test_url, timeout=5)
                        if response.status_code == 200:
                            accessible_images += 1
                            print(f"     ✅ Image accessible: {test_url}")
                            break
                    except:
                        continue
                else:
                    print(f"     ❌ Image not accessible: {field_name} -> {file_path}")
            
            success = accessible_images == total_images
            self.log_test(f"Non-Master-Kit Images - {contrib_id}", success,
                         f"Image accessibility: {accessible_images}/{total_images} images accessible")
            
            return success
            
        except Exception as e:
            self.log_test(f"Non-Master-Kit Images - {contrib_id}", False, f"Exception: {str(e)}")
            return False

    def test_problematic_images_from_logs(self):
        """Test specific problematic images identified from backend logs"""
        try:
            print("\n🚨 Testing Problematic Images from Backend Logs...")
            
            # Images that showed 404 errors in the logs
            problematic_images = [
                "image_uploaded_1758016021592",
                "image_uploaded_1758015522242", 
                "image_uploaded_nike_logo"
            ]
            
            for image_id in problematic_images:
                print(f"\n   Testing image: {image_id}")
                
                # Test different URL patterns
                test_urls = [
                    f"{BACKEND_URL}/legacy-image/{image_id}",
                    f"{BACKEND_URL}/uploads/master_kits/{image_id}.jpg",
                    f"{BACKEND_URL}/uploads/master_kits/{image_id}.png",
                    f"{BACKEND_URL}/uploads/master_kits/{image_id}.jpeg",
                    f"{BACKEND_URL}/uploads/teams/{image_id}.jpg",
                    f"{BACKEND_URL}/uploads/teams/{image_id}.png",
                    f"{BACKEND_URL}/uploads/brands/{image_id}.jpg",
                    f"{BACKEND_URL}/uploads/brands/{image_id}.png",
                    f"{BACKEND_URL}/uploads/contributions/{image_id}.jpg",
                    f"{BACKEND_URL}/uploads/contributions/{image_id}.png"
                ]
                
                found = False
                for test_url in test_urls:
                    try:
                        response = self.session.get(test_url, timeout=5)
                        if response.status_code == 200:
                            print(f"     ✅ Found at: {test_url}")
                            found = True
                            break
                    except:
                        continue
                
                if not found:
                    print(f"     ❌ Not found at any location")
                    self.log_test(f"Problematic Image - {image_id}", False,
                                 f"Image not accessible at any tested location")
                else:
                    self.log_test(f"Problematic Image - {image_id}", True,
                                 f"Image found and accessible")
            
            return True
            
        except Exception as e:
            self.log_test("Problematic Images Analysis", False, f"Exception: {str(e)}")
            return False

    def test_contribution_approval_flow(self, contribution):
        """Test the complete approval flow for a contribution"""
        try:
            contrib_id = contribution.get("id")
            entity_id = contribution.get("entity_id")
            
            print(f"\n✅ Testing Approval Flow for Contribution: {contrib_id}")
            print(f"   Entity ID: {entity_id}")
            print(f"   Entity Type: {contribution.get('entity_type')}")
            
            # Get master kit before approval
            if entity_id:
                before_response = self.session.get(f"{BACKEND_URL}/master-kits/{entity_id}", timeout=10)
                before_master_kit = before_response.json() if before_response.status_code == 200 else {}
                before_photo_url = before_master_kit.get("front_photo_url")
                
                print(f"   Before approval - Photo URL: {before_photo_url}")
            
            # Approve the contribution
            approval_data = {
                "action": "approve",
                "reason": "Testing image update approval process"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/{contrib_id}/moderate",
                json=approval_data,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test(f"Contribution Approval - {contrib_id}", False,
                             f"Approval failed with status {response.status_code}: {response.text}")
                return False
            
            approval_result = response.json()
            print(f"   Approval result: {approval_result}")
            
            # Get master kit after approval
            if entity_id:
                after_response = self.session.get(f"{BACKEND_URL}/master-kits/{entity_id}", timeout=10)
                after_master_kit = after_response.json() if after_response.status_code == 200 else {}
                after_photo_url = after_master_kit.get("front_photo_url")
                
                print(f"   After approval - Photo URL: {after_photo_url}")
                
                # Check if the photo URL was updated
                if before_photo_url != after_photo_url:
                    self.log_test(f"Contribution Approval - {contrib_id}", True,
                                 f"Master kit photo URL updated: {before_photo_url} -> {after_photo_url}")
                    
                    # Test if the new image is accessible
                    return self.test_image_accessibility(after_photo_url, entity_id)
                else:
                    self.log_test(f"Contribution Approval - {contrib_id}", False,
                                 f"Master kit photo URL not updated (still: {after_photo_url})")
                    return False
            else:
                self.log_test(f"Contribution Approval - {contrib_id}", True,
                             "Contribution approved successfully (no entity_id to verify)")
                return True
                
        except Exception as e:
            self.log_test(f"Contribution Approval - {contrib_id}", False, f"Exception: {str(e)}")
            return False

    def create_test_contribution_with_image(self):
        """Create a test contribution with image to test the approval process"""
        try:
            print("\n🧪 Creating Test Contribution with Image...")
            
            # Get a master kit to update
            master_kits = self.get_master_kits()
            if not master_kits:
                self.log_test("Create Test Contribution", False, "No master kits found to update")
                return None
            
            # Use the first master kit
            target_master_kit = master_kits[0]
            master_kit_id = target_master_kit.get("id")
            
            print(f"   Target Master Kit: {target_master_kit.get('club')} {target_master_kit.get('season')}")
            print(f"   Master Kit ID: {master_kit_id}")
            
            # Create a contribution for updating the master kit with a new image
            contribution_data = {
                "entity_type": "master_kit",
                "entity_id": master_kit_id,
                "title": f"Update jersey photo for {target_master_kit.get('club')} {target_master_kit.get('season')}",
                "description": "Testing the fixed image transfer system",
                "data": {
                    "front_photo_url": "image_uploaded_test_" + str(int(datetime.now().timestamp()))
                },
                "source_urls": []
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/",
                json=contribution_data,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Create Test Contribution", False,
                             f"Failed to create contribution: {response.status_code} - {response.text}")
                return None
            
            contribution = response.json()
            contrib_id = contribution.get("id")
            
            print(f"   Created contribution: {contrib_id}")
            
            # Create a dummy image file for testing
            import tempfile
            import os
            from PIL import Image
            
            # Create a simple test image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                # Create a simple 800x600 test image
                test_image = Image.new('RGB', (800, 600), color='red')
                test_image.save(temp_file.name, 'PNG')
                temp_file_path = temp_file.name
            
            try:
                # Upload the image to the contribution
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('test_image.png', f, 'image/png')}
                    data = {
                        'is_primary': 'true',
                        'caption': 'front_photo'
                    }
                    
                    upload_response = self.session.post(
                        f"{BACKEND_URL}/contributions-v2/{contrib_id}/images",
                        files=files,
                        data=data,
                        timeout=10
                    )
                    
                    if upload_response.status_code == 200:
                        upload_result = upload_response.json()
                        print(f"   Image uploaded: {upload_result.get('file_url')}")
                        
                        self.log_test("Create Test Contribution", True,
                                     f"Created test contribution {contrib_id} with image upload")
                        return contribution
                    else:
                        self.log_test("Create Test Contribution", False,
                                     f"Failed to upload image: {upload_response.status_code} - {upload_response.text}")
                        return None
                        
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_test("Create Test Contribution", False, f"Exception: {str(e)}")
            return None

    def test_fixed_image_transfer_system(self):
        """Test the fixed image transfer system by creating and approving a contribution"""
        try:
            print("\n🔧 Testing Fixed Image Transfer System...")
            
            # Create a test contribution with image
            test_contribution = self.create_test_contribution_with_image()
            
            if not test_contribution:
                self.log_test("Fixed Image Transfer System", False,
                             "Could not create test contribution")
                return False
            
            # Wait a moment for the contribution to be fully processed
            import time
            time.sleep(2)
            
            # Get the updated contribution to see if image was properly stored
            contrib_id = test_contribution.get("id")
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/{contrib_id}", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Fixed Image Transfer System", False,
                             f"Could not retrieve created contribution: {response.status_code}")
                return False
            
            updated_contribution = response.json()
            
            print(f"   Updated contribution data: {updated_contribution.get('data', {})}")
            print(f"   Images count: {updated_contribution.get('images_count', 0)}")
            print(f"   Uploaded images: {updated_contribution.get('uploaded_images', [])}")
            
            # Now test the approval process
            return self.test_contribution_approval_flow(updated_contribution)
            
        except Exception as e:
            self.log_test("Fixed Image Transfer System", False, f"Exception: {str(e)}")
            return False
    
    def test_moderation_stats(self):
        """Test moderation statistics endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/admin/moderation-stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                self.log_test("Moderation Stats", True,
                             f"Stats: {stats.get('pending')} pending, {stats.get('approved')} approved, {stats.get('rejected')} rejected")
                return stats
            else:
                self.log_test("Moderation Stats", False,
                             f"Failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Moderation Stats", False, f"Exception: {str(e)}")
            return None
    
    def test_specific_contribution(self, contribution_id):
        """Test a specific contribution by ID"""
        try:
            print(f"\n🔍 Testing Specific Contribution: {contribution_id}")
            
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/{contribution_id}", timeout=10)
            
            if response.status_code != 200:
                self.log_test(f"Specific Contribution - {contribution_id}", False,
                             f"Failed to retrieve contribution: {response.status_code}")
                return False
            
            contribution = response.json()
            
            print(f"   Title: {contribution.get('title')}")
            print(f"   Entity Type: {contribution.get('entity_type')}")
            print(f"   Entity ID: {contribution.get('entity_id')}")
            print(f"   Status: {contribution.get('status')}")
            print(f"   Images Count: {contribution.get('images_count', 0)}")
            print(f"   Uploaded Images: {contribution.get('uploaded_images', [])}")
            
            # Analyze this contribution
            return self.analyze_contribution_approval(contribution)
            
        except Exception as e:
            self.log_test(f"Specific Contribution - {contribution_id}", False, f"Exception: {str(e)}")
            return False

    def test_improve_team_profile_workflow(self):
        """Test the complete 'Improve Team Profile' workflow with image upload"""
        try:
            print("\n🎯 Testing 'Improve Team Profile' Workflow with Image Upload...")
            
            # Step 1: Get teams to find one to edit
            teams_response = self.session.get(f"{BACKEND_URL}/teams", timeout=10)
            if teams_response.status_code != 200:
                self.log_test("Improve Team Profile Workflow", False, "Failed to get teams")
                return False
            
            teams = teams_response.json()
            if not teams:
                self.log_test("Improve Team Profile Workflow", False, "No teams found to edit")
                return False
            
            # Use the first team for testing
            target_team = teams[0]
            team_id = target_team.get("id")
            team_name = target_team.get("name", "Unknown Team")
            
            print(f"   Target Team: {team_name} (ID: {team_id})")
            
            # Step 2: Create a contribution for editing this team with image upload
            contribution_data = {
                "entity_type": "team",
                "entity_id": team_id,
                "title": f"Update team logo for {team_name}",
                "description": "Testing the fixed image upload system for editing existing teams",
                "data": {
                    "logo_url": f"image_uploaded_test_{int(datetime.now().timestamp())}"
                },
                "source_urls": []
            }
            
            print(f"   Creating contribution for team edit...")
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/",
                json=contribution_data,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Improve Team Profile Workflow", False,
                             f"Failed to create contribution: {response.status_code} - {response.text}")
                return False
            
            contribution = response.json()
            contrib_id = contribution.get("id")
            
            print(f"   Created contribution: {contrib_id}")
            
            # Step 3: Upload an image to this contribution (simulating the fixed pendingImages system)
            import tempfile
            from PIL import Image
            
            # Create a test image
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                test_image = Image.new('RGB', (800, 600), color='blue')
                test_image.save(temp_file.name, 'PNG')
                temp_file_path = temp_file.name
            
            try:
                # Upload the image to the contribution
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('team_logo_test.png', f, 'image/png')}
                    data = {
                        'is_primary': 'true',
                        'caption': 'logo_url'
                    }
                    
                    upload_response = self.session.post(
                        f"{BACKEND_URL}/contributions-v2/{contrib_id}/images",
                        files=files,
                        data=data,
                        timeout=10
                    )
                    
                    if upload_response.status_code != 200:
                        self.log_test("Improve Team Profile Workflow", False,
                                     f"Failed to upload image: {upload_response.status_code} - {upload_response.text}")
                        return False
                    
                    upload_result = upload_response.json()
                    print(f"   Image uploaded: {upload_result.get('file_url')}")
                    
            finally:
                # Clean up temp file
                import os
                os.unlink(temp_file_path)
            
            # Step 4: Verify the contribution now shows correct images count
            updated_response = self.session.get(f"{BACKEND_URL}/contributions-v2/{contrib_id}", timeout=10)
            if updated_response.status_code == 200:
                updated_contribution = updated_response.json()
                images_count = updated_contribution.get('images_count', 0)
                uploaded_images = updated_contribution.get('uploaded_images', [])
                
                print(f"   Updated contribution images count: {images_count}")
                print(f"   Uploaded images: {len(uploaded_images)}")
                
                if images_count > 0 and len(uploaded_images) > 0:
                    self.log_test("Improve Team Profile Workflow", True,
                                 f"✅ Image upload successful - Images count: {images_count}, Uploaded images: {len(uploaded_images)}")
                    
                    # Step 5: Test the approval process
                    return self.test_contribution_approval_flow(updated_contribution)
                else:
                    self.log_test("Improve Team Profile Workflow", False,
                                 f"❌ Image upload failed - Images count: {images_count}, Uploaded images: {len(uploaded_images)}")
                    return False
            else:
                self.log_test("Improve Team Profile Workflow", False,
                             "Failed to retrieve updated contribution")
                return False
                
        except Exception as e:
            self.log_test("Improve Team Profile Workflow", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run comprehensive contribution approval system tests"""
        print("🧪 Starting TopKit Image Upload System Testing")
        print("Testing the fixed image upload system for 'Improve Team Profile' form")
        print("FOCUS: Verifying the user's reported bug is resolved")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Step 2: Get moderation stats
        print("📊 Getting Moderation Statistics...")
        stats = self.test_moderation_stats()
        print()
        
        # Step 3: Test the specific contribution mentioned by user (TK-CONTRIB-24325C)
        print("🔍 Testing Specific Contribution TK-CONTRIB-24325C...")
        # First try to find this contribution
        all_contributions = self.get_contributions()
        target_contribution = None
        for contrib in all_contributions:
            if contrib.get('topkit_reference') == 'TK-CONTRIB-24325C':
                target_contribution = contrib
                break
        
        if target_contribution:
            self.test_specific_contribution(target_contribution.get('id'))
        else:
            print("   TK-CONTRIB-24325C not found in current contributions")
        print()
        
        # Step 4: Test the complete 'Improve Team Profile' workflow
        print("🎯 Testing Complete 'Improve Team Profile' Workflow...")
        self.test_improve_team_profile_workflow()
        print()
        
        # Step 5: Test approved contributions with images
        print("✅ Testing Approved Contributions with Images...")
        self.test_approved_contributions_with_images()
        print()
        
        # Step 6: Test the fixed image transfer system
        print("🔧 Testing Fixed Image Transfer System...")
        self.test_fixed_image_transfer_system()
        print()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("📊 CONTRIBUTION APPROVAL SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        auth_tests = [r for r in self.test_results if 'Authentication' in r['test']]
        contribution_tests = [r for r in self.test_results if 'Contribution' in r['test']]
        image_tests = [r for r in self.test_results if 'Image' in r['test']]
        approval_tests = [r for r in self.test_results if 'Approval' in r['test']]
        
        print(f"\nTest Categories:")
        print(f"  Authentication: {len([r for r in auth_tests if r['success']])}/{len(auth_tests)} ✅")
        print(f"  Contributions: {len([r for r in contribution_tests if r['success']])}/{len(contribution_tests)} ✅")
        print(f"  Image Processing: {len([r for r in image_tests if r['success']])}/{len(image_tests)} ✅")
        print(f"  Approval Process: {len([r for r in approval_tests if r['success']])}/{len(approval_tests)} ✅")
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if not r['success'] and 
                           ('Image Update' in r['test'] or 'Transfer' in r['test'] or 'Approval' in r['test'])]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED: {len(critical_failures)}")
            for failure in critical_failures:
                print(f"  • {failure['test']}: {failure['message']}")
                if failure.get('details'):
                    print(f"    Details: {failure['details']}")
        
        if failed_tests > 0:
            print("\n❌ ALL FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        # Specific findings for the bug report
        image_update_failures = [r for r in self.test_results if not r['success'] and 'Image Update' in r['test']]
        transfer_failures = [r for r in self.test_results if not r['success'] and 'Transfer' in r['test']]
        accessibility_failures = [r for r in self.test_results if not r['success'] and 'Accessibility' in r['test']]
        
        print(f"\n🎯 BUG ANALYSIS RESULTS:")
        print(f"  Image Update Failures: {len(image_update_failures)}")
        print(f"  Image Transfer Failures: {len(transfer_failures)}")
        print(f"  Image Accessibility Failures: {len(accessibility_failures)}")
        
        if image_update_failures or transfer_failures or accessibility_failures:
            print("\n🔍 ROOT CAUSE ANALYSIS:")
            print("  The contribution approval system has issues with:")
            if transfer_failures:
                print("  - Image transfer from contributions/ to master_kits/ directory")
            if accessibility_failures:
                print("  - Image accessibility after transfer")
            if image_update_failures:
                print("  - Master kit front_photo_url field updates")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND!")
            print("  The contribution approval system appears to be working correctly.")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = ContributionApprovalTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()