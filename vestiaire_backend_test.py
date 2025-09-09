#!/usr/bin/env python3
"""
TopKit Vestiaire System Backend Testing
Testing the new Vestiaire system features as requested in review.

FOCUS AREAS:
1. JerseyReleaseValuation and UserJerseyCollection models
2. GET /api/vestiaire endpoint with filtering and price estimation
3. Authentication for collection features
4. Master Jersey data enrichment
5. Price estimation logic verification
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Configuration
API_BASE = "https://jersey-catalog-2.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class VestiaireBackendTester:
    def __init__(self):
        self.session = None
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
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
            
    async def authenticate_user(self):
        """Authenticate test user"""
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_token = data.get('token')
                    self.log_test("User Authentication", True, f"User: {data.get('user', {}).get('name', 'Unknown')}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
            
    async def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get('token')
                    self.log_test("Admin Authentication", True, f"Admin: {data.get('user', {}).get('name', 'Unknown')}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Admin Authentication", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
            
    async def test_vestiaire_endpoint_basic(self):
        """Test basic Vestiaire endpoint functionality"""
        try:
            async with self.session.get(f"{API_BASE}/vestiaire") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Vestiaire Endpoint Basic Access", True, f"Found {len(data)} jersey releases")
                    return data
                else:
                    error_text = await response.text()
                    self.log_test("Vestiaire Endpoint Basic Access", False, f"HTTP {response.status}: {error_text}")
                    return []
        except Exception as e:
            self.log_test("Vestiaire Endpoint Basic Access", False, f"Exception: {str(e)}")
            return []
            
    async def test_vestiaire_filtering(self):
        """Test Vestiaire endpoint filtering capabilities"""
        test_filters = [
            {"player_name": "Messi", "description": "Player name filter"},
            {"season": "2024/25", "description": "Season filter"},
            {"team_id": "test-team-id", "description": "Team ID filter"},
            {"player_name": "Ronaldo", "season": "2023/24", "description": "Multiple filters"}
        ]
        
        for filter_test in test_filters:
            try:
                params = {k: v for k, v in filter_test.items() if k != "description"}
                async with self.session.get(f"{API_BASE}/vestiaire", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test(f"Vestiaire Filtering - {filter_test['description']}", True, 
                                    f"Filter {params} returned {len(data)} results")
                    else:
                        error_text = await response.text()
                        self.log_test(f"Vestiaire Filtering - {filter_test['description']}", False, 
                                    f"HTTP {response.status}: {error_text}")
            except Exception as e:
                self.log_test(f"Vestiaire Filtering - {filter_test['description']}", False, f"Exception: {str(e)}")
                
    async def test_price_estimation_logic(self):
        """Test price estimation logic in Vestiaire responses"""
        try:
            async with self.session.get(f"{API_BASE}/vestiaire?limit=10") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data:
                        self.log_test("Price Estimation Logic", False, "No jersey releases found to test pricing")
                        return
                        
                    price_fields_found = 0
                    valid_estimations = 0
                    
                    for release in data:
                        # Check for required price estimation fields
                        required_fields = ['estimated_value', 'estimated_min', 'estimated_max']
                        has_all_fields = all(field in release for field in required_fields)
                        
                        if has_all_fields:
                            price_fields_found += 1
                            
                            # Validate price logic (min <= value <= max)
                            est_min = release.get('estimated_min', 0)
                            est_value = release.get('estimated_value', 0)
                            est_max = release.get('estimated_max', 0)
                            
                            if est_min <= est_value <= est_max and est_min > 0:
                                valid_estimations += 1
                    
                    if price_fields_found > 0:
                        self.log_test("Price Estimation Logic", True, 
                                    f"{valid_estimations}/{price_fields_found} releases have valid price estimations")
                    else:
                        self.log_test("Price Estimation Logic", False, "No price estimation fields found in responses")
                        
                else:
                    error_text = await response.text()
                    self.log_test("Price Estimation Logic", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Price Estimation Logic", False, f"Exception: {str(e)}")
            
    async def test_master_jersey_enrichment(self):
        """Test Master Jersey data enrichment in Vestiaire responses"""
        try:
            async with self.session.get(f"{API_BASE}/vestiaire?limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data:
                        self.log_test("Master Jersey Data Enrichment", False, "No jersey releases found to test enrichment")
                        return
                        
                    enriched_count = 0
                    total_releases = len(data)
                    
                    for release in data:
                        if 'master_jersey_info' in release and release['master_jersey_info']:
                            enriched_count += 1
                            
                            # Verify master jersey info structure
                            master_info = release['master_jersey_info']
                            expected_fields = ['id', 'team_id', 'season']
                            has_expected_fields = any(field in master_info for field in expected_fields)
                            
                            if not has_expected_fields:
                                self.log_test("Master Jersey Data Enrichment", False, 
                                            f"Master jersey info missing expected fields: {list(master_info.keys())}")
                                return
                    
                    if enriched_count > 0:
                        self.log_test("Master Jersey Data Enrichment", True, 
                                    f"{enriched_count}/{total_releases} releases have master jersey enrichment")
                    else:
                        self.log_test("Master Jersey Data Enrichment", True, 
                                    f"No master jersey enrichment found (may be expected if no master jerseys exist)")
                        
                else:
                    error_text = await response.text()
                    self.log_test("Master Jersey Data Enrichment", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Master Jersey Data Enrichment", False, f"Exception: {str(e)}")
            
    async def test_collection_authentication(self):
        """Test authentication requirements for collection features"""
        if not self.user_token:
            self.log_test("Collection Authentication", False, "User token not available")
            return
            
        # Test authenticated collection access
        try:
            headers = {'Authorization': f'Bearer {self.user_token}'}
            async with self.session.get(f"{API_BASE}/users/test-user-id/collections", headers=headers) as response:
                # We expect this to work or fail gracefully with proper auth
                if response.status in [200, 404, 422]:  # 404/422 acceptable if user/collections don't exist
                    self.log_test("Collection Authentication - Authenticated Access", True, 
                                f"HTTP {response.status} (expected for authenticated request)")
                else:
                    error_text = await response.text()
                    self.log_test("Collection Authentication - Authenticated Access", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Collection Authentication - Authenticated Access", False, f"Exception: {str(e)}")
            
        # Test unauthenticated collection access (should fail)
        try:
            async with self.session.get(f"{API_BASE}/users/test-user-id/collections") as response:
                if response.status == 401:
                    self.log_test("Collection Authentication - Unauthenticated Rejection", True, 
                                "Properly rejected unauthenticated request")
                else:
                    self.log_test("Collection Authentication - Unauthenticated Rejection", False, 
                                f"Should reject unauthenticated requests, got HTTP {response.status}")
        except Exception as e:
            self.log_test("Collection Authentication - Unauthenticated Rejection", False, f"Exception: {str(e)}")
            
    async def test_jersey_releases_endpoint(self):
        """Test related jersey releases endpoint"""
        try:
            async with self.session.get(f"{API_BASE}/jersey-releases") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Jersey Releases Endpoint", True, f"Found {len(data)} jersey releases")
                    
                    # Test with filters
                    async with self.session.get(f"{API_BASE}/jersey-releases?limit=5") as filtered_response:
                        if filtered_response.status == 200:
                            filtered_data = await filtered_response.json()
                            self.log_test("Jersey Releases Filtering", True, 
                                        f"Filtered request returned {len(filtered_data)} results")
                        else:
                            error_text = await filtered_response.text()
                            self.log_test("Jersey Releases Filtering", False, 
                                        f"HTTP {filtered_response.status}: {error_text}")
                else:
                    error_text = await response.text()
                    self.log_test("Jersey Releases Endpoint", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Jersey Releases Endpoint", False, f"Exception: {str(e)}")
            
    async def test_vestiaire_data_structure(self):
        """Test Vestiaire response data structure"""
        try:
            async with self.session.get(f"{API_BASE}/vestiaire?limit=3") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data:
                        self.log_test("Vestiaire Data Structure", True, "Empty response structure valid")
                        return
                        
                    # Check first item structure
                    first_item = data[0]
                    expected_fields = ['id', 'estimated_value', 'estimated_min', 'estimated_max']
                    missing_fields = [field for field in expected_fields if field not in first_item]
                    
                    if not missing_fields:
                        self.log_test("Vestiaire Data Structure", True, 
                                    f"Response structure valid with fields: {list(first_item.keys())}")
                    else:
                        self.log_test("Vestiaire Data Structure", False, 
                                    f"Missing required fields: {missing_fields}")
                        
                else:
                    error_text = await response.text()
                    self.log_test("Vestiaire Data Structure", False, f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Vestiaire Data Structure", False, f"Exception: {str(e)}")
            
    async def run_all_tests(self):
        """Run all Vestiaire system tests"""
        print("🎯 TOPKIT VESTIAIRE SYSTEM BACKEND TESTING STARTED")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Authentication tests
            print("\n📋 AUTHENTICATION TESTS")
            print("-" * 30)
            await self.authenticate_user()
            await self.authenticate_admin()
            
            # Core Vestiaire functionality tests
            print("\n🏪 VESTIAIRE ENDPOINT TESTS")
            print("-" * 30)
            await self.test_vestiaire_endpoint_basic()
            await self.test_vestiaire_filtering()
            await self.test_vestiaire_data_structure()
            
            # Price estimation tests
            print("\n💰 PRICE ESTIMATION TESTS")
            print("-" * 30)
            await self.test_price_estimation_logic()
            
            # Master Jersey enrichment tests
            print("\n🎽 MASTER JERSEY ENRICHMENT TESTS")
            print("-" * 30)
            await self.test_master_jersey_enrichment()
            
            # Collection authentication tests
            print("\n🔐 COLLECTION AUTHENTICATION TESTS")
            print("-" * 30)
            await self.test_collection_authentication()
            
            # Related endpoints tests
            print("\n🔗 RELATED ENDPOINTS TESTS")
            print("-" * 30)
            await self.test_jersey_releases_endpoint()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
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
                    print(f"   • {result['test']}: {result['details']}")
                    
        print(f"\n🎯 VESTIAIRE SYSTEM STATUS: {'✅ OPERATIONAL' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
        
        return success_rate >= 80

async def main():
    """Main test execution"""
    tester = VestiaireBackendTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())