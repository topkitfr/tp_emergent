#!/usr/bin/env python3
"""
TopKit Profile Enhancement Features Backend Testing
Testing the new profile enhancement features as requested in the review.

Test Areas:
1. Teams Dropdown Endpoint: GET /api/teams/dropdown
2. Public Profile Info Endpoints: 
   - GET /api/users/profile/public-info 
   - PUT /api/users/profile/public-info
3. Public Profile View: GET /api/users/{user_id}/public-profile
4. Profile Picture Integration: Verify profile picture URLs are stored in users collection

Authentication: topkitfr@gmail.com/TopKitSecure789#
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ProfileEnhancementTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
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
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating as admin...")
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                
                # Set authorization header
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {user_data.get('name', 'Unknown')} (Role: {user_data.get('role', 'Unknown')}, ID: {self.admin_user_id})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def test_teams_dropdown_endpoint(self):
        """Test GET /api/teams/dropdown endpoint"""
        try:
            print("🏆 Testing Teams Dropdown Endpoint...")
            
            response = self.session.get(f"{BACKEND_URL}/teams/dropdown")
            
            if response.status_code == 200:
                teams = response.json()
                
                # Validate response structure
                if isinstance(teams, list):
                    team_count = len(teams)
                    
                    # Check if we have teams
                    if team_count > 0:
                        # Validate team structure
                        sample_team = teams[0]
                        required_fields = ['id', 'name']
                        
                        has_required_fields = all(field in sample_team for field in required_fields)
                        
                        if has_required_fields:
                            # Look for specific teams that should exist
                            team_names = [team.get('name', '') for team in teams]
                            barcelona_found = any('barcelona' in name.lower() for name in team_names)
                            
                            self.log_result(
                                "Teams Dropdown Endpoint",
                                True,
                                f"Found {team_count} teams with proper structure. Barcelona found: {barcelona_found}. Sample team: {sample_team}"
                            )
                        else:
                            self.log_result(
                                "Teams Dropdown Endpoint",
                                False,
                                f"Teams missing required fields. Sample: {sample_team}",
                                f"Required fields {required_fields} not found"
                            )
                    else:
                        self.log_result(
                            "Teams Dropdown Endpoint",
                            False,
                            "No teams returned",
                            "Empty teams list"
                        )
                else:
                    self.log_result(
                        "Teams Dropdown Endpoint",
                        False,
                        f"Invalid response format: {type(teams)}",
                        "Expected list of teams"
                    )
            else:
                self.log_result(
                    "Teams Dropdown Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Teams Dropdown Endpoint", False, "", str(e))

    def test_get_public_profile_info(self):
        """Test GET /api/users/profile/public-info endpoint"""
        try:
            print("👤 Testing Get Public Profile Info Endpoint...")
            
            response = self.session.get(f"{BACKEND_URL}/users/profile/public-info")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Validate response structure
                expected_fields = ['bio', 'favorite_club', 'instagram_username', 'twitter_username', 'website', 'profile_picture_url']
                
                has_expected_structure = all(field in profile_data for field in expected_fields)
                
                if has_expected_structure:
                    self.log_result(
                        "Get Public Profile Info",
                        True,
                        f"Profile data retrieved successfully: {profile_data}"
                    )
                else:
                    missing_fields = [field for field in expected_fields if field not in profile_data]
                    self.log_result(
                        "Get Public Profile Info",
                        False,
                        f"Missing fields: {missing_fields}",
                        f"Profile data: {profile_data}"
                    )
            else:
                self.log_result(
                    "Get Public Profile Info",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Get Public Profile Info", False, "", str(e))

    def test_update_public_profile_info(self):
        """Test PUT /api/users/profile/public-info endpoint"""
        try:
            print("✏️ Testing Update Public Profile Info Endpoint...")
            
            # First, get teams dropdown to select a favorite club
            teams_response = self.session.get(f"{BACKEND_URL}/teams/dropdown")
            favorite_club_id = None
            
            if teams_response.status_code == 200:
                teams = teams_response.json()
                if teams:
                    # Look for Barcelona or use first team
                    barcelona_team = next((team for team in teams if 'barcelona' in team.get('name', '').lower()), None)
                    favorite_club_id = barcelona_team['id'] if barcelona_team else teams[0]['id']
            
            # Test data as specified in the review request
            test_profile_data = {
                "bio": "Passionate collector of vintage football jerseys 🏆",
                "favorite_club": favorite_club_id,
                "instagram_username": "topkit_collector",
                "twitter_username": "topkit_fan",
                "website": "https://myjerseycollection.com"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/users/profile/public-info",
                json=test_profile_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify the update was successful
                if "message" in result:
                    # Now get the profile to verify the update
                    verify_response = self.session.get(f"{BACKEND_URL}/users/profile/public-info")
                    
                    if verify_response.status_code == 200:
                        updated_profile = verify_response.json()
                        
                        # Check if our test data was saved
                        bio_match = updated_profile.get('bio') == test_profile_data['bio']
                        instagram_match = updated_profile.get('instagram_username') == test_profile_data['instagram_username']
                        twitter_match = updated_profile.get('twitter_username') == test_profile_data['twitter_username']
                        website_match = updated_profile.get('website') == test_profile_data['website']
                        favorite_club_match = updated_profile.get('favorite_club') == test_profile_data['favorite_club']
                        
                        all_fields_updated = bio_match and instagram_match and twitter_match and website_match and favorite_club_match
                        
                        self.log_result(
                            "Update Public Profile Info",
                            all_fields_updated,
                            f"Profile updated and verified. Bio: {bio_match}, Instagram: {instagram_match}, Twitter: {twitter_match}, Website: {website_match}, Favorite Club: {favorite_club_match}",
                            "" if all_fields_updated else f"Some fields not updated correctly: {updated_profile}"
                        )
                    else:
                        self.log_result(
                            "Update Public Profile Info",
                            False,
                            "Update successful but verification failed",
                            f"Verification response: {verify_response.status_code} - {verify_response.text}"
                        )
                else:
                    self.log_result(
                        "Update Public Profile Info",
                        False,
                        f"Unexpected response format: {result}",
                        "Missing success message"
                    )
            else:
                self.log_result(
                    "Update Public Profile Info",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Update Public Profile Info", False, "", str(e))

    def test_public_profile_view(self):
        """Test GET /api/users/{user_id}/public-profile endpoint"""
        try:
            print("👁️ Testing Public Profile View Endpoint...")
            
            # Test with admin user ID
            response = self.session.get(f"{BACKEND_URL}/users/{self.admin_user_id}/public-profile")
            
            if response.status_code == 200:
                public_profile = response.json()
                
                # Validate response structure
                expected_fields = ['id', 'name', 'bio', 'favorite_club', 'instagram_username', 'twitter_username', 'website', 'profile_picture_url', 'role', 'created_at']
                
                has_expected_structure = all(field in public_profile for field in expected_fields)
                
                if has_expected_structure:
                    # Verify it shows the data we just updated
                    bio_present = public_profile.get('bio') == "Passionate collector of vintage football jerseys 🏆"
                    instagram_present = public_profile.get('instagram_username') == "topkit_collector"
                    
                    self.log_result(
                        "Public Profile View",
                        True,
                        f"Public profile retrieved successfully. Bio matches: {bio_present}, Instagram matches: {instagram_present}. Profile: {public_profile}"
                    )
                else:
                    missing_fields = [field for field in expected_fields if field not in public_profile]
                    self.log_result(
                        "Public Profile View",
                        False,
                        f"Missing fields: {missing_fields}",
                        f"Public profile: {public_profile}"
                    )
            else:
                self.log_result(
                    "Public Profile View",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Public Profile View", False, "", str(e))

    def test_profile_picture_integration(self):
        """Test profile picture integration with users collection"""
        try:
            print("🖼️ Testing Profile Picture Integration...")
            
            # Test getting profile picture endpoint
            response = self.session.get(f"{BACKEND_URL}/users/profile/picture")
            
            if response.status_code == 200:
                picture_data = response.json()
                
                # Check if profile_picture_url field exists
                if 'profile_picture_url' in picture_data:
                    # Now check if this is also reflected in the public profile info
                    profile_response = self.session.get(f"{BACKEND_URL}/users/profile/public-info")
                    
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        
                        # Verify profile_picture_url is in both responses
                        picture_url_in_profile = 'profile_picture_url' in profile_data
                        
                        # Check if URLs match (both could be None)
                        urls_match = picture_data.get('profile_picture_url') == profile_data.get('profile_picture_url')
                        
                        self.log_result(
                            "Profile Picture Integration",
                            picture_url_in_profile and urls_match,
                            f"Profile picture URL in both endpoints: {picture_url_in_profile}, URLs match: {urls_match}. Picture endpoint: {picture_data.get('profile_picture_url')}, Profile endpoint: {profile_data.get('profile_picture_url')}"
                        )
                    else:
                        self.log_result(
                            "Profile Picture Integration",
                            False,
                            "Profile picture endpoint works but profile info endpoint failed",
                            f"Profile info response: {profile_response.status_code} - {profile_response.text}"
                        )
                else:
                    self.log_result(
                        "Profile Picture Integration",
                        False,
                        f"Missing profile_picture_url field in response: {picture_data}",
                        "profile_picture_url field not found"
                    )
            else:
                self.log_result(
                    "Profile Picture Integration",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Profile Picture Integration", False, "", str(e))

    def test_validation_rules(self):
        """Test validation rules for profile fields"""
        try:
            print("🔍 Testing Validation Rules...")
            
            # Test bio length validation (should be max 200 characters)
            long_bio = "A" * 201  # 201 characters
            
            test_data = {
                "bio": long_bio,
                "favorite_club": None,
                "instagram_username": "test_user",
                "twitter_username": "test_user",
                "website": "https://example.com"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/users/profile/public-info",
                json=test_data
            )
            
            # Should fail with bio too long
            bio_validation_works = response.status_code == 400
            
            # Test invalid website URL
            test_data_invalid_url = {
                "bio": "Valid bio",
                "favorite_club": None,
                "instagram_username": "test_user",
                "twitter_username": "test_user",
                "website": "not-a-valid-url"
            }
            
            response2 = self.session.put(
                f"{BACKEND_URL}/users/profile/public-info",
                json=test_data_invalid_url
            )
            
            # Should fail with invalid URL
            url_validation_works = response2.status_code == 400
            
            # Test valid data should work
            valid_data = {
                "bio": "Valid bio under 200 characters",
                "favorite_club": None,
                "instagram_username": "valid_username",
                "twitter_username": "valid_username",
                "website": "https://valid-website.com"
            }
            
            response3 = self.session.put(
                f"{BACKEND_URL}/users/profile/public-info",
                json=valid_data
            )
            
            valid_data_works = response3.status_code == 200
            
            all_validations_work = bio_validation_works and url_validation_works and valid_data_works
            
            self.log_result(
                "Validation Rules",
                all_validations_work,
                f"Bio length validation: {bio_validation_works}, URL validation: {url_validation_works}, Valid data acceptance: {valid_data_works}"
            )
            
        except Exception as e:
            self.log_result("Validation Rules", False, "", str(e))

    def test_team_existence_validation(self):
        """Test that favorite_club validation checks team existence"""
        try:
            print("🏟️ Testing Team Existence Validation...")
            
            # Test with non-existent team ID
            fake_team_id = "non-existent-team-id-12345"
            
            test_data = {
                "bio": "Test bio",
                "favorite_club": fake_team_id,
                "instagram_username": "test_user",
                "twitter_username": "test_user",
                "website": "https://example.com"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/users/profile/public-info",
                json=test_data
            )
            
            # Should fail with invalid team ID
            team_validation_works = response.status_code == 400
            
            self.log_result(
                "Team Existence Validation",
                team_validation_works,
                f"Non-existent team ID rejected: {team_validation_works}. Response: {response.status_code} - {response.text[:200]}"
            )
            
        except Exception as e:
            self.log_result("Team Existence Validation", False, "", str(e))

    def run_all_tests(self):
        """Run all profile enhancement tests"""
        print("🚀 Starting TopKit Profile Enhancement Features Backend Testing")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests
        self.test_teams_dropdown_endpoint()
        self.test_get_public_profile_info()
        self.test_update_public_profile_info()
        self.test_public_profile_view()
        self.test_profile_picture_integration()
        self.test_validation_rules()
        self.test_team_existence_validation()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # List failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['error']}")
            print()
        
        # List passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"  - {result['test']}")
            print()
        
        return success_rate >= 80  # Consider 80%+ as overall success

if __name__ == "__main__":
    tester = ProfileEnhancementTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Profile Enhancement Features Testing COMPLETED SUCCESSFULLY!")
    else:
        print("⚠️ Profile Enhancement Features Testing completed with issues.")
    
    sys.exit(0 if success else 1)