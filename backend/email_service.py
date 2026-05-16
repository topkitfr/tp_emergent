# backend/email_service.py
"""
Service d'envoi d'emails via Resend.
Variables d'environnement requises sur Render :
  RESEND_API_KEY   = re_xxxxxxxxxxxxxxxx
  FROM_EMAIL       = noreply@topkit.fr   (ou onboarding@resend.dev en dev)
  FRONTEND_URL     = https://tp-emergent-1.onrender.com
"""
import os
import logging

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL     = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
FRONTEND_URL   = os.getenv("FRONTEND_URL", "https://tp-emergent-1.onrender.com")

# Import optionnel : ne plante pas si resend n'est pas installé
try:
    import resend as _resend
    _resend.api_key = RESEND_API_KEY
    _RESEND_AVAILABLE = True
except ImportError:
    _RESEND_AVAILABLE = False
    logger.warning("resend package non installé — emails désactivés")


# ─── Base ─────────────────────────────────────────────────────────────────────

async def send_email(to: str, subject: str, html: str) -> None:
    """Wrapper générique. Silencieux si clé absente ou package manquant."""
    if not _RESEND_AVAILABLE or not RESEND_API_KEY:
        logger.debug(f"[email] skipped (no key): {subject} → {to}")
        return
    try:
        _resend.Emails.send({
            "from":    f"Topkit <{FROM_EMAIL}>",
            "to":      [to],
            "subject": subject,
            "html":    html,
        })
        logger.info(f"[email] sent: {subject} → {to}")
    except Exception as e:
        logger.error(f"[email] error sending '{subject}' to {to}: {e}")


# ─── Templates ────────────────────────────────────────────────────────────────

_BASE_STYLE = """
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #0f0f0f; color: #e5e5e5; padding: 32px;
"""
_BTN_STYLE = (
    "display:inline-block;background:#6366f1;color:#ffffff;"
    "padding:12px 28px;border-radius:8px;text-decoration:none;"
    "font-weight:600;margin-top:16px;"
)


def _wrap(body: str) -> str:
    return f"""
    <div style="{_BASE_STYLE}">
      <div style="max-width:520px;margin:0 auto;">
        <h1 style="color:#6366f1;margin-bottom:4px;">Topkit</h1>
        <hr style="border:none;border-top:1px solid #333;margin-bottom:24px;">
        {body}
        <hr style="border:none;border-top:1px solid #333;margin-top:32px;">
        <p style="color:#555;font-size:12px;margin-top:8px;">
          Tu reçois cet email car tu as un compte sur
          <a href="{FRONTEND_URL}" style="color:#6366f1;">Topkit</a>.
        </p>
      </div>
    </div>
    """


async def send_welcome(to: str, name: str) -> None:
    html = _wrap(f"""
      <h2 style="margin-top:0;">Bienvenue sur Topkit, {name} ! 👋</h2>
      <p>Ton compte a bien été créé. Tu peux maintenant cataloguer ta collection
         de maillots, voter pour les soumissions de la communauté et suivre tes
         équipes préférées.</p>
      <a href="{FRONTEND_URL}" style="{_BTN_STYLE}">Accéder à Topkit</a>
    """)
    await send_email(to, "Bienvenue sur Topkit !", html)


async def send_password_reset(to: str, reset_token: str) -> None:
    url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    html = _wrap(f"""
      <h2 style="margin-top:0;">Réinitialisation de mot de passe 🔑</h2>
      <p>Nous avons reçu une demande de réinitialisation du mot de passe associé
         à ce compte.</p>
      <p>Clique sur le bouton ci-dessous. Ce lien est valable <strong>1 heure</strong>.</p>
      <a href="{url}" style="{_BTN_STYLE}">Réinitialiser mon mot de passe</a>
      <p style="margin-top:24px;color:#777;font-size:13px;">
        Si tu n'as pas demandé ce reset, ignore cet email — ton mot de passe
        reste inchangé.
      </p>
    """)
    await send_email(to, "Topkit — Réinitialise ton mot de passe", html)


