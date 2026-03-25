from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from typing import List
from pathlib import Path
import os
import httpx
from ..utils import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

# URL du serveur récepteur sur la Freebox VM
RECEIVER_URL = os.getenv("RECEIVER_URL", "http://82.67.103.45:8001/receive-upload")
RECEIVER_SECRET = os.getenv("RECEIVER_SECRET", "changeme")

router = APIRouter(prefix="/api", tags=["uploads"])


FOLDER_MAP = {
    "master_kit": "master_kit",
    "version":    "version",
    "profile":    "profile",
    "brand":      "brand",
    "team":       "team",
    "league":     "league",
    "sponsor":    "sponsor",
    "player":     "player",
}


async def _forward_to_receiver(contents: bytes, filename: str, folder: str) -> str:
    """Envoie le fichier au récepteur Freebox et retourne l'URL publique."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            RECEIVER_URL,
            headers={"x-secret": RECEIVER_SECRET},
            files={"file": (filename, contents)},
            data={"folder": folder},
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Receiver error: {resp.text}")
        return resp.json()["url"]


@router.post("/upload")
async def upload_image(file: UploadFile = File(...), folder: str = "master_kit"):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")

    folder = FOLDER_MAP.get(folder, "master_kit")
    public_url = await _forward_to_receiver(contents, file.filename, folder)
    return {"filename": file.filename, "url": public_url}


@router.post("/upload/multiple")
async def upload_multiple_images(files: List[UploadFile] = File(...), folder: str = "master_kit"):
    results = []
    folder = FOLDER_MAP.get(folder, "master_kit")
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            continue
        try:
            public_url = await _forward_to_receiver(contents, file.filename, folder)
            results.append({"filename": file.filename, "url": public_url})
        except Exception:
            continue
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
