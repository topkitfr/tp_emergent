#!/usr/bin/env python3
"""
Backend Test: "Improve This File" Workflow - Entity Update via Contributions

TESTING THE EXACT WORKFLOW THE USER DESCRIBED:
1. Create a team with reference TK-TEAM-616469 (simulating existing entity)
2. Create contribution to UPDATE this specific team (not create new one)
3. Upload logo to the contribution 
4. Approve the contribution
5. Verify that the ORIGINAL TK-TEAM-616469 shows the new logo

CRITICAL TEST POINTS:
- The contribution must have entity_id pointing to the existing team
- After approval, the EXISTING team's logo_url should be updated
- NO new team should be created
- The original team TK-TEAM-616469 should show changes on database page

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
import uuid

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-fixes.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImproveEntityWorkflowTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        self.target_team_id = None
        self.target_team_reference = "TK-TEAM-616469"
        self.contribution_id = None
        self.original_logo_url = None
        self.new_logo_url = None

    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

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
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Authenticated as {self.admin_user['name']} (Role: {self.admin_user['role']})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, error=str(e))
            return False

    def create_target_team(self):
        """Create the target team TK-TEAM-616469 for testing"""
        try:
            # First check if team already exists
            response = self.session.get(f"{API_BASE}/teams")
            if response.status_code == 200:
                teams = response.json()
                for team in teams:
                    if team.get("topkit_reference") == self.target_team_reference:
                        self.target_team_id = team["id"]
                        self.original_logo_url = team.get("logo_url", "")
                        self.log_result(
                            "Target Team Exists",
                            True,
                            f"Found existing team {self.target_team_reference} with ID {self.target_team_id}"
                        )
                        return True

            # Create the team if it doesn't exist
            team_data = {
                "id": str(uuid.uuid4()),
                "name": "Test Team for Improve Workflow",
                "short_name": "TEST",
                "country": "France",
                "city": "Paris",
                "founded_year": 2020,
                "colors": ["Blue", "White"],
                "logo_url": "",  # Start with no logo
                "topkit_reference": self.target_team_reference,
                "created_at": "2025-01-27T10:00:00Z"
            }
            
            # Insert directly into database via admin endpoint or create via contribution
            # For now, let's create a contribution to create the team first
            contribution_data = {
                "entity_type": "team",
                "title": f"Create Team {self.target_team_reference}",
                "description": "Creating target team for improve workflow testing",
                "data": team_data
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data)
            if response.status_code == 200:
                contrib = response.json()
                
                # Auto-approve this contribution to create the team
                moderation_data = {
                    "action": "approve",
                    "reason": "Creating test team for improve workflow"
                }
                
                mod_response = self.session.post(
                    f"{API_BASE}/contributions-v2/{contrib['id']}/moderate",
                    json=moderation_data
                )
                
                if mod_response.status_code == 200:
                    mod_result = mod_response.json()
                    self.target_team_id = mod_result.get("entity_id")
                    
                    self.log_result(
                        "Target Team Creation",
                        True,
                        f"Created team {self.target_team_reference} with ID {self.target_team_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Target Team Creation",
                        False,
                        error=f"Failed to approve team creation: {mod_response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Target Team Creation",
                    False,
                    error=f"Failed to create team contribution: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Target Team Creation", False, error=str(e))
            return False

    def create_update_contribution(self):
        """Create contribution to UPDATE the existing team (not create new one)"""
        try:
            if not self.target_team_id:
                self.log_result(
                    "Update Contribution Creation",
                    False,
                    error="No target team ID available"
                )
                return False

            # Create contribution with entity_id to indicate this is an UPDATE
            contribution_data = {
                "entity_type": "team",
                "entity_id": self.target_team_id,  # CRITICAL: This makes it an update
                "title": f"Improve Team Logo for {self.target_team_reference}",
                "description": "Updating team logo via improve this file workflow",
                "data": {
                    "name": "Test Team for Improve Workflow",
                    "logo_url": "image_uploaded_" + str(int(time.time() * 1000))  # Will be updated after image upload
                }
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data)
            
            if response.status_code == 200:
                contribution = response.json()
                self.contribution_id = contribution["id"]
                
                # Verify the contribution has entity_id set
                if contribution.get("entity_id") == self.target_team_id:
                    self.log_result(
                        "Update Contribution Creation",
                        True,
                        f"Created update contribution {self.contribution_id} for team {self.target_team_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Update Contribution Creation",
                        False,
                        error=f"Contribution entity_id mismatch: expected {self.target_team_id}, got {contribution.get('entity_id')}"
                    )
                    return False
            else:
                self.log_result(
                    "Update Contribution Creation",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Update Contribution Creation", False, error=str(e))
            return False

    def upload_logo_to_contribution(self):
        """Upload logo to the contribution"""
        try:
            if not self.contribution_id:
                self.log_result(
                    "Logo Upload",
                    False,
                    error="No contribution ID available"
                )
                return False

            # Create a test image
            img = Image.new('RGB', (200, 200), color='blue')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Upload image to contribution
            files = {
                'file': ('test_logo.png', img_buffer, 'image/png')
            }
            data = {
                'is_primary': 'true',
                'caption': 'logo'
            }
            
            response = self.session.post(
                f"{API_BASE}/contributions-v2/{self.contribution_id}/images",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                upload_result = response.json()
                self.new_logo_url = upload_result.get("file_url", "")
                
                self.log_result(
                    "Logo Upload",
                    True,
                    f"Uploaded logo to contribution: {self.new_logo_url}"
                )
                return True
            else:
                self.log_result(
                    "Logo Upload",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Logo Upload", False, error=str(e))
            return False

    def verify_contribution_has_image(self):
        """Verify the contribution now has the uploaded image"""
        try:
            if not self.contribution_id:
                return False

            response = self.session.get(f"{API_BASE}/contributions-v2/{self.contribution_id}")
            
            if response.status_code == 200:
                contribution = response.json()
                images_count = contribution.get("images_count", 0)
                uploaded_images = contribution.get("uploaded_images", [])
                
                if images_count > 0 and len(uploaded_images) > 0:
                    self.log_result(
                        "Contribution Image Verification",
                        True,
                        f"Contribution has {images_count} images, uploaded_images array has {len(uploaded_images)} entries"
                    )
                    return True
                else:
                    self.log_result(
                        "Contribution Image Verification",
                        False,
                        error=f"Images count: {images_count}, uploaded_images length: {len(uploaded_images)}"
                    )
                    return False
            else:
                self.log_result(
                    "Contribution Image Verification",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Contribution Image Verification", False, error=str(e))
            return False

    def approve_contribution(self):
        """Approve the contribution to trigger entity update"""
        try:
            if not self.contribution_id:
                self.log_result(
                    "Contribution Approval",
                    False,
                    error="No contribution ID available"
                )
                return False

            moderation_data = {
                "action": "approve",
                "reason": "Approving logo update for improve workflow test"
            }
            
            response = self.session.post(
                f"{API_BASE}/contributions-v2/{self.contribution_id}/moderate",
                json=moderation_data
            )
            
            if response.status_code == 200:
                result = response.json()
                entity_id = result.get("entity_id")
                
                # Verify it updated the SAME entity, not created a new one
                if entity_id == self.target_team_id:
                    self.log_result(
                        "Contribution Approval",
                        True,
                        f"Approved contribution, updated existing entity {entity_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Contribution Approval",
                        False,
                        error=f"Entity ID mismatch: expected {self.target_team_id}, got {entity_id}"
                    )
                    return False
            else:
                self.log_result(
                    "Contribution Approval",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Contribution Approval", False, error=str(e))
            return False

    def verify_original_team_updated(self):
        """Verify that the ORIGINAL team TK-TEAM-616469 now shows the new logo"""
        try:
            if not self.target_team_id:
                return False

            # Get the team by ID
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                target_team = None
                
                for team in teams:
                    if team.get("id") == self.target_team_id:
                        target_team = team
                        break
                
                if target_team:
                    current_logo_url = target_team.get("logo_url", "")
                    topkit_ref = target_team.get("topkit_reference", "")
                    
                    # Verify it's still the same team reference
                    if topkit_ref != self.target_team_reference:
                        self.log_result(
                            "Original Team Update Verification",
                            False,
                            error=f"Team reference changed: expected {self.target_team_reference}, got {topkit_ref}"
                        )
                        return False
                    
                    # Verify logo was updated
                    if current_logo_url and current_logo_url != self.original_logo_url:
                        self.log_result(
                            "Original Team Update Verification",
                            True,
                            f"Team {self.target_team_reference} logo updated from '{self.original_logo_url}' to '{current_logo_url}'"
                        )
                        return True
                    else:
                        self.log_result(
                            "Original Team Update Verification",
                            False,
                            error=f"Logo not updated: original='{self.original_logo_url}', current='{current_logo_url}'"
                        )
                        return False
                else:
                    self.log_result(
                        "Original Team Update Verification",
                        False,
                        error=f"Team with ID {self.target_team_id} not found"
                    )
                    return False
            else:
                self.log_result(
                    "Original Team Update Verification",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Original Team Update Verification", False, error=str(e))
            return False

    def verify_no_duplicate_teams(self):
        """Verify that NO new team was created - only the original was updated"""
        try:
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                teams_with_reference = [
                    team for team in teams 
                    if team.get("topkit_reference") == self.target_team_reference
                ]
                
                if len(teams_with_reference) == 1:
                    self.log_result(
                        "No Duplicate Teams Verification",
                        True,
                        f"Found exactly 1 team with reference {self.target_team_reference}"
                    )
                    return True
                else:
                    self.log_result(
                        "No Duplicate Teams Verification",
                        False,
                        error=f"Found {len(teams_with_reference)} teams with reference {self.target_team_reference}"
                    )
                    return False
            else:
                self.log_result(
                    "No Duplicate Teams Verification",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("No Duplicate Teams Verification", False, error=str(e))
            return False

    def verify_file_exists_in_teams_folder(self):
        """Verify that the logo file exists in teams/ folder"""
        try:
            if not self.target_team_id:
                return False

            # Get the updated team to check logo_url
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                target_team = None
                
                for team in teams:
                    if team.get("id") == self.target_team_id:
                        target_team = team
                        break
                
                if target_team:
                    logo_url = target_team.get("logo_url", "")
                    
                    if logo_url:
                        # Try to access the image via legacy endpoint
                        if logo_url.startswith("image_uploaded_"):
                            image_response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
                        else:
                            image_response = self.session.get(f"{API_BASE}/uploads/{logo_url}")
                        
                        if image_response.status_code == 200:
                            content_type = image_response.headers.get('content-type', '')
                            content_length = len(image_response.content)
                            
                            self.log_result(
                                "File Exists in Teams Folder",
                                True,
                                f"Logo accessible at {logo_url}, Content-Type: {content_type}, Size: {content_length} bytes"
                            )
                            return True
                        else:
                            self.log_result(
                                "File Exists in Teams Folder",
                                False,
                                error=f"Logo not accessible: HTTP {image_response.status_code}"
                            )
                            return False
                    else:
                        self.log_result(
                            "File Exists in Teams Folder",
                            False,
                            error="Team has no logo_url set"
                        )
                        return False
                else:
                    self.log_result(
                        "File Exists in Teams Folder",
                        False,
                        error="Target team not found"
                    )
                    return False
            else:
                self.log_result(
                    "File Exists in Teams Folder",
                    False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("File Exists in Teams Folder", False, error=str(e))
            return False

    def run_complete_workflow_test(self):
        """Run the complete improve entity workflow test"""
        print("🚀 STARTING IMPROVE ENTITY WORKFLOW TEST")
        print("=" * 60)
        print(f"Target: Update team {self.target_team_reference} via contribution")
        print(f"Backend URL: {BACKEND_URL}")
        print()

        # Step 1: Authenticate
        if not self.authenticate_admin():
            return False

        # Step 2: Create/verify target team exists
        if not self.create_target_team():
            return False

        # Step 3: Create update contribution (with entity_id)
        if not self.create_update_contribution():
            return False

        # Step 4: Upload logo to contribution
        if not self.upload_logo_to_contribution():
            return False

        # Step 5: Verify contribution has image
        if not self.verify_contribution_has_image():
            return False

        # Step 6: Approve contribution
        if not self.approve_contribution():
            return False

        # Step 7: Verify original team was updated (not new team created)
        if not self.verify_original_team_updated():
            return False

        # Step 8: Verify no duplicate teams created
        if not self.verify_no_duplicate_teams():
            return False

        # Step 9: Verify file exists in teams/ folder
        if not self.verify_file_exists_in_teams_folder():
            return False

        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 IMPROVE ENTITY WORKFLOW TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        if self.target_team_id:
            print(f"  • Target Team ID: {self.target_team_id}")
        if self.target_team_reference:
            print(f"  • Target Team Reference: {self.target_team_reference}")
        if self.contribution_id:
            print(f"  • Contribution ID: {self.contribution_id}")
        if self.original_logo_url is not None:
            print(f"  • Original Logo URL: '{self.original_logo_url}'")
        if self.new_logo_url:
            print(f"  • New Logo URL: {self.new_logo_url}")
        
        print()
        
        # Overall result
        if success_rate >= 90:
            print("🎉 IMPROVE ENTITY WORKFLOW TEST: EXCELLENT SUCCESS!")
            print("The 'improve this file' workflow is working correctly.")
        elif success_rate >= 70:
            print("⚠️ IMPROVE ENTITY WORKFLOW TEST: PARTIAL SUCCESS")
            print("Most functionality working, but some issues need attention.")
        else:
            print("🚨 IMPROVE ENTITY WORKFLOW TEST: CRITICAL ISSUES")
            print("Major problems with the improve entity workflow.")

def main():
    """Main test execution"""
    tester = ImproveEntityWorkflowTest()
    
    try:
        success = tester.run_complete_workflow_test()
        tester.print_summary()
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        tester.print_summary()
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        tester.print_summary()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)