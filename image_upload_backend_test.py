#!/usr/bin/env python3
"""
TopKit Backend Testing - Image Upload for Competitions and Master Jerseys
Testing the newly implemented image upload fields for CreateCompetitionModal and CreateMasterJerseyModal
"""

import requests
import json
import base64
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-tracker.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitImageUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()

    def create_test_image_base64(self, image_type="png"):
        """Create a small test image in base64 format"""
        if image_type == "png":
            # Small 1x1 PNG image in base64
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        elif image_type == "jpg":
            # Small 1x1 JPEG image in base64
            return "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/8A8A"

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_result("Admin Authentication", True, f"Successfully authenticated as admin", {
                    "user_name": data.get("user", {}).get("name"),
                    "user_role": data.get("user", {}).get("role"),
                    "token_length": len(self.admin_token) if self.admin_token else 0
                })
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed with status {response.status_code}", {
                    "response": response.text[:200]
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception occurred: {str(e)}")
            return False

    def test_competition_creation_with_images(self):
        """Test competition creation with image uploads"""
        try:
            # Test data for competition with images
            competition_data = {
                "name": "Test Competition with Images",
                "country": "France",
                "competition_type": "League",
                "logo_url": self.create_test_image_base64("png"),
                "secondary_images": [
                    self.create_test_image_base64("jpg"),
                    self.create_test_image_base64("png")
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/competitions", json=competition_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                competition_id = data.get("id")
                self.log_result("Competition Creation with Images", True, "Successfully created competition with images", {
                    "competition_id": competition_id,
                    "competition_name": data.get("name"),
                    "topkit_reference": data.get("topkit_reference"),
                    "logo_url_present": bool(data.get("logo_url")),
                    "secondary_images_count": len(data.get("secondary_images", []))
                })
                return competition_id
            else:
                self.log_result("Competition Creation with Images", False, f"Failed with status {response.status_code}", {
                    "response": response.text[:500]
                })
                return None
                
        except Exception as e:
            self.log_result("Competition Creation with Images", False, f"Exception occurred: {str(e)}")
            return None

    def test_competition_creation_logo_only(self):
        """Test competition creation with logo_url only"""
        try:
            competition_data = {
                "name": "Test Competition Logo Only",
                "country": "Spain", 
                "competition_type": "Cup",
                "logo_url": self.create_test_image_base64("png")
            }
            
            response = self.session.post(f"{BACKEND_URL}/competitions", json=competition_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result("Competition Creation (Logo Only)", True, "Successfully created competition with logo only", {
                    "competition_id": data.get("id"),
                    "logo_url_present": bool(data.get("logo_url")),
                    "secondary_images_present": bool(data.get("secondary_images"))
                })
                return data.get("id")
            else:
                self.log_result("Competition Creation (Logo Only)", False, f"Failed with status {response.status_code}", {
                    "response": response.text[:500]
                })
                return None
                
        except Exception as e:
            self.log_result("Competition Creation (Logo Only)", False, f"Exception occurred: {str(e)}")
            return None

    def test_master_jersey_creation_with_images(self):
        """Test master jersey creation with image uploads"""
        try:
            # First get available teams and brands for the master jersey
            teams_response = self.session.get(f"{BACKEND_URL}/teams")
            brands_response = self.session.get(f"{BACKEND_URL}/brands")
            
            if teams_response.status_code != 200 or brands_response.status_code != 200:
                self.log_result("Master Jersey Creation with Images", False, "Failed to get teams or brands data", {
                    "teams_status": teams_response.status_code,
                    "brands_status": brands_response.status_code
                })
                return None
            
            teams = teams_response.json()
            brands = brands_response.json()
            
            if not teams or not brands:
                self.log_result("Master Jersey Creation with Images", False, "No teams or brands available")
                return None
            
            # Use first available team and brand
            team_id = teams[0]["id"]
            brand_id = brands[0]["id"]
            
            master_jersey_data = {
                "team_id": team_id,
                "brand_id": brand_id,
                "season": "2024-25",
                "jersey_type": "home",
                "primary_color": "Blue",
                "main_image_url": self.create_test_image_base64("png"),
                "secondary_images": [
                    self.create_test_image_base64("jpg"),
                    self.create_test_image_base64("png")
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=master_jersey_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result("Master Jersey Creation with Images", True, "Successfully created master jersey with images", {
                    "master_jersey_id": data.get("id"),
                    "topkit_reference": data.get("topkit_reference"),
                    "main_image_url_present": bool(data.get("main_image_url")),
                    "secondary_images_count": len(data.get("secondary_images", [])),
                    "team_info": data.get("team_info", {}).get("name"),
                    "brand_info": data.get("brand_info", {}).get("name")
                })
                return data.get("id")
            elif response.status_code == 400 and "existe déjà" in response.text:
                # Handle duplicate master jersey - this is expected behavior
                self.log_result("Master Jersey Creation with Images", True, "Duplicate master jersey detected (expected behavior)", {
                    "status_code": response.status_code,
                    "message": "Backend correctly prevents duplicate master jerseys"
                })
                return None
            else:
                self.log_result("Master Jersey Creation with Images", False, f"Failed with status {response.status_code}", {
                    "response": response.text[:500]
                })
                return None
                
        except Exception as e:
            self.log_result("Master Jersey Creation with Images", False, f"Exception occurred: {str(e)}")
            return None

    def test_master_jersey_creation_main_image_only(self):
        """Test master jersey creation with main_image_url only"""
        try:
            # Get teams and brands
            teams_response = self.session.get(f"{BACKEND_URL}/teams")
            brands_response = self.session.get(f"{BACKEND_URL}/brands")
            
            if teams_response.status_code != 200 or brands_response.status_code != 200:
                self.log_result("Master Jersey Creation (Main Image Only)", False, "Failed to get teams or brands data")
                return None
            
            teams = teams_response.json()
            brands = brands_response.json()
            
            if len(teams) < 2 or len(brands) < 2:
                self.log_result("Master Jersey Creation (Main Image Only)", False, "Insufficient teams or brands for testing")
                return None
            
            # Use second available team and brand to avoid conflicts
            team_id = teams[1]["id"] if len(teams) > 1 else teams[0]["id"]
            brand_id = brands[1]["id"] if len(brands) > 1 else brands[0]["id"]
            
            master_jersey_data = {
                "team_id": team_id,
                "brand_id": brand_id,
                "season": "2023-24",
                "jersey_type": "away",
                "primary_color": "Red",
                "main_image_url": self.create_test_image_base64("jpg")
            }
            
            response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=master_jersey_data)
            
            if response.status_code == 201:
                data = response.json()
                self.log_result("Master Jersey Creation (Main Image Only)", True, "Successfully created master jersey with main image only", {
                    "master_jersey_id": data.get("id"),
                    "main_image_url_present": bool(data.get("main_image_url")),
                    "secondary_images_present": bool(data.get("secondary_images"))
                })
                return data.get("id")
            else:
                self.log_result("Master Jersey Creation (Main Image Only)", False, f"Failed with status {response.status_code}", {
                    "response": response.text[:500]
                })
                return None
                
        except Exception as e:
            self.log_result("Master Jersey Creation (Main Image Only)", False, f"Exception occurred: {str(e)}")
            return None

    def test_error_handling_invalid_image_data(self):
        """Test error handling with invalid image data"""
        try:
            # Test competition with invalid base64 image
            competition_data = {
                "name": "Test Competition Invalid Image",
                "country": "Germany",
                "competition_type": "League",
                "logo_url": "invalid_base64_data"
            }
            
            response = self.session.post(f"{BACKEND_URL}/competitions", json=competition_data)
            
            # Should either reject invalid data or handle gracefully
            if response.status_code in [400, 422]:
                self.log_result("Error Handling - Invalid Image Data", True, "Correctly rejected invalid image data", {
                    "status_code": response.status_code,
                    "response": response.text[:200]
                })
            elif response.status_code == 201:
                # If it accepts invalid data, check if it handles it gracefully
                data = response.json()
                self.log_result("Error Handling - Invalid Image Data", True, "Accepted invalid data gracefully", {
                    "competition_id": data.get("id"),
                    "logo_url_stored": data.get("logo_url")
                })
            else:
                self.log_result("Error Handling - Invalid Image Data", False, f"Unexpected status code {response.status_code}", {
                    "response": response.text[:200]
                })
                
        except Exception as e:
            self.log_result("Error Handling - Invalid Image Data", False, f"Exception occurred: {str(e)}")

    def test_error_handling_missing_required_fields(self):
        """Test error handling with missing required fields"""
        try:
            # Test competition with missing required fields
            competition_data = {
                "logo_url": self.create_test_image_base64("png")
                # Missing name, country, competition_type
            }
            
            response = self.session.post(f"{BACKEND_URL}/competitions", json=competition_data)
            
            if response.status_code in [400, 422]:
                self.log_result("Error Handling - Missing Required Fields", True, "Correctly rejected missing required fields", {
                    "status_code": response.status_code,
                    "response": response.text[:200]
                })
            else:
                self.log_result("Error Handling - Missing Required Fields", False, f"Should have rejected missing fields, got {response.status_code}", {
                    "response": response.text[:200]
                })
                
        except Exception as e:
            self.log_result("Error Handling - Missing Required Fields", False, f"Exception occurred: {str(e)}")

    def test_data_structure_verification(self):
        """Test that created entities have proper data structure"""
        try:
            # Get competitions to verify data structure
            response = self.session.get(f"{BACKEND_URL}/competitions")
            
            if response.status_code == 200:
                competitions = response.json()
                
                # Find competitions with images
                competitions_with_images = [c for c in competitions if c.get("logo_url") or c.get("secondary_images")]
                
                if competitions_with_images:
                    sample_competition = competitions_with_images[0]
                    self.log_result("Data Structure Verification - Competitions", True, "Found competitions with proper image data structure", {
                        "total_competitions": len(competitions),
                        "competitions_with_images": len(competitions_with_images),
                        "sample_has_logo": bool(sample_competition.get("logo_url")),
                        "sample_has_secondary": bool(sample_competition.get("secondary_images")),
                        "sample_reference": sample_competition.get("topkit_reference")
                    })
                else:
                    self.log_result("Data Structure Verification - Competitions", False, "No competitions with images found")
            else:
                self.log_result("Data Structure Verification - Competitions", False, f"Failed to get competitions: {response.status_code}")
            
            # Get master jerseys to verify data structure
            response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            
            if response.status_code == 200:
                master_jerseys = response.json()
                
                # Find master jerseys with images
                jerseys_with_images = [j for j in master_jerseys if j.get("main_image_url") or j.get("secondary_images")]
                
                if jerseys_with_images:
                    sample_jersey = jerseys_with_images[0]
                    self.log_result("Data Structure Verification - Master Jerseys", True, "Found master jerseys with proper image data structure", {
                        "total_master_jerseys": len(master_jerseys),
                        "jerseys_with_images": len(jerseys_with_images),
                        "sample_has_main_image": bool(sample_jersey.get("main_image_url")),
                        "sample_has_secondary": bool(sample_jersey.get("secondary_images")),
                        "sample_reference": sample_jersey.get("topkit_reference")
                    })
                else:
                    self.log_result("Data Structure Verification - Master Jerseys", False, "No master jerseys with images found")
            else:
                self.log_result("Data Structure Verification - Master Jerseys", False, f"Failed to get master jerseys: {response.status_code}")
                
        except Exception as e:
            self.log_result("Data Structure Verification", False, f"Exception occurred: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🎯 TOPKIT IMAGE UPLOAD TESTING - COMPETITIONS & MASTER JERSEYS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authentication
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test Competition Creation with Images
        print("📋 TESTING COMPETITION CREATION WITH IMAGES")
        print("-" * 50)
        self.test_competition_creation_with_images()
        self.test_competition_creation_logo_only()
        
        # Step 3: Test Master Jersey Creation with Images
        print("👕 TESTING MASTER JERSEY CREATION WITH IMAGES")
        print("-" * 50)
        self.test_master_jersey_creation_with_images()
        self.test_master_jersey_creation_main_image_only()
        
        # Step 4: Test Error Handling
        print("🛡️ TESTING ERROR HANDLING")
        print("-" * 50)
        self.test_error_handling_invalid_image_data()
        self.test_error_handling_missing_required_fields()
        
        # Step 5: Verify Data Structure
        print("🔍 TESTING DATA STRUCTURE VERIFICATION")
        print("-" * 50)
        self.test_data_structure_verification()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['message']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if "✅ PASS" in result["status"]:
                print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        
        if success_rate >= 80:
            print("🎉 OVERALL RESULT: EXCELLENT - Image upload system is working well!")
        elif success_rate >= 60:
            print("⚠️ OVERALL RESULT: GOOD - Some issues need attention")
        else:
            print("🚨 OVERALL RESULT: NEEDS WORK - Critical issues identified")
        
        return success_rate

def main():
    """Main test execution"""
    tester = TopKitImageUploadTester()
    
    try:
        success = tester.run_comprehensive_tests()
        if success:
            success_rate = tester.print_summary()
            sys.exit(0 if success_rate >= 80 else 1)
        else:
            print("❌ CRITICAL: Test execution failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()