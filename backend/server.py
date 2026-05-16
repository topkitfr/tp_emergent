from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import logging
import time
import asyncio
from collections import defaultdict

# ─── Garde-fous configuration (avant toute initialisation) ──────────────────────
_ENV = os.environ.get("ENVIRONMENT", "production").lower()
_IS_PROD = _ENV == "production"
_RECEIVER_SECRET = os.environ.get("RECEIVER_SECRET", "")
if _IS_PROD and _RECEIVER_SECRET in ("", "changeme"):
    raise RuntimeError(
        "RECEIVER_SECRET non configuré (vide ou == 'changeme') en production. "
        "Définissez une valeur secrète robuste dans .env.backend."
    )

from .database import db, client

from .routers.beta import router as beta_router
from .routers.auth import router as auth_router
from .routers.master_kits import router as master_kits_router
from .routers.versions import router as versions_router
from .routers.kits_by_entity import router as kits_by_entity_router
from .routers.collections import router as collections_router
from .routers.estimation import router as estimation_router
from .routers.reviews import router as reviews_router
from .routers.submissions import router as submissions_router
from .routers.wishlist import router as wishlist_router
from .routers.teams import router as teams_router
from .routers.leagues import router as leagues_router
from .routers.brands import router as brands_router
from .routers.sponsors import router as sponsors_router
from .routers.players import router as players_router
from .routers.entity_workflow import router as entity_workflow_router
from .routers.uploads import router as uploads_router
from .routers.admin import router as admin_router
from .routers.admin_panel import router as admin_panel_router
from .routers.proxy import router as proxy_router
from .routers.notifications import router as notifications_router
from .routers.users import router as users_router
from .routers.user_lists import router as user_lists_router
from .routers.players_scoring import router as players_scoring_router
from .routers.awards import router as awards_router
from .routers.marketplace import router as marketplace_router
from .middleware import maintenance_middleware


ROOT_DIR = Path(__file__).parent
MEDIA_ROOT = os.environ.get("MEDIA_ROOT")
if MEDIA_ROOT:
    UPLOAD_DIR = Path(MEDIA_ROOT)
else:
    UPLOAD_DIR = ROOT_DIR / "uploads"
    UPLOAD_DIR.mkdir(exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# topkit.app + api.topkit.app sont les origines de production
# Les origins Render restent pour les previews/CI
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    ",".join([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://topkit.app",
        "https://www.topkit.app",
    ])
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

app.middleware("http")(maintenance_middleware)

_rate_limit_store: dict[str, list[float]] = defaultdict(list)

RATE_LIMITS = {
    "/api/auth/login":            (10, 60),
    "/api/auth/register":         (5,  60),
    "/api/auth/forgot-password":  (3,  60),
    "/api/auth/reset-password":   (5,  60),
    "/api/submissions":           (30, 60),
    "/api/upload":                (20, 60),
    "/api/reports":               (10, 60),
}
# 500 req/min par IP réelle et par path — suffisant pour usage normal, protège quand même
DEFAULT_RATE_LIMIT = (500, 60)


def _get_client_ip(request: Request) -> str:
    """
    Récupère la vraie IP du client en tenant compte du reverse proxy nginx.
    X-Forwarded-For peut contenir plusieurs IPs séparées par virgule,
    on prend la première (la plus proche du client réel).
    """
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


def _cors_headers_for(request: Request) -> dict:
    """Retourne les headers CORS appropriés selon l'origine de la requête."""
    origin = request.headers.get("origin", "")
    if origin in CORS_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
        }
    # Fallback : si pas d'Origin header (certains proxies le strippent),
    # on autorise topkit.app par défaut pour ne pas bloquer les legit requests
    return {
        "Access-Control-Allow-Origin": "https://topkit.app",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
    }


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = _get_client_ip(request)
    path = request.url.path
    limit, window = DEFAULT_RATE_LIMIT
    for prefix, (lim, win) in RATE_LIMITS.items():
        if path.startswith(prefix):
            limit, window = lim, win
            break
    key = f"{client_ip}:{path}"
    now = time.time()
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < window]
    if len(_rate_limit_store[key]) >= limit:
        logger.warning(f"Rate limit atteint: {client_ip} sur {path}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please slow down."},
            headers={"Retry-After": str(window)},
        )
    _rate_limit_store[key].append(now)
    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    try:
        del response.headers["server"]
    except KeyError:
        pass
    return response


