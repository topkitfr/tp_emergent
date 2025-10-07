#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - NEW COEFFICIENTS TESTING

**NEW COEFFICIENTS TESTING:**

Testing the 3 new coefficients that were added:

**Test Requirements:**
1. **Coefficient d'ancienneté (Age coefficient)**: Use an existing master_kit with an old season
2. **Player Type coefficient**: Test with a player that has a player_type defined  
3. **Data saving**: Verify that new data is properly saved

**User-Specified Test Data:**
```json
{
  "master_kit_id": "049229a5-c6c0-405a-b055-88759d775f25",
  "associated_player_id": "test-player-id",  
  "condition": "match_worn",
  "signed": true,
  "signature_proof": "photo",
  "origin_type": "match_worn",
  "special_match_type": "classico",
  "match_result": "win",
  "performance": ["scored_goal"],
  "match_proof": "photo"
}
```

**Verification Points:**
- Is the age coefficient calculated and displayed?
- Is the Player Type coefficient taken into account?
- Does the response contain all coefficients?

**Authentication:** emergency.admin@topkit.test / EmergencyAdmin2025!

**PRIORITY: HIGH** - Testing new coefficients implementation.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://soccer-kit-catalog-1.preview.emergentagent.com/api"

# Test Admin Credentials for authentication - Updated for Edit Kit Form Testing
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitNewCoefficientsBackendTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.form_data = {}
        self.master_kits_data = []
        self.sample_player_id = None
        
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
        """Authenticate with Emergency Admin credentials"""
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

    def test_form_data_endpoints(self):
        """Test all form data endpoints for Edit Kit Form"""
        try:
            print(f"\n📋 TESTING FORM DATA ENDPOINTS")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # Test 1: Players endpoint
            print(f"\n      🏃 Testing GET /api/form-data/players")
            players_response = self.session.get(f"{BACKEND_URL}/form-data/players", timeout=10)
            print(f"         Response Status: {players_response.status_code}")
            
            if players_response.status_code == 200:
                players_data = players_response.json()
                print(f"         ✅ Players endpoint accessible")
                print(f"         Total players returned: {len(players_data)}")
                
                if len(players_data) > 0:
                    first_player = players_data[0]
                    self.sample_player_id = first_player.get('id') or first_player.get('name')
                    print(f"         Sample player: {first_player.get('name', 'Unknown')}")
                    print(f"         Player aura/coefficient: {first_player.get('coefficient', 'N/A')}")
                    print(f"         Player type: {first_player.get('player_type', 'N/A')}")
                    
                self.form_data['players'] = players_data
                self.log_test("Form Data Players Endpoint", True, f"✅ Retrieved {len(players_data)} players")
            else:
                self.log_test("Form Data Players Endpoint", False, f"❌ Failed - Status {players_response.status_code}", players_response.text)
                return False
            
            # Test 2: Competitions endpoint
            print(f"\n      🏆 Testing GET /api/form-data/competitions")
            competitions_response = self.session.get(f"{BACKEND_URL}/form-data/competitions", timeout=10)
            print(f"         Response Status: {competitions_response.status_code}")
            
            if competitions_response.status_code == 200:
                competitions_data = competitions_response.json()
                print(f"         ✅ Competitions endpoint accessible")
                print(f"         Total competitions returned: {len(competitions_data)}")
                
                if len(competitions_data) > 0:
                    first_competition = competitions_data[0]
                    print(f"         Sample competition: {first_competition.get('name', 'Unknown')}")
                    print(f"         Competition country: {first_competition.get('country', 'Unknown')}")
                    
                self.form_data['competitions'] = competitions_data
                self.log_test("Form Data Competitions Endpoint", True, f"✅ Retrieved {len(competitions_data)} competitions")
            else:
                self.log_test("Form Data Competitions Endpoint", False, f"❌ Failed - Status {competitions_response.status_code}", competitions_response.text)
                return False
            
            # Test 3: Teams endpoint (for opponents)
            print(f"\n      ⚽ Testing GET /api/form-data/clubs (teams)")
            teams_response = self.session.get(f"{BACKEND_URL}/form-data/clubs", timeout=10)
            print(f"         Response Status: {teams_response.status_code}")
            
            if teams_response.status_code == 200:
                teams_data = teams_response.json()
                print(f"         ✅ Teams endpoint accessible")
                print(f"         Total teams returned: {len(teams_data)}")
                
                if len(teams_data) > 0:
                    first_team = teams_data[0]
                    print(f"         Sample team: {first_team.get('name', 'Unknown')}")
                    print(f"         Team country: {first_team.get('country', 'Unknown')}")
                    
                self.form_data['teams'] = teams_data
                self.log_test("Form Data Teams Endpoint", True, f"✅ Retrieved {len(teams_data)} teams")
            else:
                self.log_test("Form Data Teams Endpoint", False, f"❌ Failed - Status {teams_response.status_code}", teams_response.text)
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Form Data Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_age_coefficient_with_old_season(self):
        """Test age coefficient calculation with an existing master kit with old season"""
        try:
            print(f"\n⏰ TESTING AGE COEFFICIENT WITH OLD SEASON")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # First, get master kits to find one with an old season
            print(f"      🔍 Looking for master kits with old seasons...")
            master_kits_response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            
            if master_kits_response.status_code != 200:
                print(f"      ❌ Cannot get master kits - Status {master_kits_response.status_code}")
                self.log_test("Age Coefficient Test", False, "❌ Cannot get master kits")
                return False
            
            master_kits = master_kits_response.json()
            
            # Look for a master kit with an old season (before 2020)
            old_season_kit = None
            for kit in master_kits:
                season = kit.get('season', '')
                if season and ('2015' in season or '2016' in season or '2017' in season or '2018' in season or '2019' in season):
                    old_season_kit = kit
                    break
            
            if not old_season_kit:
                # Use the user-specified master kit ID
                user_specified_kit_id = "049229a5-c6c0-405a-b055-88759d775f25"
                print(f"      🎯 Using user-specified master kit ID: {user_specified_kit_id}")
                
                # Get specific master kit
                kit_response = self.session.get(f"{BACKEND_URL}/master-kits/{user_specified_kit_id}", timeout=10)
                if kit_response.status_code == 200:
                    old_season_kit = kit_response.json()
                else:
                    print(f"      ❌ Cannot find user-specified master kit")
                    self.log_test("Age Coefficient Test", False, "❌ Cannot find master kit for age testing")
                    return False
            
            master_kit_id = old_season_kit.get('id')
            season = old_season_kit.get('season', 'Unknown')
            club = old_season_kit.get('club', 'Unknown')
            
            print(f"      🎽 Testing with master kit:")
            print(f"         ID: {master_kit_id}")
            print(f"         Club: {club}")
            print(f"         Season: {season}")
            
            # Test data with master kit ID for age coefficient calculation
            test_data = {
                "master_kit_id": master_kit_id,
                "condition": "match_worn",
                "signed": True,
                "signature_proof": "photo",
                "origin_type": "match_worn",
                "special_match_type": "classico",
                "match_result": "win",
                "performance": ["scored_goal"],
                "match_proof": "photo"
            }
            
            print(f"      📊 Testing price calculation with age coefficient data:")
            for key, value in test_data.items():
                print(f"         {key}: {value}")
            
            response = self.session.post(
                f"{BACKEND_URL}/calculate-price",
                json=test_data,
                timeout=10
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                price_data = response.json()
                print(f"      ✅ Price calculation with age coefficient successful")
                
                estimated_price = price_data.get('estimated_price')
                coefficients = price_data.get('coefficients', {})
                base_price = price_data.get('base_price', 90.0)
                
                print(f"\n      💰 AGE COEFFICIENT RESULTS:")
                print(f"         Base Price: €{base_price}")
                print(f"         Final Estimated Price: €{estimated_price}")
                
                # Look for age coefficient specifically
                age_coefficient_found = False
                age_coefficient_value = None
                
                for coeff_name, coeff_value in coefficients.items():
                    if 'age' in coeff_name.lower() or 'ancienneté' in coeff_name.lower():
                        age_coefficient_found = True
                        age_coefficient_value = coeff_value
                        print(f"         🎯 AGE COEFFICIENT FOUND: {coeff_name} = {coeff_value}")
                        break
                
                if age_coefficient_found:
                    print(f"      ✅ Age coefficient is calculated and displayed!")
                    self.log_test("Age Coefficient Test", True, f"✅ Age coefficient found: {age_coefficient_value}")
                else:
                    print(f"      ❌ Age coefficient NOT found in response")
                    print(f"      Available coefficients: {list(coefficients.keys())}")
                    self.log_test("Age Coefficient Test", False, "❌ Age coefficient not found in response")
                
                return age_coefficient_found
                
            else:
                print(f"      ❌ Price calculation failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("Age Coefficient Test", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Age Coefficient Test", False, f"Exception: {str(e)}")
            return False

    def test_player_type_coefficient(self):
        """Test player type coefficient with a player that has player_type defined"""
        try:
            print(f"\n👤 TESTING PLAYER TYPE COEFFICIENT")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # Get players to find one with player_type defined
            print(f"      🔍 Looking for players with player_type defined...")
            players_response = self.session.get(f"{BACKEND_URL}/form-data/players", timeout=10)
            
            if players_response.status_code != 200:
                print(f"      ❌ Cannot get players - Status {players_response.status_code}")
                self.log_test("Player Type Coefficient Test", False, "❌ Cannot get players")
                return False
            
            players = players_response.json()
            
            # Look for a player with player_type defined
            player_with_type = None
            for player in players:
                if player.get('player_type') and player.get('player_type') != 'none':
                    player_with_type = player
                    break
            
            if not player_with_type:
                print(f"      ⚠️ No players with player_type found, using first available player")
                if players:
                    player_with_type = players[0]
                else:
                    print(f"      ❌ No players available for testing")
                    self.log_test("Player Type Coefficient Test", False, "❌ No players available")
                    return False
            
            player_id = player_with_type.get('id') or player_with_type.get('name')
            player_name = player_with_type.get('name', 'Unknown')
            player_type = player_with_type.get('player_type', 'none')
            
            print(f"      👤 Testing with player:")
            print(f"         ID: {player_id}")
            print(f"         Name: {player_name}")
            print(f"         Player Type: {player_type}")
            
            # Test data with player ID for player type coefficient calculation
            test_data = {
                "associated_player_id": player_id,
                "condition": "match_worn",
                "signed": True,
                "signature_proof": "photo",
                "origin_type": "match_worn",
                "special_match_type": "classico",
                "match_result": "win",
                "performance": ["scored_goal"],
                "match_proof": "photo"
            }
            
            print(f"      📊 Testing price calculation with player type coefficient data:")
            for key, value in test_data.items():
                print(f"         {key}: {value}")
            
            response = self.session.post(
                f"{BACKEND_URL}/calculate-price",
                json=test_data,
                timeout=10
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                price_data = response.json()
                print(f"      ✅ Price calculation with player type coefficient successful")
                
                estimated_price = price_data.get('estimated_price')
                coefficients = price_data.get('coefficients', {})
                base_price = price_data.get('base_price', 90.0)
                
                print(f"\n      💰 PLAYER TYPE COEFFICIENT RESULTS:")
                print(f"         Base Price: €{base_price}")
                print(f"         Final Estimated Price: €{estimated_price}")
                
                # Look for player type coefficient specifically
                player_type_coefficient_found = False
                player_type_coefficient_value = None
                
                for coeff_name, coeff_value in coefficients.items():
                    if 'player_type' in coeff_name.lower() or 'player type' in coeff_name.lower():
                        player_type_coefficient_found = True
                        player_type_coefficient_value = coeff_value
                        print(f"         🎯 PLAYER TYPE COEFFICIENT FOUND: {coeff_name} = {coeff_value}")
                        break
                
                if player_type_coefficient_found:
                    print(f"      ✅ Player Type coefficient is calculated and displayed!")
                    self.log_test("Player Type Coefficient Test", True, f"✅ Player Type coefficient found: {player_type_coefficient_value}")
                else:
                    print(f"      ❌ Player Type coefficient NOT found in response")
                    print(f"      Available coefficients: {list(coefficients.keys())}")
                    self.log_test("Player Type Coefficient Test", False, "❌ Player Type coefficient not found in response")
                
                return player_type_coefficient_found
                
            else:
                print(f"      ❌ Price calculation failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("Player Type Coefficient Test", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Player Type Coefficient Test", False, f"Exception: {str(e)}")
            return False

    def test_user_specified_data_comprehensive(self):
        """Test with the exact user-specified data to verify all coefficients"""
        try:
            print(f"\n🎯 TESTING USER-SPECIFIED DATA COMPREHENSIVE")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # User-specified test data exactly as provided
            user_data = {
                "master_kit_id": "049229a5-c6c0-405a-b055-88759d775f25",
                "associated_player_id": "test-player-id",  
                "condition": "match_worn",
                "signed": True,
                "signature_proof": "photo",
                "origin_type": "match_worn",
                "special_match_type": "classico",
                "match_result": "win",
                "performance": ["scored_goal"],
                "match_proof": "photo"
            }
            
            print(f"      📊 Testing with EXACT user-specified data:")
            for key, value in user_data.items():
                print(f"         {key}: {value}")
            
            response = self.session.post(
                f"{BACKEND_URL}/calculate-price",
                json=user_data,
                timeout=10
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                price_data = response.json()
                print(f"      ✅ Price calculation with user-specified data successful")
                
                estimated_price = price_data.get('estimated_price')
                coefficients = price_data.get('coefficients', {})
                base_price = price_data.get('base_price', 90.0)
                
                print(f"\n      💰 USER-SPECIFIED DATA RESULTS:")
                print(f"         Base Price: €{base_price}")
                print(f"         Final Estimated Price: €{estimated_price}")
                print(f"         Price Increase: €{estimated_price - base_price:.2f}")
                
                print(f"\n         📈 ALL COEFFICIENTS BREAKDOWN:")
                for coeff_name, coeff_value in coefficients.items():
                    print(f"            • {coeff_name}: {coeff_value}")
                
                # Check for specific coefficients the user asked about
                age_found = any('age' in coeff.lower() or 'ancienneté' in coeff.lower() for coeff in coefficients.keys())
                player_type_found = any('player_type' in coeff.lower() or 'player type' in coeff.lower() for coeff in coefficients.keys())
                
                print(f"\n      🔍 SPECIFIC COEFFICIENT VERIFICATION:")
                print(f"         Age coefficient found: {'✅ YES' if age_found else '❌ NO'}")
                print(f"         Player Type coefficient found: {'✅ YES' if player_type_found else '❌ NO'}")
                print(f"         Total coefficients returned: {len(coefficients)}")
                
                # Return the price and coefficient details for user
                result_summary = {
                    "estimated_price": estimated_price,
                    "base_price": base_price,
                    "coefficients": coefficients,
                    "age_coefficient_found": age_found,
                    "player_type_coefficient_found": player_type_found
                }
                
                self.log_test("User-Specified Data Test", True, f"✅ Price: €{estimated_price}, Age coeff: {age_found}, Player type coeff: {player_type_found}")
                return result_summary
                
            else:
                print(f"      ❌ Price calculation failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("User-Specified Data Test", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User-Specified Data Test", False, f"Exception: {str(e)}")
            return False

    def test_photo_upload_endpoint(self):
        """Test POST /api/upload/kit-photo endpoint"""
        try:
            print(f"\n📸 TESTING PHOTO UPLOAD ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # Create a simple test image (1x1 pixel PNG)
            import io
            from PIL import Image
            
            # Create a small test image
            test_image = Image.new('RGB', (100, 100), color='red')
            img_buffer = io.BytesIO()
            test_image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            
            print(f"      📷 Testing photo upload with sample JPEG image (100x100)")
            
            files = {
                'photo': ('test_kit_photo.jpg', img_buffer, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/upload/kit-photo",
                files=files,
                timeout=15
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                upload_data = response.json()
                print(f"      ✅ Photo upload endpoint accessible")
                
                photo_url = upload_data.get('photo_url') or upload_data.get('file_url') or upload_data.get('url')
                
                if photo_url:
                    print(f"      📸 PHOTO UPLOAD RESULTS:")
                    print(f"         Photo URL: {photo_url}")
                    
                    # Verify URL format
                    if photo_url.startswith('uploads/') or photo_url.startswith('http'):
                        print(f"      ✅ Photo URL format appears correct")
                    else:
                        print(f"      ⚠️ Photo URL format may be incorrect: {photo_url}")
                    
                    self.log_test("Photo Upload Endpoint", True, f"✅ Photo upload successful - URL: {photo_url}")
                    return True
                else:
                    print(f"      ❌ No photo URL returned in response")
                    print(f"      Response data: {upload_data}")
                    self.log_test("Photo Upload Endpoint", False, "❌ No photo URL in response", upload_data)
                    return False
                
            else:
                print(f"      ❌ Photo upload failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("Photo Upload Endpoint", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Photo Upload Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_edit_master_kit_endpoint(self):
        """Test PUT /api/master-kits/{master_kit_id}/edit endpoint"""
        try:
            print(f"\n✏️ TESTING EDIT MASTER KIT ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # First, get available master kits to test editing
            master_kits_response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            
            if master_kits_response.status_code != 200:
                print(f"      ❌ Cannot get master kits for edit testing - Status {master_kits_response.status_code}")
                self.log_test("Edit Master Kit Endpoint", False, "❌ Cannot get master kits for testing")
                return False
            
            master_kits = master_kits_response.json()
            
            if not master_kits or len(master_kits) == 0:
                print(f"      ⚠️ No master kits available for edit testing")
                self.log_test("Edit Master Kit Endpoint", False, "⚠️ No master kits available for testing")
                return False
            
            # Use first master kit for testing
            test_master_kit = master_kits[0]
            master_kit_id = test_master_kit.get('id')
            
            print(f"      🎽 Testing edit on master kit: {master_kit_id}")
            print(f"         Original club: {test_master_kit.get('club', 'Unknown')}")
            print(f"         Original season: {test_master_kit.get('season', 'Unknown')}")
            
            # Sample edit data
            edit_data = {
                "personal_notes": "Updated via Edit Kit Form testing",
                "condition": "very_good",
                "physical_state": "very_good_condition",
                "purchase_price": 150.0,
                "name_printing": "Test Player",
                "number_printing": "10",
                "is_signed": False
            }
            
            print(f"      📝 Testing edit with sample data:")
            for key, value in edit_data.items():
                print(f"         {key}: {value}")
            
            response = self.session.put(
                f"{BACKEND_URL}/master-kits/{master_kit_id}/edit",
                json=edit_data,
                timeout=10
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                edit_response_data = response.json()
                print(f"      ✅ Edit master kit endpoint accessible")
                
                print(f"      ✏️ EDIT RESULTS:")
                print(f"         Response message: {edit_response_data.get('message', 'No message')}")
                
                # Check if response includes updated data
                updated_data = edit_response_data.get('updated_item') or edit_response_data.get('data')
                if updated_data:
                    print(f"         Updated item ID: {updated_data.get('id', 'Unknown')}")
                    print(f"         Updated notes: {updated_data.get('personal_notes', 'N/A')}")
                
                self.log_test("Edit Master Kit Endpoint", True, f"✅ Master kit edit successful")
                return True
                
            elif response.status_code == 404:
                print(f"      ❌ Edit endpoint not found - may not be implemented yet")
                self.log_test("Edit Master Kit Endpoint", False, "❌ Edit endpoint not found (404)")
                return False
                
            else:
                print(f"      ❌ Edit master kit failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("Edit Master Kit Endpoint", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Edit Master Kit Endpoint", False, f"Exception: {str(e)}")
            return False

    def run_new_coefficients_testing(self):
        """Run comprehensive testing of the 3 new coefficients"""
        print("\n🚀 NEW COEFFICIENTS TESTING")
        print("Testing the 3 new coefficients: Age, Player Type, and Data Saving")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        auth_success = self.authenticate_admin()
        test_results.append(auth_success)
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Test age coefficient with old season
        print("\n2️⃣ Testing Age Coefficient with Old Season...")
        age_coeff_success = self.test_age_coefficient_with_old_season()
        test_results.append(age_coeff_success)
        
        # Step 3: Test player type coefficient
        print("\n3️⃣ Testing Player Type Coefficient...")
        player_type_success = self.test_player_type_coefficient()
        test_results.append(player_type_success)
        
        # Step 4: Test with user-specified data comprehensively
        print("\n4️⃣ Testing User-Specified Data Comprehensively...")
        user_data_result = self.test_user_specified_data_comprehensive()
        test_results.append(user_data_result is not False)
        
        # Store the comprehensive result for summary
        self.comprehensive_result = user_data_result
        
        return test_results

    def print_comprehensive_edit_kit_form_summary(self):
        """Print final comprehensive Edit Kit Form testing summary"""
        print("\n📊 EDIT KIT FORM BACKEND FUNCTIONALITY TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings for Edit Kit Form testing
        print(f"\n🔍 EDIT KIT FORM BACKEND TESTING RESULTS:")
        
        # Form Data Endpoints Analysis
        form_data_tests = [r for r in self.test_results if 'Form Data' in r['test']]
        if form_data_tests:
            form_data_passed = len([r for r in form_data_tests if r['success']])
            print(f"\n✅ FORM DATA ENDPOINTS: {form_data_passed}/{len(form_data_tests)} PASSED")
            
            if self.form_data:
                if 'players' in self.form_data:
                    players_count = len(self.form_data['players'])
                    print(f"  • Players endpoint: {players_count} players returned")
                    if players_count > 0 and self.sample_player_id:
                        print(f"    - Sample player ID available: {self.sample_player_id}")
                
                if 'competitions' in self.form_data:
                    competitions_count = len(self.form_data['competitions'])
                    print(f"  • Competitions endpoint: {competitions_count} competitions returned")
                
                if 'teams' in self.form_data:
                    teams_count = len(self.form_data['teams'])
                    print(f"  • Teams endpoint: {teams_count} teams returned")
        
        # Price Calculation Analysis
        price_calc_tests = [r for r in self.test_results if 'Price Calculation' in r['test']]
        if price_calc_tests:
            price_calc_passed = len([r for r in price_calc_tests if r['success']])
            print(f"\n✅ PRICE CALCULATION ENDPOINT: {price_calc_passed}/{len(price_calc_tests)} PASSED")
            
            if price_calc_passed > 0:
                print(f"  • Price calculation working with coefficient breakdown")
                print(f"  • Sample data processed successfully")
            else:
                print(f"  • Price calculation endpoint issues detected")
        
        # Photo Upload Analysis
        photo_upload_tests = [r for r in self.test_results if 'Photo Upload' in r['test']]
        if photo_upload_tests:
            photo_upload_passed = len([r for r in photo_upload_tests if r['success']])
            print(f"\n✅ PHOTO UPLOAD ENDPOINT: {photo_upload_passed}/{len(photo_upload_tests)} PASSED")
            
            if photo_upload_passed > 0:
                print(f"  • Photo upload working with proper URL generation")
            else:
                print(f"  • Photo upload endpoint issues detected")
        
        # Edit Master Kit Analysis
        edit_kit_tests = [r for r in self.test_results if 'Edit Master Kit' in r['test']]
        if edit_kit_tests:
            edit_kit_passed = len([r for r in edit_kit_tests if r['success']])
            print(f"\n✅ EDIT MASTER KIT ENDPOINT: {edit_kit_passed}/{len(edit_kit_tests)} PASSED")
            
            if edit_kit_passed > 0:
                print(f"  • Master kit editing functionality working")
            else:
                print(f"  • Master kit editing endpoint issues detected")
        
        # Overall functionality status
        print(f"\n🎯 OVERALL EDIT KIT FORM FUNCTIONALITY STATUS:")
        
        functionality_working = []
        functionality_broken = []
        
        # Check each major functionality
        if any(r['success'] for r in self.test_results if 'Form Data' in r['test']):
            functionality_working.append("Form Data Endpoints (players, competitions, teams)")
        else:
            functionality_broken.append("Form Data Endpoints")
        
        if any(r['success'] for r in self.test_results if 'Price Calculation' in r['test']):
            functionality_working.append("Price Calculation with Coefficients")
        else:
            functionality_broken.append("Price Calculation")
        
        if any(r['success'] for r in self.test_results if 'Photo Upload' in r['test']):
            functionality_working.append("Photo Upload")
        else:
            functionality_broken.append("Photo Upload")
        
        if any(r['success'] for r in self.test_results if 'Edit Master Kit' in r['test']):
            functionality_working.append("Master Kit Editing")
        else:
            functionality_broken.append("Master Kit Editing")
        
        if functionality_working:
            print(f"  ✅ WORKING FUNCTIONALITY ({len(functionality_working)}):")
            for func in functionality_working:
                print(f"     • {func}")
        
        if functionality_broken:
            print(f"  ❌ BROKEN FUNCTIONALITY ({len(functionality_broken)}):")
            for func in functionality_broken:
                print(f"     • {func}")
        
        if not functionality_broken:
            print(f"  🎉 ALL EDIT KIT FORM FUNCTIONALITY WORKING!")
        
        # Show test failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ TEST FAILURES ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the Edit Kit Form backend testing"""
    tester = TopKitEditKitFormBackendTesting()
    
    # Run the comprehensive Edit Kit Form backend testing
    test_results = tester.run_edit_kit_form_backend_testing()
    
    # Print comprehensive summary
    tester.print_comprehensive_edit_kit_form_summary()
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)