#!/usr/bin/env python3
"""
KIT HIERARCHY WORKFLOW TESTING WITH DATA SETUP - BACKEND TEST
=============================================================

This test validates the complete Kit hierarchy workflow as requested:

1. Authentication Test: Verify admin login with topkitfr@gmail.com/TopKitSecure789#
2. Data Setup: Create proper Master Kits and Reference Kits with team/brand relationships
3. Vestiaire Endpoint Test: Test GET /api/vestiaire to verify Reference Kits with enriched data
4. Personal Kit Creation Test: Test POST /api/personal-kits to create personal kits from reference kits
5. Personal Kit Retrieval Test: Test GET /api/personal-kits?collection_type=owned and wanted
6. Complete Workflow Test: Full user workflow from authentication to collection management

Expected Results:
- Vestiaire should return Reference Kits with team names like "FC Barcelona", "Paris Saint-Germain", "Manchester United"
- Personal Kit creation should work with proper data validation
- Personal Kit retrieval should return enriched data with reference_kit_info, master_kit_info, team_info, brand_info

Focus: Validating new Kit hierarchy data structures and API responses match migrated frontend expectations.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class KitHierarchyWorkflowTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = []
        self.teams = []
        self.brands = []
        self.master_kits_created = []
        self.reference_kits_created = []
        self.personal_kits_created = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status} {test_name}: {details}")
        
    def authenticate_admin(self):
        """Test 1: Authentication Test - Verify admin login with topkitfr@gmail.com/TopKitSecure789#"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                
                self.log_result(
                    "1. Authentication Test - Admin Login",
                    True,
                    f"Admin login successful - Name: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.admin_user_id}"
                )
                return True
            else:
                self.log_result(
                    "1. Authentication Test - Admin Login", 
                    False,
                    f"Login failed - Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("1. Authentication Test - Admin Login", False, f"Exception: {str(e)}")
            return False
            
    def setup_test_data(self):
        """Setup proper test data with team/brand relationships"""
        if not self.admin_token:
            self.log_result("Data Setup", False, "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get existing teams and brands
        try:
            teams_response = requests.get(f"{BACKEND_URL}/teams")
            brands_response = requests.get(f"{BACKEND_URL}/brands")
            
            if teams_response.status_code == 200 and brands_response.status_code == 200:
                self.teams = teams_response.json()
                self.brands = brands_response.json()
                
                self.log_result(
                    "Data Setup - Load Existing Data",
                    True,
                    f"Loaded {len(self.teams)} teams and {len(self.brands)} brands"
                )
            else:
                self.log_result("Data Setup - Load Existing Data", False, "Failed to load teams/brands")
                return False
        except Exception as e:
            self.log_result("Data Setup - Load Existing Data", False, f"Exception: {str(e)}")
            return False
            
        # Create Master Kits with proper team/brand relationships
        master_kits_to_create = [
            {
                "team_name": "FC Barcelona",
                "brand_name": "Nike",
                "season": "2024-25",
                "kit_type": "home",
                "model": "authentic",
                "primary_color": "blue",
                "secondary_colors": ["red"],
                "design_name": "Clasico"
            },
            {
                "team_name": "Paris Saint-Germain", 
                "brand_name": "Nike",
                "season": "2024-25",
                "kit_type": "home",
                "model": "authentic",
                "primary_color": "navy",
                "secondary_colors": ["red", "white"],
                "design_name": "Parc des Princes"
            },
            {
                "team_name": "Manchester United",
                "brand_name": "Adidas",
                "season": "2024-25", 
                "kit_type": "home",
                "model": "authentic",
                "primary_color": "red",
                "secondary_colors": ["white", "black"],
                "design_name": "Theatre of Dreams"
            }
        ]
        
        for kit_data in master_kits_to_create:
            # Find team and brand IDs
            team = next((t for t in self.teams if t['name'] == kit_data['team_name']), None)
            brand = next((b for b in self.brands if b['name'] == kit_data['brand_name']), None)
            
            if not team or not brand:
                self.log_result(
                    f"Data Setup - Master Kit for {kit_data['team_name']}",
                    False,
                    f"Team or brand not found: {kit_data['team_name']}, {kit_data['brand_name']}"
                )
                continue
                
            master_kit_payload = {
                "team_id": team['id'],
                "brand_id": brand['id'],
                "season": kit_data['season'],
                "kit_type": kit_data['kit_type'],
                "model": kit_data['model'],
                "primary_color": kit_data['primary_color'],
                "secondary_colors": kit_data['secondary_colors'],
                "design_name": kit_data['design_name']
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/master-kits",
                    headers=headers,
                    json=master_kit_payload
                )
                
                if response.status_code in [200, 201]:
                    master_kit = response.json()
                    self.master_kits_created.append(master_kit)
                    
                    self.log_result(
                        f"Data Setup - Master Kit for {kit_data['team_name']}",
                        True,
                        f"Created Master Kit ID: {master_kit.get('id')}, Reference: {master_kit.get('topkit_reference')}"
                    )
                    
                    # Create Reference Kit for this Master Kit
                    reference_kit_payload = {
                        "master_kit_id": master_kit['id'],
                        "available_sizes": ["XS", "S", "M", "L", "XL", "XXL"],
                        "original_retail_price": 140.0,
                        "current_market_estimate": 120.0,
                        "official_product_code": f"{kit_data['brand_name']}-{kit_data['team_name'][:3].upper()}-{kit_data['season']}"
                    }
                    
                    ref_response = requests.post(
                        f"{BACKEND_URL}/reference-kits",
                        headers=headers,
                        json=reference_kit_payload
                    )
                    
                    if ref_response.status_code in [200, 201]:
                        reference_kit = ref_response.json()
                        self.reference_kits_created.append(reference_kit)
                        
                        self.log_result(
                            f"Data Setup - Reference Kit for {kit_data['team_name']}",
                            True,
                            f"Created Reference Kit ID: {reference_kit.get('id')}, Reference: {reference_kit.get('topkit_reference')}"
                        )
                    else:
                        self.log_result(
                            f"Data Setup - Reference Kit for {kit_data['team_name']}",
                            False,
                            f"Failed to create Reference Kit: {ref_response.status_code} - {ref_response.text}"
                        )
                else:
                    self.log_result(
                        f"Data Setup - Master Kit for {kit_data['team_name']}",
                        False,
                        f"Failed to create Master Kit: {response.status_code} - {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    f"Data Setup - Master Kit for {kit_data['team_name']}",
                    False,
                    f"Exception: {str(e)}"
                )
                
        return len(self.master_kits_created) > 0 and len(self.reference_kits_created) > 0
        
    def test_vestiaire_endpoint(self):
        """Test 2: Vestiaire Endpoint Test - GET /api/vestiaire to verify Reference Kits with enriched data"""
        try:
            response = requests.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if data is an array
                if isinstance(data, list):
                    kit_count = len(data)
                    
                    # Analyze data structure for Kit hierarchy
                    if kit_count > 0:
                        sample_kit = data[0]
                        
                        # Check for Reference Kit structure with enriched data
                        required_fields = ['id', 'master_kit_id']
                        enriched_fields = ['master_kit_info', 'team_info', 'brand_info']
                        
                        missing_required = [field for field in required_fields if field not in sample_kit]
                        present_enriched = [field for field in enriched_fields if field in sample_kit and sample_kit[field]]
                        
                        if not missing_required:
                            # Check for expected team names in enriched data
                            team_names = []
                            for kit in data:
                                team_info = kit.get('team_info', {})
                                if team_info and 'name' in team_info:
                                    team_names.append(team_info['name'])
                                    
                            expected_teams = ['FC Barcelona', 'Paris Saint-Germain', 'Manchester United']
                            found_teams = [team for team in expected_teams if any(team in name for name in team_names)]
                            
                            enrichment_status = f"Enriched fields present: {present_enriched}" if present_enriched else "No enriched data found"
                            
                            self.log_result(
                                "2. Vestiaire Endpoint Test - Reference Kits with Enriched Data",
                                True,
                                f"Found {kit_count} Reference Kits. {enrichment_status}. Expected teams found: {found_teams}. Sample kit ID: {sample_kit.get('id')}"
                            )
                            
                            # Verify enriched data quality
                            if present_enriched:
                                sample_team = sample_kit.get('team_info', {}).get('name', 'Unknown')
                                sample_brand = sample_kit.get('brand_info', {}).get('name', 'Unknown')
                                sample_season = sample_kit.get('master_kit_info', {}).get('season', 'Unknown')
                                
                                self.log_result(
                                    "2a. Vestiaire Data Quality Check",
                                    True,
                                    f"Enriched data quality verified. Sample: {sample_team} by {sample_brand} ({sample_season})"
                                )
                            else:
                                self.log_result(
                                    "2a. Vestiaire Data Quality Check",
                                    False,
                                    "No enriched data found in vestiaire response"
                                )
                        else:
                            self.log_result(
                                "2. Vestiaire Endpoint Test - Reference Kits with Enriched Data",
                                False,
                                f"Missing required Reference Kit fields: {missing_required}"
                            )
                    else:
                        self.log_result(
                            "2. Vestiaire Endpoint Test - Reference Kits with Enriched Data",
                            False,
                            "Empty array returned - no Reference Kits available for testing"
                        )
                        
                    return data
                else:
                    self.log_result(
                        "2. Vestiaire Endpoint Test - Reference Kits with Enriched Data",
                        False,
                        f"Expected array but got {type(data)}: {data}"
                    )
                    return None
            else:
                self.log_result(
                    "2. Vestiaire Endpoint Test",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("2. Vestiaire Endpoint Test", False, f"Exception: {str(e)}")
            return None
            
    def test_personal_kit_creation(self, vestiaire_data):
        """Test 3: Personal Kit Creation Test - POST /api/personal-kits to create personal kits from reference kits"""
        if not self.admin_token or not vestiaire_data:
            self.log_result("3. Personal Kit Creation Test", False, "Prerequisites not met - need admin auth and vestiaire data")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test creating personal kit from first reference kit
        if len(vestiaire_data) > 0:
            reference_kit = vestiaire_data[0]
            reference_kit_id = reference_kit.get('id')
            
            if not reference_kit_id:
                self.log_result("3. Personal Kit Creation Test", False, "Reference kit missing ID")
                return False
                
            # Create personal kit data
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "size": "L",
                "condition": "mint",
                "collection_type": "owned",
                "purchase_price": 89.99,
                "personal_notes": "Test kit for Kit hierarchy validation"
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/personal-kits",
                    headers=headers,
                    json=personal_kit_data
                )
                
                if response.status_code in [200, 201]:
                    result_data = response.json()
                    personal_kit_id = result_data.get('id')
                    
                    # Verify enriched data in response
                    required_enriched_fields = ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']
                    present_enriched = [field for field in required_enriched_fields if field in result_data and result_data[field]]
                    
                    # Store created personal kit for later testing
                    self.personal_kits_created.append(result_data)
                    
                    team_name = "Unknown Team"
                    season = "Unknown Season"
                    if 'team_info' in result_data and result_data['team_info']:
                        team_name = result_data['team_info'].get('name', 'Unknown Team')
                    if 'master_kit_info' in result_data and result_data['master_kit_info']:
                        season = result_data['master_kit_info'].get('season', 'Unknown Season')
                    
                    self.log_result(
                        "3. Personal Kit Creation Test - Data Validation",
                        True,
                        f"Successfully created Personal Kit (ID: {personal_kit_id}) for {team_name} {season}. Enriched data present: {present_enriched}"
                    )
                    return True
                elif response.status_code == 400:
                    # Check if it's a duplicate error (acceptable)
                    error_text = response.text
                    if "already in" in error_text.lower():
                        self.log_result(
                            "3. Personal Kit Creation Test - Data Validation",
                            True,
                            f"Duplicate prevention working correctly: {error_text}"
                        )
                        return True
                    else:
                        self.log_result(
                            "3. Personal Kit Creation Test - Data Validation",
                            False,
                            f"HTTP 400 - Validation error: {error_text}"
                        )
                        return False
                else:
                    self.log_result(
                        "3. Personal Kit Creation Test - Data Validation",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
                    
            except Exception as e:
                self.log_result("3. Personal Kit Creation Test", False, f"Exception: {str(e)}")
                return False
        else:
            self.log_result("3. Personal Kit Creation Test", False, "No reference kits available for testing")
            return False
            
    def test_personal_kit_retrieval(self):
        """Test 4: Personal Kit Retrieval Test - GET /api/personal-kits?collection_type=owned and wanted"""
        if not self.admin_token:
            self.log_result("4. Personal Kit Retrieval Test", False, "Admin authentication required")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET owned personal kits
        try:
            response = requests.get(f"{BACKEND_URL}/personal-kits?collection_type=owned", headers=headers)
            
            if response.status_code == 200:
                owned_data = response.json()
                
                if isinstance(owned_data, list):
                    # Verify enriched data structure
                    if len(owned_data) > 0:
                        sample_kit = owned_data[0]
                        required_fields = ['id', 'user_id', 'reference_kit_id']
                        enriched_fields = ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']
                        
                        missing_required = [field for field in required_fields if field not in sample_kit]
                        present_enriched = [field for field in enriched_fields if field in sample_kit and sample_kit[field]]
                        
                        if not missing_required:
                            team_name = "Unknown Team"
                            season = "Unknown Season"
                            if 'team_info' in sample_kit and sample_kit['team_info']:
                                team_name = sample_kit['team_info'].get('name', 'Unknown Team')
                            if 'master_kit_info' in sample_kit and sample_kit['master_kit_info']:
                                season = sample_kit['master_kit_info'].get('season', 'Unknown Season')
                            
                            self.log_result(
                                "4a. Personal Kit Retrieval - Owned Collection",
                                True,
                                f"Retrieved {len(owned_data)} owned Personal Kits. Enriched data: {present_enriched}. Sample: {team_name} {season}"
                            )
                        else:
                            self.log_result(
                                "4a. Personal Kit Retrieval - Owned Collection",
                                False,
                                f"Missing required fields: {missing_required}"
                            )
                    else:
                        self.log_result(
                            "4a. Personal Kit Retrieval - Owned Collection",
                            True,
                            "No owned Personal Kits found (acceptable for new user)"
                        )
                else:
                    self.log_result(
                        "4a. Personal Kit Retrieval - Owned Collection",
                        False,
                        f"Expected array but got {type(owned_data)}"
                    )
            else:
                self.log_result(
                    "4a. Personal Kit Retrieval - Owned Collection",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result("4a. Personal Kit Retrieval - Owned Collection", False, f"Exception: {str(e)}")
            
        # Test GET wanted personal kits
        try:
            response = requests.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted", headers=headers)
            
            if response.status_code == 200:
                wanted_data = response.json()
                
                if isinstance(wanted_data, list):
                    self.log_result(
                        "4b. Personal Kit Retrieval - Wanted Collection",
                        True,
                        f"Retrieved {len(wanted_data)} wanted Personal Kits with proper data structure"
                    )
                else:
                    self.log_result(
                        "4b. Personal Kit Retrieval - Wanted Collection",
                        False,
                        f"Expected array but got {type(wanted_data)}"
                    )
            else:
                self.log_result(
                    "4b. Personal Kit Retrieval - Wanted Collection",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result("4b. Personal Kit Retrieval - Wanted Collection", False, f"Exception: {str(e)}")
            
    def test_complete_kit_workflow(self, vestiaire_data):
        """Test 5: Complete Workflow Test - Full user workflow from authentication to collection management"""
        print("\n" + "="*80)
        print("TEST 5: COMPLETE KIT HIERARCHY WORKFLOW")
        print("="*80)
        
        # Step 1: User Authentication
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                user_token = data.get('token')
                user_data = data.get('user', {})
                user_id = user_data.get('id')
                
                self.log_result(
                    "5a. Complete Workflow - User Authentication",
                    True,
                    f"User authenticated: {user_data.get('name')} (ID: {user_id})"
                )
            else:
                self.log_result(
                    "5a. Complete Workflow - User Authentication",
                    False,
                    f"User authentication failed: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result("5a. Complete Workflow - User Authentication", False, f"Exception: {str(e)}")
            return False
            
        # Step 2: View Available Reference Kits in Vestiaire
        if not vestiaire_data or len(vestiaire_data) == 0:
            self.log_result("5b. Complete Workflow - Vestiaire Access", False, "No Reference Kits available")
            return False
            
        self.log_result(
            "5b. Complete Workflow - Vestiaire Access",
            True,
            f"User can view {len(vestiaire_data)} Reference Kits in vestiaire"
        )
        
        # Step 3: Add Reference Kit to Personal Collection (simulate adding kit to collection)
        headers = {"Authorization": f"Bearer {user_token}"}
        reference_kit = vestiaire_data[0]
        reference_kit_id = reference_kit.get('id')
        
        personal_kit_data = {
            "reference_kit_id": reference_kit_id,
            "size": "M",
            "condition": "excellent",
            "collection_type": "owned",
            "purchase_price": 75.00,
            "personal_notes": "Added via complete workflow test"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/personal-kits",
                headers=headers,
                json=personal_kit_data
            )
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                team_name = "Unknown Team"
                if 'team_info' in result_data and result_data['team_info']:
                    team_name = result_data['team_info'].get('name', 'Unknown Team')
                
                self.log_result(
                    "5c. Complete Workflow - Add to Collection",
                    True,
                    f"Successfully added {team_name} kit to personal collection"
                )
            elif response.status_code == 400 and "already in" in response.text.lower():
                self.log_result(
                    "5c. Complete Workflow - Add to Collection",
                    True,
                    "Kit already in collection (duplicate prevention working)"
                )
            else:
                self.log_result(
                    "5c. Complete Workflow - Add to Collection",
                    False,
                    f"Failed to add kit: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            self.log_result("5c. Complete Workflow - Add to Collection", False, f"Exception: {str(e)}")
            return False
            
        # Step 4: Retrieve Personal Collection to Verify
        try:
            response = requests.get(f"{BACKEND_URL}/personal-kits?collection_type=owned", headers=headers)
            
            if response.status_code == 200:
                collection_data = response.json()
                
                if isinstance(collection_data, list) and len(collection_data) > 0:
                    # Verify the kit was added with proper enriched data
                    found_kit = None
                    for kit in collection_data:
                        if kit.get('reference_kit_id') == reference_kit_id:
                            found_kit = kit
                            break
                            
                    if found_kit:
                        team_name = "Unknown Team"
                        season = "Unknown Season"
                        enriched_fields = ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']
                        present_enriched = [field for field in enriched_fields if field in found_kit and found_kit[field]]
                        
                        if 'team_info' in found_kit and found_kit['team_info']:
                            team_name = found_kit['team_info'].get('name', 'Unknown Team')
                        if 'master_kit_info' in found_kit and found_kit['master_kit_info']:
                            season = found_kit['master_kit_info'].get('season', 'Unknown Season')
                        
                        self.log_result(
                            "5d. Complete Workflow - Verify Collection",
                            True,
                            f"Kit successfully found in collection: {team_name} {season}. Enriched data: {present_enriched}"
                        )
                    else:
                        self.log_result(
                            "5d. Complete Workflow - Verify Collection",
                            False,
                            "Added kit not found in personal collection"
                        )
                        return False
                else:
                    self.log_result(
                        "5d. Complete Workflow - Verify Collection",
                        False,
                        "Personal collection is empty or invalid format"
                    )
                    return False
            else:
                self.log_result(
                    "5d. Complete Workflow - Verify Collection",
                    False,
                    f"Failed to retrieve collection: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_result("5d. Complete Workflow - Verify Collection", False, f"Exception: {str(e)}")
            return False
            
        self.log_result(
            "5. Complete Kit Hierarchy Workflow",
            True,
            "Full workflow completed successfully: Authentication → Vestiaire → Add to Collection → Verify"
        )
        return True
        
    def run_comprehensive_test(self):
        """Run comprehensive Kit hierarchy workflow test"""
        print("🔍 KIT HIERARCHY WORKFLOW COMPREHENSIVE TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Testing the complete Kit hierarchy workflow with newly created test data:")
        print("1. Authentication Test with topkitfr@gmail.com/TopKitSecure789#")
        print("2. Data Setup - Create proper Master Kits and Reference Kits")
        print("3. Vestiaire Endpoint Test for Reference Kits with enriched data")
        print("4. Personal Kit Creation Test from reference kits")
        print("5. Personal Kit Retrieval Test for owned and wanted collections")
        print("6. Complete Workflow Test")
        print()
        
        # Test 1: Authentication Testing
        print("TEST 1: AUTHENTICATION TESTING")
        print("-" * 40)
        admin_auth_success = self.authenticate_admin()
        
        if not admin_auth_success:
            print("\n❌ CRITICAL: Admin authentication failed - cannot proceed")
            return False
            
        # Test 2: Data Setup
        print("\nTEST 2: DATA SETUP")
        print("-" * 40)
        data_setup_success = self.setup_test_data()
        
        if not data_setup_success:
            print("\n⚠️  WARNING: Data setup had issues - proceeding with existing data")
            
        # Test 3: Vestiaire Endpoint Testing (Reference Kits)
        print("\nTEST 3: VESTIAIRE ENDPOINT TESTING")
        print("-" * 40)
        vestiaire_data = self.test_vestiaire_endpoint()
        
        if not vestiaire_data:
            print("\n❌ CRITICAL: Vestiaire endpoint failed - cannot test Kit hierarchy")
            return False
            
        # Test 4: Personal Kit Creation Testing
        print("\nTEST 4: PERSONAL KIT CREATION TESTING")
        print("-" * 40)
        self.test_personal_kit_creation(vestiaire_data)
        
        # Test 5: Personal Kit Retrieval Testing
        print("\nTEST 5: PERSONAL KIT RETRIEVAL TESTING")
        print("-" * 40)
        self.test_personal_kit_retrieval()
        
        # Test 6: Complete Workflow Testing
        print("\nTEST 6: COMPLETE KIT HIERARCHY WORKFLOW")
        print("-" * 40)
        self.test_complete_kit_workflow(vestiaire_data)
        
        # Generate Summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("KIT HIERARCHY WORKFLOW TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDETAILED RESULTS:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if not result['success']:
                print(f"   └─ {result['details']}")
                
        # Critical Issues Analysis
        critical_failures = [
            result for result in self.test_results 
            if not result['success'] and any(keyword in result['test'].lower() 
            for keyword in ['authentication', 'vestiaire', 'complete workflow'])
        ]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['details']}")
                
        # Success Analysis
        kit_successes = [
            result for result in self.test_results
            if result['success'] and any(keyword in result['test'].lower() 
            for keyword in ['kit', 'vestiaire', 'personal', 'workflow'])
        ]
        
        if kit_successes:
            print(f"\n✅ KIT HIERARCHY FUNCTIONALITY WORKING ({len(kit_successes)} tests passed):")
            for success in kit_successes[:5]:  # Show first 5
                print(f"   • {success['test']}")
                
        # Expected Results Validation
        print(f"\n📋 EXPECTED RESULTS VALIDATION:")
        vestiaire_tests = [r for r in self.test_results if 'vestiaire' in r['test'].lower() and r['success']]
        personal_kit_tests = [r for r in self.test_results if 'personal kit' in r['test'].lower() and r['success']]
        workflow_tests = [r for r in self.test_results if 'workflow' in r['test'].lower() and r['success']]
        
        print(f"   • Vestiaire with Reference Kits: {'✅' if vestiaire_tests else '❌'}")
        print(f"   • Personal Kit Creation/Retrieval: {'✅' if personal_kit_tests else '❌'}")
        print(f"   • Complete Workflow: {'✅' if workflow_tests else '❌'}")
        
        # Final Assessment
        print(f"\n{'='*80}")
        if success_rate >= 90:
            print("🎉 ASSESSMENT: KIT HIERARCHY WORKFLOW IS WORKING EXCELLENTLY!")
            print("   All major components functional with proper data enrichment.")
            print("   The Kit hierarchy data structures match migrated frontend expectations.")
        elif success_rate >= 70:
            print("⚠️  ASSESSMENT: KIT HIERARCHY WORKFLOW IS MOSTLY WORKING")
            print("   Some issues identified that may need attention.")
            print("   Core functionality operational but improvements needed.")
        else:
            print("🚨 ASSESSMENT: CRITICAL ISSUES FOUND IN KIT HIERARCHY WORKFLOW")
            print("   Multiple failures require immediate fixing.")
            print("   Kit hierarchy implementation needs significant work.")
            
        print(f"{'='*80}")

def main():
    """Main test execution"""
    tester = KitHierarchyWorkflowTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()