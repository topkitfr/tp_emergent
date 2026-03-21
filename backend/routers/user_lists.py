# backend/routers/user_lists.py
# Listes personnalisées de collection (ex: "Vintage 90", "World Cup", "PSG")
# Routes:
#   GET    /api/lists             — mes listes (avec items count)
#   POST   /api/lists             — créer une liste
#   PATCH  /api/lists/{list_id}   — renommer une liste
#   DELETE /api/lists/{list_id}   — supprimer une liste
#   POST   /api/lists/{list_id}/items          — ajouter un item (collection_id)
#   DELETE /api/lists/{list_id}/items/{col_id} — retirer un item

from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid
from .database import db, client
from auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/lists", tags=["lists"])


class ListCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None   # couleur hex optionnelle ex: "#6366f1"


class ListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class ListItemAdd(BaseModel):
    collection_id: str


# ─── GET mes listes ───────────────────────────────────────────────────────────

@router.get("")
async def get_my_lists(request: Request):
    user = await get_current_user(request)
    uid = user["user_id"]
    lists = await db.user_lists.find({"user_id": uid}, {"_id": 0}).sort("created_at", 1).to_list(200)

    # Enrichit chaque liste avec le count et les 4 premières photos
    for lst in lists:
        items = lst.get("collection_ids", [])
        lst["item_count"] = len(items)

        # 4 premières photos pour preview
        previews = []
        for col_id in items[:4]:
            col = await db.collections.find_one({"collection_id": col_id}, {"_id": 0, "version_id": 1})
            if col:
                ver = await db.versions.find_one({"version_id": col["version_id"]}, {"_id": 0, "front_photo": 1, "kit_id": 1})
                if ver:
                    photo = ver.get("front_photo") or ""
                    if not photo:
                        kit = await db.master_kits.find_one({"kit_id": ver["kit_id"]}, {"_id": 0, "front_photo": 1})
                        photo = kit.get("front_photo", "") if kit else ""
                    if photo:
                        previews.append(photo)
        lst["preview_photos"] = previews

    return lists


# ─── GET une liste avec ses items ─────────────────────────────────────────────

@router.get("/{list_id}")
async def get_list_detail(list_id: str, request: Request):
    user = await get_current_user(request)
    lst = await db.user_lists.find_one({"list_id": list_id, "user_id": user["user_id"]}, {"_id": 0})
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")

    # Enrichit avec les items complets
    col_ids = lst.get("collection_ids", [])
    items = []
    for col_id in col_ids:
        col = await db.collections.find_one({"collection_id": col_id}, {"_id": 0})
        if col:
            ver = await db.versions.find_one({"version_id": col["version_id"]}, {"_id": 0})
            if ver:
                kit = await db.master_kits.find_one({"kit_id": ver["kit_id"]}, {"_id": 0})
                col["version"] = ver
                col["master_kit"] = kit
            items.append(col)
    lst["items"] = items
    lst["item_count"] = len(items)
    return lst


# ─── Créer une liste ──────────────────────────────────────────────────────────

@router.post("")
async def create_list(body: ListCreate, request: Request):
    user = await get_current_user(request)
    uid = user["user_id"]

    if not body.name.strip():
        raise HTTPException(status_code=400, detail="List name is required")
    if len(body.name) > 60:
        raise HTTPException(status_code=400, detail="Name too long (max 60 chars)")

    # Vérifie doublon de nom
    existing = await db.user_lists.find_one({"user_id": uid, "name": body.name.strip()})
    if existing:
        raise HTTPException(status_code=400, detail="A list with this name already exists")

    doc = {
        "list_id":       f"list_{uuid.uuid4().hex[:12]}",
        "user_id":       uid,
        "name":          body.name.strip(),
        "description":   body.description or "",
        "color":         body.color or "",
        "collection_ids": [],
        "created_at":    datetime.now(timezone.utc).isoformat(),
        "updated_at":    datetime.now(timezone.utc).isoformat(),
    }
    await db.user_lists.insert_one(doc)
    doc.pop("_id", None)
    doc["item_count"] = 0
    doc["preview_photos"] = []
    return doc


# ─── Renommer / modifier une liste ────────────────────────────────────────────

@router.patch("/{list_id}")
async def update_list(list_id: str, body: ListUpdate, request: Request):
    user = await get_current_user(request)
    lst = await db.user_lists.find_one({"list_id": list_id, "user_id": user["user_id"]})
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")

    patch = {}
    if body.name is not None:
        if not body.name.strip():
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        patch["name"] = body.name.strip()
    if body.description is not None:
        patch["description"] = body.description
    if body.color is not None:
        patch["color"] = body.color

    if not patch:
        raise HTTPException(status_code=400, detail="Nothing to update")

    patch["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.user_lists.update_one({"list_id": list_id}, {"$set": patch})
    updated = await db.user_lists.find_one({"list_id": list_id}, {"_id": 0})
    return updated


# ─── Supprimer une liste ──────────────────────────────────────────────────────

@router.delete("/{list_id}")
async def delete_list(list_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.user_lists.delete_one({"list_id": list_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="List not found")
    return {"message": "List deleted"}


# ─── Ajouter un item à une liste ──────────────────────────────────────────────

@router.post("/{list_id}/items")
async def add_item_to_list(list_id: str, body: ListItemAdd, request: Request):
    user = await get_current_user(request)
    lst = await db.user_lists.find_one({"list_id": list_id, "user_id": user["user_id"]})
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")

    # Vérifie que l'item appartient bien à l'user
    col = await db.collections.find_one({"collection_id": body.collection_id, "user_id": user["user_id"]})
    if not col:
        raise HTTPException(status_code=404, detail="Collection item not found")

    if body.collection_id in lst.get("collection_ids", []):
        raise HTTPException(status_code=400, detail="Item already in list")

    await db.user_lists.update_one(
        {"list_id": list_id},
        {
            "$push": {"collection_ids": body.collection_id},
            "$set":  {"updated_at": datetime.now(timezone.utc).isoformat()},
        }
    )
    return {"message": "Item added", "list_id": list_id, "collection_id": body.collection_id}


# ─── Retirer un item d'une liste ──────────────────────────────────────────────

@router.delete("/{list_id}/items/{collection_id}")
async def remove_item_from_list(list_id: str, collection_id: str, request: Request):
    user = await get_current_user(request)
    lst = await db.user_lists.find_one({"list_id": list_id, "user_id": user["user_id"]})
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")

    if collection_id not in lst.get("collection_ids", []):
        raise HTTPException(status_code=404, detail="Item not in list")

    await db.user_lists.update_one(
        {"list_id": list_id},
        {
            "$pull": {"collection_ids": collection_id},
            "$set":  {"updated_at": datetime.now(timezone.utc).isoformat()},
        }
    )
    return {"message": "Item removed"}
