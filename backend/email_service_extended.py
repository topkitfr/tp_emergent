import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from email_service import GmailSMTPService

logger = logging.getLogger(__name__)

class ExtendedEmailService(GmailSMTPService):
    """Extension du service d'email avec tous les types d'emails TopKit"""
    
    def __init__(self):
        super().__init__()
        logger.info("Extended email service initialized")

    # ========================================
    # EMAILS DE SÉCURITÉ SUPPLÉMENTAIRES
    # ========================================

    def send_password_changed_confirmation(self, user_email: str, user_name: str, user_ip: str = "N/A") -> bool:
        """Send confirmation email when password is changed"""
        
        subject = f"✅ Mot de passe modifié - {self.app_name}"
        
        text_body = f"""
Bonjour {user_name},

Votre mot de passe {self.app_name} a été modifié avec succès.

Détails de la modification :
- Date : {datetime.now().strftime('%d/%m/%Y à %H:%M')}
- Adresse IP : {user_ip}

Si vous n'avez pas effectué cette modification, contactez immédiatement notre support.

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mot de passe modifié - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #28a745; margin: 0; font-size: 28px;">✅ Mot de passe modifié</h1>
            <p style="color: #666; margin: 5px 0;">Confirmation de sécurité</p>
        </div>
        
        <p>Bonjour <strong>{user_name}</strong>,</p>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #155724;"><strong>🔐 Votre mot de passe a été modifié avec succès !</strong></p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">📋 Détails de la modification :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Date et heure</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{datetime.now().strftime('%d/%m/%Y à %H:%M')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Adresse IP</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{user_ip}</td>
            </tr>
        </table>
        
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #721c24;">⚠️ Ce n'était pas vous ?</h4>
            <p style="margin: 0; color: #721c24;">Si vous n'avez pas effectué cette modification, votre compte pourrait être compromis. Contactez immédiatement notre support.</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="mailto:support@topkit.fr" 
               style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                🚨 Signaler un problème
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>L'équipe sécurité<br><strong>{self.app_name}</strong></p>
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

    def send_2fa_enabled_notification(self, user_email: str, user_name: str) -> bool:
        """Send notification when 2FA is enabled"""
        
        subject = f"🔒 Authentification à deux facteurs activée - {self.app_name}"
        
        text_body = f"""
Bonjour {user_name},

L'authentification à deux facteurs (2FA) a été activée sur votre compte {self.app_name}.

Votre compte est maintenant encore plus sécurisé !

