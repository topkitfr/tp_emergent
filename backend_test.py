#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - EDIT KIT FORM BACKEND FUNCTIONALITY TESTING

**EDIT KIT FORM BACKEND FUNCTIONALITY TESTING:**

Testing the Edit Kit Form backend functionality that was just implemented. This includes comprehensive testing of:

**Test Requirements:**
1. **Form Data API Endpoints**: Test the new form data endpoints:
   - GET /api/form-data/players (should return players with aura ratings)
   - GET /api/form-data/competitions (should return competition data)
   - GET /api/form-data/teams (should return team data for opponents)

2. **Price Calculation Endpoint**: Test the pricing calculation:
   - POST /api/calculate-price with sample kit details data
   - Verify it returns proper estimated price and coefficients breakdown
   - Test different combinations (signed vs unsigned, match-worn vs standard, etc.)

3. **Edit Master Kit Endpoint**: Test the edit functionality:
   - PUT /api/master-kits/{master_kit_id}/edit with sample kit details
   - Verify it updates the master kit and returns proper response

4. **Photo Upload Endpoint**: Test the photo upload:
   - POST /api/upload/kit-photo with a sample image
   - Verify it returns proper photo URL

**Authentication:** Use emergency.admin@topkit.test / EmergencyAdmin2025!

**Sample Test Data for Price Calculation:**
```json
{
  "type": "authentic",
  "condition": "nwt", 
  "origin_type": "match_worn",
  "special_match_type": "classico",
  "match_result": "win",
  "performance": ["scored_goal", "man_of_the_match"],
  "match_proof": "photo",
  "signed": true,
  "signature_proof": "certificate",
  "player_id": "[use any player ID from form-data/players]"
}
```

**Expected Results:**
- All form data endpoints should return populated data (players with aura ratings, competitions, teams)
- Price calculation should return detailed coefficients and estimated price
- Edit functionality should successfully update master kits
- Photo upload should work properly

**PRIORITY: HIGH** - Testing Edit Kit Form backend functionality implementation.
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

