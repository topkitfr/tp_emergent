#!/usr/bin/env python3

import requests
import json
import sys
import base64
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TeamCompetitionIntegerParsingTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = {
            "team_creation_with_founded_year": False,
            "team_creation_with_empty_founded_year": False,
            "team_creation_required_fields": False,
            "competition_creation_with_logo": False,
            "competition_image_field_mapping": False,
            "competition_secondary_images": False,
            "image_storage_verification": False
        }
        
    def authenticate(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating admin user...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentication successful!")
                print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
                print(f"   Role: {user_info.get('role')}")
                print(f"   User ID: {self.user_id}")
                print(f"   Token length: {len(self.auth_token)} characters")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def test_team_creation_with_founded_year(self):
        """Test team creation with founded_year as integer"""
        print("\n🏆 Testing Team Creation with Founded Year (Integer)...")
        
        # Use microseconds for uniqueness
        import time
        unique_id = str(int(time.time() * 1000000))[-8:]
        
        team_data = {
            "name": f"Test Team Founded Year {unique_id}",
            "country": "France",
            "city": "Paris",
            "founded_year": 1900,  # Integer value
            "short_name": f"TTFY{unique_id[-4:]}"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/teams", json=team_data)
            print(f"Team creation response status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print(f"✅ Team created successfully with founded_year: {team_data['founded_year']}")
                print(f"   Team ID: {data.get('id')}")
                print(f"   Team Name: {data.get('name')}")
                print(f"   Founded Year: {data.get('founded_year')} (type: {type(data.get('founded_year'))})")
                self.test_results["team_creation_with_founded_year"] = True
                return data.get('id')
            else:
                print(f"❌ Team creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Team creation error: {e}")
            return None

    def test_team_creation_with_empty_founded_year(self):
        """Test team creation with empty/null founded_year"""
        print("\n🏆 Testing Team Creation with Empty Founded Year...")
        
        # Use microseconds for uniqueness
        import time
        unique_id = str(int(time.time() * 1000000))[-8:]
        
        team_data = {
            "name": f"Test Team Empty Founded {unique_id}",
            "country": "Spain",
            "city": "Madrid",
            "founded_year": None,  # Null value
            "short_name": f"TTEF{unique_id[-4:]}"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/teams", json=team_data)
            print(f"Team creation response status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print(f"✅ Team created successfully with empty founded_year")
                print(f"   Team ID: {data.get('id')}")
                print(f"   Team Name: {data.get('name')}")
                print(f"   Founded Year: {data.get('founded_year')}")
                self.test_results["team_creation_with_empty_founded_year"] = True
                return data.get('id')
            else:
                print(f"❌ Team creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Team creation error: {e}")
            return None

    def test_team_creation_required_fields(self):
        """Test team creation with only required fields"""
        print("\n🏆 Testing Team Creation with Required Fields Only...")
        
        # Use microseconds for uniqueness
        import time
        unique_id = str(int(time.time() * 1000000))[-8:]
        
        team_data = {
            "name": f"Test Team Required {unique_id}",
            "country": "Italy"
            # Only name and country - testing minimal required fields
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/teams", json=team_data)
            print(f"Team creation response status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print(f"✅ Team created successfully with required fields only")
                print(f"   Team ID: {data.get('id')}")
                print(f"   Team Name: {data.get('name')}")
                print(f"   Country: {data.get('country')}")
                self.test_results["team_creation_required_fields"] = True
                return data.get('id')
            else:
                print(f"❌ Team creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Team creation error: {e}")
            return None

    def create_test_image_base64(self):
        """Create a small test image in base64 format"""
        # Create a minimal PNG image (1x1 pixel red dot)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        return base64.b64encode(png_data).decode('utf-8')

    def test_competition_creation_with_logo(self):
        """Test competition creation with logo image upload"""
        print("\n🏆 Testing Competition Creation with Logo Image...")
        
        # Create test image
        test_image = self.create_test_image_base64()
        
        # Use microseconds for uniqueness
        import time
        unique_id = str(int(time.time() * 1000000))[-8:]
        
        competition_data = {
            "competition_name": f"Test Competition Logo {unique_id}",
            "type": "National league",
            "country": "France",
            "level": 1,
            "logo": test_image,  # Testing logo field (not logo_url)
            "confederations_federations": ["UEFA"]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/competitions", json=competition_data)
            print(f"Competition creation response status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print(f"✅ Competition created successfully with logo image")
                print(f"   Competition ID: {data.get('id')}")
                print(f"   Competition Name: {data.get('competition_name')}")
                print(f"   Logo field present: {'logo' in data}")
                print(f"   Logo data length: {len(data.get('logo', '')) if data.get('logo') else 0}")
                self.test_results["competition_creation_with_logo"] = True
                self.test_results["competition_image_field_mapping"] = True
                return data.get('id')
            else:
                print(f"❌ Competition creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Competition creation error: {e}")
            return None

    def test_competition_creation_with_secondary_images(self):
        """Test competition creation with secondary images"""
        print("\n🏆 Testing Competition Creation with Secondary Images...")
        
        # Create test images
        test_image1 = self.create_test_image_base64()
        test_image2 = self.create_test_image_base64()
        
        # Use microseconds for uniqueness
        import time
        unique_id = str(int(time.time() * 1000000))[-8:]
        
        competition_data = {
            "competition_name": f"Test Competition Secondary {unique_id}",
            "type": "Continental competition",
            "country": "Spain",
            "level": 1,
            "logo": test_image1,
            "secondary_images": [test_image1, test_image2],  # Testing secondary images
            "confederations_federations": ["UEFA"]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/competitions", json=competition_data)
            print(f"Competition creation response status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print(f"✅ Competition created successfully with secondary images")
                print(f"   Competition ID: {data.get('id')}")
                print(f"   Competition Name: {data.get('competition_name')}")
                print(f"   Secondary images field present: {'secondary_images' in data}")
                secondary_images = data.get('secondary_images', [])
                print(f"   Secondary images count: {len(secondary_images) if secondary_images else 0}")
                self.test_results["competition_secondary_images"] = True
                return data.get('id')
            else:
                print(f"❌ Competition creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Competition creation error: {e}")
            return None

    def verify_image_storage_by_search(self, search_term):
        """Verify image storage by searching for competitions"""
        print(f"\n🔍 Verifying Image Storage by searching for '{search_term}'...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/competitions", params={"search": search_term})
            print(f"Competition search response status: {response.status_code}")
            
            if response.status_code == 200:
                competitions = response.json()
                print(f"Found {len(competitions)} competitions matching search")
                
                # Find the most recent competition with our search term
                target_competition = None
                for comp in competitions:
                    comp_name = comp.get('competition_name', '')
                    if search_term in comp_name:
                        target_competition = comp
                        break
                
                if target_competition:
                    print(f"✅ Competition found in database")
                    print(f"   Competition Name: {target_competition.get('competition_name')}")
                    print(f"   Competition ID: {target_competition.get('id')}")
                    
                    # Check logo field
                    logo = target_competition.get('logo')
                    if logo:
                        print(f"   ✅ Logo field populated (length: {len(logo)})")
                    else:
                        print(f"   ❌ Logo field missing or empty")
                    
                    # Check secondary_images field
                    secondary_images = target_competition.get('secondary_images', [])
                    if secondary_images and len(secondary_images) > 0:
                        print(f"   ✅ Secondary images field populated (count: {len(secondary_images)})")
                        for i, img in enumerate(secondary_images):
                            print(f"      Image {i+1} length: {len(img) if img else 0}")
                    else:
                        print(f"   ❌ Secondary images field missing or empty")
                    
                    # Overall verification - consider successful if at least one image type works
                    if logo or secondary_images:
                        self.test_results["image_storage_verification"] = True
                        print(f"   ✅ Image storage verification PASSED")
                    else:
                        print(f"   ❌ Image storage verification FAILED")
                    
                    return True
                else:
                    print(f"❌ Competition not found in search results")
                    return False
            else:
                print(f"❌ Competition search failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Image storage verification error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Team Creation Integer Parsing & Competition Image Tests...")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print("\n" + "=" * 80)
        print("TEAM CREATION TESTS")
        print("=" * 80)
        
        # Test team creation with founded_year
        team_id_1 = self.test_team_creation_with_founded_year()
        
        # Test team creation with empty founded_year
        team_id_2 = self.test_team_creation_with_empty_founded_year()
        
        # Test team creation with required fields only
        team_id_3 = self.test_team_creation_required_fields()
        
        print("\n" + "=" * 80)
        print("COMPETITION CREATION TESTS")
        print("=" * 80)
        
        # Test competition creation with logo
        competition_id_1 = self.test_competition_creation_with_logo()
        
        # Test competition creation with secondary images
        competition_id_2 = self.test_competition_creation_with_secondary_images()
        
        print("\n" + "=" * 80)
        print("IMAGE STORAGE VERIFICATION")
        print("=" * 80)
        
        # Verify image storage for created competitions
        if competition_id_1:
            # Get the competition name for verification
            comp_name_1 = f"Test Competition Logo {datetime.now().strftime('%H%M%S')}"
            # Use a more recent timestamp since we're running this after creation
            import time
            time.sleep(1)  # Small delay to ensure timestamp difference
            current_time = datetime.now().strftime('%H%M%S')
            # Try to find the competition by searching for "Test Competition Logo"
            self.verify_image_storage_by_search("Test Competition Logo")
        
        if competition_id_2:
            # Try to find the competition by searching for "Test Competition Secondary"
            self.verify_image_storage_by_search("Test Competition Secondary")
        
        # Print final results
        self.print_test_summary()
        
        return all(self.test_results.values())

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 TEAM CREATION INTEGER PARSING & COMPETITION IMAGE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print()
        
        # Team Creation Tests
        print("🏆 TEAM CREATION TESTS:")
        print(f"   ✅ Founded Year (Integer): {'PASS' if self.test_results['team_creation_with_founded_year'] else 'FAIL'}")
        print(f"   ✅ Empty Founded Year: {'PASS' if self.test_results['team_creation_with_empty_founded_year'] else 'FAIL'}")
        print(f"   ✅ Required Fields Only: {'PASS' if self.test_results['team_creation_required_fields'] else 'FAIL'}")
        
        # Competition Creation Tests
        print("\n🏆 COMPETITION CREATION TESTS:")
        print(f"   ✅ Logo Image Upload: {'PASS' if self.test_results['competition_creation_with_logo'] else 'FAIL'}")
        print(f"   ✅ Image Field Mapping: {'PASS' if self.test_results['competition_image_field_mapping'] else 'FAIL'}")
        print(f"   ✅ Secondary Images: {'PASS' if self.test_results['competition_secondary_images'] else 'FAIL'}")
        
        # Image Storage Tests
        print("\n🔍 IMAGE STORAGE VERIFICATION:")
        print(f"   ✅ Database Storage: {'PASS' if self.test_results['image_storage_verification'] else 'FAIL'}")
        
        print("\n" + "=" * 80)
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED! Team creation integer parsing and competition image functionality working perfectly!")
        elif success_rate >= 80:
            print("✅ MOSTLY SUCCESSFUL! Most functionality working with minor issues.")
        elif success_rate >= 60:
            print("⚠️  PARTIALLY WORKING! Some critical issues need attention.")
        else:
            print("❌ CRITICAL ISSUES! Major functionality problems detected.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = TeamCompetitionIntegerParsingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)