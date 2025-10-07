#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - EDIT KIT DETAILS DATA PERSISTENCE TESTING

**URGENT - EDIT KIT DETAILS DATA PERSISTENCE ISSUE:**

Testing the Edit Kit Details form data persistence issue where:
1. Real-time calculation in form works (shows correct price)
2. After validation, displayed price "doesn't match the form info"

**Test Requirements:**
1. **PUT collection item** with specific data to test data persistence
2. **Use existing collection_id**: 0b602c78-4a36-474c-b7bb-95f92c687909 (from logs)
3. **Verify PUT returns correct calculated price**
4. **Verify new data is properly saved**
5. **Verify GET collection item after save returns same price**
6. **Check for discrepancy between calculated and saved price**

**User-Specified Test Data:**
```json
{
  "kit_type": "authentic",
  "condition": "match_worn", 
  "number": "10",
  "signed": true,
  "signature_proof": "photo",
  "origin_type": "match_worn",
  "special_match_type": "classico",
  "match_result": "win",
  "performance": ["scored_goal", "man_of_the_match"],
  "match_proof": "photo",
  "printing_style": "league",
  "competition_patch": "ucl"
}
```

**Authentication:** emergency.admin@topkit.test / EmergencyAdmin2025!

**PRIORITY: URGENT** - Testing Edit Kit Details data persistence issue.
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