Important : Gardez vos codes de récupération en lieu sûr.

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2FA activée - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #28a745; margin: 0; font-size: 28px;">🔒 2FA Activée</h1>
            <p style="color: #666; margin: 5px 0;">Votre compte est maintenant ultra-sécurisé</p>
        </div>
        
        <p>Bravo <strong>{user_name}</strong> !</p>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: center;">
            <h2 style="color: #155724; margin: 0 0 10px 0;">🛡️ Authentification à deux facteurs activée</h2>
            <p style="margin: 0; color: #155724;">Votre compte bénéficie maintenant d'une sécurité renforcée !</p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">🔐 Avantages de la 2FA :</h3>
        
        <ul style="padding-left: 20px; color: #555;">
            <li style="margin: 10px 0;"><strong>🛡️ Sécurité renforcée</strong> - Protection contre les tentatives de piratage</li>
            <li style="margin: 10px 0;"><strong>🔒 Double vérification</strong> - Code requis en plus du mot de passe</li>
            <li style="margin: 10px 0;"><strong>📱 Application mobile</strong> - Codes générés sur votre téléphone</li>
            <li style="margin: 10px 0;"><strong>🔄 Codes de récupération</strong> - Accès de secours si nécessaire</li>
        </ul>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #856404;">💾 Important</h4>
            <p style="margin: 0; color: #856404;">Conservez précieusement vos codes de récupération dans un endroit sûr. Ils vous permettront d'accéder à votre compte si vous perdez votre téléphone.</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Merci de sécuriser votre compte !<br><strong>L'équipe {self.app_name}</strong></p>
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

    def send_suspicious_login_alert(self, user_email: str, user_name: str, login_details: Dict[str, Any]) -> bool:
        """Send alert for suspicious login attempt"""
        
        subject = f"⚠️ Nouvelle connexion depuis {login_details.get('location', 'lieu inconnu')} - {self.app_name}"
        
        text_body = f"""
Bonjour {user_name},

Une nouvelle connexion à votre compte {self.app_name} a été détectée.

Détails :
- Date : {login_details.get('timestamp', 'N/A')}
- Adresse IP : {login_details.get('ip', 'N/A')}
- Lieu : {login_details.get('location', 'Inconnu')}
- Navigateur : {login_details.get('browser', 'N/A')}

Si c'était vous, ignorez cet email.
Sinon, sécurisez immédiatement votre compte.

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alerte connexion - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ffc107; margin: 0; font-size: 28px;">⚠️ Nouvelle Connexion</h1>
            <p style="color: #666; margin: 5px 0;">Alerte de sécurité</p>
        </div>
        
        <p>Bonjour <strong>{user_name}</strong>,</p>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #856404;"><strong>🔔 Une nouvelle connexion à votre compte a été détectée</strong></p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">📋 Détails de la connexion :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Date et heure</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{login_details.get('timestamp', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Adresse IP</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{login_details.get('ip', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Lieu approximatif</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{login_details.get('location', 'Inconnu')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Navigateur</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{login_details.get('browser', 'N/A')}</td>
            </tr>
        </table>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #155724;">✅ C'était vous ?</h4>
            <p style="margin: 0; color: #155724;">Si vous venez de vous connecter, tout va bien ! Vous pouvez ignorer cet email.</p>
        </div>
        
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #721c24;">🚨 Ce n'était pas vous ?</h4>
            <p style="margin: 0; color: #721c24;">Quelqu'un pourrait avoir accès à votre compte. Changez immédiatement votre mot de passe et activez la 2FA.</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{os.environ.get('FRONTEND_URL', 'https://kitauth-fix.preview.emergentagent.com')}/settings/security" 
               style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; margin-right: 10px;">
                🔐 Sécuriser mon compte
            </a>
            <a href="{os.environ.get('FRONTEND_URL', 'https://kitauth-fix.preview.emergentagent.com')}/password/change" 
               style="background-color: #ffc107; color: #212529; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                🔑 Changer le mot de passe
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>L'équipe sécurité<br><strong>{self.app_name}</strong></p>
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

    # ========================================
    # MARKETPLACE ET VENTES - EMAILS
    # ========================================

    def send_jersey_listed_confirmation(self, user_email: str, user_name: str, listing_data: Dict[str, Any]) -> bool:
        """Send confirmation when jersey is listed for sale"""
        
        jersey_name = f"{listing_data.get('jersey_team', 'Équipe')} {listing_data.get('jersey_season', '')}"
        if listing_data.get('jersey_player'):
            jersey_name += f" - {listing_data.get('jersey_player')}"
        
        subject = f"🛒 Maillot mis en vente : {jersey_name}"
        
        text_body = f"""
Bonjour {user_name},

Votre maillot "{jersey_name}" est maintenant en vente sur {self.app_name} !

Prix : €{listing_data.get('price', 'N/A')}
État : {listing_data.get('condition', 'N/A')}

Votre annonce est maintenant visible par tous les collectionneurs.

Conseils pour vendre rapidement :
- Ajoutez des photos de qualité
- Décrivez précisément l'état
- Restez réactif aux messages

