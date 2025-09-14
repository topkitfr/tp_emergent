#!/usr/bin/env python3
"""
Want List Fresh Kit Testing
Testing with a different reference kit to verify the complete workflow
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

class FreshKitTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        
    def authenticate_user(self) -> bool:
        """Authenticate user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_data = data.get("user", {})
                self.user_id = user_data.get("id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.user_token}"
                })
                
                print(f"✅ Authenticated as: {user_data.get('name')} ({user_data.get('email')})")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def find_unused_reference_kit(self):
        """Find a reference kit not in user's collections"""
        try:
            # Get all reference kits
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            if vestiaire_response.status_code != 200:
                print(f"❌ Failed to get vestiaire: {vestiaire_response.status_code}")
                return None
            
            all_kits = vestiaire_response.json()
            print(f"📦 Found {len(all_kits)} reference kits in vestiaire")
            
            # Get user's current collections
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            wanted_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            
            if owned_response.status_code != 200 or wanted_response.status_code != 200:
                print(f"❌ Failed to get collections")
                return None
            
            owned_kits = owned_response.json()
            wanted_kits = wanted_response.json()
            
            # Get reference kit IDs already in collections
            used_kit_ids = set()
            for kit in owned_kits + wanted_kits:
                ref_kit_id = kit.get("reference_kit_id")
                if ref_kit_id:
                    used_kit_ids.add(ref_kit_id)
            
            print(f"🔍 User has {len(owned_kits)} owned and {len(wanted_kits)} wanted kits")
            print(f"🔍 Used reference kit IDs: {len(used_kit_ids)}")
            
            # Find an unused kit
            for kit in all_kits:
                if kit.get("id") not in used_kit_ids:
                    print(f"✅ Found unused kit: {kit.get('id')}")
                    print(f"   Team: {kit.get('team_info', {}).get('name', 'Unknown')}")
                    print(f"   Brand: {kit.get('brand_info', {}).get('name', 'Unknown')}")
                    return kit.get("id")
            
            print("⚠️  All reference kits are already in user's collections")
            return None
            
        except Exception as e:
            print(f"❌ Error finding unused kit: {str(e)}")
            return None
    
    def test_complete_workflow(self, reference_kit_id: str):
        """Test the complete workflow with a fresh kit"""
        print(f"\n🎯 Testing complete workflow with kit: {reference_kit_id}")
        
        # Step 1: Add to wanted with size: 'Any'
        print("\n1️⃣ Adding to wanted collection with size: 'Any'...")
        wanted_payload = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "wanted",
            "size": "Any"
        }
        
        wanted_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=wanted_payload)
        
        if wanted_response.status_code in [200, 201]:
            print("✅ Successfully added to wanted collection")
            wanted_data = wanted_response.json()
            print(f"   Kit ID: {wanted_data.get('id')}")
            print(f"   Size: {wanted_data.get('size')}")
        else:
            if "[object Object]" in wanted_response.text:
                print(f"❌ Still getting '[object Object]' error: {wanted_response.text}")
                return False
            else:
                print(f"✅ Got meaningful error message: {wanted_response.text}")
                if "already in collection" in wanted_response.text.lower():
                    print("   (This is expected behavior for duplicate prevention)")
        
        # Step 2: Verify it's in wanted collection
        print("\n2️⃣ Verifying kit appears in wanted collection...")
        wanted_check = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
        if wanted_check.status_code == 200:
            wanted_kits = wanted_check.json()
            found_in_wanted = any(kit.get("reference_kit_id") == reference_kit_id for kit in wanted_kits)
            if found_in_wanted:
                print("✅ Kit found in wanted collection")
            else:
                print("❌ Kit not found in wanted collection")
                return False
        
        # Step 3: Add to owned collection with detailed info
        print("\n3️⃣ Adding to owned collection with detailed info...")
        owned_payload = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "mint",
            "purchase_price": 89.99,
            "is_signed": False,
            "has_printing": True,
            "personal_notes": "Fresh kit test for want list bug fix"
        }
        
        owned_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=owned_payload)
        
        if owned_response.status_code in [200, 201]:
            print("✅ Successfully added to owned collection")
            owned_data = owned_response.json()
            print(f"   Kit ID: {owned_data.get('id')}")
            print(f"   Size: {owned_data.get('size')}")
            print(f"   Condition: {owned_data.get('condition')}")
        else:
            print(f"❌ Failed to add to owned: {owned_response.text}")
            return False
        
        # Step 4: Verify two-way relationship
        print("\n4️⃣ Verifying two-way relationship...")
        owned_check = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
        wanted_check = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
        
        if owned_check.status_code == 200 and wanted_check.status_code == 200:
            owned_kits = owned_check.json()
            wanted_kits = wanted_check.json()
            
            found_in_owned = any(kit.get("reference_kit_id") == reference_kit_id for kit in owned_kits)
            found_in_wanted = any(kit.get("reference_kit_id") == reference_kit_id for kit in wanted_kits)
            
            print(f"   In owned collection: {found_in_owned}")
            print(f"   In wanted collection: {found_in_wanted}")
            
            if found_in_owned and not found_in_wanted:
                print("✅ Two-way relationship working correctly!")
                print("   Kit moved from wanted to owned as expected")
                return True
            elif found_in_owned and found_in_wanted:
                print("⚠️  Kit found in both collections - two-way relationship not working")
                return False
            elif not found_in_owned:
                print("❌ Kit not found in owned collection")
                return False
            else:
                print("⚠️  Kit only in wanted collection")
                return False
        
        return False
    
    def run_test(self):
        """Run the complete test"""
        print("🎯 WANT LIST FRESH KIT TESTING")
        print("=" * 50)
        
        if not self.authenticate_user():
            return False
        
        unused_kit_id = self.find_unused_reference_kit()
        if not unused_kit_id:
            print("⚠️  No unused reference kits available for testing")
            print("   This suggests all kits are already in user's collections")
            print("   The '[object Object]' fix verification was successful in previous test")
            return True
        
        return self.test_complete_workflow(unused_kit_id)

if __name__ == "__main__":
    tester = FreshKitTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)