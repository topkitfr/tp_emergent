# Topkit - Football Jersey Database PRD

## Problem Statement
Create a web application for cataloging football jerseys, similar to Discogs.com but focused on football jerseys. Extended with structured entity system for Teams, Leagues, Brands, and Players with moderation workflows.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python) - Modular router architecture
- **Database**: MongoDB
- **Auth**: Emergent-managed Google OAuth

## Backend Structure (Refactored Feb 18, 2026)
```
/app/backend/
├── server.py          # Slim entry point (~75 lines): app, middleware, router includes, startup/shutdown
├── database.py        # MongoDB client + db instance
├── models.py          # All Pydantic models
├── utils.py           # slugify, estimation logic, constants (MODERATOR_EMAILS, thresholds)
├── auth.py            # get_current_user helper + EMERGENT_AUTH_URL
└── routers/
    ├── auth.py        # /api/auth/* - Session, me, logout
    ├── kits.py        # /api/master-kits/*, /api/versions/*
    ├── collections.py # /api/collections/* + stats
    ├── estimation.py  # /api/estimate
    ├── reviews.py     # /api/reviews/*
    ├── submissions.py # /api/submissions/*, /api/reports/* (moderation)
    ├── wishlist.py    # /api/wishlist/*
    ├── entities.py    # /api/teams/*, /api/leagues/*, /api/brands/*, /api/players/*, /api/autocomplete
    ├── uploads.py     # /api/upload/*, /api/image-proxy
    └── admin.py       # /api/stats, /api/users/*, /api/seed, /api/import-excel, migrations
```

## Core Data Model

### Master Kit -> Version -> Item hierarchy
- **Master Kit**: club, season, league, type, brand, design, sponsor, gender, front_photo + team_id, league_id, brand_id (FK)
- **Version**: kit_id, competition, model, sku_code, ean_code, front/back_photo, main_player_id (FK)
- **Item (Collection)**: version_id, flocking, condition, size, purchase_cost, signed, estimated_price

### Entities
- **Teams**: name, slug, country, city, founded, primary/secondary_color, crest_url, aka
- **Leagues**: name, slug, country_or_region, level, organizer, logo_url
- **Brands**: name, slug, country, founded, logo_url
- **Players**: full_name, slug, nationality, birth_year, positions, preferred_number, photo_url

### Submissions System
- Types: master_kit, version, team, league, brand, player
- Modes: create, edit (for entity submissions)
- Approval: 5 community votes or 1 moderator vote

## User Roles
- **user**: Vote on submissions (1 vote)
- **moderator** (topkitfr@gmail.com): Single upvote = instant approval
- **admin**: Full access

## Completed Phases

### Phase 1-10: Foundation through Default Versions (COMPLETE)
- Full CRUD, OAuth, Browse/Search, Reviews, Wishlist, Estimation system
- Schema cleanup, moderator roles, default versions

### Phase 11: Structured Entity System (Feb 18, 2026) - COMPLETE
- Entity CRUD APIs (Teams, Leagues, Brands, Players)
- Entity autocomplete + migration from existing kits
- Entity pages with kits grids and filters
- Navbar Database dropdown, Topkit branding

### Phase 12: Entity Moderation + Logos (Feb 18, 2026) - COMPLETE
- Extended submissions to accept entity types (team/league/brand/player)
- Entity submissions support mode=create and mode=edit with entity_id
- Approval logic: create mode creates entity doc; edit mode patches entity doc
- EntityAutocomplete now creates submissions instead of direct entities
- EntityEditDialog reusable component with full entity fields + ImageUpload
- Suggest Edit button on all entity detail pages
- Contributions page shows entity submissions with type badges
- Logo/crest/photo upload support via ImageUpload in EntityEditDialog

### Phase 13: Backend Refactoring (Feb 18, 2026) - COMPLETE
- Refactored 1907-line server.py monolith into modular FastAPI router architecture
- Created shared modules: database.py, models.py, utils.py, auth.py
- Created 10 dedicated routers under /routers/
- All 35 API tests passed (100%), all frontend pages verified
- Zero breaking changes

### Bug Fix: Estimation & Collection Stats (Feb 18, 2026) - COMPLETE
- Fixed field name mismatch: stats endpoints read `value_estimate` but items stored estimation in `estimated_price`
- Synced all 3 estimation fields (estimated_price, value_estimate, price_estimate) on create/update
- Updated stats, category-stats, and version-estimates endpoints to read `estimated_price` with fallback
- Backfilled existing collection documents
- My Collection now correctly shows Low/Avg/High Est values

## Prioritized Backlog

### P1
- CSV/XLSX bulk import endpoints for Teams, Leagues, Brands, Players

### P2
- Notification system (wishlist updates, contribution status)

### P3
- Discussion forums
- Public profile pages / collection sharing
- Collection analytics dashboards
- Export collection data (CSV/PDF)
