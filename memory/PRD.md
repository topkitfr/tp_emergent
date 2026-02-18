# Topkit - Football Jersey Database PRD

## Problem Statement
Create a web application for cataloging football jerseys, similar to Discogs.com but focused on football jerseys. Extended with structured entity system for Teams, Leagues, Brands, and Players with moderation workflows.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Auth**: Emergent-managed Google OAuth

## Core Data Model

### Master Kit → Version → Item hierarchy
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
- [x] Extended submissions to accept entity types (team/league/brand/player)
- [x] Entity submissions support mode=create and mode=edit with entity_id
- [x] Approval logic: create mode → creates entity doc; edit mode → patches entity doc
- [x] EntityAutocomplete now creates submissions instead of direct entities
- [x] EntityEditDialog reusable component with full entity fields + ImageUpload
- [x] Suggest Edit button on all entity detail pages (team, league, brand, player)
- [x] Contributions page shows entity submissions with type badges (Team/League/Brand/Player + New/Edit)
- [x] Logo/crest/photo upload support via ImageUpload in EntityEditDialog
- [x] All existing flows preserved: browse, collection, wishlist, estimation, kit contributions

### Test Results (Phase 12)
- Backend: 21/21 tests passed (100%)
- Frontend: All pages verified, entity moderation flows working

## Prioritized Backlog

### P0
- Refactor server.py into APIRouter modules (~1800 lines, needs splitting)

### P1
- Seed endpoints for bulk CSV/XLSX import of entities
- Notification system (wishlist updates, contribution status)

### P2
- Discussion forums
- Public profile pages / collection sharing
- Collection analytics dashboards
- Export collection data (CSV/PDF)
