#!/usr/bin/env python3
"""
Create Sample Reference Kits for Testing Discogs-like Structure
This script creates sample reference kits linked to existing master jerseys to test the complete workflow.
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ReferenceKitCreator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    print(f"✅ Admin authenticated successfully")
                    return True
            
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def get_master_jerseys(self):
        """Get existing master jerseys"""
        try:
            response = self.session.get(f"{API_BASE}/master-jerseys")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📋 Found {len(data)} master jerseys")
                return data
            else:
                print(f"❌ Failed to get master jerseys: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting master jerseys: {e}")
            return []

    def create_reference_kit(self, master_jersey_id, kit_data):
        """Create a reference kit"""
        try:
            response = self.session.post(f"{API_BASE}/reference-kits", json=kit_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"✅ Created reference kit: {kit_data['model_name']}")
                return True, data
            else:
                print(f"❌ Failed to create reference kit: {response.status_code} - {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ Error creating reference kit: {e}")
            return False, None

    def create_sample_reference_kits(self):
        """Create sample reference kits for testing"""
        master_jerseys = self.get_master_jerseys()
        
        if not master_jerseys:
            print("❌ No master jerseys found")
            return
        
        # Select a few master jerseys to create versions for
        target_jerseys = master_jerseys[:3]  # Use first 3 master jerseys
        
        print(f"🎯 Creating reference kits for {len(target_jerseys)} master jerseys...")
        
        reference_kits_created = []
        
        for i, master_jersey in enumerate(target_jerseys):
            master_jersey_id = master_jersey['id']
            team_name = master_jersey.get('team_info', {}).get('name', 'Unknown Team')
            season = master_jersey.get('season', 'Unknown')
            jersey_type = master_jersey.get('jersey_type', 'home')
            
            print(f"\n📋 Creating versions for: {team_name} {season} {jersey_type}")
            
            # Create 2-4 different versions for each master jersey
            versions = [
                {
                    "id": str(uuid.uuid4()),
                    "master_kit_id": master_jersey_id,
                    "model_name": f"{team_name} {season} {jersey_type.title()} - Authentic",
                    "release_type": "authentic",
                    "retail_price": 140.00,
                    "player_name": "",
                    "player_number": "",
                    "size": "L",
                    "condition": "new",
                    "league_competition": "Premier League",
                    "season": season,
                    "available_prints": [
                        {
                            "player_name": "Messi", 
                            "number": "10", 
                            "price": 15.00
                        },
                        {
                            "player_name": "Ronaldo", 
                            "number": "7", 
                            "price": 15.00
                        }
                    ],
                    "topkit_reference": f"TK-REF-{str(uuid.uuid4())[:8].upper()}",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "master_kit_id": master_jersey_id,
                    "model_name": f"{team_name} {season} {jersey_type.title()} - Replica",
                    "release_type": "replica", 
                    "retail_price": 89.99,
                    "player_name": "",
                    "player_number": "",
                    "size": "M",
                    "condition": "new",
                    "league_competition": "UEFA Champions League",
                    "season": season,
                    "available_prints": [
                        {
                            "player_name": "Benzema", 
                            "number": "9", 
                            "price": 12.00
                        }
                    ],
                    "topkit_reference": f"TK-REF-{str(uuid.uuid4())[:8].upper()}",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "master_kit_id": master_jersey_id,
                    "model_name": f"{team_name} {season} {jersey_type.title()} - Player Version",
                    "release_type": "player_version",
                    "retail_price": 199.99,
                    "player_name": "Mbappé",
                    "player_number": "7",
                    "size": "L",
                    "condition": "new", 
                    "league_competition": "Ligue 1",
                    "season": season,
                    "available_prints": [
                        {
                            "player_name": "Mbappé", 
                            "number": "7", 
                            "price": 20.00
                        }
                    ],
                    "topkit_reference": f"TK-REF-{str(uuid.uuid4())[:8].upper()}",
                    "created_at": datetime.now().isoformat(), 
                    "updated_at": datetime.now().isoformat()
                }
            ]
            
            # Only create 2 versions for the first jersey, 3 for second, and 1 for third to show variety
            if i == 0:
                versions = versions[:2]  # 2 versions
            elif i == 1:
                versions = versions[:3]  # 3 versions
            else:
                versions = versions[:1]  # 1 version
            
            for version in versions:
                success, created_kit = self.create_reference_kit(master_jersey_id, version)
                if success and created_kit:
                    reference_kits_created.append(created_kit)
        
        print(f"\n🎉 Successfully created {len(reference_kits_created)} reference kits!")
        
        # Test the API to verify creation
        self.verify_created_kits(reference_kits_created)
        
        return reference_kits_created

    def verify_created_kits(self, created_kits):
        """Verify the created reference kits can be retrieved"""
        print(f"\n🔍 Verifying created reference kits...")
        
        try:
            # Test general endpoint
            response = self.session.get(f"{API_BASE}/reference-kits")
            if response.status_code == 200:
                all_kits = response.json()
                print(f"✅ GET /api/reference-kits returns {len(all_kits)} reference kits")
            
            # Test individual kit retrieval
            if created_kits:
                test_kit_id = created_kits[0].get('id')
                if test_kit_id:
                    response = self.session.get(f"{API_BASE}/reference-kits/{test_kit_id}")
                    if response.status_code == 200:
                        print(f"✅ Individual reference kit retrieval working")
                    else:
                        print(f"⚠️ Individual reference kit retrieval failed: {response.status_code}")
            
        except Exception as e:
            print(f"❌ Verification error: {e}")

def main():
    print("🚀 Creating Sample Reference Kits for Discogs-like Testing")
    print("="*60)
    
    creator = ReferenceKitCreator()
    
    # Authenticate
    if not creator.authenticate_admin():
        return
    
    # Create sample reference kits
    creator.create_sample_reference_kits()
    
    print("\n🎉 Sample reference kits creation completed!")
    print("Now you can test the complete Discogs-like workflow:")
    print("1. Browse master jerseys in Kit Area")
    print("2. Click on a master jersey to see 'Other Versions'")
    print("3. Click 'View All Versions' to see the versions page")
    print("4. Click on individual versions for detailed view")

if __name__ == "__main__":
    main()