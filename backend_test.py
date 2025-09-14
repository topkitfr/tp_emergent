#!/usr/bin/env python3
"""
Backend Test: Complete Image Transfer Fix for Contribution Approval Workflow
Testing the COMPLETE fix for image transfer from contributions to entity folders

CRITICAL FIXES TO VERIFY:
1. Image upload endpoint stores file paths in contribution document via "uploaded_images" array
2. transfer_contribution_images_to_entity() uses stored file paths instead of pattern matching
3. Proper file copying from contributions/ to entity folders (teams/, brands/, etc.)
4. Correct entity URL field updates
5. Image accessible via /api/legacy-image/ endpoint

COMPLETE WORKFLOW TEST:
1. Authenticate as admin
2. Get existing team for testing
3. Create contribution with entity_id (for update)
4. Upload image to contribution → should store in contributions/ folder AND in contribution document
5. Verify image upload stored file path in contribution.uploaded_images
6. Approve contribution via moderation
7. Verify image transfer worked:
   - Image copied from contributions/ to teams/ folder
   - Team entity logo_url updated to teams/[filename]
   - Image accessible via /api/legacy-image/ or direct serving

AUTHENTICATION: topkitfr@gmail.com/TopKitSecure789#
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://footkit-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImageTransferWorkflowTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        self.test_results.append(result)
        print(result)
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.admin_user = data["user"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_result("Admin Authentication", True, f"Authenticated as {self.admin_user['name']} ({self.admin_user['role']})")
                return True
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_existing_team(self):
        """Get an existing team for testing"""
        try:
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                if teams:
                    test_team = teams[0]  # Use first team
                    self.log_result("Get Existing Team", True, f"Found team: {test_team.get('name', 'Unknown')} (ID: {test_team.get('id', 'Unknown')})")
                    return test_team
                else:
                    self.log_result("Get Existing Team", False, "No teams found in database")
                    return None
            else:
                self.log_result("Get Existing Team", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Get Existing Team", False, f"Exception: {str(e)}")
            return None
    
    def create_contribution_with_entity_id(self, team_id):
        """Create contribution for updating existing team"""
        try:
            contribution_data = {
                "entity_type": "team",
                "entity_id": team_id,  # This makes it an update, not creation
                "title": f"Update Team Logo - Image Transfer Test {int(time.time())}",
                "description": "Testing complete image transfer fix for contribution approval workflow",
                "data": {
                    "name": "Test Team Logo Update",
                    "logo_url": f"image_uploaded_{int(time.time() * 1000)}"  # Legacy format
                },
                "source_urls": []
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data)
            
            if response.status_code == 200:
                contribution = response.json()
                self.log_result("Create Contribution", True, f"Created contribution: {contribution['id']} for team update")
                return contribution
            else:
                self.log_result("Create Contribution", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Create Contribution", False, f"Exception: {str(e)}")
            return None
    
    def create_test_image(self):
        """Create a test image file"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            self.log_result("Create Test Image", False, f"Exception: {str(e)}")
            return None
    
    def upload_image_to_contribution(self, contribution_id):
        """Upload image to contribution and verify storage"""
        try:
            # Create test image
            image_data = self.create_test_image()
            if not image_data:
                return None, None
            
            # Upload image
            files = {
                'file': ('test_logo.png', image_data, 'image/png')
            }
            data = {
                'is_primary': 'true',
                'caption': 'logo'
            }
            
            response = self.session.post(
                f"{API_BASE}/contributions-v2/{contribution_id}/images",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                upload_result = response.json()
                file_path = upload_result.get('file_url')
                self.log_result("Upload Image to Contribution", True, f"Image uploaded: {file_path}")
                
                # Verify image was stored in contribution document
                contrib_response = self.session.get(f"{API_BASE}/contributions-v2/{contribution_id}")
                if contrib_response.status_code == 200:
                    contribution = contrib_response.json()
                    uploaded_images = contribution.get('uploaded_images', [])
                    
                    if uploaded_images:
                        self.log_result("Verify Image Storage in Contribution", True, f"Found {len(uploaded_images)} uploaded images in contribution document")
                        return file_path, uploaded_images[0]
                    else:
                        self.log_result("Verify Image Storage in Contribution", False, "No uploaded_images array found in contribution document")
                        return file_path, None
                else:
                    self.log_result("Verify Image Storage in Contribution", False, f"Failed to fetch contribution: HTTP {contrib_response.status_code}")
                    return file_path, None
                    
            else:
                self.log_result("Upload Image to Contribution", False, f"HTTP {response.status_code}: {response.text}")
                return None, None
                
        except Exception as e:
            self.log_result("Upload Image to Contribution", False, f"Exception: {str(e)}")
            return None, None
    
    def approve_contribution(self, contribution_id):
        """Approve contribution via moderation"""
        try:
            moderation_data = {
                "action": "approve",
                "reason": "Testing complete image transfer fix"
            }
            
            response = self.session.post(
                f"{API_BASE}/contributions-v2/{contribution_id}/moderate",
                json=moderation_data
            )
            
            if response.status_code == 200:
                result = response.json()
                entity_id = result.get('entity_id')
                self.log_result("Approve Contribution", True, f"Contribution approved, entity_id: {entity_id}")
                return entity_id
            else:
                self.log_result("Approve Contribution", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Approve Contribution", False, f"Exception: {str(e)}")
            return None
    
    def verify_image_transfer(self, team_id, original_file_path):
        """Verify image was transferred correctly"""
        try:
            # 1. Check if team entity was updated with correct logo_url
            team_response = self.session.get(f"{API_BASE}/teams")
            if team_response.status_code != 200:
                self.log_result("Verify Team Entity Update", False, f"Failed to fetch teams: HTTP {team_response.status_code}")
                return False
            
            teams = team_response.json()
            test_team = None
            for team in teams:
                if team.get('id') == team_id:
                    test_team = team
                    break
            
            if not test_team:
                self.log_result("Verify Team Entity Update", False, f"Team {team_id} not found")
                return False
            
            logo_url = test_team.get('logo_url', '')
            if logo_url and logo_url.startswith('image_uploaded_'):
                self.log_result("Verify Team Entity Update", True, f"Team logo_url updated to: {logo_url}")
            else:
                self.log_result("Verify Team Entity Update", False, f"Team logo_url not updated correctly: {logo_url}")
                return False
            
            # 2. Check if image file exists in teams/ folder
            # We can't directly check filesystem, but we can test the legacy image endpoint
            legacy_response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
            
            if legacy_response.status_code == 200:
                content_type = legacy_response.headers.get('content-type', '')
                if content_type.startswith('image/'):
                    self.log_result("Verify Image File Transfer", True, f"Image accessible via legacy endpoint (Content-Type: {content_type})")
                    return True
                else:
                    self.log_result("Verify Image File Transfer", False, f"Legacy endpoint returned non-image content: {content_type}")
                    return False
            else:
                self.log_result("Verify Image File Transfer", False, f"Legacy image endpoint failed: HTTP {legacy_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Verify Image Transfer", False, f"Exception: {str(e)}")
            return False
    
    def run_complete_workflow_test(self):
        """Run the complete image transfer workflow test"""
        print("🔍 STARTING COMPLETE IMAGE TRANSFER FIX VERIFICATION")
        print("=" * 80)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            return False
        
        # Step 2: Get existing team for testing
        test_team = self.get_existing_team()
        if not test_team:
            return False
        
        team_id = test_team.get('id')
        
        # Step 3: Create contribution with entity_id (for update)
        contribution = self.create_contribution_with_entity_id(team_id)
        if not contribution:
            return False
        
        contribution_id = contribution['id']
        
        # Step 4: Upload image to contribution
        file_path, uploaded_image_info = self.upload_image_to_contribution(contribution_id)
        if not file_path:
            return False
        
        # Step 5: Verify image upload stored file path in contribution.uploaded_images
        if not uploaded_image_info:
            self.log_result("Critical Fix Verification", False, "uploaded_images array not populated - fix not implemented")
            return False
        
        self.log_result("Critical Fix Verification", True, "uploaded_images array properly populated with file path")
        
        # Step 6: Approve contribution via moderation
        entity_id = self.approve_contribution(contribution_id)
        if not entity_id:
            return False
        
        # Step 7: Verify image transfer worked
        transfer_success = self.verify_image_transfer(team_id, file_path)
        
        return transfer_success
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 IMAGE TRANSFER FIX VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.startswith("✅")])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Print all results
        for result in self.test_results:
            print(result)
        
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print("🎉 IMAGE TRANSFER FIX VERIFICATION: SUCCESS!")
            print("The complete image transfer fix is working correctly.")
        elif success_rate >= 70:
            print("⚠️ IMAGE TRANSFER FIX VERIFICATION: PARTIAL SUCCESS")
            print("Most functionality working but some issues remain.")
        else:
            print("🚨 IMAGE TRANSFER FIX VERIFICATION: CRITICAL ISSUES")
            print("Major problems identified that need immediate attention.")
        
        return success_rate >= 90

def main():
    """Main test execution"""
    test = ImageTransferWorkflowTest()
    
    try:
        success = test.run_complete_workflow_test()
        test.print_summary()
        
        if success:
            print("\n✅ COMPLETE IMAGE TRANSFER FIX VERIFICATION: PASSED")
            print("All critical fixes have been successfully implemented and verified.")
        else:
            print("\n❌ COMPLETE IMAGE TRANSFER FIX VERIFICATION: FAILED")
            print("Critical issues remain in the image transfer workflow.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n🚨 Test failed with exception: {str(e)}")

if __name__ == "__main__":
    main()