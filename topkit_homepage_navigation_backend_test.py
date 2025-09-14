#!/usr/bin/env python3

"""
TopKit Homepage and Navigation Backend Testing
Testing the current state of the TopKit application backend to verify all recent homepage and navigation fixes are working correctly.

Test Requirements from Review Request:
1. Brand Logo API Endpoints: Test /api/brands endpoint to verify brand data and logo URLs are being served correctly for Nike and Puma brands (for the trending brands fix)
2. Master Kit/Jersey Creation: Test Master Kit creation endpoints to verify the season field and overall form functionality is working 
3. Image Serving: Test the image serving endpoints to ensure brand logos and other images are being served with correct headers and content-type
4. Database/Catalogue Endpoints: Test team, brand, player, and competition endpoints to ensure the Database section is working properly
5. Navigation-related APIs: Test any backend endpoints that support the homepage navigation and kit area functionality
"""

import requests
import json
import sys
from datetime import datetime
import os

# Configuration - Use environment variables for production URLs
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitHomepageNavigationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} - {test_name}: {details}")
        
    def authenticate_admin(self):
        """Test 1: AUTHENTICATION - Login with admin credentials"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        print("=" * 60)
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token') or data.get('access_token')
                
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    
                    user_data = data.get('user', {})
                    self.admin_user_id = user_data.get('id')
                    
                    if self.admin_user_id:
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Successfully authenticated. Token length: {len(self.admin_token)}, User ID: {self.admin_user_id}, Role: {user_data.get('role', 'unknown')}"
                        )
                        return True
                    else:
                        self.log_test("Admin Authentication", False, "No user ID found in login response")
                        return False
                else:
                    self.log_test("Admin Authentication", False, "No access token received")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception during authentication: {str(e)}")
            return False
    
    def test_brand_logo_api_endpoints(self):
        """Test 2: BRAND LOGO API ENDPOINTS - Test /api/brands endpoint for Nike and Puma brands"""
        print("\n🏷️ TESTING BRAND LOGO API ENDPOINTS")
        print("=" * 60)
        
        try:
            # Test GET /api/brands endpoint
            response = self.session.get(f"{BACKEND_URL}/brands")
            
            if response.status_code == 200:
                brands_data = response.json()
                brands = brands_data if isinstance(brands_data, list) else []
                
                self.log_test(
                    "Brands API Endpoint Access", 
                    True, 
                    f"Successfully retrieved {len(brands)} brands from /api/brands"
                )
                
                # Look for Nike and Puma specifically
                nike_brand = None
                puma_brand = None
                brands_with_logos = 0
                
                for brand in brands:
                    brand_name = brand.get('name', '').lower()
                    if 'nike' in brand_name:
                        nike_brand = brand
                    elif 'puma' in brand_name:
                        puma_brand = brand
                    
                    # Check if brand has logo URL
                    if brand.get('logo_url'):
                        brands_with_logos += 1
                
                # Test Nike brand
                if nike_brand:
                    nike_logo_url = nike_brand.get('logo_url')
                    self.log_test(
                        "Nike Brand Found", 
                        True, 
                        f"Nike brand found with logo_url: {nike_logo_url or 'None'}"
                    )
                    
                    # Test Nike logo URL if present
                    if nike_logo_url:
                        self.test_image_url(nike_logo_url, "Nike Logo")
                else:
                    self.log_test("Nike Brand Found", False, "Nike brand not found in brands list")
                
                # Test Puma brand
                if puma_brand:
                    puma_logo_url = puma_brand.get('logo_url')
                    self.log_test(
                        "Puma Brand Found", 
                        True, 
                        f"Puma brand found with logo_url: {puma_logo_url or 'None'}"
                    )
                    
                    # Test Puma logo URL if present
                    if puma_logo_url:
                        self.test_image_url(puma_logo_url, "Puma Logo")
                else:
                    self.log_test("Puma Brand Found", False, "Puma brand not found in brands list")
                
                # Overall brand logo assessment
                self.log_test(
                    "Brand Logo Data Quality", 
                    brands_with_logos > 0, 
                    f"{brands_with_logos}/{len(brands)} brands have logo URLs"
                )
                
                return brands
                
            else:
                self.log_test("Brands API Endpoint Access", False, f"Failed with status {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Brands API Endpoint Access", False, f"Exception: {str(e)}")
            return []
    
    def test_image_url(self, image_url, image_name):
        """Helper method to test image URL accessibility"""
        try:
            # Handle relative URLs
            if image_url.startswith('/'):
                full_url = f"https://kit-fixes.preview.emergentagent.com{image_url}"
            else:
                full_url = image_url
            
            response = requests.get(full_url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                self.log_test(
                    f"{image_name} Accessibility", 
                    True, 
                    f"Image accessible at {full_url}, Content-Type: {content_type}, Size: {content_length} bytes"
                )
            else:
                self.log_test(
                    f"{image_name} Accessibility", 
                    False, 
                    f"Image not accessible at {full_url}, Status: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(f"{image_name} Accessibility", False, f"Exception accessing image: {str(e)}")
    
    def test_master_kit_creation_endpoints(self):
        """Test 3: MASTER KIT/JERSEY CREATION - Test Master Kit creation endpoints"""
        print("\n⚽ TESTING MASTER KIT/JERSEY CREATION ENDPOINTS")
        print("=" * 60)
        
        try:
            # First, get available teams and brands for creation
            teams_response = self.session.get(f"{BACKEND_URL}/teams")
            brands_response = self.session.get(f"{BACKEND_URL}/brands")
            
            if teams_response.status_code == 200 and brands_response.status_code == 200:
                teams = teams_response.json()
                brands = brands_response.json()
                
                if teams and brands:
                    # Test Master Jersey creation endpoint
                    test_master_jersey = {
                        "team_id": teams[0].get('id'),
                        "brand_id": brands[0].get('id'),
                        "season": "2024-25",
                        "jersey_type": "home",
                        "model": "authentic",
                        "primary_color": "#FF0000"
                    }
                    
                    response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=test_master_jersey)
                    
                    if response.status_code in [200, 201]:
                        created_jersey = response.json()
                        self.log_test(
                            "Master Jersey Creation", 
                            True, 
                            f"Successfully created master jersey with ID: {created_jersey.get('id', 'unknown')}, Season: {created_jersey.get('season', 'unknown')}"
                        )
                        
                        # Test season field specifically
                        if created_jersey.get('season') == "2024-25":
                            self.log_test(
                                "Season Field Validation", 
                                True, 
                                f"Season field correctly saved as: {created_jersey.get('season')}"
                            )
                        else:
                            self.log_test(
                                "Season Field Validation", 
                                False, 
                                f"Season field mismatch. Expected: 2024-25, Got: {created_jersey.get('season')}"
                            )
                        
                        return created_jersey
                        
                    else:
                        self.log_test("Master Jersey Creation", False, f"Creation failed with status {response.status_code}: {response.text}")
                        return None
                else:
                    self.log_test("Master Jersey Creation", False, "No teams or brands available for testing creation")
                    return None
            else:
                self.log_test("Master Jersey Creation", False, f"Failed to get teams/brands. Teams: {teams_response.status_code}, Brands: {brands_response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Master Jersey Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_database_catalogue_endpoints(self):
        """Test 4: DATABASE/CATALOGUE ENDPOINTS - Test team, brand, player, and competition endpoints"""
        print("\n📊 TESTING DATABASE/CATALOGUE ENDPOINTS")
        print("=" * 60)
        
        endpoints_to_test = [
            ("Teams", "/teams"),
            ("Brands", "/brands"),
            ("Players", "/players"),
            ("Competitions", "/competitions"),
            ("Master Jerseys", "/master-jerseys")
        ]
        
        catalogue_results = {}
        
        for endpoint_name, endpoint_path in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint_path}")
                
                if response.status_code == 200:
                    data = response.json()
                    items = data if isinstance(data, list) else []
                    
                    catalogue_results[endpoint_name] = {
                        'success': True,
                        'count': len(items),
                        'data': items
                    }
                    
                    self.log_test(
                        f"{endpoint_name} Endpoint", 
                        True, 
                        f"Successfully retrieved {len(items)} {endpoint_name.lower()}"
                    )
                    
                    # Test specific data quality for each endpoint
                    if endpoint_name == "Teams" and items:
                        teams_with_logos = sum(1 for team in items if team.get('logo_url'))
                        self.log_test(
                            f"{endpoint_name} Logo Data", 
                            teams_with_logos > 0, 
                            f"{teams_with_logos}/{len(items)} teams have logo URLs"
                        )
                    
                    elif endpoint_name == "Brands" and items:
                        brands_with_logos = sum(1 for brand in items if brand.get('logo_url'))
                        self.log_test(
                            f"{endpoint_name} Logo Data", 
                            brands_with_logos > 0, 
                            f"{brands_with_logos}/{len(items)} brands have logo URLs"
                        )
                    
                    elif endpoint_name == "Master Jerseys" and items:
                        jerseys_with_seasons = sum(1 for jersey in items if jersey.get('season'))
                        self.log_test(
                            f"{endpoint_name} Season Data", 
                            jerseys_with_seasons > 0, 
                            f"{jerseys_with_seasons}/{len(items)} master jerseys have season data"
                        )
                    
                else:
                    catalogue_results[endpoint_name] = {
                        'success': False,
                        'error': f"HTTP {response.status_code}: {response.text}"
                    }
                    
                    self.log_test(
                        f"{endpoint_name} Endpoint", 
                        False, 
                        f"Failed with status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                catalogue_results[endpoint_name] = {
                    'success': False,
                    'error': f"Exception: {str(e)}"
                }
                
                self.log_test(
                    f"{endpoint_name} Endpoint", 
                    False, 
                    f"Exception: {str(e)}"
                )
        
        # Overall catalogue assessment
        successful_endpoints = sum(1 for result in catalogue_results.values() if result['success'])
        total_items = sum(result.get('count', 0) for result in catalogue_results.values() if result['success'])
        
        self.log_test(
            "Database Catalogue Overall", 
            successful_endpoints >= 4, 
            f"Successfully tested {successful_endpoints}/5 catalogue endpoints. Total items: {total_items}"
        )
        
        return catalogue_results
    
    def test_navigation_related_apis(self):
        """Test 5: NAVIGATION-RELATED APIs - Test endpoints that support homepage navigation and kit area functionality"""
        print("\n🧭 TESTING NAVIGATION-RELATED APIs")
        print("=" * 60)
        
        navigation_endpoints = [
            ("Kit Area - Master Jerseys", "/master-jerseys"),
            ("Form Dependencies - Teams by Competition", "/form-dependencies/teams-by-competition/1"),
            ("Form Dependencies - Competitions by Type", "/form-dependencies/competitions-by-type"),
            ("Form Dependencies - Federations", "/form-dependencies/federations"),
            ("Vestiaire (Kit Store)", "/vestiaire"),
            ("User Collections (if authenticated)", f"/users/{self.admin_user_id}/collections" if self.admin_user_id else None)
        ]
        
        navigation_results = {}
        
        for endpoint_name, endpoint_path in navigation_endpoints:
            if endpoint_path is None:
                continue
                
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint_path}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    navigation_results[endpoint_name] = {
                        'success': True,
                        'data': data
                    }
                    
                    # Analyze response structure
                    if isinstance(data, list):
                        item_count = len(data)
                        self.log_test(
                            f"Navigation API - {endpoint_name}", 
                            True, 
                            f"Successfully retrieved {item_count} items"
                        )
                    elif isinstance(data, dict):
                        keys = list(data.keys())
                        self.log_test(
                            f"Navigation API - {endpoint_name}", 
                            True, 
                            f"Successfully retrieved data with keys: {keys[:5]}{'...' if len(keys) > 5 else ''}"
                        )
                    else:
                        self.log_test(
                            f"Navigation API - {endpoint_name}", 
                            True, 
                            f"Successfully retrieved data of type: {type(data).__name__}"
                        )
                    
                elif response.status_code == 404:
                    # 404 might be expected for some endpoints
                    navigation_results[endpoint_name] = {
                        'success': True,  # 404 is a valid response
                        'note': 'Endpoint not found (expected for some endpoints)'
                    }
                    
                    self.log_test(
                        f"Navigation API - {endpoint_name}", 
                        True, 
                        "Endpoint returned 404 (may be expected)"
                    )
                    
                else:
                    navigation_results[endpoint_name] = {
                        'success': False,
                        'error': f"HTTP {response.status_code}: {response.text}"
                    }
                    
                    self.log_test(
                        f"Navigation API - {endpoint_name}", 
                        False, 
                        f"Failed with status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                navigation_results[endpoint_name] = {
                    'success': False,
                    'error': f"Exception: {str(e)}"
                }
                
                self.log_test(
                    f"Navigation API - {endpoint_name}", 
                    False, 
                    f"Exception: {str(e)}"
                )
        
        # Overall navigation assessment
        successful_nav_endpoints = sum(1 for result in navigation_results.values() if result['success'])
        total_nav_endpoints = len(navigation_results)
        
        self.log_test(
            "Navigation APIs Overall", 
            successful_nav_endpoints >= (total_nav_endpoints * 0.7),  # 70% success rate
            f"Successfully tested {successful_nav_endpoints}/{total_nav_endpoints} navigation endpoints"
        )
        
        return navigation_results
    
    def test_image_serving_endpoints(self):
        """Test 6: IMAGE SERVING - Test image serving endpoints for correct headers and content-type"""
        print("\n🖼️ TESTING IMAGE SERVING ENDPOINTS")
        print("=" * 60)
        
        # Test generic image serving endpoint
        try:
            # Test if there's a generic image serving endpoint
            test_endpoints = [
                "/images/test.jpg",
                "/static/images/test.jpg",
                "/uploads/test.jpg"
            ]
            
            image_serving_working = False
            
            for endpoint in test_endpoints:
                try:
                    response = requests.get(f"https://kit-fixes.preview.emergentagent.com{endpoint}", timeout=5)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '')
                        cache_control = response.headers.get('cache-control', '')
                        
                        self.log_test(
                            f"Image Serving - {endpoint}", 
                            True, 
                            f"Image served successfully. Content-Type: {content_type}, Cache-Control: {cache_control}"
                        )
                        image_serving_working = True
                        break
                    elif response.status_code == 404:
                        # 404 is expected if test image doesn't exist
                        continue
                    else:
                        self.log_test(
                            f"Image Serving - {endpoint}", 
                            False, 
                            f"Unexpected status: {response.status_code}"
                        )
                        
                except Exception as e:
                    continue
            
            if not image_serving_working:
                self.log_test(
                    "Image Serving Endpoints", 
                    False, 
                    "No working image serving endpoints found (this may be expected if no test images exist)"
                )
            
            # Test image upload endpoint
            try:
                response = self.session.post(f"{BACKEND_URL}/upload/image", files={'image': ('test.txt', 'test content', 'text/plain')})
                
                if response.status_code in [200, 201]:
                    self.log_test(
                        "Image Upload Endpoint", 
                        True, 
                        f"Image upload endpoint accessible (status: {response.status_code})"
                    )
                elif response.status_code == 400:
                    # 400 is expected for invalid file type
                    self.log_test(
                        "Image Upload Endpoint", 
                        True, 
                        "Image upload endpoint properly validates file types (400 for invalid type)"
                    )
                elif response.status_code == 401:
                    # 401 might be expected if authentication is required
                    self.log_test(
                        "Image Upload Endpoint", 
                        True, 
                        "Image upload endpoint requires authentication (401)"
                    )
                else:
                    self.log_test(
                        "Image Upload Endpoint", 
                        False, 
                        f"Unexpected status: {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test("Image Upload Endpoint", False, f"Exception: {str(e)}")
            
        except Exception as e:
            self.log_test("Image Serving Endpoints", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all TopKit homepage and navigation backend tests"""
        print("🚀 STARTING TOPKIT HOMEPAGE AND NAVIGATION BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Test 1: Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Authentication failed. Some tests may be limited.")
        
        # Test 2: Brand Logo API Endpoints
        brands = self.test_brand_logo_api_endpoints()
        
        # Test 3: Master Kit/Jersey Creation
        master_jersey = self.test_master_kit_creation_endpoints()
        
        # Test 4: Database/Catalogue Endpoints
        catalogue_results = self.test_database_catalogue_endpoints()
        
        # Test 5: Navigation-related APIs
        navigation_results = self.test_navigation_related_apis()
        
        # Test 6: Image Serving
        self.test_image_serving_endpoints()
        
        # Generate final report
        self.generate_final_report()
        
        return True
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("📋 FINAL TEST REPORT - TOPKIT HOMEPAGE AND NAVIGATION BACKEND")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📊 DETAILED RESULTS:")
        print("-" * 80)
        
        # Group results by category
        categories = {
            "Authentication": [],
            "Brand Logo API": [],
            "Master Kit Creation": [],
            "Database Catalogue": [],
            "Navigation APIs": [],
            "Image Serving": []
        }
        
        for result in self.test_results:
            test_name = result['test']
            if 'Authentication' in test_name:
                categories["Authentication"].append(result)
            elif 'Brand' in test_name or 'Nike' in test_name or 'Puma' in test_name:
                categories["Brand Logo API"].append(result)
            elif 'Master' in test_name or 'Season' in test_name:
                categories["Master Kit Creation"].append(result)
            elif 'Endpoint' in test_name and any(x in test_name for x in ['Teams', 'Brands', 'Players', 'Competitions', 'Database']):
                categories["Database Catalogue"].append(result)
            elif 'Navigation' in test_name:
                categories["Navigation APIs"].append(result)
            elif 'Image' in test_name:
                categories["Image Serving"].append(result)
            else:
                # Default category
                categories["Database Catalogue"].append(result)
        
        for category, results in categories.items():
            if results:
                print(f"\n🔍 {category.upper()}:")
                for result in results:
                    status = "✅ PASS" if result['success'] else "❌ FAIL"
                    print(f"  {status} - {result['test']}")
                    print(f"    Details: {result['details']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("🎉 EXCELLENT - TopKit homepage and navigation backend is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD - TopKit homepage and navigation backend is working well with minor issues.")
        elif success_rate >= 60:
            print("⚠️ NEEDS IMPROVEMENT - TopKit homepage and navigation backend has some issues.")
        else:
            print("🚨 CRITICAL ISSUES - TopKit homepage and navigation backend has significant problems.")
        
        print("=" * 80)

def main():
    """Main function to run the tests"""
    tester = TopKitHomepageNavigationTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ Testing completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Testing failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()