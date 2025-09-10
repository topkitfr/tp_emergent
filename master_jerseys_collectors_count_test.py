#!/usr/bin/env python3
"""
Master Jerseys Collectors Count Testing
======================================

This test verifies that the collectors_count field in master jerseys endpoints
is now being calculated correctly instead of being hardcoded to 0.

Test Details:
- Test GET /api/master-jerseys endpoint
- Check that collectors_count field is present in the response 
- Verify that collectors_count reflects actual count of users who have personal_kits 
  that reference reference_kits belonging to each master jersey
- Test individual master jersey endpoint GET /api/master-jerseys/{id} as well
- If there are no actual collectors in the database, create some test data to verify the calculation works

Authentication: Use admin credentials topkitfr@gmail.com / TopKitSecure789#
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://kitfix-contrib.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class MasterJerseysCollectorsCountTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.created_test_data = []  # Track created test data for cleanup
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()
        
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get('token')
                    
                    if self.auth_token:
                        self.log_result(
                            "Admin Authentication",
                            True,
                            f"Successfully authenticated admin user",
                            {
                                "email": ADMIN_EMAIL,
                                "token_length": len(self.auth_token),
                                "user_name": data.get('user', {}).get('name', 'Unknown')
                            }
                        )
                        return True
                    else:
                        self.log_result("Admin Authentication", False, "No access token received")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Authentication", 
                        False, 
                        f"Authentication failed with status {response.status}",
                        {"error": error_text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
            
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_master_jerseys_list_endpoint(self) -> bool:
        """Test 1: Verify GET /api/master-jerseys endpoint includes collectors_count"""
        try:
            async with self.session.get(
                f"{API_BASE}/master-jerseys",
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        # Check first master jersey for collectors_count field
                        first_jersey = data[0]
                        
                        has_collectors_count = 'collectors_count' in first_jersey
                        collectors_count_value = first_jersey.get('collectors_count', 'NOT_FOUND')
                        
                        # Check all master jerseys for collectors_count
                        all_have_collectors_count = all('collectors_count' in jersey for jersey in data)
                        collectors_counts = [jersey.get('collectors_count', 0) for jersey in data]
                        
                        self.log_result(
                            "Master Jerseys List Endpoint",
                            has_collectors_count and all_have_collectors_count,
                            f"Found {len(data)} master jerseys, collectors_count field present: {all_have_collectors_count}",
                            {
                                "total_master_jerseys": len(data),
                                "first_jersey_collectors_count": collectors_count_value,
                                "all_collectors_counts": collectors_counts,
                                "all_have_field": all_have_collectors_count,
                                "sample_jersey_id": first_jersey.get('id', 'N/A'),
                                "sample_jersey_topkit_ref": first_jersey.get('topkit_reference', 'N/A')
                            }
                        )
                        
                        return has_collectors_count and all_have_collectors_count
                    else:
                        self.log_result(
                            "Master Jerseys List Endpoint",
                            False,
                            f"No master jerseys found in response",
                            {"response_data": data}
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Master Jerseys List Endpoint",
                        False,
                        f"Request failed with status {response.status}",
                        {"error": error_text}
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Master Jerseys List Endpoint",
                False,
                f"Test failed with exception: {str(e)}"
            )
            return False
            
    async def test_individual_master_jersey_endpoint(self) -> bool:
        """Test 2: Verify GET /api/master-jerseys/{id} endpoint includes collectors_count"""
        try:
            # First get list of master jerseys to get an ID
            async with self.session.get(
                f"{API_BASE}/master-jerseys",
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        # Test the first master jersey
                        test_jersey_id = data[0].get('id')
                        
                        if test_jersey_id:
                            # Test individual endpoint
                            async with self.session.get(
                                f"{API_BASE}/master-jerseys/{test_jersey_id}",
                                headers=self.get_auth_headers()
                            ) as individual_response:
                                
                                if individual_response.status == 200:
                                    individual_data = await individual_response.json()
                                    
                                    has_collectors_count = 'collectors_count' in individual_data
                                    collectors_count_value = individual_data.get('collectors_count', 'NOT_FOUND')
                                    
                                    self.log_result(
                                        "Individual Master Jersey Endpoint",
                                        has_collectors_count,
                                        f"Individual master jersey endpoint includes collectors_count: {has_collectors_count}",
                                        {
                                            "jersey_id": test_jersey_id,
                                            "collectors_count": collectors_count_value,
                                            "topkit_reference": individual_data.get('topkit_reference', 'N/A'),
                                            "team_name": individual_data.get('team_name', 'N/A'),
                                            "season": individual_data.get('season', 'N/A')
                                        }
                                    )
                                    
                                    return has_collectors_count
                                else:
                                    error_text = await individual_response.text()
                                    self.log_result(
                                        "Individual Master Jersey Endpoint",
                                        False,
                                        f"Individual request failed with status {individual_response.status}",
                                        {"error": error_text, "jersey_id": test_jersey_id}
                                    )
                                    return False
                        else:
                            self.log_result(
                                "Individual Master Jersey Endpoint",
                                False,
                                "No jersey ID found in master jerseys list"
                            )
                            return False
                    else:
                        self.log_result(
                            "Individual Master Jersey Endpoint",
                            False,
                            "No master jerseys available for individual testing"
                        )
                        return False
                else:
                    self.log_result(
                        "Individual Master Jersey Endpoint",
                        False,
                        f"Failed to get master jerseys list for individual testing: {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Individual Master Jersey Endpoint",
                False,
                f"Test failed with exception: {str(e)}"
            )
            return False
            
    async def get_current_database_state(self) -> Dict[str, Any]:
        """Get current state of database for analysis"""
        try:
            state = {}
            
            # Get master jerseys
            async with self.session.get(f"{API_BASE}/master-jerseys", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    state['master_jerseys'] = await response.json()
                else:
                    state['master_jerseys'] = []
                    
            # Get reference kits
            async with self.session.get(f"{API_BASE}/reference-kits", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    state['reference_kits'] = await response.json()
                else:
                    state['reference_kits'] = []
                    
            # Get personal kits
            async with self.session.get(f"{API_BASE}/personal-kits", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    state['personal_kits'] = await response.json()
                else:
                    state['personal_kits'] = []
                    
            return state
            
        except Exception as e:
            print(f"Error getting database state: {e}")
            return {}
            
    async def create_test_data_for_collectors_count(self) -> bool:
        """Create test data to verify collectors_count calculation works"""
        try:
            # Get current state
            current_state = await self.get_current_database_state()
            
            master_jerseys = current_state.get('master_jerseys', [])
            reference_kits = current_state.get('reference_kits', [])
            personal_kits = current_state.get('personal_kits', [])
            
            self.log_result(
                "Database State Analysis",
                True,
                "Current database state retrieved",
                {
                    "master_jerseys_count": len(master_jerseys),
                    "reference_kits_count": len(reference_kits),
                    "personal_kits_count": len(personal_kits)
                }
            )
            
            # If we have master jerseys and reference kits, try to create personal kits
            if master_jerseys and reference_kits:
                # Find a reference kit that belongs to a master jersey
                target_reference_kit = None
                target_master_jersey = None
                
                for ref_kit in reference_kits:
                    master_kit_id = ref_kit.get('master_kit_id')
                    if master_kit_id:
                        # Find corresponding master jersey
                        for master_jersey in master_jerseys:
                            if master_jersey.get('id') == master_kit_id:
                                target_reference_kit = ref_kit
                                target_master_jersey = master_jersey
                                break
                        if target_reference_kit:
                            break
                
                if target_reference_kit and target_master_jersey:
                    # Create a personal kit that references this reference kit
                    personal_kit_data = {
                        "reference_kit_id": target_reference_kit['id'],
                        "size": "M",
                        "condition": "mint",
                        "acquisition_date": "2024-01-15",
                        "purchase_price": 120.0,
                        "personal_notes": "Test personal kit for collectors count verification"
                    }
                    
                    async with self.session.post(
                        f"{API_BASE}/personal-kits",
                        json=personal_kit_data,
                        headers=self.get_auth_headers()
                    ) as response:
                        
                        if response.status in [200, 201]:
                            created_kit = await response.json()
                            self.created_test_data.append(('personal_kit', created_kit.get('id')))
                            
                            self.log_result(
                                "Test Data Creation",
                                True,
                                "Successfully created test personal kit",
                                {
                                    "personal_kit_id": created_kit.get('id'),
                                    "reference_kit_id": target_reference_kit['id'],
                                    "master_jersey_id": target_master_jersey['id'],
                                    "master_jersey_ref": target_master_jersey.get('topkit_reference', 'N/A')
                                }
                            )
                            return True
                        else:
                            error_text = await response.text()
                            self.log_result(
                                "Test Data Creation",
                                False,
                                f"Failed to create personal kit: {response.status}",
                                {"error": error_text}
                            )
                            return False
                else:
                    self.log_result(
                        "Test Data Creation",
                        False,
                        "No suitable reference kit found that belongs to a master jersey"
                    )
                    return False
            else:
                self.log_result(
                    "Test Data Creation",
                    False,
                    "Insufficient data in database to create test collectors",
                    {
                        "master_jerseys_available": len(master_jerseys),
                        "reference_kits_available": len(reference_kits)
                    }
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Test Data Creation",
                False,
                f"Failed to create test data: {str(e)}"
            )
            return False
            
    async def verify_collectors_count_calculation(self) -> bool:
        """Test 3: Verify that collectors_count reflects actual personal kit ownership"""
        try:
            # Get current state after potential test data creation
            current_state = await self.get_current_database_state()
            
            master_jerseys = current_state.get('master_jerseys', [])
            reference_kits = current_state.get('reference_kits', [])
            personal_kits = current_state.get('personal_kits', [])
            
            # Calculate expected collectors count for each master jersey
            expected_counts = {}
            
            for master_jersey in master_jerseys:
                master_jersey_id = master_jersey.get('id')
                expected_counts[master_jersey_id] = 0
                
                # Find reference kits that belong to this master jersey
                related_reference_kits = [
                    rk for rk in reference_kits 
                    if rk.get('master_kit_id') == master_jersey_id
                ]
                
                # Count personal kits that reference these reference kits
                for ref_kit in related_reference_kits:
                    ref_kit_id = ref_kit.get('id')
                    personal_kits_for_ref = [
                        pk for pk in personal_kits 
                        if pk.get('reference_kit_id') == ref_kit_id
                    ]
                    expected_counts[master_jersey_id] += len(personal_kits_for_ref)
            
            # Now test the actual API response
            async with self.session.get(
                f"{API_BASE}/master-jerseys",
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    api_master_jerseys = await response.json()
                    
                    calculation_correct = True
                    verification_details = {}
                    
                    for api_jersey in api_master_jerseys:
                        jersey_id = api_jersey.get('id')
                        api_collectors_count = api_jersey.get('collectors_count', 0)
                        expected_count = expected_counts.get(jersey_id, 0)
                        
                        is_correct = api_collectors_count == expected_count
                        if not is_correct:
                            calculation_correct = False
                            
                        verification_details[f"jersey_{jersey_id}"] = {
                            "topkit_reference": api_jersey.get('topkit_reference', 'N/A'),
                            "api_collectors_count": api_collectors_count,
                            "expected_count": expected_count,
                            "correct": is_correct
                        }
                    
                    self.log_result(
                        "Collectors Count Calculation Verification",
                        calculation_correct,
                        f"Collectors count calculation accuracy: {calculation_correct}",
                        {
                            "total_master_jerseys_tested": len(api_master_jerseys),
                            "calculation_details": verification_details,
                            "total_personal_kits": len(personal_kits),
                            "total_reference_kits": len(reference_kits)
                        }
                    )
                    
                    return calculation_correct
                else:
                    self.log_result(
                        "Collectors Count Calculation Verification",
                        False,
                        f"Failed to get master jerseys for verification: {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_result(
                "Collectors Count Calculation Verification",
                False,
                f"Verification failed with exception: {str(e)}"
            )
            return False
            
    async def cleanup_test_data(self):
        """Clean up any test data created during testing"""
        try:
            for data_type, data_id in self.created_test_data:
                if data_type == 'personal_kit':
                    async with self.session.delete(
                        f"{API_BASE}/personal-kits/{data_id}",
                        headers=self.get_auth_headers()
                    ) as response:
                        if response.status in [200, 204]:
                            print(f"✅ Cleaned up test personal kit: {data_id}")
                        else:
                            print(f"⚠️ Failed to clean up test personal kit: {data_id}")
                            
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
            
    async def run_all_tests(self):
        """Run all master jerseys collectors count tests"""
        print("🧪 Starting Master Jerseys Collectors Count Testing")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Step 1: Authenticate
            if not await self.authenticate_admin():
                print("❌ Authentication failed - cannot proceed with tests")
                return
            
            # Step 2: Test master jerseys list endpoint
            list_test_passed = await self.test_master_jerseys_list_endpoint()
            
            # Step 3: Test individual master jersey endpoint
            individual_test_passed = await self.test_individual_master_jersey_endpoint()
            
            # Step 4: Create test data if needed and verify calculation
            test_data_created = await self.create_test_data_for_collectors_count()
            calculation_test_passed = await self.verify_collectors_count_calculation()
            
            # Summary
            print("\n" + "=" * 60)
            print("🏁 TEST SUMMARY")
            print("=" * 60)
            
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results if result['success'])
            
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
            
            print("\nDetailed Results:")
            for result in self.test_results:
                status = "✅" if result['success'] else "❌"
                print(f"{status} {result['test']}: {result['message']}")
            
            # Overall assessment
            critical_tests_passed = list_test_passed and individual_test_passed and calculation_test_passed
            
            if critical_tests_passed:
                print("\n🎉 COLLECTORS COUNT FUNCTIONALITY: WORKING CORRECTLY!")
                print("✅ Master jerseys endpoints include collectors_count field")
                print("✅ Collectors count calculation is accurate")
                print("✅ Both list and individual endpoints working properly")
            else:
                print("\n🚨 COLLECTORS COUNT FUNCTIONALITY: ISSUES DETECTED!")
                if not list_test_passed:
                    print("❌ Master jerseys list endpoint missing collectors_count")
                if not individual_test_passed:
                    print("❌ Individual master jersey endpoint missing collectors_count")
                if not calculation_test_passed:
                    print("❌ Collectors count calculation is incorrect")
            
        finally:
            # Cleanup
            await self.cleanup_test_data()
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = MasterJerseysCollectorsCountTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())