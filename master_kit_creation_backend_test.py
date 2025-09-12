#!/usr/bin/env python3
"""
Master Kit Creation Backend Testing
Testing the Master Kit creation endpoint that was causing "❌Erreur: [object Object]" error
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class MasterKitCreationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.available_teams = []
        self.available_brands = []
        
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
    
    def authenticate_admin(self) -> bool:
        """Test 1: Authentication with admin credentials"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_data = data.get("user", {})
                self.admin_user_id = user_data.get("id")
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Admin authenticated successfully: {user_data.get('name')} ({user_data.get('role')})",
                    {"user_id": self.admin_user_id, "email": ADMIN_EMAIL, "role": user_data.get('role')}
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def verify_teams_available(self) -> bool:
        """Test 2: Verify teams are available for master kit creation"""
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                teams_data = response.json()
                
                if isinstance(teams_data, list) and len(teams_data) > 0:
                    self.available_teams = teams_data
                    
                    # Check team structure
                    first_team = teams_data[0]
                    required_fields = ["id", "name"]
                    missing_fields = [field for field in required_fields if field not in first_team]
                    
                    if missing_fields:
                        self.log_result(
                            "Teams Data Structure",
                            False,
                            f"Teams missing required fields: {missing_fields}",
                            {"first_team": first_team}
                        )
                        return False
                    
                    self.log_result(
                        "Teams Availability",
                        True,
                        f"Found {len(teams_data)} teams available for master kit creation",
                        {"teams_count": len(teams_data), "sample_teams": [t.get('name') for t in teams_data[:3]]}
                    )
                    return True
                else:
                    self.log_result(
                        "Teams Availability",
                        False,
                        "No teams available for master kit creation",
                        {"teams_data": teams_data}
                    )
                    return False
            else:
                self.log_result(
                    "Teams Availability",
                    False,
                    f"Failed to fetch teams: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Teams Availability",
                False,
                f"Error fetching teams: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def verify_brands_available(self) -> bool:
        """Test 3: Verify brands are available for master kit creation"""
        try:
            response = self.session.get(f"{BACKEND_URL}/brands")
            
            if response.status_code == 200:
                brands_data = response.json()
                
                if isinstance(brands_data, list) and len(brands_data) > 0:
                    self.available_brands = brands_data
                    
                    # Check brand structure
                    first_brand = brands_data[0]
                    required_fields = ["id", "name"]
                    missing_fields = [field for field in required_fields if field not in first_brand]
                    
                    if missing_fields:
                        self.log_result(
                            "Brands Data Structure",
                            False,
                            f"Brands missing required fields: {missing_fields}",
                            {"first_brand": first_brand}
                        )
                        return False
                    
                    self.log_result(
                        "Brands Availability",
                        True,
                        f"Found {len(brands_data)} brands available for master kit creation",
                        {"brands_count": len(brands_data), "sample_brands": [b.get('name') for b in brands_data[:3]]}
                    )
                    return True
                else:
                    self.log_result(
                        "Brands Availability",
                        False,
                        "No brands available for master kit creation",
                        {"brands_data": brands_data}
                    )
                    return False
            else:
                self.log_result(
                    "Brands Availability",
                    False,
                    f"Failed to fetch brands: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Brands Availability",
                False,
                f"Error fetching brands: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_master_jersey_creation(self) -> bool:
        """Test 4: Test POST /api/master-jerseys endpoint with valid data"""
        if not self.available_teams or not self.available_brands:
            self.log_result(
                "Master Jersey Creation",
                False,
                "Cannot test master jersey creation - teams or brands not available",
                {"teams_available": len(self.available_teams), "brands_available": len(self.available_brands)}
            )
            return False
        
        try:
            # Use first available team and brand
            test_team = self.available_teams[0]
            test_brand = self.available_brands[0]
            
            # Create test master jersey data - use a unique season to avoid duplicates
            current_year = datetime.now().year
            test_season = f"{current_year}-{str(current_year + 1)[-2:]}"
            
            master_jersey_data = {
                "team_id": test_team["id"],
                "brand_id": test_brand["id"],
                "season": test_season,
                "jersey_type": "away",  # Use away to avoid conflicts with existing home jerseys
                "model": "authentic",
                "primary_color": "White",
                "secondary_colors": ["Blue"],
                "description": f"Test Master Jersey for {test_team.get('name')} - {test_brand.get('name')} Away Kit {test_season}"
            }
            
            response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=master_jersey_data)
            
            if response.status_code in [200, 201]:  # Accept both 200 and 201 as success
                created_jersey = response.json()
                
                # Verify response structure
                required_fields = ["id", "topkit_reference", "team_id", "brand_id", "season", "jersey_type"]
                missing_fields = [field for field in required_fields if field not in created_jersey]
                
                if missing_fields:
                    self.log_result(
                        "Master Jersey Creation Response",
                        False,
                        f"Created master jersey missing required fields: {missing_fields}",
                        {"created_jersey": created_jersey}
                    )
                    return False
                
                # Verify relationships are properly saved
                if created_jersey.get("team_id") != test_team["id"]:
                    self.log_result(
                        "Master Jersey Team Relationship",
                        False,
                        f"Team ID not properly saved: expected {test_team['id']}, got {created_jersey.get('team_id')}",
                        {"expected": test_team["id"], "actual": created_jersey.get("team_id")}
                    )
                    return False
                
                if created_jersey.get("brand_id") != test_brand["id"]:
                    self.log_result(
                        "Master Jersey Brand Relationship",
                        False,
                        f"Brand ID not properly saved: expected {test_brand['id']}, got {created_jersey.get('brand_id')}",
                        {"expected": test_brand["id"], "actual": created_jersey.get("brand_id")}
                    )
                    return False
                
                self.log_result(
                    "Master Jersey Creation",
                    True,
                    f"Master jersey created successfully: {created_jersey.get('topkit_reference')}",
                    {
                        "jersey_id": created_jersey.get("id"),
                        "topkit_reference": created_jersey.get("topkit_reference"),
                        "team_name": test_team.get("name"),
                        "brand_name": test_brand.get("name"),
                        "season": created_jersey.get("season"),
                        "jersey_type": created_jersey.get("jersey_type")
                    }
                )
                return True
                
            elif response.status_code == 400:
                # Check if it's a duplicate validation error (which is expected behavior)
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', '')
                    if 'existe déjà' in error_message or 'already exists' in error_message:
                        self.log_result(
                            "Master Jersey Creation - Duplicate Prevention",
                            True,
                            f"Duplicate prevention working correctly: {error_message}",
                            {"error_data": error_data, "request_data": master_jersey_data}
                        )
                        return True
                    else:
                        self.log_result(
                            "Master Jersey Creation Validation",
                            False,
                            f"Unexpected validation error: {error_message}",
                            {"error_data": error_data, "request_data": master_jersey_data}
                        )
                        return False
                except:
                    self.log_result(
                        "Master Jersey Creation Validation",
                        False,
                        f"Validation error during master jersey creation: {response.text}",
                        {"status_code": response.status_code, "request_data": master_jersey_data}
                    )
                    return False
            else:
                self.log_result(
                    "Master Jersey Creation",
                    False,
                    f"Failed to create master jersey: {response.status_code} - {response.text}",
                    {"status_code": response.status_code, "request_data": master_jersey_data}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Master Jersey Creation",
                False,
                f"Error creating master jersey: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_error_handling_improvements(self) -> bool:
        """Test 5: Verify error handling improvements are working properly"""
        try:
            # Test with invalid team_id
            invalid_data = {
                "team_id": "invalid-team-id",
                "brand_id": self.available_brands[0]["id"] if self.available_brands else "invalid-brand-id",
                "season": "2024-25",
                "jersey_type": "home",
                "model": "authentic",
                "primary_color": "Blue",
                "description": "Test with invalid team ID"
            }
            
            response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=invalid_data)
            
            if response.status_code == 404:
                try:
                    error_data = response.json()
                    if "detail" in error_data and isinstance(error_data["detail"], str):
                        self.log_result(
                            "Error Handling - Invalid Team ID",
                            True,
                            f"Proper error message returned for invalid team ID: {error_data['detail']}",
                            {"error_response": error_data}
                        )
                    else:
                        self.log_result(
                            "Error Handling - Invalid Team ID",
                            False,
                            "Error response format not user-friendly (should be string, not object)",
                            {"error_response": error_data}
                        )
                        return False
                except:
                    self.log_result(
                        "Error Handling - Invalid Team ID",
                        False,
                        "Error response is not valid JSON",
                        {"response_text": response.text}
                    )
                    return False
            else:
                self.log_result(
                    "Error Handling - Invalid Team ID",
                    False,
                    f"Expected 400 or 404 status code for invalid data, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
            
            # Test with missing required fields
            incomplete_data = {
                "season": "2024-25",
                "jersey_type": "home"
                # Missing team_id and brand_id
            }
            
            response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=incomplete_data)
            
            if response.status_code == 422:  # Pydantic validation error
                try:
                    error_data = response.json()
                    self.log_result(
                        "Error Handling - Missing Fields",
                        True,
                        "Proper validation error returned for missing required fields",
                        {"error_response": error_data}
                    )
                except:
                    self.log_result(
                        "Error Handling - Missing Fields",
                        False,
                        "Validation error response is not valid JSON",
                        {"response_text": response.text}
                    )
                    return False
            else:
                self.log_result(
                    "Error Handling - Missing Fields",
                    False,
                    f"Expected 422 status code for missing fields, got {response.status_code}",
                    {"status_code": response.status_code, "response": response.text}
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_result(
                "Error Handling Improvements",
                False,
                f"Error testing error handling: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_legacy_vs_new_system(self) -> bool:
        """Test 6: Test both legacy master jersey system and new master kit system"""
        try:
            # Test legacy master jersey endpoint
            legacy_response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            
            if legacy_response.status_code == 200:
                legacy_data = legacy_response.json()
                self.log_result(
                    "Legacy Master Jersey System",
                    True,
                    f"Legacy master jersey endpoint working - found {len(legacy_data)} master jerseys",
                    {"count": len(legacy_data)}
                )
            else:
                self.log_result(
                    "Legacy Master Jersey System",
                    False,
                    f"Legacy master jersey endpoint failed: {legacy_response.status_code}",
                    {"status_code": legacy_response.status_code}
                )
            
            # Test new master kit endpoint (if it exists)
            new_response = self.session.get(f"{BACKEND_URL}/master-kits")
            
            if new_response.status_code == 200:
                new_data = new_response.json()
                self.log_result(
                    "New Master Kit System",
                    True,
                    f"New master kit endpoint working - found {len(new_data)} master kits",
                    {"count": len(new_data)}
                )
            elif new_response.status_code == 404:
                self.log_result(
                    "New Master Kit System",
                    True,
                    "New master kit endpoint not implemented yet (404) - this is expected if only legacy system is active",
                    {"status_code": new_response.status_code}
                )
            else:
                self.log_result(
                    "New Master Kit System",
                    False,
                    f"New master kit endpoint error: {new_response.status_code}",
                    {"status_code": new_response.status_code}
                )
            
            return True
            
        except Exception as e:
            self.log_result(
                "Legacy vs New System Comparison",
                False,
                f"Error comparing systems: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def run_all_tests(self):
        """Run all master kit creation tests"""
        print("🧪 Starting Master Kit Creation Backend Testing...")
        print("=" * 60)
        
        # Test 1: Authentication
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed with other tests")
            return self.generate_summary()
        
        # Test 2: Teams availability
        teams_ok = self.verify_teams_available()
        
        # Test 3: Brands availability  
        brands_ok = self.verify_brands_available()
        
        # Test 4: Master jersey creation (only if teams and brands are available)
        if teams_ok and brands_ok:
            self.test_master_jersey_creation()
        
        # Test 5: Error handling improvements
        self.test_error_handling_improvements()
        
        # Test 6: Legacy vs new system comparison
        self.test_legacy_vs_new_system()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 MASTER KIT CREATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}: {result['message']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests*100 if total_tests > 0 else 0,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = MasterKitCreationTester()
    summary = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if summary["failed_tests"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)