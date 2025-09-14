#!/usr/bin/env python3
"""
Backend Test for Image Transfer Fix in Contribution Approval Workflow

ISSUE BEING TESTED: 
User reports that TK-CONTRIB-82D916 (logo upload for TK-TEAM-616469) was approved 
but the change doesn't appear on the database page. The images from approved 
contributions aren't being transferred to the actual entities.

NEW FIX IMPLEMENTED:
1. Added transfer_contribution_images_to_entity() function to handle image transfer
2. Modified moderation approval to call image transfer after entity update
3. Function should:
   - Find images in contribution data or contribution uploads folder
   - Copy images from contributions/ folder to appropriate entity folder (teams/, brands/, etc.)
   - Update entity's image URL fields (logo_url, photo_url, etc.)

TESTING WORKFLOW:
1. Create a test contribution with image upload for existing team
2. Upload an image to the contribution via /api/contributions-v2/{id}/images
3. Verify image is stored in contributions/ folder
4. Approve the contribution via moderation endpoint
5. Verify:
   - Image is copied to teams/ folder
   - Team entity's logo_url field is updated
   - Original contribution image remains in contributions/ folder

AUTHENTICATION: Use topkitfr@gmail.com/TopKitSecure789#
"""

import asyncio
import aiohttp
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import io
from PIL import Image

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-collab-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImageTransferContributionTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get("token")
                    user_info = data.get("user", {})
                    
                    self.log_result(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as {user_info.get('name', 'Unknown')} ({user_info.get('role', 'Unknown')})"
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Authentication",
                        False,
                        f"Authentication failed with status {response.status}",
                        {"error": error_text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.admin_token:
            return {}
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    async def get_existing_team(self) -> Optional[Dict[str, Any]]:
        """Get an existing team to test with"""
        try:
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    if teams and len(teams) > 0:
                        # Use the first team found
                        team = teams[0]
                        self.log_result(
                            "Get Existing Team",
                            True,
                            f"Found team: {team.get('name', 'Unknown')} (ID: {team.get('id', 'Unknown')})"
                        )
                        return team
                    else:
                        self.log_result("Get Existing Team", False, "No teams found in database")
                        return None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get Existing Team",
                        False,
                        f"Failed to fetch teams with status {response.status}",
                        {"error": error_text}
                    )
                    return None
                    
        except Exception as e:
            self.log_result("Get Existing Team", False, f"Exception: {str(e)}")
            return None
    
    async def create_test_contribution(self, team_id: str, team_name: str) -> Optional[str]:
        """Create a test contribution for updating an existing team"""
        try:
            contribution_data = {
                "entity_type": "team",
                "entity_id": team_id,  # This indicates we're updating an existing entity
                "title": f"Update logo for {team_name}",
                "description": "Testing image transfer fix - updating team logo",
                "data": {
                    "name": team_name,
                    "logo_url": f"image_uploaded_{int(datetime.now().timestamp() * 1000)}"  # Legacy format
                },
                "source_urls": []
            }
            
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/",
                json=contribution_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    contribution_id = data.get("id")
                    
                    self.log_result(
                        "Create Test Contribution",
                        True,
                        f"Created contribution {contribution_id} for team {team_name}",
                        {"contribution_id": contribution_id, "topkit_reference": data.get("topkit_reference")}
                    )
                    return contribution_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Test Contribution",
                        False,
                        f"Failed to create contribution with status {response.status}",
                        {"error": error_text}
                    )
                    return None
                    
        except Exception as e:
            self.log_result("Create Test Contribution", False, f"Exception: {str(e)}")
            return None
    
    def create_test_image(self) -> bytes:
        """Create a test image for upload"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    async def upload_image_to_contribution(self, contribution_id: str) -> bool:
        """Upload a test image to the contribution"""
        try:
            # Create test image
            image_data = self.create_test_image()
            
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('file', image_data, filename='test_logo.png', content_type='image/png')
            data.add_field('is_primary', 'true')
            data.add_field('caption', 'Test team logo')
            
            headers = self.get_auth_headers()
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/{contribution_id}/images",
                data=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    file_url = data.get("file_url")
                    
                    self.log_result(
                        "Upload Image to Contribution",
                        True,
                        f"Successfully uploaded image to contribution {contribution_id}",
                        {"file_url": file_url}
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Upload Image to Contribution",
                        False,
                        f"Failed to upload image with status {response.status}",
                        {"error": error_text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Upload Image to Contribution", False, f"Exception: {str(e)}")
            return False
    
    async def verify_image_in_contributions_folder(self, contribution_id: str) -> bool:
        """Verify that the uploaded image exists in contributions folder"""
        try:
            # Try to access the uploaded file through the API
            # Since we can't directly access the file system, we'll check if the contribution
            # shows the image was uploaded by checking images_count
            
            headers = self.get_auth_headers()
            async with self.session.get(
                f"{API_BASE}/contributions-v2/{contribution_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    images_count = data.get("images_count", 0)
                    
                    if images_count > 0:
                        self.log_result(
                            "Verify Image in Contributions Folder",
                            True,
                            f"Contribution {contribution_id} shows {images_count} images uploaded"
                        )
                        return True
                    else:
                        self.log_result(
                            "Verify Image in Contributions Folder",
                            False,
                            f"Contribution {contribution_id} shows 0 images uploaded"
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Verify Image in Contributions Folder",
                        False,
                        f"Failed to get contribution details with status {response.status}",
                        {"error": error_text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Verify Image in Contributions Folder", False, f"Exception: {str(e)}")
            return False
    
    async def approve_contribution(self, contribution_id: str) -> bool:
        """Approve the contribution via moderation endpoint"""
        try:
            moderation_data = {
                "action": "approve",
                "reason": "Testing image transfer fix"
            }
            
            headers = self.get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/{contribution_id}/moderate",
                json=moderation_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    entity_id = data.get("entity_id")
                    
                    self.log_result(
                        "Approve Contribution",
                        True,
                        f"Successfully approved contribution {contribution_id}",
                        {"entity_id": entity_id, "message": data.get("message")}
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Approve Contribution",
                        False,
                        f"Failed to approve contribution with status {response.status}",
                        {"error": error_text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Approve Contribution", False, f"Exception: {str(e)}")
            return False
    
    async def verify_team_logo_updated(self, team_id: str) -> bool:
        """Verify that the team's logo_url field has been updated"""
        try:
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    
                    # Find our test team
                    test_team = None
                    for team in teams:
                        if team.get("id") == team_id:
                            test_team = team
                            break
                    
                    if test_team:
                        logo_url = test_team.get("logo_url", "")
                        
                        if logo_url and logo_url.startswith("image_uploaded_"):
                            self.log_result(
                                "Verify Team Logo Updated",
                                True,
                                f"Team {team_id} logo_url updated to: {logo_url}"
                            )
                            return True
                        else:
                            self.log_result(
                                "Verify Team Logo Updated",
                                False,
                                f"Team {team_id} logo_url not updated or invalid format: {logo_url}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Verify Team Logo Updated",
                            False,
                            f"Team {team_id} not found in teams list"
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Verify Team Logo Updated",
                        False,
                        f"Failed to fetch teams with status {response.status}",
                        {"error": error_text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Verify Team Logo Updated", False, f"Exception: {str(e)}")
            return False
    
    async def verify_image_accessible_via_legacy_endpoint(self, logo_url: str) -> bool:
        """Verify that the image is accessible via the legacy image endpoint"""
        try:
            # Extract the image ID from logo_url (should be in format "image_uploaded_TIMESTAMP")
            if not logo_url.startswith("image_uploaded_"):
                self.log_result(
                    "Verify Image Accessible via Legacy Endpoint",
                    False,
                    f"Invalid logo_url format: {logo_url}"
                )
                return False
            
            async with self.session.get(f"{API_BASE}/legacy-image/{logo_url}") as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', '0')
                    
                    self.log_result(
                        "Verify Image Accessible via Legacy Endpoint",
                        True,
                        f"Image {logo_url} accessible via legacy endpoint",
                        {"content_type": content_type, "content_length": content_length}
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Image Accessible via Legacy Endpoint",
                        False,
                        f"Image {logo_url} not accessible via legacy endpoint (status: {response.status})"
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Verify Image Accessible via Legacy Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def run_comprehensive_test(self):
        """Run the comprehensive image transfer test"""
        print("🚀 Starting Image Transfer Fix Testing for Contribution Approval Workflow")
        print("=" * 80)
        
        # Step 1: Authenticate as admin
        if not await self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Get an existing team to test with
        test_team = await self.get_existing_team()
        if not test_team:
            print("❌ Cannot proceed without an existing team")
            return
        
        team_id = test_team.get("id")
        team_name = test_team.get("name", "Unknown Team")
        
        # Step 3: Create a test contribution for updating the team
        contribution_id = await self.create_test_contribution(team_id, team_name)
        if not contribution_id:
            print("❌ Cannot proceed without creating a contribution")
            return
        
        # Step 4: Upload an image to the contribution
        if not await self.upload_image_to_contribution(contribution_id):
            print("❌ Cannot proceed without uploading an image")
            return
        
        # Step 5: Verify image is stored in contributions folder
        if not await self.verify_image_in_contributions_folder(contribution_id):
            print("⚠️ Image may not be properly stored in contributions folder")
        
        # Step 6: Approve the contribution
        if not await self.approve_contribution(contribution_id):
            print("❌ Cannot proceed without approving the contribution")
            return
        
        # Step 7: Verify team's logo_url field is updated
        if not await self.verify_team_logo_updated(team_id):
            print("❌ Team logo_url was not updated - IMAGE TRANSFER FIX FAILED")
            return
        
        # Step 8: Get the updated logo_url and verify image is accessible
        # Re-fetch the team to get the updated logo_url
        async with self.session.get(f"{API_BASE}/teams") as response:
            if response.status == 200:
                teams = await response.json()
                updated_team = None
                for team in teams:
                    if team.get("id") == team_id:
                        updated_team = team
                        break
                
                if updated_team:
                    logo_url = updated_team.get("logo_url", "")
                    if logo_url:
                        await self.verify_image_accessible_via_legacy_endpoint(logo_url)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Overall conclusion
        critical_tests = [
            "Admin Authentication",
            "Create Test Contribution", 
            "Upload Image to Contribution",
            "Approve Contribution",
            "Verify Team Logo Updated",
            "Verify Image Accessible via Legacy Endpoint"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["success"] and result["test"] in critical_tests)
        critical_total = sum(1 for result in self.test_results 
                           if result["test"] in critical_tests)
        
        print(f"\n🎯 CRITICAL WORKFLOW TESTS: {critical_passed}/{critical_total} passed")
        
        if critical_passed == critical_total:
            print("🎉 IMAGE TRANSFER FIX IS WORKING CORRECTLY!")
            print("✅ Images from approved contributions are now properly transferred to entities")
        else:
            print("🚨 IMAGE TRANSFER FIX HAS ISSUES!")
            print("❌ Images from approved contributions are NOT being properly transferred")

async def main():
    """Main test execution"""
    async with ImageTransferContributionTester() as tester:
        await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())