Bonne vente !
L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maillot en vente - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #28a745; margin: 0; font-size: 28px;">🛒 En Vente !</h1>
            <p style="color: #666; margin: 5px 0;">Votre maillot est maintenant sur le marketplace</p>
        </div>
        
        <p>Félicitations <strong>{user_name}</strong> !</p>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: center;">
            <h2 style="color: #155724; margin: 0 0 10px 0;">{jersey_name}</h2>
            <p style="margin: 0; color: #155724;"><strong>💰 Prix : €{listing_data.get('price', 'N/A')}</strong></p>
        </div>
        
        <p>Votre maillot est maintenant visible par tous les collectionneurs de {self.app_name} !</p>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">💡 Conseils pour vendre rapidement :</h3>
        
        <ul style="padding-left: 20px; color: #555;">
            <li style="margin: 10px 0;"><strong>📸 Photos de qualité</strong> - Images nettes, bien éclairées, sous tous les angles</li>
            <li style="margin: 10px 0;"><strong>📝 Description précise</strong> - Détaillez l'état, les défauts éventuels</li>
            <li style="margin: 10px 0;"><strong>💬 Réactivité</strong> - Répondez rapidement aux questions des acheteurs</li>
            <li style="margin: 10px 0;"><strong>💰 Prix juste</strong> - Comparez avec des maillots similaires</li>
        </ul>
        
        <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #004085;">📊 Statistiques</h4>
            <p style="margin: 0; color: #004085;">Vous serez notifié par email de chaque vue, question et offre sur votre maillot.</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://kitauth-fix.preview.emergentagent.com")}}/my-listings" 
               style="background-color: #1a56db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                📋 Gérer mes annonces
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Bonne vente !<br><strong>L'équipe {self.app_name}</strong></p>
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

    def send_jersey_sold_notification(self, seller_email: str, seller_name: str, sale_data: Dict[str, Any]) -> bool:
        """Send notification when jersey is sold"""
        
        jersey_name = f"{sale_data.get('jersey_team', 'Équipe')} {sale_data.get('jersey_season', '')}"
        if sale_data.get('jersey_player'):
            jersey_name += f" - {sale_data.get('jersey_player')}"
        
        subject = f"🎉 Maillot vendu : {jersey_name}"
        
        gross_amount = sale_data.get('amount', 0)
        commission = sale_data.get('commission', 0)
        net_amount = gross_amount - commission
        
        text_body = f"""
Félicitations {seller_name} !

Votre maillot "{jersey_name}" a été vendu ! 🎉

Détails de la vente :
- Prix de vente : €{gross_amount:.2f}
- Commission TopKit (5%) : €{commission:.2f}
- Vous recevrez : €{net_amount:.2f}

L'acheteur va vous contacter pour organiser l'expédition.

Merci de contribuer à la communauté TopKit !

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maillot vendu - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #28a745; margin: 0; font-size: 28px;">🎉 Vendu !</h1>
            <p style="color: #666; margin: 5px 0;">Félicitations pour votre vente</p>
        </div>
        
        <p>Bravo <strong>{seller_name}</strong> !</p>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: center;">
            <h2 style="color: #155724; margin: 0 0 10px 0;">{jersey_name}</h2>
            <p style="margin: 0; color: #155724;"><strong>💰 Vendu pour €{gross_amount:.2f} !</strong></p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">💰 Récapitulatif financier :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 60%;">Prix de vente</td>
                <td style="padding: 12px; border: 1px solid #dee2e6; text-align: right;">€{gross_amount:.2f}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6;">Commission TopKit (5%)</td>
                <td style="padding: 12px; border: 1px solid #dee2e6; text-align: right;">- €{commission:.2f}</td>
            </tr>
            <tr style="background-color: #d4edda; font-weight: bold;">
                <td style="padding: 12px; border: 1px solid #c3e6cb;">Vous recevrez</td>
                <td style="padding: 12px; border: 1px solid #c3e6cb; text-align: right;">€{net_amount:.2f}</td>
            </tr>
        </table>
        
        <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #004085;">📦 Prochaines étapes</h4>
            <p style="margin: 0; color: #004085;">L'acheteur va vous contacter pour organiser l'expédition. Assurez-vous d'emballer soigneusement le maillot.</p>
        </div>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #856404;">💡 Conseils d'expédition</h4>
            <ul style="margin: 10px 0 0 20px; color: #856404;">
                <li>Emballez dans un sac plastique étanche</li>
                <li>Utilisez un colis rigide</li>
                <li>Prenez des photos avant envoi</li>
                <li>Ajoutez un numéro de suivi</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://kitauth-fix.preview.emergentagent.com")}}/sales" 
               style="background-color: #1a56db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                📊 Voir mes ventes
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Merci de faire vivre TopKit !<br><strong>L'équipe {self.app_name}</strong></p>
            <p style="font-size: 12px;">© 2024 {self.app_name}. Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(
            to_email=seller_email,
            subject=subject,
            body=text_body,
            html_body=html_body
        )

    def send_purchase_confirmation(self, buyer_email: str, buyer_name: str, purchase_data: Dict[str, Any]) -> bool:
        """Send purchase confirmation to buyer"""
        
        jersey_name = f"{purchase_data.get('jersey_team', 'Équipe')} {purchase_data.get('jersey_season', '')}"
        if purchase_data.get('jersey_player'):
            jersey_name += f" - {purchase_data.get('jersey_player')}"
        
        subject = f"🎯 Achat confirmé : {jersey_name}"
        
        text_body = f"""
