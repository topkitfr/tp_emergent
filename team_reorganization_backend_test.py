#!/usr/bin/env python3
"""
TopKit Team Reorganization Backend Testing
Testing the massive team reorganization with new references based on global importance

Test Areas:
1. Test des équipes prioritaires - Verify first 20 clubs have correct references TK-TEAM-000001 to TK-TEAM-000020
2. Test GET /api/teams - Ensure all teams accessible with new data (countries, leagues, colors)
3. Test de recherche équipes - Test search by name with reorganized clubs
4. Test d'intégration Master Jerseys - Verify Master Jerseys work with new team references
5. Test des nouvelles équipes - Confirm new teams from CSV are accessible
6. Test de cohérence des données - Verify all teams have unique and valid TopKit references
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://mongodb-routing.preview.emergentagent.com/api"

# Expected priority teams (first 20 clubs by global importance)
PRIORITY_TEAMS = [
    {"name": "Real Madrid", "reference": "TK-TEAM-000001", "country": "Spain", "league": "La Liga"},
    {"name": "FC Barcelona", "reference": "TK-TEAM-000002", "country": "Spain", "league": "La Liga"},
    {"name": "Manchester United", "reference": "TK-TEAM-000003", "country": "England", "league": "Premier League"},
    {"name": "Liverpool", "reference": "TK-TEAM-000004", "country": "England", "league": "Premier League"},
    {"name": "Bayern Munich", "reference": "TK-TEAM-000005", "country": "Germany", "league": "Bundesliga"},
    {"name": "Paris Saint-Germain", "reference": "TK-TEAM-000006", "country": "France", "league": "Ligue 1"},
    {"name": "Chelsea", "reference": "TK-TEAM-000007", "country": "England", "league": "Premier League"},
    {"name": "Manchester City", "reference": "TK-TEAM-000008", "country": "England", "league": "Premier League"},
    {"name": "Arsenal", "reference": "TK-TEAM-000009", "country": "England", "league": "Premier League"},
    {"name": "AC Milan", "reference": "TK-TEAM-000010", "country": "Italy", "league": "Serie A"},
    {"name": "Juventus", "reference": "TK-TEAM-000011", "country": "Italy", "league": "Serie A"},
    {"name": "Inter Milan", "reference": "TK-TEAM-000012", "country": "Italy", "league": "Serie A"},
    {"name": "Borussia Dortmund", "reference": "TK-TEAM-000013", "country": "Germany", "league": "Bundesliga"},
    {"name": "Atletico Madrid", "reference": "TK-TEAM-000014", "country": "Spain", "league": "La Liga"},
    {"name": "Tottenham", "reference": "TK-TEAM-000015", "country": "England", "league": "Premier League"},
    {"name": "AS Roma", "reference": "TK-TEAM-000016", "country": "Italy", "league": "Serie A"},
    {"name": "Napoli", "reference": "TK-TEAM-000017", "country": "Italy", "league": "Serie A"},
    {"name": "Olympique de Marseille", "reference": "TK-TEAM-000018", "country": "France", "league": "Ligue 1"},
    {"name": "AS Monaco", "reference": "TK-TEAM-000019", "country": "France", "league": "Ligue 1"},
    {"name": "Benfica", "reference": "TK-TEAM-000020", "country": "Portugal", "league": "Liga Portugal"}
]

# Test search terms for reorganized clubs
SEARCH_TEST_CASES = [
    {"query": "Real Madrid", "expected_count": 1, "expected_reference": "TK-TEAM-000001"},
    {"query": "Barcelona", "expected_count": 1, "expected_reference": "TK-TEAM-000002"},
    {"query": "Manchester United", "expected_count": 1, "expected_reference": "TK-TEAM-000003"},
    {"query": "Liverpool", "expected_count": 1, "expected_reference": "TK-TEAM-000004"},
    {"query": "Bayern", "expected_count": 1, "expected_reference": "TK-TEAM-000005"},
    {"query": "PSG", "expected_count": 1, "expected_reference": "TK-TEAM-000006"},
    {"query": "Chelsea", "expected_count": 1, "expected_reference": "TK-TEAM-000007"},
    {"query": "Manchester City", "expected_count": 1, "expected_reference": "TK-TEAM-000008"},
    {"query": "Arsenal", "expected_count": 1, "expected_reference": "TK-TEAM-000009"},
    {"query": "Milan", "expected_count": 2, "expected_references": ["TK-TEAM-000010", "TK-TEAM-000012"]}
]

class TeamReorganizationTester:
    def __init__(self):
        self.session = None
        self.results = {
            "priority_teams": {"passed": 0, "failed": 0, "details": []},
            "api_teams": {"passed": 0, "failed": 0, "details": []},
            "search_teams": {"passed": 0, "failed": 0, "details": []},
            "master_jerseys": {"passed": 0, "failed": 0, "details": []},
            "new_teams": {"passed": 0, "failed": 0, "details": []},
            "data_consistency": {"passed": 0, "failed": 0, "details": []}
        }
        
    async def setup(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to backend"""
        url = f"{BACKEND_URL}{endpoint}"
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.content_type == 'application/json':
                    data = await response.json()
                else:
                    data = {"text": await response.text()}
                return {
                    "status": response.status,
                    "data": data,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "data": None
            }
    
    async def test_priority_teams(self):
        """Test 1: Verify first 20 clubs have correct references TK-TEAM-000001 to TK-TEAM-000020"""
        print("🔍 Testing Priority Teams (First 20 clubs)...")
        
        # Get all teams
        response = await self.make_request("GET", "/teams", params={"limit": 1000})
        
        if response["status"] != 200:
            self.results["priority_teams"]["failed"] += 1
            self.results["priority_teams"]["details"].append(f"❌ Failed to fetch teams: {response.get('error', 'Unknown error')}")
            return
            
        teams = response["data"]
        if not isinstance(teams, list):
            self.results["priority_teams"]["failed"] += 1
            self.results["priority_teams"]["details"].append("❌ Teams response is not a list")
            return
            
        # Create lookup by reference for quick access
        teams_by_reference = {team.get("topkit_reference", ""): team for team in teams}
        
        # Test each priority team
        for expected_team in PRIORITY_TEAMS:
            reference = expected_team["reference"]
            expected_name = expected_team["name"]
            
            if reference in teams_by_reference:
                actual_team = teams_by_reference[reference]
                actual_name = actual_team.get("name", "")
                
                # Check if names match (allowing for slight variations)
                if self.names_match(expected_name, actual_name):
                    self.results["priority_teams"]["passed"] += 1
                    self.results["priority_teams"]["details"].append(f"✅ {reference}: {actual_name} (correct)")
                else:
                    self.results["priority_teams"]["failed"] += 1
                    self.results["priority_teams"]["details"].append(f"❌ {reference}: Expected '{expected_name}', got '{actual_name}'")
            else:
                self.results["priority_teams"]["failed"] += 1
                self.results["priority_teams"]["details"].append(f"❌ {reference}: Team not found")
                
        print(f"   Priority Teams: {self.results['priority_teams']['passed']} passed, {self.results['priority_teams']['failed']} failed")
    
    def names_match(self, expected: str, actual: str) -> bool:
        """Check if team names match allowing for variations"""
        expected_lower = expected.lower().strip()
        actual_lower = actual.lower().strip()
        
        # Direct match
        if expected_lower == actual_lower:
            return True
            
        # Common variations
        variations = {
            "fc barcelona": ["barcelona", "fc barcelone", "barcelona fc"],
            "real madrid": ["real madrid cf"],
            "manchester united": ["manchester utd", "man united"],
            "manchester city": ["man city"],
            "paris saint-germain": ["psg", "paris sg"],
            "ac milan": ["milan", "ac milan"],
            "inter milan": ["internazionale", "inter"],
            "bayern munich": ["fc bayern munich", "bayern"],
            "borussia dortmund": ["bvb", "dortmund"],
            "atletico madrid": ["atletico de madrid"],
            "olympique de marseille": ["marseille", "om"],
            "as monaco": ["monaco"]
        }
        
        for canonical, alts in variations.items():
            if expected_lower == canonical and actual_lower in alts:
                return True
            if actual_lower == canonical and expected_lower in alts:
                return True
                
        return False
    
    async def test_api_teams(self):
        """Test 2: Ensure all teams are accessible and new data is correctly stored"""
        print("🔍 Testing GET /api/teams endpoint...")
        
        # Test basic endpoint
        response = await self.make_request("GET", "/teams")
        
        if response["status"] != 200:
            self.results["api_teams"]["failed"] += 1
            self.results["api_teams"]["details"].append(f"❌ GET /teams failed: {response.get('error', 'Unknown error')}")
            return
            
        teams = response["data"]
        if not isinstance(teams, list):
            self.results["api_teams"]["failed"] += 1
            self.results["api_teams"]["details"].append("❌ Teams response is not a list")
            return
            
        total_teams = len(teams)
        self.results["api_teams"]["passed"] += 1
        self.results["api_teams"]["details"].append(f"✅ GET /teams returned {total_teams} teams")
        
        # Test with filters
        test_filters = [
            {"country": "France", "expected_min": 10},
            {"country": "England", "expected_min": 15},
            {"country": "Spain", "expected_min": 10},
            {"verified_only": True, "expected_min": 0}
        ]
        
        for filter_test in test_filters:
            params = {k: v for k, v in filter_test.items() if k != "expected_min"}
            expected_min = filter_test["expected_min"]
            
            response = await self.make_request("GET", "/teams", params=params)
            
            if response["status"] == 200:
                filtered_teams = response["data"]
                if len(filtered_teams) >= expected_min:
                    self.results["api_teams"]["passed"] += 1
                    self.results["api_teams"]["details"].append(f"✅ Filter {params}: {len(filtered_teams)} teams (>= {expected_min})")
                else:
                    self.results["api_teams"]["failed"] += 1
                    self.results["api_teams"]["details"].append(f"❌ Filter {params}: {len(filtered_teams)} teams (< {expected_min})")
            else:
                self.results["api_teams"]["failed"] += 1
                self.results["api_teams"]["details"].append(f"❌ Filter {params} failed: {response.get('error', 'Unknown error')}")
        
        # Test data structure and new fields
        if teams:
            sample_team = teams[0]
            required_fields = ["id", "name", "topkit_reference"]
            new_fields = ["country", "colors"]
            
            for field in required_fields:
                if field in sample_team:
                    self.results["api_teams"]["passed"] += 1
                    self.results["api_teams"]["details"].append(f"✅ Required field '{field}' present")
                else:
                    self.results["api_teams"]["failed"] += 1
                    self.results["api_teams"]["details"].append(f"❌ Required field '{field}' missing")
                    
            for field in new_fields:
                if field in sample_team:
                    self.results["api_teams"]["passed"] += 1
                    self.results["api_teams"]["details"].append(f"✅ New field '{field}' present: {sample_team[field]}")
                else:
                    self.results["api_teams"]["failed"] += 1
                    self.results["api_teams"]["details"].append(f"❌ New field '{field}' missing")
                    
        print(f"   API Teams: {self.results['api_teams']['passed']} passed, {self.results['api_teams']['failed']} failed")
    
    async def test_search_teams(self):
        """Test 3: Test search by name with reorganized clubs"""
        print("🔍 Testing Team Search functionality...")
        
        for search_case in SEARCH_TEST_CASES:
            query = search_case["query"]
            expected_count = search_case["expected_count"]
            
            response = await self.make_request("GET", "/teams", params={"search": query})
            
            if response["status"] != 200:
                self.results["search_teams"]["failed"] += 1
                self.results["search_teams"]["details"].append(f"❌ Search '{query}' failed: {response.get('error', 'Unknown error')}")
                continue
                
            teams = response["data"]
            actual_count = len(teams)
            
            if actual_count == expected_count:
                self.results["search_teams"]["passed"] += 1
                
                # Check specific reference if provided
                if "expected_reference" in search_case:
                    expected_ref = search_case["expected_reference"]
                    if teams and teams[0].get("topkit_reference") == expected_ref:
                        self.results["search_teams"]["details"].append(f"✅ Search '{query}': {actual_count} results, reference {expected_ref} correct")
                    else:
                        actual_ref = teams[0].get("topkit_reference", "None") if teams else "None"
                        self.results["search_teams"]["details"].append(f"⚠️ Search '{query}': {actual_count} results, but reference {actual_ref} != {expected_ref}")
                        
                elif "expected_references" in search_case:
                    expected_refs = search_case["expected_references"]
                    actual_refs = [team.get("topkit_reference") for team in teams]
                    if all(ref in actual_refs for ref in expected_refs):
                        self.results["search_teams"]["details"].append(f"✅ Search '{query}': {actual_count} results, all expected references found")
                    else:
                        self.results["search_teams"]["details"].append(f"⚠️ Search '{query}': {actual_count} results, but references don't match expected")
                else:
                    self.results["search_teams"]["details"].append(f"✅ Search '{query}': {actual_count} results (expected {expected_count})")
                    
            else:
                self.results["search_teams"]["failed"] += 1
                self.results["search_teams"]["details"].append(f"❌ Search '{query}': {actual_count} results (expected {expected_count})")
                
        print(f"   Search Teams: {self.results['search_teams']['passed']} passed, {self.results['search_teams']['failed']} failed")
    
    async def test_master_jerseys_integration(self):
        """Test 4: Verify Master Jerseys work with new team references"""
        print("🔍 Testing Master Jerseys integration...")
        
        # Get master jerseys
        response = await self.make_request("GET", "/master-jerseys")
        
        if response["status"] != 200:
            self.results["master_jerseys"]["failed"] += 1
            self.results["master_jerseys"]["details"].append(f"❌ GET /master-jerseys failed: {response.get('error', 'Unknown error')}")
            return
            
        master_jerseys = response["data"]
        if not isinstance(master_jerseys, list):
            self.results["master_jerseys"]["failed"] += 1
            self.results["master_jerseys"]["details"].append("❌ Master jerseys response is not a list")
            return
            
        total_jerseys = len(master_jerseys)
        self.results["master_jerseys"]["passed"] += 1
        self.results["master_jerseys"]["details"].append(f"✅ Found {total_jerseys} master jerseys")
        
        # Test team reference integration
        valid_team_refs = 0
        invalid_team_refs = 0
        
        for jersey in master_jerseys:
            team_id = jersey.get("team_id")
            if team_id:
                # Verify team exists
                team_response = await self.make_request("GET", f"/teams/{team_id}")
                if team_response["status"] == 200:
                    team = team_response["data"]
                    team_ref = team.get("topkit_reference", "")
                    if team_ref.startswith("TK-TEAM-"):
                        valid_team_refs += 1
                    else:
                        invalid_team_refs += 1
                else:
                    invalid_team_refs += 1
            else:
                invalid_team_refs += 1
                
        if valid_team_refs > 0:
            self.results["master_jerseys"]["passed"] += 1
            self.results["master_jerseys"]["details"].append(f"✅ {valid_team_refs} master jerseys have valid team references")
            
        if invalid_team_refs > 0:
            self.results["master_jerseys"]["failed"] += 1
            self.results["master_jerseys"]["details"].append(f"❌ {invalid_team_refs} master jerseys have invalid team references")
            
        print(f"   Master Jerseys: {self.results['master_jerseys']['passed']} passed, {self.results['master_jerseys']['failed']} failed")
    
    async def test_new_teams(self):
        """Test 5: Confirm new teams from CSV are accessible"""
        print("🔍 Testing new teams from CSV import...")
        
        # Get all teams
        response = await self.make_request("GET", "/teams", params={"limit": 1000})
        
        if response["status"] != 200:
            self.results["new_teams"]["failed"] += 1
            self.results["new_teams"]["details"].append(f"❌ Failed to fetch teams: {response.get('error', 'Unknown error')}")
            return
            
        teams = response["data"]
        total_teams = len(teams)
        
        # Expected minimum teams after CSV import (should be significantly more than before)
        expected_min_teams = 300  # Assuming CSV added many teams
        
        if total_teams >= expected_min_teams:
            self.results["new_teams"]["passed"] += 1
            self.results["new_teams"]["details"].append(f"✅ Total teams: {total_teams} (>= {expected_min_teams})")
        else:
            self.results["new_teams"]["failed"] += 1
            self.results["new_teams"]["details"].append(f"❌ Total teams: {total_teams} (< {expected_min_teams})")
            
        # Test country distribution (new teams should increase country coverage)
        countries = set()
        for team in teams:
            country = team.get("country")
            if country:
                countries.add(country)
                
        expected_min_countries = 10  # Should have good international coverage
        
        if len(countries) >= expected_min_countries:
            self.results["new_teams"]["passed"] += 1
            self.results["new_teams"]["details"].append(f"✅ Countries represented: {len(countries)} (>= {expected_min_countries})")
        else:
            self.results["new_teams"]["failed"] += 1
            self.results["new_teams"]["details"].append(f"❌ Countries represented: {len(countries)} (< {expected_min_countries})")
            
        # Test for some expected new teams that should be in CSV
        expected_new_teams = [
            "Lille OSC", "Lyon", "Nice", "Rennes", "Strasbourg",  # French teams
            "Valencia", "Sevilla", "Real Sociedad", "Villarreal",  # Spanish teams
            "Bayer Leverkusen", "RB Leipzig", "Eintracht Frankfurt",  # German teams
            "Lazio", "Fiorentina", "Atalanta", "Torino"  # Italian teams
        ]
        
        team_names = [team.get("name", "").lower() for team in teams]
        found_new_teams = 0
        
        for expected_team in expected_new_teams:
            if any(expected_team.lower() in name for name in team_names):
                found_new_teams += 1
                
        if found_new_teams >= len(expected_new_teams) // 2:  # At least half should be found
            self.results["new_teams"]["passed"] += 1
            self.results["new_teams"]["details"].append(f"✅ Found {found_new_teams}/{len(expected_new_teams)} expected new teams")
        else:
            self.results["new_teams"]["failed"] += 1
            self.results["new_teams"]["details"].append(f"❌ Found only {found_new_teams}/{len(expected_new_teams)} expected new teams")
            
        print(f"   New Teams: {self.results['new_teams']['passed']} passed, {self.results['new_teams']['failed']} failed")
    
    async def test_data_consistency(self):
        """Test 6: Verify all teams have unique and valid TopKit references"""
        print("🔍 Testing data consistency...")
        
        # Get all teams
        response = await self.make_request("GET", "/teams", params={"limit": 1000})
        
        if response["status"] != 200:
            self.results["data_consistency"]["failed"] += 1
            self.results["data_consistency"]["details"].append(f"❌ Failed to fetch teams: {response.get('error', 'Unknown error')}")
            return
            
        teams = response["data"]
        
        # Test 1: All teams have TopKit references
        teams_with_refs = 0
        teams_without_refs = 0
        
        for team in teams:
            if team.get("topkit_reference"):
                teams_with_refs += 1
            else:
                teams_without_refs += 1
                
        if teams_without_refs == 0:
            self.results["data_consistency"]["passed"] += 1
            self.results["data_consistency"]["details"].append(f"✅ All {teams_with_refs} teams have TopKit references")
        else:
            self.results["data_consistency"]["failed"] += 1
            self.results["data_consistency"]["details"].append(f"❌ {teams_without_refs} teams missing TopKit references")
            
        # Test 2: All references are unique
        references = [team.get("topkit_reference") for team in teams if team.get("topkit_reference")]
        unique_references = set(references)
        
        if len(references) == len(unique_references):
            self.results["data_consistency"]["passed"] += 1
            self.results["data_consistency"]["details"].append(f"✅ All {len(references)} TopKit references are unique")
        else:
            duplicates = len(references) - len(unique_references)
            self.results["data_consistency"]["failed"] += 1
            self.results["data_consistency"]["details"].append(f"❌ Found {duplicates} duplicate TopKit references")
            
        # Test 3: All references follow correct format
        valid_format_count = 0
        invalid_format_count = 0
        
        for ref in references:
            if ref and ref.startswith("TK-TEAM-") and len(ref) == 15:  # TK-TEAM-000001 format
                try:
                    int(ref[-6:])  # Last 6 characters should be numbers
                    valid_format_count += 1
                except ValueError:
                    invalid_format_count += 1
            else:
                invalid_format_count += 1
                
        if invalid_format_count == 0:
            self.results["data_consistency"]["passed"] += 1
            self.results["data_consistency"]["details"].append(f"✅ All {valid_format_count} references follow TK-TEAM-XXXXXX format")
        else:
            self.results["data_consistency"]["failed"] += 1
            self.results["data_consistency"]["details"].append(f"❌ {invalid_format_count} references have invalid format")
            
        # Test 4: Sequential numbering (no gaps in important ranges)
        reference_numbers = []
        for ref in references:
            if ref and ref.startswith("TK-TEAM-"):
                try:
                    num = int(ref[-6:])
                    reference_numbers.append(num)
                except ValueError:
                    pass
                    
        reference_numbers.sort()
        
        # Check first 50 references for gaps (most important teams should be sequential)
        first_50 = [num for num in reference_numbers if num <= 50]
        expected_first_50 = list(range(1, len(first_50) + 1))
        
        if first_50 == expected_first_50:
            self.results["data_consistency"]["passed"] += 1
            self.results["data_consistency"]["details"].append(f"✅ First {len(first_50)} references are sequential (no gaps)")
        else:
            gaps = set(expected_first_50) - set(first_50)
            self.results["data_consistency"]["failed"] += 1
            self.results["data_consistency"]["details"].append(f"❌ Found gaps in first 50 references: {sorted(gaps)}")
            
        print(f"   Data Consistency: {self.results['data_consistency']['passed']} passed, {self.results['data_consistency']['failed']} failed")
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting TopKit Team Reorganization Backend Testing...")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test suites
            await self.test_priority_teams()
            await self.test_api_teams()
            await self.test_search_teams()
            await self.test_master_jerseys_integration()
            await self.test_new_teams()
            await self.test_data_consistency()
            
        finally:
            await self.cleanup()
            
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 TOPKIT TEAM REORGANIZATION TESTING SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL" if passed == 0 else "⚠️ PARTIAL"
            print(f"{status} {category.replace('_', ' ').title()}: {passed} passed, {failed} failed")
            
            # Show details for failed tests
            if failed > 0:
                for detail in results["details"]:
                    if detail.startswith("❌"):
                        print(f"    {detail}")
        
        print("\n" + "-" * 80)
        total_tests = total_passed + total_failed
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🎯 OVERALL RESULTS: {total_passed}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Team reorganization is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Team reorganization is working well with minor issues")
        elif success_rate >= 50:
            print("⚠️ PARTIAL: Team reorganization has significant issues")
        else:
            print("❌ CRITICAL: Team reorganization has major problems")
            
        print("\n📋 DETAILED RESULTS:")
        for category, results in self.results.items():
            if results["details"]:
                print(f"\n{category.replace('_', ' ').title()}:")
                for detail in results["details"]:
                    print(f"  {detail}")

async def main():
    """Main test execution"""
    tester = TeamReorganizationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())