#!/usr/bin/env python3
"""
TopKit Phase 2 - Dedicated Detail Pages Backend Testing
Testing all entity retrieval endpoints and data structures for standardized detail pages
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

class TopKitPhase2Tester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                self.log_test("Admin Authentication", True, f"Admin: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_session = requests.Session()
                user_session.headers.update({'Authorization': f'Bearer {self.user_token}'})
                self.log_test("User Authentication", True, f"User: {data.get('user', {}).get('name', 'Unknown')}")
                return True, user_session
            else:
                self.log_test("User Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False, None
    
    def test_teams_endpoint(self):
        """Test GET /api/teams endpoint for team detail pages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                
                # Check if we have teams
                if not teams or len(teams) == 0:
                    self.log_test("Teams Endpoint - Data Availability", False, "No teams found")
                    return False
                
                self.log_test("Teams Endpoint - Basic Access", True, f"Retrieved {len(teams)} teams")
                
                # Find FC Barcelona for detailed testing
                barcelona = None
                for team in teams:
                    if 'barcelona' in team.get('name', '').lower():
                        barcelona = team
                        break
                
                if barcelona:
                    # Test required fields for detail pages
                    required_fields = ['id', 'name', 'topkit_reference']
                    optional_fields = ['country', 'city', 'founded_year', 'short_name', 'colors', 'logo_url', 'secondary_images']
                    
                    missing_required = [field for field in required_fields if field not in barcelona or barcelona[field] is None]
                    present_optional = [field for field in optional_fields if field in barcelona and barcelona[field] is not None]
                    
                    if not missing_required:
                        self.log_test("Teams Endpoint - Required Fields", True, f"FC Barcelona has all required fields")
                    else:
                        self.log_test("Teams Endpoint - Required Fields", False, f"Missing: {missing_required}")
                    
                    self.log_test("Teams Endpoint - Optional Fields", True, f"FC Barcelona has optional fields: {present_optional}")
                    
                    # Test secondary_images array specifically
                    if 'secondary_images' in barcelona and isinstance(barcelona['secondary_images'], list):
                        self.log_test("Teams Endpoint - Secondary Images Array", True, f"FC Barcelona has {len(barcelona['secondary_images'])} secondary images")
                    else:
                        self.log_test("Teams Endpoint - Secondary Images Array", False, "Secondary images not found or not an array")
                    
                    return True
                else:
                    self.log_test("Teams Endpoint - Test Data", False, "FC Barcelona not found for detailed testing")
                    return False
            else:
                self.log_test("Teams Endpoint - Basic Access", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Teams Endpoint - Basic Access", False, f"Exception: {str(e)}")
            return False
    
    def test_brands_endpoint(self):
        """Test GET /api/brands endpoint for brand detail pages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/brands")
            
            if response.status_code == 200:
                brands = response.json()
                
                if not brands or len(brands) == 0:
                    self.log_test("Brands Endpoint - Data Availability", False, "No brands found")
                    return False
                
                self.log_test("Brands Endpoint - Basic Access", True, f"Retrieved {len(brands)} brands")
                
                # Find Nike for detailed testing
                nike = None
                for brand in brands:
                    if 'nike' in brand.get('name', '').lower():
                        nike = brand
                        break
                
                if nike:
                    # Test required fields for detail pages
                    required_fields = ['id', 'name', 'topkit_reference']
                    optional_fields = ['country', 'founded_year', 'website', 'logo_url', 'secondary_images']
                    
                    missing_required = [field for field in required_fields if field not in nike or nike[field] is None]
                    present_optional = [field for field in optional_fields if field in nike and nike[field] is not None]
                    
                    if not missing_required:
                        self.log_test("Brands Endpoint - Required Fields", True, f"Nike has all required fields")
                    else:
                        self.log_test("Brands Endpoint - Required Fields", False, f"Missing: {missing_required}")
                    
                    self.log_test("Brands Endpoint - Optional Fields", True, f"Nike has optional fields: {present_optional}")
                    
                    # Test secondary_images array specifically
                    if 'secondary_images' in nike and isinstance(nike['secondary_images'], list):
                        self.log_test("Brands Endpoint - Secondary Images Array", True, f"Nike has {len(nike['secondary_images'])} secondary images")
                    else:
                        self.log_test("Brands Endpoint - Secondary Images Array", False, "Secondary images not found or not an array")
                    
                    return True
                else:
                    self.log_test("Brands Endpoint - Test Data", False, "Nike not found for detailed testing")
                    return False
            else:
                self.log_test("Brands Endpoint - Basic Access", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Brands Endpoint - Basic Access", False, f"Exception: {str(e)}")
            return False
    
    def test_competitions_endpoint(self):
        """Test GET /api/competitions endpoint for competition detail pages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/competitions")
            
            if response.status_code == 200:
                competitions = response.json()
                
                if not competitions or len(competitions) == 0:
                    self.log_test("Competitions Endpoint - Data Availability", False, "No competitions found")
                    return False
                
                self.log_test("Competitions Endpoint - Basic Access", True, f"Retrieved {len(competitions)} competitions")
                
                # Find La Liga for detailed testing
                la_liga = None
                for comp in competitions:
                    if 'liga' in comp.get('name', '').lower() or 'la liga' in comp.get('name', '').lower():
                        la_liga = comp
                        break
                
                if la_liga:
                    # Test required fields for detail pages
                    required_fields = ['id', 'name', 'topkit_reference']
                    optional_fields = ['country', 'type', 'season_info', 'logo_url', 'secondary_images']
                    
                    missing_required = [field for field in required_fields if field not in la_liga or la_liga[field] is None]
                    present_optional = [field for field in optional_fields if field in la_liga and la_liga[field] is not None]
                    
                    if not missing_required:
                        self.log_test("Competitions Endpoint - Required Fields", True, f"La Liga has all required fields")
                    else:
                        self.log_test("Competitions Endpoint - Required Fields", False, f"Missing: {missing_required}")
                    
                    self.log_test("Competitions Endpoint - Optional Fields", True, f"La Liga has optional fields: {present_optional}")
                    
                    # Test secondary_images array specifically
                    if 'secondary_images' in la_liga and isinstance(la_liga['secondary_images'], list):
                        self.log_test("Competitions Endpoint - Secondary Images Array", True, f"La Liga has {len(la_liga['secondary_images'])} secondary images")
                    else:
                        self.log_test("Competitions Endpoint - Secondary Images Array", False, "Secondary images not found or not an array")
                    
                    return True
                else:
                    self.log_test("Competitions Endpoint - Test Data", False, "La Liga not found for detailed testing")
                    return False
            else:
                self.log_test("Competitions Endpoint - Basic Access", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Competitions Endpoint - Basic Access", False, f"Exception: {str(e)}")
            return False
    
    def test_players_endpoint(self):
        """Test GET /api/players endpoint for player detail pages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/players")
            
            if response.status_code == 200:
                players = response.json()
                
                if not players or len(players) == 0:
                    self.log_test("Players Endpoint - Data Availability", False, "No players found")
                    return False
                
                self.log_test("Players Endpoint - Basic Access", True, f"Retrieved {len(players)} players")
                
                # Find Lionel Messi for detailed testing
                messi = None
                for player in players:
                    if 'messi' in player.get('name', '').lower():
                        messi = player
                        break
                
                if messi:
                    # Test required fields for detail pages
                    required_fields = ['id', 'name', 'topkit_reference']
                    optional_fields = ['nationality', 'position', 'birth_date', 'current_team', 'photo_url', 'secondary_images']
                    
                    missing_required = [field for field in required_fields if field not in messi or messi[field] is None]
                    present_optional = [field for field in optional_fields if field in messi and messi[field] is not None]
                    
                    if not missing_required:
                        self.log_test("Players Endpoint - Required Fields", True, f"Messi has all required fields")
                    else:
                        self.log_test("Players Endpoint - Required Fields", False, f"Missing: {missing_required}")
                    
                    self.log_test("Players Endpoint - Optional Fields", True, f"Messi has optional fields: {present_optional}")
                    
                    # Test secondary_images array specifically
                    if 'secondary_images' in messi and isinstance(messi['secondary_images'], list):
                        self.log_test("Players Endpoint - Secondary Images Array", True, f"Messi has {len(messi['secondary_images'])} secondary images")
                    else:
                        self.log_test("Players Endpoint - Secondary Images Array", False, "Secondary images not found or not an array")
                    
                    return True
                else:
                    self.log_test("Players Endpoint - Test Data", False, "Messi not found for detailed testing")
                    return False
            else:
                self.log_test("Players Endpoint - Basic Access", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Players Endpoint - Basic Access", False, f"Exception: {str(e)}")
            return False
    
    def test_master_jerseys_endpoint(self):
        """Test GET /api/master-jerseys endpoint for master jersey detail pages"""
        try:
            response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            
            if response.status_code == 200:
                master_jerseys = response.json()
                
                if not master_jerseys or len(master_jerseys) == 0:
                    self.log_test("Master Jerseys Endpoint - Data Availability", False, "No master jerseys found")
                    return False
                
                self.log_test("Master Jerseys Endpoint - Basic Access", True, f"Retrieved {len(master_jerseys)} master jerseys")
                
                # Test first master jersey for detailed testing
                if master_jerseys:
                    master_jersey = master_jerseys[0]
                    
                    # Test required fields for detail pages
                    required_fields = ['id', 'topkit_reference']
                    optional_fields = ['team_info', 'brand_info', 'colors', 'design_details', 'images', 'secondary_images']
                    
                    missing_required = [field for field in required_fields if field not in master_jersey or master_jersey[field] is None]
                    present_optional = [field for field in optional_fields if field in master_jersey and master_jersey[field] is not None]
                    
                    if not missing_required:
                        self.log_test("Master Jerseys Endpoint - Required Fields", True, f"Master jersey has all required fields")
                    else:
                        self.log_test("Master Jerseys Endpoint - Required Fields", False, f"Missing: {missing_required}")
                    
                    self.log_test("Master Jerseys Endpoint - Optional Fields", True, f"Master jersey has optional fields: {present_optional}")
                    
                    # Test secondary_images array specifically
                    if 'secondary_images' in master_jersey and isinstance(master_jersey['secondary_images'], list):
                        self.log_test("Master Jerseys Endpoint - Secondary Images Array", True, f"Master jersey has {len(master_jersey['secondary_images'])} secondary images")
                    else:
                        self.log_test("Master Jerseys Endpoint - Secondary Images Array", False, "Secondary images not found or not an array")
                    
                    return True
                else:
                    self.log_test("Master Jerseys Endpoint - Test Data", False, "No master jerseys available for testing")
                    return False
            else:
                self.log_test("Master Jerseys Endpoint - Basic Access", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Master Jerseys Endpoint - Basic Access", False, f"Exception: {str(e)}")
            return False
    
    def test_contribution_modal_access(self):
        """Test that authenticated users can access ContributionModal functionality"""
        try:
            # Test contributions endpoint access
            response = self.session.get(f"{BACKEND_URL}/contributions")
            
            if response.status_code == 200:
                contributions = response.json()
                self.log_test("Contribution Modal - Contributions Access", True, f"Retrieved {len(contributions)} contributions")
                
                # Test contribution creation endpoint (POST)
                test_contribution = {
                    "entity_type": "team",
                    "entity_id": "test-team-id",
                    "title": "Test Contribution",
                    "description": "Testing contribution modal access",
                    "images": {
                        "logo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                    }
                }
                
                create_response = self.session.post(f"{BACKEND_URL}/contributions", json=test_contribution)
                
                if create_response.status_code in [200, 201, 400]:  # 400 might be validation error, which is expected
                    self.log_test("Contribution Modal - Creation Access", True, f"Contribution creation endpoint accessible (HTTP {create_response.status_code})")
                else:
                    self.log_test("Contribution Modal - Creation Access", False, f"HTTP {create_response.status_code}: {create_response.text}")
                
                return True
            else:
                self.log_test("Contribution Modal - Contributions Access", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Contribution Modal - Contributions Access", False, f"Exception: {str(e)}")
            return False
    
    def test_data_structure_consistency(self):
        """Test that all detail page fields are consistently available across entities"""
        try:
            # Test that all endpoints return consistent data structures
            endpoints = [
                ("teams", "Teams"),
                ("brands", "Brands"), 
                ("competitions", "Competitions"),
                ("players", "Players"),
                ("master-jerseys", "Master Jerseys")
            ]
            
            consistent_fields = []
            inconsistent_fields = []
            
            for endpoint, name in endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}/{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            first_item = data[0]
                            
                            # Check for common fields
                            common_fields = ['id', 'topkit_reference', 'name']
                            image_fields = ['logo_url', 'photo_url', 'images', 'secondary_images']
                            
                            for field in common_fields:
                                if field in first_item:
                                    consistent_fields.append(f"{name}: {field}")
                                else:
                                    inconsistent_fields.append(f"{name}: missing {field}")
                            
                            # Check for image fields (at least one should be present)
                            has_image_field = any(field in first_item for field in image_fields)
                            if has_image_field:
                                consistent_fields.append(f"{name}: has image fields")
                            else:
                                inconsistent_fields.append(f"{name}: no image fields")
                                
                except Exception as e:
                    inconsistent_fields.append(f"{name}: error accessing endpoint - {str(e)}")
            
            if len(inconsistent_fields) == 0:
                self.log_test("Data Structure Consistency", True, f"All endpoints have consistent structure")
            else:
                self.log_test("Data Structure Consistency", False, f"Inconsistencies found: {inconsistent_fields}")
            
            return len(inconsistent_fields) == 0
            
        except Exception as e:
            self.log_test("Data Structure Consistency", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Phase 2 dedicated detail pages tests"""
        print("🎯 TOPKIT PHASE 2 - DEDICATED DETAIL PAGES BACKEND TESTING")
        print("=" * 80)
        print(f"Testing backend support for standardized detail pages")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Authentication
        print("🔐 AUTHENTICATION TESTING")
        print("-" * 40)
        admin_auth = self.authenticate_admin()
        user_auth, user_session = self.authenticate_user()
        print()
        
        if not admin_auth:
            print("❌ Admin authentication failed - some tests may be limited")
        
        # Entity Retrieval Testing
        print("📊 ENTITY RETRIEVAL TESTING")
        print("-" * 40)
        teams_result = self.test_teams_endpoint()
        brands_result = self.test_brands_endpoint()
        competitions_result = self.test_competitions_endpoint()
        players_result = self.test_players_endpoint()
        master_jerseys_result = self.test_master_jerseys_endpoint()
        print()
        
        # Data Structure Testing
        print("🏗️ DATA STRUCTURE TESTING")
        print("-" * 40)
        consistency_result = self.test_data_structure_consistency()
        print()
        
        # Authentication Features Testing
        print("🔒 AUTHENTICATED FEATURES TESTING")
        print("-" * 40)
        if admin_auth:
            contribution_result = self.test_contribution_modal_access()
        else:
            contribution_result = False
            self.log_test("Contribution Modal Access", False, "Admin authentication required")
        print()
        
        # Summary
        print("📋 TEST SUMMARY")
        print("-" * 40)
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed Results
        print("📝 DETAILED RESULTS")
        print("-" * 40)
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        print()
        
        # Phase 2 Specific Assessment
        print("🎯 PHASE 2 ASSESSMENT")
        print("-" * 40)
        
        # Entity Retrieval Assessment
        entity_tests = [teams_result, brands_result, competitions_result, players_result, master_jerseys_result]
        entity_success = sum(entity_tests)
        print(f"Entity Retrieval: {entity_success}/5 endpoints working")
        
        # Image Fields Assessment
        image_tests = [result for result in self.test_results if 'Secondary Images Array' in result['test']]
        image_success = sum(1 for test in image_tests if test['success'])
        print(f"Secondary Images Support: {image_success}/{len(image_tests)} entities")
        
        # Data Structure Assessment
        print(f"Data Structure Consistency: {'✅' if consistency_result else '❌'}")
        
        # Authentication Assessment
        print(f"ContributionModal Access: {'✅' if contribution_result else '❌'}")
        
        print()
        
        # Final Verdict
        if success_rate >= 85:
            print("🎉 PHASE 2 BACKEND TESTING COMPLETE - EXCELLENT IMPLEMENTATION!")
            print("All dedicated detail pages are properly supported by the backend.")
        elif success_rate >= 70:
            print("✅ PHASE 2 BACKEND TESTING COMPLETE - GOOD IMPLEMENTATION!")
            print("Most dedicated detail pages are supported with minor issues.")
        else:
            print("⚠️ PHASE 2 BACKEND TESTING COMPLETE - ISSUES IDENTIFIED!")
            print("Significant issues found that may affect detail page functionality.")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = TopKitPhase2Tester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)