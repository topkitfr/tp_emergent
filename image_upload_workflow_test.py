#!/usr/bin/env python3
"""
TopKit Image Upload Workflow Testing - Complete End-to-End Testing
================================================================

OBJECTIF: Tester le processus complet d'images : soumission utilisateur → correction admin → approbation → affichage explorateur

WORKFLOW À TESTER:
1. **SOUMISSION UTILISATEUR**: 
   - Connecter un utilisateur normal (steinmetzlivio@gmail.com/TopKit123!)
   - Soumettre un nouveau maillot avec de vraies images uploadées
   - Vérifier que les images sont sauvegardées sur le serveur

2. **CORRECTION ADMIN**:
   - Connecter l'admin (topkitfr@gmail.com/TopKitSecure789#)
   - Récupérer le maillot soumis en mode "pending"
   - Vérifier que l'admin peut voir les images uploadées par l'utilisateur
   - Tester le remplacement d'images par l'admin si nécessaire

3. **APPROBATION ET EXPLORATEUR**:
   - Approuver le maillot avec les images
   - Vérifier que les images apparaissent dans /api/jerseys/approved
   - Confirmer la visibilité dans l'explorateur

FOCUS: Identifier où le workflow se casse et corriger chaque étape pour assurer un processus fluide d'upload d'images.
"""

