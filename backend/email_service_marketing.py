import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from email_service import GmailSMTPService

logger = logging.getLogger(__name__)

class MarketingEmailService(GmailSMTPService):
    """Service d'email pour le marketing et les notifications administratives TopKit"""
    
    def __init__(self):
        super().__init__()
        logger.info("Marketing email service initialized")

    # ========================================
    # MARKETING ET ENGAGEMENT - EMAILS
    # ========================================

    def send_anniversary_email(self, user_email: str, user_name: str, anniversary_data: Dict[str, Any]) -> bool:
        """Send anniversary email with year recap"""
        
        years = anniversary_data.get('years', 1)
        years_text = f"{years} an" + ("s" if years > 1 else "")
        subject = f"🎂 Joyeux anniversaire TopKit ! {years_text} avec nous"
        
        text_body = f"""
Joyeux anniversaire {user_name} !

Cela fait {years_text} que vous avez rejoint la famille {self.app_name} ! 🎉

Votre année en chiffres :
- {anniversary_data.get('jerseys_added', 0)} maillots ajoutés à votre collection
- {anniversary_data.get('sales_made', 0)} ventes réalisées
- {anniversary_data.get('purchases_made', 0)} achats effectués
- €{anniversary_data.get('total_value', 0):.2f} de valeur de collection

Cadeau anniversaire : {anniversary_data.get('gift', 'Réduction spéciale de 15% sur votre prochain achat')}

Merci de faire partie de notre communauté !

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anniversaire TopKit - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ff6b35; margin: 0; font-size: 28px;">🎂 Joyeux Anniversaire !</h1>
            <p style="color: #666; margin: 5px 0;">{years_text} avec TopKit</p>
        </div>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 30px; margin: 20px 0; text-align: center;">
            <h2 style="color: #856404; margin: 0 0 15px 0;">🎉 {user_name}, cela fait {years_text} !</h2>
            <p style="margin: 0; color: #856404;">Merci de faire partie de la famille {self.app_name}</p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">📊 Votre année en chiffres :</h3>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
            <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; text-align: center;">
                <h4 style="margin: 0 0 5px 0; color: #004085; font-size: 24px;">{anniversary_data.get('jerseys_added', 0)}</h4>
                <p style="margin: 0; color: #004085; font-size: 12px;">Maillots ajoutés</p>
            </div>
            <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; text-align: center;">
                <h4 style="margin: 0 0 5px 0; color: #155724; font-size: 24px;">{anniversary_data.get('sales_made', 0)}</h4>
                <p style="margin: 0; color: #155724; font-size: 12px;">Ventes réalisées</p>
            </div>
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; text-align: center;">
                <h4 style="margin: 0 0 5px 0; color: #856404; font-size: 24px;">{anniversary_data.get('purchases_made', 0)}</h4>
                <p style="margin: 0; color: #856404; font-size: 12px;">Achats effectués</p>
            </div>
            <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; text-align: center;">
                <h4 style="margin: 0 0 5px 0; color: #721c24; font-size: 20px;">€{anniversary_data.get('total_value', 0):.0f}</h4>
                <p style="margin: 0; color: #721c24; font-size: 12px;">Valeur collection</p>
            </div>
        </div>
        
        <div style="background-color: #d1ecf1; border: 1px solid #b8daff; border-radius: 5px; padding: 20px; margin: 25px 0; text-align: center;">
            <h3 style="color: #0c5460; margin: 0 0 15px 0;">🎁 Cadeau Anniversaire</h3>
            <p style="margin: 0; color: #0c5460; font-size: 16px; font-weight: bold;">{anniversary_data.get('gift', 'Réduction spéciale de 15% sur votre prochain achat')}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{os.environ.get('FRONTEND_URL', 'https://topkit-workflow-fix.preview.emergentagent.com')}/anniversary-gift" 
               style="background-color: #ff6b35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 18px;">
                🎁 Récupérer mon cadeau
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Merci de faire partie de notre communauté !<br><strong>L'équipe {self.app_name}</strong></p>
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

    def send_weekly_newsletter(self, user_email: str, user_name: str, newsletter_data: Dict[str, Any]) -> bool:
        """Send weekly TopKit newsletter"""
        
        subject = f"📰 Cette semaine sur {self.app_name} - Newsletter #{newsletter_data.get('week_number', '1')}"
        
        text_body = f"""
