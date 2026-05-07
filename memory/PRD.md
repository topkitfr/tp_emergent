# Topkit — Product Requirements & Architecture

> _Document vivant. Mis à jour le 7 mai 2026 après audit de reprise._
> _Source de vérité pour l'architecture cible. Chaque déviation par rapport à ce document doit être motivée et le doc mis à jour._

## 1. Problème

Web app de catalogage et de gestion de collections de maillots de foot — modèle Discogs adapté au foot. Système d'entités structurées (Teams, Leagues, Brands, Sponsors, Players) alimenté par les contributeurs avec workflow de modération communautaire.

Deux faces :

1. **Tracker de collection personnel** — chaque user déclare ses maillots (master_kit → version → collection_item) avec flocage, signature, état, estimation auto-calculée.
2. **Base de données collaborative** — entités partagées modérées via votes et contrôles modérateurs.

## 2. Architecture

### 2.1 Stack
- **Frontend** : React 19 + react-router-dom 7 + Tailwind + shadcn/ui (Radix), build CRA (react-scripts 5).
- **Backend** : FastAPI 0.110 + Motor 3.3 (Mongo async), Python 3.11. Lancement `uvicorn backend.server:app`.
- **DB** : MongoDB Atlas (URL via `MONGO_URL`).
- **Auth** : sessions cookie httpOnly samesite=none, hash bcrypt via passlib, stockées dans `db.user_sessions`.
  > _Note (07/05/2026) : auth Google OAuth Emergent du PRD initial a été remplacée par bcrypt+email lors du passage en self-hosted._
- **Médias** : Freebox NAS `/mnt/Freebox-1/TP_media/` via micro-service receiver (FastAPI port 8001), authentifié par header `x-secret`. Servis publiquement via vhost `media.topkit.app` (alias nginx direct, pas de backend en prod).
- **Reverse proxy** : nginx, vhosts `topkit.app` (front), `api.topkit.app` (backend), `media.topkit.app` (NAS), `git.topkit.app` (gitea).

### 2.2 Backend — structure cible

```
/app/backend/
├── server.py          # Entry point slim : app, middlewares, includes, startup
├── database.py        # Client + db Motor
├── models.py          # Modèles Pydantic
├── utils.py           # slugify, normalize_season, calculate_estimation, constants
├── auth.py            # get_current_user (session cookie)
├── middleware.py      # maintenance_middleware
├── email_service.py   # Resend
├── image_mirror.py    # Mirror entité → receiver Freebox
└── routers/           # 1 fichier ≈ 1 domaine, prefix /api/...
    ├── auth.py             # login/register/me/logout/forgot/reset
    ├── kits.py             # master-kits/* + versions/* (à scinder, voir §6)
    ├── collections.py      # collections + stats
    ├── estimation.py       # POST /estimate
    ├── reviews.py          # reviews
    ├── submissions.py      # submissions + votes + applications
    ├── reports.py          # reports (error / removal)
    ├── wishlist.py         # wishlist
    ├── entities.py         # teams/leagues/brands/players/sponsors CRUD (à fusionner avec *_api, §6)
    ├── users.py            # profil, follows, aura
    ├── user_lists.py       # listes personnelles
    ├── notifications.py    # notifications utilisateur
    ├── beta.py             # beta gate
    ├── uploads.py          # /upload, /upload/from-url, download_and_store
    ├── proxy.py            # /api/images proxy
    ├── admin.py            # CSV imports, migrations, maintenance
    ├── admin_panel.py      # endpoints admin UI
    ├── awards.py           # CRUD awards individuels
    ├── players_scoring.py  # /scoring/players/* (note /100, palmarès, career)
    ├── players_chart.py    # career chart transferts
    ├── apifootball_search.py
    ├── leagues_api.py      # DB-first + API-Football (à fusionner, §6)
    ├── teams_api.py        # idem
    └── players_api.py      # idem
```

> _Note (07/05/2026) : 26 routers actuellement, 10 dans le PRD initial. La Phase 15 (API-Football) a ajouté 4 routers `*_api.py` qui doublonnent partiellement `entities.py` — refacto prévue §6._

### 2.3 Architecture média

```
Source (API-Football ou upload user)
        │
        ▼
  Backend FastAPI
  download_and_store() / _forward_to_receiver()
        │  (httpx + x-secret header)
        ▼
  Receiver FastAPI (Freebox VM, port 8001)
        │
        ▼
  /TP_media/{entity}/{type}/{id}.{ext}
        │
        ▼
  MongoDB : logo_url = "/api/images/leagues/logos/39.png"
        │
        ▼
  Frontend : <img src="https://media.topkit.app/leagues/logos/39.png">
            (ou fallback /api/images/... via nginx alias)
```

