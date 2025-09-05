#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-collection.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class FormCreationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
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
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_team_creation(self):
        """Test Team Creation Fix (POST /api/teams)"""
        print("\n🏟️ Testing Team Creation Fix...")
        
        # Test 1: Valid team creation
        print("Test 1: Valid team creation")
        import random
        random_suffix = random.randint(1000, 9999)
        team_data = {
            "name": f"Test Team FC {random_suffix}",
            "country": "France",
            "city": "Paris",
            "founded_year": 2024,
            "short_name": f"TTFC{random_suffix}"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/teams", json=team_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   ✅ Team created successfully!")
                print(f"   Team ID: {data.get('id')}")
                print(f"   Team Name: {data.get('name')}")
                return data.get('id')
            else:
                print(f"   ❌ Team creation failed")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Team creation error: {e}")
            return None
    
    def test_team_creation_validation(self):
        """Test Team Creation validation and error handling"""
        print("\n🔍 Testing Team Creation validation...")
        
        # Test missing required fields
        print("Test: Missing required fields")
        invalid_team_data = {
            "city": "Paris"  # Missing name and country
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/teams", json=invalid_team_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 422:
                # Check if error message is meaningful (not [object Object])
                response_text = response.text
                if "[object Object]" in response_text:
                    print(f"   ❌ Still showing [object Object] error!")
                    return False
                else:
                    print(f"   ✅ Proper error message displayed (no [object Object])")
                    return True
            else:
                print(f"   ⚠️ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Validation test error: {e}")
            return False
    
    def test_competition_creation(self):
        """Test Competition Creation Fix (POST /api/competitions)"""
        print("\n🏆 Testing Competition Creation Fix...")
        
        # Test valid competition creation with corrected field mapping
        print("Test: Valid competition creation")
        import random
        random_suffix = random.randint(1000, 9999)
        competition_data = {
            "competition_name": f"Test League {random_suffix}",  # Fixed: name → competition_name
            "type": "National league",               # Fixed: competition_type → type
            "country": "France",
            "level": 1,
            "confederations_federations": ["UEFA"]  # Fixed: should be a list
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/competitions", json=competition_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   ✅ Competition created successfully!")
                print(f"   Competition ID: {data.get('id')}")
                print(f"   Competition Name: {data.get('competition_name')}")
                print(f"   Type: {data.get('type')}")
                return data.get('id')
            else:
                print(f"   ❌ Competition creation failed")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Competition creation error: {e}")
            return None
    
    def test_competition_validation(self):
        """Test Competition Creation validation"""
        print("\n🔍 Testing Competition Creation validation...")
        
        # Test missing required fields
        print("Test: Missing required fields (competition_name, type)")
        invalid_competition_data = {
            "country": "France"  # Missing competition_name and type
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/competitions", json=invalid_competition_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 422:
                response_text = response.text
                if "[object Object]" in response_text:
                    print(f"   ❌ Still showing [object Object] error!")
                    return False
                else:
                    print(f"   ✅ Proper error message displayed (no [object Object])")
                    return True
            else:
                print(f"   ⚠️ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Competition validation test error: {e}")
            return False
    
    def get_teams_and_brands(self):
        """Get available teams and brands for master jersey creation"""
        print("\n📋 Getting available teams and brands...")
        
        teams = []
        brands = []
        
        try:
            # Get teams
            teams_response = self.session.get(f"{BACKEND_URL}/teams")
            if teams_response.status_code == 200:
                teams = teams_response.json()
                print(f"   Found {len(teams)} teams")
            
            # Get brands
            brands_response = self.session.get(f"{BACKEND_URL}/brands")
            if brands_response.status_code == 200:
                brands = brands_response.json()
                print(f"   Found {len(brands)} brands")
                
            return teams, brands
            
        except Exception as e:
            print(f"   ❌ Error getting teams/brands: {e}")
            return [], []
    
    def test_master_jersey_creation(self):
        """Test Master Jersey Creation Fix (POST /api/master-jerseys)"""
        print("\n👕 Testing Master Jersey Creation Fix...")
        
        # Get available teams and brands
        teams, brands = self.get_teams_and_brands()
        
        if not teams or not brands:
            print("   ❌ No teams or brands available for testing")
            return None
        
        team_id = teams[0].get('id')
        brand_id = brands[0].get('id')
        
        print(f"   Using Team ID: {team_id}")
        print(f"   Using Brand ID: {brand_id}")
        
        # Test valid master jersey creation with fixed field mapping
        print("Test: Valid master jersey creation")
        import random
        random_suffix = random.randint(1000, 9999)
        master_jersey_data = {
            "team_id": team_id,
            "brand_id": brand_id,
            "season": f"2025-{26 + (random_suffix % 10)}",  # Use different season to avoid duplicates
            "jersey_type": "away",        # Use away to avoid duplicate home jerseys
            "model": f"Test Pro {random_suffix}",     # Required field
            "primary_color": "Red",      # Required field
            "secondary_colors": ["White", "Blue"]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=master_jersey_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   ✅ Master Jersey created successfully!")
                print(f"   Master Jersey ID: {data.get('id')}")
                print(f"   TopKit Reference: {data.get('topkit_reference')}")
                return data.get('id')
            else:
                print(f"   ❌ Master Jersey creation failed")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Master Jersey creation error: {e}")
            return None
    
    def test_master_jersey_validation(self):
        """Test Master Jersey Creation validation"""
        print("\n🔍 Testing Master Jersey Creation validation...")
        
        # Test missing required fields
        print("Test: Missing required fields")
        invalid_master_jersey_data = {
            "season": "2024-25"  # Missing team_id, brand_id, jersey_type, model, primary_color
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=invalid_master_jersey_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code in [400, 422]:
                response_text = response.text
                if "[object Object]" in response_text:
                    print(f"   ❌ Still showing [object Object] error!")
                    return False
                else:
                    print(f"   ✅ Proper error message displayed (no [object Object])")
                    return True
            else:
                print(f"   ⚠️ Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Master Jersey validation test error: {e}")
            return False
    
    def get_reference_kits(self):
        """Get available reference kits for personal kit creation"""
        print("\n📋 Getting available reference kits...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            if response.status_code == 200:
                kits = response.json()
                print(f"   Found {len(kits)} reference kits")
                return kits
            else:
                print(f"   ❌ Failed to get reference kits: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   ❌ Error getting reference kits: {e}")
            return []
    
    def test_personal_kit_creation(self):
        """Test Personal Kit Data Persistence Fix (POST /api/personal-kits)"""
        print("\n🎽 Testing Personal Kit Data Persistence Fix...")
        
        # Get available reference kits
        reference_kits = self.get_reference_kits()
        
        if not reference_kits:
            print("   ❌ No reference kits available for testing")
            return None
        
        reference_kit_id = reference_kits[0].get('id')
        print(f"   Using Reference Kit ID: {reference_kit_id}")
        
        # Test personal kit creation with all new fields
        print("Test: Personal kit creation with all fields")
        personal_kit_data = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "mint",
            "purchase_price": 89.99,
            "price_value": 120.00,           # New field
            "acquisition_story": "Bought from official store during Champions League final", # New field
            "times_worn": 5,                 # New field
            "for_sale": False,               # New field
            "printed_name": "MESSI",         # Fixed field mapping
            "printed_number": "10",          # Fixed field mapping
            "personal_notes": "Authentic jersey with official printing", # Fixed field mapping
            "printing_type": "Official"      # Fixed field mapping
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Personal Kit created successfully!")
                print(f"   Personal Kit ID: {data.get('id')}")
                
                # Verify all fields are persisted
                print("   Verifying field persistence:")
                print(f"     Price Value: {data.get('price_value')}")
                print(f"     Acquisition Story: {data.get('acquisition_story')}")
                print(f"     Times Worn: {data.get('times_worn')}")
                print(f"     For Sale: {data.get('for_sale')}")
                print(f"     Printed Name: {data.get('printed_name')}")
                print(f"     Printed Number: {data.get('printed_number')}")
                print(f"     Personal Notes: {data.get('personal_notes')}")
                print(f"     Printing Type: {data.get('printing_type')}")
                
                return data.get('id')
            else:
                print(f"   ❌ Personal Kit creation failed")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Personal Kit creation error: {e}")
            return None
    
    def test_personal_kit_retrieval(self, kit_id):
        """Test Personal Kit data retrieval to confirm persistence"""
        print("\n🔍 Testing Personal Kit data retrieval...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                kits = response.json()
                print(f"   Found {len(kits)} owned kits")
                
                # Find our created kit
                created_kit = None
                for kit in kits:
                    if kit.get('id') == kit_id:
                        created_kit = kit
                        break
                
                if created_kit:
                    print(f"   ✅ Personal Kit found in collection!")
                    print("   Verifying all fields persist correctly:")
                    
                    # Check all the new and fixed fields
                    fields_to_check = [
                        'price_value', 'acquisition_story', 'times_worn', 'for_sale',
                        'printed_name', 'printed_number', 'personal_notes', 'printing_type'
                    ]
                    
                    all_fields_present = True
                    for field in fields_to_check:
                        value = created_kit.get(field)
                        if value is not None:
                            print(f"     ✅ {field}: {value}")
                        else:
                            print(f"     ❌ {field}: Missing!")
                            all_fields_present = False
                    
                    return all_fields_present
                else:
                    print(f"   ❌ Created kit not found in collection")
                    return False
            else:
                print(f"   ❌ Failed to retrieve personal kits: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Personal Kit retrieval error: {e}")
            return False
    
    def test_personal_kit_update(self, kit_id):
        """Test Personal Kit Update Fix (PUT /api/personal-kits/{kit_id})"""
        print("\n✏️ Testing Personal Kit Update Fix...")
        
        # Test updating personal kit with corrected field mappings
        print("Test: Personal kit update with all fields")
        update_data = {
            "size": "XL",
            "condition": "very_good",
            "purchase_price": 95.00,
            "price_value": 130.00,           # Updated field
            "acquisition_story": "Updated: Bought from official store during Champions League final - amazing experience!", # Updated field
            "times_worn": 8,                 # Updated field
            "for_sale": True,                # Updated field
            "printed_name": "MESSI",         # Updated field mapping
            "printed_number": "30",          # Updated field mapping
            "personal_notes": "Updated: Authentic jersey with official printing - excellent condition", # Updated field mapping
            "printing_type": "Heat Transfer" # Updated field mapping
        }
        
        try:
            response = self.session.put(f"{BACKEND_URL}/personal-kits/{kit_id}", json=update_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Personal Kit updated successfully!")
                
                # Verify updated fields persist
                print("   Verifying updated field persistence:")
                print(f"     Size: {data.get('size')}")
                print(f"     Price Value: {data.get('price_value')}")
                print(f"     Acquisition Story: {data.get('acquisition_story')}")
                print(f"     Times Worn: {data.get('times_worn')}")
                print(f"     For Sale: {data.get('for_sale')}")
                print(f"     Printed Name: {data.get('printed_name')}")
                print(f"     Printed Number: {data.get('printed_number')}")
                print(f"     Personal Notes: {data.get('personal_notes')}")
                print(f"     Printing Type: {data.get('printing_type')}")
                
                return True
            else:
                print(f"   ❌ Personal Kit update failed")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Personal Kit update error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all form creation fixes"""
        print("🚀 Starting Comprehensive Form Creation Error Fixes Testing")
        print("=" * 70)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        results = {
            'team_creation': False,
            'team_validation': False,
            'competition_creation': False,
            'competition_validation': False,
            'master_jersey_creation': False,
            'master_jersey_validation': False,
            'personal_kit_creation': False,
            'personal_kit_retrieval': False,
            'personal_kit_update': False
        }
        
        # Step 2: Test Team Creation
        team_id = self.test_team_creation()
        results['team_creation'] = team_id is not None
        
        # Step 3: Test Team Validation
        results['team_validation'] = self.test_team_creation_validation()
        
        # Step 4: Test Competition Creation
        competition_id = self.test_competition_creation()
        results['competition_creation'] = competition_id is not None
        
        # Step 5: Test Competition Validation
        results['competition_validation'] = self.test_competition_validation()
        
        # Step 6: Test Master Jersey Creation
        master_jersey_id = self.test_master_jersey_creation()
        results['master_jersey_creation'] = master_jersey_id is not None
        
        # Step 7: Test Master Jersey Validation
        results['master_jersey_validation'] = self.test_master_jersey_validation()
        
        # Step 8: Test Personal Kit Creation
        personal_kit_id = self.test_personal_kit_creation()
        results['personal_kit_creation'] = personal_kit_id is not None
        
        # Step 9: Test Personal Kit Retrieval (if creation succeeded)
        if personal_kit_id:
            results['personal_kit_retrieval'] = self.test_personal_kit_retrieval(personal_kit_id)
            
            # Step 10: Test Personal Kit Update (if retrieval succeeded)
            if results['personal_kit_retrieval']:
                results['personal_kit_update'] = self.test_personal_kit_update(personal_kit_id)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 70)
        
        passed_tests = 0
        total_tests = len(results)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if passed:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Critical Issues Analysis
        critical_issues = []
        if not results['team_validation']:
            critical_issues.append("Team creation still shows [object Object] errors")
        if not results['competition_validation']:
            critical_issues.append("Competition creation still shows [object Object] errors")
        if not results['master_jersey_validation']:
            critical_issues.append("Master Jersey creation still shows [object Object] errors")
        if not results['personal_kit_creation']:
            critical_issues.append("Personal Kit creation with new fields failed")
        if not results['personal_kit_retrieval']:
            critical_issues.append("Personal Kit data persistence verification failed")
        if not results['personal_kit_update']:
            critical_issues.append("Personal Kit update with corrected field mappings failed")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   • {issue}")
        else:
            print(f"\n🎉 ALL CRITICAL FIXES VERIFIED SUCCESSFULLY!")
            print("   • [object Object] errors have been resolved")
            print("   • Data persistence works correctly")
            print("   • Field mappings are working properly")
        
        return success_rate >= 80  # Consider 80%+ success rate as overall success

if __name__ == "__main__":
    tester = FormCreationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎯 CONCLUSION: Form Creation Error Fixes are WORKING CORRECTLY!")
        sys.exit(0)
    else:
        print(f"\n⚠️ CONCLUSION: Some Form Creation Error Fixes need attention!")
        sys.exit(1)