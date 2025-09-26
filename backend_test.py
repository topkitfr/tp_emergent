#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - MASTER KIT IMAGE AND DATA FIXES VERIFICATION

**VERIFY MASTER KIT IMAGE AND DATA FIXES:**

I've just fixed several issues:
1. Fixed duplicate PIL import causing uploads endpoint 500 error
2. Fixed image URL construction in CollectionItemDetailPage.js
3. Verified backend master kit data embedding logic

**Test the fixes:**

1. **Image Serving Fix Verification**:
   - Test GET /api/uploads/ endpoint (should no longer return 500 error)
   - Test master kit image accessibility 
   - Verify image URLs are working correctly

2. **Master Kit Data Retrieval**:
   - Test GET /api/my-collection to see embedded master kit data
   - Test GET /api/my-collection/{collection_id} for individual items
   - Verify master kit fields (club, season, brand, etc.) are populated correctly

3. **Collection Item Data Quality**:
   - Check if collection items have proper master kit information embedded
   - Verify no "Unknown" values in properly created items
   - Test master kit photo URLs and accessibility

4. **Homepage and Kit Area Data**:
   - Test GET /api/master-kits for kit area data
   - Test homepage endpoints for master kit display
   - Verify image URLs and master kit information completeness

**Authentication**: emergency.admin@topkit.test / EmergencyAdmin2025!

**Expected Results**:
- /api/uploads/ endpoint now working without 500 errors
- Master kit images properly accessible
- Collection items showing complete master kit data (not "Unknown")
- All master kit endpoints returning proper data with correct image URLs

