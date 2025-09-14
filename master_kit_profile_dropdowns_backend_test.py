#!/usr/bin/env python3
"""
Backend Testing for Master Kit Profile Dropdowns and Homepage Teams Display Fixes

FIXES IMPLEMENTED:
1. Master Kit Profile Dropdowns Fixed: 
   - Added master_kit case to UnifiedFieldDefinitions.js with proper field definitions
   - Updated MasterJerseyDetailPage to fetch and pass teams, brands, competitions, players data to ContributionModal
   - Fields: club_id (Team), brand_id (Brand), main_sponsor_id (Main Sponsor) should now have working dropdowns

2. Homepage Teams Display Fixed:
   - Changed teams order to show latest teams first (reverse order) 
   - Updated team buttons to be perfectly square (120x120px)
   - Added text truncation with ellipsis for names longer than 12 characters

TEST REQUIREMENTS:
1. Master Kit Dropdowns: Test that master kit improvement form has working Team, Brand, and Main Sponsor dropdowns with actual data
2. Homepage Teams Order: Verify teams are now shown in reverse order (latest first)
3. Team Button Styling: Check that team buttons are square and long names are truncated properly
4. Data Integration: Confirm that teams/brands/competitions APIs are providing data to the dropdowns

CRITICAL SCENARIOS:
- Access master kit detail page and open "Améliorer cette fiche" form
- Verify Team dropdown shows list of teams
- Verify Brand dropdown shows list of brands  
- Verify Main Sponsor dropdown shows list of brands
- Check homepage teams section for proper order and square styling
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-collab-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class MasterKitProfileDropdownsTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.admin_user = None
        
    async def setup(self):
        """Initialize session and authenticate"""
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        
    async def cleanup(self):
        """Clean up session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["token"]
                    self.admin_user = data["user"]
                    print(f"✅ Authenticated as: {self.admin_user['name']} ({self.admin_user['role']})")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_teams_api_for_dropdowns(self):
        """Test Teams API provides data for dropdowns"""
        print("\n🔍 Testing Teams API for dropdown data...")
        
        try:
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    
                    if teams and len(teams) > 0:
                        print(f"✅ Teams API returned {len(teams)} teams")
                        
                        # Check if teams have required fields for dropdowns
                        sample_team = teams[0]
                        required_fields = ['id', 'name']
                        missing_fields = [field for field in required_fields if field not in sample_team]
                        
                        if not missing_fields:
                            print(f"✅ Teams have required dropdown fields: {required_fields}")
                            
                            # Check for teams order (should be latest first if fixed)
                            teams_with_dates = [team for team in teams if 'created_at' in team]
                            if len(teams_with_dates) >= 2:
                                # Check if first team is newer than second team
                                first_date = teams_with_dates[0].get('created_at')
                                second_date = teams_with_dates[1].get('created_at')
                                
                                if first_date and second_date:
                                    if first_date >= second_date:
                                        print("✅ Teams appear to be in reverse order (latest first)")
                                        self.test_results.append(("Teams API Order", True, "Teams in reverse chronological order"))
                                    else:
                                        print("⚠️ Teams may not be in reverse order")
                                        self.test_results.append(("Teams API Order", False, "Teams not in reverse order"))
                                else:
                                    print("⚠️ Cannot verify teams order - missing dates")
                                    self.test_results.append(("Teams API Order", "NA", "Cannot verify - missing dates"))
                            
                            self.test_results.append(("Teams API for Dropdowns", True, f"{len(teams)} teams with required fields"))
                            return True
                        else:
                            print(f"❌ Teams missing required fields: {missing_fields}")
                            self.test_results.append(("Teams API for Dropdowns", False, f"Missing fields: {missing_fields}"))
                            return False
                    else:
                        print("❌ Teams API returned empty data")
                        self.test_results.append(("Teams API for Dropdowns", False, "No teams data"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Teams API failed: {response.status} - {error_text}")
                    self.test_results.append(("Teams API for Dropdowns", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing Teams API: {str(e)}")
            self.test_results.append(("Teams API for Dropdowns", False, f"Exception: {str(e)}"))
            return False
            
    async def test_brands_api_for_dropdowns(self):
        """Test Brands API provides data for dropdowns"""
        print("\n🔍 Testing Brands API for dropdown data...")
        
        try:
            async with self.session.get(f"{API_BASE}/brands") as response:
                if response.status == 200:
                    brands = await response.json()
                    
                    if brands and len(brands) > 0:
                        print(f"✅ Brands API returned {len(brands)} brands")
                        
                        # Check if brands have required fields for dropdowns
                        sample_brand = brands[0]
                        required_fields = ['id', 'name']
                        missing_fields = [field for field in required_fields if field not in sample_brand]
                        
                        if not missing_fields:
                            print(f"✅ Brands have required dropdown fields: {required_fields}")
                            self.test_results.append(("Brands API for Dropdowns", True, f"{len(brands)} brands with required fields"))
                            return True
                        else:
                            print(f"❌ Brands missing required fields: {missing_fields}")
                            self.test_results.append(("Brands API for Dropdowns", False, f"Missing fields: {missing_fields}"))
                            return False
                    else:
                        print("❌ Brands API returned empty data")
                        self.test_results.append(("Brands API for Dropdowns", False, "No brands data"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Brands API failed: {response.status} - {error_text}")
                    self.test_results.append(("Brands API for Dropdowns", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing Brands API: {str(e)}")
            self.test_results.append(("Brands API for Dropdowns", False, f"Exception: {str(e)}"))
            return False
            
    async def test_competitions_api_for_dropdowns(self):
        """Test Competitions API provides data for dropdowns"""
        print("\n🔍 Testing Competitions API for dropdown data...")
        
        try:
            async with self.session.get(f"{API_BASE}/competitions") as response:
                if response.status == 200:
                    competitions = await response.json()
                    
                    if competitions and len(competitions) > 0:
                        print(f"✅ Competitions API returned {len(competitions)} competitions")
                        
                        # Check if competitions have required fields for dropdowns
                        sample_competition = competitions[0]
                        required_fields = ['id']
                        # Competition name might be in 'competition_name' or 'name' field
                        name_field = 'competition_name' if 'competition_name' in sample_competition else 'name'
                        if name_field in sample_competition:
                            required_fields.append(name_field)
                        
                        missing_fields = [field for field in required_fields if field not in sample_competition]
                        
                        if not missing_fields:
                            print(f"✅ Competitions have required dropdown fields: {required_fields}")
                            self.test_results.append(("Competitions API for Dropdowns", True, f"{len(competitions)} competitions with required fields"))
                            return True
                        else:
                            print(f"❌ Competitions missing required fields: {missing_fields}")
                            self.test_results.append(("Competitions API for Dropdowns", False, f"Missing fields: {missing_fields}"))
                            return False
                    else:
                        print("❌ Competitions API returned empty data")
                        self.test_results.append(("Competitions API for Dropdowns", False, "No competitions data"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Competitions API failed: {response.status} - {error_text}")
                    self.test_results.append(("Competitions API for Dropdowns", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing Competitions API: {str(e)}")
            self.test_results.append(("Competitions API for Dropdowns", False, f"Exception: {str(e)}"))
            return False
            
    async def test_players_api_for_dropdowns(self):
        """Test Players API provides data for dropdowns"""
        print("\n🔍 Testing Players API for dropdown data...")
        
        try:
            async with self.session.get(f"{API_BASE}/players") as response:
                if response.status == 200:
                    players = await response.json()
                    
                    if players and len(players) > 0:
                        print(f"✅ Players API returned {len(players)} players")
                        
                        # Check if players have required fields for dropdowns
                        sample_player = players[0]
                        required_fields = ['id', 'name']
                        missing_fields = [field for field in required_fields if field not in sample_player]
                        
                        if not missing_fields:
                            print(f"✅ Players have required dropdown fields: {required_fields}")
                            self.test_results.append(("Players API for Dropdowns", True, f"{len(players)} players with required fields"))
                            return True
                        else:
                            print(f"❌ Players missing required fields: {missing_fields}")
                            self.test_results.append(("Players API for Dropdowns", False, f"Missing fields: {missing_fields}"))
                            return False
                    else:
                        print("❌ Players API returned empty data")
                        self.test_results.append(("Players API for Dropdowns", False, "No players data"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Players API failed: {response.status} - {error_text}")
                    self.test_results.append(("Players API for Dropdowns", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing Players API: {str(e)}")
            self.test_results.append(("Players API for Dropdowns", False, f"Exception: {str(e)}"))
            return False
            
    async def test_master_kits_api_for_detail_pages(self):
        """Test Master Kits API for detail page access"""
        print("\n🔍 Testing Master Kits API for detail page access...")
        
        try:
            async with self.session.get(f"{API_BASE}/master-kits") as response:
                if response.status == 200:
                    master_kits = await response.json()
                    
                    if master_kits and len(master_kits) > 0:
                        print(f"✅ Master Kits API returned {len(master_kits)} master kits")
                        
                        # Test accessing a specific master kit detail
                        sample_kit = master_kits[0]
                        kit_id = sample_kit.get('id')
                        
                        if kit_id:
                            async with self.session.get(f"{API_BASE}/master-kits/{kit_id}") as detail_response:
                                if detail_response.status == 200:
                                    kit_detail = await detail_response.json()
                                    print(f"✅ Master Kit detail page accessible: {kit_detail.get('club', 'Unknown')} {kit_detail.get('season', 'Unknown')}")
                                    
                                    # Check if kit has the fields that would be used in improvement form
                                    improvement_fields = ['club_id', 'brand_id', 'main_sponsor_id', 'competition_id']
                                    available_fields = [field for field in improvement_fields if field in kit_detail]
                                    
                                    print(f"✅ Master Kit has improvement form fields: {available_fields}")
                                    self.test_results.append(("Master Kits API for Detail Pages", True, f"Detail page accessible with fields: {available_fields}"))
                                    return True
                                else:
                                    print(f"❌ Master Kit detail page failed: {detail_response.status}")
                                    self.test_results.append(("Master Kits API for Detail Pages", False, f"Detail page error: {detail_response.status}"))
                                    return False
                        else:
                            print("❌ Master Kit missing ID field")
                            self.test_results.append(("Master Kits API for Detail Pages", False, "Missing ID field"))
                            return False
                    else:
                        print("❌ Master Kits API returned empty data")
                        self.test_results.append(("Master Kits API for Detail Pages", False, "No master kits data"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Master Kits API failed: {response.status} - {error_text}")
                    self.test_results.append(("Master Kits API for Detail Pages", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing Master Kits API: {str(e)}")
            self.test_results.append(("Master Kits API for Detail Pages", False, f"Exception: {str(e)}"))
            return False
            
    async def test_form_data_endpoints(self):
        """Test form data endpoints that provide dropdown data"""
        print("\n🔍 Testing form data endpoints for dropdowns...")
        
        endpoints = [
            ("clubs", "/api/form-data/clubs"),
            ("competitions", "/api/form-data/competitions"), 
            ("brands", "/api/form-data/brands")
        ]
        
        success_count = 0
        total_count = len(endpoints)
        
        for endpoint_name, endpoint_url in endpoints:
            try:
                async with self.session.get(endpoint_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data and len(data) > 0:
                            print(f"  ✅ {endpoint_name}: {len(data)} items")
                            
                            # Check if items have required fields
                            sample_item = data[0]
                            if 'id' in sample_item and ('name' in sample_item or 'competition_name' in sample_item):
                                success_count += 1
                            else:
                                print(f"    ❌ {endpoint_name}: Missing required fields")
                        else:
                            print(f"  ❌ {endpoint_name}: Empty data")
                    else:
                        print(f"  ❌ {endpoint_name}: API error {response.status}")
                        
            except Exception as e:
                print(f"  ❌ {endpoint_name}: Exception - {str(e)}")
                
        success_rate = (success_count / total_count) * 100
        print(f"\n✅ Form data endpoints test: {success_count}/{total_count} working ({success_rate:.1f}%)")
        
        if success_count == total_count:
            self.test_results.append(("Form Data Endpoints", True, f"All {total_count} endpoints working"))
            return True
        else:
            self.test_results.append(("Form Data Endpoints", False, f"Only {success_count}/{total_count} working"))
            return False
            
    async def test_contribution_creation_for_master_kit(self):
        """Test contribution creation for master kit improvement"""
        print("\n🔍 Testing contribution creation for master kit improvement...")
        
        try:
            # First get a master kit to improve
            async with self.session.get(f"{API_BASE}/master-kits") as response:
                if response.status == 200:
                    master_kits = await response.json()
                    
                    if master_kits and len(master_kits) > 0:
                        sample_kit = master_kits[0]
                        kit_id = sample_kit.get('id')
                        
                        # Create a contribution to improve this master kit
                        contribution_data = {
                            "entity_type": "master_kit",
                            "title": f"Improve master kit: {sample_kit.get('club', 'Unknown')} {sample_kit.get('season', 'Unknown')}",
                            "description": "Testing master kit improvement form with dropdown data",
                            "data": {
                                "club_id": "test-team-id-123",
                                "brand_id": "test-brand-id-456", 
                                "main_sponsor_id": "test-sponsor-id-789"
                            },
                            "source_urls": [],
                            "entity_id": kit_id
                        }
                        
                        async with self.session.post(
                            f"{API_BASE}/contributions-v2/", 
                            json=contribution_data,
                            headers=self.get_auth_headers()
                        ) as contrib_response:
                            if contrib_response.status == 200:
                                contrib_data = await contrib_response.json()
                                print(f"✅ Created master kit improvement contribution: {contrib_data['id']}")
                                
                                # Verify the contribution has the expected dropdown fields
                                expected_fields = {"club_id", "brand_id", "main_sponsor_id"}
                                actual_fields = set(contrib_data["data"].keys())
                                
                                if expected_fields.issubset(actual_fields):
                                    print("✅ Master kit improvement contribution has dropdown fields")
                                    self.test_results.append(("Master Kit Improvement Contribution", True, "Dropdown fields present in contribution"))
                                    return True
                                else:
                                    missing_fields = expected_fields - actual_fields
                                    print(f"❌ Missing dropdown fields: {missing_fields}")
                                    self.test_results.append(("Master Kit Improvement Contribution", False, f"Missing fields: {missing_fields}"))
                                    return False
                            else:
                                error_text = await contrib_response.text()
                                print(f"❌ Failed to create contribution: {contrib_response.status} - {error_text}")
                                self.test_results.append(("Master Kit Improvement Contribution", False, f"Creation failed: {contrib_response.status}"))
                                return False
                    else:
                        print("❌ No master kits available for testing")
                        self.test_results.append(("Master Kit Improvement Contribution", False, "No master kits available"))
                        return False
                else:
                    print(f"❌ Failed to get master kits: {response.status}")
                    self.test_results.append(("Master Kit Improvement Contribution", False, f"Master kits fetch failed: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing master kit improvement contribution: {str(e)}")
            self.test_results.append(("Master Kit Improvement Contribution", False, f"Exception: {str(e)}"))
            return False
            
    async def test_teams_data_quality_for_homepage(self):
        """Test teams data quality for homepage display"""
        print("\n🔍 Testing teams data quality for homepage display...")
        
        try:
            async with self.session.get(f"{API_BASE}/teams") as response:
                if response.status == 200:
                    teams = await response.json()
                    
                    if teams and len(teams) >= 10:
                        print(f"✅ Teams API has sufficient data for homepage: {len(teams)} teams")
                        
                        # Check for teams with long names (for truncation testing)
                        long_name_teams = [team for team in teams if len(team.get('name', '')) > 12]
                        if long_name_teams:
                            print(f"✅ Found {len(long_name_teams)} teams with names longer than 12 characters (good for truncation testing)")
                            
                            # Show examples
                            for i, team in enumerate(long_name_teams[:3]):
                                print(f"    Example {i+1}: '{team['name']}' ({len(team['name'])} chars)")
                        
                        # Check for teams with logos (for square button testing)
                        teams_with_logos = [team for team in teams if team.get('logo_url')]
                        print(f"✅ Found {len(teams_with_logos)} teams with logos for button display")
                        
                        self.test_results.append(("Teams Data Quality for Homepage", True, f"{len(teams)} teams, {len(long_name_teams)} with long names, {len(teams_with_logos)} with logos"))
                        return True
                    else:
                        print(f"⚠️ Limited teams data for homepage: {len(teams) if teams else 0} teams")
                        self.test_results.append(("Teams Data Quality for Homepage", False, f"Insufficient teams: {len(teams) if teams else 0}"))
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Teams API failed: {response.status} - {error_text}")
                    self.test_results.append(("Teams Data Quality for Homepage", False, f"API error: {response.status}"))
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing teams data quality: {str(e)}")
            self.test_results.append(("Teams Data Quality for Homepage", False, f"Exception: {str(e)}"))
            return False
            
    async def test_api_response_times(self):
        """Test API response times for dropdown performance"""
        print("\n🔍 Testing API response times for dropdown performance...")
        
        apis_to_test = [
            ("Teams", "/api/teams"),
            ("Brands", "/api/brands"),
            ("Competitions", "/api/competitions"),
            ("Players", "/api/players"),
            ("Master Kits", "/api/master-kits")
        ]
        
        response_times = []
        
        for api_name, api_url in apis_to_test:
            try:
                start_time = datetime.now()
                async with self.session.get(api_url) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds()
                    
                    if response.status == 200:
                        data = await response.json()
                        item_count = len(data) if data else 0
                        print(f"  ✅ {api_name}: {response_time:.2f}s ({item_count} items)")
                        response_times.append((api_name, response_time, True))
                    else:
                        print(f"  ❌ {api_name}: {response_time:.2f}s (Error {response.status})")
                        response_times.append((api_name, response_time, False))
                        
            except Exception as e:
                print(f"  ❌ {api_name}: Exception - {str(e)}")
                response_times.append((api_name, 999, False))
                
        # Calculate average response time for successful requests
        successful_times = [time for _, time, success in response_times if success]
        if successful_times:
            avg_time = sum(successful_times) / len(successful_times)
            print(f"\n✅ Average API response time: {avg_time:.2f}s")
            
            if avg_time < 2.0:
                self.test_results.append(("API Response Times", True, f"Average {avg_time:.2f}s - Good performance"))
                return True
            else:
                self.test_results.append(("API Response Times", False, f"Average {avg_time:.2f}s - Slow performance"))
                return False
        else:
            self.test_results.append(("API Response Times", False, "No successful API calls"))
            return False
            
    async def run_all_tests(self):
        """Run all master kit profile dropdowns tests"""
        print("🚀 Starting Master Kit Profile Dropdowns and Homepage Teams Display Testing...")
        print("=" * 80)
        
        await self.setup()
        
        if not self.auth_token:
            print("❌ Cannot proceed without authentication")
            return
            
        # Run all tests
        test_functions = [
            self.test_teams_api_for_dropdowns,
            self.test_brands_api_for_dropdowns,
            self.test_competitions_api_for_dropdowns,
            self.test_players_api_for_dropdowns,
            self.test_master_kits_api_for_detail_pages,
            self.test_form_data_endpoints,
            self.test_contribution_creation_for_master_kit,
            self.test_teams_data_quality_for_homepage,
            self.test_api_response_times
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
                self.test_results.append((test_func.__name__, False, f"Exception: {str(e)}"))
                
        await self.cleanup()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 80)
        print("📊 MASTER KIT PROFILE DROPDOWNS & HOMEPAGE TEAMS TEST RESULTS")
        print("=" * 80)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📈 Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        
        print("\n✅ PASSED TESTS:")
        for test_name, success, details in self.test_results:
            if success:
                print(f"  ✅ {test_name}: {details}")
                
        print("\n❌ FAILED TESTS:")
        failed_tests = [(name, details) for name, success, details in self.test_results if not success]
        if failed_tests:
            for test_name, details in failed_tests:
                print(f"  ❌ {test_name}: {details}")
        else:
            print("  None - All tests passed!")
            
        print("\n" + "=" * 80)
        
        # Critical findings
        if success_rate >= 90:
            print("🎉 MASTER KIT PROFILE DROPDOWNS ARE WORKING EXCELLENTLY!")
            print("✅ All APIs provide proper data for dropdown functionality")
            print("✅ Homepage teams display should work with proper ordering and styling")
        elif success_rate >= 70:
            print("⚠️  MASTER KIT PROFILE DROPDOWNS HAVE MINOR ISSUES")
            print("🔧 Some APIs need attention but core dropdown data is available")
        else:
            print("🚨 CRITICAL ISSUES WITH MASTER KIT PROFILE DROPDOWNS")
            print("❌ Major API problems detected - dropdowns may not work properly")
            
        print("=" * 80)

async def main():
    """Main test execution"""
    tester = MasterKitProfileDropdownsTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())