"""
Iteration 9 Tests: Moderator Privileges, Contribution Forms, and Detailed Views

Tests:
1. Moderator role assignment for topkitfr@gmail.com
2. Moderator single-vote approval for submissions
3. Moderator single-vote approval for reports
4. /api/auth/me returns role field
5. Vote weight = 5 for moderator upvotes
"""

import pytest
import requests
import os
import uuid
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# MongoDB connection for direct test data setup
from pymongo import MongoClient
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]


class TestModeratorRole:
    """Test moderator role assignment and detection"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test data before each test"""
        self.test_prefix = f"TEST_MOD_{uuid.uuid4().hex[:8]}"
        self.regular_user_id = f"test_user_{uuid.uuid4().hex[:12]}"
        self.moderator_user_id = f"test_mod_{uuid.uuid4().hex[:12]}"
        self.regular_session = f"test_session_{uuid.uuid4().hex[:16]}"
        self.moderator_session = f"test_modsession_{uuid.uuid4().hex[:16]}"
        
        # Create regular user
        db.users.insert_one({
            "user_id": self.regular_user_id,
            "email": f"regular_{self.test_prefix}@example.com",
            "name": "Regular Test User",
            "role": "user",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Create session for regular user
        db.user_sessions.insert_one({
            "user_id": self.regular_user_id,
            "session_token": self.regular_session,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Create moderator user (with topkitfr@gmail.com email)
        db.users.insert_one({
            "user_id": self.moderator_user_id,
            "email": "topkitfr@gmail.com",
            "name": "Moderator Test User",
            "role": "moderator",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Create session for moderator user
        db.user_sessions.insert_one({
            "user_id": self.moderator_user_id,
            "session_token": self.moderator_session,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Add a jersey to moderator's collection (required to vote)
        # First create a test kit and version
        self.test_kit_id = f"kit_{uuid.uuid4().hex[:12]}"
        self.test_version_id = f"ver_{uuid.uuid4().hex[:12]}"
        
        db.master_kits.insert_one({
            "kit_id": self.test_kit_id,
            "club": f"{self.test_prefix} FC",
            "season": "2024/2025",
            "kit_type": "Home",
            "brand": "Nike",
            "front_photo": "https://example.com/photo.jpg",
            "league": "Test League",
            "design": "Test Design",
            "sponsor": "Test Sponsor",
            "gender": "Man",
            "created_by": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        db.versions.insert_one({
            "version_id": self.test_version_id,
            "kit_id": self.test_kit_id,
            "competition": "National Championship",
            "model": "Replica",
            "created_by": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Add version to regular user's collection (needed to vote)
        db.collections.insert_one({
            "collection_id": f"col_{uuid.uuid4().hex[:12]}",
            "user_id": self.regular_user_id,
            "version_id": self.test_version_id,
            "category": "General",
            "added_at": datetime.now(timezone.utc).isoformat()
        })
        
        yield
        
        # Cleanup
        db.users.delete_many({"user_id": {"$in": [self.regular_user_id, self.moderator_user_id]}})
        db.user_sessions.delete_many({"session_token": {"$in": [self.regular_session, self.moderator_session]}})
        db.master_kits.delete_many({"kit_id": self.test_kit_id})
        db.versions.delete_many({"version_id": self.test_version_id})
        db.collections.delete_many({"version_id": self.test_version_id})
        db.submissions.delete_many({"data.club": {"$regex": self.test_prefix}})
        db.reports.delete_many({"target_id": self.test_kit_id})

    def test_auth_me_returns_role_for_regular_user(self):
        """Test /api/auth/me returns role field for regular user"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {self.regular_session}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "role" in data, "Role field missing from /api/auth/me response"
        assert data["role"] == "user", f"Expected role 'user', got '{data['role']}'"
        print(f"✓ /api/auth/me returns role='user' for regular user")

    def test_auth_me_returns_moderator_role(self):
        """Test /api/auth/me returns moderator role for topkitfr@gmail.com"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {self.moderator_session}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "role" in data, "Role field missing from /api/auth/me response"
        assert data["role"] == "moderator", f"Expected role 'moderator', got '{data['role']}'"
        print(f"✓ /api/auth/me returns role='moderator' for topkitfr@gmail.com")


class TestModeratorSubmissionVoting:
    """Test moderator single-vote approval for submissions"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test data before each test"""
        self.test_prefix = f"TEST_SUB_{uuid.uuid4().hex[:8]}"
        self.moderator_user_id = f"test_mod_{uuid.uuid4().hex[:12]}"
        self.moderator_session = f"test_modsession_{uuid.uuid4().hex[:16]}"
        self.regular_user_id = f"test_user_{uuid.uuid4().hex[:12]}"
        self.regular_session = f"test_session_{uuid.uuid4().hex[:16]}"
        self.submitter_user_id = f"test_submitter_{uuid.uuid4().hex[:12]}"
        
        # Create moderator user
        db.users.insert_one({
            "user_id": self.moderator_user_id,
            "email": "topkitfr@gmail.com",
            "name": "Moderator",
            "role": "moderator",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        db.user_sessions.insert_one({
            "user_id": self.moderator_user_id,
            "session_token": self.moderator_session,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Create regular user with collection (needed to vote)
        db.users.insert_one({
            "user_id": self.regular_user_id,
            "email": f"regular_{self.test_prefix}@example.com",
            "name": "Regular User",
            "role": "user",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        db.user_sessions.insert_one({
            "user_id": self.regular_user_id,
            "session_token": self.regular_session,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Create a test version for regular user's collection
        self.test_version_id = f"ver_{uuid.uuid4().hex[:12]}"
        self.test_kit_id = f"kit_{uuid.uuid4().hex[:12]}"
        
        db.master_kits.insert_one({
            "kit_id": self.test_kit_id,
            "club": f"{self.test_prefix} FC",
            "season": "2024/2025",
            "kit_type": "Home",
            "brand": "Nike",
            "created_by": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        db.versions.insert_one({
            "version_id": self.test_version_id,
            "kit_id": self.test_kit_id,
            "competition": "National Championship",
            "model": "Replica",
            "created_by": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        db.collections.insert_one({
            "collection_id": f"col_{uuid.uuid4().hex[:12]}",
            "user_id": self.regular_user_id,
            "version_id": self.test_version_id,
            "category": "General",
            "added_at": datetime.now(timezone.utc).isoformat()
        })
        
        yield
        
        # Cleanup
        db.users.delete_many({"user_id": {"$in": [self.moderator_user_id, self.regular_user_id, self.submitter_user_id]}})
        db.user_sessions.delete_many({"session_token": {"$in": [self.moderator_session, self.regular_session]}})
        db.master_kits.delete_many({"kit_id": self.test_kit_id})
        db.versions.delete_many({"version_id": self.test_version_id})
        db.collections.delete_many({"version_id": self.test_version_id})
        db.submissions.delete_many({"data.club": {"$regex": self.test_prefix}})

    def test_moderator_single_vote_approves_submission(self):
        """Test that moderator upvote instantly approves submission (vote_weight=5)"""
        # Create a pending submission
        submission_id = f"sub_{uuid.uuid4().hex[:12]}"
        db.submissions.insert_one({
            "submission_id": submission_id,
            "submission_type": "master_kit",
            "data": {
                "club": f"{self.test_prefix} Club",
                "season": "2024/2025",
                "kit_type": "Home",
                "brand": "Adidas",
                "front_photo": "https://example.com/photo.jpg"
            },
            "submitted_by": self.submitter_user_id,
            "submitter_name": "Submitter",
            "status": "pending",
            "votes_up": 0,
            "votes_down": 0,
            "voters": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Moderator votes up
        response = requests.post(
            f"{BASE_URL}/api/submissions/{submission_id}/vote",
            headers={"Authorization": f"Bearer {self.moderator_session}"},
            json={"vote": "up"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check that votes_up is 5 (moderator vote weight)
        assert data["votes_up"] == 5, f"Expected votes_up=5 (moderator weight), got {data['votes_up']}"
        # Check that submission is approved
        assert data["status"] == "approved", f"Expected status='approved', got '{data['status']}'"
        
        print(f"✓ Moderator single upvote approves submission (votes_up={data['votes_up']}, status={data['status']})")

    def test_regular_user_vote_weight_is_one(self):
        """Test that regular user vote has weight of 1"""
        # Create a pending submission
        submission_id = f"sub_{uuid.uuid4().hex[:12]}"
        db.submissions.insert_one({
            "submission_id": submission_id,
            "submission_type": "master_kit",
            "data": {
                "club": f"{self.test_prefix} Club2",
                "season": "2024/2025",
                "kit_type": "Away",
                "brand": "Nike",
                "front_photo": "https://example.com/photo.jpg"
            },
            "submitted_by": self.submitter_user_id,
            "submitter_name": "Submitter",
            "status": "pending",
            "votes_up": 0,
            "votes_down": 0,
            "voters": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Regular user votes up
        response = requests.post(
            f"{BASE_URL}/api/submissions/{submission_id}/vote",
            headers={"Authorization": f"Bearer {self.regular_session}"},
            json={"vote": "up"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check that votes_up is 1 (regular user weight)
        assert data["votes_up"] == 1, f"Expected votes_up=1 (regular user weight), got {data['votes_up']}"
        # Check that submission is still pending (needs 5 votes)
        assert data["status"] == "pending", f"Expected status='pending', got '{data['status']}'"
        
        print(f"✓ Regular user vote has weight=1 (votes_up={data['votes_up']}, status={data['status']})")


class TestModeratorReportVoting:
    """Test moderator single-vote approval for reports"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test data before each test"""
        self.test_prefix = f"TEST_REP_{uuid.uuid4().hex[:8]}"
        self.moderator_user_id = f"test_mod_{uuid.uuid4().hex[:12]}"
        self.moderator_session = f"test_modsession_{uuid.uuid4().hex[:16]}"
        self.reporter_user_id = f"test_reporter_{uuid.uuid4().hex[:12]}"
        
        # Create test kit to report on
        self.test_kit_id = f"kit_{uuid.uuid4().hex[:12]}"
        db.master_kits.insert_one({
            "kit_id": self.test_kit_id,
            "club": f"{self.test_prefix} FC",
            "season": "2024/2025",
            "kit_type": "Home",
            "brand": "Nike",
            "design": "Original Design",
            "sponsor": "Original Sponsor",
            "league": "Original League",
            "gender": "Man",
            "created_by": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Create moderator user
        db.users.insert_one({
            "user_id": self.moderator_user_id,
            "email": "topkitfr@gmail.com",
            "name": "Moderator",
            "role": "moderator",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        db.user_sessions.insert_one({
            "user_id": self.moderator_user_id,
            "session_token": self.moderator_session,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        yield
        
        # Cleanup
        db.users.delete_many({"user_id": {"$in": [self.moderator_user_id, self.reporter_user_id]}})
        db.user_sessions.delete_many({"session_token": self.moderator_session})
        db.master_kits.delete_many({"kit_id": self.test_kit_id})
        db.reports.delete_many({"target_id": self.test_kit_id})

    def test_moderator_single_vote_approves_report(self):
        """Test that moderator upvote instantly approves report (vote_weight=5)"""
        # Create a pending report
        report_id = f"rep_{uuid.uuid4().hex[:12]}"
        db.reports.insert_one({
            "report_id": report_id,
            "target_type": "master_kit",
            "target_id": self.test_kit_id,
            "original_data": {
                "club": f"{self.test_prefix} FC",
                "season": "2024/2025",
                "kit_type": "Home",
                "brand": "Nike",
                "design": "Original Design"
            },
            "corrections": {
                "design": "Corrected Design"
            },
            "notes": "Design correction",
            "reported_by": self.reporter_user_id,
            "reporter_name": "Reporter",
            "status": "pending",
            "votes_up": 0,
            "votes_down": 0,
            "voters": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Moderator votes up
        response = requests.post(
            f"{BASE_URL}/api/reports/{report_id}/vote",
            headers={"Authorization": f"Bearer {self.moderator_session}"},
            json={"vote": "up"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check that votes_up is 5 (moderator vote weight)
        assert data["votes_up"] == 5, f"Expected votes_up=5 (moderator weight), got {data['votes_up']}"
        # Check that report is approved
        assert data["status"] == "approved", f"Expected status='approved', got '{data['status']}'"
        
        # Verify the correction was applied to the master kit
        kit = db.master_kits.find_one({"kit_id": self.test_kit_id})
        assert kit["design"] == "Corrected Design", f"Expected design='Corrected Design', got '{kit['design']}'"
        
        print(f"✓ Moderator single upvote approves report (votes_up={data['votes_up']}, status={data['status']})")
        print(f"✓ Correction applied to master kit: design='{kit['design']}'")


class TestMasterKitFields:
    """Test Master Kit creation with all required fields"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test data"""
        self.test_prefix = f"TEST_KIT_{uuid.uuid4().hex[:8]}"
        self.user_id = f"test_user_{uuid.uuid4().hex[:12]}"
        self.session_token = f"test_session_{uuid.uuid4().hex[:16]}"
        
        # Create test user
        db.users.insert_one({
            "user_id": self.user_id,
            "email": f"{self.test_prefix}@example.com",
            "name": "Test User",
            "role": "user",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        db.user_sessions.insert_one({
            "user_id": self.user_id,
            "session_token": self.session_token,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        yield
        
        # Cleanup
        db.users.delete_many({"user_id": self.user_id})
        db.user_sessions.delete_many({"session_token": self.session_token})
        db.master_kits.delete_many({"club": {"$regex": self.test_prefix}})

    def test_create_master_kit_with_all_fields(self):
        """Test POST /api/master-kits accepts all fields: Team, Season, League, Type, Brand, Design, Sponsor, Gender"""
        kit_data = {
            "club": f"{self.test_prefix} Test Club",
            "season": "2024/2025",
            "league": "La Liga",
            "kit_type": "Home",
            "brand": "Nike",
            "design": "Classic stripes",
            "sponsor": "Emirates",
            "gender": "Man",
            "front_photo": "https://example.com/photo.jpg"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/master-kits",
            headers={"Authorization": f"Bearer {self.session_token}"},
            json=kit_data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify all fields are present in response
        assert data["club"] == kit_data["club"], f"Club mismatch"
        assert data["season"] == kit_data["season"], f"Season mismatch"
        assert data["league"] == kit_data["league"], f"League mismatch"
        assert data["kit_type"] == kit_data["kit_type"], f"Kit type mismatch"
        assert data["brand"] == kit_data["brand"], f"Brand mismatch"
        assert data["design"] == kit_data["design"], f"Design mismatch"
        assert data["sponsor"] == kit_data["sponsor"], f"Sponsor mismatch"
        assert data["gender"] == kit_data["gender"], f"Gender mismatch"
        
        print(f"✓ Master Kit created with all fields: club, season, league, kit_type, brand, design, sponsor, gender")

    def test_get_master_kit_returns_all_fields(self):
        """Test GET /api/master-kits/{id} returns all fields"""
        # Create a kit first
        kit_id = f"kit_{uuid.uuid4().hex[:12]}"
        db.master_kits.insert_one({
            "kit_id": kit_id,
            "club": f"{self.test_prefix} Get Test",
            "season": "2024/2025",
            "league": "Premier League",
            "kit_type": "Away",
            "brand": "Adidas",
            "design": "Gradient",
            "sponsor": "Qatar Airways",
            "gender": "Woman",
            "front_photo": "https://example.com/photo.jpg",
            "created_by": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        response = requests.get(f"{BASE_URL}/api/master-kits/{kit_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify all fields are present
        assert "brand" in data, "brand field missing"
        assert "kit_type" in data, "kit_type field missing"
        assert "design" in data, "design field missing"
        assert "sponsor" in data, "sponsor field missing"
        assert "league" in data, "league field missing"
        assert "gender" in data, "gender field missing"
        
        print(f"✓ GET /api/master-kits/{kit_id} returns all fields: brand={data['brand']}, type={data['kit_type']}, design={data['design']}, sponsor={data['sponsor']}, league={data['league']}, gender={data['gender']}")


class TestVersionFields:
    """Test Version creation and retrieval with all required fields"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test data"""
        self.test_prefix = f"TEST_VER_{uuid.uuid4().hex[:8]}"
        self.user_id = f"test_user_{uuid.uuid4().hex[:12]}"
        self.session_token = f"test_session_{uuid.uuid4().hex[:16]}"
        self.kit_id = f"kit_{uuid.uuid4().hex[:12]}"
        
        # Create test user
        db.users.insert_one({
            "user_id": self.user_id,
            "email": f"{self.test_prefix}@example.com",
            "name": "Test User",
            "role": "user",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        db.user_sessions.insert_one({
            "user_id": self.user_id,
            "session_token": self.session_token,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Create test kit
        db.master_kits.insert_one({
            "kit_id": self.kit_id,
            "club": f"{self.test_prefix} FC",
            "season": "2024/2025",
            "kit_type": "Home",
            "brand": "Nike",
            "front_photo": "https://example.com/photo.jpg",
            "created_by": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        yield
        
        # Cleanup
        db.users.delete_many({"user_id": self.user_id})
        db.user_sessions.delete_many({"session_token": self.session_token})
        db.master_kits.delete_many({"kit_id": self.kit_id})
        db.versions.delete_many({"kit_id": self.kit_id})

    def test_create_version_with_all_fields(self):
        """Test POST /api/versions accepts all fields: Competition, Model, SKU Code, EAN Code"""
        version_data = {
            "kit_id": self.kit_id,
            "competition": "Continental Cup",
            "model": "Authentic",
            "sku_code": "ABC123",
            "ean_code": "1234567890123",
            "front_photo": "https://example.com/front.jpg",
            "back_photo": "https://example.com/back.jpg"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/versions",
            headers={"Authorization": f"Bearer {self.session_token}"},
            json=version_data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify all fields are present
        assert data["competition"] == version_data["competition"], f"Competition mismatch"
        assert data["model"] == version_data["model"], f"Model mismatch"
        assert data["sku_code"] == version_data["sku_code"], f"SKU code mismatch"
        assert data["ean_code"] == version_data["ean_code"], f"EAN code mismatch"
        
        print(f"✓ Version created with all fields: competition={data['competition']}, model={data['model']}, sku_code={data['sku_code']}, ean_code={data['ean_code']}")

    def test_get_version_returns_competition(self):
        """Test GET /api/versions/{id} returns competition field"""
        # Create a version first
        version_id = f"ver_{uuid.uuid4().hex[:12]}"
        db.versions.insert_one({
            "version_id": version_id,
            "kit_id": self.kit_id,
            "competition": "World Cup",
            "model": "Replica",
            "sku_code": "WC2024",
            "ean_code": "9876543210123",
            "created_by": "test",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        response = requests.get(f"{BASE_URL}/api/versions/{version_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify competition field is present
        assert "competition" in data, "competition field missing from version detail"
        assert data["competition"] == "World Cup", f"Expected competition='World Cup', got '{data['competition']}'"
        
        print(f"✓ GET /api/versions/{version_id} returns competition field: competition={data['competition']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
