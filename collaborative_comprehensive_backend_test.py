#!/usr/bin/env python3
"""
Test complet des endpoints collaboratifs TopKit
Vérification approfondie de l'import des données avec gestion des langues
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://kit-collection-5.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitCollaborativeTestComplete:
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
    
    def test_competitions_comprehensive(self):
        """Test complet des compétitions"""
        print("\n🏆 TESTING COMPETITIONS - COMPREHENSIVE")
        
        try:
            response = self.session.get(f"{BASE_URL}/competitions")
            
            if response.status_code == 200:
                competitions = response.json()
                total_competitions = len(competitions)
                
                self.log_test("competitions", "Competitions endpoint accessible", True, 
                            f"Found {total_competitions} competitions")
                
                # Analyse détaillée des compétitions par pays
                competitions_by_country = {}
                for comp in competitions:
                    country = comp.get("country", "Unknown")
                    if country not in competitions_by_country:
                        competitions_by_country[country] = []
                    competitions_by_country[country].append(comp.get("name", ""))
                
                print(f"📊 Compétitions par pays:")
                for country, comps in competitions_by_country.items():
                    print(f"  {country}: {len(comps)} compétitions")
                    for comp in comps[:3]:  # Afficher les 3 premières
                        print(f"    - {comp}")
                    if len(comps) > 3:
                        print(f"    ... et {len(comps)-3} autres")
                
                # Vérifier les compétitions majeures avec noms français/anglais
                major_competitions = {
                    "France": ["Ligue 1", "Ligue 2"],
                    "Angleterre": ["Premier League", "Championship"],
                    "Espagne": ["La Liga", "Liga 2", "Primera División"],
                    "Allemagne": ["Bundesliga", "2. Bundesliga"],
                    "Italie": ["Serie A", "Serie B"]
                }
                
                found_major = 0
                total_major = 0
                
                for country, expected_comps in major_competitions.items():
                    country_comps = competitions_by_country.get(country, [])
                    for expected in expected_comps:
                        total_major += 1
                        found = any(expected.lower() in comp.lower() for comp in country_comps)
                        if found:
                            found_major += 1
                
                self.log_test("competitions", "Major competitions coverage", 
                            found_major >= total_major * 0.7,
                            f"Found {found_major}/{total_major} major competitions")
                
                # Vérifier les niveaux
                level_distribution = {}
                for comp in competitions:
                    level = comp.get("level", "Unknown")
                    level_distribution[level] = level_distribution.get(level, 0) + 1
                
                self.log_test("competitions", "Competition levels distribution", 
                            level_distribution.get(1, 0) > 0 and level_distribution.get(2, 0) > 0,
                            f"Level distribution: {level_distribution}")
                
                return competitions
                
            else:
                self.log_test("competitions", "Competitions endpoint accessible", False,
                            f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("competitions", "Competitions endpoint accessible", False, str(e))
            return []
    
    def test_teams_comprehensive(self):
        """Test complet des équipes"""
        print("\n⚽ TESTING TEAMS - COMPREHENSIVE")
        
        try:
            response = self.session.get(f"{BASE_URL}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                total_teams = len(teams)
                
                self.log_test("teams", "Teams endpoint accessible", True,
                            f"Found {total_teams} teams")
                
                # Analyse par pays (avec noms français)
                teams_by_country = {}
                for team in teams:
                    country = team.get("country", "Unknown")
                    if country not in teams_by_country:
                        teams_by_country[country] = []
                    teams_by_country[country].append(team.get("name", ""))
                
                print(f"📊 Équipes par pays:")
                for country, team_names in teams_by_country.items():
                    print(f"  {country}: {len(team_names)} équipes")
                    # Afficher quelques exemples
                    for name in team_names[:3]:
                        print(f"    - {name}")
                    if len(team_names) > 3:
                        print(f"    ... et {len(team_names)-3} autres")
                
                # Test des équipes emblématiques par pays
                iconic_teams_by_country = {
                    "France": ["Paris Saint-Germain", "PSG", "Olympique de Marseille", "Olympique Lyonnais"],
                    "Angleterre": ["Manchester United", "Liverpool", "Arsenal", "Chelsea", "Manchester City"],
                    "Espagne": ["Real Madrid", "FC Barcelona", "Atletico Madrid"],
                    "Allemagne": ["Bayern Munich", "Borussia Dortmund"],
                    "Italie": ["Juventus", "AC Milan", "Inter Milan"]
                }
                
                found_iconic = 0
                total_iconic = 0
                
                for country, iconic_list in iconic_teams_by_country.items():
                    country_teams = teams_by_country.get(country, [])
                    for iconic in iconic_list:
                        total_iconic += 1
                        found = any(iconic.lower() in team.lower() for team in country_teams)
                        if found:
                            found_iconic += 1
                
                self.log_test("teams", "Iconic teams coverage", 
                            found_iconic >= total_iconic * 0.6,
                            f"Found {found_iconic}/{total_iconic} iconic teams")
                
                # Vérifier les références TopKit
                valid_refs = 0
                for team in teams:
                    ref = team.get("topkit_reference", "")
                    if ref.startswith("TK-TEAM-") and len(ref) >= 12:
                        valid_refs += 1
                
                self.log_test("teams", "TopKit references quality", 
                            valid_refs == total_teams,
                            f"Valid references: {valid_refs}/{total_teams}")
                
                # Vérifier les liaisons avec compétitions
                teams_with_league_info = [team for team in teams if team.get("league_info")]
                
                self.log_test("teams", "Teams-competitions linking", 
                            len(teams_with_league_info) >= total_teams * 0.8,
                            f"Teams with league info: {len(teams_with_league_info)}/{total_teams}")
                
                return teams
                
            else:
                self.log_test("teams", "Teams endpoint accessible", False,
                            f"HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("teams", "Teams endpoint accessible", False, str(e))
            return []
    
    def test_filtering_advanced(self):
        """Test avancé des capacités de filtrage"""
        print("\n🔍 TESTING FILTERING - ADVANCED")
        
        # Test filtrage par pays (avec noms français corrects)
        countries_to_test = [
            ("France", "France"),
            ("Angleterre", "England"),  # Nom français pour l'Angleterre
            ("Espagne", "Spain"),
            ("Allemagne", "Germany"),   # Nom français pour l'Allemagne
            ("Italie", "Italy")
        ]
        
        for french_name, english_name in countries_to_test:
            try:
                response = self.session.get(f"{BASE_URL}/teams", params={"country": french_name})
                
                if response.status_code == 200:
                    teams = response.json()
                    teams_count = len(teams)
                    
                    # Vérifier que les équipes retournées sont bien du bon pays
                    correct_country = all(team.get("country", "").lower() == french_name.lower() 
                                        for team in teams if team.get("country"))
                    
                    self.log_test("filtering", f"Filter teams by country: {english_name} ({french_name})", 
                                teams_count > 0 and correct_country,
                                f"Found {teams_count} teams, filter working: {correct_country}")
                else:
                    self.log_test("filtering", f"Filter teams by country: {english_name} ({french_name})", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test("filtering", f"Filter teams by country: {english_name} ({french_name})", False, str(e))
        
        # Test recherche d'équipes spécifiques
        teams_to_search = ["Real Madrid", "Manchester United", "PSG", "Bayern Munich"]
        
        for team_name in teams_to_search:
            try:
                response = self.session.get(f"{BASE_URL}/teams", params={"search": team_name})
                
                if response.status_code == 200:
                    teams = response.json()
                    found = any(team_name.lower() in team.get("name", "").lower() 
                              for team in teams)
                    
                    self.log_test("filtering", f"Search team: {team_name}", 
                                found,
                                f"Found {len(teams)} results, target found: {found}")
                else:
                    self.log_test("filtering", f"Search team: {team_name}", False,
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test("filtering", f"Search team: {team_name}", False, str(e))
    
    def test_data_consistency_advanced(self):
        """Test avancé de cohérence des données"""
        print("\n🔗 TESTING DATA CONSISTENCY - ADVANCED")
        
        try:
            # Récupérer toutes les données
            teams_response = self.session.get(f"{BASE_URL}/teams")
            competitions_response = self.session.get(f"{BASE_URL}/competitions")
            
            if teams_response.status_code == 200 and competitions_response.status_code == 200:
                teams = teams_response.json()
                competitions = competitions_response.json()
                
                # Test 1: Cohérence équipes françaises
                french_teams = [team for team in teams if team.get("country", "").lower() == "france"]
                
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
                            len(ligue1_teams) >= 15 and len(ligue2_teams) >= 10,
                            f"Ligue 1: {len(ligue1_teams)} teams, Ligue 2: {len(ligue2_teams)} teams")
                
                # Test 2: Cohérence équipes anglaises (avec nom français "Angleterre")
                english_teams = [team for team in teams if team.get("country", "").lower() == "angleterre"]
                
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
                            len(premier_league_teams) >= 10 or len(championship_teams) >= 10,
                            f"Premier League: {len(premier_league_teams)} teams, Championship: {len(championship_teams)} teams")
                
                # Test 3: Vérification des références TopKit uniques
                team_refs = [team.get("topkit_reference") for team in teams if team.get("topkit_reference")]
                comp_refs = [comp.get("topkit_reference") for comp in competitions if comp.get("topkit_reference")]
                
                unique_team_refs = len(set(team_refs))
                unique_comp_refs = len(set(comp_refs))
                
                self.log_test("consistency", "TopKit references uniqueness", 
                            unique_team_refs == len(team_refs) and unique_comp_refs == len(comp_refs),
                            f"Team refs: {unique_team_refs}/{len(team_refs)} unique, Comp refs: {unique_comp_refs}/{len(comp_refs)} unique")
                
                # Test 4: Vérification de la structure des données
                complete_teams = 0
                for team in teams[:20]:  # Test sur échantillon
                    if (team.get("name") and team.get("country") and 
                        team.get("topkit_reference") and team.get("created_at")):
                        complete_teams += 1
                
                completeness_rate = complete_teams / 20
                
                self.log_test("consistency", "Data structure completeness", 
                            completeness_rate >= 0.9,
                            f"Complete data structure: {completeness_rate:.1%} ({complete_teams}/20 sampled)")
                
            else:
                self.log_test("consistency", "Data consistency check", False,
                            "Could not fetch teams or competitions data")
                
        except Exception as e:
            self.log_test("consistency", "Data consistency check", False, str(e))
    
    def test_specific_requirements(self):
        """Test des exigences spécifiques de la review request"""
        print("\n🎯 TESTING SPECIFIC REQUIREMENTS")
        
        try:
            # Test spécifique: Rechercher "Premier League"
            response = self.session.get(f"{BASE_URL}/competitions", params={"search": "Premier League"})
            if response.status_code == 200:
                competitions = response.json()
                premier_found = any("premier league" in comp.get("name", "").lower() for comp in competitions)
                self.log_test("filtering", "Find Premier League specifically", premier_found,
                            f"Premier League found in {len(competitions)} results")
            
            # Test spécifique: Rechercher "Real Madrid"
            response = self.session.get(f"{BASE_URL}/teams", params={"search": "Real Madrid"})
            if response.status_code == 200:
                teams = response.json()
                real_found = any("real madrid" in team.get("name", "").lower() for team in teams)
                self.log_test("filtering", "Find Real Madrid specifically", real_found,
                            f"Real Madrid found in {len(teams)} results")
            
            # Test spécifique: Vérifier PSG
            response = self.session.get(f"{BASE_URL}/teams", params={"search": "PSG"})
            if response.status_code == 200:
                teams = response.json()
                psg_found = any("psg" in team.get("name", "").lower() or 
                              "paris saint-germain" in team.get("name", "").lower() for team in teams)
                self.log_test("filtering", "Find PSG specifically", psg_found,
                            f"PSG found in {len(teams)} results")
            
            # Test spécifique: Vérifier Bayern Munich
            response = self.session.get(f"{BASE_URL}/teams", params={"search": "Bayern"})
            if response.status_code == 200:
                teams = response.json()
                bayern_found = any("bayern" in team.get("name", "").lower() for team in teams)
                self.log_test("filtering", "Find Bayern Munich specifically", bayern_found,
                            f"Bayern found in {len(teams)} results")
                
        except Exception as e:
            self.log_test("filtering", "Specific requirements test", False, str(e))
    
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
    
    def print_final_summary(self):
        """Print final comprehensive summary"""
        print("\n" + "="*80)
        print("🎯 RAPPORT FINAL - TESTS COLLABORATIFS TOPKIT")
        print("="*80)
        
        categories = {
            "competitions": "🏆 COMPÉTITIONS",
            "teams": "⚽ ÉQUIPES", 
            "filtering": "🔍 FILTRAGE & RECHERCHE",
            "consistency": "🔗 COHÉRENCE DES DONNÉES"
        }
        
        for category, title in categories.items():
            results = self.test_results[category]
            success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
            print(f"\n{title}: {success_rate:.1f}% ({results['passed']}/{results['total']})")
            
            for detail in results["details"]:
                status_icon = "✅" if "PASS" in detail['status'] else "❌"
                print(f"  {status_icon} {detail['test']}")
                if detail["details"]:
                    print(f"    → {detail['details']}")
        
        summary = self.test_results["summary"]
        print(f"\n📊 RÉSUMÉ GLOBAL:")
        print(f"Tests totaux: {summary['total_tests']}")
        print(f"Tests réussis: {summary['total_passed']}")
        print(f"Taux de réussite: {summary['success_rate']:.1f}%")
        
        print(f"\n🎯 CONCLUSION:")
        if summary['success_rate'] >= 85:
            print("🎉 EXCELLENT - L'import des données collaboratives est un succès complet!")
            print("   Toutes les compétitions et équipes majeures sont présentes et bien structurées.")
        elif summary['success_rate'] >= 70:
            print("✅ TRÈS BON - L'import des données est largement réussi avec quelques points mineurs.")
            print("   Les fonctionnalités principales sont opérationnelles.")
        elif summary['success_rate'] >= 50:
            print("⚠️ ACCEPTABLE - L'import des données fonctionne mais nécessite des améliorations.")
        else:
            print("❌ PROBLÉMATIQUE - L'import des données présente des défauts majeurs à corriger.")
        
        print(f"\n📋 RECOMMANDATIONS:")
        if summary['success_rate'] < 100:
            print("• Vérifier les liaisons équipes-compétitions manquantes")
            print("• Harmoniser les noms de pays (Angleterre vs England)")
            print("• Compléter les équipes manquantes pour certains pays")
        else:
            print("• Aucune action corrective nécessaire - système opérationnel")

def main():
    """Main test execution"""
    print("🚀 TESTS COLLABORATIFS TOPKIT - VERSION COMPLÈTE")
    print("="*60)
    
    tester = TopKitCollaborativeTestComplete()
    
    # Authentification admin
    if not tester.authenticate_admin():
        print("❌ Impossible de continuer sans authentification admin")
        return
    
    # Exécution des tests
    tester.test_competitions_comprehensive()
    tester.test_teams_comprehensive()
    tester.test_filtering_advanced()
    tester.test_data_consistency_advanced()
    tester.test_specific_requirements()
    
    # Calcul et affichage du résumé final
    tester.calculate_summary()
    tester.print_final_summary()

if __name__ == "__main__":
    main()