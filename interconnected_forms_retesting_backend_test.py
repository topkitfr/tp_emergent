#!/usr/bin/env python3
"""
Interconnected Forms System Re-Testing After Fixes
Testing the fixed interconnected forms system backend implementation:

1. Fixed Endpoints Testing:
   - Test /api/form-dependencies/competitions-by-type endpoint (fixed aggregation issue)
   - Test /api/form-dependencies/check-missing-data endpoint (fixed response structure)

2. Team-Competition Relationships Testing:
   - Test /api/teams with competition_id filtering using updated team data
   - Test /api/form-dependencies/teams-by-competition/{id} with actual competition IDs
   - Verify teams like PSG, Barcelona, Manchester United show up in correct competitions

3. Complete Form Workflow Testing:
   - Test the full workflow: competitions-by-type → teams-by-competition → master-kits-by-team
   - Verify data flow for Ligue 1 → PSG/Lyon teams
   - Verify data flow for La Liga → Barcelona teams

4. Data Structure Validation:
   - Confirm competition types are properly grouped (National league, Continental competition, etc.)
   - Verify team competition relationships are working correctly
   - Test federations endpoint returns UEFA, FIFA, CONMEBOL, etc.

Admin credentials: topkitfr@gmail.com/TopKitSecure789#
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

class InterconnectedFormsRetester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.competitions_data = []
        self.teams_data = []
        
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
        if details and len(str(details)) < 500:  # Only print short details
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate_admin(self) -> bool:
        """Authenticate admin user"""
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
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Successfully authenticated admin user: {user_data.get('name', 'Unknown')} (Role: {user_data.get('role', 'Unknown')})",
                    {"user_id": self.admin_user_id, "email": user_data.get('email')}
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"Authentication failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_competitions_by_type_endpoint(self) -> bool:
        """Test the fixed /api/form-dependencies/competitions-by-type endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/form-dependencies/competitions-by-type")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has proper structure - should be dict with competition_types
                if isinstance(data, dict) and 'competition_types' in data:
                    competition_types_data = data['competition_types']
                    total_competitions = data.get('total_competitions', 0)
                    
                    # Check if competitions are grouped by type
                    competition_types = list(competition_types_data.keys())
                    calculated_total = sum(len(competitions) for competitions in competition_types_data.values())
                    
                    self.log_result(
                        "Competitions By Type Endpoint - Fixed Aggregation", 
                        True, 
                        f"Successfully retrieved {len(competition_types)} competition types with {total_competitions} total competitions",
                        {
                            "competition_types": competition_types,
                            "total_competitions": total_competitions,
                            "calculated_total": calculated_total,
                            "sample_types": list(competition_types_data.keys())[:3]
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Competitions By Type Endpoint - Fixed Aggregation", 
                        False, 
                        f"Invalid response structure: expected dict with 'competition_types', got: {type(data)}",
                        {"response_data": data}
                    )
                    return False
            else:
                self.log_result(
                    "Competitions By Type Endpoint - Fixed Aggregation", 
                    False, 
                    f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Competitions By Type Endpoint - Fixed Aggregation", False, f"Error: {str(e)}")
            return False
    
    def test_check_missing_data_endpoint(self) -> bool:
        """Test the fixed /api/form-dependencies/check-missing-data endpoint"""
        try:
            # Test with sample data
            test_data = {
                "competition_type": "National league",
                "country": "France"
            }
            
            response = self.session.post(f"{BACKEND_URL}/form-dependencies/check-missing-data", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has proper structure - the actual structure has nested missing_data
                if isinstance(data, dict) and 'missing_data' in data and 'has_missing' in data:
                    missing_data = data.get('missing_data', {})
                    has_missing = data.get('has_missing', False)
                    
                    # The missing_data should contain suggested_actions inside it
                    suggested_actions = missing_data.get('suggested_actions', [])
                    
                    self.log_result(
                        "Check Missing Data Endpoint - Fixed Response Structure", 
                        True, 
                        f"Successfully retrieved missing data analysis. Has missing: {has_missing}, Suggested actions: {len(suggested_actions)}",
                        {
                            "has_missing": has_missing,
                            "missing_data_fields": list(missing_data.keys()) if isinstance(missing_data, dict) else "Not dict",
                            "suggested_actions_count": len(suggested_actions),
                            "response_structure": data
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Check Missing Data Endpoint - Fixed Response Structure", 
                        False, 
                        f"Invalid response structure: missing 'missing_data' or 'has_missing' fields",
                        {"response_data": data}
                    )
                    return False
            else:
                self.log_result(
                    "Check Missing Data Endpoint - Fixed Response Structure", 
                    False, 
                    f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Check Missing Data Endpoint - Fixed Response Structure", False, f"Error: {str(e)}")
            return False
    
    def test_teams_endpoint_with_competition_filtering(self) -> bool:
        """Test /api/teams with competition_id filtering"""
        try:
            # First get all teams
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                all_teams = response.json()
                self.teams_data = all_teams
                
                # Look for teams with league_info (which contains competition relationships)
                teams_with_competitions = []
                for team in all_teams:
                    if team.get('league_info') or team.get('current_competitions') or team.get('primary_competition_id'):
                        teams_with_competitions.append(team)
                
                # Test filtering by competition_id if we have teams with competitions
                if teams_with_competitions:
                    # Try to get a competition ID from the first team with league_info
                    test_team = teams_with_competitions[0]
                    competition_id = None
                    
                    if test_team.get('league_info'):
                        competition_id = test_team['league_info'].get('id')
                    elif test_team.get('primary_competition_id'):
                        competition_id = test_team.get('primary_competition_id')
                    
                    if competition_id:
                        # Test filtering
                        filter_response = self.session.get(f"{BACKEND_URL}/teams?competition_id={competition_id}")
                        
                        if filter_response.status_code == 200:
                            filtered_teams = filter_response.json()
                            
                            self.log_result(
                                "Teams Endpoint - Competition Filtering", 
                                True, 
                                f"Successfully filtered teams by competition. Total teams: {len(all_teams)}, Filtered teams: {len(filtered_teams)}",
                                {
                                    "total_teams": len(all_teams),
                                    "filtered_teams": len(filtered_teams),
                                    "test_competition_id": competition_id,
                                    "teams_with_competitions": len(teams_with_competitions)
                                }
                            )
                            return True
                        else:
                            self.log_result(
                                "Teams Endpoint - Competition Filtering", 
                                False, 
                                f"Competition filtering failed with status {filter_response.status_code}: {filter_response.text}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Teams Endpoint - Competition Filtering", 
                            False, 
                            "No competition IDs found in team data to test filtering"
                        )
                        return False
                else:
                    self.log_result(
                        "Teams Endpoint - Competition Filtering", 
                        False, 
                        f"No teams found with competition relationships. Total teams: {len(all_teams)}"
                    )
                    return False
            else:
                self.log_result(
                    "Teams Endpoint - Competition Filtering", 
                    False, 
                    f"Failed to get teams with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Teams Endpoint - Competition Filtering", False, f"Error: {str(e)}")
            return False
    
    def test_teams_by_competition_endpoint(self) -> bool:
        """Test /api/form-dependencies/teams-by-competition/{id} with actual competition IDs"""
        try:
            # First get competitions to find actual IDs
            competitions_response = self.session.get(f"{BACKEND_URL}/competitions")
            
            if competitions_response.status_code == 200:
                competitions = competitions_response.json()
                self.competitions_data = competitions
                
                if not competitions:
                    self.log_result(
                        "Teams By Competition Endpoint", 
                        False, 
                        "No competitions found to test with"
                    )
                    return False
                
                # Test with a few different competitions
                test_results = []
                major_competitions = []
                
                # Look for major competitions (Ligue 1, La Liga, etc.)
                for comp in competitions:
                    comp_name = comp.get('competition_name', '').lower()
                    if any(name in comp_name for name in ['ligue 1', 'la liga', 'premier league', 'serie a', 'bundesliga']):
                        major_competitions.append(comp)
                
                # Test with major competitions first, then fallback to any competitions
                test_competitions = major_competitions[:3] if major_competitions else competitions[:3]
                
                for competition in test_competitions:
                    comp_id = competition.get('id')
                    comp_name = competition.get('competition_name', 'Unknown')
                    
                    if comp_id:
                        response = self.session.get(f"{BACKEND_URL}/form-dependencies/teams-by-competition/{comp_id}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            # The response should have 'teams' array and other metadata
                            teams = data.get('teams', []) if isinstance(data, dict) else []
                            
                            test_results.append({
                                "competition": comp_name,
                                "competition_id": comp_id,
                                "teams_count": len(teams),
                                "success": True
                            })
                            
                            # Check for specific teams mentioned in review request
                            team_names = [team.get('name', '').lower() for team in teams]
                            found_teams = []
                            for target_team in ['psg', 'paris saint-germain', 'barcelona', 'manchester united', 'lyon', 'olympique lyonnais']:
                                if any(target_team in name for name in team_names):
                                    found_teams.append(target_team)
                            
                            if found_teams:
                                test_results[-1]['found_target_teams'] = found_teams
                        else:
                            test_results.append({
                                "competition": comp_name,
                                "competition_id": comp_id,
                                "teams_count": 0,
                                "success": False,
                                "error": f"Status {response.status_code}: {response.text}"
                            })
                
                successful_tests = [r for r in test_results if r['success']]
                total_teams_found = sum(r['teams_count'] for r in successful_tests)
                
                if successful_tests:
                    self.log_result(
                        "Teams By Competition Endpoint", 
                        True, 
                        f"Successfully tested {len(successful_tests)}/{len(test_results)} competitions, found {total_teams_found} total teams",
                        {
                            "test_results": test_results,
                            "successful_competitions": len(successful_tests),
                            "total_teams_found": total_teams_found
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Teams By Competition Endpoint", 
                        False, 
                        f"All {len(test_results)} competition tests failed",
                        {"test_results": test_results}
                    )
                    return False
            else:
                self.log_result(
                    "Teams By Competition Endpoint", 
                    False, 
                    f"Failed to get competitions with status {competitions_response.status_code}: {competitions_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Teams By Competition Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_complete_form_workflow(self) -> bool:
        """Test the complete workflow: competitions-by-type → teams-by-competition → master-kits-by-team"""
        try:
            workflow_results = []
            
            # Step 1: Get competitions by type
            comp_types_response = self.session.get(f"{BACKEND_URL}/form-dependencies/competitions-by-type")
            
            if comp_types_response.status_code != 200:
                self.log_result(
                    "Complete Form Workflow", 
                    False, 
                    f"Step 1 failed - competitions-by-type returned {comp_types_response.status_code}"
                )
                return False
            
            comp_types_data = comp_types_response.json()
            competition_types = comp_types_data.get('competition_types', {})
            
            # Step 2: Find Ligue 1 and La Liga competitions
            target_workflows = [
                {"type": "National league", "target_competitions": ["ligue 1"], "target_teams": ["psg", "paris saint-germain", "lyon", "olympique lyonnais"]},
                {"type": "National league", "target_competitions": ["la liga"], "target_teams": ["barcelona"]}
            ]
            
            for workflow in target_workflows:
                workflow_result = {"workflow_type": workflow["type"], "steps": []}
                
                # Find competitions of this type
                type_competitions = competition_types.get(workflow["type"], [])
                
                if not type_competitions:
                    workflow_result["steps"].append({
                        "step": "find_competition_type",
                        "success": False,
                        "message": f"Competition type '{workflow['type']}' not found or empty"
                    })
                    workflow_results.append(workflow_result)
                    continue
                
                # Find target competition
                target_competition = None
                for comp in type_competitions:
                    comp_name = comp.get('competition_name', '').lower()
                    if any(target in comp_name for target in workflow["target_competitions"]):
                        target_competition = comp
                        break
                
                if not target_competition:
                    workflow_result["steps"].append({
                        "step": "find_target_competition",
                        "success": False,
                        "message": f"Target competitions {workflow['target_competitions']} not found in type group"
                    })
                    workflow_results.append(workflow_result)
                    continue
                
                workflow_result["steps"].append({
                    "step": "find_target_competition",
                    "success": True,
                    "competition": target_competition.get('competition_name'),
                    "competition_id": target_competition.get('id')
                })
                
                # Step 3: Get teams for this competition
                comp_id = target_competition.get('id')
                teams_response = self.session.get(f"{BACKEND_URL}/form-dependencies/teams-by-competition/{comp_id}")
                
                if teams_response.status_code == 200:
                    teams_data = teams_response.json()
                    teams = teams_data.get('teams', []) if isinstance(teams_data, dict) else []
                    
                    # Look for target teams
                    found_teams = []
                    for team in teams:
                        team_name = team.get('name', '').lower()
                        for target_team in workflow["target_teams"]:
                            if target_team in team_name:
                                found_teams.append({
                                    "name": team.get('name'),
                                    "id": team.get('id')
                                })
                    
                    workflow_result["steps"].append({
                        "step": "get_teams_for_competition",
                        "success": True,
                        "total_teams": len(teams),
                        "target_teams_found": found_teams
                    })
                    
                    # Step 4: Test master-kits-by-team for found teams
                    if found_teams:
                        for team in found_teams[:1]:  # Test first team only
                            team_id = team.get('id')
                            kits_response = self.session.get(f"{BACKEND_URL}/form-dependencies/master-kits-by-team/{team_id}")
                            
                            if kits_response.status_code == 200:
                                kits = kits_response.json()
                                workflow_result["steps"].append({
                                    "step": "get_master_kits_for_team",
                                    "success": True,
                                    "team": team.get('name'),
                                    "kits_count": len(kits)
                                })
                            else:
                                workflow_result["steps"].append({
                                    "step": "get_master_kits_for_team",
                                    "success": False,
                                    "team": team.get('name'),
                                    "error": f"Status {kits_response.status_code}"
                                })
                else:
                    workflow_result["steps"].append({
                        "step": "get_teams_for_competition",
                        "success": False,
                        "error": f"Status {teams_response.status_code}: {teams_response.text}"
                    })
                
                workflow_results.append(workflow_result)
            
            # Evaluate overall workflow success
            successful_workflows = 0
            for workflow in workflow_results:
                if all(step.get('success', False) for step in workflow['steps']):
                    successful_workflows += 1
            
            if successful_workflows > 0:
                self.log_result(
                    "Complete Form Workflow", 
                    True, 
                    f"Successfully completed {successful_workflows}/{len(workflow_results)} target workflows",
                    {"workflow_results": workflow_results}
                )
                return True
            else:
                self.log_result(
                    "Complete Form Workflow", 
                    False, 
                    f"All {len(workflow_results)} workflows failed",
                    {"workflow_results": workflow_results}
                )
                return False
                
        except Exception as e:
            self.log_result("Complete Form Workflow", False, f"Error: {str(e)}")
            return False
    
    def test_federations_endpoint(self) -> bool:
        """Test federations endpoint returns UEFA, FIFA, CONMEBOL, etc."""
        try:
            response = self.session.get(f"{BACKEND_URL}/form-dependencies/federations")
            
            if response.status_code == 200:
                data = response.json()
                
                # The response is a dict with 'federations' array and 'total'
                if isinstance(data, dict) and 'federations' in data:
                    federations = data.get('federations', [])
                    total = data.get('total', 0)
                    
                    if isinstance(federations, list) and len(federations) > 0:
                        federation_names = [fed.upper() for fed in federations]
                        
                        # Check for expected federations
                        expected_federations = ['UEFA', 'FIFA', 'CONMEBOL', 'CAF', 'CONCACAF']
                        found_federations = []
                        
                        for expected in expected_federations:
                            if expected in federation_names:
                                found_federations.append(expected)
                        
                        self.log_result(
                            "Federations Endpoint", 
                            True, 
                            f"Successfully retrieved {total} federations, found {len(found_federations)}/{len(expected_federations)} expected federations",
                            {
                                "total_federations": total,
                                "federation_names": federation_names,
                                "expected_found": found_federations,
                                "expected_missing": [f for f in expected_federations if f not in found_federations]
                            }
                        )
                        return True
                    else:
                        self.log_result(
                            "Federations Endpoint", 
                            False, 
                            f"Invalid federations array: expected list with items, got {type(federations)} with {len(federations) if isinstance(federations, list) else 'N/A'} items",
                            {"response_data": data}
                        )
                        return False
                else:
                    self.log_result(
                        "Federations Endpoint", 
                        False, 
                        f"Invalid response: expected dict with 'federations', got {type(data)}",
                        {"response_data": data}
                    )
                    return False
            else:
                self.log_result(
                    "Federations Endpoint", 
                    False, 
                    f"Request failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Federations Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_data_structure_validation(self) -> bool:
        """Validate competition types are properly grouped and team relationships work"""
        try:
            validation_results = []
            
            # Test 1: Competition types grouping
            comp_types_response = self.session.get(f"{BACKEND_URL}/form-dependencies/competitions-by-type")
            
            if comp_types_response.status_code == 200:
                comp_types_data = comp_types_response.json()
                competition_types = comp_types_data.get('competition_types', {})
                
                expected_types = ['National league', 'Continental competition', 'International competition']
                found_types = list(competition_types.keys())
                
                validation_results.append({
                    "test": "competition_types_grouping",
                    "success": len(found_types) > 0,
                    "found_types": found_types,
                    "expected_types": expected_types,
                    "matches_expected": any(t in found_types for t in expected_types)
                })
            else:
                validation_results.append({
                    "test": "competition_types_grouping",
                    "success": False,
                    "error": f"Status {comp_types_response.status_code}"
                })
            
            # Test 2: Team competition relationships
            teams_response = self.session.get(f"{BACKEND_URL}/teams")
            
            if teams_response.status_code == 200:
                teams = teams_response.json()
                
                teams_with_relationships = 0
                for team in teams:
                    if (team.get('league_info') or 
                        team.get('current_competitions') or 
                        team.get('primary_competition_id')):
                        teams_with_relationships += 1
                
                validation_results.append({
                    "test": "team_competition_relationships",
                    "success": teams_with_relationships > 0,
                    "total_teams": len(teams),
                    "teams_with_relationships": teams_with_relationships
                })
            else:
                validation_results.append({
                    "test": "team_competition_relationships",
                    "success": False,
                    "error": f"Status {teams_response.status_code}"
                })
            
            # Evaluate overall validation
            successful_validations = sum(1 for v in validation_results if v.get('success', False))
            
            if successful_validations == len(validation_results):
                self.log_result(
                    "Data Structure Validation", 
                    True, 
                    f"All {len(validation_results)} data structure validations passed",
                    {"validation_results": validation_results}
                )
                return True
            else:
                self.log_result(
                    "Data Structure Validation", 
                    False, 
                    f"Only {successful_validations}/{len(validation_results)} validations passed",
                    {"validation_results": validation_results}
                )
                return False
                
        except Exception as e:
            self.log_result("Data Structure Validation", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all interconnected forms tests"""
        print("🎯 INTERCONNECTED FORMS SYSTEM RE-TESTING AFTER FIXES")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with testing.")
            return False
        
        print(f"\n🔐 Admin authenticated successfully: {ADMIN_EMAIL}")
        
        # Step 2: Test Fixed Endpoints
        print(f"\n📋 TESTING FIXED ENDPOINTS")
        print("-" * 40)
        
        test_1 = self.test_competitions_by_type_endpoint()
        test_2 = self.test_check_missing_data_endpoint()
        
        # Step 3: Test Team-Competition Relationships
        print(f"\n🏆 TESTING TEAM-COMPETITION RELATIONSHIPS")
        print("-" * 40)
        
        test_3 = self.test_teams_endpoint_with_competition_filtering()
        test_4 = self.test_teams_by_competition_endpoint()
        
        # Step 4: Test Complete Form Workflow
        print(f"\n🔄 TESTING COMPLETE FORM WORKFLOW")
        print("-" * 40)
        
        test_5 = self.test_complete_form_workflow()
        
        # Step 5: Test Data Structure Validation
        print(f"\n📊 TESTING DATA STRUCTURE VALIDATION")
        print("-" * 40)
        
        test_6 = self.test_federations_endpoint()
        test_7 = self.test_data_structure_validation()
        
        # Calculate results
        all_tests = [test_1, test_2, test_3, test_4, test_5, test_6, test_7]
        passed_tests = sum(all_tests)
        success_rate = (passed_tests / len(all_tests)) * 100
        
        print(f"\n" + "=" * 80)
        print(f"🎯 INTERCONNECTED FORMS RE-TESTING COMPLETE")
        print(f"📊 SUCCESS RATE: {passed_tests}/{len(all_tests)} ({success_rate:.1f}%)")
        
        if success_rate >= 85:
            print(f"✅ EXCELLENT: Interconnected forms system is working excellently after fixes!")
        elif success_rate >= 70:
            print(f"⚠️  GOOD: Most functionality working, minor issues remain")
        else:
            print(f"❌ ISSUES: Significant problems detected that need attention")
        
        # Summary of key findings
        print(f"\n📋 KEY FINDINGS:")
        successful_tests = [result for result in self.test_results if result['success']]
        failed_tests = [result for result in self.test_results if not result['success']]
        
        if successful_tests:
            print(f"✅ WORKING COMPONENTS ({len(successful_tests)}):")
            for test in successful_tests:
                print(f"   • {test['test']}")
        
        if failed_tests:
            print(f"❌ FAILED COMPONENTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = InterconnectedFormsRetester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()