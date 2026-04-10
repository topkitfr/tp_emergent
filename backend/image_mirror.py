"""Download an external image URL and forward it to the Freebox receiver."""
import os
import httpx
from pathlib import Path

RECEIVER_URL    = os.getenv("RECEIVER_URL",    "http://receiver:8001")
RECEIVER_SECRET = os.getenv("RECEIVER_SECRET", "changeme")

# Champs image par type d'entité
IMAGE_FIELDS: dict[str, list[str]] = {
    "team":    ["crest_url", "stadium_image_url"],
    "nation":  ["crest_url"],
    "league":  ["logo_url", "apifootball_logo"],
    "player":  ["photo_url"],
    "brand":   ["logo_url"],
    "sponsor": ["logo_url"],
}

# Mapping type → folder attendu par receiver.py
FOLDER_MAP: dict[str, str] = {
    "team":    "team",      # → TP_media/teams/clubs
    "nation":  "nation",    # → TP_media/teams/nations
    "league":  "league",    # → TP_media/leagues/logos
    "player":  "player",    # → TP_media/players/photos
    "brand":   "brand",     # → TP_media/brands/logos
    "sponsor": "sponsor",   # → TP_media/sponsors/logos
    "stadium": "stadium",   # → TP_media/teams/stadiums
}


async def mirror_image(
    source_url: str,
    folder: str,
    entity_id: str,
) -> str:
    """Télécharge source_url et le poste au receiver.
    Retourne l'URL Freebox, ou source_url en fallback silencieux."""
    if not source_url or not source_url.startswith("http"):
        return source_url
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            # 1. Télécharger l'image depuis l'URL externe
            dl = await client.get(source_url, follow_redirects=True)
            dl.raise_for_status()
            content_type = dl.headers.get("content-type", "image/png").split(";")[0].strip()
            ext_map = {
                "image/jpeg": ".jpg",
                "image/png":  ".png",
                "image/webp": ".webp",
                "image/gif":  ".gif",
            }
            ext = ext_map.get(content_type) or Path(source_url.split("?")[0]).suffix or ".jpg"
            fname = f"{folder}_{entity_id}{ext}"

            # 2. Poster au receiver
            resp = await client.post(
                f"{RECEIVER_URL}/receive-upload",
                params={"folder": folder, "entity_id": entity_id},
                headers={"x-secret": RECEIVER_SECRET},
                files={"file": (fname, dl.content, content_type)},
            )
            resp.raise_for_status()
            return resp.json().get("url", source_url)
    except Exception as exc:
        print(f"[image_mirror] WARN: could not mirror {source_url!r}: {exc}")
        return source_url  # fallback gracieux — on garde l'URL originale


async def mirror_entity_images(doc: dict, entity_type: str, entity_id: str) -> dict:
    """Mirore tous les champs image d'une entité vers la Freebox.

    Pour les teams, on distingue automatiquement club / nation / stadium
    selon le champ concerné et le flag is_national du document.
    """
    # Résolution du type réel pour les teams
    effective_type = entity_type
    if entity_type == "team" and doc.get("is_national"):
        effective_type = "nation"

    fields = IMAGE_FIELDS.get(effective_type, [])
    for field in fields:
        url = doc.get(field)
        if not url or not url.startswith("http"):
            continue
        # Le champ stadium_image_url utilise toujours le dossier "stadium"
        if field == "stadium_image_url":
            folder = "stadium"
        else:
            folder = FOLDER_MAP.get(effective_type, effective_type)
        doc[field] = await mirror_image(url, folder, entity_id)
    return doc
