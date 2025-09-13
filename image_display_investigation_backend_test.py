#!/usr/bin/env python3
"""
TopKit Image Display Investigation - Backend Testing
Focus: Debug why uploaded images show default icons instead of actual images in cards

CRITICAL BUG INVESTIGATION:
1. Database Image Storage Check - Query database to see if teams, brands, competitions, players have logo_url/photo_url fields populated
2. FC Barcelona Test - Check if FC Barcelona team has logo_url field with actual image data  
3. Nike Brand Test - Check if Nike brand has logo_url field populated
4. La Liga Competition Test - Check if La Liga competition has logo_url field
5. Image URLs Validation - Test if image URLs are accessible and returning actual images vs default icons

ROOT CAUSE ANALYSIS:
- Are images being uploaded but not saved to database?
- Are image URLs incorrect or broken?
- Are contributions with images not being applied to main entities?
- Is there a disconnect between contribution system and entity image fields?
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com", 
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com",
    "password": "T0p_Mdp_1288*"
}

class ImageDisplayInvestigator:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        
    def log_result(self, test_name, status, details):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {details}")
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_result("Admin Authentication", "PASS", f"Admin authenticated: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_result("Admin Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", "FAIL", f"Exception: {str(e)}")
            return False
            
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.log_result("User Authentication", "PASS", f"User authenticated: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_result("User Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Authentication", "FAIL", f"Exception: {str(e)}")
            return False

    def investigate_teams_collection(self):
        """Investigate teams collection for image storage"""
        try:
            response = requests.get(f"{BACKEND_URL}/teams")
            if response.status_code == 200:
                teams = response.json()
                total_teams = len(teams)
                teams_with_logos = 0
                fc_barcelona_found = False
                fc_barcelona_data = None
                
                for team in teams:
                    # Check for logo_url field
                    if team.get('logo_url'):
                        teams_with_logos += 1
                    
                    # Look for FC Barcelona specifically
                    if 'barcelona' in team.get('name', '').lower() or 'barça' in team.get('name', '').lower():
                        fc_barcelona_found = True
                        fc_barcelona_data = team
                        
                self.log_result("Teams Collection Analysis", "PASS", 
                    f"Total teams: {total_teams}, Teams with logo_url: {teams_with_logos}, FC Barcelona found: {fc_barcelona_found}")
                
                if fc_barcelona_found:
                    logo_url = fc_barcelona_data.get('logo_url', 'None')
                    self.log_result("FC Barcelona Logo Check", "INFO", 
                        f"FC Barcelona logo_url: {logo_url}, Team ID: {fc_barcelona_data.get('id', 'Unknown')}")
                    
                    # Test if logo URL is accessible
                    if logo_url and logo_url != 'None':
                        self.test_image_url_accessibility(logo_url, "FC Barcelona Logo")
                else:
                    self.log_result("FC Barcelona Search", "WARN", "FC Barcelona team not found in teams collection")
                    
                return True
            else:
                self.log_result("Teams Collection Analysis", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Teams Collection Analysis", "FAIL", f"Exception: {str(e)}")
            return False

    def investigate_brands_collection(self):
        """Investigate brands collection for image storage"""
        try:
            response = requests.get(f"{BACKEND_URL}/brands")
            if response.status_code == 200:
                brands = response.json()
                total_brands = len(brands)
                brands_with_logos = 0
                nike_found = False
                nike_data = None
                
                for brand in brands:
                    # Check for logo_url field
                    if brand.get('logo_url'):
                        brands_with_logos += 1
                    
                    # Look for Nike specifically
                    if 'nike' in brand.get('name', '').lower():
                        nike_found = True
                        nike_data = brand
                        
                self.log_result("Brands Collection Analysis", "PASS", 
                    f"Total brands: {total_brands}, Brands with logo_url: {brands_with_logos}, Nike found: {nike_found}")
                
                if nike_found:
                    logo_url = nike_data.get('logo_url', 'None')
                    self.log_result("Nike Brand Logo Check", "INFO", 
                        f"Nike logo_url: {logo_url}, Brand ID: {nike_data.get('id', 'Unknown')}")
                    
                    # Test if logo URL is accessible
                    if logo_url and logo_url != 'None':
                        self.test_image_url_accessibility(logo_url, "Nike Brand Logo")
                else:
                    self.log_result("Nike Brand Search", "WARN", "Nike brand not found in brands collection")
                    
                return True
            else:
                self.log_result("Brands Collection Analysis", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Brands Collection Analysis", "FAIL", f"Exception: {str(e)}")
            return False

    def investigate_competitions_collection(self):
        """Investigate competitions collection for image storage"""
        try:
            response = requests.get(f"{BACKEND_URL}/competitions")
            if response.status_code == 200:
                competitions = response.json()
                total_competitions = len(competitions)
                competitions_with_logos = 0
                laliga_found = False
                laliga_data = None
                
                for competition in competitions:
                    # Check for logo_url field
                    if competition.get('logo_url'):
                        competitions_with_logos += 1
                    
                    # Look for La Liga specifically
                    comp_name = competition.get('name', '').lower()
                    if 'la liga' in comp_name or 'laliga' in comp_name or 'liga' in comp_name:
                        laliga_found = True
                        laliga_data = competition
                        
                self.log_result("Competitions Collection Analysis", "PASS", 
                    f"Total competitions: {total_competitions}, Competitions with logo_url: {competitions_with_logos}, La Liga found: {laliga_found}")
                
                if laliga_found:
                    logo_url = laliga_data.get('logo_url', 'None')
                    self.log_result("La Liga Competition Logo Check", "INFO", 
                        f"La Liga logo_url: {logo_url}, Competition ID: {laliga_data.get('id', 'Unknown')}")
                    
                    # Test if logo URL is accessible
                    if logo_url and logo_url != 'None':
                        self.test_image_url_accessibility(logo_url, "La Liga Competition Logo")
                else:
                    self.log_result("La Liga Competition Search", "WARN", "La Liga competition not found in competitions collection")
                    
                return True
            else:
                self.log_result("Competitions Collection Analysis", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Competitions Collection Analysis", "FAIL", f"Exception: {str(e)}")
            return False

    def investigate_players_collection(self):
        """Investigate players collection for image storage"""
        try:
            response = requests.get(f"{BACKEND_URL}/players")
            if response.status_code == 200:
                players = response.json()
                total_players = len(players)
                players_with_photos = 0
                messi_found = False
                messi_data = None
                
                for player in players:
                    # Check for photo_url field
                    if player.get('photo_url'):
                        players_with_photos += 1
                    
                    # Look for Messi specifically
                    player_name = player.get('name', '').lower()
                    if 'messi' in player_name or 'lionel' in player_name:
                        messi_found = True
                        messi_data = player
                        
                self.log_result("Players Collection Analysis", "PASS", 
                    f"Total players: {total_players}, Players with photo_url: {players_with_photos}, Messi found: {messi_found}")
                
                if messi_found:
                    photo_url = messi_data.get('photo_url', 'None')
                    self.log_result("Messi Player Photo Check", "INFO", 
                        f"Messi photo_url: {photo_url}, Player ID: {messi_data.get('id', 'Unknown')}")
                    
                    # Test if photo URL is accessible
                    if photo_url and photo_url != 'None':
                        self.test_image_url_accessibility(photo_url, "Messi Player Photo")
                else:
                    self.log_result("Messi Player Search", "WARN", "Messi player not found in players collection")
                    
                return True
            else:
                self.log_result("Players Collection Analysis", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Players Collection Analysis", "FAIL", f"Exception: {str(e)}")
            return False

    def investigate_master_jerseys_collection(self):
        """Investigate master jerseys collection for image storage"""
        try:
            response = requests.get(f"{BACKEND_URL}/master-jerseys")
            if response.status_code == 200:
                jerseys = response.json()
                total_jerseys = len(jerseys)
                jerseys_with_images = 0
                barcelona_jersey_found = False
                barcelona_jersey_data = None
                
                for jersey in jerseys:
                    # Check for image fields
                    if jersey.get('front_photo_url') or jersey.get('back_photo_url'):
                        jerseys_with_images += 1
                    
                    # Look for Barcelona jersey specifically
                    team_name = jersey.get('team', {}).get('name', '').lower() if isinstance(jersey.get('team'), dict) else str(jersey.get('team', '')).lower()
                    if 'barcelona' in team_name or 'barça' in team_name:
                        barcelona_jersey_found = True
                        barcelona_jersey_data = jersey
                        
                self.log_result("Master Jerseys Collection Analysis", "PASS", 
                    f"Total jerseys: {total_jerseys}, Jerseys with images: {jerseys_with_images}, Barcelona jersey found: {barcelona_jersey_found}")
                
                if barcelona_jersey_found:
                    front_url = barcelona_jersey_data.get('front_photo_url', 'None')
                    back_url = barcelona_jersey_data.get('back_photo_url', 'None')
                    self.log_result("Barcelona Jersey Images Check", "INFO", 
                        f"Front photo: {front_url}, Back photo: {back_url}, Jersey ID: {barcelona_jersey_data.get('id', 'Unknown')}")
                    
                    # Test if image URLs are accessible
                    if front_url and front_url != 'None':
                        self.test_image_url_accessibility(front_url, "Barcelona Jersey Front")
                    if back_url and back_url != 'None':
                        self.test_image_url_accessibility(back_url, "Barcelona Jersey Back")
                else:
                    self.log_result("Barcelona Jersey Search", "WARN", "Barcelona jersey not found in master jerseys collection")
                    
                return True
            else:
                self.log_result("Master Jerseys Collection Analysis", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Master Jerseys Collection Analysis", "FAIL", f"Exception: {str(e)}")
            return False

    def test_image_url_accessibility(self, image_url, image_name):
        """Test if an image URL is accessible and returns actual image data"""
        try:
            # Make HEAD request first to check if URL exists
            head_response = requests.head(image_url, timeout=10)
            
            if head_response.status_code == 200:
                content_type = head_response.headers.get('content-type', '').lower()
                content_length = head_response.headers.get('content-length', '0')
                
                if 'image' in content_type:
                    self.log_result(f"{image_name} URL Accessibility", "PASS", 
                        f"Image accessible - Content-Type: {content_type}, Size: {content_length} bytes")
                    
                    # Make GET request to verify actual image data
                    get_response = requests.get(image_url, timeout=10)
                    if get_response.status_code == 200:
                        actual_size = len(get_response.content)
                        if actual_size > 1000:  # Reasonable size for an actual image
                            self.log_result(f"{image_name} Image Data", "PASS", 
                                f"Actual image data retrieved - Size: {actual_size} bytes")
                        else:
                            self.log_result(f"{image_name} Image Data", "WARN", 
                                f"Image data seems too small - Size: {actual_size} bytes (might be placeholder)")
                    else:
                        self.log_result(f"{image_name} Image Data", "FAIL", 
                            f"Failed to retrieve image data - HTTP {get_response.status_code}")
                else:
                    self.log_result(f"{image_name} URL Accessibility", "FAIL", 
                        f"URL accessible but not an image - Content-Type: {content_type}")
            else:
                self.log_result(f"{image_name} URL Accessibility", "FAIL", 
                    f"Image URL not accessible - HTTP {head_response.status_code}")
                    
        except requests.exceptions.Timeout:
            self.log_result(f"{image_name} URL Accessibility", "FAIL", "Request timeout")
        except requests.exceptions.RequestException as e:
            self.log_result(f"{image_name} URL Accessibility", "FAIL", f"Request error: {str(e)}")
        except Exception as e:
            self.log_result(f"{image_name} URL Accessibility", "FAIL", f"Exception: {str(e)}")

    def investigate_contributions_system(self):
        """Investigate contributions system to see if images are being uploaded but not applied"""
        if not self.admin_token:
            self.log_result("Contributions Investigation", "SKIP", "Admin authentication required")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/contributions", headers=headers)
            
            if response.status_code == 200:
                contributions = response.json()
                total_contributions = len(contributions)
                contributions_with_images = 0
                
                for contribution in contributions:
                    # Check if contribution has images
                    if contribution.get('images') or contribution.get('logo') or contribution.get('secondary_photos'):
                        contributions_with_images += 1
                        
                        # Log details about this contribution
                        entity_type = contribution.get('entity_type', 'Unknown')
                        entity_id = contribution.get('entity_id', 'Unknown')
                        status = contribution.get('status', 'Unknown')
                        
                        self.log_result(f"Contribution with Images", "INFO", 
                            f"Entity: {entity_type}, ID: {entity_id}, Status: {status}, Has images: True")
                
                self.log_result("Contributions System Analysis", "PASS", 
                    f"Total contributions: {total_contributions}, Contributions with images: {contributions_with_images}")
                
                return True
            else:
                self.log_result("Contributions System Analysis", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Contributions System Analysis", "FAIL", f"Exception: {str(e)}")
            return False

    def run_comprehensive_investigation(self):
        """Run comprehensive image display investigation"""
        print("🔍 TOPKIT IMAGE DISPLAY INVESTIGATION - BACKEND TESTING")
        print("=" * 80)
        print("Focus: Debug why uploaded images show default icons instead of actual images")
        print()
        
        # Authentication
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        
        if not admin_auth and not user_auth:
            print("❌ CRITICAL: No authentication successful - cannot proceed with investigation")
            return
        
        print("\n🔍 DATABASE IMAGE STORAGE INVESTIGATION")
        print("-" * 50)
        
        # Investigate all collections for image storage
        self.investigate_teams_collection()
        self.investigate_brands_collection()
        self.investigate_competitions_collection()
        self.investigate_players_collection()
        self.investigate_master_jerseys_collection()
        
        print("\n🔍 CONTRIBUTIONS SYSTEM INVESTIGATION")
        print("-" * 50)
        
        # Investigate contributions system
        self.investigate_contributions_system()
        
        # Summary
        print("\n📊 INVESTIGATION SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warnings}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Root cause analysis
        print("\n🔍 ROOT CAUSE ANALYSIS")
        print("-" * 30)
        
        # Analyze results to identify root cause
        image_storage_issues = []
        accessibility_issues = []
        
        for result in self.test_results:
            if 'logo_url' in result['details'] or 'photo_url' in result['details']:
                if 'None' in result['details']:
                    image_storage_issues.append(result['test'])
            if 'URL Accessibility' in result['test'] and result['status'] == 'FAIL':
                accessibility_issues.append(result['test'])
        
        if image_storage_issues:
            print(f"🚨 IMAGE STORAGE ISSUES DETECTED: {len(image_storage_issues)} entities missing image URLs")
            for issue in image_storage_issues:
                print(f"   - {issue}")
        
        if accessibility_issues:
            print(f"🚨 IMAGE ACCESSIBILITY ISSUES DETECTED: {len(accessibility_issues)} broken image URLs")
            for issue in accessibility_issues:
                print(f"   - {issue}")
        
        if not image_storage_issues and not accessibility_issues:
            print("✅ No obvious image storage or accessibility issues detected")
            print("🔍 Issue might be in frontend rendering or card display logic")
        
        return success_rate > 70

if __name__ == "__main__":
    investigator = ImageDisplayInvestigator()
    success = investigator.run_comprehensive_investigation()
    
    if success:
        print("\n🎉 IMAGE DISPLAY INVESTIGATION COMPLETED SUCCESSFULLY")
    else:
        print("\n❌ IMAGE DISPLAY INVESTIGATION COMPLETED WITH ISSUES")
    
    sys.exit(0 if success else 1)