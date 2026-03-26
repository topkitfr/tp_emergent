from fastapi import APIRouter
from fastapi.responses import StreamingResponse, Response
import httpx
import os

router = APIRouter(prefix="/api", tags=["images"])

# URL de base Cloudflare tunnel (prod) ou IP directe (dev)
MEDIA_BASE_URL = os.getenv(
    "MEDIA_BASE_URL",
    "https://917824d5-a03a-481d-8a97-36ccc4c108c6.cfargotunnel.com"
)


@router.get("/images/{full_path:path}")
async def proxy_image(full_path: str):
    url = f"{MEDIA_BASE_URL}/{full_path}"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
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
