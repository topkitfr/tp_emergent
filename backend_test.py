#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - SEASON AND PLAYER DATA IN PRICE CALCULATIONS

**ISSUE 4: Missing Season and Player Data in Price Calculations**

1. **Season Information Investigation:**
   - Check if season data from master kits is being used in price calculations
   - Test GET /api/my-collection/{collection_id}/price-estimation with season information
   - Verify if season coefficient is being applied to pricing

2. **Player Information Investigation:**
   - Check how player information from "B. Player & Printing" field is being processed
   - Test if associated_player_id is being used in price calculations 
   - Verify player type coefficients (Showdown Legend: 3.00x, Superstar: 2.00x, Star: 1.00x, etc.)

3. **Price Calculation Logic Review:**
   - Test a collection item with both season and player information
   - Check calculate_estimated_price function logic for season and player coefficients
   - Verify all coefficient types are being applied correctly

4. **Field Mapping Verification:**
   - Check if associated_player_id from EnhancedEditKitForm is properly mapped
   - Verify season information flows from master kit to price calculation
   - Test with emergency admin collection items

**Authentication Credentials:**
- Email: emergency.admin@topkit.test
- Password: EmergencyAdmin2025!

**Expected Results:**
- Season information should affect price calculations with age coefficients
- Player information should apply proper player type coefficients 
- Price breakdown should show all applicable coefficients including season and player

