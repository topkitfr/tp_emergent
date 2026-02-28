from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import logging

from database import db, client

# Import all routers
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
from routers.proxy import router as proxy_router app.include_router(proxy_router, prefix="/api")


ROOT_DIR = Path(__file__).parent
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Static files
app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include all routers
app.include_router(auth_router)
app.include_router(kits_router)
app.include_router(collections_router)
app.include_router(estimation_router)
app.include_router(reviews_router)
app.include_router(submissions_router)
app.include_router(wishlist_router)
app.include_router(entities_router)
app.include_router(uploads_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def create_indexes():
    await db.teams.create_index("team_id", unique=True)
    await db.teams.create_index("slug", unique=True)
    await db.teams.create_index("name")
    await db.leagues.create_index("league_id", unique=True)
    await db.leagues.create_index("slug", unique=True)
    await db.leagues.create_index("name")
    await db.brands.create_index("brand_id", unique=True)
    await db.brands.create_index("slug", unique=True)
    await db.brands.create_index("name")
    await db.players.create_index("player_id", unique=True)
    await db.players.create_index("slug", unique=True)
    await db.players.create_index("full_name")
    await db.master_kits.create_index("team_id")
    await db.master_kits.create_index("league_id")
    await db.master_kits.create_index("brand_id")
    await db.versions.create_index("main_player_id")
    logger.info("Entity indexes created")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
