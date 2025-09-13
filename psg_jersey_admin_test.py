#!/usr/bin/env python3
"""
TopKit PSG Jersey Admin Workflow Test - FOCUSED TEST
===================================================

OBJECTIF: Tester le workflow admin complet avec le maillot PSG réel spécifique.

MAILLOT CIBLE CONFIRMÉ:
- ID: c578d59f-43ab-4b27-bda5-fc337f7c1250
- Équipe: Paris Saint-Germain
- Référence: TK-000051
- Front Photo: uploads/jerseys/c578d59f-43ab-4b27-bda5-fc337f7c1250/front_psg_front_real.jpg
- Back Photo: uploads/jerseys/c578d59f-43ab-4b27-bda5-fc337f7c1250/back_psg_back_real.jpg

WORKFLOW ADMIN À TESTER:
1. ✅ CONNEXION ADMIN: topkitfr@gmail.com/TopKitSecure789#
2. ✅ VISUALISATION PENDING: Vérifier que le PSG TK-000051 est en attente
3. ✅ PHOTOS VISIBLES: Confirmer que les vraies photos sont visibles
4. ✅ APPROBATION: Approuver le maillot avec les photos
5. ✅ VÉRIFICATION EXPLORATEUR: Confirmer présence dans /api/jerseys/approved
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://topkit-workflow-fix.preview.emergentagent.com') + '/api'
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

# Jersey spécifique confirmé
PSG_JERSEY_ID = "c578d59f-43ab-4b27-bda5-fc337f7c1250"
PSG_JERSEY_REF = "TK-000051"

class PSGJerseyAdminTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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
            print(f"   📝 {details}")
    
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
                    f"Admin connecté: {user_info.get('name')} (Role: {user_info.get('role')}, ID: {user_info.get('id')})")
                
                # Set authorization header
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
    
    def find_psg_jersey_in_pending(self):
        """Trouver le maillot PSG spécifique dans les maillots en attente"""
        print(f"\n📋 ÉTAPE 2: RECHERCHE MAILLOT PSG DANS PENDING")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/jerseys/pending")
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                total_pending = len(pending_jerseys)
                
                self.log_test("Get Pending Jerseys", True, 
                    f"Récupéré {total_pending} maillots en attente")
                
                # Chercher le maillot PSG spécifique
                psg_jersey = None
                for jersey in pending_jerseys:
                    if jersey.get('id') == PSG_JERSEY_ID:
                        psg_jersey = jersey
                        break
                
                if psg_jersey:
                    self.log_test("PSG Jersey Found", True, 
                        f"Maillot PSG trouvé - ID: {psg_jersey.get('id')}, Équipe: {psg_jersey.get('team')}, Ref: {psg_jersey.get('reference_number')}")
                    
                    # Vérifier les photos en détail
                    front_photo = psg_jersey.get('front_photo_url')
                    back_photo = psg_jersey.get('back_photo_url')
                    
                    if front_photo and back_photo:
                        self.log_test("PSG Jersey Photos Present", True, 
                            f"Photos confirmées - Front: {front_photo}, Back: {back_photo}")
                        
                        # Tester l'accessibilité des photos
                        self.test_photo_accessibility(front_photo, back_photo)
                    else:
                        self.log_test("PSG Jersey Photos Present", False, 
                            f"Photos manquantes - Front: {front_photo}, Back: {back_photo}")
                    
                    return psg_jersey
                else:
                    self.log_test("PSG Jersey Found", False, 
                        f"Maillot PSG (ID: {PSG_JERSEY_ID}) non trouvé dans les {total_pending} maillots en attente")
                    return None
                    
            else:
                self.log_test("Get Pending Jerseys", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Find PSG Jersey", False, f"Exception: {str(e)}")
            return None
    
    def test_photo_accessibility(self, front_photo, back_photo):
        """Tester l'accessibilité des photos"""
        print(f"\n📸 ÉTAPE 3: TEST ACCESSIBILITÉ PHOTOS")
        print("=" * 50)
        
        # Test front photo
        if front_photo:
            try:
                # Construire l'URL complète
                if front_photo.startswith('uploads/'):
                    photo_url = f"{BACKEND_URL.replace('/api', '')}/{front_photo}"
                else:
                    photo_url = front_photo
                
                response = requests.get(photo_url)
                if response.status_code == 200:
                    self.log_test("Front Photo Accessible", True, 
                        f"Photo avant accessible - URL: {photo_url}, Taille: {len(response.content)} bytes")
                else:
                    self.log_test("Front Photo Accessible", False, 
                        f"Photo avant inaccessible - HTTP {response.status_code}")
            except Exception as e:
                self.log_test("Front Photo Accessible", False, f"Exception: {str(e)}")
        
        # Test back photo
        if back_photo:
            try:
                # Construire l'URL complète
                if back_photo.startswith('uploads/'):
                    photo_url = f"{BACKEND_URL.replace('/api', '')}/{back_photo}"
                else:
                    photo_url = back_photo
                
                response = requests.get(photo_url)
                if response.status_code == 200:
                    self.log_test("Back Photo Accessible", True, 
                        f"Photo arrière accessible - URL: {photo_url}, Taille: {len(response.content)} bytes")
                else:
                    self.log_test("Back Photo Accessible", False, 
                        f"Photo arrière inaccessible - HTTP {response.status_code}")
            except Exception as e:
                self.log_test("Back Photo Accessible", False, f"Exception: {str(e)}")
    
    def approve_psg_jersey(self):
        """Approuver le maillot PSG"""
        print(f"\n✅ ÉTAPE 4: APPROBATION MAILLOT PSG")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{BACKEND_URL}/admin/jerseys/{PSG_JERSEY_ID}/approve")
            
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
    
    def verify_in_approved_list(self):
        """Vérifier que le maillot apparaît dans la liste des approuvés"""
        print(f"\n🔍 ÉTAPE 5: VÉRIFICATION DANS LISTE APPROUVÉS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/jerseys/approved")
            
            if response.status_code == 200:
                approved_jerseys = response.json()
                total_approved = len(approved_jerseys)
                
                self.log_test("Get Approved Jerseys", True, 
                    f"Récupéré {total_approved} maillots approuvés")
                
                # Chercher le maillot PSG
                psg_approved = None
                for jersey in approved_jerseys:
                    if jersey.get('id') == PSG_JERSEY_ID:
                        psg_approved = jersey
                        break
                
                if psg_approved:
                    self.log_test("PSG Jersey in Approved List", True, 
                        f"Maillot PSG trouvé dans les approuvés - Status: {psg_approved.get('status')}")
                    
                    # Vérifier que les photos sont préservées
                    front_photo = psg_approved.get('front_photo_url')
                    back_photo = psg_approved.get('back_photo_url')
                    
                    if front_photo and back_photo:
                        self.log_test("PSG Jersey Photos Preserved", True, 
                            f"Photos préservées - Front: {front_photo}, Back: {back_photo}")
                        
                        # Tester l'accessibilité des photos après approbation
                        self.test_photo_accessibility(front_photo, back_photo)
                    else:
                        self.log_test("PSG Jersey Photos Preserved", False, 
                            f"Photos perdues - Front: {front_photo}, Back: {back_photo}")
                    
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
    
    def test_public_visibility(self):
        """Tester la visibilité publique du maillot"""
        print(f"\n🌐 ÉTAPE 6: TEST VISIBILITÉ PUBLIQUE")
        print("=" * 50)
        
        try:
            # Test sans authentification
            temp_session = requests.Session()
            response = temp_session.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                public_jerseys = response.json()
                total_public = len(public_jerseys)
                
                self.log_test("Public Jerseys Access", True, 
                    f"Accès public réussi - {total_public} maillots visibles")
                
                # Chercher le PSG
                psg_public = None
                for jersey in public_jerseys:
                    if jersey.get('id') == PSG_JERSEY_ID:
                        psg_public = jersey
                        break
                
                if psg_public:
                    self.log_test("PSG Jersey Public Visibility", True, 
                        f"Maillot PSG visible publiquement avec photos")
                    return True
                else:
                    self.log_test("PSG Jersey Public Visibility", False, 
                        f"Maillot PSG non visible publiquement")
                    return False
                    
            else:
                self.log_test("Public Jerseys Access", False, 
                    f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Public Visibility Test", False, f"Exception: {str(e)}")
            return False
    
    def run_complete_test(self):
        """Exécuter le test complet"""
        print("🎯 TOPKIT PSG JERSEY ADMIN WORKFLOW - TEST COMPLET")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Target Jersey ID: {PSG_JERSEY_ID}")
        print(f"Target Jersey Ref: {PSG_JERSEY_REF}")
        print("=" * 70)
        
        # Étape 1: Connexion admin
        if not self.admin_login():
            return False
        
        # Étape 2: Trouver le maillot PSG
        psg_jersey = self.find_psg_jersey_in_pending()
        if not psg_jersey:
            return False
        
        # Étape 4: Approuver le maillot
        if not self.approve_psg_jersey():
            return False
        
        # Étape 5: Vérifier dans la liste des approuvés
        if not self.verify_in_approved_list():
            return False
        
        # Étape 6: Tester la visibilité publique
        self.test_public_visibility()
        
        return True
    
    def print_summary(self):
        """Afficher le résumé"""
        print(f"\n📊 RÉSUMÉ DU TEST PSG JERSEY ADMIN WORKFLOW")
        print("=" * 60)
        
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
        if success_rate >= 90:
            print("✅ WORKFLOW ADMIN PSG PARFAITEMENT OPÉRATIONNEL!")
            print("   Les vraies photos sont correctement gérées et visibles.")
        elif success_rate >= 75:
            print("⚠️  WORKFLOW ADMIN PSG MAJORITAIREMENT FONCTIONNEL")
            print("   Quelques problèmes mineurs détectés.")
        else:
            print("❌ WORKFLOW ADMIN PSG NON FONCTIONNEL")
            print("   Problèmes critiques détectés.")

def main():
    """Fonction principale"""
    tester = PSGJerseyAdminTester()
    
    try:
        success = tester.run_complete_test()
        tester.print_summary()
        
        return 0 if success else 1
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n💥 ERREUR CRITIQUE: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())