async def send_submission_result(
    to: str,
    name: str,
    kit_name: str,
    approved: bool,
) -> None:
    status_label = "approuvée ✅" if approved else "refusée ❌"
    color        = "#22c55e" if approved else "#ef4444"
    msg = (
        "Elle est désormais visible dans la base de données Topkit."
        if approved
        else "Elle n'a pas obtenu suffisamment de votes positifs de la communauté."
    )
    html = _wrap(f"""
      <h2 style="margin-top:0;color:{color};">
        Soumission {status_label}
      </h2>
      <p>Bonjour {name},</p>
      <p>Ta soumission pour le maillot <strong>{kit_name}</strong>
         a été <strong>{status_label}</strong>.</p>
      <p>{msg}</p>
      <a href="{FRONTEND_URL}" style="{_BTN_STYLE}">Voir sur Topkit</a>
    """)
    subject = f"Topkit — Soumission {'approuvée' if approved else 'refusée'}"
    await send_email(to, subject, html)


async def send_report_result(
    to: str,
    name: str,
    target_label: str,
    target_name: str,
    approved: bool,
    report_type: str = "error",
) -> None:
    """Email pour résultat d'un signalement/correction."""
    if approved:
        action = "suppression" if report_type == "removal" else "correction"
        status_label = f"{action} approuvée ✅"
        color = "#22c55e"
        msg   = f"Ta demande de {action} sur le {target_label} « {target_name} » a bien été traitée."
    else:
        status_label = "signalement rejeté ❌"
        color = "#ef4444"
        msg   = f"Ton signalement sur le {target_label} « {target_name} » n'a pas été retenu par la communauté."
    html = _wrap(f"""
      <h2 style="margin-top:0;color:{color};">Signalement — {status_label}</h2>
      <p>Bonjour {name},</p>
      <p>{msg}</p>
      <a href="{FRONTEND_URL}" style="{_BTN_STYLE}">Voir sur Topkit</a>
    """)
    subject = f"Topkit — Signalement {'approuvé' if approved else 'rejeté'}"
    await send_email(to, subject, html)


async def send_email_verification(to: str, name: str, token: str) -> None:
    url = f"{FRONTEND_URL}/verify-email?token={token}"
    html = _wrap(f"""
      <h2 style="margin-top:0;">Confirme ton adresse email ✉️</h2>
      <p>Bonjour {name},</p>
      <p>Il ne reste qu'une étape : confirme ton adresse email pour activer toutes
         les fonctionnalités de ton compte Topkit.</p>
      <p>Ce lien est valable <strong>24 heures</strong>.</p>
      <a href="{url}" style="{_BTN_STYLE}">Confirmer mon email</a>
      <p style="margin-top:24px;color:#777;font-size:13px;">
        Si tu n'as pas créé de compte sur Topkit, ignore cet email.
      </p>
    """)
    await send_email(to, "Topkit — Confirme ton adresse email", html)


async def send_offer_received(
    to: str,
    seller_name: str,
    buyer_name: str,
    listing_url: str,
    offered_price: float | None = None,
) -> None:
    price_line = f"<p>Prix proposé : <strong>{offered_price} €</strong></p>" if offered_price else ""
    html = _wrap(f"""
      <h2 style="margin-top:0;">Nouvelle offre reçue 📬</h2>
      <p>Bonjour {seller_name},</p>
      <p><strong>{buyer_name}</strong> vient de faire une offre sur ton annonce.</p>
      {price_line}
      <p>Connecte-toi pour accepter ou refuser cette offre.</p>
      <a href="{listing_url}" style="{_BTN_STYLE}">Voir l'offre</a>
    """)
    await send_email(to, "Topkit — Tu as reçu une nouvelle offre", html)


async def send_offer_accepted(
    to: str,
    buyer_name: str,
    listing_url: str,
    offered_price: float | None = None,
) -> None:
    price_line = f" pour <strong>{offered_price} €</strong>" if offered_price else ""
    html = _wrap(f"""
      <h2 style="margin-top:0;color:#22c55e;">Offre acceptée ✅</h2>
      <p>Bonjour {buyer_name},</p>
      <p>Bonne nouvelle ! Ton offre{price_line} a été <strong>acceptée</strong> par le vendeur.</p>
      <p>Connecte-toi pour contacter le vendeur et finaliser la transaction.</p>
      <a href="{listing_url}" style="{_BTN_STYLE}">Voir l'annonce</a>
    """)
    await send_email(to, "Topkit — Ton offre a été acceptée !", html)


