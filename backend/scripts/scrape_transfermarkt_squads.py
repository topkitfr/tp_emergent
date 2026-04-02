"""
scrape_transfermarkt_squads.py
==============================
Récupère les effectifs historiques (1985 → saison courante) sur Transfermarkt
pour toutes les équipes présentes dans la collection `teams` de TopKit.

Pour chaque équipe :
  1. Recherche de l'ID Transfermarkt via la recherche TM (si non stocké en base)
  2. Scraping des effectifs saison par saison (/kader/verein/{tm_id}/saison_id/{year})
  3. Pour chaque joueur trouvé :
     - Si présent en base (match nom normalisé) → update des champs manquants
     - Sinon → insert avec status="pending"

Usage :
    python backend/scripts/scrape_transfermarkt_squads.py \
        --mongo mongodb://localhost:27017 \
        --db topkit \
        [--team "Paris Saint-Germain"]  # optionnel : filtrer une équipe
        [--start-year 1985]             # optionnel (défaut: 1985)
        [--dry-run]
        [--delay 2.5]                   # secondes entre requêtes (défaut: 2.5)

NOTE : Ce script respecte les bonnes pratiques (délai entre requêtes, User-Agent
naturel). Ne pas réduire le délai en dessous de 2 secondes.
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
# Recherche ID Transfermarkt d'un club
# ---------------------------------------------------------------------------

def search_team_tm_id(client: httpx.Client, team_name: str, delay: float) -> tuple[str, str] | None:
    """
    Retourne (tm_slug, tm_id) pour le premier résultat TM correspondant au nom d'équipe.
    Ex: ('paris-saint-germain', '583')
    """
    query = team_name.replace(" ", "+")
    url = f"{BASE_URL}/schnellsuche/ergebnis/schnellsuche?query={query}&Verein_page=0"
    soup = get_soup(client, url, delay)
    if not soup:
        return None

    # Premier résultat dans la table des clubs
    table = soup.find("table", {"class": "items"})
    if not table:
        return None

    first_row = table.find("tbody").find("tr") if table.find("tbody") else None
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

def scrape_squad_season(client: httpx.Client, tm_slug: str, tm_id: str, year: int, delay: float) -> list[dict]:
    """
    Scrape l'effectif d'une équipe pour une saison donnée.
    Retourne une liste de dicts joueurs.
    """
    url = f"{BASE_URL}/{tm_slug}/kader/verein/{tm_id}/saison_id/{year}/plus/1"
    soup = get_soup(client, url, delay)
    if not soup:
        return []

    players = []
    table = soup.find("table", {"class": "items"})
    if not table:
        return []

    rows = table.find("tbody").find_all("tr", recursive=False) if table.find("tbody") else []

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
            tm_player_id = tm_player_match.group(2) if tm_player_match else ""

            # Flocage (shirt name) — souvent dans un span sous le nom
            shirt_name = ""
            name_cell = name_link.find_parent("td")
            if name_cell:
                shirt_span = name_cell.find("span", {"class": "auflistung"})
                if shirt_span:
                    shirt_name = shirt_span.get_text(strip=True).replace("Nom sur le maillot:", "").strip()

            # Position
            position_raw = ""
            pos_cell = row.find("td", {"class": "posrela"})
            if pos_cell:
                pos_span = pos_cell.find("table")
                if pos_span:
                    pos_td = pos_span.find_all("td")
                    if len(pos_td) > 1:
                        position_raw = pos_td[1].get_text(strip=True)
            position_code = POSITION_MAP.get(position_raw, position_raw)

            # Nationalité (drapeau img alt)
            nationality = ""
            nat_img = row.find("img", {"class": "flaggenrahmen"})
            if nat_img:
                nationality = nat_img.get("title", "")

            # Date de naissance + âge
            birth_date = ""
            birth_year = None
            dob_cell = row.find("td", string=re.compile(r"\d{2}\.\d{2}\.\d{4}"))
            if not dob_cell:
                # Chercher dans les td avec ce pattern
                for td in cells:
                    text = td.get_text(strip=True)
                    dob_match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", text)
                    if dob_match:
                        birth_date = f"{dob_match.group(3)}-{dob_match.group(2)}-{dob_match.group(1)}"
                        birth_year = int(dob_match.group(3))
                        break

            # Photo URL
            photo_url = ""
            img = row.find("img", {"class": "bilderrahmen-fixed"})
            if img:
                photo_url = img.get("data-src") or img.get("src", "")

            if full_name:
                players.append({
                    "full_name": full_name,
                    "shirt_name": shirt_name,
                    "positions": [position_code] if position_code else [],
                    "nationality": nationality,
                    "birth_date": birth_date,
                    "birth_year": birth_year,
                    "squad_number": squad_number,
                    "photo_url": photo_url,
                    "transfermarkt_id": tm_player_id,
                    "transfermarkt_slug": tm_player_slug,
                    "season": f"{year}/{str(year + 1)[-2:]}",
                })
        except Exception as e:
            print(f"    [WARN] Ligne ignorée : {e}")
            continue

    return players


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scrape Transfermarkt squads for TopKit teams")
    parser.add_argument("--mongo", default="mongodb://localhost:27017")
    parser.add_argument("--db", default="topkit")
    parser.add_argument("--team", default=None, help="Filtrer sur une équipe précise")
    parser.add_argument("--start-year", type=int, default=1985)
    parser.add_argument("--end-year", type=int, default=CURRENT_YEAR)
    parser.add_argument("--delay", type=float, default=2.5, help="Délai entre requêtes (secondes)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Connexion MongoDB
    mongo_client = MongoClient(args.mongo)
    db = mongo_client[args.db]

    # Charger les équipes TopKit
    team_query = {"status": {"$ne": "rejected"}}
    if args.team:
        team_query["name"] = {"$regex": args.team, "$options": "i"}

    teams = list(db.teams.find(team_query, {"_id": 0, "team_id": 1, "name": 1, "transfermarkt_id": 1, "transfermarkt_slug": 1}))
    print(f"[INFO] {len(teams)} équipe(s) TopKit trouvée(s)")

    if not teams:
        print("[WARN] Aucune équipe trouvée. Vérifier le filtre --team.")
        sys.exit(0)

    # Charger l'index des joueurs existants (nom normalisé → player_id)
    print("[INFO] Chargement des joueurs TopKit existants...")
    existing_players = list(db.players.find({}, {"_id": 0, "player_id": 1, "full_name": 1}))
    name_index: dict[str, str] = {normalize_name(p["full_name"]): p["player_id"] for p in existing_players}
    print(f"[INFO] {len(name_index)} joueurs en base")

    now = datetime.now(timezone.utc).isoformat()
    seasons_range = list(range(args.start_year, args.end_year + 1))

    total_stats = {"updated": 0, "inserted": 0, "skipped": 0}

    with httpx.Client() as http:
        for team in teams:
            team_name = team["name"]
            tm_id = team.get("transfermarkt_id", "")
            tm_slug = team.get("transfermarkt_slug", "")

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

                # Stocker l'ID TM dans la team TopKit
                if not args.dry_run:
                    db.teams.update_one(
                        {"team_id": team["team_id"]},
                        {"$set": {"transfermarkt_id": tm_id, "transfermarkt_slug": tm_slug, "updated_at": now}}
                    )

            all_players_seen: dict[str, dict] = {}  # tm_player_id → données enrichies

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
                        for field in ["birth_date", "birth_year", "nationality", "shirt_name", "photo_url"]:
                            if not existing.get(field) and p.get(field):
                                existing[field] = p[field]

            print(f"  [TOTAL] {len(all_players_seen)} joueurs uniques sur {len(seasons_range)} saisons")

            # Préparer bulk MongoDB
            updates = []
            inserts = []

            for player_data in all_players_seen.values():
                norm_key = normalize_name(player_data["full_name"])

                if norm_key in name_index:
                    # UPDATE joueur existant
                    pid = name_index[norm_key]
                    fields_to_set = {"updated_at": now}
                    for field in ["transfermarkt_id", "transfermarkt_slug", "birth_date",
                                  "birth_year", "nationality", "shirt_name"]:
                        val = player_data.get(field)
                        if val:
                            fields_to_set[field] = val
                    if player_data.get("positions"):
                        fields_to_set["positions"] = player_data["positions"]
                    # Photo : ne pas écraser une photo TopKit existante
                    if player_data.get("photo_url"):
                        fields_to_set.setdefault("transfermarkt_photo_url", player_data["photo_url"])

                    updates.append(
                        UpdateOne({"player_id": pid}, {"$set": fields_to_set})
                    )
                    total_stats["updated"] += 1
                else:
                    # INSERT nouveau joueur
                    new_pid = f"player_{uuid.uuid4().hex[:12]}"
                    slug = slugify(player_data["full_name"])
                    doc = {
                        "player_id": new_pid,
                        "status": "pending",
                        "full_name": player_data["full_name"],
                        "slug": slug,
                        "shirt_name": player_data.get("shirt_name", ""),
                        "nationality": player_data.get("nationality", ""),
                        "birth_date": player_data.get("birth_date", ""),
                        "birth_year": player_data.get("birth_year"),
                        "positions": player_data.get("positions", []),
                        "preferred_number": None,
                        "photo_url": player_data.get("photo_url", ""),
                        "transfermarkt_id": player_data.get("transfermarkt_id", ""),
                        "transfermarkt_slug": player_data.get("transfermarkt_slug", ""),
                        "bio": "",
                        "aura_level": 1,
                        "soccerwiki_id": None,
                        "team_honors": [],
                        "individual_awards": [],
                        "palmares_coefficient": 1.0,
                        "kit_count": 0,
                        "created_at": now,
                        "updated_at": now,
                    }
                    inserts.append(doc)
                    name_index[norm_key] = new_pid  # éviter doublons inter-équipes
                    total_stats["inserted"] += 1

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
    print(f"[TERMINÉ] Mis à jour : {total_stats['updated']} | Insérés : {total_stats['inserted']}")


if __name__ == "__main__":
    main()
