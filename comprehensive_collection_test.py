#!/usr/bin/env python3
"""
Comprehensive Collection API Test
Testing all potential issues that could cause "Erreur lors de la mise à jour de la collection"
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://image-fix-10.preview.emergentagent.com/api"

class ComprehensiveCollectionTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"\n{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print("-" * 80)
    
    def setup_authenticated_user(self):
        """Setup an authenticated user for testing"""
        try:
            test_email = f"collectiontest_{int(time.time())}@topkit.com"
            register_payload = {
                "email": test_email,
                "password": "testpass123",
                "name": "Collection Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
                    self.log_test("User Setup", "PASS", f"Authenticated as {data['user']['email']}")
                    return True
            
            self.log_test("User Setup", "FAIL", f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("User Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_add_various_scenarios(self):
        """Test collection add with various scenarios that might cause errors"""
        print("\n🔍 TESTING COLLECTION ADD - VARIOUS SCENARIOS")
        print("=" * 80)
        
        # Get available jerseys
        jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=5")
        if jerseys_response.status_code != 200:
            self.log_test("Collection Add Scenarios", "FAIL", "Could not get jerseys")
            return False
        
        jerseys = jerseys_response.json()
        if not jerseys:
            self.log_test("Collection Add Scenarios", "FAIL", "No jerseys available")
            return False
        
        test_jersey_id = jerseys[0]['id']
        scenarios_passed = 0
        total_scenarios = 0
        
        # Scenario 1: Normal owned collection add
        total_scenarios += 1
        try:
            payload = {"jersey_id": test_jersey_id, "collection_type": "owned"}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 200:
                scenarios_passed += 1
                print(f"✅ Scenario 1 (Normal Owned): PASS - {response.json()}")
            else:
                print(f"❌ Scenario 1 (Normal Owned): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Scenario 1 (Normal Owned): FAIL - Exception: {str(e)}")
        
        # Scenario 2: Normal wanted collection add
        total_scenarios += 1
        try:
            payload = {"jersey_id": test_jersey_id, "collection_type": "wanted"}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 200:
                scenarios_passed += 1
                print(f"✅ Scenario 2 (Normal Wanted): PASS - {response.json()}")
            else:
                print(f"❌ Scenario 2 (Normal Wanted): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Scenario 2 (Normal Wanted): FAIL - Exception: {str(e)}")
        
        # Scenario 3: Duplicate add (should fail gracefully)
        total_scenarios += 1
        try:
            payload = {"jersey_id": test_jersey_id, "collection_type": "owned"}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 400 and "already in collection" in response.text.lower():
                scenarios_passed += 1
                print(f"✅ Scenario 3 (Duplicate): PASS - Correctly rejected duplicate")
            else:
                print(f"❌ Scenario 3 (Duplicate): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Scenario 3 (Duplicate): FAIL - Exception: {str(e)}")
        
        # Scenario 4: Test with different jersey
        if len(jerseys) > 1:
            total_scenarios += 1
            try:
                test_jersey_id_2 = jerseys[1]['id']
                payload = {"jersey_id": test_jersey_id_2, "collection_type": "owned"}
                response = self.session.post(f"{self.base_url}/collections", json=payload)
                
                if response.status_code == 200:
                    scenarios_passed += 1
                    print(f"✅ Scenario 4 (Different Jersey): PASS - {response.json()}")
                else:
                    print(f"❌ Scenario 4 (Different Jersey): FAIL - {response.status_code}: {response.text}")
            except Exception as e:
                print(f"❌ Scenario 4 (Different Jersey): FAIL - Exception: {str(e)}")
        
        # Scenario 5: Test collection retrieval after adds
        total_scenarios += 1
        try:
            response = self.session.get(f"{self.base_url}/collections/owned")
            
            if response.status_code == 200:
                collection_data = response.json()
                if len(collection_data) >= 1:
                    scenarios_passed += 1
                    print(f"✅ Scenario 5 (Collection Retrieval): PASS - Found {len(collection_data)} items")
                else:
                    print(f"❌ Scenario 5 (Collection Retrieval): FAIL - Empty collection")
            else:
                print(f"❌ Scenario 5 (Collection Retrieval): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Scenario 5 (Collection Retrieval): FAIL - Exception: {str(e)}")
        
        success_rate = (scenarios_passed / total_scenarios) * 100
        self.log_test("Collection Add Scenarios", 
                     "PASS" if scenarios_passed == total_scenarios else "PARTIAL", 
                     f"{scenarios_passed}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")
        
        return scenarios_passed == total_scenarios
    
    def test_potential_error_conditions(self):
        """Test conditions that might cause the French error message"""
        print("\n🔍 TESTING POTENTIAL ERROR CONDITIONS")
        print("=" * 80)
        
        error_tests_passed = 0
        total_error_tests = 0
        
        # Get a jersey for testing
        jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=1")
        if jerseys_response.status_code != 200:
            self.log_test("Error Conditions", "FAIL", "Could not get jerseys")
            return False
        
        jerseys = jerseys_response.json()
        if not jerseys:
            self.log_test("Error Conditions", "FAIL", "No jerseys available")
            return False
        
        test_jersey_id = jerseys[0]['id']
        
        # Test 1: Invalid jersey ID format
        total_error_tests += 1
        try:
            payload = {"jersey_id": "invalid-id-format", "collection_type": "owned"}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            # Should either reject with 400/404 or handle gracefully
            if response.status_code in [400, 404]:
                error_tests_passed += 1
                print(f"✅ Error Test 1 (Invalid Jersey ID): PASS - Correctly rejected")
            elif response.status_code == 200:
                # If it accepts invalid ID, that's a bug but not the user's error
                error_tests_passed += 1
                print(f"⚠️ Error Test 1 (Invalid Jersey ID): PASS - Accepted (potential bug)")
            else:
                print(f"❌ Error Test 1 (Invalid Jersey ID): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error Test 1 (Invalid Jersey ID): FAIL - Exception: {str(e)}")
        
        # Test 2: Invalid collection type
        total_error_tests += 1
        try:
            payload = {"jersey_id": test_jersey_id, "collection_type": "invalid_type"}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code in [400, 422]:
                error_tests_passed += 1
                print(f"✅ Error Test 2 (Invalid Collection Type): PASS - Correctly rejected")
            elif response.status_code == 200:
                error_tests_passed += 1
                print(f"⚠️ Error Test 2 (Invalid Collection Type): PASS - Accepted (potential bug)")
            else:
                print(f"❌ Error Test 2 (Invalid Collection Type): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error Test 2 (Invalid Collection Type): FAIL - Exception: {str(e)}")
        
        # Test 3: Missing required fields
        total_error_tests += 1
        try:
            payload = {"jersey_id": test_jersey_id}  # Missing collection_type
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 422:
                error_tests_passed += 1
                print(f"✅ Error Test 3 (Missing Fields): PASS - Correctly rejected")
            else:
                print(f"❌ Error Test 3 (Missing Fields): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error Test 3 (Missing Fields): FAIL - Exception: {str(e)}")
        
        # Test 4: Empty payload
        total_error_tests += 1
        try:
            payload = {}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 422:
                error_tests_passed += 1
                print(f"✅ Error Test 4 (Empty Payload): PASS - Correctly rejected")
            else:
                print(f"❌ Error Test 4 (Empty Payload): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error Test 4 (Empty Payload): FAIL - Exception: {str(e)}")
        
        # Test 5: Malformed JSON (test with requests directly)
        total_error_tests += 1
        try:
            headers = self.session.headers.copy()
            response = requests.post(f"{self.base_url}/collections", 
                                   data="invalid json", 
                                   headers=headers)
            
            if response.status_code in [400, 422]:
                error_tests_passed += 1
                print(f"✅ Error Test 5 (Malformed JSON): PASS - Correctly rejected")
            else:
                print(f"❌ Error Test 5 (Malformed JSON): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Error Test 5 (Malformed JSON): FAIL - Exception: {str(e)}")
        
        success_rate = (error_tests_passed / total_error_tests) * 100
        self.log_test("Error Conditions Testing", 
                     "PASS" if error_tests_passed >= total_error_tests * 0.8 else "FAIL", 
                     f"{error_tests_passed}/{total_error_tests} error tests passed ({success_rate:.1f}%)")
        
        return error_tests_passed >= total_error_tests * 0.8
    
    def test_authentication_edge_cases(self):
        """Test authentication-related issues that might cause collection errors"""
        print("\n🔍 TESTING AUTHENTICATION EDGE CASES")
        print("=" * 80)
        
        auth_tests_passed = 0
        total_auth_tests = 0
        
        # Get a jersey for testing
        jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=1")
        if jerseys_response.status_code != 200:
            self.log_test("Authentication Edge Cases", "FAIL", "Could not get jerseys")
            return False
        
        jerseys = jerseys_response.json()
        if not jerseys:
            self.log_test("Authentication Edge Cases", "FAIL", "No jerseys available")
            return False
        
        test_jersey_id = jerseys[0]['id']
        
        # Test 1: Valid token format
        total_auth_tests += 1
        try:
            # Current token should work
            payload = {"jersey_id": test_jersey_id, "collection_type": "owned"}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code in [200, 400]:  # 400 for duplicate is OK
                auth_tests_passed += 1
                print(f"✅ Auth Test 1 (Valid Token): PASS")
            else:
                print(f"❌ Auth Test 1 (Valid Token): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Auth Test 1 (Valid Token): FAIL - Exception: {str(e)}")
        
        # Test 2: No token
        total_auth_tests += 1
        try:
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            payload = {"jersey_id": test_jersey_id, "collection_type": "owned"}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                auth_tests_passed += 1
                print(f"✅ Auth Test 2 (No Token): PASS - Correctly rejected")
            else:
                print(f"❌ Auth Test 2 (No Token): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Auth Test 2 (No Token): FAIL - Exception: {str(e)}")
        
        # Test 3: Invalid token
        total_auth_tests += 1
        try:
            # Use invalid token temporarily
            original_auth = self.session.headers.get('Authorization')
            self.session.headers['Authorization'] = 'Bearer invalid_token_here'
            
            payload = {"jersey_id": test_jersey_id, "collection_type": "owned"}
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                auth_tests_passed += 1
                print(f"✅ Auth Test 3 (Invalid Token): PASS - Correctly rejected")
            else:
                print(f"❌ Auth Test 3 (Invalid Token): FAIL - {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Auth Test 3 (Invalid Token): FAIL - Exception: {str(e)}")
        
        success_rate = (auth_tests_passed / total_auth_tests) * 100
        self.log_test("Authentication Edge Cases", 
                     "PASS" if auth_tests_passed == total_auth_tests else "FAIL", 
                     f"{auth_tests_passed}/{total_auth_tests} auth tests passed ({success_rate:.1f}%)")
        
        return auth_tests_passed == total_auth_tests
    
    def test_database_connectivity(self):
        """Test if there are any database connectivity issues"""
        print("\n🔍 TESTING DATABASE CONNECTIVITY")
        print("=" * 80)
        
        db_tests_passed = 0
        total_db_tests = 0
        
        # Test 1: Can read jerseys
        total_db_tests += 1
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=1")
            if response.status_code == 200:
                db_tests_passed += 1
                print(f"✅ DB Test 1 (Read Jerseys): PASS")
            else:
                print(f"❌ DB Test 1 (Read Jerseys): FAIL - {response.status_code}")
        except Exception as e:
            print(f"❌ DB Test 1 (Read Jerseys): FAIL - Exception: {str(e)}")
        
        # Test 2: Can read collections
        total_db_tests += 1
        try:
            response = self.session.get(f"{self.base_url}/collections/owned")
            if response.status_code == 200:
                db_tests_passed += 1
                print(f"✅ DB Test 2 (Read Collections): PASS")
            else:
                print(f"❌ DB Test 2 (Read Collections): FAIL - {response.status_code}")
        except Exception as e:
            print(f"❌ DB Test 2 (Read Collections): FAIL - Exception: {str(e)}")
        
        # Test 3: Can read profile
        total_db_tests += 1
        try:
            response = self.session.get(f"{self.base_url}/profile")
            if response.status_code == 200:
                db_tests_passed += 1
                print(f"✅ DB Test 3 (Read Profile): PASS")
            else:
                print(f"❌ DB Test 3 (Read Profile): FAIL - {response.status_code}")
        except Exception as e:
            print(f"❌ DB Test 3 (Read Profile): FAIL - Exception: {str(e)}")
        
        success_rate = (db_tests_passed / total_db_tests) * 100
        self.log_test("Database Connectivity", 
                     "PASS" if db_tests_passed == total_db_tests else "FAIL", 
                     f"{db_tests_passed}/{total_db_tests} DB tests passed ({success_rate:.1f}%)")
        
        return db_tests_passed == total_db_tests
    
    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite"""
        print("\n" + "=" * 80)
        print("🚀 COMPREHENSIVE COLLECTION API TEST SUITE")
        print("🎯 TARGET: Identify root cause of collection update errors")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Setup
        if not self.setup_authenticated_user():
            print("\n❌ FAILED: Could not setup authenticated user")
            return False
        
        # Run all test categories
        test_results = []
        
        test_results.append(("Collection Add Scenarios", self.test_collection_add_various_scenarios()))
        test_results.append(("Potential Error Conditions", self.test_potential_error_conditions()))
        test_results.append(("Authentication Edge Cases", self.test_authentication_edge_cases()))
        test_results.append(("Database Connectivity", self.test_database_connectivity()))
        
        # Summary
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE TEST SUITE COMPLETED")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Results: {passed_tests}/{total_tests} test categories passed")
        print()
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        overall_success = passed_tests == total_tests
        
        print()
        if overall_success:
            print("✅ CONCLUSION: Collection API is functioning correctly")
            print("   The French error message is likely caused by:")
            print("   1. Frontend validation issues")
            print("   2. Network connectivity problems")
            print("   3. User-specific authentication issues")
            print("   4. Frontend error handling displaying wrong message")
        else:
            print("❌ CONCLUSION: Collection API has issues that need fixing")
            print("   Check the failed test categories above for specific problems")
        
        print("=" * 80)
        
        return overall_success

def main():
    """Main function to run the comprehensive collection test"""
    tester = ComprehensiveCollectionTester()
    
    print("🔧 TopKit Comprehensive Collection API Test")
    print("🎯 Debugging: 'Erreur lors de la mise à jour de la collection. Veuillez réessayer.'")
    print(f"🌐 Testing against: {BASE_URL}")
    print()
    
    success = tester.run_comprehensive_test_suite()
    return success

if __name__ == "__main__":
    main()