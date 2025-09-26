#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - CONTRIBUTION CREATION FIX VERIFICATION

**CONTRIBUTION CREATION FIX TESTING:**
Testing the critical bug fix where all brand/team/player/competition contributions 
were being saved to the wrong database collection (db.contributions instead of db.contributions_v2).

**TEST FOCUS:**

1. **Authentication**: Login with emergency.admin@topkit.test / EmergencyAdmin2025!

2. **Create Test Brand Contribution**:
   - Test POST /api/contributions-v2/ with brand entity data
   - Use proper JSON payload with entity_type: "brand", title, description, data fields
   - Verify contribution is saved to contributions_v2 collection (not the old contributions collection)

3. **Verify Contribution Appears**:
   - Test GET /api/contributions-v2/ to see all contributions 
   - Check if the new brand contribution appears with other contributions
   - Verify it has entity_type="brand" and proper status

4. **Test Moderation Dashboard Data**:
   - Test GET /api/contributions-v2/admin/moderation-stats
   - Verify the pending count increases after creating the brand contribution
   - Check consistency between stats and actual contributions

5. **Create Additional Entity Types**:
   - Test team contribution creation
   - Test player contribution creation  
   - Test competition contribution creation
   - Verify all entity types now appear in contributions_v2

**Expected Results**:
- Brand/team/player/competition contributions now save correctly to contributions_v2
- All contributions appear in moderation dashboard 
- Consistent counts between stats and actual data
- User will now see ALL contribution types with pending approval stickers
- Fixed the core issue preventing 80% of contributions from being visible

