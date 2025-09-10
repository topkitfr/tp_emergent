#!/usr/bin/env python3
"""
TEAM CREATION AND CONTRIBUTIONS SYSTEM TESTING
Testing the specific issues reported in the review request:

1. Team Creation Issue: User created a team but it's not showing on the contributions page
2. Edit Form Issue: User tried to use "améliorer cette page" form to add a logo to the team, but changes are not visible anywhere

Test Plan:
- Team creation endpoint POST /api/teams 
- Check if created teams appear in database
- Test contributions endpoint GET /api/contributions
- Test team update/edit functionality via contribution system
- Check image upload functionality for teams
- Verify if auto-approval is working correctly for new teams
- Test the form that allows editing team information

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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kitfix-contrib.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class TeamContributionsTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = []
        self.created_team_id = None
        
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
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
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
                user_data = data.get('user', {})
                self.user_user_id = user_data.get('id')
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

    def test_team_creation(self):
        """Test team creation endpoint POST /api/teams"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Create a unique team name for testing
            team_name = f"Test Team FC {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            team_data = {
                "name": team_name,
                "country": "France",
                "city": "Paris",
                "founded_year": 2024,
                "short_name": "TTFC",
                "team_colors": ["blue", "white"]
            }
            
            response = requests.post(f"{API_BASE}/teams", json=team_data, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.created_team_id = data.get('id')
                self.log_result(
                    "Team Creation", 
                    True, 
                    f"Team created successfully. ID: {self.created_team_id}, Name: {team_name}, Status: {data.get('verified_level', 'Unknown')}"
                )
                return True
            else:
                self.log_result("Team Creation", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Team Creation", False, "", str(e))
            return False

    def test_team_in_database(self):
        """Check if created team appears in database via GET /api/teams"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.get(f"{API_BASE}/teams", headers=headers)
            
            if response.status_code == 200:
                teams = response.json()
                
                # Look for our created team
                created_team = None
                if self.created_team_id:
                    for team in teams:
                        if team.get('id') == self.created_team_id:
                            created_team = team
                            break
                
                if created_team:
                    self.log_result(
                        "Team in Database", 
                        True, 
                        f"Created team found in database. Name: {created_team.get('name')}, Verified Level: {created_team.get('verified_level')}, Total teams: {len(teams)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Team in Database", 
                        False, 
                        f"Created team NOT found in database. Total teams: {len(teams)}, Looking for ID: {self.created_team_id}"
                    )
                    return False
            else:
                self.log_result("Team in Database", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Team in Database", False, "", str(e))
            return False

    def test_contributions_endpoint(self):
        """Test contributions endpoint GET /api/contributions"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.get(f"{API_BASE}/contributions", headers=headers)
            
            if response.status_code == 200:
                contributions = response.json()
                
                # Look for team-related contributions
                team_contributions = [c for c in contributions if c.get('entity_type') == 'team']
                
                # Check if our created team appears in contributions
                our_team_contribution = None
                if self.created_team_id:
                    for contrib in team_contributions:
                        if contrib.get('entity_id') == self.created_team_id:
                            our_team_contribution = contrib
                            break
                
                if our_team_contribution:
                    self.log_result(
                        "Team in Contributions", 
                        True, 
                        f"Created team found in contributions. Status: {our_team_contribution.get('status')}, Total contributions: {len(contributions)}, Team contributions: {len(team_contributions)}"
                    )
                else:
                    self.log_result(
                        "Team in Contributions", 
                        False, 
                        f"Created team NOT found in contributions. Total contributions: {len(contributions)}, Team contributions: {len(team_contributions)}, Looking for team ID: {self.created_team_id}"
                    )
                
                return True
            else:
                self.log_result("Contributions Endpoint", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Contributions Endpoint", False, "", str(e))
            return False

    def test_team_update_contribution(self):
        """Test team update/edit functionality via contribution system"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            if not self.created_team_id:
                self.log_result("Team Update Contribution", False, "", "No team ID available for testing")
                return False
            
            # Create a contribution to update the team (simulate "améliorer cette page" form)
            contribution_data = {
                "entity_type": "team",
                "entity_id": self.created_team_id,
                "action_type": "UPDATE",
                "proposed_data": {
                    "name": f"Updated Test Team FC {datetime.now().strftime('%H%M%S')}",
                    "city": "Lyon",
                    "colors": ["red", "blue", "white"]
                },
                "title": "Update team information and add logo",
                "description": "Adding logo and updating team information via améliorer cette page form"
            }
            
            response = requests.post(f"{API_BASE}/contributions", json=contribution_data, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                contribution_id = data.get('id')
                self.log_result(
                    "Team Update Contribution", 
                    True, 
                    f"Team update contribution created successfully. ID: {contribution_id}, Status: {data.get('status')}"
                )
                return True
            else:
                self.log_result("Team Update Contribution", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Team Update Contribution", False, "", str(e))
            return False

    def test_image_upload_functionality(self):
        """Test image upload functionality for teams"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Create a simple test image (1x1 pixel PNG)
            test_image_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            )
            
            # Test image upload endpoint
            files = {
                'file': ('test_logo.png', test_image_data, 'image/png')
            }
            
            response = requests.post(f"{API_BASE}/upload/image", files=files, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                image_url = data.get('url') or data.get('file_url') or data.get('image_url')
                self.log_result(
                    "Image Upload Functionality", 
                    True, 
                    f"Image uploaded successfully. URL: {image_url}"
                )
                return True
            else:
                self.log_result("Image Upload Functionality", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Image Upload Functionality", False, "", str(e))
            return False

    def test_auto_approval_system(self):
        """Verify if auto-approval is working correctly for new teams"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Check admin settings for auto-approval
            response = requests.get(f"{API_BASE}/admin/settings", headers=headers)
            
            if response.status_code == 200:
                settings = response.json()
                auto_approval_enabled = settings.get('auto_approval_enabled', False)
                
                self.log_result(
                    "Auto-Approval System Check", 
                    True, 
                    f"Auto-approval enabled: {auto_approval_enabled}, Admin notifications: {settings.get('admin_notifications')}, Community voting: {settings.get('community_voting_enabled')}"
                )
                
                # If we created a team, check its verification status
                if self.created_team_id:
                    team_response = requests.get(f"{API_BASE}/teams", headers=headers)
                    if team_response.status_code == 200:
                        teams = team_response.json()
                        created_team = next((t for t in teams if t.get('id') == self.created_team_id), None)
                        
                        if created_team:
                            verification_level = created_team.get('verified_level')
                            expected_level = 'COMMUNITY_VERIFIED' if auto_approval_enabled else 'PENDING'
                            
                            if verification_level == expected_level:
                                self.log_result(
                                    "Auto-Approval Behavior", 
                                    True, 
                                    f"Team verification level matches auto-approval setting. Level: {verification_level}, Expected: {expected_level}"
                                )
                            else:
                                self.log_result(
                                    "Auto-Approval Behavior", 
                                    False, 
                                    f"Team verification level doesn't match auto-approval setting. Level: {verification_level}, Expected: {expected_level}"
                                )
                
                return True
            else:
                self.log_result("Auto-Approval System Check", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Auto-Approval System Check", False, "", str(e))
            return False

    def test_team_edit_form_endpoints(self):
        """Test the endpoints that power the team edit form"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test form dependencies endpoint for teams
            response = requests.get(f"{API_BASE}/form-dependencies/teams", headers=headers)
            
            if response.status_code == 200:
                teams_data = response.json()
                self.log_result(
                    "Team Edit Form Dependencies", 
                    True, 
                    f"Form dependencies endpoint working. Teams available: {len(teams_data) if isinstance(teams_data, list) else 'N/A'}"
                )
            else:
                self.log_result("Team Edit Form Dependencies", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test individual team detail endpoint if we have a team ID
            if self.created_team_id:
                response = requests.get(f"{API_BASE}/teams/{self.created_team_id}", headers=headers)
                
                if response.status_code == 200:
                    team_detail = response.json()
                    self.log_result(
                        "Team Detail Endpoint", 
                        True, 
                        f"Team detail retrieved successfully. Name: {team_detail.get('name')}, Fields available: {len(team_detail.keys())}"
                    )
                else:
                    self.log_result("Team Detail Endpoint", False, "", f"HTTP {response.status_code}: {response.text}")
            
            return True
                
        except Exception as e:
            self.log_result("Team Edit Form Endpoints", False, "", str(e))
            return False

    def run_all_tests(self):
        """Run all team creation and contributions tests"""
        print("🚀 STARTING TEAM CREATION AND CONTRIBUTIONS SYSTEM TESTING")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - some tests may not run")
        
        if not self.authenticate_user():
            print("❌ User authentication failed - cannot continue")
            return
        
        # Core functionality tests
        print("\n📝 TESTING TEAM CREATION WORKFLOW")
        print("-" * 50)
        self.test_team_creation()
        self.test_team_in_database()
        
        print("\n📋 TESTING CONTRIBUTIONS SYSTEM")
        print("-" * 50)
        self.test_contributions_endpoint()
        self.test_team_update_contribution()
        
        print("\n🖼️ TESTING IMAGE UPLOAD SYSTEM")
        print("-" * 50)
        self.test_image_upload_functionality()
        
        print("\n⚙️ TESTING AUTO-APPROVAL SYSTEM")
        print("-" * 50)
        self.test_auto_approval_system()
        
        print("\n📝 TESTING EDIT FORM ENDPOINTS")
        print("-" * 50)
        self.test_team_edit_form_endpoints()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['error']}")
        
        print("\n🎯 KEY FINDINGS FOR TEAM CREATION AND CONTRIBUTIONS ISSUE:")
        
        # Analyze specific issues
        team_created = any(r['test'] == 'Team Creation' and r['success'] for r in self.test_results)
        team_in_db = any(r['test'] == 'Team in Database' and r['success'] for r in self.test_results)
        team_in_contributions = any(r['test'] == 'Team in Contributions' and r['success'] for r in self.test_results)
        
        if team_created and team_in_db and not team_in_contributions:
            print("🔍 ISSUE IDENTIFIED: Teams are being created and stored in database but NOT appearing in contributions page")
            print("   This suggests a problem with the contributions endpoint or contribution creation logic")
        elif team_created and not team_in_db:
            print("🔍 ISSUE IDENTIFIED: Teams are being created but NOT persisted to database")
            print("   This suggests a database storage issue in the team creation endpoint")
        elif not team_created:
            print("🔍 ISSUE IDENTIFIED: Team creation endpoint is failing")
            print("   This suggests a problem with the POST /api/teams endpoint")
        else:
            print("✅ Team creation and contributions workflow appears to be working correctly")

if __name__ == "__main__":
    tester = TeamContributionsTester()
    tester.run_all_tests()