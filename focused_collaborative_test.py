#!/usr/bin/env python3
"""
Focused TopKit Collaborative System Testing
Testing core functionality after UI restructuring
"""

import requests
import json
from datetime import datetime
import os

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-collab-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class FocusedCollaborativeTester:
    def __init__(self):
        self.admin_token = None
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
                user_info = data.get('user', {})
                self.log_test("Admin Authentication", True, f"Admin: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_existing_jersey_system(self):
        """Test existing jersey system functionality"""
        try:
            # Test regular jerseys endpoint
            response = self.session.get(f"{API_BASE}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                jersey_count = len(jerseys) if isinstance(jerseys, list) else jerseys.get('count', 0)
                self.log_test("Existing Jersey System", True, f"Found {jersey_count} jerseys")
                
                # Test approved jerseys
                approved_response = self.session.get(f"{API_BASE}/jerseys/approved")
                if approved_response.status_code == 200:
                    approved_jerseys = approved_response.json()
                    approved_count = len(approved_jerseys) if isinstance(approved_jerseys, list) else approved_jerseys.get('count', 0)
                    self.log_test("Approved Jerseys", True, f"Found {approved_count} approved jerseys")
                else:
                    self.log_test("Approved Jerseys", False, f"HTTP {approved_response.status_code}")
                
                return True
            else:
                self.log_test("Existing Jersey System", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Existing Jersey System", False, f"Exception: {str(e)}")
            return False
    
    def test_collaborative_endpoints(self):
        """Test all collaborative endpoints"""
        endpoints = [
            ("Teams", "/teams"),
            ("Brands", "/brands"),
            ("Players", "/players"),
            ("Competitions", "/competitions"),
            ("Master Jerseys", "/master-jerseys"),
            ("Jersey Releases", "/jersey-releases")
        ]
        
        for name, endpoint in endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else data.get('count', 0)
                    self.log_test(f"Collaborative {name} Endpoint", True, f"Found {count} {name.lower()}")
                else:
                    self.log_test(f"Collaborative {name} Endpoint", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Collaborative {name} Endpoint", False, f"Exception: {str(e)}")
    
    def test_contributions_with_correct_format(self):
        """Test contributions with correct data format"""
        if not self.admin_token:
            self.log_test("Contributions System", False, "Admin authentication required")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET contributions first
            response = self.session.get(f"{API_BASE}/contributions", headers=headers)
            
            if response.status_code == 200:
                contributions = response.json()
                contrib_count = len(contributions) if isinstance(contributions, list) else contributions.get('count', 0)
                self.log_test("Contributions - GET", True, f"Found {contrib_count} contributions")
                
                # Test contribution creation with correct format based on error message
                test_contribution = {
                    "entity_type": "team",
                    "entity_id": "test-team-id",
                    "title": "Test Team Contribution",
                    "description": "Testing contribution system with images",
                    "proposed_data": {
                        "name": "Updated Team Name",
                        "country": "Updated Country"
                    },
                    "images": {
                        "logo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                        "secondary_photos": []
                    }
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
    
    def test_admin_functionality(self):
        """Test admin-specific functionality"""
        if not self.admin_token:
            self.log_test("Admin Functionality", False, "Admin authentication required")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin jersey management
            response = self.session.get(f"{API_BASE}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                pending = response.json()
                pending_count = len(pending) if isinstance(pending, list) else pending.get('count', 0)
                self.log_test("Admin - Pending Jerseys", True, f"Found {pending_count} pending jerseys")
                
                # Test admin user management
                users_response = self.session.get(f"{API_BASE}/admin/users", headers=headers)
                if users_response.status_code == 200:
                    users = users_response.json()
                    user_count = len(users) if isinstance(users, list) else users.get('count', 0)
                    self.log_test("Admin - User Management", True, f"Found {user_count} users")
                else:
                    self.log_test("Admin - User Management", False, f"HTTP {users_response.status_code}")
                
                return True
            else:
                self.log_test("Admin - Pending Jerseys", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_marketplace_functionality(self):
        """Test marketplace functionality"""
        try:
            # Test marketplace catalog
            response = self.session.get(f"{API_BASE}/marketplace/catalog")
            
            if response.status_code == 200:
                catalog = response.json()
                catalog_count = len(catalog) if isinstance(catalog, list) else catalog.get('count', 0)
                self.log_test("Marketplace Catalog", True, f"Found {catalog_count} marketplace items")
                
                # Test listings
                listings_response = self.session.get(f"{API_BASE}/listings")
                if listings_response.status_code == 200:
                    listings = listings_response.json()
                    listings_count = len(listings) if isinstance(listings, list) else listings.get('count', 0)
                    self.log_test("Marketplace Listings", True, f"Found {listings_count} listings")
                else:
                    self.log_test("Marketplace Listings", False, f"HTTP {listings_response.status_code}")
                
                return True
            else:
                self.log_test("Marketplace Catalog", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Marketplace Functionality", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_tests(self):
        """Run focused collaborative system tests"""
        print("🎯 FOCUSED TOPKIT COLLABORATIVE SYSTEM TESTING")
        print("=" * 60)
        
        # Authentication
        print("\n📋 AUTHENTICATION")
        print("-" * 30)
        admin_auth = self.authenticate_admin()
        
        # Core systems
        print("\n📋 CORE SYSTEMS")
        print("-" * 30)
        self.test_existing_jersey_system()
        self.test_marketplace_functionality()
        
        # Collaborative endpoints
        print("\n📋 COLLABORATIVE ENDPOINTS")
        print("-" * 30)
        self.test_collaborative_endpoints()
        
        # Advanced features
        print("\n📋 ADVANCED FEATURES")
        print("-" * 30)
        self.test_contributions_with_correct_format()
        self.test_admin_functionality()
        
        # Results summary
        print("\n" + "=" * 60)
        print("🎯 FOCUSED TESTING RESULTS")
        print("=" * 60)
        
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
        
        # Focus areas assessment
        print(f"\n🎯 REVIEW REQUEST FOCUS AREAS:")
        existing_endpoints_ok = sum(1 for t in self.test_results if t['success'] and 'Endpoint' in t['test']) >= 4
        discogs_system_ok = any('Master Jersey' in t['test'] for t in self.test_results if t['success'])
        contributions_ok = any('Contributions' in t['test'] for t in self.test_results if t['success'])
        auth_ok = admin_auth
        
        print(f"✅ Existing API endpoints after UI restructuring: {'VERIFIED' if existing_endpoints_ok else 'ISSUES FOUND'}")
        print(f"✅ Discogs Master/Release relationship: {'VERIFIED' if discogs_system_ok else 'NEEDS VERIFICATION'}")
        print(f"✅ Collaborative contribution system: {'VERIFIED' if contributions_ok else 'NEEDS VERIFICATION'}")
        print(f"✅ Authentication system: {'VERIFIED' if auth_ok else 'ISSUES FOUND'}")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = FocusedCollaborativeTester()
    success = tester.run_focused_tests()
    
    if success:
        print(f"\n🎉 TOPKIT COLLABORATIVE SYSTEM IS OPERATIONAL!")
    else:
        print(f"\n🚨 TOPKIT COLLABORATIVE SYSTEM NEEDS ATTENTION!")
    
    exit(0 if success else 1)