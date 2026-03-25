from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from typing import List
from pathlib import Path
import uuid
import os
import aiofiles
import httpx
from ..utils import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

# Dossier de destination : Freebox NAS en prod, dossier local en dev
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(Path(__file__).parent.parent / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# URL publique de base pour construire l'URL retournée après upload
MEDIA_BASE_URL = os.getenv(
    "MEDIA_BASE_URL",
    "https://917824d5-a03a-481d-8a97-36ccc4c108c6.cfargotunnel.com"
)

router = APIRouter(prefix="/api", tags=["uploads"])


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")

    filename = f"{uuid.uuid4().hex[:16]}{ext}"
    filepath = UPLOAD_DIR / filename
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    public_url = f"{MEDIA_BASE_URL}/images/master_kits/photos/{filename}"
    return {"filename": filename, "url": public_url}


@router.post("/upload/multiple")
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            continue
        filename = f"{uuid.uuid4().hex[:16]}{ext}"
        filepath = UPLOAD_DIR / filename
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(contents)
        public_url = f"{MEDIA_BASE_URL}/images/master_kits/photos/{filename}"
        results.append({"filename": filename, "url": public_url})
    return results


@router.get("/image-proxy")
async def image_proxy(url: str):
    if not url.startswith("https://cdn.footballkitarchive.com/"):
        raise HTTPException(status_code=400, detail="Only footballkitarchive CDN URLs allowed")
    async with httpx.AsyncClient() as hc:
        resp = await hc.get(url, timeout=10)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch image")
        content_type = resp.headers.get("content-type", "image/jpeg")
        return Response(
            content=resp.content,
            media_type=content_type,
            headers={"Cache-Control": "public, max-age=86400"}
        )
