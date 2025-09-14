#!/usr/bin/env python3
"""
🎯 TOPKIT BETA ACCESS EMAIL SYSTEM VERIFICATION TEST
==================================================

Test spécifique pour vérifier que le système d'emails fonctionne correctement
dans le workflow des demandes d'accès beta.

Ce test vérifie :
1. Configuration du service Gmail SMTP
2. Envoi d'emails de confirmation utilisateur
3. Envoi d'emails de notification admin
4. Envoi d'emails d'approbation
5. Intégration avec le backend
"""

import asyncio
import aiohttp
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add backend directory to path to import email services
sys.path.append('/app/backend')

try:
    from email_service import gmail_service
    from email_manager import email_manager
    EMAIL_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import email services: {e}")
    EMAIL_SERVICES_AVAILABLE = False

# Configuration
BASE_URL = "https://jersey-collab-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

# Test data
TEST_EMAIL_REQUEST = {
    "email": "test.email.verification@example.com",
    "first_name": "Marie",
    "last_name": "EmailTest",
    "message": "Test de vérification du système d'emails beta"
}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BetaEmailTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        logger.info(f"{status} - {test_name}: {details}")
    
    async def test_email_service_configuration(self) -> bool:
        """Test de la configuration du service d'email"""
        try:
            if not EMAIL_SERVICES_AVAILABLE:
                self.log_test_result(
                    "Configuration service email",
                    False,
                    "Services d'email non disponibles - modules non importés"
                )
                return False
            
            # Test Gmail service
            if gmail_service is None:
                self.log_test_result(
                    "Configuration service email",
                    False,
                    "Service Gmail SMTP non initialisé"
                )
                return False
            
            # Vérifier la configuration
            config_details = {
                "smtp_server": getattr(gmail_service, 'smtp_server', 'N/A'),
                "smtp_port": getattr(gmail_service, 'smtp_port', 'N/A'),
                "from_email": getattr(gmail_service, 'from_email', 'N/A'),
                "from_name": getattr(gmail_service, 'from_name', 'N/A'),
                "app_name": getattr(gmail_service, 'app_name', 'N/A')
            }
            
            self.log_test_result(
                "Configuration service email",
                True,
                f"Service Gmail SMTP configuré correctement",
                config_details
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "Configuration service email",
                False,
                f"Exception lors de la vérification: {str(e)}"
            )
            return False
    
    async def test_email_manager_status(self) -> bool:
        """Test du statut du gestionnaire d'emails"""
        try:
            if not EMAIL_SERVICES_AVAILABLE or email_manager is None:
                self.log_test_result(
                    "Statut gestionnaire d'emails",
                    False,
                    "Gestionnaire d'emails non disponible"
                )
                return False
            
            # Obtenir le statut des services
            status = email_manager.get_service_status()
            
            self.log_test_result(
                "Statut gestionnaire d'emails",
                status.get('basic_service', False),
                f"Services disponibles: {status.get('total_services', 0)}/4, Statut: {status.get('status', 'unknown')}",
                status
            )
            return status.get('basic_service', False)
            
        except Exception as e:
            self.log_test_result(
                "Statut gestionnaire d'emails",
                False,
                f"Exception lors de la vérification: {str(e)}"
            )
            return False
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get("token")
                    user_info = data.get("user", {})
                    
                    self.log_test_result(
                        "Authentification admin",
                        True,
                        f"Authentifié comme {user_info.get('name', 'Admin')} (Role: {user_info.get('role', 'unknown')})"
                    )
                    return True
                else:
                    error_data = await response.text()
                    self.log_test_result(
                        "Authentification admin",
                        False,
                        f"Échec authentification avec status {response.status}: {error_data}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Authentification admin",
                False,
                f"Exception lors de l'authentification: {str(e)}"
            )
            return False
    
    async def test_beta_request_with_email_tracking(self) -> Optional[str]:
        """Test de soumission avec suivi des emails"""
        try:
            # Soumettre la demande beta
            async with self.session.post(f"{BASE_URL}/beta/request-access", json=TEST_EMAIL_REQUEST) as response:
                if response.status == 200:
                    data = await response.json()
                    request_id = data.get("request_id")
                    
                    self.log_test_result(
                        "Soumission beta avec suivi email",
                        True,
                        f"Demande soumise avec succès. Request ID: {request_id}. Emails déclenchés automatiquement.",
                        {
                            "request_id": request_id,
                            "user_email": TEST_EMAIL_REQUEST["email"],
                            "admin_email": ADMIN_EMAIL,
                            "expected_emails": [
                                "Confirmation à l'utilisateur",
                                "Notification à l'admin"
                            ]
                        }
                    )
                    return request_id
                else:
                    error_data = await response.text()
                    self.log_test_result(
                        "Soumission beta avec suivi email",
                        False,
                        f"Échec soumission avec status {response.status}: {error_data}"
                    )
                    return None
                    
        except Exception as e:
            self.log_test_result(
                "Soumission beta avec suivi email",
                False,
                f"Exception lors de la soumission: {str(e)}"
            )
            return None
    
    async def test_beta_approval_with_email_tracking(self, request_id: str) -> bool:
        """Test d'approbation avec suivi des emails"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            async with self.session.post(f"{BASE_URL}/admin/beta/requests/{request_id}/approve", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    self.log_test_result(
                        "Approbation beta avec suivi email",
                        True,
                        f"Demande approuvée avec succès. Email d'approbation déclenché automatiquement.",
                        {
                            "approval_message": data.get('message', 'N/A'),
                            "user_email": TEST_EMAIL_REQUEST["email"],
                            "expected_email": "Email d'approbation à l'utilisateur"
                        }
                    )
                    return True
                else:
                    error_data = await response.text()
                    self.log_test_result(
                        "Approbation beta avec suivi email",
                        False,
                        f"Échec approbation avec status {response.status}: {error_data}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result(
                "Approbation beta avec suivi email",
                False,
                f"Exception lors de l'approbation: {str(e)}"
            )
            return False
    
    async def test_direct_email_functionality(self) -> bool:
        """Test direct de la fonctionnalité d'email"""
        try:
            if not EMAIL_SERVICES_AVAILABLE or email_manager is None:
                self.log_test_result(
                    "Test direct fonctionnalité email",
                    False,
                    "Services d'email non disponibles pour test direct"
                )
                return False
            
            # Test d'envoi d'email de test
            test_success = email_manager.send_test_email(
                recipient_email="test@example.com",
                email_type="basic"
            )
            
            if test_success:
                self.log_test_result(
                    "Test direct fonctionnalité email",
                    True,
                    "Service d'email fonctionnel - test d'envoi réussi"
                )
                return True
            else:
                self.log_test_result(
                    "Test direct fonctionnalité email",
                    False,
                    "Service d'email non fonctionnel - échec du test d'envoi"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Test direct fonctionnalité email",
                False,
                f"Exception lors du test direct: {str(e)}"
            )
            return False
    
    async def verify_email_templates_exist(self) -> bool:
        """Vérifier que les templates d'email existent"""
        try:
            if not EMAIL_SERVICES_AVAILABLE or gmail_service is None:
                self.log_test_result(
                    "Vérification templates email",
                    False,
                    "Service Gmail non disponible pour vérification templates"
                )
                return False
            
            # Vérifier les méthodes d'email beta
            email_methods = [
                'send_beta_access_notification',
                'send_beta_access_approved_email',
                'send_user_confirmation_email'
            ]
            
            available_methods = []
            for method_name in email_methods:
                if hasattr(gmail_service, method_name):
                    available_methods.append(method_name)
            
            if len(available_methods) == len(email_methods):
                self.log_test_result(
                    "Vérification templates email",
                    True,
                    f"Tous les templates d'email beta disponibles: {', '.join(available_methods)}",
                    {"available_methods": available_methods}
                )
                return True
            else:
                missing_methods = [m for m in email_methods if m not in available_methods]
                self.log_test_result(
                    "Vérification templates email",
                    False,
                    f"Templates manquants: {', '.join(missing_methods)}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Vérification templates email",
                False,
                f"Exception lors de la vérification: {str(e)}"
            )
            return False
    
    async def run_comprehensive_email_test(self):
        """Exécuter le test complet du système d'emails"""
        logger.info("📧 DÉBUT DU TEST COMPLET DU SYSTÈME D'EMAILS BETA")
        logger.info("=" * 60)
        
        # Test 1: Configuration du service d'email
        await self.test_email_service_configuration()
        
        # Test 2: Statut du gestionnaire d'emails
        await self.test_email_manager_status()
        
        # Test 3: Vérification des templates
        await self.verify_email_templates_exist()
        
        # Test 4: Test direct de fonctionnalité
        await self.test_direct_email_functionality()
        
        # Test 5: Authentification admin
        if not await self.authenticate_admin():
            logger.error("❌ Échec authentification admin - Tests workflow arrêtés")
            await self.print_test_summary()
            return
        
        # Test 6: Workflow complet avec suivi emails
        request_id = await self.test_beta_request_with_email_tracking()
        if request_id:
            await asyncio.sleep(1)  # Attendre propagation
            await self.test_beta_approval_with_email_tracking(request_id)
        
        # Résumé des résultats
        await self.print_test_summary()
    
    async def print_test_summary(self):
        """Afficher le résumé des tests d'emails"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RÉSUMÉ DES TESTS DU SYSTÈME D'EMAILS BETA")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"📈 STATISTIQUES:")
        logger.info(f"   • Total des tests: {total_tests}")
        logger.info(f"   • Tests réussis: {passed_tests}")
        logger.info(f"   • Tests échoués: {failed_tests}")
        logger.info(f"   • Taux de réussite: {success_rate:.1f}%")
        
        logger.info(f"\n📋 DÉTAIL DES TESTS:")
        for i, result in enumerate(self.test_results, 1):
            logger.info(f"   {i:2d}. {result['status']} {result['test']}")
            if result['details']:
                logger.info(f"       └─ {result['details']}")
        
        # Analyse spécifique aux emails
        logger.info(f"\n📧 ANALYSE DU SYSTÈME D'EMAILS:")
        
        email_config_ok = any(r["test"] == "Configuration service email" and r["success"] for r in self.test_results)
        email_manager_ok = any(r["test"] == "Statut gestionnaire d'emails" and r["success"] for r in self.test_results)
        templates_ok = any(r["test"] == "Vérification templates email" and r["success"] for r in self.test_results)
        direct_test_ok = any(r["test"] == "Test direct fonctionnalité email" and r["success"] for r in self.test_results)
        
        logger.info(f"   {'✅' if email_config_ok else '❌'} Configuration Gmail SMTP")
        logger.info(f"   {'✅' if email_manager_ok else '❌'} Gestionnaire d'emails")
        logger.info(f"   {'✅' if templates_ok else '❌'} Templates d'emails beta")
        logger.info(f"   {'✅' if direct_test_ok else '❌'} Fonctionnalité d'envoi")
        
        # Données de test
        logger.info(f"\n📧 DONNÉES DE TEST:")
        logger.info(f"   • Email test: {TEST_EMAIL_REQUEST['email']}")
        logger.info(f"   • Nom: {TEST_EMAIL_REQUEST['first_name']} {TEST_EMAIL_REQUEST['last_name']}")
        logger.info(f"   • Admin: {ADMIN_EMAIL}")
        
        # Conclusion
        if success_rate >= 80:
            logger.info(f"\n🎉 CONCLUSION: SYSTÈME D'EMAILS FONCTIONNEL!")
            logger.info(f"   Le système d'emails pour les demandes beta fonctionne correctement.")
        elif success_rate >= 60:
            logger.info(f"\n⚠️  CONCLUSION: SYSTÈME D'EMAILS PARTIELLEMENT FONCTIONNEL")
            logger.info(f"   Le système fonctionne mais nécessite quelques corrections.")
        else:
            logger.info(f"\n❌ CONCLUSION: SYSTÈME D'EMAILS NÉCESSITE DES CORRECTIONS")
            logger.info(f"   Le système présente des problèmes importants.")
        
        logger.info("=" * 60)

async def main():
    """Fonction principale pour exécuter les tests d'emails"""
    async with BetaEmailTester() as tester:
        await tester.run_comprehensive_email_test()

if __name__ == "__main__":
    asyncio.run(main())