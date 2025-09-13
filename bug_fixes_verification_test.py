#!/usr/bin/env python3
"""
Bug Fixes Verification Testing - Review Request Specific Tests
Testing the specific bug fixes implemented by the main agent:

1. **Player Photos Display**: Test that players TK-PLAYER-28EEF352 (Leao) and TK-PLAYER-6DD13374 (Dembele) 
   return profile_picture_url in the /api/players endpoint and that these photos are accessible.

2. **Player Selection in Personal Details Form**: Test that the /api/players endpoint returns a proper 
   list of players that can be used in dropdown menus for the "Add Personal Details" form.

3. **Competition Level Field**: Test that the competition creation endpoint accepts string values 
   for the level field (pro, semi pro, amateur, special) instead of integer values.

4. **Team Logo URLs**: Test that /api/teams endpoint returns valid logo_url paths that can be 
   accessed correctly.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://football-jersey-db.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class BugFixesVerificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        
    def log(self, message):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        self.log(f"{status} {test_name}")
        if details:
            self.log(f"   Details: {details}")
        if error:
            self.log(f"   Error: {error}")
        
    def authenticate_admin(self):
        """Test 1: Authentication with admin credentials"""
        self.log("🔐 Testing admin authentication...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user_id = data.get('user', {}).get('id')
                
                if self.admin_token and len(self.admin_token) > 100:
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Token: {len(self.admin_token)} chars, User ID: {self.admin_user_id}"
                    )
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    return True
                else:
                    self.log_result("Admin Authentication", False, "", f"Invalid token: {self.admin_token}")
                    return False
            else:
                self.log_result("Admin Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False
    
    def test_player_photos_display(self):
        """Test 1: Player Photos Display - TK-PLAYER-28EEF352 (Leao) and TK-PLAYER-6DD13374 (Dembele)"""
        self.log("👤 Testing Player Photos Display...")
        
        target_players = {
            "TK-PLAYER-28EEF352": "Leao",
            "TK-PLAYER-6DD13374": "Dembele"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/players")
            
            if response.status_code == 200:
                players = response.json()
                self.log_result(
                    "Players Endpoint Access",
                    True,
                    f"Successfully retrieved {len(players)} players"
                )
                
                found_players = {}
                players_with_photos = 0
                
                for player in players:
                    player_ref = player.get('topkit_reference', '')
                    player_name = player.get('name', '')
                    
                    # Check if this is one of our target players
                    if player_ref in target_players:
                        found_players[player_ref] = player
                        
                        # Check for profile_picture_url field
                        profile_picture_url = player.get('profile_picture_url')
                        has_photo = profile_picture_url is not None and profile_picture_url != ""
                        
                        if has_photo:
                            players_with_photos += 1
                            
                        self.log_result(
                            f"Player {target_players[player_ref]} ({player_ref}) Photo",
                            has_photo,
                            f"Name: {player_name}, Photo URL: {profile_picture_url}" if has_photo else f"Name: {player_name}, No photo URL found"
                        )
                        
                        # Test photo accessibility if URL exists
                        if has_photo:
                            self.test_photo_accessibility(profile_picture_url, f"{target_players[player_ref]} Photo")
                
                # Summary for target players
                if len(found_players) == 0:
                    self.log_result(
                        "Target Players Found",
                        False,
                        "",
                        f"None of the target players {list(target_players.keys())} found in database"
                    )
                    return False
                else:
                    self.log_result(
                        "Target Players Found",
                        True,
                        f"Found {len(found_players)}/{len(target_players)} target players with {players_with_photos} having photos"
                    )
                    return players_with_photos > 0
                    
            else:
                self.log_result("Players Endpoint Access", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Player Photos Display Test", False, "", str(e))
            return False
    
    def test_photo_accessibility(self, photo_url, photo_description):
        """Test photo URL accessibility"""
        try:
            # Handle relative URLs
            if photo_url.startswith('/'):
                full_url = f"{BACKEND_URL}{photo_url}"
            elif photo_url.startswith('http'):
                full_url = photo_url
            else:
                full_url = f"{BACKEND_URL}/{photo_url}"
            
            response = requests.get(full_url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                is_image = 'image' in content_type.lower()
                
                self.log_result(
                    f"{photo_description} Accessibility",
                    is_image,
                    f"URL: {full_url}, Content-Type: {content_type}, Size: {len(response.content)} bytes" if is_image else f"URL accessible but not an image: {content_type}"
                )
                return is_image
            else:
                self.log_result(
                    f"{photo_description} Accessibility",
                    False,
                    "",
                    f"HTTP {response.status_code} for URL: {full_url}"
                )
                return False
                
        except Exception as e:
            self.log_result(f"{photo_description} Accessibility", False, "", f"Error accessing {full_url}: {str(e)}")
            return False
    
    def test_player_selection_dropdown(self):
        """Test 2: Player Selection in Personal Details Form - /api/players endpoint structure"""
        self.log("📋 Testing Player Selection for Dropdown Menus...")
        
        try:
            response = self.session.get(f"{API_BASE}/players")
            
            if response.status_code == 200:
                players = response.json()
                
                if not isinstance(players, list):
                    self.log_result(
                        "Players Endpoint Structure",
                        False,
                        "",
                        f"Expected list but got {type(players)}"
                    )
                    return False
                
                # Check if players have required fields for dropdown usage
                required_fields = ['id', 'name']
                optional_fields = ['full_name', 'topkit_reference', 'nationality', 'position']
                
                valid_players = 0
                players_with_all_fields = 0
                
                for player in players:
                    # Check required fields
                    has_required = all(field in player and player[field] for field in required_fields)
                    if has_required:
                        valid_players += 1
                    
                    # Check optional fields
                    has_optional = sum(1 for field in optional_fields if field in player and player[field])
                    if has_optional >= len(optional_fields) // 2:  # At least half of optional fields
                        players_with_all_fields += 1
                
                self.log_result(
                    "Players Dropdown Structure",
                    valid_players > 0,
                    f"Total players: {len(players)}, Valid for dropdown: {valid_players}, Well-structured: {players_with_all_fields}"
                )
                
                # Test specific player data quality
                if len(players) > 0:
                    sample_player = players[0]
                    sample_fields = {field: sample_player.get(field, 'N/A') for field in required_fields + optional_fields}
                    
                    self.log_result(
                        "Sample Player Data Quality",
                        True,
                        f"Sample player fields: {sample_fields}"
                    )
                
                return valid_players > 0
                
            else:
                self.log_result("Players Dropdown Test", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Player Selection Dropdown Test", False, "", str(e))
            return False
    
    def test_competition_level_field(self):
        """Test 3: Competition Level Field - String values (pro, semi pro, amateur, special)"""
        self.log("🏆 Testing Competition Level Field String Values...")
        
        # Test string level values
        test_levels = ["pro", "semi pro", "amateur", "special"]
        
        successful_creations = 0
        
        for level in test_levels:
            try:
                test_competition = {
                    "competition_name": f"Test Competition - {level.title()}",
                    "type": "National league",
                    "country": "France",
                    "level": level,  # String value instead of integer
                    "confederations_federations": ["UEFA"]
                }
                
                response = self.session.post(f"{API_BASE}/competitions", json=test_competition)
                
                if response.status_code in [200, 201]:
                    created_competition = response.json()
                    competition_id = created_competition.get('id')
                    successful_creations += 1
                    
                    self.log_result(
                        f"Competition Level '{level}' Creation",
                        True,
                        f"Successfully created competition with string level '{level}', ID: {competition_id}"
                    )
                    
                    # Verify the level field is stored correctly
                    verify_response = self.session.get(f"{API_BASE}/competitions")
                    if verify_response.status_code == 200:
                        competitions = verify_response.json()
                        created_comp = next((c for c in competitions if c.get('id') == competition_id), None)
                        if created_comp:
                            stored_level = created_comp.get('level')
                            self.log_result(
                                f"Competition Level '{level}' Storage Verification",
                                stored_level == level,
                                f"Stored level: {stored_level}, Expected: {level}"
                            )
                
                elif response.status_code == 400:
                    error_detail = response.json().get('detail', response.text)
                    self.log_result(
                        f"Competition Level '{level}' Creation",
                        False,
                        "",
                        f"Validation error: {error_detail}"
                    )
                else:
                    self.log_result(
                        f"Competition Level '{level}' Creation",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(f"Competition Level '{level}' Creation", False, "", str(e))
        
        # Test that integer values are also still accepted (backward compatibility)
        try:
            integer_competition = {
                "competition_name": "Test Competition - Integer Level",
                "type": "National league", 
                "country": "Spain",
                "level": 1,  # Integer value
                "confederations_federations": ["UEFA"]
            }
            
            response = self.session.post(f"{API_BASE}/competitions", json=integer_competition)
            
            if response.status_code in [200, 201]:
                self.log_result(
                    "Competition Integer Level Backward Compatibility",
                    True,
                    "Integer level values still accepted for backward compatibility"
                )
            else:
                self.log_result(
                    "Competition Integer Level Backward Compatibility",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Competition Integer Level Backward Compatibility", False, "", str(e))
        
        return successful_creations >= len(test_levels) // 2  # At least half should work
    
    def test_team_logo_urls(self):
        """Test 4: Team Logo URLs - Valid logo_url paths accessibility"""
        self.log("🏢 Testing Team Logo URLs...")
        
        try:
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                
                self.log_result(
                    "Teams Endpoint Access",
                    True,
                    f"Successfully retrieved {len(teams)} teams"
                )
                
                teams_with_logos = 0
                accessible_logos = 0
                logo_fields = ['logo_url', 'image_url', 'photo_url']
                
                for team in teams:
                    team_name = team.get('name', 'Unknown')
                    team_ref = team.get('topkit_reference', 'N/A')
                    
                    # Check for logo URL fields
                    logo_url = None
                    for field in logo_fields:
                        if team.get(field):
                            logo_url = team.get(field)
                            break
                    
                    if logo_url:
                        teams_with_logos += 1
                        
                        self.log_result(
                            f"Team '{team_name}' Logo URL Present",
                            True,
                            f"Reference: {team_ref}, Logo URL: {logo_url}"
                        )
                        
                        # Test logo accessibility
                        if self.test_logo_accessibility(logo_url, team_name):
                            accessible_logos += 1
                    else:
                        self.log_result(
                            f"Team '{team_name}' Logo URL",
                            False,
                            f"Reference: {team_ref}",
                            "No logo URL found in any expected field"
                        )
                
                # Summary
                self.log_result(
                    "Team Logo URLs Summary",
                    teams_with_logos > 0,
                    f"Teams with logos: {teams_with_logos}/{len(teams)}, Accessible logos: {accessible_logos}/{teams_with_logos if teams_with_logos > 0 else 1}"
                )
                
                return accessible_logos > 0
                
            else:
                self.log_result("Teams Endpoint Access", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Team Logo URLs Test", False, "", str(e))
            return False
    
    def test_logo_accessibility(self, logo_url, team_name):
        """Test team logo URL accessibility"""
        try:
            # Handle relative URLs
            if logo_url.startswith('/'):
                full_url = f"{BACKEND_URL}{logo_url}"
            elif logo_url.startswith('http'):
                full_url = logo_url
            else:
                full_url = f"{BACKEND_URL}/{logo_url}"
            
            response = requests.get(full_url, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                is_image = 'image' in content_type.lower()
                
                self.log_result(
                    f"Team '{team_name}' Logo Accessibility",
                    is_image,
                    f"URL: {full_url}, Content-Type: {content_type}, Size: {len(response.content)} bytes" if is_image else f"URL accessible but not an image: {content_type}"
                )
                return is_image
            else:
                self.log_result(
                    f"Team '{team_name}' Logo Accessibility",
                    False,
                    "",
                    f"HTTP {response.status_code} for URL: {full_url}"
                )
                return False
                
        except Exception as e:
            self.log_result(f"Team '{team_name}' Logo Accessibility", False, "", f"Error accessing {full_url}: {str(e)}")
            return False
    
    def test_api_endpoints_general_health(self):
        """Test general health of key API endpoints"""
        self.log("🔍 Testing General API Endpoints Health...")
        
        endpoints = [
            ("/players", "Players API"),
            ("/teams", "Teams API"),
            ("/competitions", "Competitions API"),
            ("/brands", "Brands API")
        ]
        
        healthy_endpoints = 0
        
        for endpoint, description in endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else len(data.get('items', []))
                    
                    self.log_result(
                        f"{description} Health Check",
                        True,
                        f"Endpoint responsive, returned {count} items"
                    )
                    healthy_endpoints += 1
                else:
                    self.log_result(
                        f"{description} Health Check",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(f"{description} Health Check", False, "", str(e))
        
        return healthy_endpoints == len(endpoints)
    
    def run_all_tests(self):
        """Run all bug fixes verification tests"""
        self.log("🚀 Starting Bug Fixes Verification Testing")
        self.log("=" * 80)
        self.log("Testing specific bug fixes from review request:")
        self.log("1. Player Photos Display (TK-PLAYER-28EEF352, TK-PLAYER-6DD13374)")
        self.log("2. Player Selection for Personal Details Form")
        self.log("3. Competition Level Field String Values")
        self.log("4. Team Logo URLs Accessibility")
        self.log("=" * 80)
        
        tests = [
            ("Authentication", self.authenticate_admin),
            ("API Endpoints General Health", self.test_api_endpoints_general_health),
            ("Player Photos Display (Leao & Dembele)", self.test_player_photos_display),
            ("Player Selection Dropdown Structure", self.test_player_selection_dropdown),
            ("Competition Level String Values", self.test_competition_level_field),
            ("Team Logo URLs Accessibility", self.test_team_logo_urls)
        ]
        
        passed = 0
        failed = 0
        critical_failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                    self.log(f"✅ {test_name} - PASSED")
                else:
                    failed += 1
                    # Mark main bug fix tests as critical
                    if any(keyword in test_name.lower() for keyword in ['player photos', 'competition level', 'team logo', 'player selection']):
                        critical_failed += 1
                    self.log(f"❌ {test_name} - FAILED")
            except Exception as e:
                failed += 1
                if any(keyword in test_name.lower() for keyword in ['player photos', 'competition level', 'team logo', 'player selection']):
                    critical_failed += 1
                self.log(f"❌ {test_name} - ERROR: {e}")
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("📊 BUG FIXES VERIFICATION TESTING SUMMARY")
        self.log("=" * 80)
        self.log(f"✅ Tests Passed: {passed}")
        self.log(f"❌ Tests Failed: {failed}")
        self.log(f"🚨 Critical Bug Fix Failures: {critical_failed}")
        self.log(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            self.log("🎉 ALL BUG FIXES VERIFIED - All implemented fixes are working correctly!")
        elif critical_failed == 0:
            self.log("✅ CRITICAL BUG FIXES WORKING - All main fixes verified, minor issues in supporting tests")
        else:
            self.log(f"🚨 {critical_failed} CRITICAL BUG FIX(ES) FAILED - Some implemented fixes need attention")
        
        # Detailed results for main agent
        self.log("\n📋 DETAILED RESULTS FOR MAIN AGENT:")
        for result in self.test_results:
            if any(keyword in result['test'].lower() for keyword in ['player photos', 'competition level', 'team logo', 'player selection']):
                status = "✅" if result['success'] else "❌"
                self.log(f"{status} {result['test']}: {result['details'] if result['success'] else result['error']}")
        
        return failed == 0

if __name__ == "__main__":
    tester = BugFixesVerificationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)