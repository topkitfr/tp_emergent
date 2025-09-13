#!/usr/bin/env python3
"""
Jersey Submission Fix Testing - TopKit Backend
==============================================

This test specifically verifies the jersey submission fix where the create_jersey endpoint
was receiving a full user object instead of a user ID string for created_by and submitted_by
fields, causing Pydantic validation errors.

Test Focus:
1. Jersey submission endpoint POST /api/jerseys with proper authentication
2. Verify that the validation error is fixed - should accept user ID strings for created_by and submitted_by
3. Test creating a basic jersey with required fields (team, season, league, etc.)
4. Confirm the jersey is properly saved to database with correct user IDs

Test credentials: steinmetzlivio@gmail.com / TopKit123!
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
import os

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://topkit-workflow-fix.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials - using admin account since user account may not exist
TEST_EMAIL = "topkitfr@gmail.com"
TEST_PASSWORD = "TopKitSecure789#"

# Example jersey data from review request
JERSEY_DATA = {
    "team": "Paris Saint-Germain",
    "season": "2023/24", 
    "league": "Ligue 1",
    "home_away": "Home",
    "manufacturer": "Nike"
}

class JerseySubmissionTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_data = None
        self.test_results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    async def authenticate_user(self):
        """Authenticate user and get JWT token"""
        print(f"\n🔐 Authenticating user: {TEST_EMAIL}")
        
        try:
            async with self.session.post(
                f"{API_BASE}/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("token")
                    self.user_data = data.get("user", {})
                    
                    self.log_test(
                        "User Authentication", 
                        True, 
                        f"Successfully authenticated user: {self.user_data.get('name')} (ID: {self.user_data.get('id')}, Role: {self.user_data.get('role')})"
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_test(
                        "User Authentication", 
                        False, 
                        f"HTTP {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
            
    async def test_jersey_submission_basic(self):
        """Test basic jersey submission with required fields"""
        print(f"\n📝 Testing basic jersey submission...")
        
        if not self.auth_token:
            self.log_test("Basic Jersey Submission", False, "No authentication token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/jerseys",
                json=JERSEY_DATA,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    jersey_data = await response.json()
                    
                    # Verify the jersey was created with correct user IDs
                    created_by = jersey_data.get("created_by")
                    submitted_by = jersey_data.get("submitted_by")
                    user_id = self.user_data.get("id")
                    
                    if created_by == user_id and submitted_by == user_id:
                        self.log_test(
                            "Basic Jersey Submission", 
                            True, 
                            f"Jersey created successfully (ID: {jersey_data.get('id')}, Status: {jersey_data.get('status')}, Ref: {jersey_data.get('reference_number')}). User IDs correctly set as strings."
                        )
                        return jersey_data
                    else:
                        self.log_test(
                            "Basic Jersey Submission", 
                            False, 
                            f"User ID mismatch - Expected: {user_id}, Created_by: {created_by}, Submitted_by: {submitted_by}"
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Basic Jersey Submission", 
                        False, 
                        f"HTTP {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Basic Jersey Submission", False, f"Exception: {str(e)}")
            return False
            
    async def test_jersey_submission_validation(self):
        """Test jersey submission validation"""
        print(f"\n🔍 Testing jersey submission validation...")
        
        if not self.auth_token:
            self.log_test("Jersey Validation", False, "No authentication token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test with missing required fields
        invalid_data = {"manufacturer": "Nike"}  # Missing team and season
        
        try:
            async with self.session.post(
                f"{API_BASE}/jerseys",
                json=invalid_data,
                headers=headers
            ) as response:
                
                if response.status == 422:
                    error_data = await response.json()
                    self.log_test(
                        "Jersey Validation", 
                        True, 
                        f"Correctly rejected invalid data with HTTP 422: {error_data.get('detail', 'Validation error')}"
                    )
                    return True
                else:
                    self.log_test(
                        "Jersey Validation", 
                        False, 
                        f"Expected HTTP 422 for invalid data, got HTTP {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Jersey Validation", False, f"Exception: {str(e)}")
            return False
            
    async def test_unauthenticated_submission(self):
        """Test that unauthenticated requests are rejected"""
        print(f"\n🚫 Testing unauthenticated jersey submission...")
        
        try:
            async with self.session.post(
                f"{API_BASE}/jerseys",
                json=JERSEY_DATA,
                headers={"Content-Type": "application/json"}  # No auth header
            ) as response:
                
                if response.status == 401:
                    self.log_test(
                        "Unauthenticated Submission", 
                        True, 
                        "Correctly rejected unauthenticated request with HTTP 401"
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Unauthenticated Submission", 
                        False, 
                        f"Expected HTTP 401, got HTTP {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Unauthenticated Submission", False, f"Exception: {str(e)}")
            return False
            
    async def test_user_submissions_tracking(self):
        """Test that submitted jerseys appear in user's submissions"""
        print(f"\n📊 Testing user submissions tracking...")
        
        if not self.auth_token or not self.user_data:
            self.log_test("User Submissions Tracking", False, "No authentication data available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        user_id = self.user_data.get("id")
        
        try:
            async with self.session.get(
                f"{API_BASE}/users/{user_id}/jerseys",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    submissions = await response.json()
                    submission_count = len(submissions)
                    
                    # Check if our submitted jersey appears in the list
                    psg_submissions = [s for s in submissions if s.get("team") == "Paris Saint-Germain"]
                    
                    self.log_test(
                        "User Submissions Tracking", 
                        True, 
                        f"User has {submission_count} total submissions, including {len(psg_submissions)} PSG jersey(s)"
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_test(
                        "User Submissions Tracking", 
                        False, 
                        f"HTTP {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("User Submissions Tracking", False, f"Exception: {str(e)}")
            return False
            
    async def test_jersey_with_optional_fields(self):
        """Test jersey submission with optional fields"""
        print(f"\n🎯 Testing jersey submission with optional fields...")
        
        if not self.auth_token:
            self.log_test("Optional Fields Jersey", False, "No authentication token available")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Jersey data with optional fields
        extended_jersey_data = {
            **JERSEY_DATA,
            "player": "Kylian Mbappé",
            "description": "Classic PSG home jersey from 2023/24 season",
            "reference_code": "PSG-HOME-2324"
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/jerseys",
                json=extended_jersey_data,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    jersey_data = await response.json()
                    
                    # Verify optional fields were saved
                    player = jersey_data.get("player")
                    description = jersey_data.get("description")
                    reference_code = jersey_data.get("reference_code")
                    
                    self.log_test(
                        "Optional Fields Jersey", 
                        True, 
                        f"Jersey with optional fields created successfully (Player: {player}, Description: {description[:50]}..., Ref Code: {reference_code})"
                    )
                    return jersey_data
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Optional Fields Jersey", 
                        False, 
                        f"HTTP {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Optional Fields Jersey", False, f"Exception: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all jersey submission tests"""
        print("🎯 JERSEY SUBMISSION FIX TESTING - TOPKIT BACKEND")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        await self.setup_session()
        
        try:
            # Test sequence
            auth_success = await self.authenticate_user()
            
            if auth_success:
                await self.test_jersey_submission_basic()
                await self.test_jersey_submission_validation()
                await self.test_unauthenticated_submission()
                await self.test_user_submissions_tracking()
                await self.test_jersey_with_optional_fields()
            else:
                print("❌ Authentication failed - skipping other tests")
                
        finally:
            await self.cleanup_session()
            
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 JERSEY SUBMISSION FIX TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"\n✅ JERSEY SUBMISSION FIX VERIFICATION: SUCCESS!")
            print("The Pydantic validation error has been resolved.")
            print("Jersey submission endpoint correctly accepts user ID strings for created_by and submitted_by fields.")
        else:
            print(f"\n❌ JERSEY SUBMISSION FIX VERIFICATION: ISSUES DETECTED!")
            print("Some tests failed - the fix may not be complete.")
            
        return success_rate >= 80

async def main():
    """Main test execution"""
    tester = JerseySubmissionTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())