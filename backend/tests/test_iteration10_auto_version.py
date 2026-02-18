"""
Tests for Iteration 10 features:
1. Auto-version creation when Master Kit is created (POST /api/master-kits)
2. Auto-version creation when master_kit submission is approved
3. Verify default version values: competition='National Championship', model='Replica'
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test session (we'll create this dynamically)
TEST_SESSION_TOKEN = None
TEST_USER_ID = None

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="module")
def test_user_session(api_client):
    """Create test user and session via MongoDB for authenticated endpoints"""
    import subprocess
    import json
    
    timestamp = int(time.time() * 1000)
    user_id = f"test_user_{timestamp}"
    session_token = f"test_session_{timestamp}"
    
    # Create test user and session
    mongo_script = f'''
    use test_database;
    db.users.insertOne({{
        user_id: "{user_id}",
        email: "testuser{timestamp}@example.com",
        name: "Test User",
        picture: "",
        role: "user",
        created_at: new Date().toISOString()
    }});
    db.user_sessions.insertOne({{
        user_id: "{user_id}",
        session_token: "{session_token}",
        expires_at: new Date(Date.now() + 7*24*60*60*1000).toISOString(),
        created_at: new Date().toISOString()
    }});
    db.collections.insertOne({{
        collection_id: "test_col_{timestamp}",
        user_id: "{user_id}",
        version_id: "dummy_version",
        category: "Test",
        added_at: new Date().toISOString()
    }});
    print("created");
    '''
    result = subprocess.run(['mongosh', '--quiet', '--eval', mongo_script], capture_output=True, text=True)
    
    yield {"user_id": user_id, "session_token": session_token}
    
    # Cleanup
    cleanup_script = f'''
    use test_database;
    db.users.deleteOne({{ user_id: "{user_id}" }});
    db.user_sessions.deleteOne({{ session_token: "{session_token}" }});
    db.collections.deleteMany({{ user_id: "{user_id}" }});
    db.master_kits.deleteMany({{ created_by: "{user_id}" }});
    db.versions.deleteMany({{ created_by: "{user_id}" }});
    db.submissions.deleteMany({{ submitted_by: "{user_id}" }});
    '''
    subprocess.run(['mongosh', '--quiet', '--eval', cleanup_script], capture_output=True, text=True)

@pytest.fixture(scope="module")
def moderator_session(api_client):
    """Create moderator user and session for testing submission approval"""
    import subprocess
    
    timestamp = int(time.time() * 1000) + 1
    user_id = f"mod_user_{timestamp}"
    session_token = f"mod_session_{timestamp}"
    
    # Create moderator user and session
    mongo_script = f'''
    use test_database;
    db.users.insertOne({{
        user_id: "{user_id}",
        email: "topkitfr@gmail.com",
        name: "Moderator User",
        picture: "",
        role: "moderator",
        created_at: new Date().toISOString()
    }});
    db.user_sessions.insertOne({{
        user_id: "{user_id}",
        session_token: "{session_token}",
        expires_at: new Date(Date.now() + 7*24*60*60*1000).toISOString(),
        created_at: new Date().toISOString()
    }});
    print("created");
    '''
    result = subprocess.run(['mongosh', '--quiet', '--eval', mongo_script], capture_output=True, text=True)
    
    yield {"user_id": user_id, "session_token": session_token}
    
    # Cleanup
    cleanup_script = f'''
    use test_database;
    db.users.deleteOne({{ user_id: "{user_id}" }});
    db.user_sessions.deleteOne({{ session_token: "{session_token}" }});
    '''
    subprocess.run(['mongosh', '--quiet', '--eval', cleanup_script], capture_output=True, text=True)


class TestAutoVersionCreation:
    """Test that creating a Master Kit automatically creates a default Version"""
    
    def test_create_master_kit_creates_default_version(self, api_client, test_user_session):
        """POST /api/master-kits should auto-create a default Version"""
        # Create a new master kit
        kit_data = {
            "club": "TEST_AutoVersion_FC",
            "season": "2024/2025",
            "kit_type": "Home",
            "brand": "TestBrand",
            "front_photo": "https://example.com/test.jpg",
            "league": "Test League",
            "design": "Classic",
            "sponsor": "Test Sponsor",
            "gender": "Man"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/master-kits",
            json=kit_data,
            headers={"Authorization": f"Bearer {test_user_session['session_token']}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        kit = response.json()
        kit_id = kit.get("kit_id")
        assert kit_id is not None, "Kit ID should be returned"
        
        # Response should show version_count = 1
        assert kit.get("version_count") == 1, f"Expected version_count=1, got {kit.get('version_count')}"
        
        # Verify default version was created by fetching the kit details
        detail_response = api_client.get(f"{BASE_URL}/api/master-kits/{kit_id}")
        assert detail_response.status_code == 200
        
        kit_detail = detail_response.json()
        versions = kit_detail.get("versions", [])
        
        assert len(versions) == 1, f"Expected 1 version, got {len(versions)}"
        
        default_version = versions[0]
        assert default_version.get("competition") == "National Championship", \
            f"Expected competition='National Championship', got '{default_version.get('competition')}'"
        assert default_version.get("model") == "Replica", \
            f"Expected model='Replica', got '{default_version.get('model')}'"
        assert default_version.get("front_photo") == kit_data["front_photo"], \
            "Default version should inherit front_photo from master kit"
        
        # Cleanup
        import subprocess
        cleanup_script = f'''
        use test_database;
        db.master_kits.deleteOne({{ kit_id: "{kit_id}" }});
        db.versions.deleteMany({{ kit_id: "{kit_id}" }});
        '''
        subprocess.run(['mongosh', '--quiet', '--eval', cleanup_script], capture_output=True, text=True)
        
        print(f"PASS: Master kit creation auto-created default version with competition='National Championship', model='Replica'")

    def test_default_version_has_empty_sku_and_ean(self, api_client, test_user_session):
        """Verify default version has empty SKU and EAN codes"""
        kit_data = {
            "club": "TEST_EmptySKU_FC",
            "season": "2025/2026",
            "kit_type": "Away",
            "brand": "TestBrand2",
            "front_photo": "https://example.com/test2.jpg"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/master-kits",
            json=kit_data,
            headers={"Authorization": f"Bearer {test_user_session['session_token']}"}
        )
        
        assert response.status_code == 200
        kit_id = response.json().get("kit_id")
        
        # Get the default version
        detail_response = api_client.get(f"{BASE_URL}/api/master-kits/{kit_id}")
        versions = detail_response.json().get("versions", [])
        
        assert len(versions) == 1
        default_version = versions[0]
        
        assert default_version.get("sku_code") == "", f"Expected empty sku_code, got '{default_version.get('sku_code')}'"
        assert default_version.get("ean_code") == "", f"Expected empty ean_code, got '{default_version.get('ean_code')}'"
        
        # Cleanup
        import subprocess
        subprocess.run(['mongosh', '--quiet', '--eval', f'''
        use test_database;
        db.master_kits.deleteOne({{ kit_id: "{kit_id}" }});
        db.versions.deleteMany({{ kit_id: "{kit_id}" }});
        '''], capture_output=True, text=True)
        
        print("PASS: Default version has empty SKU and EAN codes")


class TestSubmissionApprovalAutoVersion:
    """Test that approving a master_kit submission auto-creates default version"""
    
    def test_master_kit_submission_approval_creates_version(self, api_client, test_user_session, moderator_session):
        """When a master_kit submission is approved, it should auto-create a default version"""
        # Create a submission for a new master kit
        submission_data = {
            "submission_type": "master_kit",
            "data": {
                "club": "TEST_SubmissionAutoVersion_FC",
                "season": "2023/2024",
                "kit_type": "Third",
                "brand": "SubmissionBrand",
                "front_photo": "https://example.com/submission.jpg",
                "league": "Submission League",
                "design": "Modern",
                "sponsor": "Sub Sponsor",
                "gender": "Woman"
            }
        }
        
        # Create submission as regular user
        sub_response = api_client.post(
            f"{BASE_URL}/api/submissions",
            json=submission_data,
            headers={"Authorization": f"Bearer {test_user_session['session_token']}"}
        )
        
        assert sub_response.status_code == 200, f"Failed to create submission: {sub_response.text}"
        submission = sub_response.json()
        submission_id = submission.get("submission_id")
        
        assert submission.get("status") == "pending"
        
        # Approve as moderator (moderator vote has weight 5, instant approval)
        vote_response = api_client.post(
            f"{BASE_URL}/api/submissions/{submission_id}/vote",
            json={"vote": "up"},
            headers={"Authorization": f"Bearer {moderator_session['session_token']}"}
        )
        
        assert vote_response.status_code == 200, f"Failed to vote: {vote_response.text}"
        updated_submission = vote_response.json()
        
        # Should be approved now
        assert updated_submission.get("status") == "approved", \
            f"Expected status='approved', got '{updated_submission.get('status')}'"
        
        # Find the created kit
        import subprocess
        import json
        find_script = f'''
        use test_database;
        var kit = db.master_kits.findOne({{ club: "TEST_SubmissionAutoVersion_FC" }});
        if (kit) {{
            var versions = db.versions.find({{ kit_id: kit.kit_id }}).toArray();
            print(JSON.stringify({{ kit_id: kit.kit_id, version_count: versions.length, versions: versions }}));
        }} else {{
            print("null");
        }}
        '''
        result = subprocess.run(['mongosh', '--quiet', '--eval', find_script], capture_output=True, text=True)
        
        output = result.stdout.strip()
        if output and output != "null":
            data = json.loads(output)
            assert data["version_count"] == 1, f"Expected 1 version after approval, got {data['version_count']}"
            
            version = data["versions"][0]
            assert version.get("competition") == "National Championship"
            assert version.get("model") == "Replica"
            assert version.get("front_photo") == submission_data["data"]["front_photo"]
            
            print("PASS: Submission approval auto-created default version")
            
            # Cleanup
            kit_id = data["kit_id"]
            subprocess.run(['mongosh', '--quiet', '--eval', f'''
            use test_database;
            db.master_kits.deleteOne({{ kit_id: "{kit_id}" }});
            db.versions.deleteMany({{ kit_id: "{kit_id}" }});
            db.submissions.deleteOne({{ submission_id: "{submission_id}" }});
            '''], capture_output=True, text=True)
        else:
            pytest.fail("Kit was not created after submission approval")


class TestVersionDetailFields:
    """Test that Version API returns all fields properly"""
    
    def test_version_returns_all_fields(self, api_client, test_user_session):
        """GET /api/versions/{id} should return all fields including empty ones"""
        # First create a kit to get a version
        kit_data = {
            "club": "TEST_VersionFields_FC",
            "season": "2024/2025",
            "kit_type": "Home",
            "brand": "TestBrand",
            "front_photo": "https://example.com/test.jpg"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/master-kits",
            json=kit_data,
            headers={"Authorization": f"Bearer {test_user_session['session_token']}"}
        )
        assert response.status_code == 200
        kit_id = response.json().get("kit_id")
        
        # Get kit detail to find version
        detail_response = api_client.get(f"{BASE_URL}/api/master-kits/{kit_id}")
        versions = detail_response.json().get("versions", [])
        assert len(versions) > 0
        
        version_id = versions[0].get("version_id")
        
        # Get version detail
        ver_response = api_client.get(f"{BASE_URL}/api/versions/{version_id}")
        assert ver_response.status_code == 200
        
        version = ver_response.json()
        
        # Verify all fields are present
        expected_fields = ["version_id", "kit_id", "competition", "model", "sku_code", "ean_code", 
                          "front_photo", "back_photo", "collection_count", "avg_rating", "review_count"]
        
        for field in expected_fields:
            assert field in version, f"Field '{field}' should be present in version response"
        
        print(f"PASS: Version detail returns all expected fields: {expected_fields}")
        
        # Cleanup
        import subprocess
        subprocess.run(['mongosh', '--quiet', '--eval', f'''
        use test_database;
        db.master_kits.deleteOne({{ kit_id: "{kit_id}" }});
        db.versions.deleteMany({{ kit_id: "{kit_id}" }});
        '''], capture_output=True, text=True)


class TestMasterKitDetailFields:
    """Test that Master Kit API returns all fields properly"""
    
    def test_master_kit_returns_all_fields(self, api_client, test_user_session):
        """GET /api/master-kits/{id} should return all fields including empty ones"""
        # Create a kit with some empty fields
        kit_data = {
            "club": "TEST_KitFields_FC",
            "season": "2024/2025",
            "kit_type": "Home",
            "brand": "TestBrand",
            "front_photo": "https://example.com/test.jpg"
            # league, design, sponsor, gender are intentionally not provided
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/master-kits",
            json=kit_data,
            headers={"Authorization": f"Bearer {test_user_session['session_token']}"}
        )
        assert response.status_code == 200
        kit_id = response.json().get("kit_id")
        
        # Get kit detail
        detail_response = api_client.get(f"{BASE_URL}/api/master-kits/{kit_id}")
        assert detail_response.status_code == 200
        
        kit = detail_response.json()
        
        # Verify all fields are present (even if empty)
        expected_fields = ["kit_id", "club", "season", "kit_type", "brand", "front_photo",
                          "league", "design", "sponsor", "gender", "version_count", "avg_rating", "versions"]
        
        for field in expected_fields:
            assert field in kit, f"Field '{field}' should be present in kit response"
        
        # Fields that weren't provided should be empty strings or defaults
        assert kit.get("league") == "", f"Expected empty league, got '{kit.get('league')}'"
        assert kit.get("design") == "", f"Expected empty design, got '{kit.get('design')}'"
        assert kit.get("sponsor") == "", f"Expected empty sponsor, got '{kit.get('sponsor')}'"
        assert kit.get("gender") == "", f"Expected empty gender, got '{kit.get('gender')}'"
        
        print(f"PASS: Master kit detail returns all expected fields with proper defaults")
        
        # Cleanup
        import subprocess
        subprocess.run(['mongosh', '--quiet', '--eval', f'''
        use test_database;
        db.master_kits.deleteOne({{ kit_id: "{kit_id}" }});
        db.versions.deleteMany({{ kit_id: "{kit_id}" }});
        '''], capture_output=True, text=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