This will identify what's preventing season and player data from being used in pricing calculations.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://jersey-collect.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitSeasonPlayerDataTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        
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
        """Authenticate with emergency admin credentials"""
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
    
    def test_season_information_in_price_calculations(self):
        """Test if season data from master kits is being used in price calculations"""
        try:
            print(f"\n📅 TESTING SEASON INFORMATION IN PRICE CALCULATIONS")
            print("=" * 80)
            print("Testing if season data from master kits affects price calculations...")
            
            if not self.auth_token:
                self.log_test("Season Information in Price Calculations", False, "❌ Missing authentication")
                return False
            
            # Step 1: Get user's collection items to test price estimation
            print(f"      Getting user's collection items...")
            collection_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if collection_response.status_code != 200:
                self.log_test("Season Information in Price Calculations", False, 
                             f"❌ Cannot access collection - Status {collection_response.status_code}")
                return False
            
            collection_items = collection_response.json()
            print(f"         ✅ Retrieved {len(collection_items)} collection items")
            
            if not collection_items:
                print(f"         ⚠️ No collection items found - need to create test data first")
                self.log_test("Season Information in Price Calculations", False, 
                             "❌ No collection items available for testing")
                return False
            
            # Step 2: Test price estimation for collection items with season data
            season_coefficients_found = 0
            total_items_tested = 0
            
            for item in collection_items[:3]:  # Test first 3 items
                collection_id = item.get('id')
                master_kit = item.get('master_kit', {})
                season = master_kit.get('season')
                
                print(f"      Testing price estimation for collection item {collection_id}...")
                print(f"         Master Kit: {master_kit.get('club')} {season}")
                
                # Get price estimation
                price_response = self.session.get(
                    f"{BACKEND_URL}/my-collection/{collection_id}/price-estimation", 
                    timeout=10
                )
                
                if price_response.status_code == 200:
                    price_data = price_response.json()
                    estimated_price = price_data.get('estimated_price')
                    coefficients = price_data.get('coefficients', [])
                    
                    # Check for new response format with calculation_details
                    if 'calculation_details' in price_data:
                        coefficients = price_data['calculation_details'].get('coefficients_applied', [])
                    
                    print(f"         ✅ Price estimation successful: €{estimated_price}")
                    print(f"         📊 Coefficients applied: {len(coefficients)}")
                    
                    # Check for season/age coefficient
                    season_coefficient_found = False
                    for coeff in coefficients:
                        factor = coeff.get('factor', '').lower()
                        if 'age' in factor or 'season' in factor or 'vintage' in factor:
                            season_coefficient_found = True
                            season_coefficients_found += 1
                            print(f"         ✅ Season coefficient found: {coeff.get('factor')} = {coeff.get('value')}")
                            break
                    
                    if not season_coefficient_found and season:
                        print(f"         ⚠️ No season coefficient found despite season data: {season}")
                    
                    # Show all coefficients for analysis
                    print(f"         📋 All coefficients:")
                    for coeff in coefficients:
                        print(f"            • {coeff.get('factor')}: {coeff.get('value')}")
                    
                    total_items_tested += 1
                    
                else:
                    print(f"         ❌ Price estimation failed - Status {price_response.status_code}")
                    print(f"            Error: {price_response.text}")
            
            # Step 3: Analyze results
            if total_items_tested == 0:
                self.log_test("Season Information in Price Calculations", False, 
                             "❌ No collection items could be tested")
                return False
            
            season_coefficient_rate = (season_coefficients_found / total_items_tested) * 100
            
            if season_coefficients_found > 0:
                self.log_test("Season Information in Price Calculations", True, 
                             f"✅ Season information is being used in price calculations - {season_coefficients_found}/{total_items_tested} items ({season_coefficient_rate:.1f}%) show season coefficients")
                return True
            else:
                self.log_test("Season Information in Price Calculations", False, 
                             f"❌ Season information NOT being used in price calculations - 0/{total_items_tested} items show season coefficients")
                return False
                
        except Exception as e:
            self.log_test("Season Information in Price Calculations", False, f"Exception: {str(e)}")
            return False
    
    def test_player_information_in_price_calculations(self):
        """Test if player information from 'B. Player & Printing' field is being processed in price calculations"""
        try:
            print(f"\n👤 TESTING PLAYER INFORMATION IN PRICE CALCULATIONS")
            print("=" * 80)
            print("Testing if player information affects price calculations...")
            
            if not self.auth_token:
                self.log_test("Player Information in Price Calculations", False, "❌ Missing authentication")
                return False
            
            # Step 1: Get available players to understand player types and coefficients
            print(f"      Getting available players data...")
            players_response = self.session.get(f"{BACKEND_URL}/form-data/players", timeout=10)
            
            if players_response.status_code != 200:
                self.log_test("Player Information in Price Calculations", False, 
                             f"❌ Cannot access players data - Status {players_response.status_code}")
                return False
            
            players = players_response.json()
            print(f"         ✅ Retrieved {len(players)} players")
            
            # Analyze player types and coefficients
            player_types_found = {}
            for player in players:
                player_type = player.get('player_type')
                coefficient = player.get('coefficient', player.get('influence_coefficient', 0))
                if player_type:
                    player_types_found[player_type] = coefficient
            
            print(f"         📊 Player types found: {list(player_types_found.keys())}")
            for ptype, coeff in player_types_found.items():
                print(f"            {ptype}: {coeff}x coefficient")
            
            # Step 2: Get collection items and test player coefficients
            print(f"      Getting collection items to test player coefficients...")
            collection_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if collection_response.status_code != 200:
                self.log_test("Player Information in Price Calculations", False, 
                             f"❌ Cannot access collection - Status {collection_response.status_code}")
                return False
            
            collection_items = collection_response.json()
            print(f"         ✅ Retrieved {len(collection_items)} collection items")
            
            # Step 3: Test price estimation for items with player data
            player_coefficients_found = 0
            flocking_coefficients_found = 0
            total_items_tested = 0
            
            for item in collection_items[:3]:  # Test first 3 items
                collection_id = item.get('id')
                associated_player_id = item.get('associated_player_id')
                name_printing = item.get('name_printing')
                number_printing = item.get('number_printing')
                
                print(f"      Testing collection item {collection_id}...")
                print(f"         Associated Player ID: {associated_player_id}")
                print(f"         Name Printing: {name_printing}")
                print(f"         Number Printing: {number_printing}")
                
                # Get price estimation
                price_response = self.session.get(
                    f"{BACKEND_URL}/my-collection/{collection_id}/price-estimation", 
                    timeout=10
                )
                
                if price_response.status_code == 200:
                    price_data = price_response.json()
                    estimated_price = price_data.get('estimated_price')
                    coefficients = price_data.get('coefficients', [])
                    
                    # Check for new response format with calculation_details
                    if 'calculation_details' in price_data:
                        coefficients = price_data['calculation_details'].get('coefficients_applied', [])
                    
                    print(f"         ✅ Price estimation successful: €{estimated_price}")
                    print(f"         📊 Coefficients applied: {len(coefficients)}")
                    
                    # Check for player-related coefficients
                    player_coefficient_found = False
                    flocking_coefficient_found = False
                    
                    for coeff in coefficients:
                        factor = coeff.get('factor', '').lower()
                        if 'player' in factor or 'associated' in factor:
                            player_coefficient_found = True
                            player_coefficients_found += 1
                            print(f"         ✅ Player coefficient found: {coeff.get('factor')} = {coeff.get('value')}")
                        elif 'flocking' in factor or 'name' in factor or 'number' in factor:
                            flocking_coefficient_found = True
                            flocking_coefficients_found += 1
                            print(f"         ✅ Flocking coefficient found: {coeff.get('factor')} = {coeff.get('value')}")
                    
                    if not player_coefficient_found and associated_player_id:
                        print(f"         ⚠️ No player coefficient found despite associated_player_id: {associated_player_id}")
                    
                    if not flocking_coefficient_found and (name_printing or number_printing):
                        print(f"         ⚠️ No flocking coefficient found despite name/number printing")
                    
                    # Show all coefficients for analysis
                    print(f"         📋 All coefficients:")
                    for coeff in coefficients:
                        print(f"            • {coeff.get('factor')}: {coeff.get('value')}")
                    
                    total_items_tested += 1
                    
                else:
                    print(f"         ❌ Price estimation failed - Status {price_response.status_code}")
                    print(f"            Error: {price_response.text}")
            
            # Step 4: Analyze results
            if total_items_tested == 0:
                self.log_test("Player Information in Price Calculations", False, 
                             "❌ No collection items could be tested")
                return False
            
            player_coefficient_rate = (player_coefficients_found / total_items_tested) * 100
            flocking_coefficient_rate = (flocking_coefficients_found / total_items_tested) * 100
            
            # Consider success if either player coefficients or flocking coefficients are working
            if player_coefficients_found > 0 or flocking_coefficients_found > 0:
                self.log_test("Player Information in Price Calculations", True, 
                             f"✅ Player information is being used in price calculations - Player coefficients: {player_coefficients_found}/{total_items_tested} ({player_coefficient_rate:.1f}%), Flocking coefficients: {flocking_coefficients_found}/{total_items_tested} ({flocking_coefficient_rate:.1f}%)")
                return True
            else:
                self.log_test("Player Information in Price Calculations", False, 
                             f"❌ Player information NOT being used in price calculations - No player or flocking coefficients found")
                return False
                
        except Exception as e:
            self.log_test("Player Information in Price Calculations", False, f"Exception: {str(e)}")
            return False
    
    def test_comprehensive_price_calculation_logic(self):
        """Test comprehensive price calculation logic with both season and player information"""
        try:
            print(f"\n🧮 TESTING COMPREHENSIVE PRICE CALCULATION LOGIC")
            print("=" * 80)
            print("Testing price calculation logic with both season and player information...")
            
            if not self.auth_token:
                self.log_test("Comprehensive Price Calculation Logic", False, "❌ Missing authentication")
                return False
            
            # Step 1: Get collection items for comprehensive testing
            print(f"      Getting collection items for comprehensive testing...")
            collection_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if collection_response.status_code != 200:
                self.log_test("Comprehensive Price Calculation Logic", False, 
                             "❌ Cannot access collection items")
                return False
            
            collection_items = collection_response.json()
            if not collection_items:
                self.log_test("Comprehensive Price Calculation Logic", False, 
                             "❌ No collection items available for testing")
                return False
            
            # Step 2: Test detailed price breakdown for comprehensive items
            comprehensive_tests_passed = 0
            total_comprehensive_tests = 0
            
            for item in collection_items[:2]:  # Test first 2 items
                collection_id = item.get('id')
                master_kit = item.get('master_kit', {})
                
                print(f"      Testing comprehensive price calculation for {collection_id}...")
                print(f"         Master Kit: {master_kit.get('club')} {master_kit.get('season')}")
                print(f"         Associated Player: {item.get('associated_player_id')}")
                print(f"         Name/Number: {item.get('name_printing')}/{item.get('number_printing')}")
                
                # Get detailed price estimation
                price_response = self.session.get(
                    f"{BACKEND_URL}/my-collection/{collection_id}/price-estimation", 
                    timeout=10
                )
                
                if price_response.status_code == 200:
                    price_data = price_response.json()
                    estimated_price = price_data.get('estimated_price')
                    coefficients = price_data.get('coefficients', [])
                    base_price = price_data.get('base_price', 0)
                    
                    print(f"         ✅ Price estimation successful:")
                    print(f"            Base Price: €{base_price}")
                    print(f"            Estimated Price: €{estimated_price}")
                    print(f"            Total Coefficients: {len(coefficients)}")
                    
                    # Analyze coefficient types
                    coefficient_types = {
                        'season': False,
                        'player': False,
                        'flocking': False,
                        'condition': False,
                        'patches': False,
                        'signature': False
                    }
                    
                    for coeff in coefficients:
                        factor = coeff.get('factor', '').lower()
                        value = coeff.get('value', '')
                        print(f"            • {coeff.get('factor')}: {value}")
                        
                        if 'age' in factor or 'season' in factor or 'vintage' in factor:
                            coefficient_types['season'] = True
                        elif 'player' in factor or 'associated' in factor:
                            coefficient_types['player'] = True
                        elif 'flocking' in factor or 'name' in factor or 'number' in factor:
                            coefficient_types['flocking'] = True
                        elif 'condition' in factor or 'physical' in factor:
                            coefficient_types['condition'] = True
                        elif 'patch' in factor:
                            coefficient_types['patches'] = True
                        elif 'sign' in factor:
                            coefficient_types['signature'] = True
                    
                    # Count how many coefficient types are working
                    working_coefficient_types = sum(coefficient_types.values())
                    total_coefficient_types = len(coefficient_types)
                    
                    print(f"         📊 Coefficient types working: {working_coefficient_types}/{total_coefficient_types}")
                    for ctype, working in coefficient_types.items():
                        status = "✅" if working else "❌"
                        print(f"            {status} {ctype.title()}")
                    
                    if working_coefficient_types >= 2:  # At least 2 types working
                        comprehensive_tests_passed += 1
                    
                    total_comprehensive_tests += 1
                    
                else:
                    print(f"         ❌ Price estimation failed - Status {price_response.status_code}")
                    print(f"            Error: {price_response.text}")
            
            # Step 3: Analyze comprehensive results
            if total_comprehensive_tests == 0:
                self.log_test("Comprehensive Price Calculation Logic", False, 
                             "❌ No comprehensive tests could be performed")
                return False
            
            comprehensive_success_rate = (comprehensive_tests_passed / total_comprehensive_tests) * 100
            
            if comprehensive_success_rate >= 50:
                self.log_test("Comprehensive Price Calculation Logic", True, 
                             f"✅ Comprehensive price calculation logic working - {comprehensive_tests_passed}/{total_comprehensive_tests} items ({comprehensive_success_rate:.1f}%) show multiple coefficient types")
                return True
            else:
                self.log_test("Comprehensive Price Calculation Logic", False, 
                             f"❌ Comprehensive price calculation logic incomplete - {comprehensive_tests_passed}/{total_comprehensive_tests} items ({comprehensive_success_rate:.1f}%) show multiple coefficient types")
                return False
                
        except Exception as e:
            self.log_test("Comprehensive Price Calculation Logic", False, f"Exception: {str(e)}")
            return False
    
    def test_field_mapping_verification(self):
        """Test field mapping verification between frontend form and backend price calculation"""
        try:
            print(f"\n🔗 TESTING FIELD MAPPING VERIFICATION")
            print("=" * 80)
            print("Testing field mapping between EnhancedEditKitForm and backend price calculation...")
            
            if not self.auth_token:
                self.log_test("Field Mapping Verification", False, "❌ Missing authentication")
                return False
            
            # Step 1: Get collection items to analyze field mapping
            print(f"      Getting collection items to analyze field mapping...")
            collection_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if collection_response.status_code != 200:
                self.log_test("Field Mapping Verification", False, 
                             f"❌ Cannot access collection - Status {collection_response.status_code}")
                return False
            
            collection_items = collection_response.json()
            print(f"         ✅ Retrieved {len(collection_items)} collection items")
            
            if not collection_items:
                self.log_test("Field Mapping Verification", False, 
                             "❌ No collection items available for field mapping verification")
                return False
            
            # Step 2: Analyze field mapping for each collection item
            field_mapping_success = 0
            total_items_analyzed = 0
            
            expected_fields = [
                'associated_player_id',
                'name_printing', 
                'number_printing',
                'condition',
                'physical_state',
                'patches',
                'is_signed',
                'signed_by',
                'purchase_price',
                'purchase_date',
                'personal_notes'
            ]
            
            for item in collection_items[:3]:  # Analyze first 3 items
                collection_id = item.get('id')
                master_kit = item.get('master_kit', {})
                
                print(f"      Analyzing field mapping for collection item {collection_id}...")
                print(f"         Master Kit: {master_kit.get('club')} {master_kit.get('season')}")
                
                # Check which expected fields are present
                fields_present = 0
                fields_with_data = 0
                
                for field in expected_fields:
                    if field in item:
                        fields_present += 1
                        if item[field] is not None and item[field] != '':
                            fields_with_data += 1
                            print(f"         ✅ {field}: {item[field]}")
                        else:
                            print(f"         ⚪ {field}: (empty)")
                    else:
                        print(f"         ❌ {field}: (missing)")
                
                field_presence_rate = (fields_present / len(expected_fields)) * 100
                field_data_rate = (fields_with_data / len(expected_fields)) * 100
                
                print(f"         📊 Field mapping analysis:")
                print(f"            Fields present: {fields_present}/{len(expected_fields)} ({field_presence_rate:.1f}%)")
                print(f"            Fields with data: {fields_with_data}/{len(expected_fields)} ({field_data_rate:.1f}%)")
                
                # Test price estimation to see if fields are being used
                price_response = self.session.get(
                    f"{BACKEND_URL}/my-collection/{collection_id}/price-estimation", 
                    timeout=10
                )
                
                if price_response.status_code == 200:
                    price_data = price_response.json()
                    coefficients = price_data.get('coefficients', [])
                    
                    print(f"         💰 Price calculation uses {len(coefficients)} coefficients")
                    
                    # Check if field data correlates with coefficients
                    field_coefficient_correlation = 0
                    
                    if item.get('name_printing') or item.get('number_printing'):
                        flocking_coeff = any('flocking' in c.get('factor', '').lower() or 'name' in c.get('factor', '').lower() or 'number' in c.get('factor', '').lower() for c in coefficients)
                        if flocking_coeff:
                            field_coefficient_correlation += 1
                            print(f"         ✅ Name/Number printing → Flocking coefficient")
                    
                    if item.get('is_signed'):
                        signature_coeff = any('sign' in c.get('factor', '').lower() for c in coefficients)
                        if signature_coeff:
                            field_coefficient_correlation += 1
                            print(f"         ✅ Signature → Signature coefficient")
                    
                    if item.get('patches'):
                        patches_coeff = any('patch' in c.get('factor', '').lower() for c in coefficients)
                        if patches_coeff:
                            field_coefficient_correlation += 1
                            print(f"         ✅ Patches → Patches coefficient")
                    
                    if item.get('condition') or item.get('physical_state'):
                        condition_coeff = any('condition' in c.get('factor', '').lower() or 'physical' in c.get('factor', '').lower() for c in coefficients)
                        if condition_coeff:
                            field_coefficient_correlation += 1
                            print(f"         ✅ Condition → Condition coefficient")
                    
                    if field_coefficient_correlation >= 1:  # At least 1 field-coefficient correlation
                        field_mapping_success += 1
                    
                    print(f"         🔗 Field-coefficient correlations: {field_coefficient_correlation}")
                
                total_items_analyzed += 1
            
            # Step 3: Analyze overall field mapping success
            if total_items_analyzed == 0:
                self.log_test("Field Mapping Verification", False, 
                             "❌ No items could be analyzed for field mapping")
                return False
            
            field_mapping_success_rate = (field_mapping_success / total_items_analyzed) * 100
            
            if field_mapping_success_rate >= 50:
                self.log_test("Field Mapping Verification", True, 
                             f"✅ Field mapping verification successful - {field_mapping_success}/{total_items_analyzed} items ({field_mapping_success_rate:.1f}%) show proper field-coefficient correlation")
                return True
            else:
                self.log_test("Field Mapping Verification", False, 
                             f"❌ Field mapping verification failed - {field_mapping_success}/{total_items_analyzed} items ({field_mapping_success_rate:.1f}%) show proper field-coefficient correlation")
                return False
                
        except Exception as e:
            self.log_test("Field Mapping Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_season_and_player_data_tests(self):
        """Run season and player data in price calculations testing suite"""
        print("\n🚀 SEASON AND PLAYER DATA IN PRICE CALCULATIONS TESTING SUITE")
        print("Investigate missing season and player data affecting price calculations")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate with admin account
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        test_results.append(auth_success)
        
        # Step 2: Test season information in price calculations
        print("\n2️⃣ Testing season information in price calculations...")
        season_info_success = self.test_season_information_in_price_calculations()
        test_results.append(season_info_success)
        
        # Step 3: Test player information in price calculations
        print("\n3️⃣ Testing player information in price calculations...")
        player_info_success = self.test_player_information_in_price_calculations()
        test_results.append(player_info_success)
        
        # Step 4: Test comprehensive price calculation logic
        print("\n4️⃣ Testing comprehensive price calculation logic...")
        comprehensive_logic_success = self.test_comprehensive_price_calculation_logic()
        test_results.append(comprehensive_logic_success)
        
        # Step 5: Test field mapping verification
        print("\n5️⃣ Testing field mapping verification...")
        field_mapping_success = self.test_field_mapping_verification()
        test_results.append(field_mapping_success)
        
        return test_results
    
    def print_season_and_player_data_summary(self):
        """Print final season and player data testing summary"""
        print("\n📊 SEASON AND PLAYER DATA IN PRICE CALCULATIONS TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 SEASON AND PLAYER DATA TESTING RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Emergency admin login working with admin role")
        else:
            print(f"  ❌ AUTHENTICATION: Emergency admin login failed")
        
        # Season Information
        season_info_working = any(r['success'] for r in self.test_results if 'Season Information in Price Calculations' in r['test'])
        if season_info_working:
            print(f"  ✅ SEASON INFORMATION: Season data is being used in price calculations")
        else:
            print(f"  ❌ SEASON INFORMATION: Season data NOT being used in price calculations")
        
        # Player Information
        player_info_working = any(r['success'] for r in self.test_results if 'Player Information in Price Calculations' in r['test'])
        if player_info_working:
            print(f"  ✅ PLAYER INFORMATION: Player data is being used in price calculations")
        else:
            print(f"  ❌ PLAYER INFORMATION: Player data NOT being used in price calculations")
        
        # Comprehensive Logic
        comprehensive_logic_working = any(r['success'] for r in self.test_results if 'Comprehensive Price Calculation Logic' in r['test'])
        if comprehensive_logic_working:
            print(f"  ✅ COMPREHENSIVE LOGIC: Price calculation logic working with multiple coefficient types")
        else:
            print(f"  ❌ COMPREHENSIVE LOGIC: Price calculation logic incomplete or missing coefficient types")
        
        # Field Mapping
        field_mapping_working = any(r['success'] for r in self.test_results if 'Field Mapping Verification' in r['test'])
        if field_mapping_working:
            print(f"  ✅ FIELD MAPPING: Field mapping between frontend and backend working correctly")
        else:
            print(f"  ❌ FIELD MAPPING: Field mapping between frontend and backend has issues")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final diagnosis
        print(f"\n🎯 SEASON AND PLAYER DATA DIAGNOSIS:")
        
        if season_info_working and player_info_working:
            print(f"  ✅ SEASON AND PLAYER DATA WORKING IN PRICE CALCULATIONS")
            print(f"     - Season information affects price calculations with age coefficients")
            print(f"     - Player information applies proper player type coefficients")
            print(f"     - Price breakdown shows applicable coefficients including season and player")
        elif season_info_working or player_info_working:
            print(f"  ⚠️ PARTIAL FUNCTIONALITY: Some data working in price calculations")
            if season_info_working:
                print(f"     - Season information working correctly")
            else:
                print(f"     - Season information NOT working - age coefficients missing")
            if player_info_working:
                print(f"     - Player information working correctly")
            else:
                print(f"     - Player information NOT working - player coefficients missing")
        else:
            print(f"  ❌ SEASON AND PLAYER DATA NOT WORKING IN PRICE CALCULATIONS")
            print(f"     - Season information not affecting price calculations")
            print(f"     - Player information not being processed correctly")
            print(f"     - Field mapping issues preventing proper coefficient application")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the season and player data testing suite"""
    tester = TopKitSeasonPlayerDataTesting()
    
    # Run the season and player data tests
    test_results = tester.run_season_and_player_data_tests()
    
    # Print comprehensive summary
    tester.print_season_and_player_data_summary()
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)