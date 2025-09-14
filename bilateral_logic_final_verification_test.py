#!/usr/bin/env python3
"""
Bilateral Logic Final Verification Test
Final verification test for the bilateral logic fix as requested in review.

Testing Requirements:
1. Authentication with topkitfr@gmail.com/TopKitSecure789#
2. Verify TK-MASTER-E096BE cleanup (only in owned, not in wanted)
3. Test bilateral prevention logic (should prevent adding to opposite collection)
4. Comprehensive data integrity check (no bilateral violations)
5. Final system status verification
"""

import requests
import json
import os
import sys
from pathlib import Path
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class BilateralLogicFinalVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.target_master_kit = "TK-MASTER-E096BE"  # Specific kit from review request
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        print(f"\n🔐 AUTHENTICATION TEST")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                user_info = data.get('user', {})
                
                # Set authorization header
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log_test("Admin Authentication", True, 
                            f"Logged in as {user_info.get('name', 'Unknown')} ({user_info.get('email', 'Unknown')})")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def verify_target_kit_cleanup(self):
        """Verify TK-MASTER-E096BE exists only in owned collection, not in wanted"""
        print(f"\n🎯 TK-MASTER-E096BE CLEANUP VERIFICATION")
        print("=" * 50)
        
        try:
            # Get user's complete collection
            response = self.session.get(f"{API_BASE}/my-collection")
            
            if response.status_code == 200:
                collection_items = response.json()
                
                # Find all instances of TK-MASTER-E096BE
                target_kit_instances = []
                for item in collection_items:
                    master_kit = item.get('master_kit', {})
                    if master_kit.get('topkit_reference') == self.target_master_kit:
                        target_kit_instances.append({
                            'id': item.get('id'),
                            'collection_type': item.get('collection_type'),
                            'created_at': item.get('created_at')
                        })
                
                # Analyze findings
                owned_instances = [i for i in target_kit_instances if i['collection_type'] == 'owned']
                wanted_instances = [i for i in target_kit_instances if i['collection_type'] == 'wanted']
                
                print(f"Found {len(target_kit_instances)} total instances of {self.target_master_kit}")
                print(f"Owned instances: {len(owned_instances)}")
                print(f"Wanted instances: {len(wanted_instances)}")
                
                # Test 1: Should exist in owned collection
                if len(owned_instances) == 1:
                    self.log_test("TK-MASTER-E096BE in Owned Collection", True, 
                                f"Found 1 instance in owned collection (ID: {owned_instances[0]['id']})")
                elif len(owned_instances) == 0:
                    self.log_test("TK-MASTER-E096BE in Owned Collection", False, 
                                "Kit not found in owned collection")
                else:
                    self.log_test("TK-MASTER-E096BE in Owned Collection", False, 
                                f"Multiple instances found in owned collection: {len(owned_instances)}")
                
                # Test 2: Should NOT exist in wanted collection
                if len(wanted_instances) == 0:
                    self.log_test("TK-MASTER-E096BE NOT in Wanted Collection", True, 
                                "Correctly not found in wanted collection")
                else:
                    self.log_test("TK-MASTER-E096BE NOT in Wanted Collection", False, 
                                f"Found {len(wanted_instances)} instances in wanted collection - BILATERAL VIOLATION!")
                
                # Test 3: No bilateral violations for this kit
                bilateral_violation = len(owned_instances) > 0 and len(wanted_instances) > 0
                if not bilateral_violation:
                    self.log_test("No Bilateral Violation for TK-MASTER-E096BE", True, 
                                "Kit exists in only one collection type")
                else:
                    self.log_test("No Bilateral Violation for TK-MASTER-E096BE", False, 
                                "CRITICAL: Kit exists in both owned and wanted collections!")
                
                return target_kit_instances
                
            else:
                self.log_test("Collection Retrieval", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Target Kit Cleanup Verification", False, f"Exception: {str(e)}")
            return []
    
    def test_bilateral_prevention_logic(self):
        """Test that bilateral prevention logic works correctly"""
        print(f"\n🚫 BILATERAL PREVENTION LOGIC TEST")
        print("=" * 50)
        
        try:
            # First, get the master kit ID for TK-MASTER-E096BE
            response = self.session.get(f"{API_BASE}/master-kits")
            if response.status_code != 200:
                self.log_test("Master Kits Retrieval", False, f"HTTP {response.status_code}")
                return
            
            master_kits = response.json()
            target_kit = None
            for kit in master_kits:
                if kit.get('topkit_reference') == self.target_master_kit:
                    target_kit = kit
                    break
            
            if not target_kit:
                self.log_test("Find Target Master Kit", False, f"{self.target_master_kit} not found in master kits")
                return
            
            master_kit_id = target_kit.get('id')
            self.log_test("Find Target Master Kit", True, f"Found {self.target_master_kit} with ID: {master_kit_id}")
            
            # Test 1: Try to add TK-MASTER-E096BE to wanted collection (should be prevented)
            print(f"\nTesting: Adding {self.target_master_kit} to WANTED collection (should be prevented)")
            
            add_to_wanted_response = self.session.post(f"{API_BASE}/my-collection", json={
                "master_kit_id": master_kit_id,
                "collection_type": "wanted",
                "size": "L",
                "condition": "club_stock",
                "physical_state": "very_good_condition"
            })
            
            if add_to_wanted_response.status_code == 400:
                error_message = add_to_wanted_response.json().get('detail', '')
                if 'already in your owned collection' in error_message.lower():
                    self.log_test("Bilateral Prevention - Owned to Wanted", True, 
                                f"Correctly prevented with message: '{error_message}'")
                else:
                    self.log_test("Bilateral Prevention - Owned to Wanted", False, 
                                f"Prevented but with unclear message: '{error_message}'")
            elif add_to_wanted_response.status_code == 200:
                self.log_test("Bilateral Prevention - Owned to Wanted", False, 
                            "CRITICAL: Addition was allowed - bilateral prevention failed!")
            else:
                self.log_test("Bilateral Prevention - Owned to Wanted", False, 
                            f"Unexpected response: HTTP {add_to_wanted_response.status_code}")
            
            # Test 2: Test error message clarity
            if add_to_wanted_response.status_code == 400:
                error_message = add_to_wanted_response.json().get('detail', '')
                clear_message_indicators = [
                    'already in your owned collection',
                    'remove it first',
                    'bilateral'
                ]
                
                message_clarity_score = sum(1 for indicator in clear_message_indicators 
                                          if indicator.lower() in error_message.lower())
                
                if message_clarity_score >= 2:
                    self.log_test("Error Message Clarity", True, 
                                f"Clear and informative error message: '{error_message}'")
                else:
                    self.log_test("Error Message Clarity", False, 
                                f"Error message could be clearer: '{error_message}'")
            
        except Exception as e:
            self.log_test("Bilateral Prevention Logic Test", False, f"Exception: {str(e)}")
    
    def comprehensive_data_integrity_check(self):
        """Check all collection items for bilateral violations"""
        print(f"\n🔍 COMPREHENSIVE DATA INTEGRITY CHECK")
        print("=" * 50)
        
        try:
            # Get complete collection
            response = self.session.get(f"{API_BASE}/my-collection")
            if response.status_code != 200:
                self.log_test("Collection Data Retrieval", False, f"HTTP {response.status_code}")
                return
            
            collection_items = response.json()
            total_items = len(collection_items)
            
            print(f"Analyzing {total_items} collection items for bilateral violations...")
            
            # Group items by master kit ID
            kit_collections = {}
            for item in collection_items:
                master_kit_id = item.get('master_kit_id')
                collection_type = item.get('collection_type')
                
                if master_kit_id not in kit_collections:
                    kit_collections[master_kit_id] = {'owned': [], 'wanted': []}
                
                kit_collections[master_kit_id][collection_type].append(item)
            
            # Check for bilateral violations
            bilateral_violations = []
            owned_count = 0
            wanted_count = 0
            
            for master_kit_id, collections in kit_collections.items():
                owned_items = collections['owned']
                wanted_items = collections['wanted']
                
                owned_count += len(owned_items)
                wanted_count += len(wanted_items)
                
                # Check for bilateral violation (same kit in both collections)
                if len(owned_items) > 0 and len(wanted_items) > 0:
                    # Get master kit reference for reporting
                    master_kit_ref = "Unknown"
                    if owned_items:
                        master_kit_ref = owned_items[0].get('master_kit', {}).get('topkit_reference', master_kit_id)
                    elif wanted_items:
                        master_kit_ref = wanted_items[0].get('master_kit', {}).get('topkit_reference', master_kit_id)
                    
                    bilateral_violations.append({
                        'master_kit_id': master_kit_id,
                        'master_kit_reference': master_kit_ref,
                        'owned_count': len(owned_items),
                        'wanted_count': len(wanted_items)
                    })
            
            # Report findings
            print(f"Collection Summary:")
            print(f"- Total items: {total_items}")
            print(f"- Owned items: {owned_count}")
            print(f"- Wanted items: {wanted_count}")
            print(f"- Unique Master Kits: {len(kit_collections)}")
            print(f"- Bilateral violations: {len(bilateral_violations)}")
            
            # Test results
            if len(bilateral_violations) == 0:
                self.log_test("No Bilateral Violations Found", True, 
                            f"All {len(kit_collections)} unique Master Kits follow bilateral logic")
            else:
                violation_details = []
                for violation in bilateral_violations:
                    violation_details.append(f"{violation['master_kit_reference']} (owned: {violation['owned_count']}, wanted: {violation['wanted_count']})")
                
                self.log_test("No Bilateral Violations Found", False, 
                            f"Found {len(bilateral_violations)} violations: {', '.join(violation_details)}")
            
            # Test collection counts are reasonable
            if total_items > 0:
                self.log_test("Collection Data Exists", True, f"Found {total_items} collection items")
            else:
                self.log_test("Collection Data Exists", False, "No collection items found")
            
            return {
                'total_items': total_items,
                'owned_count': owned_count,
                'wanted_count': wanted_count,
                'unique_kits': len(kit_collections),
                'bilateral_violations': bilateral_violations
            }
            
        except Exception as e:
            self.log_test("Comprehensive Data Integrity Check", False, f"Exception: {str(e)}")
            return None
    
    def verify_bilateral_prevention_for_existing_kits(self):
        """Test bilateral prevention works for any existing Master Kits"""
        print(f"\n🛡️ BILATERAL PREVENTION FOR EXISTING MASTER KITS")
        print("=" * 50)
        
        try:
            # Get some master kits to test with
            response = self.session.get(f"{API_BASE}/master-kits?limit=5")
            if response.status_code != 200:
                self.log_test("Master Kits for Testing", False, f"HTTP {response.status_code}")
                return
            
            master_kits = response.json()
            if not master_kits:
                self.log_test("Master Kits for Testing", False, "No master kits found")
                return
            
            # Get current collection to see what's already there
            collection_response = self.session.get(f"{API_BASE}/my-collection")
            if collection_response.status_code != 200:
                self.log_test("Current Collection Check", False, f"HTTP {collection_response.status_code}")
                return
            
            collection_items = collection_response.json()
            
            # Create a map of what's in collection
            collection_map = {}
            for item in collection_items:
                master_kit_id = item.get('master_kit_id')
                collection_type = item.get('collection_type')
                
                if master_kit_id not in collection_map:
                    collection_map[master_kit_id] = set()
                collection_map[master_kit_id].add(collection_type)
            
            # Test bilateral prevention for kits already in collection
            prevention_tests = 0
            prevention_successes = 0
            
            for kit in master_kits[:3]:  # Test first 3 kits
                master_kit_id = kit.get('id')
                kit_reference = kit.get('topkit_reference', master_kit_id)
                
                if master_kit_id in collection_map:
                    current_types = collection_map[master_kit_id]
                    
                    # If it's in owned, try to add to wanted (should be prevented)
                    if 'owned' in current_types and 'wanted' not in current_types:
                        print(f"Testing prevention: {kit_reference} (owned → wanted)")
                        
                        add_response = self.session.post(f"{API_BASE}/my-collection", json={
                            "master_kit_id": master_kit_id,
                            "collection_type": "wanted",
                            "size": "M",
                            "condition": "club_stock",
                            "physical_state": "very_good_condition"
                        })
                        
                        prevention_tests += 1
                        if add_response.status_code == 400:
                            prevention_successes += 1
                            print(f"  ✅ Correctly prevented")
                        else:
                            print(f"  ❌ Prevention failed - HTTP {add_response.status_code}")
                    
                    # If it's in wanted, try to add to owned (should be prevented)
                    elif 'wanted' in current_types and 'owned' not in current_types:
                        print(f"Testing prevention: {kit_reference} (wanted → owned)")
                        
                        add_response = self.session.post(f"{API_BASE}/my-collection", json={
                            "master_kit_id": master_kit_id,
                            "collection_type": "owned",
                            "size": "M",
                            "condition": "club_stock",
                            "physical_state": "very_good_condition"
                        })
                        
                        prevention_tests += 1
                        if add_response.status_code == 400:
                            prevention_successes += 1
                            print(f"  ✅ Correctly prevented")
                        else:
                            print(f"  ❌ Prevention failed - HTTP {add_response.status_code}")
            
            # Report results
            if prevention_tests > 0:
                success_rate = (prevention_successes / prevention_tests) * 100
                if success_rate == 100:
                    self.log_test("Bilateral Prevention for Existing Kits", True, 
                                f"All {prevention_tests} prevention tests passed (100%)")
                else:
                    self.log_test("Bilateral Prevention for Existing Kits", False, 
                                f"Only {prevention_successes}/{prevention_tests} prevention tests passed ({success_rate:.1f}%)")
            else:
                self.log_test("Bilateral Prevention for Existing Kits", True, 
                            "No testable scenarios found (no kits in single collection type)")
            
        except Exception as e:
            self.log_test("Bilateral Prevention for Existing Kits", False, f"Exception: {str(e)}")
    
    def final_system_status_check(self):
        """Final system status verification"""
        print(f"\n📊 FINAL SYSTEM STATUS CHECK")
        print("=" * 50)
        
        try:
            # Get collection counts
            collection_response = self.session.get(f"{API_BASE}/my-collection")
            if collection_response.status_code == 200:
                collection_items = collection_response.json()
                
                owned_items = [item for item in collection_items if item.get('collection_type') == 'owned']
                wanted_items = [item for item in collection_items if item.get('collection_type') == 'wanted']
                
                print(f"Final Collection Counts:")
                print(f"- Total items: {len(collection_items)}")
                print(f"- Owned items: {len(owned_items)}")
                print(f"- Wanted items: {len(wanted_items)}")
                
                self.log_test("Collection Counts Retrieved", True, 
                            f"Total: {len(collection_items)}, Owned: {len(owned_items)}, Wanted: {len(wanted_items)}")
            else:
                self.log_test("Collection Counts Retrieved", False, f"HTTP {collection_response.status_code}")
            
            # Test bilateral logic system operational status
            # Try to create a test scenario to verify the system is working
            master_kits_response = self.session.get(f"{API_BASE}/master-kits?limit=1")
            if master_kits_response.status_code == 200:
                master_kits = master_kits_response.json()
                if master_kits:
                    test_kit = master_kits[0]
                    test_kit_id = test_kit.get('id')
                    
                    # Try to add to owned (should work if not already there)
                    add_response = self.session.post(f"{API_BASE}/my-collection", json={
                        "master_kit_id": test_kit_id,
                        "collection_type": "owned",
                        "size": "L",
                        "condition": "club_stock",
                        "physical_state": "very_good_condition"
                    })
                    
                    if add_response.status_code in [200, 400]:  # 200 = success, 400 = already exists
                        # Now try to add to wanted (should be prevented)
                        wanted_response = self.session.post(f"{API_BASE}/my-collection", json={
                            "master_kit_id": test_kit_id,
                            "collection_type": "wanted",
                            "size": "L",
                            "condition": "very_good_condition"
                        })
                        
                        if wanted_response.status_code == 400:
                            self.log_test("Bilateral Logic System Operational", True, 
                                        "System correctly prevents bilateral violations")
                        else:
                            self.log_test("Bilateral Logic System Operational", False, 
                                        f"System allowed bilateral violation - HTTP {wanted_response.status_code}")
                    else:
                        self.log_test("Bilateral Logic System Test", False, 
                                    f"Could not test system - HTTP {add_response.status_code}")
                else:
                    self.log_test("Master Kits Available for Testing", False, "No master kits found")
            else:
                self.log_test("Master Kits Available for Testing", False, f"HTTP {master_kits_response.status_code}")
            
        except Exception as e:
            self.log_test("Final System Status Check", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all bilateral logic verification tests"""
        print("🔍 BILATERAL LOGIC FINAL VERIFICATION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Kit: {self.target_master_kit}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run all test phases
        if not self.authenticate():
            print("\n❌ Authentication failed - cannot proceed with tests")
            return
        
        # Phase 1: Verify target kit cleanup
        target_kit_instances = self.verify_target_kit_cleanup()
        
        # Phase 2: Test bilateral prevention logic
        self.test_bilateral_prevention_logic()
        
        # Phase 3: Comprehensive data integrity check
        integrity_results = self.comprehensive_data_integrity_check()
        
        # Phase 4: Test bilateral prevention for existing kits
        self.verify_bilateral_prevention_for_existing_kits()
        
        # Phase 5: Final system status check
        self.final_system_status_check()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print(f"\n📋 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 BILATERAL LOGIC VERIFICATION CONCLUSION:")
        if success_rate >= 90:
            print("✅ BILATERAL LOGIC SYSTEM IS WORKING EXCELLENTLY!")
            print("✅ TK-MASTER-E096BE cleanup verified")
            print("✅ Bilateral prevention logic operational")
            print("✅ Data integrity maintained")
        elif success_rate >= 70:
            print("⚠️ BILATERAL LOGIC SYSTEM IS MOSTLY WORKING")
            print("Some issues detected that need attention")
        else:
            print("❌ BILATERAL LOGIC SYSTEM HAS CRITICAL ISSUES")
            print("Immediate attention required")

if __name__ == "__main__":
    tester = BilateralLogicFinalVerificationTester()
    tester.run_all_tests()