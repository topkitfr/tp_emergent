from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Query
from pathlib import Path
import aiofiles
import uuid
import os

app = FastAPI()

MEDIA_ROOT = Path("/mnt/Freebox-1/TP_media")
BASE_URL = os.getenv("MEDIA_BASE_URL", "https://82.67.103.45")
SECRET = os.getenv("RECEIVER_SECRET", "changeme")

# Types MIME acceptés — on inclut octet-stream comme fallback générique
ALLOWED_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "application/octet-stream",  # fallback quand le browser ne précise pas
}

FOLDERS = {
    # Kits
    "master_kit": MEDIA_ROOT / "kits"     / "masters",
    "version":    MEDIA_ROOT / "kits"     / "versions",
    # Teams
    "team":       MEDIA_ROOT / "teams"    / "clubs",
    "nation":     MEDIA_ROOT / "teams"    / "nations",
    "stadium":    MEDIA_ROOT / "teams"    / "stadiums",
    # Autres entités
    "league":     MEDIA_ROOT / "leagues"  / "logos",
    "brand":      MEDIA_ROOT / "brands"   / "logos",
    "sponsor":    MEDIA_ROOT / "sponsors" / "logos",
    "player":     MEDIA_ROOT / "players"  / "photos",
    "profile":    MEDIA_ROOT / "users"    / "photos",
}


@app.post("/receive-upload")
async def receive_upload(
    file: UploadFile = File(...),
    folder: str = Query("master_kit"),
    entity_id: str = Query(None),
    side: str = Query(None),       # "front" | "back" | None
    x_secret: str = Header(...)
):
    if x_secret != SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail=f"Type non autorisé: {file.content_type}")

    dest = FOLDERS.get(folder, MEDIA_ROOT / "kits" / "masters")
    dest.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower() or ".jpg"
    uid = uuid.uuid4().hex[:12]

    # Naming: {folder}_{entity_id}_{side}_{uid}{ext}  (entity_id et side optionnels)
    parts = [folder]
    if entity_id:
        parts.append(entity_id)
    if side in ("front", "back"):
        parts.append(side)
    parts.append(uid)
    filename = "_".join(parts) + ext

    filepath = dest / filename

    contents = await file.read()
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    relative = str(filepath.relative_to(MEDIA_ROOT))
    public_url = f"{BASE_URL}/{relative}"
    return {
        "filename": filename,
        "relative_path": relative,
        "url": public_url,
    }


@app.delete("/delete-file")
async def delete_file(
    relative_path: str = Query(...),
    x_secret: str = Header(...)
):
    if x_secret != SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    filepath = MEDIA_ROOT / relative_path
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Fichier introuvable")

    if not filepath.resolve().is_relative_to(MEDIA_ROOT.resolve()):
        raise HTTPException(status_code=400, detail="Chemin invalide")

    filepath.unlink()
    return {"deleted": relative_path}
