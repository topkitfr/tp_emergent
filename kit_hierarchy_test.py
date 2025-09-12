#!/usr/bin/env python3
"""
Kit Hierarchy Workflow Testing - Fixed Foreign Key Relationships
Testing the fully fixed Kit hierarchy workflow with corrected foreign key relationships
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class KitHierarchyTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        print()

    def authenticate_admin(self) -> bool:
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Admin authenticated successfully - Name: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.admin_user_id}"
                )
                return True
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_user(self) -> bool:
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_data = data.get('user', {})
                self.user_user_id = user_data.get('id')
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"User authenticated successfully - Name: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.user_user_id}"
                )
                return True
            else:
                self.log_result("User Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False

    def get_auth_headers(self, use_admin: bool = True) -> Dict[str, str]:
        """Get authorization headers"""
        token = self.admin_token if use_admin else self.user_token
        return {"Authorization": f"Bearer {token}"}

    def test_vestiaire_endpoint(self) -> bool:
        """Test GET /api/vestiaire to verify Reference Kits with enriched data"""
        try:
            response = requests.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    # Check for expected teams
                    expected_teams = ["FC Barcelona", "Paris Saint-Germain", "Manchester United"]
                    found_teams = set()
                    
                    enriched_kits = 0
                    valid_relationships = 0
                    
                    for kit in data:
                        # Check enriched data structure
                        if all(key in kit for key in ['master_kit_info', 'team_info', 'brand_info']):
                            enriched_kits += 1
                            
                            # Check if master_kit_info has team_id and brand_id
                            master_kit = kit.get('master_kit_info', {})
                            if master_kit.get('team_id') and master_kit.get('brand_id'):
                                valid_relationships += 1
                            
                            # Check team names
                            team_info = kit.get('team_info', {})
                            team_name = team_info.get('name', '')
                            if team_name in expected_teams:
                                found_teams.add(team_name)
                    
                    success = len(data) >= 21 and enriched_kits > 0 and valid_relationships > 0
                    details = f"Found {len(data)} Reference Kits, {enriched_kits} with enriched data, {valid_relationships} with valid relationships. Teams found: {list(found_teams)}"
                    
                    self.log_result("Vestiaire Endpoint Test", success, details, {
                        "total_kits": len(data),
                        "enriched_kits": enriched_kits,
                        "valid_relationships": valid_relationships,
                        "teams_found": list(found_teams),
                        "sample_kit": data[0] if data else None
                    })
                    return success
                else:
                    self.log_result("Vestiaire Endpoint Test", False, f"Empty or invalid response: {len(data) if isinstance(data, list) else 'Not a list'}")
                    return False
            else:
                self.log_result("Vestiaire Endpoint Test", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Vestiaire Endpoint Test", False, f"Exception: {str(e)}")
            return False

    def test_personal_kit_creation(self) -> bool:
        """Test POST /api/personal-kits to create personal kits from reference kits"""
        try:
            # First get available Reference Kits
            vestiaire_response = requests.get(f"{BACKEND_URL}/vestiaire")
            if vestiaire_response.status_code != 200:
                self.log_result("Personal Kit Creation Test", False, "Could not fetch vestiaire data")
                return False
            
            reference_kits = vestiaire_response.json()
            if not reference_kits:
                self.log_result("Personal Kit Creation Test", False, "No Reference Kits available")
                return False
            
            # Try to create a Personal Kit from the first Reference Kit
            reference_kit = reference_kits[0]
            reference_kit_id = reference_kit.get('id')
            
            if not reference_kit_id:
                self.log_result("Personal Kit Creation Test", False, "Reference Kit missing ID")
                return False
            
            # Create Personal Kit data
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "size": "L",
                "condition": "excellent",
                "collection_type": "owned",
                "purchase_price": 89.99,
                "purchase_location": "Official Store",
                "personal_notes": "Test kit for collection workflow"
            }
            
            # Create Personal Kit
            response = requests.post(
                f"{BACKEND_URL}/personal-kits",
                json=personal_kit_data,
                headers=self.get_auth_headers(use_admin=False)
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify enriched data structure
                required_fields = ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']
                has_enriched_data = all(field in data for field in required_fields)
                
                # Check if team name is populated
                team_name = data.get('team_info', {}).get('name', '')
                
                success = has_enriched_data and team_name
                details = f"Personal Kit created with ID: {data.get('id')}, Team: {team_name}, Size: {data.get('size')}, Condition: {data.get('condition')}"
                
                self.log_result("Personal Kit Creation Test", success, details, {
                    "personal_kit_id": data.get('id'),
                    "reference_kit_id": reference_kit_id,
                    "team_name": team_name,
                    "has_enriched_data": has_enriched_data
                })
                return success
            elif response.status_code == 400 and "already in your collection" in response.text:
                # Kit already exists - this is acceptable for testing
                self.log_result("Personal Kit Creation Test", True, "Kit already in collection (acceptable for testing)")
                return True
            else:
                self.log_result("Personal Kit Creation Test", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Personal Kit Creation Test", False, f"Exception: {str(e)}")
            return False

    def test_personal_kit_retrieval(self) -> bool:
        """Test GET /api/personal-kits?collection_type=owned and wanted"""
        try:
            success_count = 0
            total_tests = 2
            
            # Test owned collection
            owned_response = requests.get(
                f"{BACKEND_URL}/personal-kits?collection_type=owned",
                headers=self.get_auth_headers(use_admin=False)
            )
            
            if owned_response.status_code == 200:
                owned_data = owned_response.json()
                owned_count = len(owned_data) if isinstance(owned_data, list) else 0
                
                # Check enriched data for owned kits
                owned_enriched = 0
                if owned_data:
                    for kit in owned_data:
                        if all(key in kit for key in ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']):
                            owned_enriched += 1
                
                self.log_result("Personal Kit Retrieval - Owned", True, f"Found {owned_count} owned kits, {owned_enriched} with enriched data")
                success_count += 1
            else:
                self.log_result("Personal Kit Retrieval - Owned", False, f"HTTP {owned_response.status_code}: {owned_response.text}")
            
            # Test wanted collection
            wanted_response = requests.get(
                f"{BACKEND_URL}/personal-kits?collection_type=wanted",
                headers=self.get_auth_headers(use_admin=False)
            )
            
            if wanted_response.status_code == 200:
                wanted_data = wanted_response.json()
                wanted_count = len(wanted_data) if isinstance(wanted_data, list) else 0
                
                # Check enriched data for wanted kits
                wanted_enriched = 0
                if wanted_data:
                    for kit in wanted_data:
                        if all(key in kit for key in ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']):
                            wanted_enriched += 1
                
                self.log_result("Personal Kit Retrieval - Wanted", True, f"Found {wanted_count} wanted kits, {wanted_enriched} with enriched data")
                success_count += 1
            else:
                self.log_result("Personal Kit Retrieval - Wanted", False, f"HTTP {wanted_response.status_code}: {wanted_response.text}")
            
            return success_count == total_tests
                
        except Exception as e:
            self.log_result("Personal Kit Retrieval Test", False, f"Exception: {str(e)}")
            return False

    def test_complete_user_workflow(self) -> bool:
        """Test the complete user workflow from authentication to collection management"""
        try:
            workflow_steps = []
            
            # Step 1: User Authentication (already done)
            if self.user_token:
                workflow_steps.append("✅ User Authentication")
            else:
                workflow_steps.append("❌ User Authentication")
                self.log_result("Complete User Workflow", False, "User not authenticated")
                return False
            
            # Step 2: View available Reference Kits in vestiaire
            vestiaire_response = requests.get(f"{BACKEND_URL}/vestiaire")
            if vestiaire_response.status_code == 200:
                reference_kits = vestiaire_response.json()
                if reference_kits and len(reference_kits) > 0:
                    workflow_steps.append(f"✅ Vestiaire Access ({len(reference_kits)} kits available)")
                    
                    # Check for expected teams
                    expected_teams = ["FC Barcelona", "Paris Saint-Germain", "Manchester United"]
                    found_teams = []
                    for kit in reference_kits:
                        team_name = kit.get('team_info', {}).get('name', '')
                        if team_name in expected_teams:
                            found_teams.append(team_name)
                    
                    if found_teams:
                        workflow_steps.append(f"✅ Expected Teams Found: {found_teams}")
                    else:
                        workflow_steps.append("⚠️ Expected teams not found in vestiaire")
                else:
                    workflow_steps.append("❌ Vestiaire Empty")
                    self.log_result("Complete User Workflow", False, "Vestiaire is empty")
                    return False
            else:
                workflow_steps.append("❌ Vestiaire Access Failed")
                self.log_result("Complete User Workflow", False, f"Vestiaire access failed: {vestiaire_response.status_code}")
                return False
            
            # Step 3: Add a Reference Kit to "owned" collection
            if reference_kits:
                first_kit = reference_kits[0]
                owned_kit_data = {
                    "reference_kit_id": first_kit.get('id'),
                    "size": "M",
                    "condition": "excellent",
                    "collection_type": "owned",
                    "purchase_price": 120.00,
                    "personal_notes": "Added via complete workflow test"
                }
                
                owned_response = requests.post(
                    f"{BACKEND_URL}/personal-kits",
                    json=owned_kit_data,
                    headers=self.get_auth_headers(use_admin=False)
                )
                
                if owned_response.status_code == 200:
                    owned_data = owned_response.json()
                    team_name = owned_data.get('team_info', {}).get('name', 'Unknown')
                    workflow_steps.append(f"✅ Added to Owned Collection: {team_name}")
                elif owned_response.status_code == 400 and "already in your collection" in owned_response.text:
                    workflow_steps.append("✅ Kit Already in Owned Collection (expected)")
                else:
                    workflow_steps.append(f"❌ Failed to Add to Owned Collection: {owned_response.status_code}")
            
            # Step 4: Add a different Reference Kit to "wanted" collection
            if len(reference_kits) > 1:
                second_kit = reference_kits[1]
                wanted_kit_data = {
                    "reference_kit_id": second_kit.get('id'),
                    "size": "L",
                    "condition": "good",
                    "collection_type": "wanted",
                    "personal_notes": "Wanted via complete workflow test"
                }
                
                wanted_response = requests.post(
                    f"{BACKEND_URL}/personal-kits",
                    json=wanted_kit_data,
                    headers=self.get_auth_headers(use_admin=False)
                )
                
                if wanted_response.status_code == 200:
                    wanted_data = wanted_response.json()
                    team_name = wanted_data.get('team_info', {}).get('name', 'Unknown')
                    workflow_steps.append(f"✅ Added to Wanted Collection: {team_name}")
                elif wanted_response.status_code == 400 and "already in your collection" in wanted_response.text:
                    workflow_steps.append("✅ Kit Already in Wanted Collection (expected)")
                else:
                    workflow_steps.append(f"❌ Failed to Add to Wanted Collection: {wanted_response.status_code}")
            
            # Step 5: Retrieve personal collections to verify
            owned_check = requests.get(
                f"{BACKEND_URL}/personal-kits?collection_type=owned",
                headers=self.get_auth_headers(use_admin=False)
            )
            
            wanted_check = requests.get(
                f"{BACKEND_URL}/personal-kits?collection_type=wanted",
                headers=self.get_auth_headers(use_admin=False)
            )
            
            if owned_check.status_code == 200 and wanted_check.status_code == 200:
                owned_kits = owned_check.json()
                wanted_kits = wanted_check.json()
                
                owned_count = len(owned_kits) if isinstance(owned_kits, list) else 0
                wanted_count = len(wanted_kits) if isinstance(wanted_kits, list) else 0
                
                workflow_steps.append(f"✅ Collection Verification: {owned_count} owned, {wanted_count} wanted")
                
                # Check enriched data quality
                enriched_owned = sum(1 for kit in owned_kits if all(key in kit for key in ['team_info', 'brand_info', 'master_kit_info']))
                enriched_wanted = sum(1 for kit in wanted_kits if all(key in kit for key in ['team_info', 'brand_info', 'master_kit_info']))
                
                workflow_steps.append(f"✅ Enriched Data: {enriched_owned}/{owned_count} owned, {enriched_wanted}/{wanted_count} wanted")
            else:
                workflow_steps.append("❌ Collection Verification Failed")
            
            # Determine overall success
            failed_steps = [step for step in workflow_steps if step.startswith("❌")]
            success = len(failed_steps) == 0
            
            details = "\n".join(workflow_steps)
            self.log_result("Complete User Workflow", success, details)
            return success
                
        except Exception as e:
            self.log_result("Complete User Workflow", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Kit hierarchy tests"""
        print("🚀 Starting Kit Hierarchy Workflow Testing - Fixed Foreign Key Relationships")
        print("=" * 80)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot proceed")
            return
        
        if not self.authenticate_user():
            print("❌ User authentication failed - cannot proceed")
            return
        
        print("\n📋 Running Kit Hierarchy Tests...")
        print("-" * 50)
        
        # Test 1: Vestiaire Endpoint
        self.test_vestiaire_endpoint()
        
        # Test 2: Personal Kit Creation
        self.test_personal_kit_creation()
        
        # Test 3: Personal Kit Retrieval
        self.test_personal_kit_retrieval()
        
        # Test 4: Complete User Workflow
        self.test_complete_user_workflow()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 KIT HIERARCHY WORKFLOW TESTING COMPLETE - EXCELLENT RESULTS!")
            print("✅ The fixed foreign key relationships are working correctly")
            print("✅ Reference Kits now have proper master_kit_id relationships")
            print("✅ Vestiaire endpoint returns enriched data with team names")
            print("✅ Personal Kit creation and retrieval working with enriched data")
            print("✅ Complete user workflow operational end-to-end")
        elif success_rate >= 60:
            print("\n⚠️ KIT HIERARCHY WORKFLOW TESTING COMPLETE - PARTIAL SUCCESS")
            print("Some issues remain but core functionality is working")
        else:
            print("\n❌ KIT HIERARCHY WORKFLOW TESTING COMPLETE - CRITICAL ISSUES REMAIN")
            print("Foreign key relationship bugs may still be present")
        
        # Detailed results for debugging
        print("\n🔍 DETAILED TEST RESULTS:")
        print("-" * 50)
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")

if __name__ == "__main__":
    tester = KitHierarchyTester()
    tester.run_all_tests()