Bonjour {user_name},

Voici les actualités de cette semaine sur {self.app_name} :

🔥 TENDANCES :
- {newsletter_data.get('trend1', 'Maillots rétro en forte demande')}
- {newsletter_data.get('trend2', 'Nouveaux maillots 2024/25 disponibles')}
- {newsletter_data.get('trend3', 'Éditions limitées très recherchées')}

📊 CHIFFRES DE LA SEMAINE :
- {newsletter_data.get('stat1', '150 nouveaux maillots ajoutés')}
- {newsletter_data.get('stat2', '89 ventes réalisées')}
- {newsletter_data.get('stat3', '234 nouveaux collectionneurs')}

⚽ ACTUALITÉS FOOT :
{newsletter_data.get('football_news', 'Les clubs préparent leurs nouveaux maillots pour la saison prochaine')}

À la semaine prochaine !

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Newsletter - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1a56db; margin: 0; font-size: 28px;">📰 Newsletter TopKit</h1>
            <p style="color: #666; margin: 5px 0;">Semaine #{newsletter_data.get('week_number', '1')} - {datetime.now().strftime('%d/%m/%Y')}</p>
        </div>
        
        <p>Bonjour <strong>{user_name}</strong>,</p>
        
        <p>Voici le récapitulatif de cette semaine sur {self.app_name} :</p>
        
        <div style="background-color: #ff6b35; color: white; padding: 20px; border-radius: 5px; margin: 25px 0;">
            <h3 style="margin: 0 0 15px 0;">🔥 TENDANCES DE LA SEMAINE</h3>
            <ul style="margin: 0; padding-left: 20px;">
                <li style="margin: 8px 0;">{newsletter_data.get('trend1', 'Maillots rétro en forte demande')}</li>
                <li style="margin: 8px 0;">{newsletter_data.get('trend2', 'Nouveaux maillots 2024/25 disponibles')}</li>
                <li style="margin: 8px 0;">{newsletter_data.get('trend3', 'Éditions limitées très recherchées')}</li>
            </ul>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">📊 Chiffres de la semaine :</h3>
        
        <div style="display: flex; flex-wrap: wrap; margin: 20px -10px;">
            <div style="flex: 1; min-width: 150px; margin: 10px; background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; text-align: center;">
                <h4 style="margin: 0 0 5px 0; color: #004085;">📦 Nouveautés</h4>
                <p style="margin: 0; color: #004085; font-size: 18px; font-weight: bold;">{newsletter_data.get('new_jerseys', '150')}</p>
            </div>
            <div style="flex: 1; min-width: 150px; margin: 10px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; text-align: center;">
                <h4 style="margin: 0 0 5px 0; color: #155724;">💰 Ventes</h4>
                <p style="margin: 0; color: #155724; font-size: 18px; font-weight: bold;">{newsletter_data.get('sales', '89')}</p>
            </div>
            <div style="flex: 1; min-width: 150px; margin: 10px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; text-align: center;">
                <h4 style="margin: 0 0 5px 0; color: #856404;">👥 Nouveaux membres</h4>
                <p style="margin: 0; color: #856404; font-size: 18px; font-weight: bold;">{newsletter_data.get('new_members', '234')}</p>
            </div>
        </div>
        
        <div style="background-color: #f8f9fa; border-radius: 5px; padding: 20px; margin: 25px 0;">
            <h3 style="color: #333; margin: 0 0 15px 0;">⚽ Actualités Football</h3>
            <p style="margin: 0; color: #666; font-style: italic;">{newsletter_data.get('football_news', 'Les clubs préparent leurs nouveaux maillots pour la saison prochaine.')}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://topkit-workflow-fix.preview.emergentagent.com")}}" 
               style="background-color: #1a56db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                🔍 Découvrir les nouveautés
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>À la semaine prochaine !<br><strong>L'équipe {self.app_name}</strong></p>
            <p style="font-size: 12px;">© 2024 {self.app_name}. Tous droits réservés.</p>
            <p style="font-size: 11px;"><a href="{{os.environ.get("FRONTEND_URL", "https://topkit-workflow-fix.preview.emergentagent.com")}}/unsubscribe" style="color: #999;">Se désinscrire</a></p>
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

# Initialize the marketing email service
try:
    marketing_email_service = MarketingEmailService()
    logger.info("Marketing email service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize marketing email service: {e}")
    marketing_email_service = None