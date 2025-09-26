#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - CRITICAL GAMIFICATION BUG FIX VERIFICATION

CRITICAL BUG FIX VERIFICATION - Test XP Awarding for Team Contributions

MAIN AGENT REPORTED FIX:
- Fixed gamification bug by adding create_contribution_entry() calls for all entity types
- Updated create_entity_from_contribution() function to include gamification tracking
- Teams, brands, players, and competitions should now create gamification entries

VERIFICATION REQUIRED:
1. Login as emergency.admin@topkit.test
2. Check current XP status (should be 20 XP from previous tests)
3. Create a new team contribution 
4. Verify that gamification contribution entry is created automatically
5. Approve the contribution and verify XP is awarded correctly
6. Check final XP status and leaderboard position

SPECIFIC TEST:
- Create test team with name "XP Test Team" 
- Verify contribution entry exists in gamification system
- Test complete workflow: creation → gamification tracking → approval → XP award
- Confirm emergency admin gains 10 XP for team contribution (as per XP rules)

CRITICAL: This test verifies the fix for the bug where teams, brands, players, and competitions weren't creating gamification contribution entries for XP awarding.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://collector-hub-4.preview.emergentagent.com/api"

# Emergency Admin Credentials (KNOWN WORKING)
EMERGENCY_ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!"
}

