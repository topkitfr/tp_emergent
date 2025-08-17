import logging
from typing import Dict, Any, List, Optional
from email_service import gmail_service
from email_service_extended import extended_gmail_service
from email_service_community import community_email_service
from email_service_marketing import marketing_email_service

logger = logging.getLogger(__name__)

class TopKitEmailManager:
    """Gestionnaire central pour tous les types d'emails TopKit"""
    
    def __init__(self):
        self.basic_service = gmail_service
        self.extended_service = extended_gmail_service
        self.community_service = community_email_service
        self.marketing_service = marketing_email_service
        logger.info("TopKit Email Manager initialized")
    
    # ========================================
    # EMAILS DE BASE (DÉJÀ IMPLÉMENTÉS)
    # ========================================
    
    def send_user_confirmation_email(self, user_email: str, user_name: str, confirmation_token: str) -> bool:
        """Email de confirmation d'inscription"""
        if self.basic_service:
            return self.basic_service.send_user_confirmation_email(user_email, user_name, confirmation_token)
        return False
    
    def send_beta_access_notification(self, admin_email: str, request_data: Dict[str, Any]) -> bool:
        """Notification admin pour demande d'accès beta"""
        if self.basic_service:
            return self.basic_service.send_beta_access_notification(admin_email, request_data)
        return False
    
    def send_beta_access_approved_email(self, user_email: str, user_name: str, temp_password: Optional[str] = None) -> bool:
        """Email d'approbation d'accès beta"""
        if self.basic_service:
            return self.basic_service.send_beta_access_approved_email(user_email, user_name, temp_password)
        return False

    # ========================================
    # EMAILS SYSTÈME DE MAILLOTS
    # ========================================
    
    def send_jersey_submitted_confirmation(self, user_email: str, user_name: str, jersey_data: Dict[str, Any]) -> bool:
        """Confirmation de soumission de maillot"""
        if self.basic_service:
            return self.basic_service.send_jersey_submitted_confirmation(user_email, user_name, jersey_data)
        return False
    
    def send_jersey_submitted_admin_notification(self, admin_email: str, jersey_data: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Notification admin pour nouveau maillot soumis"""
        if self.basic_service:
            return self.basic_service.send_jersey_submitted_admin_notification(admin_email, jersey_data, user_data)
        return False
    
    def send_jersey_approved_notification(self, user_email: str, user_name: str, jersey_data: Dict[str, Any]) -> bool:
        """Notification d'approbation de maillot"""
        if self.basic_service:
            return self.basic_service.send_jersey_approved_notification(user_email, user_name, jersey_data)
        return False
    
    def send_jersey_rejected_notification(self, user_email: str, user_name: str, jersey_data: Dict[str, Any], rejection_reason: str) -> bool:
        """Notification de rejet de maillot"""
        if self.basic_service:
            return self.basic_service.send_jersey_rejected_notification(user_email, user_name, jersey_data, rejection_reason)
        return False

    # ========================================
    # EMAILS DE SÉCURITÉ
    # ========================================
    
    def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Email de réinitialisation de mot de passe"""
        if self.basic_service:
            return self.basic_service.send_password_reset_email(user_email, user_name, reset_token)
        return False
    
    def send_password_changed_confirmation(self, user_email: str, user_name: str, user_ip: str = "N/A") -> bool:
        """Confirmation de changement de mot de passe"""
        if self.extended_service:
            return self.extended_service.send_password_changed_confirmation(user_email, user_name, user_ip)
        return False
    
    def send_2fa_enabled_notification(self, user_email: str, user_name: str) -> bool:
        """Notification d'activation 2FA"""
        if self.extended_service:
            return self.extended_service.send_2fa_enabled_notification(user_email, user_name)
        return False
    
    def send_suspicious_login_alert(self, user_email: str, user_name: str, login_details: Dict[str, Any]) -> bool:
        """Alerte de connexion suspecte"""
        if self.extended_service:
            return self.extended_service.send_suspicious_login_alert(user_email, user_name, login_details)
        return False

    # ========================================
    # EMAILS MARKETPLACE ET VENTES
    # ========================================
    
    def send_jersey_listed_confirmation(self, user_email: str, user_name: str, listing_data: Dict[str, Any]) -> bool:
        """Confirmation de mise en vente"""
        if self.extended_service:
            return self.extended_service.send_jersey_listed_confirmation(user_email, user_name, listing_data)
        return False
    
    def send_jersey_sold_notification(self, seller_email: str, seller_name: str, sale_data: Dict[str, Any]) -> bool:
        """Notification de vente réussie"""
        if self.extended_service:
            return self.extended_service.send_jersey_sold_notification(seller_email, seller_name, sale_data)
        return False
    
    def send_purchase_confirmation(self, buyer_email: str, buyer_name: str, purchase_data: Dict[str, Any]) -> bool:
        """Confirmation d'achat"""
        if self.extended_service:
            return self.extended_service.send_purchase_confirmation(buyer_email, buyer_name, purchase_data)
        return False

    # ========================================
    # EMAILS COLLECTIONS ET WISHLIST
    # ========================================
    
    def send_wishlist_jersey_available(self, user_email: str, user_name: str, jersey_data: Dict[str, Any], listing_data: Dict[str, Any]) -> bool:
        """Alerte maillot de wishlist disponible"""
        if self.community_service:
            return self.community_service.send_wishlist_jersey_available(user_email, user_name, jersey_data, listing_data)
        return False

    # ========================================
    # EMAILS SOCIAUX ET COMMUNAUTÉ
    # ========================================
    
    def send_friend_request_notification(self, user_email: str, user_name: str, requester_data: Dict[str, Any]) -> bool:
        """Notification de demande d'ami"""
        if self.community_service:
            return self.community_service.send_friend_request_notification(user_email, user_name, requester_data)
        return False

    # ========================================
    # EMAILS MARKETING ET ENGAGEMENT
    # ========================================
    
    def send_weekly_newsletter(self, user_email: str, user_name: str, newsletter_data: Dict[str, Any]) -> bool:
        """Newsletter hebdomadaire"""
        if self.marketing_service:
            return self.marketing_service.send_weekly_newsletter(user_email, user_name, newsletter_data)
        return False
    
    def send_anniversary_email(self, user_email: str, user_name: str, anniversary_data: Dict[str, Any]) -> bool:
        """Email d'anniversaire"""
        if self.marketing_service:
            return self.marketing_service.send_anniversary_email(user_email, user_name, anniversary_data)
        return False

    # ========================================
    # EMAILS DE TEST ET UTILITAIRES
    # ========================================
    
    def send_test_email(self, recipient_email: str, email_type: str = "basic") -> bool:
        """Envoyer un email de test"""
        test_data = {
            "user_name": "Test User",
            "jersey": {
                "team": "Manchester United",
                "season": "1999",
                "player": "Beckham",
                "size": "L",
                "condition": "Excellent"
            }
        }
        
        if email_type == "jersey_submitted":
            return self.send_jersey_submitted_confirmation(
                recipient_email, 
                test_data["user_name"], 
                test_data["jersey"]
            )
        elif email_type == "password_reset":
            return self.send_password_reset_email(
                recipient_email,
                test_data["user_name"],
                "test-token-123"
            )
        elif email_type == "newsletter":
            newsletter_data = {
                "week_number": "42",
                "trend1": "Maillots rétro Manchester United",
                "trend2": "Nouveaux maillots PSG 2024/25",
                "trend3": "Éditions limitées Real Madrid",
                "new_jerseys": "156",
                "sales": "98",
                "new_members": "267",
                "football_news": "Le mercato d'hiver bat son plein avec de nombreux transferts."
            }
            return self.send_weekly_newsletter(recipient_email, test_data["user_name"], newsletter_data)
        else:
            # Email de test basique
            if self.basic_service:
                return self.basic_service.send_email(
                    to_email=recipient_email,
                    subject="🧪 Test Email TopKit",
                    body="Ceci est un email de test du système TopKit.",
                    html_body="""
                    <html>
                        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #1a56db;">🧪 Test Email TopKit</h2>
                            <p>Félicitations ! Le système d'email TopKit fonctionne parfaitement.</p>
                            <p><strong>Types d'emails disponibles :</strong></p>
                            <ul>
                                <li>✅ Confirmation d'inscription</li>
                                <li>✅ Notifications beta</li>
                                <li>✅ Système de maillots</li>
                                <li>✅ Sécurité et 2FA</li>
                                <li>✅ Marketplace et ventes</li>
                                <li>✅ Collections et wishlist</li>
                                <li>✅ Communauté et amis</li>
                                <li>✅ Marketing et newsletters</li>
                            </ul>
                            <hr>
                            <p style="color: #666; font-size: 14px;">
                                Email de test envoyé depuis TopKit<br>
                                Service: Gmail SMTP
                            </p>
                        </body>
                    </html>
                    """
                )
        return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtenir le statut de tous les services d'email"""
        return {
            "basic_service": self.basic_service is not None,
            "extended_service": self.extended_service is not None,
            "community_service": self.community_service is not None,
            "marketing_service": self.marketing_service is not None,
            "total_services": sum([
                self.basic_service is not None,
                self.extended_service is not None,
                self.community_service is not None,
                self.marketing_service is not None
            ]),
            "status": "fully_operational" if all([
                self.basic_service,
                self.extended_service,
                self.community_service,
                self.marketing_service
            ]) else "partially_operational"
        }

# Initialize the email manager
try:
    email_manager = TopKitEmailManager()
    logger.info("TopKit Email Manager initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize TopKit Email Manager: {e}")
    email_manager = None