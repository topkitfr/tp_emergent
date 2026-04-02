"""
import_soccerwiki_players.py
============================
Synchronise la collection `players` MongoDB avec le JSON SoccerWiki.

Pour chaque joueur du JSON :
  1. Si un player TopKit matche par nom normalisé → update soccerwiki_id + photo_url + photo_action_url
  2. Si aucun match → insert du joueur (status="pending" pour review manuelle)

Usage :
    python backend/scripts/import_soccerwiki_players.py \
        --json chemin/vers/SoccerWiki_players.json \
        [--mongo mongodb://localhost:27017] \
        [--db topkit] \
        [--dry-run]
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_name(name: str) -> str:
    """Lowercase, strip accents, collapse spaces — pour comparaison floue."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_str).strip().lower()


def build_full_name(forename: str, surname: str) -> str:
    return f"{forename} {surname}".strip()


def slugify(name: str) -> str:
    normalized = normalize_name(name)
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Import SoccerWiki players into TopKit MongoDB")
    parser.add_argument("--json", required=True, help="Chemin vers le fichier JSON SoccerWiki")
    parser.add_argument("--mongo", default="mongodb://localhost:27017", help="URI MongoDB")
    parser.add_argument("--db", default="topkit", help="Nom de la base de données")
    parser.add_argument("--dry-run", action="store_true", help="Simule sans écrire en base")
    args = parser.parse_args()

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"[ERREUR] Fichier introuvable : {json_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Lecture du JSON : {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sw_players = data.get("PlayerData", [])
    print(f"[INFO] {len(sw_players)} joueurs trouvés dans le JSON SoccerWiki")

    # Connexion MongoDB
    client = MongoClient(args.mongo)
    db = client[args.db]
    col = db["players"]

    # --- Charger tous les players TopKit en mémoire pour matching rapide ---
    print("[INFO] Chargement des players TopKit existants...")
    existing = list(col.find({}, {"_id": 1, "player_id": 1, "full_name": 1, "photo_url": 1}))
    # Index par nom normalisé → player_id
    name_index: dict[str, str] = {}
    for p in existing:
        key = normalize_name(p.get("full_name", ""))
        name_index[key] = str(p["_id"])
    print(f"[INFO] {len(existing)} players TopKit en base")

    # --- Préparer les opérations bulk ---
    updates = []       # UpdateOne pour players existants
    inserts = []       # documents nouveaux joueurs
    stats = {"matched": 0, "inserted": 0, "skipped": 0}

    now = datetime.now(timezone.utc).isoformat()

    for sw in sw_players:
        sw_id = sw.get("ID")
        forename = (sw.get("Forename") or "").strip()
        surname = (sw.get("Surname") or "").strip()
        full_name = build_full_name(forename, surname)
        image_url = sw.get("ImageURL", "")
        action_url = sw.get("ImageActionURL", "")

        norm_key = normalize_name(full_name)

        if norm_key in name_index:
            # UPDATE joueur existant
            oid = name_index[norm_key]
            update_fields = {
                "soccerwiki_id": sw_id,
                "updated_at": now,
            }
            # Ne pas écraser une photo_url déjà définie par l'équipe TopKit
            # (on l'écrit seulement si vide ou si c'est déjà une URL soccerwiki)
            update_fields["soccerwiki_photo_url"] = image_url
            if action_url:
                update_fields["soccerwiki_photo_action_url"] = action_url

            updates.append(
                UpdateOne(
                    {"player_id": oid} if "_id" not in oid else {"_id": oid},
                    {"$set": update_fields},
                )
            )
            stats["matched"] += 1
        else:
            # INSERT nouveau joueur (status pending — review manuelle)
            import uuid
            player_id = str(uuid.uuid4())
            doc = {
                "player_id": player_id,
                "status": "pending",
                "full_name": full_name,
                "slug": slugify(full_name),
                "nationality": "",
                "birth_date": "",
                "birth_year": None,
                "positions": [],
                "preferred_number": None,
                "photo_url": image_url,
                "bio": "",
                "aura_level": 1,
                "soccerwiki_id": sw_id,
                "soccerwiki_photo_url": image_url,
                "soccerwiki_photo_action_url": action_url if action_url else "",
                "kit_count": 0,
                "created_at": now,
                "updated_at": now,
                # Palmarès (prêt pour la prochaine étape)
                "team_honors": [],
                "individual_awards": [],
                "palmares_coefficient": 1.0,
            }
            inserts.append(doc)
            stats["inserted"] += 1

    print(f"\n[RÉSULTAT] Matchés (update)  : {stats['matched']}")
    print(f"[RÉSULTAT] Nouveaux (insert) : {stats['inserted']}")
    print(f"[RÉSULTAT] Total JSON traité : {stats['matched'] + stats['inserted']}")

    if args.dry_run:
        print("\n[DRY-RUN] Aucune écriture effectuée.")
        return

    # --- Exécution bulk ---
    if updates:
        print(f"\n[MONGO] Envoi de {len(updates)} updates...")
        try:
            result = col.bulk_write(updates, ordered=False)
            print(f"[MONGO] Updates OK : {result.modified_count} modifiés")
        except BulkWriteError as e:
            print(f"[MONGO] Erreurs bulk write : {e.details}", file=sys.stderr)

    if inserts:
        print(f"[MONGO] Insertion de {len(inserts)} nouveaux joueurs (status=pending)...")
        result = col.insert_many(inserts, ordered=False)
        print(f"[MONGO] Inserts OK : {len(result.inserted_ids)} insérés")

    print("\n[DONE] Import terminé.")


if __name__ == "__main__":
    main()
