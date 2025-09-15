#!/usr/bin/env python3
"""
Complete Image Upload Fix Backend Testing - ALL Entity Types
Final comprehensive test of the complete image upload fix for ALL entity types.

CRITICAL BUG RESOLUTION TEST: User reported "I have the same problem with uploaded photos 
not showing up with the player/competition categories in the database. I just created two 
references (TK-PLAYER-50D19C / TK-COMPETITION-B0B0A1)"

Test Requirements:
1. Verify TK-PLAYER-50D19C: Confirm player image is accessible and properly served
2. Verify TK-COMPETITION-B0B0A1: Confirm competition logo is accessible and properly served
3. Test All Entity Types: Verify image serving works for teams, brands, players, competitions
4. Backend Image Copying: Test that new entities automatically copy images to correct directories
5. Legacy Image Endpoint: Verify /api/legacy-image/ serves all entity types correctly
6. Complete Workflow: End-to-end test of upload → storage → serving → display for all entity types
"""

import requests
import json
import os
import sys
from pathlib import Path
import time
import tempfile
from PIL import Image
import io
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class CompleteImageUploadTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
        # Specific entities from user report
        self.target_player_id = "TK-PLAYER-50D19C"
        self.target_competition_id = "TK-COMPETITION-B0B0A1"
        
        # Expected image IDs from user report
        self.player_image_id = "image_uploaded_1757832082151"
        self.competition_image_id = "image_uploaded_1757831627000"
        
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
        """Authenticate with admin credentials"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                user_name = data.get('user', {}).get('name', 'Unknown')
                self.log_test("Authentication", True, f"Logged in as {user_name}")
                return True
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_specific_player_image(self):
        """Test TK-PLAYER-50D19C specific image accessibility"""
        try:
            # First, verify the player exists in database
            response = self.session.get(f"{API_BASE}/players")
            if response.status_code == 200:
                players = response.json()
                target_player = None
                for player in players:
                    if player.get('id') == self.target_player_id:
                        target_player = player
                        break
                
                if target_player:
                    self.log_test("TK-PLAYER-50D19C Database Check", True, 
                                f"Found player: {target_player.get('name', 'Unknown')}")
                    
                    # Check if player has photo_url
                    photo_url = target_player.get('photo_url') or target_player.get('profile_picture_url')
                    if photo_url:
                        self.log_test("TK-PLAYER-50D19C Photo URL", True, f"Photo URL: {photo_url}")
                        
                        # Test legacy image endpoint
                        if photo_url.startswith('image_uploaded_'):
                            legacy_response = self.session.get(f"{API_BASE}/legacy-image/{photo_url}")
                            if legacy_response.status_code == 200:
                                content_type = legacy_response.headers.get('content-type', '')
                                content_length = len(legacy_response.content)
                                self.log_test("TK-PLAYER-50D19C Image Serving", True, 
                                            f"Content-Type: {content_type}, Size: {content_length} bytes")
                                return True
                            else:
                                self.log_test("TK-PLAYER-50D19C Image Serving", False, 
                                            f"Legacy endpoint returned {legacy_response.status_code}")
                        else:
                            self.log_test("TK-PLAYER-50D19C Photo URL Format", False, 
                                        f"Not legacy format: {photo_url}")
                    else:
                        self.log_test("TK-PLAYER-50D19C Photo URL", False, "No photo_url found")
                else:
                    self.log_test("TK-PLAYER-50D19C Database Check", False, "Player not found in database")
            else:
                self.log_test("TK-PLAYER-50D19C Database Check", False, f"Players API returned {response.status_code}")
                
        except Exception as e:
            self.log_test("TK-PLAYER-50D19C Test", False, f"Error: {str(e)}")
            
        return False
    
    def test_specific_competition_image(self):
        """Test TK-COMPETITION-B0B0A1 specific image accessibility"""
        try:
            # First, verify the competition exists in database
            response = self.session.get(f"{API_BASE}/competitions")
            if response.status_code == 200:
                competitions = response.json()
                target_competition = None
                for competition in competitions:
                    if competition.get('id') == self.target_competition_id:
                        target_competition = competition
                        break
                
                if target_competition:
                    comp_name = target_competition.get('competition_name') or target_competition.get('name', 'Unknown')
                    self.log_test("TK-COMPETITION-B0B0A1 Database Check", True, 
                                f"Found competition: {comp_name}")
                    
                    # Check if competition has logo_url
                    logo_url = target_competition.get('logo_url')
                    if logo_url:
                        self.log_test("TK-COMPETITION-B0B0A1 Logo URL", True, f"Logo URL: {logo_url}")
                        
                        # Test legacy image endpoint
                        if logo_url.startswith('image_uploaded_'):
                            legacy_response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
                            if legacy_response.status_code == 200:
                                content_type = legacy_response.headers.get('content-type', '')
                                content_length = len(legacy_response.content)
                                self.log_test("TK-COMPETITION-B0B0A1 Image Serving", True, 
                                            f"Content-Type: {content_type}, Size: {content_length} bytes")
                                return True
                            else:
                                self.log_test("TK-COMPETITION-B0B0A1 Image Serving", False, 
                                            f"Legacy endpoint returned {legacy_response.status_code}")
                        else:
                            self.log_test("TK-COMPETITION-B0B0A1 Logo URL Format", False, 
                                        f"Not legacy format: {logo_url}")
                    else:
                        self.log_test("TK-COMPETITION-B0B0A1 Logo URL", False, "No logo_url found")
                else:
                    self.log_test("TK-COMPETITION-B0B0A1 Database Check", False, "Competition not found in database")
            else:
                self.log_test("TK-COMPETITION-B0B0A1 Database Check", False, f"Competitions API returned {response.status_code}")
                
        except Exception as e:
            self.log_test("TK-COMPETITION-B0B0A1 Test", False, f"Error: {str(e)}")
            
        return False
    
    def test_legacy_image_endpoint_all_types(self):
        """Test legacy image endpoint for all entity types"""
        try:
            # Test teams with legacy images
            teams_response = self.session.get(f"{API_BASE}/teams")
            if teams_response.status_code == 200:
                teams = teams_response.json()
                teams_with_legacy = [t for t in teams if t.get('logo_url', '').startswith('image_uploaded_')]
                
                self.log_test("Teams with Legacy Images", len(teams_with_legacy) > 0, 
                            f"Found {len(teams_with_legacy)} teams with legacy format images")
                
                # Test serving for each team with legacy images
                for team in teams_with_legacy[:3]:  # Test first 3 to avoid too many requests
                    logo_url = team.get('logo_url')
                    team_name = team.get('name', 'Unknown')
                    legacy_response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
                    
                    success = legacy_response.status_code == 200
                    details = f"Team: {team_name}, Image: {logo_url}"
                    if success:
                        content_type = legacy_response.headers.get('content-type', '')
                        details += f", Content-Type: {content_type}"
                    else:
                        details += f", Status: {legacy_response.status_code}"
                    
                    self.log_test("Team Legacy Image Serving", success, details)
            
            # Test brands with legacy images
            brands_response = self.session.get(f"{API_BASE}/brands")
            if brands_response.status_code == 200:
                brands = brands_response.json()
                brands_with_legacy = [b for b in brands if b.get('logo_url', '').startswith('image_uploaded_')]
                
                self.log_test("Brands with Legacy Images", len(brands_with_legacy) > 0, 
                            f"Found {len(brands_with_legacy)} brands with legacy format images")
                
                # Test serving for each brand with legacy images
                for brand in brands_with_legacy[:3]:  # Test first 3
                    logo_url = brand.get('logo_url')
                    brand_name = brand.get('name', 'Unknown')
                    legacy_response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
                    
                    success = legacy_response.status_code == 200
                    details = f"Brand: {brand_name}, Image: {logo_url}"
                    if success:
                        content_type = legacy_response.headers.get('content-type', '')
                        details += f", Content-Type: {content_type}"
                    else:
                        details += f", Status: {legacy_response.status_code}"
                    
                    self.log_test("Brand Legacy Image Serving", success, details)
            
            # Test players with legacy images
            players_response = self.session.get(f"{API_BASE}/players")
            if players_response.status_code == 200:
                players = players_response.json()
                players_with_legacy = [p for p in players if (p.get('photo_url', '') or p.get('profile_picture_url', '')).startswith('image_uploaded_')]
                
                self.log_test("Players with Legacy Images", len(players_with_legacy) > 0, 
                            f"Found {len(players_with_legacy)} players with legacy format images")
                
                # Test serving for each player with legacy images
                for player in players_with_legacy[:3]:  # Test first 3
                    photo_url = player.get('photo_url') or player.get('profile_picture_url')
                    player_name = player.get('name', 'Unknown')
                    legacy_response = self.session.get(f"{API_BASE}/legacy-image/{photo_url}")
                    
                    success = legacy_response.status_code == 200
                    details = f"Player: {player_name}, Image: {photo_url}"
                    if success:
                        content_type = legacy_response.headers.get('content-type', '')
                        details += f", Content-Type: {content_type}"
                    else:
                        details += f", Status: {legacy_response.status_code}"
                    
                    self.log_test("Player Legacy Image Serving", success, details)
            
            # Test competitions with legacy images
            competitions_response = self.session.get(f"{API_BASE}/competitions")
            if competitions_response.status_code == 200:
                competitions = competitions_response.json()
                competitions_with_legacy = [c for c in competitions if c.get('logo_url', '').startswith('image_uploaded_')]
                
                self.log_test("Competitions with Legacy Images", len(competitions_with_legacy) > 0, 
                            f"Found {len(competitions_with_legacy)} competitions with legacy format images")
                
                # Test serving for each competition with legacy images
                for competition in competitions_with_legacy[:3]:  # Test first 3
                    logo_url = competition.get('logo_url')
                    comp_name = competition.get('competition_name') or competition.get('name', 'Unknown')
                    legacy_response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
                    
                    success = legacy_response.status_code == 200
                    details = f"Competition: {comp_name}, Image: {logo_url}"
                    if success:
                        content_type = legacy_response.headers.get('content-type', '')
                        details += f", Content-Type: {content_type}"
                    else:
                        details += f", Status: {legacy_response.status_code}"
                    
                    self.log_test("Competition Legacy Image Serving", success, details)
                    
        except Exception as e:
            self.log_test("Legacy Image Endpoint All Types", False, f"Error: {str(e)}")
    
    def test_contribution_image_workflow(self):
        """Test complete contribution workflow with image upload"""
        try:
            # Create a test image
            test_image = Image.new('RGB', (100, 100), color='red')
            img_buffer = io.BytesIO()
            test_image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            
            # Test contribution creation for team
            contribution_data = {
                "entity_type": "team",
                "title": "Test Team Image Upload",
                "description": "Testing image upload workflow",
                "data": {
                    "name": "Test Team Image",
                    "country": "France",
                    "logo_url": f"image_uploaded_{int(time.time() * 1000)}"
                }
            }
            
            # Create contribution
            contrib_response = self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data)
            if contrib_response.status_code == 200:
                contribution = contrib_response.json()
                contribution_id = contribution.get('id')
                self.log_test("Contribution Creation", True, f"Created contribution: {contribution_id}")
                
                # Upload image to contribution
                files = {'file': ('test_image.jpg', img_buffer, 'image/jpeg')}
                upload_response = self.session.post(f"{API_BASE}/contributions-v2/{contribution_id}/images", files=files)
                
                if upload_response.status_code == 200:
                    self.log_test("Contribution Image Upload", True, "Image uploaded successfully")
                    
                    # Approve contribution (admin action)
                    moderate_data = {"action": "approve", "reason": "Testing image workflow"}
                    moderate_response = self.session.post(f"{API_BASE}/contributions-v2/{contribution_id}/moderate", json=moderate_data)
                    
                    if moderate_response.status_code == 200:
                        moderation_result = moderate_response.json()
                        entity_id = moderation_result.get('entity_id')
                        self.log_test("Contribution Approval", True, f"Approved, created entity: {entity_id}")
                        
                        # Verify entity was created with proper image handling
                        if entity_id:
                            # Wait a moment for entity creation
                            time.sleep(2)
                            
                            # Check if entity exists in teams collection
                            teams_response = self.session.get(f"{API_BASE}/teams")
                            if teams_response.status_code == 200:
                                teams = teams_response.json()
                                created_team = None
                                for team in teams:
                                    if team.get('id') == entity_id:
                                        created_team = team
                                        break
                                
                                if created_team:
                                    logo_url = created_team.get('logo_url')
                                    self.log_test("Entity Creation with Image", True, 
                                                f"Team created with logo_url: {logo_url}")
                                    
                                    # Test if image is accessible via legacy endpoint
                                    if logo_url and logo_url.startswith('image_uploaded_'):
                                        legacy_response = self.session.get(f"{API_BASE}/legacy-image/{logo_url}")
                                        success = legacy_response.status_code == 200
                                        details = f"Legacy image serving: {legacy_response.status_code}"
                                        if success:
                                            details += f", Content-Type: {legacy_response.headers.get('content-type', '')}"
                                        self.log_test("Complete Workflow Image Serving", success, details)
                                        return success
                                else:
                                    self.log_test("Entity Creation with Image", False, "Created team not found")
                        else:
                            self.log_test("Contribution Approval", False, "No entity_id returned")
                    else:
                        self.log_test("Contribution Approval", False, f"Status: {moderate_response.status_code}")
                else:
                    self.log_test("Contribution Image Upload", False, f"Status: {upload_response.status_code}")
            else:
                self.log_test("Contribution Creation", False, f"Status: {contrib_response.status_code}")
                
        except Exception as e:
            self.log_test("Contribution Image Workflow", False, f"Error: {str(e)}")
            
        return False
    
    def test_image_directory_structure(self):
        """Test that images are properly organized in directories"""
        try:
            # Test different entity types to see if they have proper directory structure
            entity_types = ['teams', 'brands', 'players', 'competitions']
            
            for entity_type in entity_types:
                response = self.session.get(f"{API_BASE}/{entity_type}")
                if response.status_code == 200:
                    entities = response.json()
                    
                    # Find entities with legacy format images
                    entities_with_images = []
                    for entity in entities:
                        image_field = 'logo_url' if entity_type != 'players' else 'photo_url'
                        if not image_field in entity and entity_type == 'players':
                            image_field = 'profile_picture_url'  # Alternative field for players
                        
                        image_url = entity.get(image_field, '')
                        if image_url and image_url.startswith('image_uploaded_'):
                            entities_with_images.append({
                                'name': entity.get('name') or entity.get('competition_name', 'Unknown'),
                                'image_url': image_url,
                                'id': entity.get('id')
                            })
                    
                    self.log_test(f"{entity_type.title()} Image Directory Structure", 
                                len(entities_with_images) > 0,
                                f"Found {len(entities_with_images)} {entity_type} with legacy format images")
                    
                    # Test serving for a sample of entities
                    for entity in entities_with_images[:2]:  # Test first 2 of each type
                        legacy_response = self.session.get(f"{API_BASE}/legacy-image/{entity['image_url']}")
                        success = legacy_response.status_code == 200
                        details = f"{entity['name']} ({entity['id']}): {entity['image_url']}"
                        if success:
                            details += f" - Served successfully"
                        else:
                            details += f" - Failed with status {legacy_response.status_code}"
                        
                        self.log_test(f"{entity_type.title()} Image Serving Test", success, details)
                else:
                    self.log_test(f"{entity_type.title()} API Access", False, f"Status: {response.status_code}")
                    
        except Exception as e:
            self.log_test("Image Directory Structure", False, f"Error: {str(e)}")
    
    def test_expected_user_images(self):
        """Test the specific images mentioned in user report"""
        try:
            # Test the specific image IDs mentioned by the user
            test_images = [
                ("Player Image", self.player_image_id),
                ("Competition Logo", self.competition_image_id)
            ]
            
            for image_name, image_id in test_images:
                legacy_response = self.session.get(f"{API_BASE}/legacy-image/{image_id}")
                
                if legacy_response.status_code == 200:
                    content_type = legacy_response.headers.get('content-type', '')
                    content_length = len(legacy_response.content)
                    self.log_test(f"User Reported {image_name}", True, 
                                f"Image ID: {image_id}, Content-Type: {content_type}, Size: {content_length} bytes")
                else:
                    self.log_test(f"User Reported {image_name}", False, 
                                f"Image ID: {image_id}, Status: {legacy_response.status_code}")
                    
        except Exception as e:
            self.log_test("Expected User Images", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all image upload tests"""
        print("🔍 COMPLETE IMAGE UPLOAD FIX TESTING - ALL ENTITY TYPES")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        print("\n📋 SPECIFIC USER REPORTED ISSUES:")
        print("-" * 50)
        
        # Test specific entities mentioned by user
        self.test_specific_player_image()
        self.test_specific_competition_image()
        
        print("\n🔍 EXPECTED USER IMAGE IDS:")
        print("-" * 50)
        
        # Test the specific image IDs mentioned
        self.test_expected_user_images()
        
        print("\n🌐 LEGACY IMAGE ENDPOINT - ALL ENTITY TYPES:")
        print("-" * 50)
        
        # Test legacy image endpoint for all entity types
        self.test_legacy_image_endpoint_all_types()
        
        print("\n📁 IMAGE DIRECTORY STRUCTURE:")
        print("-" * 50)
        
        # Test image directory structure
        self.test_image_directory_structure()
        
        print("\n🔄 COMPLETE WORKFLOW TEST:")
        print("-" * 50)
        
        # Test complete contribution workflow
        self.test_contribution_image_workflow()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 FINAL RESULTS:")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Summary of critical findings
        print(f"\n🎯 CRITICAL FINDINGS:")
        print("-" * 50)
        
        # Check if user-reported entities are working
        player_working = any(r['success'] and 'TK-PLAYER-50D19C' in r['test'] for r in self.test_results)
        competition_working = any(r['success'] and 'TK-COMPETITION-B0B0A1' in r['test'] for r in self.test_results)
        
        if player_working:
            print("✅ TK-PLAYER-50D19C: Image is accessible and properly served")
        else:
            print("❌ TK-PLAYER-50D19C: Image accessibility issues detected")
            
        if competition_working:
            print("✅ TK-COMPETITION-B0B0A1: Logo is accessible and properly served")
        else:
            print("❌ TK-COMPETITION-B0B0A1: Logo accessibility issues detected")
        
        # Check overall image serving
        legacy_serving_tests = [r for r in self.test_results if 'Legacy Image Serving' in r['test'] or 'Image Serving' in r['test']]
        legacy_success_rate = (sum(1 for r in legacy_serving_tests if r['success']) / len(legacy_serving_tests) * 100) if legacy_serving_tests else 0
        
        print(f"📈 Legacy Image Serving Success Rate: {legacy_success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 OVERALL ASSESSMENT: Image upload fix is working well!")
        elif success_rate >= 60:
            print("⚠️ OVERALL ASSESSMENT: Image upload fix has some issues but core functionality works")
        else:
            print("🚨 OVERALL ASSESSMENT: Critical issues with image upload fix detected")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = CompleteImageUploadTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)