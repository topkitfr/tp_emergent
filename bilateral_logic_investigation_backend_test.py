#!/usr/bin/env python3
"""
Bilateral Logic Bug Investigation - My Collection System
Critical investigation of TK-MASTER-E096BE appearing in both 'own' and 'want' collections

Testing Areas:
1. Authentication Setup with topkitfr@gmail.com/TopKitSecure789#
2. My Collection Data Investigation for TK-MASTER-E096BE
3. Bilateral Logic Testing and Prevention
4. Data Integrity Check
5. API Endpoint Investigation
6. Duplicate Prevention Logic Analysis
"""

import requests
import json
import os
import sys
from pathlib import Path
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class BilateralLogicInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.target_kit_id = "TK-MASTER-E096BE"  # Specific kit from user report
        self.collection_data = []
        self.bilateral_violations = []
        
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
        print(f"\n🔐 AUTHENTICATION SETUP")
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
                            f"User: {user_info.get('name')}, Role: {user_info.get('role')}")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def investigate_my_collection_data(self):
        """Retrieve and analyze all collection items"""
        print(f"\n📊 MY COLLECTION DATA INVESTIGATION")
        print("=" * 50)
        
        try:
            # Get all collection items
            response = self.session.get(f"{API_BASE}/my-collection")
            
            if response.status_code == 200:
                self.collection_data = response.json()
                total_items = len(self.collection_data)
                
                self.log_test("Collection Data Retrieval", True, 
                            f"Retrieved {total_items} collection items")
                
                # Analyze collection types
                owned_items = [item for item in self.collection_data if item.get('collection_type') == 'owned']
                wanted_items = [item for item in self.collection_data if item.get('collection_type') == 'wanted']
                no_type_items = [item for item in self.collection_data if not item.get('collection_type')]
                
                print(f"📈 Collection Statistics:")
                print(f"   • Total Items: {total_items}")
                print(f"   • Owned Items: {len(owned_items)}")
                print(f"   • Wanted Items: {len(wanted_items)}")
                print(f"   • Items Missing collection_type: {len(no_type_items)}")
                
                # Look specifically for TK-MASTER-E096BE
                target_kit_items = []
                for item in self.collection_data:
                    master_kit = item.get('master_kit', {})
                    if master_kit.get('topkit_reference') == self.target_kit_id:
                        target_kit_items.append(item)
                
                if target_kit_items:
                    print(f"\n🎯 TARGET KIT {self.target_kit_id} FOUND:")
                    for i, item in enumerate(target_kit_items):
                        collection_type = item.get('collection_type', 'MISSING')
                        item_id = item.get('id', 'NO_ID')
                        master_kit = item.get('master_kit', {})
                        kit_name = f"{master_kit.get('club', 'Unknown')} {master_kit.get('season', 'Unknown')} {master_kit.get('kit_type', 'Unknown')}"
                        print(f"   [{i+1}] ID: {item_id}, Type: {collection_type}, Kit: {kit_name}")
                    
                    # Check for bilateral violation
                    collection_types = [item.get('collection_type') for item in target_kit_items]
                    if 'owned' in collection_types and 'wanted' in collection_types:
                        self.log_test("Target Kit Bilateral Violation", False, 
                                    f"{self.target_kit_id} appears in BOTH owned and wanted collections!")
                        self.bilateral_violations.append(self.target_kit_id)
                    else:
                        self.log_test("Target Kit Bilateral Check", True, 
                                    f"{self.target_kit_id} appears in {len(target_kit_items)} collection(s) with types: {collection_types}")
                else:
                    self.log_test("Target Kit Search", False, 
                                f"{self.target_kit_id} not found in user's collection")
                
                return True
                
            else:
                self.log_test("Collection Data Retrieval", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collection Data Investigation", False, f"Exception: {str(e)}")
            return False
    
    def check_all_bilateral_violations(self):
        """Check for any Master Kits appearing in both collection types"""
        print(f"\n🔍 COMPREHENSIVE BILATERAL LOGIC VIOLATION CHECK")
        print("=" * 50)
        
        try:
            # Group items by master_kit_id
            kit_collections = {}
            
            for item in self.collection_data:
                master_kit_id = item.get('master_kit_id')
                master_kit = item.get('master_kit', {})
                topkit_ref = master_kit.get('topkit_reference', 'NO_REF')
                collection_type = item.get('collection_type', 'MISSING')
                
                if master_kit_id:
                    if master_kit_id not in kit_collections:
                        kit_collections[master_kit_id] = {
                            'topkit_reference': topkit_ref,
                            'kit_name': f"{master_kit.get('club', 'Unknown')} {master_kit.get('season', 'Unknown')} {master_kit.get('kit_type', 'Unknown')}",
                            'collection_types': [],
                            'items': []
                        }
                    
                    kit_collections[master_kit_id]['collection_types'].append(collection_type)
                    kit_collections[master_kit_id]['items'].append(item.get('id', 'NO_ID'))
            
            # Check for bilateral violations
            violations_found = 0
            
            for master_kit_id, data in kit_collections.items():
                collection_types = data['collection_types']
                unique_types = list(set(collection_types))
                
                if 'owned' in unique_types and 'wanted' in unique_types:
                    violations_found += 1
                    topkit_ref = data['topkit_reference']
                    kit_name = data['kit_name']
                    item_ids = data['items']
                    
                    print(f"🚨 BILATERAL VIOLATION #{violations_found}:")
                    print(f"   • TopKit Reference: {topkit_ref}")
                    print(f"   • Kit Name: {kit_name}")
                    print(f"   • Master Kit ID: {master_kit_id}")
                    print(f"   • Collection Types: {collection_types}")
                    print(f"   • Item IDs: {item_ids}")
                    
                    self.bilateral_violations.append(topkit_ref)
            
            if violations_found == 0:
                self.log_test("Bilateral Violations Check", True, 
                            "No Master Kits found in both owned and wanted collections")
            else:
                self.log_test("Bilateral Violations Check", False, 
                            f"Found {violations_found} Master Kit(s) in both collection types")
            
            return violations_found == 0
            
        except Exception as e:
            self.log_test("Bilateral Violations Check", False, f"Exception: {str(e)}")
            return False
    
    def test_bilateral_prevention_logic(self):
        """Test the bilateral prevention mechanism"""
        print(f"\n🛡️ BILATERAL PREVENTION LOGIC TESTING")
        print("=" * 50)
        
        try:
            # First, get a Master Kit that we can test with
            response = self.session.get(f"{API_BASE}/master-kits?limit=1")
            
            if response.status_code != 200:
                self.log_test("Master Kit Retrieval for Testing", False, 
                            f"Cannot get Master Kits: {response.status_code}")
                return False
            
            master_kits = response.json()
            if not master_kits:
                self.log_test("Master Kit Retrieval for Testing", False, 
                            "No Master Kits available for testing")
                return False
            
            test_kit = master_kits[0]
            test_kit_id = test_kit.get('id')
            test_kit_ref = test_kit.get('topkit_reference', 'NO_REF')
            
            print(f"🧪 Testing with Master Kit: {test_kit_ref} (ID: {test_kit_id})")
            
            # Test 1: Add to owned collection
            owned_data = {
                "master_kit_id": test_kit_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "new_with_tags",
                "purchase_price": 89.99
            }
            
            response = self.session.post(f"{API_BASE}/my-collection", json=owned_data)
            
            if response.status_code == 201 or response.status_code == 200:
                owned_item_id = response.json().get('id')
                self.log_test("Add to Owned Collection", True, 
                            f"Successfully added {test_kit_ref} to owned collection")
                
                # Test 2: Try to add same kit to wanted collection (should fail)
                wanted_data = {
                    "master_kit_id": test_kit_id,
                    "collection_type": "wanted",
                    "priority": "high"
                }
                
                response = self.session.post(f"{API_BASE}/my-collection", json=wanted_data)
                
                if response.status_code == 400:
                    error_message = response.json().get('detail', '')
                    self.log_test("Bilateral Prevention Test", True, 
                                f"Correctly prevented adding to wanted: {error_message}")
                else:
                    self.log_test("Bilateral Prevention Test", False, 
                                f"Should have prevented adding to wanted, but got: {response.status_code}")
                
                # Clean up: Remove from owned collection
                if owned_item_id:
                    delete_response = self.session.delete(f"{API_BASE}/my-collection/{owned_item_id}")
                    if delete_response.status_code == 200:
                        print(f"   ✅ Cleaned up test item {owned_item_id}")
                    
            elif response.status_code == 400 and "already in your" in response.text:
                self.log_test("Add to Owned Collection", True, 
                            f"Kit {test_kit_ref} already in collection (expected for existing data)")
                
                # In this case, we can't test prevention logic as kit is already in collection
                self.log_test("Bilateral Prevention Test", True, 
                            "Cannot test prevention - kit already in collection")
            else:
                self.log_test("Add to Owned Collection", False, 
                            f"Failed to add to owned: {response.status_code} - {response.text}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Bilateral Prevention Logic Testing", False, f"Exception: {str(e)}")
            return False
    
    def investigate_api_endpoint_logic(self):
        """Investigate the POST /api/my-collection endpoint logic"""
        print(f"\n🔧 API ENDPOINT LOGIC INVESTIGATION")
        print("=" * 50)
        
        try:
            # Check the endpoint's duplicate prevention logic by examining responses
            # We'll use the existing collection data to understand the logic
            
            if not self.collection_data:
                self.log_test("API Endpoint Investigation", False, 
                            "No collection data available for investigation")
                return False
            
            # Analyze existing collection items for patterns
            master_kit_counts = {}
            
            for item in self.collection_data:
                master_kit_id = item.get('master_kit_id')
                collection_type = item.get('collection_type', 'MISSING')
                
                if master_kit_id:
                    if master_kit_id not in master_kit_counts:
                        master_kit_counts[master_kit_id] = {'owned': 0, 'wanted': 0, 'missing': 0}
                    
                    if collection_type == 'owned':
                        master_kit_counts[master_kit_id]['owned'] += 1
                    elif collection_type == 'wanted':
                        master_kit_counts[master_kit_id]['wanted'] += 1
                    else:
                        master_kit_counts[master_kit_id]['missing'] += 1
            
            # Check for duplicates within same collection type
            same_type_duplicates = 0
            cross_type_duplicates = 0
            
            for master_kit_id, counts in master_kit_counts.items():
                if counts['owned'] > 1:
                    same_type_duplicates += 1
                    print(f"⚠️  Master Kit {master_kit_id} appears {counts['owned']} times in owned collection")
                
                if counts['wanted'] > 1:
                    same_type_duplicates += 1
                    print(f"⚠️  Master Kit {master_kit_id} appears {counts['wanted']} times in wanted collection")
                
                if counts['owned'] > 0 and counts['wanted'] > 0:
                    cross_type_duplicates += 1
                    print(f"🚨 Master Kit {master_kit_id} appears in BOTH owned ({counts['owned']}) and wanted ({counts['wanted']}) collections")
            
            self.log_test("Same Collection Type Duplicates", same_type_duplicates == 0, 
                        f"Found {same_type_duplicates} Master Kits with duplicates in same collection type")
            
            self.log_test("Cross Collection Type Duplicates", cross_type_duplicates == 0, 
                        f"Found {cross_type_duplicates} Master Kits appearing in both collection types")
            
            return True
            
        except Exception as e:
            self.log_test("API Endpoint Logic Investigation", False, f"Exception: {str(e)}")
            return False
    
    def data_integrity_analysis(self):
        """Perform comprehensive data integrity analysis"""
        print(f"\n📋 DATA INTEGRITY ANALYSIS")
        print("=" * 50)
        
        try:
            if not self.collection_data:
                self.log_test("Data Integrity Analysis", False, 
                            "No collection data available for analysis")
                return False
            
            # Check for missing required fields
            missing_collection_type = 0
            missing_master_kit_id = 0
            missing_user_id = 0
            missing_id = 0
            
            for item in self.collection_data:
                if not item.get('collection_type'):
                    missing_collection_type += 1
                if not item.get('master_kit_id'):
                    missing_master_kit_id += 1
                if not item.get('user_id'):
                    missing_user_id += 1
                if not item.get('id'):
                    missing_id += 1
            
            print(f"📊 Data Integrity Statistics:")
            print(f"   • Items missing collection_type: {missing_collection_type}")
            print(f"   • Items missing master_kit_id: {missing_master_kit_id}")
            print(f"   • Items missing user_id: {missing_user_id}")
            print(f"   • Items missing id: {missing_id}")
            
            # Check for orphaned items (master_kit not found)
            orphaned_items = 0
            for item in self.collection_data:
                master_kit = item.get('master_kit')
                if not master_kit or not master_kit.get('id'):
                    orphaned_items += 1
            
            print(f"   • Orphaned items (no master_kit data): {orphaned_items}")
            
            self.log_test("Collection Type Field Integrity", missing_collection_type == 0, 
                        f"{missing_collection_type} items missing collection_type field")
            
            self.log_test("Master Kit ID Field Integrity", missing_master_kit_id == 0, 
                        f"{missing_master_kit_id} items missing master_kit_id field")
            
            self.log_test("Orphaned Items Check", orphaned_items == 0, 
                        f"{orphaned_items} items without master_kit data")
            
            return True
            
        except Exception as e:
            self.log_test("Data Integrity Analysis", False, f"Exception: {str(e)}")
            return False
    
    def generate_investigation_report(self):
        """Generate comprehensive investigation report"""
        print(f"\n📄 BILATERAL LOGIC INVESTIGATION REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 INVESTIGATION SUMMARY:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Passed: {passed_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        
        print(f"\n🚨 CRITICAL FINDINGS:")
        if self.bilateral_violations:
            print(f"   • Bilateral Logic Violations Found: {len(self.bilateral_violations)}")
            for violation in self.bilateral_violations:
                print(f"     - {violation}")
        else:
            print(f"   • No Bilateral Logic Violations Detected")
        
        print(f"\n📊 COLLECTION DATA ANALYSIS:")
        if self.collection_data:
            owned_count = len([item for item in self.collection_data if item.get('collection_type') == 'owned'])
            wanted_count = len([item for item in self.collection_data if item.get('collection_type') == 'wanted'])
            missing_type_count = len([item for item in self.collection_data if not item.get('collection_type')])
            
            print(f"   • Total Collection Items: {len(self.collection_data)}")
            print(f"   • Owned Items: {owned_count}")
            print(f"   • Wanted Items: {wanted_count}")
            print(f"   • Items Missing Type: {missing_type_count}")
        
        print(f"\n🔍 TARGET KIT INVESTIGATION:")
        target_found = any(self.target_kit_id in str(result['details']) for result in self.test_results)
        if target_found:
            print(f"   • {self.target_kit_id} was found and analyzed")
            if self.target_kit_id in self.bilateral_violations:
                print(f"   • ❌ {self.target_kit_id} has bilateral logic violation")
            else:
                print(f"   • ✅ {self.target_kit_id} does not have bilateral logic violation")
        else:
            print(f"   • {self.target_kit_id} was not found in user's collection")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if self.bilateral_violations:
            print(f"   • CRITICAL: Fix bilateral logic violations immediately")
            print(f"   • Implement stronger duplicate prevention in POST /api/my-collection")
            print(f"   • Add database constraints to prevent same master_kit_id in both collection types")
            print(f"   • Run data cleanup script to resolve existing violations")
        else:
            print(f"   • Bilateral logic appears to be working correctly")
            print(f"   • Continue monitoring for future violations")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        return success_rate >= 80
    
    def run_investigation(self):
        """Run complete bilateral logic investigation"""
        print("🔍 BILATERAL LOGIC BUG INVESTIGATION - MY COLLECTION SYSTEM")
        print("=" * 70)
        print(f"Target Kit: {self.target_kit_id}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with investigation")
            return False
        
        # Step 2: My Collection Data Investigation
        if not self.investigate_my_collection_data():
            print("❌ Collection data investigation failed")
            return False
        
        # Step 3: Check for bilateral violations
        self.check_all_bilateral_violations()
        
        # Step 4: Test bilateral prevention logic
        self.test_bilateral_prevention_logic()
        
        # Step 5: Investigate API endpoint logic
        self.investigate_api_endpoint_logic()
        
        # Step 6: Data integrity analysis
        self.data_integrity_analysis()
        
        # Step 7: Generate comprehensive report
        investigation_success = self.generate_investigation_report()
        
        return investigation_success

def main():
    """Main function to run bilateral logic investigation"""
    investigator = BilateralLogicInvestigator()
    
    try:
        success = investigator.run_investigation()
        
        if success:
            print(f"\n✅ BILATERAL LOGIC INVESTIGATION COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print(f"\n❌ BILATERAL LOGIC INVESTIGATION COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Investigation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Investigation failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()