**Structure `/TP_media/`** :
```
brands/logos/         kits/masters/        kits/versions/
leagues/logos/        players/photos/      sponsors/logos/
teams/clubs/          teams/nations/       users/photos/
```

**`FOLDER_KEYS` (uploads.py)** : `master_kit`, `version`, `profile`, `brand`, `team`, `nation`, `league`, `sponsor`, `player`, `stadium`. Le mapping clé → chemin réel est fait côté receiver.

**Route seed** : `POST /api/upload/from-url?image_url=…&folder=…&entity_id=…` — point d'entrée unique pour tous les scripts de seed.

## 3. Modèle de données

### Hiérarchie maillot
- **Master Kit** : club, season, league, kit_type, brand, design, sponsor, gender, front_photo, color, entity_type (club/national), confederation_id + FK team_id, league_id, brand_id, sponsor_id.
- **Version** : kit_id, competition, model, sku_code, ean_code, front_photo, back_photo, main_player_id, competition_id.
- **Collection Item** : version_id, category, flocking_*, condition_origin, physical_state, size, signed_*, patch, is_rare, purchase_cost, estimated_price.

### Entités
- **Teams** : name, slug, country, city, founded, primary/secondary_color, crest_url, aka, apifootball_team_id, is_national, stadium_name, stadium_capacity, stadium_surface, stadium_image_url.
- **Leagues** : name, slug, country_or_region, level, organizer, logo_url, apifootball_league_id, scoring_weight, entity_type, scope, region, country_*, gender, level_type, seasons[].
- **Brands** : name, slug, country, founded, logo_url.
- **Players** : full_name, slug, nationality, birth_date, birth_year, positions, preferred_number, photo_url, bio, aura_level, apifootball_id, firstname, lastname, height, weight, honours[], individual_awards[], score_palmares, aura, note, gender, level, position_detail, jersey_number, current_team_id.
- **Awards** : award_id, name, category, scoring_weight, logo_url, description.

### Submissions
- Types : `master_kit`, `version`, `team`, `league`, `brand`, `player`, `sponsor`.
- Modes : `create`, `edit`, `removal`.
- Approbation : 5 votes communautaires (`APPROVAL_THRESHOLD=5`) ou 1 vote modérateur (`MODERATOR_APPROVAL_THRESHOLD=1`).
- Quotas par user/24h : 10 master_kit, 20 versions, 15 entités (team/league/brand/player/sponsor).

### Reports
- `report_type` : `error` (corrections) ou `removal` (suppression).
- À l'approbation : error → patche la cible ; removal → supprime la cible (et les versions associées si master_kit).

### Estimation
- Formule : `prix_base × (1 + Σ coeffs)`.
- Sources : `backend/utils.py` (`calculate_estimation`) + duplication front `frontend/src/utils/estimation.js`. **Doivent rester strictement alignées** — bug récurrent quand un coeff est ajouté d'un seul côté.
- Coefficients : compétition, état physique, origine, flocage, signature (par type), preuve, message personnel, profil joueur (Option A — déduit auto de la note /100), patch, rareté, ancienneté.

### Scoring joueur
- `note /100 = palmarès × 0.4 + awards × 0.3 + aura × 0.2 + topkit_kits × 0.1`
- `aura` votée par les users (1-10 → ramené /10, multiplié par 10 pour la note communautaire).
- `topkit_kits` comptés depuis collections via `flocking_player_id` ou `signed_by_player_id`.

## 4. Rôles

- **user** : 1 vote sur submissions/reports.
- **moderator** : 1 vote = approbation immédiate. Liste configurable via `MODERATOR_EMAILS` (defaut `topkitfr@gmail.com,dev@topkit.fr,steinmetzolivier@gmail.com`).
- **admin** : full access (`ADMIN_EMAILS` env vide par défaut).

## 5. Phases — historique

### Phases 1-12 — Fondations (terminées)
CRUD complet, OAuth (puis remplacée), browse/search, reviews, wishlist, estimation v1, défaut versions, entités structurées + autocomplete + migration, modération entités (Phase 12).

### Phase 13 — Refacto backend (Feb 18, 2026)
Décomposition `server.py` 1907 l → router architecture modulaire. **Ré-évaluation 07/05/2026** : `server.py` actuel = 272 l (rate-limit + middleware + 22 includes), au-dessus de la cible "slim entry point" mais reste lisible.

### Phase 14 — UI/UX (Feb 19, 2026 — terminée)
Select dropdowns Competition/Model/Gender, Request Removal, Homepage cleanup, header reorg, ImageUpload profil, profils par username.

### Phase 15 — API-Football + Média Freebox (en cours, 08/04/2026)

**Sprint 1 — Seeds (PARTIEL)**
- [x] `seed_leagues_apifootball.py` exécuté (15 inserts + 12 updates / 27 ligues cibles).
- [x] `seed_confederations.py` exécuté.
- [ ] `seed_teams_apifootball.py` — à écrire.
- [ ] `seed_players_apifootball.py` — à écrire.

