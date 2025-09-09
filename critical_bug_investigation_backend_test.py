#!/usr/bin/env python3
"""
Critical Bug Investigation - Backend Testing
Investigating two major issues:
1. Integration Issue: Approved team contributions (TK-TEAM-4156DC3C, etc.) not appearing in Teams Catalogue
2. View Link Issue: "view" link in Community DB leads to blank pages

Testing Required:
1. Test the GET /api/teams endpoint to see what specific error is occurring
2. Test if other catalogue endpoints (/api/brands, /api/competitions) are working
3. Check if the approved contributions exist in the database
4. Investigate if there's an integration function that should move approved contributions to main catalogue collections
5. Test the specific contribution detail endpoint for approved contributions
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-catalog-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class CriticalBugInvestigator:
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
        """Authenticate admin user and get JWT token"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Successfully authenticated admin user. Token length: {len(self.admin_token)}"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, "", "No token in response")
                    return False
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    "", 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def test_teams_endpoint_detailed(self):
        """Test GET /api/teams endpoint with detailed error analysis"""
        try:
            print("🔍 Testing GET /api/teams endpoint for Internal Server Error...")
            response = self.session.get(f"{API_BASE}/teams")
            
            if response.status_code == 200:
                data = response.json()
                teams_count = len(data) if isinstance(data, list) else len(data.get('teams', []))
                
                # Look for specific team contributions mentioned in the bug report
                tk_teams = []
                if isinstance(data, list):
                    for team in data:
                        if isinstance(team, dict):
                            topkit_ref = team.get('topkit_reference', '')
                            if 'TK-TEAM-' in topkit_ref:
                                tk_teams.append(topkit_ref)
                
                self.log_result(
                    "GET /api/teams - Success Analysis",
                    True,
                    f"Retrieved {teams_count} teams successfully. Found {len(tk_teams)} TK-TEAM references: {tk_teams}"
                )
                return data
            else:
                # Detailed error analysis
                error_details = f"HTTP {response.status_code}"
                try:
                    error_json = response.json()
                    error_details += f" - {error_json}"
                except:
                    error_details += f" - {response.text}"
                
                self.log_result(
                    "GET /api/teams - Internal Server Error",
                    False,
                    "",
                    error_details
                )
                return None
                
        except Exception as e:
            self.log_result("GET /api/teams - Exception", False, "", str(e))
            return None

    def test_other_catalogue_endpoints(self):
        """Test other catalogue endpoints to see if the issue is specific to teams"""
        endpoints = [
            ("/brands", "Brands Catalogue"),
            ("/competitions", "Competitions Catalogue"),
            ("/players", "Players Catalogue"),
            ("/master-jerseys", "Master Jerseys Catalogue")
        ]
        
        working_endpoints = []
        failing_endpoints = []
        
        for endpoint, description in endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else len(data.get('items', []))
                    working_endpoints.append(f"{endpoint} ({count} items)")
                    self.log_result(
                        f"GET {endpoint} - {description}",
                        True,
                        f"Retrieved {count} items successfully"
                    )
                else:
                    failing_endpoints.append(f"{endpoint} (HTTP {response.status_code})")
                    self.log_result(
                        f"GET {endpoint} - {description}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                failing_endpoints.append(f"{endpoint} (Exception)")
                self.log_result(f"GET {endpoint} - {description}", False, "", str(e))
        
        # Summary analysis
        if len(working_endpoints) > 0 and len(failing_endpoints) == 0:
            self.log_result(
                "Catalogue Endpoints Analysis",
                True,
                f"All catalogue endpoints working: {', '.join(working_endpoints)}"
            )
        elif len(failing_endpoints) > 0:
            self.log_result(
                "Catalogue Endpoints Analysis",
                False,
                f"Working: {', '.join(working_endpoints)}",
                f"Failing: {', '.join(failing_endpoints)}"
            )
        
        return working_endpoints, failing_endpoints

    def test_approved_contributions_exist(self):
        """Check if approved contributions exist in the database"""
        try:
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if response.status_code == 200:
                data = response.json()
                contributions = data if isinstance(data, list) else data.get('contributions', [])
                
                # Look for approved team contributions
                approved_teams = []
                pending_teams = []
                tk_team_contributions = []
                
                for contrib in contributions:
                    if isinstance(contrib, dict):
                        entity_type = contrib.get('entity_type', '')
                        status = contrib.get('status', '')
                        topkit_ref = contrib.get('topkit_reference', '')
                        
                        if entity_type == 'team':
                            if 'TK-TEAM-' in topkit_ref:
                                tk_team_contributions.append({
                                    'id': contrib.get('id'),
                                    'topkit_reference': topkit_ref,
                                    'status': status,
                                    'title': contrib.get('title', 'Unknown')
                                })
                            
                            if status == 'APPROVED':
                                approved_teams.append(contrib)
                            elif status == 'PENDING':
                                pending_teams.append(contrib)
                
                self.log_result(
                    "Approved Contributions Analysis",
                    True,
                    f"Found {len(contributions)} total contributions. "
                    f"Team contributions: {len(approved_teams)} approved, {len(pending_teams)} pending. "
                    f"TK-TEAM references: {len(tk_team_contributions)}"
                )
                
                # Detailed analysis of TK-TEAM contributions
                if tk_team_contributions:
                    print("   🔍 TK-TEAM Contributions Found:")
                    for tk_team in tk_team_contributions:
                        print(f"      - {tk_team['topkit_reference']}: {tk_team['title']} (Status: {tk_team['status']})")
                
                return {
                    'total_contributions': len(contributions),
                    'approved_teams': approved_teams,
                    'pending_teams': pending_teams,
                    'tk_team_contributions': tk_team_contributions
                }
            else:
                self.log_result(
                    "Approved Contributions Check",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Approved Contributions Check", False, "", str(e))
            return None

    def test_integration_function_investigation(self):
        """Investigate if there's an integration function that should move approved contributions to main collections"""
        try:
            # Check admin settings for auto-approval
            response = self.session.get(f"{API_BASE}/admin/settings")
            
            if response.status_code == 200:
                settings = response.json()
                auto_approval = settings.get("auto_approval_enabled", False)
                
                self.log_result(
                    "Integration Settings Check",
                    True,
                    f"Auto-approval enabled: {auto_approval}, Community voting: {settings.get('community_voting_enabled', False)}"
                )
                
                # Test creating a new team contribution to see if it auto-integrates
                test_team_data = {
                    "entity_type": "team",
                    "entity_id": None,
                    "title": "Integration Test Team - Critical Bug Investigation",
                    "description": "Testing if approved contributions auto-integrate to main teams collection",
                    "changes": {
                        "name": "Critical Bug Test FC",
                        "short_name": "CBT",
                        "country": "France",
                        "city": "Paris",
                        "founded_year": 2024,
                        "team_colors": ["Red", "White"]
                    }
                }
                
                create_response = self.session.post(f"{API_BASE}/contributions-v2/", json=test_team_data)
                
                if create_response.status_code in [200, 201]:
                    create_data = create_response.json()
                    contribution_id = create_data.get('id')
                    
                    # Check if it immediately appears in teams collection
                    teams_response = self.session.get(f"{API_BASE}/teams")
                    
                    if teams_response.status_code == 200:
                        teams_data = teams_response.json()
                        teams = teams_data if isinstance(teams_data, list) else teams_data.get('teams', [])
                        
                        integration_found = any(
                            team.get('name') == 'Critical Bug Test FC' 
                            for team in teams
                        )
                        
                        self.log_result(
                            "Auto-Integration Test",
                            integration_found,
                            f"Created contribution {contribution_id}. Team {'found' if integration_found else 'NOT found'} in main teams collection"
                        )
                        
                        return {
                            'auto_approval_enabled': auto_approval,
                            'contribution_created': contribution_id,
                            'auto_integrated': integration_found
                        }
                    else:
                        self.log_result(
                            "Auto-Integration Test - Teams Check",
                            False,
                            "",
                            f"Failed to check teams after contribution creation: HTTP {teams_response.status_code}"
                        )
                        return None
                else:
                    self.log_result(
                        "Auto-Integration Test - Contribution Creation",
                        False,
                        "",
                        f"Failed to create test contribution: HTTP {create_response.status_code}: {create_response.text}"
                    )
                    return None
            else:
                self.log_result(
                    "Integration Settings Check",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Integration Function Investigation", False, "", str(e))
            return None

    def test_contribution_detail_endpoints(self, tk_team_contributions):
        """Test the specific contribution detail endpoint for approved contributions"""
        if not tk_team_contributions:
            self.log_result(
                "Contribution Detail Endpoints Test",
                False,
                "",
                "No TK-TEAM contributions found to test"
            )
            return False
        
        working_details = []
        failing_details = []
        
        for tk_team in tk_team_contributions:
            contribution_id = tk_team['id']
            topkit_ref = tk_team['topkit_reference']
            
            try:
                # Test contribution detail endpoint
                response = self.session.get(f"{API_BASE}/contributions-v2/{contribution_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    working_details.append(f"{topkit_ref} (ID: {contribution_id})")
                    self.log_result(
                        f"Contribution Detail - {topkit_ref}",
                        True,
                        f"Successfully retrieved contribution details for {topkit_ref}"
                    )
                else:
                    failing_details.append(f"{topkit_ref} (HTTP {response.status_code})")
                    self.log_result(
                        f"Contribution Detail - {topkit_ref}",
                        False,
                        "",
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                failing_details.append(f"{topkit_ref} (Exception)")
                self.log_result(f"Contribution Detail - {topkit_ref}", False, "", str(e))
        
        # Summary
        if len(working_details) > 0:
            self.log_result(
                "Contribution Detail Endpoints Summary",
                len(failing_details) == 0,
                f"Working details: {', '.join(working_details)}",
                f"Failing details: {', '.join(failing_details)}" if failing_details else ""
            )
        
        return len(failing_details) == 0

    def test_view_link_investigation(self):
        """Investigate the view link issue in Community DB"""
        try:
            # Get contributions to test view links
            response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if response.status_code == 200:
                data = response.json()
                contributions = data if isinstance(data, list) else data.get('contributions', [])
                
                if contributions:
                    # Test the first few contributions
                    test_contributions = contributions[:3]  # Test first 3
                    
                    view_link_results = []
                    
                    for contrib in test_contributions:
                        contrib_id = contrib.get('id')
                        title = contrib.get('title', 'Unknown')
                        
                        if contrib_id:
                            # Test the contribution detail endpoint (what the view link should call)
                            detail_response = self.session.get(f"{API_BASE}/contributions-v2/{contrib_id}")
                            
                            if detail_response.status_code == 200:
                                detail_data = detail_response.json()
                                view_link_results.append(f"✅ {title[:30]}...")
                            else:
                                view_link_results.append(f"❌ {title[:30]}... (HTTP {detail_response.status_code})")
                    
                    success_count = sum(1 for result in view_link_results if result.startswith('✅'))
                    
                    self.log_result(
                        "View Link Investigation",
                        success_count == len(view_link_results),
                        f"Tested {len(view_link_results)} contribution detail endpoints. {success_count} working, {len(view_link_results) - success_count} failing",
                        f"Results: {', '.join(view_link_results)}" if success_count < len(view_link_results) else ""
                    )
                    
                    return success_count == len(view_link_results)
                else:
                    self.log_result(
                        "View Link Investigation",
                        False,
                        "",
                        "No contributions found to test view links"
                    )
                    return False
            else:
                self.log_result(
                    "View Link Investigation",
                    False,
                    "",
                    f"Failed to get contributions: HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("View Link Investigation", False, "", str(e))
            return False

    def run_critical_bug_investigation(self):
        """Run all critical bug investigation tests"""
        print("🚨 CRITICAL BUG INVESTIGATION - Backend Testing")
        print("Investigating Integration and View Link Issues")
        print("=" * 70)
        
        # Step 1: Authenticate admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test GET /api/teams endpoint for Internal Server Error
        print("\n🔍 ISSUE 1: Testing GET /api/teams endpoint for Internal Server Error")
        print("-" * 60)
        teams_data = self.test_teams_endpoint_detailed()
        
        # Step 3: Test other catalogue endpoints
        print("\n📊 COMPARATIVE ANALYSIS: Testing other catalogue endpoints")
        print("-" * 60)
        working_endpoints, failing_endpoints = self.test_other_catalogue_endpoints()
        
        # Step 4: Check if approved contributions exist
        print("\n🔍 DATABASE ANALYSIS: Checking approved contributions in database")
        print("-" * 60)
        contributions_data = self.test_approved_contributions_exist()
        
        # Step 5: Investigate integration function
        print("\n🔄 INTEGRATION ANALYSIS: Testing auto-integration functionality")
        print("-" * 60)
        integration_data = self.test_integration_function_investigation()
        
        # Step 6: Test contribution detail endpoints
        print("\n🔍 ISSUE 2: Testing contribution detail endpoints (view links)")
        print("-" * 60)
        if contributions_data and contributions_data.get('tk_team_contributions'):
            detail_success = self.test_contribution_detail_endpoints(contributions_data['tk_team_contributions'])
        else:
            detail_success = self.test_view_link_investigation()
        
        # Generate investigation summary
        self.generate_investigation_summary(teams_data, working_endpoints, failing_endpoints, contributions_data, integration_data, detail_success)
        
        return True

    def generate_investigation_summary(self, teams_data, working_endpoints, failing_endpoints, contributions_data, integration_data, detail_success):
        """Generate comprehensive investigation summary"""
        print("\n" + "=" * 70)
        print("📋 CRITICAL BUG INVESTIGATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        # Issue 1: Teams endpoint analysis
        if teams_data is not None:
            print("✅ ISSUE 1 RESOLVED: GET /api/teams endpoint is working correctly")
            if contributions_data and contributions_data.get('tk_team_contributions'):
                tk_teams = contributions_data['tk_team_contributions']
                approved_tk_teams = [t for t in tk_teams if t['status'] == 'APPROVED']
                if approved_tk_teams:
                    print(f"   - Found {len(approved_tk_teams)} approved TK-TEAM contributions")
                    print("   - Issue may be in frontend display or data filtering")
                else:
                    print("   - No approved TK-TEAM contributions found in database")
                    print("   - Contributions may still be pending approval")
        else:
            print("❌ ISSUE 1 CONFIRMED: GET /api/teams endpoint has Internal Server Error")
            print("   - This is the root cause of teams not appearing in catalogue")
        
        # Issue 2: View link analysis
        if detail_success:
            print("✅ ISSUE 2 RESOLVED: Contribution detail endpoints working correctly")
            print("   - View links should work properly")
        else:
            print("❌ ISSUE 2 CONFIRMED: Contribution detail endpoints have issues")
            print("   - This explains blank pages when clicking view links")
        
        # Integration analysis
        if integration_data:
            if integration_data.get('auto_integrated'):
                print("✅ AUTO-INTEGRATION: Working correctly")
                print("   - Approved contributions should appear in main catalogue")
            else:
                print("⚠️ AUTO-INTEGRATION: Not working as expected")
                print("   - Approved contributions may not auto-integrate to main collections")
        
        print("\n🛠️ RECOMMENDED FIXES:")
        print("-" * 30)
        
        if teams_data is None:
            print("1. 🔧 Fix GET /api/teams endpoint Internal Server Error")
            print("   - Check server logs for specific error details")
            print("   - Verify database connection and query syntax")
            print("   - Test with empty database to isolate data-related issues")
        
        if not detail_success:
            print("2. 🔧 Fix contribution detail endpoints")
            print("   - Check /api/contributions-v2/{id} endpoint implementation")
            print("   - Verify contribution ID format and database queries")
            print("   - Test with known contribution IDs")
        
        if integration_data and not integration_data.get('auto_integrated'):
            print("3. 🔧 Fix auto-integration pipeline")
            print("   - Verify auto-approval settings are properly configured")
            print("   - Check integration function that moves approved contributions")
            print("   - Test manual approval process if auto-approval fails")
        
        print("\n📊 ENDPOINT STATUS SUMMARY:")
        print("-" * 35)
        print(f"Working endpoints: {len(working_endpoints)}")
        for endpoint in working_endpoints:
            print(f"  ✅ {endpoint}")
        
        if failing_endpoints:
            print(f"Failing endpoints: {len(failing_endpoints)}")
            for endpoint in failing_endpoints:
                print(f"  ❌ {endpoint}")
        
        # Final assessment
        print("\n🎯 INVESTIGATION CONCLUSION:")
        print("-" * 35)
        
        critical_issues = []
        if teams_data is None:
            critical_issues.append("Teams endpoint Internal Server Error")
        if not detail_success:
            critical_issues.append("Contribution detail endpoints failing")
        
        if not critical_issues:
            print("✅ NO CRITICAL BACKEND ISSUES FOUND")
            print("   - Issues may be in frontend implementation or data state")
            print("   - Verify frontend routing and API integration")
        else:
            print(f"❌ {len(critical_issues)} CRITICAL BACKEND ISSUES IDENTIFIED:")
            for i, issue in enumerate(critical_issues, 1):
                print(f"   {i}. {issue}")
            print("   - These issues require immediate backend fixes")

if __name__ == "__main__":
    investigator = CriticalBugInvestigator()
    investigator.run_critical_bug_investigation()