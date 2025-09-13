#!/usr/bin/env python3
"""
TopKit Contribution Approval Testing
Focus: Test contribution approval process and fix image application issue

DISCOVERED ISSUES:
1. All 7 contributions with images are still pending
2. No manual approval endpoint found - only auto-approval
3. Auto-approval requires vote_score >= 3, but contributions have no votes
4. Need to test voting system and manual approval process
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-jersey-db.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com", 
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com",
    "password": "T0p_Mdp_1288*"
}

class ContributionApprovalTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        
    def log_result(self, test_name, status, details):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {details}")
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log_result("Admin Authentication", "PASS", f"Admin authenticated: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_result("Admin Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", "FAIL", f"Exception: {str(e)}")
            return False
            
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.log_result("User Authentication", "PASS", f"User authenticated: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_result("User Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("User Authentication", "FAIL", f"Exception: {str(e)}")
            return False

    def test_voting_system(self):
        """Test the contribution voting system"""
        if not self.user_token:
            self.log_result("Voting System Test", "SKIP", "User authentication required")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Get pending contributions
            response = requests.get(f"{BACKEND_URL}/contributions?status=pending", headers=headers)
            if response.status_code != 200:
                self.log_result("Voting System Test", "FAIL", "Failed to fetch pending contributions")
                return False
            
            contributions = response.json()
            pending_with_images = [c for c in contributions if c.get('images') or c.get('logo') or c.get('secondary_photos')]
            
            if not pending_with_images:
                self.log_result("Voting System Test", "WARN", "No pending contributions with images found")
                return False
            
            # Test voting on the first contribution with images
            test_contribution = pending_with_images[0]
            contribution_id = test_contribution.get('id')
            
            self.log_result("Voting Test Setup", "INFO", 
                f"Testing voting on contribution {contribution_id[:8]} with images")
            
            # Test upvote
            vote_data = {
                "vote_type": "upvote",
                "reason": "Testing voting system for image contributions"
            }
            
            vote_response = requests.post(
                f"{BACKEND_URL}/contributions/{contribution_id}/vote", 
                json=vote_data, 
                headers=headers
            )
            
            if vote_response.status_code == 200:
                vote_result = vote_response.json()
                new_score = vote_result.get('contribution_score', 0)
                self.log_result("Contribution Voting", "PASS", 
                    f"Vote successful - New score: {new_score}")
                
                # Check if this triggers auto-approval (score >= 3)
                if new_score >= 3:
                    self.log_result("Auto-Approval Trigger", "INFO", 
                        f"Score {new_score} >= 3 - Should trigger auto-approval")
                    
                    # Wait and check if contribution was auto-approved
                    import time
                    time.sleep(3)
                    
                    # Check contribution status
                    status_response = requests.get(f"{BACKEND_URL}/contributions/{contribution_id}", headers=headers)
                    if status_response.status_code == 200:
                        updated_contribution = status_response.json()
                        new_status = updated_contribution.get('status', 'unknown')
                        
                        if new_status in ['approved', 'auto_approved']:
                            self.log_result("Auto-Approval Success", "PASS", 
                                f"Contribution auto-approved with status: {new_status}")
                            
                            # Check if images were applied to entity
                            self.check_entity_images_after_approval(updated_contribution)
                        else:
                            self.log_result("Auto-Approval Check", "WARN", 
                                f"Contribution still has status: {new_status} despite score >= 3")
                    else:
                        self.log_result("Auto-Approval Check", "FAIL", 
                            f"Failed to check contribution status: HTTP {status_response.status_code}")
                else:
                    self.log_result("Auto-Approval Trigger", "INFO", 
                        f"Score {new_score} < 3 - Need more votes for auto-approval")
                
                return True
            else:
                self.log_result("Contribution Voting", "FAIL", 
                    f"Vote failed: HTTP {vote_response.status_code} - {vote_response.text}")
                return False
                
        except Exception as e:
            self.log_result("Voting System Test", "FAIL", f"Exception: {str(e)}")
            return False

    def check_entity_images_after_approval(self, contribution):
        """Check if entity has images after contribution approval"""
        try:
            entity_type = contribution.get('entity_type')
            entity_id = contribution.get('entity_id')
            
            # Map entity types to endpoints
            endpoint_map = {
                'team': 'teams',
                'brand': 'brands', 
                'competition': 'competitions',
                'player': 'players',
                'master_jersey': 'master-jerseys'
            }
            
            endpoint = endpoint_map.get(entity_type)
            if not endpoint:
                self.log_result("Entity Image Check", "FAIL", f"Unknown entity type: {entity_type}")
                return
            
            # Get the specific entity
            response = requests.get(f"{BACKEND_URL}/{endpoint}")
            if response.status_code == 200:
                entities = response.json()
                
                # Find the specific entity
                target_entity = None
                for entity in entities:
                    if entity.get('id') == entity_id:
                        target_entity = entity
                        break
                
                if target_entity:
                    # Check if entity has image URLs populated
                    image_fields = ['logo_url', 'photo_url', 'front_photo_url', 'back_photo_url']
                    populated_fields = [field for field in image_fields if target_entity.get(field)]
                    
                    if populated_fields:
                        self.log_result("Entity Images Applied", "PASS", 
                            f"SUCCESS! Images applied to {entity_type}: {', '.join(populated_fields)}")
                        
                        # Test if the image URLs are accessible
                        for field in populated_fields:
                            image_url = target_entity.get(field)
                            self.test_image_url_accessibility(image_url, f"{entity_type} {field}")
                    else:
                        self.log_result("Entity Images Applied", "FAIL", 
                            f"CRITICAL: Approved contribution images NOT applied to {entity_type}")
                else:
                    self.log_result("Entity Image Check", "FAIL", 
                        f"Entity {entity_id} not found in {entity_type} collection")
            else:
                self.log_result("Entity Image Check", "FAIL", 
                    f"Failed to fetch {entity_type} collection: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("Entity Image Check", "FAIL", f"Exception: {str(e)}")

    def test_image_url_accessibility(self, image_url, image_name):
        """Test if an image URL is accessible"""
        try:
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'image' in content_type:
                    self.log_result(f"{image_name} Accessibility", "PASS", 
                        f"Image URL accessible - Content-Type: {content_type}")
                else:
                    self.log_result(f"{image_name} Accessibility", "WARN", 
                        f"URL accessible but not an image - Content-Type: {content_type}")
            else:
                self.log_result(f"{image_name} Accessibility", "FAIL", 
                    f"Image URL not accessible - HTTP {response.status_code}")
        except Exception as e:
            self.log_result(f"{image_name} Accessibility", "FAIL", f"Exception: {str(e)}")

    def add_multiple_votes_to_trigger_approval(self):
        """Add multiple votes to a contribution to trigger auto-approval"""
        if not self.admin_token or not self.user_token:
            self.log_result("Multiple Votes Test", "SKIP", "Both admin and user authentication required")
            return False
            
        try:
            # Get pending contributions with images
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/contributions?status=pending", headers=headers)
            
            if response.status_code != 200:
                self.log_result("Multiple Votes Test", "FAIL", "Failed to fetch contributions")
                return False
            
            contributions = response.json()
            pending_with_images = [c for c in contributions if c.get('images') or c.get('logo') or c.get('secondary_photos')]
            
            if not pending_with_images:
                self.log_result("Multiple Votes Test", "WARN", "No pending contributions with images found")
                return False
            
            # Select a contribution that hasn't been voted on yet
            test_contribution = None
            for contrib in pending_with_images:
                if contrib.get('vote_score', 0) < 3:
                    test_contribution = contrib
                    break
            
            if not test_contribution:
                self.log_result("Multiple Votes Test", "WARN", "No suitable contribution found for voting test")
                return False
            
            contribution_id = test_contribution.get('id')
            current_score = test_contribution.get('vote_score', 0)
            
            self.log_result("Multiple Votes Setup", "INFO", 
                f"Testing multiple votes on contribution {contribution_id[:8]} (current score: {current_score})")
            
            # Add votes from different users (admin and user)
            votes_needed = max(1, 3 - current_score)
            
            for i in range(votes_needed):
                # Alternate between admin and user tokens
                token = self.admin_token if i % 2 == 0 else self.user_token
                user_type = "admin" if i % 2 == 0 else "user"
                
                vote_headers = {"Authorization": f"Bearer {token}"}
                vote_data = {
                    "vote_type": "upvote",
                    "reason": f"Testing vote #{i+1} from {user_type} to trigger auto-approval"
                }
                
                vote_response = requests.post(
                    f"{BACKEND_URL}/contributions/{contribution_id}/vote", 
                    json=vote_data, 
                    headers=vote_headers
                )
                
                if vote_response.status_code == 200:
                    vote_result = vote_response.json()
                    new_score = vote_result.get('contribution_score', 0)
                    self.log_result(f"Vote #{i+1} ({user_type})", "PASS", 
                        f"Vote successful - Score: {new_score}")
                    
                    if new_score >= 3:
                        self.log_result("Auto-Approval Threshold", "INFO", 
                            f"Score {new_score} >= 3 - Auto-approval should trigger")
                        break
                else:
                    self.log_result(f"Vote #{i+1} ({user_type})", "FAIL", 
                        f"Vote failed: HTTP {vote_response.status_code} - {vote_response.text}")
            
            # Wait for auto-approval to process
            import time
            time.sleep(5)
            
            # Check final status
            status_response = requests.get(f"{BACKEND_URL}/contributions/{contribution_id}", headers=headers)
            if status_response.status_code == 200:
                final_contribution = status_response.json()
                final_status = final_contribution.get('status', 'unknown')
                final_score = final_contribution.get('vote_score', 0)
                
                self.log_result("Final Contribution Status", "INFO", 
                    f"Status: {final_status}, Score: {final_score}")
                
                if final_status in ['approved', 'auto_approved']:
                    self.log_result("Auto-Approval Success", "PASS", 
                        f"Contribution successfully auto-approved!")
                    
                    # Check if images were applied
                    self.check_entity_images_after_approval(final_contribution)
                    return True
                else:
                    self.log_result("Auto-Approval Failure", "FAIL", 
                        f"Contribution not auto-approved despite score >= 3")
                    return False
            else:
                self.log_result("Final Status Check", "FAIL", 
                    f"Failed to check final status: HTTP {status_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Multiple Votes Test", "FAIL", f"Exception: {str(e)}")
            return False

    def run_comprehensive_approval_test(self):
        """Run comprehensive contribution approval testing"""
        print("🧪 TOPKIT CONTRIBUTION APPROVAL TESTING")
        print("=" * 80)
        print("Focus: Test contribution approval process and fix image application")
        print()
        
        # Authentication
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        
        if not admin_auth or not user_auth:
            print("❌ CRITICAL: Both admin and user authentication required")
            return False
        
        print("\n🗳️ CONTRIBUTION VOTING SYSTEM TEST")
        print("-" * 50)
        
        # Test voting system
        self.test_voting_system()
        
        print("\n🗳️ MULTIPLE VOTES FOR AUTO-APPROVAL TEST")
        print("-" * 50)
        
        # Test multiple votes to trigger auto-approval
        self.add_multiple_votes_to_trigger_approval()
        
        # Summary
        print("\n📊 APPROVAL TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warnings}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Check if we successfully applied images
        image_application_success = any(
            'Images Applied' in r['test'] and r['status'] == 'PASS' 
            for r in self.test_results
        )
        
        if image_application_success:
            print("\n🎉 SUCCESS: Images successfully applied to entities!")
            print("✅ Root cause identified and resolved:")
            print("   - Contributions with images were pending approval")
            print("   - Auto-approval requires vote_score >= 3")
            print("   - After voting, contributions are auto-approved")
            print("   - Images are successfully applied to main entities")
        else:
            print("\n🚨 ISSUE PERSISTS: Images still not applied to entities")
            print("❌ Further investigation needed in approval logic")
        
        return success_rate > 60

if __name__ == "__main__":
    tester = ContributionApprovalTester()
    success = tester.run_comprehensive_approval_test()
    
    if success:
        print("\n🎉 CONTRIBUTION APPROVAL TESTING COMPLETED SUCCESSFULLY")
    else:
        print("\n❌ CONTRIBUTION APPROVAL TESTING COMPLETED WITH ISSUES")
    
    sys.exit(0 if success else 1)