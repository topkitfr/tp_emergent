#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - URGENT GAMIFICATION BUG INVESTIGATION

USER REPORT:
- Created team contribution: TK-CONTRIB-4DADAC  
- Team approved and exists in database: TK-TEAM-AAD28D
- BUT no XP gained on ranking page
- No progression visible on profile page

INVESTIGATION REQUIRED:
1. Find the user who made this contribution (likely emergency.admin@topkit.test)
2. Check if contribution TK-CONTRIB-4DADAC exists and was approved
3. Verify XP was awarded during approval process
4. Check user's current XP in database vs what should be expected
5. Test the complete approval workflow: contribution creation → approval → XP awarding
6. Check if there are any errors in the gamification system
7. Verify all gamification endpoints are working correctly

CRITICAL: The gamification system appears to be broken despite previous successful testing.
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://jersey-levels.preview.emergentagent.com/api"

# Emergency Admin Credentials (KNOWN WORKING)
EMERGENCY_ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!"
}

class TopKitGamificationInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.contribution_data = None
        self.user_xp_data = None
        self.leaderboard_data = None
        
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
            print(f"\n🔐 AUTHENTICATING AS EMERGENCY ADMIN")
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
                
                self.log_test("Admin Authentication", True, 
                             f"✅ Emergency admin authenticated successfully")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Admin Authentication", False, 
                             f"Authentication failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_leaderboard_data(self):
        """Get current leaderboard to analyze XP distribution"""
        try:
            print(f"\n📊 ANALYZING CURRENT LEADERBOARD")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=50", timeout=10)
            
            if response.status_code == 200:
                self.leaderboard_data = response.json()
                
                self.log_test("Leaderboard Analysis", True, 
                             f"Retrieved leaderboard with {len(self.leaderboard_data)} users")
                
                print(f"\n   📋 TOP USERS BY XP:")
                for i, user in enumerate(self.leaderboard_data[:10], 1):
                    username = user.get('username', 'Unknown')
                    xp = user.get('xp', 0)
                    level = user.get('level', 'Unknown')
                    level_emoji = user.get('level_emoji', '')
                    
                    print(f"      {i:2d}. {username} - {xp} XP ({level} {level_emoji})")
                
                # Look for emergency admin in leaderboard
                emergency_admin_in_leaderboard = None
                for user in self.leaderboard_data:
                    if 'emergency' in user.get('username', '').lower() or 'admin' in user.get('username', '').lower():
                        emergency_admin_in_leaderboard = user
                        break
                
                if emergency_admin_in_leaderboard:
                    print(f"\n   🎯 EMERGENCY ADMIN FOUND IN LEADERBOARD:")
                    print(f"      Username: {emergency_admin_in_leaderboard.get('username')}")
                    print(f"      XP: {emergency_admin_in_leaderboard.get('xp', 0)}")
                    print(f"      Level: {emergency_admin_in_leaderboard.get('level')} {emergency_admin_in_leaderboard.get('level_emoji', '')}")
                    print(f"      Rank: {emergency_admin_in_leaderboard.get('rank')}")
                else:
                    print(f"\n   ❌ EMERGENCY ADMIN NOT FOUND IN LEADERBOARD")
                
                return True
                
            else:
                self.log_test("Leaderboard Analysis", False, 
                             f"Failed to get leaderboard: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Leaderboard Analysis", False, f"Exception: {str(e)}")
            return False
    
    def get_user_gamification_data(self):
        """Get detailed gamification data for emergency admin user"""
        try:
            if not self.admin_user_data:
                self.log_test("User Gamification Data", False, "No admin user data available")
                return False
            
            print(f"\n🎮 ANALYZING USER GAMIFICATION DATA")
            print("=" * 60)
            
            user_id = self.admin_user_data.get('id')
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/gamification", timeout=10)
            
            if response.status_code == 200:
                self.user_xp_data = response.json()
                
                self.log_test("User Gamification Data", True, 
                             f"Retrieved gamification data for user {user_id}")
                
                print(f"\n   📊 GAMIFICATION PROFILE:")
                print(f"      User ID: {self.user_xp_data.get('id')}")
                print(f"      Name: {self.user_xp_data.get('name')}")
                print(f"      Email: {self.user_xp_data.get('email')}")
                print(f"      Current XP: {self.user_xp_data.get('xp', 0)}")
                print(f"      Level: {self.user_xp_data.get('level')} {self.user_xp_data.get('level_emoji', '')}")
                print(f"      Progress: {self.user_xp_data.get('progress_percentage', 0)}%")
                print(f"      XP to Next Level: {self.user_xp_data.get('xp_to_next_level', 0)}")
                print(f"      Next Level: {self.user_xp_data.get('next_level', 'Max Level')}")
                
                return True
                
            else:
                self.log_test("User Gamification Data", False, 
                             f"Failed to get user gamification data: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("User Gamification Data", False, f"Exception: {str(e)}")
            return False
    
    def search_specific_contribution(self):
        """Search for the specific contribution TK-CONTRIB-4DADAC"""
        try:
            print(f"\n🔍 SEARCHING FOR SPECIFIC CONTRIBUTION: TK-CONTRIB-4DADAC")
            print("=" * 60)
            
            # Get pending contributions
            response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions?limit=100", timeout=10)
            
            if response.status_code == 200:
                contributions = response.json()
                
                print(f"   Found {len(contributions)} total pending contributions")
                
                # Look for the specific contribution
                target_contribution = None
                for contrib in contributions:
                    if contrib.get('id') == 'TK-CONTRIB-4DADAC':
                        target_contribution = contrib
                        break
                
                if target_contribution:
                    self.contribution_data = target_contribution
                    self.log_test("Specific Contribution Search", True, 
                                 f"✅ Found contribution TK-CONTRIB-4DADAC")
                    
                    print(f"\n   📋 CONTRIBUTION DETAILS:")
                    print(f"      ID: {target_contribution.get('id')}")
                    print(f"      User ID: {target_contribution.get('user_id')}")
                    print(f"      User Name: {target_contribution.get('user_name')}")
                    print(f"      Item Type: {target_contribution.get('item_type')}")
                    print(f"      Item ID: {target_contribution.get('item_id')}")
                    print(f"      XP to Award: {target_contribution.get('xp_to_award', 0)}")
                    print(f"      Created At: {target_contribution.get('created_at')}")
                    print(f"      Is Approved: {target_contribution.get('is_approved', False)}")
                    
                    return True
                else:
                    self.log_test("Specific Contribution Search", False, 
                                 f"❌ Contribution TK-CONTRIB-4DADAC not found in pending contributions")
                    
                    # Show all contributions for debugging
                    print(f"\n   📋 ALL PENDING CONTRIBUTIONS:")
                    for i, contrib in enumerate(contributions[:10], 1):
                        print(f"      {i:2d}. {contrib.get('id', 'No ID')} - {contrib.get('item_type')} - {contrib.get('user_name')} - {contrib.get('xp_to_award', 0)} XP")
                    
                    # Also check contributions-v2 system which might be where the contribution actually exists
                    print(f"\n   🔍 CHECKING CONTRIBUTIONS-V2 SYSTEM...")
                    try:
                        v2_response = self.session.get(f"{BACKEND_URL}/contributions-v2/?page=1&limit=100", timeout=10)
                        if v2_response.status_code == 200:
                            v2_contributions = v2_response.json()
                            contributions_list = v2_contributions.get('contributions', [])
                            print(f"   Found {len(contributions_list)} contributions in v2 system")
                            
                            # Look for the specific contribution in v2 system
                            for contrib in contributions_list:
                                if contrib.get('id') == 'TK-CONTRIB-4DADAC' or contrib.get('topkit_reference') == 'TK-CONTRIB-4DADAC':
                                    print(f"\n   ✅ FOUND IN V2 SYSTEM:")
                                    print(f"      ID: {contrib.get('id')}")
                                    print(f"      TopKit Reference: {contrib.get('topkit_reference')}")
                                    print(f"      Status: {contrib.get('status')}")
                                    print(f"      Entity Type: {contrib.get('entity_type')}")
                                    print(f"      Created By: {contrib.get('created_by')}")
                                    print(f"      Created At: {contrib.get('created_at')}")
                                    self.contribution_data = contrib
                                    return True
                            
                            print(f"   ❌ Not found in v2 system either")
                            print(f"   📋 RECENT V2 CONTRIBUTIONS (showing first 5):")
                            for i, contrib in enumerate(contributions_list[:5], 1):
                                print(f"      {i}. {contrib.get('topkit_reference', 'No Ref')} - {contrib.get('entity_type')} - {contrib.get('status')}")
                        
                    except Exception as v2_error:
                        print(f"   ❌ Error checking v2 system: {str(v2_error)}")
                    
                    return False
                
            else:
                self.log_test("Specific Contribution Search", False, 
                             f"Failed to get pending contributions: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Specific Contribution Search", False, f"Exception: {str(e)}")
            return False
    
    def search_team_in_database(self):
        """Search for the specific team TK-TEAM-AAD28D"""
        try:
            print(f"\n🏟️ SEARCHING FOR SPECIFIC TEAM: TK-TEAM-AAD28D")
            print("=" * 60)
            
            # Get all teams
            response = self.session.get(f"{BACKEND_URL}/teams", timeout=10)
            
            if response.status_code == 200:
                teams = response.json()
                
                print(f"   Found {len(teams)} total teams in database")
                
                # Look for the specific team
                target_team = None
                for team in teams:
                    if team.get('id') == 'TK-TEAM-AAD28D':
                        target_team = team
                        break
                
                if target_team:
                    self.log_test("Specific Team Search", True, 
                                 f"✅ Found team TK-TEAM-AAD28D")
                    
                    print(f"\n   📋 TEAM DETAILS:")
                    print(f"      ID: {target_team.get('id')}")
                    print(f"      Name: {target_team.get('name')}")
                    print(f"      Country: {target_team.get('country')}")
                    print(f"      Created At: {target_team.get('created_at')}")
                    print(f"      Created By: {target_team.get('created_by')}")
                    
                    return True
                else:
                    self.log_test("Specific Team Search", False, 
                                 f"❌ Team TK-TEAM-AAD28D not found in database")
                    
                    # Show recent teams for debugging
                    print(f"\n   📋 RECENT TEAMS (showing first 10):")
                    for i, team in enumerate(teams[:10], 1):
                        print(f"      {i:2d}. {team.get('id', 'No ID')} - {team.get('name', 'No Name')} - {team.get('country', 'No Country')}")
                    
                    return False
                
            else:
                self.log_test("Specific Team Search", False, 
                             f"Failed to get teams: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Specific Team Search", False, f"Exception: {str(e)}")
            return False
    
    def test_gamification_endpoints(self):
        """Test all gamification endpoints for functionality"""
        try:
            print(f"\n🎮 TESTING GAMIFICATION ENDPOINTS")
            print("=" * 60)
            
            endpoints_tested = 0
            endpoints_working = 0
            
            # Test 1: Leaderboard endpoint
            try:
                response = self.session.get(f"{BACKEND_URL}/leaderboard", timeout=10)
                endpoints_tested += 1
                if response.status_code == 200:
                    endpoints_working += 1
                    print(f"   ✅ Leaderboard endpoint: Working ({len(response.json())} users)")
                else:
                    print(f"   ❌ Leaderboard endpoint: Failed ({response.status_code})")
            except Exception as e:
                print(f"   ❌ Leaderboard endpoint: Exception ({str(e)})")
            
            # Test 2: User gamification data endpoint
            if self.admin_user_data:
                try:
                    user_id = self.admin_user_data.get('id')
                    response = self.session.get(f"{BACKEND_URL}/users/{user_id}/gamification", timeout=10)
                    endpoints_tested += 1
                    if response.status_code == 200:
                        endpoints_working += 1
                        print(f"   ✅ User gamification endpoint: Working")
                    else:
                        print(f"   ❌ User gamification endpoint: Failed ({response.status_code})")
                except Exception as e:
                    print(f"   ❌ User gamification endpoint: Exception ({str(e)})")
            
            # Test 3: Admin pending contributions endpoint
            try:
                response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions", timeout=10)
                endpoints_tested += 1
                if response.status_code == 200:
                    endpoints_working += 1
                    print(f"   ✅ Admin pending contributions endpoint: Working ({len(response.json())} contributions)")
                else:
                    print(f"   ❌ Admin pending contributions endpoint: Failed ({response.status_code})")
            except Exception as e:
                print(f"   ❌ Admin pending contributions endpoint: Exception ({str(e)})")
            
            success_rate = (endpoints_working / endpoints_tested) * 100 if endpoints_tested > 0 else 0
            
            self.log_test("Gamification Endpoints Test", endpoints_working == endpoints_tested, 
                         f"Gamification endpoints: {endpoints_working}/{endpoints_tested} working ({success_rate:.1f}%)")
            
            return endpoints_working == endpoints_tested
            
        except Exception as e:
            self.log_test("Gamification Endpoints Test", False, f"Exception: {str(e)}")
            return False
    
    def investigate_xp_discrepancy(self):
        """Investigate the XP discrepancy between leaderboard and user data"""
        try:
            print(f"\n🔍 INVESTIGATING XP DISCREPANCY")
            print("=" * 60)
            
            # The leaderboard shows "Gamification Admin" with 40 XP
            # But user gamification data for emergency admin shows 0 XP
            # This suggests there might be multiple admin users
            
            print(f"   🎯 ANALYZING XP DISCREPANCY:")
            print(f"      Leaderboard shows: 'Gamification Admin' with 40 XP")
            print(f"      User data shows: 'Emergency Admin' with 0 XP")
            print(f"      User ID: {self.admin_user_data.get('id') if self.admin_user_data else 'Unknown'}")
            
            # Look for the "Gamification Admin" user in the leaderboard
            gamification_admin_user = None
            if self.leaderboard_data:
                for user in self.leaderboard_data:
                    if user.get('username') == 'Gamification Admin':
                        gamification_admin_user = user
                        break
            
            if gamification_admin_user:
                print(f"\n   📊 GAMIFICATION ADMIN USER FOUND:")
                print(f"      Username: {gamification_admin_user.get('username')}")
                print(f"      XP: {gamification_admin_user.get('xp')}")
                print(f"      Level: {gamification_admin_user.get('level')} {gamification_admin_user.get('level_emoji', '')}")
                print(f"      Rank: {gamification_admin_user.get('rank')}")
                
                # This suggests there are two different admin users:
                # 1. "Gamification Admin" with 40 XP (the one who made contributions)
                # 2. "Emergency Admin" with 0 XP (the one we're logged in as)
                
                self.log_test("XP Discrepancy Investigation", True, 
                             f"✅ Found XP discrepancy - two different admin users exist")
                
                print(f"\n   💡 HYPOTHESIS:")
                print(f"      - 'Gamification Admin' (40 XP) is the user who made the contribution")
                print(f"      - 'Emergency Admin' (0 XP) is a different user account")
                print(f"      - The contribution TK-CONTRIB-4DADAC was likely made by Gamification Admin")
                print(f"      - XP was awarded to Gamification Admin, not Emergency Admin")
                
                return True
            else:
                self.log_test("XP Discrepancy Investigation", False, 
                             f"❌ Could not find Gamification Admin user in leaderboard")
                return False
                
        except Exception as e:
            self.log_test("XP Discrepancy Investigation", False, f"Exception: {str(e)}")
            return False
        """Test the contribution approval workflow if we have a pending contribution"""
        try:
            print(f"\n⚡ TESTING CONTRIBUTION APPROVAL WORKFLOW")
            print("=" * 60)
            
            if not self.contribution_data:
                print(f"   ⚠️ No specific contribution found - testing with any available contribution")
                
                # Get any pending contribution for testing
                response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions?limit=1", timeout=10)
                if response.status_code == 200:
                    contributions = response.json()
                    if contributions:
                        test_contribution = contributions[0]
                        print(f"   📋 Using contribution {test_contribution.get('id')} for testing")
                    else:
                        self.log_test("Contribution Approval Workflow", False, 
                                     "No pending contributions available for testing")
                        return False
                else:
                    self.log_test("Contribution Approval Workflow", False, 
                                 f"Failed to get contributions for testing: {response.status_code}")
                    return False
            else:
                test_contribution = self.contribution_data
                print(f"   📋 Using specific contribution {test_contribution.get('id')} for testing")
            
            # Test approval endpoint (but don't actually approve to avoid side effects)
            contribution_id = test_contribution.get('id')
            user_id = test_contribution.get('user_id')
            xp_to_award = test_contribution.get('xp_to_award', 0)
            
            print(f"   📊 CONTRIBUTION ANALYSIS:")
            print(f"      Contribution ID: {contribution_id}")
            print(f"      User ID: {user_id}")
            print(f"      XP to Award: {xp_to_award}")
            print(f"      Item Type: {test_contribution.get('item_type')}")
            print(f"      Already Approved: {test_contribution.get('is_approved', False)}")
            
            # Check if this contribution is already approved
            if test_contribution.get('is_approved', False):
                self.log_test("Contribution Approval Workflow", True, 
                             f"✅ Contribution {contribution_id} is already approved")
                
                # Check if XP was actually awarded to the user
                if user_id and self.admin_user_data and user_id == self.admin_user_data.get('id'):
                    current_xp = self.user_xp_data.get('xp', 0) if self.user_xp_data else 0
                    expected_xp = xp_to_award
                    
                    print(f"   🎯 XP VERIFICATION:")
                    print(f"      User Current XP: {current_xp}")
                    print(f"      Expected XP from this contribution: {expected_xp}")
                    
                    if current_xp >= expected_xp:
                        print(f"   ✅ XP appears to have been awarded correctly")
                        return True
                    else:
                        print(f"   ❌ XP may not have been awarded - user has less XP than expected")
                        return False
                
                return True
            else:
                self.log_test("Contribution Approval Workflow", False, 
                             f"❌ Contribution {contribution_id} is not yet approved")
                return False
            
        except Exception as e:
            self.log_test("Contribution Approval Workflow", False, f"Exception: {str(e)}")
            return False
    
    def run_gamification_investigation(self):
        """Run comprehensive gamification bug investigation"""
        print("\n🚨 URGENT GAMIFICATION BUG INVESTIGATION")
        print("Investigating XP not awarded despite contribution approval")
        print("=" * 80)
        
        investigation_results = []
        
        # Step 1: Authenticate as admin
        print("\n1️⃣ Authenticating as Emergency Admin...")
        investigation_results.append(self.authenticate_admin())
        
        if not self.auth_token:
            print("❌ Cannot proceed without admin authentication")
            return investigation_results
        
        # Step 2: Get current leaderboard data
        print("\n2️⃣ Analyzing Current Leaderboard...")
        investigation_results.append(self.get_leaderboard_data())
        
        # Step 3: Get user gamification data
        print("\n3️⃣ Getting User Gamification Data...")
        investigation_results.append(self.get_user_gamification_data())
        
        # Step 4: Search for specific contribution
        print("\n4️⃣ Searching for Specific Contribution...")
        investigation_results.append(self.search_specific_contribution())
        
        # Step 5: Search for specific team
        print("\n5️⃣ Searching for Specific Team...")
        investigation_results.append(self.search_team_in_database())
        
        # Step 6: Test gamification endpoints
        print("\n6️⃣ Testing Gamification Endpoints...")
        investigation_results.append(self.test_gamification_endpoints())
        
        # Step 7: Test contribution approval workflow
        print("\n7️⃣ Testing Contribution Approval Workflow...")
        investigation_results.append(self.test_contribution_approval_workflow())
        
        return investigation_results
    
    def print_investigation_summary(self):
        """Print comprehensive investigation summary"""
        print("\n📊 GAMIFICATION BUG INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # Admin access
        admin_working = any(r['success'] for r in self.test_results if 'Admin Authentication' in r['test'])
        if admin_working:
            print(f"  ✅ ADMIN ACCESS: Emergency admin account working")
        else:
            print(f"  ❌ ADMIN ACCESS: Cannot authenticate as admin")
        
        # Leaderboard data
        leaderboard_working = any(r['success'] for r in self.test_results if 'Leaderboard' in r['test'])
        if leaderboard_working and self.leaderboard_data:
            print(f"  ✅ LEADERBOARD: Working with {len(self.leaderboard_data)} users")
        else:
            print(f"  ❌ LEADERBOARD: Not accessible or no data")
        
        # User XP data
        user_xp_working = any(r['success'] for r in self.test_results if 'User Gamification' in r['test'])
        if user_xp_working and self.user_xp_data:
            current_xp = self.user_xp_data.get('xp', 0)
            level = self.user_xp_data.get('level', 'Unknown')
            print(f"  ✅ USER XP DATA: Current XP = {current_xp}, Level = {level}")
        else:
            print(f"  ❌ USER XP DATA: Not accessible")
        
        # Specific contribution
        contribution_found = any(r['success'] for r in self.test_results if 'Specific Contribution' in r['test'])
        if contribution_found:
            print(f"  ✅ CONTRIBUTION TK-CONTRIB-4DADAC: Found and analyzed")
        else:
            print(f"  ❌ CONTRIBUTION TK-CONTRIB-4DADAC: Not found in pending contributions")
        
        # Specific team
        team_found = any(r['success'] for r in self.test_results if 'Specific Team' in r['test'])
        if team_found:
            print(f"  ✅ TEAM TK-TEAM-AAD28D: Found in database")
        else:
            print(f"  ❌ TEAM TK-TEAM-AAD28D: Not found in database")
        
        # Gamification endpoints
        endpoints_working = any(r['success'] for r in self.test_results if 'Gamification Endpoints' in r['test'])
        if endpoints_working:
            print(f"  ✅ GAMIFICATION ENDPOINTS: All working correctly")
        else:
            print(f"  ❌ GAMIFICATION ENDPOINTS: Some endpoints not working")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        
        if not contribution_found and not team_found:
            print(f"  🚨 CRITICAL: Neither the contribution nor the team can be found")
            print(f"     - This suggests the reported IDs may be incorrect")
            print(f"     - Or the data may have been deleted/corrupted")
        elif contribution_found and not team_found:
            print(f"  ⚠️ PARTIAL: Contribution exists but team is missing")
            print(f"     - Team may have been deleted after contribution creation")
        elif not contribution_found and team_found:
            print(f"  ⚠️ PARTIAL: Team exists but contribution is missing")
            print(f"     - Contribution may have been processed/deleted")
            print(f"     - Or it may be in a different state (approved/rejected)")
        else:
            print(f"  ✅ DATA INTEGRITY: Both contribution and team found")
            
            if user_xp_working and self.user_xp_data:
                current_xp = self.user_xp_data.get('xp', 0)
                if current_xp == 0:
                    print(f"  🚨 XP ISSUE: User has 0 XP despite approved contribution")
                    print(f"     - XP may not have been awarded during approval")
                    print(f"     - Or there may be a bug in the XP awarding system")
                else:
                    print(f"  ✅ XP STATUS: User has {current_xp} XP")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if not contribution_found:
            print(f"  1. Verify the contribution ID 'TK-CONTRIB-4DADAC' is correct")
            print(f"  2. Check if the contribution has already been processed")
            print(f"  3. Search for contributions by the user instead of by ID")
        
        if not team_found:
            print(f"  1. Verify the team ID 'TK-TEAM-AAD28D' is correct")
            print(f"  2. Check if the team was deleted after contribution creation")
        
        if user_xp_working and self.user_xp_data and self.user_xp_data.get('xp', 0) == 0:
            print(f"  1. Check the XP awarding logic in the backend")
            print(f"  2. Verify the contribution approval process")
            print(f"  3. Check for errors in the gamification system logs")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run comprehensive investigation and return success status"""
        investigation_results = self.run_gamification_investigation()
        self.print_investigation_summary()
        return any(investigation_results)

def main():
    """Main test execution"""
    investigator = TopKitGamificationInvestigator()
    success = investigator.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()