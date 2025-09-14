#!/usr/bin/env python3
"""
TopKit Admin PSG Jersey Workflow Backend Test
============================================

OBJECTIF: Tester le workflow admin complet avec le maillot PSG réel soumis par l'utilisateur.

MAILLOT À TRAITER:
- ID: c578d59f-43ab-4b27-bda5-fc337f7c1250
- Équipe: Paris Saint-Germain  
- Référence: TK-000051
- Photos: Vraies photos uploadées par l'utilisateur

WORKFLOW ADMIN À TESTER:
1. **CONNEXION ADMIN**: Se connecter avec topkitfr@gmail.com/TopKitSecure789#
2. **VISUALISATION PENDING**: Récupérer la liste des maillots en attente et vérifier que le PSG y figure
3. **CORRECTION (optionnel)**: Tester la possibilité de voir les images et les modifier si nécessaire
4. **APPROBATION**: Approuver le maillot avec les vraies photos
5. **VÉRIFICATION EXPLORATEUR**: Confirmer que le maillot approuvé apparaît dans /api/jerseys/approved avec les photos

FOCUS: Valider que les vraies photos uploadées sont visibles par l'admin et persistent après approbation.
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-collab-1.preview.emergentagent.com') + '/api'
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

# Jersey spécifique à tester
PSG_JERSEY_ID = "c578d59f-43ab-4b27-bda5-fc337f7c1250"
PSG_JERSEY_REF = "TK-000051"

class AdminPSGWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.psg_jersey_data = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def admin_login(self):
        """Test admin authentication"""
        print(f"\n🔐 ÉTAPE 1: CONNEXION ADMIN")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_info = data.get('user', {})
                
                self.log_test("Admin Authentication", True, 
                    f"Admin connecté: {user_info.get('name')} (Role: {user_info.get('role')})")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                return True
            else:
                self.log_test("Admin Authentication", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_pending_jerseys(self):
        """Test récupération des maillots en attente"""
        print(f"\n📋 ÉTAPE 2: VISUALISATION MAILLOTS EN ATTENTE")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/jerseys/pending")
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                total_pending = len(pending_jerseys)
                
                self.log_test("Get Pending Jerseys", True, 
                    f"Trouvé {total_pending} maillots en attente")
                
                # Chercher le maillot PSG spécifique
                psg_jersey = None
                for jersey in pending_jerseys:
                    if (jersey.get('id') == PSG_JERSEY_ID or 
                        jersey.get('reference_number') == PSG_JERSEY_REF or
                        'Paris Saint-Germain' in jersey.get('team', '')):
                        psg_jersey = jersey
                        break
                
                if psg_jersey:
                    self.psg_jersey_data = psg_jersey
                    self.log_test("PSG Jersey Found in Pending", True, 
                        f"Maillot PSG trouvé - ID: {psg_jersey.get('id')}, Équipe: {psg_jersey.get('team')}, Ref: {psg_jersey.get('reference_number')}")
                    
                    # Vérifier les photos
                    front_photo = psg_jersey.get('front_photo_url')
                    back_photo = psg_jersey.get('back_photo_url')
                    images_array = psg_jersey.get('images_array', [])
                    
                    photo_details = []
                    if front_photo:
                        photo_details.append(f"Front: {front_photo}")
                    if back_photo:
                        photo_details.append(f"Back: {back_photo}")
                    if images_array:
                        photo_details.append(f"Images array: {images_array}")
                    
                    if photo_details:
                        self.log_test("PSG Jersey Photos Present", True, 
                            f"Photos détectées - {'; '.join(photo_details)}")
                    else:
                        self.log_test("PSG Jersey Photos Present", False, 
                            "Aucune photo détectée sur le maillot PSG")
                    
                    return True
                else:
                    self.log_test("PSG Jersey Found in Pending", False, 
                        f"Maillot PSG (ID: {PSG_JERSEY_ID} ou Ref: {PSG_JERSEY_REF}) non trouvé dans les {total_pending} maillots en attente")
                    
                    # Afficher les maillots disponibles pour debug
                    print("\n📝 Maillots en attente disponibles:")
                    for i, jersey in enumerate(pending_jerseys[:5], 1):  # Afficher les 5 premiers
                        print(f"   {i}. {jersey.get('team', 'N/A')} - {jersey.get('reference_number', 'N/A')} (ID: {jersey.get('id', 'N/A')})")
                    
                    return False
                    
            else:
                self.log_test("Get Pending Jerseys", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Pending Jerseys", False, f"Exception: {str(e)}")
            return False
    
    def test_jersey_correction_access(self):
        """Test accès aux fonctionnalités de correction (optionnel)"""
        print(f"\n🔍 ÉTAPE 3: TEST ACCÈS CORRECTION MAILLOT (OPTIONNEL)")
        print("=" * 50)
        
        if not self.psg_jersey_data:
            self.log_test("Jersey Correction Access", False, "Pas de données PSG disponibles")
            return False
        
        jersey_id = self.psg_jersey_data.get('id')
        
        try:
            # Test accès aux détails du maillot pour correction
            response = self.session.get(f"{BACKEND_URL}/admin/jerseys/{jersey_id}")
            
            if response.status_code == 200:
                jersey_details = response.json()
                self.log_test("Jersey Details Access", True, 
                    f"Accès aux détails du maillot PSG réussi")
                
                # Vérifier que les photos sont accessibles
                front_photo = jersey_details.get('front_photo_url')
                back_photo = jersey_details.get('back_photo_url')
                
                if front_photo or back_photo:
                    self.log_test("Jersey Photos Accessible", True, 
                        f"Photos accessibles pour correction - Front: {bool(front_photo)}, Back: {bool(back_photo)}")
                else:
                    self.log_test("Jersey Photos Accessible", False, 
                        "Aucune photo accessible pour correction")
                
                return True
            else:
                self.log_test("Jersey Details Access", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Correction Access", False, f"Exception: {str(e)}")
            return False
    
    def approve_psg_jersey(self):
        """Test approbation du maillot PSG"""
        print(f"\n✅ ÉTAPE 4: APPROBATION MAILLOT PSG")
        print("=" * 50)
        
        if not self.psg_jersey_data:
            self.log_test("PSG Jersey Approval", False, "Pas de données PSG disponibles")
            return False
        
        jersey_id = self.psg_jersey_data.get('id')
        
        try:
            # Approuver le maillot
            response = self.session.post(f"{BACKEND_URL}/admin/jerseys/{jersey_id}/approve")
            
            if response.status_code == 200:
                approval_data = response.json()
                self.log_test("PSG Jersey Approval", True, 
                    f"Maillot PSG approuvé avec succès - {approval_data.get('message', 'Pas de message')}")
                return True
            else:
                self.log_test("PSG Jersey Approval", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PSG Jersey Approval", False, f"Exception: {str(e)}")
            return False
    
    def verify_approved_jersey_in_explorer(self):
        """Test vérification que le maillot approuvé apparaît dans l'explorateur"""
        print(f"\n🔍 ÉTAPE 5: VÉRIFICATION EXPLORATEUR")
        print("=" * 50)
        
        try:
            # Vérifier dans les maillots approuvés
            response = self.session.get(f"{BACKEND_URL}/jerseys/approved")
            
            if response.status_code == 200:
                approved_jerseys = response.json()
                total_approved = len(approved_jerseys)
                
                self.log_test("Get Approved Jerseys", True, 
                    f"Trouvé {total_approved} maillots approuvés")
                
                # Chercher le maillot PSG dans les approuvés
                psg_approved = None
                for jersey in approved_jerseys:
                    if (jersey.get('id') == PSG_JERSEY_ID or 
                        jersey.get('reference_number') == PSG_JERSEY_REF or
                        'Paris Saint-Germain' in jersey.get('team', '')):
                        psg_approved = jersey
                        break
                
                if psg_approved:
                    self.log_test("PSG Jersey in Approved List", True, 
                        f"Maillot PSG trouvé dans les approuvés - Status: {psg_approved.get('status')}")
                    
                    # Vérifier que les photos sont toujours présentes
                    front_photo = psg_approved.get('front_photo_url')
                    back_photo = psg_approved.get('back_photo_url')
                    images_array = psg_approved.get('images_array', [])
                    
                    photo_details = []
                    if front_photo:
                        photo_details.append(f"Front: {front_photo}")
                    if back_photo:
                        photo_details.append(f"Back: {back_photo}")
                    if images_array:
                        photo_details.append(f"Images array: {images_array}")
                    
                    if photo_details:
                        self.log_test("PSG Jersey Photos Preserved", True, 
                            f"Photos préservées après approbation - {'; '.join(photo_details)}")
                    else:
                        self.log_test("PSG Jersey Photos Preserved", False, 
                            "Photos perdues après approbation")
                    
                    return True
                else:
                    self.log_test("PSG Jersey in Approved List", False, 
                        f"Maillot PSG non trouvé dans les {total_approved} maillots approuvés")
                    return False
                    
            else:
                self.log_test("Get Approved Jerseys", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Approved Jersey", False, f"Exception: {str(e)}")
            return False
    
    def test_general_explorer_access(self):
        """Test accès général à l'explorateur (sans auth)"""
        print(f"\n🌐 ÉTAPE 6: TEST ACCÈS EXPLORATEUR PUBLIC")
        print("=" * 50)
        
        try:
            # Tester l'accès public aux maillots
            temp_session = requests.Session()  # Session sans auth
            response = temp_session.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                public_jerseys = response.json()
                total_public = len(public_jerseys)
                
                self.log_test("Public Explorer Access", True, 
                    f"Accès public réussi - {total_public} maillots visibles")
                
                # Chercher le PSG dans l'accès public
                psg_public = None
                for jersey in public_jerseys:
                    if (jersey.get('id') == PSG_JERSEY_ID or 
                        jersey.get('reference_number') == PSG_JERSEY_REF or
                        'Paris Saint-Germain' in jersey.get('team', '')):
                        psg_public = jersey
                        break
                
                if psg_public:
                    self.log_test("PSG Jersey Public Visibility", True, 
                        f"Maillot PSG visible publiquement")
                else:
                    self.log_test("PSG Jersey Public Visibility", False, 
                        f"Maillot PSG non visible publiquement")
                
                return True
            else:
                self.log_test("Public Explorer Access", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Public Explorer Access", False, f"Exception: {str(e)}")
            return False
    
    def run_complete_workflow(self):
        """Exécuter le workflow complet"""
        print("🎯 TOPKIT ADMIN PSG JERSEY WORKFLOW TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Jersey ID: {PSG_JERSEY_ID}")
        print(f"Target Jersey Ref: {PSG_JERSEY_REF}")
        print("=" * 60)
        
        # Étape 1: Connexion admin
        if not self.admin_login():
            print("\n❌ ÉCHEC: Impossible de se connecter en tant qu'admin")
            return False
        
        # Étape 2: Récupération des maillots en attente
        if not self.get_pending_jerseys():
            print("\n❌ ÉCHEC: Maillot PSG non trouvé dans les maillots en attente")
            return False
        
        # Étape 3: Test accès correction (optionnel)
        self.test_jersey_correction_access()
        
        # Étape 4: Approbation du maillot
        if not self.approve_psg_jersey():
            print("\n❌ ÉCHEC: Impossible d'approuver le maillot PSG")
            return False
        
        # Étape 5: Vérification dans l'explorateur
        if not self.verify_approved_jersey_in_explorer():
            print("\n❌ ÉCHEC: Maillot PSG non visible après approbation")
            return False
        
        # Étape 6: Test accès public
        self.test_general_explorer_access()
        
        return True
    
    def print_summary(self):
        """Afficher le résumé des tests"""
        print(f"\n📊 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total des tests: {total_tests}")
        print(f"Tests réussis: {passed_tests}")
        print(f"Tests échoués: {failed_tests}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ TESTS ÉCHOUÉS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 CONCLUSION:")
        if success_rate >= 80:
            print("✅ WORKFLOW ADMIN PSG OPÉRATIONNEL - Les photos sont correctement gérées!")
        elif success_rate >= 60:
            print("⚠️  WORKFLOW ADMIN PSG PARTIELLEMENT FONCTIONNEL - Quelques problèmes détectés")
        else:
            print("❌ WORKFLOW ADMIN PSG NON FONCTIONNEL - Problèmes critiques détectés")

def main():
    """Fonction principale"""
    tester = AdminPSGWorkflowTester()
    
    try:
        success = tester.run_complete_workflow()
        tester.print_summary()
        
        if success:
            print(f"\n🎉 SUCCÈS: Le workflow admin PSG est opérationnel!")
            return 0
        else:
            print(f"\n💥 ÉCHEC: Le workflow admin PSG a des problèmes")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n💥 ERREUR CRITIQUE: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())