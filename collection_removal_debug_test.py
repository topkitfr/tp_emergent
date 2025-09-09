#!/usr/bin/env python3
"""
TopKit Collection Removal Debug Test
Debugging the collection removal issue where DELETE button shows "jersey not found in collection" error
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-tracker.preview.emergentagent.com/api"

# Test credentials - using admin since user account is locked
TEST_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

ADMIN_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class CollectionRemovalDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.user_id = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
        
    def authenticate_user(self):
        """Authenticate test user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                user_data = data.get('user', {})
                self.user_id = user_data.get('id')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"User: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "User Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, "", str(e))
            return False
    
    def test_get_owned_collections_format(self):
        """Test 1: Check the format of collection data returned by GET /api/collections/owned"""
        try:
            # The correct endpoint is /api/collections/{collection_type} where collection_type = "owned"
            response = self.session.get(f"{BACKEND_URL}/collections/owned")
            
            if response.status_code == 200:
                collections = response.json()
                
                # Analyze the structure
                collection_count = len(collections)
                sample_collection = collections[0] if collections else None
                
                details = f"Found {collection_count} collections"
                if sample_collection:
                    # Check what fields are available
                    available_fields = list(sample_collection.keys())
                    details += f"\nSample collection fields: {available_fields}"
                    
                    # Check for key identifiers
                    collection_id = sample_collection.get('id')
                    jersey_id = sample_collection.get('jersey_id')
                    collection_type = sample_collection.get('collection_type')
                    
                    details += f"\nCollection ID: {collection_id}"
                    details += f"\nJersey ID: {jersey_id}"
                    details += f"\nCollection Type: {collection_type}"
                    
                    # Check if jersey data is embedded
                    if 'jersey' in sample_collection:
                        jersey_data = sample_collection['jersey']
                        details += f"\nJersey data embedded: {type(jersey_data)} with keys: {list(jersey_data.keys()) if isinstance(jersey_data, dict) else 'Not a dict'}"
                
                self.log_result(
                    "GET /api/collections/owned Format Analysis",
                    True,
                    details
                )
                return collections
            else:
                self.log_result(
                    "GET /api/collections/owned Format Analysis",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result("GET /api/collections/owned Format Analysis", False, "", str(e))
            return []
    
    def test_collection_remove_with_collection_id(self, collections):
        """Test 2: Test DELETE /api/collections/remove with collection_id parameter"""
        if not collections:
            self.log_result(
                "DELETE with collection_id",
                False,
                "No collections available to test removal"
            )
            return
        
        try:
            # Use the first collection for testing
            test_collection = collections[0]
            collection_id = test_collection.get('id')
            
            if not collection_id:
                self.log_result(
                    "DELETE with collection_id",
                    False,
                    "No collection ID found in collection data"
                )
                return
            
            # Test with collection_id parameter
            response = self.session.delete(f"{BACKEND_URL}/collections/remove", json={
                "collection_id": collection_id
            })
            
            details = f"Tested with collection_id: {collection_id}"
            details += f"\nResponse status: {response.status_code}"
            details += f"\nResponse body: {response.text}"
            
            if response.status_code == 200:
                self.log_result(
                    "DELETE with collection_id",
                    True,
                    details
                )
            else:
                self.log_result(
                    "DELETE with collection_id",
                    False,
                    details,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DELETE with collection_id", False, "", str(e))
    
    def test_collection_remove_post_method(self, collections):
        """Test 2b: Test POST /api/collections/remove (the actual backend endpoint)"""
        if not collections:
            self.log_result(
                "POST /api/collections/remove",
                False,
                "No collections available to test removal"
            )
            return
        
        try:
            # Use the first collection for testing
            test_collection = collections[0]
            jersey_id = test_collection.get('jersey_id')
            collection_type = test_collection.get('collection_type')
            
            if not jersey_id or not collection_type:
                self.log_result(
                    "POST /api/collections/remove",
                    False,
                    f"Missing required data - jersey_id: {jersey_id}, collection_type: {collection_type}"
                )
                return
            
            # Test with the correct format expected by backend
            response = self.session.post(f"{BACKEND_URL}/collections/remove", json={
                "jersey_id": jersey_id,
                "collection_type": collection_type
            })
            
            details = f"Tested POST with jersey_id: {jersey_id}, collection_type: {collection_type}"
            details += f"\nResponse status: {response.status_code}"
            details += f"\nResponse body: {response.text}"
            
            if response.status_code == 200:
                self.log_result(
                    "POST /api/collections/remove",
                    True,
                    details
                )
            else:
                self.log_result(
                    "POST /api/collections/remove",
                    False,
                    details,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("POST /api/collections/remove", False, "", str(e))
    
    def test_collection_remove_with_jersey_id(self, collections):
        """Test 3: Test DELETE /api/collections/remove with jersey_id parameter"""
        if not collections:
            self.log_result(
                "DELETE with jersey_id",
                False,
                "No collections available to test removal"
            )
            return
        
        try:
            # Use the second collection if available, or first if only one
            test_collection = collections[1] if len(collections) > 1 else collections[0]
            jersey_id = test_collection.get('jersey_id')
            
            if not jersey_id:
                self.log_result(
                    "DELETE with jersey_id",
                    False,
                    "No jersey_id found in collection data"
                )
                return
            
            # Test with jersey_id parameter
            response = self.session.delete(f"{BACKEND_URL}/collections/remove", json={
                "jersey_id": jersey_id
            })
            
            details = f"Tested with jersey_id: {jersey_id}"
            details += f"\nResponse status: {response.status_code}"
            details += f"\nResponse body: {response.text}"
            
            if response.status_code == 200:
                self.log_result(
                    "DELETE with jersey_id",
                    True,
                    details
                )
            else:
                self.log_result(
                    "DELETE with jersey_id",
                    False,
                    details,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DELETE with jersey_id", False, "", str(e))
    
    def test_delete_collections_jersey_id_endpoint(self, collections):
        """Test 4b: Test DELETE /api/collections/{jersey_id} endpoint"""
        if not collections:
            self.log_result(
                "DELETE /api/collections/{jersey_id}",
                False,
                "No collections available to test removal"
            )
            return
        
        try:
            # Use the last collection if available
            test_collection = collections[-1] if collections else collections[0]
            jersey_id = test_collection.get('jersey_id')
            
            if not jersey_id:
                self.log_result(
                    "DELETE /api/collections/{jersey_id}",
                    False,
                    f"Missing jersey_id: {jersey_id}"
                )
                return
            
            # Test the DELETE /api/collections/{jersey_id} endpoint
            response = self.session.delete(f"{BACKEND_URL}/collections/{jersey_id}")
            
            details = f"Tested DELETE /api/collections/{jersey_id}"
            details += f"\nResponse status: {response.status_code}"
            details += f"\nResponse body: {response.text}"
            
            if response.status_code == 200:
                self.log_result(
                    "DELETE /api/collections/{jersey_id}",
                    True,
                    details
                )
            else:
                self.log_result(
                    "DELETE /api/collections/{jersey_id}",
                    False,
                    details,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("DELETE /api/collections/{jersey_id}", False, "", str(e))
    
    def test_alternative_endpoints(self):
        """Test 5: Check if there are alternative collection removal endpoints"""
        alternative_endpoints = [
            "/collections/remove-item",
            "/collections/delete",
            "/user/collections/remove",
            f"/users/{self.user_id}/collections/remove" if self.user_id else None,
            "/collections/owned/remove"
        ]
        
        # Filter out None values
        alternative_endpoints = [ep for ep in alternative_endpoints if ep is not None]
        
        for endpoint in alternative_endpoints:
            try:
                # Test with a dummy collection_id
                response = self.session.delete(f"{BACKEND_URL}{endpoint}", json={
                    "collection_id": "test-id"
                })
                
                details = f"Endpoint: {endpoint}"
                details += f"\nResponse status: {response.status_code}"
                details += f"\nResponse body: {response.text[:200]}..."  # Truncate long responses
                
                # Consider 404 as expected for non-existent endpoints
                # Consider 400/422 as potentially valid endpoints with wrong parameters
                if response.status_code in [400, 422, 401, 403]:
                    self.log_result(
                        f"Alternative endpoint {endpoint}",
                        True,
                        details + "\n(Endpoint exists but requires different parameters/auth)"
                    )
                elif response.status_code == 404:
                    self.log_result(
                        f"Alternative endpoint {endpoint}",
                        False,
                        details + "\n(Endpoint does not exist)"
                    )
                else:
                    self.log_result(
                        f"Alternative endpoint {endpoint}",
                        True,
                        details
                    )
                    
            except Exception as e:
                self.log_result(f"Alternative endpoint {endpoint}", False, "", str(e))
    
    def test_backend_collection_endpoints_discovery(self):
        """Test 6: Discover all collection-related endpoints by checking server.py"""
        try:
            # This is a conceptual test - in practice we'd analyze the server code
            # Let's test some common patterns
            
            collection_endpoints = [
                ("GET", "/collections"),
                ("GET", "/collections/owned"),
                ("GET", "/collections/wanted"), 
                ("POST", "/collections"),
                ("DELETE", "/collections/remove"),
                ("PUT", "/collections/update"),
                ("GET", f"/users/{self.user_id}/collections" if self.user_id else "/users/USER_ID/collections"),
            ]
            
            endpoint_results = []
            
            for method, endpoint in collection_endpoints:
                try:
                    if method == "GET":
                        response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    elif method == "POST":
                        response = self.session.post(f"{BACKEND_URL}{endpoint}", json={"test": "data"})
                    elif method == "DELETE":
                        response = self.session.delete(f"{BACKEND_URL}{endpoint}", json={"test": "data"})
                    elif method == "PUT":
                        response = self.session.put(f"{BACKEND_URL}{endpoint}", json={"test": "data"})
                    
                    endpoint_results.append({
                        "method": method,
                        "endpoint": endpoint,
                        "status": response.status_code,
                        "exists": response.status_code != 404
                    })
                    
                except Exception as e:
                    endpoint_results.append({
                        "method": method,
                        "endpoint": endpoint,
                        "status": "ERROR",
                        "exists": False,
                        "error": str(e)
                    })
            
            # Summarize findings
            existing_endpoints = [ep for ep in endpoint_results if ep["exists"]]
            details = f"Found {len(existing_endpoints)} existing collection endpoints:\n"
            
            for ep in existing_endpoints:
                details += f"  {ep['method']} {ep['endpoint']} (HTTP {ep['status']})\n"
            
            self.log_result(
                "Collection Endpoints Discovery",
                True,
                details
            )
            
        except Exception as e:
            self.log_result("Collection Endpoints Discovery", False, "", str(e))
    
    def add_test_collection_for_removal(self):
        """Helper: Add a test collection item to ensure we have something to remove"""
        try:
            # First, get available jerseys
            response = self.session.get(f"{BACKEND_URL}/jerseys")
            if response.status_code != 200:
                self.log_result(
                    "Add Test Collection Item",
                    False,
                    "Could not fetch jerseys to add to collection"
                )
                return False
            
            jerseys = response.json()
            if not jerseys:
                self.log_result(
                    "Add Test Collection Item",
                    False,
                    "No jerseys available to add to collection"
                )
                return False
            
            # Add first jersey to collection
            test_jersey = jerseys[0]
            jersey_id = test_jersey.get('id')
            
            add_response = self.session.post(f"{BACKEND_URL}/collections", json={
                "jersey_id": jersey_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "good"
            })
            
            if add_response.status_code in [200, 201]:
                self.log_result(
                    "Add Test Collection Item",
                    True,
                    f"Added jersey {jersey_id} to collection for testing removal"
                )
                return True
            else:
                self.log_result(
                    "Add Test Collection Item",
                    False,
                    f"Failed to add jersey to collection: HTTP {add_response.status_code}",
                    add_response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Add Test Collection Item", False, "", str(e))
            return False
    
    def run_all_tests(self):
        """Run all collection removal debug tests"""
        print("🔍 TOPKIT COLLECTION REMOVAL DEBUG TEST")
        print("=" * 50)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Step 2: Add a test collection item to ensure we have data
        print("📝 Adding test collection item...")
        self.add_test_collection_for_removal()
        print()
        
        # Step 3: Test collection data format
        print("🔍 Testing collection data format...")
        collections = self.test_get_owned_collections_format()
        print()
        
        # Step 4: Test different removal parameter formats
        print("🗑️ Testing collection removal with different parameters...")
        self.test_collection_remove_with_collection_id(collections)
        self.test_collection_remove_post_method(collections)
        self.test_collection_remove_with_jersey_id(collections)
        self.test_delete_collections_jersey_id_endpoint(collections)
        print()
        
        # Step 5: Test alternative endpoints
        print("🔍 Testing alternative collection removal endpoints...")
        self.test_alternative_endpoints()
        print()
        
        # Step 6: Discover all collection endpoints
        print("📋 Discovering all collection endpoints...")
        self.test_backend_collection_endpoints_discovery()
        print()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("🔍 KEY FINDINGS:")
        
        # Analyze results for key insights
        collection_format_test = next((r for r in self.test_results if "Format Analysis" in r['test']), None)
        if collection_format_test and collection_format_test['success']:
            print("  • Collection data format successfully analyzed")
        
        removal_tests = [r for r in self.test_results if "DELETE with" in r['test']]
        successful_removals = [r for r in removal_tests if r['success']]
        
        if successful_removals:
            print(f"  • Found {len(successful_removals)} working removal method(s)")
            for test in successful_removals:
                method = test['test'].replace("DELETE with ", "")
                print(f"    - {method} works")
        else:
            print("  • No working removal methods found - this explains the user's issue!")
        
        print()
        print("💡 RECOMMENDATIONS:")
        if not successful_removals:
            print("  • The collection removal functionality appears to be broken")
            print("  • Check backend server.py for the correct DELETE /api/collections/remove implementation")
            print("  • Verify the expected parameter format in the backend code")
            print("  • Consider if the endpoint path is correct")
        
        print()

if __name__ == "__main__":
    debugger = CollectionRemovalDebugger()
    debugger.run_all_tests()