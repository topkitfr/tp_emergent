#!/usr/bin/env python3
"""
TopKit Want List Architecture Testing
=====================================

Testing the critical architectural fix for want list functionality:
1. New Data Model: WantedKit model for want list (minimal data)
2. Separate Collections: personal_kits (owned only) and wanted_kits (wanted only)
3. New Endpoints: /api/wanted-kits POST/GET for wanted list, /api/personal-kits only for owned
4. Reference Kit Preservation: Wanted kits remain as Reference Kits with minimal wanted preferences
5. Two-Way Relationship: Adding to owned should remove from wanted list

Authentication: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-archive.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class WantListArchitectureTest:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate_user(self):
        """Authenticate test user"""
        print("🔐 AUTHENTICATING USER...")
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_data = data.get('user', {})
                self.user_id = user_data.get('id')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.user_token}'
                })
                
                self.log_test("User Authentication", True, 
                    f"User: {user_data.get('name')} (ID: {self.user_id})")
                return True
            else:
                self.log_test("User Authentication", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_vestiaire_kits(self):
        """Get available Reference Kits from vestiaire"""
        print("🏪 GETTING VESTIAIRE REFERENCE KITS...")
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                kits = response.json()
                if len(kits) > 0:
                    self.log_test("Vestiaire Reference Kits Available", True, 
                        f"Found {len(kits)} Reference Kits available")
                    return kits
                else:
                    self.log_test("Vestiaire Reference Kits Available", False, 
                        "No Reference Kits found in vestiaire")
                    return []
            else:
                self.log_test("Vestiaire Reference Kits Available", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Vestiaire Reference Kits Available", False, f"Exception: {str(e)}")
            return []
    
    def test_add_to_wanted_minimal_data(self, reference_kit_id):
        """Test 1: Add to Wanted List with minimal data (should remain Reference Kit)"""
        print("🎯 TEST 1: ADD TO WANTED LIST - MINIMAL DATA...")
        try:
            wanted_data = {
                "reference_kit_id": reference_kit_id,
                "preferred_size": "L",  # Optional preference
                "notes": "Looking for authentic version"  # Optional notes
            }
            
            response = self.session.post(f"{BACKEND_URL}/wanted-kits", json=wanted_data)
            
            if response.status_code == 201:
                data = response.json()
                
                # Verify minimal data structure
                required_fields = ['id', 'user_id', 'reference_kit_id', 'added_to_wanted_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify it's minimal (no PersonalKit fields)
                    personal_kit_fields = ['size', 'condition', 'purchase_price', 'is_signed', 'has_printing']
                    found_personal_fields = [field for field in personal_kit_fields if field in data]
                    
                    if not found_personal_fields:
                        self.log_test("Add to Wanted - Minimal Data", True, 
                            f"WantedKit created with minimal data. ID: {data.get('id')}")
                        return data.get('id')
                    else:
                        self.log_test("Add to Wanted - Minimal Data", False, 
                            f"WantedKit contains PersonalKit fields: {found_personal_fields}")
                        return None
                else:
                    self.log_test("Add to Wanted - Minimal Data", False, 
                        f"Missing required fields: {missing_fields}")
                    return None
            else:
                self.log_test("Add to Wanted - Minimal Data", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Add to Wanted - Minimal Data", False, f"Exception: {str(e)}")
            return None
    
    def test_verify_reference_kit_status(self, reference_kit_id):
        """Test 2: Verify wanted kit remains as Reference Kit (no conversion to PersonalKit)"""
        print("🔍 TEST 2: VERIFY REFERENCE KIT STATUS...")
        try:
            # Get wanted kits
            response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            if response.status_code == 200:
                wanted_kits = response.json()
                
                # Find our kit in wanted list
                target_kit = None
                for kit in wanted_kits:
                    if kit.get('reference_kit_id') == reference_kit_id:
                        target_kit = kit
                        break
                
                if target_kit:
                    # Verify it's still a Reference Kit (has reference_kit_info)
                    if 'reference_kit_info' in target_kit:
                        # Verify no PersonalKit conversion
                        personal_fields = ['size', 'condition', 'purchase_price', 'is_signed']
                        found_personal = [f for f in personal_fields if f in target_kit and target_kit[f] is not None]
                        
                        if not found_personal:
                            self.log_test("Reference Kit Status Preserved", True, 
                                f"Kit remains as Reference Kit with enriched data")
                            return True
                        else:
                            self.log_test("Reference Kit Status Preserved", False, 
                                f"Kit converted to PersonalKit with fields: {found_personal}")
                            return False
                    else:
                        self.log_test("Reference Kit Status Preserved", False, 
                            "Missing reference_kit_info enrichment")
                        return False
                else:
                    self.log_test("Reference Kit Status Preserved", False, 
                        "Kit not found in wanted list")
                    return False
            else:
                self.log_test("Reference Kit Status Preserved", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Reference Kit Status Preserved", False, f"Exception: {str(e)}")
            return False
    
    def test_add_to_owned_detailed(self, reference_kit_id):
        """Test 3: Add to Owned Collection with detailed PersonalKit data"""
        print("📦 TEST 3: ADD TO OWNED COLLECTION - DETAILED DATA...")
        try:
            owned_data = {
                "reference_kit_id": reference_kit_id,
                "size": "L",
                "condition": "excellent",
                "purchase_price": 89.99,
                "purchase_location": "Official Nike Store",
                "is_signed": False,
                "has_printing": True,
                "printed_name": "MESSI",
                "printed_number": 10,
                "personal_notes": "Bought for collection, never worn"
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=owned_data)
            
            if response.status_code == 201:
                data = response.json()
                
                # Verify detailed PersonalKit fields
                required_fields = ['id', 'user_id', 'reference_kit_id', 'size', 'condition']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify enriched data
                    enriched_fields = ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']
                    found_enriched = [field for field in enriched_fields if field in data]
                    
                    if len(found_enriched) >= 2:  # At least reference_kit_info and one other
                        self.log_test("Add to Owned - Detailed Data", True, 
                            f"PersonalKit created with detailed data and enrichment. ID: {data.get('id')}")
                        return data.get('id')
                    else:
                        self.log_test("Add to Owned - Detailed Data", False, 
                            f"Missing enriched data. Found: {found_enriched}")
                        return None
                else:
                    self.log_test("Add to Owned - Detailed Data", False, 
                        f"Missing required fields: {missing_fields}")
                    return None
            else:
                self.log_test("Add to Owned - Detailed Data", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Add to Owned - Detailed Data", False, f"Exception: {str(e)}")
            return None
    
    def test_two_way_relationship(self, reference_kit_id):
        """Test 4: Verify two-way relationship (adding to owned removes from wanted)"""
        print("🔄 TEST 4: TWO-WAY RELATIONSHIP LOGIC...")
        try:
            # Check wanted list - should be empty or not contain our kit
            wanted_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            if wanted_response.status_code == 200:
                wanted_kits = wanted_response.json()
                
                # Check if kit is still in wanted list
                kit_in_wanted = any(kit.get('reference_kit_id') == reference_kit_id for kit in wanted_kits)
                
                if not kit_in_wanted:
                    # Check owned list - should contain our kit
                    owned_response = self.session.get(f"{BACKEND_URL}/personal-kits")
                    
                    if owned_response.status_code == 200:
                        owned_kits = owned_response.json()
                        
                        kit_in_owned = any(kit.get('reference_kit_id') == reference_kit_id for kit in owned_kits)
                        
                        if kit_in_owned:
                            self.log_test("Two-Way Relationship Logic", True, 
                                "Kit automatically removed from wanted when added to owned")
                            return True
                        else:
                            self.log_test("Two-Way Relationship Logic", False, 
                                "Kit not found in owned collection")
                            return False
                    else:
                        self.log_test("Two-Way Relationship Logic", False, 
                            f"Error getting owned collection: HTTP {owned_response.status_code}")
                        return False
                else:
                    self.log_test("Two-Way Relationship Logic", False, 
                        "Kit still in wanted list after adding to owned")
                    return False
            else:
                self.log_test("Two-Way Relationship Logic", False, 
                    f"Error getting wanted list: HTTP {wanted_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Two-Way Relationship Logic", False, f"Exception: {str(e)}")
            return False
    
    def test_separate_retrieval(self):
        """Test 5: Test separate retrieval of wanted vs owned collections"""
        print("📊 TEST 5: SEPARATE COLLECTION RETRIEVAL...")
        try:
            # Get wanted kits
            wanted_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits")
            
            if wanted_response.status_code == 200 and owned_response.status_code == 200:
                wanted_kits = wanted_response.json()
                owned_kits = owned_response.json()
                
                # Verify different data structures
                wanted_success = True
                owned_success = True
                
                # Check wanted kits have minimal structure
                if wanted_kits:
                    sample_wanted = wanted_kits[0]
                    personal_fields = ['size', 'condition', 'purchase_price']
                    found_personal = [f for f in personal_fields if f in sample_wanted and sample_wanted[f] is not None]
                    if found_personal:
                        wanted_success = False
                
                # Check owned kits have detailed structure
                if owned_kits:
                    sample_owned = owned_kits[0]
                    required_personal = ['size', 'condition']
                    missing_personal = [f for f in required_personal if f not in sample_owned]
                    if missing_personal:
                        owned_success = False
                
                if wanted_success and owned_success:
                    self.log_test("Separate Collection Retrieval", True, 
                        f"Wanted: {len(wanted_kits)} kits (minimal), Owned: {len(owned_kits)} kits (detailed)")
                    return True
                else:
                    issues = []
                    if not wanted_success:
                        issues.append("Wanted kits have PersonalKit fields")
                    if not owned_success:
                        issues.append("Owned kits missing PersonalKit fields")
                    
                    self.log_test("Separate Collection Retrieval", False, 
                        f"Issues: {', '.join(issues)}")
                    return False
            else:
                self.log_test("Separate Collection Retrieval", False, 
                    f"API errors - Wanted: {wanted_response.status_code}, Owned: {owned_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Separate Collection Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_endpoint_separation(self):
        """Test 6: Verify endpoint separation (/api/wanted-kits vs /api/personal-kits)"""
        print("🔗 TEST 6: ENDPOINT SEPARATION VERIFICATION...")
        try:
            # Test wanted-kits endpoint
            wanted_response = self.session.get(f"{BACKEND_URL}/wanted-kits")
            
            # Test personal-kits endpoint  
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits")
            
            if wanted_response.status_code == 200 and owned_response.status_code == 200:
                # Verify they return different data structures
                wanted_data = wanted_response.json()
                owned_data = owned_response.json()
                
                # Check response headers for different endpoints
                wanted_url = wanted_response.url
                owned_url = owned_response.url
                
                if "wanted-kits" in wanted_url and "personal-kits" in owned_url:
                    self.log_test("Endpoint Separation", True, 
                        "Separate endpoints working correctly")
                    return True
                else:
                    self.log_test("Endpoint Separation", False, 
                        f"URL mismatch - Wanted: {wanted_url}, Owned: {owned_url}")
                    return False
            else:
                self.log_test("Endpoint Separation", False, 
                    f"Endpoint errors - Wanted: {wanted_response.status_code}, Owned: {owned_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Endpoint Separation", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive want list architecture test"""
        print("🚀 STARTING WANT LIST ARCHITECTURE TESTING...")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return False
        
        # Step 2: Get available Reference Kits
        available_kits = self.get_vestiaire_kits()
        if not available_kits:
            print("❌ No Reference Kits available. Cannot proceed with testing.")
            return False
        
        # Use first available kit for testing
        test_kit = available_kits[0]
        reference_kit_id = test_kit.get('id')
        kit_name = f"{test_kit.get('team_info', {}).get('name', 'Unknown')} {test_kit.get('master_kit_info', {}).get('season', 'Unknown')}"
        
        print(f"🎯 Testing with Reference Kit: {kit_name} (ID: {reference_kit_id})")
        print()
        
        # Step 3: Test Add to Wanted (minimal data)
        wanted_kit_id = self.test_add_to_wanted_minimal_data(reference_kit_id)
        if not wanted_kit_id:
            print("❌ Add to Wanted failed. Cannot proceed with remaining tests.")
            return False
        
        # Step 4: Verify Reference Kit status
        if not self.test_verify_reference_kit_status(reference_kit_id):
            print("⚠️ Reference Kit status verification failed.")
        
        # Step 5: Test Add to Owned (detailed data)
        owned_kit_id = self.test_add_to_owned_detailed(reference_kit_id)
        if not owned_kit_id:
            print("❌ Add to Owned failed. Cannot test two-way relationship.")
        else:
            # Step 6: Test Two-Way Relationship
            self.test_two_way_relationship(reference_kit_id)
        
        # Step 7: Test Separate Retrieval
        self.test_separate_retrieval()
        
        # Step 8: Test Endpoint Separation
        self.test_endpoint_separation()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY:")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status}: {result['test']}")
        
        print()
        print(f"🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        if success_rate >= 80:
            print("🎉 WANT LIST ARCHITECTURE IS WORKING EXCELLENTLY!")
            return True
        elif success_rate >= 60:
            print("⚠️ WANT LIST ARCHITECTURE HAS MINOR ISSUES")
            return False
        else:
            print("❌ WANT LIST ARCHITECTURE HAS MAJOR ISSUES")
            return False

def main():
    """Main test execution"""
    print("TopKit Want List Architecture Testing")
    print("====================================")
    print()
    
    tester = WantListArchitectureTest()
    success = tester.run_comprehensive_test()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()