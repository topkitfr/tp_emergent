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
BACKEND_URL = "https://jersey-levels.preview.emergentagent.com/api"

# Emergency Admin Credentials (KNOWN WORKING)
EMERGENCY_ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!"
}

class TopKitGamificationFollowUpInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.user_xp_data = None
        self.leaderboard_data = None
        self.test_contribution_id = None
        self.test_team_id = None
        
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
    
    def get_current_xp_status(self):
        """Get current XP status for emergency admin account"""
        try:
            if not self.admin_user_data:
                self.log_test("Current XP Status", False, "No admin user data available")
                return False
            
            print(f"\n🎮 CHECKING CURRENT XP STATUS FOR EMERGENCY ADMIN")
            print("=" * 60)
            
            user_id = self.admin_user_data.get('id')
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/gamification", timeout=10)
            
            if response.status_code == 200:
                self.user_xp_data = response.json()
                
                current_xp = self.user_xp_data.get('xp', 0)
                level = self.user_xp_data.get('level', 'Unknown')
                level_emoji = self.user_xp_data.get('level_emoji', '')
                progress = self.user_xp_data.get('progress_percentage', 0)
                xp_to_next = self.user_xp_data.get('xp_to_next_level', 0)
                next_level = self.user_xp_data.get('next_level', 'Max Level')
                
                self.log_test("Current XP Status", True, 
                             f"Emergency admin current XP: {current_xp}")
                
                print(f"\n   📊 EMERGENCY ADMIN XP STATUS:")
                print(f"      User ID: {self.user_xp_data.get('id')}")
                print(f"      Name: {self.user_xp_data.get('name')}")
                print(f"      Email: {self.user_xp_data.get('email')}")
                print(f"      Current XP: {current_xp}")
                print(f"      Level: {level} {level_emoji}")
                print(f"      Progress: {progress}%")
                print(f"      XP to Next Level: {xp_to_next}")
                print(f"      Next Level: {next_level}")
                
                return True
                
            else:
                self.log_test("Current XP Status", False, 
                             f"Failed to get user gamification data: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Current XP Status", False, f"Exception: {str(e)}")
            return False
    
    def check_leaderboard_position(self):
        """Check emergency admin's position on leaderboard"""
        try:
            print(f"\n📊 CHECKING LEADERBOARD POSITION")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=50", timeout=10)
            
            if response.status_code == 200:
                self.leaderboard_data = response.json()
                
                print(f"   Found {len(self.leaderboard_data)} users on leaderboard")
                
                # Look for emergency admin in leaderboard
                emergency_admin_position = None
                admin_user_id = self.admin_user_data.get('id') if self.admin_user_data else None
                
                for i, user in enumerate(self.leaderboard_data):
                    username = user.get('username', 'Unknown')
                    if ('emergency' in username.lower() and 'admin' in username.lower()) or \
                       (admin_user_id and user.get('user_id') == admin_user_id):
                        emergency_admin_position = i + 1
                        break
                
                if emergency_admin_position:
                    user_data = self.leaderboard_data[emergency_admin_position - 1]
                    self.log_test("Leaderboard Position", True, 
                                 f"Emergency admin found at position {emergency_admin_position}")
                    
                    print(f"\n   🎯 EMERGENCY ADMIN ON LEADERBOARD:")
                    print(f"      Position: #{emergency_admin_position}")
                    print(f"      Username: {user_data.get('username')}")
                    print(f"      XP: {user_data.get('xp', 0)}")
                    print(f"      Level: {user_data.get('level')} {user_data.get('level_emoji', '')}")
                else:
                    self.log_test("Leaderboard Position", False, 
                                 "Emergency admin not found on leaderboard")
                    
                    print(f"\n   ❌ EMERGENCY ADMIN NOT FOUND ON LEADERBOARD")
                    print(f"   📋 TOP 10 USERS:")
                    for i, user in enumerate(self.leaderboard_data[:10], 1):
                        username = user.get('username', 'Unknown')
                        xp = user.get('xp', 0)
                        level = user.get('level', 'Unknown')
                        level_emoji = user.get('level_emoji', '')
                        print(f"      {i:2d}. {username} - {xp} XP ({level} {level_emoji})")
                
                return True
                
            else:
                self.log_test("Leaderboard Position", False, 
                             f"Failed to get leaderboard: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Leaderboard Position", False, f"Exception: {str(e)}")
            return False
    
    def identify_admin_accounts(self):
        """Identify all admin accounts in the system"""
        try:
            print(f"\n👥 IDENTIFYING ALL ADMIN ACCOUNTS")
            print("=" * 60)
            
            if not self.leaderboard_data:
                self.log_test("Admin Accounts Identification", False, "No leaderboard data available")
                return False
            
            admin_accounts = []
            for user in self.leaderboard_data:
                username = user.get('username', '').lower()
                if 'admin' in username:
                    admin_accounts.append(user)
            
            if admin_accounts:
                self.log_test("Admin Accounts Identification", True, 
                             f"Found {len(admin_accounts)} admin accounts")
                
                print(f"\n   👥 ALL ADMIN ACCOUNTS FOUND:")
                for i, admin in enumerate(admin_accounts, 1):
                    username = admin.get('username')
                    xp = admin.get('xp', 0)
                    level = admin.get('level', 'Unknown')
                    level_emoji = admin.get('level_emoji', '')
                    rank = admin.get('rank', 'Unknown')
                    
                    print(f"      {i}. {username}")
                    print(f"         XP: {xp}")
                    print(f"         Level: {level} {level_emoji}")
                    print(f"         Rank: #{rank}")
                    print()
                
                # Check if there's confusion between accounts
                if len(admin_accounts) > 1:
                    print(f"   ⚠️ MULTIPLE ADMIN ACCOUNTS DETECTED!")
                    print(f"      This could explain user confusion about XP progress")
                    
                    # Find the admin with highest XP
                    highest_xp_admin = max(admin_accounts, key=lambda x: x.get('xp', 0))
                    print(f"\n   🏆 HIGHEST XP ADMIN:")
                    print(f"      Username: {highest_xp_admin.get('username')}")
                    print(f"      XP: {highest_xp_admin.get('xp', 0)}")
                    print(f"      This account likely received XP from contributions")
                
                return True
            else:
                self.log_test("Admin Accounts Identification", False, "No admin accounts found on leaderboard")
                return False
                
        except Exception as e:
            self.log_test("Admin Accounts Identification", False, f"Exception: {str(e)}")
            return False
    
    def search_for_reported_team(self):
        """Search for the specific team TK-TEAM-018D25 reported by user"""
        try:
            print(f"\n🔍 SEARCHING FOR REPORTED TEAM: TK-TEAM-018D25")
            print("=" * 60)
            
            # Get all teams to search for the specific team
            response = self.session.get(f"{BACKEND_URL}/teams", timeout=10)
            
            if response.status_code == 200:
                teams = response.json()
                
                # Search for the specific team by reference or ID
                reported_team = None
                for team in teams:
                    team_ref = team.get('topkit_reference', '')
                    team_id = team.get('id', '')
                    team_name = team.get('name', '')
                    
                    if ('TK-TEAM-018D25' in team_ref or 
                        'TK-TEAM-018D25' in team_id or
                        '018D25' in team_ref or
                        '018D25' in team_id):
                        reported_team = team
                        break
                
                if reported_team:
                    self.log_test("Reported Team Search", True, 
                                 f"Found reported team TK-TEAM-018D25")
                    
                    print(f"\n   📋 REPORTED TEAM DETAILS:")
                    print(f"      Team ID: {reported_team.get('id')}")
                    print(f"      Name: {reported_team.get('name')}")
                    print(f"      TopKit Reference: {reported_team.get('topkit_reference')}")
                    print(f"      Created By: {reported_team.get('created_by')}")
                    print(f"      Created At: {reported_team.get('created_at')}")
                    print(f"      Country: {reported_team.get('country', 'Unknown')}")
                    
                    return reported_team
                else:
                    self.log_test("Reported Team Search", False, 
                                 f"Team TK-TEAM-018D25 not found in database")
                    
                    print(f"   📋 RECENT TEAMS (showing first 10):")
                    for i, team in enumerate(teams[:10], 1):
                        team_ref = team.get('topkit_reference', 'No Reference')
                        team_name = team.get('name', 'No Name')
                        created_by = team.get('created_by', 'Unknown')
                        print(f"      {i:2d}. {team_ref} - {team_name} (by {created_by})")
                    
                    return None
                
            else:
                self.log_test("Reported Team Search", False, 
                             f"Failed to get teams: {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Reported Team Search", False, f"Exception: {str(e)}")
            return None
    
    def check_gamification_contribution_for_team(self, team_data):
        """Check if gamification contribution exists for the reported team"""
        try:
            print(f"\n🎯 CHECKING GAMIFICATION CONTRIBUTION FOR REPORTED TEAM")
            print("=" * 60)
            
            if not team_data:
                self.log_test("Team Gamification Contribution Check", False, "No team data provided")
                return None
            
            team_id = team_data.get('id')
            team_name = team_data.get('name', 'Unknown Team')
            
            # Get all contributions (both pending and approved)
            pending_response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions?limit=100", timeout=10)
            
            if pending_response.status_code != 200:
                self.log_test("Team Gamification Contribution Check", False, 
                             f"Failed to get contributions: {pending_response.status_code}")
                return None
            
            all_contributions = pending_response.json()
            
            # Look for contribution related to the reported team
            team_contribution = None
            for contrib in all_contributions:
                if (contrib.get('item_type') == 'team' and 
                    contrib.get('item_id') == team_id):
                    team_contribution = contrib
                    break
            
            if team_contribution:
                self.log_test("Team Gamification Contribution Check", True, 
                             f"Found gamification contribution for team {team_name}")
                
                print(f"\n   📋 TEAM GAMIFICATION CONTRIBUTION:")
                print(f"      Contribution ID: {team_contribution.get('id')}")
                print(f"      User ID: {team_contribution.get('user_id')}")
                print(f"      User Name: {team_contribution.get('user_name')}")
                print(f"      Item Type: {team_contribution.get('item_type')}")
                print(f"      Item ID: {team_contribution.get('item_id')}")
                print(f"      XP to Award: {team_contribution.get('xp_to_award', 0)}")
                print(f"      Is Approved: {team_contribution.get('is_approved', False)}")
                print(f"      Created At: {team_contribution.get('created_at')}")
                print(f"      Approved At: {team_contribution.get('approved_at', 'Not approved')}")
                print(f"      Approved By: {team_contribution.get('approved_by', 'Not approved')}")
                
                # Check if this contribution was created by emergency admin
                emergency_admin_id = self.admin_user_data.get('id') if self.admin_user_data else None
                if team_contribution.get('user_id') == emergency_admin_id:
                    print(f"   ✅ MATCH: This contribution was created by emergency admin!")
                else:
                    print(f"   ⚠️ MISMATCH: This contribution was NOT created by emergency admin")
                    print(f"      Expected User ID: {emergency_admin_id}")
                    print(f"      Actual User ID: {team_contribution.get('user_id')}")
                
                return team_contribution
            else:
                self.log_test("Team Gamification Contribution Check", False, 
                             f"No gamification contribution found for team {team_name}")
                
                print(f"   📋 TEAM-TYPE CONTRIBUTIONS (showing all):")
                team_contributions = [c for c in all_contributions if c.get('item_type') == 'team']
                if team_contributions:
                    for i, contrib in enumerate(team_contributions, 1):
                        print(f"      {i}. {contrib.get('id', 'No ID')} - {contrib.get('user_name')} - {contrib.get('item_details', {}).get('name', 'Unknown Team')} - {contrib.get('xp_to_award', 0)} XP")
                else:
                    print(f"      No team-type contributions found")
                
                return None
                
        except Exception as e:
            self.log_test("Team Gamification Contribution Check", False, f"Exception: {str(e)}")
            return None
    
    def investigate_xp_awarding_bug(self, team_contribution):
        """Investigate why XP was not awarded for the team contribution"""
        try:
            print(f"\n🐛 INVESTIGATING XP AWARDING BUG")
            print("=" * 60)
            
            if not team_contribution:
                self.log_test("XP Awarding Bug Investigation", False, "No team contribution data provided")
                return False
            
            contribution_id = team_contribution.get('id')
            is_approved = team_contribution.get('is_approved', False)
            xp_awarded = team_contribution.get('xp_awarded', 0)
            user_id = team_contribution.get('user_id')
            
            print(f"   📋 CONTRIBUTION STATUS:")
            print(f"      Contribution ID: {contribution_id}")
            print(f"      Is Approved: {is_approved}")
            print(f"      XP Awarded: {xp_awarded}")
            print(f"      User ID: {user_id}")
            
            # Check if contribution is approved but XP not awarded
            if is_approved and xp_awarded == 0:
                self.log_test("XP Awarding Bug Investigation", False, 
                             "🚨 BUG CONFIRMED: Contribution is approved but XP was not awarded!")
                
                print(f"\n   🚨 CRITICAL BUG IDENTIFIED:")
                print(f"      - Contribution is marked as approved")
                print(f"      - But XP awarded field is 0")
                print(f"      - This indicates the XP awarding mechanism failed")
                
                return False
                
            elif is_approved and xp_awarded > 0:
                self.log_test("XP Awarding Bug Investigation", True, 
                             f"Contribution is approved and XP was awarded ({xp_awarded} XP)")
                
                print(f"\n   ✅ XP AWARDING WORKING:")
                print(f"      - Contribution is approved")
                print(f"      - XP was awarded: {xp_awarded}")
                
                # But check if the user actually received the XP
                if user_id == self.admin_user_data.get('id'):
                    current_xp = self.user_xp_data.get('xp', 0) if self.user_xp_data else 0
                    if current_xp >= xp_awarded:
                        print(f"      - User has {current_xp} XP (includes awarded XP)")
                        return True
                    else:
                        print(f"      - 🚨 USER HAS ONLY {current_xp} XP (less than awarded {xp_awarded})")
                        print(f"      - This suggests XP was awarded but not properly added to user")
                        return False
                else:
                    print(f"      - Contribution was made by different user")
                    return True
                
            elif not is_approved:
                self.log_test("XP Awarding Bug Investigation", True, 
                             "Contribution is not yet approved - XP awarding pending")
                
                print(f"\n   ⏳ CONTRIBUTION PENDING:")
                print(f"      - Contribution is not yet approved")
                print(f"      - XP will be awarded upon approval")
                print(f"      - This is normal behavior")
                
                return True
            else:
                self.log_test("XP Awarding Bug Investigation", False, 
                             "Unknown contribution state")
                return False
                
        except Exception as e:
            self.log_test("XP Awarding Bug Investigation", False, f"Exception: {str(e)}")
            return False
    
    def create_test_master_kit_contribution(self):
        """Create a test master kit contribution to verify the workflow"""
        try:
            print(f"\n🏗️ CREATING TEST MASTER KIT CONTRIBUTION")
            print("=" * 60)
            
            # First, get available teams, brands, and competitions for the master kit
            teams_response = self.session.get(f"{BACKEND_URL}/teams", timeout=10)
            brands_response = self.session.get(f"{BACKEND_URL}/brands", timeout=10)
            competitions_response = self.session.get(f"{BACKEND_URL}/competitions", timeout=10)
            
            if teams_response.status_code != 200 or brands_response.status_code != 200 or competitions_response.status_code != 200:
                self.log_test("Test Master Kit Creation", False, "Failed to get required data for master kit creation")
                return False
            
            teams = teams_response.json()
            brands = brands_response.json()
            competitions = competitions_response.json()
            
            if not teams or not brands or not competitions:
                self.log_test("Test Master Kit Creation", False, "No teams, brands, or competitions available")
                return False
            
            # Use the first available team, brand, and competition
            team = teams[0]
            brand = brands[0]
            competition = competitions[0]
            
            # Generate unique master kit data
            kit_name = f"Test Kit {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            master_kit_data = {
                "club_id": team.get('id'),
                "brand_id": brand.get('id'),
                "competition_id": competition.get('id'),
                "season": "2025-2026",  # Fixed format
                "kit_type": "home",
                "gender": "man",
                "model": "authentic",  # Fixed field name
                "primary_color": "Test Blue",
                "secondary_color": "Test White",
                "front_photo_url": "test_image.jpg"
            }
            
            print(f"   📋 Creating test master kit for: {team.get('name')} {master_kit_data['season']}")
            
            # Create master kit
            response = self.session.post(
                f"{BACKEND_URL}/master-kits",
                json=master_kit_data,
                timeout=10
            )
            
            if response.status_code == 200:
                kit_response = response.json()
                self.test_team_id = kit_response.get('id')  # Using team_id variable for the kit ID
                
                self.log_test("Test Master Kit Creation", True, 
                             f"Test master kit created successfully")
                
                print(f"      Kit ID: {self.test_team_id}")
                print(f"      Club: {kit_response.get('club')}")
                print(f"      Season: {kit_response.get('season')}")
                print(f"      Kit Type: {kit_response.get('kit_type')}")
                print(f"      Created By: {kit_response.get('created_by')}")
                
                return True
                
            else:
                self.log_test("Test Master Kit Creation", False, 
                             f"Failed to create test master kit: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Test Master Kit Creation", False, f"Exception: {str(e)}")
            return False
    
    def check_gamification_contribution_created(self):
        """Check if gamification contribution was created for the test master kit"""
        try:
            print(f"\n🎯 CHECKING GAMIFICATION CONTRIBUTION CREATION")
            print("=" * 60)
            
            if not self.test_team_id:
                self.log_test("Gamification Contribution Check", False, "No test master kit ID available")
                return False
            
            # Get pending contributions
            response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions?limit=100", timeout=10)
            
            if response.status_code == 200:
                contributions = response.json()
                
                # Look for contribution related to our test master kit
                test_contribution = None
                for contrib in contributions:
                    if (contrib.get('item_type') == 'jersey' and 
                        contrib.get('item_id') == self.test_team_id):
                        test_contribution = contrib
                        break
                
                if test_contribution:
                    self.test_contribution_id = test_contribution.get('id')
                    
                    self.log_test("Gamification Contribution Check", True, 
                                 f"Gamification contribution created for test master kit")
                    
                    print(f"\n   📋 GAMIFICATION CONTRIBUTION DETAILS:")
                    print(f"      Contribution ID: {test_contribution.get('id')}")
                    print(f"      User ID: {test_contribution.get('user_id')}")
                    print(f"      User Name: {test_contribution.get('user_name')}")
                    print(f"      Item Type: {test_contribution.get('item_type')}")
                    print(f"      Item ID: {test_contribution.get('item_id')}")
                    print(f"      XP to Award: {test_contribution.get('xp_to_award', 0)}")
                    print(f"      Is Approved: {test_contribution.get('is_approved', False)}")
                    print(f"      Created At: {test_contribution.get('created_at')}")
                    
                    return True
                else:
                    self.log_test("Gamification Contribution Check", False, 
                                 f"No gamification contribution found for test master kit {self.test_team_id}")
                    
                    print(f"   📋 RECENT CONTRIBUTIONS (showing first 5):")
                    for i, contrib in enumerate(contributions[:5], 1):
                        print(f"      {i}. {contrib.get('id', 'No ID')} - {contrib.get('item_type')} - {contrib.get('user_name')} - {contrib.get('xp_to_award', 0)} XP")
                    
                    return False
                
            else:
                self.log_test("Gamification Contribution Check", False, 
                             f"Failed to get pending contributions: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Gamification Contribution Check", False, f"Exception: {str(e)}")
            return False
    
    def test_contribution_approval_and_xp_awarding(self):
        """Test the contribution approval process and XP awarding"""
        try:
            print(f"\n⚡ TESTING CONTRIBUTION APPROVAL AND XP AWARDING")
            print("=" * 60)
            
            if not self.test_contribution_id:
                self.log_test("Contribution Approval Test", False, "No test contribution ID available")
                return False
            
            # Get current XP before approval
            current_xp_before = self.user_xp_data.get('xp', 0) if self.user_xp_data else 0
            print(f"   📊 XP BEFORE APPROVAL: {current_xp_before}")
            
            # Approve the contribution
            approval_data = {"contribution_id": self.test_contribution_id}
            response = self.session.post(
                f"{BACKEND_URL}/admin/approve-contribution",
                data=approval_data,
                timeout=10
            )
            
            if response.status_code == 200:
                approval_response = response.json()
                
                self.log_test("Contribution Approval Test", True, 
                             f"Contribution approved successfully")
                
                print(f"\n   ✅ APPROVAL RESPONSE:")
                print(f"      Message: {approval_response.get('message')}")
                print(f"      XP Awarded: {approval_response.get('xp_awarded', 0)}")
                print(f"      New Level: {approval_response.get('new_level')}")
                print(f"      Level Changed: {approval_response.get('level_changed', False)}")
                
                # Get updated XP after approval
                user_id = self.admin_user_data.get('id')
                xp_response = self.session.get(f"{BACKEND_URL}/users/{user_id}/gamification", timeout=10)
                
                if xp_response.status_code == 200:
                    updated_xp_data = xp_response.json()
                    current_xp_after = updated_xp_data.get('xp', 0)
                    xp_gained = current_xp_after - current_xp_before
                    
                    print(f"\n   📊 XP VERIFICATION:")
                    print(f"      XP Before: {current_xp_before}")
                    print(f"      XP After: {current_xp_after}")
                    print(f"      XP Gained: {xp_gained}")
                    print(f"      Expected XP Gain: {approval_response.get('xp_awarded', 0)}")
                    
                    if xp_gained == approval_response.get('xp_awarded', 0):
                        print(f"   ✅ XP AWARDING SUCCESSFUL!")
                        return True
                    else:
                        print(f"   ❌ XP MISMATCH - Expected {approval_response.get('xp_awarded', 0)}, got {xp_gained}")
                        return False
                else:
                    print(f"   ❌ Failed to get updated XP data: {xp_response.status_code}")
                    return False
                
            else:
                self.log_test("Contribution Approval Test", False, 
                             f"Failed to approve contribution: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Contribution Approval Test", False, f"Exception: {str(e)}")
            return False
    
    def verify_final_xp_status(self):
        """Verify final XP status after the test"""
        try:
            print(f"\n🎯 VERIFYING FINAL XP STATUS")
            print("=" * 60)
            
            if not self.admin_user_data:
                self.log_test("Final XP Verification", False, "No admin user data available")
                return False
            
            user_id = self.admin_user_data.get('id')
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/gamification", timeout=10)
            
            if response.status_code == 200:
                final_xp_data = response.json()
                
                final_xp = final_xp_data.get('xp', 0)
                final_level = final_xp_data.get('level', 'Unknown')
                final_level_emoji = final_xp_data.get('level_emoji', '')
                final_progress = final_xp_data.get('progress_percentage', 0)
                
                self.log_test("Final XP Verification", True, 
                             f"Final XP status verified: {final_xp} XP")
                
                print(f"\n   📊 FINAL XP STATUS:")
                print(f"      User: {final_xp_data.get('name')}")
                print(f"      Email: {final_xp_data.get('email')}")
                print(f"      Final XP: {final_xp}")
                print(f"      Final Level: {final_level} {final_level_emoji}")
                print(f"      Progress: {final_progress}%")
                print(f"      XP to Next Level: {final_xp_data.get('xp_to_next_level', 0)}")
                
                # Compare with initial XP
                initial_xp = self.user_xp_data.get('xp', 0) if self.user_xp_data else 0
                xp_change = final_xp - initial_xp
                
                print(f"\n   📈 XP CHANGE SUMMARY:")
                print(f"      Initial XP: {initial_xp}")
                print(f"      Final XP: {final_xp}")
                print(f"      Total XP Gained: {xp_change}")
                
                if xp_change > 0:
                    print(f"   ✅ XP SUCCESSFULLY AWARDED!")
                else:
                    print(f"   ❌ NO XP GAINED")
                
                return True
                
            else:
                self.log_test("Final XP Verification", False, 
                             f"Failed to get final XP data: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Final XP Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_follow_up_investigation(self):
        """Run comprehensive follow-up investigation"""
        print("\n🔍 CRITICAL GAMIFICATION BUG INVESTIGATION")
        print("Investigating team TK-TEAM-018D25 and XP awarding failure")
        print("=" * 80)
        
        investigation_results = []
        
        # Step 1: Authenticate as emergency admin
        print("\n1️⃣ Authenticating as Emergency Admin...")
        investigation_results.append(self.authenticate_admin())
        
        if not self.auth_token:
            print("❌ Cannot proceed without admin authentication")
            return investigation_results
        
        # Step 2: Check current XP status
        print("\n2️⃣ Checking Current XP Status...")
        investigation_results.append(self.get_current_xp_status())
        
        # Step 3: Check leaderboard position
        print("\n3️⃣ Checking Leaderboard Position...")
        investigation_results.append(self.check_leaderboard_position())
        
        # Step 4: Identify all admin accounts
        print("\n4️⃣ Identifying All Admin Accounts...")
        investigation_results.append(self.identify_admin_accounts())
        
        # Step 5: Search for the reported team TK-TEAM-018D25
        print("\n5️⃣ Searching for Reported Team TK-TEAM-018D25...")
        reported_team = self.search_for_reported_team()
        investigation_results.append(reported_team is not None)
        
        # Step 6: Check gamification contribution for the reported team
        print("\n6️⃣ Checking Gamification Contribution for Reported Team...")
        team_contribution = None
        if reported_team:
            team_contribution = self.check_gamification_contribution_for_team(reported_team)
            investigation_results.append(team_contribution is not None)
        else:
            investigation_results.append(False)
        
        # Step 7: Investigate XP awarding bug
        print("\n7️⃣ Investigating XP Awarding Bug...")
        if team_contribution:
            investigation_results.append(self.investigate_xp_awarding_bug(team_contribution))
        else:
            investigation_results.append(False)
        
        # Step 8: Create test master kit contribution to verify workflow
        print("\n8️⃣ Creating Test Master Kit Contribution...")
        investigation_results.append(self.create_test_master_kit_contribution())
        
        # Step 9: Check if gamification contribution was created for test
        print("\n9️⃣ Checking Gamification Contribution Creation for Test...")
        investigation_results.append(self.check_gamification_contribution_created())
        
        # Step 10: Test contribution approval and XP awarding
        print("\n🔟 Testing Contribution Approval and XP Awarding...")
        investigation_results.append(self.test_contribution_approval_and_xp_awarding())
        
        # Step 11: Verify final XP status
        print("\n1️⃣1️⃣ Verifying Final XP Status...")
        investigation_results.append(self.verify_final_xp_status())
        
        return investigation_results
    
    def print_investigation_summary(self):
        """Print comprehensive investigation summary"""
        print("\n📊 CRITICAL GAMIFICATION BUG INVESTIGATION SUMMARY")
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
            if self.admin_user_data:
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
        else:
            print(f"  ❌ ADMIN ACCESS: Cannot authenticate as admin")
        
        # XP Status
        xp_status_working = any(r['success'] for r in self.test_results if 'Current XP Status' in r['test'])
        if xp_status_working and self.user_xp_data:
            current_xp = self.user_xp_data.get('xp', 0)
            level = self.user_xp_data.get('level', 'Unknown')
            print(f"  ✅ XP STATUS: Emergency admin has {current_xp} XP ({level})")
        else:
            print(f"  ❌ XP STATUS: Could not retrieve XP data")
        
        # Reported team search
        reported_team_found = any(r['success'] for r in self.test_results if 'Reported Team Search' in r['test'])
        if reported_team_found:
            print(f"  ✅ REPORTED TEAM: Found team TK-TEAM-018D25 in database")
        else:
            print(f"  ❌ REPORTED TEAM: Team TK-TEAM-018D25 not found in database")
        
        # Team contribution check
        team_contribution_found = any(r['success'] for r in self.test_results if 'Team Gamification Contribution Check' in r['test'])
        if team_contribution_found:
            print(f"  ✅ TEAM CONTRIBUTION: Found gamification contribution for reported team")
        else:
            print(f"  ❌ TEAM CONTRIBUTION: No gamification contribution found for reported team")
        
        # XP awarding bug investigation
        xp_bug_investigated = any(r['success'] for r in self.test_results if 'XP Awarding Bug Investigation' in r['test'])
        if xp_bug_investigated:
            print(f"  ✅ XP BUG INVESTIGATION: XP awarding mechanism working correctly")
        else:
            print(f"  🚨 XP BUG INVESTIGATION: XP awarding mechanism has issues")
        
        # Contribution workflow
        contribution_created = any(r['success'] for r in self.test_results if 'Test Master Kit Creation' in r['test'])
        gamification_tracked = any(r['success'] for r in self.test_results if 'Gamification Contribution Check' in r['test'])
        approval_worked = any(r['success'] for r in self.test_results if 'Contribution Approval Test' in r['test'])
        
        if contribution_created and gamification_tracked and approval_worked:
            print(f"  ✅ CONTRIBUTION WORKFLOW: Complete workflow working")
        elif contribution_created and gamification_tracked:
            print(f"  ⚠️ CONTRIBUTION WORKFLOW: Creation and tracking work, approval failed")
        elif contribution_created:
            print(f"  ⚠️ CONTRIBUTION WORKFLOW: Creation works, tracking/approval failed")
        else:
            print(f"  ❌ CONTRIBUTION WORKFLOW: Creation failed")
        
        # Admin accounts analysis
        admin_accounts_identified = any(r['success'] for r in self.test_results if 'Admin Accounts Identification' in r['test'])
        if admin_accounts_identified:
            print(f"  ✅ ADMIN ACCOUNTS: Multiple admin accounts identified")
        else:
            print(f"  ❌ ADMIN ACCOUNTS: Could not identify admin accounts")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        
        if admin_working and xp_status_working:
            current_xp = self.user_xp_data.get('xp', 0) if self.user_xp_data else 0
            
            if not reported_team_found:
                print(f"  🚨 TEAM NOT FOUND: The reported team TK-TEAM-018D25 does not exist in database")
                print(f"     - Team may have been deleted or reference is incorrect")
                print(f"     - User may have misremembered the team reference")
            elif not team_contribution_found:
                print(f"  🚨 CONTRIBUTION MISSING: No gamification contribution found for the team")
                print(f"     - Team creation may not have triggered gamification tracking")
                print(f"     - This indicates a bug in the contribution creation process")
            elif not xp_bug_investigated:
                print(f"  🚨 XP AWARDING BUG: XP was not awarded despite team approval")
                print(f"     - This confirms the user's report of the XP awarding bug")
                print(f"     - The approval process is not properly awarding XP")
            else:
                print(f"  ✅ SYSTEM WORKING: All components appear to be functioning correctly")
                print(f"     - The issue may be user confusion or a resolved bug")
        
        if contribution_created and gamification_tracked and approval_worked:
            print(f"  ✅ WORKFLOW CONFIRMED: Complete contribution → XP workflow is working")
            print(f"     - New contributions properly trigger gamification tracking")
            print(f"     - Approval process awards XP correctly")
            print(f"     - The system is functioning as intended for new contributions")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if not reported_team_found:
            print(f"  1. Verify the correct team reference - TK-TEAM-018D25 may be incorrect")
            print(f"  2. Check if the team was created under a different admin account")
            print(f"  3. Search for teams created around the same time period")
        elif not team_contribution_found:
            print(f"  1. 🚨 CRITICAL BUG: Team creation is not triggering gamification contributions")
            print(f"  2. The create_contribution_entry function may not be called for teams")
            print(f"  3. Check the team creation endpoint for gamification integration")
        elif not xp_bug_investigated:
            print(f"  1. 🚨 CRITICAL BUG: XP awarding mechanism is broken")
            print(f"  2. The award_xp function may have issues")
            print(f"  3. Check the contribution approval process for XP awarding")
        
        if contribution_created and gamification_tracked and approval_worked:
            print(f"  1. The contribution workflow is working correctly for new contributions")
            print(f"  2. The issue may be specific to team contributions vs master kit contributions")
            print(f"  3. Consider testing team creation specifically")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run comprehensive investigation and return success status"""
        investigation_results = self.run_follow_up_investigation()
        self.print_investigation_summary()
        return any(investigation_results)

def main():
    """Main test execution"""
    investigator = TopKitGamificationFollowUpInvestigator()
    success = investigator.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()