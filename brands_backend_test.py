#!/usr/bin/env python3
"""
TopKit Brands API Testing - Football Equipment Manufacturers Import Verification
Testing all brands endpoints after importing football equipment manufacturers
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"

class BrandsAPITester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        print(result)
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_get_all_brands(self):
        """Test GET /api/brands - Récupérer toutes les marques"""
        try:
            response = requests.get(f"{self.backend_url}/brands", timeout=10)
            
            if response.status_code == 200:
                brands = response.json()
                
                # Vérifier qu'on a au moins 12 marques (Nike, Adidas + 10 nouvelles)
                if len(brands) >= 12:
                    self.log_test("GET /api/brands - Count verification", True, 
                                f"Found {len(brands)} brands (≥12 expected)")
                else:
                    self.log_test("GET /api/brands - Count verification", False, 
                                f"Found {len(brands)} brands (<12 expected)")
                
                # Vérifier les nouvelles marques importées
                expected_brands = [
                    "Nike", "Adidas", "Puma", "New Balance", "Umbro", 
                    "Kappa", "Le Coq Sportif", "Hummel", "Joma", 
                    "Erreà", "Macron", "Under Armour"
                ]
                
                found_brands = [brand['name'] for brand in brands]
                missing_brands = []
                
                for expected in expected_brands:
                    if expected not in found_brands:
                        missing_brands.append(expected)
                
                if not missing_brands:
                    self.log_test("GET /api/brands - Expected brands verification", True, 
                                f"All {len(expected_brands)} expected brands found")
                else:
                    self.log_test("GET /api/brands - Expected brands verification", False, 
                                f"Missing brands: {', '.join(missing_brands)}")
                
                # Vérifier les références TopKit (TK-BRAND-XXXXXX)
                brands_with_refs = [b for b in brands if b.get('topkit_reference', '').startswith('TK-BRAND-')]
                if len(brands_with_refs) == len(brands):
                    self.log_test("GET /api/brands - TopKit references", True, 
                                f"All {len(brands)} brands have TK-BRAND-XXXXXX references")
                else:
                    self.log_test("GET /api/brands - TopKit references", False, 
                                f"Only {len(brands_with_refs)}/{len(brands)} brands have proper references")
                
                # Vérifier les données complètes pour quelques marques
                complete_data_count = 0
                for brand in brands:
                    if (brand.get('official_name') and 
                        brand.get('country') and 
                        brand.get('founded_year') and 
                        brand.get('website')):
                        complete_data_count += 1
                
                if complete_data_count >= 8:  # Au moins 8 marques avec données complètes
                    self.log_test("GET /api/brands - Complete data verification", True, 
                                f"{complete_data_count} brands have complete data")
                else:
                    self.log_test("GET /api/brands - Complete data verification", False, 
                                f"Only {complete_data_count} brands have complete data")
                
                return brands
                
            else:
                self.log_test("GET /api/brands - HTTP Status", False, 
                            f"HTTP {response.status_code}")
                return []
                
        except Exception as e:
            self.log_test("GET /api/brands - Request", False, f"Error: {str(e)}")
            return []
    
    def test_search_brands(self, brands_data):
        """Test GET /api/brands avec recherche par nom"""
        search_tests = [
            ("Puma", "Puma"),
            ("Nike", "Nike"),
            ("Adidas", "Adidas"),
            ("Under Armour", "Under Armour")
        ]
        
        for search_term, expected_brand in search_tests:
            try:
                response = requests.get(f"{self.backend_url}/brands", 
                                      params={'search': search_term}, timeout=10)
                
                if response.status_code == 200:
                    results = response.json()
                    found_brand = None
                    
                    for brand in results:
                        if brand['name'] == expected_brand:
                            found_brand = brand
                            break
                    
                    if found_brand:
                        self.log_test(f"GET /api/brands?search={search_term}", True, 
                                    f"Found {expected_brand}")
                    else:
                        self.log_test(f"GET /api/brands?search={search_term}", False, 
                                    f"{expected_brand} not found in search results")
                else:
                    self.log_test(f"GET /api/brands?search={search_term}", False, 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"GET /api/brands?search={search_term}", False, f"Error: {str(e)}")
    
    def test_filter_by_country(self, brands_data):
        """Test GET /api/brands avec filtre pays"""
        country_tests = [
            ("Germany", "Puma"),
            ("Italy", ["Kappa", "Erreà", "Macron"]),
            ("France", "Le Coq Sportif"),
            ("United States", ["New Balance", "Under Armour"])
        ]
        
        for country, expected_brands in country_tests:
            try:
                response = requests.get(f"{self.backend_url}/brands", 
                                      params={'country': country}, timeout=10)
                
                if response.status_code == 200:
                    results = response.json()
                    found_brands = [brand['name'] for brand in results if brand.get('country') == country]
                    
                    if isinstance(expected_brands, str):
                        expected_brands = [expected_brands]
                    
                    found_expected = [brand for brand in expected_brands if brand in found_brands]
                    
                    if found_expected:
                        self.log_test(f"GET /api/brands?country={country}", True, 
                                    f"Found {len(found_expected)} expected brands: {', '.join(found_expected)}")
                    else:
                        self.log_test(f"GET /api/brands?country={country}", False, 
                                    f"No expected brands found for {country}")
                else:
                    self.log_test(f"GET /api/brands?country={country}", False, 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"GET /api/brands?country={country}", False, f"Error: {str(e)}")
    
    def test_brand_data_integrity(self, brands_data):
        """Vérifier l'intégrité des données importées"""
        # Test des marques spécifiques avec leurs données attendues
        brand_tests = [
            {
                'name': 'Puma',
                'expected_country': 'Germany',
                'expected_founded': 1948,
                'expected_website': 'https://www.puma.com'
            },
            {
                'name': 'New Balance',
                'expected_country': 'United States',
                'expected_founded': 1906,
                'expected_website': 'https://www.newbalance.com'
            },
            {
                'name': 'Le Coq Sportif',
                'expected_country': 'France',
                'expected_founded': 1882,
                'expected_website': 'https://www.lecoqsportif.com'
            },
            {
                'name': 'Hummel',
                'expected_country': 'Denmark',
                'expected_founded': 1923,
                'expected_website': 'https://www.hummel.net'
            }
        ]
        
        for test_brand in brand_tests:
            brand_found = None
            for brand in brands_data:
                if brand['name'] == test_brand['name']:
                    brand_found = brand
                    break
            
            if brand_found:
                # Vérifier les données
                checks = []
                
                if brand_found.get('country') == test_brand['expected_country']:
                    checks.append("country ✓")
                else:
                    checks.append(f"country ✗ (got: {brand_found.get('country')})")
                
                if brand_found.get('founded_year') == test_brand['expected_founded']:
                    checks.append("founded_year ✓")
                else:
                    checks.append(f"founded_year ✗ (got: {brand_found.get('founded_year')})")
                
                if brand_found.get('website') == test_brand['expected_website']:
                    checks.append("website ✓")
                else:
                    checks.append(f"website ✗ (got: {brand_found.get('website')})")
                
                # Vérifier les noms alternatifs
                if brand_found.get('common_names') and len(brand_found['common_names']) > 0:
                    checks.append("common_names ✓")
                else:
                    checks.append("common_names ✗")
                
                all_correct = all("✓" in check for check in checks)
                
                self.log_test(f"Data integrity - {test_brand['name']}", all_correct, 
                            f"{', '.join(checks)}")
            else:
                self.log_test(f"Data integrity - {test_brand['name']}", False, "Brand not found")
    
    def test_master_jerseys_integration(self):
        """Vérifier que les marques peuvent être utilisées dans les Master Jerseys"""
        try:
            # Tester l'endpoint des Master Jerseys pour voir s'il utilise les marques
            response = requests.get(f"{self.backend_url}/master-jerseys", timeout=10)
            
            if response.status_code == 200:
                master_jerseys = response.json()
                
                # Vérifier s'il y a des Master Jerseys qui utilisent les nouvelles marques
                brands_in_use = set()
                for jersey in master_jerseys:
                    if 'brand_info' in jersey and jersey['brand_info']:
                        brands_in_use.add(jersey['brand_info'].get('name', ''))
                
                if brands_in_use:
                    self.log_test("Master Jerseys integration", True, 
                                f"Brands in use: {', '.join(brands_in_use)}")
                else:
                    self.log_test("Master Jerseys integration", True, 
                                "Master Jerseys endpoint accessible (no brands in use yet)")
            else:
                self.log_test("Master Jerseys integration", False, 
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Master Jerseys integration", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🎯 TOPKIT BRANDS API TESTING - FOOTBALL EQUIPMENT MANUFACTURERS IMPORT VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test 1: GET /api/brands - Récupérer toutes les marques
        print("📋 TEST 1: GET /api/brands - Récupérer toutes les marques")
        brands_data = self.test_get_all_brands()
        print()
        
        # Test 2: Recherche par nom
        print("🔍 TEST 2: GET /api/brands avec recherche par nom")
        self.test_search_brands(brands_data)
        print()
        
        # Test 3: Filtre par pays
        print("🌍 TEST 3: GET /api/brands avec filtre pays")
        self.test_filter_by_country(brands_data)
        print()
        
        # Test 4: Vérification des données
        print("📊 TEST 4: Vérification de l'intégrité des données")
        self.test_brand_data_integrity(brands_data)
        print()
        
        # Test 5: Intégration Master Jerseys
        print("🔗 TEST 5: Test de l'intégration avec Master Jerseys")
        self.test_master_jerseys_integration()
        print()
        
        # Résumé
        print("=" * 80)
        print("📊 RÉSUMÉ DES TESTS")
        print(f"Total tests: {self.total_tests}")
        print(f"Tests réussis: {self.passed_tests}")
        print(f"Tests échoués: {self.total_tests - self.passed_tests}")
        print(f"Taux de réussite: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("🎉 TOUS LES TESTS SONT PASSÉS!")
        else:
            print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        
        return self.passed_tests / self.total_tests

if __name__ == "__main__":
    tester = BrandsAPITester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate == 1.0 else 1)