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
FREEBOX_BASE = "http://82.67.103.45"

CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000",
).split(",")


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
    """Proxy HTTPS (Render) → HTTP (Freebox NAS) pour éviter le Mixed Content.
    Supporte tous les types de médias :
      /api/images/master_kits/photos/abc.jpg
      /api/images/brands/logos/abc.jpg
      /api/images/teams/logos/abc.jpg
      /api/images/versions/photos/abc.jpg
      /api/images/players/photos/abc.jpg
      /api/images/users/photos/abc.jpg
      /api/images/leagues/logos/abc.jpg
      /api/images/sponsors/logos/abc.jpg
      # Legacy : juste le filename (anciens kits importés)
      /api/images/abc.jpg  → fallback master_kits/photos/
    """
    # Legacy : filename seul sans sous-dossier → fallback master_kits/photos
    if "/" not in filepath:
        filepath = f"master_kits/photos/{filepath}"

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
    except Exception:
        return Response(status_code=404)
