import requests
import sys
import json
import subprocess
import tempfile
from datetime import datetime
from io import BytesIO
from PIL import Image

class FootballJerseyAPITester:
    def __init__(self, base_url="https://kit-collection-7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.kit_id = None
        self.version_id = None
        self.collection_id = None
        self.review_id = None
        self.submission_id = None
        self.report_id = None

    def log_test(self, name, result, status_code=None, details=""):
        self.tests_run += 1
        if result:
            self.tests_passed += 1
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        
        print(f"\n{status} - {name}")
        if status_code:
            print(f"   Status Code: {status_code}")
        if details:
            print(f"   Details: {details}")

    def test_stats_endpoint(self):
        """Test GET /api/stats"""
        try:
            response = requests.get(f"{self.api_url}/stats")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Stats Endpoint", success, response.status_code, 
                         f"Stats: {data}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Stats Endpoint", False, details=str(e))
            return False, {}

    def test_seed_endpoint(self):
        """Test POST /api/seed"""
        try:
            response = requests.post(f"{self.api_url}/seed")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Seed Data Endpoint", success, response.status_code, 
                         f"Response: {data}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Seed Data Endpoint", False, details=str(e))
            return False, {}

    def test_filters_endpoint(self):
        """Test GET /api/master-kits/filters"""
        try:
            response = requests.get(f"{self.api_url}/master-kits/filters")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Filters Endpoint", success, response.status_code,
                         f"Filters: clubs={len(data.get('clubs', []))}, brands={len(data.get('brands', []))}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Filters Endpoint", False, details=str(e))
            return False, {}

    def test_master_kits_list(self):
        """Test GET /api/master-kits"""
        try:
            response = requests.get(f"{self.api_url}/master-kits")
            success = response.status_code == 200
            data = response.json() if success else []
            
            if success and len(data) > 0:
                self.kit_id = data[0].get('kit_id')
            
            self.log_test("Master Kits List", success, response.status_code,
                         f"Found {len(data)} kits" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Master Kits List", False, details=str(e))
            return False, []

    def test_master_kit_detail(self):
        """Test GET /api/master-kits/{kit_id}"""
        if not self.kit_id:
            self.log_test("Master Kit Detail", False, details="No kit_id available")
            return False, {}
        
        try:
            response = requests.get(f"{self.api_url}/master-kits/{self.kit_id}")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success and data.get('versions') and len(data['versions']) > 0:
                self.version_id = data['versions'][0].get('version_id')
            
            self.log_test("Master Kit Detail", success, response.status_code,
                         f"Kit: {data.get('club', 'Unknown')}, Versions: {len(data.get('versions', []))}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Master Kit Detail", False, details=str(e))
            return False, {}

    def test_version_detail(self):
        """Test GET /api/versions/{version_id}"""
        if not self.version_id:
            self.log_test("Version Detail", False, details="No version_id available")
            return False, {}
        
        try:
            response = requests.get(f"{self.api_url}/versions/{self.version_id}")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Version Detail", success, response.status_code,
                         f"Version: {data.get('competition', 'Unknown')}, Reviews: {data.get('review_count', 0)}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Version Detail", False, details=str(e))
            return False, {}

    def create_test_session(self):
        """Create a test session using mongosh"""
        try:
            print("\n🔧 Creating test user and session...")
            mongo_command = """
mongosh --eval "
use('test_database');
var userId = 'test-user-' + Date.now();
var sessionToken = 'test_session_' + Date.now();
db.users.insertOne({
  user_id: userId,
  email: 'test.user.' + Date.now() + '@example.com',
  name: 'Test User',
  picture: 'https://via.placeholder.com/150',
  created_at: new Date()
});
db.user_sessions.insertOne({
  user_id: userId,
  session_token: sessionToken,
  expires_at: new Date(Date.now() + 7*24*60*60*1000),
  created_at: new Date()
});
print('SESSION_TOKEN:' + sessionToken);
print('USER_ID:' + userId);
"
            """
            result = subprocess.run(mongo_command, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to create test session: {result.stderr}")
                return False
            
            # Parse output to extract session token and user ID
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'SESSION_TOKEN:' in line:
                    self.session_token = line.split('SESSION_TOKEN:')[1].strip()
                elif 'USER_ID:' in line:
                    self.user_id = line.split('USER_ID:')[1].strip()
            
            if self.session_token and self.user_id:
                print(f"✅ Test session created - User: {self.user_id}, Token: {self.session_token[:20]}...")
                return True
            else:
                print("❌ Could not extract session token or user ID")
                return False
                
        except Exception as e:
            print(f"❌ Error creating test session: {str(e)}")
            return False

    def test_auth_me(self):
        """Test GET /api/auth/me"""
        if not self.session_token:
            self.log_test("Auth Me Endpoint", False, details="No session token available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}'}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Auth Me Endpoint", success, response.status_code,
                         f"User: {data.get('email', 'Unknown')}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Auth Me Endpoint", False, details=str(e))
            return False, {}

    def test_collections_get(self):
        """Test GET /api/collections"""
        if not self.session_token:
            self.log_test("Get Collections", False, details="No session token available")
            return False, []
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}'}
            response = requests.get(f"{self.api_url}/collections", headers=headers)
            success = response.status_code == 200
            data = response.json() if success else []
            
            self.log_test("Get Collections", success, response.status_code,
                         f"Collections: {len(data)}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Get Collections", False, details=str(e))
            return False, []

    def test_collection_add(self):
        """Test POST /api/collections"""
        if not self.session_token or not self.version_id:
            self.log_test("Add to Collection", False, details="No session token or version_id available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            payload = {
                'version_id': self.version_id,
                'category': 'Test Collection',
                'notes': 'Test jersey for automated testing'
            }
            response = requests.post(f"{self.api_url}/collections", headers=headers, json=payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                self.collection_id = data.get('collection_id')
            
            self.log_test("Add to Collection", success, response.status_code,
                         f"Collection ID: {self.collection_id}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Add to Collection", False, details=str(e))
            return False, {}

    def test_review_create(self):
        """Test POST /api/reviews"""
        if not self.session_token or not self.version_id:
            self.log_test("Create Review", False, details="No session token or version_id available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            payload = {
                'version_id': self.version_id,
                'rating': 4,
                'comment': 'Great jersey! Testing review functionality.'
            }
            response = requests.post(f"{self.api_url}/reviews", headers=headers, json=payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                self.review_id = data.get('review_id')
            
            self.log_test("Create Review", success, response.status_code,
                         f"Review ID: {self.review_id}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Create Review", False, details=str(e))
            return False, {}

    def test_collection_remove(self):
        """Test DELETE /api/collections/{id}"""
        if not self.session_token or not self.collection_id:
            self.log_test("Remove from Collection", False, details="No session token or collection_id available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}'}
            response = requests.delete(f"{self.api_url}/collections/{self.collection_id}", headers=headers)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Remove from Collection", success, response.status_code,
                         f"Response: {data}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Remove from Collection", False, details=str(e))
            return False, {}

    def test_collection_update(self):
        """Test PUT /api/collections/{id} with Phase 2 fields"""
        if not self.session_token or not self.version_id:
            self.log_test("Update Collection Item", False, details="No session token or version_id available")
            return False, {}
        
        # First add an item to collection to update (use different version if possible)
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            
            # Get a list of versions to find a different one
            versions_resp = requests.get(f"{self.api_url}/versions")
            if versions_resp.status_code == 200:
                versions = versions_resp.json()
                # Find a version different from self.version_id 
                test_version_id = next((v['version_id'] for v in versions if v['version_id'] != self.version_id), self.version_id)
            else:
                test_version_id = self.version_id
                
            payload = {
                'version_id': test_version_id,
                'category': 'Update Test',
                'condition': 'Very good',
                'size': 'L',
                'value_estimate': 150.00,
                'notes': 'Test item for update testing'
            }
            response = requests.post(f"{self.api_url}/collections", headers=headers, json=payload)
            if response.status_code != 200:
                self.log_test("Update Collection Item", False, response.status_code, f"Setup failed: {response.text[:100]}")
                return False, {}
            
            collection_id = response.json().get('collection_id')
            
            # Now update the item
            update_payload = {
                'condition': 'New with tag',
                'size': 'XL', 
                'value_estimate': 200.00,
                'notes': 'Updated test item'
            }
            update_response = requests.put(f"{self.api_url}/collections/{collection_id}", headers=headers, json=update_payload)
            success = update_response.status_code == 200
            data = update_response.json() if success else {}
            
            # Clean up - remove the test item
            requests.delete(f"{self.api_url}/collections/{collection_id}", headers=headers)
            
            self.log_test("Update Collection Item", success, update_response.status_code,
                         f"Updated condition/size/value" if success else update_response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Update Collection Item", False, details=str(e))
            return False, {}

    def test_collection_stats(self):
        """Test GET /api/collections/stats"""
        if not self.session_token:
            self.log_test("Collection Stats", False, details="No session token available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}'}
            response = requests.get(f"{self.api_url}/collections/stats", headers=headers)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Collection Stats", success, response.status_code,
                         f"Total: {data.get('total_jerseys', 0)}, Est. Value: ${data.get('estimated_value', {}).get('average', 0)}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Collection Stats", False, details=str(e))
            return False, {}

    def test_category_stats(self):
        """Test GET /api/collections/category-stats"""
        if not self.session_token:
            self.log_test("Category Stats", False, details="No session token available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}'}
            response = requests.get(f"{self.api_url}/collections/category-stats", headers=headers)
            success = response.status_code == 200
            data = response.json() if success else []
            
            self.log_test("Category Stats", success, response.status_code,
                         f"Found {len(data)} categories" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Category Stats", False, details=str(e))
            return False, []

    def test_version_estimates(self):
        """Test GET /api/versions/{id}/estimates"""
        if not self.version_id:
            self.log_test("Version Estimates", False, details="No version_id available")
            return False, {}
        
        try:
            response = requests.get(f"{self.api_url}/versions/{self.version_id}/estimates")
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Version Estimates", success, response.status_code,
                         f"Estimates count: {data.get('count', 0)}, Avg: ${data.get('average', 0)}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Version Estimates", False, details=str(e))
            return False, {}

    def test_profile_update(self):
        """Test PUT /api/users/profile"""
        if not self.session_token:
            self.log_test("Profile Update", False, details="No session token available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            payload = {
                'username': f'testuser_{int(datetime.now().timestamp())}',
                'description': 'Updated test user description',
                'collection_privacy': 'private'
            }
            response = requests.put(f"{self.api_url}/users/profile", headers=headers, json=payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Profile Update", success, response.status_code,
                         f"Updated profile: {data.get('username', 'N/A')}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Profile Update", False, details=str(e))
            return False, {}

    def test_submissions_create(self):
        """Test POST /api/submissions"""
        if not self.session_token:
            self.log_test("Create Submission", False, details="No session token available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            payload = {
                'submission_type': 'master_kit',
                'data': {
                    'club': 'Test FC',
                    'season': '2024/2025',
                    'kit_type': 'Home',
                    'brand': 'Test Brand',
                    'front_photo': 'https://via.placeholder.com/400x600',
                    'year': 2024
                }
            }
            response = requests.post(f"{self.api_url}/submissions", headers=headers, json=payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                self.submission_id = data.get('submission_id')
            
            self.log_test("Create Submission", success, response.status_code,
                         f"Submission ID: {self.submission_id}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Create Submission", False, details=str(e))
            return False, {}

    def test_submissions_list(self):
        """Test GET /api/submissions"""
        try:
            response = requests.get(f"{self.api_url}/submissions", params={'status': 'pending'})
            success = response.status_code == 200
            data = response.json() if success else []
            
            self.log_test("List Submissions", success, response.status_code,
                         f"Found {len(data)} pending submissions" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("List Submissions", False, details=str(e))
            return False, []

    def test_submission_vote(self):
        """Test POST /api/submissions/{id}/vote"""
        if not self.session_token or not hasattr(self, 'submission_id') or not self.submission_id:
            self.log_test("Vote on Submission", False, details="No session token or submission_id available")
            return False, {}
        
        # First add an item to collection so user can vote
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            # Add to collection first
            requests.post(f"{self.api_url}/collections", headers=headers, json={'version_id': self.version_id, 'category': 'Test'})
            
            # Now vote
            vote_payload = {'vote': 'up'}
            response = requests.post(f"{self.api_url}/submissions/{self.submission_id}/vote", headers=headers, json=vote_payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Vote on Submission", success, response.status_code,
                         f"Votes: {data.get('votes_up', 0)} up, {data.get('votes_down', 0)} down" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Vote on Submission", False, details=str(e))
            return False, {}

    def test_reports_create(self):
        """Test POST /api/reports"""
        if not self.session_token:
            self.log_test("Create Report", False, details="No session token available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            payload = {
                'target_type': 'version',
                'target_id': self.version_id,
                'corrections': {
                    'competition': 'Corrected Competition Name',
                    'model': 'Authentic'
                },
                'notes': 'Testing report creation'
            }
            response = requests.post(f"{self.api_url}/reports", headers=headers, json=payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                self.report_id = data.get('report_id')
            
            self.log_test("Create Report", success, response.status_code,
                         f"Report ID: {self.report_id}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Create Report", False, details=str(e))
            return False, {}

    def test_reports_list(self):
        """Test GET /api/reports"""
        try:
            response = requests.get(f"{self.api_url}/reports", params={'status': 'pending'})
            success = response.status_code == 200
            data = response.json() if success else []
            
            self.log_test("List Reports", success, response.status_code,
                         f"Found {len(data)} pending reports" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("List Reports", False, details=str(e))
            return False, []

    def test_report_vote(self):
        """Test POST /api/reports/{id}/vote"""
        if not self.session_token or not hasattr(self, 'report_id') or not self.report_id:
            self.log_test("Vote on Report", False, details="No session token or report_id available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            vote_payload = {'vote': 'up'}
            response = requests.post(f"{self.api_url}/reports/{self.report_id}/vote", headers=headers, json=vote_payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Vote on Report", success, response.status_code,
                         f"Votes: {data.get('votes_up', 0)} up, {data.get('votes_down', 0)} down" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Vote on Report", False, details=str(e))
            return False, {}

    def create_test_image(self, format='JPEG', width=200, height=300):
        """Create a test image file"""
        try:
            # Create a test image
            img = Image.new('RGB', (width, height), color='red')
            img_bytes = BytesIO()
            img.save(img_bytes, format=format)
            img_bytes.seek(0)
            return img_bytes.getvalue()
        except Exception as e:
            print(f"Error creating test image: {e}")
            return None

    def test_upload_image_valid(self):
        """Test POST /api/upload with valid image"""
        try:
            # Create a test image
            image_data = self.create_test_image('JPEG')
            if not image_data:
                self.log_test("Upload Valid Image", False, details="Failed to create test image")
                return False, {}
            
            files = {'file': ('test.jpg', image_data, 'image/jpeg')}
            response = requests.post(f"{self.api_url}/upload", files=files)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            # Store uploaded filename for later testing
            if success and 'filename' in data:
                self.uploaded_filename = data['filename']
                self.uploaded_url = data['url']
            
            self.log_test("Upload Valid Image", success, response.status_code,
                         f"Filename: {data.get('filename', 'N/A')}, URL: {data.get('url', 'N/A')}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Upload Valid Image", False, details=str(e))
            return False, {}

    def test_upload_image_invalid_type(self):
        """Test POST /api/upload with invalid file type"""
        try:
            # Create a text file instead of image
            text_content = b"This is not an image"
            files = {'file': ('test.txt', text_content, 'text/plain')}
            response = requests.post(f"{self.api_url}/upload", files=files)
            success = response.status_code == 400  # Should reject non-image files
            
            self.log_test("Upload Invalid File Type", success, response.status_code,
                         "Correctly rejected non-image file" if success else f"Unexpected response: {response.text[:100]}")
            return success, {}
        except Exception as e:
            self.log_test("Upload Invalid File Type", False, details=str(e))
            return False, {}

    def test_upload_image_too_large(self):
        """Test POST /api/upload with file over 10MB"""
        try:
            # Create a large image (over 10MB)
            large_image_data = self.create_test_image('PNG', width=2000, height=3000)
            if not large_image_data:
                self.log_test("Upload Large Image", False, details="Failed to create large test image")
                return False, {}
                
            # Make it even larger by padding with zeros
            large_data = large_image_data + b'0' * (11 * 1024 * 1024)  # Add 11MB of data
            
            files = {'file': ('large_test.png', large_data, 'image/png')}
            response = requests.post(f"{self.api_url}/upload", files=files)
            success = response.status_code == 400  # Should reject large files
            
            self.log_test("Upload Large Image", success, response.status_code,
                         "Correctly rejected oversized file" if success else f"Unexpected response: {response.text[:100]}")
            return success, {}
        except Exception as e:
            self.log_test("Upload Large Image", False, details=str(e))
            return False, {}

    def test_static_file_serving(self):
        """Test GET /api/uploads/{filename} - static file serving"""
        if not hasattr(self, 'uploaded_filename') or not self.uploaded_filename:
            self.log_test("Static File Serving", False, details="No uploaded filename available")
            return False, {}
        
        try:
            # Test accessing the uploaded file
            response = requests.get(f"{self.api_url}/uploads/{self.uploaded_filename}")
            success = response.status_code == 200 and response.headers.get('content-type', '').startswith('image/')
            
            self.log_test("Static File Serving", success, response.status_code,
                         f"Served image file, Content-Type: {response.headers.get('content-type', 'N/A')}" if success else response.text[:100])
            return success, {}
        except Exception as e:
            self.log_test("Static File Serving", False, details=str(e))
            return False, {}

    def test_upload_multiple_images(self):
        """Test POST /api/upload/multiple with multiple images"""
        try:
            # Create multiple test images
            image1 = self.create_test_image('JPEG', 150, 200)
            image2 = self.create_test_image('PNG', 200, 250)
            
            if not image1 or not image2:
                self.log_test("Upload Multiple Images", False, details="Failed to create test images")
                return False, {}
            
            files = [
                ('files', ('test1.jpg', image1, 'image/jpeg')),
                ('files', ('test2.png', image2, 'image/png'))
            ]
            response = requests.post(f"{self.api_url}/upload/multiple", files=files)
            success = response.status_code == 200
            data = response.json() if success else []
            
            self.log_test("Upload Multiple Images", success, response.status_code,
                         f"Uploaded {len(data)} images" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Upload Multiple Images", False, details=str(e))
            return False, []

    def test_create_kit_with_uploaded_image(self):
        """Test creating a master kit with an uploaded image URL"""
        if not self.session_token or not hasattr(self, 'uploaded_url') or not self.uploaded_url:
            self.log_test("Create Kit with Uploaded Image", False, details="No session token or uploaded URL available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            payload = {
                'club': 'Test Upload FC',
                'season': '2024/2025',
                'kit_type': 'Home',
                'brand': 'Upload Test',
                'front_photo': self.uploaded_url,  # Use uploaded image URL
                'year': 2024
            }
            response = requests.post(f"{self.api_url}/master-kits", headers=headers, json=payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                self.uploaded_kit_id = data.get('kit_id')
            
            self.log_test("Create Kit with Uploaded Image", success, response.status_code,
                         f"Kit ID: {self.uploaded_kit_id}, Photo URL: {data.get('front_photo', 'N/A')}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Create Kit with Uploaded Image", False, details=str(e))
            return False, {}

    def test_create_version_with_uploaded_image(self):
        """Test creating a version with an uploaded image URL"""
        if not self.session_token or not hasattr(self, 'uploaded_kit_id') or not self.uploaded_kit_id:
            self.log_test("Create Version with Uploaded Image", False, details="No session token or kit ID available")
            return False, {}
        
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            payload = {
                'kit_id': self.uploaded_kit_id,
                'competition': 'Upload Test League',
                'model': 'Replica',
                'gender': 'Men',
                'front_photo': self.uploaded_url,  # Use uploaded image URL
                'back_photo': self.uploaded_url   # Use same URL for back photo
            }
            response = requests.post(f"{self.api_url}/versions", headers=headers, json=payload)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test("Create Version with Uploaded Image", success, response.status_code,
                         f"Version ID: {data.get('version_id', 'N/A')}" if success else response.text[:100])
            return success, data
        except Exception as e:
            self.log_test("Create Version with Uploaded Image", False, details=str(e))
            return False, {}

    def run_all_tests(self):
        print("=" * 60)
        print("🏟️  FOOTBALL JERSEY CATALOG API TESTING - PHASE 3 (IMAGE UPLOAD)")
        print("=" * 60)
        print(f"Testing API at: {self.api_url}")
        
        # Test public endpoints first
        self.test_seed_endpoint()
        self.test_stats_endpoint() 
        self.test_filters_endpoint()
        self.test_master_kits_list()
        self.test_master_kit_detail()
        self.test_version_detail()
        self.test_version_estimates()
        
        # Test image upload endpoints (Phase 3 features)
        print(f"\n📸 TESTING IMAGE UPLOAD FEATURES")
        self.test_upload_image_valid()
        self.test_upload_image_invalid_type()
        self.test_upload_image_too_large()
        self.test_static_file_serving()
        self.test_upload_multiple_images()
        
        # Create test session for authenticated endpoints
        if self.create_test_session():
            # Basic auth tests
            self.test_auth_me()
            self.test_collections_get()
            self.test_collection_add()
            self.test_review_create()
            
            # Phase 2 features
            self.test_collection_update()
            self.test_collection_stats()
            self.test_category_stats()
            self.test_profile_update()
            self.test_submissions_create()
            self.test_submissions_list()
            self.test_submission_vote()
            self.test_reports_create()
            self.test_reports_list()
            self.test_report_vote()
            
            # Test integration with uploaded images
            print(f"\n🔗 TESTING INTEGRATION WITH UPLOADED IMAGES")
            self.test_create_kit_with_uploaded_image()
            self.test_create_version_with_uploaded_image()
            
            # Cleanup
            self.test_collection_remove()
        
        print("\n" + "=" * 60)
        print(f"🏁 TESTING COMPLETE")
        print(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "No tests run")
        print("=" * 60)
        
        return self.tests_passed == self.tests_run

def main():
    tester = FootballJerseyAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())