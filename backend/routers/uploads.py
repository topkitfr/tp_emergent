from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from typing import List, Optional
from pathlib import Path
import os
import re
import httpx
from ..utils import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

# URL du serveur récepteur sur la Freebox VM
RECEIVER_URL = os.getenv("RECEIVER_URL", "http://82.67.103.45:8001/receive-upload")
RECEIVER_SECRET = os.getenv("RECEIVER_SECRET", "changeme")

router = APIRouter(prefix="/api", tags=["uploads"])


# Aligné sur la structure réelle /TP_media/ de la Freebox
FOLDER_MAP = {
    "master_kit": "kits/masters",
    "version":    "kits/versions",
    "profile":    "users/photos",
    "brand":      "brands/logos",
    "team":       "teams/clubs",
    "nation":     "teams/nations",
    "league":     "leagues/logos",
    "sponsor":    "sponsors/logos",
    "player":     "players/photos",
}


def _to_relative_path(public_url: str) -> str:
    """
    Convertit l'URL absolue retournée par le receiver Freebox
    (ex: http://82.67.103.45/leagues/logos/39.png)
    en chemin relatif via le proxy backend existant
    (ex: /api/images/leagues/logos/39.png).
    """
    pattern = re.compile(r'^https?://[^/]+')
    match = pattern.match(public_url)
    if not match:
        return public_url
    relative = public_url[match.end():]
    return f"/api/images{relative}"


async def _forward_to_receiver(
    contents: bytes,
    filename: str,
    folder: str,
    entity_id: Optional[str] = None,
    side: Optional[str] = None,
) -> dict:
    """Envoie le fichier au récepteur Freebox et retourne url + relative_path."""
    params = {"folder": folder}
    if entity_id:
        params["entity_id"] = entity_id
    if side in ("front", "back"):
        params["side"] = side

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            RECEIVER_URL,
            headers={"x-secret": RECEIVER_SECRET},
            files={"file": (filename, contents)},
            params=params,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Receiver error: {resp.text}")
        data = resp.json()
        return {
            "url": _to_relative_path(data["url"]),
            "relative_path": data.get("relative_path"),
        }


async def download_and_store(
    image_url: str,
    folder: str,
    entity_id: str,
    filename: Optional[str] = None,
) -> dict:
    """
    Télécharge une image depuis une URL externe (API-Football, etc.)
    et la stocke sur la Freebox via le receiver.
    Retourne { url, relative_path } prêts à persister en base.

    Flux : source externe → backend → Freebox NAS → logo_url en base
    """
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(image_url)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Échec du téléchargement de l'image : {image_url} (status {resp.status_code})"
            )
        contents = resp.content
        # Détermine l'extension depuis le Content-Type si pas de filename fourni
        ct = resp.headers.get("content-type", "image/png")
        ext = ct.split("/")[-1].split(";")[0].strip()  # png, jpeg, webp…
        ext = "jpg" if ext == "jpeg" else ext
        fname = filename or f"{entity_id}.{ext}"

    return await _forward_to_receiver(contents, fname, folder, entity_id)


@router.post("/upload/from-url")
async def upload_from_url(
    image_url: str,
    folder: str,
    entity_id: str,
    filename: Optional[str] = None,
):
    """
    Route pour les seeds API-Football et tout import automatique.
    Reçoit une URL externe, télécharge l'image et la stocke sur la Freebox.

    Exemples d'usage :
      - seed_leagues  → folder="league",  entity_id="39"
      - seed_teams    → folder="team",    entity_id="33"
      - seed_players  → folder="player",  entity_id="276"
    """
    mapped_folder = FOLDER_MAP.get(folder)
    if not mapped_folder:
        raise HTTPException(
            status_code=400,
            detail=f"Dossier inconnu : '{folder}'. Valeurs valides : {list(FOLDER_MAP.keys())}"
        )
    return await download_and_store(image_url, mapped_folder, entity_id, filename)


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = "master_kit",
    entity_id: Optional[str] = None,
    side: Optional[str] = None,
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB")

    mapped_folder = FOLDER_MAP.get(folder, "kits/masters")
    result = await _forward_to_receiver(contents, file.filename, mapped_folder, entity_id, side)
    return {"filename": file.filename, **result}


@router.post("/upload/multiple")
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    folder: str = "master_kit",
    entity_id: Optional[str] = None,
    side: Optional[str] = None,
):
    results = []
    mapped_folder = FOLDER_MAP.get(folder, "kits/masters")
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            continue
        try:
            result = await _forward_to_receiver(contents, file.filename, mapped_folder, entity_id, side)
            results.append({"filename": file.filename, **result})
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
