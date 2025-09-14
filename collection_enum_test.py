#!/usr/bin/env python3
"""
Collection Saving Bug Fix Testing - Enum Values Verification
Testing the collection saving bug fix after updating enum values

CRITICAL BUG FIXED:
- Updated frontend enum values for condition/physical_state fields
- Frontend was sending wrong enum values causing 422 errors
- Backend expects: condition = KitCondition enum ('club_stock', 'match_prepared', 'match_worn', 'training', 'other')
- Backend expects: physical_state = PhysicalState enum ('new_with_tags', 'very_good_condition', 'used', 'damaged', 'needs_restoration')

TEST REQUIREMENTS:
1. Create Test Master Kit for collection testing
2. Test Collection Saving with CORRECT Enums (condition: "club_stock", physical_state: "new_with_tags")
3. Test Collection Retrieval
4. Test Want List functionality
5. Test Both Collection Types filtering

Authentication: topkitfr@gmail.com / TopKitSecure789#
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://kit-fixes.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class CollectionEnumTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_data = None
        self.test_master_kit_id = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate_admin(self):
        """Authenticate with admin credentials"""
        print("🔐 Authenticating admin user...")
        
        login_data = {
            "email": "topkitfr@gmail.com",
            "password": "TopKitSecure789#"
        }
        
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get('token')
                    self.user_data = data.get('user')
                    print(f"✅ Admin authentication successful")
                    print(f"   User: {self.user_data.get('name')} ({self.user_data.get('role')})")
                    print(f"   Token length: {len(self.auth_token)} characters")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def create_test_master_kit(self):
        """Create a test Master Kit for collection testing"""
        print("\n📦 Creating test Master Kit...")
        
        master_kit_data = {
            "club": "Test Collection Club",
            "season": "2024-25",
            "kit_type": "home",
            "competition": "Test League",
            "model": "authentic",
            "brand": "Test Brand",
            "gender": "men",
            "front_photo_url": "test_photo.jpg"
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/master-kits",
                json=master_kit_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_master_kit_id = data.get('id')
                    print(f"✅ Test Master Kit created successfully")
                    print(f"   ID: {self.test_master_kit_id}")
                    print(f"   TopKit Reference: {data.get('topkit_reference')}")
                    print(f"   Club: {data.get('club')}")
                    print(f"   Season: {data.get('season')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Master Kit creation failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Master Kit creation error: {str(e)}")
            return False
            
    async def test_collection_saving_with_correct_enums(self):
        """Test collection saving with CORRECT enum values"""
        print("\n🎯 Testing Collection Saving with CORRECT Enum Values...")
        
        # Test data with CORRECT enum values as specified in review request
        collection_data = {
            "master_kit_id": self.test_master_kit_id,
            "collection_type": "owned",
            "condition": "club_stock",  # CORRECT KitCondition enum value
            "physical_state": "new_with_tags",  # CORRECT PhysicalState enum value
            "size": "L",
            "purchase_price": 120.00,
            "purchase_date": "2024-01-15",
            "personal_notes": "Test collection item with correct enum values"
        }
        
        print(f"   Testing with condition: '{collection_data['condition']}' (KitCondition enum)")
        print(f"   Testing with physical_state: '{collection_data['physical_state']}' (PhysicalState enum)")
        
        try:
            async with self.session.post(
                f"{API_BASE}/my-collection",
                json=collection_data,
                headers=self.get_auth_headers()
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Collection saving SUCCESS - No more 422 errors!")
                    print(f"   Response status: {response.status}")
                    print(f"   Collection ID: {data.get('id')}")
                    print(f"   Collection type: {data.get('collection_type')}")
                    print(f"   Condition: {data.get('condition')}")
                    print(f"   Physical state: {data.get('physical_state')}")
                    print(f"   Size: {data.get('size')}")
                    print(f"   Purchase price: €{data.get('purchase_price')}")
                    
                    self.test_results.append({
                        "test": "Collection Saving with Correct Enums",
                        "status": "PASS",
                        "details": f"Successfully saved with condition='{collection_data['condition']}' and physical_state='{collection_data['physical_state']}'"
                    })
                    return True
                else:
                    print(f"❌ Collection saving FAILED: {response.status}")
                    print(f"   Response: {response_text}")
                    
                    # Check if it's the old 422 error
                    if response.status == 422:
                        print("🚨 CRITICAL: Still getting 422 errors - enum fix not working!")
                        try:
                            error_data = json.loads(response_text)
                            print(f"   Error details: {error_data}")
                        except:
                            pass
                    
                    self.test_results.append({
                        "test": "Collection Saving with Correct Enums",
                        "status": "FAIL",
                        "details": f"Status {response.status}: {response_text}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Collection saving error: {str(e)}")
            self.test_results.append({
                "test": "Collection Saving with Correct Enums",
                "status": "ERROR",
                "details": str(e)
            })
            return False
            
    async def test_collection_retrieval(self):
        """Test collection retrieval"""
        print("\n📋 Testing Collection Retrieval...")
        
        try:
            async with self.session.get(
                f"{API_BASE}/my-collection",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Collection retrieval successful")
                    print(f"   Found {len(data)} collection items")
                    
                    # Verify our test item appears
                    test_item_found = False
                    for item in data:
                        if item.get('master_kit_id') == self.test_master_kit_id:
                            test_item_found = True
                            print(f"   ✅ Test collection item found:")
                            print(f"      ID: {item.get('id')}")
                            print(f"      Collection type: {item.get('collection_type')}")
                            print(f"      Condition: {item.get('condition')}")
                            print(f"      Physical state: {item.get('physical_state')}")
                            print(f"      Personal notes: {item.get('personal_notes')}")
                            
                            # Verify Master Kit info is embedded
                            master_kit = item.get('master_kit')
                            if master_kit:
                                print(f"      Master Kit: {master_kit.get('club')} {master_kit.get('season')}")
                            break
                    
                    if test_item_found:
                        self.test_results.append({
                            "test": "Collection Retrieval",
                            "status": "PASS",
                            "details": f"Successfully retrieved {len(data)} items, test item found"
                        })
                        return True
                    else:
                        print(f"❌ Test collection item not found in retrieval")
                        self.test_results.append({
                            "test": "Collection Retrieval",
                            "status": "FAIL",
                            "details": "Test item not found in collection"
                        })
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Collection retrieval failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Collection Retrieval",
                        "status": "FAIL",
                        "details": f"Status {response.status}: {error_text}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Collection retrieval error: {str(e)}")
            self.test_results.append({
                "test": "Collection Retrieval",
                "status": "ERROR",
                "details": str(e)
            })
            return False
            
    async def test_want_list_functionality(self):
        """Test Want List functionality"""
        print("\n💝 Testing Want List Functionality...")
        
        # Test data for want list with CORRECT enum values
        want_data = {
            "master_kit_id": self.test_master_kit_id,
            "collection_type": "wanted",
            "condition": "match_prepared",  # Different KitCondition enum value
            "physical_state": "very_good_condition",  # Different PhysicalState enum value
            "size": "M",
            "max_price": 150.00,
            "personal_notes": "Want list item with correct enum values"
        }
        
        print(f"   Testing want list with condition: '{want_data['condition']}'")
        print(f"   Testing want list with physical_state: '{want_data['physical_state']}'")
        
        try:
            async with self.session.post(
                f"{API_BASE}/my-collection",
                json=want_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Want list addition successful")
                    print(f"   Collection ID: {data.get('id')}")
                    print(f"   Collection type: {data.get('collection_type')}")
                    print(f"   Condition: {data.get('condition')}")
                    print(f"   Physical state: {data.get('physical_state')}")
                    
                    self.test_results.append({
                        "test": "Want List Functionality",
                        "status": "PASS",
                        "details": f"Successfully added to want list with correct enums"
                    })
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Want list addition failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Want List Functionality",
                        "status": "FAIL",
                        "details": f"Status {response.status}: {error_text}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Want list error: {str(e)}")
            self.test_results.append({
                "test": "Want List Functionality",
                "status": "ERROR",
                "details": str(e)
            })
            return False
            
    async def test_collection_type_filtering(self):
        """Test collection type filtering"""
        print("\n🔍 Testing Collection Type Filtering...")
        
        # Test owned collection filtering
        print("   Testing owned collection filtering...")
        try:
            async with self.session.get(
                f"{API_BASE}/my-collection?collection_type=owned",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    owned_data = await response.json()
                    owned_count = len(owned_data)
                    print(f"   ✅ Owned collection: {owned_count} items")
                    
                    # Verify all items are owned type
                    all_owned = all(item.get('collection_type') == 'owned' for item in owned_data)
                    if all_owned:
                        print(f"   ✅ All items correctly filtered as 'owned'")
                    else:
                        print(f"   ❌ Some items have incorrect collection_type")
                        
                else:
                    print(f"   ❌ Owned filtering failed: {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Owned filtering error: {str(e)}")
            return False
            
        # Test wanted collection filtering
        print("   Testing wanted collection filtering...")
        try:
            async with self.session.get(
                f"{API_BASE}/my-collection?collection_type=wanted",
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 200:
                    wanted_data = await response.json()
                    wanted_count = len(wanted_data)
                    print(f"   ✅ Wanted collection: {wanted_count} items")
                    
                    # Verify all items are wanted type
                    all_wanted = all(item.get('collection_type') == 'wanted' for item in wanted_data)
                    if all_wanted:
                        print(f"   ✅ All items correctly filtered as 'wanted'")
                    else:
                        print(f"   ❌ Some items have incorrect collection_type")
                        
                    self.test_results.append({
                        "test": "Collection Type Filtering",
                        "status": "PASS",
                        "details": f"Owned: {owned_count}, Wanted: {wanted_count} - filtering works correctly"
                    })
                    return True
                else:
                    print(f"   ❌ Wanted filtering failed: {response.status}")
                    self.test_results.append({
                        "test": "Collection Type Filtering",
                        "status": "FAIL",
                        "details": f"Wanted filtering failed with status {response.status}"
                    })
                    return False
        except Exception as e:
            print(f"   ❌ Wanted filtering error: {str(e)}")
            self.test_results.append({
                "test": "Collection Type Filtering",
                "status": "ERROR",
                "details": str(e)
            })
            return False
            
    async def test_enum_validation(self):
        """Test enum validation with invalid values"""
        print("\n⚠️  Testing Enum Validation with Invalid Values...")
        
        # Test with invalid condition enum
        invalid_condition_data = {
            "master_kit_id": self.test_master_kit_id,
            "collection_type": "owned",
            "condition": "invalid_condition",  # Invalid enum value
            "physical_state": "new_with_tags",
            "size": "L"
        }
        
        print("   Testing invalid condition enum...")
        try:
            async with self.session.post(
                f"{API_BASE}/my-collection",
                json=invalid_condition_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 422:
                    print(f"   ✅ Invalid condition properly rejected with 422")
                    error_text = await response.text()
                    print(f"   Error details: {error_text}")
                else:
                    print(f"   ❌ Invalid condition not properly rejected: {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ Invalid condition test error: {str(e)}")
            return False
            
        # Test with invalid physical_state enum
        invalid_physical_state_data = {
            "master_kit_id": self.test_master_kit_id,
            "collection_type": "owned",
            "condition": "club_stock",
            "physical_state": "invalid_physical_state",  # Invalid enum value
            "size": "L"
        }
        
        print("   Testing invalid physical_state enum...")
        try:
            async with self.session.post(
                f"{API_BASE}/my-collection",
                json=invalid_physical_state_data,
                headers=self.get_auth_headers()
            ) as response:
                if response.status == 422:
                    print(f"   ✅ Invalid physical_state properly rejected with 422")
                    error_text = await response.text()
                    print(f"   Error details: {error_text}")
                    
                    self.test_results.append({
                        "test": "Enum Validation",
                        "status": "PASS",
                        "details": "Invalid enum values properly rejected with 422 errors"
                    })
                    return True
                else:
                    print(f"   ❌ Invalid physical_state not properly rejected: {response.status}")
                    self.test_results.append({
                        "test": "Enum Validation",
                        "status": "FAIL",
                        "details": f"Invalid enum not rejected, got status {response.status}"
                    })
                    return False
        except Exception as e:
            print(f"   ❌ Invalid physical_state test error: {str(e)}")
            self.test_results.append({
                "test": "Enum Validation",
                "status": "ERROR",
                "details": str(e)
            })
            return False
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 COLLECTION SAVING BUG FIX TEST SUMMARY")
        print("="*80)
        
        passed_tests = [t for t in self.test_results if t['status'] == 'PASS']
        failed_tests = [t for t in self.test_results if t['status'] == 'FAIL']
        error_tests = [t for t in self.test_results if t['status'] == 'ERROR']
        
        total_tests = len(self.test_results)
        success_rate = (len(passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {len(passed_tests)}")
        print(f"   Failed: {len(failed_tests)}")
        print(f"   Errors: {len(error_tests)}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test['test']}: {test['details']}")
            
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
                
        if error_tests:
            print(f"\n🚨 ERROR TESTS:")
            for test in error_tests:
                print(f"   • {test['test']}: {test['details']}")
                
        print(f"\n🎯 CRITICAL BUG FIX VERIFICATION:")
        collection_saving_test = next((t for t in self.test_results if t['test'] == 'Collection Saving with Correct Enums'), None)
        if collection_saving_test and collection_saving_test['status'] == 'PASS':
            print(f"   ✅ COLLECTION SAVING BUG FIX CONFIRMED WORKING!")
            print(f"   ✅ No more 422 errors with correct enum values")
            print(f"   ✅ condition='club_stock' (KitCondition) accepted")
            print(f"   ✅ physical_state='new_with_tags' (PhysicalState) accepted")
        else:
            print(f"   ❌ COLLECTION SAVING BUG FIX NOT WORKING!")
            print(f"   ❌ Still getting errors with correct enum values")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all collection enum tests"""
        print("🚀 Starting Collection Saving Bug Fix Testing...")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        
        await self.setup_session()
        
        try:
            # Step 1: Authenticate
            if not await self.authenticate_admin():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Step 2: Create test Master Kit
            if not await self.create_test_master_kit():
                print("❌ Master Kit creation failed - cannot proceed with collection tests")
                return
                
            # Step 3: Test collection saving with correct enums (CRITICAL TEST)
            await self.test_collection_saving_with_correct_enums()
            
            # Step 4: Test collection retrieval
            await self.test_collection_retrieval()
            
            # Step 5: Test want list functionality
            await self.test_want_list_functionality()
            
            # Step 6: Test collection type filtering
            await self.test_collection_type_filtering()
            
            # Step 7: Test enum validation
            await self.test_enum_validation()
            
            # Print comprehensive summary
            self.print_test_summary()
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    test_suite = CollectionEnumTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())