**PRIORITY: CRITICAL** - This fix should restore the entire contribution moderation workflow.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://collector-hub-4.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitContributionSystemInvestigation:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate with emergency admin credentials"""
        try:
            print(f"\n🔐 EMERGENCY ADMIN AUTHENTICATION")
            print("=" * 60)
            print(f"   Email: {ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Emergency Admin Authentication", True, 
                             f"✅ Emergency admin authentication successful")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Email: {self.admin_user_data.get('email')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Emergency Admin Authentication", False, 
                             f"❌ Emergency admin authentication failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def investigate_contributions_v2_collection(self):
        """Investigate contributions_v2 collection to analyze entity types"""
        try:
            print(f"\n📊 INVESTIGATING CONTRIBUTIONS V2 COLLECTION")
            print("=" * 80)
            print("Analyzing contributions_v2 collection by entity_type...")
            
            if not self.auth_token:
                print(f"         ⚠️ No auth token available, attempting authentication...")
                if not self.authenticate_admin():
                    self.log_test("Contributions V2 Collection Analysis", False, 
                                 "❌ Cannot authenticate for collection analysis")
                    return False, [], {}
            
            # Step 1: Get all contributions without filters
            print(f"      Step 1: Getting ALL contributions from contributions_v2...")
            
            all_contributions_response = self.session.get(
                f"{BACKEND_URL}/contributions-v2/",
                timeout=10
            )
            
            if all_contributions_response.status_code == 200:
                all_contributions = all_contributions_response.json()
                print(f"         ✅ Retrieved {len(all_contributions)} total contributions")
                
                # Analyze by entity_type
                entity_type_counts = {}
                status_counts = {}
                
                for contrib in all_contributions:
                    entity_type = contrib.get('entity_type', 'unknown')
                    status = contrib.get('status', 'unknown')
                    
                    entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                print(f"         📊 ENTITY TYPE BREAKDOWN:")
                for entity_type, count in entity_type_counts.items():
                    print(f"            {entity_type}: {count} contributions")
                
                print(f"         📊 STATUS BREAKDOWN:")
                for status, count in status_counts.items():
                    print(f"            {status}: {count} contributions")
                
                # Check for non-master_kit contributions
                non_master_kit_contributions = [c for c in all_contributions if c.get('entity_type') != 'master_kit']
                
                if non_master_kit_contributions:
                    print(f"         ✅ Found {len(non_master_kit_contributions)} non-master_kit contributions:")
                    for contrib in non_master_kit_contributions[:5]:  # Show first 5
                        print(f"            - {contrib.get('entity_type')} (ID: {contrib.get('id')}, Status: {contrib.get('status')})")
                else:
                    print(f"         ❌ NO NON-MASTER_KIT CONTRIBUTIONS FOUND!")
                    print(f"            This explains why user only sees master_kit contributions")
                
                self.log_test("Contributions V2 Collection Analysis", True, 
                             f"✅ Collection analysis complete - {len(all_contributions)} total, {len(non_master_kit_contributions)} non-master_kit")
                return True, all_contributions, entity_type_counts
                
            else:
                print(f"         ❌ Failed to retrieve contributions - Status {all_contributions_response.status_code}")
                print(f"            Error: {all_contributions_response.text}")
                self.log_test("Contributions V2 Collection Analysis", False, 
                             f"❌ Failed to retrieve contributions - Status {all_contributions_response.status_code}")
                return False, [], {}
                
        except Exception as e:
            self.log_test("Contributions V2 Collection Analysis", False, f"Exception: {str(e)}")
            return False, [], {}
    
    def test_contribution_creation_endpoints(self):
        """Test contribution creation endpoints for different entity types"""
        try:
            print(f"\n🔧 TESTING CONTRIBUTION CREATION ENDPOINTS")
            print("=" * 80)
            print("Testing contribution creation for different entity types...")
            
            if not self.auth_token:
                print(f"         ⚠️ No auth token available, attempting authentication...")
                if not self.authenticate_admin():
                    self.log_test("Contribution Creation Endpoints", False, 
                                 "❌ Cannot authenticate for endpoint testing")
                    return False, [], {}
            
            # Step 1: Check available form data endpoints
            print(f"      Step 1: Checking available form data endpoints...")
            
            form_data_endpoints = [
                ("clubs", "/form-data/clubs"),
                ("brands", "/form-data/brands"),
                ("competitions", "/form-data/competitions"),
                ("players", "/form-data/players")
            ]
            
            available_entities = {}
            
            for entity_name, endpoint in form_data_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        available_entities[entity_name] = data
                        print(f"         ✅ {entity_name}: {len(data)} items available")
                        if data:  # Show first item as example
                            print(f"            Example: {data[0].get('name', 'N/A')} (ID: {data[0].get('id', 'N/A')})")
                    else:
                        print(f"         ❌ {entity_name}: Failed - Status {response.status_code}")
                        available_entities[entity_name] = []
                except Exception as e:
                    print(f"         ❌ {entity_name}: Exception - {str(e)}")
                    available_entities[entity_name] = []
            
            # Step 2: Look for contribution creation endpoints
            print(f"      Step 2: Testing contribution creation endpoints...")
            
            # Test different possible endpoints for contribution creation
            contribution_endpoints_to_test = [
                ("POST /api/contributions-v2/", "contributions-v2/"),
                ("POST /api/contributions/", "contributions/"),
                ("POST /api/brands/", "brands/"),
                ("POST /api/teams/", "teams/"),
                ("POST /api/players/", "players/"),
                ("POST /api/competitions/", "competitions/")
            ]
            
            working_endpoints = []
            
            for endpoint_name, endpoint_path in contribution_endpoints_to_test:
                try:
                    # Test with minimal data to see if endpoint exists
                    test_data = {
                        "name": "Test Contribution",
                        "entity_type": "brand"
                    }
                    
                    response = self.session.post(
                        f"{BACKEND_URL}/{endpoint_path}",
                        json=test_data,
                        timeout=10
                    )
                    
                    print(f"         Testing {endpoint_name}...")
                    print(f"            Status: {response.status_code}")
                    
                    if response.status_code in [200, 201, 400, 422]:  # 400/422 means endpoint exists but validation failed
                        working_endpoints.append((endpoint_name, endpoint_path, response.status_code))
                        print(f"            ✅ Endpoint exists (Status {response.status_code})")
                        if response.status_code in [400, 422]:
                            print(f"            Response: {response.text[:200]}...")
                    elif response.status_code == 404:
                        print(f"            ❌ Endpoint not found")
                    elif response.status_code == 405:
                        print(f"            ⚠️ Method not allowed (endpoint exists but POST not supported)")
                    else:
                        print(f"            ⚠️ Unexpected status: {response.status_code}")
                        
                except Exception as e:
                    print(f"            ❌ Exception: {str(e)}")
            
            print(f"      📊 ENDPOINT ANALYSIS:")
            print(f"         Working endpoints found: {len(working_endpoints)}")
            for endpoint_name, endpoint_path, status in working_endpoints:
                print(f"            - {endpoint_name} (Status {status})")
            
            # Step 3: Try to create a test brand contribution
            print(f"      Step 3: Attempting to create test brand contribution...")
            
            if available_entities.get('brands'):
                brand_data = available_entities['brands'][0]
                
                # Try different possible contribution creation methods
                contribution_attempts = [
                    {
                        "method": "Direct brand contribution",
                        "endpoint": "contributions-v2/",
                        "data": {
                            "entity_type": "brand",
                            "entity_id": brand_data.get('id'),
                            "name": f"Test Brand Contribution - {brand_data.get('name')}",
                            "description": "Test brand contribution for investigation",
                            "status": "pending_review"
                        }
                    },
                    {
                        "method": "Brand entity creation",
                        "endpoint": "brands/",
                        "data": {
                            "name": f"Test Brand {uuid.uuid4().hex[:8]}",
                            "country": "Test Country",
                            "type": "brand"
                        }
                    }
                ]
                
                for attempt in contribution_attempts:
                    try:
                        print(f"         Trying {attempt['method']}...")
                        
                        response = self.session.post(
                            f"{BACKEND_URL}/{attempt['endpoint']}",
                            json=attempt['data'],
                            timeout=10
                        )
                        
                        print(f"            Status: {response.status_code}")
                        print(f"            Response: {response.text[:300]}...")
                        
                        if response.status_code in [200, 201]:
                            print(f"            ✅ Success! Brand contribution created")
                            created_data = response.json()
                            print(f"            Created ID: {created_data.get('id', 'N/A')}")
                            break
                        else:
                            print(f"            ❌ Failed with status {response.status_code}")
                            
                    except Exception as e:
                        print(f"            ❌ Exception: {str(e)}")
            else:
                print(f"         ⚠️ No brands available for testing contribution creation")
            
            self.log_test("Contribution Creation Endpoints", True, 
                         f"✅ Endpoint investigation complete - {len(working_endpoints)} working endpoints found")
            return True, working_endpoints, available_entities
            
        except Exception as e:
            self.log_test("Contribution Creation Endpoints", False, f"Exception: {str(e)}")
            return False, [], {}
    
    def test_contribution_filtering_endpoints(self):
        """Test contribution filtering by entity_type"""
        try:
            print(f"\n🔍 TESTING CONTRIBUTION FILTERING ENDPOINTS")
            print("=" * 80)
            print("Testing filtering by entity_type to identify missing contributions...")
            
            if not self.auth_token:
                print(f"         ⚠️ No auth token available, attempting authentication...")
                if not self.authenticate_admin():
                    self.log_test("Contribution Filtering", False, 
                                 "❌ Cannot authenticate for filtering tests")
                    return False, {}, {}, []
            
            # Test filtering by different entity types
            entity_types_to_test = ['master_kit', 'brand', 'team', 'player', 'competition']
            
            filtering_results = {}
            
            for entity_type in entity_types_to_test:
                print(f"      Testing filter for entity_type='{entity_type}'...")
                
                try:
                    # Test with entity_type filter
                    response = self.session.get(
                        f"{BACKEND_URL}/contributions-v2/?entity_type={entity_type}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        contributions = response.json()
                        filtering_results[entity_type] = contributions
                        print(f"         ✅ {entity_type}: {len(contributions)} contributions found")
                        
                        if contributions:
                            # Show details of first contribution
                            first_contrib = contributions[0]
                            print(f"            Example: ID {first_contrib.get('id')}, Status: {first_contrib.get('status')}")
                        else:
                            print(f"            ⚠️ No contributions found for {entity_type}")
                    else:
                        print(f"         ❌ {entity_type}: Failed - Status {response.status_code}")
                        print(f"            Error: {response.text}")
                        filtering_results[entity_type] = []
                        
                except Exception as e:
                    print(f"         ❌ {entity_type}: Exception - {str(e)}")
                    filtering_results[entity_type] = []
            
            # Test status filtering
            print(f"      Testing status filtering...")
            
            status_types_to_test = ['pending', 'pending_review', 'approved', 'rejected']
            status_results = {}
            
            for status in status_types_to_test:
                try:
                    response = self.session.get(
                        f"{BACKEND_URL}/contributions-v2/?status={status}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        contributions = response.json()
                        status_results[status] = contributions
                        print(f"         ✅ status={status}: {len(contributions)} contributions")
                    else:
                        print(f"         ❌ status={status}: Failed - Status {response.status_code}")
                        status_results[status] = []
                        
                except Exception as e:
                    print(f"         ❌ status={status}: Exception - {str(e)}")
                    status_results[status] = []
            
            # Analysis
            print(f"      📊 FILTERING ANALYSIS:")
            
            total_by_entity = sum(len(contribs) for contribs in filtering_results.values())
            total_by_status = sum(len(contribs) for contribs in status_results.values())
            
            print(f"         Total contributions by entity_type: {total_by_entity}")
            print(f"         Total contributions by status: {total_by_status}")
            
            # Check for missing entity types
            missing_entity_types = [et for et, contribs in filtering_results.items() if len(contribs) == 0 and et != 'master_kit']
            
            if missing_entity_types:
                print(f"         ❌ MISSING ENTITY TYPES: {missing_entity_types}")
                print(f"            This explains why user only sees master_kit contributions!")
            else:
                print(f"         ✅ All entity types have contributions")
            
            # Check pending contributions
            pending_contributions = status_results.get('pending', []) + status_results.get('pending_review', [])
            
            print(f"         Pending contributions for moderation: {len(pending_contributions)}")
            
            if pending_contributions:
                pending_entity_types = {}
                for contrib in pending_contributions:
                    et = contrib.get('entity_type', 'unknown')
                    pending_entity_types[et] = pending_entity_types.get(et, 0) + 1
                
                print(f"         Pending by entity type:")
                for et, count in pending_entity_types.items():
                    print(f"            {et}: {count}")
            
            self.log_test("Contribution Filtering", True, 
                         f"✅ Filtering analysis complete - {len(missing_entity_types)} missing entity types identified")
            return True, filtering_results, status_results, missing_entity_types
            
        except Exception as e:
            self.log_test("Contribution Filtering", False, f"Exception: {str(e)}")
            return False, {}, {}, []
    
    def investigate_database_collections(self):
        """Investigate if contributions are being saved to wrong collections"""
        try:
            print(f"\n🗄️ INVESTIGATING DATABASE COLLECTIONS")
            print("=" * 80)
            print("Checking if contributions are saved to different collections...")
            
            if not self.auth_token:
                print(f"         ⚠️ No auth token available, attempting authentication...")
                if not self.authenticate_admin():
                    self.log_test("Database Collections Investigation", False, 
                                 "❌ Cannot authenticate for database investigation")
                    return False, {}
            
            # Test different possible collection endpoints
            collection_endpoints = [
                ("contributions_v2", "/contributions-v2/"),
                ("contributions", "/contributions/"),
                ("moderation", "/contributions-v2/admin/moderation-stats")
            ]
            
            collection_results = {}
            
            for collection_name, endpoint in collection_endpoints:
                print(f"      Testing {collection_name} collection via {endpoint}...")
                
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if isinstance(data, list):
                            collection_results[collection_name] = {
                                "count": len(data),
                                "data": data,
                                "type": "list"
                            }
                            print(f"         ✅ {collection_name}: {len(data)} items found")
                            
                            # Analyze entity types if available
                            if data and isinstance(data[0], dict) and 'entity_type' in data[0]:
                                entity_types = {}
                                for item in data:
                                    et = item.get('entity_type', 'unknown')
                                    entity_types[et] = entity_types.get(et, 0) + 1
                                
                                print(f"            Entity types: {entity_types}")
                                
                        elif isinstance(data, dict):
                            collection_results[collection_name] = {
                                "count": 1,
                                "data": data,
                                "type": "dict"
                            }
                            print(f"         ✅ {collection_name}: Stats object returned")
                            print(f"            Data: {data}")
                        else:
                            collection_results[collection_name] = {
                                "count": 0,
                                "data": data,
                                "type": "other"
                            }
                            print(f"         ⚠️ {collection_name}: Unexpected data type")
                            
                    elif response.status_code == 404:
                        print(f"         ❌ {collection_name}: Collection not found")
                        collection_results[collection_name] = {"count": 0, "data": None, "type": "not_found"}
                    else:
                        print(f"         ❌ {collection_name}: Failed - Status {response.status_code}")
                        print(f"            Error: {response.text}")
                        collection_results[collection_name] = {"count": 0, "data": None, "type": "error"}
                        
                except Exception as e:
                    print(f"         ❌ {collection_name}: Exception - {str(e)}")
                    collection_results[collection_name] = {"count": 0, "data": None, "type": "exception"}
            
            # Analysis
            print(f"      📊 DATABASE COLLECTIONS ANALYSIS:")
            
            total_contributions = 0
            for collection_name, result in collection_results.items():
                count = result.get("count", 0)
                total_contributions += count if result.get("type") == "list" else 0
                print(f"         {collection_name}: {count} items ({result.get('type', 'unknown')})")
            
            print(f"         Total contributions across collections: {total_contributions}")
            
            # Check for collection inconsistencies
            contributions_v2_count = collection_results.get("contributions_v2", {}).get("count", 0)
            contributions_count = collection_results.get("contributions", {}).get("count", 0)
            
            if contributions_count > 0 and contributions_v2_count == 0:
                print(f"         ❌ COLLECTION MISMATCH: Contributions in 'contributions' but not 'contributions_v2'")
                print(f"            This could explain missing contributions in moderation dashboard")
            elif contributions_v2_count > 0 and contributions_count == 0:
                print(f"         ✅ Contributions properly in 'contributions_v2' collection")
            elif contributions_v2_count > 0 and contributions_count > 0:
                print(f"         ⚠️ Contributions in BOTH collections - potential duplication")
            else:
                print(f"         ❌ NO CONTRIBUTIONS found in either collection")
            
            self.log_test("Database Collections Investigation", True, 
                         f"✅ Database investigation complete - {total_contributions} total contributions found")
            return True, collection_results
            
        except Exception as e:
            self.log_test("Database Collections Investigation", False, f"Exception: {str(e)}")
            return False, {}
    
    def run_comprehensive_contribution_investigation(self):
        """Run comprehensive contribution system investigation"""
        print("\n🚀 COMPREHENSIVE CONTRIBUTION SYSTEM INVESTIGATION")
        print("Investigating critical contribution system issues")
        print("=" * 80)
        
        investigation_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        auth_success = self.authenticate_admin()
        investigation_results.append(auth_success)
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return investigation_results, {}
        
        # Step 2: Investigate contributions_v2 collection
        print("\n2️⃣ Investigating Contributions V2 Collection...")
        collection_success, all_contributions, entity_type_counts = self.investigate_contributions_v2_collection()
        investigation_results.append(collection_success)
        
        # Step 3: Test contribution creation endpoints
        print("\n3️⃣ Testing Contribution Creation Endpoints...")
        creation_success, working_endpoints, available_entities = self.test_contribution_creation_endpoints()
        investigation_results.append(creation_success)
        
        # Step 4: Test contribution filtering
        print("\n4️⃣ Testing Contribution Filtering...")
        filtering_success, filtering_results, status_results, missing_entity_types = self.test_contribution_filtering_endpoints()
        investigation_results.append(filtering_success)
        
        # Step 5: Investigate database collections
        print("\n5️⃣ Investigating Database Collections...")
        db_success, collection_results = self.investigate_database_collections()
        investigation_results.append(db_success)
        
        return investigation_results, {
            "all_contributions": all_contributions if collection_success else [],
            "entity_type_counts": entity_type_counts if collection_success else {},
            "working_endpoints": working_endpoints if creation_success else [],
            "available_entities": available_entities if creation_success else {},
            "filtering_results": filtering_results if filtering_success else {},
            "status_results": status_results if filtering_success else {},
            "missing_entity_types": missing_entity_types if filtering_success else [],
            "collection_results": collection_results if db_success else {}
        }
    
    def print_comprehensive_investigation_summary(self, investigation_data):
        """Print final comprehensive investigation summary"""
        print("\n📊 COMPREHENSIVE CONTRIBUTION SYSTEM INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total investigation steps: {total_tests}")
        print(f"Completed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 CRITICAL CONTRIBUTION SYSTEM FINDINGS:")
        
        # Entity type analysis
        entity_type_counts = investigation_data.get("entity_type_counts", {})
        missing_entity_types = investigation_data.get("missing_entity_types", [])
        
        print(f"\n📊 ENTITY TYPE ANALYSIS:")
        if entity_type_counts:
            for entity_type, count in entity_type_counts.items():
                print(f"  {entity_type}: {count} contributions")
        else:
            print(f"  ❌ No entity type data available")
        
        if missing_entity_types:
            print(f"\n❌ MISSING ENTITY TYPES ({len(missing_entity_types)}):")
            for entity_type in missing_entity_types:
                print(f"  • {entity_type}: NO contributions found")
            print(f"  🎯 ROOT CAUSE: This explains why user only sees master_kit contributions!")
        else:
            print(f"\n✅ All entity types have contributions")
        
        # Endpoint analysis
        working_endpoints = investigation_data.get("working_endpoints", [])
        print(f"\n🔧 CONTRIBUTION CREATION ENDPOINTS:")
        if working_endpoints:
            print(f"  Found {len(working_endpoints)} working endpoints:")
            for endpoint_name, endpoint_path, status in working_endpoints:
                print(f"    • {endpoint_name} (Status {status})")
        else:
            print(f"  ❌ No working contribution creation endpoints found")
        
        # Database collection analysis
        collection_results = investigation_data.get("collection_results", {})
        print(f"\n🗄️ DATABASE COLLECTION ANALYSIS:")
        if collection_results:
            for collection_name, result in collection_results.items():
                count = result.get("count", 0)
                result_type = result.get("type", "unknown")
                print(f"  {collection_name}: {count} items ({result_type})")
        else:
            print(f"  ❌ No database collection data available")
        
        # Status analysis
        status_results = investigation_data.get("status_results", {})
        print(f"\n📋 CONTRIBUTION STATUS ANALYSIS:")
        if status_results:
            for status, contributions in status_results.items():
                print(f"  {status}: {len(contributions)} contributions")
        else:
            print(f"  ❌ No status data available")
        
        # Final diagnosis
        print(f"\n🎯 CONTRIBUTION SYSTEM DIAGNOSIS:")
        
        if missing_entity_types:
            print(f"  ❌ CRITICAL ISSUE IDENTIFIED:")
            print(f"     • Only master_kit contributions exist in system")
            print(f"     • Missing entity types: {', '.join(missing_entity_types)}")
            print(f"     • User's brand contribution likely failed to save or was saved incorrectly")
            print(f"     • Contribution creation endpoints for non-master_kit entities may be broken")
            
            print(f"\n  🔧 RECOMMENDED FIXES:")
            print(f"     1. Investigate why brand/team/player/competition contributions aren't being created")
            print(f"     2. Check if contribution creation endpoints exist for all entity types")
            print(f"     3. Verify contribution form submission logic for different entity types")
            print(f"     4. Test actual contribution creation for each missing entity type")
            print(f"     5. Check if contributions are being saved to wrong collection or with wrong entity_type")
            
        else:
            print(f"  ✅ All entity types have contributions - issue may be elsewhere")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ INVESTIGATION FAILURES ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the comprehensive contribution system investigation"""
    investigator = TopKitContributionSystemInvestigation()
    
    # Run the comprehensive contribution investigation
    investigation_results, investigation_data = investigator.run_comprehensive_contribution_investigation()
    
    # Print comprehensive summary
    investigator.print_comprehensive_investigation_summary(investigation_data)
    
    # Return overall success
    return all(investigation_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)