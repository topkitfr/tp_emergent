#!/usr/bin/env python3
"""
Backend Test for Fixed Moderation Workflow - Entity Update vs Creation
Testing the fix where approved contributions now properly update existing entities instead of creating new ones.

ISSUE FIXED: When users submit "improve this file" corrections via ContributionModal, 
the approved contributions were creating new entities instead of updating existing ones.

CHANGES TESTED:
1. ContributionModal now includes entity_id in submissions for existing entity updates
2. ContributionCreate model updated to accept optional entity_id field  
3. New function create_or_update_entity_from_contribution() that:
   - Updates existing entities when entity_id is provided
   - Creates new entities when no entity_id is provided
4. Moderation endpoint updated to use the new function

TEST CASES:
1. Test contribution creation with entity_id (for updates)
2. Test contribution creation without entity_id (for new entities)  
3. Test moderation approval for both cases:
   - Approve contribution with entity_id → should update existing entity
   - Approve contribution without entity_id → should create new entity
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://footkit-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ModerationWorkflowTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data["token"]
                    user_info = data["user"]
                    
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Authenticated as {user_info['name']} (Role: {user_info['role']})"
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result("Admin Authentication", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    async def find_existing_team(self) -> Optional[str]:
        """Find an existing team to test updates on"""
        try:
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    if teams:
                        # Look for TK-TEAM-4111E2 as mentioned in the review request
                        for team in teams:
                            if team.get("topkit_reference") == "TK-TEAM-4111E2":
                                self.log_result(
                                    "Find Target Team TK-TEAM-4111E2", 
                                    True, 
                                    f"Found team: {team.get('name', 'Unknown')} (ID: {team['id']})"
                                )
                                return team["id"]
                        
                        # If TK-TEAM-4111E2 not found, use any existing team
                        first_team = teams[0]
                        self.log_result(
                            "Find Existing Team for Testing", 
                            True, 
                            f"Using team: {first_team.get('name', 'Unknown')} (ID: {first_team['id']})"
                        )
                        return first_team["id"]
                    else:
                        self.log_result("Find Existing Team", False, "No teams found in database")
                        return None
                else:
                    self.log_result("Find Existing Team", False, f"API error: {response.status}")
                    return None
                    
        except Exception as e:
            self.log_result("Find Existing Team", False, f"Exception: {str(e)}")
            return None
    
    async def create_contribution_with_entity_id(self, entity_id: str) -> Optional[str]:
        """Create a contribution for updating an existing entity"""
        try:
            contribution_data = {
                "entity_type": "team",
                "entity_id": entity_id,  # This is the key field for updates
                "title": "Update Team Name - Testing Moderation Fix",
                "description": "Testing the fix where contributions with entity_id should update existing entities instead of creating new ones",
                "data": {
                    "name": "Updated Team Name",
                    "country": "Updated Country",
                    "city": "Updated City"
                },
                "source_urls": []
            }
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/", 
                json=contribution_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    contribution_id = data["id"]
                    
                    self.log_result(
                        "Create Contribution with entity_id (Update)", 
                        True, 
                        f"Created contribution {contribution_id} for entity {entity_id}"
                    )
                    return contribution_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Contribution with entity_id", 
                        False, 
                        f"Status {response.status}: {error_text}"
                    )
                    return None
                    
        except Exception as e:
            self.log_result("Create Contribution with entity_id", False, f"Exception: {str(e)}")
            return None
    
    async def create_contribution_without_entity_id(self) -> Optional[str]:
        """Create a contribution for creating a new entity"""
        try:
            contribution_data = {
                "entity_type": "team",
                # No entity_id field - this should create a new entity
                "title": "New Team Creation - Testing Moderation Fix",
                "description": "Testing the fix where contributions without entity_id should create new entities",
                "data": {
                    "name": "Brand New Test Team",
                    "country": "Test Country",
                    "city": "Test City",
                    "founded_year": 2024
                },
                "source_urls": []
            }
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/", 
                json=contribution_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    contribution_id = data["id"]
                    
                    self.log_result(
                        "Create Contribution without entity_id (New)", 
                        True, 
                        f"Created contribution {contribution_id} for new entity creation"
                    )
                    return contribution_id
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Contribution without entity_id", 
                        False, 
                        f"Status {response.status}: {error_text}"
                    )
                    return None
                    
        except Exception as e:
            self.log_result("Create Contribution without entity_id", False, f"Exception: {str(e)}")
            return None
    
    async def get_entity_before_update(self, entity_id: str) -> Optional[Dict]:
        """Get entity data before update for comparison"""
        try:
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    for team in teams:
                        if team["id"] == entity_id:
                            self.log_result(
                                "Get Entity Before Update", 
                                True, 
                                f"Found entity: {team.get('name', 'Unknown')}"
                            )
                            return team
                    
                    self.log_result("Get Entity Before Update", False, f"Entity {entity_id} not found")
                    return None
                else:
                    self.log_result("Get Entity Before Update", False, f"API error: {response.status}")
                    return None
                    
        except Exception as e:
            self.log_result("Get Entity Before Update", False, f"Exception: {str(e)}")
            return None
    
    async def approve_contribution(self, contribution_id: str) -> bool:
        """Approve a contribution via moderation endpoint"""
        try:
            moderation_data = {
                "action": "approve",
                "reason": "Testing moderation workflow fix"
            }
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/{contribution_id}/moderate",
                json=moderation_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    entity_id = data.get("entity_id")
                    
                    self.log_result(
                        "Approve Contribution", 
                        True, 
                        f"Approved contribution {contribution_id}, entity_id: {entity_id}"
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Approve Contribution", 
                        False, 
                        f"Status {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Approve Contribution", False, f"Exception: {str(e)}")
            return False
    
    async def verify_entity_updated(self, entity_id: str, original_data: Dict) -> bool:
        """Verify that the entity was updated, not duplicated"""
        try:
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    
                    # Find the updated entity
                    updated_entity = None
                    for team in teams:
                        if team["id"] == entity_id:
                            updated_entity = team
                            break
                    
                    if not updated_entity:
                        self.log_result("Verify Entity Updated", False, f"Entity {entity_id} not found after update")
                        return False
                    
                    # Check if the entity was actually updated
                    name_updated = updated_entity.get("name") != original_data.get("name")
                    country_updated = updated_entity.get("country") != original_data.get("country")
                    
                    # Check for duplicates (should not exist)
                    duplicate_count = 0
                    for team in teams:
                        if team.get("name") == "Updated Team Name":
                            duplicate_count += 1
                    
                    if name_updated and duplicate_count == 1:
                        self.log_result(
                            "Verify Entity Updated (No Duplicates)", 
                            True, 
                            f"Entity updated correctly: '{original_data.get('name')}' → '{updated_entity.get('name')}', no duplicates found"
                        )
                        return True
                    elif duplicate_count > 1:
                        self.log_result(
                            "Verify Entity Updated", 
                            False, 
                            f"CRITICAL: Found {duplicate_count} entities with updated name - creating duplicates instead of updating!"
                        )
                        return False
                    else:
                        self.log_result(
                            "Verify Entity Updated", 
                            False, 
                            f"Entity not updated: name='{updated_entity.get('name')}', country='{updated_entity.get('country')}'"
                        )
                        return False
                else:
                    self.log_result("Verify Entity Updated", False, f"API error: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Verify Entity Updated", False, f"Exception: {str(e)}")
            return False
    
    async def verify_new_entity_created(self) -> bool:
        """Verify that a new entity was created (not an update)"""
        try:
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    
                    # Look for the new entity
                    new_entity_found = False
                    for team in teams:
                        if team.get("name") == "Brand New Test Team":
                            new_entity_found = True
                            self.log_result(
                                "Verify New Entity Created", 
                                True, 
                                f"New entity created: {team.get('name')} (ID: {team['id']})"
                            )
                            break
                    
                    if not new_entity_found:
                        self.log_result("Verify New Entity Created", False, "New entity 'Brand New Test Team' not found")
                        return False
                    
                    return True
                else:
                    self.log_result("Verify New Entity Created", False, f"API error: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_result("Verify New Entity Created", False, f"Exception: {str(e)}")
            return False
    
    async def test_moderation_workflow_fix(self):
        """Main test function for the moderation workflow fix"""
        print("🔍 TESTING MODERATION WORKFLOW FIX - Entity Update vs Creation")
        print("=" * 80)
        
        # Step 1: Authenticate as admin
        if not await self.authenticate_admin():
            return
        
        # Step 2: Find existing team for update testing
        existing_team_id = await self.find_existing_team()
        if not existing_team_id:
            print("⚠️  Cannot test entity updates without existing team")
            return
        
        # Step 3: Get original entity data
        original_entity_data = await self.get_entity_before_update(existing_team_id)
        if not original_entity_data:
            return
        
        # Step 4: Test Case 1 - Contribution with entity_id (should update existing)
        print("\n📝 TEST CASE 1: Contribution with entity_id (Update Existing Entity)")
        print("-" * 60)
        
        update_contribution_id = await self.create_contribution_with_entity_id(existing_team_id)
        if update_contribution_id:
            # Approve the contribution
            if await self.approve_contribution(update_contribution_id):
                # Verify the entity was updated, not duplicated
                await self.verify_entity_updated(existing_team_id, original_entity_data)
        
        # Step 5: Test Case 2 - Contribution without entity_id (should create new)
        print("\n📝 TEST CASE 2: Contribution without entity_id (Create New Entity)")
        print("-" * 60)
        
        new_contribution_id = await self.create_contribution_without_entity_id()
        if new_contribution_id:
            # Approve the contribution
            if await self.approve_contribution(new_contribution_id):
                # Verify a new entity was created
                await self.verify_new_entity_created()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 MODERATION WORKFLOW FIX TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: Moderation workflow fix is working correctly!")
        elif success_rate >= 70:
            print(f"\n⚠️  GOOD: Moderation workflow mostly working with minor issues")
        else:
            print(f"\n🚨 CRITICAL: Moderation workflow fix has significant issues")

async def main():
    """Main test execution"""
    async with ModerationWorkflowTester() as tester:
        await tester.test_moderation_workflow_fix()
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())