**PRIORITY: CRITICAL** - Verifying fixes for core user experience issues.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://collector-hub-4.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitMasterKitDisplayIssuesInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.master_kits_data = []
        self.image_test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate with emergency admin credentials"""
        try:
            print(f"\n🔐 EMERGENCY ADMIN AUTHENTICATION")
            print("=" * 60)
            print(f"   Email: {ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Emergency Admin Authentication", True, 
                             f"✅ Emergency admin authentication successful")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Email: {self.admin_user_data.get('email')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Emergency Admin Authentication", False, 
                             f"❌ Emergency admin authentication failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_master_kits_endpoint(self):
        """Test GET /api/master-kits endpoint for data retrieval"""
        try:
            print(f"\n🎽 TESTING MASTER KITS ENDPOINT")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                master_kits = response.json()
                self.master_kits_data = master_kits
                
                print(f"      ✅ Master kits endpoint accessible")
                print(f"      Total master kits returned: {len(master_kits)}")
                
                if len(master_kits) > 0:
                    # Analyze first master kit for data completeness
                    first_kit = master_kits[0]
                    print(f"\n      📋 FIRST MASTER KIT DATA ANALYSIS:")
                    print(f"         ID: {first_kit.get('id', 'MISSING')}")
                    print(f"         Club: {first_kit.get('club', 'MISSING')}")
                    print(f"         Season: {first_kit.get('season', 'MISSING')}")
                    print(f"         Brand: {first_kit.get('brand', 'MISSING')}")
                    print(f"         Kit Type: {first_kit.get('kit_type', 'MISSING')}")
                    print(f"         Front Photo URL: {first_kit.get('front_photo_url', 'MISSING')}")
                    print(f"         Back Photo URL: {first_kit.get('back_photo_url', 'MISSING')}")
                    print(f"         TopKit Reference: {first_kit.get('topkit_reference', 'MISSING')}")
                    
                    # Check for "Unknown" values
                    unknown_fields = []
                    for field, value in first_kit.items():
                        if value == "Unknown" or value == "unknown":
                            unknown_fields.append(field)
                    
                    if unknown_fields:
                        print(f"         ⚠️ Fields with 'Unknown' values: {unknown_fields}")
                    else:
                        print(f"         ✅ No 'Unknown' values detected in first master kit")
                    
                    # Check image URLs format
                    front_photo = first_kit.get('front_photo_url')
                    back_photo = first_kit.get('back_photo_url')
                    
                    if front_photo:
                        print(f"         Front photo path: {front_photo}")
                        if front_photo.startswith('uploads/') or front_photo.startswith('master_kits/'):
                            print(f"         ✅ Front photo URL format looks correct")
                        else:
                            print(f"         ⚠️ Front photo URL format may be incorrect")
                    
                    if back_photo:
                        print(f"         Back photo path: {back_photo}")
                        if back_photo.startswith('uploads/') or back_photo.startswith('master_kits/'):
                            print(f"         ✅ Back photo URL format looks correct")
                        else:
                            print(f"         ⚠️ Back photo URL format may be incorrect")
                
                self.log_test("Master Kits Endpoint", True, 
                             f"✅ Retrieved {len(master_kits)} master kits successfully")
                return True, master_kits
            else:
                print(f"      ❌ Failed to get master kits - Status {response.status_code}")
                print(f"      Response: {response.text}")
                
                self.log_test("Master Kits Endpoint", False, 
                             f"❌ Failed - Status {response.status_code}", response.text)
                return False, []
                
        except Exception as e:
            self.log_test("Master Kits Endpoint", False, f"Exception: {str(e)}")
            return False, []
    
    def test_image_serving_endpoints(self):
        """Test image serving endpoints for master kit images"""
        try:
            print(f"\n🖼️ TESTING IMAGE SERVING ENDPOINTS")
            print("=" * 60)
            
            if not self.master_kits_data:
                print("      ⚠️ No master kits data available for image testing")
                return False, []
            
            image_test_results = []
            
            # Test uploads endpoint accessibility
            print(f"      Testing /api/uploads/ endpoint accessibility...")
            uploads_response = self.session.get(f"{BACKEND_URL}/uploads/", timeout=10)
            print(f"      /api/uploads/ response status: {uploads_response.status_code}")
            
            if uploads_response.status_code == 500:
                print(f"      ❌ /api/uploads/ endpoint returning 500 Internal Server Error")
                print(f"      Response: {uploads_response.text}")
                self.log_test("Uploads Endpoint", False, 
                             f"❌ /api/uploads/ endpoint broken - Status 500", uploads_response.text)
            
            # Test specific master kit images
            tested_images = 0
            accessible_images = 0
            
            for kit in self.master_kits_data[:5]:  # Test first 5 kits
                kit_id = kit.get('id', 'unknown')
                front_photo = kit.get('front_photo_url')
                back_photo = kit.get('back_photo_url')
                
                print(f"\n      🎽 Testing images for Master Kit: {kit_id}")
                print(f"         Club: {kit.get('club', 'Unknown')}")
                print(f"         Season: {kit.get('season', 'Unknown')}")
                
                # Test front photo
                if front_photo:
                    tested_images += 1
                    print(f"         Testing front photo: {front_photo}")
                    
                    # Try different URL formats
                    image_urls_to_test = [
                        f"{BACKEND_URL}/uploads/{front_photo}",
                        f"{BACKEND_URL}/{front_photo}",
                        f"https://collector-hub-4.preview.emergentagent.com/{front_photo}",
                        f"https://collector-hub-4.preview.emergentagent.com/api/{front_photo}"
                    ]
                    
                    image_accessible = False
                    for url in image_urls_to_test:
                        try:
                            img_response = self.session.get(url, timeout=5)
                            if img_response.status_code == 200:
                                print(f"         ✅ Front photo accessible at: {url}")
                                accessible_images += 1
                                image_accessible = True
                                break
                            else:
                                print(f"         ❌ Front photo not accessible at: {url} (Status: {img_response.status_code})")
                        except Exception as e:
                            print(f"         ❌ Error accessing {url}: {str(e)}")
                    
                    if not image_accessible:
                        print(f"         ❌ Front photo not accessible via any tested URL")
                        image_test_results.append({
                            "kit_id": kit_id,
                            "image_type": "front",
                            "image_path": front_photo,
                            "accessible": False,
                            "issue": "Image not accessible via any URL format"
                        })
                    else:
                        image_test_results.append({
                            "kit_id": kit_id,
                            "image_type": "front", 
                            "image_path": front_photo,
                            "accessible": True
                        })
                
                # Test back photo
                if back_photo:
                    tested_images += 1
                    print(f"         Testing back photo: {back_photo}")
                    
                    # Try different URL formats
                    image_urls_to_test = [
                        f"{BACKEND_URL}/uploads/{back_photo}",
                        f"{BACKEND_URL}/{back_photo}",
                        f"https://collector-hub-4.preview.emergentagent.com/{back_photo}",
                        f"https://collector-hub-4.preview.emergentagent.com/api/{back_photo}"
                    ]
                    
                    image_accessible = False
                    for url in image_urls_to_test:
                        try:
                            img_response = self.session.get(url, timeout=5)
                            if img_response.status_code == 200:
                                print(f"         ✅ Back photo accessible at: {url}")
                                accessible_images += 1
                                image_accessible = True
                                break
                            else:
                                print(f"         ❌ Back photo not accessible at: {url} (Status: {img_response.status_code})")
                        except Exception as e:
                            print(f"         ❌ Error accessing {url}: {str(e)}")
                    
                    if not image_accessible:
                        print(f"         ❌ Back photo not accessible via any tested URL")
                        image_test_results.append({
                            "kit_id": kit_id,
                            "image_type": "back",
                            "image_path": back_photo,
                            "accessible": False,
                            "issue": "Image not accessible via any URL format"
                        })
                    else:
                        image_test_results.append({
                            "kit_id": kit_id,
                            "image_type": "back",
                            "image_path": back_photo,
                            "accessible": True
                        })
            
            self.image_test_results = image_test_results
            
            print(f"\n      📊 IMAGE ACCESSIBILITY SUMMARY:")
            print(f"         Total images tested: {tested_images}")
            print(f"         Accessible images: {accessible_images}")
            print(f"         Failed images: {tested_images - accessible_images}")
            print(f"         Success rate: {(accessible_images/tested_images)*100:.1f}%" if tested_images > 0 else "N/A")
            
            success = accessible_images > 0 if tested_images > 0 else False
            
            self.log_test("Image Serving Endpoints", success, 
                         f"{'✅' if success else '❌'} Image accessibility: {accessible_images}/{tested_images} images accessible")
            return success, image_test_results
                
        except Exception as e:
            self.log_test("Image Serving Endpoints", False, f"Exception: {str(e)}")
            return False, []
    
    def test_collection_item_data_retrieval(self):
        """Test collection item data retrieval with master kit information"""
        try:
            print(f"\n📦 TESTING COLLECTION ITEM DATA RETRIEVAL")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False, {}
            
            # Get user's collection
            collection_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            print(f"      Response Status: {collection_response.status_code}")
            
            if collection_response.status_code == 200:
                collection_items = collection_response.json()
                
                print(f"      ✅ Collection endpoint accessible")
                print(f"      Total collection items: {len(collection_items)}")
                
                if len(collection_items) > 0:
                    # Analyze first collection item
                    first_item = collection_items[0]
                    print(f"\n      📋 FIRST COLLECTION ITEM ANALYSIS:")
                    print(f"         Item ID: {first_item.get('id', 'MISSING')}")
                    print(f"         Master Kit ID: {first_item.get('master_kit_id', 'MISSING')}")
                    print(f"         Collection Type: {first_item.get('collection_type', 'MISSING')}")
                    
                    # Check embedded master kit data
                    master_kit_data = first_item.get('master_kit')
                    if master_kit_data:
                        print(f"         ✅ Master kit data embedded in collection item")
                        print(f"         Master Kit Club: {master_kit_data.get('club', 'MISSING')}")
                        print(f"         Master Kit Season: {master_kit_data.get('season', 'MISSING')}")
                        print(f"         Master Kit Brand: {master_kit_data.get('brand', 'MISSING')}")
                        
                        # Check for "Unknown" values in master kit data
                        unknown_fields = []
                        for field, value in master_kit_data.items():
                            if value == "Unknown" or value == "unknown":
                                unknown_fields.append(field)
                        
                        if unknown_fields:
                            print(f"         ⚠️ Master kit fields with 'Unknown' values: {unknown_fields}")
                        else:
                            print(f"         ✅ No 'Unknown' values in embedded master kit data")
                    else:
                        print(f"         ❌ No master kit data embedded in collection item")
                
                self.log_test("Collection Item Data Retrieval", True, 
                             f"✅ Retrieved {len(collection_items)} collection items successfully")
                return True, collection_items
            else:
                print(f"      ❌ Failed to get collection items - Status {collection_response.status_code}")
                print(f"      Response: {collection_response.text}")
                
                self.log_test("Collection Item Data Retrieval", False, 
                             f"❌ Failed - Status {collection_response.status_code}", collection_response.text)
                return False, []
                
        except Exception as e:
            self.log_test("Collection Item Data Retrieval", False, f"Exception: {str(e)}")
            return False, []
    
    def test_homepage_master_kit_endpoints(self):
        """Test homepage endpoints that should display master kit data"""
        try:
            print(f"\n🏠 TESTING HOMEPAGE MASTER KIT ENDPOINTS")
            print("=" * 60)
            
            homepage_endpoints = [
                "/homepage/expensive-kits",
                "/homepage/recent-master-kits", 
                "/homepage/recent-contributions"
            ]
            
            homepage_results = []
            
            for endpoint in homepage_endpoints:
                print(f"\n      Testing {endpoint}...")
                
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                    print(f"         Response Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"         ✅ Endpoint accessible")
                        print(f"         Items returned: {len(data) if isinstance(data, list) else 'N/A'}")
                        
                        # Check for master kit data quality
                        if isinstance(data, list) and len(data) > 0:
                            first_item = data[0]
                            
                            # Check for image URLs
                            front_photo = first_item.get('front_photo_url')
                            if front_photo:
                                print(f"         Front photo URL present: {front_photo}")
                            else:
                                print(f"         ⚠️ No front photo URL in first item")
                            
                            # Check for basic master kit fields
                            club = first_item.get('club')
                            season = first_item.get('season')
                            brand = first_item.get('brand')
                            
                            if club and club != "Unknown":
                                print(f"         ✅ Club data present: {club}")
                            else:
                                print(f"         ⚠️ Club data missing or 'Unknown': {club}")
                            
                            if season and season != "Unknown":
                                print(f"         ✅ Season data present: {season}")
                            else:
                                print(f"         ⚠️ Season data missing or 'Unknown': {season}")
                            
                            if brand and brand != "Unknown":
                                print(f"         ✅ Brand data present: {brand}")
                            else:
                                print(f"         ⚠️ Brand data missing or 'Unknown': {brand}")
                        
                        homepage_results.append({
                            "endpoint": endpoint,
                            "status": response.status_code,
                            "success": True,
                            "data_count": len(data) if isinstance(data, list) else 0
                        })
                    else:
                        print(f"         ❌ Endpoint failed - Status {response.status_code}")
                        print(f"         Response: {response.text}")
                        
                        homepage_results.append({
                            "endpoint": endpoint,
                            "status": response.status_code,
                            "success": False,
                            "error": response.text
                        })
                        
                except Exception as e:
                    print(f"         ❌ Exception testing {endpoint}: {str(e)}")
                    homepage_results.append({
                        "endpoint": endpoint,
                        "success": False,
                        "error": str(e)
                    })
            
            successful_endpoints = len([r for r in homepage_results if r.get('success')])
            total_endpoints = len(homepage_endpoints)
            
            print(f"\n      📊 HOMEPAGE ENDPOINTS SUMMARY:")
            print(f"         Successful endpoints: {successful_endpoints}/{total_endpoints}")
            print(f"         Success rate: {(successful_endpoints/total_endpoints)*100:.1f}%")
            
            success = successful_endpoints > 0
            
            self.log_test("Homepage Master Kit Endpoints", success, 
                         f"{'✅' if success else '❌'} Homepage endpoints: {successful_endpoints}/{total_endpoints} working")
            return success, homepage_results
                
        except Exception as e:
            self.log_test("Homepage Master Kit Endpoints", False, f"Exception: {str(e)}")
            return False, []
    
    def run_master_kit_display_investigation(self):
        """Run comprehensive master kit display issues investigation"""
        print("\n🚀 MASTER KIT DISPLAY ISSUES INVESTIGATION")
        print("Investigating critical master kit image and data display problems")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        auth_success = self.authenticate_admin()
        test_results.append(auth_success)
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return test_results, {}
        
        # Step 2: Test master kits endpoint
        print("\n2️⃣ Testing Master Kits Endpoint...")
        master_kits_success, master_kits_data = self.test_master_kits_endpoint()
        test_results.append(master_kits_success)
        
        # Step 3: Test image serving
        print("\n3️⃣ Testing Image Serving Endpoints...")
        image_success, image_results = self.test_image_serving_endpoints()
        test_results.append(image_success)
        
        # Step 4: Test collection item data
        print("\n4️⃣ Testing Collection Item Data Retrieval...")
        collection_success, collection_data = self.test_collection_item_data_retrieval()
        test_results.append(collection_success)
        
        # Step 5: Test homepage endpoints
        print("\n5️⃣ Testing Homepage Master Kit Endpoints...")
        homepage_success, homepage_results = self.test_homepage_master_kit_endpoints()
        test_results.append(homepage_success)
        
        return test_results, {
            "master_kits_data": master_kits_data if master_kits_success else [],
            "image_results": image_results if image_success else [],
            "collection_data": collection_data if collection_success else [],
            "homepage_results": homepage_results if homepage_success else []
        }
    
    def print_comprehensive_investigation_summary(self, test_data):
        """Print final comprehensive investigation summary"""
        print("\n📊 MASTER KIT DISPLAY ISSUES INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 CRITICAL ISSUES INVESTIGATION RESULTS:")
        
        # Master kits data analysis
        master_kits_data = test_data.get("master_kits_data", [])
        if master_kits_data:
            print(f"\n🎽 MASTER KITS DATA ANALYSIS:")
            print(f"  Total master kits available: {len(master_kits_data)}")
            
            if len(master_kits_data) > 0:
                first_kit = master_kits_data[0]
                unknown_fields = []
                for field, value in first_kit.items():
                    if value == "Unknown" or value == "unknown":
                        unknown_fields.append(field)
                
                if unknown_fields:
                    print(f"  ❌ ISSUE CONFIRMED: Fields showing 'Unknown' values: {unknown_fields}")
                else:
                    print(f"  ✅ No 'Unknown' values detected in master kit data")
        
        # Image serving analysis
        image_results = test_data.get("image_results", [])
        if image_results:
            accessible_images = len([r for r in image_results if r.get('accessible')])
            total_images = len(image_results)
            
            print(f"\n🖼️ IMAGE SERVING ANALYSIS:")
            print(f"  Images tested: {total_images}")
            print(f"  Accessible images: {accessible_images}")
            print(f"  Failed images: {total_images - accessible_images}")
            
            if accessible_images == 0 and total_images > 0:
                print(f"  ❌ CRITICAL ISSUE CONFIRMED: NO MASTER KIT IMAGES ARE ACCESSIBLE")
                print(f"  Root cause: Image serving infrastructure is broken")
            elif accessible_images < total_images:
                print(f"  ⚠️ PARTIAL ISSUE: Some master kit images not accessible")
            else:
                print(f"  ✅ All tested images are accessible")
        
        # Collection data analysis
        collection_data = test_data.get("collection_data", [])
        if collection_data:
            print(f"\n📦 COLLECTION DATA ANALYSIS:")
            print(f"  Collection items found: {len(collection_data)}")
            
            if len(collection_data) > 0:
                first_item = collection_data[0]
                master_kit_data = first_item.get('master_kit')
                
                if master_kit_data:
                    unknown_fields = []
                    for field, value in master_kit_data.items():
                        if value == "Unknown" or value == "unknown":
                            unknown_fields.append(field)
                    
                    if unknown_fields:
                        print(f"  ❌ ISSUE CONFIRMED: Collection items showing 'Unknown' master kit data: {unknown_fields}")
                    else:
                        print(f"  ✅ Collection items have proper master kit data")
                else:
                    print(f"  ❌ CRITICAL ISSUE: No master kit data embedded in collection items")
        
        # Homepage endpoints analysis
        homepage_results = test_data.get("homepage_results", [])
        if homepage_results:
            successful_endpoints = len([r for r in homepage_results if r.get('success')])
            total_endpoints = len(homepage_results)
            
            print(f"\n🏠 HOMEPAGE ENDPOINTS ANALYSIS:")
            print(f"  Working endpoints: {successful_endpoints}/{total_endpoints}")
            
            if successful_endpoints == 0:
                print(f"  ❌ CRITICAL ISSUE: All homepage master kit endpoints are broken")
            elif successful_endpoints < total_endpoints:
                print(f"  ⚠️ PARTIAL ISSUE: Some homepage endpoints not working")
            else:
                print(f"  ✅ All homepage endpoints working")
        
        # Final diagnosis
        print(f"\n🎯 CRITICAL ISSUES DIAGNOSIS:")
        
        critical_issues = []
        
        # Check for image serving issues
        if image_results:
            accessible_images = len([r for r in image_results if r.get('accessible')])
            if accessible_images == 0:
                critical_issues.append("Master kit images not displaying - image serving infrastructure broken")
        
        # Check for unknown data issues
        if master_kits_data and len(master_kits_data) > 0:
            first_kit = master_kits_data[0]
            unknown_fields = [field for field, value in first_kit.items() if value == "Unknown" or value == "unknown"]
            if unknown_fields:
                critical_issues.append(f"Master kit data showing 'Unknown' instead of actual values in fields: {unknown_fields}")
        
        # Check for collection data issues
        if collection_data and len(collection_data) > 0:
            first_item = collection_data[0]
            master_kit_data = first_item.get('master_kit')
            if not master_kit_data:
                critical_issues.append("Collection items missing embedded master kit data")
            elif master_kit_data:
                unknown_fields = [field for field, value in master_kit_data.items() if value == "Unknown" or value == "unknown"]
                if unknown_fields:
                    critical_issues.append(f"Collection items showing 'Unknown' master kit data in fields: {unknown_fields}")
        
        if critical_issues:
            print(f"  ❌ CRITICAL ISSUES CONFIRMED:")
            for i, issue in enumerate(critical_issues, 1):
                print(f"     {i}. {issue}")
        else:
            print(f"  ✅ NO CRITICAL ISSUES DETECTED:")
            print(f"     • Master kit images appear to be accessible")
            print(f"     • Master kit data appears to be properly populated")
            print(f"     • Collection items have proper master kit information")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ TEST FAILURES ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the master kit display issues investigation"""
    tester = TopKitMasterKitDisplayIssuesInvestigation()
    
    # Run the comprehensive master kit display investigation
    test_results, test_data = tester.run_master_kit_display_investigation()
    
    # Print comprehensive summary
    tester.print_comprehensive_investigation_summary(test_data)
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)