#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING - CRITICAL ISSUES INVESTIGATION
Testing all critical backend issues reported in the review request:

1. Reference Kit Creation Issue - Master Kits not appearing in dropdown
2. Admin Dashboard Validation System - "Error updating settings" message  
3. Image Upload System Testing across all categories
4. Navigation Implementation - Master Kit creation navigation

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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-collection-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
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
                self.admin_user_id = data.get('user', {}).get('id')
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
                self.user_user_id = data.get('user', {}).get('id')
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

    def test_admin_settings_system(self):
        """Test Admin Dashboard Settings System - Critical Issue #2"""
        if not self.admin_token:
            self.log_result("Admin Settings Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test GET admin settings
            response = requests.get(f"{API_BASE}/admin/settings", headers=headers)
            if response.status_code != 200:
                self.log_result("Admin Settings GET", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            current_settings = response.json()
            self.log_result("Admin Settings GET", True, f"Retrieved settings: {current_settings}")
            
            # Test PUT admin settings - This is where the "Error updating settings" occurs
            test_settings = {
                "auto_approval_enabled": not current_settings.get("auto_approval_enabled", True),
                "admin_notifications": True,
                "community_voting_enabled": True
            }
            
            response = requests.put(f"{API_BASE}/admin/settings", json=test_settings, headers=headers)
            if response.status_code != 200:
                self.log_result("Admin Settings UPDATE", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            self.log_result("Admin Settings UPDATE", True, f"Settings updated successfully: {test_settings}")
            
            # Verify settings were actually updated
            response = requests.get(f"{API_BASE}/admin/settings", headers=headers)
            if response.status_code == 200:
                updated_settings = response.json()
                if updated_settings.get("auto_approval_enabled") == test_settings["auto_approval_enabled"]:
                    self.log_result("Admin Settings VERIFICATION", True, "Settings persistence verified")
                else:
                    self.log_result("Admin Settings VERIFICATION", False, "", "Settings not persisted correctly")
                    return False
            
            return True
            
        except Exception as e:
            self.log_result("Admin Settings Test", False, "", str(e))
            return False

    def test_master_kit_dropdown_population(self):
        """Test Master Kit Dropdown Population - Critical Issue #1"""
        if not self.admin_token:
            self.log_result("Master Kit Dropdown Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # First, get available teams for Master Kit creation
            response = requests.get(f"{API_BASE}/teams", headers=headers)
            if response.status_code != 200:
                self.log_result("Teams Endpoint", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            teams = response.json()
            self.log_result("Teams Endpoint", True, f"Found {len(teams)} teams available")
            
            if not teams:
                self.log_result("Master Kit Dropdown Test", False, "", "No teams available for Master Kit creation")
                return False
            
            # Get available brands
            response = requests.get(f"{API_BASE}/brands", headers=headers)
            if response.status_code != 200:
                self.log_result("Brands Endpoint", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            brands = response.json()
            self.log_result("Brands Endpoint", True, f"Found {len(brands)} brands available")
            
            # Test Master Kit creation to verify dropdown data is accessible
            if teams and brands:
                team_id = teams[0].get('id')
                brand_id = brands[0].get('id')
                
                master_kit_data = {
                    "team_id": team_id,
                    "brand_id": brand_id,
                    "season": "2024-25",
                    "jersey_type": "home",
                    "kit_type": "home",
                    "model": "authentic",
                    "primary_color": "blue",
                    "secondary_colors": ["white"]
                }
                
                response = requests.post(f"{API_BASE}/master-kits", json=master_kit_data, headers=headers)
                if response.status_code in [200, 201]:
                    created_kit = response.json()
                    self.log_result("Master Kit Creation", True, f"Master Kit created: {created_kit.get('topkit_reference', 'Unknown')}")
                else:
                    self.log_result("Master Kit Creation", False, "", f"HTTP {response.status_code}: {response.text}")
                    return False
            
            # Now test the dropdown population for Reference Kit creation
            response = requests.get(f"{API_BASE}/master-kits", headers=headers)
            if response.status_code != 200:
                self.log_result("Master Kits Dropdown", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            master_kits = response.json()
            self.log_result("Master Kits Dropdown", True, f"Found {len(master_kits)} Master Kits for dropdown")
            
            # Test team-specific Master Kit filtering (this is likely where the dropdown issue occurs)
            if teams:
                team_id = teams[0].get('id')
                response = requests.get(f"{API_BASE}/master-kits?team_id={team_id}", headers=headers)
                if response.status_code == 200:
                    team_master_kits = response.json()
                    self.log_result("Team Master Kits Filter", True, f"Found {len(team_master_kits)} Master Kits for team {teams[0].get('name', 'Unknown')}")
                else:
                    self.log_result("Team Master Kits Filter", False, "", f"HTTP {response.status_code}: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_result("Master Kit Dropdown Test", False, "", str(e))
            return False

    def test_form_dependency_endpoints(self):
        """Test form dependency endpoints that populate dropdowns"""
        if not self.admin_token:
            self.log_result("Form Dependencies Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test competitions by type endpoint
            response = requests.get(f"{API_BASE}/form-dependencies/competitions-by-type", headers=headers)
            if response.status_code == 200:
                competitions_by_type = response.json()
                self.log_result("Competitions By Type", True, f"Found {len(competitions_by_type)} competition types")
            else:
                self.log_result("Competitions By Type", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test teams by competition endpoint
            response = requests.get(f"{API_BASE}/competitions", headers=headers)
            if response.status_code == 200:
                competitions = response.json()
                if competitions:
                    comp_id = competitions[0].get('id')
                    response = requests.get(f"{API_BASE}/form-dependencies/teams-by-competition/{comp_id}", headers=headers)
                    if response.status_code == 200:
                        teams_by_comp = response.json()
                        self.log_result("Teams By Competition", True, f"Found {len(teams_by_comp)} teams for competition")
                    else:
                        self.log_result("Teams By Competition", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test master kits by team endpoint
            response = requests.get(f"{API_BASE}/teams", headers=headers)
            if response.status_code == 200:
                teams = response.json()
                if teams:
                    team_id = teams[0].get('id')
                    response = requests.get(f"{API_BASE}/form-dependencies/master-kits-by-team/{team_id}", headers=headers)
                    if response.status_code == 200:
                        master_kits_by_team = response.json()
                        self.log_result("Master Kits By Team", True, f"Found {len(master_kits_by_team)} master kits for team")
                    else:
                        self.log_result("Master Kits By Team", False, "", f"HTTP {response.status_code}: {response.text}")
            
            return True
            
        except Exception as e:
            self.log_result("Form Dependencies Test", False, "", str(e))
            return False

    def test_image_upload_system(self):
        """Test Image Upload System - Critical Issue #3"""
        if not self.admin_token:
            self.log_result("Image Upload Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create a simple test image (1x1 pixel PNG in base64)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        try:
            # Test 1: Team Logo Upload
            team_data = {
                "name": f"Test Team {uuid.uuid4().hex[:8]}",
                "country": "France",
                "city": "Paris",
                "logo_image": f"data:image/png;base64,{test_image_base64}"
            }
            
            response = requests.post(f"{API_BASE}/teams", json=team_data, headers=headers)
            if response.status_code in [200, 201]:
                team = response.json()
                self.log_result("Team Logo Upload", True, f"Team created with logo: {team.get('name')}")
            else:
                self.log_result("Team Logo Upload", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test 2: Brand Logo Upload
            brand_data = {
                "name": f"Test Brand {uuid.uuid4().hex[:8]}",
                "country": "France",
                "logo_image": f"data:image/png;base64,{test_image_base64}"
            }
            
            response = requests.post(f"{API_BASE}/brands", json=brand_data, headers=headers)
            if response.status_code in [200, 201]:
                brand = response.json()
                self.log_result("Brand Logo Upload", True, f"Brand created with logo: {brand.get('name')}")
            else:
                self.log_result("Brand Logo Upload", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test 3: Competition Logo Upload
            competition_data = {
                "competition_name": f"Test Competition {uuid.uuid4().hex[:8]}",
                "type": "National league",
                "country": "France",
                "logo_image": f"data:image/png;base64,{test_image_base64}"
            }
            
            response = requests.post(f"{API_BASE}/competitions", json=competition_data, headers=headers)
            if response.status_code in [200, 201]:
                competition = response.json()
                self.log_result("Competition Logo Upload", True, f"Competition created with logo: {competition.get('competition_name')}")
            else:
                self.log_result("Competition Logo Upload", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test 4: Player Photo Upload
            player_data = {
                "name": f"Test Player {uuid.uuid4().hex[:8]}",
                "nationality": "France",
                "position": "Forward",
                "photo_image": f"data:image/png;base64,{test_image_base64}"
            }
            
            response = requests.post(f"{API_BASE}/players", json=player_data, headers=headers)
            if response.status_code in [200, 201]:
                player = response.json()
                self.log_result("Player Photo Upload", True, f"Player created with photo: {player.get('name')}")
            else:
                self.log_result("Player Photo Upload", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test 5: Reference Kit Jersey Image Upload
            # First get teams and brands for reference kit creation
            teams_response = requests.get(f"{API_BASE}/teams", headers=headers)
            brands_response = requests.get(f"{API_BASE}/brands", headers=headers)
            
            if teams_response.status_code == 200 and brands_response.status_code == 200:
                teams = teams_response.json()
                brands = brands_response.json()
                
                if teams and brands:
                    # Create a master kit first
                    master_kit_data = {
                        "team_id": teams[0].get('id'),
                        "brand_id": brands[0].get('id'),
                        "season": "2024-25",
                        "jersey_type": "home",
                        "kit_type": "jersey",
                        "model": "authentic",
                        "primary_color": "red"
                    }
                    
                    mk_response = requests.post(f"{API_BASE}/master-kits", json=master_kit_data, headers=headers)
                    if mk_response.status_code in [200, 201]:
                        master_kit = mk_response.json()
                        
                        # Now create reference kit with image
                        ref_kit_data = {
                            "master_kit_id": master_kit.get('id'),
                            "player_name": "Test Player",
                            "player_number": "10",
                            "jersey_image": f"data:image/png;base64,{test_image_base64}"
                        }
                        
                        response = requests.post(f"{API_BASE}/reference-kits", json=ref_kit_data, headers=headers)
                        if response.status_code in [200, 201]:
                            ref_kit = response.json()
                            self.log_result("Reference Kit Image Upload", True, f"Reference Kit created with image: {ref_kit.get('topkit_reference')}")
                        else:
                            self.log_result("Reference Kit Image Upload", False, "", f"HTTP {response.status_code}: {response.text}")
            
            return True
            
        except Exception as e:
            self.log_result("Image Upload Test", False, "", str(e))
            return False

    def test_navigation_implementation(self):
        """Test Navigation Implementation - Critical Issue #4"""
        if not self.admin_token:
            self.log_result("Navigation Test", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test the navigation flow: Reference Kit form → Master Kit creation
            # This tests if the "Create New Master Kit" navigation works
            
            # 1. Test if we can access the reference kit creation endpoint
            response = requests.get(f"{API_BASE}/master-kits", headers=headers)
            if response.status_code != 200:
                self.log_result("Master Kit Navigation Access", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            master_kits = response.json()
            self.log_result("Master Kit Navigation Access", True, f"Master Kit endpoint accessible with {len(master_kits)} items")
            
            # 2. Test if we can create a new master kit (simulating navigation from Reference Kit form)
            teams_response = requests.get(f"{API_BASE}/teams", headers=headers)
            brands_response = requests.get(f"{API_BASE}/brands", headers=headers)
            
            if teams_response.status_code == 200 and brands_response.status_code == 200:
                teams = teams_response.json()
                brands = brands_response.json()
                
                if teams and brands:
                    navigation_master_kit = {
                        "team_id": teams[0].get('id'),
                        "brand_id": brands[0].get('id'),
                        "season": "2024-25",
                        "jersey_type": "away",
                        "kit_type": "away",
                        "model": "replica",
                        "primary_color": "white",
                        "secondary_colors": ["blue"]
                    }
                    
                    response = requests.post(f"{API_BASE}/master-kits", json=navigation_master_kit, headers=headers)
                    if response.status_code in [200, 201]:
                        created_kit = response.json()
                        self.log_result("Master Kit Navigation Creation", True, f"Navigation Master Kit created: {created_kit.get('topkit_reference')}")
                        
                        # 3. Test if the newly created master kit appears in the dropdown
                        response = requests.get(f"{API_BASE}/master-kits", headers=headers)
                        if response.status_code == 200:
                            updated_master_kits = response.json()
                            if len(updated_master_kits) > len(master_kits):
                                self.log_result("Master Kit Dropdown Update", True, "New Master Kit appears in dropdown")
                            else:
                                self.log_result("Master Kit Dropdown Update", False, "", "New Master Kit not appearing in dropdown")
                                return False
                    else:
                        self.log_result("Master Kit Navigation Creation", False, "", f"HTTP {response.status_code}: {response.text}")
                        return False
            
            return True
            
        except Exception as e:
            self.log_result("Navigation Test", False, "", str(e))
            return False

    def test_complete_reference_kit_workflow(self):
        """Test complete Reference Kit creation workflow"""
        if not self.admin_token:
            self.log_result("Reference Kit Workflow", False, "", "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get master kits for reference kit creation
            response = requests.get(f"{API_BASE}/master-kits", headers=headers)
            if response.status_code != 200:
                self.log_result("Reference Kit Workflow - Master Kits", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
            master_kits = response.json()
            if not master_kits:
                self.log_result("Reference Kit Workflow", False, "", "No Master Kits available for Reference Kit creation")
                return False
                
            self.log_result("Reference Kit Workflow - Master Kits", True, f"Found {len(master_kits)} Master Kits available")
            
            # Create a reference kit
            master_kit_id = master_kits[0].get('id')
            ref_kit_data = {
                "master_kit_id": master_kit_id,
                "player_name": "Workflow Test Player",
                "player_number": "99",
                "original_retail_price": 89.99,
                "available_sizes": ["S", "M", "L", "XL"]
            }
            
            response = requests.post(f"{API_BASE}/reference-kits", json=ref_kit_data, headers=headers)
            if response.status_code in [200, 201]:
                ref_kit = response.json()
                self.log_result("Reference Kit Creation", True, f"Reference Kit created: {ref_kit.get('topkit_reference')}")
                
                # Verify it appears in vestiaire
                response = requests.get(f"{API_BASE}/vestiaire", headers=headers)
                if response.status_code == 200:
                    vestiaire_items = response.json()
                    ref_kit_found = any(item.get('topkit_reference') == ref_kit.get('topkit_reference') for item in vestiaire_items)
                    if ref_kit_found:
                        self.log_result("Reference Kit in Vestiaire", True, "Reference Kit appears in vestiaire")
                    else:
                        self.log_result("Reference Kit in Vestiaire", False, "", "Reference Kit not found in vestiaire")
                else:
                    self.log_result("Vestiaire Access", False, "", f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_result("Reference Kit Creation", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Reference Kit Workflow", False, "", str(e))
            return False

    def run_all_tests(self):
        """Run all critical backend tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING - CRITICAL ISSUES INVESTIGATION")
        print("=" * 80)
        
        # Authentication Tests
        print("\n📋 AUTHENTICATION TESTS")
        print("-" * 40)
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        
        if not admin_auth:
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Critical Issue Tests
        print("\n🔥 CRITICAL ISSUE TESTS")
        print("-" * 40)
        
        # Issue #1: Reference Kit Creation - Master Kit Dropdown Population
        print("\n1️⃣ TESTING: Master Kit Dropdown Population Issue")
        self.test_master_kit_dropdown_population()
        self.test_form_dependency_endpoints()
        
        # Issue #2: Admin Dashboard Validation System
        print("\n2️⃣ TESTING: Admin Dashboard Settings Validation")
        self.test_admin_settings_system()
        
        # Issue #3: Image Upload System
        print("\n3️⃣ TESTING: Image Upload System Across All Categories")
        self.test_image_upload_system()
        
        # Issue #4: Navigation Implementation
        print("\n4️⃣ TESTING: Master Kit Creation Navigation")
        self.test_navigation_implementation()
        
        # Complete Workflow Test
        print("\n🔄 COMPLETE WORKFLOW TESTS")
        print("-" * 40)
        self.test_complete_reference_kit_workflow()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['error']}")
        
        print(f"\n🎯 CRITICAL ISSUES STATUS:")
        
        # Analyze results for each critical issue
        master_kit_tests = [r for r in self.test_results if 'Master Kit' in r['test'] or 'Form Dependencies' in r['test']]
        master_kit_success = all(r['success'] for r in master_kit_tests)
        print(f"   1. Master Kit Dropdown Population: {'✅ RESOLVED' if master_kit_success else '❌ ISSUE PERSISTS'}")
        
        admin_tests = [r for r in self.test_results if 'Admin Settings' in r['test']]
        admin_success = all(r['success'] for r in admin_tests)
        print(f"   2. Admin Dashboard Settings: {'✅ RESOLVED' if admin_success else '❌ ISSUE PERSISTS'}")
        
        image_tests = [r for r in self.test_results if 'Upload' in r['test'] and 'Image' in r['test']]
        image_success = all(r['success'] for r in image_tests)
        print(f"   3. Image Upload System: {'✅ RESOLVED' if image_success else '❌ ISSUE PERSISTS'}")
        
        nav_tests = [r for r in self.test_results if 'Navigation' in r['test']]
        nav_success = all(r['success'] for r in nav_tests)
        print(f"   4. Navigation Implementation: {'✅ RESOLVED' if nav_success else '❌ ISSUE PERSISTS'}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 BACKEND TESTING COMPLETED SUCCESSFULLY!")
        print(f"All critical issues have been investigated and most functionality is working correctly.")
    else:
        print(f"\n⚠️ BACKEND TESTING COMPLETED WITH ISSUES!")
        print(f"Some critical issues require attention. Check the failed tests above for details.")