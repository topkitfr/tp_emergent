#!/usr/bin/env python3
"""
TopKit Contribution Approval Testing - FIXED VERSION
Focus: Test contribution approval process with correct API calls

FIXES:
1. Use query parameters for vote_type instead of JSON body
2. Test the actual voting and auto-approval workflow
3. Verify image application after approval
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com", 
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com",
    "password": "T0p_Mdp_1288*"
}

class ContributionApprovalFixedTester:
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

    def test_single_vote(self, contribution_id, token, user_type):
        """Test a single vote on a contribution"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Use query parameters for the vote
            params = {
                "vote_type": "upvote",
                "reason": f"Testing vote from {user_type} to trigger auto-approval"
            }
            
            vote_response = requests.post(
                f"{BACKEND_URL}/contributions/{contribution_id}/vote", 
                params=params,
                headers=headers
            )
            
            if vote_response.status_code == 200:
                vote_result = vote_response.json()
                new_score = vote_result.get('contribution_score', 0)
                self.log_result(f"Vote from {user_type}", "PASS", 
                    f"Vote successful - New score: {new_score}")
                return new_score
            else:
                self.log_result(f"Vote from {user_type}", "FAIL", 
                    f"Vote failed: HTTP {vote_response.status_code} - {vote_response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"Vote from {user_type}", "FAIL", f"Exception: {str(e)}")
            return None

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
                return False
            
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
                        self.log_result("🎉 Entity Images Applied", "PASS", 
                            f"SUCCESS! Images applied to {entity_type}: {', '.join(populated_fields)}")
                        
                        # Test if the image URLs are accessible
                        for field in populated_fields:
                            image_url = target_entity.get(field)
                            self.test_image_url_accessibility(image_url, f"{entity_type} {field}")
                        return True
                    else:
                        self.log_result("Entity Images Applied", "FAIL", 
                            f"CRITICAL: Approved contribution images NOT applied to {entity_type}")
                        return False
                else:
                    self.log_result("Entity Image Check", "FAIL", 
                        f"Entity {entity_id} not found in {entity_type} collection")
                    return False
            else:
                self.log_result("Entity Image Check", "FAIL", 
                    f"Failed to fetch {entity_type} collection: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Entity Image Check", "FAIL", f"Exception: {str(e)}")
            return False

    def test_image_url_accessibility(self, image_url, image_name):
        """Test if an image URL is accessible"""
        try:
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'image' in content_type:
                    self.log_result(f"✅ {image_name} Accessible", "PASS", 
                        f"Image URL working - Content-Type: {content_type}")
                else:
                    self.log_result(f"⚠️ {image_name} Accessible", "WARN", 
                        f"URL accessible but not an image - Content-Type: {content_type}")
            else:
                self.log_result(f"❌ {image_name} Accessible", "FAIL", 
                    f"Image URL not accessible - HTTP {response.status_code}")
        except Exception as e:
            self.log_result(f"❌ {image_name} Accessible", "FAIL", f"Exception: {str(e)}")

    def test_complete_approval_workflow(self):
        """Test the complete approval workflow for contributions with images"""
        if not self.admin_token or not self.user_token:
            self.log_result("Complete Workflow Test", "SKIP", "Both admin and user authentication required")
            return False
            
        try:
            # Get pending contributions with images
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/contributions?status=pending", headers=headers)
            
            if response.status_code != 200:
                self.log_result("Complete Workflow Test", "FAIL", "Failed to fetch contributions")
                return False
            
            contributions = response.json()
            pending_with_images = [c for c in contributions if c.get('images') or c.get('logo') or c.get('secondary_photos')]
            
            if not pending_with_images:
                self.log_result("Complete Workflow Test", "WARN", "No pending contributions with images found")
                return False
            
            # Select the first contribution with images
            test_contribution = pending_with_images[0]
            contribution_id = test_contribution.get('id')
            current_score = test_contribution.get('vote_score', 0)
            entity_type = test_contribution.get('entity_type', 'unknown')
            
            self.log_result("Workflow Test Setup", "INFO", 
                f"Testing complete workflow on {entity_type} contribution {contribution_id[:8]} (current score: {current_score})")
            
            # Add votes to reach auto-approval threshold (score >= 3)
            votes_needed = max(1, 3 - current_score)
            final_score = current_score
            
            for i in range(votes_needed):
                # Alternate between admin and user tokens to simulate different voters
                token = self.admin_token if i % 2 == 0 else self.user_token
                user_type = "admin" if i % 2 == 0 else "user"
                
                score = self.test_single_vote(contribution_id, token, user_type)
                if score is not None:
                    final_score = score
                    if final_score >= 3:
                        self.log_result("Auto-Approval Threshold Reached", "INFO", 
                            f"Score {final_score} >= 3 - Auto-approval should trigger")
                        break
                else:
                    self.log_result("Voting Failed", "WARN", f"Failed to vote with {user_type}")
            
            # Wait for auto-approval to process
            self.log_result("Auto-Approval Processing", "INFO", "Waiting 5 seconds for auto-approval...")
            import time
            time.sleep(5)
            
            # Check final contribution status
            status_response = requests.get(f"{BACKEND_URL}/contributions/{contribution_id}", headers=headers)
            if status_response.status_code == 200:
                final_contribution = status_response.json()
                final_status = final_contribution.get('status', 'unknown')
                final_score_check = final_contribution.get('vote_score', 0)
                
                self.log_result("Final Contribution Status", "INFO", 
                    f"Status: {final_status}, Score: {final_score_check}")
                
                if final_status in ['approved', 'auto_approved']:
                    self.log_result("🎉 Auto-Approval Success", "PASS", 
                        f"Contribution successfully auto-approved with status: {final_status}")
                    
                    # Check if images were applied to the entity
                    images_applied = self.check_entity_images_after_approval(final_contribution)
                    
                    if images_applied:
                        self.log_result("🎉 COMPLETE SUCCESS", "PASS", 
                            "Images successfully applied to entity after approval!")
                        return True
                    else:
                        self.log_result("❌ Image Application Failed", "FAIL", 
                            "Contribution approved but images not applied to entity")
                        return False
                else:
                    self.log_result("❌ Auto-Approval Failed", "FAIL", 
                        f"Contribution not auto-approved despite score {final_score_check}")
                    return False
            else:
                self.log_result("Final Status Check Failed", "FAIL", 
                    f"Failed to check final status: HTTP {status_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Complete Workflow Test", "FAIL", f"Exception: {str(e)}")
            return False

    def run_fixed_approval_test(self):
        """Run the fixed contribution approval test"""
        print("🔧 TOPKIT CONTRIBUTION APPROVAL TESTING - FIXED VERSION")
        print("=" * 80)
        print("Focus: Test complete approval workflow with correct API calls")
        print()
        
        # Authentication
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        
        if not admin_auth or not user_auth:
            print("❌ CRITICAL: Both admin and user authentication required")
            return False
        
        print("\n🔄 COMPLETE APPROVAL WORKFLOW TEST")
        print("-" * 50)
        
        # Test complete workflow
        workflow_success = self.test_complete_approval_workflow()
        
        # Summary
        print("\n📊 FIXED APPROVAL TEST SUMMARY")
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
        
        # Final conclusion
        print("\n🎯 FINAL CONCLUSION")
        print("-" * 30)
        
        if workflow_success:
            print("🎉 ROOT CAUSE IDENTIFIED AND RESOLVED!")
            print("✅ Issue: Contributions with images were pending approval")
            print("✅ Solution: Vote on contributions to trigger auto-approval (score >= 3)")
            print("✅ Result: Images successfully applied to main entities")
            print("✅ Cards should now display actual uploaded images instead of default icons")
        else:
            print("🚨 ISSUE STILL PERSISTS")
            print("❌ Further investigation needed in the approval/application logic")
            print("❌ Images may not be properly applied to entities after approval")
        
        return workflow_success

if __name__ == "__main__":
    tester = ContributionApprovalFixedTester()
    success = tester.run_fixed_approval_test()
    
    if success:
        print("\n🎉 IMAGE DISPLAY ISSUE RESOLVED!")
        print("Cards should now show actual uploaded images instead of default icons.")
    else:
        print("\n❌ IMAGE DISPLAY ISSUE PERSISTS")
        print("Additional backend fixes may be required.")
    
    sys.exit(0 if success else 1)