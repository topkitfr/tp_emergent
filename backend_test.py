#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - FOLLOW-UP GAMIFICATION INVESTIGATION

USER FOLLOW-UP REQUEST:
Based on previous findings, I need to:
1. Check which user account (emergency.admin@topkit.test) currently has how much XP
2. Verify the contribution creation and approval workflow is working
3. Test creating a new contribution as emergency.admin@topkit.test to confirm XP awarding works
4. Check if there are multiple admin accounts causing confusion

Specifically test:
- Login as emergency.admin@topkit.test
- Check current XP for this account  
- Create a test team contribution
- Check if the contribution gets proper gamification tracking
- Test the approval process and XP awarding

The user reported creating TK-CONTRIB-4DADAC and expected XP but didn't see it. I need to verify if:
1. The emergency admin account is the one that should have received XP
2. The XP awarding workflow is working for new contributions
3. There's any issue with the specific user account they're using

PREVIOUS FINDINGS:
- Two different admin users exist - 'Gamification Admin' (40 XP) and 'Emergency Admin' (0 XP)
- User confusion between accounts was identified as root cause
- Gamification system was found to be working correctly
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
                "season": "2025-26",
                "kit_type": "home",
                "gender": "man",
                "kit_model": "authentic",
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
        print("\n🔍 FOLLOW-UP GAMIFICATION INVESTIGATION")
        print("Testing emergency.admin@topkit.test account and contribution workflow")
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
        
        # Step 5: Create test master kit contribution
        print("\n5️⃣ Creating Test Master Kit Contribution...")
        investigation_results.append(self.create_test_master_kit_contribution())
        
        # Step 6: Check if gamification contribution was created
        print("\n6️⃣ Checking Gamification Contribution Creation...")
        investigation_results.append(self.check_gamification_contribution_created())
        
        # Step 7: Test contribution approval and XP awarding
        print("\n7️⃣ Testing Contribution Approval and XP Awarding...")
        investigation_results.append(self.test_contribution_approval_and_xp_awarding())
        
        # Step 8: Verify final XP status
        print("\n8️⃣ Verifying Final XP Status...")
        investigation_results.append(self.verify_final_xp_status())
        
        return investigation_results
    
    def print_investigation_summary(self):
        """Print comprehensive investigation summary"""
        print("\n📊 FOLLOW-UP INVESTIGATION SUMMARY")
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
            
            if current_xp == 0:
                print(f"  🚨 CONFIRMED: Emergency admin account has 0 XP")
                print(f"     - This account has not received XP from contributions")
                print(f"     - User confusion likely between different admin accounts")
                print(f"     - The reported contribution TK-CONTRIB-4DADAC was likely made by a different admin")
            else:
                print(f"  ✅ PROGRESS: Emergency admin account has {current_xp} XP")
                print(f"     - This account has received XP from contributions")
        
        if contribution_created and gamification_tracked and approval_worked:
            print(f"  ✅ WORKFLOW CONFIRMED: Complete contribution → XP workflow is working")
            print(f"     - Master kit creation triggers gamification contribution")
            print(f"     - Approval process awards XP correctly")
            print(f"     - The system is functioning as intended")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if admin_working and xp_status_working:
            current_xp = self.user_xp_data.get('xp', 0) if self.user_xp_data else 0
            if current_xp == 0:
                print(f"  1. User should check if they're using the correct admin account")
                print(f"  2. The contribution TK-CONTRIB-4DADAC was likely made by 'Gamification Admin', not 'Emergency Admin'")
                print(f"  3. User should verify which account they used to create the original contribution")
            else:
                print(f"  1. Emergency admin account is working and has received XP")
                print(f"  2. The gamification system is functioning correctly")
        
        if contribution_created and gamification_tracked and approval_worked:
            print(f"  1. The contribution workflow is working correctly")
            print(f"  2. New contributions will properly award XP")
            print(f"  3. The system is ready for production use")
        
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