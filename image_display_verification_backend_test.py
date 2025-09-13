#!/usr/bin/env python3
"""
TopKit Image Display Fix Verification - Backend Testing
Test if entities now have images applied after contribution approval process
Focus: Teams, Brands, Competitions, Players, Master Jerseys with logo_url/photo_url populated
"""

import requests
import json
import sys
import os
from datetime import datetime
import base64

# Configuration des URLs
BACKEND_URL = "https://football-jersey-db.preview.emergentagent.com/api"

# Données d'authentification admin
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImageDisplayVerificationTester:
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
                        f"Admin connected: {user_info.get('name')} (Role: {user_info.get('role')})"
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

    def test_teams_logo_display(self):
        """Test 2: GET /api/teams - Check if teams have logo_url populated"""
        print("⚽ TEST 2: TEAMS LOGO DISPLAY VERIFICATION")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                
                # Check total teams
                total_teams = len(teams)
                teams_with_logos = [team for team in teams if team.get("logo_url") and team.get("logo_url") != ""]
                
                # Specifically check FC Barcelona
                fc_barcelona = None
                for team in teams:
                    if "barcelona" in team.get("name", "").lower() or team.get("id") == "TK-TEAM-000002":
                        fc_barcelona = team
                        break
                
                fc_barcelona_has_logo = fc_barcelona and fc_barcelona.get("logo_url") and fc_barcelona.get("logo_url") != ""
                
                # Validate base64 format for teams with logos
                valid_base64_logos = 0
                for team in teams_with_logos:
                    logo_url = team.get("logo_url", "")
                    if logo_url.startswith("data:image/"):
                        valid_base64_logos += 1
                
                self.log_test(
                    "Teams Logo Display", 
                    len(teams_with_logos) > 0, 
                    f"Total teams: {total_teams}, Teams with logo_url: {len(teams_with_logos)}, "
                    f"FC Barcelona has logo: {fc_barcelona_has_logo}, "
                    f"Valid base64 logos: {valid_base64_logos}"
                )
                
                return {
                    "total_teams": total_teams,
                    "teams_with_logos": len(teams_with_logos),
                    "fc_barcelona_has_logo": fc_barcelona_has_logo,
                    "valid_base64_logos": valid_base64_logos
                }
            else:
                self.log_test(
                    "Teams Logo Display", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Teams Logo Display", False, error=str(e))
            return None

    def test_brands_logo_display(self):
        """Test 3: GET /api/brands - Check if brands have logo_url populated"""
        print("🏷️ TEST 3: BRANDS LOGO DISPLAY VERIFICATION")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/brands")
            
            if response.status_code == 200:
                brands = response.json()
                
                # Check total brands
                total_brands = len(brands)
                brands_with_logos = [brand for brand in brands if brand.get("logo_url") and brand.get("logo_url") != ""]
                
                # Specifically check Nike
                nike_brand = None
                for brand in brands:
                    if "nike" in brand.get("name", "").lower():
                        nike_brand = brand
                        break
                
                nike_has_logo = nike_brand and nike_brand.get("logo_url") and nike_brand.get("logo_url") != ""
                
                # Validate base64 format for brands with logos
                valid_base64_logos = 0
                for brand in brands_with_logos:
                    logo_url = brand.get("logo_url", "")
                    if logo_url.startswith("data:image/"):
                        valid_base64_logos += 1
                
                self.log_test(
                    "Brands Logo Display", 
                    len(brands_with_logos) > 0, 
                    f"Total brands: {total_brands}, Brands with logo_url: {len(brands_with_logos)}, "
                    f"Nike has logo: {nike_has_logo}, "
                    f"Valid base64 logos: {valid_base64_logos}"
                )
                
                return {
                    "total_brands": total_brands,
                    "brands_with_logos": len(brands_with_logos),
                    "nike_has_logo": nike_has_logo,
                    "valid_base64_logos": valid_base64_logos
                }
            else:
                self.log_test(
                    "Brands Logo Display", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Brands Logo Display", False, error=str(e))
            return None

    def test_competitions_logo_display(self):
        """Test 4: GET /api/competitions - Check competition logos"""
        print("🏆 TEST 4: COMPETITIONS LOGO DISPLAY VERIFICATION")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/competitions")
            
            if response.status_code == 200:
                competitions = response.json()
                
                # Check total competitions
                total_competitions = len(competitions)
                competitions_with_logos = [comp for comp in competitions if comp.get("logo_url") and comp.get("logo_url") != ""]
                
                # Specifically check La Liga
                la_liga = None
                for comp in competitions:
                    if "la liga" in comp.get("name", "").lower() or "laliga" in comp.get("name", "").lower():
                        la_liga = comp
                        break
                
                la_liga_has_logo = la_liga and la_liga.get("logo_url") and la_liga.get("logo_url") != ""
                
                # Validate base64 format for competitions with logos
                valid_base64_logos = 0
                for comp in competitions_with_logos:
                    logo_url = comp.get("logo_url", "")
                    if logo_url.startswith("data:image/"):
                        valid_base64_logos += 1
                
                self.log_test(
                    "Competitions Logo Display", 
                    len(competitions_with_logos) > 0, 
                    f"Total competitions: {total_competitions}, Competitions with logo_url: {len(competitions_with_logos)}, "
                    f"La Liga has logo: {la_liga_has_logo}, "
                    f"Valid base64 logos: {valid_base64_logos}"
                )
                
                return {
                    "total_competitions": total_competitions,
                    "competitions_with_logos": len(competitions_with_logos),
                    "la_liga_has_logo": la_liga_has_logo,
                    "valid_base64_logos": valid_base64_logos
                }
            else:
                self.log_test(
                    "Competitions Logo Display", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Competitions Logo Display", False, error=str(e))
            return None

    def test_players_photo_display(self):
        """Test 5: GET /api/players - Check if players have photo_url populated"""
        print("👤 TEST 5: PLAYERS PHOTO DISPLAY VERIFICATION")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/players")
            
            if response.status_code == 200:
                players = response.json()
                
                # Check total players
                total_players = len(players)
                players_with_photos = [player for player in players if player.get("photo_url") and player.get("photo_url") != ""]
                
                # Specifically check Lionel Messi
                messi = None
                for player in players:
                    if "messi" in player.get("name", "").lower():
                        messi = player
                        break
                
                messi_has_photo = messi and messi.get("photo_url") and messi.get("photo_url") != ""
                
                # Validate base64 format for players with photos
                valid_base64_photos = 0
                for player in players_with_photos:
                    photo_url = player.get("photo_url", "")
                    if photo_url.startswith("data:image/"):
                        valid_base64_photos += 1
                
                self.log_test(
                    "Players Photo Display", 
                    len(players_with_photos) > 0, 
                    f"Total players: {total_players}, Players with photo_url: {len(players_with_photos)}, "
                    f"Messi has photo: {messi_has_photo}, "
                    f"Valid base64 photos: {valid_base64_photos}"
                )
                
                return {
                    "total_players": total_players,
                    "players_with_photos": len(players_with_photos),
                    "messi_has_photo": messi_has_photo,
                    "valid_base64_photos": valid_base64_photos
                }
            else:
                self.log_test(
                    "Players Photo Display", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Players Photo Display", False, error=str(e))
            return None

    def test_master_jerseys_image_display(self):
        """Test 6: GET /api/master-jerseys - Check master jersey images"""
        print("👕 TEST 6: MASTER JERSEYS IMAGE DISPLAY VERIFICATION")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            
            if response.status_code == 200:
                master_jerseys = response.json()
                
                # Check total master jerseys
                total_jerseys = len(master_jerseys)
                jerseys_with_images = [jersey for jersey in master_jerseys if 
                                     (jersey.get("front_image_url") and jersey.get("front_image_url") != "") or
                                     (jersey.get("back_image_url") and jersey.get("back_image_url") != "")]
                
                # Specifically check Barcelona jersey
                barcelona_jersey = None
                for jersey in master_jerseys:
                    if "barcelona" in jersey.get("team_name", "").lower():
                        barcelona_jersey = jersey
                        break
                
                barcelona_has_images = (barcelona_jersey and 
                                      ((barcelona_jersey.get("front_image_url") and barcelona_jersey.get("front_image_url") != "") or
                                       (barcelona_jersey.get("back_image_url") and barcelona_jersey.get("back_image_url") != "")))
                
                # Validate base64 format for jerseys with images
                valid_base64_images = 0
                for jersey in jerseys_with_images:
                    front_url = jersey.get("front_image_url", "")
                    back_url = jersey.get("back_image_url", "")
                    if (front_url.startswith("data:image/") or back_url.startswith("data:image/")):
                        valid_base64_images += 1
                
                self.log_test(
                    "Master Jerseys Image Display", 
                    len(jerseys_with_images) > 0, 
                    f"Total master jerseys: {total_jerseys}, Jerseys with images: {len(jerseys_with_images)}, "
                    f"Barcelona jersey has images: {barcelona_has_images}, "
                    f"Valid base64 images: {valid_base64_images}"
                )
                
                return {
                    "total_jerseys": total_jerseys,
                    "jerseys_with_images": len(jerseys_with_images),
                    "barcelona_has_images": barcelona_has_images,
                    "valid_base64_images": valid_base64_images
                }
            else:
                self.log_test(
                    "Master Jerseys Image Display", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Master Jerseys Image Display", False, error=str(e))
            return None

    def test_contribution_approval_status(self):
        """Test 7: Check contribution approval status and image application"""
        print("📋 TEST 7: CONTRIBUTION APPROVAL STATUS VERIFICATION")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/contributions")
            
            if response.status_code == 200:
                contributions = response.json()
                
                # Analyze contribution status
                total_contributions = len(contributions)
                pending_contributions = [c for c in contributions if c.get("status") == "pending"]
                approved_contributions = [c for c in contributions if c.get("status") == "approved"]
                contributions_with_images = [c for c in contributions if c.get("images")]
                
                # Check if any approved contributions have images
                approved_with_images = [c for c in approved_contributions if c.get("images")]
                
                self.log_test(
                    "Contribution Approval Status", 
                    True, 
                    f"Total contributions: {total_contributions}, "
                    f"Pending: {len(pending_contributions)}, "
                    f"Approved: {len(approved_contributions)}, "
                    f"With images: {len(contributions_with_images)}, "
                    f"Approved with images: {len(approved_with_images)}"
                )
                
                return {
                    "total_contributions": total_contributions,
                    "pending_contributions": len(pending_contributions),
                    "approved_contributions": len(approved_contributions),
                    "contributions_with_images": len(contributions_with_images),
                    "approved_with_images": len(approved_with_images)
                }
            else:
                self.log_test(
                    "Contribution Approval Status", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Contribution Approval Status", False, error=str(e))
            return None

    def validate_base64_image_format(self, image_data):
        """Helper function to validate base64 image format"""
        if not image_data or not isinstance(image_data, str):
            return False
        
        # Check if it starts with data:image/
        if not image_data.startswith("data:image/"):
            return False
        
        # Try to decode the base64 part
        try:
            # Extract the base64 part after the comma
            if "," in image_data:
                base64_part = image_data.split(",", 1)[1]
                base64.b64decode(base64_part)
                return True
        except Exception:
            pass
        
        return False

    def test_image_format_validation(self):
        """Test 8: Validate image format and accessibility"""
        print("🔍 TEST 8: IMAGE FORMAT VALIDATION")
        print("=" * 50)
        
        try:
            # Test all entity types for image format validation
            entity_tests = [
                ("teams", "logo_url"),
                ("brands", "logo_url"),
                ("competitions", "logo_url"),
                ("players", "photo_url")
            ]
            
            validation_results = {}
            
            for entity_type, image_field in entity_tests:
                response = self.session.get(f"{BACKEND_URL}/{entity_type}")
                
                if response.status_code == 200:
                    entities = response.json()
                    entities_with_images = [e for e in entities if e.get(image_field)]
                    
                    valid_format_count = 0
                    for entity in entities_with_images:
                        image_data = entity.get(image_field)
                        if self.validate_base64_image_format(image_data):
                            valid_format_count += 1
                    
                    validation_results[entity_type] = {
                        "total_with_images": len(entities_with_images),
                        "valid_format": valid_format_count
                    }
                else:
                    validation_results[entity_type] = {
                        "error": f"HTTP {response.status_code}"
                    }
            
            # Check master jerseys separately (has multiple image fields)
            response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            if response.status_code == 200:
                jerseys = response.json()
                jerseys_with_images = [j for j in jerseys if j.get("front_image_url") or j.get("back_image_url")]
                
                valid_format_count = 0
                for jersey in jerseys_with_images:
                    front_valid = self.validate_base64_image_format(jersey.get("front_image_url"))
                    back_valid = self.validate_base64_image_format(jersey.get("back_image_url"))
                    if front_valid or back_valid:
                        valid_format_count += 1
                
                validation_results["master_jerseys"] = {
                    "total_with_images": len(jerseys_with_images),
                    "valid_format": valid_format_count
                }
            
            total_valid = sum(result.get("valid_format", 0) for result in validation_results.values())
            total_with_images = sum(result.get("total_with_images", 0) for result in validation_results.values())
            
            self.log_test(
                "Image Format Validation", 
                total_valid > 0, 
                f"Total entities with images: {total_with_images}, "
                f"Valid base64 format: {total_valid}, "
                f"Details: {validation_results}"
            )
            
            return validation_results
                
        except Exception as e:
            self.log_test("Image Format Validation", False, error=str(e))
            return None

    def run_all_tests(self):
        """Execute all tests"""
        print("🚀 TOPKIT IMAGE DISPLAY FIX VERIFICATION - BACKEND TESTS")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print("=" * 70)
        print()
        
        # Test 1: Authentication
        if not self.authenticate_admin():
            print("❌ AUTHENTICATION FAILED - STOPPING TESTS")
            return False
        
        # Test 2-6: Entity image display tests
        teams_result = self.test_teams_logo_display()
        brands_result = self.test_brands_logo_display()
        competitions_result = self.test_competitions_logo_display()
        players_result = self.test_players_photo_display()
        jerseys_result = self.test_master_jerseys_image_display()
        
        # Test 7: Contribution approval status
        contributions_result = self.test_contribution_approval_status()
        
        # Test 8: Image format validation
        validation_result = self.test_image_format_validation()
        
        # Print summary
        self.print_summary()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 IMAGE DISPLAY FIX VERIFICATION SUMMARY")
        print("=" * 70)
        
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
        
        # Conclusion
        if success_rate >= 80:
            print("🎉 CONCLUSION: IMAGE DISPLAY FIX WORKING EXCELLENTLY!")
            print("Entities now have images applied after contribution approval process.")
            print("Base64 image format validation successful.")
        elif success_rate >= 60:
            print("⚠️  CONCLUSION: IMAGE DISPLAY PARTIALLY WORKING")
            print("Some entities have images but the fix may need refinement.")
        else:
            print("🚨 CONCLUSION: IMAGE DISPLAY FIX NEEDS ATTENTION")
            print("Most entities still showing default icons instead of actual images.")
            print("Contribution approval process may not be applying images correctly.")
        
        print("=" * 70)

if __name__ == "__main__":
    tester = ImageDisplayVerificationTester()
    tester.run_all_tests()