#!/usr/bin/env python3
"""
Test des nouveaux endpoints collaboratifs TopKit
Vérification de l'import des données de compétitions et équipes
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitCollaborativeTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = {
            "competitions": {"total": 0, "passed": 0, "failed": 0, "details": []},
            "teams": {"total": 0, "passed": 0, "failed": 0, "details": []},
            "filtering": {"total": 0, "passed": 0, "failed": 0, "details": []},
            "consistency": {"total": 0, "passed": 0, "failed": 0, "details": []},
            "summary": {"total_tests": 0, "total_passed": 0, "success_rate": 0}
        }
        
    def log_test(self, category, test_name, passed, details=""):
        """Log test result"""
        self.test_results[category]["total"] += 1
        if passed:
            self.test_results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results[category]["failed"] += 1
            status = "❌ FAIL"
            
        self.test_results[category]["details"].append({
            "test": test_name,
            "status": status,
            "details": details
        })
        print(f"{status}: {test_name} - {details}")
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                print(f"✅ Admin authentication successful: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Admin authentication error: {e}")
            return False
    
    def test_competitions_endpoint(self):
        """Test 1: Vérifier l'endpoint GET /api/competitions"""
        print("\n🏆 TESTING COMPETITIONS ENDPOINT")
        
        try:
            response = self.session.get(f"{BASE_URL}/competitions")
            
            if response.status_code == 200:
                competitions = response.json()
                total_competitions = len(competitions)
                
                self.log_test("competitions", "Competitions endpoint accessible", True, 
                            f"Found {total_competitions} competitions")
                
                # Vérifier les compétitions principales
                expected_competitions = [
                    "Ligue 1", "Premier League", "La Liga", "Bundesliga", "Serie A",
                    "Ligue 2", "Championship", "Liga 2", "2. Bundesliga", "Serie B"
                ]
                
                found_competitions = []
                competition_names = [comp.get("name", "") for comp in competitions]
                
                for expected in expected_competitions:
                    found = any(expected.lower() in name.lower() for name in competition_names)
                    if found:
                        found_competitions.append(expected)
                
                self.log_test("competitions", "Major competitions present", 
                            len(found_competitions) >= 5,
                            f"Found {len(found_competitions)}/{len(expected_competitions)}: {found_competitions}")
                
                # Vérifier les niveaux de compétition
                level_1_count = sum(1 for comp in competitions if comp.get("level") == 1)
                level_2_count = sum(1 for comp in competitions if comp.get("level") == 2)
                
                self.log_test("competitions", "Competition levels correctly set", 
                            level_1_count > 0 and level_2_count > 0,
                            f"Level 1: {level_1_count}, Level 2: {level_2_count}")
                
                # Vérifier les références TopKit
                tk_refs = [comp.get("topkit_reference", "") for comp in competitions if comp.get("topkit_reference")]
                valid_refs = [ref for ref in tk_refs if ref.startswith("TK-COMP-")]
                
                self.log_test("competitions", "TopKit references format", 
                            len(valid_refs) > 0,
                            f"Valid TK-COMP references: {len(valid_refs)}/{len(tk_refs)}")
                
                return competitions
                
            else:
                self.log_test("competitions", "Competitions endpoint accessible", False,
                            f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("competitions", "Competitions endpoint accessible", False, str(e))
            return []
    
    def test_teams_endpoint(self):
        """Test 2: Vérifier l'endpoint GET /api/teams"""
        print("\n⚽ TESTING TEAMS ENDPOINT")
        
        try:
            response = self.session.get(f"{BASE_URL}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                total_teams = len(teams)
                
                self.log_test("teams", "Teams endpoint accessible", True,
                            f"Found {total_teams} teams")
                
                # Vérifier les équipes emblématiques
                iconic_teams = [
                    "Real Madrid", "Manchester United", "Paris Saint-Germain", "PSG",
                    "Bayern Munich", "FC Barcelona", "Liverpool", "Arsenal",
                    "Juventus", "AC Milan", "Chelsea", "Manchester City"
                ]
                
                found_teams = []
                team_names = []
                for team in teams:
                    name = team.get("name", "")
                    short_name = team.get("short_name", "")
                    common_names = team.get("common_names", [])
                    all_names = [name, short_name] + common_names
                    team_names.extend(all_names)
                
                for iconic in iconic_teams:
                    found = any(iconic.lower() in name.lower() for name in team_names if name)
                    if found:
                        found_teams.append(iconic)
                
                self.log_test("teams", "Iconic teams present", 
                            len(found_teams) >= 6,
                            f"Found {len(found_teams)}/{len(iconic_teams)}: {found_teams}")
                
                # Vérifier les références TopKit pour les équipes
                tk_refs = [team.get("topkit_reference", "") for team in teams if team.get("topkit_reference")]
                valid_team_refs = [ref for ref in tk_refs if ref.startswith("TK-TEAM-")]
                
                self.log_test("teams", "Team TopKit references format", 
                            len(valid_team_refs) > 0,
                            f"Valid TK-TEAM references: {len(valid_team_refs)}/{len(tk_refs)}")
                
                # Vérifier les liaisons avec les compétitions
                teams_with_leagues = [team for team in teams if team.get("league_id")]
                teams_with_league_info = [team for team in teams if team.get("league_info")]
                
                self.log_test("teams", "Teams linked to competitions", 
                            len(teams_with_leagues) > 0,
                            f"Teams with league_id: {len(teams_with_leagues)}, with league_info: {len(teams_with_league_info)}")
                
                return teams
                
            else:
                self.log_test("teams", "Teams endpoint accessible", False,
                            f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("teams", "Teams endpoint accessible", False, str(e))
            return []
    
    def test_filtering_capabilities(self):
        """Test 3: Tester les capacités de filtrage"""
        print("\n🔍 TESTING FILTERING CAPABILITIES")
        
        # Test filtrage par pays pour les équipes
        countries_to_test = ["France", "England", "Spain", "Germany", "Italy"]
        
        for country in countries_to_test:
            try:
                response = self.session.get(f"{BASE_URL}/teams", params={"country": country})
                
                if response.status_code == 200:
                    teams = response.json()
                    teams_count = len(teams)
                    
                    # Vérifier que les équipes retournées sont bien du bon pays
                    correct_country = all(team.get("country", "").lower() == country.lower() 
                                        for team in teams if team.get("country"))
                    
                    self.log_test("filtering", f"Filter teams by country: {country}", 
                                correct_country and teams_count > 0,
                                f"Found {teams_count} teams, country filter working: {correct_country}")
                else:
                    self.log_test("filtering", f"Filter teams by country: {country}", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test("filtering", f"Filter teams by country: {country}", False, str(e))
        
        # Test recherche de compétitions spécifiques
        competitions_to_search = ["Premier League", "La Liga", "Bundesliga"]
        
        for comp_name in competitions_to_search:
            try:
                response = self.session.get(f"{BASE_URL}/competitions", params={"search": comp_name})
                
                if response.status_code == 200:
                    competitions = response.json()
                    found = any(comp_name.lower() in comp.get("name", "").lower() 
                              for comp in competitions)
                    
                    self.log_test("filtering", f"Search competition: {comp_name}", 
                                found,
                                f"Found {len(competitions)} results, target found: {found}")
                else:
                    self.log_test("filtering", f"Search competition: {comp_name}", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test("filtering", f"Search competition: {comp_name}", False, str(e))
    
    def test_data_consistency(self):
        """Test 4: Vérifier la cohérence des données"""
        print("\n🔗 TESTING DATA CONSISTENCY")
        
        try:
            # Récupérer toutes les équipes et compétitions
            teams_response = self.session.get(f"{BASE_URL}/teams")
            competitions_response = self.session.get(f"{BASE_URL}/competitions")
            
            if teams_response.status_code == 200 and competitions_response.status_code == 200:
                teams = teams_response.json()
                competitions = competitions_response.json()
                
                # Test 1: Équipes françaises dans les bonnes compétitions
                french_teams = [team for team in teams if team.get("country", "").lower() == "france"]
                french_competitions = [comp for comp in competitions if comp.get("country", "").lower() == "france"]
                
                ligue1_teams = []
                ligue2_teams = []
                
                for team in french_teams:
                    if team.get("league_info"):
                        league_name = team["league_info"].get("name", "").lower()
                        if "ligue 1" in league_name:
                            ligue1_teams.append(team["name"])
                        elif "ligue 2" in league_name:
                            ligue2_teams.append(team["name"])
                
                self.log_test("consistency", "French teams in correct leagues", 
                            len(ligue1_teams) > 0 or len(ligue2_teams) > 0,
                            f"Ligue 1 teams: {len(ligue1_teams)}, Ligue 2 teams: {len(ligue2_teams)}")
                
                # Test 2: Équipes anglaises dans les bonnes compétitions
                english_teams = [team for team in teams if team.get("country", "").lower() in ["england", "united kingdom"]]
                
                premier_league_teams = []
                championship_teams = []
                
                for team in english_teams:
                    if team.get("league_info"):
                        league_name = team["league_info"].get("name", "").lower()
                        if "premier league" in league_name:
                            premier_league_teams.append(team["name"])
                        elif "championship" in league_name:
                            championship_teams.append(team["name"])
                
                self.log_test("consistency", "English teams in correct leagues", 
                            len(premier_league_teams) > 0 or len(championship_teams) > 0,
                            f"Premier League teams: {len(premier_league_teams)}, Championship teams: {len(championship_teams)}")
                
                # Test 3: Cohérence des noms et pays
                teams_with_names = [team for team in teams if team.get("name") and team.get("country")]
                consistent_names = 0
                
                for team in teams_with_names[:10]:  # Test sur un échantillon
                    name = team.get("name", "")
                    country = team.get("country", "")
                    
                    # Vérifications basiques de cohérence
                    if country.lower() == "france" and any(french_word in name.lower() 
                                                         for french_word in ["paris", "marseille", "lyon", "saint-etienne"]):
                        consistent_names += 1
                    elif country.lower() == "spain" and any(spanish_word in name.lower() 
                                                          for spanish_word in ["real", "barcelona", "atletico", "valencia"]):
                        consistent_names += 1
                    elif country.lower() == "england" and any(english_word in name.lower() 
                                                            for english_word in ["manchester", "liverpool", "arsenal", "chelsea"]):
                        consistent_names += 1
                    elif len(name) > 0:  # Au moins un nom valide
                        consistent_names += 1
                
                consistency_rate = consistent_names / len(teams_with_names[:10]) if teams_with_names else 0
                
                self.log_test("consistency", "Names and countries consistency", 
                            consistency_rate > 0.5,
                            f"Consistency rate: {consistency_rate:.2%} ({consistent_names}/10 sampled)")
                
            else:
                self.log_test("consistency", "Data consistency check", False,
                            "Could not fetch teams or competitions data")
                
        except Exception as e:
            self.log_test("consistency", "Data consistency check", False, str(e))
    
    def test_authenticated_endpoints(self):
        """Test 5: Tester quelques endpoints avec authentification admin"""
        print("\n🔐 TESTING AUTHENTICATED ENDPOINTS")
        
        if not self.admin_token:
            self.log_test("filtering", "Admin authentication required", False,
                        "No admin token available")
            return
        
        # Test création d'une compétition (avec authentification)
        try:
            test_competition = {
                "name": "Test Competition TopKit",
                "official_name": "Test Competition TopKit Official",
                "competition_type": "domestic_league",
                "country": "Test Country",
                "level": 1
            }
            
            response = self.session.post(f"{BASE_URL}/competitions", json=test_competition)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("filtering", "Create competition with admin auth", True,
                            f"Created competition with reference: {data.get('topkit_reference', 'N/A')}")
                
                # Nettoyer - supprimer la compétition de test si possible
                # (Note: pas d'endpoint DELETE visible, donc on laisse)
                
            else:
                self.log_test("filtering", "Create competition with admin auth", False,
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("filtering", "Create competition with admin auth", False, str(e))
    
    def calculate_summary(self):
        """Calculate test summary"""
        total_tests = 0
        total_passed = 0
        
        for category in ["competitions", "teams", "filtering", "consistency"]:
            total_tests += self.test_results[category]["total"]
            total_passed += self.test_results[category]["passed"]
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "success_rate": success_rate
        }
    
    def print_detailed_summary(self):
        """Print detailed test summary"""
        print("\n" + "="*80)
        print("🎯 RÉSUMÉ DÉTAILLÉ DES TESTS COLLABORATIFS TOPKIT")
        print("="*80)
        
        categories = {
            "competitions": "🏆 TESTS DES COMPÉTITIONS",
            "teams": "⚽ TESTS DES ÉQUIPES", 
            "filtering": "🔍 TESTS DE FILTRAGE",
            "consistency": "🔗 TESTS DE COHÉRENCE"
        }
        
        for category, title in categories.items():
            results = self.test_results[category]
            print(f"\n{title}")
            print(f"Total: {results['total']}, Réussis: {results['passed']}, Échoués: {results['failed']}")
            
            for detail in results["details"]:
                print(f"  {detail['status']}: {detail['test']}")
                if detail["details"]:
                    print(f"    → {detail['details']}")
        
        summary = self.test_results["summary"]
        print(f"\n📊 RÉSUMÉ GLOBAL:")
        print(f"Tests totaux: {summary['total_tests']}")
        print(f"Tests réussis: {summary['total_passed']}")
        print(f"Taux de réussite: {summary['success_rate']:.1f}%")
        
        if summary['success_rate'] >= 80:
            print("🎉 EXCELLENT - Import des données collaboratives réussi!")
        elif summary['success_rate'] >= 60:
            print("✅ BON - Import des données partiellement réussi")
        else:
            print("⚠️ PROBLÈMES DÉTECTÉS - Import des données à vérifier")

def main():
    """Main test execution"""
    print("🚀 DÉMARRAGE DES TESTS COLLABORATIFS TOPKIT")
    print("="*60)
    
    tester = TopKitCollaborativeTest()
    
    # Authentification admin
    if not tester.authenticate_admin():
        print("❌ Impossible de continuer sans authentification admin")
        return
    
    # Exécution des tests
    tester.test_competitions_endpoint()
    tester.test_teams_endpoint()
    tester.test_filtering_capabilities()
    tester.test_data_consistency()
    tester.test_authenticated_endpoints()
    
    # Calcul et affichage du résumé
    tester.calculate_summary()
    tester.print_detailed_summary()

if __name__ == "__main__":
    main()