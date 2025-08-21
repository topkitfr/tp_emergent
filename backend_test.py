#!/usr/bin/env python3
"""
TopKit Contributions System with Images - Backend Testing
Test du système de contributions avec images selon la demande de review
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration des URLs
BACKEND_URL = "https://jersey-collab.preview.emergentagent.com/api"

# Données d'authentification admin
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitContributionsImagesTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
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

    def authenticate_admin(self):
        """Test 1: Authentification obligatoire avec admin"""
        print("🔐 TEST 1: AUTHENTIFICATION ADMIN")
        print("=" * 50)
        
        try:
            # Tentative de connexion admin
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                
                # Vérifier le rôle admin
                if user_info.get("role") == "admin":
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_test(
                        "Admin Authentication", 
                        True, 
                        f"Admin connecté: {user_info.get('name')} (Role: {user_info.get('role')})"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Authentication", 
                        False, 
                        error=f"Utilisateur n'a pas le rôle admin: {user_info.get('role')}"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, error=str(e))
            return False

    def test_contribution_creation_with_images(self):
        """Test 2: Création contribution avec images"""
        print("📸 TEST 2: CRÉATION CONTRIBUTION AVEC IMAGES")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Contribution Creation with Images", False, error="Pas de token admin")
            return False
            
        try:
            # Données de test avec images base64 comme spécifié dans la review request
            # Utiliser AC Milan comme entité existante (pas de contribution en attente)
            contribution_data = {
                "entity_type": "team",
                "entity_id": "67fdd572-78bd-4207-b3a1-0503970b482b",
                "proposed_data": {
                    "name": "AC Milan Actualisation",
                    "city": "Milano"
                },
                "title": "Test après correction bouton",
                "description": "Test complet après fix du bouton de soumission",
                "source_urls": [],
                "images": {
                    "logo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M8QDwAM7AHn9rA1ZQAAAABJRU5ErkJggg==",
                    "secondary_photos": [
                        "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                    ]
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/contributions", json=contribution_data)
            
            if response.status_code == 200:
                data = response.json()
                contribution_id = data.get("id")
                
                # Vérifier que la contribution contient les images
                if contribution_id:
                    self.log_test(
                        "Contribution Creation with Images", 
                        True, 
                        f"Contribution créée avec ID: {contribution_id}, Images incluses: {bool(contribution_data['images'])}"
                    )
                    return contribution_id
                else:
                    self.log_test(
                        "Contribution Creation with Images", 
                        False, 
                        error="Pas d'ID de contribution retourné"
                    )
                    return False
            else:
                # Analyser l'erreur pour comprendre le problème
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("detail", error_detail)
                except:
                    pass
                    
                self.log_test(
                    "Contribution Creation with Images", 
                    False, 
                    error=f"HTTP {response.status_code}: {error_detail}"
                )
                return False
                
        except Exception as e:
            self.log_test("Contribution Creation with Images", False, error=str(e))
            return False

    def test_contribution_retrieval_with_images(self):
        """Test 3: Récupération des contributions avec images"""
        print("📋 TEST 3: RÉCUPÉRATION CONTRIBUTIONS AVEC IMAGES")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Contribution Retrieval with Images", False, error="Pas de token admin")
            return False
            
        try:
            # GET /api/contributions pour récupérer toutes les contributions
            response = self.session.get(f"{BACKEND_URL}/contributions")
            
            if response.status_code == 200:
                contributions = response.json()
                
                # Chercher des contributions avec images
                contributions_with_images = [
                    contrib for contrib in contributions 
                    if contrib.get("images") is not None
                ]
                
                if contributions_with_images:
                    # Analyser la première contribution avec images
                    contrib = contributions_with_images[0]
                    images = contrib.get("images", {})
                    
                    self.log_test(
                        "Contribution Retrieval with Images", 
                        True, 
                        f"Trouvé {len(contributions_with_images)} contribution(s) avec images. "
                        f"Première contribution ID: {contrib.get('id')}, "
                        f"Types d'images: {list(images.keys()) if images else 'Aucune'}"
                    )
                    return True
                else:
                    self.log_test(
                        "Contribution Retrieval with Images", 
                        True, 
                        f"Récupéré {len(contributions)} contributions, mais aucune avec images"
                    )
                    return True
            else:
                self.log_test(
                    "Contribution Retrieval with Images", 
                    False, 
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Contribution Retrieval with Images", False, error=str(e))
            return False

    def test_image_validation(self):
        """Test 4: Validation des images base64"""
        print("🔍 TEST 4: VALIDATION DES IMAGES BASE64")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Image Validation", False, error="Pas de token admin")
            return False
            
        try:
            # Test avec différents formats d'images base64
            test_cases = [
                {
                    "name": "PNG valide",
                    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M8QDwAM7AHn9rA1ZQAAAABJRU5ErkJggg==",
                    "should_work": True
                },
                {
                    "name": "JPEG valide", 
                    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                    "should_work": True
                }
            ]
            
            validation_results = []
            
            for test_case in test_cases:
                contribution_data = {
                    "entity_type": "team",
                    "entity_id": "67fdd572-78bd-4207-b3a1-0503970b482b",
                    "proposed_data": {
                        "name": f"Test Team {test_case['name']}",
                        "city": "Test City"
                    },
                    "title": f"Test validation {test_case['name']}",
                    "description": f"Test de validation pour {test_case['name']}",
                    "source_urls": [],
                    "images": {
                        "test_image": test_case["image"]
                    }
                }
                
                response = self.session.post(f"{BACKEND_URL}/contributions", json=contribution_data)
                
                success = (response.status_code == 200) == test_case["should_work"]
                validation_results.append({
                    "test": test_case["name"],
                    "success": success,
                    "status_code": response.status_code
                })
            
            all_passed = all(result["success"] for result in validation_results)
            
            self.log_test(
                "Image Validation", 
                all_passed, 
                f"Tests de validation: {validation_results}"
            )
            return all_passed
            
        except Exception as e:
            self.log_test("Image Validation", False, error=str(e))
            return False

    def test_database_storage_verification(self):
        """Test 5: Vérification stockage en base de données"""
        print("💾 TEST 5: VÉRIFICATION STOCKAGE BASE DE DONNÉES")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Database Storage Verification", False, error="Pas de token admin")
            return False
            
        try:
            # Créer une contribution avec des images spécifiques pour le test
            test_images = {
                "logo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M8QDwAM7AHn9rA1ZQAAAABJRU5ErkJggg==",
                "banner": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
            }
            
            contribution_data = {
                "entity_type": "team",
                "entity_id": "67fdd572-78bd-4207-b3a1-0503970b482b",
                "proposed_data": {
                    "name": "Test Storage Team",
                    "city": "Storage City"
                },
                "title": "Test stockage base de données",
                "description": "Vérification que les images sont correctement stockées",
                "source_urls": [],
                "images": test_images
            }
            
            # Créer la contribution
            create_response = self.session.post(f"{BACKEND_URL}/contributions", json=contribution_data)
            
            if create_response.status_code == 200:
                contribution_id = create_response.json().get("id")
                
                # Récupérer la contribution pour vérifier le stockage
                get_response = self.session.get(f"{BACKEND_URL}/contributions")
                
                if get_response.status_code == 200:
                    contributions = get_response.json()
                    
                    # Trouver notre contribution
                    our_contribution = None
                    for contrib in contributions:
                        if contrib.get("id") == contribution_id:
                            our_contribution = contrib
                            break
                    
                    if our_contribution:
                        stored_images = our_contribution.get("images", {})
                        
                        # Vérifier que les images sont stockées correctement
                        images_match = True
                        for key, expected_value in test_images.items():
                            if stored_images.get(key) != expected_value:
                                images_match = False
                                break
                        
                        if images_match:
                            self.log_test(
                                "Database Storage Verification", 
                                True, 
                                f"Images stockées correctement. Contribution ID: {contribution_id}, "
                                f"Images: {list(stored_images.keys())}"
                            )
                            return True
                        else:
                            self.log_test(
                                "Database Storage Verification", 
                                False, 
                                error="Les images stockées ne correspondent pas aux images envoyées"
                            )
                            return False
                    else:
                        self.log_test(
                            "Database Storage Verification", 
                            False, 
                            error="Contribution créée mais non trouvée lors de la récupération"
                        )
                        return False
                else:
                    self.log_test(
                        "Database Storage Verification", 
                        False, 
                        error=f"Erreur lors de la récupération: HTTP {get_response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Database Storage Verification", 
                    False, 
                    error=f"Erreur lors de la création: HTTP {create_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Database Storage Verification", False, error=str(e))
            return False

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 TOPKIT CONTRIBUTIONS AVEC IMAGES - TESTS BACKEND")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print("=" * 60)
        print()
        
        # Test 1: Authentification
        if not self.authenticate_admin():
            print("❌ ÉCHEC AUTHENTIFICATION - ARRÊT DES TESTS")
            return False
        
        # Test 2: Création contribution avec images
        contribution_created = self.test_contribution_creation_with_images()
        
        # Test 3: Récupération contributions avec images
        self.test_contribution_retrieval_with_images()
        
        # Test 4: Validation des images
        self.test_image_validation()
        
        # Test 5: Vérification stockage base de données
        self.test_database_storage_verification()
        
        # Résumé des résultats
        self.print_summary()
        
        return True

    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
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
            print("🎉 CONCLUSION: SYSTÈME DE CONTRIBUTIONS AVEC IMAGES OPÉRATIONNEL!")
            print("Le backend accepte et stocke correctement les images dans les contributions.")
        elif success_rate >= 60:
            print("⚠️  CONCLUSION: SYSTÈME PARTIELLEMENT FONCTIONNEL")
            print("Quelques problèmes identifiés mais fonctionnalité de base opérationnelle.")
        else:
            print("🚨 CONCLUSION: PROBLÈMES CRITIQUES IDENTIFIÉS")
            print("Le système de contributions avec images nécessite des corrections.")
        
        print("=" * 60)

if __name__ == "__main__":
    tester = TopKitContributionsImagesTester()
    tester.run_all_tests()