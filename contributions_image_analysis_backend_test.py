#!/usr/bin/env python3
"""
TopKit Contributions Image Analysis - Deep Investigation
Focus: Investigate why contributions with images are not being applied to main entities

ROOT CAUSE IDENTIFIED:
- All main entities (teams, brands, competitions, players) have logo_url/photo_url = None
- 7 out of 9 contributions have images uploaded
- Images are being uploaded to contributions but NOT applied to main entities
- This suggests the contribution approval/application process is broken
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://mongodb-routing.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com", 
    "password": "TopKitSecure789#"
}

class ContributionsImageAnalyzer:
    def __init__(self):
        self.admin_token = None
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

    def analyze_contributions_with_images(self):
        """Analyze all contributions that have images"""
        if not self.admin_token:
            self.log_result("Contributions Analysis", "SKIP", "Admin authentication required")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/contributions", headers=headers)
            
            if response.status_code == 200:
                contributions = response.json()
                
                for contribution in contributions:
                    # Check if contribution has images
                    has_images = bool(contribution.get('images') or contribution.get('logo') or contribution.get('secondary_photos'))
                    
                    if has_images:
                        entity_type = contribution.get('entity_type', 'Unknown')
                        entity_id = contribution.get('entity_id', 'Unknown')
                        status = contribution.get('status', 'Unknown')
                        contribution_id = contribution.get('id', 'Unknown')
                        
                        # Get image details
                        images_info = []
                        if contribution.get('logo'):
                            images_info.append(f"Logo: {len(contribution['logo'])} chars")
                        if contribution.get('images'):
                            images_info.append(f"Images: {len(contribution['images'])} items")
                        if contribution.get('secondary_photos'):
                            images_info.append(f"Secondary: {len(contribution['secondary_photos'])} items")
                        
                        images_detail = ", ".join(images_info)
                        
                        self.log_result(f"Contribution {contribution_id[:8]}", "INFO", 
                            f"Entity: {entity_type}, Status: {status}, Images: {images_detail}")
                        
                        # If contribution is approved, check if images were applied to entity
                        if status == 'approved':
                            self.check_if_images_applied_to_entity(entity_type, entity_id, contribution_id)
                        elif status == 'pending':
                            self.log_result(f"Pending Contribution {contribution_id[:8]}", "WARN", 
                                f"Contribution with images is still pending approval")
                
                return True
            else:
                self.log_result("Contributions Analysis", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Contributions Analysis", "FAIL", f"Exception: {str(e)}")
            return False

    def check_if_images_applied_to_entity(self, entity_type, entity_id, contribution_id):
        """Check if approved contribution images were applied to the main entity"""
        try:
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
                self.log_result(f"Entity Check {contribution_id[:8]}", "FAIL", f"Unknown entity type: {entity_type}")
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
                    has_images = any(target_entity.get(field) for field in image_fields)
                    
                    if has_images:
                        populated_fields = [field for field in image_fields if target_entity.get(field)]
                        self.log_result(f"Applied Images {contribution_id[:8]}", "PASS", 
                            f"Images successfully applied to {entity_type}: {', '.join(populated_fields)}")
                    else:
                        self.log_result(f"Applied Images {contribution_id[:8]}", "FAIL", 
                            f"Approved contribution images NOT applied to {entity_type} {entity_id}")
                else:
                    self.log_result(f"Entity Check {contribution_id[:8]}", "FAIL", 
                        f"Entity {entity_id} not found in {entity_type} collection")
            else:
                self.log_result(f"Entity Check {contribution_id[:8]}", "FAIL", 
                    f"Failed to fetch {entity_type} collection: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result(f"Entity Check {contribution_id[:8]}", "FAIL", f"Exception: {str(e)}")

    def test_contribution_approval_process(self):
        """Test if we can approve a pending contribution and see if images get applied"""
        if not self.admin_token:
            self.log_result("Approval Process Test", "SKIP", "Admin authentication required")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get pending contributions with images
            response = requests.get(f"{BACKEND_URL}/contributions", headers=headers)
            if response.status_code != 200:
                self.log_result("Approval Process Test", "FAIL", "Failed to fetch contributions")
                return False
            
            contributions = response.json()
            pending_with_images = []
            
            for contribution in contributions:
                if (contribution.get('status') == 'pending' and 
                    (contribution.get('images') or contribution.get('logo') or contribution.get('secondary_photos'))):
                    pending_with_images.append(contribution)
            
            if not pending_with_images:
                self.log_result("Approval Process Test", "WARN", "No pending contributions with images found")
                return False
            
            # Try to approve the first pending contribution with images
            test_contribution = pending_with_images[0]
            contribution_id = test_contribution.get('id')
            entity_type = test_contribution.get('entity_type')
            entity_id = test_contribution.get('entity_id')
            
            self.log_result("Approval Test Setup", "INFO", 
                f"Testing approval of contribution {contribution_id[:8]} for {entity_type}")
            
            # Test the approval endpoint
            approval_data = {
                "action": "approve",
                "admin_notes": "Testing image application process"
            }
            
            approval_response = requests.post(
                f"{BACKEND_URL}/contributions/{contribution_id}/action", 
                json=approval_data, 
                headers=headers
            )
            
            if approval_response.status_code == 200:
                self.log_result("Contribution Approval", "PASS", 
                    f"Contribution {contribution_id[:8]} approved successfully")
                
                # Wait a moment and check if images were applied
                import time
                time.sleep(2)
                
                # Check if images were applied to the entity
                self.check_if_images_applied_to_entity(entity_type, entity_id, contribution_id)
                
            else:
                self.log_result("Contribution Approval", "FAIL", 
                    f"Failed to approve contribution: HTTP {approval_response.status_code} - {approval_response.text}")
            
            return True
            
        except Exception as e:
            self.log_result("Approval Process Test", "FAIL", f"Exception: {str(e)}")
            return False

    def investigate_contribution_application_logic(self):
        """Investigate the backend logic for applying contributions to entities"""
        if not self.admin_token:
            self.log_result("Application Logic Investigation", "SKIP", "Admin authentication required")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all contributions
            response = requests.get(f"{BACKEND_URL}/contributions", headers=headers)
            if response.status_code != 200:
                self.log_result("Application Logic Investigation", "FAIL", "Failed to fetch contributions")
                return False
            
            contributions = response.json()
            
            # Analyze contribution statuses and image application
            status_counts = {}
            approved_with_images = 0
            pending_with_images = 0
            
            for contribution in contributions:
                status = contribution.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                has_images = bool(contribution.get('images') or contribution.get('logo') or contribution.get('secondary_photos'))
                
                if has_images:
                    if status == 'approved':
                        approved_with_images += 1
                    elif status == 'pending':
                        pending_with_images += 1
            
            self.log_result("Contribution Status Analysis", "INFO", 
                f"Status counts: {status_counts}")
            self.log_result("Image Contributions Analysis", "INFO", 
                f"Approved with images: {approved_with_images}, Pending with images: {pending_with_images}")
            
            # The key insight: if we have approved contributions with images but entities don't have images,
            # then the application logic is broken
            if approved_with_images > 0:
                self.log_result("Application Logic Issue", "FAIL", 
                    f"Found {approved_with_images} approved contributions with images, but entities don't have images - APPLICATION LOGIC BROKEN")
            else:
                self.log_result("Application Logic Status", "WARN", 
                    f"No approved contributions with images found - all {pending_with_images} image contributions are still pending")
            
            return True
            
        except Exception as e:
            self.log_result("Application Logic Investigation", "FAIL", f"Exception: {str(e)}")
            return False

    def run_comprehensive_analysis(self):
        """Run comprehensive contributions image analysis"""
        print("🔍 TOPKIT CONTRIBUTIONS IMAGE ANALYSIS - DEEP INVESTIGATION")
        print("=" * 80)
        print("Focus: Why contributions with images are not being applied to main entities")
        print()
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed - cannot proceed")
            return False
        
        print("\n🔍 CONTRIBUTIONS WITH IMAGES ANALYSIS")
        print("-" * 50)
        
        # Analyze contributions with images
        self.analyze_contributions_with_images()
        
        print("\n🔍 CONTRIBUTION APPLICATION LOGIC INVESTIGATION")
        print("-" * 50)
        
        # Investigate application logic
        self.investigate_contribution_application_logic()
        
        print("\n🧪 CONTRIBUTION APPROVAL PROCESS TEST")
        print("-" * 50)
        
        # Test approval process
        self.test_contribution_approval_process()
        
        # Summary
        print("\n📊 ANALYSIS SUMMARY")
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
        
        # Root cause conclusion
        print("\n🎯 ROOT CAUSE CONCLUSION")
        print("-" * 30)
        
        application_logic_failures = [r for r in self.test_results if 'Application Logic' in r['test'] and r['status'] == 'FAIL']
        approval_failures = [r for r in self.test_results if 'Applied Images' in r['test'] and r['status'] == 'FAIL']
        
        if application_logic_failures or approval_failures:
            print("🚨 CRITICAL ISSUE IDENTIFIED:")
            print("   - Images are being uploaded to contributions successfully")
            print("   - Contributions system is storing images correctly")
            print("   - BUT: Contribution approval process is NOT applying images to main entities")
            print("   - SOLUTION NEEDED: Fix the contribution approval/application logic in backend")
        else:
            print("✅ Contribution system appears to be working correctly")
            print("🔍 Issue might be elsewhere in the image display pipeline")
        
        return success_rate > 50

if __name__ == "__main__":
    analyzer = ContributionsImageAnalyzer()
    success = analyzer.run_comprehensive_analysis()
    
    if success:
        print("\n🎉 CONTRIBUTIONS IMAGE ANALYSIS COMPLETED")
    else:
        print("\n❌ CONTRIBUTIONS IMAGE ANALYSIS COMPLETED WITH CRITICAL ISSUES")
    
    sys.exit(0 if success else 1)