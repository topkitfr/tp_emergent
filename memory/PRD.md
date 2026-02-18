# Topkit - Football Jersey Database PRD

## Problem Statement
Create a web application for cataloging football jerseys, similar to Discogs.com but focused on football jerseys. Extended with structured entity system for Teams, Leagues, Brands, and Players.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Auth**: Emergent-managed Google OAuth

## Core Data Model (Hierarchy)

### A. Master Kit (Reference)
| Field | Type | Required |
|-------|------|----------|
| Team (club) | String | Yes |
| Season | Date (YYYY/YYYY) | Yes |
| League | String | No |
| Type | Enum: Home/Away/Third/Fourth/GK/Special/Other | Yes |
| Brand | String | Yes |
| Design | String | No |
| Sponsor | String | No |
| Gender | Enum: Man/Woman/Kid | No |
| Photo Front | Image | Yes |
| team_id | String (FK to teams) | No |
| league_id | String (FK to leagues) | No |
| brand_id | String (FK to brands) | No |

### B. Version (Child of Master Kit)
| Field | Type | Required |
|-------|------|----------|
| Competition | Enum: National Championship/National Cup/Continental Cup/Intercontinental Cup/World Cup | Yes |
| Model | Enum: Authentic/Replica/Other | Yes |
| Code SKU | String | No |
| Code EAN | String | No |
| Photo Front | Image | No |
| Photo Back | Image | No |
| main_player_id | String (FK to players) | No |

### C. Item (Version added to collection)
| Field | Type | Required |
|-------|------|----------|
| Flocking Type | Enum | No |
| Flocking Origin | Enum | No |
| Flocking Detail | String | No |
| Condition (Origin) | Enum | No |
| Physical State | Enum | No |
| Size | String | No |
| Purchase Cost | Number | No |
| Signed | Boolean | No |
| Signed By | String | No |
| Signed Proof | Boolean | No |
| Notes | Text | No |
| Estimated Price | Number | Auto |

### D. Entities (NEW in Phase 11)

#### Teams
| Field | Type | Required |
|-------|------|----------|
| name | String | Yes |
| slug | String (unique, URL-safe) | Auto |
| country | String | No |
| city | String | No |
| founded | Int | No |
| primary_color | String | No |
| secondary_color | String | No |
| crest_url | String | No |
| aka | Array[String] | No |

#### Leagues
| Field | Type | Required |
|-------|------|----------|
| name | String | Yes |
| slug | String (unique) | Auto |
| country_or_region | String | No |
| level | Enum: domestic/continental/international/cup | No |
| organizer | String | No |
| logo_url | String | No |

#### Brands
| Field | Type | Required |
|-------|------|----------|
| name | String | Yes |
| slug | String (unique) | Auto |
| country | String | No |
| founded | Int | No |
| logo_url | String | No |

#### Players
| Field | Type | Required |
|-------|------|----------|
| full_name | String | Yes |
| slug | String (unique) | Auto |
| nationality | String | No |
| birth_year | Int | No |
| positions | Array[String] | No |
| preferred_number | Int | No |
| photo_url | String | No |

## Estimation System (TopKit)
**Formula**: `Estimated Price = Base Price x (1 + sum of coefficients)`
- Base: Authentic=140, Replica=90, Other=60
- Competition, Origin, State, Flocking, Signed, Age coefficients

## User Roles System
| Role | Description | Privileges |
|------|-------------|------------|
| user | Regular user | Vote (1 vote each) |
| moderator | Trusted moderator | Single upvote = instant approval |
| admin | Administrator | Full system access |

**Moderator Emails**: topkitfr@gmail.com

## Completed Phases

### Phase 1-5: Foundation (COMPLETE)
- Full CRUD for Master Kits, Versions, Collection Items
- Google OAuth, Browse/Search, Ratings/Reviews, Wishlist
- Image proxy, Excel import (167 kits), Contributions/Submissions, Autocomplete

### Phase 6-8: Schema + Estimation (COMPLETE)
- Estimation system with breakdown
- Schema cleanup (removed deprecated fields)

### Phase 9: Moderator Privileges (COMPLETE)
- Role system, single-vote approval for moderators

### Phase 10: Default Versions + Display All Fields (COMPLETE)
- Migration for default versions, all fields displayed with "None" fallback

### Phase 11: Structured Entity System (Feb 18, 2026) - COMPLETE
- [x] Renamed app from KitLog to Topkit (logo, navbar, landing, title)
- [x] Created MongoDB collections: teams, leagues, brands, players with Pydantic models
- [x] Added CRUD endpoints: GET/POST/PUT for all 4 entity types with pagination, search, filters
- [x] Entity detail endpoints return linked kits/versions with aggregated stats
- [x] Extended autocomplete to support `type=team|league|brand|player` (returns {id, label, extra})
- [x] Legacy field-based autocomplete preserved (backward compatible)
- [x] Added team_id, league_id, brand_id fields to MasterKitCreate/Out models
- [x] Added main_player_id field to VersionCreate/Out models
- [x] Created MongoDB indexes for all entity collections (slug, name, foreign keys)
- [x] Migration endpoint POST /api/migrate-entities-from-kits (idempotent)
- [x] Migration ran: 11 teams, 5 leagues, 8 brands created from existing 170 kits
- [x] EntityAutocomplete component with create-on-the-fly dialog
- [x] Updated AddJersey.js with entity autocomplete for Team, Brand, League
- [x] Updated Contributions.js with entity autocomplete for Team, Brand, League
- [x] New pages: /teams, /teams/:slug, /leagues, /leagues/:slug, /brands, /brands/:slug, /players, /players/:slug
- [x] Team detail page: header + kits grid with season/type/brand filters
- [x] League detail page: header + kits grid with season/team filters
- [x] Brand detail page: header + kits grid with season/team filters
- [x] Player detail page: header + "Career in Shirts" timeline grouped by team
- [x] Navbar updated with Database dropdown (Teams, Leagues, Brands, Players)
- [x] All existing flows preserved: browse, collection, wishlist, estimation, contributions

### Test Results (Phase 11)
- Backend: 28/28 tests passed (100%)
- Frontend: All pages verified, all entity flows working
- Migration: Idempotent, no duplicates on re-run

## Prioritized Backlog

### P0
- Phase 5: Entity submission moderation (entities created via forms go through moderation)

### P1
- Refactor server.py into APIRouter modules
- Notification system (wishlist updates, contribution votes)
- Seed endpoints for bulk CSV/XLSX import of entities

### P2
- Discussion forums (posts, comments, voting)
- Public profile pages / collection sharing
- Collection analytics dashboards
- Export collection data (CSV/PDF)
