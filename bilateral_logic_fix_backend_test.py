#!/usr/bin/env python3
"""
Bilateral Logic Fix Backend Testing
Testing the bilateral logic prevention fix for My Collection system:
- Authentication with topkitfr@gmail.com/TopKitSecure789#
- Bilateral Logic Prevention Testing
- Same-Type Duplicate Prevention Still Working
- Data Integrity Check for TK-MASTER-E096BE
- Test New Master Kit Addition
"""

import requests
import json
import os
import sys
from pathlib import Path
import time
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class BilateralLogicTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.target_master_kit = "TK-MASTER-E096BE"  # Specific kit mentioned in review
        
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
        try:
            print(f"\n🔐 AUTHENTICATING WITH {ADMIN_EMAIL}")
            
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
                
                self.log_test("Authentication", True, 
                    f"Logged in as {user_info.get('name', 'Unknown')} ({user_info.get('role', 'user')})")
                return True
            else:
                self.log_test("Authentication", False, 
                    f"Status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_my_collection(self):
        """Get current user's collection"""
        try:
            print(f"\n📋 GETTING MY COLLECTION")
            
            response = self.session.get(f"{API_BASE}/my-collection")
            
            if response.status_code == 200:
                collection = response.json()
                
                # Analyze collection by type
                owned_items = [item for item in collection if item.get('collection_type') == 'owned']
                wanted_items = [item for item in collection if item.get('collection_type') == 'wanted']
                
                self.log_test("Get My Collection", True, 
                    f"Found {len(collection)} total items: {len(owned_items)} owned, {len(wanted_items)} wanted")
                
                return {
                    'all': collection,
                    'owned': owned_items,
                    'wanted': wanted_items
                }
            else:
                self.log_test("Get My Collection", False, 
                    f"Status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Get My Collection", False, f"Exception: {str(e)}")
            return None
    
    def check_bilateral_violation(self, collection_data):
        """Check for existing bilateral violations"""
        try:
            print(f"\n🔍 CHECKING FOR BILATERAL VIOLATIONS")
            
            if not collection_data:
                self.log_test("Bilateral Violation Check", False, "No collection data available")
                return []
            
            owned_kits = {item['master_kit_id']: item for item in collection_data['owned']}
            wanted_kits = {item['master_kit_id']: item for item in collection_data['wanted']}
            
            # Find kits that exist in both collections
            bilateral_violations = []
            for kit_id in owned_kits.keys():
                if kit_id in wanted_kits:
                    bilateral_violations.append({
                        'master_kit_id': kit_id,
                        'owned_item': owned_kits[kit_id],
                        'wanted_item': wanted_kits[kit_id]
                    })
            
            # Check specifically for TK-MASTER-E096BE
            target_violation = None
            for violation in bilateral_violations:
                if self.target_master_kit in str(violation.get('master_kit_id', '')):
                    target_violation = violation
                    break
            
            if bilateral_violations:
                violation_details = f"Found {len(bilateral_violations)} bilateral violations"
                if target_violation:
                    violation_details += f", including target kit {self.target_master_kit}"
                self.log_test("Bilateral Violation Check", True, violation_details)
            else:
                self.log_test("Bilateral Violation Check", True, "No bilateral violations found")
            
            return bilateral_violations
            
        except Exception as e:
            self.log_test("Bilateral Violation Check", False, f"Exception: {str(e)}")
            return []
    
    def get_available_master_kits(self):
        """Get available Master Kits for testing"""
        try:
            print(f"\n📦 GETTING AVAILABLE MASTER KITS")
            
            response = self.session.get(f"{API_BASE}/master-kits?limit=10")
            
            if response.status_code == 200:
                master_kits = response.json()
                self.log_test("Get Master Kits", True, f"Found {len(master_kits)} Master Kits")
                return master_kits
            else:
                self.log_test("Get Master Kits", False, 
                    f"Status {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Get Master Kits", False, f"Exception: {str(e)}")
            return []
    
    def test_bilateral_prevention_owned_to_wanted(self, collection_data, master_kits):
        """Test: Try to add Master Kit from owned collection to wanted collection"""
        try:
            print(f"\n🚫 TESTING BILATERAL PREVENTION: OWNED → WANTED")
            
            if not collection_data or not collection_data['owned']:
                self.log_test("Bilateral Prevention (Owned→Wanted)", False, 
                    "No owned items to test with")
                return False
            
            # Get first owned item
            owned_item = collection_data['owned'][0]
            master_kit_id = owned_item['master_kit_id']
            
            print(f"Attempting to add owned Master Kit {master_kit_id} to wanted collection...")
            
            response = self.session.post(f"{API_BASE}/my-collection", json={
                "master_kit_id": master_kit_id,
                "collection_type": "wanted",
                "size": "L",
                "condition": "very_good_condition"
            })
            
            if response.status_code == 400:
                error_msg = response.json().get('detail', '')
                if 'already in your owned collection' in error_msg.lower():
                    self.log_test("Bilateral Prevention (Owned→Wanted)", True, 
                        f"Correctly prevented: {error_msg}")
                    return True
                else:
                    self.log_test("Bilateral Prevention (Owned→Wanted)", False, 
                        f"Wrong error message: {error_msg}")
                    return False
            else:
                self.log_test("Bilateral Prevention (Owned→Wanted)", False, 
                    f"Should have been prevented but got status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Bilateral Prevention (Owned→Wanted)", False, f"Exception: {str(e)}")
            return False
    
    def test_bilateral_prevention_wanted_to_owned(self, collection_data, master_kits):
        """Test: Try to add Master Kit from wanted collection to owned collection"""
        try:
            print(f"\n🚫 TESTING BILATERAL PREVENTION: WANTED → OWNED")
            
            if not collection_data or not collection_data['wanted']:
                self.log_test("Bilateral Prevention (Wanted→Owned)", False, 
                    "No wanted items to test with")
                return False
            
            # Get first wanted item
            wanted_item = collection_data['wanted'][0]
            master_kit_id = wanted_item['master_kit_id']
            
            print(f"Attempting to add wanted Master Kit {master_kit_id} to owned collection...")
            
            response = self.session.post(f"{API_BASE}/my-collection", json={
                "master_kit_id": master_kit_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "very_good_condition",
                "purchase_price": 120.00
            })
            
            if response.status_code == 400:
                error_msg = response.json().get('detail', '')
                if 'already in your want list' in error_msg.lower():
                    self.log_test("Bilateral Prevention (Wanted→Owned)", True, 
                        f"Correctly prevented: {error_msg}")
                    return True
                else:
                    self.log_test("Bilateral Prevention (Wanted→Owned)", False, 
                        f"Wrong error message: {error_msg}")
                    return False
            else:
                self.log_test("Bilateral Prevention (Wanted→Owned)", False, 
                    f"Should have been prevented but got status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Bilateral Prevention (Wanted→Owned)", False, f"Exception: {str(e)}")
            return False
    
    def test_same_type_duplicate_prevention(self, collection_data):
        """Test: Same-type duplicate prevention still works"""
        try:
            print(f"\n🔄 TESTING SAME-TYPE DUPLICATE PREVENTION")
            
            if not collection_data or not collection_data['owned']:
                self.log_test("Same-Type Duplicate Prevention", False, 
                    "No owned items to test with")
                return False
            
            # Try to add same Master Kit to same collection type
            owned_item = collection_data['owned'][0]
            master_kit_id = owned_item['master_kit_id']
            
            print(f"Attempting to add owned Master Kit {master_kit_id} to owned collection again...")
            
            response = self.session.post(f"{API_BASE}/my-collection", json={
                "master_kit_id": master_kit_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "new_with_tags",
                "purchase_price": 150.00
            })
            
            if response.status_code == 400:
                error_msg = response.json().get('detail', '')
                if 'already in your owned collection' in error_msg.lower():
                    self.log_test("Same-Type Duplicate Prevention", True, 
                        f"Correctly prevented: {error_msg}")
                    return True
                else:
                    self.log_test("Same-Type Duplicate Prevention", False, 
                        f"Wrong error message: {error_msg}")
                    return False
            else:
                self.log_test("Same-Type Duplicate Prevention", False, 
                    f"Should have been prevented but got status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Same-Type Duplicate Prevention", False, f"Exception: {str(e)}")
            return False
    
    def test_new_master_kit_addition(self, collection_data, master_kits):
        """Test: Add completely new Master Kit that doesn't exist in any collection"""
        try:
            print(f"\n➕ TESTING NEW MASTER KIT ADDITION")
            
            if not master_kits:
                self.log_test("New Master Kit Addition", False, "No Master Kits available")
                return False
            
            # Find a Master Kit not in any collection
            existing_kit_ids = set()
            if collection_data:
                for item in collection_data['all']:
                    existing_kit_ids.add(item['master_kit_id'])
            
            new_kit = None
            for kit in master_kits:
                if kit['id'] not in existing_kit_ids:
                    new_kit = kit
                    break
            
            if not new_kit:
                self.log_test("New Master Kit Addition", False, 
                    "All available Master Kits are already in collection")
                return False
            
            print(f"Attempting to add new Master Kit {new_kit['id']} to owned collection...")
            
            response = self.session.post(f"{API_BASE}/my-collection", json={
                "master_kit_id": new_kit['id'],
                "collection_type": "owned",
                "size": "L",
                "condition": "very_good_condition",
                "purchase_price": 100.00
            })
            
            if response.status_code == 200:
                self.log_test("New Master Kit Addition (Owned)", True, 
                    f"Successfully added {new_kit['id']} to owned collection")
                
                # Now try adding same kit to wanted collection (should be prevented)
                print(f"Now attempting to add same kit to wanted collection (should be prevented)...")
                
                response2 = self.session.post(f"{API_BASE}/my-collection", json={
                    "master_kit_id": new_kit['id'],
                    "collection_type": "wanted",
                    "size": "M",
                    "condition": "new_with_tags"
                })
                
                if response2.status_code == 400:
                    error_msg = response2.json().get('detail', '')
                    self.log_test("New Master Kit Addition (Bilateral Prevention)", True, 
                        f"Correctly prevented bilateral addition: {error_msg}")
                else:
                    self.log_test("New Master Kit Addition (Bilateral Prevention)", False, 
                        f"Should have prevented bilateral addition but got status {response2.status_code}")
                
                return True
            else:
                self.log_test("New Master Kit Addition (Owned)", False, 
                    f"Failed to add new kit: Status {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            self.log_test("New Master Kit Addition", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive bilateral logic testing"""
        print("=" * 80)
        print("🧪 BILATERAL LOGIC FIX COMPREHENSIVE TESTING")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("\n❌ AUTHENTICATION FAILED - CANNOT CONTINUE")
            return False
        
        # Step 2: Get current collection state
        collection_data = self.get_my_collection()
        
        # Step 3: Check for existing bilateral violations
        violations = self.check_bilateral_violation(collection_data)
        
        # Step 4: Get available Master Kits
        master_kits = self.get_available_master_kits()
        
        # Step 5: Test bilateral prevention (owned → wanted)
        self.test_bilateral_prevention_owned_to_wanted(collection_data, master_kits)
        
        # Step 6: Test bilateral prevention (wanted → owned)
        self.test_bilateral_prevention_wanted_to_owned(collection_data, master_kits)
        
        # Step 7: Test same-type duplicate prevention still works
        self.test_same_type_duplicate_prevention(collection_data)
        
        # Step 8: Test new Master Kit addition
        self.test_new_master_kit_addition(collection_data, master_kits)
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 BILATERAL LOGIC FIX TEST RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Summary of key findings
        print(f"\n🔍 KEY FINDINGS:")
        if violations:
            print(f"• Found {len(violations)} existing bilateral violations (expected until cleanup)")
            if any(self.target_master_kit in str(v.get('master_kit_id', '')) for v in violations):
                print(f"• Target kit {self.target_master_kit} confirmed in both collections")
        else:
            print(f"• No bilateral violations found")
        
        # Determine overall success
        critical_tests = [
            "Bilateral Prevention (Owned→Wanted)",
            "Bilateral Prevention (Wanted→Owned)",
            "Same-Type Duplicate Prevention"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        if critical_passed == len(critical_tests):
            print(f"\n✅ BILATERAL LOGIC FIX IS WORKING CORRECTLY!")
            print(f"• New bilateral violations are being prevented")
            print(f"• Same-type duplicate prevention still works")
            print(f"• Error messages are clear and informative")
        else:
            print(f"\n❌ BILATERAL LOGIC FIX HAS ISSUES!")
            print(f"• {len(critical_tests) - critical_passed} critical tests failed")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = BilateralLogicTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()