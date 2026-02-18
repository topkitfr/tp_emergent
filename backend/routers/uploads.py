from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from typing import List
from pathlib import Path
import uuid
import aiofiles
import httpx
from utils import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/api", tags=["uploads"])


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}")
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")
    filename = f"{uuid.uuid4().hex[:16]}{ext}"
    filepath = UPLOAD_DIR / filename
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)
    return {"filename": filename, "url": f"/api/uploads/{filename}"}


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
        results.append({"filename": filename, "url": f"/api/uploads/{filename}"})
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
        return Response(content=resp.content, media_type=content_type, headers={"Cache-Control": "public, max-age=86400"})
