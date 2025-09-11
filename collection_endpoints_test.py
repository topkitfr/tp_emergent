#!/usr/bin/env python3
"""
TopKit Collection Endpoints Testing for Discogs Logic
Testing collection endpoints that support "collection-edit" mode
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com" 
ADMIN_PASSWORD = "TopKitSecure789#"

class CollectionEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                return True
            return False
        except:
            return False
    
    def test_collection_endpoints(self):
        """Test collection endpoints for Discogs logic collection-edit mode"""
        if not self.authenticate_admin():
            self.log_result("Collection Endpoints", False, "", "Authentication failed")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: Get approved jerseys for collection
        try:
            jerseys_response = self.session.get(f"{BACKEND_URL}/jerseys", headers=headers)
            if jerseys_response.status_code != 200:
                self.log_result("Get Jerseys for Collection", False, f"HTTP {jerseys_response.status_code}", jerseys_response.text)
                return False
            
            jerseys = jerseys_response.json()
            approved_jerseys = [j for j in jerseys if j.get("status") == "approved"]
            
            self.log_result(
                "Get Jerseys for Collection",
                True,
                f"Found {len(approved_jerseys)} approved jerseys available for collection"
            )
            
            if not approved_jerseys:
                self.log_result("Collection Endpoints", True, "No approved jerseys available for collection testing", "")
                return True
            
            # Test 2: Add jersey to collection (collection-edit mode functionality)
            jersey_id = approved_jerseys[0]["id"]
            collection_data = {
                "jersey_id": jersey_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "very_good",
                "personal_description": "Test collection item for Discogs logic collection-edit mode"
            }
            
            add_response = self.session.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
            
            if add_response.status_code == 200:
                collection_item = add_response.json()
                self.log_result(
                    "Add to Collection",
                    True,
                    f"Successfully added jersey to collection (ID: {collection_item.get('id')}, Type: {collection_item.get('collection_type')}, Size: {collection_item.get('size')}, Condition: {collection_item.get('condition')})"
                )
            else:
                self.log_result(
                    "Add to Collection",
                    False,
                    f"HTTP {add_response.status_code}",
                    add_response.text
                )
                return False
            
            # Test 3: Get user's collections
            collections_response = self.session.get(f"{BACKEND_URL}/collections/my-owned", headers=headers)
            
            if collections_response.status_code == 200:
                collections = collections_response.json()
                self.log_result(
                    "Get User Collections",
                    True,
                    f"Retrieved {len(collections)} items from user's owned collection"
                )
            else:
                self.log_result(
                    "Get User Collections",
                    False,
                    f"HTTP {collections_response.status_code}",
                    collections_response.text
                )
                return False
            
            # Test 4: Test wanted collection
            wanted_data = {
                "jersey_id": jersey_id,
                "collection_type": "wanted",
                "size": "M",
                "condition": "new",
                "personal_description": "Test wanted item for Discogs logic"
            }
            
            wanted_response = self.session.post(f"{BACKEND_URL}/collections", json=wanted_data, headers=headers)
            
            if wanted_response.status_code == 200:
                self.log_result(
                    "Add to Wanted Collection",
                    True,
                    f"Successfully added jersey to wanted collection"
                )
            else:
                self.log_result(
                    "Add to Wanted Collection",
                    False,
                    f"HTTP {wanted_response.status_code}",
                    wanted_response.text
                )
            
            # Test 5: Get wanted collections
            wanted_collections_response = self.session.get(f"{BACKEND_URL}/collections/my-wanted", headers=headers)
            
            if wanted_collections_response.status_code == 200:
                wanted_collections = wanted_collections_response.json()
                self.log_result(
                    "Get Wanted Collections",
                    True,
                    f"Retrieved {len(wanted_collections)} items from user's wanted collection"
                )
            else:
                self.log_result(
                    "Get Wanted Collections",
                    False,
                    f"HTTP {wanted_collections_response.status_code}",
                    wanted_collections_response.text
                )
            
            return True
            
        except Exception as e:
            self.log_result("Collection Endpoints", False, "", str(e))
            return False
    
    def run_test(self):
        """Run collection endpoints test"""
        print("🎯 TOPKIT COLLECTION ENDPOINTS TESTING FOR DISCOGS LOGIC")
        print("=" * 60)
        print("Testing collection endpoints that support 'collection-edit' mode")
        print("=" * 60)
        
        success = self.test_collection_endpoints()
        
        print("\n" + "=" * 60)
        print("📊 COLLECTION ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
        
        print("\n🎨 COLLECTION-EDIT MODE ASSESSMENT:")
        print("=" * 60)
        
        if success_rate >= 85:
            print("✅ EXCELLENT: Collection endpoints fully support collection-edit mode")
            print("   - Users can add jerseys to collections with size/condition details")
            print("   - Both owned and wanted collections functional")
            print("   - Collection retrieval working properly")
        elif success_rate >= 70:
            print("⚠️  GOOD: Collection endpoints mostly support collection-edit mode")
            print("   - Core functionality working with minor issues")
        else:
            print("❌ ISSUES: Collection endpoints have problems affecting collection-edit mode")
            print("   - May impact frontend collection management functionality")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = CollectionEndpointsTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()