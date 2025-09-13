#!/usr/bin/env python3
"""
TopKit Backend Deployment Verification Testing
Comprehensive testing to verify that deployment fixes didn't break existing functionality.

Testing Focus Areas:
1. Authentication System (login/logout, JWT tokens)
2. Database Operations (CRUD for all entities)
3. Critical API Endpoints
4. File Upload System
5. Form Dependencies
6. Error Handling

Admin Credentials: topkitfr@gmail.com / TopKitSecure789#
"""

import requests
import json
import base64
import os
import io
from datetime import datetime
from PIL import Image

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://topkit-debug-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class DeploymentVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.created_entities = {
            'teams': [],
            'brands': [],
            'competitions': [],
            'players': [],
            'master_jerseys': [],
            'reference_kits': [],
            'personal_kits': []
        }
        
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

    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*80)
        print("DEPLOYMENT VERIFICATION TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['error']}")
        
        print("="*80)

    # ==========================================
    # 1. AUTHENTICATION SYSTEM TESTING
    # ==========================================
    
    def test_authentication_system(self):
        """Test complete authentication system"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        print("-" * 50)
        
        # Test 1: Admin Login
        self.test_admin_login()
        
        # Test 2: JWT Token Validation
        self.test_jwt_token_validation()
        
        # Test 3: Protected Endpoint Access
        self.test_protected_endpoint_access()
        
        # Test 4: Invalid Credentials
        self.test_invalid_credentials()

    def test_admin_login(self):
        """Test admin login functionality"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                
                if self.admin_token and user_data.get('role') == 'admin':
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    self.log_result(
                        "Admin Login", 
                        True, 
                        f"Successfully authenticated admin. Token length: {len(self.admin_token)}, Role: {user_data.get('role')}"
                    )
                    return True
                else:
                    self.log_result("Admin Login", False, "", "Missing token or incorrect role")
                    return False
            else:
                self.log_result(
                    "Admin Login", 
                    False, 
                    "", 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, "", str(e))
            return False

    def test_jwt_token_validation(self):
        """Test JWT token validation by accessing protected endpoint"""
        if not self.admin_token:
            self.log_result("JWT Token Validation", False, "", "No admin token available")
            return False
            
        try:
            # Test with valid token by accessing admin dashboard (protected endpoint)
            response = self.session.get(f"{API_BASE}/admin/dashboard-stats")
            
            if response.status_code == 200:
                stats = response.json()
                self.log_result(
                    "JWT Token Validation",
                    True,
                    f"Token valid. Successfully accessed protected endpoint. Total users: {stats.get('users', {}).get('total', 0)}"
                )
                return True
            else:
                self.log_result(
                    "JWT Token Validation",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("JWT Token Validation", False, "", str(e))
            return False

    def test_protected_endpoint_access(self):
        """Test access to protected endpoints"""
        try:
            # Test admin dashboard access
            response = self.session.get(f"{API_BASE}/admin/dashboard-stats")
            
            if response.status_code == 200:
                stats = response.json()
                self.log_result(
                    "Protected Endpoint Access",
                    True,
                    f"Admin dashboard accessible. Users: {stats.get('users', {}).get('total', 0)}"
                )
                return True
            else:
                self.log_result(
                    "Protected Endpoint Access",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Protected Endpoint Access", False, "", str(e))
            return False

    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        try:
            # Create a session without auth headers
            temp_session = requests.Session()
            
            auth_data = {
                "email": "invalid@example.com",
                "password": "wrongpassword"
            }
            
            response = temp_session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 401:
                self.log_result(
                    "Invalid Credentials Test",
                    True,
                    "Correctly rejected invalid credentials with 401 status"
                )
                return True
            else:
                self.log_result(
                    "Invalid Credentials Test",
                    False,
                    "",
                    f"Expected 401, got HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Invalid Credentials Test", False, "", str(e))
            return False

    # ==========================================
    # 2. DATABASE OPERATIONS TESTING
    # ==========================================
    
    def test_database_operations(self):
        """Test CRUD operations for all entities"""
        print("\n🗄️ TESTING DATABASE OPERATIONS")
        print("-" * 50)
        
        # Test CRUD for each entity type
        self.test_teams_crud()
        self.test_brands_crud()
        self.test_competitions_crud()
        self.test_players_crud()
        self.test_master_jerseys_crud()
        self.test_reference_kits_crud()
        self.test_personal_kits_crud()

    def test_teams_crud(self):
        """Test Teams CRUD operations"""
        try:
            # CREATE
            team_data = {
                "name": "Deployment Test FC",
                "short_name": "DTFC",
                "country": "France",
                "city": "Paris",
                "founded_year": 2024,
                "team_colors": ["Blue", "Red"]
            }
            
            response = self.session.post(f"{API_BASE}/teams", json=team_data)
            
            if response.status_code in [200, 201]:
                created_team = response.json()
                team_id = created_team.get('id')
                self.created_entities['teams'].append(team_id)
                
                # READ
                read_response = self.session.get(f"{API_BASE}/teams/{team_id}")
                if read_response.status_code == 200:
                    team = read_response.json()
                    
                    # UPDATE
                    update_data = {"city": "Lyon"}
                    update_response = self.session.put(f"{API_BASE}/teams/{team_id}", json=update_data)
                    
                    if update_response.status_code == 200:
                        self.log_result(
                            "Teams CRUD Operations",
                            True,
                            f"Successfully created, read, and updated team: {team.get('name')}"
                        )
                        return True
                    else:
                        self.log_result("Teams CRUD Operations", False, "", f"Update failed: {update_response.status_code}")
                        return False
                else:
                    self.log_result("Teams CRUD Operations", False, "", f"Read failed: {read_response.status_code}")
                    return False
            else:
                self.log_result("Teams CRUD Operations", False, "", f"Create failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Teams CRUD Operations", False, "", str(e))
            return False

    def test_brands_crud(self):
        """Test Brands CRUD operations"""
        try:
            # CREATE
            brand_data = {
                "name": "Deployment Test Sports",
                "country": "Germany",
                "founded_year": 2024,
                "website": "https://deploymenttest.com"
            }
            
            response = self.session.post(f"{API_BASE}/brands", json=brand_data)
            
            if response.status_code in [200, 201]:
                created_brand = response.json()
                brand_id = created_brand.get('id')
                self.created_entities['brands'].append(brand_id)
                
                # READ
                read_response = self.session.get(f"{API_BASE}/brands/{brand_id}")
                if read_response.status_code == 200:
                    brand = read_response.json()
                    self.log_result(
                        "Brands CRUD Operations",
                        True,
                        f"Successfully created and read brand: {brand.get('name')}"
                    )
                    return True
                else:
                    self.log_result("Brands CRUD Operations", False, "", f"Read failed: {read_response.status_code}")
                    return False
            else:
                self.log_result("Brands CRUD Operations", False, "", f"Create failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Brands CRUD Operations", False, "", str(e))
            return False

    def test_competitions_crud(self):
        """Test Competitions CRUD operations"""
        try:
            # CREATE
            competition_data = {
                "competition_name": "Deployment Test League",
                "type": "National league",
                "country": "France",
                "level": 1,
                "confederations_federations": ["UEFA"]
            }
            
            response = self.session.post(f"{API_BASE}/competitions", json=competition_data)
            
            if response.status_code in [200, 201]:
                created_competition = response.json()
                competition_id = created_competition.get('id')
                self.created_entities['competitions'].append(competition_id)
                
                # READ
                read_response = self.session.get(f"{API_BASE}/competitions/{competition_id}")
                if read_response.status_code == 200:
                    competition = read_response.json()
                    self.log_result(
                        "Competitions CRUD Operations",
                        True,
                        f"Successfully created and read competition: {competition.get('competition_name')}"
                    )
                    return True
                else:
                    self.log_result("Competitions CRUD Operations", False, "", f"Read failed: {read_response.status_code}")
                    return False
            else:
                self.log_result("Competitions CRUD Operations", False, "", f"Create failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Competitions CRUD Operations", False, "", str(e))
            return False

    def test_players_crud(self):
        """Test Players CRUD operations"""
        try:
            # CREATE
            player_data = {
                "name": "Deployment Test Player",
                "full_name": "Deployment Test Player Jr",
                "nationality": "France",
                "position": "Forward",
                "birth_date": "1995-01-01"
            }
            
            response = self.session.post(f"{API_BASE}/players", json=player_data)
            
            if response.status_code in [200, 201]:
                created_player = response.json()
                player_id = created_player.get('id')
                self.created_entities['players'].append(player_id)
                
                # READ
                read_response = self.session.get(f"{API_BASE}/players/{player_id}")
                if read_response.status_code == 200:
                    player = read_response.json()
                    self.log_result(
                        "Players CRUD Operations",
                        True,
                        f"Successfully created and read player: {player.get('name')}"
                    )
                    return True
                else:
                    self.log_result("Players CRUD Operations", False, "", f"Read failed: {read_response.status_code}")
                    return False
            else:
                self.log_result("Players CRUD Operations", False, "", f"Create failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Players CRUD Operations", False, "", str(e))
            return False

    def test_master_jerseys_crud(self):
        """Test Master Jerseys CRUD operations"""
        try:
            # First get a team and brand for the master jersey
            teams_response = self.session.get(f"{API_BASE}/teams")
            brands_response = self.session.get(f"{API_BASE}/brands")
            
            if teams_response.status_code == 200 and brands_response.status_code == 200:
                teams = teams_response.json()
                brands = brands_response.json()
                
                if teams and brands:
                    team_id = teams[0].get('id')
                    brand_id = brands[0].get('id')
                    
                    # CREATE
                    master_jersey_data = {
                        "team_id": team_id,
                        "brand_id": brand_id,
                        "season": "2024-25",
                        "jersey_type": "home",
                        "model": "authentic",
                        "primary_color": "#FF0000"
                    }
                    
                    response = self.session.post(f"{API_BASE}/master-jerseys", json=master_jersey_data)
                    
                    if response.status_code in [200, 201]:
                        created_jersey = response.json()
                        jersey_id = created_jersey.get('id')
                        self.created_entities['master_jerseys'].append(jersey_id)
                        
                        # READ
                        read_response = self.session.get(f"{API_BASE}/master-jerseys/{jersey_id}")
                        if read_response.status_code == 200:
                            jersey = read_response.json()
                            self.log_result(
                                "Master Jerseys CRUD Operations",
                                True,
                                f"Successfully created and read master jersey: {jersey.get('topkit_reference', 'N/A')}"
                            )
                            return True
                        else:
                            self.log_result("Master Jerseys CRUD Operations", False, "", f"Read failed: {read_response.status_code}")
                            return False
                    else:
                        self.log_result("Master Jerseys CRUD Operations", False, "", f"Create failed: {response.status_code} - {response.text}")
                        return False
                else:
                    self.log_result("Master Jerseys CRUD Operations", False, "", "No teams or brands available for testing")
                    return False
            else:
                self.log_result("Master Jerseys CRUD Operations", False, "", "Failed to fetch teams or brands")
                return False
                
        except Exception as e:
            self.log_result("Master Jerseys CRUD Operations", False, "", str(e))
            return False

    def test_reference_kits_crud(self):
        """Test Reference Kits CRUD operations"""
        try:
            # First get a master jersey for the reference kit
            master_jerseys_response = self.session.get(f"{API_BASE}/master-jerseys")
            
            if master_jerseys_response.status_code == 200:
                master_jerseys = master_jerseys_response.json()
                
                if master_jerseys:
                    master_kit_id = master_jerseys[0].get('id')
                    
                    # CREATE
                    reference_kit_data = {
                        "master_kit_id": master_kit_id,
                        "player_name": "Deployment Test",
                        "player_number": "99",
                        "retail_price": 89.99,
                        "release_type": "authentic"
                    }
                    
                    response = self.session.post(f"{API_BASE}/reference-kits", json=reference_kit_data)
                    
                    if response.status_code in [200, 201]:
                        created_kit = response.json()
                        kit_id = created_kit.get('id')
                        self.created_entities['reference_kits'].append(kit_id)
                        
                        # READ
                        read_response = self.session.get(f"{API_BASE}/reference-kits/{kit_id}")
                        if read_response.status_code == 200:
                            kit = read_response.json()
                            self.log_result(
                                "Reference Kits CRUD Operations",
                                True,
                                f"Successfully created and read reference kit: {kit.get('topkit_reference', 'N/A')}"
                            )
                            return True
                        else:
                            self.log_result("Reference Kits CRUD Operations", False, "", f"Read failed: {read_response.status_code}")
                            return False
                    else:
                        self.log_result("Reference Kits CRUD Operations", False, "", f"Create failed: {response.status_code} - {response.text}")
                        return False
                else:
                    self.log_result("Reference Kits CRUD Operations", False, "", "No master jerseys available for testing")
                    return False
            else:
                self.log_result("Reference Kits CRUD Operations", False, "", "Failed to fetch master jerseys")
                return False
                
        except Exception as e:
            self.log_result("Reference Kits CRUD Operations", False, "", str(e))
            return False

    def test_personal_kits_crud(self):
        """Test Personal Kits CRUD operations"""
        try:
            # First get a reference kit for the personal kit
            reference_kits_response = self.session.get(f"{API_BASE}/reference-kits")
            
            if reference_kits_response.status_code == 200:
                reference_kits = reference_kits_response.json()
                
                if reference_kits:
                    reference_kit_id = reference_kits[0].get('id')
                    
                    # CREATE
                    personal_kit_data = {
                        "reference_kit_id": reference_kit_id,
                        "size": "M",
                        "condition": "mint",
                        "price_value": 120.00,
                        "acquisition_story": "Deployment test acquisition",
                        "times_worn": 0,
                        "printed_name": "TEST",
                        "printed_number": "99",
                        "personal_notes": "Deployment verification test"
                    }
                    
                    response = self.session.post(f"{API_BASE}/personal-kits", json=personal_kit_data)
                    
                    if response.status_code in [200, 201]:
                        created_kit = response.json()
                        kit_id = created_kit.get('id')
                        self.created_entities['personal_kits'].append(kit_id)
                        
                        # READ
                        read_response = self.session.get(f"{API_BASE}/personal-kits/{kit_id}")
                        if read_response.status_code == 200:
                            kit = read_response.json()
                            self.log_result(
                                "Personal Kits CRUD Operations",
                                True,
                                f"Successfully created and read personal kit with size: {kit.get('size', 'N/A')}"
                            )
                            return True
                        else:
                            self.log_result("Personal Kits CRUD Operations", False, "", f"Read failed: {read_response.status_code}")
                            return False
                    else:
                        self.log_result("Personal Kits CRUD Operations", False, "", f"Create failed: {response.status_code} - {response.text}")
                        return False
                else:
                    self.log_result("Personal Kits CRUD Operations", False, "", "No reference kits available for testing")
                    return False
            else:
                self.log_result("Personal Kits CRUD Operations", False, "", "Failed to fetch reference kits")
                return False
                
        except Exception as e:
            self.log_result("Personal Kits CRUD Operations", False, "", str(e))
            return False

    # ==========================================
    # 3. API ENDPOINTS TESTING
    # ==========================================
    
    def test_critical_api_endpoints(self):
        """Test all critical API endpoints"""
        print("\n🌐 TESTING CRITICAL API ENDPOINTS")
        print("-" * 50)
        
        endpoints = [
            ("/teams", "Teams Endpoint"),
            ("/brands", "Brands Endpoint"),
            ("/competitions", "Competitions Endpoint"),
            ("/players", "Players Endpoint"),
            ("/master-jerseys", "Master Jerseys Endpoint"),
            ("/contributions-v2/", "Contributions V2 Endpoint"),
            ("/collections/my-owned", "Collections Endpoint")
        ]
        
        for endpoint, name in endpoints:
            self.test_endpoint_get(endpoint, name)

    def test_endpoint_get(self, endpoint, name):
        """Test GET request to specific endpoint"""
        try:
            response = self.session.get(f"{API_BASE}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else len(data.get('items', []))
                self.log_result(
                    name,
                    True,
                    f"Successfully retrieved {count} items"
                )
                return True
            else:
                self.log_result(
                    name,
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(name, False, "", str(e))
            return False

    # ==========================================
    # 4. FILE UPLOAD SYSTEM TESTING
    # ==========================================
    
    def test_file_upload_system(self):
        """Test image upload functionality"""
        print("\n📁 TESTING FILE UPLOAD SYSTEM")
        print("-" * 50)
        
        self.test_image_upload_endpoint()

    def test_image_upload_endpoint(self):
        """Test /api/upload/image endpoint"""
        try:
            # Create a test image
            img = Image.new('RGB', (100, 100), color='red')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Prepare multipart form data with required fields
            files = {
                'file': ('test_deployment.png', img_buffer, 'image/png')
            }
            data = {
                'entity_type': 'team',
                'generate_variants': 'true'
            }
            
            # Remove Content-Type header for multipart upload
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.post(f"{API_BASE}/upload/image", files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                image_url = data.get('image_url')
                self.log_result(
                    "Image Upload Endpoint",
                    True,
                    f"Successfully uploaded image: {image_url}"
                )
                return True
            else:
                self.log_result(
                    "Image Upload Endpoint",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Image Upload Endpoint", False, "", str(e))
            return False

    # ==========================================
    # 5. FORM DEPENDENCIES TESTING
    # ==========================================
    
    def test_form_dependencies(self):
        """Test form dependency endpoints"""
        print("\n🔗 TESTING FORM DEPENDENCIES")
        print("-" * 50)
        
        self.test_teams_by_competition()
        self.test_competitions_by_type()
        self.test_federations_endpoint()

    def test_teams_by_competition(self):
        """Test teams by competition endpoint"""
        try:
            # First get competitions
            competitions_response = self.session.get(f"{API_BASE}/competitions")
            
            if competitions_response.status_code == 200:
                competitions = competitions_response.json()
                
                if competitions:
                    competition_id = competitions[0].get('id')
                    
                    response = self.session.get(f"{API_BASE}/form-dependencies/teams-by-competition/{competition_id}")
                    
                    if response.status_code == 200:
                        teams = response.json()
                        self.log_result(
                            "Teams by Competition",
                            True,
                            f"Successfully retrieved teams for competition: {len(teams)} teams"
                        )
                        return True
                    else:
                        self.log_result(
                            "Teams by Competition",
                            False,
                            "",
                            f"HTTP {response.status_code}: {response.text}"
                        )
                        return False
                else:
                    self.log_result("Teams by Competition", False, "", "No competitions available for testing")
                    return False
            else:
                self.log_result("Teams by Competition", False, "", "Failed to fetch competitions")
                return False
                
        except Exception as e:
            self.log_result("Teams by Competition", False, "", str(e))
            return False

    def test_competitions_by_type(self):
        """Test competitions by type endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/form-dependencies/competitions-by-type")
            
            if response.status_code == 200:
                data = response.json()
                types_count = len(data) if isinstance(data, list) else len(data.get('competition_types', []))
                self.log_result(
                    "Competitions by Type",
                    True,
                    f"Successfully retrieved competition types: {types_count} types"
                )
                return True
            else:
                self.log_result(
                    "Competitions by Type",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Competitions by Type", False, "", str(e))
            return False

    def test_federations_endpoint(self):
        """Test federations endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/form-dependencies/federations")
            
            if response.status_code == 200:
                federations = response.json()
                self.log_result(
                    "Federations Endpoint",
                    True,
                    f"Successfully retrieved federations: {len(federations)} federations"
                )
                return True
            else:
                self.log_result(
                    "Federations Endpoint",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Federations Endpoint", False, "", str(e))
            return False

    # ==========================================
    # 6. ERROR HANDLING TESTING
    # ==========================================
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n⚠️ TESTING ERROR HANDLING")
        print("-" * 50)
        
        self.test_invalid_endpoint()
        self.test_invalid_data_format()
        self.test_missing_required_fields()

    def test_invalid_endpoint(self):
        """Test request to non-existent endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/nonexistent-endpoint")
            
            if response.status_code == 404:
                self.log_result(
                    "Invalid Endpoint Error Handling",
                    True,
                    "Correctly returned 404 for non-existent endpoint"
                )
                return True
            else:
                self.log_result(
                    "Invalid Endpoint Error Handling",
                    False,
                    "",
                    f"Expected 404, got HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Invalid Endpoint Error Handling", False, "", str(e))
            return False

    def test_invalid_data_format(self):
        """Test request with invalid data format"""
        try:
            # Send invalid JSON to teams endpoint
            response = self.session.post(f"{API_BASE}/teams", data="invalid json")
            
            if response.status_code in [400, 422]:
                self.log_result(
                    "Invalid Data Format Error Handling",
                    True,
                    f"Correctly rejected invalid data with status {response.status_code}"
                )
                return True
            else:
                self.log_result(
                    "Invalid Data Format Error Handling",
                    False,
                    "",
                    f"Expected 400/422, got HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Invalid Data Format Error Handling", False, "", str(e))
            return False

    def test_missing_required_fields(self):
        """Test request with missing required fields"""
        try:
            # Send team data without required fields
            incomplete_data = {"city": "Paris"}  # Missing required name and country
            
            response = self.session.post(f"{API_BASE}/teams", json=incomplete_data)
            
            if response.status_code in [400, 422]:
                self.log_result(
                    "Missing Required Fields Error Handling",
                    True,
                    f"Correctly rejected incomplete data with status {response.status_code}"
                )
                return True
            else:
                self.log_result(
                    "Missing Required Fields Error Handling",
                    False,
                    "",
                    f"Expected 400/422, got HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Missing Required Fields Error Handling", False, "", str(e))
            return False

    # ==========================================
    # MAIN TEST RUNNER
    # ==========================================
    
    def run_all_tests(self):
        """Run all deployment verification tests"""
        print("🚀 STARTING DEPLOYMENT VERIFICATION TESTS")
        print("=" * 80)
        
        # 1. Authentication System
        self.test_authentication_system()
        
        # 2. Database Operations
        self.test_database_operations()
        
        # 3. API Endpoints
        self.test_critical_api_endpoints()
        
        # 4. File Upload System
        self.test_file_upload_system()
        
        # 5. Form Dependencies
        self.test_form_dependencies()
        
        # 6. Error Handling
        self.test_error_handling()
        
        # Print summary
        self.print_summary()
        
        return self.test_results

def main():
    """Main function to run deployment verification tests"""
    tester = DeploymentVerificationTester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    failed_tests = sum(1 for result in results if not result['success'])
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    exit(main())