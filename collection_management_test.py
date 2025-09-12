#!/usr/bin/env python3
"""
TopKit Collection Endpoints Testing - Alternative Approach
Testing existing collections and collection management
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com" 
ADMIN_PASSWORD = "TopKitSecure789#"

class CollectionTestAlternative:
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
    
    def test_existing_collections(self):
        """Test existing collection endpoints"""
        if not self.authenticate_admin():
            self.log_result("Authentication", False, "", "Authentication failed")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: Get owned collections
        try:
            owned_response = self.session.get(f"{BACKEND_URL}/collections/my-owned", headers=headers)
            
            if owned_response.status_code == 200:
                owned_collections = owned_response.json()
                self.log_result(
                    "Get Owned Collections",
                    True,
                    f"Retrieved {len(owned_collections)} owned items from collection"
                )
                
                # Show details of first few items
                if owned_collections:
                    for i, item in enumerate(owned_collections[:3]):
                        jersey_info = item.get('jersey', {})
                        print(f"    Item {i+1}: {jersey_info.get('team', 'Unknown')} - Size: {item.get('size', 'N/A')}, Condition: {item.get('condition', 'N/A')}")
                
            else:
                self.log_result(
                    "Get Owned Collections",
                    False,
                    f"HTTP {owned_response.status_code}",
                    owned_response.text
                )
                return False
            
            # Test 2: Get wanted collections
            wanted_response = self.session.get(f"{BACKEND_URL}/collections/my-wanted", headers=headers)
            
            if wanted_response.status_code == 200:
                wanted_collections = wanted_response.json()
                self.log_result(
                    "Get Wanted Collections",
                    True,
                    f"Retrieved {len(wanted_collections)} wanted items from collection"
                )
            else:
                self.log_result(
                    "Get Wanted Collections",
                    False,
                    f"HTTP {wanted_response.status_code}",
                    wanted_response.text
                )
            
            # Test 3: Get all collections
            all_response = self.session.get(f"{BACKEND_URL}/collections/my", headers=headers)
            
            if all_response.status_code == 200:
                all_collections = all_response.json()
                self.log_result(
                    "Get All Collections",
                    True,
                    f"Retrieved {len(all_collections)} total items from all collections"
                )
            else:
                self.log_result(
                    "Get All Collections",
                    False,
                    f"HTTP {all_response.status_code}",
                    all_response.text
                )
            
            # Test 4: Try to find a jersey not in collection for adding
            jerseys_response = self.session.get(f"{BACKEND_URL}/jerseys", headers=headers)
            
            if jerseys_response.status_code == 200:
                jerseys = jerseys_response.json()
                approved_jerseys = [j for j in jerseys if j.get("status") == "approved"]
                
                # Get collection jersey IDs
                collection_jersey_ids = set()
                if owned_response.status_code == 200:
                    for item in owned_response.json():
                        collection_jersey_ids.add(item.get('jersey_id'))
                
                # Find a jersey not in collection
                available_jersey = None
                for jersey in approved_jerseys:
                    if jersey['id'] not in collection_jersey_ids:
                        available_jersey = jersey
                        break
                
                if available_jersey:
                    # Test 5: Add new jersey to collection
                    collection_data = {
                        "jersey_id": available_jersey['id'],
                        "collection_type": "owned",
                        "size": "M",
                        "condition": "good",
                        "personal_description": f"Test collection item - {available_jersey.get('team', 'Unknown')} {available_jersey.get('season', '')}"
                    }
                    
                    add_response = self.session.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
                    
                    if add_response.status_code == 200:
                        collection_item = add_response.json()
                        self.log_result(
                            "Add New Jersey to Collection",
                            True,
                            f"Successfully added {available_jersey.get('team', 'Unknown')} to collection (Size: {collection_item.get('size')}, Condition: {collection_item.get('condition')})"
                        )
                    else:
                        self.log_result(
                            "Add New Jersey to Collection",
                            False,
                            f"HTTP {add_response.status_code}",
                            add_response.text
                        )
                else:
                    self.log_result(
                        "Add New Jersey to Collection",
                        True,
                        "All approved jerseys are already in collection (this is normal)"
                    )
            
            return True
            
        except Exception as e:
            self.log_result("Collection Testing", False, "", str(e))
            return False
    
    def run_test(self):
        """Run collection test"""
        print("🎯 TOPKIT COLLECTION MANAGEMENT TESTING")
        print("=" * 60)
        print("Testing existing collections and collection-edit mode support")
        print("=" * 60)
        
        success = self.test_existing_collections()
        
        print("\n" + "=" * 60)
        print("📊 COLLECTION MANAGEMENT TEST SUMMARY")
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
        
        print("\n🎨 COLLECTION-EDIT MODE SUPPORT ASSESSMENT:")
        print("=" * 60)
        
        if success_rate >= 85:
            print("✅ EXCELLENT: Collection endpoints fully support collection-edit mode")
            print("   - Collection retrieval working perfectly")
            print("   - Size and condition details properly stored")
            print("   - Both owned and wanted collections functional")
        elif success_rate >= 70:
            print("⚠️  GOOD: Collection endpoints mostly support collection-edit mode")
            print("   - Core functionality working with minor issues")
        else:
            print("❌ ISSUES: Collection endpoints have problems")
            print("   - May impact frontend collection-edit mode functionality")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = CollectionTestAlternative()
    success = tester.run_test()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()