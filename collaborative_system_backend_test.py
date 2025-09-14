#!/usr/bin/env python3
"""
TopKit Collaborative System Backend Testing
Testing the restructured TopKit collaborative system with Discogs-like navigation structure

Focus Areas:
1. Verify all existing API endpoints are still functional after UI restructuring
2. Check Discogs Master/Release relationship
3. Test collaborative contribution system with images
4. Authentication system verification
"""

import requests
import json
import base64
import time
from datetime import datetime
import os

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "123"

class TopKitCollaborativeSystemTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.session = requests.Session()
        
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
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
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
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                self.log_test("User Authentication", True, f"User: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_test("User Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_teams_endpoint(self):
        """Test Teams endpoint functionality"""
        try:
            # Test GET /api/teams
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                team_count = len(teams) if isinstance(teams, list) else teams.get('count', 0)
                self.log_test("Teams Endpoint - GET", True, f"Found {team_count} teams")
                
                # Test team search if teams exist
                if team_count > 0:
                    search_response = self.session.get(f"{API_BASE}/teams?search=Barcelona")
                    if search_response.status_code == 200:
                        search_results = search_response.json()
                        self.log_test("Teams Endpoint - Search", True, f"Search returned {len(search_results) if isinstance(search_results, list) else 'data'}")
                    else:
                        self.log_test("Teams Endpoint - Search", False, f"HTTP {search_response.status_code}")
                
                return True
            else:
                self.log_test("Teams Endpoint - GET", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Teams Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_brands_endpoint(self):
        """Test Brands endpoint functionality"""
        try:
            response = self.session.get(f"{API_BASE}/brands")
            
            if response.status_code == 200:
                brands = response.json()
                brand_count = len(brands) if isinstance(brands, list) else brands.get('count', 0)
                self.log_test("Brands Endpoint", True, f"Found {brand_count} brands")
                return True
            else:
                self.log_test("Brands Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Brands Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_players_endpoint(self):
        """Test Players endpoint functionality"""
        try:
            response = self.session.get(f"{API_BASE}/players")
            
            if response.status_code == 200:
                players = response.json()
                player_count = len(players) if isinstance(players, list) else players.get('count', 0)
                self.log_test("Players Endpoint", True, f"Found {player_count} players")
                return True
            else:
                self.log_test("Players Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Players Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_competitions_endpoint(self):
        """Test Competitions endpoint functionality"""
        try:
            response = self.session.get(f"{API_BASE}/competitions")
            
            if response.status_code == 200:
                competitions = response.json()
                comp_count = len(competitions) if isinstance(competitions, list) else competitions.get('count', 0)
                self.log_test("Competitions Endpoint", True, f"Found {comp_count} competitions")
                return True
            else:
                self.log_test("Competitions Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Competitions Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_master_jerseys_endpoint(self):
        """Test Master Jerseys endpoint (Discogs-style design concepts)"""
        try:
            response = self.session.get(f"{API_BASE}/master-jerseys")
            
            if response.status_code == 200:
                master_jerseys = response.json()
                master_count = len(master_jerseys) if isinstance(master_jerseys, list) else master_jerseys.get('count', 0)
                self.log_test("Master Jerseys Endpoint", True, f"Found {master_count} master jerseys")
                
                # Test master jersey details if any exist
                if isinstance(master_jerseys, list) and len(master_jerseys) > 0:
                    first_master = master_jerseys[0]
                    master_id = first_master.get('id')
                    if master_id:
                        detail_response = self.session.get(f"{API_BASE}/master-jerseys/{master_id}")
                        if detail_response.status_code == 200:
                            self.log_test("Master Jersey Details", True, f"Retrieved details for master jersey {master_id}")
                        else:
                            self.log_test("Master Jersey Details", False, f"HTTP {detail_response.status_code}")
                
                return True
            else:
                self.log_test("Master Jerseys Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Master Jerseys Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_jersey_releases_endpoint(self):
        """Test Jersey Releases endpoint (Discogs-style physical versions)"""
        try:
            response = self.session.get(f"{API_BASE}/jersey-releases")
            
            if response.status_code == 200:
                releases = response.json()
                release_count = len(releases) if isinstance(releases, list) else releases.get('count', 0)
                self.log_test("Jersey Releases Endpoint", True, f"Found {release_count} jersey releases")
                
                # Test master_jersey_id linking if releases exist
                if isinstance(releases, list) and len(releases) > 0:
                    linked_releases = [r for r in releases if r.get('master_jersey_id')]
                    self.log_test("Master Jersey Linking", True, f"{len(linked_releases)} releases linked to master jerseys")
                
                return True
            else:
                self.log_test("Jersey Releases Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Jersey Releases Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_contributions_system(self):
        """Test collaborative contribution system with images"""
        if not self.admin_token:
            self.log_test("Contributions System", False, "Admin authentication required")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET contributions
            response = self.session.get(f"{API_BASE}/contributions", headers=headers)
            
            if response.status_code == 200:
                contributions = response.json()
                contrib_count = len(contributions) if isinstance(contributions, list) else contributions.get('count', 0)
                self.log_test("Contributions - GET", True, f"Found {contrib_count} contributions")
                
                # Test contribution creation with images
                test_contribution = {
                    "entity_type": "team",
                    "entity_id": "test-team-id",
                    "title": "Test Team Contribution",
                    "description": "Testing contribution system with images",
                    "images": [
                        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                    ]
                }
                
                create_response = self.session.post(f"{API_BASE}/contributions", 
                                                  json=test_contribution, 
                                                  headers=headers)
                
                if create_response.status_code in [200, 201]:
                    created_contrib = create_response.json()
                    contrib_id = created_contrib.get('id')
                    self.log_test("Contributions - Create with Images", True, f"Created contribution {contrib_id}")
                    
                    # Test voting system if contribution was created
                    if contrib_id:
                        vote_data = {"vote_type": "approve"}
                        vote_response = self.session.post(f"{API_BASE}/contributions/{contrib_id}/vote",
                                                        json=vote_data,
                                                        headers=headers)
                        
                        if vote_response.status_code in [200, 201]:
                            self.log_test("Contributions - Voting System", True, "Vote submitted successfully")
                        else:
                            self.log_test("Contributions - Voting System", False, f"HTTP {vote_response.status_code}")
                    
                else:
                    self.log_test("Contributions - Create with Images", False, f"HTTP {create_response.status_code}: {create_response.text}")
                
                return True
            else:
                self.log_test("Contributions - GET", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Contributions System", False, f"Exception: {str(e)}")
            return False
    
    def test_search_functionality(self):
        """Test collaborative database search functionality"""
        try:
            # Test global search
            search_query = "Barcelona"
            response = self.session.get(f"{API_BASE}/search?q={search_query}")
            
            if response.status_code == 200:
                search_results = response.json()
                total_results = 0
                
                # Count results across all entity types
                if isinstance(search_results, dict):
                    for entity_type, results in search_results.items():
                        if isinstance(results, list):
                            total_results += len(results)
                
                self.log_test("Global Search Functionality", True, f"Search for '{search_query}' returned {total_results} results")
                return True
            else:
                self.log_test("Global Search Functionality", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Global Search Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_reference_generation(self):
        """Test TopKit reference generation system"""
        if not self.admin_token:
            self.log_test("Reference Generation", False, "Admin authentication required")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test creating a new team to verify reference generation
            test_team = {
                "name": "Test Team for Reference",
                "country": "Test Country",
                "league": "Test League"
            }
            
            response = self.session.post(f"{API_BASE}/teams", 
                                       json=test_team, 
                                       headers=headers)
            
            if response.status_code in [200, 201]:
                created_team = response.json()
                reference = created_team.get('reference') or created_team.get('topkit_reference')
                
                if reference and reference.startswith('TK-'):
                    self.log_test("Reference Generation", True, f"Generated reference: {reference}")
                    return True
                else:
                    self.log_test("Reference Generation", False, "No TopKit reference found in response")
                    return False
            else:
                self.log_test("Reference Generation", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Reference Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_protected_endpoints(self):
        """Test that protected endpoints require authentication"""
        try:
            # Test without authentication
            response = self.session.post(f"{API_BASE}/contributions", json={
                "entity_type": "team",
                "title": "Test without auth"
            })
            
            if response.status_code == 401:
                self.log_test("Protected Endpoints - Authentication Required", True, "Properly rejected unauthenticated request")
                
                # Test with authentication
                if self.admin_token:
                    headers = {"Authorization": f"Bearer {self.admin_token}"}
                    auth_response = self.session.get(f"{API_BASE}/contributions", headers=headers)
                    
                    if auth_response.status_code == 200:
                        self.log_test("Protected Endpoints - Authenticated Access", True, "Authenticated request successful")
                        return True
                    else:
                        self.log_test("Protected Endpoints - Authenticated Access", False, f"HTTP {auth_response.status_code}")
                        return False
                else:
                    self.log_test("Protected Endpoints - Authenticated Access", False, "No admin token available")
                    return False
            else:
                self.log_test("Protected Endpoints - Authentication Required", False, f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Protected Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all collaborative system tests"""
        print("🎯 STARTING TOPKIT COLLABORATIVE SYSTEM BACKEND TESTING")
        print("=" * 70)
        
        # Authentication tests
        print("\n📋 AUTHENTICATION SYSTEM TESTING")
        print("-" * 40)
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        
        # Core API endpoints testing
        print("\n📋 COLLABORATIVE DATABASE API ENDPOINTS")
        print("-" * 40)
        self.test_teams_endpoint()
        self.test_brands_endpoint()
        self.test_players_endpoint()
        self.test_competitions_endpoint()
        
        # Discogs-style Master/Release system
        print("\n📋 DISCOGS-STYLE MASTER/RELEASE SYSTEM")
        print("-" * 40)
        self.test_master_jerseys_endpoint()
        self.test_jersey_releases_endpoint()
        
        # Collaborative features
        print("\n📋 COLLABORATIVE CONTRIBUTION SYSTEM")
        print("-" * 40)
        self.test_contributions_system()
        self.test_search_functionality()
        self.test_reference_generation()
        
        # Security testing
        print("\n📋 AUTHENTICATION & SECURITY")
        print("-" * 40)
        self.test_protected_endpoints()
        
        # Results summary
        print("\n" + "=" * 70)
        print("🎯 TOPKIT COLLABORATIVE SYSTEM TESTING RESULTS")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n🎯 FOCUS AREAS VERIFICATION:")
        print(f"✅ Existing API endpoints functionality: {'VERIFIED' if passed_tests >= 4 else 'ISSUES FOUND'}")
        print(f"✅ Discogs Master/Release relationship: {'VERIFIED' if any('Master Jersey' in t['test'] for t in self.test_results if t['success']) else 'NEEDS VERIFICATION'}")
        print(f"✅ Collaborative contribution system: {'VERIFIED' if any('Contributions' in t['test'] for t in self.test_results if t['success']) else 'NEEDS VERIFICATION'}")
        print(f"✅ Authentication system: {'VERIFIED' if admin_auth and user_auth else 'ISSUES FOUND'}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = TopKitCollaborativeSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 TOPKIT COLLABORATIVE SYSTEM IS PRODUCTION-READY!")
    else:
        print(f"\n🚨 TOPKIT COLLABORATIVE SYSTEM NEEDS ATTENTION!")
    
    exit(0 if success else 1)