**Architecture média centralisée — DONE**
- `download_and_store()` + route `POST /api/upload/from-url` opérationnelles.
- Receiver Freebox + `/api/images/...` proxy + vhost `media.topkit.app` en prod.

**Sprint 2 — Recherche enrichie (PARTIEL)**
- [x] Routers `apifootball_search`, `players_api`, `teams_api`, `leagues_api` + cache mémoire 24h.
- [x] Career chart joueur (`players_chart.py` + SVG area chart front).
- [x] Score /100 joueur + breakdown.
- [ ] Migration `logo_url` externes API-Football → Freebox pour les ligues seedées.
- [ ] Enrichissement batch des joueurs existants sans `flocking_player_id`.

## 6. Dette technique connue (07/05/2026)

Reportée d'un audit complet du repo. Ces points doivent être adressés avant nouvelles features lourdes.

### 6.1 Sécurité — Vague 1 (en cours)
- [ ] Routes `POST /api/{teams,leagues,brands,players}` non-pending sans auth → exiger rôle modérateur (ou supprimer si redondantes).
- [ ] `POST /api/teams-api/upsert` (et homologues) sans auth ni Pydantic → ajouter `get_current_user` + modèle.
- [ ] `DEV_LOGIN=true` court-circuite l'auth → garde `RuntimeError` si `IS_PRODUCTION` au boot.
- [ ] Régex utilisateur injectées dans Mongo (`$regex`) → helper `safe_regex(s)` avec `re.escape()`.
- [ ] `RECEIVER_SECRET` defaut `"changeme"` → refuser ce fallback au boot.
- [ ] `Db_topkit-Data.csv` versionné et embarqué dans l'image Docker → sortir du repo + `.dockerignore`.
- [ ] `MODERATOR_EMAILS` defaut hardcode des emails personnels dans le code public → lire uniquement depuis env, defaut vide.

### 6.2 Architecture
- Doublons `entities.py` ↔ `*_api.py` (teams, leagues, players) → fusionner en un router par domaine avec sous-route `/search` DB-first.
- `kits.py` (989 l) → split `master_kits.py` / `versions.py` / `reviews.py` / `kits_by_entity.py`.
- `entities.py` (856 l) → un router par type ou module générique config-driven.
- Estimation dupliquée Python ↔ JS → exposer `POST /api/estimate` et supprimer la version JS.
- Rate-limit en mémoire process (jamais purgé) → Redis ou drop d'entrées trop vieilles.
- Caches `players_api`/`teams_api` en mémoire process → Redis (mêmes raisons).
- Indexes recréés à chaque startup (drop + create) → `create_index` idempotent ou migration dédiée.
- `Contributions.js` (1228 l, déjà corrompu une fois) → split en sous-composants.

### 6.3 Qualité
- Tests = 0. Cible : pytest sur auth + submissions + estimation + scoring + kits (~30-50 tests golden path).
- Pas de CI. Cible : GitHub Actions lint + pytest sur PR + `npm run build` côté front.
- Pre-commit hook local (py_compile + eslint) — éviterait la moitié des `fix:` du dernier mois.
- `pandas==3.0.0` dans `requirements.txt` (version inexistante) → fix pin.
- `print(...)` debug épars → utiliser `logging`.
- README vide.
- `design_guidelines.json` parle encore de "KitLog" (ancien nom).

## 7. Backlog produit

### P1
- Finir Phase 15 (seeds teams + players + migration `logo_url` Freebox).
- Bulk import CSV/XLSX pour Teams, Leagues, Brands, Players (admin only).
- Vague 1 sécurité (cf. §6.1).
- Pytest minimal + CI (cf. §6.3).

### P2
- Notifications utilisateur sur approbation/refus de ses submissions.
- Admin panel : suppression physique sur approval d'un removal.
- Affichage note /100 sur PlayerDetail (`note_breakdown` déjà committé, intégration React à finir).
- Career chart visible sur PlayerDetail (vérifier intégration finale).
- Enrichissement batch joueurs existants.

### P3
- Page joueur complète : carrière, stats, maillots portés, section aura.
- Page league dédiée (modèle enrichi déjà committé).
- Discussion forums / community page.
- Profils publics, partage de collection.
- Dashboards analytics collection.
- Export collection CSV/PDF.
- Backup automatique MongoDB Atlas.
- Logs centralisés + monitoring 5xx.

### Refactoring (cf. §6.2)
- Fusion `entities.py` ↔ `*_api.py`.
- Split `kits.py`, `entities.py`, `Contributions.js`.
- Centralisation estimation Python.
- Migration rate-limit + caches vers Redis.
