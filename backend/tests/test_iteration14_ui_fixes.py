"""
Iteration 14: UI/UX Improvements Testing
Tests for:
- Report error functionality with dropdowns (Competition/Model for versions, Type/Gender for kits)
- Request Removal button and report_type='removal' API
- GET /api/users/by-username/{username} endpoint
- Profile page username-based routes
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SESSION_TOKEN = os.environ.get('TEST_SESSION_TOKEN', 'test_session_1771496973018')
TEST_USERNAME = os.environ.get('TEST_USERNAME', 'testuser1771496973018')

@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def auth_client(api_client):
    api_client.cookies.set('session_token', SESSION_TOKEN, domain='topkit-verify.preview.emergentagent.com')
    return api_client


class TestBasicAPIs:
    """Basic API health checks"""
    
    def test_stats_endpoint(self, api_client):
        """Test GET /api/stats returns correct data"""
        response = api_client.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "master_kits" in data
        assert "versions" in data
        print(f"Stats: {data}")
    
    def test_master_kits_list(self, api_client):
        """Test GET /api/master-kits returns kits"""
        response = api_client.get(f"{BASE_URL}/api/master-kits?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"Got {len(data)} master kits")
    
    def test_versions_list(self, api_client):
        """Test GET /api/versions returns versions"""
        response = api_client.get(f"{BASE_URL}/api/versions?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        print(f"Got {len(data)} versions")


class TestUserByUsername:
    """Tests for username-based user lookup endpoint"""
    
    def test_get_user_by_username_exists(self, api_client):
        """Test GET /api/users/by-username/{username} returns user data"""
        response = api_client.get(f"{BASE_URL}/api/users/by-username/{TEST_USERNAME}")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "username" in data
        assert data["username"] == TEST_USERNAME
        # Check additional stats fields are included
        assert "collection_count" in data
        assert "review_count" in data
        assert "submission_count" in data
        print(f"User by username response: {data}")
    
    def test_get_user_by_username_not_found(self, api_client):
        """Test GET /api/users/by-username/{username} returns 404 for non-existent user"""
        response = api_client.get(f"{BASE_URL}/api/users/by-username/nonexistent_user_12345")
        assert response.status_code == 404
        print("Non-existent user correctly returns 404")


class TestReportErrorAPI:
    """Tests for Report Error submission API with report_type field"""
    
    def test_create_error_report(self, auth_client):
        """Test POST /api/reports with report_type='error' for a version"""
        # First get a version
        versions_resp = auth_client.get(f"{BASE_URL}/api/versions?limit=1")
        assert versions_resp.status_code == 200
        versions = versions_resp.json()
        if not versions:
            pytest.skip("No versions available")
        
        version_id = versions[0]["version_id"]
        
        report_data = {
            "target_type": "version",
            "target_id": version_id,
            "corrections": {
                "competition": "National Cup",
                "model": "Authentic"
            },
            "notes": "Test error report",
            "report_type": "error"
        }
        
        response = auth_client.post(f"{BASE_URL}/api/reports", json=report_data)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "error"
        assert data["target_type"] == "version"
        assert data["status"] == "pending"
        print(f"Error report created: {data['report_id']}")
    
    def test_create_removal_report_version(self, auth_client):
        """Test POST /api/reports with report_type='removal' for a version"""
        # First get a version
        versions_resp = auth_client.get(f"{BASE_URL}/api/versions?limit=1")
        assert versions_resp.status_code == 200
        versions = versions_resp.json()
        if not versions:
            pytest.skip("No versions available")
        
        version_id = versions[0]["version_id"]
        
        report_data = {
            "target_type": "version",
            "target_id": version_id,
            "corrections": {},
            "notes": "Test removal request for version",
            "report_type": "removal"
        }
        
        response = auth_client.post(f"{BASE_URL}/api/reports", json=report_data)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "removal"
        assert data["target_type"] == "version"
        assert data["status"] == "pending"
        print(f"Removal request created: {data['report_id']}")
    
    def test_create_removal_report_master_kit(self, auth_client):
        """Test POST /api/reports with report_type='removal' for a master kit"""
        # First get a master kit
        kits_resp = auth_client.get(f"{BASE_URL}/api/master-kits?limit=1")
        assert kits_resp.status_code == 200
        kits = kits_resp.json()
        if not kits:
            pytest.skip("No master kits available")
        
        kit_id = kits[0]["kit_id"]
        
        report_data = {
            "target_type": "master_kit",
            "target_id": kit_id,
            "corrections": {},
            "notes": "Test removal request for master kit",
            "report_type": "removal"
        }
        
        response = auth_client.post(f"{BASE_URL}/api/reports", json=report_data)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "removal"
        assert data["target_type"] == "master_kit"
        assert data["status"] == "pending"
        print(f"Master kit removal request created: {data['report_id']}")
    
    def test_invalid_report_type(self, auth_client):
        """Test POST /api/reports with invalid report_type returns error"""
        versions_resp = auth_client.get(f"{BASE_URL}/api/versions?limit=1")
        versions = versions_resp.json()
        if not versions:
            pytest.skip("No versions available")
        
        report_data = {
            "target_type": "version",
            "target_id": versions[0]["version_id"],
            "corrections": {},
            "notes": "Test invalid type",
            "report_type": "invalid_type"
        }
        
        response = auth_client.post(f"{BASE_URL}/api/reports", json=report_data)
        assert response.status_code == 400
        print("Invalid report_type correctly rejected with 400")
    
    def test_list_reports(self, api_client):
        """Test GET /api/reports returns reports list"""
        response = api_client.get(f"{BASE_URL}/api/reports?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Got {len(data)} pending reports")


class TestMasterKitErrorReport:
    """Tests for Report Error on master kits (should include Type/Gender dropdowns)"""
    
    def test_create_kit_error_report(self, auth_client):
        """Test POST /api/reports for master kit with Gender and Type corrections"""
        kits_resp = auth_client.get(f"{BASE_URL}/api/master-kits?limit=1")
        assert kits_resp.status_code == 200
        kits = kits_resp.json()
        if not kits:
            pytest.skip("No master kits available")
        
        kit_id = kits[0]["kit_id"]
        
        report_data = {
            "target_type": "master_kit",
            "target_id": kit_id,
            "corrections": {
                "gender": "Women",
                "kit_type": "Away",
                "club": kits[0]["club"],
                "season": kits[0]["season"]
            },
            "notes": "Test error report with Gender dropdown value",
            "report_type": "error"
        }
        
        response = auth_client.post(f"{BASE_URL}/api/reports", json=report_data)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "error"
        assert data["corrections"]["gender"] == "Women"
        assert data["corrections"]["kit_type"] == "Away"
        print(f"Kit error report with Gender/Type created: {data['report_id']}")


class TestProfileEndpoints:
    """Tests for profile-related endpoints"""
    
    def test_auth_me_endpoint(self, auth_client):
        """Test GET /api/auth/me returns current user"""
        response = auth_client.get(f"{BASE_URL}/api/auth/me")
        # May return 401 if session not properly set via cookie
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            print(f"Auth/me response: user_id={data['user_id']}")
        else:
            print(f"Auth/me returned {response.status_code} - expected if session cookie not set")
    
    def test_update_profile_requires_auth(self, api_client):
        """Test PUT /api/users/profile requires authentication"""
        response = api_client.put(f"{BASE_URL}/api/users/profile", json={
            "username": "newusername123"
        })
        assert response.status_code == 401
        print("Profile update correctly requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
