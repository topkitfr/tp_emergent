from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from pathlib import Path
import aiofiles
import uuid
import os

app = FastAPI()

MEDIA_ROOT = Path("/mnt/Freebox-1/topkit-media")
BASE_URL = "http://82.67.103.45"
SECRET = os.getenv("RECEIVER_SECRET", "changeme")

FOLDERS = {
    "master_kit": MEDIA_ROOT / "master_kits" / "photos",
    "version":    MEDIA_ROOT / "versions"    / "photos",
    "profile":    MEDIA_ROOT / "users"       / "photos",
    "brand":      MEDIA_ROOT / "brands"      / "logos",
    "team":       MEDIA_ROOT / "teams"       / "logos",
    "league":     MEDIA_ROOT / "leagues"     / "logos",
    "sponsor":    MEDIA_ROOT / "sponsors"    / "logos",
    "player":     MEDIA_ROOT / "players"     / "photos",
}

@app.post("/receive-upload")
async def receive_upload(
    file: UploadFile = File(...),
    folder: str = "master_kit",
    x_secret: str = Header(...)
):
    if x_secret != SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    dest = FOLDERS.get(folder, MEDIA_ROOT / "master_kits" / "photos")
    dest.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4().hex[:16]}{ext}"
    filepath = dest / filename

    contents = await file.read()
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(contents)

    relative = str(filepath.relative_to(MEDIA_ROOT))
    public_url = f"/api/uploads/{relative}"
    return {"filename": filename, "url": public_url}
