#!/usr/bin/env python3
"""
TopKit Backend Deployment Verification Testing - Focused Version
Testing existing functionality without creating new entities to avoid reference generation issues.

Testing Focus Areas:
1. Authentication System (login/logout, JWT tokens)
2. Database Read Operations (GET endpoints)
3. Critical API Endpoints
4. Form Dependencies
5. Error Handling

Admin Credentials: topkitfr@gmail.com / TopKitSecure789#
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-collection-5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class FocusedDeploymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
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

    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*80)
        print("FOCUSED DEPLOYMENT VERIFICATION TEST SUMMARY")
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
                content_stats = stats.get('content', {})
                self.log_result(
                    "Protected Endpoint Access",
                    True,
                    f"Admin dashboard accessible. Teams: {content_stats.get('teams', 0)}, Brands: {content_stats.get('brands', 0)}, Master Jerseys: {content_stats.get('master_jerseys', 0)}"
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
    # 2. DATABASE READ OPERATIONS TESTING
    # ==========================================
    
    def test_database_read_operations(self):
        """Test read operations for all entities"""
        print("\n🗄️ TESTING DATABASE READ OPERATIONS")
        print("-" * 50)
        
        # Test read operations for each entity type
        self.test_teams_read()
        self.test_brands_read()
        self.test_competitions_read()
        self.test_players_read()
        self.test_master_jerseys_read()

    def test_teams_read(self):
        """Test Teams read operations"""
        try:
            # READ ALL
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                if teams:
                    # READ INDIVIDUAL
                    team_id = teams[0].get('id')
                    individual_response = self.session.get(f"{API_BASE}/teams/{team_id}")
                    
                    if individual_response.status_code == 200:
                        team = individual_response.json()
                        self.log_result(
                            "Teams Read Operations",
                            True,
                            f"Successfully read {len(teams)} teams and individual team: {team.get('name', 'N/A')}"
                        )
                        return True
                    else:
                        self.log_result("Teams Read Operations", False, "", f"Individual read failed: {individual_response.status_code}")
                        return False
                else:
                    self.log_result(
                        "Teams Read Operations",
                        True,
                        "Successfully read teams endpoint (empty result)"
                    )
                    return True
            else:
                self.log_result("Teams Read Operations", False, "", f"Read all failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Teams Read Operations", False, "", str(e))
            return False

    def test_brands_read(self):
        """Test Brands read operations"""
        try:
            response = self.session.get(f"{API_BASE}/brands")
            
            if response.status_code == 200:
                brands = response.json()
                if brands:
                    brand_id = brands[0].get('id')
                    individual_response = self.session.get(f"{API_BASE}/brands/{brand_id}")
                    
                    if individual_response.status_code == 200:
                        brand = individual_response.json()
                        self.log_result(
                            "Brands Read Operations",
                            True,
                            f"Successfully read {len(brands)} brands and individual brand: {brand.get('name', 'N/A')}"
                        )
                        return True
                    else:
                        self.log_result("Brands Read Operations", False, "", f"Individual read failed: {individual_response.status_code}")
                        return False
                else:
                    self.log_result(
                        "Brands Read Operations",
                        True,
                        "Successfully read brands endpoint (empty result)"
                    )
                    return True
            else:
                self.log_result("Brands Read Operations", False, "", f"Read failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Brands Read Operations", False, "", str(e))
            return False

    def test_competitions_read(self):
        """Test Competitions read operations"""
        try:
            response = self.session.get(f"{API_BASE}/competitions")
            
            if response.status_code == 200:
                competitions = response.json()
                if competitions:
                    competition_id = competitions[0].get('id')
                    individual_response = self.session.get(f"{API_BASE}/competitions/{competition_id}")
                    
                    if individual_response.status_code == 200:
                        competition = individual_response.json()
                        self.log_result(
                            "Competitions Read Operations",
                            True,
                            f"Successfully read {len(competitions)} competitions and individual: {competition.get('competition_name', 'N/A')}"
                        )
                        return True
                    else:
                        self.log_result("Competitions Read Operations", False, "", f"Individual read failed: {individual_response.status_code}")
                        return False
                else:
                    self.log_result(
                        "Competitions Read Operations",
                        True,
                        "Successfully read competitions endpoint (empty result)"
                    )
                    return True
            else:
                self.log_result("Competitions Read Operations", False, "", f"Read failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Competitions Read Operations", False, "", str(e))
            return False

    def test_players_read(self):
        """Test Players read operations"""
        try:
            response = self.session.get(f"{API_BASE}/players")
            
            if response.status_code == 200:
                players = response.json()
                if players:
                    player_id = players[0].get('id')
                    individual_response = self.session.get(f"{API_BASE}/players/{player_id}")
                    
                    if individual_response.status_code == 200:
                        player = individual_response.json()
                        self.log_result(
                            "Players Read Operations",
                            True,
                            f"Successfully read {len(players)} players and individual: {player.get('name', 'N/A')}"
                        )
                        return True
                    else:
                        self.log_result("Players Read Operations", False, "", f"Individual read failed: {individual_response.status_code}")
                        return False
                else:
                    self.log_result(
                        "Players Read Operations",
                        True,
                        "Successfully read players endpoint (empty result)"
                    )
                    return True
            else:
                self.log_result("Players Read Operations", False, "", f"Read failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Players Read Operations", False, "", str(e))
            return False

    def test_master_jerseys_read(self):
        """Test Master Jerseys read operations"""
        try:
            response = self.session.get(f"{API_BASE}/master-jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                if jerseys:
                    jersey_id = jerseys[0].get('id')
                    individual_response = self.session.get(f"{API_BASE}/master-jerseys/{jersey_id}")
                    
                    if individual_response.status_code == 200:
                        jersey = individual_response.json()
                        self.log_result(
                            "Master Jerseys Read Operations",
                            True,
                            f"Successfully read {len(jerseys)} master jerseys and individual: {jersey.get('topkit_reference', 'N/A')}"
                        )
                        return True
                    else:
                        self.log_result("Master Jerseys Read Operations", False, "", f"Individual read failed: {individual_response.status_code}")
                        return False
                else:
                    self.log_result(
                        "Master Jerseys Read Operations",
                        True,
                        "Successfully read master jerseys endpoint (empty result)"
                    )
                    return True
            else:
                self.log_result("Master Jerseys Read Operations", False, "", f"Read failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Master Jerseys Read Operations", False, "", str(e))
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
    # 4. FORM DEPENDENCIES TESTING
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
                    self.log_result("Teams by Competition", True, "No competitions available for testing (expected)")
                    return True
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
    # 5. ERROR HANDLING TESTING
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
        print("🚀 STARTING FOCUSED DEPLOYMENT VERIFICATION TESTS")
        print("=" * 80)
        
        # 1. Authentication System
        self.test_authentication_system()
        
        # 2. Database Read Operations
        self.test_database_read_operations()
        
        # 3. API Endpoints
        self.test_critical_api_endpoints()
        
        # 4. Form Dependencies
        self.test_form_dependencies()
        
        # 5. Error Handling
        self.test_error_handling()
        
        # Print summary
        self.print_summary()
        
        return self.test_results

def main():
    """Main function to run deployment verification tests"""
    tester = FocusedDeploymentTester()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    failed_tests = sum(1 for result in results if not result['success'])
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    exit(main())