async def send_offer_refused(
    to: str,
    buyer_name: str,
    listing_url: str,
) -> None:
    html = _wrap(f"""
      <h2 style="margin-top:0;color:#ef4444;">Offre refusée ❌</h2>
      <p>Bonjour {buyer_name},</p>
      <p>Le vendeur n'a pas retenu ton offre cette fois-ci.</p>
      <p>Tu peux continuer à explorer le marketplace pour trouver d'autres maillots.</p>
      <a href="{FRONTEND_URL}/marketplace" style="{_BTN_STYLE}">Voir le marketplace</a>
    """)
    await send_email(to, "Topkit — Ton offre n'a pas été retenue", html)


async def send_email_changed(
    old_email: str,
    new_email: str,
    name: str,
) -> None:
    """M2 — Notification à l'ancienne adresse + confirmation à la nouvelle."""
    html_old = _wrap(f"""
      <h2 style="margin-top:0;color:#f59e0b;">Adresse email modifiée ⚠️</h2>
      <p>Bonjour {name},</p>
      <p>L'adresse email de ton compte Topkit vient d'être changée pour
         <strong>{new_email}</strong>.</p>
      <p>Si tu n'es pas à l'origine de cette modification, contacte-nous
         immédiatement en répondant à cet email.</p>
    """)
    await send_email(old_email, "Topkit — Ton adresse email a été modifiée", html_old)

    html_new = _wrap(f"""
      <h2 style="margin-top:0;">Nouvelle adresse confirmée ✅</h2>
      <p>Bonjour {name},</p>
      <p>Ton adresse email Topkit a bien été mise à jour vers <strong>{new_email}</strong>.
         Tu recevras désormais toutes les notifications à cette adresse.</p>
      <a href="{FRONTEND_URL}" style="{_BTN_STYLE}">Accéder à Topkit</a>
    """)
    await send_email(new_email, "Topkit — Bienvenue sur ta nouvelle adresse", html_new)


async def send_login_alert(to: str, name: str, ip: str) -> None:
    """M3 — Alerte de connexion (envoyée à chaque login email/password)."""
    html = _wrap(f"""
      <h2 style="margin-top:0;">Nouvelle connexion détectée 🔐</h2>
      <p>Bonjour {name},</p>
      <p>Une connexion à ton compte Topkit vient d'être effectuée.</p>
      <p style="color:#777;font-size:13px;">IP : {ip}</p>
      <p>Si ce n'est pas toi, change immédiatement ton mot de passe.</p>
      <a href="{FRONTEND_URL}/forgot-password" style="{_BTN_STYLE}">Changer mon mot de passe</a>
    """)
    await send_email(to, "Topkit — Nouvelle connexion à ton compte", html)


async def send_listing_cancelled_by_admin(to: str, name: str, kit_label: str) -> None:
    """M7 — Notification annulation d'annonce par un modérateur."""
    html = _wrap(f"""
      <h2 style="margin-top:0;color:#f59e0b;">Annonce retirée ⚠️</h2>
      <p>Bonjour {name},</p>
      <p>Ton annonce pour <strong>{kit_label}</strong> a été retirée par l'équipe de modération
         car elle ne respecte pas nos conditions d'utilisation.</p>
      <p>Si tu penses qu'il s'agit d'une erreur, contacte-nous en répondant à cet email.</p>
      <a href="{FRONTEND_URL}/marketplace" style="{_BTN_STYLE}">Voir le marketplace</a>
    """)
    await send_email(to, "Topkit — Ton annonce a été retirée", html)


async def send_account_banned(to: str, name: str) -> None:
    """M10 — Notification de bannissement."""
    html = _wrap(f"""
      <h2 style="margin-top:0;color:#ef4444;">Compte suspendu ❌</h2>
      <p>Bonjour {name},</p>
      <p>Ton compte Topkit a été suspendu suite à une violation de nos conditions
         d'utilisation.</p>
      <p>Si tu penses qu'il s'agit d'une erreur, tu peux contacter notre équipe
         en répondant à cet email.</p>
    """)
    await send_email(to, "Topkit — Ton compte a été suspendu", html)
