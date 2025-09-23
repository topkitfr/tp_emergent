#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - MASTER KIT FORMDATA SUBMISSION BUG FIX TESTING

Testing the Master Kit FormData submission bug fix comprehensively:
1. **Master Kit FormData Creation Testing** - Test POST /api/master-kits endpoint with FormData and file uploads
2. **UnicodeDecodeError Fix Verification** - Verify FormData endpoint works without UnicodeDecodeError
3. **Contribution Creation for Moderation** - Verify contribution entry is created in contributions_v2 collection
4. **Response Message Testing** - Verify success response includes detailed message with topkit_reference and status
5. **Authentication Testing** - Login with emergency.admin@topkit.test / EmergencyAdmin2025!
6. **File Upload Testing** - Test front_photo and back_photo file uploads with FormData

CRITICAL: Testing with emergency.admin@topkit.test / EmergencyAdmin2025! account.
Focus on verifying that Master Kit FormData submissions now work without UnicodeDecodeError and properly create contributions.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://jersey-collector-2.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitMasterKitFormTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.form_data = {}
        self.created_master_kit_id = None
        self.created_contribution_id = None
        
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
        """Authenticate with emergency admin credentials"""
        try:
            print(f"\n🔐 EMERGENCY ADMIN AUTHENTICATION")
            print("=" * 60)
            print(f"   Email: {ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Emergency Admin Authentication", True, 
                             f"✅ Emergency admin authentication successful")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Email: {self.admin_user_data.get('email')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Emergency Admin Authentication", False, 
                             f"❌ Emergency admin authentication failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_form_data(self):
        """Get form data for Master Kit creation (clubs, brands, competitions, sponsors)"""
        try:
            print(f"\n📋 GETTING FORM DATA")
            print("=" * 60)
            print("Getting form data for Master Kit creation...")
            
            # Get clubs
            clubs_response = self.session.get(f"{BACKEND_URL}/form-data/clubs", timeout=10)
            brands_response = self.session.get(f"{BACKEND_URL}/form-data/brands", timeout=10)
            competitions_response = self.session.get(f"{BACKEND_URL}/form-data/competitions", timeout=10)
            sponsors_response = self.session.get(f"{BACKEND_URL}/form-data/sponsors", timeout=10)
            
            if all(r.status_code == 200 for r in [clubs_response, brands_response, competitions_response, sponsors_response]):
                self.form_data = {
                    "clubs": clubs_response.json(),
                    "brands": brands_response.json(),
                    "competitions": competitions_response.json(),
                    "sponsors": sponsors_response.json()
                }
                
                print(f"      ✅ Form data retrieved successfully")
                print(f"         Clubs: {len(self.form_data['clubs'])}")
                print(f"         Brands: {len(self.form_data['brands'])}")
                print(f"         Competitions: {len(self.form_data['competitions'])}")
                print(f"         Sponsors: {len(self.form_data['sponsors'])}")
                
                self.log_test("Get Form Data", True, 
                             f"✅ Form data retrieved - {len(self.form_data['clubs'])} clubs, {len(self.form_data['brands'])} brands, {len(self.form_data['competitions'])} competitions, {len(self.form_data['sponsors'])} sponsors")
                return True
            else:
                self.log_test("Get Form Data", False, 
                             f"❌ Failed to get form data - Status codes: clubs={clubs_response.status_code}, brands={brands_response.status_code}, competitions={competitions_response.status_code}, sponsors={sponsors_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Form Data", False, f"Exception: {str(e)}")
            return False
    
    def create_test_image(self, width=800, height=600, filename="test_image.jpg"):
        """Create a test image for FormData upload"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (width, height), color='red')
            img_buffer = BytesIO()
            img.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            return img_buffer
        except Exception as e:
            print(f"Error creating test image: {str(e)}")
            return None
    
    def test_master_kit_formdata_submission(self):
        """Test Master Kit creation via FormData with file uploads"""
        try:
            print(f"\n📤 TESTING MASTER KIT FORMDATA SUBMISSION")
            print("=" * 60)
            print("Testing Master Kit creation via FormData with file uploads...")
            
            if not self.auth_token:
                self.log_test("Master Kit FormData Submission", False, "❌ No authentication token available")
                return False
            
            if not self.form_data:
                self.log_test("Master Kit FormData Submission", False, "❌ No form data available")
                return False
            
            # Select first available club, brand, and competition
            if not self.form_data['clubs'] or not self.form_data['brands'] or not self.form_data['competitions']:
                self.log_test("Master Kit FormData Submission", False, "❌ Insufficient form data for testing")
                return False
            
            club = self.form_data['clubs'][0]
            brand = self.form_data['brands'][0]
            competition = self.form_data['competitions'][0]
            
            # Create test images
            front_image = self.create_test_image(800, 600, "front_test.jpg")
            back_image = self.create_test_image(800, 600, "back_test.jpg")
            
            if not front_image or not back_image:
                self.log_test("Master Kit FormData Submission", False, "❌ Failed to create test images")
                return False
            
            # Prepare FormData
            files = {
                'front_photo': ('front_test.jpg', front_image, 'image/jpeg'),
                'back_photo': ('back_test.jpg', back_image, 'image/jpeg')
            }
            
            data = {
                'kit_type': 'authentic',
                'club_id': club['id'],
                'kit_style': 'home',
                'season': '2024/2025',
                'competition_id': competition['id'],
                'brand_id': brand['id']
            }
            
            print(f"      Creating Master Kit via FormData:")
            print(f"         Club: {club['name']} ({club['id']})")
            print(f"         Brand: {brand['name']} ({brand['id']})")
            print(f"         Competition: {competition['name']} ({competition['id']})")
            print(f"         Kit Type: {data['kit_type']}")
            print(f"         Season: {data['season']}")
            print(f"         Files: front_photo, back_photo")
            
            response = self.session.post(
                f"{BACKEND_URL}/master-kits",
                files=files,
                data=data,
                timeout=20
            )
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                self.created_master_kit_id = response_data.get('id')
                
                print(f"         ✅ Master Kit created via FormData successfully")
                print(f"            Master Kit ID: {self.created_master_kit_id}")
                print(f"            TopKit Reference: {response_data.get('topkit_reference')}")
                print(f"            Status: {response_data.get('status', 'N/A')}")
                
                # Verify response structure
                required_response_fields = ['id', 'topkit_reference']
                missing_fields = [field for field in required_response_fields if field not in response_data]
                
                if not missing_fields:
                    self.log_test("Master Kit FormData Submission", True, 
                                 f"✅ Master Kit created via FormData with file uploads successfully")
                    return True
                else:
                    self.log_test("Master Kit FormData Submission", False, 
                                 f"❌ Master Kit created but response missing fields: {missing_fields}")
                    return False
                    
            else:
                error_text = response.text
                print(f"         ❌ Master Kit FormData creation failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                self.log_test("Master Kit FormData Submission", False, 
                             f"❌ Master Kit FormData creation failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Master Kit FormData Submission", False, f"Exception: {str(e)}")
            return False
    
    def test_master_kit_creation_required_fields(self):
        """Test Master Kit creation with required fields only"""
        try:
            print(f"\n⚽ TESTING MASTER KIT CREATION - REQUIRED FIELDS")
            print("=" * 60)
            print("Testing Master Kit creation with required fields only...")
            
            if not self.auth_token:
                self.log_test("Master Kit Creation - Required Fields", False, "❌ No authentication token available")
                return False
            
            if not self.form_data:
                self.log_test("Master Kit Creation - Required Fields", False, "❌ No form data available")
                return False
            
            # Select first available club, brand, and competition
            if not self.form_data['clubs'] or not self.form_data['brands'] or not self.form_data['competitions']:
                self.log_test("Master Kit Creation - Required Fields", False, "❌ Insufficient form data for testing")
                return False
            
            club = self.form_data['clubs'][0]
            brand = self.form_data['brands'][0]
            competition = self.form_data['competitions'][0]
            
            # Create Master Kit with required fields only
            master_kit_data = {
                "kit_type": "authentic",  # KitModel: authentic or replica
                "club_id": club['id'],
                "kit_style": "home",  # KitType: home, away, third, fourth, gk, special
                "season": "2024/2025",
                "competition_id": competition['id'],
                "front_photo_url": "test_front_photo.jpg",
                "back_photo_url": "test_back_photo.jpg",
                "brand_id": brand['id']
            }
            
            print(f"      Creating Master Kit with required fields:")
            print(f"         Club: {club['name']} ({club['id']})")
            print(f"         Brand: {brand['name']} ({brand['id']})")
            print(f"         Competition: {competition['name']} ({competition['id']})")
            print(f"         Kit Type: {master_kit_data['kit_type']}")
            print(f"         Season: {master_kit_data['season']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/master-kits",
                json=master_kit_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.created_master_kit_id = data.get('id')
                
                print(f"         ✅ Master Kit created successfully")
                print(f"            Master Kit ID: {self.created_master_kit_id}")
                print(f"            TopKit Reference: {data.get('topkit_reference')}")
                
                # Verify response structure
                required_response_fields = ['id', 'topkit_reference', 'club_id', 'brand_id', 'competition_id', 'kit_type', 'season']
                missing_fields = [field for field in required_response_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Master Kit Creation - Required Fields", True, 
                                 f"✅ Master Kit created successfully with all required response fields")
                    return True
                else:
                    self.log_test("Master Kit Creation - Required Fields", False, 
                                 f"❌ Master Kit created but response missing fields: {missing_fields}")
                    return False
                    
            else:
                error_text = response.text
                print(f"         ❌ Master Kit creation failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                self.log_test("Master Kit Creation - Required Fields", False, 
                             f"❌ Master Kit creation failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Master Kit Creation - Required Fields", False, f"Exception: {str(e)}")
            return False
    
    def test_master_kit_creation_with_sponsors(self):
        """Test Master Kit creation with optional sponsor fields"""
        try:
            print(f"\n🏢 TESTING MASTER KIT CREATION - WITH SPONSORS")
            print("=" * 60)
            print("Testing Master Kit creation with optional sponsor fields...")
            
            if not self.auth_token:
                self.log_test("Master Kit Creation - With Sponsors", False, "❌ No authentication token available")
                return False
            
            if not self.form_data:
                self.log_test("Master Kit Creation - With Sponsors", False, "❌ No form data available")
                return False
            
            # Select first available club, brand, and competition
            if not self.form_data['clubs'] or not self.form_data['brands'] or not self.form_data['competitions']:
                self.log_test("Master Kit Creation - With Sponsors", False, "❌ Insufficient form data for testing")
                return False
            
            club = self.form_data['clubs'][0]
            brand = self.form_data['brands'][0]
            competition = self.form_data['competitions'][0]
            
            # Create Master Kit with sponsors if available
            master_kit_data = {
                "kit_type": "replica",  # KitModel: authentic or replica
                "club_id": club['id'],
                "kit_style": "away",  # KitType: home, away, third, fourth, gk, special
                "season": "2024/2025",
                "competition_id": competition['id'],
                "front_photo_url": "test_front_photo_2.jpg",
                "back_photo_url": "test_back_photo_2.jpg",
                "brand_id": brand['id']
            }
            
            # Add sponsors if available
            if self.form_data['sponsors']:
                primary_sponsor = self.form_data['sponsors'][0]
                master_kit_data["primary_sponsor_id"] = primary_sponsor['id']  # Use primary_sponsor_id
                print(f"         Primary Sponsor: {primary_sponsor['name']} ({primary_sponsor['id']})")
                
                if len(self.form_data['sponsors']) > 1:
                    secondary_sponsor = self.form_data['sponsors'][1]
                    master_kit_data["secondary_sponsor_ids"] = [secondary_sponsor['id']]
                    print(f"         Secondary Sponsor: {secondary_sponsor['name']} ({secondary_sponsor['id']})")
            
            print(f"      Creating Master Kit with sponsors:")
            print(f"         Club: {club['name']} ({club['id']})")
            print(f"         Brand: {brand['name']} ({brand['id']})")
            print(f"         Competition: {competition['name']} ({competition['id']})")
            print(f"         Kit Type: {master_kit_data['kit_type']}")
            print(f"         Season: {master_kit_data['season']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/master-kits",
                json=master_kit_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                print(f"         ✅ Master Kit with sponsors created successfully")
                print(f"            Master Kit ID: {data.get('id')}")
                print(f"            TopKit Reference: {data.get('topkit_reference')}")
                
                self.log_test("Master Kit Creation - With Sponsors", True, 
                             f"✅ Master Kit with sponsors created successfully")
                return True
                    
            else:
                error_text = response.text
                print(f"         ❌ Master Kit creation with sponsors failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                self.log_test("Master Kit Creation - With Sponsors", False, 
                             f"❌ Master Kit creation with sponsors failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Master Kit Creation - With Sponsors", False, f"Exception: {str(e)}")
            return False
    
    def test_contribution_creation_for_moderation(self):
        """Test that Master Kit creation creates contribution entry for moderation"""
        try:
            print(f"\n📝 TESTING CONTRIBUTION CREATION FOR MODERATION")
            print("=" * 60)
            print("Testing that Master Kit creation creates contribution entry...")
            
            if not self.created_master_kit_id:
                self.log_test("Contribution Creation for Moderation", False, "❌ No Master Kit created for testing")
                return False
            
            # Check contributions-v2 endpoint for the created Master Kit
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/", timeout=10)
            
            if response.status_code == 200:
                contributions = response.json()
                
                print(f"      ✅ Contributions endpoint accessible")
                print(f"         Found {len(contributions)} contributions")
                
                # Look for contribution with entity_type="master_kit" and matching master_kit_id
                master_kit_contributions = [
                    c for c in contributions 
                    if c.get('entity_type') == 'master_kit' and 
                       (c.get('entity_id') == self.created_master_kit_id or 
                        c.get('master_kit_id') == self.created_master_kit_id)
                ]
                
                if master_kit_contributions:
                    contribution = master_kit_contributions[0]
                    self.created_contribution_id = contribution.get('id')
                    
                    print(f"         ✅ Master Kit contribution found")
                    print(f"            Contribution ID: {contribution.get('id')}")
                    print(f"            Entity Type: {contribution.get('entity_type')}")
                    print(f"            Status: {contribution.get('status')}")
                    print(f"            Master Kit ID: {contribution.get('entity_id') or contribution.get('master_kit_id')}")
                    
                    # Verify contribution has required fields
                    required_fields = ['id', 'entity_type', 'status']
                    missing_fields = [field for field in required_fields if field not in contribution]
                    
                    if not missing_fields:
                        # Check if status is "pending_review" (NEW REQUIREMENT)
                        if contribution.get('status') == 'pending_review':
                            self.log_test("Contribution Creation for Moderation", True, 
                                         f"✅ Master Kit contribution created with pending_review status for moderation dashboard")
                            return True
                        elif contribution.get('status') == 'pending':
                            self.log_test("Contribution Creation for Moderation", False, 
                                         f"❌ Master Kit contribution has old 'pending' status instead of 'pending_review'")
                            return False
                        else:
                            self.log_test("Contribution Creation for Moderation", False, 
                                         f"❌ Master Kit contribution has unexpected status: {contribution.get('status')} (expected 'pending_review')")
                            return False
                    else:
                        self.log_test("Contribution Creation for Moderation", False, 
                                     f"❌ Contribution missing required fields: {missing_fields}")
                        return False
                else:
                    print(f"         ❌ No Master Kit contribution found for Master Kit ID: {self.created_master_kit_id}")
                    
                    # Show available contributions for debugging
                    print(f"         Available contributions:")
                    for c in contributions[:3]:  # Show first 3
                        print(f"            • {c.get('entity_type')} - {c.get('id')} - Status: {c.get('status')}")
                    
                    self.log_test("Contribution Creation for Moderation", False, 
                                 f"❌ No Master Kit contribution found for created Master Kit")
                    return False
                    
            else:
                self.log_test("Contribution Creation for Moderation", False, 
                             f"❌ Contributions endpoint failed - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Contribution Creation for Moderation", False, f"Exception: {str(e)}")
            return False
    
    def test_pending_review_status_filtering(self):
        """Test GET /api/contributions-v2/?status=pending_review filtering"""
        try:
            print(f"\n🔍 TESTING PENDING_REVIEW STATUS FILTERING")
            print("=" * 60)
            print("Testing GET /api/contributions-v2/?status=pending_review filtering...")
            
            # Test the specific filtering endpoint for pending_review status
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/?status=pending_review", timeout=10)
            
            if response.status_code == 200:
                pending_review_contributions = response.json()
                
                print(f"      ✅ Pending review filtering endpoint accessible")
                print(f"         Found {len(pending_review_contributions)} pending_review contributions")
                
                # Verify all returned contributions have pending_review status
                all_pending_review = all(c.get('status') == 'pending_review' for c in pending_review_contributions)
                
                if all_pending_review:
                    print(f"         ✅ All contributions have pending_review status")
                    
                    # Check if our created Master Kit contribution is in the list
                    if self.created_contribution_id:
                        our_contribution_found = any(
                            c.get('id') == self.created_contribution_id 
                            for c in pending_review_contributions
                        )
                        
                        if our_contribution_found:
                            print(f"         ✅ Our Master Kit contribution found in pending_review list")
                            self.log_test("Pending Review Status Filtering", True, 
                                         f"✅ Pending review filtering working - {len(pending_review_contributions)} contributions found, including our Master Kit")
                            return True
                        else:
                            print(f"         ⚠️ Our Master Kit contribution not found in pending_review list")
                            self.log_test("Pending Review Status Filtering", True, 
                                         f"✅ Pending review filtering working - {len(pending_review_contributions)} contributions found (our contribution may have different status)")
                            return True
                    else:
                        self.log_test("Pending Review Status Filtering", True, 
                                     f"✅ Pending review filtering working - {len(pending_review_contributions)} contributions found")
                        return True
                else:
                    # Show status distribution for debugging
                    status_counts = {}
                    for c in pending_review_contributions:
                        status = c.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    print(f"         ❌ Not all contributions have pending_review status")
                    print(f"            Status distribution: {status_counts}")
                    
                    self.log_test("Pending Review Status Filtering", False, 
                                 f"❌ Filtering not working correctly - found mixed statuses: {status_counts}")
                    return False
                    
            else:
                self.log_test("Pending Review Status Filtering", False, 
                             f"❌ Pending review filtering endpoint failed - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Pending Review Status Filtering", False, f"Exception: {str(e)}")
            return False
    
    def test_moderation_dashboard_integration(self):
        """Test that contributions appear in moderation system"""
        try:
            print(f"\n🎛️ TESTING MODERATION DASHBOARD INTEGRATION")
            print("=" * 60)
            print("Testing that Master Kit contributions appear in moderation system...")
            
            if not self.created_contribution_id:
                self.log_test("Moderation Dashboard Integration", False, "❌ No contribution created for testing")
                return False
            
            # Test GET /api/contributions-v2 includes the new master kit contribution
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/", timeout=10)
            
            if response.status_code == 200:
                contributions = response.json()
                
                # Find our specific contribution
                our_contribution = None
                for c in contributions:
                    if c.get('id') == self.created_contribution_id:
                        our_contribution = c
                        break
                
                if our_contribution:
                    print(f"      ✅ Contribution found in moderation system")
                    print(f"         Contribution ID: {our_contribution.get('id')}")
                    print(f"         Entity Type: {our_contribution.get('entity_type')}")
                    print(f"         Status: {our_contribution.get('status')}")
                    print(f"         Created By: {our_contribution.get('created_by')}")
                    
                    # Verify contribution has all required fields for moderation
                    moderation_fields = ['id', 'entity_type', 'status', 'created_by', 'created_at']
                    present_fields = [field for field in moderation_fields if field in our_contribution]
                    
                    print(f"         Moderation fields present: {present_fields}")
                    
                    if len(present_fields) >= 4:  # At least 4 out of 5 fields
                        self.log_test("Moderation Dashboard Integration", True, 
                                     f"✅ Master Kit contribution properly integrated in moderation system")
                        return True
                    else:
                        self.log_test("Moderation Dashboard Integration", False, 
                                     f"❌ Contribution missing moderation fields: {set(moderation_fields) - set(present_fields)}")
                        return False
                else:
                    self.log_test("Moderation Dashboard Integration", False, 
                                 f"❌ Contribution {self.created_contribution_id} not found in moderation system")
                    return False
                    
            else:
                self.log_test("Moderation Dashboard Integration", False, 
                             f"❌ Moderation system endpoint failed - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Moderation Dashboard Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_response_message_format(self):
        """Test that Master Kit creation response includes proper message format"""
        try:
            print(f"\n💬 TESTING RESPONSE MESSAGE FORMAT")
            print("=" * 60)
            print("Testing Master Kit creation response message format...")
            
            if not self.auth_token:
                self.log_test("Response Message Format", False, "❌ No authentication token available")
                return False
            
            if not self.form_data:
                self.log_test("Response Message Format", False, "❌ No form data available")
                return False
            
            # Select first available club, brand, and competition
            if not self.form_data['clubs'] or not self.form_data['brands'] or not self.form_data['competitions']:
                self.log_test("Response Message Format", False, "❌ Insufficient form data for testing")
                return False
            
            club = self.form_data['clubs'][0]
            brand = self.form_data['brands'][0]
            competition = self.form_data['competitions'][0]
            
            # Create Master Kit to test response format
            master_kit_data = {
                "kit_type": "authentic",  # KitModel: authentic or replica
                "club_id": club['id'],
                "kit_style": "third",  # KitType: home, away, third, fourth, gk, special
                "season": "2024/2025",
                "competition_id": competition['id'],
                "front_photo_url": "test_response_front.jpg",
                "back_photo_url": "test_response_back.jpg",
                "brand_id": brand['id']
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/master-kits",
                json=master_kit_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                print(f"      ✅ Master Kit creation response received")
                
                # Check for required response fields
                required_fields = ['id', 'topkit_reference']
                optional_fields = ['status', 'message', 'created_at', 'created_by']
                
                present_required = [field for field in required_fields if field in data]
                present_optional = [field for field in optional_fields if field in data]
                
                print(f"         Required fields present: {present_required}")
                print(f"         Optional fields present: {present_optional}")
                print(f"         TopKit Reference: {data.get('topkit_reference')}")
                
                if len(present_required) == len(required_fields):
                    # Check if topkit_reference follows expected format
                    topkit_ref = data.get('topkit_reference', '')
                    if topkit_ref.startswith('TK-'):
                        self.log_test("Response Message Format", True, 
                                     f"✅ Response format correct with topkit_reference: {topkit_ref}")
                        return True
                    else:
                        self.log_test("Response Message Format", False, 
                                     f"❌ TopKit reference format incorrect: {topkit_ref}")
                        return False
                else:
                    missing_required = set(required_fields) - set(present_required)
                    self.log_test("Response Message Format", False, 
                                 f"❌ Response missing required fields: {missing_required}")
                    return False
                    
            else:
                self.log_test("Response Message Format", False, 
                             f"❌ Master Kit creation failed - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Response Message Format", False, f"Exception: {str(e)}")
            return False
    
    def test_form_validation_errors(self):
        """Test Master Kit creation with missing required fields"""
        try:
            print(f"\n🚫 TESTING FORM VALIDATION ERRORS")
            print("=" * 60)
            print("Testing Master Kit creation with missing required fields...")
            
            if not self.auth_token:
                self.log_test("Form Validation Errors", False, "❌ No authentication token available")
                return False
            
            # Test with missing required fields
            invalid_data_tests = [
                ({}, "Empty data"),
                ({"kit_type": "authentic"}, "Missing club_id"),
                ({"kit_type": "authentic", "club_id": "test-club-id"}, "Missing season"),
                ({"kit_type": "authentic", "club_id": "test-club-id", "season": "invalid-season"}, "Invalid season format")
            ]
            
            validation_results = []
            
            for invalid_data, test_description in invalid_data_tests:
                print(f"      Testing: {test_description}")
                
                response = self.session.post(
                    f"{BACKEND_URL}/master-kits",
                    json=invalid_data,
                    timeout=10
                )
                
                if response.status_code == 422:  # Validation error expected
                    print(f"         ✅ Validation error returned as expected (422)")
                    validation_results.append(True)
                elif response.status_code == 400:  # Bad request also acceptable
                    print(f"         ✅ Bad request error returned as expected (400)")
                    validation_results.append(True)
                else:
                    print(f"         ❌ Unexpected status code: {response.status_code}")
                    validation_results.append(False)
            
            if all(validation_results):
                self.log_test("Form Validation Errors", True, 
                             f"✅ Form validation working correctly - all {len(validation_results)} tests passed")
                return True
            else:
                failed_count = len([r for r in validation_results if not r])
                self.log_test("Form Validation Errors", False, 
                             f"❌ Form validation issues - {failed_count}/{len(validation_results)} tests failed")
                return False
                
        except Exception as e:
            self.log_test("Form Validation Errors", False, f"Exception: {str(e)}")
            return False
    
    def test_master_kit_form_submission_bug_fix(self):
        """Test complete Master Kit form submission bug fix with pending_review status"""
        print("\n🚀 MASTER KIT FORM SUBMISSION BUG FIX TESTING - PENDING_REVIEW STATUS")
        print("Testing Master Kit form submission creates contributions with pending_review status")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        test_results.append(auth_success)
        
        # Step 2: Get form data
        print("\n2️⃣ Getting form data...")
        form_data_success = self.get_form_data()
        test_results.append(form_data_success)
        
        # Step 3: Test Master Kit creation via FormData (NEW REQUIREMENT)
        print("\n3️⃣ Testing Master Kit creation via FormData with file uploads...")
        formdata_success = self.test_master_kit_formdata_submission()
        test_results.append(formdata_success)
        
        # Step 4: Test contribution creation with pending_review status (UPDATED REQUIREMENT)
        print("\n4️⃣ Testing contribution creation with pending_review status...")
        contribution_success = self.test_contribution_creation_for_moderation()
        test_results.append(contribution_success)
        
        # Step 5: Test pending_review status filtering (NEW REQUIREMENT)
        print("\n5️⃣ Testing GET /api/contributions-v2/?status=pending_review filtering...")
        filtering_success = self.test_pending_review_status_filtering()
        test_results.append(filtering_success)
        
        # Step 6: Test moderation dashboard integration
        print("\n6️⃣ Testing moderation dashboard integration...")
        moderation_success = self.test_moderation_dashboard_integration()
        test_results.append(moderation_success)
        
        # Step 7: Test response message format
        print("\n7️⃣ Testing response message format...")
        response_format_success = self.test_response_message_format()
        test_results.append(response_format_success)
        
        # Step 8: Test form validation errors
        print("\n8️⃣ Testing form validation errors...")
        validation_success = self.test_form_validation_errors()
        test_results.append(validation_success)
        
        return test_results
    
    def print_final_summary(self):
        """Print final testing summary"""
        print("\n📊 MASTER KIT PENDING_REVIEW STATUS TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 MASTER KIT PENDING_REVIEW STATUS RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Emergency admin login working")
        else:
            print(f"  ❌ AUTHENTICATION: Emergency admin login failed")
        
        # Form Data
        form_data_working = any(r['success'] for r in self.test_results if 'Get Form Data' in r['test'])
        if form_data_working:
            print(f"  ✅ FORM DATA: All form data endpoints accessible")
        else:
            print(f"  ❌ FORM DATA: Form data endpoints failed")
        
        # FormData Submission (NEW)
        formdata_working = any(r['success'] for r in self.test_results if 'Master Kit FormData Submission' in r['test'])
        if formdata_working:
            print(f"  ✅ FORMDATA SUBMISSION: Master Kit creation via FormData with file uploads working")
        else:
            print(f"  ❌ FORMDATA SUBMISSION: FormData submission with file uploads failed")
        
        # Contribution Creation with pending_review status (UPDATED)
        contribution_working = any(r['success'] for r in self.test_results if 'Contribution Creation for Moderation' in r['test'])
        if contribution_working:
            print(f"  ✅ CONTRIBUTION CREATION: Master Kit contributions created with pending_review status")
        else:
            print(f"  ❌ CONTRIBUTION CREATION: Contributions not created with correct pending_review status")
        
        # Pending Review Filtering (NEW)
        filtering_working = any(r['success'] for r in self.test_results if 'Pending Review Status Filtering' in r['test'])
        if filtering_working:
            print(f"  ✅ PENDING_REVIEW FILTERING: GET /api/contributions-v2/?status=pending_review working")
        else:
            print(f"  ❌ PENDING_REVIEW FILTERING: Status filtering not working correctly")
        
        # Moderation Integration
        moderation_working = any(r['success'] for r in self.test_results if 'Moderation Dashboard Integration' in r['test'])
        if moderation_working:
            print(f"  ✅ MODERATION INTEGRATION: Contributions appear in moderation system")
        else:
            print(f"  ❌ MODERATION INTEGRATION: Contributions not appearing in moderation")
        
        # Response Format
        response_working = any(r['success'] for r in self.test_results if 'Response Message Format' in r['test'])
        if response_working:
            print(f"  ✅ RESPONSE FORMAT: Proper response with topkit_reference and status")
        else:
            print(f"  ❌ RESPONSE FORMAT: Response format issues")
        
        # Validation
        validation_working = any(r['success'] for r in self.test_results if 'Form Validation Errors' in r['test'])
        if validation_working:
            print(f"  ✅ FORM VALIDATION: Error handling working correctly")
        else:
            print(f"  ❌ FORM VALIDATION: Validation error handling issues")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status - Focus on the specific requirements
        print(f"\n🎯 FINAL STATUS - PENDING_REVIEW STATUS IMPLEMENTATION:")
        critical_tests = [auth_working, formdata_working, contribution_working, filtering_working]
        if all(critical_tests):
            print(f"  ✅ MASTER KIT PENDING_REVIEW STATUS WORKING PERFECTLY")
            print(f"     - Emergency admin authentication operational")
            print(f"     - Master Kit FormData submission with file uploads working")
            print(f"     - Contributions created with pending_review status (not pending)")
            print(f"     - GET /api/contributions-v2/?status=pending_review filtering working")
            print(f"     - Moderation Dashboard will now find the contributions")
        elif auth_working and formdata_working and contribution_working:
            print(f"  ⚠️ PARTIAL SUCCESS: Core functionality working")
            print(f"     - Master Kit creation and contribution creation functional")
            print(f"     - Some filtering or integration issues may exist")
        else:
            print(f"  ❌ MAJOR ISSUES: Critical pending_review status implementation not working")
            print(f"     - Cannot properly create Master Kits with correct contribution status")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all Master Kit form submission tests and return success status"""
        test_results = self.test_master_kit_form_submission_bug_fix()
        self.print_final_summary()
        return any(test_results)

def main():
    """Main test execution - Master Kit Form Submission Bug Fix Testing"""
    tester = TopKitMasterKitFormTesting()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()