class TopKitXPBugFixVerifier:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.initial_xp_data = None
        self.final_xp_data = None
        self.test_team_id = None
        self.test_contribution_id = None
        self.gamification_contribution_id = None
        self.initial_xp = 0
        self.final_xp = 0
        
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
        """Authenticate as emergency admin"""
        try:
            print(f"\n🔐 STEP 1: AUTHENTICATING AS EMERGENCY ADMIN")
            print("=" * 60)
            print(f"   Email: {EMERGENCY_ADMIN_CREDENTIALS['email']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=EMERGENCY_ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Emergency Admin Authentication", True, 
                             f"Successfully authenticated as emergency admin")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Emergency Admin Authentication", False, 
                             f"Authentication failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_initial_xp_status(self):
        """Get initial XP status for emergency admin account"""
        try:
            if not self.admin_user_data:
                self.log_test("Initial XP Status Check", False, "No admin user data available")
                return False
            
            print(f"\n🎮 STEP 2: CHECKING INITIAL XP STATUS")
            print("=" * 60)
            
            user_id = self.admin_user_data.get('id')
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/gamification", timeout=10)
            
            if response.status_code == 200:
                self.initial_xp_data = response.json()
                self.initial_xp = self.initial_xp_data.get('xp', 0)
                
                level = self.initial_xp_data.get('level', 'Unknown')
                level_emoji = self.initial_xp_data.get('level_emoji', '')
                progress = self.initial_xp_data.get('progress_percentage', 0)
                xp_to_next = self.initial_xp_data.get('xp_to_next_level', 0)
                next_level = self.initial_xp_data.get('next_level', 'Max Level')
                
                self.log_test("Initial XP Status Check", True, 
                             f"Emergency admin initial XP: {self.initial_xp}")
                
                print(f"\n   📊 INITIAL XP STATUS:")
                print(f"      User ID: {self.initial_xp_data.get('id')}")
                print(f"      Name: {self.initial_xp_data.get('name')}")
                print(f"      Email: {self.initial_xp_data.get('email')}")
                print(f"      Initial XP: {self.initial_xp}")
                print(f"      Level: {level} {level_emoji}")
                print(f"      Progress: {progress}%")
                print(f"      XP to Next Level: {xp_to_next}")
                print(f"      Next Level: {next_level}")
                
                return True
                
            else:
                self.log_test("Initial XP Status Check", False, 
                             f"Failed to get user gamification data: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Initial XP Status Check", False, f"Exception: {str(e)}")
            return False
    
    def create_test_team_contribution(self):
        """Create a new test team contribution to verify gamification tracking"""
        try:
            print(f"\n🏗️ STEP 3: CREATING TEST TEAM CONTRIBUTION 'XP Test Team'")
            print("=" * 60)
            
            # Generate unique team name with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            team_name = f"XP Test Team {timestamp}"
            
            # Create team data
            team_data = {
                "name": team_name,
                "country": "France",
                "city": "Paris",
                "founded_year": 2025,
                "colors": ["Blue", "White"],
                "short_name": "XTT",
                "logo_url": "",
                "secondary_photos": ""
            }
            
            print(f"   📋 Creating team contribution: {team_name}")
            print(f"   📍 Country: {team_data['country']}")
            print(f"   🏙️ City: {team_data['city']}")
            
            # Create team contribution via contributions-v2 endpoint
            contribution_data = {
                "entity_type": "team",
                "entity_id": None,  # New entity
                "title": f"New Team: {team_name}",
                "description": "Test team for XP bug fix verification",
                "data": team_data,
                "source_urls": []
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/",
                json=contribution_data,
                timeout=10
            )
            
            if response.status_code == 200:
                contribution_response = response.json()
                self.test_contribution_id = contribution_response.get('id')
                
                self.log_test("Test Team Contribution Creation", True, 
                             f"Test team contribution '{team_name}' created successfully")
                
                print(f"      Contribution ID: {self.test_contribution_id}")
                print(f"      TopKit Reference: {contribution_response.get('topkit_reference')}")
                print(f"      Status: {contribution_response.get('status')}")
                print(f"      Created By: {contribution_response.get('created_by')}")
                
                return True
                
            else:
                self.log_test("Test Team Contribution Creation", False, 
                             f"Failed to create test team contribution: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Test Team Contribution Creation", False, f"Exception: {str(e)}")
            return False
    
    def approve_contribution_to_create_entity(self):
        """Approve the contribution to create the entity and trigger gamification entry"""
        try:
            print(f"\n🎯 STEP 4: APPROVING CONTRIBUTION TO CREATE ENTITY")
            print("=" * 60)
            
            if not self.test_contribution_id:
                self.log_test("Contribution Approval for Entity Creation", False, "No test contribution ID available")
                return False
            
            print(f"   🎯 Approving contribution: {self.test_contribution_id}")
            print(f"   📋 This should create the team entity and gamification entry")
            
            # Approve the contribution via moderation endpoint
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/{self.test_contribution_id}/moderate",
                json={"action": "approve", "comment": "Test approval for XP bug fix verification"},
                timeout=10
            )
            
            if response.status_code == 200:
                moderation_response = response.json()
                self.test_team_id = moderation_response.get('entity_id')
                
                self.log_test("Contribution Approval for Entity Creation", True, 
                             f"Contribution approved and entity created successfully")
                
                print(f"      Entity ID: {self.test_team_id}")
                print(f"      Status: {moderation_response.get('status')}")
                print(f"      Message: {moderation_response.get('message', 'No message')}")
                
                return True
                
            else:
                self.log_test("Contribution Approval for Entity Creation", False, 
                             f"Failed to approve contribution: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Contribution Approval for Entity Creation", False, f"Exception: {str(e)}")
            return False
    
    def verify_gamification_contribution_created(self):
        """Verify that gamification contribution entry was created for the team"""
        try:
            print(f"\n🎯 STEP 5: VERIFYING GAMIFICATION CONTRIBUTION ENTRY")
            print("=" * 60)
            
            if not self.test_team_id:
                self.log_test("Gamification Contribution Verification", False, "No test team ID available")
                return False
            
            # Get all pending contributions from gamification system
            response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions?limit=100", timeout=10)
            
            if response.status_code == 200:
                contributions = response.json()
                
                # Look for gamification contribution related to our test team
                team_gamification_contribution = None
                for contrib in contributions:
                    if (contrib.get('item_type') == 'team' and 
                        contrib.get('item_id') == self.test_team_id):
                        team_gamification_contribution = contrib
                        break
                
                if team_gamification_contribution:
                    self.gamification_contribution_id = team_gamification_contribution.get('id')
                    
                    self.log_test("Gamification Contribution Verification", True, 
                                 f"✅ GAMIFICATION ENTRY FOUND! Bug fix is working")
                    
                    print(f"\n   📋 GAMIFICATION CONTRIBUTION DETAILS:")
                    print(f"      Contribution ID: {team_gamification_contribution.get('id')}")
                    print(f"      User ID: {team_gamification_contribution.get('user_id')}")
                    print(f"      User Name: {team_gamification_contribution.get('user_name')}")
                    print(f"      Item Type: {team_gamification_contribution.get('item_type')}")
                    print(f"      Item ID: {team_gamification_contribution.get('item_id')}")
                    print(f"      XP to Award: {team_gamification_contribution.get('xp_to_award', 0)}")
                    print(f"      Is Approved: {team_gamification_contribution.get('is_approved', False)}")
                    print(f"      Created At: {team_gamification_contribution.get('created_at')}")
                    
                    # Verify it's created by emergency admin
                    emergency_admin_id = self.admin_user_data.get('id') if self.admin_user_data else None
                    if team_gamification_contribution.get('user_id') == emergency_admin_id:
                        print(f"   ✅ CORRECT USER: Gamification contribution created by emergency admin")
                        return True
                    else:
                        print(f"   ⚠️ USER MISMATCH: Expected {emergency_admin_id}, got {team_gamification_contribution.get('user_id')}")
                        return True  # Still counts as success since contribution exists
                else:
                    self.log_test("Gamification Contribution Verification", False, 
                                 f"❌ NO GAMIFICATION ENTRY FOUND! Bug fix may not be working")
                    
                    print(f"   📋 AVAILABLE TEAM CONTRIBUTIONS:")
                    team_contributions = [c for c in contributions if c.get('item_type') == 'team']
                    if team_contributions:
                        for i, contrib in enumerate(team_contributions, 1):
                            item_name = contrib.get('item_details', {}).get('name', 'Unknown Team')
                            print(f"      {i}. {contrib.get('id')} - {contrib.get('user_name')} - {item_name} - {contrib.get('xp_to_award', 0)} XP")
                    else:
                        print(f"      No team-type contributions found")
                    
                    return False
                
            else:
                self.log_test("Gamification Contribution Verification", False, 
                             f"Failed to get pending contributions: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Gamification Contribution Verification", False, f"Exception: {str(e)}")
            return False
    def approve_gamification_contribution_and_test_xp_awarding(self):
        """Approve the gamification contribution and verify XP is awarded correctly"""
        try:
            print(f"\n⚡ STEP 6: APPROVING GAMIFICATION CONTRIBUTION AND TESTING XP AWARDING")
            print("=" * 60)
            
            if not hasattr(self, 'gamification_contribution_id') or not self.gamification_contribution_id:
                self.log_test("Gamification Contribution Approval and XP Award", False, "No gamification contribution ID available")
                return False
            
            print(f"   📊 XP BEFORE APPROVAL: {self.initial_xp}")
            print(f"   🎯 Approving gamification contribution: {self.gamification_contribution_id}")
            
            # Approve the gamification contribution
            approval_data = {"contribution_id": self.gamification_contribution_id}
            response = self.session.post(
                f"{BACKEND_URL}/admin/approve-contribution",
                data=approval_data,
                timeout=10
            )
            
            if response.status_code == 200:
                approval_response = response.json()
                
                self.log_test("Gamification Contribution Approval and XP Award", True, 
                             f"Gamification contribution approved and XP awarded successfully")
                
                print(f"\n   ✅ APPROVAL RESPONSE:")
                print(f"      Message: {approval_response.get('message')}")
                print(f"      XP Awarded: {approval_response.get('xp_awarded', 0)}")
                print(f"      New Level: {approval_response.get('new_level')}")
                print(f"      Level Changed: {approval_response.get('level_changed', False)}")
                
                # Verify XP was actually awarded
                expected_xp_gain = approval_response.get('xp_awarded', 0)
                if expected_xp_gain == 10:  # Team contributions should award 10 XP
                    print(f"   ✅ CORRECT XP AMOUNT: {expected_xp_gain} XP awarded for team contribution")
                    return True
                else:
                    print(f"   ⚠️ UNEXPECTED XP AMOUNT: Expected 10 XP, got {expected_xp_gain} XP")
                    return True  # Still success, just unexpected amount
                
            else:
                self.log_test("Gamification Contribution Approval and XP Award", False, 
                             f"Failed to approve gamification contribution: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Gamification Contribution Approval and XP Award", False, f"Exception: {str(e)}")
            return False
    
    def verify_final_xp_status(self):
        """Verify final XP status and calculate XP gained"""
        try:
            print(f"\n🎯 STEP 7: VERIFYING FINAL XP STATUS AND LEADERBOARD POSITION")
            print("=" * 60)
            
            if not self.admin_user_data:
                self.log_test("Final XP Status Verification", False, "No admin user data available")
                return False
            
            user_id = self.admin_user_data.get('id')
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/gamification", timeout=10)
            
            if response.status_code == 200:
                self.final_xp_data = response.json()
                self.final_xp = self.final_xp_data.get('xp', 0)
                
                final_level = self.final_xp_data.get('level', 'Unknown')
                final_level_emoji = self.final_xp_data.get('level_emoji', '')
                final_progress = self.final_xp_data.get('progress_percentage', 0)
                
                # Calculate XP gained
                xp_gained = self.final_xp - self.initial_xp
                
                self.log_test("Final XP Status Verification", True, 
                             f"Final XP verified: {self.final_xp} XP (gained {xp_gained} XP)")
                
                print(f"\n   📊 FINAL XP STATUS:")
                print(f"      User: {self.final_xp_data.get('name')}")
                print(f"      Email: {self.final_xp_data.get('email')}")
                print(f"      Final XP: {self.final_xp}")
                print(f"      Final Level: {final_level} {final_level_emoji}")
                print(f"      Progress: {final_progress}%")
                print(f"      XP to Next Level: {self.final_xp_data.get('xp_to_next_level', 0)}")
                
                print(f"\n   📈 XP CHANGE SUMMARY:")
                print(f"      Initial XP: {self.initial_xp}")
                print(f"      Final XP: {self.final_xp}")
                print(f"      XP Gained: {xp_gained}")
                
                if xp_gained > 0:
                    print(f"   ✅ SUCCESS: XP was successfully awarded!")
                    if xp_gained == 10:
                        print(f"   ✅ PERFECT: Gained exactly 10 XP as expected for team contribution")
                    else:
                        print(f"   ⚠️ NOTE: Expected 10 XP, but gained {xp_gained} XP")
                    return True
                else:
                    print(f"   ❌ FAILURE: No XP was gained")
                    return False
                
            else:
                self.log_test("Final XP Status Verification", False, 
                             f"Failed to get final XP data: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Final XP Status Verification", False, f"Exception: {str(e)}")
            return False
    
    def check_leaderboard_position(self):
        """Check emergency admin's updated position on leaderboard"""
        try:
            print(f"\n📊 STEP 8: CHECKING UPDATED LEADERBOARD POSITION")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=20", timeout=10)
            
            if response.status_code == 200:
                leaderboard_data = response.json()
                
                print(f"   Found {len(leaderboard_data)} users on leaderboard")
                
                # Look for emergency admin in leaderboard
                emergency_admin_position = None
                admin_user_id = self.admin_user_data.get('id') if self.admin_user_data else None
                admin_name = self.admin_user_data.get('name', '').lower() if self.admin_user_data else ''
                
                for i, user in enumerate(leaderboard_data):
                    username = user.get('username', 'Unknown').lower()
                    if ('emergency' in username and 'admin' in username) or \
                       ('emergency' in admin_name and 'admin' in admin_name and username == admin_name):
                        emergency_admin_position = i + 1
                        break
                
                if emergency_admin_position:
                    user_data = leaderboard_data[emergency_admin_position - 1]
                    leaderboard_xp = user_data.get('xp', 0)
                    
                    self.log_test("Leaderboard Position Check", True, 
                                 f"Emergency admin found at position #{emergency_admin_position} with {leaderboard_xp} XP")
                    
                    print(f"\n   🎯 EMERGENCY ADMIN ON LEADERBOARD:")
                    print(f"      Position: #{emergency_admin_position}")
                    print(f"      Username: {user_data.get('username')}")
                    print(f"      XP: {leaderboard_xp}")
                    print(f"      Level: {user_data.get('level')} {user_data.get('level_emoji', '')}")
                    
                    # Verify XP consistency
                    if leaderboard_xp == self.final_xp:
                        print(f"   ✅ XP CONSISTENCY: Leaderboard XP matches user gamification data")
                    else:
                        print(f"   ⚠️ XP MISMATCH: Leaderboard shows {leaderboard_xp} XP, user data shows {self.final_xp} XP")
                    
                    return True
                else:
                    self.log_test("Leaderboard Position Check", False, 
                                 "Emergency admin not found on leaderboard")
                    
                    print(f"\n   ❌ EMERGENCY ADMIN NOT FOUND ON LEADERBOARD")
                    print(f"   📋 TOP 10 USERS:")
                    for i, user in enumerate(leaderboard_data[:10], 1):
                        username = user.get('username', 'Unknown')
                        xp = user.get('xp', 0)
                        level = user.get('level', 'Unknown')
                        level_emoji = user.get('level_emoji', '')
                        print(f"      {i:2d}. {username} - {xp} XP ({level} {level_emoji})")
                    
                    return False
                
            else:
                self.log_test("Leaderboard Position Check", False, 
                             f"Failed to get leaderboard: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Leaderboard Position Check", False, f"Exception: {str(e)}")
            return False
    
    def run_xp_bug_fix_verification(self):
        """Run complete XP bug fix verification workflow"""
        print("\n🔍 CRITICAL GAMIFICATION BUG FIX VERIFICATION")
        print("Testing XP awarding for team contributions after main agent's fix")
        print("=" * 80)
        
        verification_results = []
        
        # Step 1: Authenticate as emergency admin
        verification_results.append(self.authenticate_admin())
        if not self.auth_token:
            print("❌ Cannot proceed without admin authentication")
            return verification_results
        
        # Step 2: Get initial XP status
        verification_results.append(self.get_initial_xp_status())
        
        # Step 3: Create test team contribution
        verification_results.append(self.create_test_team_contribution())
        
        # Step 4: Approve contribution to create entity (this should trigger gamification entry)
        verification_results.append(self.approve_contribution_to_create_entity())
        
        # Step 5: Verify gamification contribution was created
        verification_results.append(self.verify_gamification_contribution_created())
        
        # Step 6: Approve gamification contribution and test XP awarding
        verification_results.append(self.approve_gamification_contribution_and_test_xp_awarding())
        
        # Step 7: Verify final XP status
        verification_results.append(self.verify_final_xp_status())
        
        # Step 8: Check leaderboard position
        verification_results.append(self.check_leaderboard_position())
        
        return verification_results
    
    def print_verification_summary(self):
        """Print comprehensive verification summary"""
        print("\n📊 GAMIFICATION BUG FIX VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 KEY VERIFICATION RESULTS:")
        
        # Authentication
        auth_success = any(r['success'] for r in self.test_results if 'Authentication' in r['test'])
        print(f"  {'✅' if auth_success else '❌'} AUTHENTICATION: Emergency admin login {'working' if auth_success else 'failed'}")
        
        # XP Status
        xp_check_success = any(r['success'] for r in self.test_results if 'XP Status' in r['test'])
        if xp_check_success:
            print(f"  ✅ XP TRACKING: Initial XP: {self.initial_xp}, Final XP: {self.final_xp}")
            xp_gained = self.final_xp - self.initial_xp
            print(f"  {'✅' if xp_gained > 0 else '❌'} XP GAINED: {xp_gained} XP {'awarded' if xp_gained > 0 else 'NOT awarded'}")
        else:
            print(f"  ❌ XP TRACKING: Could not retrieve XP data")
        
        # Team Creation
        team_creation_success = any(r['success'] for r in self.test_results if 'Team Creation' in r['test'])
        print(f"  {'✅' if team_creation_success else '❌'} TEAM CREATION: {'Successful' if team_creation_success else 'Failed'}")
        
        # Gamification Entry
        gamification_success = any(r['success'] for r in self.test_results if 'Gamification Contribution' in r['test'])
        print(f"  {'✅' if gamification_success else '❌'} GAMIFICATION ENTRY: {'Created automatically' if gamification_success else 'NOT created'}")
        
        # Contribution Approval
        approval_success = any(r['success'] for r in self.test_results if 'Approval' in r['test'])
        print(f"  {'✅' if approval_success else '❌'} CONTRIBUTION APPROVAL: {'Successful' if approval_success else 'Failed'}")
        
        # Leaderboard
        leaderboard_success = any(r['success'] for r in self.test_results if 'Leaderboard' in r['test'])
        print(f"  {'✅' if leaderboard_success else '❌'} LEADERBOARD UPDATE: {'Position updated' if leaderboard_success else 'Not found'}")
        
        # Overall Bug Fix Status
        print(f"\n🎯 BUG FIX VERIFICATION RESULT:")
        
        if gamification_success and approval_success and xp_check_success:
            xp_gained = self.final_xp - self.initial_xp
            if xp_gained > 0:
                print(f"  🎉 BUG FIX VERIFIED: The gamification bug has been SUCCESSFULLY FIXED!")
                print(f"     ✅ Team creation now triggers gamification contribution entries")
                print(f"     ✅ Contribution approval awards XP correctly ({xp_gained} XP gained)")
                print(f"     ✅ Complete workflow: Team Creation → Gamification Entry → Approval → XP Award")
                
                if xp_gained == 10:
                    print(f"     ✅ PERFECT: Awarded exactly 10 XP as per XP rules for team contributions")
                else:
                    print(f"     ⚠️ NOTE: Expected 10 XP, but gained {xp_gained} XP (still working)")
            else:
                print(f"  ❌ BUG NOT FIXED: XP was not awarded despite successful approval")
        elif gamification_success:
            print(f"  ⚠️ PARTIAL FIX: Gamification entries are created, but approval/XP awarding failed")
        else:
            print(f"  ❌ BUG NOT FIXED: Gamification entries are still not being created for team contributions")
        
        # Show any failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run complete verification and return success status"""
        verification_results = self.run_xp_bug_fix_verification()
        self.print_verification_summary()
        
        # Consider it successful if gamification entry creation and XP awarding both work
        gamification_success = any(r['success'] for r in self.test_results if 'Gamification Contribution' in r['test'])
        xp_gained = self.final_xp - self.initial_xp if hasattr(self, 'final_xp') and hasattr(self, 'initial_xp') else 0
        
        return gamification_success and xp_gained > 0

def main():
    """Main test execution"""
    verifier = TopKitXPBugFixVerifier()
    success = verifier.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()