import requests
import json
import os
import io
from datetime import datetime
import uuid
from PIL import Image

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"
USER_EMAIL = "testuser.images@gmail.com"
USER_PASSWORD = "SecureTestPass789!"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImageUploadWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        self.test_jersey_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def create_test_image(self, filename, color=(255, 0, 0), size=(300, 300)):
        """Create a test image in memory"""
        try:
            # Create a colored image
            img = Image.new('RGB', size, color)
            
            # Save to bytes buffer
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None
    
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                
                user_info = data.get('user', {})
                self.log_test("User Authentication", True, 
                            f"User: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}")
                return True
            else:
                self.log_test("User Authentication", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                
                user_info = data.get('user', {})
                self.log_test("Admin Authentication", True, 
                            f"Admin: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def submit_jersey_with_images(self):
        """Submit a jersey with real image uploads as user"""
        try:
            # Set user authorization
            headers = {'Authorization': f'Bearer {self.user_token}'}
            
            # Create test images
            front_image = self.create_test_image("front_test.jpg", color=(0, 100, 200))  # Blue
            back_image = self.create_test_image("back_test.jpg", color=(200, 0, 100))   # Red
            
            if not front_image or not back_image:
                self.log_test("Submit Jersey with Images", False, "Failed to create test images")
                return None
            
            # Prepare form data
            form_data = {
                'team': 'Paris Saint-Germain Test Upload',
                'league': 'Ligue 1',
                'season': '2024/25',
                'manufacturer': 'Nike',
                'jersey_type': 'home',
                'sku_code': 'PSG-TEST-IMG-001',
                'model': 'authentic',
                'description': 'Maillot de test pour workflow complet upload images - Mbappé #7'
            }
            
            # Prepare files
            files = {
                'front_photo': ('front_test.jpg', front_image, 'image/jpeg'),
                'back_photo': ('back_test.jpg', back_image, 'image/jpeg')
            }
            
            response = requests.post(f"{BACKEND_URL}/jerseys", 
                                   data=form_data, 
                                   files=files, 
                                   headers=headers)
            
            if response.status_code == 200:
                jersey = response.json()
                self.test_jersey_id = jersey.get('id')
                
                self.log_test("Submit Jersey with Images", True,
                            f"Jersey ID: {self.test_jersey_id}, Team: {jersey.get('team')}, Status: {jersey.get('status')}, Ref: {jersey.get('reference_number')}")
                
                # Check if images were saved
                front_url = jersey.get('front_photo_url')
                back_url = jersey.get('back_photo_url')
                
                if front_url or back_url:
                    print(f"   Front Photo URL: {front_url}")
                    print(f"   Back Photo URL: {back_url}")
                
                return self.test_jersey_id
            else:
                self.log_test("Submit Jersey with Images", False,
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Submit Jersey with Images", False, f"Exception: {str(e)}")
            return None
    
    def verify_images_saved_on_server(self):
        """Verify that uploaded images are accessible on server"""
        try:
            if not self.test_jersey_id:
                self.log_test("Verify Images Saved on Server", False, "No test jersey ID available")
                return False
            
            # Get jersey details to check image URLs
            headers = {'Authorization': f'Bearer {self.user_token}'}
            response = requests.get(f"{BACKEND_URL}/jerseys/{self.test_jersey_id}", headers=headers)
            
            if response.status_code == 200:
                jersey = response.json()
                front_url = jersey.get('front_photo_url')
                back_url = jersey.get('back_photo_url')
                
                images_accessible = 0
                total_images = 0
                
                # Test front image accessibility
                if front_url:
                    total_images += 1
                    try:
                        # Try to access the image URL
                        if front_url.startswith('/'):
                            # Relative URL - construct full URL
                            full_url = f"https://kit-collection-5.preview.emergentagent.com{front_url}"
                        else:
                            full_url = front_url
                        
                        img_response = requests.get(full_url, timeout=10)
                        if img_response.status_code == 200:
                            images_accessible += 1
                            print(f"   Front image accessible: {full_url}")
                        else:
                            print(f"   Front image not accessible: {full_url} (HTTP {img_response.status_code})")
                    except Exception as e:
                        print(f"   Front image access error: {e}")
                
                # Test back image accessibility
                if back_url:
                    total_images += 1
                    try:
                        # Try to access the image URL
                        if back_url.startswith('/'):
                            # Relative URL - construct full URL
                            full_url = f"https://kit-collection-5.preview.emergentagent.com{back_url}"
                        else:
                            full_url = back_url
                        
                        img_response = requests.get(full_url, timeout=10)
                        if img_response.status_code == 200:
                            images_accessible += 1
                            print(f"   Back image accessible: {full_url}")
                        else:
                            print(f"   Back image not accessible: {full_url} (HTTP {img_response.status_code})")
                    except Exception as e:
                        print(f"   Back image access error: {e}")
                
                success = images_accessible > 0
                self.log_test("Verify Images Saved on Server", success,
                            f"Images accessible: {images_accessible}/{total_images}")
                return success
            else:
                self.log_test("Verify Images Saved on Server", False,
                            f"Could not get jersey details - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Verify Images Saved on Server", False, f"Exception: {str(e)}")
            return False
    
    def admin_retrieve_pending_jersey(self):
        """Admin retrieves the submitted jersey in pending status"""
        try:
            # Set admin authorization
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                
                # Find our test jersey
                test_jersey = None
                for jersey in pending_jerseys:
                    if jersey.get('id') == self.test_jersey_id:
                        test_jersey = jersey
                        break
                
                if test_jersey:
                    self.log_test("Admin Retrieve Pending Jersey", True,
                                f"Found test jersey in pending list - Team: {test_jersey.get('team')}, Status: {test_jersey.get('status')}")
                    
                    # Check if admin can see the uploaded images
                    front_url = test_jersey.get('front_photo_url')
                    back_url = test_jersey.get('back_photo_url')
                    
                    if front_url or back_url:
                        print(f"   Admin can see front photo: {front_url}")
                        print(f"   Admin can see back photo: {back_url}")
                    else:
                        print(f"   No image URLs visible to admin")
                    
                    return True
                else:
                    self.log_test("Admin Retrieve Pending Jersey", False,
                                f"Test jersey {self.test_jersey_id} not found in pending list")
                    return False
            else:
                self.log_test("Admin Retrieve Pending Jersey", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Retrieve Pending Jersey", False, f"Exception: {str(e)}")
            return False
    
    def admin_replace_images(self):
        """Admin replaces/corrects images on the jersey"""
        try:
            if not self.test_jersey_id:
                self.log_test("Admin Replace Images", False, "No test jersey ID available")
                return False
            
            # Set admin authorization
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            # Create new test images for admin correction
            new_front_image = self.create_test_image("admin_front.jpg", color=(0, 200, 0))  # Green
            new_back_image = self.create_test_image("admin_back.jpg", color=(200, 200, 0))  # Yellow
            
            if not new_front_image or not new_back_image:
                self.log_test("Admin Replace Images", False, "Failed to create admin correction images")
                return False
            
            # Prepare form data for admin edit
            form_data = {
                'team': 'Paris Saint-Germain Test Upload (Admin Corrected)',
                'league': 'Ligue 1',
                'season': '2024/25',
                'manufacturer': 'Nike',
                'jersey_type': 'home',
                'sku_code': 'PSG-TEST-IMG-001-CORRECTED',
                'model': 'authentic',
                'description': 'Maillot de test pour workflow complet upload images - Mbappé #7 - Images corrigées par admin'
            }
            
            # Prepare files for replacement
            files = {
                'front_photo': ('admin_front.jpg', new_front_image, 'image/jpeg'),
                'back_photo': ('admin_back.jpg', new_back_image, 'image/jpeg')
            }
            
            response = requests.put(f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}/edit", 
                                  data=form_data, 
                                  files=files, 
                                  headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Admin Replace Images", True,
                            f"Admin successfully replaced images - Message: {result.get('message')}")
                
                # Check photos_uploaded count
                photos_uploaded = result.get('photos_uploaded', 0)
                print(f"   Photos uploaded count: {photos_uploaded}")
                
                return True
            else:
                self.log_test("Admin Replace Images", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Replace Images", False, f"Exception: {str(e)}")
            return False
    
    def admin_approve_jersey(self):
        """Admin approves the jersey with images"""
        try:
            if not self.test_jersey_id:
                self.log_test("Admin Approve Jersey", False, "No test jersey ID available")
                return False
            
            # Set admin authorization
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = requests.post(f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}/approve", 
                                   headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Admin Approve Jersey", True,
                            f"Jersey approved successfully - Message: {result.get('message')}")
                return True
            else:
                self.log_test("Admin Approve Jersey", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Approve Jersey", False, f"Exception: {str(e)}")
            return False
    
    def verify_approved_jersey_in_explorer(self):
        """Verify that approved jersey with images appears in explorer"""
        try:
            # Check approved jerseys endpoint
            response = requests.get(f"{BACKEND_URL}/jerseys/approved")
            
            if response.status_code == 200:
                approved_jerseys = response.json()
                
                # Find our test jersey
                test_jersey = None
                for jersey in approved_jerseys:
                    if jersey.get('id') == self.test_jersey_id:
                        test_jersey = jersey
                        break
                
                if test_jersey:
                    self.log_test("Verify Approved Jersey in Explorer", True,
                                f"Test jersey found in approved list - Team: {test_jersey.get('team')}, Status: {test_jersey.get('status')}")
                    
                    # Check if images are visible in explorer
                    front_url = test_jersey.get('front_photo_url')
                    back_url = test_jersey.get('back_photo_url')
                    images_array = test_jersey.get('images', [])
                    
                    if front_url or back_url or images_array:
                        print(f"   Explorer shows front photo: {front_url}")
                        print(f"   Explorer shows back photo: {back_url}")
                        print(f"   Explorer shows images array: {images_array}")
                        return True
                    else:
                        print(f"   No images visible in explorer")
                        return False
                else:
                    self.log_test("Verify Approved Jersey in Explorer", False,
                                f"Test jersey {self.test_jersey_id} not found in approved list")
                    return False
            else:
                self.log_test("Verify Approved Jersey in Explorer", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Approved Jersey in Explorer", False, f"Exception: {str(e)}")
            return False
    
    def test_explorer_jersey_endpoint(self):
        """Test the main explorer jersey endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                all_jerseys = response.json()
                
                # Find our test jersey
                test_jersey = None
                for jersey in all_jerseys:
                    if jersey.get('id') == self.test_jersey_id:
                        test_jersey = jersey
                        break
                
                if test_jersey:
                    self.log_test("Test Explorer Jersey Endpoint", True,
                                f"Test jersey visible in main explorer - Team: {test_jersey.get('team')}")
                    
                    # Check image visibility
                    front_url = test_jersey.get('front_photo_url')
                    back_url = test_jersey.get('back_photo_url')
                    
                    if front_url or back_url:
                        print(f"   Main explorer shows images: Front={bool(front_url)}, Back={bool(back_url)}")
                    
                    return True
                else:
                    self.log_test("Test Explorer Jersey Endpoint", False,
                                f"Test jersey not visible in main explorer")
                    return False
            else:
                self.log_test("Test Explorer Jersey Endpoint", False,
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test Explorer Jersey Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_complete_workflow_test(self):
        """Run the complete image upload workflow test"""
        print("🎯 TOPKIT IMAGE UPLOAD WORKFLOW TESTING STARTED")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"User Email: {USER_EMAIL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # PHASE 1: USER SUBMISSION
        print("\n📤 PHASE 1: USER SUBMISSION WITH IMAGE UPLOAD")
        print("-" * 50)
        
        if not self.authenticate_user():
            print("❌ CRITICAL: User authentication failed. Cannot proceed with workflow.")
            return
        
        if not self.submit_jersey_with_images():
            print("❌ CRITICAL: Jersey submission with images failed. Cannot proceed with workflow.")
            return
        
        self.verify_images_saved_on_server()
        
        # PHASE 2: ADMIN CORRECTION
        print("\n🔧 PHASE 2: ADMIN CORRECTION AND IMAGE MANAGEMENT")
        print("-" * 50)
        
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with admin workflow.")
            return
        
        self.admin_retrieve_pending_jersey()
        self.admin_replace_images()
        
        # PHASE 3: APPROVAL AND EXPLORER
        print("\n✅ PHASE 3: APPROVAL AND EXPLORER VISIBILITY")
        print("-" * 50)
        
        self.admin_approve_jersey()
        self.verify_approved_jersey_in_explorer()
        self.test_explorer_jersey_endpoint()
        
        # Calculate success rate
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print(f"🎉 TOPKIT IMAGE UPLOAD WORKFLOW TESTING COMPLETE - {success_rate:.1f}% SUCCESS RATE!")
        print("=" * 80)
        
        # Print detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n📊 SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Workflow analysis
        print("\n🔍 WORKFLOW ANALYSIS:")
        
        # Check each phase
        user_auth_success = any(r['test'] == 'User Authentication' and r['success'] for r in self.test_results)
        image_submit_success = any(r['test'] == 'Submit Jersey with Images' and r['success'] for r in self.test_results)
        admin_auth_success = any(r['test'] == 'Admin Authentication' and r['success'] for r in self.test_results)
        admin_retrieve_success = any(r['test'] == 'Admin Retrieve Pending Jersey' and r['success'] for r in self.test_results)
        admin_replace_success = any(r['test'] == 'Admin Replace Images' and r['success'] for r in self.test_results)
        approval_success = any(r['test'] == 'Admin Approve Jersey' and r['success'] for r in self.test_results)
        explorer_success = any(r['test'] == 'Verify Approved Jersey in Explorer' and r['success'] for r in self.test_results)
        
        print(f"✅ User Authentication: {'WORKING' if user_auth_success else 'BROKEN'}")
        print(f"✅ Image Upload Submission: {'WORKING' if image_submit_success else 'BROKEN'}")
        print(f"✅ Admin Authentication: {'WORKING' if admin_auth_success else 'BROKEN'}")
        print(f"✅ Admin Retrieve Pending: {'WORKING' if admin_retrieve_success else 'BROKEN'}")
        print(f"✅ Admin Image Replacement: {'WORKING' if admin_replace_success else 'BROKEN'}")
        print(f"✅ Jersey Approval: {'WORKING' if approval_success else 'BROKEN'}")
        print(f"✅ Explorer Visibility: {'WORKING' if explorer_success else 'BROKEN'}")
        
        # Identify where workflow breaks
        if not user_auth_success:
            print("\n🚨 WORKFLOW BREAKS AT: User Authentication")
        elif not image_submit_success:
            print("\n🚨 WORKFLOW BREAKS AT: Image Upload Submission")
        elif not admin_auth_success:
            print("\n🚨 WORKFLOW BREAKS AT: Admin Authentication")
        elif not admin_retrieve_success:
            print("\n🚨 WORKFLOW BREAKS AT: Admin Retrieve Pending Jersey")
        elif not admin_replace_success:
            print("\n🚨 WORKFLOW BREAKS AT: Admin Image Replacement")
        elif not approval_success:
            print("\n🚨 WORKFLOW BREAKS AT: Jersey Approval")
        elif not explorer_success:
            print("\n🚨 WORKFLOW BREAKS AT: Explorer Visibility")
        else:
            print("\n🎉 COMPLETE WORKFLOW: WORKING END-TO-END!")
        
        if success_rate >= 85:
            print("\n🎉 CONCLUSION: Image upload workflow is PRODUCTION-READY!")
        else:
            print("\n⚠️ CONCLUSION: Image upload workflow has issues that need attention.")
        
        return success_rate

if __name__ == "__main__":
    tester = ImageUploadWorkflowTester()
    tester.run_complete_workflow_test()