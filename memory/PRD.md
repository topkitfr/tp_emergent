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
    ├── players_scoring.py  # /scoring/players/* (note /100, palmarès, career — DB-only depuis Vague 3)
    └── leagues_api.py      # GET /api/leagues — recherche DB
```

> _Note (09/05/2026) : 22 routers actuellement (10 dans le PRD initial). La Vague 3 (cleanup API-Football) a retiré `apifootball_search.py`, `players_api.py`, `teams_api.py`, `players_chart.py`. Reste l'écart du dédoublonnage entities.py / leagues_api.py à traiter en §6._

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
- **Teams** : name, slug, country, city, founded, primary/secondary_color, crest_url, aka, is_national, stadium_name, stadium_capacity, stadium_surface, stadium_image_url.
- **Leagues** : name, slug, country_or_region, level, organizer, logo_url, scoring_weight, entity_type, scope, region, country_*, gender, level_type, seasons[].
- **Brands** : name, slug, country, founded, logo_url.
- **Players** : full_name, slug, nationality, birth_date, birth_year, positions, preferred_number, photo_url, bio, aura_level, firstname, lastname, height, weight, honours[], individual_awards[], score_palmares, aura, note, gender, level, position_detail, jersey_number, current_team_id.
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

### Phase 15 — API-Football + Média Freebox (ABANDONNÉE, Vague 3 — 09/05/2026)

**Architecture média centralisée — DONE et conservée**
- `download_and_store()` + route `POST /api/upload/from-url` opérationnelles.
- Receiver Freebox + `/api/images/...` proxy + vhost `media.topkit.app` en prod.
- Sert maintenant uniquement les uploads manuels (admin / scripts d'import internes).

**Sprint 1 — Seeds API-Football : ABANDONNÉ**
- `seed_leagues_apifootball.py` retiré du repo.
- `seed_teams_apifootball.py` / `seed_players_apifootball.py` ne seront pas écrits.

**Sprint 2 — Recherche enrichie : ABANDONNÉ**
- Routers `apifootball_search`, `players_api`, `teams_api`, `players_chart` supprimés.
- `services/thesportsdb.py` (client API + scoring) scindé : la partie scoring est conservée
  dans `services/scoring.py`, le reste (clients HTTP, normalisation, lookup *trophies/transfers/profile*)
  est supprimé.
- `services/normalize_league.py` supprimé.
- POST `/api/leagues/import-from-apifootball` retiré.
- `players_scoring.py` simplifié en DB-only (routes `/full`, `/career`, `/{player_id}`,
  `/{player_id}/aura` conservées ; `/search` et `/enrich` supprimées).
- Champs `apifootball_id` / `apifootball_team_id` / `apifootball_league_id` /
  `apifootball_logo` / `source_payload` retirés des modèles Pydantic et purgés en base via
  `backend/scripts/drop_apifootball_fields.py --apply`.
- Indexes Mongo `apifootball_team_id_1` et `apifootball_league_id_1` droppés au startup.
- Front : `ApiFootballSearch.js`, `CompetitionSelector.js` supprimés ;
  `UnifiedEntitySearch.js` simplifié en DB-only ; `EntityEditDialog`, `AddEntityDialog`,
  `EntityDetailPage`, `PlayerDetail`, `PlayerCard` nettoyés. Bouton « Enrich »,
  graphe carrière (transferts) et bandeau « ID API-Football manquant » supprimés.

**Pourquoi l'abandon** : le quota free 100 req/jour étranglait l'usage réel et la couverture
était incomplète (clubs / nationales mineures, awards individuels). La saisie manuelle via
les fiches `EntityEditDialog` / `AddEntityDialog` (workflow communautaire submission/vote)
remplace la couche d'enrichissement automatique. Le scoring `/100` reste calculé en local
à partir des données saisies (palmarès, awards, aura, kits).

## 6. Dette technique connue (07/05/2026)

Reportée d'un audit complet du repo. Ces points doivent être adressés avant nouvelles features lourdes.

### 6.1 Sécurité — Vague 1 (LIVE en prod, 07/05/2026)
- [x] Routes `POST /api/{teams,leagues,brands,players}` non-pending verrouillées modérateur.
- [x] `DEV_LOGIN=true` court-circuit auth → garde `RuntimeError` si `IS_PRODUCTION` au boot.
- [x] Régex utilisateur injectées dans Mongo (`$regex`) → helper `safe_regex(s)` avec `re.escape()`.
- [x] `RECEIVER_SECRET` defaut `"changeme"` → refus au boot en prod.
- [x] `Db_topkit-Data.csv` sorti du repo + `.dockerignore`.
- [x] `MODERATOR_EMAILS` lu depuis env uniquement.
- ~~`POST /api/teams-api/upsert` à durcir~~ → router supprimé en Vague 3.

### 6.1bis Sécurité — Vague 4 (LIVE en prod, 10/05/2026)
- [x] PAT GitHub en clair dans `.git/config` VM → deploy key SSH read-only (PAT révoqué).
- [x] `.env` / `.env.backend` permissions 644 → 600.
- [x] `API_FOOTBALL_KEY` morte en `.env.backend` → retirée + clé révoquée chez api-sports.io.
- [x] `PGADMIN_*` orphelins (vhost retiré en Vague 3) → retirés des deux `.env*`.
- [x] Service `certbot` du compose orphelin (renew tenu par container ad-hoc qui aurait été tué au prochain `--remove-orphans`) → service compose géré, `restart: unless-stopped`, boucle 12h.
- [x] Bots scannant `/.env`, `/wp-*`, `/.php`, `/ueditor` → `return 444 + access_log off` dans nginx.
- Reste à terme : rotation `MONGO_URL`/`SECRET_KEY`/`RECEIVER_SECRET`/`RESEND_API_KEY` (clear text protégés par 600) → Docker secrets ou vault.

### 6.2 Architecture
- [x] `entities.py` (857 l) splité en 5 routers per-type (`teams.py`, `leagues.py`, `brands.py`, `sponsors.py`, `players.py`) + `entity_workflow.py` (pending/approve/reject/autocomplete) + `_entity_helpers.py` (helpers partagés). 11/05/2026 — commits `c231997a` + `cfd2e4de`. Filet 29 tests dans `tests/test_entities_crud.py` (commit `de9d99ab`).
- Doublon `routers/leagues.py` ↔ `routers/leagues_api.py` (résidu pré-split) : tous deux exposent `GET /api/leagues`. Conservé par ordre d'include (`leagues_router` gagne). Reco : drop `leagues_api.py`.
- `kits.py` (989 l) → split `master_kits.py` / `versions.py` / `reviews.py` / `kits_by_entity.py`.
- Estimation dupliquée Python ↔ JS → exposer `POST /api/estimate` et supprimer la version JS.
- Rate-limit en mémoire process (jamais purgé) → Redis ou drop d'entrées trop vieilles.
- Indexes recréés à chaque startup (drop + create) → `create_index` idempotent ou migration dédiée.
- `Contributions.js` (1228 l, déjà corrompu une fois) → split en sous-composants.

### 6.3 Qualité
- [x] Tests pytest = 63 verts (auth, estimation, security_guards). Étendre à submissions/scoring/kits (Vague 2.5).
- [x] CI GitHub Actions = LIVE (lint + pytest gate avant build/deploy).
- [x] Backup auto Mongo Atlas — `scripts/mongo-backup.sh` quotidien 03:00, rétention 30j, dumps sur NAS Freebox (`/mnt/Freebox-1/backups/mongo/`). Vague 4.
- [x] Bug `restart nginx` ne re-mount pas le bind-mount → CD utilise `up -d --force-recreate --no-deps nginx`. Vague 4.
- [x] Drop collection legacy `kits` (14 330 docs footballkitarchive zombies). Vague 4.
- Pre-commit hook local (py_compile + eslint) — éviterait la moitié des `fix:` du dernier mois.
- `pandas==3.0.0` dans `requirements.txt` (version inexistante) → fix pin.
- `print(...)` debug épars → utiliser `logging`.
- README vide.
- `design_guidelines.json` parle encore de "KitLog" (ancien nom).

## 7. Backlog produit

### P1
- Bulk import CSV/XLSX pour Teams, Leagues, Brands, Players (admin only).
- Refonte saisie manuelle des fiches club / player / league (workflow communautaire renforcé suite cleanup Vague 3).
- Vague 2.5 : étendre la suite tests (submissions, scoring, kits).

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