Félicitations {buyer_name} !

Votre achat de "{jersey_name}" est confirmé ! ✅

Montant payé : €{purchase_data.get('amount', 0):.2f}
Vendeur : {purchase_data.get('seller_name', 'N/A')}

Le vendeur va vous contacter pour organiser l'expédition.

Si vous avez des questions, n'hésitez pas à nous contacter.

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Achat confirmé - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1a56db; margin: 0; font-size: 28px;">🎯 Achat Confirmé !</h1>
            <p style="color: #666; margin: 5px 0;">Votre nouveau maillot arrive bientôt</p>
        </div>
        
        <p>Félicitations <strong>{buyer_name}</strong> !</p>
        
        <div style="background-color: #d1ecf1; border: 1px solid #b8daff; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: center;">
            <h2 style="color: #0c5460; margin: 0 0 10px 0;">{jersey_name}</h2>
            <p style="margin: 0; color: #0c5460;"><strong>💰 Montant : €{purchase_data.get('amount', 0):.2f}</strong></p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">📋 Détails de l'achat :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Maillot</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_name}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Vendeur</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{purchase_data.get('seller_name', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Montant payé</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">€{purchase_data.get('amount', 0):.2f}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Date d'achat</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{datetime.now().strftime('%d/%m/%Y à %H:%M')}</td>
            </tr>
        </table>
        
        <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #004085;">📦 Expédition</h4>
            <p style="margin: 0; color: #004085;">Le vendeur va vous contacter dans les 24-48h pour organiser l'expédition et vous donner un numéro de suivi.</p>
        </div>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #155724;">🛡️ Protection acheteur</h4>
            <p style="margin: 0; color: #155724;">Votre achat est protégé. Si le maillot ne correspond pas à la description, contactez notre support.</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://kitauth-fix.preview.emergentagent.com")}}/purchases" 
               style="background-color: #1a56db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; margin-right: 10px;">
                📋 Mes achats
            </a>
            <a href="mailto:support@topkit.fr" 
               style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                💬 Support
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Profitez de votre nouveau maillot !<br><strong>L'équipe {self.app_name}</strong></p>
            <p style="font-size: 12px;">© 2024 {self.app_name}. Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(
            to_email=buyer_email,
            subject=subject,
            body=text_body,
            html_body=html_body
        )

# Initialize the extended email service
try:
    extended_gmail_service = ExtendedEmailService()
    logger.info("Extended Gmail SMTP service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize extended Gmail SMTP service: {e}")
    extended_gmail_service = None