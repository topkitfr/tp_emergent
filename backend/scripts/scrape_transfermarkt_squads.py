"""
scrape_transfermarkt_squads.py
==============================
Récupère les effectifs historiques (1985 → saison courante) sur Transfermarkt
pour toutes les équipes présentes dans la collection `teams` de TopKit.

Pour chaque équipe :
  1. Recherche de l'ID Transfermarkt via la recherche TM (si non stocké en base)
  2. Scraping des effectifs saison par saison (/kader/verein/{tm_id}/saison_id/{year})
  3. Pour chaque joueur :
     - Si présent en base (match nom normalisé) → update des champs manquants
     - Sinon → insert avec status="pending"
  4. Si --download-photos : télécharge la photo TM et l'envoie au receiver Freebox
     → stockée dans /Freebox 1/topkit-media/players/photos/{player_id}.jpg

Usage :
    python backend/scripts/scrape_transfermarkt_squads.py \
        --mongo mongodb://localhost:27017 \
        --db topkit \
        [--team "Paris Saint-Germain"]       # filtrer une équipe
        [--start-year 1985]                   # défaut: 1985
        [--end-year 2026]                     # défaut: année courante
        [--delay 2.5]                         # secondes entre requêtes (défaut: 2.5)
        [--download-photos]                   # activer le téléchargement photos
        [--receiver-url http://IP:8001/upload]
        [--receiver-secret VOTRE_SECRET]
        [--dry-run]

NOTE : Ne pas réduire --delay en dessous de 2 secondes (risque de ban TM).
"""

import argparse
import re
import sys
import time
import unicodedata
import uuid
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = "https://www.transfermarkt.fr"
CURRENT_YEAR = datetime.now().year

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.transfermarkt.fr/",
}

# Mapping positions TM → format TopKit
POSITION_MAP = {
    "Gardien de but": "GK",
    "Libero": "SW",
    "Défenseur central": "CB",
    "Arrière droit": "RB",
    "Arrière gauche": "LB",
    "Milieu défensif": "DM",
    "Milieu central": "CM",
    "Milieu offensif": "AM",
    "Ailier droit": "RW",
    "Ailier gauche": "LW",
    "Attaquant centre": "ST",
    "Avant-centre": "ST",
    "Deuxième attaquant": "SS",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_name(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_str).strip().lower()


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normalize_name(name)).strip("-")


def get_soup(client: httpx.Client, url: str, delay: float) -> BeautifulSoup | None:
    """GET avec gestion d'erreur + délai."""
    try:
        time.sleep(delay)
        resp = client.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
        elif resp.status_code == 429:
            print(f"  [WARN] Rate limited (429) sur {url} — attente 30s")
            time.sleep(30)
            resp = client.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
            return BeautifulSoup(resp.text, "html.parser") if resp.status_code == 200 else None
        else:
            print(f"  [WARN] HTTP {resp.status_code} sur {url}")
            return None
    except Exception as e:
        print(f"  [ERROR] Requête échouée : {e}")
        return None


# ---------------------------------------------------------------------------
# Upload photo vers Freebox receiver
# ---------------------------------------------------------------------------

