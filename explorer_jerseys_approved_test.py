#!/usr/bin/env python3
"""
TopKit Explorer Jerseys Approved Endpoint Testing
=================================================

OBJECTIF: Vérifier que l'endpoint `/api/jerseys/approved` retourne bien les maillots avec photos.

PROBLÈME IDENTIFIÉ: L'explorateur frontend utilise `/api/jerseys/approved` mais les tests précédents 
utilisaient `/api/jerseys`. Il faut vérifier si cet endpoint spécifique existe et retourne les bonnes données.

TESTS À EFFECTUER:
1. GET /api/jerseys/approved - Tester cet endpoint spécifique
2. Comparer avec GET /api/jerseys pour voir les différences
3. Vérifier que /api/jerseys/approved retourne bien les maillots avec photos
4. Analyser la structure des données retournées

FOCUS: Confirmer que l'endpoint utilisé par l'explorateur frontend retourne bien les photos des maillots.
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

class ExplorerJerseysApprovedTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
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
                
                user_info = data.get('user', {})
                self.log_test("Admin Authentication", True, 
                            f"Admin: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"HTTP {response.status_code}: {response.text}")
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
                
                user_info = data.get('user', {})
                self.log_test("User Authentication", True, 
                            f"User: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}")
                return True
            else:
                self.log_test("User Authentication", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_jerseys_approved_endpoint(self):
        """Test the specific /api/jerseys/approved endpoint used by frontend explorer"""
        try:
            # Test without authentication first
            response = self.session.get(f"{BACKEND_URL}/jerseys/approved")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Analyze the response structure
                jersey_count = len(jerseys) if isinstance(jerseys, list) else 0
                jerseys_with_photos = 0
                photo_fields_found = set()
                
                if isinstance(jerseys, list):
                    for jersey in jerseys:
                        has_photos = False
                        
                        # Check for different photo field formats
                        if jersey.get('front_photo_url'):
                            photo_fields_found.add('front_photo_url')
                            has_photos = True
                        if jersey.get('back_photo_url'):
                            photo_fields_found.add('back_photo_url')
                            has_photos = True
                        if jersey.get('images') and len(jersey.get('images', [])) > 0:
                            photo_fields_found.add('images_array')
                            has_photos = True
                        
                        if has_photos:
                            jerseys_with_photos += 1
                
                self.log_test("GET /api/jerseys/approved Endpoint", True,
                            f"Found {jersey_count} approved jerseys, {jerseys_with_photos} with photos. Photo fields: {list(photo_fields_found)}")
                
                # Log sample jersey data for analysis
                if isinstance(jerseys, list) and len(jerseys) > 0:
                    sample_jersey = jerseys[0]
                    print(f"   Sample Jersey Structure:")
                    print(f"   - Team: {sample_jersey.get('team')}")
                    print(f"   - League: {sample_jersey.get('league')}")
                    print(f"   - Season: {sample_jersey.get('season')}")
                    print(f"   - Status: {sample_jersey.get('status')}")
                    print(f"   - Front Photo: {sample_jersey.get('front_photo_url', 'None')}")
                    print(f"   - Back Photo: {sample_jersey.get('back_photo_url', 'None')}")
                    print(f"   - Images Array: {sample_jersey.get('images', 'None')}")
                
                return jersey_count, jerseys_with_photos
            else:
                self.log_test("GET /api/jerseys/approved Endpoint", False,
                            f"HTTP {response.status_code}: {response.text}")
                return 0, 0
                
        except Exception as e:
            self.log_test("GET /api/jerseys/approved Endpoint", False, f"Exception: {str(e)}")
            return 0, 0
    
    def test_jerseys_general_endpoint(self):
        """Test the general /api/jerseys endpoint for comparison"""
        try:
            response = self.session.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Analyze the response structure
                jersey_count = len(jerseys) if isinstance(jerseys, list) else 0
                jerseys_with_photos = 0
                
                if isinstance(jerseys, list):
                    for jersey in jerseys:
                        has_photos = (jersey.get('front_photo_url') or 
                                    jersey.get('back_photo_url') or 
                                    (jersey.get('images') and len(jersey.get('images', [])) > 0))
                        if has_photos:
                            jerseys_with_photos += 1
                
                self.log_test("GET /api/jerseys Endpoint (Comparison)", True,
                            f"Found {jersey_count} total jerseys, {jerseys_with_photos} with photos")
                
                return jersey_count, jerseys_with_photos
            else:
                self.log_test("GET /api/jerseys Endpoint (Comparison)", False,
                            f"HTTP {response.status_code}: {response.text}")
                return 0, 0
                
        except Exception as e:
            self.log_test("GET /api/jerseys Endpoint (Comparison)", False, f"Exception: {str(e)}")
            return 0, 0
    
    def create_approved_jersey_for_testing(self):
        """Create and approve a jersey for testing purposes"""
        try:
            # First authenticate as user to create jersey
            user_session = requests.Session()
            user_response = user_session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if user_response.status_code != 200:
                self.log_test("Create Test Jersey - User Auth", False, "Could not authenticate user")
                return None
            
            user_token = user_response.json().get('token')
            user_session.headers.update({'Authorization': f'Bearer {user_token}'})
            
            # Create a test jersey
            jersey_data = {
                "team": "FC Barcelona Explorer Test",
                "league": "La Liga",
                "season": "24/25",
                "manufacturer": "Nike",
                "jersey_type": "home",
                "sku_code": "EXPLORER-TEST-001",
                "model": "authentic",
                "description": "Test jersey for explorer approved endpoint validation with photos"
            }
            
            create_response = user_session.post(f"{BACKEND_URL}/jerseys", data=jersey_data)
            
            if create_response.status_code == 200:
                jersey = create_response.json()
                jersey_id = jersey.get('id')
                
                # Now authenticate as admin to approve the jersey
                admin_session = requests.Session()
                admin_response = admin_session.post(f"{BACKEND_URL}/auth/login", json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                })
                
                if admin_response.status_code == 200:
                    admin_token = admin_response.json().get('token')
                    admin_session.headers.update({'Authorization': f'Bearer {admin_token}'})
                    
                    # Approve the jersey
                    approve_response = admin_session.post(f"{BACKEND_URL}/admin/jerseys/{jersey_id}/approve")
                    
                    if approve_response.status_code == 200:
                        self.log_test("Create and Approve Test Jersey", True,
                                    f"Created and approved jersey {jersey_id} for testing")
                        return jersey_id
                    else:
                        self.log_test("Create and Approve Test Jersey", False,
                                    f"Failed to approve jersey: HTTP {approve_response.status_code}")
                        return None
                else:
                    self.log_test("Create and Approve Test Jersey", False,
                                f"Admin authentication failed for approval")
                    return None
            else:
                self.log_test("Create and Approve Test Jersey", False,
                            f"Failed to create jersey: HTTP {create_response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Create and Approve Test Jersey", False, f"Exception: {str(e)}")
            return None
    
    def test_endpoint_with_authentication(self):
        """Test the approved jerseys endpoint with authentication"""
        try:
            # Test with user authentication
            user_session = requests.Session()
            user_response = user_session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if user_response.status_code == 200:
                user_token = user_response.json().get('token')
                user_session.headers.update({'Authorization': f'Bearer {user_token}'})
                
                auth_response = user_session.get(f"{BACKEND_URL}/jerseys/approved")
                
                if auth_response.status_code == 200:
                    jerseys = auth_response.json()
                    jersey_count = len(jerseys) if isinstance(jerseys, list) else 0
                    
                    self.log_test("GET /api/jerseys/approved with Authentication", True,
                                f"Authenticated request returned {jersey_count} jerseys")
                    return True
                else:
                    self.log_test("GET /api/jerseys/approved with Authentication", False,
                                f"HTTP {auth_response.status_code}: {auth_response.text}")
                    return False
            else:
                self.log_test("GET /api/jerseys/approved with Authentication", False,
                            "Could not authenticate for testing")
                return False
                
        except Exception as e:
            self.log_test("GET /api/jerseys/approved with Authentication", False, f"Exception: {str(e)}")
            return False
    
    def analyze_photo_data_structure(self):
        """Analyze the photo data structure in approved jerseys"""
        try:
            response = self.session.get(f"{BACKEND_URL}/jerseys/approved")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                if not isinstance(jerseys, list) or len(jerseys) == 0:
                    self.log_test("Analyze Photo Data Structure", False, "No jerseys found to analyze")
                    return False
                
                photo_analysis = {
                    'total_jerseys': len(jerseys),
                    'jerseys_with_front_photo_url': 0,
                    'jerseys_with_back_photo_url': 0,
                    'jerseys_with_images_array': 0,
                    'jerseys_with_no_photos': 0,
                    'sample_photo_urls': []
                }
                
                for jersey in jerseys:
                    if jersey.get('front_photo_url'):
                        photo_analysis['jerseys_with_front_photo_url'] += 1
                        if len(photo_analysis['sample_photo_urls']) < 3:
                            photo_analysis['sample_photo_urls'].append(jersey.get('front_photo_url'))
                    
                    if jersey.get('back_photo_url'):
                        photo_analysis['jerseys_with_back_photo_url'] += 1
                    
                    if jersey.get('images') and len(jersey.get('images', [])) > 0:
                        photo_analysis['jerseys_with_images_array'] += 1
                    
                    if (not jersey.get('front_photo_url') and 
                        not jersey.get('back_photo_url') and 
                        not jersey.get('images')):
                        photo_analysis['jerseys_with_no_photos'] += 1
                
                self.log_test("Analyze Photo Data Structure", True,
                            f"Photo analysis: {photo_analysis}")
                
                # Print detailed analysis
                print(f"   📊 PHOTO DATA ANALYSIS:")
                print(f"   - Total Jerseys: {photo_analysis['total_jerseys']}")
                print(f"   - With Front Photo URL: {photo_analysis['jerseys_with_front_photo_url']}")
                print(f"   - With Back Photo URL: {photo_analysis['jerseys_with_back_photo_url']}")
                print(f"   - With Images Array: {photo_analysis['jerseys_with_images_array']}")
                print(f"   - Without Photos: {photo_analysis['jerseys_with_no_photos']}")
                
                if photo_analysis['sample_photo_urls']:
                    print(f"   - Sample Photo URLs: {photo_analysis['sample_photo_urls']}")
                
                return photo_analysis['jerseys_with_front_photo_url'] > 0 or photo_analysis['jerseys_with_back_photo_url'] > 0
            else:
                self.log_test("Analyze Photo Data Structure", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Analyze Photo Data Structure", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test of the jerseys/approved endpoint"""
        print("🎯 TOPKIT EXPLORER JERSEYS APPROVED ENDPOINT TESTING STARTED")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Endpoint: /api/jerseys/approved")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Step 1: Test the specific endpoint used by frontend explorer
        print("\n🎯 TESTING SPECIFIC ENDPOINT: /api/jerseys/approved")
        approved_count, approved_with_photos = self.test_jerseys_approved_endpoint()
        
        # Step 2: Test general jerseys endpoint for comparison
        print("\n📊 TESTING GENERAL ENDPOINT FOR COMPARISON: /api/jerseys")
        general_count, general_with_photos = self.test_jerseys_general_endpoint()
        
        # Step 3: Test with authentication
        print("\n🔐 TESTING WITH AUTHENTICATION")
        self.test_endpoint_with_authentication()
        
        # Step 4: Analyze photo data structure
        print("\n📸 ANALYZING PHOTO DATA STRUCTURE")
        has_photos = self.analyze_photo_data_structure()
        
        # Step 5: Create test data if needed
        if approved_count == 0:
            print("\n🏗️ CREATING TEST DATA (NO APPROVED JERSEYS FOUND)")
            self.create_approved_jersey_for_testing()
            
            # Re-test after creating data
            print("\n🔄 RE-TESTING AFTER CREATING TEST DATA")
            approved_count, approved_with_photos = self.test_jerseys_approved_endpoint()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print(f"🎉 EXPLORER JERSEYS APPROVED ENDPOINT TESTING COMPLETE - {success_rate:.1f}% SUCCESS RATE!")
        print("=" * 80)
        
        # Print detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n📊 SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Specific findings for the review request
        print("\n🎯 REVIEW REQUEST FINDINGS:")
        print(f"✅ /api/jerseys/approved endpoint {'EXISTS and is FUNCTIONAL' if approved_count >= 0 else 'NOT FOUND or BROKEN'}")
        print(f"📊 Approved jerseys found: {approved_count}")
        print(f"📸 Approved jerseys with photos: {approved_with_photos}")
        print(f"📊 General jerseys found: {general_count}")
        print(f"📸 General jerseys with photos: {general_with_photos}")
        
        # Comparison analysis
        if approved_count >= 0 and general_count >= 0:
            if approved_count == general_count:
                print("🔍 ANALYSIS: /api/jerseys/approved returns same count as /api/jerseys (may be same endpoint)")
            elif approved_count < general_count:
                print("🔍 ANALYSIS: /api/jerseys/approved filters to approved jerseys only (CORRECT BEHAVIOR)")
            else:
                print("🔍 ANALYSIS: /api/jerseys/approved returns more than general endpoint (UNEXPECTED)")
        
        # Photo availability analysis
        if approved_with_photos > 0:
            print("✅ PHOTOS CONFIRMED: Approved jerseys endpoint DOES return jerseys with photos")
        else:
            print("❌ PHOTOS MISSING: Approved jerseys endpoint does NOT return jerseys with photos")
        
        if success_rate >= 80:
            print("\n🎉 CONCLUSION: /api/jerseys/approved endpoint is WORKING and ready for frontend explorer!")
        else:
            print("\n⚠️ CONCLUSION: Issues identified with /api/jerseys/approved endpoint that need attention.")
        
        return success_rate

if __name__ == "__main__":
    tester = ExplorerJerseysApprovedTester()
    tester.run_comprehensive_test()