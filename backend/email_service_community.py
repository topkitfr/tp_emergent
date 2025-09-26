import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from email_service import GmailSMTPService

logger = logging.getLogger(__name__)

class CommunityEmailService(GmailSMTPService):
    """Service d'email pour les fonctionnalités communautaires et collections TopKit"""
    
    def __init__(self):
        super().__init__()
        logger.info("Community email service initialized")

    # ========================================
    # COLLECTIONS ET WISHLIST - EMAILS
    # ========================================

    def send_wishlist_jersey_available(self, user_email: str, user_name: str, jersey_data: Dict[str, Any], listing_data: Dict[str, Any]) -> bool:
        """Send notification when a jersey from wishlist becomes available"""
        
        jersey_name = f"{jersey_data.get('team', 'Équipe')} {jersey_data.get('season', '')}"
        if jersey_data.get('player'):
            jersey_name += f" - {jersey_data.get('player')}"
        
        subject = f"🔍 Maillot recherché disponible : {jersey_name}"
        
        text_body = f"""
Bonne nouvelle {user_name} !

Le maillot "{jersey_name}" de votre liste de souhaits est maintenant disponible ! 🎯

Prix : €{listing_data.get('price', 'N/A')}
État : {listing_data.get('condition', 'N/A')}
Vendeur : {listing_data.get('seller_name', 'N/A')}

Dépêchez-vous, les maillots populaires partent vite !

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maillot recherché disponible - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ff6b35; margin: 0; font-size: 28px;">🔍 Trouvé !</h1>
            <p style="color: #666; margin: 5px 0;">Le maillot de vos rêves est disponible</p>
        </div>
        
        <p>Bonne nouvelle <strong>{user_name}</strong> !</p>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: center;">
            <h2 style="color: #856404; margin: 0 0 10px 0;">{jersey_name}</h2>
            <p style="margin: 0; color: #856404;"><strong>🎯 De votre liste de souhaits est maintenant disponible !</strong></p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">📋 Détails de l'annonce :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Prix</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">€{listing_data.get('price', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">État</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{listing_data.get('condition', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Vendeur</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{listing_data.get('seller_name', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Taille</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('size', 'N/A')}</td>
            </tr>
        </table>
        
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #721c24;">⚡ Attention !</h4>
            <p style="margin: 0; color: #721c24;">Les maillots populaires partent très vite. N'attendez pas trop pour prendre votre décision !</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{os.environ.get('FRONTEND_URL', 'https://topkit-auth-fix-2.preview.emergentagent.com')}/jersey/{jersey_data.get('id', '')}" 
               style="background-color: #ff6b35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 18px;">
                👀 Voir le maillot
            </a>
        </div>
        
        <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #004085;">💡 Astuce</h4>
            <p style="margin: 0; color: #004085;">Vous pouvez contacter directement le vendeur pour poser des questions ou négocier le prix.</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Bonne chasse aux maillots !<br><strong>L'équipe {self.app_name}</strong></p>
            <p style="font-size: 12px;">© 2024 {self.app_name}. Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(
            to_email=user_email,
            subject=subject,
            body=text_body,
            html_body=html_body
        )

    def send_friend_request_notification(self, user_email: str, user_name: str, requester_data: Dict[str, Any]) -> bool:
        """Send notification for new friend request"""
        
        requester_name = requester_data.get('name', 'Quelqu\'un')
        subject = f"🤝 {requester_name} souhaite être votre ami sur {self.app_name}"
        
        text_body = f"""
Bonjour {user_name},

{requester_data.get('name', 'Un utilisateur')} souhaite être votre ami sur {self.app_name} !

Profil :
- Nom : {requester_data.get('name', 'N/A')}
- Maillots en collection : {requester_data.get('collection_size', 0)}
- Membre depuis : {requester_data.get('member_since', 'N/A')}

Maillots en commun : {requester_data.get('common_jerseys', 0)}

Acceptez sa demande pour commencer à échanger !

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nouvelle demande d'ami - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #17a2b8; margin: 0; font-size: 28px;">🤝 Nouvelle Demande d'Ami</h1>
            <p style="color: #666; margin: 5px 0;">Quelqu'un souhaite rejoindre votre réseau</p>
        </div>
        
        <p>Bonjour <strong>{user_name}</strong>,</p>
        
        <div style="background-color: #d1ecf1; border: 1px solid #b8daff; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: center;">
            <h2 style="color: #0c5460; margin: 0 0 10px 0;">{requester_data.get('name', 'Un utilisateur')}</h2>
            <p style="margin: 0; color: #0c5460;">souhaite être votre ami sur {self.app_name} !</p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">👤 Profil du demandeur :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 40%;">Nom</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{requester_data.get('name', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Collection</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{requester_data.get('collection_size', 0)} maillots</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Membre depuis</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{requester_data.get('member_since', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Maillots en commun</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{requester_data.get('common_jerseys', 0)}</td>
            </tr>
        </table>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #155724;">🎯 Pourquoi être ami ?</h4>
            <ul style="margin: 10px 0 0 20px; color: #155724;">
                <li>Messages privés pour négocier</li>
                <li>Accès prioritaire à ses ventes</li>
                <li>Partage de conseils de collection</li>
                <li>Alertes sur ses nouveaux maillots</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://topkit-auth-fix-2.preview.emergentagent.com")}}/friends/requests" 
               style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; margin-right: 10px;">
                ✅ Accepter
            </a>
            <a href="{{os.environ.get("FRONTEND_URL", "https://topkit-auth-fix-2.preview.emergentagent.com")}}/profile/{requester_data.get('id', '')}" 
               style="background-color: #17a2b8; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                👀 Voir profil
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Agrandissez votre réseau de collectionneurs !<br><strong>L'équipe {self.app_name}</strong></p>
            <p style="font-size: 12px;">© 2024 {self.app_name}. Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(
            to_email=user_email,
            subject=subject,
            body=text_body,
            html_body=html_body
        )

# Initialize the community email service
try:
    community_email_service = CommunityEmailService()
    logger.info("Community email service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize community email service: {e}")
    community_email_service = None