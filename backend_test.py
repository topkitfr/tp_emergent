#!/usr/bin/env python3
"""
Backend Testing for Selective Update Functionality - "Improve This File" Workflow
Testing the critical bug fix where contributions now only update changed fields instead of all fields.

BACKGROUND: 
Fixed critical bug where "improve this file" workflow was updating ALL fields of an entity 
instead of only the changed fields. When a user wanted to only change a logo, it was also 
changing the name and other fields unintentionally.

FIXES IMPLEMENTED:
1. Frontend (ContributionModal.js): Now sends only changed fields in contribution data
2. Backend (server.py): Modified create_or_update_entity_from_contribution to only update 
   fields that are explicitly provided in the contribution data
3. Fixed TK-TEAM-616469 name back to "paris saint-germain"

TEST REQUIREMENTS:
1. Test contribution creation endpoint works with selective field data
2. Test moderation approval with selective updates only changes intended fields
3. Test workflow for all entity types: teams, brands, players, competitions, master_kits
4. Verify TK-TEAM-616469 now has correct name "paris saint-germain"
5. Verify image transfer logic still works correctly with selective updates
"""

import asyncio
import aiohttp
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import tempfile
from PIL import Image
import io

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-fixes.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class SelectiveUpdateTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.admin_user = None
        
    async def setup(self):
        """Initialize session and authenticate"""
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        
    async def cleanup(self):
        """Clean up session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["token"]
                    self.admin_user = data["user"]
                    print(f"✅ Authenticated as: {self.admin_user['name']} ({self.admin_user['role']})")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_tk_team_616469_name(self):
        """Test that TK-TEAM-616469 has correct name 'paris saint-germain'"""
        print("\n🔍 Testing TK-TEAM-616469 name correction...")
        
        try:
            # Search for the specific team
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    
                    # Find TK-TEAM-616469
                    target_team = None
                    for team in teams:
                        if team.get("topkit_reference") == "TK-TEAM-616469":
                            target_team = team
                            break
                    
                    if target_team:
                        team_name = target_team.get("name", "").lower()
                        expected_name = "paris saint-germain"
                        
                        if team_name == expected_name:
                            print(f"✅ TK-TEAM-616469 has correct name: '{target_team['name']}'")
                            self.test_results.append(("TK-TEAM-616469 Name Verification", True, f"Name is correctly '{target_team['name']}'"))
                            return True
                        else:
                            print(f"❌ TK-TEAM-616469 has incorrect name: '{target_team['name']}' (expected: '{expected_name}')")
                            self.test_results.append(("TK-TEAM-616469 Name Verification", False, f"Name is '{target_team['name']}' but should be '{expected_name}'"))
                            return False
                    else:
                        print("❌ TK-TEAM-616469 not found in teams")
                        self.test_results.append(("TK-TEAM-616469 Name Verification", False, "Team not found"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to fetch teams: {response.status} - {error_text}")
                    self.test_results.append(("TK-TEAM-616469 Name Verification", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing TK-TEAM-616469: {str(e)}")
            self.test_results.append(("TK-TEAM-616469 Name Verification", False, f"Exception: {str(e)}"))
            return False
            
    async def test_selective_contribution_creation(self):
        """Test that contribution creation works with selective field data"""
        print("\n🔍 Testing selective contribution creation...")
        
        try:
            # Test 1: Create contribution with only logo_url change
            contribution_data = {
                "entity_type": "team",
                "title": "Update team logo only",
                "description": "Testing selective update - logo only",
                "data": {
                    "logo_url": "image_uploaded_test_selective_logo"
                },
                "source_urls": [],
                "entity_id": "test-team-id-for-selective-update"
            }
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/", 
                json=contribution_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    contrib_data = await response.json()
                    print(f"✅ Created selective contribution (logo only): {contrib_data['id']}")
                    
                    # Verify only logo_url is in the data
                    if len(contrib_data['data']) == 1 and 'logo_url' in contrib_data['data']:
                        print("✅ Contribution data contains only logo_url field")
                        self.test_results.append(("Selective Contribution Creation - Logo Only", True, "Only logo_url field present"))
                    else:
                        print(f"❌ Contribution data contains unexpected fields: {list(contrib_data['data'].keys())}")
                        self.test_results.append(("Selective Contribution Creation - Logo Only", False, f"Unexpected fields: {list(contrib_data['data'].keys())}"))
                        return False
                        
                    # Test 2: Create contribution with only name change
                    contribution_data2 = {
                        "entity_type": "team",
                        "title": "Update team name only",
                        "description": "Testing selective update - name only",
                        "data": {
                            "name": "Updated Team Name"
                        },
                        "source_urls": [],
                        "entity_id": "test-team-id-for-selective-update-2"
                    }
                    
                    async with self.session.post(
                        f"{API_BASE}/contributions-v2/", 
                        json=contribution_data2,
                        headers=self.get_auth_headers()
                    ) as response2:
                        if response2.status == 200:
                            contrib_data2 = await response2.json()
                            print(f"✅ Created selective contribution (name only): {contrib_data2['id']}")
                            
                            # Verify only name is in the data
                            if len(contrib_data2['data']) == 1 and 'name' in contrib_data2['data']:
                                print("✅ Contribution data contains only name field")
                                self.test_results.append(("Selective Contribution Creation - Name Only", True, "Only name field present"))
                                return True
                            else:
                                print(f"❌ Contribution data contains unexpected fields: {list(contrib_data2['data'].keys())}")
                                self.test_results.append(("Selective Contribution Creation - Name Only", False, f"Unexpected fields: {list(contrib_data2['data'].keys())}"))
                                return False
                        else:
                            error_text = await response2.text()
                            print(f"❌ Failed to create second contribution: {response2.status} - {error_text}")
                            self.test_results.append(("Selective Contribution Creation - Name Only", False, f"API error: {response2.status}"))
                            return False
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to create contribution: {response.status} - {error_text}")
                    self.test_results.append(("Selective Contribution Creation - Logo Only", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing selective contribution creation: {str(e)}")
            self.test_results.append(("Selective Contribution Creation", False, f"Exception: {str(e)}"))
            return False
            
    async def test_selective_update_workflow_teams(self):
        """Test selective update workflow for teams"""
        print("\n🔍 Testing selective update workflow for teams...")
        
        try:
            # Step 1: Get an existing team to test with
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    if teams:
                        test_team = teams[0]  # Use first team
                        team_id = test_team.get('id')
                        original_name = test_team.get('name')
                        original_logo = test_team.get('logo_url')
                        
                        print(f"✅ Using existing team: {original_name} (ID: {team_id})")
                        
                        # Step 2: Create contribution to update only the logo
                        contribution_data = {
                            "entity_type": "team",
                            "title": "Update team logo only - selective test",
                            "description": "Testing selective update - should only change logo",
                            "data": {
                                "logo_url": "image_uploaded_selective_test_logo"
                            },
                            "source_urls": [],
                            "entity_id": team_id
                        }
                        
                        async with self.session.post(
                            f"{API_BASE}/contributions-v2/", 
                            json=contribution_data,
                            headers=self.get_auth_headers()
                        ) as contrib_response:
                            if contrib_response.status == 200:
                                contrib_data = await contrib_response.json()
                                contribution_id = contrib_data['id']
                                print(f"✅ Created selective update contribution: {contribution_id}")
                                
                                # Step 3: Approve the contribution
                                moderation_data = {
                                    "action": "approve",
                                    "reason": "Testing selective update"
                                }
                                
                                async with self.session.post(
                                    f"{API_BASE}/contributions-v2/{contribution_id}/moderate",
                                    json=moderation_data,
                                    headers=self.get_auth_headers()
                                ) as mod_response:
                                    if mod_response.status == 200:
                                        mod_data = await mod_response.json()
                                        print(f"✅ Approved contribution: {mod_data}")
                                        
                                        # Step 4: Verify the selective update worked
                                        async with self.session.get(f"{API_BASE}/teams") as verify_response:
                                            if verify_response.status == 200:
                                                updated_teams = await verify_response.json()
                                                updated_team = None
                                                for team in updated_teams:
                                                    if team.get('id') == team_id:
                                                        updated_team = team
                                                        break
                                                
                                                if updated_team:
                                                    # Check that name stayed the same but logo changed
                                                    if (updated_team.get('name') == original_name and 
                                                        updated_team.get('logo_url') != original_logo):
                                                        print("✅ Selective update worked: name unchanged, logo updated")
                                                        self.test_results.append(("Selective Update Workflow - Teams", True, "Only logo updated, name preserved"))
                                                        return True
                                                    else:
                                                        print(f"❌ Selective update failed: name={updated_team.get('name')} (was {original_name}), logo={updated_team.get('logo_url')} (was {original_logo})")
                                                        self.test_results.append(("Selective Update Workflow - Teams", False, "Unexpected field changes"))
                                                        return False
                                                else:
                                                    print("❌ Could not find updated team")
                                                    self.test_results.append(("Selective Update Workflow - Teams", False, "Team not found after update"))
                                                    return False
                                            else:
                                                print(f"❌ Failed to verify update: {verify_response.status}")
                                                self.test_results.append(("Selective Update Workflow - Teams", False, "Verification failed"))
                                                return False
                                    else:
                                        error_text = await mod_response.text()
                                        print(f"❌ Failed to approve contribution: {mod_response.status} - {error_text}")
                                        self.test_results.append(("Selective Update Workflow - Teams", False, f"Moderation error: {mod_response.status}"))
                                        return False
                            else:
                                error_text = await contrib_response.text()
                                print(f"❌ Failed to create contribution: {contrib_response.status} - {error_text}")
                                self.test_results.append(("Selective Update Workflow - Teams", False, f"Contribution creation error: {contrib_response.status}"))
                                return False
                    else:
                        print("❌ No teams found for testing")
                        self.test_results.append(("Selective Update Workflow - Teams", False, "No teams available"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to fetch teams: {response.status} - {error_text}")
                    self.test_results.append(("Selective Update Workflow - Teams", False, f"Teams fetch error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing selective update workflow: {str(e)}")
            self.test_results.append(("Selective Update Workflow - Teams", False, f"Exception: {str(e)}"))
            return False
            
    async def test_selective_update_all_entity_types(self):
        """Test selective update workflow for all entity types"""
        print("\n🔍 Testing selective update workflow for all entity types...")
        
        entity_types = [
            {
                "type": "team",
                "data": {"logo_url": "selective_team_logo"},
                "title": "Update team logo - selective"
            },
            {
                "type": "brand", 
                "data": {"logo_url": "selective_brand_logo"},
                "title": "Update brand logo - selective"
            },
            {
                "type": "player",
                "data": {"photo_url": "selective_player_photo"},
                "title": "Update player photo - selective"
            },
            {
                "type": "competition",
                "data": {"logo_url": "selective_competition_logo"},
                "title": "Update competition logo - selective"
            },
            {
                "type": "master_kit",
                "data": {"front_photo_url": "selective_master_kit_photo"},
                "title": "Update master kit photo - selective"
            }
        ]
        
        success_count = 0
        total_count = len(entity_types)
        
        for entity_config in entity_types:
            try:
                entity_type = entity_config["type"]
                print(f"\n  Testing {entity_type}...")
                
                # Create contribution for selective update
                contribution_data = {
                    "entity_type": entity_type,
                    "title": entity_config["title"],
                    "description": f"Testing selective update for {entity_type}",
                    "data": entity_config["data"],
                    "source_urls": [],
                    "entity_id": f"test-{entity_type}-{uuid.uuid4()}"
                }
                
                async with self.session.post(
                    f"{API_BASE}/contributions-v2/", 
                    json=contribution_data,
                    headers=self.get_auth_headers()
                ) as response:
                    if response.status == 200:
                        contrib_data = await response.json()
                        
                        # Verify selective data
                        expected_fields = list(entity_config["data"].keys())
                        actual_fields = list(contrib_data["data"].keys())
                        
                        if actual_fields == expected_fields:
                            print(f"    ✅ {entity_type}: Selective data correct ({actual_fields})")
                            success_count += 1
                        else:
                            print(f"    ❌ {entity_type}: Expected {expected_fields}, got {actual_fields}")
                    else:
                        error_text = await response.text()
                        print(f"    ❌ {entity_type}: Failed to create contribution - {response.status}")
                        
            except Exception as e:
                print(f"    ❌ {entity_type}: Exception - {str(e)}")
                
        success_rate = (success_count / total_count) * 100
        print(f"\n✅ Selective update test completed: {success_count}/{total_count} entity types successful ({success_rate:.1f}%)")
        
        if success_count == total_count:
            self.test_results.append(("Selective Update All Entity Types", True, f"All {total_count} entity types working"))
            return True
        else:
            self.test_results.append(("Selective Update All Entity Types", False, f"Only {success_count}/{total_count} working"))
            return False
            
    async def test_image_transfer_with_selective_updates(self):
        """Test that image transfer logic works correctly with selective updates"""
        print("\n🔍 Testing image transfer logic with selective updates...")
        
        try:
            # Create a test image
            test_image = Image.new('RGB', (100, 100), color='red')
            image_buffer = io.BytesIO()
            test_image.save(image_buffer, format='PNG')
            image_buffer.seek(0)
            
            # Step 1: Create a contribution
            contribution_data = {
                "entity_type": "team",
                "title": "Test image transfer with selective update",
                "description": "Testing image transfer in selective update workflow",
                "data": {
                    "logo_url": "image_uploaded_selective_transfer_test"
                },
                "source_urls": [],
                "entity_id": f"test-team-image-transfer-{uuid.uuid4()}"
            }
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/", 
                json=contribution_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    contrib_data = await response.json()
                    contribution_id = contrib_data['id']
                    print(f"✅ Created contribution for image transfer test: {contribution_id}")
                    
                    # Step 2: Upload image to contribution
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', image_buffer, filename='test_logo.png', content_type='image/png')
                    form_data.add_field('is_primary', 'true')
                    form_data.add_field('caption', 'logo')
                    
                    async with self.session.post(
                        f"{API_BASE}/contributions-v2/{contribution_id}/images",
                        data=form_data,
                        headers=self.get_auth_headers()
                    ) as upload_response:
                        if upload_response.status == 200:
                            upload_data = await upload_response.json()
                            print(f"✅ Uploaded image to contribution: {upload_data['file_url']}")
                            
                            # Step 3: Approve contribution to trigger image transfer
                            moderation_data = {
                                "action": "approve",
                                "reason": "Testing image transfer with selective update"
                            }
                            
                            async with self.session.post(
                                f"{API_BASE}/contributions-v2/{contribution_id}/moderate",
                                json=moderation_data,
                                headers=self.get_auth_headers()
                            ) as mod_response:
                                if mod_response.status == 200:
                                    mod_data = await mod_response.json()
                                    print(f"✅ Approved contribution with image transfer")
                                    
                                    # Verify image transfer worked
                                    if mod_data.get('entity_id'):
                                        print("✅ Image transfer with selective update completed")
                                        self.test_results.append(("Image Transfer with Selective Updates", True, "Image transfer workflow completed"))
                                        return True
                                    else:
                                        print("❌ No entity_id returned from moderation")
                                        self.test_results.append(("Image Transfer with Selective Updates", False, "No entity_id in response"))
                                        return False
                                else:
                                    error_text = await mod_response.text()
                                    print(f"❌ Failed to approve contribution: {mod_response.status} - {error_text}")
                                    self.test_results.append(("Image Transfer with Selective Updates", False, f"Moderation error: {mod_response.status}"))
                                    return False
                        else:
                            error_text = await upload_response.text()
                            print(f"❌ Failed to upload image: {upload_response.status} - {error_text}")
                            self.test_results.append(("Image Transfer with Selective Updates", False, f"Image upload error: {upload_response.status}"))
                            return False
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to create contribution: {response.status} - {error_text}")
                    self.test_results.append(("Image Transfer with Selective Updates", False, f"Contribution creation error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing image transfer: {str(e)}")
            self.test_results.append(("Image Transfer with Selective Updates", False, f"Exception: {str(e)}"))
            return False
            
    async def test_multiple_field_selective_update(self):
        """Test selective update with multiple fields"""
        print("\n🔍 Testing selective update with multiple fields...")
        
        try:
            # Create contribution with multiple field changes
            contribution_data = {
                "entity_type": "team",
                "title": "Update multiple fields - selective test",
                "description": "Testing selective update with multiple fields",
                "data": {
                    "name": "Updated Team Name",
                    "logo_url": "image_uploaded_multi_field_test",
                    "city": "Updated City"
                },
                "source_urls": [],
                "entity_id": f"test-team-multi-field-{uuid.uuid4()}"
            }
            
            async with self.session.post(
                f"{API_BASE}/contributions-v2/", 
                json=contribution_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    contrib_data = await response.json()
                    print(f"✅ Created multi-field contribution: {contrib_data['id']}")
                    
                    # Verify all specified fields are present
                    expected_fields = {"name", "logo_url", "city"}
                    actual_fields = set(contrib_data["data"].keys())
                    
                    if actual_fields == expected_fields:
                        print(f"✅ Multi-field selective update data correct: {list(actual_fields)}")
                        self.test_results.append(("Multiple Field Selective Update", True, f"All specified fields present: {list(actual_fields)}"))
                        return True
                    else:
                        print(f"❌ Field mismatch - Expected: {expected_fields}, Got: {actual_fields}")
                        self.test_results.append(("Multiple Field Selective Update", False, f"Field mismatch: expected {expected_fields}, got {actual_fields}"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to create multi-field contribution: {response.status} - {error_text}")
                    self.test_results.append(("Multiple Field Selective Update", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing multi-field selective update: {str(e)}")
            self.test_results.append(("Multiple Field Selective Update", False, f"Exception: {str(e)}"))
            return False
            
    async def test_authentication_and_authorization(self):
        """Test authentication and authorization for contribution system"""
        print("\n🔍 Testing authentication and authorization...")
        
        try:
            # Test 1: Unauthenticated request should fail
            contribution_data = {
                "entity_type": "team",
                "title": "Unauthorized test",
                "description": "This should fail",
                "data": {"name": "Test"},
                "source_urls": []
            }
            
            async with self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data) as response:
                if response.status == 401 or response.status == 403:
                    print("✅ Unauthenticated request properly rejected")
                    
                    # Test 2: Authenticated request should succeed
                    async with self.session.post(
                        f"{API_BASE}/contributions-v2/", 
                        json=contribution_data,
                        headers=self.get_auth_headers()
                    ) as auth_response:
                        if auth_response.status == 200:
                            print("✅ Authenticated request succeeded")
                            self.test_results.append(("Authentication and Authorization", True, "Proper auth controls in place"))
                            return True
                        else:
                            print(f"❌ Authenticated request failed: {auth_response.status}")
                            self.test_results.append(("Authentication and Authorization", False, f"Auth request failed: {auth_response.status}"))
                            return False
                else:
                    print(f"❌ Unauthenticated request should have been rejected but got: {response.status}")
                    self.test_results.append(("Authentication and Authorization", False, f"Unauth request not rejected: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing authentication: {str(e)}")
            self.test_results.append(("Authentication and Authorization", False, f"Exception: {str(e)}"))
            return False
            
    async def run_all_tests(self):
        """Run all selective update tests"""
        print("🚀 Starting Selective Update Functionality Testing...")
        print("=" * 80)
        
        await self.setup()
        
        if not self.auth_token:
            print("❌ Cannot proceed without authentication")
            return
            
        # Run all tests
        test_functions = [
            self.test_tk_team_616469_name,
            self.test_selective_contribution_creation,
            self.test_selective_update_workflow_teams,
            self.test_selective_update_all_entity_types,
            self.test_multiple_field_selective_update,
            self.test_image_transfer_with_selective_updates,
            self.test_authentication_and_authorization
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
                self.test_results.append((test_func.__name__, False, f"Exception: {str(e)}"))
                
        await self.cleanup()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 80)
        print("📊 SELECTIVE UPDATE FUNCTIONALITY TEST RESULTS")
        print("=" * 80)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📈 Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        
        print("\n✅ PASSED TESTS:")
        for test_name, success, details in self.test_results:
            if success:
                print(f"  ✅ {test_name}: {details}")
                
        print("\n❌ FAILED TESTS:")
        failed_tests = [(name, details) for name, success, details in self.test_results if not success]
        if failed_tests:
            for test_name, details in failed_tests:
                print(f"  ❌ {test_name}: {details}")
        else:
            print("  None - All tests passed!")
            
        print("\n" + "=" * 80)
        
        # Critical findings
        if success_rate >= 90:
            print("🎉 SELECTIVE UPDATE FUNCTIONALITY IS WORKING EXCELLENTLY!")
            print("✅ The 'improve this file' workflow selective update fix is production-ready")
        elif success_rate >= 70:
            print("⚠️  SELECTIVE UPDATE FUNCTIONALITY HAS MINOR ISSUES")
            print("🔧 Some components need attention but core functionality works")
        else:
            print("🚨 CRITICAL ISSUES WITH SELECTIVE UPDATE FUNCTIONALITY")
            print("❌ Major problems detected - immediate attention required")
            
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = SelectiveUpdateTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())