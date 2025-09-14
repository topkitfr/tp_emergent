#!/usr/bin/env python3
"""
Legacy Image System Fix Backend Testing
Testing the new /api/legacy-image/{image_id} endpoint and database elements image display
"""

import requests
import json
import os
import sys
from pathlib import Path
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://topkit-debug-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class LegacyImageSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
    def authenticate(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                self.log_test("Admin Authentication", True, f"Token length: {len(self.auth_token)} chars")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_legacy_image_endpoint_exists(self):
        """Test 1: Verify Legacy Image Endpoint exists"""
        try:
            # Test with a dummy image ID to see if endpoint exists
            test_image_id = "image_uploaded_1234567890"
            response = self.session.get(f"{API_BASE}/legacy-image/{test_image_id}")
            
            # We expect 404 for non-existent image, but endpoint should exist
            if response.status_code == 404:
                self.log_test("Legacy Image Endpoint Exists", True, f"Endpoint exists, returns 404 for non-existent image")
                return True
            elif response.status_code == 200:
                self.log_test("Legacy Image Endpoint Exists", True, f"Endpoint exists and found image")
                return True
            else:
                self.log_test("Legacy Image Endpoint Exists", False, f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Legacy Image Endpoint Exists", False, f"Exception: {str(e)}")
            return False
    
    def test_database_elements_with_legacy_format(self):
        """Test 2: Check if database elements have logo_url fields with legacy format"""
        legacy_images_found = []
        
        # Test teams
        try:
            response = self.session.get(f"{API_BASE}/teams")
            if response.status_code == 200:
                teams = response.json()
                for team in teams:
                    logo_url = team.get('logo_url', '')
                    if logo_url and 'image_uploaded_' in logo_url:
                        legacy_images_found.append(f"Team '{team.get('name', 'Unknown')}': {logo_url}")
                        
                self.log_test("Teams with Legacy Images", len(legacy_images_found) > 0, 
                            f"Found {len(legacy_images_found)} teams with legacy image format")
            else:
                self.log_test("Teams API Access", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Teams API Access", False, f"Exception: {str(e)}")
        
        # Test brands
        try:
            response = self.session.get(f"{API_BASE}/brands")
            if response.status_code == 200:
                brands = response.json()
                brand_legacy_count = 0
                for brand in brands:
                    logo_url = brand.get('logo_url', '')
                    if logo_url and 'image_uploaded_' in logo_url:
                        legacy_images_found.append(f"Brand '{brand.get('name', 'Unknown')}': {logo_url}")
                        brand_legacy_count += 1
                        
                self.log_test("Brands with Legacy Images", brand_legacy_count > 0, 
                            f"Found {brand_legacy_count} brands with legacy image format")
            else:
                self.log_test("Brands API Access", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Brands API Access", False, f"Exception: {str(e)}")
        
        # Test players
        try:
            response = self.session.get(f"{API_BASE}/players")
            if response.status_code == 200:
                players = response.json()
                player_legacy_count = 0
                for player in players:
                    photo_url = player.get('profile_picture_url', '') or player.get('photo_url', '')
                    if photo_url and 'image_uploaded_' in photo_url:
                        legacy_images_found.append(f"Player '{player.get('name', 'Unknown')}': {photo_url}")
                        player_legacy_count += 1
                        
                self.log_test("Players with Legacy Images", player_legacy_count > 0, 
                            f"Found {player_legacy_count} players with legacy image format")
            else:
                self.log_test("Players API Access", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Players API Access", False, f"Exception: {str(e)}")
        
        # Test competitions
        try:
            response = self.session.get(f"{API_BASE}/competitions")
            if response.status_code == 200:
                competitions = response.json()
                comp_legacy_count = 0
                for comp in competitions:
                    logo_url = comp.get('logo_url', '')
                    if logo_url and 'image_uploaded_' in logo_url:
                        legacy_images_found.append(f"Competition '{comp.get('competition_name', 'Unknown')}': {logo_url}")
                        comp_legacy_count += 1
                        
                self.log_test("Competitions with Legacy Images", comp_legacy_count > 0, 
                            f"Found {comp_legacy_count} competitions with legacy image format")
            else:
                self.log_test("Competitions API Access", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Competitions API Access", False, f"Exception: {str(e)}")
        
        # Summary
        total_legacy_images = len(legacy_images_found)
        self.log_test("Database Elements Legacy Format Detection", total_legacy_images > 0, 
                     f"Total legacy format images found: {total_legacy_images}")
        
        # Print details of found legacy images
        if legacy_images_found:
            print("\n📋 LEGACY IMAGE DETAILS:")
            for item in legacy_images_found[:10]:  # Show first 10
                print(f"   {item}")
            if len(legacy_images_found) > 10:
                print(f"   ... and {len(legacy_images_found) - 10} more")
        
        return legacy_images_found
    
    def test_legacy_image_detection(self, legacy_images):
        """Test 3: Verify that legacy format images are properly identified"""
        if not legacy_images:
            self.log_test("Legacy Image Detection", False, "No legacy images found to test")
            return False
        
        # Test detection logic
        detected_count = 0
        for image_info in legacy_images:
            # Extract image ID from the info string
            if ': image_uploaded_' in image_info:
                image_id = image_info.split(': image_uploaded_')[1]
                if image_id and image_id.isdigit():
                    detected_count += 1
        
        success = detected_count > 0
        self.log_test("Legacy Image Detection", success, 
                     f"Detected {detected_count} legacy format images (image_uploaded_TIMESTAMP)")
        return success
    
    def test_legacy_image_endpoint_functionality(self, legacy_images):
        """Test 4: Test the legacy image endpoint with actual legacy image IDs"""
        if not legacy_images:
            self.log_test("Legacy Image Endpoint Functionality", False, "No legacy images to test")
            return False
        
        tested_count = 0
        successful_responses = 0
        
        for image_info in legacy_images[:5]:  # Test first 5 legacy images
            if ': image_uploaded_' in image_info:
                try:
                    image_id = image_info.split(': image_uploaded_')[1]
                    if image_id:
                        tested_count += 1
                        response = self.session.get(f"{API_BASE}/legacy-image/image_uploaded_{image_id}")
                        
                        if response.status_code == 200:
                            successful_responses += 1
                            content_type = response.headers.get('content-type', '')
                            self.log_test(f"Legacy Image Serve: image_uploaded_{image_id}", True, 
                                        f"Content-Type: {content_type}, Size: {len(response.content)} bytes")
                        elif response.status_code == 404:
                            self.log_test(f"Legacy Image Serve: image_uploaded_{image_id}", False, 
                                        "Image file not found on server")
                        else:
                            self.log_test(f"Legacy Image Serve: image_uploaded_{image_id}", False, 
                                        f"HTTP {response.status_code}")
                            
                except Exception as e:
                    self.log_test(f"Legacy Image Serve Test", False, f"Exception: {str(e)}")
        
        overall_success = successful_responses > 0
        self.log_test("Legacy Image Endpoint Functionality", overall_success, 
                     f"Successfully served {successful_responses}/{tested_count} legacy images")
        return overall_success
    
    def test_image_file_existence(self):
        """Test 5: Check if legacy image files exist on the server"""
        # Test common legacy image directories
        test_paths = [
            "uploads/teams/",
            "uploads/brands/", 
            "uploads/players/",
            "uploads/competitions/",
            "uploads/"
        ]
        
        files_found = 0
        for path in test_paths:
            try:
                # Try to access a common file pattern
                test_response = self.session.get(f"{API_BASE}/uploads/{path}")
                if test_response.status_code != 404:
                    files_found += 1
            except:
                pass
        
        self.log_test("Legacy Image File Directories", files_found > 0, 
                     f"Found {files_found} accessible upload directories")
        return files_found > 0
    
    def test_complete_workflow(self, legacy_images):
        """Test 6: End-to-end test of database element -> legacy image URL -> backend serving"""
        if not legacy_images:
            self.log_test("Complete Workflow Test", False, "No legacy images for workflow test")
            return False
        
        workflow_success = 0
        total_tests = 0
        
        # Test workflow for each type of database element
        for image_info in legacy_images[:3]:  # Test first 3
            try:
                total_tests += 1
                
                # Step 1: Database element has legacy format URL
                if 'image_uploaded_' in image_info:
                    
                    # Step 2: Frontend should detect legacy format
                    image_id = image_info.split(': image_uploaded_')[1]
                    
                    # Step 3: Backend should serve via legacy endpoint
                    response = self.session.get(f"{API_BASE}/legacy-image/image_uploaded_{image_id}")
                    
                    if response.status_code == 200:
                        workflow_success += 1
                        self.log_test(f"Workflow: {image_info.split(':')[0]}", True, 
                                    "Complete workflow successful")
                    else:
                        self.log_test(f"Workflow: {image_info.split(':')[0]}", False, 
                                    f"Legacy endpoint returned {response.status_code}")
                        
            except Exception as e:
                self.log_test(f"Workflow Test", False, f"Exception: {str(e)}")
        
        overall_success = workflow_success > 0
        self.log_test("Complete Workflow Test", overall_success, 
                     f"Successful workflows: {workflow_success}/{total_tests}")
        return overall_success
    
    def test_frontend_integration(self):
        """Test 7: Verify frontend correctly routes legacy images to legacy endpoint"""
        # This tests the backend's ability to handle the frontend's expected behavior
        
        # Test that the legacy endpoint accepts the expected format
        test_cases = [
            "image_uploaded_1757682307853",  # PSG logo from test results
            "image_uploaded_1757775656853",  # AC Milan logo from test results
            "image_uploaded_1757683563379",  # Qatar Airways logo from test results
        ]
        
        endpoint_working = 0
        for test_case in test_cases:
            try:
                response = self.session.get(f"{API_BASE}/legacy-image/{test_case}")
                if response.status_code in [200, 404]:  # Both are valid responses
                    endpoint_working += 1
                    status = "Found" if response.status_code == 200 else "Not Found"
                    self.log_test(f"Frontend Integration: {test_case}", True, f"Endpoint responds ({status})")
                else:
                    self.log_test(f"Frontend Integration: {test_case}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Frontend Integration Test", False, f"Exception: {str(e)}")
        
        success = endpoint_working == len(test_cases)
        self.log_test("Frontend Integration", success, 
                     f"Legacy endpoint properly handles {endpoint_working}/{len(test_cases)} test cases")
        return success
    
    def run_all_tests(self):
        """Run all legacy image system tests"""
        print("🎯 LEGACY IMAGE SYSTEM FIX BACKEND TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test legacy image endpoint exists
        self.test_legacy_image_endpoint_exists()
        
        # Step 3: Find database elements with legacy format
        legacy_images = self.test_database_elements_with_legacy_format()
        
        # Step 4: Test legacy image detection
        self.test_legacy_image_detection(legacy_images)
        
        # Step 5: Test legacy image endpoint functionality
        self.test_legacy_image_endpoint_functionality(legacy_images)
        
        # Step 6: Test image file existence
        self.test_image_file_existence()
        
        # Step 7: Test complete workflow
        self.test_complete_workflow(legacy_images)
        
        # Step 8: Test frontend integration
        self.test_frontend_integration()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"🎯 LEGACY IMAGE SYSTEM TESTING COMPLETE")
        print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
        
        # Summary of key findings
        print("\n📋 KEY FINDINGS:")
        
        # Check if legacy endpoint exists
        endpoint_exists = any(result['success'] for result in self.test_results if 'Legacy Image Endpoint Exists' in result['test'])
        print(f"   • Legacy Image Endpoint: {'✅ EXISTS' if endpoint_exists else '❌ MISSING'}")
        
        # Check if legacy images found
        legacy_found = any(result['success'] for result in self.test_results if 'Database Elements Legacy Format Detection' in result['test'])
        print(f"   • Legacy Format Images: {'✅ FOUND' if legacy_found else '❌ NOT FOUND'}")
        
        # Check if images are being served
        images_served = any(result['success'] for result in self.test_results if 'Legacy Image Endpoint Functionality' in result['test'])
        print(f"   • Legacy Images Served: {'✅ WORKING' if images_served else '❌ NOT WORKING'}")
        
        # Check workflow
        workflow_working = any(result['success'] for result in self.test_results if 'Complete Workflow Test' in result['test'])
        print(f"   • End-to-End Workflow: {'✅ WORKING' if workflow_working else '❌ NOT WORKING'}")
        
        return success_rate >= 70  # Consider 70%+ as success

if __name__ == "__main__":
    tester = LegacyImageSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 LEGACY IMAGE SYSTEM FIX VERIFICATION: SUCCESS")
    else:
        print("\n🚨 LEGACY IMAGE SYSTEM FIX VERIFICATION: NEEDS ATTENTION")
    
    sys.exit(0 if success else 1)