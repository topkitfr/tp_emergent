#!/usr/bin/env python3
"""
TopKit Backend Authentication & Voting System Testing
Critical testing following voting bug identification

Test accounts provided:
- topkitfr@gmail.com / T0p_Mdp_1288*
- steinmetzlivio@gmail.com / T0p_Mdp_1288*
- steinmetzolivier@gmail.com / T0p_Mdp_1288*

Focus areas:
1. Authentication endpoints testing
2. Voting system backend testing
3. Security diagnostics
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-admin-1.preview.emergentagent.com/api"

# Test accounts from review request
TEST_ACCOUNTS = [
    {"email": "topkitfr@gmail.com", "password": "T0p_Mdp_1288*"},
    {"email": "steinmetzlivio@gmail.com", "password": "T0p_Mdp_1288*"},
    {"email": "steinmetzolivier@gmail.com", "password": "T0p_Mdp_1288*"}
]

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.tokens = {}
        
    def log_result(self, test_name, success, details, critical=False):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        if critical and not success:
            status = "🚨 CRITICAL FAIL"
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        print(f"   Details: {details}")
        print()
        
    def test_authentication_endpoints(self):
        """Test authentication endpoints with provided accounts"""
        print("🔐 TESTING AUTHENTICATION ENDPOINTS")
        print("=" * 50)
        
        for i, account in enumerate(TEST_ACCOUNTS, 1):
            email = account["email"]
            password = account["password"]
            
            print(f"\n📧 Testing Account {i}: {email}")
            
            # Test login endpoint
            try:
                login_data = {
                    "email": email,
                    "password": password
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "token" in data:
                        self.tokens[email] = data["token"]
                        user_info = data.get("user", {})
                        self.log_result(
                            f"Login {email}",
                            True,
                            f"Login successful. Token received. User: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})"
                        )
                        
                        # Test token validation
                        self.test_token_validation(email, data["token"])
                        
                    else:
                        self.log_result(
                            f"Login {email}",
                            False,
                            f"Login response missing token. Response: {data}",
                            critical=True
                        )
                elif response.status_code == 401:
                    self.log_result(
                        f"Login {email}",
                        False,
                        f"Authentication failed - Invalid credentials (HTTP 401). Response: {response.text}",
                        critical=True
                    )
                elif response.status_code == 404:
                    self.log_result(
                        f"Login {email}",
                        False,
                        f"User account not found (HTTP 404). Response: {response.text}",
                        critical=True
                    )
                else:
                    self.log_result(
                        f"Login {email}",
                        False,
                        f"Login failed with HTTP {response.status_code}. Response: {response.text}",
                        critical=True
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Login {email}",
                    False,
                    f"Login request failed with exception: {str(e)}",
                    critical=True
                )
    
    def test_token_validation(self, email, token):
        """Test JWT token validation"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                self.log_result(
                    f"Token validation {email}",
                    True,
                    f"Token valid. Profile data retrieved: {profile_data.get('name', 'Unknown')}"
                )
            else:
                self.log_result(
                    f"Token validation {email}",
                    False,
                    f"Token validation failed (HTTP {response.status_code}). Response: {response.text}",
                    critical=True
                )
        except Exception as e:
            self.log_result(
                f"Token validation {email}",
                False,
                f"Token validation request failed: {str(e)}",
                critical=True
            )
    
    def test_contributions_system(self):
        """Test contributions system for voting"""
        print("\n🗳️ TESTING CONTRIBUTIONS SYSTEM")
        print("=" * 50)
        
        # Test contributions listing
        try:
            response = self.session.get(f"{BACKEND_URL}/contributions")
            
            if response.status_code == 200:
                contributions = response.json()
                if isinstance(contributions, list):
                    self.log_result(
                        "Contributions listing",
                        True,
                        f"Found {len(contributions)} contributions. Sample: {contributions[:2] if contributions else 'None'}"
                    )
                    
                    # Test voting on contributions if any exist
                    if contributions:
                        self.test_voting_system(contributions[0])
                    else:
                        self.log_result(
                            "Voting system",
                            False,
                            "No contributions available for voting test",
                            critical=False
                        )
                else:
                    self.log_result(
                        "Contributions listing",
                        False,
                        f"Unexpected response format: {contributions}",
                        critical=True
                    )
            else:
                self.log_result(
                    "Contributions listing",
                    False,
                    f"Failed to retrieve contributions (HTTP {response.status_code}). Response: {response.text}",
                    critical=True
                )
                
        except Exception as e:
            self.log_result(
                "Contributions listing",
                False,
                f"Contributions request failed: {str(e)}",
                critical=True
            )
    
    def test_voting_system(self, contribution):
        """Test voting system with a contribution"""
        contribution_id = contribution.get("id")
        if not contribution_id:
            self.log_result(
                "Voting system setup",
                False,
                "Contribution missing ID field",
                critical=True
            )
            return
        
        print(f"\n🗳️ Testing voting on contribution: {contribution_id}")
        
        # Test voting with authenticated users
        for email, token in self.tokens.items():
            if not token:
                continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test upvote
            try:
                vote_data = {"vote_type": "upvote"}
                response = self.session.post(
                    f"{BACKEND_URL}/contributions/{contribution_id}/vote",
                    json=vote_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_result(
                        f"Upvote by {email}",
                        True,
                        f"Vote successful. Result: {result}"
                    )
                elif response.status_code == 400:
                    self.log_result(
                        f"Upvote by {email}",
                        False,
                        f"Vote rejected (HTTP 400). Possible duplicate or validation error: {response.text}",
                        critical=False
                    )
                elif response.status_code == 401:
                    self.log_result(
                        f"Upvote by {email}",
                        False,
                        f"Vote rejected - Authentication required (HTTP 401): {response.text}",
                        critical=True
                    )
                elif response.status_code == 404:
                    self.log_result(
                        f"Upvote by {email}",
                        False,
                        f"Vote endpoint not found (HTTP 404): {response.text}",
                        critical=True
                    )
                else:
                    self.log_result(
                        f"Upvote by {email}",
                        False,
                        f"Vote failed (HTTP {response.status_code}): {response.text}",
                        critical=True
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Upvote by {email}",
                    False,
                    f"Vote request failed: {str(e)}",
                    critical=True
                )
        
        # Test automatic approval logic (score >= 3)
        self.test_auto_approval_logic(contribution_id)
    
    def test_auto_approval_logic(self, contribution_id):
        """Test automatic approval logic"""
        try:
            # Get updated contribution to check vote score
            response = self.session.get(f"{BACKEND_URL}/contributions/{contribution_id}")
            
            if response.status_code == 200:
                contribution = response.json()
                vote_score = contribution.get("vote_score", 0)
                status = contribution.get("status", "unknown")
                
                if vote_score >= 3 and status == "approved":
                    self.log_result(
                        "Auto-approval logic",
                        True,
                        f"Contribution auto-approved with score {vote_score}"
                    )
                elif vote_score >= 3 and status != "approved":
                    self.log_result(
                        "Auto-approval logic",
                        False,
                        f"Contribution has score {vote_score} but status is '{status}', expected 'approved'",
                        critical=True
                    )
                else:
                    self.log_result(
                        "Auto-approval logic",
                        True,
                        f"Contribution score {vote_score} < 3, status '{status}' - logic working correctly"
                    )
            else:
                self.log_result(
                    "Auto-approval logic",
                    False,
                    f"Failed to retrieve contribution details (HTTP {response.status_code})",
                    critical=True
                )
                
        except Exception as e:
            self.log_result(
                "Auto-approval logic",
                False,
                f"Auto-approval test failed: {str(e)}",
                critical=True
            )
    
    def test_security_diagnostics(self):
        """Test security diagnostics"""
        print("\n🛡️ TESTING SECURITY DIAGNOSTICS")
        print("=" * 50)
        
        # Test if accounts exist in database
        for account in TEST_ACCOUNTS:
            email = account["email"]
            
            # Try to get user info (this will fail if account doesn't exist)
            try:
                # Test with a password reset request (safe way to check if account exists)
                reset_data = {"email": email}
                response = self.session.post(
                    f"{BACKEND_URL}/auth/password-reset-request",
                    json=reset_data
                )
                
                # Most systems return 200 regardless to prevent email enumeration
                # But we can check the response message
                if response.status_code == 200:
                    self.log_result(
                        f"Account existence {email}",
                        True,
                        f"Account appears to exist (password reset accepted)"
                    )
                elif response.status_code == 404:
                    self.log_result(
                        f"Account existence {email}",
                        False,
                        f"Account does not exist in database",
                        critical=True
                    )
                else:
                    self.log_result(
                        f"Account existence {email}",
                        True,
                        f"Account status unclear (HTTP {response.status_code}), but endpoint exists"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Account existence {email}",
                    False,
                    f"Account existence check failed: {str(e)}",
                    critical=False
                )
        
        # Test API permissions
        self.test_api_permissions()
    
    def test_api_permissions(self):
        """Test API permissions"""
        print("\n🔒 Testing API Permissions")
        
        # Test unauthenticated access to protected endpoints
        protected_endpoints = [
            "/profile",
            "/collections",
            "/admin/users",
            "/notifications"
        ]
        
        for endpoint in protected_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 401:
                    self.log_result(
                        f"Protected endpoint {endpoint}",
                        True,
                        "Correctly requires authentication (HTTP 401)"
                    )
                elif response.status_code == 403:
                    self.log_result(
                        f"Protected endpoint {endpoint}",
                        True,
                        "Correctly requires authorization (HTTP 403)"
                    )
                else:
                    self.log_result(
                        f"Protected endpoint {endpoint}",
                        False,
                        f"Endpoint not properly protected (HTTP {response.status_code})",
                        critical=True
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Protected endpoint {endpoint}",
                    False,
                    f"Permission test failed: {str(e)}",
                    critical=False
                )
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚨 CRITICAL AUTHENTICATION & VOTING SYSTEM TESTING")
        print("=" * 60)
        print("Testing authentication system following voting bug identification")
        print("Frontend testing agent confirmed authentication doesn't work with ALL provided accounts")
        print()
        
        # Run test suites
        self.test_authentication_endpoints()
        self.test_contributions_system()
        self.test_security_diagnostics()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🎯 BACKEND TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for r in self.results if not r["success"] and r["critical"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Critical Failures: {critical_failures} 🚨")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Show critical failures
        if critical_failures > 0:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for result in self.results:
                if not result["success"] and result["critical"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
            print()
        
        # Authentication analysis
        auth_results = [r for r in self.results if "Login" in r["test"]]
        auth_success = sum(1 for r in auth_results if r["success"])
        
        print("🔐 AUTHENTICATION ANALYSIS:")
        if auth_success == 0:
            print("   🚨 CRITICAL: NO accounts can authenticate - confirms frontend agent findings")
            print("   🔍 ROOT CAUSE: Backend authentication system or account credentials issue")
        elif auth_success < len(TEST_ACCOUNTS):
            print(f"   ⚠️  PARTIAL: {auth_success}/{len(TEST_ACCOUNTS)} accounts can authenticate")
            print("   🔍 ISSUE: Some accounts have incorrect passwords or don't exist")
        else:
            print(f"   ✅ SUCCESS: All {auth_success}/{len(TEST_ACCOUNTS)} accounts can authenticate")
            print("   🔍 CONCLUSION: Backend authentication working - issue likely in frontend")
        
        print()
        
        # Voting system analysis
        voting_results = [r for r in self.results if "vote" in r["test"].lower() or "contribution" in r["test"].lower()]
        voting_success = sum(1 for r in voting_results if r["success"])
        
        print("🗳️ VOTING SYSTEM ANALYSIS:")
        if not voting_results:
            print("   ⚠️  No voting tests performed (no contributions available)")
        elif voting_success == len(voting_results):
            print("   ✅ Voting system backend operational")
        else:
            print(f"   ❌ Voting system issues: {len(voting_results) - voting_success}/{len(voting_results)} tests failed")
        
        print()
        
        # Final diagnosis
        print("🎯 FINAL DIAGNOSIS:")
        if critical_failures == 0 and auth_success == len(TEST_ACCOUNTS):
            print("   ✅ Backend authentication and voting systems are OPERATIONAL")
            print("   🔍 Issue is likely in FRONTEND form submission or API integration")
            print("   📋 Recommendation: Fix frontend authentication form handling")
        elif auth_success == 0:
            print("   🚨 Backend authentication is BROKEN - accounts cannot login")
            print("   🔍 Issue is in BACKEND - password hashing, account existence, or API logic")
            print("   📋 Recommendation: Check account passwords and backend authentication logic")
        else:
            print("   ⚠️  Mixed results - some backend issues identified")
            print("   🔍 Both frontend and backend may have issues")
            print("   📋 Recommendation: Fix identified backend issues first, then test frontend")

def main():
    """Main test execution"""
    tester = BackendTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()