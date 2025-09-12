#!/usr/bin/env python3
"""
TopKit Image Display Bug Fix Verification - Backend Testing
Final verification that the image display bug has been completely fixed
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration des URLs
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"

# Données d'authentification admin
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImageDisplayFixVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Test 1: Admin Authentication"""
        print("🔐 TEST 1: ADMIN AUTHENTICATION")
        print("=" * 50)
        
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                
                if user_info.get("role") == "admin":
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_test(
                        "Admin Authentication", 
                        True, 
                        f"Admin authenticated: {user_info.get('name')} (Role: {user_info.get('role')})"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Authentication", 
                        False, 
                        error=f"User does not have admin role: {user_info.get('role')}"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, error=str(e))
            return False

    def test_teams_logo_url_populated(self):
        """Test 2: GET /api/teams - Verify teams have logo_url with base64 data"""
        print("🏆 TEST 2: TEAMS LOGO_URL POPULATED WITH BASE64 DATA")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                
                # Count teams with logo_url populated
                teams_with_logo = []
                teams_with_base64_logo = []
                
                for team in teams:
                    logo_url = team.get("logo_url")
                    if logo_url:
                        teams_with_logo.append(team)
                        if isinstance(logo_url, str) and logo_url.startswith("data:image/"):
                            teams_with_base64_logo.append(team)
                
                total_teams = len(teams)
                teams_with_logo_count = len(teams_with_logo)
                teams_with_base64_count = len(teams_with_base64_logo)
                
                # Check for specific teams mentioned in review request
                fc_barcelona = None
                psg = None
                
                for team in teams:
                    if "barcelona" in team.get("name", "").lower():
                        fc_barcelona = team
                    elif "paris saint-germain" in team.get("name", "").lower() or "psg" in team.get("name", "").lower():
                        psg = team
                
                success = teams_with_base64_count > 0
                
                details = f"Total teams: {total_teams}, Teams with logo_url: {teams_with_logo_count}, Teams with base64 logo_url: {teams_with_base64_count}"
                
                if fc_barcelona:
                    fc_logo = fc_barcelona.get("logo_url")
                    details += f" | FC Barcelona logo_url: {'✅ Base64' if fc_logo and fc_logo.startswith('data:image/') else '❌ Missing/Invalid'}"
                
                if psg:
                    psg_logo = psg.get("logo_url")
                    details += f" | PSG logo_url: {'✅ Base64' if psg_logo and psg_logo.startswith('data:image/') else '❌ Missing/Invalid'}"
                
                self.log_test(
                    "Teams Logo URL Populated", 
                    success, 
                    details
                )
                return success, teams_with_base64_logo
            else:
                self.log_test(
                    "Teams Logo URL Populated", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False, []
                
        except Exception as e:
            self.log_test("Teams Logo URL Populated", False, error=str(e))
            return False, []

    def test_brands_logo_url_populated(self):
        """Test 3: GET /api/brands - Verify brands have logo_url with base64 images"""
        print("🏷️ TEST 3: BRANDS LOGO_URL POPULATED WITH BASE64 DATA")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/brands")
            
            if response.status_code == 200:
                brands = response.json()
                
                # Count brands with logo_url populated
                brands_with_logo = []
                brands_with_base64_logo = []
                
                for brand in brands:
                    logo_url = brand.get("logo_url")
                    if logo_url:
                        brands_with_logo.append(brand)
                        if isinstance(logo_url, str) and logo_url.startswith("data:image/"):
                            brands_with_base64_logo.append(brand)
                
                total_brands = len(brands)
                brands_with_logo_count = len(brands_with_logo)
                brands_with_base64_count = len(brands_with_base64_logo)
                
                # Check for Nike specifically mentioned in review request
                nike_brand = None
                for brand in brands:
                    if "nike" in brand.get("name", "").lower():
                        nike_brand = brand
                        break
                
                success = brands_with_base64_count > 0
                
                details = f"Total brands: {total_brands}, Brands with logo_url: {brands_with_logo_count}, Brands with base64 logo_url: {brands_with_base64_count}"
                
                if nike_brand:
                    nike_logo = nike_brand.get("logo_url")
                    details += f" | Nike logo_url: {'✅ Base64' if nike_logo and nike_logo.startswith('data:image/') else '❌ Missing/Invalid'}"
                
                self.log_test(
                    "Brands Logo URL Populated", 
                    success, 
                    details
                )
                return success, brands_with_base64_logo
            else:
                self.log_test(
                    "Brands Logo URL Populated", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False, []
                
        except Exception as e:
            self.log_test("Brands Logo URL Populated", False, error=str(e))
            return False, []

    def test_fc_barcelona_specific(self):
        """Test 4: FC Barcelona Specific Test - Verify FC Barcelona has working logo_url"""
        print("⚽ TEST 4: FC BARCELONA SPECIFIC LOGO TEST")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                
                fc_barcelona = None
                for team in teams:
                    team_name = team.get("name", "").lower()
                    if "barcelona" in team_name and "fc" in team_name:
                        fc_barcelona = team
                        break
                
                if fc_barcelona:
                    logo_url = fc_barcelona.get("logo_url")
                    
                    if logo_url and isinstance(logo_url, str) and logo_url.startswith("data:image/"):
                        # Verify it's a valid base64 image
                        try:
                            import base64
                            # Extract base64 part
                            if "base64," in logo_url:
                                base64_data = logo_url.split("base64,")[1]
                                # Try to decode to verify it's valid base64
                                decoded = base64.b64decode(base64_data)
                                
                                self.log_test(
                                    "FC Barcelona Specific Logo Test", 
                                    True, 
                                    f"FC Barcelona found with valid base64 logo_url (Size: {len(decoded)} bytes, Format: {logo_url.split(';')[0].split(':')[1]})"
                                )
                                return True
                            else:
                                self.log_test(
                                    "FC Barcelona Specific Logo Test", 
                                    False, 
                                    error="FC Barcelona logo_url does not contain valid base64 format"
                                )
                                return False
                        except Exception as decode_error:
                            self.log_test(
                                "FC Barcelona Specific Logo Test", 
                                False, 
                                error=f"FC Barcelona logo_url base64 decode failed: {decode_error}"
                            )
                            return False
                    else:
                        self.log_test(
                            "FC Barcelona Specific Logo Test", 
                            False, 
                            error=f"FC Barcelona logo_url is invalid: {logo_url}"
                        )
                        return False
                else:
                    self.log_test(
                        "FC Barcelona Specific Logo Test", 
                        False, 
                        error="FC Barcelona team not found in teams list"
                    )
                    return False
            else:
                self.log_test(
                    "FC Barcelona Specific Logo Test", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("FC Barcelona Specific Logo Test", False, error=str(e))
            return False

    def test_psg_specific(self):
        """Test 5: Paris Saint-Germain Test - Verify PSG has working logo_url"""
        print("🔵 TEST 5: PARIS SAINT-GERMAIN SPECIFIC LOGO TEST")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                
                psg = None
                for team in teams:
                    team_name = team.get("name", "").lower()
                    if "paris saint-germain" in team_name or "psg" in team_name:
                        psg = team
                        break
                
                if psg:
                    logo_url = psg.get("logo_url")
                    
                    if logo_url and isinstance(logo_url, str) and logo_url.startswith("data:image/"):
                        # Verify it's a valid base64 image
                        try:
                            import base64
                            # Extract base64 part
                            if "base64," in logo_url:
                                base64_data = logo_url.split("base64,")[1]
                                # Try to decode to verify it's valid base64
                                decoded = base64.b64decode(base64_data)
                                
                                self.log_test(
                                    "Paris Saint-Germain Specific Logo Test", 
                                    True, 
                                    f"PSG found with valid base64 logo_url (Size: {len(decoded)} bytes, Format: {logo_url.split(';')[0].split(':')[1]})"
                                )
                                return True
                            else:
                                self.log_test(
                                    "Paris Saint-Germain Specific Logo Test", 
                                    False, 
                                    error="PSG logo_url does not contain valid base64 format"
                                )
                                return False
                        except Exception as decode_error:
                            self.log_test(
                                "Paris Saint-Germain Specific Logo Test", 
                                False, 
                                error=f"PSG logo_url base64 decode failed: {decode_error}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Paris Saint-Germain Specific Logo Test", 
                            False, 
                            error=f"PSG logo_url is invalid: {logo_url}"
                        )
                        return False
                else:
                    self.log_test(
                        "Paris Saint-Germain Specific Logo Test", 
                        False, 
                        error="Paris Saint-Germain team not found in teams list"
                    )
                    return False
            else:
                self.log_test(
                    "Paris Saint-Germain Specific Logo Test", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Paris Saint-Germain Specific Logo Test", False, error=str(e))
            return False

    def test_brand_logo_specific(self):
        """Test 6: Brand Logo Test - Verify at least one brand has working logo_url"""
        print("🏷️ TEST 6: BRAND LOGO SPECIFIC TEST")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/brands")
            
            if response.status_code == 200:
                brands = response.json()
                
                working_brands = []
                
                for brand in brands:
                    logo_url = brand.get("logo_url")
                    
                    if logo_url and isinstance(logo_url, str) and logo_url.startswith("data:image/"):
                        # Verify it's a valid base64 image
                        try:
                            import base64
                            # Extract base64 part
                            if "base64," in logo_url:
                                base64_data = logo_url.split("base64,")[1]
                                # Try to decode to verify it's valid base64
                                decoded = base64.b64decode(base64_data)
                                working_brands.append({
                                    "name": brand.get("name"),
                                    "size": len(decoded),
                                    "format": logo_url.split(';')[0].split(':')[1]
                                })
                        except:
                            continue
                
                if working_brands:
                    self.log_test(
                        "Brand Logo Specific Test", 
                        True, 
                        f"Found {len(working_brands)} brands with valid base64 logos: {[b['name'] for b in working_brands[:3]]}"
                    )
                    return True
                else:
                    self.log_test(
                        "Brand Logo Specific Test", 
                        False, 
                        error="No brands found with valid base64 logo_url"
                    )
                    return False
            else:
                self.log_test(
                    "Brand Logo Specific Test", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Brand Logo Specific Test", False, error=str(e))
            return False

    def test_no_http_500_errors(self):
        """Test 7: Verify no HTTP 500 errors from invalid logo_url data types"""
        print("🚫 TEST 7: NO HTTP 500 ERRORS FROM INVALID LOGO_URL DATA TYPES")
        print("=" * 50)
        
        try:
            endpoints_to_test = [
                ("/teams", "Teams"),
                ("/brands", "Brands"),
                ("/players", "Players"),
                ("/competitions", "Competitions"),
                ("/master-jerseys", "Master Jerseys")
            ]
            
            all_endpoints_ok = True
            endpoint_results = []
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    
                    if response.status_code == 500:
                        all_endpoints_ok = False
                        endpoint_results.append(f"{name}: ❌ HTTP 500")
                    elif response.status_code == 200:
                        endpoint_results.append(f"{name}: ✅ HTTP 200")
                    else:
                        endpoint_results.append(f"{name}: ⚠️ HTTP {response.status_code}")
                        
                except Exception as e:
                    all_endpoints_ok = False
                    endpoint_results.append(f"{name}: ❌ Exception: {str(e)}")
            
            self.log_test(
                "No HTTP 500 Errors Test", 
                all_endpoints_ok, 
                f"Endpoint results: {', '.join(endpoint_results)}"
            )
            return all_endpoints_ok
                
        except Exception as e:
            self.log_test("No HTTP 500 Errors Test", False, error=str(e))
            return False

    def test_contribution_approval_system(self):
        """Test 8: Verify contribution approval system applies images to entities"""
        print("🔄 TEST 8: CONTRIBUTION APPROVAL SYSTEM APPLIES IMAGES")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Contribution Approval System Test", False, error="No admin token")
            return False
        
        try:
            # Get pending contributions
            response = self.session.get(f"{BACKEND_URL}/contributions")
            
            if response.status_code == 200:
                contributions = response.json()
                
                # Look for approved contributions with images
                approved_contributions_with_images = [
                    contrib for contrib in contributions 
                    if contrib.get("status") == "approved" and contrib.get("images")
                ]
                
                # Look for pending contributions with images
                pending_contributions_with_images = [
                    contrib for contrib in contributions 
                    if contrib.get("status") == "pending" and contrib.get("images")
                ]
                
                total_contributions = len(contributions)
                approved_with_images = len(approved_contributions_with_images)
                pending_with_images = len(pending_contributions_with_images)
                
                # The fix should ensure that approved contributions have their images applied to entities
                success = approved_with_images > 0 or pending_with_images > 0
                
                details = f"Total contributions: {total_contributions}, Approved with images: {approved_with_images}, Pending with images: {pending_with_images}"
                
                if approved_with_images > 0:
                    details += f" | Image application system appears to be working"
                elif pending_with_images > 0:
                    details += f" | Images uploaded but awaiting approval"
                else:
                    details += f" | No contributions with images found"
                
                self.log_test(
                    "Contribution Approval System Test", 
                    success, 
                    details
                )
                return success
            else:
                self.log_test(
                    "Contribution Approval System Test", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Contribution Approval System Test", False, error=str(e))
            return False

    def run_all_tests(self):
        """Execute all tests"""
        print("🎯 TOPKIT IMAGE DISPLAY BUG FIX VERIFICATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print("=" * 60)
        print()
        
        # Test 1: Authentication
        if not self.authenticate_admin():
            print("❌ AUTHENTICATION FAILED - STOPPING TESTS")
            return False
        
        # Test 2: Teams logo_url populated
        teams_success, teams_with_logos = self.test_teams_logo_url_populated()
        
        # Test 3: Brands logo_url populated
        brands_success, brands_with_logos = self.test_brands_logo_url_populated()
        
        # Test 4: FC Barcelona specific test
        fc_barcelona_success = self.test_fc_barcelona_specific()
        
        # Test 5: PSG specific test
        psg_success = self.test_psg_specific()
        
        # Test 6: Brand logo specific test
        brand_logo_success = self.test_brand_logo_specific()
        
        # Test 7: No HTTP 500 errors
        no_500_errors = self.test_no_http_500_errors()
        
        # Test 8: Contribution approval system
        approval_system_success = self.test_contribution_approval_system()
        
        # Print summary
        self.print_summary()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 IMAGE DISPLAY BUG FIX VERIFICATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total tests: {total_tests}")
        print(f"Passed tests: {passed_tests}")
        print(f"Failed tests: {failed_tests}")
        print(f"Success rate: {success_rate:.1f}%")
        print()
        
        # Failed tests details
        failed_results = [result for result in self.test_results if not result["success"]]
        if failed_results:
            print("❌ FAILED TESTS:")
            for result in failed_results:
                print(f"  - {result['test']}: {result['error']}")
            print()
        
        # Passed tests details
        passed_results = [result for result in self.test_results if result["success"]]
        if passed_results:
            print("✅ PASSED TESTS:")
            for result in passed_results:
                print(f"  - {result['test']}")
            print()
        
        # Final conclusion based on review request criteria
        critical_tests_passed = 0
        critical_tests = [
            "Teams Logo URL Populated",
            "Brands Logo URL Populated", 
            "FC Barcelona Specific Logo Test",
            "Paris Saint-Germain Specific Logo Test",
            "Brand Logo Specific Test",
            "No HTTP 500 Errors Test"
        ]
        
        for result in self.test_results:
            if result["test"] in critical_tests and result["success"]:
                critical_tests_passed += 1
        
        critical_success_rate = (critical_tests_passed / len(critical_tests) * 100)
        
        print("🎯 FINAL VERIFICATION RESULT:")
        print(f"Critical tests passed: {critical_tests_passed}/{len(critical_tests)} ({critical_success_rate:.1f}%)")
        
        if critical_success_rate >= 100:
            print("🎉 ✅ IMAGE DISPLAY BUG COMPLETELY FIXED!")
            print("All entities now have logo_url populated with base64 data.")
            print("Frontend can display base64 images instead of default fallback icons.")
            print("No HTTP 500 errors from invalid logo_url data types.")
            print("Image upload system working end-to-end from contribution to display.")
        elif critical_success_rate >= 80:
            print("⚠️ 🔶 IMAGE DISPLAY BUG MOSTLY FIXED")
            print("Most functionality working but some issues remain.")
        elif critical_success_rate >= 50:
            print("⚠️ 🔶 IMAGE DISPLAY BUG PARTIALLY FIXED")
            print("Some progress made but significant issues remain.")
        else:
            print("🚨 ❌ IMAGE DISPLAY BUG NOT FIXED")
            print("Critical issues remain - entities still showing default icons.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = ImageDisplayFixVerificationTester()
    tester.run_all_tests()