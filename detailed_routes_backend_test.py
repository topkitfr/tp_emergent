#!/usr/bin/env python3
"""
TopKit Detailed Routes Backend Testing
Test des nouvelles routes détaillées pour les fiches selon la demande de review
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration des URLs
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"

class TopKitDetailedRoutesTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_teams_endpoint(self):
        """Test 1: Endpoint /api/teams"""
        print("🏆 TEST 1: ENDPOINT /api/teams")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                teams = response.json()
                
                if isinstance(teams, list) and len(teams) > 0:
                    # Analyser la structure des données
                    sample_team = teams[0]
                    required_fields = ['id', 'name', 'country', 'city']
                    optional_fields = ['logo_url', 'founded', 'colors', 'stadium']
                    
                    # Vérifier les champs requis
                    missing_required = [field for field in required_fields if field not in sample_team]
                    present_optional = [field for field in optional_fields if field in sample_team and sample_team[field] is not None]
                    
                    # Compter les équipes avec logo_url
                    teams_with_logo = sum(1 for team in teams if team.get('logo_url'))
                    
                    # Chercher FC Barcelona spécifiquement
                    fc_barcelona = None
                    for team in teams:
                        if 'barcelona' in team.get('name', '').lower() or 'barça' in team.get('name', '').lower():
                            fc_barcelona = team
                            break
                    
                    self.log_test(
                        "Teams Endpoint Structure", 
                        len(missing_required) == 0, 
                        f"Total teams: {len(teams)}, Teams with logo_url: {teams_with_logo}, "
                        f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, "
                        f"Optional fields present: {present_optional}, "
                        f"FC Barcelona found: {'Yes' if fc_barcelona else 'No'}",
                        f"Missing required fields: {missing_required}" if missing_required else ""
                    )
                    
                    # Test spécifique FC Barcelona
                    if fc_barcelona:
                        self.test_specific_team_data(fc_barcelona, "FC Barcelona")
                    
                    return len(missing_required) == 0
                else:
                    self.log_test(
                        "Teams Endpoint Structure", 
                        False, 
                        error="Aucune équipe trouvée ou format de réponse incorrect"
                    )
                    return False
            else:
                self.log_test(
                    "Teams Endpoint Structure", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Teams Endpoint Structure", False, error=str(e))
            return False

    def test_specific_team_data(self, team_data, team_name):
        """Test spécifique pour les données d'une équipe"""
        try:
            # Vérifier les données complètes pour les fiches détaillées
            completeness_score = 0
            total_fields = 8
            
            fields_to_check = {
                'name': team_data.get('name'),
                'country': team_data.get('country'),
                'city': team_data.get('city'),
                'logo_url': team_data.get('logo_url'),
                'founded': team_data.get('founded'),
                'colors': team_data.get('colors'),
                'stadium': team_data.get('stadium'),
                'league': team_data.get('league')
            }
            
            for field, value in fields_to_check.items():
                if value is not None and value != "":
                    completeness_score += 1
            
            completeness_percentage = (completeness_score / total_fields) * 100
            
            self.log_test(
                f"{team_name} Data Completeness", 
                completeness_percentage >= 50,  # Au moins 50% des champs remplis
                f"Completeness: {completeness_percentage:.1f}% ({completeness_score}/{total_fields} fields), "
                f"Logo URL: {'Present' if team_data.get('logo_url') else 'Missing'}, "
                f"Founded: {team_data.get('founded', 'N/A')}, "
                f"Stadium: {team_data.get('stadium', 'N/A')}",
                f"Insufficient data for detailed page" if completeness_percentage < 50 else ""
            )
            
            return completeness_percentage >= 50
            
        except Exception as e:
            self.log_test(f"{team_name} Data Completeness", False, error=str(e))
            return False

    def test_brands_endpoint(self):
        """Test 2: Endpoint /api/brands"""
        print("👕 TEST 2: ENDPOINT /api/brands")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/brands")
            
            if response.status_code == 200:
                brands = response.json()
                
                if isinstance(brands, list) and len(brands) > 0:
                    # Analyser la structure des données
                    sample_brand = brands[0]
                    required_fields = ['id', 'name']
                    optional_fields = ['logo_url', 'country', 'founded', 'website']
                    
                    # Vérifier les champs requis
                    missing_required = [field for field in required_fields if field not in sample_brand]
                    present_optional = [field for field in optional_fields if field in sample_brand and sample_brand[field] is not None]
                    
                    # Compter les marques avec logo_url
                    brands_with_logo = sum(1 for brand in brands if brand.get('logo_url'))
                    
                    # Chercher Nike spécifiquement
                    nike_brand = None
                    for brand in brands:
                        if 'nike' in brand.get('name', '').lower():
                            nike_brand = brand
                            break
                    
                    self.log_test(
                        "Brands Endpoint Structure", 
                        len(missing_required) == 0, 
                        f"Total brands: {len(brands)}, Brands with logo_url: {brands_with_logo}, "
                        f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, "
                        f"Optional fields present: {present_optional}, "
                        f"Nike found: {'Yes' if nike_brand else 'No'}",
                        f"Missing required fields: {missing_required}" if missing_required else ""
                    )
                    
                    # Test spécifique Nike
                    if nike_brand:
                        self.test_specific_brand_data(nike_brand, "Nike")
                    
                    return len(missing_required) == 0
                else:
                    self.log_test(
                        "Brands Endpoint Structure", 
                        False, 
                        error="Aucune marque trouvée ou format de réponse incorrect"
                    )
                    return False
            else:
                self.log_test(
                    "Brands Endpoint Structure", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Brands Endpoint Structure", False, error=str(e))
            return False

    def test_specific_brand_data(self, brand_data, brand_name):
        """Test spécifique pour les données d'une marque"""
        try:
            # Vérifier les données complètes pour les fiches détaillées
            completeness_score = 0
            total_fields = 6
            
            fields_to_check = {
                'name': brand_data.get('name'),
                'logo_url': brand_data.get('logo_url'),
                'country': brand_data.get('country'),
                'founded': brand_data.get('founded'),
                'website': brand_data.get('website'),
                'description': brand_data.get('description')
            }
            
            for field, value in fields_to_check.items():
                if value is not None and value != "":
                    completeness_score += 1
            
            completeness_percentage = (completeness_score / total_fields) * 100
            
            self.log_test(
                f"{brand_name} Data Completeness", 
                completeness_percentage >= 40,  # Au moins 40% des champs remplis
                f"Completeness: {completeness_percentage:.1f}% ({completeness_score}/{total_fields} fields), "
                f"Logo URL: {'Present' if brand_data.get('logo_url') else 'Missing'}, "
                f"Country: {brand_data.get('country', 'N/A')}, "
                f"Website: {brand_data.get('website', 'N/A')}",
                f"Insufficient data for detailed page" if completeness_percentage < 40 else ""
            )
            
            return completeness_percentage >= 40
            
        except Exception as e:
            self.log_test(f"{brand_name} Data Completeness", False, error=str(e))
            return False

    def test_competitions_endpoint(self):
        """Test 3: Endpoint /api/competitions"""
        print("🏆 TEST 3: ENDPOINT /api/competitions")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/competitions")
            
            if response.status_code == 200:
                competitions = response.json()
                
                if isinstance(competitions, list) and len(competitions) > 0:
                    # Analyser la structure des données
                    sample_competition = competitions[0]
                    required_fields = ['id', 'name']
                    optional_fields = ['logo_url', 'country', 'type', 'founded', 'organizer']
                    
                    # Vérifier les champs requis
                    missing_required = [field for field in required_fields if field not in sample_competition]
                    present_optional = [field for field in optional_fields if field in sample_competition and sample_competition[field] is not None]
                    
                    # Compter les compétitions avec logo_url
                    competitions_with_logo = sum(1 for comp in competitions if comp.get('logo_url'))
                    
                    # Chercher La Liga spécifiquement
                    la_liga = None
                    for comp in competitions:
                        if 'liga' in comp.get('name', '').lower() or 'laliga' in comp.get('name', '').lower():
                            la_liga = comp
                            break
                    
                    self.log_test(
                        "Competitions Endpoint Structure", 
                        len(missing_required) == 0, 
                        f"Total competitions: {len(competitions)}, Competitions with logo_url: {competitions_with_logo}, "
                        f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, "
                        f"Optional fields present: {present_optional}, "
                        f"La Liga found: {'Yes' if la_liga else 'No'}",
                        f"Missing required fields: {missing_required}" if missing_required else ""
                    )
                    
                    # Test spécifique La Liga
                    if la_liga:
                        self.test_specific_competition_data(la_liga, "La Liga")
                    
                    return len(missing_required) == 0
                else:
                    self.log_test(
                        "Competitions Endpoint Structure", 
                        False, 
                        error="Aucune compétition trouvée ou format de réponse incorrect"
                    )
                    return False
            else:
                self.log_test(
                    "Competitions Endpoint Structure", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Competitions Endpoint Structure", False, error=str(e))
            return False

    def test_specific_competition_data(self, comp_data, comp_name):
        """Test spécifique pour les données d'une compétition"""
        try:
            # Vérifier les données complètes pour les fiches détaillées
            completeness_score = 0
            total_fields = 7
            
            fields_to_check = {
                'name': comp_data.get('name'),
                'logo_url': comp_data.get('logo_url'),
                'country': comp_data.get('country'),
                'type': comp_data.get('type'),
                'founded': comp_data.get('founded'),
                'organizer': comp_data.get('organizer'),
                'description': comp_data.get('description')
            }
            
            for field, value in fields_to_check.items():
                if value is not None and value != "":
                    completeness_score += 1
            
            completeness_percentage = (completeness_score / total_fields) * 100
            
            self.log_test(
                f"{comp_name} Data Completeness", 
                completeness_percentage >= 40,  # Au moins 40% des champs remplis
                f"Completeness: {completeness_percentage:.1f}% ({completeness_score}/{total_fields} fields), "
                f"Logo URL: {'Present' if comp_data.get('logo_url') else 'Missing'}, "
                f"Type: {comp_data.get('type', 'N/A')}, "
                f"Founded: {comp_data.get('founded', 'N/A')}",
                f"Insufficient data for detailed page" if completeness_percentage < 40 else ""
            )
            
            return completeness_percentage >= 40
            
        except Exception as e:
            self.log_test(f"{comp_name} Data Completeness", False, error=str(e))
            return False

    def test_players_endpoint(self):
        """Test 4: Endpoint /api/players"""
        print("⚽ TEST 4: ENDPOINT /api/players")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/players")
            
            if response.status_code == 200:
                players = response.json()
                
                if isinstance(players, list):
                    if len(players) > 0:
                        # Analyser la structure des données
                        sample_player = players[0]
                        required_fields = ['id', 'name']
                        optional_fields = ['photo_url', 'position', 'nationality', 'birth_date', 'current_team']
                        
                        # Vérifier les champs requis
                        missing_required = [field for field in required_fields if field not in sample_player]
                        present_optional = [field for field in optional_fields if field in sample_player and sample_player[field] is not None]
                        
                        # Compter les joueurs avec photo_url
                        players_with_photo = sum(1 for player in players if player.get('photo_url'))
                        
                        # Chercher Messi spécifiquement
                        messi = None
                        for player in players:
                            if 'messi' in player.get('name', '').lower():
                                messi = player
                                break
                        
                        self.log_test(
                            "Players Endpoint Structure", 
                            len(missing_required) == 0, 
                            f"Total players: {len(players)}, Players with photo_url: {players_with_photo}, "
                            f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, "
                            f"Optional fields present: {present_optional}, "
                            f"Messi found: {'Yes' if messi else 'No'}",
                            f"Missing required fields: {missing_required}" if missing_required else ""
                        )
                        
                        # Test spécifique Messi
                        if messi:
                            self.test_specific_player_data(messi, "Lionel Messi")
                        
                        return len(missing_required) == 0
                    else:
                        self.log_test(
                            "Players Endpoint Structure", 
                            True,  # Pas d'erreur si pas de joueurs
                            "Aucun joueur trouvé - collection vide mais endpoint fonctionnel"
                        )
                        return True
                else:
                    self.log_test(
                        "Players Endpoint Structure", 
                        False, 
                        error="Format de réponse incorrect - attendu: liste"
                    )
                    return False
            else:
                self.log_test(
                    "Players Endpoint Structure", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Players Endpoint Structure", False, error=str(e))
            return False

    def test_specific_player_data(self, player_data, player_name):
        """Test spécifique pour les données d'un joueur"""
        try:
            # Vérifier les données complètes pour les fiches détaillées
            completeness_score = 0
            total_fields = 8
            
            fields_to_check = {
                'name': player_data.get('name'),
                'photo_url': player_data.get('photo_url'),
                'position': player_data.get('position'),
                'nationality': player_data.get('nationality'),
                'birth_date': player_data.get('birth_date'),
                'current_team': player_data.get('current_team'),
                'height': player_data.get('height'),
                'weight': player_data.get('weight')
            }
            
            for field, value in fields_to_check.items():
                if value is not None and value != "":
                    completeness_score += 1
            
            completeness_percentage = (completeness_score / total_fields) * 100
            
            self.log_test(
                f"{player_name} Data Completeness", 
                completeness_percentage >= 40,  # Au moins 40% des champs remplis
                f"Completeness: {completeness_percentage:.1f}% ({completeness_score}/{total_fields} fields), "
                f"Photo URL: {'Present' if player_data.get('photo_url') else 'Missing'}, "
                f"Position: {player_data.get('position', 'N/A')}, "
                f"Team: {player_data.get('current_team', 'N/A')}",
                f"Insufficient data for detailed page" if completeness_percentage < 40 else ""
            )
            
            return completeness_percentage >= 40
            
        except Exception as e:
            self.log_test(f"{player_name} Data Completeness", False, error=str(e))
            return False

    def test_master_jerseys_endpoint(self):
        """Test 5: Endpoint /api/master-jerseys"""
        print("👕 TEST 5: ENDPOINT /api/master-jerseys")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            
            if response.status_code == 200:
                master_jerseys = response.json()
                
                if isinstance(master_jerseys, list):
                    if len(master_jerseys) > 0:
                        # Analyser la structure des données
                        sample_jersey = master_jerseys[0]
                        required_fields = ['id', 'name', 'team_id', 'season']
                        optional_fields = ['images', 'description', 'type', 'manufacturer', 'colors']
                        
                        # Vérifier les champs requis
                        missing_required = [field for field in required_fields if field not in sample_jersey]
                        present_optional = [field for field in optional_fields if field in sample_jersey and sample_jersey[field] is not None]
                        
                        # Compter les maillots avec images
                        jerseys_with_images = sum(1 for jersey in master_jerseys if jersey.get('images'))
                        
                        # Chercher un maillot Barcelona spécifiquement
                        barcelona_jersey = None
                        for jersey in master_jerseys:
                            if 'barcelona' in jersey.get('name', '').lower() or 'barça' in jersey.get('name', '').lower():
                                barcelona_jersey = jersey
                                break
                        
                        self.log_test(
                            "Master Jerseys Endpoint Structure", 
                            len(missing_required) == 0, 
                            f"Total master jerseys: {len(master_jerseys)}, Jerseys with images: {jerseys_with_images}, "
                            f"Required fields present: {len(required_fields) - len(missing_required)}/{len(required_fields)}, "
                            f"Optional fields present: {present_optional}, "
                            f"Barcelona jersey found: {'Yes' if barcelona_jersey else 'No'}",
                            f"Missing required fields: {missing_required}" if missing_required else ""
                        )
                        
                        # Test spécifique maillot Barcelona
                        if barcelona_jersey:
                            self.test_specific_master_jersey_data(barcelona_jersey, "Barcelona Jersey")
                        
                        return len(missing_required) == 0
                    else:
                        self.log_test(
                            "Master Jerseys Endpoint Structure", 
                            True,  # Pas d'erreur si pas de maillots
                            "Aucun master jersey trouvé - collection vide mais endpoint fonctionnel"
                        )
                        return True
                else:
                    self.log_test(
                        "Master Jerseys Endpoint Structure", 
                        False, 
                        error="Format de réponse incorrect - attendu: liste"
                    )
                    return False
            else:
                self.log_test(
                    "Master Jerseys Endpoint Structure", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Master Jerseys Endpoint Structure", False, error=str(e))
            return False

    def test_specific_master_jersey_data(self, jersey_data, jersey_name):
        """Test spécifique pour les données d'un master jersey"""
        try:
            # Vérifier les données complètes pour les fiches détaillées
            completeness_score = 0
            total_fields = 9
            
            fields_to_check = {
                'name': jersey_data.get('name'),
                'team_id': jersey_data.get('team_id'),
                'season': jersey_data.get('season'),
                'images': jersey_data.get('images'),
                'description': jersey_data.get('description'),
                'type': jersey_data.get('type'),
                'manufacturer': jersey_data.get('manufacturer'),
                'colors': jersey_data.get('colors'),
                'price_range': jersey_data.get('price_range')
            }
            
            for field, value in fields_to_check.items():
                if value is not None and value != "":
                    completeness_score += 1
            
            completeness_percentage = (completeness_score / total_fields) * 100
            
            # Analyser les images si présentes
            images_info = "No images"
            if jersey_data.get('images'):
                images = jersey_data['images']
                if isinstance(images, list):
                    images_info = f"{len(images)} images"
                elif isinstance(images, dict):
                    images_info = f"Images dict with keys: {list(images.keys())}"
                else:
                    images_info = "Images present (unknown format)"
            
            self.log_test(
                f"{jersey_name} Data Completeness", 
                completeness_percentage >= 50,  # Au moins 50% des champs remplis
                f"Completeness: {completeness_percentage:.1f}% ({completeness_score}/{total_fields} fields), "
                f"Images: {images_info}, "
                f"Season: {jersey_data.get('season', 'N/A')}, "
                f"Type: {jersey_data.get('type', 'N/A')}",
                f"Insufficient data for detailed page" if completeness_percentage < 50 else ""
            )
            
            return completeness_percentage >= 50
            
        except Exception as e:
            self.log_test(f"{jersey_name} Data Completeness", False, error=str(e))
            return False

    def test_data_consistency(self):
        """Test 6: Cohérence des données entre endpoints"""
        print("🔗 TEST 6: COHÉRENCE DES DONNÉES")
        print("=" * 50)
        
        try:
            # Récupérer les données de tous les endpoints
            endpoints_data = {}
            
            for endpoint in ['teams', 'brands', 'competitions', 'players', 'master-jerseys']:
                try:
                    response = self.session.get(f"{BACKEND_URL}/{endpoint}")
                    if response.status_code == 200:
                        endpoints_data[endpoint] = response.json()
                    else:
                        endpoints_data[endpoint] = []
                except:
                    endpoints_data[endpoint] = []
            
            # Vérifier la cohérence des références
            consistency_issues = []
            
            # Vérifier que les master jerseys référencent des équipes existantes
            if endpoints_data.get('master-jerseys') and endpoints_data.get('teams'):
                team_ids = {team.get('id') for team in endpoints_data['teams']}
                for jersey in endpoints_data['master-jerseys']:
                    jersey_team_id = jersey.get('team_id')
                    if jersey_team_id and jersey_team_id not in team_ids:
                        consistency_issues.append(f"Master jersey {jersey.get('id')} references non-existent team {jersey_team_id}")
            
            # Vérifier la présence d'images/logos
            image_stats = {}
            for endpoint, data in endpoints_data.items():
                if data:
                    if endpoint == 'teams':
                        with_images = sum(1 for item in data if item.get('logo_url'))
                    elif endpoint == 'brands':
                        with_images = sum(1 for item in data if item.get('logo_url'))
                    elif endpoint == 'competitions':
                        with_images = sum(1 for item in data if item.get('logo_url'))
                    elif endpoint == 'players':
                        with_images = sum(1 for item in data if item.get('photo_url'))
                    elif endpoint == 'master-jerseys':
                        with_images = sum(1 for item in data if item.get('images'))
                    else:
                        with_images = 0
                    
                    image_stats[endpoint] = {
                        'total': len(data),
                        'with_images': with_images,
                        'percentage': (with_images / len(data) * 100) if len(data) > 0 else 0
                    }
            
            self.log_test(
                "Data Consistency Check", 
                len(consistency_issues) == 0, 
                f"Image statistics: {image_stats}, "
                f"Endpoints responding: {len([k for k, v in endpoints_data.items() if v])}/5",
                f"Consistency issues: {consistency_issues}" if consistency_issues else ""
            )
            
            return len(consistency_issues) == 0
            
        except Exception as e:
            self.log_test("Data Consistency Check", False, error=str(e))
            return False

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 TOPKIT DETAILED ROUTES - TESTS BACKEND")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print("Testing endpoints for detailed entity pages...")
        print("=" * 60)
        print()
        
        # Test 1: Teams endpoint
        self.test_teams_endpoint()
        
        # Test 2: Brands endpoint
        self.test_brands_endpoint()
        
        # Test 3: Competitions endpoint
        self.test_competitions_endpoint()
        
        # Test 4: Players endpoint
        self.test_players_endpoint()
        
        # Test 5: Master jerseys endpoint
        self.test_master_jerseys_endpoint()
        
        # Test 6: Data consistency
        self.test_data_consistency()
        
        # Résumé des résultats
        self.print_summary()
        
        return True

    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS - ROUTES DÉTAILLÉES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total des tests: {total_tests}")
        print(f"Tests réussis: {passed_tests}")
        print(f"Tests échoués: {failed_tests}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        print()
        
        # Détail des tests échoués
        failed_results = [result for result in self.test_results if not result["success"]]
        if failed_results:
            print("❌ TESTS ÉCHOUÉS:")
            for result in failed_results:
                print(f"  - {result['test']}: {result['error']}")
            print()
        
        # Détail des tests réussis
        passed_results = [result for result in self.test_results if result["success"]]
        if passed_results:
            print("✅ TESTS RÉUSSIS:")
            for result in passed_results:
                print(f"  - {result['test']}")
            print()
        
        # Conclusion
        if success_rate >= 80:
            print("🎉 CONCLUSION: ENDPOINTS POUR FICHES DÉTAILLÉES OPÉRATIONNELS!")
            print("Les données backend sont suffisantes pour les nouvelles pages détaillées.")
        elif success_rate >= 60:
            print("⚠️  CONCLUSION: ENDPOINTS PARTIELLEMENT FONCTIONNELS")
            print("Quelques problèmes identifiés mais données de base disponibles.")
        else:
            print("🚨 CONCLUSION: PROBLÈMES CRITIQUES IDENTIFIÉS")
            print("Les endpoints nécessitent des corrections pour supporter les fiches détaillées.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = TopKitDetailedRoutesTester()
    tester.run_all_tests()