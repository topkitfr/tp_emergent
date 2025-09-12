#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Profile Settings API Testing
Testing the new profile settings API update with name and picture fields
"""

import requests
import json
import uuid
import base64
from datetime import datetime
import time

# Configuration
BASE_URL = "https://kit-collection-5.preview.emergentagent.com/api"

class ProfileSettingsAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def create_test_user(self):
        """Create a test user for profile settings testing"""
        try:
            unique_email = f"profiletest_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "Profile Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("Create Test User", "PASS", f"User created: {unique_email}")
                    return True
                else:
                    self.log_test("Create Test User", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Create Test User", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Test User", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_initial_profile(self):
        """Test getting initial profile data"""
        try:
            if not self.auth_token:
                self.log_test("Get Initial Profile", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                if "user" in profile:
                    user_data = profile["user"]
                    initial_name = user_data.get("name")
                    initial_picture = user_data.get("picture")
                    
                    self.log_test("Get Initial Profile", "PASS", 
                                f"Initial profile - Name: '{initial_name}', Picture: {initial_picture}")
                    return True
                else:
                    self.log_test("Get Initial Profile", "FAIL", "Missing user data in response")
                    return False
            else:
                self.log_test("Get Initial Profile", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Initial Profile", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_update_name_only(self):
        """Test updating name only via PUT /api/profile/settings"""
        try:
            if not self.auth_token:
                self.log_test("Update Name Only", "FAIL", "No auth token available")
                return False
            
            new_name = "Updated Profile Name"
            payload = {
                "name": new_name
            }
            
            response = self.session.put(f"{self.base_url}/profile/settings", json=payload)
            
            if response.status_code == 200:
                # Verify the update by getting profile
                profile_response = self.session.get(f"{self.base_url}/profile")
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    updated_name = profile["user"].get("name")
                    
                    if updated_name == new_name:
                        self.log_test("Update Name Only", "PASS", 
                                    f"Name successfully updated to: '{updated_name}'")
                        return True
                    else:
                        self.log_test("Update Name Only", "FAIL", 
                                    f"Name not updated correctly. Expected: '{new_name}', Got: '{updated_name}'")
                        return False
                else:
                    self.log_test("Update Name Only", "FAIL", "Could not verify profile update")
                    return False
            else:
                self.log_test("Update Name Only", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Name Only", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_update_picture_only(self):
        """Test updating picture only via PUT /api/profile/settings"""
        try:
            if not self.auth_token:
                self.log_test("Update Picture Only", "FAIL", "No auth token available")
                return False
            
            # Create a simple base64 encoded image data (1x1 pixel PNG)
            base64_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
            
            payload = {
                "picture": base64_image
            }
            
            response = self.session.put(f"{self.base_url}/profile/settings", json=payload)
            
            if response.status_code == 200:
                # Verify the update by getting profile
                profile_response = self.session.get(f"{self.base_url}/profile")
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    updated_picture = profile["user"].get("picture")
                    
                    if updated_picture == base64_image:
                        self.log_test("Update Picture Only", "PASS", 
                                    f"Picture successfully updated (base64 data: {len(base64_image)} chars)")
                        return True
                    else:
                        self.log_test("Update Picture Only", "FAIL", 
                                    f"Picture not updated correctly. Expected length: {len(base64_image)}, Got: {len(updated_picture) if updated_picture else 0}")
                        return False
                else:
                    self.log_test("Update Picture Only", "FAIL", "Could not verify profile update")
                    return False
            else:
                self.log_test("Update Picture Only", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Picture Only", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_update_name_and_picture_together(self):
        """Test updating both name and picture together via PUT /api/profile/settings"""
        try:
            if not self.auth_token:
                self.log_test("Update Name and Picture Together", "FAIL", "No auth token available")
                return False
            
            new_name = "Complete Profile Update"
            # Different base64 image for this test
            base64_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFklEQVR42mNkYGBgYGBgYGBgYGBgYAAABQABDQottAAAAABJRU5ErkJggg=="
            
            payload = {
                "name": new_name,
                "picture": base64_image
            }
            
            response = self.session.put(f"{self.base_url}/profile/settings", json=payload)
            
            if response.status_code == 200:
                # Verify the update by getting profile
                profile_response = self.session.get(f"{self.base_url}/profile")
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    updated_name = profile["user"].get("name")
                    updated_picture = profile["user"].get("picture")
                    
                    name_correct = updated_name == new_name
                    picture_correct = updated_picture == base64_image
                    
                    if name_correct and picture_correct:
                        self.log_test("Update Name and Picture Together", "PASS", 
                                    f"Both fields updated - Name: '{updated_name}', Picture: {len(base64_image)} chars")
                        return True
                    else:
                        self.log_test("Update Name and Picture Together", "FAIL", 
                                    f"Update failed - Name correct: {name_correct}, Picture correct: {picture_correct}")
                        return False
                else:
                    self.log_test("Update Name and Picture Together", "FAIL", "Could not verify profile update")
                    return False
            else:
                self.log_test("Update Name and Picture Together", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Update Name and Picture Together", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_optional_fields_behavior(self):
        """Test that optional fields work correctly (can send empty payload)"""
        try:
            if not self.auth_token:
                self.log_test("Optional Fields Behavior", "FAIL", "No auth token available")
                return False
            
            # Get current profile state
            profile_response = self.session.get(f"{self.base_url}/profile")
            if profile_response.status_code != 200:
                self.log_test("Optional Fields Behavior", "FAIL", "Could not get current profile")
                return False
            
            current_profile = profile_response.json()["user"]
            current_name = current_profile.get("name")
            current_picture = current_profile.get("picture")
            
            # Send empty payload (should not change anything)
            empty_payload = {}
            
            response = self.session.put(f"{self.base_url}/profile/settings", json=empty_payload)
            
            if response.status_code == 200:
                # Verify nothing changed
                verify_response = self.session.get(f"{self.base_url}/profile")
                
                if verify_response.status_code == 200:
                    verify_profile = verify_response.json()["user"]
                    verify_name = verify_profile.get("name")
                    verify_picture = verify_profile.get("picture")
                    
                    if verify_name == current_name and verify_picture == current_picture:
                        self.log_test("Optional Fields Behavior", "PASS", 
                                    "Empty payload correctly preserved existing values")
                        return True
                    else:
                        self.log_test("Optional Fields Behavior", "FAIL", 
                                    "Empty payload unexpectedly changed profile values")
                        return False
                else:
                    self.log_test("Optional Fields Behavior", "FAIL", "Could not verify profile after empty update")
                    return False
            else:
                self.log_test("Optional Fields Behavior", "FAIL", f"Empty payload failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Optional Fields Behavior", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_profile_privacy_settings(self):
        """Test updating profile privacy settings"""
        try:
            if not self.auth_token:
                self.log_test("Profile Privacy Settings", "FAIL", "No auth token available")
                return False
            
            # Test setting profile to private
            payload = {
                "profile_privacy": "private"
            }
            
            response = self.session.put(f"{self.base_url}/profile/settings", json=payload)
            
            if response.status_code == 200:
                # Verify the update
                profile_response = self.session.get(f"{self.base_url}/profile")
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    privacy_setting = profile["user"].get("profile_privacy")
                    
                    if privacy_setting == "private":
                        # Test setting back to public
                        public_payload = {"profile_privacy": "public"}
                        public_response = self.session.put(f"{self.base_url}/profile/settings", json=public_payload)
                        
                        if public_response.status_code == 200:
                            self.log_test("Profile Privacy Settings", "PASS", 
                                        "Privacy settings updated successfully (private → public)")
                            return True
                        else:
                            self.log_test("Profile Privacy Settings", "FAIL", "Could not set back to public")
                            return False
                    else:
                        self.log_test("Profile Privacy Settings", "FAIL", 
                                    f"Privacy not updated correctly. Expected: 'private', Got: '{privacy_setting}'")
                        return False
                else:
                    self.log_test("Profile Privacy Settings", "FAIL", "Could not verify privacy update")
                    return False
            else:
                self.log_test("Profile Privacy Settings", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Profile Privacy Settings", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_value_visibility_setting(self):
        """Test updating show_collection_value setting"""
        try:
            if not self.auth_token:
                self.log_test("Collection Value Visibility", "FAIL", "No auth token available")
                return False
            
            # Test enabling collection value visibility
            payload = {
                "show_collection_value": True
            }
            
            response = self.session.put(f"{self.base_url}/profile/settings", json=payload)
            
            if response.status_code == 200:
                # Verify the update
                profile_response = self.session.get(f"{self.base_url}/profile")
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    show_value = profile["user"].get("show_collection_value")
                    
                    if show_value == True:
                        # Test disabling it
                        disable_payload = {"show_collection_value": False}
                        disable_response = self.session.put(f"{self.base_url}/profile/settings", json=disable_payload)
                        
                        if disable_response.status_code == 200:
                            self.log_test("Collection Value Visibility", "PASS", 
                                        "Collection value visibility updated successfully (True → False)")
                            return True
                        else:
                            self.log_test("Collection Value Visibility", "FAIL", "Could not disable collection value visibility")
                            return False
                    else:
                        self.log_test("Collection Value Visibility", "FAIL", 
                                    f"Setting not updated correctly. Expected: True, Got: {show_value}")
                        return False
                else:
                    self.log_test("Collection Value Visibility", "FAIL", "Could not verify setting update")
                    return False
            else:
                self.log_test("Collection Value Visibility", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Collection Value Visibility", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_create_jersey_functionality(self):
        """Test that jersey creation still works after profile updates"""
        try:
            if not self.auth_token:
                self.log_test("Jersey Creation Still Works", "FAIL", "No auth token available")
                return False
            
            payload = {
                "team": "Chelsea FC",
                "season": "2023-24",
                "player": "Enzo Fernandez",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Chelsea FC home jersey with Enzo Fernandez #8",
                "images": ["https://example.com/chelsea-enzo.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("team") == "Chelsea FC":
                    self.log_test("Jersey Creation Still Works", "PASS", 
                                f"Jersey created successfully: {data['team']} {data.get('player', 'N/A')}")
                    return True
                else:
                    self.log_test("Jersey Creation Still Works", "FAIL", "Invalid jersey data returned")
                    return False
            else:
                self.log_test("Jersey Creation Still Works", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Creation Still Works", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_management_still_works(self):
        """Test that collection management still works after profile updates"""
        try:
            if not self.auth_token:
                self.log_test("Collection Management Still Works", "FAIL", "No auth token available")
                return False
            
            # First create a jersey to add to collection
            jersey_payload = {
                "team": "Arsenal FC",
                "season": "2023-24",
                "player": "Bukayo Saka",
                "size": "M",
                "condition": "mint",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Arsenal FC home jersey with Bukayo Saka #7",
                "images": ["https://example.com/arsenal-saka.jpg"]
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if jersey_response.status_code != 200:
                self.log_test("Collection Management Still Works", "FAIL", "Could not create test jersey")
                return False
            
            jersey_id = jersey_response.json()["id"]
            
            # Add to collection
            collection_payload = {
                "jersey_id": jersey_id,
                "collection_type": "owned"
            }
            
            collection_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
            
            if collection_response.status_code == 200:
                # Verify it's in collection
                get_collection_response = self.session.get(f"{self.base_url}/collections/owned")
                
                if get_collection_response.status_code == 200:
                    collections = get_collection_response.json()
                    jersey_in_collection = any(item.get('jersey_id') == jersey_id for item in collections)
                    
                    if jersey_in_collection:
                        self.log_test("Collection Management Still Works", "PASS", 
                                    "Collection management working correctly after profile updates")
                        return True
                    else:
                        self.log_test("Collection Management Still Works", "FAIL", "Jersey not found in collection")
                        return False
                else:
                    self.log_test("Collection Management Still Works", "FAIL", "Could not retrieve collection")
                    return False
            else:
                self.log_test("Collection Management Still Works", "FAIL", f"Collection add failed: {collection_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Collection Management Still Works", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_authentication_flows_still_work(self):
        """Test that authentication flows still work after profile updates"""
        try:
            # Test creating a new user (registration flow)
            unique_email = f"authtest_{int(time.time())}@topkit.com"
            
            register_payload = {
                "email": unique_email,
                "password": "authtest123",
                "name": "Auth Test User"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code == 200:
                # Test login flow
                login_payload = {
                    "email": unique_email,
                    "password": "authtest123"
                }
                
                login_response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    if "token" in login_data and "user" in login_data:
                        self.log_test("Authentication Flows Still Work", "PASS", 
                                    "Registration and login flows working correctly")
                        return True
                    else:
                        self.log_test("Authentication Flows Still Work", "FAIL", "Invalid login response")
                        return False
                else:
                    self.log_test("Authentication Flows Still Work", "FAIL", f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.log_test("Authentication Flows Still Work", "FAIL", f"Registration failed: {register_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Flows Still Work", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all profile settings tests"""
        print("🎯 TOPKIT PROFILE SETTINGS API TESTING")
        print("=" * 60)
        print()
        
        tests_passed = 0
        total_tests = 0
        
        # Priority 1 - Profile Settings API (CRITICAL)
        print("🔥 PRIORITY 1 - PROFILE SETTINGS API (CRITICAL)")
        print("-" * 50)
        
        if self.create_test_user():
            total_tests += 1
            tests_passed += 1
        else:
            print("❌ Cannot continue without test user")
            return
        
        test_methods = [
            self.test_get_initial_profile,
            self.test_update_name_only,
            self.test_update_picture_only,
            self.test_update_name_and_picture_together,
            self.test_optional_fields_behavior,
            self.test_profile_privacy_settings,
            self.test_collection_value_visibility_setting
        ]
        
        for test_method in test_methods:
            total_tests += 1
            if test_method():
                tests_passed += 1
        
        print()
        print("🔧 PRIORITY 2 - EXISTING FUNCTIONALITY")
        print("-" * 50)
        
        existing_functionality_tests = [
            self.test_create_jersey_functionality,
            self.test_collection_management_still_works,
            self.test_authentication_flows_still_work
        ]
        
        for test_method in existing_functionality_tests:
            total_tests += 1
            if test_method():
                tests_passed += 1
        
        print()
        print("📊 FINAL RESULTS")
        print("=" * 60)
        success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"Tests Passed: {tests_passed}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT - Profile Settings API is working perfectly!")
        elif success_rate >= 75:
            print("✅ GOOD - Profile Settings API is mostly working with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE - Profile Settings API has some significant issues")
        else:
            print("❌ CRITICAL - Profile Settings API has major problems")
        
        return tests_passed, total_tests

def main():
    """Main test execution"""
    tester = ProfileSettingsAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()