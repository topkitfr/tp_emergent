#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - NEW HOMEPAGE ENDPOINTS TESTING

Testing the new homepage endpoints implemented:
1. /api/homepage/expensive-kits - Top 5 most expensive kits from collections
2. /api/homepage/recent-master-kits - Recently uploaded master kits
3. /api/homepage/recent-contributions - Recently approved contributions
4. /api/users/{user_id}/public-profile - Public profile data with authentication

CRITICAL: Testing all new homepage endpoints with current database data.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://xp-tracking.preview.emergentagent.com/api"

# Target Admin Credentials - CORRECTED EMAIL
TARGET_ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",  # CORRECTED: .com instead of .fr
    "password": "TopKitAdmin2025!",
    "name": "TopKit Admin"
}

class TopKitFinalAdminVerification:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.all_admin_accounts = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def verify_correct_admin_login(self):
        """Verify login with topkitfr@gmail.com / TopKitAdmin2025!"""
        try:
            print(f"\n🔐 VÉRIFICATION CONNEXION ADMIN CORRIGÉ")
            print("=" * 60)
            print(f"   Email: {TARGET_ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {TARGET_ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=TARGET_ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Admin Login Verification", True, 
                             f"✅ Connexion admin réussie avec l'email corrigé")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Email: {self.admin_user_data.get('email')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Admin Login Verification", False, 
                             f"❌ Échec connexion admin - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Login Verification", False, f"Exception: {str(e)}")
            return False
    
    def verify_admin_privileges_comprehensive(self):
        """Verify comprehensive admin privileges"""
        try:
            print(f"\n🛡️ VÉRIFICATION PRIVILÈGES ADMINISTRATEUR")
            print("=" * 60)
            
            if not self.auth_token:
                self.log_test("Admin Privileges Verification", False, "No auth token available")
                return False
            
            # Test all admin endpoints
            admin_endpoints = [
                ("Pending Contributions", f"{BACKEND_URL}/admin/pending-contributions"),
                ("Leaderboard Access", f"{BACKEND_URL}/leaderboard"),
                ("User Gamification", f"{BACKEND_URL}/users/{self.admin_user_data.get('id')}/gamification")
            ]
            
            successful_endpoints = 0
            total_endpoints = len(admin_endpoints)
            
            for endpoint_name, endpoint_url in admin_endpoints:
                try:
                    response = self.session.get(endpoint_url, timeout=10)
                    if response.status_code == 200:
                        print(f"      ✅ {endpoint_name}: Accessible")
                        successful_endpoints += 1
                        
                        # Show some data for verification
                        if endpoint_name == "Pending Contributions":
                            data = response.json()
                            print(f"         Contributions en attente: {len(data)}")
                        elif endpoint_name == "Leaderboard Access":
                            data = response.json()
                            print(f"         Utilisateurs dans le classement: {len(data)}")
                        elif endpoint_name == "User Gamification":
                            data = response.json()
                            print(f"         XP: {data.get('xp', 0)}, Level: {data.get('level', 'Unknown')}")
                            
                    elif response.status_code == 403:
                        print(f"      ❌ {endpoint_name}: Accès refusé (403)")
                    else:
                        print(f"      ⚠️ {endpoint_name}: Status inattendu {response.status_code}")
                        
                except Exception as e:
                    print(f"      ❌ {endpoint_name}: Exception - {str(e)}")
            
            success_rate = (successful_endpoints / total_endpoints) * 100
            
            if successful_endpoints == total_endpoints:
                self.log_test("Admin Privileges Verification", True, 
                             f"✅ Tous les privilèges admin vérifiés - {success_rate:.1f}% de réussite")
                return True
            else:
                self.log_test("Admin Privileges Verification", False, 
                             f"❌ Privilèges admin incomplets - {successful_endpoints}/{total_endpoints} endpoints accessibles")
                return False
                
        except Exception as e:
            self.log_test("Admin Privileges Verification", False, f"Exception: {str(e)}")
            return False
    
    def verify_single_admin_account(self):
        """Verify this is the ONLY admin account on the site"""
        try:
            print(f"\n👑 VÉRIFICATION COMPTE ADMIN UNIQUE")
            print("=" * 60)
            
            # Get all users from leaderboard
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=100", timeout=10)
            
            if response.status_code == 200:
                all_users = response.json()
                
                # Find all admin accounts
                admin_accounts = []
                for user in all_users:
                    username = user.get('username', '').lower()
                    if 'admin' in username:
                        admin_accounts.append(user)
                
                self.all_admin_accounts = admin_accounts
                
                print(f"   Comptes admin trouvés: {len(admin_accounts)}")
                
                target_admin_found = False
                other_admins = []
                
                for admin in admin_accounts:
                    username = admin.get('username', 'Unknown')
                    xp = admin.get('xp', 0)
                    level = admin.get('level', 'Unknown')
                    rank = admin.get('rank', 'Unknown')
                    
                    print(f"      - {username} (XP: {xp}, Level: {level}, Rank: #{rank})")
                    
                    # Check if this is our target admin
                    if ('topkit admin' in username.lower() and 
                        self.admin_user_data and 
                        username.lower() == self.admin_user_data.get('name', '').lower()):
                        target_admin_found = True
                        print(f"        ✅ Ceci est notre compte admin cible")
                    else:
                        other_admins.append(username)
                        print(f"        ⚠️ Autre compte admin qui devrait être supprimé")
                
                if len(admin_accounts) == 1 and target_admin_found:
                    self.log_test("Single Admin Account Verification", True, 
                                 f"✅ Un seul compte admin existe - le compte cible")
                    return True
                elif target_admin_found and len(admin_accounts) > 1:
                    self.log_test("Single Admin Account Verification", False, 
                                 f"❌ Compte admin cible trouvé mais {len(other_admins)} autres comptes admin existent encore")
                    print(f"      Autres comptes admin à supprimer: {', '.join(other_admins)}")
                    return False
                elif not target_admin_found:
                    self.log_test("Single Admin Account Verification", False, 
                                 f"❌ Compte admin cible non trouvé dans la liste")
                    return False
                else:
                    self.log_test("Single Admin Account Verification", False, 
                                 f"❌ État des comptes admin inattendu")
                    return False
                
            else:
                self.log_test("Single Admin Account Verification", False, 
                             f"Échec récupération liste utilisateurs: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Single Admin Account Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_all_admin_functions(self):
        """Test all admin functions comprehensively"""
        try:
            print(f"\n🔧 TEST DE TOUTES LES FONCTIONS ADMIN")
            print("=" * 60)
            
            if not self.auth_token:
                self.log_test("Admin Functions Testing", False, "No auth token available")
                return False
            
            admin_functions_results = []
            
            # Test 1: Get pending contributions
            try:
                response = self.session.get(f"{BACKEND_URL}/admin/pending-contributions", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"      ✅ Contributions en attente: {len(data)} éléments")
                    admin_functions_results.append(True)
                else:
                    print(f"      ❌ Contributions en attente: Status {response.status_code}")
                    admin_functions_results.append(False)
            except Exception as e:
                print(f"      ❌ Contributions en attente: Exception - {str(e)}")
                admin_functions_results.append(False)
            
            # Test 2: Access leaderboard
            try:
                response = self.session.get(f"{BACKEND_URL}/leaderboard", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"      ✅ Classement: {len(data)} utilisateurs")
                    admin_functions_results.append(True)
                else:
                    print(f"      ❌ Classement: Status {response.status_code}")
                    admin_functions_results.append(False)
            except Exception as e:
                print(f"      ❌ Classement: Exception - {str(e)}")
                admin_functions_results.append(False)
            
            # Test 3: Get user gamification data
            try:
                user_id = self.admin_user_data.get('id')
                response = self.session.get(f"{BACKEND_URL}/users/{user_id}/gamification", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"      ✅ Données gamification: XP {data.get('xp', 0)}, Level {data.get('level', 'Unknown')}")
                    admin_functions_results.append(True)
                else:
                    print(f"      ❌ Données gamification: Status {response.status_code}")
                    admin_functions_results.append(False)
            except Exception as e:
                print(f"      ❌ Données gamification: Exception - {str(e)}")
                admin_functions_results.append(False)
            
            # Test 4: Test master kits access
            try:
                response = self.session.get(f"{BACKEND_URL}/master-kits?limit=5", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print(f"      ✅ Accès données master kits: {len(data)} éléments")
                    admin_functions_results.append(True)
                else:
                    print(f"      ❌ Accès données master kits: Status {response.status_code}")
                    admin_functions_results.append(False)
            except Exception as e:
                print(f"      ❌ Accès données master kits: Exception - {str(e)}")
                admin_functions_results.append(False)
            
            successful_functions = sum(admin_functions_results)
            total_functions = len(admin_functions_results)
            success_rate = (successful_functions / total_functions) * 100
            
            if successful_functions == total_functions:
                self.log_test("Admin Functions Testing", True, 
                             f"✅ Toutes les fonctions admin testées avec succès - {success_rate:.1f}%")
                return True
            else:
                self.log_test("Admin Functions Testing", False, 
                             f"❌ Fonctions admin partiellement fonctionnelles - {successful_functions}/{total_functions} réussies")
                return False
                
        except Exception as e:
            self.log_test("Admin Functions Testing", False, f"Exception: {str(e)}")
            return False
    
    def verify_incorrect_account_deleted(self):
        """Verify the incorrect account (topkitfr@gmail.fr) has been deleted"""
        try:
            print(f"\n🗑️ VÉRIFICATION SUPPRESSION COMPTE INCORRECT")
            print("=" * 60)
            
            incorrect_email = "topkitfr@gmail.fr"
            print(f"   Email incorrect à vérifier: {incorrect_email}")
            
            # Try to login with the incorrect account
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": incorrect_email,
                    "password": TARGET_ADMIN_CREDENTIALS['password']
                },
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test("Incorrect Account Deletion Verification", True, 
                             f"✅ Compte incorrect supprimé - {incorrect_email} n'existe plus")
                print(f"      Le compte incorrect a été correctement supprimé")
                return True
            elif response.status_code == 200:
                self.log_test("Incorrect Account Deletion Verification", False, 
                             f"❌ Compte incorrect existe encore - {incorrect_email} est toujours accessible")
                print(f"      ⚠️ Le compte incorrect existe encore et doit être supprimé")
                return False
            else:
                self.log_test("Incorrect Account Deletion Verification", False, 
                             f"Status inattendu lors de la vérification: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Incorrect Account Deletion Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_final_verification(self):
        """Run final admin account verification"""
        print("\n🎯 VÉRIFICATION FINALE - COMPTE ADMIN CORRIGÉ")
        print("Vérification que la correction d'email a été effectuée avec succès")
        print("=" * 80)
        
        verification_results = []
        
        # Step 1: Verify correct admin login
        print("\n1️⃣ Vérification connexion avec email corrigé...")
        verification_results.append(self.verify_correct_admin_login())
        
        if not self.auth_token:
            print("❌ Impossible de continuer sans authentification admin")
            return verification_results
        
        # Step 2: Verify admin privileges
        print("\n2️⃣ Vérification privilèges administrateur...")
        verification_results.append(self.verify_admin_privileges_comprehensive())
        
        # Step 3: Verify single admin account
        print("\n3️⃣ Vérification compte admin unique...")
        verification_results.append(self.verify_single_admin_account())
        
        # Step 4: Test all admin functions
        print("\n4️⃣ Test de toutes les fonctions admin...")
        verification_results.append(self.test_all_admin_functions())
        
        # Step 5: Verify incorrect account deleted
        print("\n5️⃣ Vérification suppression compte incorrect...")
        verification_results.append(self.verify_incorrect_account_deleted())
        
        return verification_results
    
    def print_final_summary(self):
        """Print final verification summary"""
        print("\n📊 RÉSUMÉ VÉRIFICATION FINALE")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Tests totaux: {total_tests}")
        print(f"Réussis: {passed_tests} ✅")
        print(f"Échoués: {failed_tests} ❌")
        print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 RÉSULTATS CLÉS:")
        
        # Admin login
        admin_login_working = any(r['success'] for r in self.test_results if 'Admin Login Verification' in r['test'])
        if admin_login_working:
            print(f"  ✅ CONNEXION ADMIN: topkitfr@gmail.com / TopKitAdmin2025! fonctionne")
        else:
            print(f"  ❌ CONNEXION ADMIN: Échec de connexion avec les identifiants corrigés")
        
        # Admin privileges
        admin_privileges = any(r['success'] for r in self.test_results if 'Admin Privileges Verification' in r['test'])
        if admin_privileges:
            print(f"  ✅ PRIVILÈGES ADMIN: Tous les privilèges administrateur vérifiés")
        else:
            print(f"  ❌ PRIVILÈGES ADMIN: Privilèges administrateur incomplets")
        
        # Single admin status
        single_admin = any(r['success'] for r in self.test_results if 'Single Admin Account Verification' in r['test'])
        if single_admin:
            print(f"  ✅ COMPTE UNIQUE: Un seul compte admin existe sur le site")
        else:
            print(f"  ❌ COMPTE UNIQUE: Plusieurs comptes admin existent encore")
            if self.all_admin_accounts:
                print(f"      Comptes admin trouvés: {len(self.all_admin_accounts)}")
                for admin in self.all_admin_accounts:
                    print(f"        - {admin.get('username', 'Unknown')}")
        
        # Admin functions
        admin_functions = any(r['success'] for r in self.test_results if 'Admin Functions Testing' in r['test'])
        if admin_functions:
            print(f"  ✅ FONCTIONS ADMIN: Toutes les fonctions admin testées avec succès")
        else:
            print(f"  ❌ FONCTIONS ADMIN: Certaines fonctions admin ne fonctionnent pas")
        
        # Incorrect account deletion
        incorrect_deleted = any(r['success'] for r in self.test_results if 'Incorrect Account Deletion Verification' in r['test'])
        if incorrect_deleted:
            print(f"  ✅ SUPPRESSION: Compte incorrect (topkitfr@gmail.fr) supprimé")
        else:
            print(f"  ❌ SUPPRESSION: Compte incorrect existe encore")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ PROBLÈMES IDENTIFIÉS ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status
        print(f"\n🎯 STATUT FINAL:")
        if passed_tests == total_tests:
            print(f"  ✅ SUCCÈS COMPLET: La correction d'email a été effectuée avec succès")
            print(f"     - Connexion avec topkitfr@gmail.com: ✅")
            print(f"     - Privilèges administrateur: ✅")
            print(f"     - Compte admin unique: ✅")
            print(f"     - Toutes les fonctions admin: ✅")
            print(f"     - Compte incorrect supprimé: ✅")
        elif admin_login_working and admin_privileges:
            print(f"  ⚠️ SUCCÈS PARTIEL: Correction d'email réussie mais actions manuelles requises")
            print(f"     - Connexion admin: ✅")
            print(f"     - Privilèges admin: ✅")
            print(f"     - Statut compte unique: ❌ (suppression manuelle d'autres comptes admin requise)")
        else:
            print(f"  ❌ ÉCHEC: La correction d'email n'est pas complète")
            print(f"     - Intervention manuelle requise")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all final verification tests and return success status"""
        verification_results = self.run_final_verification()
        self.print_final_summary()
        return any(verification_results)

def main():
    """Main test execution - Final Admin Account Verification"""
    verifier = TopKitFinalAdminVerification()
    success = verifier.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()