def push_photo_to_receiver(
    client: httpx.Client,
    image_url: str,
    player_id: str,
    receiver_url: str,
    receiver_secret: str | None,
    delay: float,
) -> str:
    """
    Télécharge la photo depuis image_url et l'envoie au receiver Freebox.
    Retourne le chemin Freebox final, ou "" en cas d'échec.
    """
    if not image_url or not receiver_url:
        return ""

    # Ignorer les placeholders TM (silhouette générique)
    if "default" in image_url or "dummy" in image_url or "nobody" in image_url:
        return ""

    try:
        time.sleep(delay / 2)  # délai réduit pour les images (même domaine que TM)
        img_resp = client.get(image_url, headers=HEADERS, timeout=20, follow_redirects=True)
        if img_resp.status_code != 200 or not img_resp.content:
            print(f"    [PHOTO] téléchargement KO ({img_resp.status_code}) : {image_url}")
            return ""

        # Vérifier que c'est bien une image
        content_type = img_resp.headers.get("content-type", "")
        if "image" not in content_type and "octet-stream" not in content_type:
            print(f"    [PHOTO] contenu non-image ({content_type}) : {image_url}")
            return ""

        filename = f"{player_id}.jpg"
        files = {"file": (filename, img_resp.content, "image/jpeg")}
        data = {
            "folder": "players/photos",
            "filename": filename,
        }
        headers = {}
        if receiver_secret:
            headers["X-Receiver-Secret"] = receiver_secret

        up_resp = client.post(receiver_url, data=data, files=files, headers=headers, timeout=30)

        if up_resp.status_code not in (200, 201):
            print(f"    [PHOTO] upload receiver KO {up_resp.status_code}: {up_resp.text[:200]}")
            return ""

        try:
            payload = up_resp.json()
            return payload.get("path") or payload.get("url") or f"/players/photos/{filename}"
        except Exception:
            return f"/players/photos/{filename}"

    except Exception as e:
        print(f"    [PHOTO] erreur upload : {e}")
        return ""


# ---------------------------------------------------------------------------
# Recherche ID Transfermarkt d'un club
# ---------------------------------------------------------------------------

def search_team_tm_id(
    client: httpx.Client, team_name: str, delay: float
) -> tuple[str, str] | None:
    """
    Retourne (tm_slug, tm_id) pour le premier résultat TM correspondant au nom d'équipe.
    Ex: ('paris-saint-germain', '583')
    """
    query = team_name.replace(" ", "+")
    url = f"{BASE_URL}/schnellsuche/ergebnis/schnellsuche?query={query}&Verein_page=0"
    soup = get_soup(client, url, delay)
    if not soup:
        return None

    table = soup.find("table", {"class": "items"})
    if not table:
        return None

    tbody = table.find("tbody")
    first_row = tbody.find("tr") if tbody else None
    if not first_row:
        return None

    link = first_row.find("a", href=re.compile(r"/startseite/verein/\d+"))
    if not link:
        return None

    href = link.get("href", "")
    match = re.search(r"/([^/]+)/startseite/verein/(\d+)", href)
    if match:
        return match.group(1), match.group(2)
    return None


# ---------------------------------------------------------------------------
# Scraping effectif d'une saison
# ---------------------------------------------------------------------------

