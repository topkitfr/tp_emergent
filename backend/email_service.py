import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
import ssl
from dotenv import load_dotenv
from pathlib import Path

# Configure logging for email operations
logger = logging.getLogger(__name__)

class GmailSMTPService:
    def __init__(self):
        # Load environment variables
        env_path = Path(__file__).parent / '.env'
        load_dotenv(env_path)
        self.smtp_server = os.getenv("GMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
        self.username = os.getenv("GMAIL_USERNAME")
        self.app_password = os.getenv("GMAIL_APP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
        self.from_name = os.getenv("FROM_NAME", "TopKit")
        self.app_name = os.getenv("APP_NAME", "TopKit")
        
        # Validate required configuration
        self._validate_configuration()
        
        logger.info("Gmail SMTP service initialized successfully")
    
    def _validate_configuration(self):
        """Validate that all required configuration parameters are present"""
        required_vars = [
            ("GMAIL_USERNAME", self.username),
            ("GMAIL_APP_PASSWORD", self.app_password),
            ("FROM_EMAIL", self.from_email)
        ]
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required Gmail SMTP environment variables: {', '.join(missing_vars)}")
        
        logger.info("Gmail SMTP configuration validated successfully")

    def create_message(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> MIMEMultipart:
        """Create an email message with support for HTML content and multiple recipients"""
        
        message = MIMEMultipart("alternative" if html_body else "mixed")
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        if cc_emails:
            message["Cc"] = ", ".join(cc_emails)
        
        # Add plain text body
        text_part = MIMEText(body, "plain", "utf-8")
        message.attach(text_part)
        
        # Add HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)
        
        return message

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """Send an email using Gmail SMTP with comprehensive error handling"""
        
        try:
            # Create the email message
            message = self.create_message(to_email, subject, body, html_body, cc_emails, bcc_emails)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    self._add_attachment(message, file_path)
            
            # Prepare recipient list
            all_recipients = [to_email]
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            # Create secure SSL context
            context = ssl.create_default_context()
            
            # Establish SMTP connection and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)  # Enable TLS encryption
                server.login(self.username, self.app_password)
                server.sendmail(self.from_email, all_recipients, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Recipients refused: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"SMTP server disconnected: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False

    def _add_attachment(self, message: MIMEMultipart, file_path: str):
        """Add a file attachment to the email message"""
        try:
            with open(file_path, "rb") as attachment_file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment_file.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(file_path)}"
            )
            message.attach(part)
            
        except FileNotFoundError:
            logger.error(f"Attachment file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error adding attachment {file_path}: {e}")
            raise

    def send_user_confirmation_email(self, user_email: str, user_name: str, confirmation_token: str) -> bool:
        """Send user confirmation email with activation link"""
        
        subject = f"Confirmez votre compte - {self.app_name}"
        
        # Create confirmation URL using environment variable
        frontend_url = os.environ.get('FRONTEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
        confirmation_url = f"{frontend_url}/verify-email?token={confirmation_token}"
        
        # Plain text version
        text_body = f"""
Bonjour {user_name},

Merci de vous être inscrit(e) sur {self.app_name} ! 

Pour activer votre compte et commencer à explorer notre marketplace de maillots de football, veuillez cliquer sur le lien suivant :

{confirmation_url}

Ce lien est valide pendant 24 heures.

Si vous n'avez pas créé de compte sur {self.app_name}, vous pouvez ignorer cet email.

Sportivement,
L'équipe {self.app_name}
"""
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmation de compte - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1a56db; margin: 0; font-size: 28px;">⚽ {self.app_name}</h1>
            <p style="color: #666; margin: 5px 0;">Marketplace de maillots de football</p>
        </div>
        
        <h2 style="color: #333; margin-bottom: 20px;">Bienvenue, {user_name} !</h2>
        
        <p>Merci de vous être inscrit(e) sur <strong>{self.app_name}</strong> ! 🎉</p>
        
        <p>Pour activer votre compte et commencer à explorer notre marketplace de maillots de football, veuillez cliquer sur le bouton ci-dessous :</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{confirmation_url}" 
               style="background-color: #1a56db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                ✅ Confirmer mon compte
            </a>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0; font-size: 14px;"><strong>Important :</strong> Ce lien est valide pendant 24 heures seulement.</p>
        </div>
        
        <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
        <p style="word-break: break-all; background-color: #f1f1f1; padding: 10px; border-radius: 3px; font-family: monospace; font-size: 12px;">
            {confirmation_url}
        </p>
        
        <p style="color: #666; font-size: 14px;">Si vous n'avez pas créé de compte sur {self.app_name}, vous pouvez ignorer cet email.</p>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Sportivement,<br><strong>L'équipe {self.app_name}</strong></p>
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

    def send_beta_access_notification(self, admin_email: str, request_data: Dict[str, Any]) -> bool:
        """Send notification to admin about new beta access request"""
        
        subject = f"🔔 Nouvelle demande d'accès beta - {self.app_name}"
        
        # Plain text version
        text_body = f"""
Nouvelle demande d'accès à la beta privée !

Détails de la demande :
- Email : {request_data.get('email', 'N/A')}
- Prénom : {request_data.get('first_name', 'N/A')}
- Nom : {request_data.get('last_name', 'N/A')}
- Message : {request_data.get('message', 'Aucun message')}
- Date de demande : {datetime.now().strftime('%d/%m/%Y à %H:%M')}
- ID de demande : {request_data.get('request_id', 'N/A')}

Connectez-vous à l'admin panel pour gérer cette demande.

{self.app_name} Admin System
"""
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nouvelle demande d'accès beta - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #dc3545; margin: 0; font-size: 24px;">🔔 Nouvelle demande d'accès beta</h1>
            <p style="color: #666; margin: 5px 0;">{self.app_name} Admin Notification</p>
        </div>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; color: #856404;"><strong>⚠️ Action requise :</strong> Une nouvelle personne souhaite accéder à la beta privée.</p>
        </div>
        
        <h3 style="color: #333; margin-bottom: 15px;">📋 Détails de la demande :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Email</td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{request_data.get('email', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Prénom</td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{request_data.get('first_name', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Nom</td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{request_data.get('last_name', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Date de demande</td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{datetime.now().strftime('%d/%m/%Y à %H:%M')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">ID de demande</td>
                <td style="padding: 10px; border: 1px solid #dee2e6;">{request_data.get('request_id', 'N/A')}</td>
            </tr>
        </table>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4 style="margin: 0 0 10px 0; color: #333;">💬 Message du demandeur :</h4>
            <p style="margin: 0; font-style: italic; color: #666;">
                "{request_data.get('message', 'Aucun message fourni')}"
            </p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://mongodb-routing.preview.emergentagent.com")}}/#beta-requests" 
               style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; margin-right: 10px;">
                ✅ Gérer la demande
            </a>
            <a href="{{os.environ.get("FRONTEND_URL", "https://mongodb-routing.preview.emergentagent.com")}}/admin" 
               style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                🔧 Panel Admin
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p><strong>{self.app_name} Admin System</strong></p>
            <p style="font-size: 12px;">Notification automatique - Ne pas répondre à cet email</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(
            to_email=admin_email,
            subject=subject,
            body=text_body,
            html_body=html_body
        )

    def send_beta_access_approved_email(self, user_email: str, user_name: str, temp_password: Optional[str] = None) -> bool:
        """Send email when beta access is approved"""
        
        subject = f"🎉 Accès accordé à {self.app_name} !"
        
        frontend_url = os.environ.get('FRONTEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
        login_url = frontend_url
        
        # Plain text version
        text_body = f"""
Félicitations {user_name} !

Votre demande d'accès à la beta privée de {self.app_name} a été approuvée ! 🎉

Vous pouvez maintenant accéder à notre marketplace de maillots de football :
{login_url}

{"Votre mot de passe temporaire : " + temp_password if temp_password else "Utilisez vos identifiants habituels pour vous connecter."}

Que pouvez-vous faire sur {self.app_name} :
- Explorer notre catalogue de maillots
- Ajouter des maillots à votre collection
- Acheter et vendre des maillots
- Echanger avec d'autres collectionneurs

Bienvenue dans la communauté {self.app_name} !

Sportivement,
L'équipe {self.app_name}
"""
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accès accordé - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #28a745; margin: 0; font-size: 28px;">🎉 Félicitations !</h1>
            <p style="color: #666; margin: 5px 0;">{self.app_name} - Accès accordé</p>
        </div>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: center;">
            <h2 style="color: #155724; margin: 0 0 10px 0;">Votre accès à la beta a été approuvé !</h2>
            <p style="margin: 0; color: #155724;">Bienvenue dans la communauté {self.app_name}, {user_name} !</p>
        </div>
        
        <p>Vous pouvez maintenant accéder à notre marketplace exclusif de maillots de football ⚽</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{login_url}" 
               style="background-color: #1a56db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 18px;">
                🚀 Accéder à {self.app_name}
            </a>
        </div>
        
        {f'<div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;"><p style="margin: 0; color: #856404;"><strong>🔑 Mot de passe temporaire :</strong> {temp_password}</p><p style="margin: 10px 0 0 0; font-size: 14px; color: #856404;">Nous vous recommandons de changer ce mot de passe après votre première connexion.</p></div>' if temp_password else ''}
        
        <h3 style="color: #333; margin: 30px 0 15px 0;">🎯 Que pouvez-vous faire sur {self.app_name} :</h3>
        
        <ul style="padding-left: 20px; color: #555;">
            <li style="margin: 10px 0;">🔍 <strong>Explorer</strong> notre catalogue de maillots authentiques</li>
            <li style="margin: 10px 0;">📚 <strong>Créer</strong> votre collection personnelle</li>
            <li style="margin: 10px 0;">💰 <strong>Acheter et vendre</strong> des maillots rares</li>
            <li style="margin: 10px 0;">💬 <strong>Échanger</strong> avec d'autres collectionneurs</li>
            <li style="margin: 10px 0;">📈 <strong>Suivre</strong> les tendances du marché</li>
        </ul>
        
        <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 30px 0;">
            <p style="margin: 0; color: #004085;"><strong>💡 Conseil :</strong> Commencez par explorer le catalogue et ajouter vos maillots préférés à votre liste de souhaits !</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Sportivement,<br><strong>L'équipe {self.app_name}</strong></p>
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
    # SYSTÈME DE MAILLOTS - EMAILS
    # ========================================

    def send_jersey_submitted_confirmation(self, user_email: str, user_name: str, jersey_data: Dict[str, Any]) -> bool:
        """Send confirmation email when user submits a new jersey"""
        
        subject = f"📤 Maillot soumis avec succès - {jersey_data.get('team', 'Équipe')} {jersey_data.get('season', '')}"
        
        jersey_name = f"{jersey_data.get('team', 'Équipe')} {jersey_data.get('season', '')}"
        if jersey_data.get('player'):
            jersey_name += f" - {jersey_data.get('player')}"
        
        text_body = f"""
Bonjour {user_name},

Votre maillot "{jersey_name}" a été soumis avec succès ! 📤

Détails du maillot soumis :
- Équipe : {jersey_data.get('team', 'N/A')}
- Saison : {jersey_data.get('season', 'N/A')}
- Joueur : {jersey_data.get('player', 'Sans nom')}
- Taille : {jersey_data.get('size', 'N/A')}
- État : {jersey_data.get('condition', 'N/A')}

Notre équipe de modération examine maintenant votre soumission. 
Temps d'attente habituel : 24-48 heures.

Vous recevrez un email dès que votre maillot sera approuvé !

Sportivement,
L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maillot soumis - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1a56db; margin: 0; font-size: 28px;">📤 Maillot Soumis</h1>
            <p style="color: #666; margin: 5px 0;">Votre soumission a été reçue avec succès</p>
        </div>
        
        <div style="background-color: #d1ecf1; border: 1px solid #b8daff; border-radius: 5px; padding: 20px; margin: 20px 0;">
            <h2 style="color: #0c5460; margin: 0 0 15px 0;">{jersey_name}</h2>
            <p style="margin: 0; color: #0c5460;">✅ Soumission reçue et en cours d'examen</p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">📋 Détails de votre maillot :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Équipe</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('team', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Saison</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('season', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Joueur</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('player', 'Sans nom')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Taille</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('size', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">État</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('condition', 'N/A')}</td>
            </tr>
        </table>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #856404;">⏱️ Temps d'attente habituel</h4>
            <p style="margin: 0; color: #856404;">Notre équipe examine votre soumission sous <strong>24-48 heures</strong>.</p>
        </div>
        
        <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #004085;">🔍 Processus de modération</h4>
            <p style="margin: 0; color: #004085;">Nos modérateurs vérifient l'authenticité, la qualité des photos et les informations du maillot.</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <p style="margin: 0; color: #666;">Vous recevrez un email dès que votre maillot sera approuvé ! 📧</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Sportivement,<br><strong>L'équipe {self.app_name}</strong></p>
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

    def send_jersey_submitted_admin_notification(self, admin_email: str, jersey_data: Dict[str, Any], user_data: Dict[str, Any]) -> bool:
        """Send notification to admin when a new jersey is submitted for approval"""
        
        jersey_name = f"{jersey_data.get('team', 'Équipe')} {jersey_data.get('season', '')}"
        if jersey_data.get('player'):
            jersey_name += f" - {jersey_data.get('player')}"
        
        subject = f"🔔 Nouveau maillot à approuver : {jersey_name}"
        
        text_body = f"""
Nouveau maillot soumis pour approbation !

Maillot : {jersey_name}
Soumis par : {user_data.get('name', 'Utilisateur')} ({user_data.get('email', 'N/A')})

Détails :
- Équipe : {jersey_data.get('team', 'N/A')}
- Saison : {jersey_data.get('season', 'N/A')}
- Joueur : {jersey_data.get('player', 'Sans nom')}
- Taille : {jersey_data.get('size', 'N/A')}
- État : {jersey_data.get('condition', 'N/A')}
- Description : {jersey_data.get('description', 'Aucune description')}

ID du maillot : {jersey_data.get('id', 'N/A')}

Connectez-vous au panel admin pour approuver ou rejeter cette soumission.

{self.app_name} Admin System
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nouveau maillot à approuver - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #dc3545; margin: 0; font-size: 24px;">🔔 Nouveau Maillot à Approuver</h1>
            <p style="color: #666; margin: 5px 0;">{self.app_name} - Modération</p>
        </div>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
            <p style="margin: 0; color: #856404;"><strong>⚠️ Action requise :</strong> Un nouveau maillot attend votre approbation.</p>
        </div>
        
        <h2 style="color: #333; margin: 25px 0 15px 0;">👕 {jersey_name}</h2>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0; color: #666;"><strong>👤 Soumis par :</strong> {user_data.get('name', 'Utilisateur')} ({user_data.get('email', 'N/A')})</p>
            <p style="margin: 5px 0 0 0; color: #666;"><strong>🆔 ID Maillot :</strong> {jersey_data.get('id', 'N/A')}</p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">📋 Détails du maillot :</h3>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold; width: 30%;">Équipe</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('team', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Saison</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('season', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Joueur</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('player', 'Sans nom')}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">Taille</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('size', 'N/A')}</td>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 12px; border: 1px solid #dee2e6; font-weight: bold;">État</td>
                <td style="padding: 12px; border: 1px solid #dee2e6;">{jersey_data.get('condition', 'N/A')}</td>
            </tr>
        </table>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4 style="margin: 0 0 10px 0; color: #333;">💬 Description :</h4>
            <p style="margin: 0; color: #666; font-style: italic;">{jersey_data.get('description', 'Aucune description fournie')}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://mongodb-routing.preview.emergentagent.com")}}/admin" 
               style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; margin-right: 10px;">
                ✅ Approuver
            </a>
            <a href="{{os.environ.get("FRONTEND_URL", "https://mongodb-routing.preview.emergentagent.com")}}/admin" 
               style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                ❌ Rejeter
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p><strong>{self.app_name} Admin System</strong></p>
            <p style="font-size: 12px;">Notification automatique - Ne pas répondre à cet email</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(
            to_email=admin_email,
            subject=subject,
            body=text_body,
            html_body=html_body
        )

    def send_jersey_approved_notification(self, user_email: str, user_name: str, jersey_data: Dict[str, Any]) -> bool:
        """Send notification when a jersey is approved"""
        
        jersey_name = f"{jersey_data.get('team', 'Équipe')} {jersey_data.get('season', '')}"
        if jersey_data.get('player'):
            jersey_name += f" - {jersey_data.get('player')}"
        
        subject = f"✅ Maillot approuvé : {jersey_name}"
        
        text_body = f"""
Félicitations {user_name} !

Votre maillot "{jersey_name}" a été approuvé par notre équipe ! ✅

Votre maillot fait maintenant partie du catalogue officiel {self.app_name}.

Prochaines étapes :
1. Ajoutez-le à votre collection personnelle
2. Mettez-le en vente si vous le souhaitez
3. Partagez-le avec la communauté

Merci de contribuer à enrichir notre catalogue !

Sportivement,
L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maillot approuvé - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #28a745; margin: 0; font-size: 28px;">✅ Maillot Approuvé !</h1>
            <p style="color: #666; margin: 5px 0;">Félicitations, votre contribution est validée</p>
        </div>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 20px; margin: 20px 0; text-align: center;">
            <h2 style="color: #155724; margin: 0 0 10px 0;">{jersey_name}</h2>
            <p style="margin: 0; color: #155724;">🎉 Approuvé et ajouté au catalogue officiel !</p>
        </div>
        
        <p>Bravo {user_name} ! Votre maillot fait maintenant partie du catalogue officiel {self.app_name}.</p>
        
        <h3 style="color: #333; margin: 30px 0 15px 0;">🚀 Prochaines étapes :</h3>
        
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <div style="margin-bottom: 15px;">
                <strong style="color: #1a56db;">1️⃣ Ajoutez à votre collection</strong>
                <p style="margin: 5px 0 0 0; color: #666;">Marquez ce maillot comme "possédé" dans votre collection personnelle</p>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong style="color: #1a56db;">2️⃣ Mettez-le en vente</strong>
                <p style="margin: 5px 0 0 0; color: #666;">Si vous souhaitez le vendre, créez une annonce sur le marketplace</p>
            </div>
            
            <div style="margin-bottom: 0;">
                <strong style="color: #1a56db;">3️⃣ Partagez avec la communauté</strong>
                <p style="margin: 5px 0 0 0; color: #666;">Les autres collectionneurs peuvent maintenant découvrir ce maillot</p>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://mongodb-routing.preview.emergentagent.com")}}" 
               style="background-color: #1a56db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                🔍 Voir mon maillot
            </a>
        </div>
        
        <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <p style="margin: 0; color: #004085;"><strong>💡 Le saviez-vous ?</strong> Chaque maillot approuvé enrichit notre base de données et aide la communauté à identifier des maillots authentiques.</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>Merci de contribuer à {self.app_name} !<br><strong>L'équipe {self.app_name}</strong></p>
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

    def send_jersey_rejected_notification(self, user_email: str, user_name: str, jersey_data: Dict[str, Any], rejection_reason: str) -> bool:
        """Send notification when a jersey is rejected"""
        
        jersey_name = f"{jersey_data.get('team', 'Équipe')} {jersey_data.get('season', '')}"
        if jersey_data.get('player'):
            jersey_name += f" - {jersey_data.get('player')}"
        
        subject = f"⚠️ Maillot à modifier : {jersey_name}"
        
        text_body = f"""
Bonjour {user_name},

Votre soumission "{jersey_name}" nécessite quelques modifications avant d'être approuvée.

Raison : {rejection_reason}

Recommandations :
- Vérifiez la qualité des photos (haute résolution, bien éclairées)
- Assurez-vous que toutes les informations sont correctes
- Ajoutez plus de détails si nécessaire

Vous pouvez re-soumettre votre maillot une fois les modifications effectuées.

Notre guide de soumission : {{os.environ.get("FRONTEND_URL", "https://mongodb-routing.preview.emergentagent.com")}}/guide

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maillot à modifier - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #ffc107; margin: 0; font-size: 28px;">⚠️ Modifications requises</h1>
            <p style="color: #666; margin: 5px 0;">Votre soumission nécessite quelques ajustements</p>
        </div>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 20px; margin: 20px 0;">
            <h2 style="color: #856404; margin: 0 0 10px 0;">{jersey_name}</h2>
            <p style="margin: 0; color: #856404;">📝 Modifications nécessaires avant approbation</p>
        </div>
        
        <h3 style="color: #333; margin: 25px 0 15px 0;">💬 Commentaire de notre équipe :</h3>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
            <p style="margin: 0; color: #333; font-style: italic;">"{rejection_reason}"</p>
        </div>
        
        <h3 style="color: #333; margin: 30px 0 15px 0;">💡 Recommandations :</h3>
        
        <ul style="padding-left: 20px; color: #555;">
            <li style="margin: 10px 0;"><strong>📸 Photos :</strong> Utilisez des images haute résolution, bien éclairées, sans flou</li>
            <li style="margin: 10px 0;"><strong>ℹ️ Informations :</strong> Vérifiez que l'équipe, la saison et le joueur sont corrects</li>
            <li style="margin: 10px 0;"><strong>📝 Description :</strong> Ajoutez plus de détails sur l'état et l'authenticité</li>
            <li style="margin: 10px 0;"><strong>🏷️ Étiquettes :</strong> Incluez des photos d'étiquettes officielles si possible</li>
        </ul>
        
        <div style="background-color: #e7f3ff; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <h4 style="margin: 0 0 10px 0; color: #004085;">🔄 Re-soumission</h4>
            <p style="margin: 0; color: #004085;">Une fois les modifications effectuées, vous pouvez soumettre à nouveau votre maillot.</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{os.environ.get("FRONTEND_URL", "https://mongodb-routing.preview.emergentagent.com")}}/guide" 
               style="background-color: #1a56db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; margin-right: 10px;">
                📖 Guide de soumission
            </a>
            <a href="{{os.environ.get("FRONTEND_URL", "https://mongodb-routing.preview.emergentagent.com")}}" 
               style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                🔄 Re-soumettre
            </a>
        </div>
        
        <div style="background-color: #d1ecf1; border: 1px solid #b8daff; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <p style="margin: 0; color: #0c5460;"><strong>💪 Ne vous découragez pas !</strong> Notre équipe vous aide à améliorer votre soumission pour qu'elle soit parfaite.</p>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p>L'équipe de modération<br><strong>{self.app_name}</strong></p>
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
    # SÉCURITÉ ET COMPTE - EMAILS
    # ========================================

    def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        
        subject = f"🔑 Réinitialisation de votre mot de passe - {self.app_name}"
        
        frontend_url = os.environ.get('FRONTEND_URL', 'https://mongodb-routing.preview.emergentagent.com')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        text_body = f"""
Bonjour {user_name},

Vous avez demandé la réinitialisation de votre mot de passe pour {self.app_name}.

Cliquez sur le lien suivant pour créer un nouveau mot de passe :
{reset_url}

Ce lien est valide pendant 24 heures seulement.

Si vous n'avez pas demandé cette réinitialisation, ignorez cet email et votre mot de passe restera inchangé.

L'équipe {self.app_name}
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Réinitialisation mot de passe - {self.app_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #dc3545; margin: 0; font-size: 28px;">🔑 Réinitialisation</h1>
            <p style="color: #666; margin: 5px 0;">Mot de passe - {self.app_name}</p>
        </div>
        
        <p>Bonjour <strong>{user_name}</strong>,</p>
        
        <p>Vous avez demandé la réinitialisation de votre mot de passe pour {self.app_name}.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" 
               style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 16px;">
                🔐 Réinitialiser mon mot de passe
            </a>
        </div>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <p style="margin: 0; color: #856404;"><strong>⏰ Important :</strong> Ce lien est valide pendant <strong>24 heures seulement</strong>.</p>
        </div>
        
        <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
        <p style="word-break: break-all; background-color: #f1f1f1; padding: 10px; border-radius: 3px; font-family: monospace; font-size: 12px;">
            {reset_url}
        </p>
        
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 15px; margin: 25px 0;">
            <p style="margin: 0; color: #721c24;"><strong>🛡️ Sécurité :</strong> Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. Votre mot de passe actuel restera inchangé.</p>
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

# Initialize the email service instance
try:
    gmail_service = GmailSMTPService()
    logger.info("Gmail SMTP service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gmail SMTP service: {e}")
    gmail_service = None