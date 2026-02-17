import requests
import sys
import json
import subprocess
from datetime import datetime

class FootballJerseyAPITester:
    def __init__(self, base_url="https://squad-archive-1.preview.emergentagent.com"):
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
        if not self.session_token:
            self.log_test("Update Collection Item", False, details="No session token available")
            return False, {}
        
        # First add an item to collection to update
        try:
            headers = {'Authorization': f'Bearer {self.session_token}', 'Content-Type': 'application/json'}
            payload = {
                'version_id': self.version_id,
                'category': 'Test Category',
                'condition': 'Very good',
                'size': 'L',
                'value_estimate': 150.00,
                'notes': 'Test item for update testing'
            }
            response = requests.post(f"{self.api_url}/collections", headers=headers, json=payload)
            if response.status_code != 200:
                self.log_test("Update Collection Item (Setup)", False, response.status_code, "Failed to create item for update")
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
                         f"Updated item with new condition/size/value" if success else update_response.text[:100])
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

    def run_all_tests(self):
        print("=" * 60)
        print("🏟️  FOOTBALL JERSEY CATALOG API TESTING")
        print("=" * 60)
        print(f"Testing API at: {self.api_url}")
        
        # Test public endpoints first
        self.test_seed_endpoint()
        self.test_stats_endpoint() 
        self.test_filters_endpoint()
        self.test_master_kits_list()
        self.test_master_kit_detail()
        self.test_version_detail()
        
        # Create test session for authenticated endpoints
        if self.create_test_session():
            self.test_auth_me()
            self.test_collections_get()
            self.test_collection_add()
            self.test_review_create()
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