app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# ─── Routers ────────────────────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(user_lists_router)
app.include_router(master_kits_router)
app.include_router(versions_router)
app.include_router(kits_by_entity_router)
app.include_router(collections_router)
app.include_router(estimation_router)
app.include_router(reviews_router)
app.include_router(submissions_router)
app.include_router(wishlist_router)
app.include_router(teams_router)
app.include_router(leagues_router)
app.include_router(brands_router)
app.include_router(sponsors_router)
app.include_router(players_router)
app.include_router(entity_workflow_router)
app.include_router(uploads_router)
app.include_router(admin_router)
app.include_router(admin_panel_router)
app.include_router(proxy_router, prefix="/api")
app.include_router(notifications_router)
app.include_router(beta_router)
app.include_router(players_scoring_router)
app.include_router(awards_router)
app.include_router(marketplace_router)


async def _purge_rate_limit_store():
    """Supprime toutes les 5 min les clés expirées du store rate-limit."""
    while True:
        await asyncio.sleep(300)
        now = time.time()
        max_window = max(w for _, w in RATE_LIMITS.values()) if RATE_LIMITS else DEFAULT_RATE_LIMIT[1]
        stale = [k for k, ts in _rate_limit_store.items() if not any(now - t < max_window for t in ts)]
        for k in stale:
            del _rate_limit_store[k]
        if stale:
            logger.info(f"Rate-limit store purgé : {len(stale)} clés supprimées")


@app.on_event("startup")
async def create_indexes():
    if _ENV != "test":
        asyncio.create_task(_purge_rate_limit_store())
    for collection, index_name in [
        ("teams", "team_id_1"),
        ("leagues", "league_id_1"),
        ("brands", "brand_id_1"),
        ("players", "player_id_1"),
        ("players", "slug_1"),
        # Cleanup Vague 3 — indexes API-Football abandonnés
        ("teams", "apifootball_team_id_1"),
        ("leagues", "apifootball_league_id_1"),
    ]:
        try:
            await db[collection].drop_index(index_name)
            logger.info(f"Index {index_name} supprime sur {collection}")
        except Exception:
            pass

    await db.teams.create_index("team_id", unique=True, sparse=True)
    await db.teams.create_index("slug", unique=True)
    await db.teams.create_index("name")
    await db.leagues.create_index("league_id", unique=True, sparse=True)
    await db.leagues.create_index("slug", unique=True)
    await db.leagues.create_index("name")
    await db.brands.create_index("brand_id", unique=True, sparse=True)
    await db.brands.create_index("slug", unique=True)
    await db.brands.create_index("name")
    await db.players.create_index("player_id", unique=True, sparse=True)
    await db.players.create_index("slug", unique=True)
    await db.players.create_index("full_name")
    # Index awards
    await db.awards.create_index("award_id", unique=True, sparse=True)
    await db.awards.create_index("name")

    await db.notifications.create_index("user_id")
    await db.notifications.create_index([("user_id", 1), ("read", 1)])
    await db.notifications.create_index("created_at")
    await db.submissions.create_index([("submitted_by", 1), ("submission_type", 1), ("created_at", 1)])
    await db.users.create_index("is_banned")
    await db.users.create_index("role")
    await db.password_resets.create_index("token", unique=True)
    await db.password_resets.create_index("email")
    await db.password_resets.create_index("user_id")
    await db.password_resets.create_index("expires_at")
    await db.user_sessions.create_index("session_token", unique=True, sparse=True)
    await db.user_sessions.create_index("user_id")
    await db.user_sessions.create_index("expires_at")
    await db.listings.create_index("listing_id", unique=True, sparse=True)
    await db.listings.create_index([("status", 1), ("created_at", -1)])
    await db.listings.create_index("user_id")
    await db.listings.create_index("version_id")
    await db.offers.create_index("offer_id", unique=True, sparse=True)
    await db.offers.create_index([("listing_id", 1), ("status", 1)])
    await db.offers.create_index("offerer_id")
    await db.email_verifications.create_index("token", unique=True, sparse=True)
    await db.email_verifications.create_index("user_id")
    await db.email_verifications.create_index("expires_at")
    await db.reports.create_index([("reported_by", 1), ("target_id", 1), ("status", 1)])
    await db.reports.create_index("status")
    await db.reports.create_index("created_at")

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    deleted_sessions = await db.user_sessions.delete_many({"expires_at": {"$lt": now_iso}})
    deleted_resets   = await db.password_resets.delete_many({"expires_at": {"$lt": now_iso}})
    logger.info(
        f"Startup cleanup: {deleted_sessions.deleted_count} sessions expirées, "
        f"{deleted_resets.deleted_count} reset tokens expirés supprimés"
    )
    logger.info("Indexes created successfully")
