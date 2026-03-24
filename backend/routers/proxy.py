import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
from urllib.parse import urlparse

router = APIRouter()

ALLOWED_DOMAINS = [
    "cdn.footballkitarchive.com",
    "upload.wikimedia.org",
    "i.imgur.com",
]

# IP publique Freebox
FREEBOX_BASE = "http://82.67.103.45/images/master_kits/photos"


@router.get("/image-proxy")
async def image_proxy(url: str):
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
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch image: {e}")


@router.get("/images/{filename}")
async def freebox_image_proxy(filename: str):
    """Proxy HTTPS (Render) → HTTP (Freebox NAS) pour éviter le Mixed Content."""
    url = f"{FREEBOX_BASE}/{filename}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return Response(status_code=404)
            return StreamingResponse(
                iter([r.content]),
                media_type=r.headers.get("content-type", "image/jpeg"),
            )
    except Exception:
        return Response(status_code=404)
