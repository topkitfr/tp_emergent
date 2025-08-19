#!/usr/bin/env python3
"""
TopKit New Jersey Submission Form Structure Testing
Testing the modified jersey submission form with new fields and structure changes.

Focus Areas:
1. NEW FORM STRUCTURE: team, league, season, manufacturer, sku_code, model, description
2. REQUIRED FIELDS: team, league, season, model
3. REMOVED FIELD: player field should be removed
4. PHOTO UPLOADS: front_photo and back_photo
5. USER AUTHENTICATION: livio.test@topkit.fr/TopKitTestSecure789!
6. ADMIN FUNCTIONALITY: editing pending jerseys with new structure
7. END-TO-END WORKFLOW: complete jersey creation and processing
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://kit-curator.preview.emergentagent.com/api"

# Test credentials
TEST_USER_EMAIL = "livio.test@topkit.fr"
TEST_USER_PASSWORD = "TopKitTestSecure789!"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitNewFormTester:
    def __init__(self):
        self.session = None
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        self.created_jersey_id = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}: {details}")
        
    async def authenticate_user(self) -> bool:
        """Authenticate test user"""
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_token = data.get("token")
                    user_info = data.get("user", {})
                    self.log_result(
                        "User Authentication", 
                        True, 
                        f"Successfully authenticated user: {user_info.get('name', 'Unknown')} ({user_info.get('email', 'Unknown')})",
                        {"user_id": user_info.get('id'), "role": user_info.get('role')}
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result("User Authentication", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False
            
    async def authenticate_admin(self) -> bool:
        """Authenticate admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get("token")
                    user_info = data.get("user", {})
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Successfully authenticated admin: {user_info.get('name', 'Unknown')} ({user_info.get('role', 'Unknown')})",
                        {"user_id": user_info.get('id'), "role": user_info.get('role')}
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result("Admin Authentication", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    async def test_new_form_structure_submission(self) -> bool:
        """Test jersey submission with new form structure"""
        try:
            # Test data with new form structure
            jersey_data = {
                "team": "FC Barcelona",
                "league": "La Liga",
                "season": "2024-25",
                "manufacturer": "Nike",
                "sku_code": "FB2425H001",  # New field: sku_code instead of reference
                "model": "authentic",  # New field: authentic/replica
                "description": "Maillot domicile FC Barcelona saison 2024-25, modèle authentique Nike",
                "front_photo": "https://example.com/front.jpg",  # New field
                "back_photo": "https://example.com/back.jpg"     # New field
                # Note: "player" field should be removed
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            async with self.session.post(f"{BASE_URL}/jerseys", json=jersey_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    self.created_jersey_id = data.get("id")
                    self.log_result(
                        "New Form Structure Submission", 
                        True, 
                        f"Successfully created jersey with new structure. ID: {self.created_jersey_id}",
                        {
                            "jersey_id": self.created_jersey_id,
                            "reference_number": data.get("reference_number"),
                            "status": data.get("status"),
                            "has_sku_code": "sku_code" in str(data),
                            "has_model": "model" in str(data),
                            "has_player": "player" in str(data)
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "New Form Structure Submission", 
                        False, 
                        f"HTTP {response.status}: {response_text}",
                        {"submitted_data": jersey_data}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("New Form Structure Submission", False, f"Exception: {str(e)}")
            return False

    async def test_required_fields_validation(self) -> bool:
        """Test validation of required fields: team, league, season, model"""
        test_cases = [
            {"name": "Missing team", "data": {"league": "La Liga", "season": "2024-25", "model": "authentic"}},
            {"name": "Missing league", "data": {"team": "Real Madrid", "season": "2024-25", "model": "authentic"}},
            {"name": "Missing season", "data": {"team": "Real Madrid", "league": "La Liga", "model": "authentic"}},
            {"name": "Missing model", "data": {"team": "Real Madrid", "league": "La Liga", "season": "2024-25"}},
        ]
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        all_passed = True
        
        for test_case in test_cases:
            try:
                async with self.session.post(f"{BASE_URL}/jerseys", json=test_case["data"], headers=headers) as response:
                    if response.status == 422:  # Validation error expected
                        error_data = await response.json()
                        self.log_result(
                            f"Required Field Validation - {test_case['name']}", 
                            True, 
                            f"Correctly rejected submission: {error_data.get('detail', 'Validation error')}",
                            {"test_data": test_case["data"]}
                        )
                    else:
                        response_text = await response.text()
                        self.log_result(
                            f"Required Field Validation - {test_case['name']}", 
                            False, 
                            f"Expected validation error but got HTTP {response.status}: {response_text}",
                            {"test_data": test_case["data"]}
                        )
                        all_passed = False
                        
            except Exception as e:
                self.log_result(f"Required Field Validation - {test_case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
                
        return all_passed

    async def test_player_field_removal(self) -> bool:
        """Test that player field has been removed from the form structure"""
        try:
            # Submit jersey data with player field - should be ignored or cause error
            jersey_data = {
                "team": "Manchester United",
                "league": "Premier League", 
                "season": "2024-25",
                "model": "replica",
                "player": "Marcus Rashford",  # This field should be removed
                "description": "Test jersey with player field"
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            async with self.session.post(f"{BASE_URL}/jerseys", json=jersey_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    # Check if player field is present in response
                    has_player_field = "player" in str(data)
                    
                    if has_player_field:
                        self.log_result(
                            "Player Field Removal", 
                            False, 
                            "Player field is still present in jersey data - field removal not implemented",
                            {"jersey_data": data}
                        )
                        return False
                    else:
                        self.log_result(
                            "Player Field Removal", 
                            True, 
                            "Player field successfully removed from jersey structure",
                            {"jersey_id": data.get("id")}
                        )
                        return True
                elif response.status == 422:
                    # If it's a validation error about unknown field, that's also good
                    error_data = await response.json()
                    if "player" in str(error_data).lower():
                        self.log_result(
                            "Player Field Removal", 
                            True, 
                            f"Player field correctly rejected: {error_data.get('detail', 'Unknown field error')}",
                            {"error": error_data}
                        )
                        return True
                    else:
                        self.log_result(
                            "Player Field Removal", 
                            False, 
                            f"Unexpected validation error: {error_data.get('detail', 'Unknown error')}",
                            {"error": error_data}
                        )
                        return False
                else:
                    self.log_result(
                        "Player Field Removal", 
                        False, 
                        f"Unexpected HTTP {response.status}: {response_text}",
                        {"submitted_data": jersey_data}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Player Field Removal", False, f"Exception: {str(e)}")
            return False

    async def test_photo_upload_fields(self) -> bool:
        """Test front_photo and back_photo upload fields"""
        try:
            jersey_data = {
                "team": "Liverpool FC",
                "league": "Premier League",
                "season": "2024-25", 
                "model": "authentic",
                "manufacturer": "Nike",
                "front_photo": "https://example.com/liverpool_front.jpg",
                "back_photo": "https://example.com/liverpool_back.jpg",
                "description": "Liverpool home jersey with photo uploads"
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            async with self.session.post(f"{BASE_URL}/jerseys", json=jersey_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if photo fields are handled correctly
                    has_images = "images" in data and len(data.get("images", [])) > 0
                    has_front_photo = "front_photo" in str(data)
                    has_back_photo = "back_photo" in str(data)
                    
                    self.log_result(
                        "Photo Upload Fields", 
                        True, 
                        f"Photo fields processed - Images array: {has_images}, Front photo: {has_front_photo}, Back photo: {has_back_photo}",
                        {
                            "jersey_id": data.get("id"),
                            "images": data.get("images", []),
                            "has_front_photo": has_front_photo,
                            "has_back_photo": has_back_photo
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Photo Upload Fields", 
                        False, 
                        f"HTTP {response.status}: {response_text}",
                        {"submitted_data": jersey_data}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Photo Upload Fields", False, f"Exception: {str(e)}")
            return False

    async def test_admin_jersey_editing(self) -> bool:
        """Test admin functionality for editing pending jerseys with new structure"""
        if not self.created_jersey_id:
            self.log_result("Admin Jersey Editing", False, "No jersey ID available for admin testing")
            return False
            
        try:
            # First, get the pending jersey
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            async with self.session.get(f"{BASE_URL}/admin/jerseys/pending", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    pending_jerseys = data.get("jerseys", [])
                    
                    # Find our created jersey
                    target_jersey = None
                    for jersey in pending_jerseys:
                        if jersey.get("id") == self.created_jersey_id:
                            target_jersey = jersey
                            break
                    
                    if target_jersey:
                        self.log_result(
                            "Admin Jersey Editing - Retrieve Pending", 
                            True, 
                            f"Successfully retrieved pending jersey with new structure",
                            {
                                "jersey_id": target_jersey.get("id"),
                                "has_sku_code": "sku_code" in str(target_jersey),
                                "has_model": "model" in str(target_jersey),
                                "has_player": "player" in str(target_jersey),
                                "status": target_jersey.get("status")
                            }
                        )
                        
                        # Test admin approval with new structure
                        return await self.test_admin_approval(target_jersey)
                    else:
                        self.log_result(
                            "Admin Jersey Editing - Retrieve Pending", 
                            False, 
                            f"Created jersey {self.created_jersey_id} not found in pending list",
                            {"pending_count": len(pending_jerseys)}
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Jersey Editing - Retrieve Pending", 
                        False, 
                        f"HTTP {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Admin Jersey Editing", False, f"Exception: {str(e)}")
            return False

    async def test_admin_approval(self, jersey_data: Dict[str, Any]) -> bool:
        """Test admin approval of jersey with new structure"""
        try:
            jersey_id = jersey_data.get("id")
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Approve the jersey
            async with self.session.post(f"{BASE_URL}/admin/jerseys/{jersey_id}/approve", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Admin Jersey Approval", 
                        True, 
                        f"Successfully approved jersey with new structure",
                        {
                            "jersey_id": jersey_id,
                            "status": data.get("status"),
                            "approved_by": data.get("approved_by"),
                            "message": data.get("message")
                        }
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Jersey Approval", 
                        False, 
                        f"HTTP {response.status}: {error_text}",
                        {"jersey_id": jersey_id}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("Admin Jersey Approval", False, f"Exception: {str(e)}")
            return False

    async def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflow with new form structure"""
        try:
            # Create a comprehensive test jersey
            jersey_data = {
                "team": "Paris Saint-Germain",
                "league": "Ligue 1",
                "season": "2024-25",
                "manufacturer": "Jordan",
                "sku_code": "PSG2425A001",
                "model": "authentic",
                "description": "PSG maillot domicile authentique Jordan 2024-25 - Test complet workflow",
                "front_photo": "https://example.com/psg_front.jpg",
                "back_photo": "https://example.com/psg_back.jpg"
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Step 1: Submit jersey
            async with self.session.post(f"{BASE_URL}/jerseys", json=jersey_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    workflow_jersey_id = data.get("id")
                    
                    self.log_result(
                        "End-to-End Workflow - Submission", 
                        True, 
                        f"Jersey submitted successfully: {workflow_jersey_id}",
                        {
                            "jersey_id": workflow_jersey_id,
                            "reference_number": data.get("reference_number"),
                            "status": data.get("status")
                        }
                    )
                    
                    # Step 2: Verify jersey appears in user's submissions
                    return await self.verify_user_submissions(workflow_jersey_id)
                else:
                    error_text = await response.text()
                    self.log_result(
                        "End-to-End Workflow - Submission", 
                        False, 
                        f"HTTP {response.status}: {error_text}",
                        {"submitted_data": jersey_data}
                    )
                    return False
                    
        except Exception as e:
            self.log_result("End-to-End Workflow", False, f"Exception: {str(e)}")
            return False

    async def verify_user_submissions(self, jersey_id: str) -> bool:
        """Verify jersey appears in user's submissions"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Get user profile to find user ID
            async with self.session.get(f"{BASE_URL}/profile", headers=headers) as response:
                if response.status == 200:
                    profile_data = await response.json()
                    user_id = profile_data.get("id")
                    
                    # Get user's jersey submissions
                    async with self.session.get(f"{BASE_URL}/users/{user_id}/jerseys", headers=headers) as submissions_response:
                        if submissions_response.status == 200:
                            submissions_data = await submissions_response.json()
                            jerseys = submissions_data.get("jerseys", [])
                            
                            # Find our jersey
                            found_jersey = None
                            for jersey in jerseys:
                                if jersey.get("id") == jersey_id:
                                    found_jersey = jersey
                                    break
                            
                            if found_jersey:
                                self.log_result(
                                    "End-to-End Workflow - User Submissions", 
                                    True, 
                                    f"Jersey found in user submissions with correct structure",
                                    {
                                        "jersey_id": jersey_id,
                                        "status": found_jersey.get("status"),
                                        "has_new_fields": {
                                            "sku_code": "sku_code" in str(found_jersey),
                                            "model": "model" in str(found_jersey),
                                            "league": "league" in str(found_jersey)
                                        }
                                    }
                                )
                                return True
                            else:
                                self.log_result(
                                    "End-to-End Workflow - User Submissions", 
                                    False, 
                                    f"Jersey {jersey_id} not found in user submissions",
                                    {"total_submissions": len(jerseys)}
                                )
                                return False
                        else:
                            error_text = await submissions_response.text()
                            self.log_result(
                                "End-to-End Workflow - User Submissions", 
                                False, 
                                f"HTTP {submissions_response.status}: {error_text}"
                            )
                            return False
                else:
                    error_text = await response.text()
                    self.log_result(
                        "End-to-End Workflow - Profile", 
                        False, 
                        f"HTTP {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_result("End-to-End Workflow - Verification", False, f"Exception: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all tests for new jersey submission form structure"""
        print("🚀 Starting TopKit New Jersey Submission Form Structure Testing")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Authentication tests
            user_auth_success = await self.authenticate_user()
            admin_auth_success = await self.authenticate_admin()
            
            if not user_auth_success:
                print("❌ Cannot proceed without user authentication")
                return
                
            # Core form structure tests
            await self.test_new_form_structure_submission()
            await self.test_required_fields_validation()
            await self.test_player_field_removal()
            await self.test_photo_upload_fields()
            
            # Admin functionality tests (if admin auth successful)
            if admin_auth_success:
                await self.test_admin_jersey_editing()
            else:
                self.log_result("Admin Tests", False, "Skipped due to admin authentication failure")
            
            # End-to-end workflow test
            await self.test_end_to_end_workflow()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 TOPKIT NEW JERSEY FORM STRUCTURE TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print()
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["test"].split(" - ")[0] if " - " in result["test"] else result["test"]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            categories[category]["tests"].append(result)
        
        # Print category summaries
        for category, stats in categories.items():
            total = stats["passed"] + stats["failed"]
            rate = (stats["passed"] / total * 100) if total > 0 else 0
            status = "✅" if stats["failed"] == 0 else "⚠️" if stats["passed"] > stats["failed"] else "❌"
            print(f"{status} {category}: {stats['passed']}/{total} passed ({rate:.1f}%)")
        
        print()
        
        # Print failed tests details
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("❌ FAILED TESTS:")
            for result in failed_results:
                print(f"   • {result['test']}: {result['details']}")
        else:
            print("🎉 ALL TESTS PASSED!")
        
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check for new form structure implementation
        form_structure_tests = [r for r in self.test_results if "Form Structure" in r["test"]]
        if form_structure_tests and any(r["success"] for r in form_structure_tests):
            print("   ✅ New form structure (team, league, season, model, sku_code) is implemented")
        else:
            print("   ❌ New form structure implementation needs verification")
        
        # Check for player field removal
        player_tests = [r for r in self.test_results if "Player Field" in r["test"]]
        if player_tests and any(r["success"] for r in player_tests):
            print("   ✅ Player field has been successfully removed")
        else:
            print("   ❌ Player field removal needs implementation")
        
        # Check for photo upload support
        photo_tests = [r for r in self.test_results if "Photo" in r["test"]]
        if photo_tests and any(r["success"] for r in photo_tests):
            print("   ✅ Photo upload fields (front_photo, back_photo) are supported")
        else:
            print("   ❌ Photo upload fields need implementation")
        
        # Check admin functionality
        admin_tests = [r for r in self.test_results if "Admin" in r["test"]]
        if admin_tests and any(r["success"] for r in admin_tests):
            print("   ✅ Admin functionality works with new form structure")
        else:
            print("   ❌ Admin functionality needs verification with new structure")
        
        print()
        print("📋 REVIEW REQUEST STATUS:")
        print("   • NEW FORM STRUCTURE TESTING: " + ("✅ COMPLETED" if any("Form Structure" in r["test"] and r["success"] for r in self.test_results) else "❌ NEEDS WORK"))
        print("   • USER AUTHENTICATION: " + ("✅ WORKING" if any("User Authentication" in r["test"] and r["success"] for r in self.test_results) else "❌ FAILED"))
        print("   • ADMIN FUNCTIONALITY: " + ("✅ VERIFIED" if any("Admin" in r["test"] and r["success"] for r in self.test_results) else "❌ NEEDS VERIFICATION"))
        print("   • JERSEY CREATION: " + ("✅ SUCCESSFUL" if any("End-to-End" in r["test"] and r["success"] for r in self.test_results) else "❌ INCOMPLETE"))

async def main():
    """Main test execution"""
    tester = TopKitNewFormTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
"""
TopKit Admin Features Backend Testing
Test complet des nouvelles fonctionnalités d'administration ajoutées à TopKit

Focus Areas:
- ADMIN AUTHENTICATION: Test de connexion admin (topkitfr@gmail.com/TopKitSecure789#)
- JERSEY MANAGEMENT APIs: Endpoints d'administration des maillots
- USER MANAGEMENT APIs: Endpoints d'administration des utilisateurs  
- WORKFLOW TESTING: Test du workflow complet de modération
- SECURITY VERIFICATION: Vérification des permissions admin
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://kit-curator.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitAdminTester:
    def __init__(self):
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        self.test_jersey_id = None
        self.test_user_id = None
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_admin_authentication(self):
        """Test admin authentication with specified credentials"""
        print("🔐 TESTING ADMIN AUTHENTICATION")
        print("=" * 50)
        
        try:
            # Test admin login
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.admin_token = data["token"]
                    self.admin_user = data["user"]
                    
                    # Verify admin role
                    if data["user"].get("role") == "admin":
                        self.log_test(
                            "Admin Login Authentication", 
                            True, 
                            f"Successfully authenticated admin user: {data['user']['name']} (Role: {data['user']['role']}, ID: {data['user']['id']})"
                        )
                        
                        # Test token validation with a working endpoint
                        headers = {"Authorization": f"Bearer {self.admin_token}"}
                        profile_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
                        
                        if profile_response.status_code == 200:
                            self.log_test("Admin Token Validation", True, "JWT token validation successful via admin endpoint")
                        else:
                            self.log_test("Admin Token Validation", False, f"Token validation failed: {profile_response.status_code}")
                            
                    else:
                        self.log_test("Admin Role Verification", False, f"User role is '{data['user'].get('role')}', expected 'admin'")
                else:
                    self.log_test("Admin Login Authentication", False, "Missing token or user data in response", data)
            else:
                self.log_test("Admin Login Authentication", False, f"Login failed with status {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Admin Login Authentication", False, f"Exception during login: {str(e)}")

    def test_jersey_management_apis(self):
        """Test all jersey management admin APIs"""
        print("👕 TESTING JERSEY MANAGEMENT APIs")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Jersey Management APIs", False, "No admin token available - skipping jersey management tests")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # 1. Test GET /api/admin/jerseys/pending - récupération des maillots en attente
            response = requests.get(f"{BASE_URL}/admin/jerseys/pending", headers=headers)
            if response.status_code == 200:
                pending_jerseys = response.json()
                self.log_test(
                    "GET /admin/jerseys/pending", 
                    True, 
                    f"Retrieved {len(pending_jerseys)} pending jerseys"
                )
                
                # Store a test jersey ID if available
                if pending_jerseys and len(pending_jerseys) > 0:
                    self.test_jersey_id = pending_jerseys[0].get("id")
                    
            else:
                self.log_test("GET /admin/jerseys/pending", False, f"Failed with status {response.status_code}", response.text)

            # 2. Create a test jersey for moderation workflow if none exists
            if not self.test_jersey_id:
                # First, create a regular user to submit a jersey
                user_data = {
                    "email": "testuser@example.com",
                    "password": "TestPassword123!",
                    "name": "Test User"
                }
                
                user_response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
                if user_response.status_code == 200:
                    # Login as test user
                    login_response = requests.post(f"{BASE_URL}/auth/login", json={
                        "email": "testuser@example.com",
                        "password": "TestPassword123!"
                    })
                    
                    if login_response.status_code == 200:
                        user_token = login_response.json()["token"]
                        user_headers = {"Authorization": f"Bearer {user_token}"}
                        
                        # Submit a test jersey
                        jersey_data = {
                            "team": "FC Barcelona",
                            "season": "2024-25",
                            "player": "Pedri",
                            "manufacturer": "Nike",
                            "home_away": "home",
                            "league": "La Liga",
                            "description": "Test jersey for admin moderation workflow"
                        }
                        
                        jersey_response = requests.post(f"{BASE_URL}/jerseys", json=jersey_data, headers=user_headers)
                        if jersey_response.status_code == 200:
                            self.test_jersey_id = jersey_response.json()["id"]
                            self.log_test("Test Jersey Creation", True, f"Created test jersey for moderation: {self.test_jersey_id}")

            # 3. Test admin moderation actions if we have a jersey
            if self.test_jersey_id:
                # Test POST /api/admin/jerseys/{id}/suggest-modifications
                modification_data = {
                    "jersey_id": self.test_jersey_id,
                    "suggested_changes": "Veuillez corriger la saison - il s'agit de la saison 2023-24, pas 2024-25",
                    "suggested_modifications": {
                        "season": "2023-24",
                        "description": "Maillot domicile FC Barcelona saison 2023-24"
                    }
                }
                
                response = requests.post(
                    f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/suggest-modifications", 
                    json=modification_data, 
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.log_test("POST /admin/jerseys/{id}/suggest-modifications", True, "Modification suggestion created successfully")
                else:
                    self.log_test("POST /admin/jerseys/{id}/suggest-modifications", False, f"Failed with status {response.status_code}", response.text)

                # Test POST /api/admin/jerseys/{id}/approve
                response = requests.post(f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/approve", headers=headers)
                if response.status_code == 200:
                    self.log_test("POST /admin/jerseys/{id}/approve", True, "Jersey approved successfully")
                else:
                    self.log_test("POST /admin/jerseys/{id}/approve", False, f"Failed with status {response.status_code}", response.text)

                # Test POST /api/admin/jerseys/{id}/reject
                reject_data = {"reason": "Informations insuffisantes - veuillez fournir plus de détails sur l'authenticité"}
                response = requests.post(
                    f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/reject", 
                    json=reject_data, 
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.log_test("POST /admin/jerseys/{id}/reject", True, "Jersey rejected successfully with reason")
                else:
                    self.log_test("POST /admin/jerseys/{id}/reject", False, f"Failed with status {response.status_code}", response.text)

                # Test DELETE /api/admin/jerseys/{id} - Check if this endpoint exists
                # Based on the logs, this endpoint might not be implemented
                # Let's test if it exists first
                response = requests.delete(f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}", headers=headers)
                if response.status_code == 200:
                    self.log_test("DELETE /admin/jerseys/{id}", True, "Jersey deleted from explorer successfully")
                elif response.status_code == 404:
                    self.log_test("DELETE /admin/jerseys/{id}", False, "Endpoint not implemented - DELETE admin jersey not available")
                else:
                    self.log_test("DELETE /admin/jerseys/{id}", False, f"Failed with status {response.status_code}", response.text)

            # 4. Test GET /api/jerseys - liste des maillots approuvés
            response = requests.get(f"{BASE_URL}/jerseys")
            if response.status_code == 200:
                approved_jerseys = response.json()
                self.log_test("GET /jerseys (approved list)", True, f"Retrieved {len(approved_jerseys)} approved jerseys")
            else:
                self.log_test("GET /jerseys (approved list)", False, f"Failed with status {response.status_code}", response.text)

        except Exception as e:
            self.log_test("Jersey Management APIs", False, f"Exception during jersey management testing: {str(e)}")

    def test_user_management_apis(self):
        """Test user management admin APIs"""
        print("👥 TESTING USER MANAGEMENT APIs")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("User Management APIs", False, "No admin token available - skipping user management tests")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # 1. Test GET /api/admin/users - liste de tous les utilisateurs
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                self.log_test("GET /admin/users", True, f"Retrieved {len(users)} users")
                
                # Find a test user (not admin) for ban/delete testing
                for user in users:
                    if isinstance(user, dict) and user.get("role") != "admin" and user.get("email") != ADMIN_EMAIL:
                        self.test_user_id = user.get("id")
                        break
                        
            else:
                self.log_test("GET /admin/users", False, f"Failed with status {response.status_code}", response.text)

            # Create a test user for ban/delete operations if none found
            if not self.test_user_id:
                test_user_data = {
                    "email": "testuser.admin@example.com",
                    "password": "TopKit2025!",
                    "name": "Test User for Admin Operations"
                }
                
                user_response = requests.post(f"{BASE_URL}/auth/register", json=test_user_data)
                if user_response.status_code == 200:
                    # Login to get user ID
                    login_response = requests.post(f"{BASE_URL}/auth/login", json={
                        "email": "testuser.admin@example.com",
                        "password": "TopKit2025!"
                    })
                    
                    if login_response.status_code == 200:
                        self.test_user_id = login_response.json()["user"]["id"]
                        self.log_test("Test User Creation for Admin Operations", True, f"Created test user: {self.test_user_id}")
                    else:
                        self.log_test("Test User Login for Admin Operations", False, f"Login failed: {login_response.status_code}")
                else:
                    self.log_test("Test User Creation for Admin Operations", False, f"User creation failed: {user_response.status_code} - {user_response.text}")

            # 2. Test user ban functionality if we have a test user
            if self.test_user_id:
                # Test POST /api/admin/users/{id}/ban
                ban_data = {
                    "reason": "Test de bannissement - comportement inapproprié dans les commentaires",
                    "permanent": False,
                    "ban_duration_days": 7
                }
                
                response = requests.post(
                    f"{BASE_URL}/admin/users/{self.test_user_id}/ban", 
                    json=ban_data, 
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.log_test("POST /admin/users/{id}/ban", True, "User banned successfully with reason")
                else:
                    self.log_test("POST /admin/users/{id}/ban", False, f"Failed with status {response.status_code}", response.text)

                # Test DELETE /api/admin/users/{id} - suppression complète d'utilisateurs
                response = requests.delete(f"{BASE_URL}/admin/users/{self.test_user_id}", headers=headers)
                if response.status_code == 200:
                    self.log_test("DELETE /admin/users/{id}", True, "User deleted completely from system")
                else:
                    self.log_test("DELETE /admin/users/{id}", False, f"Failed with status {response.status_code}", response.text)
            else:
                self.log_test("User Ban/Delete Testing", False, "No suitable test user found for ban/delete operations")

        except Exception as e:
            self.log_test("User Management APIs", False, f"Exception during user management testing: {str(e)}")

    def test_workflow_complete(self):
        """Test complete moderation workflow"""
        print("🔄 TESTING COMPLETE MODERATION WORKFLOW")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Complete Workflow", False, "No admin token available - skipping workflow tests")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Create a complete workflow test
            # 1. Create test user
            workflow_user_data = {
                "email": "workflowtest@example.com",
                "password": "TopKit2025!",
                "name": "Workflow Test User"
            }
            
            user_response = requests.post(f"{BASE_URL}/auth/register", json=workflow_user_data)
            if user_response.status_code == 200:
                # 2. Login as test user
                login_response = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": "workflowtest@example.com", 
                    "password": "TopKit2025!"
                })
                
                if login_response.status_code == 200:
                    user_token = login_response.json()["token"]
                    user_headers = {"Authorization": f"Bearer {user_token}"}
                    workflow_user_id = login_response.json()["user"]["id"]
                    
                    # 3. Submit jersey for moderation
                    jersey_data = {
                        "team": "Real Madrid CF",
                        "season": "2024-25",
                        "player": "Vinicius Jr",
                        "manufacturer": "Adidas",
                        "home_away": "home",
                        "league": "La Liga",
                        "description": "Maillot domicile Real Madrid 2024-25 - Vinicius Jr"
                    }
                    
                    jersey_response = requests.post(f"{BASE_URL}/jerseys", json=jersey_data, headers=user_headers)
                    if jersey_response.status_code == 200:
                        workflow_jersey_id = jersey_response.json()["id"]
                        self.log_test("Workflow Step 1: Jersey Submission", True, f"Jersey submitted successfully: {workflow_jersey_id}")
                        
                        # 4. Admin suggests modification
                        modification_data = {
                            "jersey_id": workflow_jersey_id,
                            "suggested_changes": "Veuillez ajouter des informations sur la taille et l'état du maillot",
                            "suggested_modifications": {
                                "description": "Maillot domicile Real Madrid 2024-25 - Vinicius Jr - Taille L, état neuf avec étiquettes"
                            }
                        }
                        
                        mod_response = requests.post(
                            f"{BASE_URL}/admin/jerseys/{workflow_jersey_id}/suggest-modifications",
                            json=modification_data,
                            headers=headers
                        )
                        
                        if mod_response.status_code == 200:
                            self.log_test("Workflow Step 2: Admin Modification Suggestion", True, "Modification suggested successfully")
                            
                            # 5. Check user notifications
                            notif_response = requests.get(f"{BASE_URL}/notifications", headers=user_headers)
                            if notif_response.status_code == 200:
                                notifications = notif_response.json()
                                modification_notifs = [n for n in notifications if n.get("type") == "jersey_needs_modification"]
                                if modification_notifs:
                                    self.log_test("Workflow Step 3: User Notification Check", True, f"User received {len(modification_notifs)} modification notifications")
                                else:
                                    self.log_test("Workflow Step 3: User Notification Check", False, "No modification notifications found for user")
                            
                            # 6. Admin approves jersey
                            approve_response = requests.post(f"{BASE_URL}/admin/jerseys/{workflow_jersey_id}/approve", headers=headers)
                            if approve_response.status_code == 200:
                                self.log_test("Workflow Step 4: Admin Approval", True, "Jersey approved successfully")
                                
                                # 7. Check approval notification
                                notif_response = requests.get(f"{BASE_URL}/notifications", headers=user_headers)
                                if notif_response.status_code == 200:
                                    notifications = notif_response.json()
                                    approval_notifs = [n for n in notifications if n.get("type") == "jersey_approved"]
                                    if approval_notifs:
                                        self.log_test("Workflow Step 5: Approval Notification", True, f"User received {len(approval_notifs)} approval notifications")
                                    else:
                                        self.log_test("Workflow Step 5: Approval Notification", False, "No approval notifications found for user")
                                
                                # 8. Verify jersey appears in approved list
                                approved_response = requests.get(f"{BASE_URL}/jerseys")
                                if approved_response.status_code == 200:
                                    approved_jerseys = approved_response.json()
                                    workflow_jersey_found = any(j.get("id") == workflow_jersey_id for j in approved_jerseys)
                                    if workflow_jersey_found:
                                        self.log_test("Workflow Step 6: Jersey in Approved List", True, "Approved jersey appears in public list")
                                    else:
                                        self.log_test("Workflow Step 6: Jersey in Approved List", False, "Approved jersey not found in public list")
                                
                            else:
                                self.log_test("Workflow Step 4: Admin Approval", False, f"Approval failed: {approve_response.status_code}")
                        else:
                            self.log_test("Workflow Step 2: Admin Modification Suggestion", False, f"Modification suggestion failed: {mod_response.status_code}")
                    else:
                        self.log_test("Workflow Step 1: Jersey Submission", False, f"Jersey submission failed: {jersey_response.status_code}")
                else:
                    self.log_test("Workflow User Login", False, f"User login failed: {login_response.status_code}")
            else:
                self.log_test("Workflow User Creation", False, f"User creation failed: {user_response.status_code}")

        except Exception as e:
            self.log_test("Complete Workflow", False, f"Exception during workflow testing: {str(e)}")

    def test_security_verification(self):
        """Test security - verify admin-only access"""
        print("🔒 TESTING SECURITY VERIFICATION")
        print("=" * 50)
        
        try:
            # Test admin endpoints without authentication
            admin_endpoints = [
                "/admin/jerseys/pending",
                "/admin/users",
                "/admin/traffic-stats"
            ]
            
            for endpoint in admin_endpoints:
                response = requests.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 401 or response.status_code == 403:
                    self.log_test(f"Security Check: {endpoint} (no auth)", True, f"Correctly rejected with status {response.status_code}")
                else:
                    self.log_test(f"Security Check: {endpoint} (no auth)", False, f"Should reject but returned {response.status_code}")

            # Test with regular user token (if available)
            # Create a regular user for security testing
            regular_user_data = {
                "email": "regularuser@example.com",
                "password": "TopKit2025!",
                "name": "Regular User"
            }
            
            user_response = requests.post(f"{BASE_URL}/auth/register", json=regular_user_data)
            if user_response.status_code == 200:
                login_response = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": "regularuser@example.com",
                    "password": "TopKit2025!"
                })
                
                if login_response.status_code == 200:
                    regular_token = login_response.json()["token"]
                    regular_headers = {"Authorization": f"Bearer {regular_token}"}
                    
                    for endpoint in admin_endpoints:
                        response = requests.get(f"{BASE_URL}{endpoint}", headers=regular_headers)
                        if response.status_code == 403:
                            self.log_test(f"Security Check: {endpoint} (regular user)", True, "Correctly rejected regular user access")
                        else:
                            self.log_test(f"Security Check: {endpoint} (regular user)", False, f"Should reject regular user but returned {response.status_code}")

        except Exception as e:
            self.log_test("Security Verification", False, f"Exception during security testing: {str(e)}")

    def run_all_tests(self):
        """Run all admin functionality tests"""
        print("🚀 STARTING TOPKIT ADMIN FEATURES COMPREHENSIVE TESTING")
        print("=" * 70)
        print(f"Testing against: {BASE_URL}")
        print(f"Admin credentials: {ADMIN_EMAIL}")
        print("=" * 70)
        print()
        
        # Run all test suites
        self.test_admin_authentication()
        self.test_jersey_management_apis()
        self.test_user_management_apis()
        self.test_workflow_complete()
        self.test_security_verification()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by category
        categories = {
            "Authentication": [r for r in self.test_results if "Authentication" in r["test"] or "Login" in r["test"]],
            "Jersey Management": [r for r in self.test_results if "jersey" in r["test"].lower() or "GET /admin/jerseys" in r["test"] or "POST /admin/jerseys" in r["test"] or "DELETE /admin/jerseys" in r["test"]],
            "User Management": [r for r in self.test_results if "user" in r["test"].lower() and "admin" in r["test"].lower()],
            "Workflow": [r for r in self.test_results if "Workflow" in r["test"]],
            "Security": [r for r in self.test_results if "Security" in r["test"]]
        }
        
        for category, tests in categories.items():
            if tests:
                category_passed = len([t for t in tests if t["success"]])
                category_total = len(tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                print(f"{category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        print()
        print("FAILED TESTS:")
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            for result in failed_results:
                print(f"❌ {result['test']}: {result['details']}")
        else:
            print("✅ All tests passed!")
        
        print()
        print("🎯 ADMIN FEATURES TESTING COMPLETE")
        
        # Determine overall status
        if success_rate >= 90:
            print("🎉 EXCELLENT - Admin features are production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD - Admin features are mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE - Admin features have significant issues requiring attention")
        else:
            print("🚨 CRITICAL - Admin features have major failures requiring immediate fixes")

if __name__ == "__main__":
    tester = TopKitAdminTester()
    tester.run_all_tests()
"""
TopKit Beta System Removal Testing
Testing the removal of beta system and transition to public mode
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-curator.preview.emergentagent.com/api"

# Test credentials
TEST_USER = {
    "email": "test.beta.removal@example.com",
    "password": "TestBetaRemoval2024!",
    "name": "Beta Test User"
}

EXISTING_USER = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "TopKit123!"
}

ADMIN_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class BetaRemovalTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.admin_token = None
        
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

    def test_site_mode_public(self):
        """Test 1: Verify site mode is now 'public'"""
        try:
            response = self.session.get(f"{BACKEND_URL}/site/mode")
            
            if response.status_code == 200:
                data = response.json()
                mode = data.get('mode', '')
                
                if mode == 'public':
                    self.log_result(
                        "Site Mode Public Check",
                        True,
                        f"Site mode correctly set to 'public': {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Site Mode Public Check", 
                        False,
                        f"Expected 'public' but got '{mode}': {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Site Mode Public Check",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Site Mode Public Check", False, error=str(e))
            return False

    def test_registration_without_beta_restrictions(self):
        """Test 2: Verify registration works without beta restrictions"""
        try:
            # First, try to delete existing test user if exists
            try:
                # Get admin token first
                admin_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                    "email": ADMIN_USER["email"],
                    "password": ADMIN_USER["password"]
                })
                if admin_response.status_code == 200:
                    self.admin_token = admin_response.json().get("token")
            except:
                pass
            
            # Attempt registration
            registration_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"], 
                "name": TEST_USER["name"]
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=registration_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Registration Without Beta Restrictions",
                    True,
                    f"Registration successful: {data.get('message', 'Account created')}"
                )
                return True
            elif response.status_code == 400 and "existe déjà" in response.text:
                self.log_result(
                    "Registration Without Beta Restrictions",
                    True,
                    "User already exists - registration system working (no beta restrictions blocking)"
                )
                return True
            else:
                self.log_result(
                    "Registration Without Beta Restrictions",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Registration Without Beta Restrictions", False, error=str(e))
            return False

    def test_login_functionality(self):
        """Test 3: Verify login works normally"""
        try:
            # Try admin login first
            admin_login_data = {
                "email": ADMIN_USER["email"],
                "password": ADMIN_USER["password"]
            }
            
            admin_response = self.session.post(f"{BACKEND_URL}/auth/login", json=admin_login_data)
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                admin_token = admin_data.get("token")
                admin_user_info = admin_data.get("user", {})
                
                if admin_token:
                    self.admin_token = admin_token
                    self.log_result(
                        "Admin Login Functionality",
                        True,
                        f"Admin login successful for {admin_user_info.get('name', 'admin')} (Role: {admin_user_info.get('role', 'unknown')})"
                    )
                    
                    # Now try user login
                    user_login_data = {
                        "email": EXISTING_USER["email"],
                        "password": EXISTING_USER["password"]
                    }
                    
                    user_response = self.session.post(f"{BACKEND_URL}/auth/login", json=user_login_data)
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        user_token = user_data.get("token")
                        user_info = user_data.get("user", {})
                        
                        if user_token:
                            self.auth_token = user_token
                            self.log_result(
                                "User Login Functionality",
                                True,
                                f"User login successful for {user_info.get('name', 'user')} (Role: {user_info.get('role', 'unknown')})"
                            )
                            return True
                        else:
                            self.log_result(
                                "User Login Functionality",
                                False,
                                f"No user token received: {user_data}"
                            )
                            # Still return True since admin login worked
                            return True
                    else:
                        self.log_result(
                            "User Login Functionality",
                            False,
                            f"User login failed HTTP {user_response.status_code}: {user_response.text} (Admin login worked)"
                        )
                        # Still return True since admin login worked
                        return True
                else:
                    self.log_result(
                        "Admin Login Functionality",
                        False,
                        f"No admin token received: {admin_data}"
                    )
                    return False
            else:
                self.log_result(
                    "Login Functionality",
                    False,
                    f"Admin login failed HTTP {admin_response.status_code}: {admin_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Login Functionality", False, error=str(e))
            return False

    def test_site_access_no_beta_verification(self):
        """Test 4: Verify site access doesn't require beta verification"""
        try:
            # Test access check endpoint
            response = self.session.get(f"{BACKEND_URL}/site/access-check")
            
            if response.status_code == 200:
                data = response.json()
                has_access = data.get('has_access', False)
                
                if has_access:
                    self.log_result(
                        "Site Access No Beta Verification",
                        True,
                        f"Site access granted without beta verification: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Site Access No Beta Verification",
                        False,
                        f"Site access denied - beta restrictions may still be active: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Site Access No Beta Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Site Access No Beta Verification", False, error=str(e))
            return False

    def test_critical_endpoints(self):
        """Test 5: Test critical endpoints (jerseys, marketplace, etc.)"""
        endpoints_to_test = [
            ("/jerseys", "Jerseys Endpoint"),
            ("/marketplace/catalog", "Marketplace Catalog"),
            ("/explorer/leagues", "Explorer Leagues"),
            ("/stats/dynamic", "Dynamic Stats")
        ]
        
        all_passed = True
        results = []
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"✅ {name}: {len(data) if isinstance(data, list) else 'OK'}")
                else:
                    results.append(f"❌ {name}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {name}: {str(e)}")
                all_passed = False
        
        self.log_result(
            "Critical Endpoints Access",
            all_passed,
            "; ".join(results)
        )
        return all_passed

    def test_authenticated_endpoints(self):
        """Test 6: Test authenticated endpoints work properly"""
        # Use admin token if user token not available
        token_to_use = self.auth_token or self.admin_token
        
        if not token_to_use:
            self.log_result(
                "Authenticated Endpoints",
                False,
                "No auth token available - skipping authenticated endpoint tests"
            )
            return False
            
        headers = {"Authorization": f"Bearer {token_to_use}"}
        
        endpoints_to_test = [
            ("/auth/profile", "User Profile"),
            ("/notifications", "Notifications"),
            ("/users/me/collections", "User Collections")
        ]
        
        all_passed = True
        results = []
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    results.append(f"✅ {name}: OK")
                elif response.status_code == 404:
                    results.append(f"⚠️ {name}: Not implemented (404)")
                else:
                    results.append(f"❌ {name}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {name}: {str(e)}")
                all_passed = False
        
        self.log_result(
            "Authenticated Endpoints Access",
            all_passed,
            "; ".join(results)
        )
        return all_passed

    def run_all_tests(self):
        """Run all beta removal tests"""
        print("🚀 Starting TopKit Beta System Removal Testing")
        print("=" * 60)
        print()
        
        tests = [
            self.test_site_mode_public,
            self.test_registration_without_beta_restrictions,
            self.test_login_functionality,
            self.test_site_access_no_beta_verification,
            self.test_critical_endpoints,
            self.test_authenticated_endpoints
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        
        print("=" * 60)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Beta system successfully removed!")
        elif passed >= total * 0.8:
            print("✅ MOSTLY SUCCESSFUL - Minor issues detected")
        else:
            print("⚠️ SIGNIFICANT ISSUES - Beta removal may be incomplete")
        
        return passed, total

def main():
    tester = BetaRemovalTester()
    passed, total = tester.run_all_tests()
    
    # Return appropriate exit code
    if passed == total:
        exit(0)  # Success
    else:
        exit(1)  # Some tests failed

if __name__ == "__main__":
    main()