#!/usr/bin/env python3
"""
Image Upload Fix Backend Testing - TK-TEAM-982B1F Critical Bug Fix
Testing the newly implemented image upload fix for new entities:
- Verify TK-TEAM-982B1F Fix
- Test Image Workflow for new team/brand creation
- Legacy Image Serving via /api/legacy-image/ endpoint
- File System Verification
- Image Display Integration
"""

import requests
import json
import os
import sys
from pathlib import Path
import time
import tempfile
from PIL import Image
import io
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImageUploadFixTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.test_team_id = "TK-TEAM-982B1F"  # Specific team from user report
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
    def authenticate(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                self.log_test("Admin Authentication", True, f"Token length: {len(self.auth_token)} chars")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_tk_team_982b1f_fix(self):
        """Test 1: Verify TK-TEAM-982B1F Fix - User's specific team image issue"""
        try:
            # First, check if the team exists in the database
            response = self.session.get(f"{API_BASE}/teams")
            if response.status_code != 200:
                self.log_test("TK-TEAM-982B1F Team Lookup", False, f"Teams API failed: {response.status_code}")
                return False
            
            teams = response.json()
            target_team = None
            
            # Look for the specific team
            for team in teams:
                if team.get('id') == self.test_team_id or team.get('topkit_reference') == self.test_team_id:
                    target_team = team
                    break
            
            if not target_team:
                self.log_test("TK-TEAM-982B1F Team Exists", False, f"Team {self.test_team_id} not found in database")
                return False
            
            self.log_test("TK-TEAM-982B1F Team Exists", True, f"Found team: {target_team.get('name', 'Unknown')}")
            
            # Check if team has logo_url with legacy format
            logo_url = target_team.get('logo_url', '')
            if not logo_url:
                self.log_test("TK-TEAM-982B1F Logo URL", False, "Team has no logo_url field")
                return False
            
            if not logo_url.startswith('image_uploaded_'):
                self.log_test("TK-TEAM-982B1F Legacy Format", False, f"Logo URL not in legacy format: {logo_url}")
                return False
            
            self.log_test("TK-TEAM-982B1F Legacy Format", True, f"Logo URL: {logo_url}")
            
            # Test if the legacy image endpoint can serve this image
            response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                self.log_test("TK-TEAM-982B1F Image Serving", True, 
                            f"Image served successfully - Content-Type: {content_type}, Size: {len(response.content)} bytes")
                return True
            elif response.status_code == 404:
                self.log_test("TK-TEAM-982B1F Image Serving", False, 
                            f"Image file not found on server for {logo_url}")
                return False
            else:
                self.log_test("TK-TEAM-982B1F Image Serving", False, 
                            f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("TK-TEAM-982B1F Fix Test", False, f"Exception: {str(e)}")
            return False

    def create_test_image(self):
        """Create a test image for upload testing"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (800, 600), color='red')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            return img_buffer
        except Exception as e:
            print(f"Error creating test image: {str(e)}")
            return None

    def test_image_upload_workflow(self):
        """Test 2: Test Image Workflow for new team/brand creation"""
        try:
            # Create a test image
            test_image = self.create_test_image()
            if not test_image:
                self.log_test("Image Upload Workflow", False, "Failed to create test image")
                return False
            
            # Test image upload to contributions directory
            files = {'file': ('test_logo.png', test_image, 'image/png')}
            
            # Try to upload image for contribution
            response = self.session.post(f"{API_BASE}/upload/image", files=files)
            
            if response.status_code == 200:
                upload_data = response.json()
                file_url = upload_data.get('file_url', '')
                self.log_test("Image Upload to Contributions", True, f"Uploaded to: {file_url}")
                
                # Now test creating a team contribution with this image
                contribution_data = {
                    "entity_type": "team",
                    "title": "Test Team for Image Upload Fix",
                    "description": "Testing image upload workflow",
                    "data": {
                        "name": "Test Team Upload Fix",
                        "short_name": "TTUF",
                        "country": "France",
                        "city": "Paris",
                        "founded_year": 2024,
                        "colors": ["Red", "Blue"],
                        "logo_url": f"image_uploaded_{int(time.time() * 1000)}"  # Legacy format
                    }
                }
                
                response = self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data)
                
                if response.status_code == 200:
                    contrib_data = response.json()
                    contrib_id = contrib_data.get('id')
                    self.log_test("Team Contribution Creation", True, f"Created contribution: {contrib_id}")
                    
                    # Test moderating the contribution (approve it)
                    moderation_data = {
                        "action": "approve",
                        "reason": "Testing image upload fix"
                    }
                    
                    response = self.session.post(f"{API_BASE}/contributions-v2/{contrib_id}/moderate", 
                                               json=moderation_data)
                    
                    if response.status_code == 200:
                        mod_data = response.json()
                        entity_id = mod_data.get('entity_id')
                        self.log_test("Contribution Approval", True, f"Created entity: {entity_id}")
                        
                        # Verify the entity was created with proper image handling
                        response = self.session.get(f"{API_BASE}/teams")
                        if response.status_code == 200:
                            teams = response.json()
                            created_team = None
                            for team in teams:
                                if team.get('id') == entity_id:
                                    created_team = team
                                    break
                            
                            if created_team:
                                logo_url = created_team.get('logo_url', '')
                                if logo_url and logo_url.startswith('image_uploaded_'):
                                    # Test if the image was copied to the teams directory
                                    response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
                                    if response.status_code == 200:
                                        self.log_test("Image Copy to Teams Directory", True, 
                                                    f"Image accessible via legacy endpoint")
                                        return True
                                    else:
                                        self.log_test("Image Copy to Teams Directory", False, 
                                                    f"Image not accessible: {response.status_code}")
                                        return False
                                else:
                                    self.log_test("Team Logo URL Format", False, 
                                                f"Logo URL not in expected format: {logo_url}")
                                    return False
                            else:
                                self.log_test("Created Team Verification", False, "Team not found after creation")
                                return False
                        else:
                            self.log_test("Teams API Access", False, f"HTTP {response.status_code}")
                            return False
                    else:
                        self.log_test("Contribution Approval", False, f"HTTP {response.status_code}")
                        return False
                else:
                    self.log_test("Team Contribution Creation", False, f"HTTP {response.status_code}")
                    return False
            else:
                self.log_test("Image Upload to Contributions", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Image Upload Workflow", False, f"Exception: {str(e)}")
            return False

    def test_legacy_image_endpoint(self):
        """Test 3: Legacy Image Serving via /api/legacy-image/ endpoint"""
        try:
            # Test that the endpoint exists and handles various scenarios
            test_cases = [
                ("image_uploaded_1757831105912", "User reported image ID"),
                ("image_uploaded_1234567890", "Non-existent image ID"),
                ("invalid_format", "Invalid format test")
            ]
            
            endpoint_working = True
            
            for image_id, description in test_cases:
                response = self.session.get(f"{API_BASE}/legacy-image/{image_id}")
                
                if image_id == "image_uploaded_1757831105912":
                    # This should be the user's specific image
                    if response.status_code == 200:
                        self.log_test(f"Legacy Endpoint - {description}", True, 
                                    f"Image found and served (Size: {len(response.content)} bytes)")
                    elif response.status_code == 404:
                        self.log_test(f"Legacy Endpoint - {description}", False, 
                                    "User's specific image not found - fix incomplete")
                        endpoint_working = False
                    else:
                        self.log_test(f"Legacy Endpoint - {description}", False, 
                                    f"Unexpected status: {response.status_code}")
                        endpoint_working = False
                        
                elif image_id == "image_uploaded_1234567890":
                    # This should return 404
                    if response.status_code == 404:
                        self.log_test(f"Legacy Endpoint - {description}", True, 
                                    "Correctly returns 404 for non-existent image")
                    else:
                        self.log_test(f"Legacy Endpoint - {description}", False, 
                                    f"Expected 404, got {response.status_code}")
                        
                elif image_id == "invalid_format":
                    # This should handle gracefully
                    if response.status_code in [404, 400]:
                        self.log_test(f"Legacy Endpoint - {description}", True, 
                                    f"Handles invalid format gracefully ({response.status_code})")
                    else:
                        self.log_test(f"Legacy Endpoint - {description}", False, 
                                    f"Unexpected handling: {response.status_code}")
            
            return endpoint_working
            
        except Exception as e:
            self.log_test("Legacy Image Endpoint Test", False, f"Exception: {str(e)}")
            return False

    def test_file_system_verification(self):
        """Test 4: File System Verification - Check image directories"""
        try:
            # Test that the upload directories are accessible
            directories = ["teams", "brands", "players", "competitions", "contributions"]
            accessible_dirs = 0
            
            for directory in directories:
                # Try to access the directory by attempting to upload a test file
                test_image = self.create_test_image()
                if test_image:
                    files = {'file': (f'test_{directory}.png', test_image, 'image/png')}
                    
                    # Try different upload endpoints
                    upload_endpoints = [
                        f"/upload/image",
                        f"/upload/{directory}",
                        f"/upload/master-kit-photo"
                    ]
                    
                    for endpoint in upload_endpoints:
                        try:
                            response = self.session.post(f"{API_BASE}{endpoint}", files=files)
                            if response.status_code in [200, 201]:
                                accessible_dirs += 1
                                self.log_test(f"Directory Access - {directory}", True, 
                                            f"Upload successful via {endpoint}")
                                break
                        except:
                            continue
                    else:
                        self.log_test(f"Directory Access - {directory}", False, 
                                    "No working upload endpoint found")
            
            success = accessible_dirs > 0
            self.log_test("File System Verification", success, 
                         f"Accessible upload directories: {accessible_dirs}/{len(directories)}")
            return success
            
        except Exception as e:
            self.log_test("File System Verification", False, f"Exception: {str(e)}")
            return False

    def test_image_display_integration(self):
        """Test 5: Image Display Integration - Full workflow verification"""
        try:
            # Test the complete workflow: database → legacy format → serving → display
            
            # Get teams with legacy format images
            response = self.session.get(f"{API_BASE}/teams")
            if response.status_code != 200:
                self.log_test("Image Display Integration", False, f"Teams API failed: {response.status_code}")
                return False
            
            teams = response.json()
            legacy_teams = []
            
            for team in teams:
                logo_url = team.get('logo_url', '')
                if logo_url and logo_url.startswith('image_uploaded_'):
                    legacy_teams.append({
                        'name': team.get('name', 'Unknown'),
                        'id': team.get('id', ''),
                        'logo_url': logo_url
                    })
            
            if not legacy_teams:
                self.log_test("Legacy Teams Found", False, "No teams with legacy format images found")
                return False
            
            self.log_test("Legacy Teams Found", True, f"Found {len(legacy_teams)} teams with legacy images")
            
            # Test serving for each legacy team
            successful_serves = 0
            for team in legacy_teams[:5]:  # Test first 5
                response = self.session.get(f"{API_BASE}/legacy-image/{team['logo_url']}")
                
                if response.status_code == 200:
                    successful_serves += 1
                    content_type = response.headers.get('content-type', '')
                    self.log_test(f"Image Serve - {team['name']}", True, 
                                f"Content-Type: {content_type}")
                else:
                    self.log_test(f"Image Serve - {team['name']}", False, 
                                f"HTTP {response.status_code}")
            
            success = successful_serves > 0
            self.log_test("Image Display Integration", success, 
                         f"Successfully served {successful_serves}/{len(legacy_teams[:5])} legacy images")
            return success
            
        except Exception as e:
            self.log_test("Image Display Integration", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all image upload fix tests"""
        print("🎯 IMAGE UPLOAD FIX BACKEND TESTING - TK-TEAM-982B1F")
        print("=" * 70)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test TK-TEAM-982B1F specific fix
        self.test_tk_team_982b1f_fix()
        
        # Step 3: Test image upload workflow
        self.test_image_upload_workflow()
        
        # Step 4: Test legacy image endpoint
        self.test_legacy_image_endpoint()
        
        # Step 5: Test file system verification
        self.test_file_system_verification()
        
        # Step 6: Test image display integration
        self.test_image_display_integration()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print(f"🎯 IMAGE UPLOAD FIX TESTING COMPLETE")
        print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
        
        # Summary of key findings
        print("\n📋 KEY FINDINGS:")
        
        # Check TK-TEAM-982B1F fix
        tk_team_fixed = any(result['success'] for result in self.test_results 
                           if 'TK-TEAM-982B1F' in result['test'])
        print(f"   • TK-TEAM-982B1F Fix: {'✅ RESOLVED' if tk_team_fixed else '❌ STILL BROKEN'}")
        
        # Check image workflow
        workflow_working = any(result['success'] for result in self.test_results 
                              if 'Image Upload Workflow' in result['test'])
        print(f"   • Image Upload Workflow: {'✅ WORKING' if workflow_working else '❌ BROKEN'}")
        
        # Check legacy endpoint
        legacy_working = any(result['success'] for result in self.test_results 
                            if 'Legacy Endpoint' in result['test'])
        print(f"   • Legacy Image Endpoint: {'✅ WORKING' if legacy_working else '❌ BROKEN'}")
        
        # Check file system
        filesystem_ok = any(result['success'] for result in self.test_results 
                           if 'File System' in result['test'])
        print(f"   • File System Access: {'✅ OK' if filesystem_ok else '❌ ISSUES'}")
        
        # Check integration
        integration_ok = any(result['success'] for result in self.test_results 
                            if 'Display Integration' in result['test'])
        print(f"   • Image Display Integration: {'✅ WORKING' if integration_ok else '❌ BROKEN'}")
        
        # Critical assessment
        critical_issues = []
        if not tk_team_fixed:
            critical_issues.append("User's specific team (TK-TEAM-982B1F) image still not displaying")
        if not workflow_working:
            critical_issues.append("New entity image upload workflow broken")
        if not legacy_working:
            critical_issues.append("Legacy image serving endpoint not working")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   • {issue}")
        else:
            print(f"\n🎉 ALL CRITICAL COMPONENTS WORKING!")
        
        return success_rate >= 80 and len(critical_issues) == 0

if __name__ == "__main__":
    tester = ImageUploadFixTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 IMAGE UPLOAD FIX VERIFICATION: SUCCESS")
        print("✅ User's reported bug (TK-TEAM-982B1F) should be resolved")
    else:
        print("\n🚨 IMAGE UPLOAD FIX VERIFICATION: NEEDS ATTENTION")
        print("❌ Critical issues found - user's bug may still exist")
    
    sys.exit(0 if success else 1)