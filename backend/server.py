from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import logging
import time
from collections import defaultdict
from fastapi.responses import JSONResponse

from .database import db, client

from routers.auth import router as auth_router
from routers.kits import router as kits_router
from routers.collections import router as collections_router
from routers.estimation import router as estimation_router
from routers.reviews import router as reviews_router
from routers.submissions import router as submissions_router
from routers.wishlist import router as wishlist_router
from routers.entities import router as entities_router
from routers.uploads import router as uploads_router
from routers.admin import router as admin_router
from routers.proxy import router as proxy_router
from routers.notifications import router as notifications_router
from routers.users import router as users_router
from routers.user_lists import router as user_lists_router

# --- Debug PORT from environment ---------------------------------------------
PORT = os.environ.get("PORT")
print("DEBUG PORT FROM ENV:", PORT)
# -----------------------------------------------------------------------------


ROOT_DIR = Path(__file__).parent
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


# ─── CORS en PREMIER ──────────────────────────────────────────────────────────
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# ─── Rate Limiting (simple in-memory) ─────────────────────────────────────────
# Limite : 60 req/min par IP pour les routes /api/auth/*
# et 200 req/min par IP pour le reste
_rate_limit_store: dict[str, list[float]] = defaultdict(list)

RATE_LIMITS = {
    "/api/auth/login": (10, 60),      # 10 requêtes par minute
    "/api/auth/register": (5, 60),    # 5 requêtes par minute
    "/api/submissions": (30, 60),     # 30 soumissions par minute
    "/api/upload": (20, 60),          # 20 uploads par minute
}
DEFAULT_RATE_LIMIT = (200, 60)  # 200 req/min pour tout le reste


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path

    # Trouver la limite applicable
    limit, window = DEFAULT_RATE_LIMIT
    for prefix, (lim, win) in RATE_LIMITS.items():
        if path.startswith(prefix):
            limit, window = lim, win
            break

    key = f"{client_ip}:{path}"
    now = time.time()
    # Nettoyer les timestamps anciens
    _rate_limit_store[key] = [
        t for t in _rate_limit_store[key] if now - t < window
    ]

    if len(_rate_limit_store[key]) >= limit:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please slow down."},
            headers={"Retry-After": str(window)},
        )

    _rate_limit_store[key].append(now)
    return await call_next(request)


# ─── Security Headers + CORS sur erreurs 500 ─────────────────────────────────
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as exc:
        # Catch toutes les exceptions non gérées pour garantir les headers CORS
        origin = request.headers.get("origin", "")
        cors_headers = {}
        if origin in CORS_ORIGINS:
            cors_headers = {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
            }
        logger.error(f"Unhandled exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers=cors_headers,
        )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    try:
        del response.headers["server"]
    except KeyError:
        pass
    return response


app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(user_lists_router)
app.include_router(kits_router)
app.include_router(collections_router)
app.include_router(estimation_router)
app.include_router(reviews_router)
app.include_router(submissions_router)
app.include_router(wishlist_router)
app.include_router(entities_router)
app.include_router(uploads_router)
app.include_router(admin_router)
app.include_router(proxy_router, prefix="/api")
app.include_router(notifications_router)


@app.on_event("startup")
async def create_indexes():
    for collection, index_name in [
        ("teams", "team_id_1"),
        ("leagues", "league_id_1"),
        ("brands", "brand_id_1"),
        ("players", "player_id_1"),
        ("players", "slug_1"),
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

    # Index notifications
    await db.notifications.create_index("user_id")
    await db.notifications.create_index([("user_id", 1), ("read", 1)])
    await db.notifications.create_index("created_at")

    logger.info("Indexes created successfully")