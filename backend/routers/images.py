from fastapi import APIRouter
from fastapi.responses import StreamingResponse, Response
import httpx

router = APIRouter(prefix="/api", tags=["images"])

FREEBOX_BASE = "http://192.168.0.47/images/master_kits/photos"

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