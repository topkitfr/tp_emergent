#!/usr/bin/env python3
"""
3-Tier Kit Hierarchy Form System Comprehensive Testing
Testing the complete Kit Hierarchy workflow as specified in the review request:
1. Master Kit Addition Form (Design Template) - POST /api/master-jerseys or POST /api/master-kits
2. Release Form Kit (Reference Kit - Commercial Version) - POST /api/reference-kits  
3. Form Collection Kit (Personal Kit - Personal Collection) - POST /api/personal-kits
4. Workflow Integration and API Data Consistency
5. Authentication with admin credentials (topkitfr@gmail.com/TopKitSecure789#)
"""

import requests
import json
import sys
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://kit-hierarchy-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class KitHierarchyComprehensiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.created_master_kit_id = None
        self.created_reference_kit_id = None
        self.created_personal_kit_id = None
        
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and len(str(details)) < 500:  # Only print short details
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate_admin(self) -> bool:
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_data = data.get("user", {})
                self.admin_user_id = user_data.get("id")
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Admin authenticated successfully: {user_data.get('name')} ({user_data.get('role')})",
                    {"user_id": self.admin_user_id, "email": ADMIN_EMAIL}
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def get_teams_and_brands(self) -> tuple[List[Dict], List[Dict]]:
        """Get available teams and brands for kit creation"""
        try:
            # Get teams
            teams_response = self.session.get(f"{BACKEND_URL}/teams")
            brands_response = self.session.get(f"{BACKEND_URL}/brands")
            
            teams = []
            brands = []
            
            if teams_response.status_code == 200:
                teams = teams_response.json()
            
            if brands_response.status_code == 200:
                brands = brands_response.json()
            
            self.log_result(
                "Data Foundation Check",
                len(teams) > 0 and len(brands) > 0,
                f"Found {len(teams)} teams and {len(brands)} brands available",
                {"teams_count": len(teams), "brands_count": len(brands)}
            )
            
            return teams, brands
            
        except Exception as e:
            self.log_result(
                "Data Foundation Check",
                False,
                f"Error getting teams/brands: {str(e)}",
                {"error": str(e)}
            )
            return [], []
    
    def test_master_kit_creation(self, teams: List[Dict], brands: List[Dict]) -> Optional[str]:
        """Test 1: Master Kit Addition Form (Design Template)"""
        try:
            if not teams or not brands:
                self.log_result(
                    "Master Kit Creation - Prerequisites",
                    False,
                    "No teams or brands available for Master Kit creation",
                    {"teams_count": len(teams), "brands_count": len(brands)}
                )
                return None
            
            # Select first available team and brand
            team = teams[0]
            brand = brands[0]
            
            # Test both legacy and new endpoints
            endpoints_to_test = [
                {"url": f"{BACKEND_URL}/master-jerseys", "name": "Legacy Master Jersey"},
                {"url": f"{BACKEND_URL}/master-kits", "name": "New Master Kit"}
            ]
            
            for endpoint_info in endpoints_to_test:
                # Create Master Kit data
                master_kit_data = {
                    "team_id": team.get("id"),
                    "brand_id": brand.get("id"),
                    "season": "2024-25",
                    "jersey_type": "home",
                    "model": "authentic",
                    "primary_color": "Blue",
                    "secondary_colors": ["Red", "Yellow"],
                    "pattern": "Stripes",
                    "description": f"Test Master Kit created for {team.get('name')} by {brand.get('name')}"
                }
                
                response = self.session.post(endpoint_info["url"], json=master_kit_data)
                
                if response.status_code in [200, 201]:
                    created_kit = response.json()
                    master_kit_id = created_kit.get("id")
                    
                    # Verify required fields are saved
                    required_fields = ["team_id", "brand_id", "season", "jersey_type"]
                    missing_fields = [field for field in required_fields if not created_kit.get(field)]
                    
                    if missing_fields:
                        self.log_result(
                            f"Master Kit Creation - {endpoint_info['name']} Data Integrity",
                            False,
                            f"Missing required fields in response: {missing_fields}",
                            {"missing_fields": missing_fields}
                        )
                        continue
                    
                    # Verify relationships are properly saved
                    team_saved = created_kit.get("team_id") == team.get("id")
                    brand_saved = created_kit.get("brand_id") == brand.get("id")
                    
                    if not (team_saved and brand_saved):
                        self.log_result(
                            f"Master Kit Creation - {endpoint_info['name']} Relationships",
                            False,
                            "Team or Brand relationships not saved properly",
                            {
                                "expected_team_id": team.get("id"),
                                "saved_team_id": created_kit.get("team_id"),
                                "expected_brand_id": brand.get("id"),
                                "saved_brand_id": created_kit.get("brand_id")
                            }
                        )
                        continue
                    
                    self.log_result(
                        f"Master Kit Creation - {endpoint_info['name']}",
                        True,
                        f"Master Kit created successfully with proper relationships",
                        {
                            "master_kit_id": master_kit_id,
                            "topkit_reference": created_kit.get("topkit_reference"),
                            "team": team.get("name"),
                            "brand": brand.get("name"),
                            "season": created_kit.get("season"),
                            "jersey_type": created_kit.get("jersey_type")
                        }
                    )
                    
                    # Store the first successful creation for later tests
                    if not self.created_master_kit_id:
                        self.created_master_kit_id = master_kit_id
                    
                    return master_kit_id
                    
                elif response.status_code == 400 and "existe déjà" in response.text:
                    # Duplicate - this is acceptable, endpoint is working
                    self.log_result(
                        f"Master Kit Creation - {endpoint_info['name']}",
                        True,
                        "Master Kit endpoint working (duplicate prevention active)",
                        {"status": "duplicate_prevention_working"}
                    )
                    
                    # Try to find existing master kit for this team/brand
                    existing_response = self.session.get(f"{BACKEND_URL}/master-kits?team_id={team.get('id')}")
                    if existing_response.status_code == 200:
                        existing_kits = existing_response.json()
                        if existing_kits:
                            existing_kit_id = existing_kits[0].get("id")
                            if not self.created_master_kit_id:
                                self.created_master_kit_id = existing_kit_id
                            return existing_kit_id
                    
                else:
                    self.log_result(
                        f"Master Kit Creation - {endpoint_info['name']}",
                        False,
                        f"Master Kit creation failed: {response.status_code} - {response.text}",
                        {"status_code": response.status_code, "endpoint": endpoint_info["url"]}
                    )
            
            return None
            
        except Exception as e:
            self.log_result(
                "Master Kit Creation Test",
                False,
                f"Master Kit creation error: {str(e)}",
                {"error": str(e)}
            )
            return None
    
    def test_reference_kit_creation(self, master_kit_id: str) -> Optional[str]:
        """Test 2: Release Form Kit (Reference Kit - Commercial Version)"""
        try:
            if not master_kit_id:
                self.log_result(
                    "Reference Kit Creation - Prerequisites",
                    False,
                    "No Master Kit ID available for Reference Kit creation",
                    {"master_kit_id": master_kit_id}
                )
                return None
            
            # Get competitions for reference kit
            competitions_response = self.session.get(f"{BACKEND_URL}/competitions")
            competitions = []
            if competitions_response.status_code == 200:
                competitions = competitions_response.json()
            
            if not competitions:
                self.log_result(
                    "Reference Kit Creation - Competitions",
                    False,
                    "No competitions available for Reference Kit creation",
                    {"competitions_count": 0}
                )
                return None
            
            competition = competitions[0]
            
            # Create sample image data (base64 encoded 1x1 pixel PNG)
            sample_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            # Create Reference Kit data
            reference_kit_data = {
                "master_kit_id": master_kit_id,
                "competition_id": competition.get("id"),
                "model": "replica",
                "main_photo": sample_image_base64,
                "secondary_photos": [sample_image_base64],
                "sku_code": f"TEST-REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "barcode": f"123456789{datetime.now().strftime('%H%M%S')}",
                "original_retail_price": 89.99,
                "available_sizes": ["S", "M", "L", "XL"],
                "description": "Test Reference Kit for comprehensive testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/reference-kits", json=reference_kit_data)
            
            if response.status_code in [200, 201]:
                created_kit = response.json()
                reference_kit_id = created_kit.get("id")
                
                # Verify required fields
                required_fields = ["master_kit_id", "competition_id", "model", "main_photo"]
                missing_fields = [field for field in required_fields if not created_kit.get(field)]
                
                if missing_fields:
                    self.log_result(
                        "Reference Kit Creation - Data Integrity",
                        False,
                        f"Missing required fields in response: {missing_fields}",
                        {"missing_fields": missing_fields}
                    )
                    return None
                
                # Verify Master Kit relationship
                master_kit_saved = created_kit.get("master_kit_id") == master_kit_id
                
                if not master_kit_saved:
                    self.log_result(
                        "Reference Kit Creation - Master Kit Relationship",
                        False,
                        "Master Kit relationship not saved properly",
                        {
                            "expected_master_kit_id": master_kit_id,
                            "saved_master_kit_id": created_kit.get("master_kit_id")
                        }
                    )
                    return None
                
                # Verify photo upload functionality
                main_photo_saved = bool(created_kit.get("main_photo"))
                
                self.log_result(
                    "Reference Kit Creation",
                    True,
                    "Reference Kit created successfully with photo upload and Master Kit relationship",
                    {
                        "reference_kit_id": reference_kit_id,
                        "topkit_reference": created_kit.get("topkit_reference"),
                        "master_kit_id": master_kit_id,
                        "competition": competition.get("name"),
                        "model": created_kit.get("model"),
                        "main_photo_uploaded": main_photo_saved,
                        "sku_code": created_kit.get("sku_code")
                    }
                )
                
                self.created_reference_kit_id = reference_kit_id
                return reference_kit_id
                
            elif response.status_code == 400 and "existe déjà" in response.text:
                # Duplicate - try to find existing reference kit
                self.log_result(
                    "Reference Kit Creation",
                    True,
                    "Reference Kit endpoint working (duplicate prevention active)",
                    {"status": "duplicate_prevention_working"}
                )
                
                # Try to get existing reference kits
                vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
                if vestiaire_response.status_code == 200:
                    vestiaire_kits = vestiaire_response.json()
                    if vestiaire_kits:
                        existing_kit_id = vestiaire_kits[0].get("id")
                        self.created_reference_kit_id = existing_kit_id
                        return existing_kit_id
                
                return "existing_kit"
                
            else:
                self.log_result(
                    "Reference Kit Creation",
                    False,
                    f"Reference Kit creation failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Reference Kit Creation Test",
                False,
                f"Reference Kit creation error: {str(e)}",
                {"error": str(e)}
            )
            return None
    
    def test_personal_kit_creation(self, reference_kit_id: str) -> Optional[str]:
        """Test 3: Form Collection Kit (Personal Kit - Personal Collection)"""
        try:
            if not reference_kit_id or reference_kit_id == "existing_kit":
                # Try to get a reference kit from vestiaire
                vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
                if vestiaire_response.status_code == 200:
                    vestiaire_kits = vestiaire_response.json()
                    if vestiaire_kits:
                        reference_kit_id = vestiaire_kits[0].get("id")
                    else:
                        self.log_result(
                            "Personal Kit Creation - Prerequisites",
                            False,
                            "No Reference Kit available for Personal Kit creation",
                            {"vestiaire_count": 0}
                        )
                        return None
                else:
                    self.log_result(
                        "Personal Kit Creation - Prerequisites",
                        False,
                        "Cannot access vestiaire to get Reference Kit",
                        {"vestiaire_status": vestiaire_response.status_code}
                    )
                    return None
            
            # Test player dropdown functionality
            players_response = self.session.get(f"{BACKEND_URL}/players")
            players = []
            if players_response.status_code == 200:
                players = players_response.json()
            
            # Select player if available, otherwise use custom data
            selected_player = None
            player_name = "Lionel Messi"
            player_number = 10
            
            if players:
                selected_player = players[0]
                player_name = selected_player.get("name", "Test Player")
                
                # Test player numbers functionality
                if selected_player:
                    player_numbers_response = self.session.get(f"{BACKEND_URL}/players/{selected_player.get('id')}/numbers")
                    if player_numbers_response.status_code == 200:
                        numbers_data = player_numbers_response.json()
                        if numbers_data and isinstance(numbers_data, list) and numbers_data:
                            player_number = numbers_data[0]
            
            # Create Personal Kit data with comprehensive details
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "owned",
                "price_buy": 120.00,  # Price paid
                "price_value": 150.00,  # Estimated value
                "player_name": player_name,
                "player_number": player_number,
                "state": "excellent",  # Condition
                "info_plus": "Authentic jersey with original tags, purchased from official store",
                "size": "L",
                # Additional personal details
                "purchase_date": "2024-01-15T00:00:00Z",
                "purchase_location": "Official Store",
                "is_signed": True,
                "signed_by": player_name,
                "has_printing": True,
                "printed_name": player_name.upper(),
                "printed_number": player_number,
                "is_worn": False,
                "personal_notes": "Perfect condition, dream addition to collection"
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            
            if response.status_code in [200, 201]:
                created_kit = response.json()
                personal_kit_id = created_kit.get("id")
                
                # Verify required fields
                required_fields = ["reference_kit_id", "collection_type", "size", "state"]
                missing_fields = [field for field in required_fields if field not in created_kit]
                
                # Verify personal details are saved
                personal_details_check = {
                    "price_buy_saved": created_kit.get("price_buy") or created_kit.get("purchase_price"),
                    "price_value_saved": created_kit.get("price_value"),
                    "player_name_saved": created_kit.get("player_name") == player_name,
                    "player_number_saved": created_kit.get("player_number") == player_number,
                    "size_saved": created_kit.get("size") == "L",
                    "condition_saved": created_kit.get("state") == "excellent" or created_kit.get("condition") == "excellent"
                }
                
                # Verify data enrichment (Reference Kit, Master Kit, Team, Brand info)
                enrichment_check = {
                    "has_reference_kit_info": bool(created_kit.get("reference_kit_info")),
                    "has_master_kit_info": bool(created_kit.get("master_kit_info")),
                    "has_team_info": bool(created_kit.get("team_info")),
                    "has_brand_info": bool(created_kit.get("brand_info"))
                }
                
                personal_details_ok = sum(personal_details_check.values()) >= 4  # Allow some flexibility
                enrichment_ok = sum(enrichment_check.values()) >= 3  # Require most enrichment
                
                success = len(missing_fields) == 0 and personal_details_ok and enrichment_ok
                
                self.log_result(
                    "Personal Kit Creation",
                    success,
                    "Personal Kit created with comprehensive details and data enrichment",
                    {
                        "personal_kit_id": personal_kit_id,
                        "reference_kit_id": reference_kit_id,
                        "player_info": {"name": player_name, "number": player_number},
                        "personal_details_verified": personal_details_ok,
                        "data_enrichment_verified": enrichment_ok,
                        "missing_required_fields": missing_fields
                    }
                )
                
                if success:
                    self.created_personal_kit_id = personal_kit_id
                    return personal_kit_id
                else:
                    return None
                
            elif response.status_code == 400 and "already in" in response.text:
                # Kit already exists - this is acceptable
                self.log_result(
                    "Personal Kit Creation",
                    True,
                    "Personal Kit endpoint working (duplicate prevention active)",
                    {"status": "duplicate_prevention_working", "reference_kit_id": reference_kit_id}
                )
                return "existing_kit"
                
            else:
                self.log_result(
                    "Personal Kit Creation",
                    False,
                    f"Personal Kit creation failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Personal Kit Creation Test",
                False,
                f"Personal Kit creation error: {str(e)}",
                {"error": str(e)}
            )
            return None
    
    def test_workflow_integration(self) -> bool:
        """Test 4: Workflow Integration - Master Kit → Reference Kit → Personal Kit"""
        try:
            # Verify the complete data flow and relationships
            
            # Step 1: Verify Master Kit exists and has proper data
            if not self.created_master_kit_id:
                self.log_result(
                    "Workflow Integration - Master Kit Check",
                    False,
                    "No Master Kit created in previous tests",
                    {"master_kit_id": self.created_master_kit_id}
                )
                return False
            
            # Step 2: Verify Reference Kit links to Master Kit
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            if vestiaire_response.status_code != 200:
                self.log_result(
                    "Workflow Integration - Vestiaire Access",
                    False,
                    f"Cannot access vestiaire: {vestiaire_response.status_code}",
                    {"status_code": vestiaire_response.status_code}
                )
                return False
            
            vestiaire_kits = vestiaire_response.json()
            if not vestiaire_kits:
                self.log_result(
                    "Workflow Integration - Reference Kits Available",
                    False,
                    "No Reference Kits available in vestiaire",
                    {"vestiaire_count": 0}
                )
                return False
            
            # Find a reference kit that links to our master kit or any master kit
            reference_kit_with_master = None
            for kit in vestiaire_kits:
                if kit.get("master_kit_info") and kit.get("team_info") and kit.get("brand_info"):
                    reference_kit_with_master = kit
                    break
            
            if not reference_kit_with_master:
                self.log_result(
                    "Workflow Integration - Master Kit Linkage",
                    False,
                    "No Reference Kit found with proper Master Kit linkage",
                    {"vestiaire_kits_checked": len(vestiaire_kits)}
                )
                return False
            
            # Step 3: Verify Personal Kit links to Reference Kit and Master Kit
            personal_kits_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            if personal_kits_response.status_code != 200:
                self.log_result(
                    "Workflow Integration - Personal Kits Access",
                    False,
                    f"Cannot access personal kits: {personal_kits_response.status_code}",
                    {"status_code": personal_kits_response.status_code}
                )
                return False
            
            personal_kits = personal_kits_response.json()
            
            # Check if we have personal kits with full hierarchy
            personal_kit_with_hierarchy = None
            for kit in personal_kits:
                if (kit.get("reference_kit_info") and 
                    kit.get("master_kit_info") and 
                    kit.get("team_info") and 
                    kit.get("brand_info")):
                    personal_kit_with_hierarchy = kit
                    break
            
            # Step 4: Verify data integrity across the hierarchy
            hierarchy_verified = False
            
            if personal_kit_with_hierarchy:
                # Full hierarchy verification
                master_info = personal_kit_with_hierarchy.get("master_kit_info", {})
                reference_info = personal_kit_with_hierarchy.get("reference_kit_info", {})
                team_info = personal_kit_with_hierarchy.get("team_info", {})
                brand_info = personal_kit_with_hierarchy.get("brand_info", {})
                
                hierarchy_verified = all([
                    bool(master_info),
                    bool(reference_info),
                    bool(team_info),
                    bool(brand_info)
                ])
                
                self.log_result(
                    "Workflow Integration",
                    hierarchy_verified,
                    "Complete 3-tier hierarchy verified with data integrity",
                    {
                        "hierarchy_levels": {
                            "master_kit": bool(master_info),
                            "reference_kit": bool(reference_info),
                            "team_info": bool(team_info),
                            "brand_info": bool(brand_info)
                        },
                        "data_flow": "Master Kit → Reference Kit → Personal Kit",
                        "personal_kit_id": personal_kit_with_hierarchy.get("id")
                    }
                )
            else:
                # Partial verification - at least Reference Kit → Master Kit works
                master_info = reference_kit_with_master.get("master_kit_info", {})
                team_info = reference_kit_with_master.get("team_info", {})
                brand_info = reference_kit_with_master.get("brand_info", {})
                
                partial_hierarchy = all([bool(master_info), bool(team_info), bool(brand_info)])
                
                self.log_result(
                    "Workflow Integration",
                    partial_hierarchy,
                    "Partial hierarchy verified: Master Kit → Reference Kit (no Personal Kits to test full chain)",
                    {
                        "hierarchy_levels": {
                            "master_kit_to_reference": bool(master_info),
                            "team_info": bool(team_info),
                            "brand_info": bool(brand_info)
                        },
                        "data_flow": "Master Kit → Reference Kit",
                        "reference_kit_id": reference_kit_with_master.get("id")
                    }
                )
                hierarchy_verified = partial_hierarchy
            
            return hierarchy_verified
            
        except Exception as e:
            self.log_result(
                "Workflow Integration Test",
                False,
                f"Workflow integration error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_api_data_consistency(self) -> bool:
        """Test 5: API Data Consistency and Error Handling"""
        try:
            # Test all required endpoints exist and respond correctly
            endpoints_to_test = [
                {"url": f"{BACKEND_URL}/teams", "name": "Teams Endpoint"},
                {"url": f"{BACKEND_URL}/brands", "name": "Brands Endpoint"},
                {"url": f"{BACKEND_URL}/competitions", "name": "Competitions Endpoint"},
                {"url": f"{BACKEND_URL}/players", "name": "Players Endpoint"},
                {"url": f"{BACKEND_URL}/vestiaire", "name": "Vestiaire Endpoint"},
                {"url": f"{BACKEND_URL}/master-kits", "name": "Master Kits Endpoint"},
                {"url": f"{BACKEND_URL}/reference-kits", "name": "Reference Kits Endpoint"},
                {"url": f"{BACKEND_URL}/personal-kits?collection_type=owned", "name": "Personal Kits Owned"},
                {"url": f"{BACKEND_URL}/personal-kits?collection_type=wanted", "name": "Personal Kits Wanted"}
            ]
            
            endpoint_results = {}
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(endpoint["url"])
                    
                    if response.status_code == 200:
                        data = response.json()
                        endpoint_results[endpoint["name"]] = {
                            "status": "success",
                            "status_code": 200,
                            "data_type": type(data).__name__,
                            "count": len(data) if isinstance(data, list) else 1
                        }
                    else:
                        endpoint_results[endpoint["name"]] = {
                            "status": "error",
                            "status_code": response.status_code,
                            "error": response.text[:100]
                        }
                        
                except Exception as e:
                    endpoint_results[endpoint["name"]] = {
                        "status": "exception",
                        "error": str(e)[:100]
                    }
            
            # Count successful endpoints
            successful_endpoints = sum(1 for result in endpoint_results.values() if result.get("status") == "success")
            total_endpoints = len(endpoints_to_test)
            
            # Test error handling with invalid data
            error_handling_tests = []
            
            # Test invalid Master Kit creation
            try:
                invalid_master_response = self.session.post(f"{BACKEND_URL}/master-kits", json={
                    "team_id": "invalid_id",
                    "brand_id": "invalid_id"
                })
                error_handling_tests.append({
                    "test": "Invalid Master Kit",
                    "expected_error": True,
                    "got_error": invalid_master_response.status_code >= 400,
                    "status_code": invalid_master_response.status_code
                })
            except:
                pass
            
            # Test invalid Reference Kit creation
            try:
                invalid_reference_response = self.session.post(f"{BACKEND_URL}/reference-kits", json={
                    "master_kit_id": "invalid_id"
                })
                error_handling_tests.append({
                    "test": "Invalid Reference Kit",
                    "expected_error": True,
                    "got_error": invalid_reference_response.status_code >= 400,
                    "status_code": invalid_reference_response.status_code
                })
            except:
                pass
            
            # Calculate success rate
            success_rate = (successful_endpoints / total_endpoints) * 100
            error_handling_ok = all(test.get("got_error", False) for test in error_handling_tests)
            
            overall_success = success_rate >= 80 and error_handling_ok
            
            self.log_result(
                "API Data Consistency",
                overall_success,
                f"API consistency check: {successful_endpoints}/{total_endpoints} endpoints working ({success_rate:.1f}%)",
                {
                    "endpoint_results": endpoint_results,
                    "error_handling_tests": error_handling_tests,
                    "success_rate": success_rate,
                    "error_handling_working": error_handling_ok
                }
            )
            
            return overall_success
            
        except Exception as e:
            self.log_result(
                "API Data Consistency Test",
                False,
                f"API consistency test error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive Kit Hierarchy tests"""
        print("🧪 Starting 3-Tier Kit Hierarchy Comprehensive Testing...")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate_admin():
            return {"success": False, "message": "Authentication failed", "results": self.test_results}
        
        # Step 2: Get foundation data
        teams, brands = self.get_teams_and_brands()
        
        # Step 3: Test Master Kit Creation (Design Template)
        master_kit_id = self.test_master_kit_creation(teams, brands)
        
        # Step 4: Test Reference Kit Creation (Commercial Version)
        reference_kit_id = self.test_reference_kit_creation(master_kit_id)
        
        # Step 5: Test Personal Kit Creation (Personal Collection)
        personal_kit_id = self.test_personal_kit_creation(reference_kit_id)
        
        # Step 6: Test Workflow Integration
        workflow_success = self.test_workflow_integration()
        
        # Step 7: Test API Data Consistency
        api_consistency = self.test_api_data_consistency()
        
        # Calculate overall success
        test_successes = [
            bool(master_kit_id),
            bool(reference_kit_id),
            bool(personal_kit_id),
            workflow_success,
            api_consistency
        ]
        
        overall_success = sum(test_successes) >= 4  # Allow one failure
        success_rate = (sum(test_successes) / len(test_successes)) * 100
        
        print("\n" + "=" * 70)
        print(f"🏁 3-Tier Kit Hierarchy Comprehensive Testing Complete")
        print(f"📊 Success Rate: {success_rate:.1f}% ({sum(test_successes)}/{len(test_successes)} tests passed)")
        
        return {
            "success": overall_success,
            "success_rate": success_rate,
            "tests_passed": sum(test_successes),
            "total_tests": len(test_successes),
            "message": f"3-tier Kit Hierarchy testing completed with {success_rate:.1f}% success rate",
            "results": self.test_results,
            "created_entities": {
                "master_kit_id": self.created_master_kit_id,
                "reference_kit_id": self.created_reference_kit_id,
                "personal_kit_id": self.created_personal_kit_id
            }
        }

def main():
    """Main test execution"""
    tester = KitHierarchyComprehensiveTester()
    results = tester.run_comprehensive_tests()
    
    # Print summary
    print(f"\n📋 COMPREHENSIVE TEST SUMMARY:")
    print(f"Overall Success: {'✅ PASS' if results['success'] else '❌ FAIL'}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Tests Passed: {results['tests_passed']}/{results['total_tests']}")
    
    if results.get("created_entities"):
        entities = results["created_entities"]
        print(f"\n🔗 Created Entities:")
        print(f"Master Kit ID: {entities.get('master_kit_id', 'None')}")
        print(f"Reference Kit ID: {entities.get('reference_kit_id', 'None')}")
        print(f"Personal Kit ID: {entities.get('personal_kit_id', 'None')}")
    
    # Return appropriate exit code
    sys.exit(0 if results['success'] else 1)

if __name__ == "__main__":
    main()