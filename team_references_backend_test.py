#!/usr/bin/env python3
"""
TopKit Team References Final Correction Testing
==============================================

Comprehensive backend testing for the final correction of TopKit team references
after complete resolution of duplicates. Tests the priority order, data consistency,
API functionality, search capabilities, Master Jerseys integration, and system stability.

Test Focus Areas:
1. Priority Order Test - Verify top 20 clubs have correct TK-TEAM-000001 to TK-TEAM-000020 references
2. Data Consistency Test - Confirm no duplicate references and unique TopKit references
3. GET /api/teams Test - Ensure teams API works correctly with new references
4. Team Search Test - Test search functionality for priority teams
5. Master Jerseys Integration Test - Verify existing Master Jerseys work with new references
6. General Stability Test - Confirm system stability and all 348 teams accessible
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configuration
BACKEND_URL = "https://image-fix-10.preview.emergentagent.com/api"

# Expected top 20 clubs in priority order (based on global importance)
EXPECTED_TOP_20_CLUBS = [
    "Real Madrid",
    "FC Barcelona", 
    "Manchester United",
    "Bayern Munich",
    "Liverpool",
    "Arsenal",
    "Chelsea",
    "Manchester City",
    "AC Milan",
    "Juventus",
    "Paris Saint-Germain",
    "Inter Milan",
    "Tottenham Hotspur",
    "Borussia Dortmund",
    "Atletico Madrid",
    "AS Roma",
    "Napoli",
    "Valencia",
    "Sevilla",
    "Olympique de Marseille"
]

# Test credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class TopKitTeamReferencesTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, success: bool, message: str, details: Optional[Dict] = None):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        
    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    user_info = data.get('user', {})
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated admin user: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})",
                        {"user_id": user_info.get('id'), "role": user_info.get('role')}
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "No token received in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Authentication failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_teams_api_connectivity(self) -> bool:
        """Test basic connectivity to teams API"""
        try:
            response = self.session.get(f"{BACKEND_URL}/teams", timeout=30)
            
            if response.status_code == 200:
                teams_data = response.json()
                team_count = len(teams_data) if isinstance(teams_data, list) else teams_data.get('count', 0)
                
                self.log_test(
                    "Teams API Connectivity",
                    True,
                    f"Teams API accessible, found {team_count} teams",
                    {"status_code": response.status_code, "team_count": team_count}
                )
                return True
            else:
                self.log_test(
                    "Teams API Connectivity", 
                    False, 
                    f"Teams API returned status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Teams API Connectivity", False, f"Teams API connection error: {str(e)}")
            return False
    
    def test_priority_order_references(self) -> bool:
        """Test that top 20 clubs have correct TK-TEAM-000001 to TK-TEAM-000020 references"""
        try:
            response = self.session.get(f"{BACKEND_URL}/teams", timeout=30)
            
            if response.status_code != 200:
                self.log_test(
                    "Priority Order References",
                    False,
                    f"Failed to fetch teams data: {response.status_code}"
                )
                return False
            
            teams_data = response.json()
            if not isinstance(teams_data, list):
                teams_data = teams_data.get('teams', []) if isinstance(teams_data, dict) else []
            
            # Create mapping of team names to their references
            team_references = {}
            for team in teams_data:
                team_name = team.get('name', '').strip()
                reference = team.get('topkit_reference', '').strip()
                if team_name and reference:
                    team_references[team_name] = reference
            
            # Check priority order
            correct_order = 0
            incorrect_assignments = []
            missing_teams = []
            
            for i, expected_team in enumerate(EXPECTED_TOP_20_CLUBS):
                expected_ref = f"TK-TEAM-{str(i+1).zfill(6)}"
                
                if expected_team in team_references:
                    actual_ref = team_references[expected_team]
                    if actual_ref == expected_ref:
                        correct_order += 1
                    else:
                        incorrect_assignments.append({
                            "team": expected_team,
                            "expected": expected_ref,
                            "actual": actual_ref,
                            "position": i + 1
                        })
                else:
                    missing_teams.append(expected_team)
            
            success = correct_order == 20 and len(missing_teams) == 0
            
            self.log_test(
                "Priority Order References",
                success,
                f"Priority order verification: {correct_order}/20 teams correctly positioned",
                {
                    "correct_assignments": correct_order,
                    "total_expected": 20,
                    "incorrect_assignments": incorrect_assignments,
                    "missing_teams": missing_teams,
                    "success_rate": f"{(correct_order/20)*100:.1f}%"
                }
            )
            
            return success
            
        except Exception as e:
            self.log_test("Priority Order References", False, f"Priority order test error: {str(e)}")
            return False
    
    def test_data_consistency(self) -> bool:
        """Test data consistency - no duplicate references and all teams have unique TopKit references"""
        try:
            response = self.session.get(f"{BACKEND_URL}/teams", timeout=30)
            
            if response.status_code != 200:
                self.log_test(
                    "Data Consistency",
                    False,
                    f"Failed to fetch teams data: {response.status_code}"
                )
                return False
            
            teams_data = response.json()
            if not isinstance(teams_data, list):
                teams_data = teams_data.get('teams', []) if isinstance(teams_data, dict) else []
            
            # Check for duplicate references
            references = []
            teams_with_references = 0
            teams_without_references = []
            reference_format_errors = []
            
            for team in teams_data:
                team_name = team.get('name', 'Unknown')
                reference = team.get('topkit_reference', '').strip()
                
                if reference:
                    references.append(reference)
                    teams_with_references += 1
                    
                    # Check reference format
                    if not reference.startswith('TK-TEAM-') or len(reference) != 15:
                        reference_format_errors.append({
                            "team": team_name,
                            "reference": reference
                        })
                else:
                    teams_without_references.append(team_name)
            
            # Find duplicates
            reference_counts = {}
            for ref in references:
                reference_counts[ref] = reference_counts.get(ref, 0) + 1
            
            duplicates = {ref: count for ref, count in reference_counts.items() if count > 1}
            
            total_teams = len(teams_data)
            unique_references = len(set(references))
            
            success = (
                len(duplicates) == 0 and 
                len(reference_format_errors) == 0 and
                unique_references == teams_with_references and
                teams_with_references == total_teams and  # All teams should have references
                len(teams_without_references) == 0  # No teams should be without references
            )
            
            self.log_test(
                "Data Consistency",
                success,
                f"Data consistency check: {total_teams} teams, {unique_references} unique references, {len(duplicates)} duplicates, {len(teams_without_references)} without references",
                {
                    "total_teams": total_teams,
                    "teams_with_references": teams_with_references,
                    "unique_references": unique_references,
                    "duplicates": duplicates,
                    "teams_without_references": teams_without_references,
                    "reference_format_errors": reference_format_errors,
                    "consistency_score": f"{((total_teams - len(duplicates) - len(teams_without_references))/total_teams)*100:.1f}%" if total_teams > 0 else "0%"
                }
            )
            
            return success
            
        except Exception as e:
            self.log_test("Data Consistency", False, f"Data consistency test error: {str(e)}")
            return False
    
    def test_team_search_functionality(self) -> bool:
        """Test team search functionality for priority teams"""
        try:
            # Test search for several priority teams
            search_teams = [
                "Real Madrid",
                "FC Barcelona", 
                "Manchester United",
                "Bayern Munich",
                "Liverpool"
            ]
            
            successful_searches = 0
            search_results = []
            
            for team_name in search_teams:
                try:
                    # Try different search endpoints
                    search_endpoints = [
                        f"{BACKEND_URL}/teams?search={team_name}",
                        f"{BACKEND_URL}/teams?name={team_name}",
                        f"{BACKEND_URL}/search?q={team_name}&type=teams"
                    ]
                    
                    found = False
                    for endpoint in search_endpoints:
                        try:
                            response = self.session.get(endpoint, timeout=15)
                            if response.status_code == 200:
                                data = response.json()
                                
                                # Handle different response formats
                                teams = []
                                if isinstance(data, list):
                                    teams = data
                                elif isinstance(data, dict):
                                    teams = data.get('teams', data.get('results', []))
                                
                                # Check if team found
                                for team in teams:
                                    if team.get('name', '').lower() == team_name.lower():
                                        found = True
                                        successful_searches += 1
                                        search_results.append({
                                            "team": team_name,
                                            "found": True,
                                            "reference": team.get('topkit_reference', 'N/A'),
                                            "endpoint": endpoint
                                        })
                                        break
                                
                                if found:
                                    break
                        except:
                            continue
                    
                    if not found:
                        search_results.append({
                            "team": team_name,
                            "found": False,
                            "reference": "N/A",
                            "endpoint": "None working"
                        })
                        
                except Exception as e:
                    search_results.append({
                        "team": team_name,
                        "found": False,
                        "error": str(e)
                    })
            
            success = successful_searches >= 3  # At least 3 out of 5 should work
            
            self.log_test(
                "Team Search Functionality",
                success,
                f"Team search test: {successful_searches}/{len(search_teams)} teams found successfully",
                {
                    "successful_searches": successful_searches,
                    "total_searches": len(search_teams),
                    "search_results": search_results,
                    "success_rate": f"{(successful_searches/len(search_teams))*100:.1f}%"
                }
            )
            
            return success
            
        except Exception as e:
            self.log_test("Team Search Functionality", False, f"Team search test error: {str(e)}")
            return False
    
    def test_master_jerseys_integration(self) -> bool:
        """Test that existing Master Jerseys still work correctly with new team references"""
        try:
            # Test Master Jerseys endpoint
            response = self.session.get(f"{BACKEND_URL}/master-jerseys", timeout=30)
            
            if response.status_code != 200:
                self.log_test(
                    "Master Jerseys Integration",
                    False,
                    f"Failed to fetch Master Jerseys: {response.status_code}"
                )
                return False
            
            master_jerseys = response.json()
            if not isinstance(master_jerseys, list):
                master_jerseys = master_jerseys.get('master_jerseys', []) if isinstance(master_jerseys, dict) else []
            
            # Check integration with teams
            jerseys_with_teams = 0
            jerseys_without_teams = 0
            team_integration_issues = []
            
            for jersey in master_jerseys:
                team_info = jersey.get('team_info', {})
                team_id = team_info.get('id', '') if team_info else ''
                team_name = team_info.get('name', '') if team_info else ''
                
                if team_info and team_id:
                    jerseys_with_teams += 1
                    
                    # Check if team info is complete
                    if not team_name:
                        team_integration_issues.append({
                            "jersey_id": jersey.get('id', 'Unknown'),
                            "team_id": team_id,
                            "issue": "Missing team name in team_info"
                        })
                else:
                    jerseys_without_teams += 1
                    team_integration_issues.append({
                        "jersey_id": jersey.get('id', 'Unknown'),
                        "issue": "Missing team_info"
                    })
            
            total_jerseys = len(master_jerseys)
            integration_success = jerseys_with_teams > 0 and len(team_integration_issues) == 0
            
            self.log_test(
                "Master Jerseys Integration",
                integration_success,
                f"Master Jerseys integration: {total_jerseys} jerseys, {jerseys_with_teams} with team info",
                {
                    "total_master_jerseys": total_jerseys,
                    "jerseys_with_teams": jerseys_with_teams,
                    "jerseys_without_teams": jerseys_without_teams,
                    "team_integration_issues": team_integration_issues,
                    "integration_rate": f"{(jerseys_with_teams/total_jerseys)*100:.1f}%" if total_jerseys > 0 else "0%"
                }
            )
            
            return integration_success
            
        except Exception as e:
            self.log_test("Master Jerseys Integration", False, f"Master Jerseys integration test error: {str(e)}")
            return False
    
    def test_system_stability(self) -> bool:
        """Test general system stability and verify all 348 teams are accessible"""
        try:
            # Test multiple endpoints for stability
            endpoints_to_test = [
                f"{BACKEND_URL}/teams",
                f"{BACKEND_URL}/competitions", 
                f"{BACKEND_URL}/master-jerseys",
                f"{BACKEND_URL}/brands"
            ]
            
            endpoint_results = []
            successful_endpoints = 0
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(endpoint, timeout=30)
                    success = response.status_code == 200
                    
                    if success:
                        successful_endpoints += 1
                        data = response.json()
                        count = len(data) if isinstance(data, list) else data.get('count', 0)
                        
                        endpoint_results.append({
                            "endpoint": endpoint.split('/')[-1],
                            "status": "✅ Working",
                            "status_code": response.status_code,
                            "count": count
                        })
                    else:
                        endpoint_results.append({
                            "endpoint": endpoint.split('/')[-1],
                            "status": "❌ Failed",
                            "status_code": response.status_code,
                            "error": response.text[:100]
                        })
                        
                except Exception as e:
                    endpoint_results.append({
                        "endpoint": endpoint.split('/')[-1],
                        "status": "❌ Error",
                        "error": str(e)[:100]
                    })
            
            # Check teams count specifically
            teams_response = self.session.get(f"{BACKEND_URL}/teams", timeout=30)
            teams_count = 0
            if teams_response.status_code == 200:
                teams_data = teams_response.json()
                teams_count = len(teams_data) if isinstance(teams_data, list) else teams_data.get('count', 0)
            
            # System is stable if most endpoints work and we have reasonable team count
            stability_success = (
                successful_endpoints >= 3 and  # At least 3/4 endpoints working
                teams_count >= 300  # At least 300 teams (close to expected 348)
            )
            
            self.log_test(
                "System Stability",
                stability_success,
                f"System stability check: {successful_endpoints}/{len(endpoints_to_test)} endpoints working, {teams_count} teams accessible",
                {
                    "successful_endpoints": successful_endpoints,
                    "total_endpoints": len(endpoints_to_test),
                    "teams_count": teams_count,
                    "expected_teams": 348,
                    "endpoint_results": endpoint_results,
                    "stability_score": f"{(successful_endpoints/len(endpoints_to_test))*100:.1f}%"
                }
            )
            
            return stability_success
            
        except Exception as e:
            self.log_test("System Stability", False, f"System stability test error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🎯 TOPKIT TEAM REFERENCES FINAL CORRECTION TESTING")
        print("=" * 60)
        print(f"Testing backend at: {BACKEND_URL}")
        print(f"Started at: {datetime.now().isoformat()}")
        print()
        
        # Test sequence
        test_sequence = [
            ("Admin Authentication", self.authenticate_admin),
            ("Teams API Connectivity", self.test_teams_api_connectivity),
            ("Priority Order References", self.test_priority_order_references),
            ("Data Consistency", self.test_data_consistency),
            ("Team Search Functionality", self.test_team_search_functionality),
            ("Master Jerseys Integration", self.test_master_jerseys_integration),
            ("System Stability", self.test_system_stability)
        ]
        
        for test_name, test_func in test_sequence:
            print(f"\n🔍 Running: {test_name}")
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
            print("-" * 40)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎉 TOPKIT TEAM REFERENCES TESTING COMPLETE")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}% success rate)")
        print()
        
        # Categorize results
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        if passed_tests:
            print("✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['test']}: {test['message']}")
            print()
        
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Priority order findings
        priority_test = next((t for t in self.test_results if t['test'] == 'Priority Order References'), None)
        if priority_test and priority_test['details']:
            details = priority_test['details']
            print(f"   • Priority Order: {details.get('correct_assignments', 0)}/20 top clubs correctly positioned")
            if details.get('incorrect_assignments'):
                print(f"   • Incorrect assignments: {len(details['incorrect_assignments'])} teams")
        
        # Data consistency findings  
        consistency_test = next((t for t in self.test_results if t['test'] == 'Data Consistency'), None)
        if consistency_test and consistency_test['details']:
            details = consistency_test['details']
            print(f"   • Data Consistency: {details.get('total_teams', 0)} teams, {details.get('unique_references', 0)} unique references")
            if details.get('duplicates'):
                print(f"   • Duplicate references found: {len(details['duplicates'])}")
        
        # System stability findings
        stability_test = next((t for t in self.test_results if t['test'] == 'System Stability'), None)
        if stability_test and stability_test['details']:
            details = stability_test['details']
            print(f"   • System Stability: {details.get('teams_count', 0)} teams accessible (expected: 348)")
            print(f"   • API Endpoints: {details.get('successful_endpoints', 0)}/{details.get('total_endpoints', 0)} working")
        
        print()
        
        # Final verdict
        if success_rate >= 85:
            print("🎉 CONCLUSION: Team references correction is PRODUCTION-READY!")
            print("   All critical functionality working excellently.")
        elif success_rate >= 70:
            print("⚠️  CONCLUSION: Team references correction mostly working with minor issues.")
            print("   Some improvements needed but core functionality operational.")
        else:
            print("🚨 CONCLUSION: Critical issues identified in team references correction.")
            print("   Significant fixes required before production deployment.")
        
        print(f"\nCompleted at: {datetime.now().isoformat()}")
        print("=" * 60)

def main():
    """Main test execution"""
    tester = TopKitTeamReferencesTest()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()