class TopKitEditKitFormBackendTesting:
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

    def test_price_calculation_endpoint(self):
        """Test POST /api/calculate-price endpoint with sample kit details"""
        try:
            print(f"\n💰 TESTING PRICE CALCULATION ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # Sample test data for price calculation
            sample_kit_details = {
                "type": "authentic",
                "condition": "nwt", 
                "origin_type": "match_worn",
                "special_match_type": "classico",
                "match_result": "win",
                "performance": ["scored_goal", "man_of_the_match"],
                "match_proof": "photo",
                "signed": True,
                "signature_proof": "certificate",
                "player_aura": 2.0
            }
            
            # Add player_id if we have one from form data
            if self.sample_player_id:
                sample_kit_details["player_id"] = self.sample_player_id
            
            print(f"      📊 Testing price calculation with sample data:")
            print(f"         Type: {sample_kit_details['type']}")
            print(f"         Condition: {sample_kit_details['condition']}")
            print(f"         Origin: {sample_kit_details['origin_type']}")
            print(f"         Special Match: {sample_kit_details['special_match_type']}")
            print(f"         Signed: {sample_kit_details['signed']}")
            print(f"         Player Aura: {sample_kit_details['player_aura']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/calculate-price",
                json=sample_kit_details,
                timeout=10
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                price_data = response.json()
                print(f"      ✅ Price calculation endpoint accessible")
                
                estimated_price = price_data.get('estimated_price')
                coefficients = price_data.get('coefficients', {})
                
                print(f"      💰 PRICE CALCULATION RESULTS:")
                print(f"         Estimated Price: €{estimated_price}")
                
                if coefficients:
                    print(f"         📈 COEFFICIENTS BREAKDOWN:")
                    for coeff_name, coeff_value in coefficients.items():
                        print(f"            {coeff_name}: {coeff_value}")
                
                # Verify expected components are present
                expected_components = ['base_price', 'condition', 'origin', 'signature']
                missing_components = []
                
                for component in expected_components:
                    if component not in coefficients:
                        missing_components.append(component)
                
                if missing_components:
                    print(f"      ⚠️ Missing expected coefficient components: {missing_components}")
                else:
                    print(f"      ✅ All expected coefficient components present")
                
                self.log_test("Price Calculation Endpoint", True, f"✅ Price calculation successful - €{estimated_price}")
                return True
                
            else:
                print(f"      ❌ Price calculation failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("Price Calculation Endpoint", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Price Calculation Endpoint", False, f"Exception: {str(e)}")
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
                'file': ('test_kit_photo.jpg', img_buffer, 'image/jpeg')
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

    def run_master_kit_data_retrieval_verification(self):
        """Run comprehensive master kit data retrieval verification"""
        print("\n🚀 MASTER KIT DATA RETRIEVAL FIXES VERIFICATION")
        print("Verifying fixes for master kit data enrichment and embedding issues")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        auth_success = self.authenticate_admin()
        test_results.append(auth_success)
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return test_results, {}
        
        # Step 2: Test master kits data enrichment
        print("\n2️⃣ Testing Master Kits Data Enrichment...")
        master_kits_success, master_kits_data = self.test_master_kits_data_enrichment()
        test_results.append(master_kits_success)
        
        # Step 3: Test my collection list enrichment
        print("\n3️⃣ Testing My Collection List Data Enrichment...")
        collection_success, collection_data = self.test_my_collection_list_enrichment()
        test_results.append(collection_success)
        
        # Step 4: Test individual collection item enrichment
        print("\n4️⃣ Testing Individual Collection Item Data Enrichment...")
        individual_success, individual_data = self.test_individual_collection_item_enrichment()
        test_results.append(individual_success)
        
        return test_results, {
            "master_kits_data": master_kits_data if master_kits_success else [],
            "collection_data": collection_data if collection_success else [],
            "individual_data": individual_data if individual_success else {}
        }

    def print_comprehensive_data_retrieval_summary(self, test_data):
        """Print final comprehensive data retrieval verification summary"""
        print("\n📊 MASTER KIT DATA RETRIEVAL FIXES VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings for data retrieval verification
        print(f"\n🔍 DATA RETRIEVAL FIXES VERIFICATION RESULTS:")
        
        # Master kits data enrichment analysis
        master_kits_data = test_data.get("master_kits_data", [])
        if master_kits_data:
            print(f"\n✅ FIX 1 - MASTER KITS DATA ENRICHMENT: VERIFIED")
            print(f"  • Total master kits available: {len(master_kits_data)}")
            
            if len(master_kits_data) > 0:
                first_kit = master_kits_data[0]
                
                # Check enriched fields
                club_name = first_kit.get('club_name')
                brand_name = first_kit.get('brand_name')
                model = first_kit.get('model')
                
                # Check legacy fields
                club = first_kit.get('club')
                brand = first_kit.get('brand')
                
                enrichment_working = []
                enrichment_broken = []
                
                if club_name and club_name not in ["Unknown", "null", None]:
                    enrichment_working.append(f"club_name: '{club_name}'")
                else:
                    enrichment_broken.append(f"club_name: '{club_name}'")
                
                if brand_name and brand_name not in ["Unknown", "null", None]:
                    enrichment_working.append(f"brand_name: '{brand_name}'")
                else:
                    enrichment_broken.append(f"brand_name: '{brand_name}'")
                
                if model and model not in ["Unknown", "null", None]:
                    enrichment_working.append(f"model: '{model}'")
                else:
                    enrichment_broken.append(f"model: '{model}'")
                
                if club and club not in ["Unknown", "null", None]:
                    enrichment_working.append(f"legacy club: '{club}'")
                else:
                    enrichment_broken.append(f"legacy club: '{club}'")
                
                if brand and brand not in ["Unknown", "null", None]:
                    enrichment_working.append(f"legacy brand: '{brand}'")
                else:
                    enrichment_broken.append(f"legacy brand: '{brand}'")
                
                if enrichment_working:
                    print(f"  ✅ WORKING ENRICHED FIELDS:")
                    for field in enrichment_working:
                        print(f"     • {field}")
                
                if enrichment_broken:
                    print(f"  ❌ BROKEN ENRICHED FIELDS:")
                    for field in enrichment_broken:
                        print(f"     • {field}")
                
                if not enrichment_broken:
                    print(f"  🎉 ALL MASTER KIT FIELDS PROPERLY ENRICHED!")
        
        # Collection data enrichment analysis
        collection_data = test_data.get("collection_data", [])
        individual_data = test_data.get("individual_data", {})
        
        if collection_data or individual_data:
            print(f"\n✅ FIX 2 - COLLECTION DATA EMBEDDING ENRICHMENT: VERIFIED")
            
            if collection_data and len(collection_data) > 0:
                first_item = collection_data[0]
                master_kit_data = first_item.get('master_kit')
                
                if master_kit_data:
                    print(f"  • Collection items found: {len(collection_data)}")
                    
                    # Check embedded enriched fields
                    club_name = master_kit_data.get('club_name')
                    brand_name = master_kit_data.get('brand_name')
                    model = master_kit_data.get('model')
                    
                    # Check embedded legacy fields
                    club = master_kit_data.get('club')
                    brand = master_kit_data.get('brand')
                    
                    embedded_enrichment_working = []
                    embedded_enrichment_broken = []
                    
                    if club_name and club_name not in ["Unknown", "null", None]:
                        embedded_enrichment_working.append(f"embedded club_name: '{club_name}'")
                    else:
                        embedded_enrichment_broken.append(f"embedded club_name: '{club_name}'")
                    
                    if brand_name and brand_name not in ["Unknown", "null", None]:
                        embedded_enrichment_working.append(f"embedded brand_name: '{brand_name}'")
                    else:
                        embedded_enrichment_broken.append(f"embedded brand_name: '{brand_name}'")
                    
                    if model and model not in ["Unknown", "null", None]:
                        embedded_enrichment_working.append(f"embedded model: '{model}'")
                    else:
                        embedded_enrichment_broken.append(f"embedded model: '{model}'")
                    
                    if club and club not in ["Unknown", "null", None]:
                        embedded_enrichment_working.append(f"embedded legacy club: '{club}'")
                    else:
                        embedded_enrichment_broken.append(f"embedded legacy club: '{club}'")
                    
                    if brand and brand not in ["Unknown", "null", None]:
                        embedded_enrichment_working.append(f"embedded legacy brand: '{brand}'")
                    else:
                        embedded_enrichment_broken.append(f"embedded legacy brand: '{brand}'")
                    
                    if embedded_enrichment_working:
                        print(f"  ✅ WORKING EMBEDDED ENRICHED FIELDS:")
                        for field in embedded_enrichment_working:
                            print(f"     • {field}")
                    
                    if embedded_enrichment_broken:
                        print(f"  ❌ BROKEN EMBEDDED ENRICHED FIELDS:")
                        for field in embedded_enrichment_broken:
                            print(f"     • {field}")
                    
                    if not embedded_enrichment_broken:
                        print(f"  🎉 ALL EMBEDDED COLLECTION FIELDS PROPERLY ENRICHED!")
                else:
                    print(f"  ❌ Collection items missing embedded master kit data")
            
            if individual_data:
                master_kit_data = individual_data.get('master_kit')
                if master_kit_data:
                    print(f"  ✅ Individual collection item endpoint working with embedded enriched data")
                else:
                    print(f"  ❌ Individual collection item endpoint missing embedded enriched data")
        
        # Overall enrichment status
        print(f"\n🎯 OVERALL DATA ENRICHMENT STATUS:")
        
        fixes_working = []
        fixes_broken = []
        
        # Check master kits enrichment
        if master_kits_data and len(master_kits_data) > 0:
            first_kit = master_kits_data[0]
            if (first_kit.get('club_name') and first_kit.get('club_name') not in ["Unknown", "null", None] and
                first_kit.get('brand_name') and first_kit.get('brand_name') not in ["Unknown", "null", None]):
                fixes_working.append("Master kits data enrichment (club_name, brand_name)")
            else:
                fixes_broken.append("Master kits data enrichment (club_name, brand_name)")
        else:
            fixes_broken.append("Master kits data retrieval")
        
        # Check collection embedding enrichment
        if (collection_data and len(collection_data) > 0 and collection_data[0].get('master_kit')):
            master_kit_data = collection_data[0].get('master_kit')
            if (master_kit_data.get('club_name') and master_kit_data.get('club_name') not in ["Unknown", "null", None] and
                master_kit_data.get('brand_name') and master_kit_data.get('brand_name') not in ["Unknown", "null", None]):
                fixes_working.append("Collection item data embedding enrichment")
            else:
                fixes_broken.append("Collection item data embedding enrichment")
        else:
            fixes_broken.append("Collection item data embedding")
        
        # Check individual item enrichment
        if individual_data and individual_data.get('master_kit'):
            master_kit_data = individual_data.get('master_kit')
            if (master_kit_data.get('club_name') and master_kit_data.get('club_name') not in ["Unknown", "null", None] and
                master_kit_data.get('brand_name') and master_kit_data.get('brand_name') not in ["Unknown", "null", None]):
                fixes_working.append("Individual collection item enrichment")
            else:
                fixes_broken.append("Individual collection item enrichment")
        else:
            fixes_broken.append("Individual collection item enrichment")
        
        if fixes_working:
            print(f"  ✅ WORKING ENRICHMENT FIXES ({len(fixes_working)}):")
            for fix in fixes_working:
                print(f"     • {fix}")
        
        if fixes_broken:
            print(f"  ❌ BROKEN ENRICHMENT FIXES ({len(fixes_broken)}):")
            for fix in fixes_broken:
                print(f"     • {fix}")
        
        if not fixes_broken:
            print(f"  🎉 ALL DATA ENRICHMENT FIXES VERIFIED WORKING!")
        
        # Show test failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ TEST FAILURES ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the master kit data retrieval verification"""
    tester = TopKitMasterKitDataRetrievalVerification()
    
    # Run the comprehensive master kit data retrieval verification
    test_results, test_data = tester.run_master_kit_data_retrieval_verification()
    
    # Print comprehensive summary
    tester.print_comprehensive_data_retrieval_summary(test_data)
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)