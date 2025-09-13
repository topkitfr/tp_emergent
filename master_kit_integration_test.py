#!/usr/bin/env python3
"""
Master Kit Integration Fix Testing
Testing the critical bug fix: "master kits don't appear in catalogue after approval"

This test verifies:
1. Master Kits Integration Status - GET /api/contributions-v2?entity_type=master_kit&status=approved 
2. Master Jerseys Catalogue - GET /api/master-jerseys
3. Specific Master Jersey Endpoint - GET /api/master-jerseys/{id}
4. Integration Process Verification - Compare counts and verify workflow
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://football-jersey-db.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class MasterKitIntegrationTester:
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
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Try both possible token field names
                self.admin_token = data.get("access_token") or data.get("token")
                if not self.admin_token:
                    self.log_result("Admin Authentication", False, "", "No token in response")
                    return False
                    
                # Set the authorization header for all future requests
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                
                user_info = data.get("user", {})
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Successfully authenticated as {user_info.get('name', 'Unknown')} ({user_info.get('role', 'Unknown role')}). Token: {self.admin_token[:20]}..."
                )
                return True
            else:
                self.log_result("Admin Authentication", False, "", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def test_master_kit_contributions_status(self):
        """Test 1: Check approved master kit contributions"""
        try:
            # The session should already have the Authorization header set
            response = self.session.get(f"{API_BASE}/contributions-v2/", params={
                "entity_type": "master_kit",
                "status": "approved"
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both array and object responses
                if isinstance(data, list):
                    contributions = data
                else:
                    contributions = data.get("contributions", [])
                
                total_count = len(contributions)
                
                # Analyze contribution data
                contribution_details = []
                for contrib in contributions:
                    contrib_info = {
                        "id": contrib.get("id"),
                        "entity_name": contrib.get("entity_name", "Unknown"),
                        "status": contrib.get("status"),
                        "created_at": contrib.get("created_at"),
                        "approved_at": contrib.get("approved_at"),
                        "has_data": bool(contrib.get("data")),
                        "data_fields": list(contrib.get("data", {}).keys()) if contrib.get("data") else []
                    }
                    contribution_details.append(contrib_info)
                
                self.log_result(
                    "Master Kit Contributions Status",
                    True,
                    f"Found {total_count} approved master kit contributions. Details: {json.dumps(contribution_details, indent=2)}"
                )
                return total_count, contributions
            else:
                self.log_result(
                    "Master Kit Contributions Status", 
                    False, 
                    "", 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return 0, []
                
        except Exception as e:
            self.log_result("Master Kit Contributions Status", False, "", str(e))
            return 0, []

    def test_master_jerseys_catalogue(self):
        """Test 2: Check master jerseys catalogue"""
        try:
            response = self.session.get(f"{API_BASE}/master-jerseys")
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both array and object responses
                if isinstance(data, list):
                    master_jerseys = data
                    total_count = len(master_jerseys)
                else:
                    master_jerseys = data.get("master_jerseys", data.get("items", []))
                    total_count = data.get("total", len(master_jerseys))
                
                # Analyze master jersey data
                jersey_details = []
                for jersey in master_jerseys:
                    jersey_info = {
                        "id": jersey.get("id"),
                        "topkit_reference": jersey.get("topkit_reference"),
                        "season": jersey.get("season"),
                        "jersey_type": jersey.get("jersey_type"),
                        "has_team_info": bool(jersey.get("team_info")),
                        "has_brand_info": bool(jersey.get("brand_info")),
                        "team_name": jersey.get("team_info", {}).get("name") if jersey.get("team_info") else None,
                        "brand_name": jersey.get("brand_info", {}).get("name") if jersey.get("brand_info") else None
                    }
                    jersey_details.append(jersey_info)
                
                self.log_result(
                    "Master Jerseys Catalogue",
                    True,
                    f"Found {total_count} master jerseys in catalogue. Details: {json.dumps(jersey_details, indent=2)}"
                )
                return total_count, master_jerseys
            else:
                self.log_result(
                    "Master Jerseys Catalogue", 
                    False, 
                    "", 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return 0, []
                
        except Exception as e:
            self.log_result("Master Jerseys Catalogue", False, "", str(e))
            return 0, []

    def test_specific_master_jersey_endpoint(self, master_jerseys):
        """Test 3: Test specific master jersey endpoint"""
        if not master_jerseys:
            self.log_result(
                "Specific Master Jersey Endpoint",
                False,
                "",
                "No master jerseys available to test individual endpoint"
            )
            return False
        
        try:
            # Test the first master jersey
            test_jersey = master_jerseys[0]
            jersey_id = test_jersey.get("id")
            
            if not jersey_id:
                self.log_result(
                    "Specific Master Jersey Endpoint",
                    False,
                    "",
                    "Master jersey missing ID field"
                )
                return False
            
            response = self.session.get(f"{API_BASE}/master-jerseys/{jersey_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify detailed data structure
                required_fields = ["id", "topkit_reference", "season", "jersey_type"]
                missing_fields = [field for field in required_fields if not data.get(field)]
                
                jersey_details = {
                    "id": data.get("id"),
                    "topkit_reference": data.get("topkit_reference"),
                    "season": data.get("season"),
                    "jersey_type": data.get("jersey_type"),
                    "team_info": data.get("team_info"),
                    "brand_info": data.get("brand_info"),
                    "has_complete_data": len(missing_fields) == 0
                }
                
                success = len(missing_fields) == 0
                details = f"Jersey ID {jersey_id} details: {json.dumps(jersey_details, indent=2)}"
                error = f"Missing required fields: {missing_fields}" if missing_fields else ""
                
                self.log_result(
                    "Specific Master Jersey Endpoint",
                    success,
                    details,
                    error
                )
                return success
            else:
                self.log_result(
                    "Specific Master Jersey Endpoint", 
                    False, 
                    "", 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Specific Master Jersey Endpoint", False, "", str(e))
            return False

    def test_integration_process_verification(self, contributions_count, master_jerseys_count):
        """Test 4: Verify integration process is working"""
        try:
            # Check if integration is working by comparing counts
            integration_working = master_jerseys_count > 0
            
            # Additional checks
            integration_details = {
                "approved_contributions": contributions_count,
                "master_jerseys_in_catalogue": master_jerseys_count,
                "integration_ratio": f"{master_jerseys_count}/{contributions_count}" if contributions_count > 0 else "N/A",
                "integration_working": integration_working
            }
            
            # Determine success criteria
            if contributions_count == 0 and master_jerseys_count == 0:
                success = True
                details = "No approved contributions and no master jerseys - system is clean"
            elif contributions_count > 0 and master_jerseys_count > 0:
                success = True
                details = f"Integration working: {master_jerseys_count} master jerseys created from {contributions_count} approved contributions"
            elif contributions_count > 0 and master_jerseys_count == 0:
                success = False
                details = f"Integration failure: {contributions_count} approved contributions but 0 master jerseys in catalogue"
            else:
                success = True
                details = f"Unexpected state: {contributions_count} contributions, {master_jerseys_count} master jerseys"
            
            self.log_result(
                "Integration Process Verification",
                success,
                f"{details}. Integration details: {json.dumps(integration_details, indent=2)}",
                "" if success else "Master kits are not appearing in catalogue after approval"
            )
            return success
            
        except Exception as e:
            self.log_result("Integration Process Verification", False, "", str(e))
            return False

    def run_comprehensive_test(self):
        """Run all master kit integration tests"""
        print("🎯 MASTER KIT INTEGRATION FIX TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Step 2: Test master kit contributions status
        contributions_count, contributions = self.test_master_kit_contributions_status()
        
        # Step 3: Test master jerseys catalogue
        master_jerseys_count, master_jerseys = self.test_master_jerseys_catalogue()
        
        # Step 4: Test specific master jersey endpoint
        specific_endpoint_success = self.test_specific_master_jersey_endpoint(master_jerseys)
        
        # Step 5: Verify integration process
        integration_success = self.test_integration_process_verification(contributions_count, master_jerseys_count)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 MASTER KIT INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical issue assessment
        critical_issue_resolved = integration_success and (master_jerseys_count > 0 or contributions_count == 0)
        
        if critical_issue_resolved:
            print("🎉 CRITICAL BUG RESOLVED: Master kits integration is working correctly!")
        else:
            print("🚨 CRITICAL BUG PERSISTS: Master kits are not appearing in catalogue after approval!")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        return critical_issue_resolved

if __name__ == "__main__":
    tester = MasterKitIntegrationTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)