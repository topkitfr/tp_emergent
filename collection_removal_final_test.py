#!/usr/bin/env python3
"""
TopKit Collection Removal Final Test
Testing the exact issue: DELETE button shows "jersey not found in collection" error
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"

# Test credentials
ADMIN_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class CollectionRemovalFinalTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_USER)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                user_data = data.get('user', {})
                self.user_id = user_data.get('id')
                
                # Set authorization header
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                print(f"✅ Authenticated as: {user_data.get('name')} (ID: {self.user_id})")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_collections(self):
        """Get user's owned collections"""
        try:
            response = self.session.get(f"{BACKEND_URL}/collections/owned")
            
            if response.status_code == 200:
                collections = response.json()
                print(f"✅ Found {len(collections)} owned collections")
                
                for i, collection in enumerate(collections):
                    jersey = collection.get('jersey', {})
                    print(f"  {i+1}. {jersey.get('team', 'Unknown')} - {jersey.get('player', 'No player')} (ID: {collection.get('jersey_id')})")
                
                return collections
            else:
                print(f"❌ Failed to get collections: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting collections: {e}")
            return []
    
    def test_wrong_method_delete(self, jersey_id):
        """Test what happens when frontend uses DELETE method (likely the bug)"""
        print(f"\n🔍 Testing DELETE method (likely what frontend is doing wrong)...")
        
        try:
            # Test 1: DELETE with JSON body (common frontend mistake)
            response = self.session.delete(f"{BACKEND_URL}/collections/remove", json={
                "jersey_id": jersey_id,
                "collection_type": "owned"
            })
            
            print(f"DELETE /api/collections/remove with JSON body:")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            
            # Test 2: DELETE with URL parameter
            response2 = self.session.delete(f"{BACKEND_URL}/collections/{jersey_id}")
            
            print(f"DELETE /api/collections/{jersey_id}:")
            print(f"  Status: {response2.status_code}")
            print(f"  Response: {response2.text}")
            
            return response.status_code != 200 and response2.status_code != 200
            
        except Exception as e:
            print(f"❌ Error testing DELETE method: {e}")
            return True
    
    def test_correct_method_post(self, jersey_id):
        """Test the correct POST method"""
        print(f"\n✅ Testing correct POST method...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/collections/remove", json={
                "jersey_id": jersey_id,
                "collection_type": "owned"
            })
            
            print(f"POST /api/collections/remove:")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error testing POST method: {e}")
            return False
    
    def test_missing_collection_type(self, jersey_id):
        """Test what happens when collection_type is missing"""
        print(f"\n🔍 Testing missing collection_type parameter...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/collections/remove", json={
                "jersey_id": jersey_id
                # Missing collection_type
            })
            
            print(f"POST /api/collections/remove without collection_type:")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            
            return response.status_code != 200
            
        except Exception as e:
            print(f"❌ Error testing missing collection_type: {e}")
            return True
    
    def test_wrong_collection_type(self, jersey_id):
        """Test what happens with wrong collection_type"""
        print(f"\n🔍 Testing wrong collection_type parameter...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/collections/remove", json={
                "jersey_id": jersey_id,
                "collection_type": "wanted"  # Wrong type - should be "owned"
            })
            
            print(f"POST /api/collections/remove with wrong collection_type:")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            
            return response.status_code != 200
            
        except Exception as e:
            print(f"❌ Error testing wrong collection_type: {e}")
            return True
    
    def add_test_item_back(self, jersey_id):
        """Add the test item back to collection for future tests"""
        print(f"\n🔄 Adding test item back to collection...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/collections", json={
                "jersey_id": jersey_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "good"
            })
            
            if response.status_code in [200, 201]:
                print(f"✅ Successfully added jersey back to collection")
                return True
            elif response.status_code == 400 and "Already in collection" in response.text:
                print(f"✅ Jersey already in collection")
                return True
            else:
                print(f"❌ Failed to add jersey back: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding jersey back: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive collection removal test"""
        print("🔍 TOPKIT COLLECTION REMOVAL ISSUE DIAGNOSIS")
        print("=" * 60)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate():
            return
        
        # Step 2: Get collections
        collections = self.get_collections()
        if not collections:
            print("❌ No collections found to test with")
            return
        
        # Use first collection for testing
        test_collection = collections[0]
        jersey_id = test_collection.get('jersey_id')
        jersey_info = test_collection.get('jersey', {})
        
        print(f"\n🎯 Testing with jersey: {jersey_info.get('team', 'Unknown')} - {jersey_info.get('player', 'No player')}")
        print(f"   Jersey ID: {jersey_id}")
        print(f"   Collection ID: {test_collection.get('id')}")
        print(f"   Collection Type: {test_collection.get('collection_type')}")
        
        # Step 3: Test wrong methods (what frontend might be doing)
        delete_fails = self.test_wrong_method_delete(jersey_id)
        
        # Step 4: Test missing parameters
        missing_type_fails = self.test_missing_collection_type(jersey_id)
        wrong_type_fails = self.test_wrong_collection_type(jersey_id)
        
        # Step 5: Test correct method
        post_works = self.test_correct_method_post(jersey_id)
        
        # Step 6: Add item back for future tests
        self.add_test_item_back(jersey_id)
        
        # Step 7: Summary and diagnosis
        print("\n" + "=" * 60)
        print("🔍 DIAGNOSIS SUMMARY")
        print("=" * 60)
        
        print(f"❌ DELETE methods fail: {'Yes' if delete_fails else 'No'}")
        print(f"❌ Missing collection_type fails: {'Yes' if missing_type_fails else 'No'}")
        print(f"❌ Wrong collection_type fails: {'Yes' if wrong_type_fails else 'No'}")
        print(f"✅ POST method works: {'Yes' if post_works else 'No'}")
        
        print("\n💡 ROOT CAUSE ANALYSIS:")
        
        if delete_fails and post_works:
            print("🎯 ISSUE IDENTIFIED: Frontend is using DELETE method instead of POST")
            print("   - Backend expects: POST /api/collections/remove")
            print("   - Frontend likely sends: DELETE /api/collections/remove")
            print("   - This causes 'Jersey not found in collection' error")
            
        if missing_type_fails:
            print("🎯 POTENTIAL ISSUE: Frontend might not be sending collection_type parameter")
            print("   - Backend requires both jersey_id AND collection_type")
            
        if wrong_type_fails:
            print("🎯 POTENTIAL ISSUE: Frontend might be sending wrong collection_type")
            print("   - Must match the actual collection type ('owned' vs 'wanted')")
        
        print("\n🔧 RECOMMENDED FIXES:")
        print("1. Change frontend DELETE request to POST request")
        print("2. Ensure frontend sends both jersey_id and collection_type parameters")
        print("3. Verify collection_type matches the actual collection ('owned' or 'wanted')")
        print("4. Consider updating backend to accept DELETE method for better REST compliance")
        
        print(f"\n✅ CORRECT API CALL FORMAT:")
        print(f"   Method: POST")
        print(f"   URL: {BACKEND_URL}/collections/remove")
        print(f"   Body: {{\"jersey_id\": \"{jersey_id}\", \"collection_type\": \"owned\"}}")

if __name__ == "__main__":
    tester = CollectionRemovalFinalTest()
    tester.run_comprehensive_test()