class TopKitEditKitDataPersistenceBackendTesting:
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

    def test_edit_kit_data_persistence_issue(self):
        """Test the specific Edit Kit Details data persistence issue"""
        try:
            print(f"\n🚨 TESTING EDIT KIT DATA PERSISTENCE ISSUE")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # User-specified collection ID from logs
            collection_id = "0b602c78-4a36-474c-b7bb-95f92c687909"
            
            print(f"      🎯 Testing with collection ID: {collection_id}")
            
            # Step 1: Get current collection item data
            print(f"\n      1️⃣ Getting current collection item data...")
            get_response = self.session.get(f"{BACKEND_URL}/my-collection/{collection_id}", timeout=10)
            
            if get_response.status_code != 200:
                print(f"      ❌ Cannot get collection item - Status {get_response.status_code}")
                print(f"      Response: {get_response.text}")
                self.log_test("Edit Kit Data Persistence - GET Before", False, f"❌ Cannot get collection item - Status {get_response.status_code}")
                return False
            
            original_data = get_response.json()
            original_price = original_data.get('estimated_price')
            print(f"      ✅ Original collection item retrieved")
            print(f"         Original estimated price: €{original_price}")
            print(f"         Master kit ID: {original_data.get('master_kit_id')}")
            
            # Step 2: Test price calculation with user-specified data
            print(f"\n      2️⃣ Testing price calculation with user-specified data...")
            
            # User-specified test data exactly as provided
            calculation_data = {
                "kit_type": "authentic",
                "condition": "match_worn", 
                "number": "10",
                "signed": True,
                "signature_proof": "photo",
                "origin_type": "match_worn",
                "special_match_type": "classico",
                "match_result": "win",
                "performance": ["scored_goal", "man_of_the_match"],
                "match_proof": "photo",
                "printing_style": "league",
                "competition_patch": "ucl",
                "master_kit_id": original_data.get('master_kit_id')  # Use the master kit ID from collection
            }
            
            print(f"      📊 Calculating price with user-specified data:")
            for key, value in calculation_data.items():
                print(f"         {key}: {value}")
            
            calc_response = self.session.post(
                f"{BACKEND_URL}/calculate-price",
                json=calculation_data,
                timeout=10
            )
            
            if calc_response.status_code != 200:
                print(f"      ❌ Price calculation failed - Status {calc_response.status_code}")
                print(f"      Response: {calc_response.text}")
                self.log_test("Edit Kit Data Persistence - Price Calculation", False, f"❌ Price calculation failed - Status {calc_response.status_code}")
                return False
            
            calc_data = calc_response.json()
            calculated_price = calc_data.get('estimated_price')
            coefficients = calc_data.get('coefficients', {})
            
            print(f"      ✅ Price calculation successful")
            print(f"         Calculated price: €{calculated_price}")
            print(f"         Number of coefficients: {len(coefficients)}")
            
            # Step 3: Update collection item with user-specified data
            print(f"\n      3️⃣ Updating collection item with user-specified data...")
            
            # Prepare update data (map to collection item fields)
            update_data = {
                "condition": calculation_data["condition"],
                "number_printing": calculation_data["number"],
                "is_signed": calculation_data["signed"],
                "signature_proof": calculation_data["signature_proof"],
                "origin_type": calculation_data["origin_type"],
                "special_match_type": calculation_data["special_match_type"],
                "match_result": calculation_data["match_result"],
                "performance": calculation_data["performance"],
                "match_proof": calculation_data["match_proof"],
                "printing_style": calculation_data["printing_style"],
                "competition_patch": calculation_data["competition_patch"]
            }
            
            print(f"      📝 Updating collection item with data:")
            for key, value in update_data.items():
                print(f"         {key}: {value}")
            
            put_response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_id}",
                json=update_data,
                timeout=10
            )
            
            print(f"      PUT Response Status: {put_response.status_code}")
            
            if put_response.status_code != 200:
                print(f"      ❌ Collection item update failed - Status {put_response.status_code}")
                print(f"      Response: {put_response.text}")
                self.log_test("Edit Kit Data Persistence - PUT Update", False, f"❌ Update failed - Status {put_response.status_code}")
                return False
            
            put_data = put_response.json()
            put_returned_price = put_data.get('estimated_price')
            
            print(f"      ✅ Collection item update successful")
            print(f"         PUT returned price: €{put_returned_price}")
            
            # Step 4: Get updated collection item to verify persistence
            print(f"\n      4️⃣ Getting updated collection item to verify persistence...")
            
            get_after_response = self.session.get(f"{BACKEND_URL}/my-collection/{collection_id}", timeout=10)
            
            if get_after_response.status_code != 200:
                print(f"      ❌ Cannot get updated collection item - Status {get_after_response.status_code}")
                self.log_test("Edit Kit Data Persistence - GET After", False, f"❌ Cannot get updated item - Status {get_after_response.status_code}")
                return False
            
            updated_data = get_after_response.json()
            final_price = updated_data.get('estimated_price')
            
            print(f"      ✅ Updated collection item retrieved")
            print(f"         Final stored price: €{final_price}")
            
            # Step 5: Compare prices and identify discrepancies
            print(f"\n      5️⃣ Analyzing price discrepancies...")
            
            print(f"\n      💰 PRICE COMPARISON ANALYSIS:")
            print(f"         Original price: €{original_price}")
            print(f"         Calculated price (real-time): €{calculated_price}")
            print(f"         PUT returned price: €{put_returned_price}")
            print(f"         Final stored price (GET after): €{final_price}")
            
            # Check for discrepancies
            discrepancies = []
            
            if calculated_price != put_returned_price:
                discrepancy = f"Calculated price (€{calculated_price}) ≠ PUT returned price (€{put_returned_price})"
                discrepancies.append(discrepancy)
                print(f"      🚨 DISCREPANCY 1: {discrepancy}")
            
            if put_returned_price != final_price:
                discrepancy = f"PUT returned price (€{put_returned_price}) ≠ Final stored price (€{final_price})"
                discrepancies.append(discrepancy)
                print(f"      🚨 DISCREPANCY 2: {discrepancy}")
            
            if calculated_price != final_price:
                discrepancy = f"Calculated price (€{calculated_price}) ≠ Final stored price (€{final_price})"
                discrepancies.append(discrepancy)
                print(f"      🚨 DISCREPANCY 3: {discrepancy}")
            
            # Step 6: Verify data persistence
            print(f"\n      6️⃣ Verifying data persistence...")
            
            data_persistence_issues = []
            
            # Check if the updated data matches what we sent
            for key, expected_value in update_data.items():
                actual_value = updated_data.get(key)
                if actual_value != expected_value:
                    issue = f"{key}: expected {expected_value}, got {actual_value}"
                    data_persistence_issues.append(issue)
                    print(f"      🚨 DATA PERSISTENCE ISSUE: {issue}")
            
            # Final assessment
            print(f"\n      📊 FINAL ASSESSMENT:")
            
            if not discrepancies and not data_persistence_issues:
                print(f"      ✅ NO ISSUES FOUND - Edit Kit Details data persistence working correctly")
                self.log_test("Edit Kit Data Persistence Issue", True, "✅ No price discrepancies or data persistence issues found")
                return True
            else:
                print(f"      ❌ ISSUES IDENTIFIED:")
                print(f"         Price discrepancies: {len(discrepancies)}")
                print(f"         Data persistence issues: {len(data_persistence_issues)}")
                
                issue_summary = {
                    "price_discrepancies": discrepancies,
                    "data_persistence_issues": data_persistence_issues,
                    "calculated_price": calculated_price,
                    "put_returned_price": put_returned_price,
                    "final_stored_price": final_price
                }
                
                self.log_test("Edit Kit Data Persistence Issue", False, f"❌ Found {len(discrepancies)} price discrepancies and {len(data_persistence_issues)} data issues", issue_summary)
                return False
                
        except Exception as e:
            self.log_test("Edit Kit Data Persistence Issue", False, f"Exception: {str(e)}")
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

    def run_edit_kit_data_persistence_testing(self):
        """Run comprehensive testing of Edit Kit Details data persistence issue"""
        print("\n🚀 EDIT KIT DETAILS DATA PERSISTENCE TESTING")
        print("Testing the Edit Kit Details form data persistence issue")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        auth_success = self.authenticate_admin()
        test_results.append(auth_success)
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Test Edit Kit Details data persistence issue
        print("\n2️⃣ Testing Edit Kit Details Data Persistence Issue...")
        persistence_success = self.test_edit_kit_data_persistence_issue()
        test_results.append(persistence_success)
        
        return test_results

    def print_comprehensive_edit_kit_data_persistence_summary(self):
        """Print final comprehensive Edit Kit Details data persistence testing summary"""
        print("\n📊 EDIT KIT DETAILS DATA PERSISTENCE TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings for Edit Kit Details data persistence testing
        print(f"\n🔍 EDIT KIT DETAILS DATA PERSISTENCE RESULTS:")
        
        # Data Persistence Analysis
        persistence_tests = [r for r in self.test_results if 'Edit Kit Data Persistence' in r['test']]
        if persistence_tests:
            persistence_passed = len([r for r in persistence_tests if r['success']])
            print(f"\n🚨 DATA PERSISTENCE ISSUE: {'✅ RESOLVED' if persistence_passed > 0 else '❌ CONFIRMED'}")
            
            if persistence_passed > 0:
                print(f"  • Edit Kit Details form data persistence is working correctly")
                print(f"  • No discrepancies found between calculated and saved prices")
                print(f"  • Form data is properly saved and retrieved")
            else:
                print(f"  • Edit Kit Details form data persistence issue CONFIRMED")
                print(f"  • Price discrepancies found between calculation and storage")
                
                # Show specific issues if available
                failed_test = [r for r in persistence_tests if not r['success']][0]
                if failed_test.get('details'):
                    details = failed_test['details']
                    if isinstance(details, dict):
                        if details.get('price_discrepancies'):
                            print(f"  • Price Discrepancies Found:")
                            for discrepancy in details['price_discrepancies']:
                                print(f"    - {discrepancy}")
                        
                        if details.get('data_persistence_issues'):
                            print(f"  • Data Persistence Issues Found:")
                            for issue in details['data_persistence_issues']:
                                print(f"    - {issue}")
                        
                        print(f"  • Price Analysis:")
                        print(f"    - Calculated price (real-time): €{details.get('calculated_price', 'N/A')}")
                        print(f"    - PUT returned price: €{details.get('put_returned_price', 'N/A')}")
                        print(f"    - Final stored price: €{details.get('final_stored_price', 'N/A')}")
        
        # Authentication Analysis
        auth_tests = [r for r in self.test_results if 'Authentication' in r['test']]
        if auth_tests:
            auth_passed = len([r for r in auth_tests if r['success']])
            print(f"\n🔐 AUTHENTICATION: {'✅ WORKING' if auth_passed > 0 else '❌ FAILED'}")
            if auth_passed > 0:
                print(f"  • Emergency admin authentication successful")
            else:
                print(f"  • Emergency admin authentication failed")
        
        # Overall status
        print(f"\n🎯 OVERALL EDIT KIT DETAILS STATUS:")
        
        if persistence_tests and any(r['success'] for r in persistence_tests):
            print(f"  ✅ ISSUE RESOLVED: Edit Kit Details data persistence working correctly")
            print(f"  • Real-time price calculation matches saved price")
            print(f"  • Form data is properly persisted in database")
            print(f"  • No discrepancies between form display and stored data")
        else:
            print(f"  ❌ ISSUE CONFIRMED: Edit Kit Details data persistence problem exists")
            print(f"  • Price discrepancy between real-time calculation and saved data")
            print(f"  • Form data may not be properly persisted")
            print(f"  • Investigation needed to identify root cause")
        
        # Show test failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ TEST FAILURES ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
                if failure.get('details') and isinstance(failure['details'], str):
                    print(f"    Details: {failure['details']}")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the Edit Kit Details data persistence testing"""
    tester = TopKitEditKitDataPersistenceBackendTesting()
    
    # Run the comprehensive Edit Kit Details data persistence testing
    test_results = tester.run_edit_kit_data_persistence_testing()
    
    # Print comprehensive summary
    tester.print_comprehensive_edit_kit_data_persistence_summary()
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)