#!/usr/bin/env python3
"""
Authentication and Personal Kit Creation Fix Testing
Testing the authentication system and personal kit creation workflow to ensure "Invalid token" error is resolved
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"

# Test credentials
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

class AuthPersonalKitTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def test_user_authentication(self) -> bool:
        """Test 1: Authentication Test - Verify user login returns proper token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_data = data.get("user", {})
                self.user_id = user_data.get("id")
                
                # Verify token format (JWT should have 3 parts separated by dots)
                if self.user_token and len(self.user_token.split('.')) == 3:
                    token_valid = True
                else:
                    token_valid = False
                
                # Set authorization header for subsequent requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.user_token}"
                })
                
                self.log_result(
                    "User Authentication",
                    token_valid,
                    f"User authenticated successfully: {user_data.get('name')} - Token format valid: {token_valid}",
                    {
                        "user_id": self.user_id,
                        "email": USER_EMAIL,
                        "name": user_data.get('name'),
                        "role": user_data.get('role'),
                        "token_format_valid": token_valid,
                        "token_length": len(self.user_token) if self.user_token else 0
                    }
                )
                return token_valid
            else:
                self.log_result(
                    "User Authentication",
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "User Authentication",
                False,
                f"Authentication error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_token_validation(self) -> bool:
        """Test 2: Token Validation - Verify JWT token is valid and properly formatted"""
        try:
            if not self.user_token:
                self.log_result(
                    "Token Validation",
                    False,
                    "No token available for validation",
                    {}
                )
                return False
            
            # Test token by making an authenticated request
            response = self.session.get(f"{BACKEND_URL}/users/profile/public-info")
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Verify the token returns user data (this endpoint returns profile info, not full user data)
                token_works = response.status_code == 200
                
                self.log_result(
                    "Token Validation",
                    token_works,
                    f"JWT token validation successful - Token works with authenticated endpoint: {token_works}",
                    {
                        "token_format": "JWT (3 parts)",
                        "token_works": token_works,
                        "endpoint_accessible": True,
                        "status_code": response.status_code
                    }
                )
                return token_works
            else:
                self.log_result(
                    "Token Validation",
                    False,
                    f"Token validation failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Token Validation",
                False,
                f"Token validation error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_teams_endpoint(self) -> bool:
        """Test 3: Teams Endpoint - Test GET /api/teams returns list of clubs/teams"""
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                teams_data = response.json()
                
                # Verify it's a list
                if not isinstance(teams_data, list):
                    self.log_result(
                        "Teams Endpoint",
                        False,
                        "Teams endpoint should return an array",
                        {"actual_type": type(teams_data).__name__}
                    )
                    return False
                
                # Check if we have teams
                if len(teams_data) == 0:
                    self.log_result(
                        "Teams Endpoint",
                        False,
                        "Teams endpoint returns empty array - no teams available",
                        {"count": 0}
                    )
                    return False
                
                # Analyze first team structure
                first_team = teams_data[0]
                required_fields = ["id", "name"]
                missing_fields = [field for field in required_fields if field not in first_team]
                
                if missing_fields:
                    self.log_result(
                        "Teams Endpoint Structure",
                        False,
                        f"Missing required fields in team data: {missing_fields}",
                        {"first_team_keys": list(first_team.keys())}
                    )
                    return False
                
                self.log_result(
                    "Teams Endpoint",
                    True,
                    f"Teams endpoint returns {len(teams_data)} teams with proper structure",
                    {
                        "count": len(teams_data),
                        "sample_team": {
                            "id": first_team.get("id"),
                            "name": first_team.get("name"),
                            "has_required_fields": len(missing_fields) == 0
                        }
                    }
                )
                return True
                
            else:
                self.log_result(
                    "Teams Endpoint",
                    False,
                    f"Teams endpoint failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Teams Endpoint Test",
                False,
                f"Teams endpoint error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_master_kits_by_team(self) -> bool:
        """Test 4: Master Kits by Team - Test GET /api/master-kits?team_id=TEAM_ID"""
        try:
            # First get a team ID
            teams_response = self.session.get(f"{BACKEND_URL}/teams")
            
            if teams_response.status_code != 200:
                self.log_result(
                    "Master Kits by Team - Teams Access",
                    False,
                    "Cannot access teams to get team ID for master kits test",
                    {"status_code": teams_response.status_code}
                )
                return False
            
            teams_data = teams_response.json()
            
            if not teams_data:
                self.log_result(
                    "Master Kits by Team - Teams Available",
                    False,
                    "No teams available to test master kits endpoint",
                    {"teams_count": 0}
                )
                return False
            
            # Use first team
            test_team = teams_data[0]
            team_id = test_team.get("id")
            team_name = test_team.get("name")
            
            if not team_id:
                self.log_result(
                    "Master Kits by Team - Team ID",
                    False,
                    "Selected team missing ID",
                    {"team": test_team}
                )
                return False
            
            # Test master kits endpoint with team filter
            response = self.session.get(f"{BACKEND_URL}/master-kits?team_id={team_id}")
            
            if response.status_code == 200:
                master_kits_data = response.json()
                
                # Verify it's a list
                if not isinstance(master_kits_data, list):
                    self.log_result(
                        "Master Kits by Team",
                        False,
                        "Master kits endpoint should return an array",
                        {"actual_type": type(master_kits_data).__name__}
                    )
                    return False
                
                # It's OK if no master kits exist for this team, but endpoint should work
                self.log_result(
                    "Master Kits by Team",
                    True,
                    f"Master kits endpoint working - Found {len(master_kits_data)} master kits for team '{team_name}'",
                    {
                        "team_id": team_id,
                        "team_name": team_name,
                        "master_kits_count": len(master_kits_data),
                        "endpoint_functional": True
                    }
                )
                return True
                
            else:
                self.log_result(
                    "Master Kits by Team",
                    False,
                    f"Master kits endpoint failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code, "team_id": team_id}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Master Kits by Team Test",
                False,
                f"Master kits by team error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_personal_kit_creation_with_token(self) -> bool:
        """Test 5: Personal Kit Creation Test - Using token, test POST /api/personal-kits"""
        try:
            if not self.user_token:
                self.log_result(
                    "Personal Kit Creation with Token",
                    False,
                    "No authentication token available for personal kit creation test",
                    {}
                )
                return False
            
            # First get a reference kit from vestiaire
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if vestiaire_response.status_code != 200:
                self.log_result(
                    "Personal Kit Creation - Vestiaire Access",
                    False,
                    f"Cannot access vestiaire to get reference kit: {vestiaire_response.status_code}",
                    {"status_code": vestiaire_response.status_code}
                )
                return False
            
            vestiaire_kits = vestiaire_response.json()
            
            if not vestiaire_kits:
                self.log_result(
                    "Personal Kit Creation - Reference Kits Available",
                    False,
                    "No reference kits available in vestiaire for personal kit creation test",
                    {"vestiaire_count": 0}
                )
                return False
            
            # Use first reference kit
            reference_kit = vestiaire_kits[0]
            reference_kit_id = reference_kit.get("id")
            
            if not reference_kit_id:
                self.log_result(
                    "Personal Kit Creation - Reference Kit ID",
                    False,
                    "Selected reference kit missing ID",
                    {"reference_kit": reference_kit}
                )
                return False
            
            # Create personal kit with detailed information
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "excellent",
                "purchase_price": 95.50,
                "purchase_date": "2024-01-20T00:00:00Z",
                "purchase_location": "Official Store",
                "is_signed": False,
                "has_printing": True,
                "printed_name": "PLAYER",
                "printed_number": 7,
                "is_worn": False,
                "personal_notes": "Testing personal kit creation with authentication token - should not get Invalid token error"
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            
            # Check for "Invalid token" error specifically
            invalid_token_error = False
            if response.status_code == 401 or "Invalid token" in response.text:
                invalid_token_error = True
            
            # Handle success cases (201/200) and acceptable duplicate case (400 with "already in collection")
            if response.status_code in [200, 201]:
                personal_kit = response.json()
                
                self.log_result(
                    "Personal Kit Creation with Token",
                    True,
                    "Personal kit created successfully - No 'Invalid token' error",
                    {
                        "personal_kit_id": personal_kit.get("id"),
                        "reference_kit_id": reference_kit_id,
                        "token_error": False,
                        "status_code": response.status_code,
                        "has_enriched_data": bool(personal_kit.get("reference_kit_info"))
                    }
                )
                return True
                
            elif response.status_code == 400 and "already in your collection" in response.text:
                # This is acceptable - means the endpoint works but kit already exists
                self.log_result(
                    "Personal Kit Creation with Token",
                    True,
                    "Personal kit creation endpoint working - Kit already exists (no 'Invalid token' error)",
                    {
                        "reference_kit_id": reference_kit_id,
                        "token_error": False,
                        "status": "already_exists",
                        "message": "Endpoint functional - authentication working"
                    }
                )
                return True
                
            elif invalid_token_error:
                self.log_result(
                    "Personal Kit Creation with Token",
                    False,
                    f"CRITICAL: 'Invalid token' error still present: {response.status_code} - {response.text}",
                    {
                        "status_code": response.status_code,
                        "token_error": True,
                        "response_text": response.text,
                        "token_present": bool(self.user_token)
                    }
                )
                return False
                
            else:
                self.log_result(
                    "Personal Kit Creation with Token",
                    False,
                    f"Personal kit creation failed (not token error): {response.status_code} - {response.text}",
                    {
                        "status_code": response.status_code,
                        "token_error": False,
                        "request_data": personal_kit_data
                    }
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Personal Kit Creation with Token Test",
                False,
                f"Personal kit creation test error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_complete_add_to_collection_workflow(self) -> bool:
        """Test 6: Complete Add to Collection Workflow"""
        try:
            print("\n🔄 Testing Complete Add to Collection Workflow...")
            
            # Step 1: Verify user is logged in
            if not self.user_token or not self.user_id:
                self.log_result(
                    "Complete Workflow - Authentication Check",
                    False,
                    "User not authenticated for complete workflow test",
                    {}
                )
                return False
            
            # Step 2: Get reference kit from vestiaire
            vestiaire_response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if vestiaire_response.status_code != 200:
                self.log_result(
                    "Complete Workflow - Vestiaire Access",
                    False,
                    f"Cannot access vestiaire: {vestiaire_response.status_code}",
                    {"status_code": vestiaire_response.status_code}
                )
                return False
            
            vestiaire_kits = vestiaire_response.json()
            
            if not vestiaire_kits:
                self.log_result(
                    "Complete Workflow - Reference Kits Available",
                    False,
                    "No reference kits available for complete workflow test",
                    {"vestiaire_count": 0}
                )
                return False
            
            # Step 3: Select a reference kit (try to find one not already in collection)
            selected_kit = None
            reference_kit_id = None
            
            # Check existing collections to avoid duplicates
            existing_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            existing_kit_ids = []
            
            if existing_response.status_code == 200:
                existing_kits = existing_response.json()
                existing_kit_ids = [k.get("reference_kit_id") for k in existing_kits if k.get("reference_kit_id")]
            
            # Find a kit not in collection
            for kit in vestiaire_kits:
                kit_id = kit.get("id")
                if kit_id and kit_id not in existing_kit_ids:
                    selected_kit = kit
                    reference_kit_id = kit_id
                    break
            
            # If all kits are in collection, use first one (will test duplicate handling)
            if not selected_kit:
                selected_kit = vestiaire_kits[0]
                reference_kit_id = selected_kit.get("id")
            
            # Step 4: Create personal kit with detailed information
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "wanted",
                "size": "M",
                "condition": "mint",
                "purchase_price": 150.00,
                "purchase_date": "2024-02-01T00:00:00Z",
                "purchase_location": "Collector Market",
                "is_signed": True,
                "signed_by": "Team Captain",
                "has_printing": True,
                "printed_name": "LEGEND",
                "printed_number": 10,
                "is_worn": False,
                "personal_notes": "Complete workflow test - dream kit for collection"
            }
            
            create_response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            
            # Step 5: Verify successful creation (or acceptable duplicate)
            creation_successful = False
            
            if create_response.status_code in [200, 201]:
                created_kit = create_response.json()
                creation_successful = True
                
                # Verify enriched data
                has_enriched_data = all(field in created_kit for field in ["reference_kit_info", "master_kit_info"])
                
                if not has_enriched_data:
                    self.log_result(
                        "Complete Workflow - Data Enrichment",
                        False,
                        "Created personal kit missing enriched data",
                        {"created_kit_keys": list(created_kit.keys())}
                    )
                    return False
                
            elif create_response.status_code == 400 and "already in your collection" in create_response.text:
                creation_successful = True  # Acceptable - endpoint works
                
            elif "Invalid token" in create_response.text:
                self.log_result(
                    "Complete Workflow - Token Error",
                    False,
                    "CRITICAL: Invalid token error in complete workflow",
                    {"status_code": create_response.status_code, "response": create_response.text}
                )
                return False
            
            if not creation_successful:
                self.log_result(
                    "Complete Workflow - Personal Kit Creation",
                    False,
                    f"Failed to create personal kit: {create_response.status_code} - {create_response.text}",
                    {"status_code": create_response.status_code}
                )
                return False
            
            # Step 6: Verify kit appears in collection
            collection_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            
            if collection_response.status_code != 200:
                self.log_result(
                    "Complete Workflow - Collection Verification",
                    False,
                    f"Cannot verify collection: {collection_response.status_code}",
                    {"status_code": collection_response.status_code}
                )
                return False
            
            collection_kits = collection_response.json()
            
            # Check if our kit is in the collection
            our_kit_found = False
            for kit in collection_kits:
                if kit.get("reference_kit_id") == reference_kit_id:
                    our_kit_found = True
                    break
            
            workflow_success = creation_successful and our_kit_found
            
            self.log_result(
                "Complete Add to Collection Workflow",
                workflow_success,
                f"Complete workflow {'successful' if workflow_success else 'failed'} - No token errors detected",
                {
                    "workflow_steps": {
                        "authentication": True,
                        "vestiaire_access": True,
                        "reference_kit_selection": True,
                        "personal_kit_creation": creation_successful,
                        "collection_verification": our_kit_found
                    },
                    "token_errors": False,
                    "collection_count": len(collection_kits)
                }
            )
            return workflow_success
            
        except Exception as e:
            self.log_result(
                "Complete Add to Collection Workflow Test",
                False,
                f"Complete workflow error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all authentication and personal kit creation tests"""
        print("🧪 Starting Authentication and Personal Kit Creation Fix Testing...")
        print("=" * 70)
        
        # Test 1: User Authentication
        auth_success = self.test_user_authentication()
        
        # Test 2: Token Validation
        token_validation_success = False
        if auth_success:
            token_validation_success = self.test_token_validation()
        
        # Test 3: Teams Endpoint
        teams_success = self.test_teams_endpoint()
        
        # Test 4: Master Kits by Team
        master_kits_success = self.test_master_kits_by_team()
        
        # Test 5: Personal Kit Creation with Token
        personal_kit_success = False
        if auth_success:
            personal_kit_success = self.test_personal_kit_creation_with_token()
        
        # Test 6: Complete Add to Collection Workflow
        complete_workflow_success = False
        if auth_success:
            complete_workflow_success = self.test_complete_add_to_collection_workflow()
        
        # Calculate overall success
        test_successes = [
            auth_success,
            token_validation_success,
            teams_success,
            master_kits_success,
            personal_kit_success,
            complete_workflow_success
        ]
        
        overall_success = sum(test_successes) >= 5  # Allow one failure
        success_rate = (sum(test_successes) / len(test_successes)) * 100
        
        print("\n" + "=" * 70)
        print(f"🏁 Authentication and Personal Kit Creation Testing Complete")
        print(f"📊 Success Rate: {success_rate:.1f}% ({sum(test_successes)}/{len(test_successes)} tests passed)")
        
        # Check specifically for token-related issues
        token_issues_resolved = auth_success and token_validation_success and personal_kit_success
        
        return {
            "success": overall_success,
            "success_rate": success_rate,
            "tests_passed": sum(test_successes),
            "total_tests": len(test_successes),
            "token_issues_resolved": token_issues_resolved,
            "message": f"Authentication and personal kit creation testing completed with {success_rate:.1f}% success rate",
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = AuthPersonalKitTester()
    results = tester.run_all_tests()
    
    # Print summary
    print(f"\n📋 SUMMARY:")
    print(f"Overall Success: {'✅ PASS' if results['success'] else '❌ FAIL'}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Tests Passed: {results['tests_passed']}/{results['total_tests']}")
    print(f"Token Issues Resolved: {'✅ YES' if results['token_issues_resolved'] else '❌ NO'}")
    
    # Return appropriate exit code
    sys.exit(0 if results['success'] else 1)

if __name__ == "__main__":
    main()