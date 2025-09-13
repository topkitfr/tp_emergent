#!/usr/bin/env python3
"""
Setup Test Profile for TopKit Collection Testing
Creates a complete test profile with jerseys and collection data
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

TEST_USER = {
    "email": "livio.test@topkit.fr",
    "password": "TopKitTestSecure789!",
    "name": "Livio Test User"
}

class TestProfileSetup:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.user_id = None
        self.created_jerseys = []
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def get_admin_token(self):
        """Get admin authentication token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_USER)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.log("✅ Admin authentication successful")
                return True
            else:
                self.log(f"❌ Admin authentication failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Admin authentication error: {e}")
            return False
    
    def create_test_user(self):
        """Create or verify test user exists"""
        try:
            # Try to register the user
            register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=TEST_USER)
            
            if register_response.status_code == 200:
                self.log("✅ Test user created successfully")
            elif "existe déjà" in register_response.text:
                self.log("✅ Test user already exists")
            else:
                self.log(f"⚠️ User registration response: {register_response.status_code} - {register_response.text[:100]}")
            
            # Try to login
            login_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                self.log(f"✅ Test user login successful: {user_info.get('name')} (ID: {self.user_id})")
                return True
            else:
                self.log(f"❌ Test user login failed: {login_response.status_code} - {login_response.text[:100]}")
                return False
                
        except Exception as e:
            self.log(f"❌ Test user creation error: {e}")
            return False
    
    def create_sample_jerseys(self):
        """Create sample jerseys for testing"""
        if not self.user_token:
            self.log("❌ No user token available for jersey creation")
            return False
            
        sample_jerseys = [
            {
                "team": "FC Barcelona",
                "season": "2024-25",
                "player": "Pedri",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "FC Barcelona home jersey 2024-25 season with Pedri #8"
            },
            {
                "team": "Real Madrid CF",
                "season": "2024-25", 
                "player": "Vinicius Jr",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Real Madrid home jersey 2024-25 season with Vinicius Jr #7"
            },
            {
                "team": "Manchester City",
                "season": "2024-25",
                "player": "Haaland",
                "manufacturer": "Puma",
                "home_away": "home", 
                "league": "Premier League",
                "description": "Manchester City home jersey 2024-25 season with Haaland #9"
            },
            {
                "team": "Paris Saint-Germain",
                "season": "2024-25",
                "player": "Mbappé",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Ligue 1",
                "description": "PSG home jersey 2024-25 season with Mbappé #7"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        created_count = 0
        
        for jersey_data in sample_jerseys:
            try:
                response = self.session.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    jersey_id = data.get("id")
                    self.created_jerseys.append({
                        "id": jersey_id,
                        "team": jersey_data["team"],
                        "player": jersey_data.get("player", ""),
                        "season": jersey_data["season"]
                    })
                    created_count += 1
                    self.log(f"✅ Created jersey: {jersey_data['team']} - {jersey_data.get('player', 'No player')} ({jersey_data['season']})")
                else:
                    self.log(f"⚠️ Jersey creation failed: {response.status_code} - {response.text[:100]}")
                    
            except Exception as e:
                self.log(f"❌ Jersey creation error: {e}")
        
        self.log(f"✅ Created {created_count}/{len(sample_jerseys)} sample jerseys")
        return created_count > 0
    
    def approve_jerseys(self):
        """Approve created jerseys using admin token"""
        if not self.admin_token or not self.created_jerseys:
            self.log("❌ No admin token or jerseys to approve")
            return False
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        approved_count = 0
        
        # Get pending jerseys
        try:
            pending_response = self.session.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            
            if pending_response.status_code == 200:
                pending_jerseys = pending_response.json()
                self.log(f"Found {len(pending_jerseys)} pending jerseys")
                
                for jersey in pending_jerseys:
                    jersey_id = jersey.get("id")
                    if jersey_id:
                        # Approve the jersey
                        approve_response = self.session.post(
                            f"{BACKEND_URL}/admin/jerseys/{jersey_id}/approve", 
                            headers=headers
                        )
                        
                        if approve_response.status_code == 200:
                            approved_count += 1
                            self.log(f"✅ Approved jersey: {jersey.get('team', 'Unknown')} - {jersey.get('player', 'No player')}")
                        else:
                            self.log(f"⚠️ Jersey approval failed: {approve_response.status_code}")
            else:
                self.log(f"⚠️ Could not get pending jerseys: {pending_response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Jersey approval error: {e}")
        
        self.log(f"✅ Approved {approved_count} jerseys")
        return approved_count > 0
    
    def create_collection_items(self):
        """Add jerseys to user's collection"""
        if not self.user_token:
            self.log("❌ No user token available for collection creation")
            return False
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Get approved jerseys
        try:
            jerseys_response = self.session.get(f"{BACKEND_URL}/jerseys", headers=headers)
            
            if jerseys_response.status_code == 200:
                jerseys = jerseys_response.json()
                self.log(f"Found {len(jerseys)} approved jerseys")
                
                collection_count = 0
                
                # Add some jerseys to owned collection
                for i, jersey in enumerate(jerseys[:2]):  # Add first 2 to owned
                    collection_data = {
                        "jersey_id": jersey.get("id"),
                        "collection_type": "owned",
                        "size": "M",
                        "condition": "very_good",
                        "personal_description": f"Great condition {jersey.get('team', 'jersey')} jersey"
                    }
                    
                    collection_response = self.session.post(
                        f"{BACKEND_URL}/collections", 
                        json=collection_data, 
                        headers=headers
                    )
                    
                    if collection_response.status_code in [200, 201]:
                        collection_count += 1
                        self.log(f"✅ Added to owned collection: {jersey.get('team', 'Unknown')} - {jersey.get('player', 'No player')}")
                    else:
                        self.log(f"⚠️ Collection add failed: {collection_response.status_code} - {collection_response.text[:100]}")
                
                # Add some jerseys to wanted collection
                for i, jersey in enumerate(jerseys[2:4]):  # Add next 2 to wanted
                    collection_data = {
                        "jersey_id": jersey.get("id"),
                        "collection_type": "wanted",
                        "size": "L",
                        "condition": "new"
                    }
                    
                    collection_response = self.session.post(
                        f"{BACKEND_URL}/collections", 
                        json=collection_data, 
                        headers=headers
                    )
                    
                    if collection_response.status_code in [200, 201]:
                        collection_count += 1
                        self.log(f"✅ Added to wanted collection: {jersey.get('team', 'Unknown')} - {jersey.get('player', 'No player')}")
                    else:
                        self.log(f"⚠️ Collection add failed: {collection_response.status_code} - {collection_response.text[:100]}")
                
                self.log(f"✅ Created {collection_count} collection items")
                return collection_count > 0
            else:
                self.log(f"⚠️ Could not get jerseys: {jerseys_response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Collection creation error: {e}")
            return False
    
    def verify_setup(self):
        """Verify the test profile setup"""
        if not self.user_token:
            self.log("❌ No user token for verification")
            return False
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            # Check collections
            collections_response = self.session.get(f"{BACKEND_URL}/users/{self.user_id}/collections", headers=headers)
            if collections_response.status_code == 200:
                collections_data = collections_response.json()
                owned_count = collections_data.get("owned_count", 0)
                wanted_count = collections_data.get("wanted_count", 0)
                self.log(f"✅ Collections verified: {owned_count} owned, {wanted_count} wanted")
            else:
                self.log(f"⚠️ Collections verification failed: {collections_response.status_code}")
            
            # Check jerseys
            jerseys_response = self.session.get(f"{BACKEND_URL}/jerseys")
            if jerseys_response.status_code == 200:
                jerseys = jerseys_response.json()
                self.log(f"✅ Jerseys verified: {len(jerseys)} approved jerseys available")
            else:
                self.log(f"⚠️ Jerseys verification failed: {jerseys_response.status_code}")
            
            # Check profile
            profile_response = self.session.get(f"{BACKEND_URL}/auth/profile", headers=headers)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                self.log(f"✅ Profile verified: {profile_data.get('name', 'Unknown')} ({profile_data.get('email', 'Unknown')})")
            else:
                self.log(f"⚠️ Profile verification failed: {profile_response.status_code}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Verification error: {e}")
            return False
    
    def run_setup(self):
        """Run complete test profile setup"""
        self.log("🚀 Starting TopKit Test Profile Setup")
        self.log("=" * 60)
        
        steps = [
            ("Getting admin token", self.get_admin_token),
            ("Creating test user", self.create_test_user),
            ("Creating sample jerseys", self.create_sample_jerseys),
            ("Approving jerseys", self.approve_jerseys),
            ("Creating collection items", self.create_collection_items),
            ("Verifying setup", self.verify_setup)
        ]
        
        success_count = 0
        
        for step_name, step_func in steps:
            self.log(f"\n📋 {step_name}...")
            if step_func():
                success_count += 1
            time.sleep(1)  # Brief pause between steps
        
        self.log("\n" + "=" * 60)
        self.log(f"📊 SETUP SUMMARY: {success_count}/{len(steps)} steps completed successfully")
        
        if success_count == len(steps):
            self.log("🎉 Test profile setup completed successfully!")
            self.log(f"👤 Test user: {TEST_USER['email']} / {TEST_USER['password']}")
            self.log(f"🆔 User ID: {self.user_id}")
        elif success_count >= len(steps) * 0.8:
            self.log("✅ Test profile setup mostly successful")
        else:
            self.log("⚠️ Test profile setup had significant issues")
        
        return success_count, len(steps)

def main():
    setup = TestProfileSetup()
    success_count, total_steps = setup.run_setup()
    
    # Return appropriate exit code
    if success_count == total_steps:
        exit(0)  # Success
    else:
        exit(1)  # Some steps failed

if __name__ == "__main__":
    main()