def scrape_squad_season(
    client: httpx.Client, tm_slug: str, tm_id: str, year: int, delay: float
) -> list[dict]:
    """
    Scrape l'effectif d'une équipe pour une saison donnée.
    Retourne une liste de dicts joueurs.
    """
    url = f"{BASE_URL}/{tm_slug}/kader/verein/{tm_id}/saison_id/{year}/plus/1"
    soup = get_soup(client, url, delay)
    if not soup:
        return []

    table = soup.find("table", {"class": "items"})
    if not table:
        return []

    tbody = table.find("tbody")
    rows = tbody.find_all("tr", recursive=False) if tbody else []

    players = []
    for row in rows:
        if "spacer" in row.get("class", []):
            continue

        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        try:
            # Numéro
            squad_number = None
            num_cell = row.find("td", {"class": "rn_nummer"})
            if num_cell:
                try:
                    squad_number = int(num_cell.get_text(strip=True))
                except ValueError:
                    pass

            # Nom + lien TM joueur
            name_link = row.find("a", href=re.compile(r"/profil/spieler/\d+"))
            if not name_link:
                continue
            full_name = name_link.get_text(strip=True)
            player_href = name_link.get("href", "")
            tm_player_match = re.search(r"/([^/]+)/profil/spieler/(\d+)", player_href)
            tm_player_slug = tm_player_match.group(1) if tm_player_match else ""
            tm_player_id   = tm_player_match.group(2) if tm_player_match else ""

            # Flocage (shirt name)
            shirt_name = ""
            name_cell = name_link.find_parent("td")
            if name_cell:
                shirt_span = name_cell.find("span", {"class": "auflistung"})
                if shirt_span:
                    shirt_name = shirt_span.get_text(strip=True)
                    shirt_name = re.sub(r"Nom sur le maillot\s*:", "", shirt_name).strip()

            # Position
            position_raw = ""
            pos_cell = row.find("td", {"class": "posrela"})
            if pos_cell:
                pos_table = pos_cell.find("table")
                if pos_table:
                    pos_tds = pos_table.find_all("td")
                    if len(pos_tds) > 1:
                        position_raw = pos_tds[1].get_text(strip=True)
            position_code = POSITION_MAP.get(position_raw, position_raw)

            # Nationalité
            nationality = ""
            nat_img = row.find("img", {"class": "flaggenrahmen"})
            if nat_img:
                nationality = nat_img.get("title", "")

            # Date de naissance
            birth_date = ""
            birth_year = None
            for td in cells:
                text = td.get_text(strip=True)
                dob_match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", text)
                if dob_match:
                    birth_date = f"{dob_match.group(3)}-{dob_match.group(2)}-{dob_match.group(1)}"
                    birth_year = int(dob_match.group(3))
                    break

            # Photo URL (data-src en priorité pour le lazy loading TM)
            photo_url = ""
            img = row.find("img", {"class": "bilderrahmen-fixed"})
            if img:
                photo_url = img.get("data-src") or img.get("src", "")
                # Nettoyer les placeholders TM
                if photo_url and any(x in photo_url for x in ["default", "dummy", "nobody", "silhouette"]):
                    photo_url = ""

            if full_name:
                players.append({
                    "full_name":           full_name,
                    "shirt_name":          shirt_name,
                    "positions":           [position_code] if position_code else [],
                    "nationality":         nationality,
                    "birth_date":          birth_date,
                    "birth_year":          birth_year,
                    "squad_number":        squad_number,
                    "photo_url":           photo_url,
                    "transfermarkt_id":    tm_player_id,
                    "transfermarkt_slug":  tm_player_slug,
                    "season":              f"{year}/{str(year + 1)[-2:]}",
                })

        except Exception as e:
            print(f"    [WARN] Ligne ignorée : {e}")
            continue

    return players


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scrape Transfermarkt squads for TopKit teams"
    )
    parser.add_argument("--mongo",          default="mongodb://localhost:27017")
    parser.add_argument("--db",             default="topkit")
    parser.add_argument("--team",           default=None,  help="Filtrer sur une équipe précise")
    parser.add_argument("--start-year",     type=int, default=1985)
    parser.add_argument("--end-year",       type=int, default=CURRENT_YEAR)
    parser.add_argument("--delay",          type=float, default=2.5)
    parser.add_argument("--dry-run",        action="store_true")
    parser.add_argument("--download-photos",action="store_true",
                        help="Télécharger et envoyer les photos vers le receiver Freebox")
    parser.add_argument("--receiver-url",   default="",
                        help="URL du receiver Freebox ex: http://192.168.x.x:8001/upload")
    parser.add_argument("--receiver-secret",default=None,
                        help="Secret X-Receiver-Secret du receiver Freebox")
    args = parser.parse_args()

    if args.download_photos and not args.receiver_url:
        print("[ERROR] --download-photos nécessite --receiver-url")
        sys.exit(1)

    # Connexion MongoDB
    mongo_client = MongoClient(args.mongo)
    db = mongo_client[args.db]

    # Charger les équipes TopKit
    team_query = {"status": {"$ne": "rejected"}}
    if args.team:
        team_query["name"] = {"$regex": args.team, "$options": "i"}

    teams = list(db.teams.find(
        team_query,
        {"_id": 0, "team_id": 1, "name": 1, "transfermarkt_id": 1, "transfermarkt_slug": 1}
    ))
    print(f"[INFO] {len(teams)} équipe(s) TopKit trouvée(s)")

    if not teams:
        print("[WARN] Aucune équipe trouvée. Vérifier le filtre --team.")
        sys.exit(0)

    # Index joueurs existants (nom normalisé → player_id)
    print("[INFO] Chargement des joueurs TopKit existants...")
    existing_players = list(db.players.find({}, {"_id": 0, "player_id": 1, "full_name": 1, "photo_url": 1}))
    name_index:  dict[str, str]  = {normalize_name(p["full_name"]): p["player_id"] for p in existing_players}
    photo_index: dict[str, str]  = {p["player_id"]: p.get("photo_url", "") for p in existing_players}
    print(f"[INFO] {len(name_index)} joueurs en base")

    now = datetime.now(timezone.utc).isoformat()
    seasons_range = list(range(args.start_year, args.end_year + 1))
    total_stats = {"updated": 0, "inserted": 0, "photos_ok": 0, "photos_ko": 0}

    with httpx.Client() as http:
        for team in teams:
            team_name = team["name"]
            tm_id     = team.get("transfermarkt_id", "")
            tm_slug   = team.get("transfermarkt_slug", "")

            print(f"\n{'='*60}")
            print(f"[ÉQUIPE] {team_name}")

            # Recherche TM ID si non stocké
            if not tm_id:
                print(f"  [SEARCH] Recherche TM ID pour '{team_name}'...")
                result = search_team_tm_id(http, team_name, args.delay)
                if not result:
                    print(f"  [SKIP] Aucun résultat TM pour '{team_name}'")
                    continue
                tm_slug, tm_id = result
                print(f"  [FOUND] TM ID={tm_id}, slug={tm_slug}")

                if not args.dry_run:
                    db.teams.update_one(
                        {"team_id": team["team_id"]},
                        {"$set": {
                            "transfermarkt_id":   tm_id,
                            "transfermarkt_slug": tm_slug,
                            "updated_at":         now,
                        }}
                    )

            # Scraping toutes les saisons
            all_players_seen: dict[str, dict] = {}  # clé: tm_player_id ou norm_name

            for year in seasons_range:
                season_label = f"{year}/{str(year + 1)[-2:]}"
                print(f"  [SAISON] {season_label}...", end=" ", flush=True)

                squad = scrape_squad_season(http, tm_slug, tm_id, year, args.delay)
                print(f"{len(squad)} joueurs")

                for p in squad:
                    key = p["transfermarkt_id"] or normalize_name(p["full_name"])
                    if key not in all_players_seen:
                        all_players_seen[key] = p
                    else:
                        # Compléter les champs manquants avec des données d'autres saisons
                        existing = all_players_seen[key]
                        for field in ["birth_date", "birth_year", "nationality",
                                      "shirt_name", "photo_url"]:
                            if not existing.get(field) and p.get(field):
                                existing[field] = p[field]

            print(f"  [TOTAL] {len(all_players_seen)} joueurs uniques")

            # Préparer les opérations MongoDB
            updates = []
            inserts = []

            for player_data in all_players_seen.values():
                norm_key = normalize_name(player_data["full_name"])

                if norm_key in name_index:
                    # ── UPDATE joueur existant ──────────────────────────────
                    pid = name_index[norm_key]
                    fields_to_set = {"updated_at": now}

                    for field in ["transfermarkt_id", "transfermarkt_slug",
                                  "birth_date", "birth_year", "nationality", "shirt_name"]:
                        val = player_data.get(field)
                        if val:
                            fields_to_set[field] = val

                    if player_data.get("positions"):
                        fields_to_set["positions"] = player_data["positions"]

                    # Toujours stocker l'URL TM d'origine
                    if player_data.get("photo_url"):
                        fields_to_set["transfermarkt_photo_url"] = player_data["photo_url"]

                    # Photo Freebox : seulement si pas encore de photo locale
                    if (args.download_photos
                            and player_data.get("photo_url")
                            and not photo_index.get(pid)):
                        if not args.dry_run:
                            freebox_path = push_photo_to_receiver(
                                http,
                                player_data["photo_url"],
                                pid,
                                args.receiver_url,
                                args.receiver_secret,
                                args.delay,
                            )
                            if freebox_path:
                                fields_to_set["photo_url"] = freebox_path
                                photo_index[pid] = freebox_path
                                total_stats["photos_ok"] += 1
                                print(f"    [PHOTO ✓] {player_data['full_name']}")
                            else:
                                total_stats["photos_ko"] += 1
                        else:
                            print(f"    [PHOTO DRY] {player_data['full_name']} → {player_data['photo_url']}")

                    updates.append(
                        UpdateOne({"player_id": pid}, {"$set": fields_to_set})
                    )
                    total_stats["updated"] += 1

                else:
                    # ── INSERT nouveau joueur ───────────────────────────────
                    new_pid = f"player_{uuid.uuid4().hex[:12]}"
                    slug    = slugify(player_data["full_name"])

                    # Photo Freebox pour le nouveau joueur
                    freebox_photo_path = ""
                    if (args.download_photos
                            and player_data.get("photo_url")
                            and not args.dry_run):
                        freebox_photo_path = push_photo_to_receiver(
                            http,
                            player_data["photo_url"],
                            new_pid,
                            args.receiver_url,
                            args.receiver_secret,
                            args.delay,
                        )
                        if freebox_photo_path:
                            total_stats["photos_ok"] += 1
                            print(f"    [PHOTO ✓] {player_data['full_name']}")
                        else:
                            total_stats["photos_ko"] += 1
                    elif args.download_photos and player_data.get("photo_url") and args.dry_run:
                        print(f"    [PHOTO DRY] {player_data['full_name']} → {player_data['photo_url']}")

                    doc = {
                        "player_id":               new_pid,
                        "status":                  "pending",
                        "full_name":               player_data["full_name"],
                        "slug":                    slug,
                        "shirt_name":              player_data.get("shirt_name", ""),
                        "nationality":             player_data.get("nationality", ""),
                        "birth_date":              player_data.get("birth_date", ""),
                        "birth_year":              player_data.get("birth_year"),
                        "positions":               player_data.get("positions", []),
                        "preferred_number":        None,
                        # photo_url = chemin Freebox si uploadé, sinon URL TM en fallback
                        "photo_url":               freebox_photo_path or player_data.get("photo_url", ""),
                        "transfermarkt_photo_url": player_data.get("photo_url", ""),
                        "transfermarkt_id":        player_data.get("transfermarkt_id", ""),
                        "transfermarkt_slug":      player_data.get("transfermarkt_slug", ""),
                        "bio":                     "",
                        "aura_level":              1,
                        "soccerwiki_id":           None,
                        "team_honors":             [],
                        "individual_awards":       [],
                        "palmares_coefficient":    1.0,
                        "kit_count":               0,
                        "created_at":              now,
                        "updated_at":              now,
                    }
                    inserts.append(doc)
                    name_index[norm_key] = new_pid  # éviter doublons inter-équipes
                    photo_index[new_pid] = freebox_photo_path
                    total_stats["inserted"] += 1

            # Écriture MongoDB
            if not args.dry_run:
                if updates:
                    try:
                        res = db.players.bulk_write(updates, ordered=False)
                        print(f"  [MONGO] {res.modified_count} joueurs mis à jour")
                    except BulkWriteError as e:
                        print(f"  [MONGO ERROR] {e.details}")
                if inserts:
                    res = db.players.insert_many(inserts, ordered=False)
                    print(f"  [MONGO] {len(res.inserted_ids)} joueurs insérés (pending)")
            else:
                print(f"  [DRY-RUN] {len(updates)} updates, {len(inserts)} inserts (non exécutés)")

    print(f"\n{'='*60}")
    print(f"[TERMINÉ]")
    print(f"  Mis à jour : {total_stats['updated']}")
    print(f"  Insérés    : {total_stats['inserted']}")
    if args.download_photos:
        print(f"  Photos OK  : {total_stats['photos_ok']}")
        print(f"  Photos KO  : {total_stats['photos_ko']}")


if __name__ == "__main__":
    main()
