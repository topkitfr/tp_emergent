#!/usr/bin/env python3
"""
TopKit Backend Testing - Jersey Photos for Explorer
Test script to verify that approved jerseys have photos for display in the explorer.

OBJECTIF: Vérifier que l'API qui fournit les maillots à l'explorateur retourne bien les photos.

TESTS À EFFECTUER:
1. GET /api/jerseys - Récupérer les maillots approuvés qui sont affichés dans l'explorateur
2. Vérifier la structure des données : 
   - Champ "images" (array)
   - Champs "front_photo_url" et "back_photo_url"
3. Analyser quelques maillots spécifiques pour s'assurer qu'ils ont des photos
4. Si nécessaire, approuver quelques maillots de test pour avoir des données dans l'explorateur

FOCUS: S'assurer que l'explorateur a des maillots avec photos à afficher après mes corrections frontend.
"""

import requests
import json
import sys
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

class JerseyPhotoTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.jerseys_with_photos = []
        self.jerseys_without_photos = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Admin authenticated successfully: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})",
                    {"user_id": user_info.get("id"), "email": user_info.get("email")}
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Admin authentication failed: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Admin authentication error: {str(e)}")
            return False
    
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.log_result(
                    "User Authentication",
                    True,
                    f"User authenticated successfully: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})",
                    {"user_id": user_info.get("id"), "email": user_info.get("email")}
                )
                return True
            else:
                self.log_result(
                    "User Authentication",
                    False,
                    f"User authentication failed: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"User authentication error: {str(e)}")
            return False
    
    def get_approved_jerseys(self):
        """Get approved jerseys from the explorer API"""
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                approved_jerseys = [j for j in jerseys if j.get('status') == 'approved']
                
                self.log_result(
                    "Get Approved Jerseys",
                    True,
                    f"Retrieved {len(approved_jerseys)} approved jerseys out of {len(jerseys)} total jerseys",
                    {
                        "total_jerseys": len(jerseys),
                        "approved_jerseys": len(approved_jerseys),
                        "jersey_statuses": [j.get('status') for j in jerseys]
                    }
                )
                return approved_jerseys
            else:
                self.log_result(
                    "Get Approved Jerseys",
                    False,
                    f"Failed to retrieve jerseys: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return []
                
        except Exception as e:
            self.log_result("Get Approved Jerseys", False, f"Error retrieving jerseys: {str(e)}")
            return []
    
    def analyze_jersey_photo_structure(self, jerseys):
        """Analyze the photo structure of jerseys"""
        if not jerseys:
            self.log_result(
                "Jersey Photo Structure Analysis",
                False,
                "No jerseys to analyze"
            )
            return
        
        # Analyze first jersey structure
        sample_jersey = jerseys[0]
        has_images_field = 'images' in sample_jersey
        has_front_photo = 'front_photo_url' in sample_jersey
        has_back_photo = 'back_photo_url' in sample_jersey
        
        structure_details = {
            "sample_jersey_id": sample_jersey.get('id'),
            "sample_jersey_team": sample_jersey.get('team'),
            "has_images_field": has_images_field,
            "has_front_photo_url": has_front_photo,
            "has_back_photo_url": has_back_photo,
            "images_value": sample_jersey.get('images') if has_images_field else None,
            "front_photo_value": sample_jersey.get('front_photo_url') if has_front_photo else None,
            "back_photo_value": sample_jersey.get('back_photo_url') if has_back_photo else None,
            "all_fields": list(sample_jersey.keys())
        }
        
        success = has_front_photo or has_back_photo or has_images_field
        
        self.log_result(
            "Jersey Photo Structure Analysis",
            success,
            f"Photo fields analysis: images={has_images_field}, front_photo_url={has_front_photo}, back_photo_url={has_back_photo}",
            structure_details
        )
    
    def analyze_jerseys_with_photos(self, jerseys):
        """Analyze which jerseys have photos and which don't"""
        jerseys_with_photos = []
        jerseys_without_photos = []
        
        for jersey in jerseys:
            jersey_id = jersey.get('id', 'unknown')
            team = jersey.get('team', 'Unknown Team')
            
            # Check for photos
            has_front_photo = jersey.get('front_photo_url') is not None and jersey.get('front_photo_url') != ""
            has_back_photo = jersey.get('back_photo_url') is not None and jersey.get('back_photo_url') != ""
            has_images = jersey.get('images') and len(jersey.get('images', [])) > 0
            
            jersey_info = {
                "id": jersey_id,
                "team": team,
                "season": jersey.get('season', 'Unknown'),
                "reference_number": jersey.get('reference_number', 'Unknown'),
                "has_front_photo": has_front_photo,
                "has_back_photo": has_back_photo,
                "has_images": has_images,
                "front_photo_url": jersey.get('front_photo_url'),
                "back_photo_url": jersey.get('back_photo_url'),
                "images": jersey.get('images', [])
            }
            
            if has_front_photo or has_back_photo or has_images:
                jerseys_with_photos.append(jersey_info)
            else:
                jerseys_without_photos.append(jersey_info)
        
        self.jerseys_with_photos = jerseys_with_photos
        self.jerseys_without_photos = jerseys_without_photos
        
        success = len(jerseys_with_photos) > 0
        
        self.log_result(
            "Jersey Photo Analysis",
            success,
            f"Found {len(jerseys_with_photos)} jerseys WITH photos and {len(jerseys_without_photos)} jerseys WITHOUT photos",
            {
                "jerseys_with_photos": len(jerseys_with_photos),
                "jerseys_without_photos": len(jerseys_without_photos),
                "with_photos_details": jerseys_with_photos[:3],  # Show first 3
                "without_photos_details": jerseys_without_photos[:3]  # Show first 3
            }
        )
        
        return success
    
    def get_pending_jerseys(self):
        """Get pending jerseys that could be approved for testing"""
        if not self.admin_token:
            self.log_result(
                "Get Pending Jerseys",
                False,
                "Admin token required to get pending jerseys"
            )
            return []
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                self.log_result(
                    "Get Pending Jerseys",
                    True,
                    f"Retrieved {len(pending_jerseys)} pending jerseys",
                    {"pending_count": len(pending_jerseys)}
                )
                return pending_jerseys
            else:
                self.log_result(
                    "Get Pending Jerseys",
                    False,
                    f"Failed to retrieve pending jerseys: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return []
                
        except Exception as e:
            self.log_result("Get Pending Jerseys", False, f"Error retrieving pending jerseys: {str(e)}")
            return []
    
    def approve_jersey_for_testing(self, jersey_id):
        """Approve a jersey for testing purposes"""
        if not self.admin_token:
            self.log_result(
                "Approve Jersey for Testing",
                False,
                "Admin token required to approve jerseys"
            )
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/admin/jerseys/{jersey_id}/approve", headers=headers)
            
            if response.status_code == 200:
                self.log_result(
                    "Approve Jersey for Testing",
                    True,
                    f"Successfully approved jersey {jersey_id}",
                    {"jersey_id": jersey_id}
                )
                return True
            else:
                self.log_result(
                    "Approve Jersey for Testing",
                    False,
                    f"Failed to approve jersey {jersey_id}: HTTP {response.status_code}",
                    {"jersey_id": jersey_id, "response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result("Approve Jersey for Testing", False, f"Error approving jersey {jersey_id}: {str(e)}")
            return False
    
    def create_test_jersey_with_photos(self):
        """Create a test jersey with photos for testing"""
        if not self.user_token:
            self.log_result(
                "Create Test Jersey",
                False,
                "User token required to create test jersey"
            )
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Create a test jersey
            jersey_data = {
                "team": "FC Barcelona",
                "league": "La Liga",
                "season": "24/25",
                "manufacturer": "Nike",
                "jersey_type": "home",
                "model": "authentic",
                "description": "Test jersey for photo verification - FC Barcelona home kit 24/25"
            }
            
            response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                jersey_info = response.json()
                jersey_id = jersey_info.get('id') or jersey_info.get('jersey_id')
                
                self.log_result(
                    "Create Test Jersey",
                    True,
                    f"Successfully created test jersey: {jersey_info.get('reference_number', jersey_id)}",
                    {"jersey_id": jersey_id, "team": jersey_data["team"], "season": jersey_data["season"]}
                )
                return jersey_id
            else:
                self.log_result(
                    "Create Test Jersey",
                    False,
                    f"Failed to create test jersey: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return None
                
        except Exception as e:
            self.log_result("Create Test Jersey", False, f"Error creating test jersey: {str(e)}")
            return None
    
    def run_comprehensive_test(self):
        """Run comprehensive jersey photo testing"""
        print("🎯 TOPKIT JERSEY PHOTOS FOR EXPLORER - COMPREHENSIVE TESTING")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate
        print("📋 STEP 1: AUTHENTICATION")
        admin_auth = self.authenticate_admin()
        user_auth = self.authenticate_user()
        print()
        
        # Step 2: Get approved jerseys
        print("📋 STEP 2: GET APPROVED JERSEYS FROM EXPLORER")
        approved_jerseys = self.get_approved_jerseys()
        print()
        
        # Step 3: Analyze photo structure
        print("📋 STEP 3: ANALYZE JERSEY PHOTO STRUCTURE")
        if approved_jerseys:
            self.analyze_jersey_photo_structure(approved_jerseys)
        print()
        
        # Step 4: Analyze jerseys with/without photos
        print("📋 STEP 4: ANALYZE JERSEYS WITH PHOTOS")
        has_photos = False
        if approved_jerseys:
            has_photos = self.analyze_jerseys_with_photos(approved_jerseys)
        print()
        
        # Step 5: If no approved jerseys with photos, try to create some
        if not has_photos and admin_auth:
            print("📋 STEP 5: CREATE TEST DATA (NO PHOTOS FOUND)")
            
            # Get pending jerseys
            pending_jerseys = self.get_pending_jerseys()
            
            if pending_jerseys:
                # Approve first pending jersey
                first_pending = pending_jerseys[0]
                jersey_id = first_pending.get('id')
                if jersey_id:
                    self.approve_jersey_for_testing(jersey_id)
                    
                    # Re-check approved jerseys
                    print("\n📋 RE-CHECKING APPROVED JERSEYS AFTER APPROVAL")
                    approved_jerseys = self.get_approved_jerseys()
                    if approved_jerseys:
                        self.analyze_jerseys_with_photos(approved_jerseys)
            else:
                # Create new test jersey
                if user_auth:
                    test_jersey_id = self.create_test_jersey_with_photos()
                    if test_jersey_id and admin_auth:
                        # Approve the test jersey
                        self.approve_jersey_for_testing(test_jersey_id)
                        
                        # Re-check approved jerseys
                        print("\n📋 RE-CHECKING APPROVED JERSEYS AFTER CREATING AND APPROVING")
                        approved_jerseys = self.get_approved_jerseys()
                        if approved_jerseys:
                            self.analyze_jerseys_with_photos(approved_jerseys)
            print()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Photo analysis summary
        if self.jerseys_with_photos or self.jerseys_without_photos:
            print("📸 PHOTO ANALYSIS SUMMARY:")
            print(f"✅ Jerseys WITH photos: {len(self.jerseys_with_photos)}")
            print(f"❌ Jerseys WITHOUT photos: {len(self.jerseys_without_photos)}")
            
            if self.jerseys_with_photos:
                print("\n🎯 JERSEYS WITH PHOTOS (Ready for Explorer):")
                for jersey in self.jerseys_with_photos[:5]:  # Show first 5
                    photos = []
                    if jersey['has_front_photo']:
                        photos.append("front")
                    if jersey['has_back_photo']:
                        photos.append("back")
                    if jersey['has_images']:
                        photos.append(f"images({len(jersey['images'])})")
                    
                    print(f"  • {jersey['team']} {jersey['season']} - {jersey['reference_number']} - Photos: {', '.join(photos)}")
            
            if self.jerseys_without_photos:
                print(f"\n⚠️  JERSEYS WITHOUT PHOTOS (Need photos for Explorer):")
                for jersey in self.jerseys_without_photos[:5]:  # Show first 5
                    print(f"  • {jersey['team']} {jersey['season']} - {jersey['reference_number']} - NO PHOTOS")
        
        print()
        
        # Failed tests details
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("❌ FAILED TESTS:")
            for result in failed_results:
                print(f"  • {result['test']}: {result['message']}")
        
        print()
        
        # Final recommendation
        jerseys_ready_for_explorer = len(self.jerseys_with_photos)
        if jerseys_ready_for_explorer > 0:
            print(f"🎉 CONCLUSION: {jerseys_ready_for_explorer} jerseys are ready for Explorer display with photos!")
        else:
            print("⚠️  CONCLUSION: No approved jerseys with photos found. Explorer will be empty.")
            print("   RECOMMENDATION: Add photos to existing jerseys or approve jerseys with photos.")

if __name__ == "__main__":
    tester = JerseyPhotoTester()
    tester.run_comprehensive_test()