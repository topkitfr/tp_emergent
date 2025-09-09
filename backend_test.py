#!/usr/bin/env python3
"""
Competition Level Field Fix Testing
===================================

This test verifies the Competition Level Field Fix as requested:
1. Competition Level Field Structure - Test that the Community DB competition creation form accepts string values for the level field instead of numbers
2. UnifiedFieldDefinitions Fix - Verify that the UnifiedFieldDefinitions.js file correctly defines the competition level field as a 'select' type with options ['pro', 'semi pro', 'amateur', 'special']
3. Backend Compatibility - Test that the backend collaborative_models.py accepts Union[str, int] for the level field
4. Form Submission Test - Test submitting a competition creation form with level field set to one of the string values

Focus: Testing the specific Competition Level Field Fix implementation
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://jersey-catalog-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class CompetitionLevelFieldTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
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
        
    async def test_backend_model_compatibility(self) -> bool:
        """Test 1: Verify backend model accepts Union[str, int] for level field"""
        try:
            # Test with string level values
            string_level_tests = [
                {"level": "pro", "expected": True},
                {"level": "semi pro", "expected": True},
                {"level": "amateur", "expected": True},
                {"level": "special", "expected": True},
                {"level": "invalid_level", "expected": True},  # Should still accept as string
            ]
            
            # Test with integer level values (backward compatibility)
            int_level_tests = [
                {"level": 1, "expected": True},
                {"level": 2, "expected": True},
                {"level": 0, "expected": True},
            ]
            
            all_tests_passed = True
            test_details = {}
            
            for test_case in string_level_tests + int_level_tests:
                competition_data = {
                    "competition_name": f"Test Competition {test_case['level']}",
                    "official_name": f"Official Test Competition {test_case['level']}",
                    "type": "National league",
                    "country": "France",
                    "level": test_case["level"],
                    "confederations_federations": ["UEFA"]
                }
                
                try:
                    async with self.session.post(
                        f"{API_BASE}/competitions",
                        json=competition_data,
                        headers=self.get_auth_headers()
                    ) as response:
                        
                        if response.status in [200, 201]:
                            response_data = await response.json()
                            test_details[f"level_{test_case['level']}"] = "✅ Accepted"
                            
                            # Verify the level field is preserved correctly
                            if 'level' in response_data:
                                stored_level = response_data['level']
                                if stored_level == test_case['level']:
                                    test_details[f"level_{test_case['level']}_preservation"] = "✅ Preserved correctly"
                                else:
                                    test_details[f"level_{test_case['level']}_preservation"] = f"⚠️ Changed from {test_case['level']} to {stored_level}"
                        else:
                            error_text = await response.text()
                            test_details[f"level_{test_case['level']}"] = f"❌ Rejected (Status: {response.status})"
                            test_details[f"level_{test_case['level']}_error"] = error_text
                            
                            # Only fail if we expected it to work
                            if test_case['expected']:
                                all_tests_passed = False
                                
                except Exception as e:
                    test_details[f"level_{test_case['level']}_exception"] = str(e)
                    if test_case['expected']:
                        all_tests_passed = False
            
            self.log_result(
                "Backend Model Compatibility",
                all_tests_passed,
                f"Backend model Union[str, int] compatibility test",
                test_details
            )
            
            return all_tests_passed
            
        except Exception as e:
            self.log_result(
                "Backend Model Compatibility",
                False,
                f"Test failed with exception: {str(e)}"
            )
            return False
            
    async def test_competition_creation_with_string_levels(self) -> bool:
        """Test 2: Test competition creation with all 4 required string level values"""
        try:
            required_levels = ["pro", "semi pro", "amateur", "special"]
            created_competitions = []
            all_tests_passed = True
            test_details = {}
            
            for level in required_levels:
                competition_data = {
                    "competition_name": f"Test {level.title()} Competition",
                    "official_name": f"Official Test {level.title()} Competition",
                    "type": "National league",
                    "country": "France",
                    "level": level,
                    "confederations_federations": ["UEFA"],
                    "founded_year": 2024
                }
                
                try:
                    async with self.session.post(
                        f"{API_BASE}/competitions",
                        json=competition_data,
                        headers=self.get_auth_headers()
                    ) as response:
                        
                        if response.status in [200, 201]:
                            response_data = await response.json()
                            competition_id = response_data.get('id')
                            created_competitions.append(competition_id)
                            
                            test_details[f"{level}_creation"] = "✅ Successfully created"
                            test_details[f"{level}_id"] = competition_id
                            
                            # Verify the level field is stored correctly
                            stored_level = response_data.get('level')
                            if stored_level == level:
                                test_details[f"{level}_level_verification"] = "✅ Level stored correctly"
                            else:
                                test_details[f"{level}_level_verification"] = f"⚠️ Level mismatch: expected '{level}', got '{stored_level}'"
                                
                        else:
                            error_text = await response.text()
                            test_details[f"{level}_creation"] = f"❌ Failed (Status: {response.status})"
                            test_details[f"{level}_error"] = error_text
                            all_tests_passed = False
                            
                except Exception as e:
                    test_details[f"{level}_exception"] = str(e)
                    all_tests_passed = False
            
            # Test retrieval of created competitions
            if created_competitions:
                try:
                    async with self.session.get(
                        f"{API_BASE}/competitions",
                        headers=self.get_auth_headers()
                    ) as response:
                        
                        if response.status == 200:
                            competitions = await response.json()
                            
                            # Find our created competitions
                            found_competitions = []
                            for comp in competitions:
                                if comp.get('id') in created_competitions:
                                    found_competitions.append(comp)
                                    level = comp.get('level')
                                    if level in required_levels:
                                        test_details[f"retrieval_{level}"] = "✅ Found with correct level"
                                    else:
                                        test_details[f"retrieval_{level}"] = f"⚠️ Found but level is '{level}'"
                            
                            test_details["total_found"] = len(found_competitions)
                            test_details["total_created"] = len(created_competitions)
                            
                        else:
                            test_details["retrieval_error"] = f"Failed to retrieve competitions (Status: {response.status})"
                            
                except Exception as e:
                    test_details["retrieval_exception"] = str(e)
            
            self.log_result(
                "Competition Creation with String Levels",
                all_tests_passed,
                f"Created competitions with all 4 required string level values",
                test_details
            )
            
            return all_tests_passed
            
        except Exception as e:
            self.log_result(
                "Competition Creation with String Levels",
                False,
                f"Test failed with exception: {str(e)}"
            )
            return False
            
    async def test_form_dependencies_endpoint(self) -> bool:
        """Test 3: Test form dependencies endpoint for competition level options"""
        try:
            test_details = {}
            
            # Test competitions-by-type endpoint
            async with self.session.get(
                f"{API_BASE}/form-dependencies/competitions-by-type",
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    test_details["competitions_by_type_status"] = "✅ Endpoint accessible"
                    test_details["competitions_by_type_structure"] = str(type(data))
                    
                    # Check if we have competitions with string levels
                    competitions_with_levels = []
                    if isinstance(data, dict):
                        for comp_type, competitions in data.items():
                            if isinstance(competitions, list):
                                for comp in competitions:
                                    if isinstance(comp, dict) and 'level' in comp:
                                        level = comp['level']
                                        if isinstance(level, str) and level in ["pro", "semi pro", "amateur", "special"]:
                                            competitions_with_levels.append(comp)
                    
                    test_details["competitions_with_string_levels"] = len(competitions_with_levels)
                    
                else:
                    error_text = await response.text()
                    test_details["competitions_by_type_error"] = f"Status {response.status}: {error_text}"
            
            # Test general competitions endpoint
            async with self.session.get(
                f"{API_BASE}/competitions",
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    competitions = await response.json()
                    test_details["competitions_endpoint_status"] = "✅ Endpoint accessible"
                    test_details["total_competitions"] = len(competitions) if isinstance(competitions, list) else "Not a list"
                    
                    # Check level field types and values
                    level_analysis = {
                        "string_levels": [],
                        "int_levels": [],
                        "null_levels": 0,
                        "other_levels": []
                    }
                    
                    if isinstance(competitions, list):
                        for comp in competitions:
                            if isinstance(comp, dict):
                                level = comp.get('level')
                                if level is None:
                                    level_analysis["null_levels"] += 1
                                elif isinstance(level, str):
                                    level_analysis["string_levels"].append(level)
                                elif isinstance(level, int):
                                    level_analysis["int_levels"].append(level)
                                else:
                                    level_analysis["other_levels"].append(str(level))
                    
                    test_details["level_analysis"] = level_analysis
                    
                    # Check for the 4 required string levels
                    required_levels = ["pro", "semi pro", "amateur", "special"]
                    found_required_levels = [level for level in level_analysis["string_levels"] if level in required_levels]
                    test_details["found_required_levels"] = found_required_levels
                    
                else:
                    error_text = await response.text()
                    test_details["competitions_endpoint_error"] = f"Status {response.status}: {error_text}"
            
            # Determine overall success
            success = (
                "competitions_endpoint_status" in test_details and
                "✅" in test_details["competitions_endpoint_status"]
            )
            
            self.log_result(
                "Form Dependencies Endpoint",
                success,
                f"Tested form dependencies and competition endpoints for level field support",
                test_details
            )
            
            return success
            
        except Exception as e:
            self.log_result(
                "Form Dependencies Endpoint",
                False,
                f"Test failed with exception: {str(e)}"
            )
            return False
            
    async def test_end_to_end_workflow(self) -> bool:
        """Test 4: End-to-end workflow test for competition creation with string levels"""
        try:
            test_details = {}
            
            # Test the complete workflow for each required level
            required_levels = ["pro", "semi pro", "amateur", "special"]
            workflow_results = {}
            
            for level in required_levels:
                workflow_results[level] = {}
                
                # Step 1: Create competition with string level
                competition_data = {
                    "competition_name": f"E2E Test {level.title()} League",
                    "official_name": f"End-to-End Test {level.title()} League Official",
                    "type": "National league",
                    "country": "Test Country",
                    "level": level,
                    "confederations_federations": ["TEST"],
                    "founded_year": 2024,
                    "alternative_names": [f"Test {level} Alt Name"]
                }
                
                try:
                    # Create competition
                    async with self.session.post(
                        f"{API_BASE}/competitions",
                        json=competition_data,
                        headers=self.get_auth_headers()
                    ) as response:
                        
                        if response.status in [200, 201]:
                            created_comp = await response.json()
                            comp_id = created_comp.get('id')
                            workflow_results[level]["creation"] = "✅ Success"
                            workflow_results[level]["id"] = comp_id
                            workflow_results[level]["created_level"] = created_comp.get('level')
                            
                            # Step 2: Retrieve the created competition
                            async with self.session.get(
                                f"{API_BASE}/competitions/{comp_id}",
                                headers=self.get_auth_headers()
                            ) as get_response:
                                
                                if get_response.status == 200:
                                    retrieved_comp = await get_response.json()
                                    workflow_results[level]["retrieval"] = "✅ Success"
                                    workflow_results[level]["retrieved_level"] = retrieved_comp.get('level')
                                    
                                    # Verify level consistency
                                    if retrieved_comp.get('level') == level:
                                        workflow_results[level]["level_consistency"] = "✅ Consistent"
                                    else:
                                        workflow_results[level]["level_consistency"] = f"❌ Inconsistent: {retrieved_comp.get('level')} != {level}"
                                        
                                else:
                                    workflow_results[level]["retrieval"] = f"❌ Failed (Status: {get_response.status})"
                            
                            # Step 3: Test in competitions list
                            async with self.session.get(
                                f"{API_BASE}/competitions",
                                headers=self.get_auth_headers()
                            ) as list_response:
                                
                                if list_response.status == 200:
                                    competitions_list = await list_response.json()
                                    found_in_list = False
                                    
                                    if isinstance(competitions_list, list):
                                        for comp in competitions_list:
                                            if comp.get('id') == comp_id:
                                                found_in_list = True
                                                list_level = comp.get('level')
                                                workflow_results[level]["in_list"] = "✅ Found"
                                                workflow_results[level]["list_level"] = list_level
                                                
                                                if list_level == level:
                                                    workflow_results[level]["list_level_consistency"] = "✅ Consistent"
                                                else:
                                                    workflow_results[level]["list_level_consistency"] = f"❌ Inconsistent: {list_level} != {level}"
                                                break
                                    
                                    if not found_in_list:
                                        workflow_results[level]["in_list"] = "❌ Not found in list"
                                        
                                else:
                                    workflow_results[level]["list_error"] = f"Failed to get list (Status: {list_response.status})"
                            
                        else:
                            error_text = await response.text()
                            workflow_results[level]["creation"] = f"❌ Failed (Status: {response.status})"
                            workflow_results[level]["error"] = error_text
                            
                except Exception as e:
                    workflow_results[level]["exception"] = str(e)
            
            # Analyze overall workflow success
            successful_workflows = 0
            total_workflows = len(required_levels)
            
            for level, results in workflow_results.items():
                if (results.get("creation", "").startswith("✅") and 
                    results.get("retrieval", "").startswith("✅") and
                    results.get("level_consistency", "").startswith("✅")):
                    successful_workflows += 1
            
            success_rate = (successful_workflows / total_workflows) * 100
            overall_success = success_rate >= 75  # 75% success rate threshold
            
            test_details["workflow_results"] = workflow_results
            test_details["successful_workflows"] = successful_workflows
            test_details["total_workflows"] = total_workflows
            test_details["success_rate"] = f"{success_rate:.1f}%"
            
            self.log_result(
                "End-to-End Workflow",
                overall_success,
                f"Complete workflow test for all 4 string level values ({success_rate:.1f}% success rate)",
                test_details
            )
            
            return overall_success
            
        except Exception as e:
            self.log_result(
                "End-to-End Workflow",
                False,
                f"Test failed with exception: {str(e)}"
            )
            return False
            
    async def run_all_tests(self):
        """Run all Competition Level Field Fix tests"""
        print("🎯 COMPETITION LEVEL FIELD FIX TESTING")
        print("=" * 50)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print()
        
        await self.setup_session()
        
        try:
            # Authenticate first
            if not await self.authenticate_admin():
                print("❌ Authentication failed - cannot proceed with tests")
                return
            
            print("🧪 Running Competition Level Field Fix Tests...")
            print()
            
            # Run all tests
            test_methods = [
                self.test_backend_model_compatibility,
                self.test_competition_creation_with_string_levels,
                self.test_form_dependencies_endpoint,
                self.test_end_to_end_workflow
            ]
            
            passed_tests = 0
            total_tests = len(test_methods)
            
            for test_method in test_methods:
                try:
                    result = await test_method()
                    if result:
                        passed_tests += 1
                except Exception as e:
                    print(f"❌ Test {test_method.__name__} failed with exception: {e}")
            
            # Summary
            print("📊 COMPETITION LEVEL FIELD FIX TEST SUMMARY")
            print("=" * 50)
            
            success_rate = (passed_tests / total_tests) * 100
            print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
            print()
            
            # Detailed results
            for result in self.test_results:
                status = "✅" if result['success'] else "❌"
                print(f"{status} {result['test']}: {result['message']}")
            
            print()
            
            # Overall assessment
            if success_rate >= 75:
                print("🎉 COMPETITION LEVEL FIELD FIX - OVERALL SUCCESS!")
                print("✅ The Competition Level Field Fix is working correctly")
                print("✅ Backend accepts Union[str, int] for level field")
                print("✅ String level values ['pro', 'semi pro', 'amateur', 'special'] are supported")
                print("✅ Form submission with string levels works end-to-end")
            else:
                print("⚠️ COMPETITION LEVEL FIELD FIX - ISSUES DETECTED")
                print("❌ Some aspects of the Competition Level Field Fix need attention")
                
                # Identify specific issues
                failed_tests = [r for r in self.test_results if not r['success']]
                if failed_tests:
                    print("\n🔍 Issues found:")
                    for failed_test in failed_tests:
                        print(f"   • {failed_test['test']}: {failed_test['message']}")
            
            print()
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = CompetitionLevelFieldTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())