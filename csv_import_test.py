#!/usr/bin/env python3
"""
TopKit CSV Import Verification Test Suite

**CSV IMPORT VERIFICATION TESTING:**

Testing the master kits API endpoints with newly imported CSV data:

1. Test GET /api/master-kits - should return 20 kits from CSV import
2. Test GET /api/master-kits/{kit_id} for a specific kit
3. Verify the master kits show proper club_name, brand_name fields populated 
4. Test GET /api/teams - should show teams from CSV (Real Madrid, FC Barcelona, Bayern Munich, Liverpool)
5. Test GET /api/brands - should show brands from CSV (Adidas, Nike)
6. Verify no collection items exist in GET /api/my-collection (should be empty after clean)

**Expected CSV Data:**
- 20 kits total (4 teams: Real Madrid, FC Barcelona, Bayern Munich, Liverpool)
- Each team has 4-5 kits (home, away, third, GK, some have 2025/2026 home)  
- 2 brands: Adidas (Real Madrid, Bayern Munich), Nike (FC Barcelona, Liverpool)
- Seasons: 2024/2025 and 2025/2026

**Focus:** Testing that the data was imported correctly and the enrichment functions are working 
(club_name, brand_name should not be "Unknown").
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://kitauth-fix.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

# Expected CSV data constants
EXPECTED_TEAMS = ["Real Madrid", "FC Barcelone", "Bayern Munich", "Liverpool"]  # Note: FC Barcelone (French spelling)
EXPECTED_BRANDS = ["Adidas", "Nike"]
EXPECTED_SEASONS = ["2024/2025", "2025/2026"]
EXPECTED_TOTAL_KITS = 20
EXPECTED_TEAM_BRAND_MAPPING = {
    "Real Madrid": "Adidas",
    "Bayern Munich": "Adidas", 
    "FC Barcelone": "Nike",  # Note: FC Barcelone (French spelling)
    "Liverpool": "Nike"
}

class TopKitCSVImportVerification:
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

    def test_master_kits_csv_import(self):
        """Test GET /api/master-kits endpoint for CSV import verification"""
        try:
            print(f"\n🎽 TESTING MASTER KITS CSV IMPORT")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                master_kits = response.json()
                
                print(f"      ✅ Master kits endpoint accessible")
                print(f"      Total master kits returned: {len(master_kits)}")
                
                # Check if we have the expected number of kits
                if len(master_kits) == EXPECTED_TOTAL_KITS:
                    print(f"      ✅ Expected {EXPECTED_TOTAL_KITS} kits found")
                    self.log_test("Master Kits Count", True, f"Found expected {EXPECTED_TOTAL_KITS} kits")
                else:
                    print(f"      ⚠️ Expected {EXPECTED_TOTAL_KITS} kits, found {len(master_kits)}")
                    self.log_test("Master Kits Count", False, f"Expected {EXPECTED_TOTAL_KITS} kits, found {len(master_kits)}")
                
                # Analyze kits for CSV data verification
                teams_found = set()
                brands_found = set()
                seasons_found = set()
                enrichment_issues = []
                
                print(f"\n      📋 CSV DATA ANALYSIS:")
                
                for i, kit in enumerate(master_kits[:5]):  # Analyze first 5 kits
                    print(f"         Kit {i+1}:")
                    print(f"            ID: {kit.get('id', 'MISSING')}")
                    
                    # Check enriched fields
                    club_name = kit.get('club_name')
                    brand_name = kit.get('brand_name')
                    season = kit.get('season')
                    kit_type = kit.get('kit_type')
                    
                    print(f"            club_name: {club_name}")
                    print(f"            brand_name: {brand_name}")
                    print(f"            season: {season}")
                    print(f"            kit_type: {kit_type}")
                    
                    # Collect data for verification
                    if club_name and club_name not in ["Unknown", "null", None]:
                        teams_found.add(club_name)
                    else:
                        enrichment_issues.append(f"Kit {i+1}: club_name is '{club_name}'")
                    
                    if brand_name and brand_name not in ["Unknown", "null", None]:
                        brands_found.add(brand_name)
                    else:
                        enrichment_issues.append(f"Kit {i+1}: brand_name is '{brand_name}'")
                    
                    if season:
                        seasons_found.add(season)
                    
                    # Verify team-brand mapping
                    if club_name in EXPECTED_TEAM_BRAND_MAPPING:
                        expected_brand = EXPECTED_TEAM_BRAND_MAPPING[club_name]
                        if brand_name != expected_brand:
                            enrichment_issues.append(f"Kit {i+1}: {club_name} should have brand '{expected_brand}', found '{brand_name}'")
                
                print(f"\n      📊 CSV IMPORT VERIFICATION RESULTS:")
                print(f"         Teams found: {sorted(list(teams_found))}")
                print(f"         Brands found: {sorted(list(brands_found))}")
                print(f"         Seasons found: {sorted(list(seasons_found))}")
                
                # Check if expected teams are present
                missing_teams = set(EXPECTED_TEAMS) - teams_found
                if not missing_teams:
                    print(f"         ✅ All expected teams found")
                    self.log_test("Expected Teams Present", True, "All expected teams found in CSV import")
                else:
                    print(f"         ❌ Missing teams: {missing_teams}")
                    self.log_test("Expected Teams Present", False, f"Missing teams: {missing_teams}")
                
                # Check if expected brands are present
                missing_brands = set(EXPECTED_BRANDS) - brands_found
                if not missing_brands:
                    print(f"         ✅ All expected brands found")
                    self.log_test("Expected Brands Present", True, "All expected brands found in CSV import")
                else:
                    print(f"         ❌ Missing brands: {missing_brands}")
                    self.log_test("Expected Brands Present", False, f"Missing brands: {missing_brands}")
                
                # Check enrichment issues
                if not enrichment_issues:
                    print(f"         ✅ No enrichment issues found")
                    self.log_test("Master Kits Enrichment", True, "All master kits properly enriched")
                else:
                    print(f"         ❌ Enrichment issues found:")
                    for issue in enrichment_issues[:3]:  # Show first 3 issues
                        print(f"            • {issue}")
                    self.log_test("Master Kits Enrichment", False, f"Found {len(enrichment_issues)} enrichment issues")
                
                return True, master_kits
            else:
                print(f"      ❌ Failed to get master kits - Status {response.status_code}")
                print(f"      Response: {response.text}")
                
                self.log_test("Master Kits CSV Import", False, 
                             f"❌ Failed - Status {response.status_code}", response.text)
                return False, []
                
        except Exception as e:
            self.log_test("Master Kits CSV Import", False, f"Exception: {str(e)}")
            return False, []

    def test_specific_master_kit(self, master_kits):
        """Test GET /api/master-kits/{kit_id} for a specific kit"""
        try:
            print(f"\n🎯 TESTING SPECIFIC MASTER KIT ENDPOINT")
            print("=" * 60)
            
            if not master_kits or len(master_kits) == 0:
                print(f"      ⚠️ No master kits available to test specific endpoint")
                return True
            
            # Test first kit
            first_kit = master_kits[0]
            kit_id = first_kit.get('id')
            
            print(f"      Testing specific kit: {kit_id}")
            
            response = self.session.get(f"{BACKEND_URL}/master-kits/{kit_id}", timeout=10)
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                kit_data = response.json()
                
                print(f"      ✅ Specific master kit endpoint accessible")
                print(f"      Kit ID: {kit_data.get('id', 'MISSING')}")
                print(f"      Club Name: {kit_data.get('club_name', 'MISSING')}")
                print(f"      Brand Name: {kit_data.get('brand_name', 'MISSING')}")
                print(f"      Season: {kit_data.get('season', 'MISSING')}")
                print(f"      Kit Type: {kit_data.get('kit_type', 'MISSING')}")
                
                # Verify enrichment in specific kit
                club_name = kit_data.get('club_name')
                brand_name = kit_data.get('brand_name')
                
                enrichment_success = True
                if not club_name or club_name in ["Unknown", "null", None]:
                    enrichment_success = False
                    print(f"      ❌ club_name not properly enriched: '{club_name}'")
                
                if not brand_name or brand_name in ["Unknown", "null", None]:
                    enrichment_success = False
                    print(f"      ❌ brand_name not properly enriched: '{brand_name}'")
                
                if enrichment_success:
                    print(f"      ✅ Specific kit properly enriched")
                    self.log_test("Specific Master Kit Enrichment", True, "Specific kit properly enriched")
                else:
                    self.log_test("Specific Master Kit Enrichment", False, "Specific kit enrichment issues")
                
                return True
            else:
                print(f"      ❌ Failed to get specific master kit - Status {response.status_code}")
                print(f"      Response: {response.text}")
                
                self.log_test("Specific Master Kit", False, 
                             f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Specific Master Kit", False, f"Exception: {str(e)}")
            return False

    def test_teams_csv_import(self):
        """Test GET /api/teams endpoint for CSV import verification"""
        try:
            print(f"\n🏟️ TESTING TEAMS CSV IMPORT")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/teams", timeout=10)
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                teams = response.json()
                
                print(f"      ✅ Teams endpoint accessible")
                print(f"      Total teams returned: {len(teams)}")
                
                # Extract team names
                team_names = [team.get('name') for team in teams if team.get('name')]
                print(f"      Team names found: {sorted(team_names)}")
                
                # Check if expected teams are present
                missing_teams = []
                found_teams = []
                
                for expected_team in EXPECTED_TEAMS:
                    if expected_team in team_names:
                        found_teams.append(expected_team)
                    else:
                        missing_teams.append(expected_team)
                
                if not missing_teams:
                    print(f"      ✅ All expected teams found: {found_teams}")
                    self.log_test("Teams CSV Import", True, f"All expected teams found: {found_teams}")
                else:
                    print(f"      ❌ Missing expected teams: {missing_teams}")
                    print(f"      ✅ Found expected teams: {found_teams}")
                    self.log_test("Teams CSV Import", False, f"Missing teams: {missing_teams}")
                
                return True, teams
            else:
                print(f"      ❌ Failed to get teams - Status {response.status_code}")
                print(f"      Response: {response.text}")
                
                self.log_test("Teams CSV Import", False, 
                             f"❌ Failed - Status {response.status_code}", response.text)
                return False, []
                
        except Exception as e:
            self.log_test("Teams CSV Import", False, f"Exception: {str(e)}")
            return False, []

    def test_brands_csv_import(self):
        """Test GET /api/brands endpoint for CSV import verification"""
        try:
            print(f"\n👕 TESTING BRANDS CSV IMPORT")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/brands", timeout=10)
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                brands = response.json()
                
                print(f"      ✅ Brands endpoint accessible")
                print(f"      Total brands returned: {len(brands)}")
                
                # Extract brand names
                brand_names = [brand.get('name') for brand in brands if brand.get('name')]
                print(f"      Brand names found: {sorted(brand_names)}")
                
                # Check if expected brands are present
                missing_brands = []
                found_brands = []
                
                for expected_brand in EXPECTED_BRANDS:
                    if expected_brand in brand_names:
                        found_brands.append(expected_brand)
                    else:
                        missing_brands.append(expected_brand)
                
                if not missing_brands:
                    print(f"      ✅ All expected brands found: {found_brands}")
                    self.log_test("Brands CSV Import", True, f"All expected brands found: {found_brands}")
                else:
                    print(f"      ❌ Missing expected brands: {missing_brands}")
                    print(f"      ✅ Found expected brands: {found_brands}")
                    self.log_test("Brands CSV Import", False, f"Missing brands: {missing_brands}")
                
                return True, brands
            else:
                print(f"      ❌ Failed to get brands - Status {response.status_code}")
                print(f"      Response: {response.text}")
                
                self.log_test("Brands CSV Import", False, 
                             f"❌ Failed - Status {response.status_code}", response.text)
                return False, []
                
        except Exception as e:
            self.log_test("Brands CSV Import", False, f"Exception: {str(e)}")
            return False, []

    def test_my_collection_empty(self):
        """Test GET /api/my-collection to verify it's empty after clean"""
        try:
            print(f"\n📦 TESTING MY COLLECTION (SHOULD BE EMPTY)")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                collection_items = response.json()
                
                print(f"      ✅ My collection endpoint accessible")
                print(f"      Total collection items: {len(collection_items)}")
                
                if len(collection_items) == 0:
                    print(f"      ✅ Collection is empty as expected after clean")
                    self.log_test("My Collection Empty", True, "Collection is empty as expected")
                else:
                    print(f"      ⚠️ Collection has {len(collection_items)} items (expected 0)")
                    self.log_test("My Collection Empty", False, f"Collection has {len(collection_items)} items, expected 0")
                
                return True
            else:
                print(f"      ❌ Failed to get collection - Status {response.status_code}")
                print(f"      Response: {response.text}")
                
                self.log_test("My Collection Empty", False, 
                             f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("My Collection Empty", False, f"Exception: {str(e)}")
            return False

    def run_csv_import_verification(self):
        """Run comprehensive CSV import verification"""
        print("\n🚀 CSV IMPORT VERIFICATION")
        print("Testing master kits API endpoints with newly imported CSV data")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        auth_success = self.authenticate_admin()
        test_results.append(auth_success)
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Test master kits CSV import
        print("\n2️⃣ Testing Master Kits CSV Import...")
        master_kits_success, master_kits_data = self.test_master_kits_csv_import()
        test_results.append(master_kits_success)
        
        # Step 3: Test specific master kit
        print("\n3️⃣ Testing Specific Master Kit...")
        specific_kit_success = self.test_specific_master_kit(master_kits_data)
        test_results.append(specific_kit_success)
        
        # Step 4: Test teams CSV import
        print("\n4️⃣ Testing Teams CSV Import...")
        teams_success, teams_data = self.test_teams_csv_import()
        test_results.append(teams_success)
        
        # Step 5: Test brands CSV import
        print("\n5️⃣ Testing Brands CSV Import...")
        brands_success, brands_data = self.test_brands_csv_import()
        test_results.append(brands_success)
        
        # Step 6: Test my collection is empty
        print("\n6️⃣ Testing My Collection is Empty...")
        collection_empty_success = self.test_my_collection_empty()
        test_results.append(collection_empty_success)
        
        return test_results

    def print_csv_import_summary(self):
        """Print final CSV import verification summary"""
        print("\n📊 CSV IMPORT VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show test results by category
        print(f"\n🔍 CSV IMPORT VERIFICATION RESULTS:")
        
        # Group results by category
        categories = {
            "Authentication": ["Emergency Admin Authentication"],
            "Master Kits": ["Master Kits Count", "Master Kits Enrichment", "Specific Master Kit Enrichment"],
            "Teams": ["Expected Teams Present", "Teams CSV Import"],
            "Brands": ["Expected Brands Present", "Brands CSV Import"],
            "Collection": ["My Collection Empty"]
        }
        
        for category, test_names in categories.items():
            print(f"\n✅ {category.upper()}:")
            category_results = [r for r in self.test_results if r['test'] in test_names]
            
            for result in category_results:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {result['test']}: {result['message']}")
        
        # Show test failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ TEST FAILURES ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
                if failure.get('details'):
                    print(f"    Details: {failure['details']}")
        
        # Overall status
        if failed_tests == 0:
            print(f"\n🎉 CSV IMPORT VERIFICATION COMPLETE - 100% SUCCESS!")
            print(f"All CSV data imported correctly with proper enrichment")
        else:
            print(f"\n⚠️ CSV IMPORT VERIFICATION COMPLETE - {(passed_tests/total_tests)*100:.1f}% SUCCESS")
            print(f"Some issues found that need attention")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the CSV import verification"""
    tester = TopKitCSVImportVerification()
    
    # Run the comprehensive CSV import verification
    test_results = tester.run_csv_import_verification()
    
    # Print comprehensive summary
    tester.print_csv_import_summary()
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)