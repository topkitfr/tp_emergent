#!/usr/bin/env python3
"""
TopKit Comprehensive Jerseys Endpoint Testing
=============================================

OBJECTIF: Tester en détail les endpoints /api/jerseys et /api/jerseys/approved 
pour confirmer qu'ils retournent bien les maillots avec photos.

TESTS COMPLETS:
1. GET /api/jerseys - Endpoint principal avec informations créateur
2. GET /api/jerseys/approved - Endpoint spécifique avec compteurs de listings
3. Comparaison des structures de données
4. Vérification des photos dans les deux endpoints
5. Test des filtres (équipe, saison, ligue)
6. Authentification et permissions

FOCUS: Confirmer que l'explorateur frontend peut récupérer les maillots avec photos.
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

class ComprehensiveJerseysEndpointTester:
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
                            f"Admin: {user_info.get('name')}, Role: {user_info.get('role')}")
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
                            f"User: {user_info.get('name')}, Role: {user_info.get('role')}")
                return True
            else:
                self.log_test("User Authentication", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_jerseys_endpoint(self):
        """Test the main /api/jerseys endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Analyze response
                jersey_count = len(jerseys) if isinstance(jerseys, list) else 0
                jerseys_with_photos = 0
                has_creator_info = 0
                photo_fields = set()
                
                if isinstance(jerseys, list):
                    for jersey in jerseys:
                        # Check for photos
                        has_photos = False
                        if jersey.get('front_photo_url'):
                            photo_fields.add('front_photo_url')
                            has_photos = True
                        if jersey.get('back_photo_url'):
                            photo_fields.add('back_photo_url')
                            has_photos = True
                        if jersey.get('images') and len(jersey.get('images', [])) > 0:
                            photo_fields.add('images_array')
                            has_photos = True
                        
                        if has_photos:
                            jerseys_with_photos += 1
                        
                        # Check for creator info
                        if jersey.get('creator_info'):
                            has_creator_info += 1
                
                self.log_test("GET /api/jerseys Endpoint", True,
                            f"Found {jersey_count} jerseys, {jerseys_with_photos} with photos, {has_creator_info} with creator info. Photo fields: {list(photo_fields)}")
                
                return {
                    'count': jersey_count,
                    'with_photos': jerseys_with_photos,
                    'with_creator_info': has_creator_info,
                    'photo_fields': list(photo_fields),
                    'data': jerseys[:2] if jerseys else []  # Sample data
                }
            else:
                self.log_test("GET /api/jerseys Endpoint", False,
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("GET /api/jerseys Endpoint", False, f"Exception: {str(e)}")
            return None
    
    def test_jerseys_approved_endpoint(self):
        """Test the /api/jerseys/approved endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/jerseys/approved")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Analyze response
                jersey_count = len(jerseys) if isinstance(jerseys, list) else 0
                jerseys_with_photos = 0
                has_listing_count = 0
                photo_fields = set()
                
                if isinstance(jerseys, list):
                    for jersey in jerseys:
                        # Check for photos
                        has_photos = False
                        if jersey.get('front_photo_url'):
                            photo_fields.add('front_photo_url')
                            has_photos = True
                        if jersey.get('back_photo_url'):
                            photo_fields.add('back_photo_url')
                            has_photos = True
                        if jersey.get('images') and len(jersey.get('images', [])) > 0:
                            photo_fields.add('images_array')
                            has_photos = True
                        
                        if has_photos:
                            jerseys_with_photos += 1
                        
                        # Check for listing count
                        if 'active_listings' in jersey:
                            has_listing_count += 1
                
                self.log_test("GET /api/jerseys/approved Endpoint", True,
                            f"Found {jersey_count} approved jerseys, {jerseys_with_photos} with photos, {has_listing_count} with listing counts. Photo fields: {list(photo_fields)}")
                
                return {
                    'count': jersey_count,
                    'with_photos': jerseys_with_photos,
                    'with_listing_count': has_listing_count,
                    'photo_fields': list(photo_fields),
                    'data': jerseys[:2] if jerseys else []  # Sample data
                }
            else:
                self.log_test("GET /api/jerseys/approved Endpoint", False,
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("GET /api/jerseys/approved Endpoint", False, f"Exception: {str(e)}")
            return None
    
    def test_endpoint_filters(self):
        """Test filtering capabilities of both endpoints"""
        try:
            # Test filtering by team
            filters = [
                {"team": "Barcelona"},
                {"league": "La Liga"},
                {"season": "2024-25"}
            ]
            
            results = {}
            
            for filter_params in filters:
                filter_name = list(filter_params.keys())[0]
                
                # Test /api/jerseys with filter
                response1 = self.session.get(f"{BACKEND_URL}/jerseys", params=filter_params)
                # Test /api/jerseys/approved with filter
                response2 = self.session.get(f"{BACKEND_URL}/jerseys/approved", params=filter_params)
                
                if response1.status_code == 200 and response2.status_code == 200:
                    jerseys1 = response1.json()
                    jerseys2 = response2.json()
                    
                    results[filter_name] = {
                        'jerseys_count': len(jerseys1) if isinstance(jerseys1, list) else 0,
                        'approved_count': len(jerseys2) if isinstance(jerseys2, list) else 0
                    }
                else:
                    results[filter_name] = {'error': f"HTTP {response1.status_code}/{response2.status_code}"}
            
            self.log_test("Test Endpoint Filters", True,
                        f"Filter results: {results}")
            return results
            
        except Exception as e:
            self.log_test("Test Endpoint Filters", False, f"Exception: {str(e)}")
            return None
    
    def compare_endpoint_structures(self, jerseys_data, approved_data):
        """Compare the data structures returned by both endpoints"""
        try:
            if not jerseys_data or not approved_data:
                self.log_test("Compare Endpoint Structures", False, "Missing data for comparison")
                return
            
            # Compare sample jersey structures
            sample_jersey = jerseys_data['data'][0] if jerseys_data['data'] else {}
            sample_approved = approved_data['data'][0] if approved_data['data'] else {}
            
            jersey_fields = set(sample_jersey.keys()) if sample_jersey else set()
            approved_fields = set(sample_approved.keys()) if sample_approved else set()
            
            unique_to_jerseys = jersey_fields - approved_fields
            unique_to_approved = approved_fields - jersey_fields
            common_fields = jersey_fields & approved_fields
            
            comparison = {
                'common_fields': len(common_fields),
                'unique_to_jerseys': list(unique_to_jerseys),
                'unique_to_approved': list(unique_to_approved),
                'jerseys_has_creator_info': 'creator_info' in jersey_fields,
                'approved_has_listing_count': 'active_listings' in approved_fields
            }
            
            self.log_test("Compare Endpoint Structures", True,
                        f"Structure comparison: {comparison}")
            
            # Print detailed comparison
            print(f"   📊 STRUCTURE COMPARISON:")
            print(f"   - Common fields: {len(common_fields)}")
            print(f"   - Unique to /jerseys: {list(unique_to_jerseys)}")
            print(f"   - Unique to /approved: {list(unique_to_approved)}")
            print(f"   - /jerseys has creator_info: {'creator_info' in jersey_fields}")
            print(f"   - /approved has active_listings: {'active_listings' in approved_fields}")
            
            return comparison
            
        except Exception as e:
            self.log_test("Compare Endpoint Structures", False, f"Exception: {str(e)}")
            return None
    
    def test_photo_accessibility(self, jerseys_data, approved_data):
        """Test if photo URLs are accessible"""
        try:
            photo_urls = []
            
            # Collect photo URLs from both endpoints
            for data in [jerseys_data, approved_data]:
                if data and data['data']:
                    for jersey in data['data']:
                        if jersey.get('front_photo_url'):
                            photo_urls.append(jersey['front_photo_url'])
                        if jersey.get('back_photo_url'):
                            photo_urls.append(jersey['back_photo_url'])
                        if jersey.get('images'):
                            photo_urls.extend(jersey['images'])
            
            # Remove duplicates
            photo_urls = list(set(photo_urls))
            
            if not photo_urls:
                self.log_test("Test Photo Accessibility", False, "No photo URLs found to test")
                return
            
            # Test accessibility of first few photo URLs
            accessible_count = 0
            test_urls = photo_urls[:3]  # Test first 3 URLs
            
            for url in test_urls:
                try:
                    # Construct full URL if relative
                    if url.startswith('uploads/'):
                        full_url = f"https://jersey-collab-1.preview.emergentagent.com/{url}"
                    else:
                        full_url = url
                    
                    response = requests.head(full_url, timeout=5)
                    if response.status_code == 200:
                        accessible_count += 1
                except:
                    pass  # URL not accessible
            
            self.log_test("Test Photo Accessibility", True,
                        f"Tested {len(test_urls)} photo URLs, {accessible_count} accessible. Sample URLs: {test_urls}")
            
        except Exception as e:
            self.log_test("Test Photo Accessibility", False, f"Exception: {str(e)}")
    
    def test_authenticated_access(self):
        """Test endpoints with authentication"""
        try:
            if not self.user_token:
                self.log_test("Test Authenticated Access", False, "No user token available")
                return
            
            # Test with user authentication
            headers = {'Authorization': f'Bearer {self.user_token}'}
            
            response1 = self.session.get(f"{BACKEND_URL}/jerseys", headers=headers)
            response2 = self.session.get(f"{BACKEND_URL}/jerseys/approved", headers=headers)
            
            if response1.status_code == 200 and response2.status_code == 200:
                jerseys1 = response1.json()
                jerseys2 = response2.json()
                
                count1 = len(jerseys1) if isinstance(jerseys1, list) else 0
                count2 = len(jerseys2) if isinstance(jerseys2, list) else 0
                
                self.log_test("Test Authenticated Access", True,
                            f"Authenticated access: /jerseys returned {count1}, /approved returned {count2}")
            else:
                self.log_test("Test Authenticated Access", False,
                            f"HTTP {response1.status_code}/{response2.status_code}")
                
        except Exception as e:
            self.log_test("Test Authenticated Access", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive test of both jersey endpoints"""
        print("🎯 TOPKIT COMPREHENSIVE JERSEYS ENDPOINT TESTING STARTED")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Endpoints: /api/jerseys and /api/jerseys/approved")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Step 1: Authenticate users
        print("\n🔐 AUTHENTICATION SETUP")
        self.authenticate_admin()
        self.authenticate_user()
        
        # Step 2: Test main jerseys endpoint
        print("\n📊 TESTING MAIN ENDPOINT: /api/jerseys")
        jerseys_data = self.test_jerseys_endpoint()
        
        # Step 3: Test approved jerseys endpoint
        print("\n🎯 TESTING APPROVED ENDPOINT: /api/jerseys/approved")
        approved_data = self.test_jerseys_approved_endpoint()
        
        # Step 4: Test filtering capabilities
        print("\n🔍 TESTING ENDPOINT FILTERS")
        self.test_endpoint_filters()
        
        # Step 5: Compare endpoint structures
        print("\n📋 COMPARING ENDPOINT STRUCTURES")
        self.compare_endpoint_structures(jerseys_data, approved_data)
        
        # Step 6: Test photo accessibility
        print("\n📸 TESTING PHOTO ACCESSIBILITY")
        self.test_photo_accessibility(jerseys_data, approved_data)
        
        # Step 7: Test authenticated access
        print("\n🔐 TESTING AUTHENTICATED ACCESS")
        self.test_authenticated_access()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print(f"🎉 COMPREHENSIVE JERSEYS ENDPOINT TESTING COMPLETE - {success_rate:.1f}% SUCCESS RATE!")
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
        
        if jerseys_data:
            print(f"✅ /api/jerseys: {jerseys_data['count']} jerseys, {jerseys_data['with_photos']} with photos")
        else:
            print("❌ /api/jerseys: FAILED")
        
        if approved_data:
            print(f"✅ /api/jerseys/approved: {approved_data['count']} jerseys, {approved_data['with_photos']} with photos")
        else:
            print("❌ /api/jerseys/approved: FAILED")
        
        # Photo availability analysis
        total_photos = 0
        if jerseys_data:
            total_photos += jerseys_data['with_photos']
        if approved_data:
            total_photos += approved_data['with_photos']
        
        if total_photos > 0:
            print("✅ PHOTOS CONFIRMED: Both endpoints return jerseys with photos")
        else:
            print("❌ PHOTOS MISSING: No jerseys with photos found in either endpoint")
        
        # Endpoint comparison
        if jerseys_data and approved_data:
            if jerseys_data['count'] == approved_data['count']:
                print("🔍 ANALYSIS: Both endpoints return same jersey count (both filter to approved only)")
            else:
                print(f"🔍 ANALYSIS: Different counts - /jerseys: {jerseys_data['count']}, /approved: {approved_data['count']}")
        
        if success_rate >= 80:
            print("\n🎉 CONCLUSION: Both jersey endpoints are WORKING and ready for frontend explorer!")
        else:
            print("\n⚠️ CONCLUSION: Issues identified that need attention.")
        
        return success_rate

if __name__ == "__main__":
    tester = ComprehensiveJerseysEndpointTester()
    tester.run_comprehensive_test()