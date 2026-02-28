import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import urlparse

router = APIRouter()

ALLOWED_DOMAINS = [
    "cdn.footballkitarchive.com",
    "upload.wikimedia.org",
    "i.imgur.com",
]

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
            media_type=resp.headers.get("content-type", "image/jpeg")
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch image: {e}")
