from fastapi import APIRouter
from fastapi.responses import StreamingResponse, Response
import httpx
import os

router = APIRouter(prefix="/api", tags=["images"])

# URL de base pour les médias — Cloudflare tunnel en prod, IP locale en dev
MEDIA_BASE_URL = os.getenv(
    "MEDIA_BASE_URL",
    "https://917824d5-a03a-481d-8a97-36ccc4c108c6.cfargotunnel.com"
)
FREEBOX_BASE = f"{MEDIA_BASE_URL}/images/master_kits/photos"


@router.get("/images/{filename}")
async def proxy_image(filename: str):
    url = f"{FREEBOX_BASE}/{filename}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return Response(status_code=404)
            return StreamingResponse(
                iter([r.content]),
                media_type=r.headers.get("content-type", "image/jpeg"),
                headers={"Cache-Control": "public, max-age=86400"},
            )
    except Exception:
        return Response(status_code=404)
