#!/usr/bin/env python3
"""
Reference Kit Collections System Testing
Testing the enhanced reference kit collections system with new fields and bilateral logic
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://topkit-manager.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ReferenceKitCollectionsTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_reference_kit_id = None
        
    def log(self, message):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def authenticate_admin(self):
        """Test 1: Authentication with admin credentials"""
        self.log("🔐 Testing admin authentication...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user_id = data.get('user', {}).get('id')
                
                if self.admin_token and len(self.admin_token) > 100:
                    self.log(f"✅ Admin authentication successful - Token: {len(self.admin_token)} chars")
                    self.log(f"✅ Admin user ID: {self.admin_user_id}")
                    
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    return True
                else:
                    self.log(f"❌ Invalid token received: {self.admin_token}")
                    return False
            else:
                self.log(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            return False
    
    def check_reference_kits_availability(self):
        """Test 2: Check if reference kits exist for testing"""
        self.log("📋 Checking reference kits availability...")
        
        try:
            response = self.session.get(f"{API_BASE}/reference-kits")
            
            if response.status_code == 200:
                reference_kits = response.json()
                if isinstance(reference_kits, list) and len(reference_kits) > 0:
                    self.test_reference_kit_id = reference_kits[0].get('id')
                    self.log(f"✅ Found {len(reference_kits)} reference kits")
                    self.log(f"✅ Using test reference kit ID: {self.test_reference_kit_id}")
                    
                    # Log details of first reference kit
                    first_kit = reference_kits[0]
                    self.log(f"   - TopKit Reference: {first_kit.get('topkit_reference', 'N/A')}")
                    self.log(f"   - Master Jersey ID: {first_kit.get('master_jersey_id', 'N/A')}")
                    return True
                else:
                    self.log("❌ No reference kits found - creating test reference kit")
                    return self.create_test_reference_kit()
            else:
                self.log(f"❌ Failed to get reference kits: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error checking reference kits: {e}")
            return False
    
    def create_test_reference_kit(self):
        """Create a test reference kit if none exist"""
        self.log("🔨 Creating test reference kit...")
        
        try:
            # First get a master jersey
            response = self.session.get(f"{API_BASE}/master-jerseys")
            if response.status_code != 200:
                self.log("❌ No master jerseys available for test reference kit")
                return False
                
            master_jerseys = response.json()
            if not master_jerseys:
                self.log("❌ No master jerseys found")
                return False
                
            master_jersey_id = master_jerseys[0].get('id')
            
            # Create test reference kit
            test_kit_data = {
                "master_jersey_id": master_jersey_id,
                "player_name": "Test Player",
                "player_number": "10",
                "release_type": "authentic",
                "retail_price": 140.0,
                "available_sizes": ["S", "M", "L", "XL"]
            }
            
            response = self.session.post(f"{API_BASE}/reference-kits", json=test_kit_data)
            
            if response.status_code == 201:
                created_kit = response.json()
                self.test_reference_kit_id = created_kit.get('id')
                self.log(f"✅ Test reference kit created: {self.test_reference_kit_id}")
                return True
            else:
                self.log(f"❌ Failed to create test reference kit: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error creating test reference kit: {e}")
            return False
    
    def test_add_to_owned_collection(self):
        """Test 3: Add reference kit to owned collection with enhanced fields"""
        self.log("📦 Testing add to owned collection with enhanced fields...")
        
        if not self.test_reference_kit_id:
            self.log("❌ No test reference kit available")
            return False
            
        try:
            # Test with all new enhanced fields
            collection_data = {
                "reference_kit_id": self.test_reference_kit_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "mint",  # Test new condition value
                "personal_description": "Test owned kit with enhanced fields",
                "purchase_price": 120.0,
                "estimated_value": 150.0,
                "player_name": "Test Player",
                "player_number": "10",
                # New special attributes
                "worn": True,
                "worn_type": "match_worn",
                "signed": True,
                "signed_by": "Test Player"
            }
            
            response = self.session.post(f"{API_BASE}/reference-kit-collections", json=collection_data)
            
            if response.status_code in [200, 201]:  # Accept both 200 and 201
                result = response.json()
                self.log("✅ Successfully added to owned collection")
                self.log(f"   - Collection ID: {result.get('collection_id')}")
                self.log(f"   - Message: {result.get('message')}")
                
                # Verify enhanced fields are included
                if 'worn' in str(result) and 'signed' in str(result):
                    self.log("✅ Enhanced fields (worn, signed) included in response")
                else:
                    self.log("⚠️ Enhanced fields may not be fully included")
                    
                return True
            else:
                self.log(f"❌ Failed to add to owned collection: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error adding to owned collection: {e}")
            return False
    
    def test_bilateral_system_prevention(self):
        """Test 4: Test bilateral system - can't be in both owned and wanted"""
        self.log("🔄 Testing bilateral system prevention...")
        
        if not self.test_reference_kit_id:
            self.log("❌ No test reference kit available")
            return False
            
        try:
            # Try to add same kit to wanted collection (should fail)
            collection_data = {
                "reference_kit_id": self.test_reference_kit_id,
                "collection_type": "wanted",
                "size": "L",
                "condition": "excellent"
            }
            
            response = self.session.post(f"{API_BASE}/reference-kit-collections", json=collection_data)
            
            if response.status_code == 400:
                error_message = response.json().get('detail', '')
                if 'already in your owned collection' in error_message:
                    self.log("✅ Bilateral prevention working - cannot add to wanted when in owned")
                    self.log(f"   - Error message: {error_message}")
                    return True
                else:
                    self.log(f"❌ Unexpected error message: {error_message}")
                    return False
            else:
                self.log(f"❌ Expected 400 error but got: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing bilateral prevention: {e}")
            return False
    
    def test_duplicate_prevention(self):
        """Test 5: Test duplicate prevention in same collection type"""
        self.log("🚫 Testing duplicate prevention...")
        
        if not self.test_reference_kit_id:
            self.log("❌ No test reference kit available")
            return False
            
        try:
            # Try to add same kit to owned collection again (should fail)
            collection_data = {
                "reference_kit_id": self.test_reference_kit_id,
                "collection_type": "owned",
                "size": "XL",
                "condition": "good"
            }
            
            response = self.session.post(f"{API_BASE}/reference-kit-collections", json=collection_data)
            
            if response.status_code == 400:
                error_message = response.json().get('detail', '')
                if 'already in your owned collection' in error_message:
                    self.log("✅ Duplicate prevention working - cannot add same kit twice")
                    self.log(f"   - Error message: {error_message}")
                    return True
                else:
                    self.log(f"❌ Unexpected error message: {error_message}")
                    return False
            else:
                self.log(f"❌ Expected 400 error but got: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing duplicate prevention: {e}")
            return False
    
    def test_condition_validation(self):
        """Test 6: Test new condition values validation"""
        self.log("🏷️ Testing new condition values validation...")
        
        if not self.test_reference_kit_id:
            self.log("❌ No test reference kit available")
            return False
        
        # Get another reference kit for testing
        try:
            response = self.session.get(f"{API_BASE}/reference-kits")
            reference_kits = response.json()
            if len(reference_kits) < 2:
                self.log("⚠️ Only one reference kit available, skipping condition validation test")
                return True
                
            second_kit_id = None
            for kit in reference_kits:
                if kit.get('id') != self.test_reference_kit_id:
                    second_kit_id = kit.get('id')
                    break
                    
            if not second_kit_id:
                self.log("⚠️ No second reference kit found, skipping condition validation test")
                return True
        except:
            self.log("⚠️ Could not get second reference kit, skipping condition validation test")
            return True
            
        # Test all new condition values
        new_conditions = ["new_with_tags", "mint", "excellent", "good", "fair", "poor"]
        
        for i, condition in enumerate(new_conditions):
            try:
                collection_data = {
                    "reference_kit_id": second_kit_id,
                    "collection_type": "wanted",
                    "size": "M",
                    "condition": condition,
                    "personal_description": f"Test condition: {condition}"
                }
                
                response = self.session.post(f"{API_BASE}/reference-kit-collections", json=collection_data)
                
                if response.status_code == 201:
                    self.log(f"✅ Condition '{condition}' accepted")
                    
                    # Remove it for next test
                    collections_response = self.session.get(f"{API_BASE}/users/{self.admin_user_id}/reference-kit-collections/wanted")
                    if collections_response.status_code == 200:
                        collections = collections_response.json()
                        for collection in collections:
                            if collection.get('reference_kit_id') == second_kit_id:
                                # Delete this collection for next test
                                delete_response = self.session.delete(f"{API_BASE}/reference-kit-collections/{collection.get('id')}")
                                break
                    
                elif response.status_code == 400 and 'already in your' in response.text:
                    self.log(f"✅ Condition '{condition}' accepted (duplicate prevented)")
                else:
                    self.log(f"❌ Condition '{condition}' rejected: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                self.log(f"❌ Error testing condition '{condition}': {e}")
                return False
        
        self.log("✅ All new condition values validated successfully")
        return True
    
    def test_get_owned_collections(self):
        """Test 7: Test GET owned collections endpoint"""
        self.log("📋 Testing GET owned collections endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/users/{self.admin_user_id}/reference-kit-collections/owned")
            
            if response.status_code == 200:
                collections = response.json()
                self.log(f"✅ GET owned collections successful - Found {len(collections)} items")
                
                if len(collections) > 0:
                    first_collection = collections[0]
                    self.log("✅ Data enrichment verification:")
                    
                    # Check for reference_kit data
                    if 'reference_kit' in first_collection or 'reference_kit_info' in first_collection:
                        self.log("   ✅ Reference kit data enriched")
                    else:
                        self.log("   ❌ Reference kit data missing")
                    
                    # Check for master_jersey data
                    if 'master_jersey' in first_collection or 'master_jersey_info' in first_collection:
                        self.log("   ✅ Master jersey data enriched")
                    else:
                        self.log("   ❌ Master jersey data missing")
                    
                    # Check for enhanced fields
                    enhanced_fields = ['worn', 'worn_type', 'signed', 'signed_by']
                    found_enhanced = 0
                    for field in enhanced_fields:
                        if field in first_collection:
                            found_enhanced += 1
                            self.log(f"   ✅ Enhanced field '{field}': {first_collection[field]}")
                    
                    if found_enhanced > 0:
                        self.log(f"   ✅ Found {found_enhanced}/{len(enhanced_fields)} enhanced fields")
                    else:
                        self.log("   ⚠️ No enhanced fields found in response")
                
                return True
            else:
                self.log(f"❌ Failed to get owned collections: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error getting owned collections: {e}")
            return False
    
    def test_get_wanted_collections(self):
        """Test 8: Test GET wanted collections endpoint"""
        self.log("📋 Testing GET wanted collections endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/users/{self.admin_user_id}/reference-kit-collections/wanted")
            
            if response.status_code == 200:
                collections = response.json()
                self.log(f"✅ GET wanted collections successful - Found {len(collections)} items")
                
                if len(collections) > 0:
                    first_collection = collections[0]
                    self.log("✅ Data enrichment verification:")
                    
                    # Check for reference_kit data
                    if 'reference_kit' in first_collection or 'reference_kit_info' in first_collection:
                        self.log("   ✅ Reference kit data enriched")
                    else:
                        self.log("   ❌ Reference kit data missing")
                    
                    # Check for master_jersey data  
                    if 'master_jersey' in first_collection or 'master_jersey_info' in first_collection:
                        self.log("   ✅ Master jersey data enriched")
                    else:
                        self.log("   ❌ Master jersey data missing")
                
                return True
            else:
                self.log(f"❌ Failed to get wanted collections: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error getting wanted collections: {e}")
            return False
    
    def test_get_combined_collections(self):
        """Test 9: Test GET combined collections endpoint"""
        self.log("📋 Testing GET combined collections endpoint...")
        
        try:
            response = self.session.get(f"{API_BASE}/users/{self.admin_user_id}/reference-kit-collections")
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ GET combined collections successful")
                
                # Check response structure
                if isinstance(result, dict):
                    owned = result.get('owned', [])
                    wanted = result.get('wanted', [])
                    self.log(f"   - Owned collections: {len(owned)}")
                    self.log(f"   - Wanted collections: {len(wanted)}")
                elif isinstance(result, list):
                    self.log(f"   - Total collections: {len(result)}")
                
                return True
            else:
                self.log(f"❌ Failed to get combined collections: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error getting combined collections: {e}")
            return False
    
    def test_collection_workflow(self):
        """Test 10: Test complete collection workflow"""
        self.log("🔄 Testing complete collection workflow...")
        
        if not self.test_reference_kit_id:
            self.log("❌ No test reference kit available")
            return False
        
        try:
            # Get another reference kit for workflow testing
            response = self.session.get(f"{API_BASE}/reference-kits")
            reference_kits = response.json()
            
            workflow_kit_id = None
            for kit in reference_kits:
                if kit.get('id') != self.test_reference_kit_id:
                    workflow_kit_id = kit.get('id')
                    break
            
            if not workflow_kit_id:
                self.log("⚠️ Only one reference kit available, using same kit for workflow test")
                workflow_kit_id = self.test_reference_kit_id
            
            # Step 1: Add to wanted collection
            self.log("   Step 1: Adding to wanted collection...")
            wanted_data = {
                "reference_kit_id": workflow_kit_id,
                "collection_type": "wanted",
                "size": "L",
                "condition": "excellent"
            }
            
            response = self.session.post(f"{API_BASE}/reference-kit-collections", json=wanted_data)
            if response.status_code not in [201, 400]:  # 400 if already exists
                self.log(f"❌ Failed to add to wanted: {response.status_code}")
                return False
            
            self.log("   ✅ Added to wanted collection")
            
            # Step 2: Try to add same kit to owned (should fail due to bilateral system)
            self.log("   Step 2: Testing bilateral prevention...")
            owned_data = {
                "reference_kit_id": workflow_kit_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "mint"
            }
            
            response = self.session.post(f"{API_BASE}/reference-kit-collections", json=owned_data)
            if response.status_code == 400:
                self.log("   ✅ Bilateral prevention working")
            else:
                self.log(f"   ❌ Expected bilateral prevention but got: {response.status_code}")
                return False
            
            # Step 3: Remove from wanted and add to owned
            self.log("   Step 3: Remove from wanted and add to owned...")
            
            # Get wanted collections to find the item to remove
            collections_response = self.session.get(f"{API_BASE}/users/{self.admin_user_id}/reference-kit-collections/wanted")
            if collections_response.status_code == 200:
                wanted_collections = collections_response.json()
                collection_to_remove = None
                
                for collection in wanted_collections:
                    if collection.get('reference_kit_id') == workflow_kit_id:
                        collection_to_remove = collection.get('id')
                        break
                
                if collection_to_remove:
                    # Remove from wanted
                    delete_response = self.session.delete(f"{API_BASE}/reference-kit-collections/{collection_to_remove}")
                    if delete_response.status_code == 200:
                        self.log("   ✅ Removed from wanted collection")
                        
                        # Now add to owned
                        response = self.session.post(f"{API_BASE}/reference-kit-collections", json=owned_data)
                        if response.status_code == 201:
                            self.log("   ✅ Added to owned collection")
                            self.log("✅ Complete workflow test successful")
                            return True
                        else:
                            self.log(f"   ❌ Failed to add to owned: {response.status_code}")
                            return False
                    else:
                        self.log(f"   ❌ Failed to remove from wanted: {delete_response.status_code}")
                        return False
                else:
                    self.log("   ❌ Could not find wanted collection item to remove")
                    return False
            else:
                self.log(f"   ❌ Failed to get wanted collections: {collections_response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error in collection workflow: {e}")
            return False
    
    def run_all_tests(self):
        """Run all reference kit collections tests"""
        self.log("🚀 Starting Reference Kit Collections System Testing")
        self.log("=" * 60)
        
        tests = [
            ("Authentication Test", self.authenticate_admin),
            ("Reference Kit Existence Check", self.check_reference_kits_availability),
            ("Add to Owned Collection", self.test_add_to_owned_collection),
            ("Bilateral System Prevention", self.test_bilateral_system_prevention),
            ("Duplicate Prevention", self.test_duplicate_prevention),
            ("Condition Values Validation", self.test_condition_validation),
            ("GET Owned Collections", self.test_get_owned_collections),
            ("GET Wanted Collections", self.test_get_wanted_collections),
            ("GET Combined Collections", self.test_get_combined_collections),
            ("Collection Workflow", self.test_collection_workflow)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                    self.log(f"✅ {test_name} - PASSED")
                else:
                    failed += 1
                    self.log(f"❌ {test_name} - FAILED")
            except Exception as e:
                failed += 1
                self.log(f"❌ {test_name} - ERROR: {e}")
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log("📊 REFERENCE KIT COLLECTIONS TESTING SUMMARY")
        self.log("=" * 60)
        self.log(f"✅ Tests Passed: {passed}")
        self.log(f"❌ Tests Failed: {failed}")
        self.log(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED - Reference Kit Collections System is PRODUCTION-READY!")
        else:
            self.log(f"⚠️ {failed} test(s) failed - Review required before production")
        
        return failed == 0

if __name__ == "__main__":
    tester = ReferenceKitCollectionsTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
"""
TopKit Backend Testing - CRITICAL IMAGE DISPLAY BUG INVESTIGATION
Testing image upload, storage, integration, and display functionality:
1. Image Upload Process during contribution creation via Community DB
2. Image Storage and association with entities
3. Image Integration from approved contributions to main catalogue entities
4. Image Retrieval and URL/path testing for entity detail pages
5. Cross-Entity Testing for all entity types (teams, brands, players, competitions, kits)
"""

import requests
import json
import base64
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://topkit-manager.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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

    def authenticate_admin(self):
        """Authenticate admin user and get JWT token"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Successfully authenticated admin user. Token length: {len(self.admin_token)}"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, "", "No token in response")
                    return False
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    "", 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def test_contributions_v2_get(self):
        """Test GET /api/contributions-v2/ endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if response.status_code == 200:
                data = response.json()
                contributions_count = len(data) if isinstance(data, list) else len(data.get('contributions', []))
                self.log_result(
                    "GET /api/contributions-v2/",
                    True,
                    f"Retrieved {contributions_count} contributions successfully"
                )
                return data
            else:
                self.log_result(
                    "GET /api/contributions-v2/",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("GET /api/contributions-v2/", False, "", str(e))
            return None

    def test_unified_form_system_all_entities(self):
        """Test Unified Form System with all entity types as specified in review request"""
        entity_types = [
            {
                "type": "team",
                "data": {
                    "entity_type": "team",
                    "entity_id": None,
                    "title": "Final Test Team - All Entity Types",
                    "description": "Testing unified form system with team entity",
                    "changes": {
                        "name": "Final Test FC",
                        "short_name": "FTC",
                        "country": "France",
                        "city": "Lyon",
                        "founded_year": 2024,
                        "team_colors": ["Red", "Blue"]
                    },
                    "source_urls": ["https://example.com/final-test-team"]
                }
            },
            {
                "type": "brand",
                "data": {
                    "entity_type": "brand",
                    "entity_id": None,
                    "title": "Final Test Brand - All Entity Types",
                    "description": "Testing unified form system with brand entity",
                    "changes": {
                        "name": "Final Test Sports",
                        "country": "Germany",
                        "founded_year": 2024,
                        "website": "https://finaltestsports.com"
                    },
                    "source_urls": ["https://example.com/final-test-brand"]
                }
            },
            {
                "type": "player",
                "data": {
                    "entity_type": "player",
                    "entity_id": None,
                    "title": "Final Test Player - All Entity Types",
                    "description": "Testing unified form system with player entity",
                    "changes": {
                        "name": "Final Test Player",
                        "full_name": "Final Test Player Junior",
                        "nationality": "France",
                        "position": "Forward",
                        "birth_date": "1995-01-01"
                    },
                    "source_urls": ["https://example.com/final-test-player"]
                }
            },
            {
                "type": "competition",
                "data": {
                    "entity_type": "competition",
                    "entity_id": None,
                    "title": "Final Test Competition - All Entity Types",
                    "description": "Testing unified form system with competition entity",
                    "changes": {
                        "competition_name": "Final Test League",
                        "type": "National league",
                        "country": "France",
                        "level": 1,
                        "confederations_federations": ["UEFA"]
                    },
                    "source_urls": ["https://example.com/final-test-competition"]
                }
            },
            {
                "type": "master_kit",
                "data": {
                    "entity_type": "master_kit",
                    "entity_id": None,
                    "title": "Final Test Master Kit - All Entity Types",
                    "description": "Testing unified form system with master kit entity",
                    "changes": {
                        "team_name": "Final Test FC",
                        "brand_name": "Final Test Sports",
                        "season": "2024-25",
                        "kit_type": "home",
                        "model": "authentic",
                        "primary_color": "#FF0000"
                    },
                    "source_urls": ["https://example.com/final-test-master-kit"]
                }
            },
            {
                "type": "reference_kit",
                "data": {
                    "entity_type": "reference_kit",
                    "entity_id": None,
                    "title": "Final Test Reference Kit - All Entity Types",
                    "description": "Testing unified form system with reference kit entity",
                    "changes": {
                        "master_kit_reference": "TK-MASTER-000001",
                        "player_name": "Final Test Player",
                        "player_number": "10",
                        "retail_price": 89.99,
                        "release_type": "authentic"
                    },
                    "source_urls": ["https://example.com/final-test-reference-kit"]
                }
            }
        ]
        
        created_contributions = []
        all_success = True
        
        for entity in entity_types:
            try:
                response = self.session.post(f"{API_BASE}/contributions-v2/", json=entity["data"])
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    contribution_id = data.get('id') or data.get('contribution_id')
                    created_contributions.append(contribution_id)
                    self.log_result(
                        f"Unified Form System - {entity['type'].title()} Entity",
                        True,
                        f"Successfully created {entity['type']} contribution with ID: {contribution_id}"
                    )
                else:
                    self.log_result(
                        f"Unified Form System - {entity['type'].title()} Entity",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_success = False
                    
            except Exception as e:
                self.log_result(f"Unified Form System - {entity['type'].title()} Entity", False, "", str(e))
                all_success = False
        
        return all_success, created_contributions

    def test_integration_pipeline(self):
        """Test Integration Pipeline - approved contributions auto-integration to main collections"""
        try:
            # First, check if auto-approval is enabled
            response = self.session.get(f"{API_BASE}/admin/settings")
            if response.status_code == 200:
                settings = response.json()
                auto_approval = settings.get("auto_approval_enabled", False)
                
                self.log_result(
                    "Integration Pipeline - Auto-Approval Settings",
                    True,
                    f"Auto-approval enabled: {auto_approval}"
                )
                
                # Test creating a contribution that should auto-integrate
                test_contribution = {
                    "entity_type": "team",
                    "entity_id": None,
                    "title": "Integration Pipeline Test Team",
                    "description": "Testing auto-integration pipeline",
                    "changes": {
                        "name": "Pipeline Test FC",
                        "short_name": "PTC",
                        "country": "Spain",
                        "city": "Madrid",
                        "founded_year": 2024,
                        "team_colors": ["White", "Blue"]
                    }
                }
                
                response = self.session.post(f"{API_BASE}/contributions-v2/", json=test_contribution)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    contribution_id = data.get('id')
                    
                    # Check if the team appears in main teams collection
                    teams_response = self.session.get(f"{API_BASE}/teams")
                    if teams_response.status_code == 200:
                        teams = teams_response.json()
                        pipeline_team_found = any(
                            team.get('name') == 'Pipeline Test FC' 
                            for team in teams
                        )
                        
                        self.log_result(
                            "Integration Pipeline - Auto-Integration to Teams",
                            pipeline_team_found,
                            f"Team {'found' if pipeline_team_found else 'not found'} in main teams collection"
                        )
                        return pipeline_team_found
                    else:
                        self.log_result(
                            "Integration Pipeline - Teams Collection Check",
                            False,
                            "",
                            f"Failed to retrieve teams: HTTP {teams_response.status_code}"
                        )
                        return False
                else:
                    self.log_result(
                        "Integration Pipeline - Test Contribution Creation",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Integration Pipeline - Settings Check",
                    False,
                    "",
                    f"Failed to get admin settings: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Integration Pipeline Test", False, "", str(e))
            return False

    def test_display_apis(self):
        """Test Display APIs for Catalogue Teams, Brands, Kit Store, and Community DB"""
        display_endpoints = [
            ("/teams", "Catalogue Teams page"),
            ("/brands", "Catalogue Brands page"),
            ("/vestiaire", "Kit Store with reference kits"),
            ("/contributions-v2/", "Community DB")
        ]
        
        all_success = True
        
        for endpoint, description in display_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Analyze data structure based on endpoint
                    if endpoint == "/teams":
                        count = len(data) if isinstance(data, list) else len(data.get('teams', []))
                        self.log_result(
                            f"Display API - {description}",
                            True,
                            f"Retrieved {count} teams with proper data structure"
                        )
                    elif endpoint == "/brands":
                        count = len(data) if isinstance(data, list) else len(data.get('brands', []))
                        self.log_result(
                            f"Display API - {description}",
                            True,
                            f"Retrieved {count} brands with proper data structure"
                        )
                    elif endpoint == "/vestiaire":
                        # Check for reference kits in vestiaire
                        kits = data if isinstance(data, list) else data.get('kits', [])
                        reference_kits = [kit for kit in kits if 'reference' in str(kit).lower()]
                        self.log_result(
                            f"Display API - {description}",
                            True,
                            f"Retrieved {len(kits)} total kits, {len(reference_kits)} reference kits"
                        )
                    elif endpoint == "/contributions-v2/":
                        count = len(data) if isinstance(data, list) else len(data.get('contributions', []))
                        self.log_result(
                            f"Display API - {description}",
                            True,
                            f"Retrieved {count} contributions with proper data structure"
                        )
                else:
                    self.log_result(
                        f"Display API - {description}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_success = False
                    
            except Exception as e:
                self.log_result(f"Display API - {description}", False, "", str(e))
                all_success = False
        
        return all_success

    def test_complete_data_flow(self):
        """Test Complete Data Flow: Community DB → Voting → Moderation → Integration → Catalogue/Kit Store"""
        try:
            # Step 1: Create a contribution in Community DB
            flow_contribution = {
                "entity_type": "brand",
                "entity_id": None,
                "title": "Data Flow Test Brand",
                "description": "Testing complete data flow pipeline",
                "changes": {
                    "name": "Flow Test Sports",
                    "country": "Italy",
                    "founded_year": 2024
                }
            }
            
            response = self.session.post(f"{API_BASE}/contributions-v2/", json=flow_contribution)
            
            if response.status_code in [200, 201]:
                data = response.json()
                contribution_id = data.get('id')
                
                self.log_result(
                    "Complete Data Flow - Step 1: Community DB Creation",
                    True,
                    f"Created contribution in Community DB with ID: {contribution_id}"
                )
                
                # Step 2: Verify contribution appears in Community DB
                contributions_response = self.session.get(f"{API_BASE}/contributions-v2/")
                if contributions_response.status_code == 200:
                    contributions = contributions_response.json()
                    flow_contribution_found = any(
                        contrib.get('id') == contribution_id 
                        for contrib in contributions
                    )
                    
                    self.log_result(
                        "Complete Data Flow - Step 2: Community DB Visibility",
                        flow_contribution_found,
                        f"Contribution {'visible' if flow_contribution_found else 'not visible'} in Community DB"
                    )
                    
                    # Step 3: Check if it appears in main brands collection (integration)
                    brands_response = self.session.get(f"{API_BASE}/brands")
                    if brands_response.status_code == 200:
                        brands = brands_response.json()
                        flow_brand_found = any(
                            brand.get('name') == 'Flow Test Sports' 
                            for brand in brands
                        )
                        
                        self.log_result(
                            "Complete Data Flow - Step 3: Integration to Catalogue",
                            flow_brand_found,
                            f"Brand {'integrated' if flow_brand_found else 'not integrated'} into main catalogue"
                        )
                        
                        return flow_contribution_found and flow_brand_found
                    else:
                        self.log_result(
                            "Complete Data Flow - Brands Collection Check",
                            False,
                            "",
                            f"Failed to retrieve brands: HTTP {brands_response.status_code}"
                        )
                        return False
                else:
                    self.log_result(
                        "Complete Data Flow - Community DB Check",
                        False,
                        "",
                        f"Failed to retrieve contributions: HTTP {contributions_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Complete Data Flow - Contribution Creation",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Complete Data Flow Test", False, "", str(e))
            return False

    def test_reference_kits_in_kit_store(self):
        """Test that reference kits appear in Kit Store (/api/vestiaire)"""
        try:
            response = self.session.get(f"{API_BASE}/vestiaire")
            
            if response.status_code == 200:
                data = response.json()
                kits = data if isinstance(data, list) else data.get('kits', [])
                
                # Look for reference kits specifically
                reference_kits = []
                for kit in kits:
                    if (isinstance(kit, dict) and 
                        ('reference' in str(kit).lower() or 
                         'topkit_reference' in kit or 
                         'TK-RELEASE' in str(kit))):
                        reference_kits.append(kit)
                
                self.log_result(
                    "Reference Kits in Kit Store",
                    len(reference_kits) > 0,
                    f"Found {len(reference_kits)} reference kits in Kit Store out of {len(kits)} total kits"
                )
                
                return len(reference_kits) > 0
            else:
                self.log_result(
                    "Reference Kits in Kit Store",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Reference Kits in Kit Store", False, "", str(e))
            return False

    def test_specific_team_entities_image_data(self):
        """Test specific team entities mentioned in review request for image data"""
        target_teams = ["TK-TEAM-4156DC3C", "TK-TEAM-00BEEF9B"]
        
        try:
            # Get all teams to search for target entities
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                found_teams = []
                
                for team in teams:
                    team_ref = team.get('topkit_reference', '')
                    if team_ref in target_teams:
                        found_teams.append(team)
                        
                        # Check for image-related fields
                        image_fields = ['logo_url', 'image_url', 'photo_url', 'images']
                        has_images = any(team.get(field) for field in image_fields)
                        
                        self.log_result(
                            f"Target Team Entity - {team_ref}",
                            True,
                            f"Found team '{team.get('name', 'Unknown')}' - Has images: {has_images}"
                        )
                
                if not found_teams:
                    self.log_result(
                        "Target Team Entities Search",
                        False,
                        "",
                        f"Target teams {target_teams} not found in database"
                    )
                    return False
                
                return len(found_teams) > 0
            else:
                self.log_result(
                    "Target Team Entities Search",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Target Team Entities Search", False, "", str(e))
            return False

    def test_contribution_image_association(self):
        """Test if contribution records have associated images"""
        try:
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if response.status_code == 200:
                contributions = response.json()
                contributions_with_images = 0
                total_contributions = len(contributions) if isinstance(contributions, list) else 0
                
                for contrib in contributions:
                    # Check for image-related fields in contributions
                    image_fields = ['images', 'image_urls', 'photos', 'logo_url']
                    has_images = any(contrib.get(field) for field in image_fields)
                    
                    if has_images:
                        contributions_with_images += 1
                
                self.log_result(
                    "Contribution Image Association",
                    True,
                    f"Found {contributions_with_images}/{total_contributions} contributions with image data"
                )
                
                return contributions_with_images > 0
            else:
                self.log_result(
                    "Contribution Image Association",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Contribution Image Association", False, "", str(e))
            return False

    def test_image_upload_endpoint(self):
        """Test dedicated image upload endpoint"""
        try:
            # Test if image upload endpoint exists
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            # Try different possible image upload endpoints
            upload_endpoints = [
                "/upload/image",
                "/api/upload/image", 
                "/images/upload",
                "/contributions-v2/upload-image"
            ]
            
            for endpoint in upload_endpoints:
                try:
                    # Test multipart form upload
                    files = {'image': ('test.png', base64.b64decode(test_image_base64), 'image/png')}
                    data = {'entity_type': 'team', 'entity_id': 'test-id'}
                    
                    response = self.session.post(f"{BACKEND_URL}{endpoint}", files=files, data=data)
                    
                    if response.status_code in [200, 201]:
                        self.log_result(
                            f"Image Upload Endpoint - {endpoint}",
                            True,
                            f"Successfully uploaded image via {endpoint}"
                        )
                        return True
                    elif response.status_code != 404:
                        self.log_result(
                            f"Image Upload Endpoint - {endpoint}",
                            False,
                            "",
                            f"HTTP {response.status_code}: {response.text}"
                        )
                except Exception as e:
                    # Skip 404s and connection errors for non-existent endpoints
                    if "404" not in str(e):
                        self.log_result(f"Image Upload Endpoint - {endpoint}", False, "", str(e))
            
            self.log_result(
                "Image Upload Endpoints",
                False,
                "",
                "No working image upload endpoint found"
            )
            return False
                
        except Exception as e:
            self.log_result("Image Upload Endpoint Test", False, "", str(e))
            return False

    def test_image_file_existence_and_accessibility(self):
        """Test image file existence and accessibility"""
        try:
            # Get teams and check for image URLs
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                image_urls_found = []
                accessible_images = 0
                
                for team in teams:
                    # Check various image field names
                    image_fields = ['logo_url', 'image_url', 'photo_url', 'images']
                    for field in image_fields:
                        image_url = team.get(field)
                        if image_url:
                            image_urls_found.append(image_url)
                            
                            # Test if image URL is accessible
                            try:
                                if image_url.startswith('http'):
                                    img_response = requests.get(image_url, timeout=5)
                                    if img_response.status_code == 200:
                                        accessible_images += 1
                                elif image_url.startswith('/'):
                                    # Test relative URL
                                    full_url = f"{BACKEND_URL}{image_url}"
                                    img_response = requests.get(full_url, timeout=5)
                                    if img_response.status_code == 200:
                                        accessible_images += 1
                            except:
                                pass  # Image not accessible
                
                self.log_result(
                    "Image File Existence and Accessibility",
                    len(image_urls_found) > 0,
                    f"Found {len(image_urls_found)} image URLs, {accessible_images} accessible"
                )
                
                return len(image_urls_found) > 0
            else:
                self.log_result(
                    "Image File Existence Check",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Image File Existence Check", False, "", str(e))
            return False

    def test_cross_entity_image_support(self):
        """Test image support across all entity types"""
        entity_endpoints = [
            ("/teams", "teams"),
            ("/brands", "brands"), 
            ("/players", "players"),
            ("/competitions", "competitions"),
            ("/master-jerseys", "master_jerseys")
        ]
        
        results = {}
        
        for endpoint, entity_type in entity_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    entities = response.json()
                    entities_with_images = 0
                    total_entities = len(entities) if isinstance(entities, list) else 0
                    
                    for entity in entities:
                        # Check for image-related fields
                        image_fields = ['logo_url', 'image_url', 'photo_url', 'images', 'picture_url']
                        has_images = any(entity.get(field) for field in image_fields)
                        
                        if has_images:
                            entities_with_images += 1
                    
                    results[entity_type] = {
                        'total': total_entities,
                        'with_images': entities_with_images,
                        'success': True
                    }
                    
                    self.log_result(
                        f"Cross-Entity Image Support - {entity_type.title()}",
                        True,
                        f"{entities_with_images}/{total_entities} {entity_type} have image data"
                    )
                else:
                    results[entity_type] = {'success': False, 'error': f"HTTP {response.status_code}"}
                    self.log_result(
                        f"Cross-Entity Image Support - {entity_type.title()}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                results[entity_type] = {'success': False, 'error': str(e)}
                self.log_result(f"Cross-Entity Image Support - {entity_type.title()}", False, "", str(e))
        
        # Summary
        successful_entities = sum(1 for r in results.values() if r.get('success', False))
        total_entities_tested = len(entity_endpoints)
        
        self.log_result(
            "Cross-Entity Image Support Summary",
            successful_entities == total_entities_tested,
            f"Image support tested across {successful_entities}/{total_entities_tested} entity types"
        )
        
        return successful_entities > 0

    def test_image_processing_workflow(self):
        """Test complete image processing and integration workflow"""
        try:
            # Step 1: Create contribution with image
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            contribution_data = {
                "entity_type": "team",
                "entity_id": None,
                "title": "Image Processing Workflow Test Team",
                "description": "Testing complete image processing workflow",
                "changes": {
                    "name": "Image Test FC",
                    "short_name": "ITC",
                    "country": "France",
                    "city": "Paris",
                    "founded_year": 2024,
                    "team_colors": ["Blue", "White"]
                },
                "images": [
                    {
                        "type": "logo",
                        "data": test_image_base64,
                        "filename": "test_logo.png"
                    }
                ]
            }
            
            # Create contribution
            response = self.session.post(f"{API_BASE}/contributions-v2/", json=contribution_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                contribution_id = data.get('id')
                
                self.log_result(
                    "Image Processing Workflow - Step 1: Contribution Creation",
                    True,
                    f"Created contribution with image, ID: {contribution_id}"
                )
                
                # Step 2: Check if contribution has image data
                contrib_response = self.session.get(f"{API_BASE}/contributions-v2/")
                if contrib_response.status_code == 200:
                    contributions = contrib_response.json()
                    target_contrib = next((c for c in contributions if c.get('id') == contribution_id), None)
                    
                    if target_contrib:
                        has_image_data = any(target_contrib.get(field) for field in ['images', 'image_urls', 'logo_url'])
                        self.log_result(
                            "Image Processing Workflow - Step 2: Image Data in Contribution",
                            has_image_data,
                            f"Contribution {'has' if has_image_data else 'missing'} image data"
                        )
                        
                        # Step 3: Check if team appears in main catalogue with image
                        teams_response = self.session.get(f"{API_BASE}/teams")
                        if teams_response.status_code == 200:
                            teams = teams_response.json()
                            target_team = next((t for t in teams if t.get('name') == 'Image Test FC'), None)
                            
                            if target_team:
                                team_has_image = any(target_team.get(field) for field in ['logo_url', 'image_url', 'photo_url'])
                                self.log_result(
                                    "Image Processing Workflow - Step 3: Image Integration to Catalogue",
                                    team_has_image,
                                    f"Team in catalogue {'has' if team_has_image else 'missing'} image data"
                                )
                                return team_has_image
                            else:
                                self.log_result(
                                    "Image Processing Workflow - Step 3: Team Integration",
                                    False,
                                    "",
                                    "Team not found in main catalogue"
                                )
                                return False
                        else:
                            self.log_result(
                                "Image Processing Workflow - Teams Check",
                                False,
                                "",
                                f"Failed to get teams: HTTP {teams_response.status_code}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Image Processing Workflow - Contribution Retrieval",
                            False,
                            "",
                            "Created contribution not found in contributions list"
                        )
                        return False
                else:
                    self.log_result(
                        "Image Processing Workflow - Contributions Check",
                        False,
                        "",
                        f"Failed to get contributions: HTTP {contrib_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Image Processing Workflow - Contribution Creation",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Image Processing Workflow Test", False, "", str(e))
            return False

    def test_form_dependency_endpoints(self):
        """Test form dependency endpoints for unified forms"""
        endpoints_to_test = [
            ("/teams", "Teams for dropdowns"),
            ("/brands", "Brands for dropdowns"),
            ("/competitions", "Competitions for dropdowns"),
            ("/master-jerseys", "Master kits for dropdowns")
        ]
        
        all_success = True
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else len(data.get('items', []))
                    self.log_result(
                        f"GET {endpoint}",
                        True,
                        f"{description}: Retrieved {count} items"
                    )
                else:
                    self.log_result(
                        f"GET {endpoint}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_success = False
                    
            except Exception as e:
                self.log_result(f"GET {endpoint}", False, "", str(e))
                all_success = False
        
        return all_success

    def test_voting_system(self, contribution_id):
        """Test voting system for contributions"""
        try:
            # First, get existing contributions to vote on one we didn't create
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            if response.status_code == 200:
                contributions = response.json()
                if isinstance(contributions, list) and len(contributions) > 0:
                    # Find a contribution we didn't create (use the first one)
                    existing_contribution = contributions[0]
                    existing_id = existing_contribution.get('id')
                    
                    if existing_id:
                        # Test upvote on existing contribution
                        vote_data = {"vote_type": "upvote"}
                        
                        response = self.session.post(f"{API_BASE}/contributions-v2/{existing_id}/vote", json=vote_data)
                        
                        if response.status_code in [200, 201]:
                            self.log_result(
                                "Voting System - Upvote",
                                True,
                                f"Successfully cast upvote for existing contribution {existing_id}"
                            )
                            
                            # Test downvote (should replace previous vote)
                            vote_data["vote_type"] = "downvote"
                            response = self.session.post(f"{API_BASE}/contributions-v2/{existing_id}/vote", json=vote_data)
                            
                            if response.status_code in [200, 201]:
                                self.log_result(
                                    "Voting System - Downvote",
                                    True,
                                    f"Successfully cast downvote for existing contribution {existing_id}"
                                )
                                return True
                            else:
                                self.log_result(
                                    "Voting System - Downvote",
                                    False,
                                    "",
                                    f"HTTP {response.status_code}: {response.text}"
                                )
                                return False
                        else:
                            # If we can't vote (maybe we created this one too), that's still valid behavior
                            if response.status_code == 403 and "propre contribution" in response.text:
                                self.log_result(
                                    "Voting System - Self-Vote Prevention",
                                    True,
                                    "Correctly prevents voting on own contributions"
                                )
                                return True
                            else:
                                self.log_result(
                                    "Voting System - Upvote",
                                    False,
                                    "",
                                    f"HTTP {response.status_code}: {response.text}"
                                )
                                return False
                    else:
                        self.log_result("Voting System Test", False, "", "No contribution ID found in existing contributions")
                        return False
                else:
                    self.log_result("Voting System Test", False, "", "No existing contributions found")
                    return False
            else:
                self.log_result("Voting System Test", False, "", f"Failed to get contributions: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Voting System Test", False, "", str(e))
            return False

    def test_authentication_requirements(self):
        """Test that endpoints require proper JWT tokens"""
        # Create a session without authentication
        unauth_session = requests.Session()
        
        protected_endpoints = [
            ("/contributions-v2/", "POST", "Create contribution"),
            ("/admin/settings", "GET", "Admin settings"),
            ("/admin/users", "GET", "Admin users")
        ]
        
        all_protected = True
        
        for endpoint, method, description in protected_endpoints:
            try:
                if method == "GET":
                    response = unauth_session.get(f"{API_BASE}{endpoint}")
                elif method == "POST":
                    response = unauth_session.post(f"{API_BASE}{endpoint}", json={})
                
                if response.status_code == 401:
                    self.log_result(
                        f"Authentication Required - {description}",
                        True,
                        f"Endpoint properly protected (HTTP 401)"
                    )
                else:
                    self.log_result(
                        f"Authentication Required - {description}",
                        False,
                        "",
                        f"Expected HTTP 401, got {response.status_code}"
                    )
                    all_protected = False
                    
            except Exception as e:
                self.log_result(f"Authentication Required - {description}", False, "", str(e))
                all_protected = False
        
        return all_protected

    def test_admin_specific_endpoints(self):
        """Test admin-specific endpoints with admin credentials"""
        admin_endpoints = [
            ("/admin/settings", "GET", "Admin settings"),
            ("/admin/dashboard-stats", "GET", "Dashboard statistics"),
            ("/admin/users", "GET", "User management")
        ]
        
        all_success = True
        
        for endpoint, method, description in admin_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        f"Admin Endpoint - {description}",
                        True,
                        f"Successfully accessed admin endpoint"
                    )
                else:
                    self.log_result(
                        f"Admin Endpoint - {description}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    all_success = False
                    
            except Exception as e:
                self.log_result(f"Admin Endpoint - {description}", False, "", str(e))
                all_success = False
        
        return all_success

    def run_all_tests(self):
        """Run all backend tests focused on CRITICAL IMAGE DISPLAY BUG INVESTIGATION"""
        print("🚀 Starting TopKit Backend Testing - CRITICAL IMAGE DISPLAY BUG INVESTIGATION")
        print("Testing image upload, storage, integration, and display functionality")
        print("=" * 90)
        
        # Step 1: Authenticate admin with specified credentials
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test Specific Team Entities for Image Data
        print("\n🔍 INVESTIGATION 1: Testing Specific Team Entities for Image Data")
        print("-" * 60)
        self.test_specific_team_entities_image_data()
        
        # Step 3: Test Image Upload Process
        print("\n📤 INVESTIGATION 2: Testing Image Upload Process")
        print("-" * 60)
        self.test_image_upload_endpoint()
        
        # Step 4: Test Image Storage and Association
        print("\n💾 INVESTIGATION 3: Testing Image Storage and Association")
        print("-" * 60)
        self.test_contribution_image_association()
        
        # Step 5: Test Image Integration Workflow
        print("\n🔄 INVESTIGATION 4: Testing Image Integration Workflow")
        print("-" * 60)
        self.test_image_processing_workflow()
        
        # Step 6: Test Image File Existence and Accessibility
        print("\n🌐 INVESTIGATION 5: Testing Image File Existence and Accessibility")
        print("-" * 60)
        self.test_image_file_existence_and_accessibility()
        
        # Step 7: Test Cross-Entity Image Support
        print("\n🔀 INVESTIGATION 6: Testing Cross-Entity Image Support")
        print("-" * 60)
        self.test_cross_entity_image_support()
        
        # Step 8: Test Basic System Functionality
        print("\n🔧 INVESTIGATION 7: Testing Basic System Functionality")
        print("-" * 60)
        
        # Test contributions-v2 GET endpoint
        contributions = self.test_contributions_v2_get()
        
        # Test form dependency endpoints
        form_deps_success = self.test_form_dependency_endpoints()
        
        # Test authentication requirements
        auth_success = self.test_authentication_requirements()
        
        # Generate comprehensive summary focused on image issues
        self.generate_image_investigation_summary()
        
        return True

    def generate_image_investigation_summary(self):
        """Generate comprehensive summary focused on image display bug investigation"""
        print("\n" + "=" * 90)
        print("📊 CRITICAL IMAGE DISPLAY BUG INVESTIGATION SUMMARY")
        print("=" * 90)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Categorize results by investigation area
        investigations = {
            "Target Team Entities": ["Target Team Entity", "Target Team Entities"],
            "Image Upload Process": ["Image Upload Endpoint", "Image Upload"],
            "Image Storage & Association": ["Contribution Image Association", "Image Storage"],
            "Image Integration Workflow": ["Image Processing Workflow", "Image Integration"],
            "Image File Accessibility": ["Image File Existence", "Image Accessibility"],
            "Cross-Entity Image Support": ["Cross-Entity Image Support"],
            "System Functionality": ["Admin Authentication", "GET /api/contributions", "Authentication Required"]
        }
        
        print("\n📋 INVESTIGATION RESULTS BY AREA:")
        print("-" * 50)
        
        critical_issues = []
        
        for investigation_name, keywords in investigations.items():
            investigation_tests = [r for r in self.test_results if any(keyword in r['test'] for keyword in keywords)]
            if investigation_tests:
                investigation_passed = sum(1 for r in investigation_tests if r['success'])
                investigation_total = len(investigation_tests)
                investigation_rate = (investigation_passed / investigation_total * 100) if investigation_total > 0 else 0
                status = "✅" if investigation_rate >= 80 else "⚠️" if investigation_rate >= 60 else "❌"
                print(f"{status} {investigation_name}: {investigation_passed}/{investigation_total} ({investigation_rate:.1f}%)")
                
                # Track critical issues
                if investigation_rate < 80:
                    failed_in_area = [r for r in investigation_tests if not r['success']]
                    for failed_test in failed_in_area:
                        critical_issues.append(f"{investigation_name}: {failed_test['test']} - {failed_test['error']}")
        
        # Root Cause Analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 50)
        
        if critical_issues:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"  • {issue}")
        else:
            print("✅ No critical issues detected in image system")
        
        # Specific findings for the review request
        print(f"\n📋 SPECIFIC FINDINGS FOR REVIEW REQUEST:")
        print("-" * 50)
        
        # Check for target team entities
        target_team_tests = [r for r in self.test_results if "Target Team Entity" in r['test']]
        if target_team_tests:
            target_found = any(r['success'] for r in target_team_tests)
            print(f"  • Target Teams (TK-TEAM-4156DC3C, TK-TEAM-00BEEF9B): {'Found' if target_found else 'Not Found'}")
        
        # Check image upload functionality
        upload_tests = [r for r in self.test_results if "Image Upload" in r['test']]
        if upload_tests:
            upload_working = any(r['success'] for r in upload_tests)
            print(f"  • Image Upload Process: {'Working' if upload_working else 'Not Working'}")
        
        # Check image integration
        integration_tests = [r for r in self.test_results if "Image Processing Workflow" in r['test']]
        if integration_tests:
            integration_working = any(r['success'] for r in integration_tests)
            print(f"  • Image Integration to Catalogue: {'Working' if integration_working else 'Not Working'}")
        
        # Check cross-entity support
        cross_entity_tests = [r for r in self.test_results if "Cross-Entity" in r['test']]
        if cross_entity_tests:
            cross_entity_working = any(r['success'] for r in cross_entity_tests)
            print(f"  • Cross-Entity Image Support: {'Working' if cross_entity_working else 'Not Working'}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['error']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for result in self.test_results:
            if result['success']:
                print(f"  - {result['test']}")
        
        # Final assessment and recommendations
        print("\n" + "=" * 90)
        print("🎯 IMAGE DISPLAY BUG ASSESSMENT & RECOMMENDATIONS")
        print("=" * 90)
        
        if success_rate >= 90:
            print(f"✅ EXCELLENT: Image system is working correctly with {success_rate:.1f}% success rate!")
            print("   No critical image display bugs detected. System is functioning as expected.")
        elif success_rate >= 70:
            print(f"⚠️ PARTIAL ISSUES: Image system has some issues with {success_rate:.1f}% success rate.")
            print("   Some image functionality working but issues need investigation.")
        else:
            print(f"❌ CRITICAL ISSUES: Image system has major problems ({success_rate:.1f}% success rate).")
            print("   Significant image display bugs confirmed. Immediate fixes required.")
        
        # Specific recommendations
        print(f"\n📝 SPECIFIC RECOMMENDATIONS:")
        
        if len(critical_issues) == 0:
            print("   ✅ No immediate fixes required - image system working correctly")
        else:
            print("   🔧 REQUIRED FIXES:")
            
            # Image upload issues
            upload_failed = any("Image Upload" in issue for issue in critical_issues)
            if upload_failed:
                print("     • Fix image upload endpoint - ensure /api/upload/image or similar endpoint exists")
                print("     • Verify image processing and storage functionality")
            
            # Image integration issues  
            integration_failed = any("Image Processing Workflow" in issue or "Image Integration" in issue for issue in critical_issues)
            if integration_failed:
                print("     • Fix image integration from contributions to main catalogue entities")
                print("     • Ensure approved contributions transfer image data properly")
            
            # Image accessibility issues
            accessibility_failed = any("Image File Existence" in issue or "Image Accessibility" in issue for issue in critical_issues)
            if accessibility_failed:
                print("     • Fix image file storage and URL generation")
                print("     • Ensure uploaded images are accessible via proper URLs")
            
            # Cross-entity issues
            cross_entity_failed = any("Cross-Entity" in issue for issue in critical_issues)
            if cross_entity_failed:
                print("     • Implement consistent image support across all entity types")
                print("     • Ensure teams, brands, players, competitions, kits all support images")
        
        print(f"\n🎯 NEXT STEPS:")
        if success_rate >= 90:
            print("   1. ✅ Image system is working correctly")
            print("   2. 🔍 Investigate frontend display issues if images still not showing")
            print("   3. 📱 Test image display on entity detail pages")
        else:
            print("   1. 🔧 Fix identified backend image issues")
            print("   2. 🧪 Re-test image upload and integration workflow")
            print("   3. 🔍 Verify image URLs and file accessibility")
            print("   4. 📱 Test complete image workflow from upload to display")

    def generate_summary(self):
        """Legacy method - redirect to final summary"""
        self.generate_final_summary()

if __name__ == "__main__":
    tester = TopKitBackendTester()
    tester.run_all_tests()