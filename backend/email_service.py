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
        
        # Create confirmation URL
        confirmation_url = f"https://topkit-admin.preview.emergentagent.com/verify-email?token={confirmation_token}"
        
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
            <a href="https://topkit-admin.preview.emergentagent.com/admin" 
               style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                🔧 Gérer la demande
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
        
        login_url = "https://topkit-admin.preview.emergentagent.com"
        
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

# Initialize the email service instance
try:
    gmail_service = GmailSMTPService()
    logger.info("Gmail SMTP service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gmail SMTP service: {e}")
    gmail_service = None