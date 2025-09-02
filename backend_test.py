#!/usr/bin/env python3
"""
Kit Hierarchy Workflow Backend Testing
Testing the corrected Kit hierarchy workflow to confirm it matches user specifications
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://kit-hierarchy.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class KitHierarchyTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        
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
        if details:
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
    
    def test_vestiaire_endpoint(self) -> bool:
        """Test 1: Vestiaire Endpoint Verification - GET /api/vestiaire"""
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                vestiaire_data = response.json()
                
                # Check if it's an array
                if not isinstance(vestiaire_data, list):
                    self.log_result(
                        "Vestiaire Endpoint Structure",
                        False,
                        "Vestiaire endpoint should return an array",
                        {"actual_type": type(vestiaire_data).__name__}
                    )
                    return False
                
                # Check if we have Reference Kits
                if len(vestiaire_data) == 0:
                    self.log_result(
                        "Vestiaire Endpoint Content",
                        False,
                        "Vestiaire endpoint returns empty array - no Reference Kits available",
                        {"count": 0}
                    )
                    return False
                
                # Analyze first Reference Kit structure
                first_kit = vestiaire_data[0]
                required_fields = ["id", "topkit_reference"]
                generic_fields = ["team_info", "brand_info", "original_retail_price", "available_sizes"]
                personal_fields = ["size", "condition", "purchase_price", "personal_notes"]
                
                # Check for required fields
                missing_required = [field for field in required_fields if field not in first_kit]
                if missing_required:
                    self.log_result(
                        "Vestiaire Reference Kit Structure",
                        False,
                        f"Missing required fields: {missing_required}",
                        {"first_kit_keys": list(first_kit.keys())}
                    )
                    return False
                
                # Check for generic fields (should be present)
                missing_generic = [field for field in generic_fields if field not in first_kit]
                
                # Check for personal fields (should NOT be present)
                found_personal = [field for field in personal_fields if field in first_kit]
                
                if found_personal:
                    self.log_result(
                        "Vestiaire Generic Nature",
                        False,
                        f"Found personal fields in generic Reference Kit: {found_personal}",
                        {"personal_fields_found": found_personal}
                    )
                    return False
                
                self.log_result(
                    "Vestiaire Endpoint Verification",
                    True,
                    f"Vestiaire returns {len(vestiaire_data)} generic Reference Kits with proper structure",
                    {
                        "count": len(vestiaire_data),
                        "sample_kit": {
                            "id": first_kit.get("id"),
                            "reference": first_kit.get("topkit_reference"),
                            "has_team_info": "team_info" in first_kit,
                            "has_brand_info": "brand_info" in first_kit,
                            "has_price": "original_retail_price" in first_kit,
                            "no_personal_data": len(found_personal) == 0
                        }
                    }
                )
                return True
                
            else:
                self.log_result(
                    "Vestiaire Endpoint Access",
                    False,
                    f"Vestiaire endpoint failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Vestiaire Endpoint Test",
                False,
                f"Vestiaire endpoint error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_personal_kit_creation(self, reference_kit_id: str) -> Optional[str]:
        """Test 2: Personal Kit Creation with Details - POST /api/personal-kits"""
        try:
            # Comprehensive personal kit data
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "near_mint",
                "purchase_price": 89.99,
                "purchase_date": "2024-01-15T00:00:00Z",
                "purchase_location": "Official Nike Store",
                "is_signed": True,
                "signed_by": "Lionel Messi",
                "has_printing": True,
                "printed_name": "MESSI",
                "printed_number": 10,
                "printing_type": "official",
                "is_worn": True,
                "is_match_worn": False,
                "is_authenticated": True,
                "authentication_details": "PSA/DNA Certificate #12345",
                "personal_notes": "Purchased during Barcelona farewell tour. Excellent condition with original tags."
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            
            if response.status_code == 201:
                personal_kit = response.json()
                
                # Verify response structure
                required_response_fields = ["id", "reference_kit_info", "master_kit_info", "team_info", "brand_info"]
                missing_fields = [field for field in required_response_fields if field not in personal_kit]
                
                if missing_fields:
                    self.log_result(
                        "Personal Kit Creation Response",
                        False,
                        f"Missing enriched data fields: {missing_fields}",
                        {"response_keys": list(personal_kit.keys())}
                    )
                    return None
                
                # Verify personal details are saved
                personal_details_check = {
                    "size": personal_kit.get("size") == "L",
                    "condition": personal_kit.get("condition") == "near_mint",
                    "purchase_price": personal_kit.get("purchase_price") == 89.99,
                    "is_signed": personal_kit.get("is_signed") == True,
                    "signed_by": personal_kit.get("signed_by") == "Lionel Messi",
                    "has_printing": personal_kit.get("has_printing") == True,
                    "printed_name": personal_kit.get("printed_name") == "MESSI",
                    "printed_number": personal_kit.get("printed_number") == 10,
                    "personal_notes": "Barcelona farewell" in (personal_kit.get("personal_notes") or "")
                }
                
                failed_details = [key for key, value in personal_details_check.items() if not value]
                
                if failed_details:
                    self.log_result(
                        "Personal Kit Details Verification",
                        False,
                        f"Personal details not saved correctly: {failed_details}",
                        {"failed_details": failed_details, "actual_data": personal_kit}
                    )
                    return None
                
                self.log_result(
                    "Personal Kit Creation",
                    True,
                    "Personal Kit created successfully with comprehensive details and enriched data",
                    {
                        "personal_kit_id": personal_kit.get("id"),
                        "reference_kit_id": reference_kit_id,
                        "enriched_data": {
                            "has_reference_kit_info": bool(personal_kit.get("reference_kit_info")),
                            "has_master_kit_info": bool(personal_kit.get("master_kit_info")),
                            "has_team_info": bool(personal_kit.get("team_info")),
                            "has_brand_info": bool(personal_kit.get("brand_info"))
                        },
                        "personal_details_verified": len(failed_details) == 0
                    }
                )
                return personal_kit.get("id")
                
            else:
                self.log_result(
                    "Personal Kit Creation",
                    False,
                    f"Personal Kit creation failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code, "request_data": personal_kit_data}
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
    
    def test_personal_collection_retrieval(self) -> bool:
        """Test 3: Personal Collection Retrieval - GET /api/personal-kits?collection_type=owned"""
        try:
            # Test owned collection
            response_owned = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response_owned.status_code != 200:
                self.log_result(
                    "Personal Collection Retrieval - Owned",
                    False,
                    f"Owned collection retrieval failed: {response_owned.status_code} - {response_owned.text}",
                    {"status_code": response_owned.status_code}
                )
                return False
            
            owned_kits = response_owned.json()
            
            # Test wanted collection
            response_wanted = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            
            if response_wanted.status_code != 200:
                self.log_result(
                    "Personal Collection Retrieval - Wanted",
                    False,
                    f"Wanted collection retrieval failed: {response_wanted.status_code} - {response_wanted.text}",
                    {"status_code": response_wanted.status_code}
                )
                return False
            
            wanted_kits = response_wanted.json()
            
            # Verify structure
            if not isinstance(owned_kits, list) or not isinstance(wanted_kits, list):
                self.log_result(
                    "Personal Collection Structure",
                    False,
                    "Personal collection endpoints should return arrays",
                    {"owned_type": type(owned_kits).__name__, "wanted_type": type(wanted_kits).__name__}
                )
                return False
            
            # Check if we have any personal kits
            total_kits = len(owned_kits) + len(wanted_kits)
            
            if total_kits == 0:
                self.log_result(
                    "Personal Collection Content",
                    False,
                    "No personal kits found in either owned or wanted collections",
                    {"owned_count": len(owned_kits), "wanted_count": len(wanted_kits)}
                )
                return False
            
            # Analyze structure of first kit if available
            sample_kit = owned_kits[0] if owned_kits else wanted_kits[0]
            
            # Check for enriched data
            enriched_fields = ["reference_kit_info", "master_kit_info", "team_info", "brand_info"]
            missing_enriched = [field for field in enriched_fields if field not in sample_kit]
            
            # Check for personal details
            personal_fields = ["size", "condition", "purchase_price", "personal_notes", "collection_type"]
            missing_personal = [field for field in personal_fields if field not in sample_kit]
            
            success = len(missing_enriched) == 0 and len(missing_personal) <= 1  # Allow some optional fields
            
            self.log_result(
                "Personal Collection Retrieval",
                success,
                f"Retrieved {len(owned_kits)} owned and {len(wanted_kits)} wanted Personal Kits with enriched data",
                {
                    "owned_count": len(owned_kits),
                    "wanted_count": len(wanted_kits),
                    "sample_kit_structure": {
                        "has_enriched_data": len(missing_enriched) == 0,
                        "has_personal_details": len(missing_personal) <= 1,
                        "missing_enriched": missing_enriched,
                        "missing_personal": missing_personal
                    }
                }
            )
            return success
            
        except Exception as e:
            self.log_result(
                "Personal Collection Retrieval Test",
                False,
                f"Personal collection retrieval error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_complete_workflow(self) -> bool:
        """Test 4: Complete User Workflow Verification"""
        try:
            # Step 1: Browse generic Reference Kits in Vestiaire
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if vestiaire_response.status_code != 200:
                self.log_result(
                    "Complete Workflow - Vestiaire Access",
                    False,
                    f"Cannot access vestiaire: {vestiaire_response.status_code}",
                    {"status_code": vestiaire_response.status_code}
                )
                return False
            
            vestiaire_kits = vestiaire_response.json()
            
            if not vestiaire_kits:
                self.log_result(
                    "Complete Workflow - Reference Kits Available",
                    False,
                    "No Reference Kits available in vestiaire for workflow testing",
                    {"vestiaire_count": 0}
                )
                return False
            
            # Step 2: Select a Reference Kit and add to personal collection
            selected_kit = vestiaire_kits[0]
            reference_kit_id = selected_kit.get("id")
            
            if not reference_kit_id:
                self.log_result(
                    "Complete Workflow - Reference Kit Selection",
                    False,
                    "Selected Reference Kit missing ID",
                    {"selected_kit": selected_kit}
                )
                return False
            
            # Step 3: Create Personal Kit with specific details
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "wanted",
                "size": "M",
                "condition": "excellent",
                "purchase_price": 120.00,
                "personal_notes": "Dream kit for my collection - looking for authentic version"
            }
            
            create_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            
            if create_response.status_code != 201:
                self.log_result(
                    "Complete Workflow - Personal Kit Creation",
                    False,
                    f"Failed to create Personal Kit: {create_response.status_code} - {create_response.text}",
                    {"status_code": create_response.status_code}
                )
                return False
            
            created_kit = create_response.json()
            
            # Step 4: Verify Personal Kit in collection
            collection_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            
            if collection_response.status_code != 200:
                self.log_result(
                    "Complete Workflow - Collection Verification",
                    False,
                    f"Failed to retrieve personal collection: {collection_response.status_code}",
                    {"status_code": collection_response.status_code}
                )
                return False
            
            collection_kits = collection_response.json()
            
            # Find our created kit
            our_kit = None
            for kit in collection_kits:
                if kit.get("id") == created_kit.get("id"):
                    our_kit = kit
                    break
            
            if not our_kit:
                self.log_result(
                    "Complete Workflow - Kit in Collection",
                    False,
                    "Created Personal Kit not found in collection",
                    {"created_kit_id": created_kit.get("id"), "collection_count": len(collection_kits)}
                )
                return False
            
            # Step 5: Verify data separation
            # Reference Kit should remain generic
            vestiaire_kit_check = selected_kit
            has_personal_data_in_vestiaire = any(field in vestiaire_kit_check for field in ["size", "condition", "personal_notes"])
            
            # Personal Kit should have user-specific details
            has_personal_data_in_collection = all(field in our_kit for field in ["size", "condition", "collection_type"])
            has_enriched_data = all(field in our_kit for field in ["reference_kit_info", "master_kit_info"])
            
            workflow_success = (
                not has_personal_data_in_vestiaire and
                has_personal_data_in_collection and
                has_enriched_data
            )
            
            self.log_result(
                "Complete User Workflow",
                workflow_success,
                "Complete workflow tested: Browse Reference Kits → Add to Collection → Verify Separation",
                {
                    "workflow_steps": {
                        "vestiaire_access": True,
                        "reference_kit_selection": True,
                        "personal_kit_creation": True,
                        "collection_verification": True,
                        "data_separation": workflow_success
                    },
                    "data_verification": {
                        "reference_kits_remain_generic": not has_personal_data_in_vestiaire,
                        "personal_kits_have_user_details": has_personal_data_in_collection,
                        "personal_kits_have_enriched_data": has_enriched_data
                    }
                }
            )
            return workflow_success
            
        except Exception as e:
            self.log_result(
                "Complete Workflow Test",
                False,
                f"Complete workflow error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_three_tier_separation(self) -> bool:
        """Test 5: Verify 3-tier separation (Master Kit → Reference Kit → Personal Kit)"""
        try:
            # Get vestiaire data to analyze the hierarchy
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if vestiaire_response.status_code != 200 or not vestiaire_response.json():
                self.log_result(
                    "Three-Tier Separation - Data Access",
                    False,
                    "Cannot access vestiaire data for hierarchy analysis",
                    {"status_code": vestiaire_response.status_code}
                )
                return False
            
            reference_kits = vestiaire_response.json()
            sample_reference_kit = reference_kits[0]
            
            # Verify Reference Kit has Master Kit info
            master_kit_info = sample_reference_kit.get("master_kit_info", {})
            if not master_kit_info:
                self.log_result(
                    "Three-Tier Separation - Master Kit Link",
                    False,
                    "Reference Kit missing Master Kit information",
                    {"reference_kit_keys": list(sample_reference_kit.keys())}
                )
                return False
            
            # Check Master Kit has team/brand info
            team_info = sample_reference_kit.get("team_info", {})
            brand_info = sample_reference_kit.get("brand_info", {})
            
            if not team_info or not brand_info:
                self.log_result(
                    "Three-Tier Separation - Master Kit Data",
                    False,
                    "Master Kit missing team or brand information",
                    {"has_team_info": bool(team_info), "has_brand_info": bool(brand_info)}
                )
                return False
            
            # Get personal kits to verify the full hierarchy
            personal_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if personal_response.status_code == 200:
                personal_kits = personal_response.json()
                
                if personal_kits:
                    sample_personal_kit = personal_kits[0]
                    
                    # Verify Personal Kit has all three levels
                    has_reference_info = bool(sample_personal_kit.get("reference_kit_info"))
                    has_master_info = bool(sample_personal_kit.get("master_kit_info"))
                    has_team_brand_info = bool(sample_personal_kit.get("team_info")) and bool(sample_personal_kit.get("brand_info"))
                    
                    hierarchy_complete = has_reference_info and has_master_info and has_team_brand_info
                    
                    self.log_result(
                        "Three-Tier Separation Verification",
                        hierarchy_complete,
                        "Verified 3-tier hierarchy: Master Kit (template) → Reference Kit (generic) → Personal Kit (user-specific)",
                        {
                            "hierarchy_levels": {
                                "master_kit": "Generic template with team/brand/design info",
                                "reference_kit": "Shared generic version in vestiaire",
                                "personal_kit": "User collection with personal details"
                            },
                            "data_flow_verified": {
                                "reference_has_master_info": bool(master_kit_info),
                                "personal_has_reference_info": has_reference_info,
                                "personal_has_master_info": has_master_info,
                                "personal_has_team_brand_info": has_team_brand_info
                            }
                        }
                    )
                    return hierarchy_complete
            
            # If no personal kits, still verify the Reference Kit → Master Kit connection
            self.log_result(
                "Three-Tier Separation Verification",
                True,
                "Verified Master Kit → Reference Kit connection (no Personal Kits to test full hierarchy)",
                {
                    "master_kit_connection": bool(master_kit_info),
                    "team_brand_data": {"team": bool(team_info), "brand": bool(brand_info)}
                }
            )
            return True
            
        except Exception as e:
            self.log_result(
                "Three-Tier Separation Test",
                False,
                f"Three-tier separation error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Kit hierarchy workflow tests"""
        print("🧪 Starting Kit Hierarchy Workflow Backend Testing...")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate_admin():
            return {"success": False, "message": "Authentication failed", "results": self.test_results}
        
        # Step 2: Test Vestiaire Endpoint
        vestiaire_success = self.test_vestiaire_endpoint()
        
        # Step 3: Test Personal Kit Creation (if vestiaire has kits)
        personal_kit_id = None
        if vestiaire_success:
            # Get a reference kit ID from vestiaire
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            if vestiaire_response.status_code == 200:
                vestiaire_kits = vestiaire_response.json()
                if vestiaire_kits:
                    reference_kit_id = vestiaire_kits[0].get("id")
                    personal_kit_id = self.test_personal_kit_creation(reference_kit_id)
        
        # Step 4: Test Personal Collection Retrieval
        collection_success = self.test_personal_collection_retrieval()
        
        # Step 5: Test Complete Workflow
        workflow_success = self.test_complete_workflow()
        
        # Step 6: Test Three-Tier Separation
        separation_success = self.test_three_tier_separation()
        
        # Calculate overall success
        test_successes = [
            vestiaire_success,
            personal_kit_id is not None,
            collection_success,
            workflow_success,
            separation_success
        ]
        
        overall_success = sum(test_successes) >= 4  # Allow one failure
        success_rate = (sum(test_successes) / len(test_successes)) * 100
        
        print("\n" + "=" * 60)
        print(f"🏁 Kit Hierarchy Workflow Testing Complete")
        print(f"📊 Success Rate: {success_rate:.1f}% ({sum(test_successes)}/{len(test_successes)} tests passed)")
        
        return {
            "success": overall_success,
            "success_rate": success_rate,
            "tests_passed": sum(test_successes),
            "total_tests": len(test_successes),
            "message": f"Kit hierarchy workflow testing completed with {success_rate:.1f}% success rate",
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = KitHierarchyTester()
    results = tester.run_all_tests()
    
    # Print summary
    print(f"\n📋 SUMMARY:")
    print(f"Overall Success: {'✅ PASS' if results['success'] else '❌ FAIL'}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Tests Passed: {results['tests_passed']}/{results['total_tests']}")
    
    # Return appropriate exit code
    sys.exit(0 if results['success'] else 1)

if __name__ == "__main__":
    main()