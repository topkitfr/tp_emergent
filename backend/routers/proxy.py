import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from urllib.parse import urlparse
import os

router = APIRouter()

ALLOWED_DOMAINS = [
    "cdn.footballkitarchive.com",
    "upload.wikimedia.org",
    "i.imgur.com",
]

# IP publique Freebox — racine des médias
FREEBOX_BASE = os.getenv("FREEBOX_BASE_URL", "http://82.67.103.45")

CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,https://tp-emergent.onrender.com,https://tp-emergent-1.onrender.com",
).split(",")

# Mapping préfixe filename → sous-dossier Freebox (legacy : filename seul en base)
LEGACY_PREFIX_MAP = {
    "version_": "versions/photos",
    "ver_":     "versions/photos",
    "kit_":     "master_kits/photos",
    "brand_":   "brands/logos",
    "team_":    "teams/logos",
    "league_":  "leagues/logos",
    "sponsor_": "sponsors/logos",
    "player_":  "players/photos",
    "user_":    "users/photos",
}


def _resolve_legacy_filepath(filename: str) -> str:
    """Déduit le sous-dossier Freebox depuis le préfixe du filename."""
    for prefix, folder in LEGACY_PREFIX_MAP.items():
        if filename.startswith(prefix):
            return f"{folder}/{filename}"
    # fallback générique
    return f"master_kits/photos/{filename}"


def get_cors_headers(request: Request) -> dict:
    origin = request.headers.get("origin", "")
    allowed = origin if origin in CORS_ORIGINS else (CORS_ORIGINS[0] if CORS_ORIGINS else "*")
    return {
        "Access-Control-Allow-Origin": allowed,
        "Access-Control-Allow-Credentials": "true",
        "Cross-Origin-Resource-Policy": "cross-origin",
        "Cache-Control": "public, max-age=86400",
    }


@router.get("/image-proxy")
async def image_proxy(url: str, request: Request):
    domain = urlparse(url).netloc
    if not any(domain.endswith(d) for d in ALLOWED_DOMAINS):
        raise HTTPException(status_code=403, detail=f"Domain not allowed: {domain}")
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        return StreamingResponse(
            content=iter([resp.content]),
            media_type=resp.headers.get("content-type", "image/jpeg"),
            headers=get_cors_headers(request),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch image: {e}")


@router.get("/images/{filepath:path}")
async def freebox_image_proxy(filepath: str, request: Request):
    """
    Proxy HTTPS (Render) → HTTP (Freebox NAS) pour éviter le Mixed Content.
    Cas gérés :
      - chemin complet : versions/photos/abc.webp
      - filename seul (legacy) : version_abc.webp → déduit versions/photos/
    """
    if "/" not in filepath:
        filepath = _resolve_legacy_filepath(filepath)

    url = f"{FREEBOX_BASE}/{filepath}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return Response(status_code=404)
            return StreamingResponse(
                iter([r.content]),
                media_type=r.headers.get("content-type", "image/jpeg"),
                headers=get_cors_headers(request),
            )
    except httpx.TimeoutException:
        return Response(status_code=504)
    except Exception:
        return Response(status_code=502)
