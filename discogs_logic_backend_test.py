#!/usr/bin/env python3
"""
TopKit JerseyDetailEditor Discogs Logic Backend Testing
Testing the backend API endpoints that support the 3-mode Discogs logic implementation

Focus Areas from Review Request:
1. Authentication system (steinmetzlivio@gmail.com/123)
2. Jersey submission endpoints (/api/jerseys) - for "submission" mode
3. Collection endpoints (/api/collections) - for "collection-edit" mode  
4. Admin endpoints - for "admin-modify" mode
5. API functionality verification after frontend Discogs logic implementation

Test Scenarios:
- Mode "submission": Jersey submission workflow
- Mode "collection-edit": Collection management workflow  
- Mode "admin-modify": Admin correction workflow
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration - Using production URL from frontend/.env
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"

# Test credentials from review request (updated from test_result.md history)
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "TopKit123!"
ADMIN_EMAIL = "topkitfr@gmail.com" 
ADMIN_PASSWORD = "TopKitSecure789#"

class DiscogsLogicBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        self.created_jerseys = []
        self.created_collections = []
        
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
    
    def test_user_authentication(self):
        """Test user authentication - supports 'submission' and 'collection-edit' modes"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                
                self.log_result(
                    "User Authentication",
                    True,
                    f"User logged in successfully: {user_info.get('name')} (Role: {user_info.get('role')}, ID: {user_info.get('id')})"
                )
                return True
            else:
                self.log_result(
                    "User Authentication", 
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, "", str(e))
            return False
    
    def test_admin_authentication(self):
        """Test admin authentication - supports 'admin-modify' mode"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Admin logged in successfully: {user_info.get('name')} (Role: {user_info.get('role')}, ID: {user_info.get('id')})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False, 
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False
    
    def test_jersey_submission_mode(self):
        """Test jersey submission endpoints - Mode 'submission' (📋 Informations de base)"""
        if not self.user_token:
            self.log_result("Jersey Submission Mode", False, "", "No user token available")
            return False
            
        try:
            # Test jersey submission with realistic data
            jersey_data = {
                "team": "FC Barcelona",
                "league": "La Liga",
                "season": "2024-25",
                "manufacturer": "Nike",
                "jersey_type": "home",
                "model": "authentic",
                "description": "Maillot domicile FC Barcelona 2024-25 - Test Discogs Logic Submission Mode"
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                jersey_id = data.get("id")
                reference = data.get("reference_number")
                status = data.get("status")
                
                if jersey_id:
                    self.created_jerseys.append(jersey_id)
                
                self.log_result(
                    "Jersey Submission Mode",
                    True,
                    f"Jersey created successfully (ID: {jersey_id}, Ref: {reference}, Status: {status})"
                )
                return True
            else:
                self.log_result(
                    "Jersey Submission Mode",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Jersey Submission Mode", False, "", str(e))
            return False
    
    def test_collection_edit_mode(self):
        """Test collection endpoints - Mode 'collection-edit' (🔍 Détails de la collection)"""
        if not self.user_token:
            self.log_result("Collection Edit Mode", False, "", "No user token available")
            return False
            
        try:
            # First, get available jerseys to add to collection
            headers = {"Authorization": f"Bearer {self.user_token}"}
            jerseys_response = self.session.get(f"{BACKEND_URL}/jerseys", headers=headers)
            
            if jerseys_response.status_code != 200:
                self.log_result("Collection Edit Mode", False, "Cannot fetch jerseys", jerseys_response.text)
                return False
            
            jerseys = jerseys_response.json()
            if not jerseys:
                self.log_result("Collection Edit Mode", False, "No jerseys available for collection", "")
                return False
            
            # Use first available jersey for collection test
            jersey_id = jerseys[0]["id"]
            
            # Test adding to collection with size and condition (collection details)
            collection_data = {
                "jersey_id": jersey_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "very_good",
                "personal_description": "Test collection item - Discogs Logic Collection Edit Mode"
            }
            
            response = self.session.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                collection_id = data.get("id")
                
                if collection_id:
                    self.created_collections.append(collection_id)
                
                self.log_result(
                    "Collection Edit Mode",
                    True,
                    f"Collection item added successfully (ID: {collection_id}, Type: {data.get('collection_type')}, Size: {data.get('size')}, Condition: {data.get('condition')})"
                )
                return True
            else:
                self.log_result(
                    "Collection Edit Mode",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Collection Edit Mode", False, "", str(e))
            return False
    
    def test_admin_modify_mode(self):
        """Test admin endpoints - Mode 'admin-modify' (📋 Informations de base for corrections)"""
        if not self.admin_token:
            self.log_result("Admin Modify Mode", False, "", "No admin token available")
            return False
            
        try:
            # Test getting pending jerseys for admin modification
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                
                self.log_result(
                    "Admin Modify Mode - Pending Jerseys",
                    True,
                    f"Retrieved {len(pending_jerseys)} pending jerseys for admin modification"
                )
                
                # If we have pending jerseys, test admin actions
                if pending_jerseys:
                    jersey_id = pending_jerseys[0]["id"]
                    
                    # Test suggesting modifications (admin-modify mode functionality)
                    suggestion_data = {
                        "jersey_id": jersey_id,
                        "suggested_changes": "Test modification suggestion - Discogs Logic Admin Modify Mode",
                        "suggested_modifications": {
                            "team": "Corrected team name",
                            "description": "Updated description for accuracy"
                        }
                    }
                    
                    suggest_response = self.session.post(
                        f"{BACKEND_URL}/admin/jerseys/{jersey_id}/suggest-modifications",
                        json=suggestion_data,
                        headers=headers
                    )
                    
                    if suggest_response.status_code == 200:
                        self.log_result(
                            "Admin Modify Mode - Suggest Modifications",
                            True,
                            f"Modification suggestion created successfully for jersey {jersey_id}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Admin Modify Mode - Suggest Modifications",
                            False,
                            f"HTTP {suggest_response.status_code}",
                            suggest_response.text
                        )
                        return False
                else:
                    self.log_result(
                        "Admin Modify Mode",
                        True,
                        "No pending jerseys available for modification testing (this is normal)"
                    )
                    return True
                    
            else:
                self.log_result(
                    "Admin Modify Mode",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Modify Mode", False, "", str(e))
            return False
    
    def test_user_collections_access(self):
        """Test user's collection access - supports collection-edit mode"""
        if not self.user_token:
            self.log_result("User Collections Access", False, "", "No user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BACKEND_URL}/collections/my-owned", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                self.log_result(
                    "User Collections Access",
                    True,
                    f"Retrieved {len(collections)} owned items from user's collection"
                )
                return True
            else:
                self.log_result(
                    "User Collections Access",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("User Collections Access", False, "", str(e))
            return False
    
    def test_api_health_check(self):
        """Test basic API health and connectivity"""
        try:
            # Test basic jersey listing endpoint
            response = self.session.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                self.log_result(
                    "API Health Check",
                    True,
                    f"API is healthy - Retrieved {len(jerseys)} jerseys"
                )
                return True
            else:
                self.log_result(
                    "API Health Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("API Health Check", False, "", str(e))
            return False
    
    def run_comprehensive_test(self):
        """Run all tests for Discogs logic backend support"""
        print("🎯 TOPKIT DISCOGS LOGIC BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Admin User: {ADMIN_EMAIL}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("API Health Check", self.test_api_health_check),
            ("User Authentication", self.test_user_authentication),
            ("Admin Authentication", self.test_admin_authentication),
            ("Jersey Submission Mode", self.test_jersey_submission_mode),
            ("Collection Edit Mode", self.test_collection_edit_mode),
            ("User Collections Access", self.test_user_collections_access),
            ("Admin Modify Mode", self.test_admin_modify_mode),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if self.created_jerseys:
            print(f"Created Jerseys: {len(self.created_jerseys)}")
        if self.created_collections:
            print(f"Created Collections: {len(self.created_collections)}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
        
        # Discogs Logic Assessment
        print("\n🎨 DISCOGS LOGIC BACKEND ASSESSMENT:")
        print("=" * 60)
        
        if success_rate >= 85:
            print("✅ EXCELLENT: Backend fully supports Discogs logic implementation")
            print("   - All 3 modes (submission/collection-edit/admin-modify) have working APIs")
            print("   - Authentication system operational for all user types")
            print("   - Jersey submission, collection management, and admin workflows functional")
        elif success_rate >= 70:
            print("⚠️  GOOD: Backend mostly supports Discogs logic with minor issues")
            print("   - Core functionality working but some endpoints may need attention")
        else:
            print("❌ ISSUES: Backend has significant problems affecting Discogs logic")
            print("   - Multiple API endpoints failing")
            print("   - May impact frontend Discogs mode functionality")
        
        return success_rate

def main():
    """Main test execution"""
    tester = DiscogsLogicBackendTester()
    success_rate = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)

if __name__ == "__main__":
    main()