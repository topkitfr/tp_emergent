# KitLog - Football Jersey Catalog PRD

## Problem Statement
Create a web application for cataloging football jerseys, similar to Discogs.com but focused on football jerseys instead of music.

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

### B. Version (Child of Master Kit)
| Field | Type | Required |
|-------|------|----------|
| Competition | Enum: National Championship/National Cup/Continental Cup/Intercontinental Cup/World Cup | Yes |
| Model | Enum: Authentic/Replica/Other | Yes |
| Code SKU | String | No |
| Code EAN | String | No |
| Photo Front | Image | No |
| Photo Back | Image | No |

### C. Item (Version added to collection)
| Field | Type | Required |
|-------|------|----------|
| Flocking Type | Enum: Name+Number/Name/Number | No |
| Flocking Origin | Enum: Official/Personalized | No |
| Flocking Detail | String | No |
| Condition (Origin) | Enum: Club Stock/Match Prepared/Match Worn/Training/Shop | No |
| Physical State | Enum: New with tag/Very good/Used/Damaged/Needs restoration | No |
| Size | String | No |
| Purchase Cost | Number (€) | No |
| Signed | Boolean | No |
| Signed By | String (if signed) | No |
| Signed Proof | Boolean (certificate) | No |
| Notes | Text | No |
| Estimated Price | Number (auto-calculated) | Auto |

## Estimation System (TopKit)
**Formula**: `Estimated Price = Base Price × (1 + sum of coefficients)`

| Parameter | Value | Coefficient |
|-----------|-------|-------------|
| **Base - Authentic** | 140€ | — |
| **Base - Replica** | 90€ | — |
| **Base - Other** | 60€ | — |
| Competition: National Championship | | 0.0 |
| Competition: National Cup | | +0.05 |
| Competition: Continental Cup | | +1.0 |
| Competition: Intercontinental Cup | | +1.0 |
| Competition: World Cup | | +1.0 |
| Origin: Club Stock | | +0.5 |
| Origin: Match Prepared | | +1.0 |
| Origin: Match Worn | | +1.5 |
| Origin: Training | | 0.0 |
| Origin: Shop | | 0.0 |
| State: New with tag | | +0.3 |
| State: Very good | | +0.1 |
| State: Used | | 0.0 |
| State: Damaged | | -0.2 |
| State: Needs restoration | | -0.4 |
| Flocking: Official | | +0.15 |
| Flocking: Personalized | | 0.0 |
| Signed | | +1.5 |
| Proof/Certificate | | +1.0 |
| Age | | +0.05/year (max +1.0) |

## Completed Phases

### Phase 1-5: Foundation (COMPLETE)
- Full CRUD for Master Kits, Versions, Collection Items
- Google OAuth, Browse/Search, Ratings/Reviews, Wishlist
- Image proxy, Excel import (167 kits), Contributions/Submissions, Autocomplete

### Phase 6: Schema + Wishlist + Autocomplete (Feb 18, 2026) - COMPLETE

### Phase 7: Estimation System v1 (Feb 18, 2026) - COMPLETE

### Phase 8: Schema Cleanup + Estimation v2 (Feb 18, 2026) - COMPLETE
- [x] Removed deprecated fields from master_kits: year, colors, competition, source_url (167 records migrated)
- [x] Removed gender from versions (moved to master kit level)
- [x] Updated Master Kit model: Team, Season, League, Type, Brand, Design, Sponsor, Gender, Photo Front
- [x] Updated Version Competition to enum: National Championship/National Cup/Continental Cup/Intercontinental Cup/World Cup
- [x] Updated Version Model: Authentic/Replica/Other (added Other with 60€ base)
- [x] Updated estimation coefficients: Competition (0 to +1.0), Origin (Club Stock +0.5, Match Prepared +1.0, Match Worn +1.5), Signed +1.5
- [x] All forms updated consistently: AddJersey, VersionDetail, MyCollection, KitDetail report, Browse filters
- [x] Browse page: Season filter replaces Year filter, no colors on cards
- [x] KitDetail: No Year/Colors, shows Design/Sponsor/League/Gender, report form has all fields
- [x] Real-time EstimationBreakdown with Competition coefficient line

### Test Results (Phase 8)
- Backend: 100% (21/21 tests passed)
- Frontend: 100% (all features verified)

## Prioritized Backlog

### P1
- Notification system (wishlist updates, contribution votes, comments)
- Discussion forums (posts, comments, voting)
- Public profile pages / collection sharing

### P2
- Collection analytics dashboards with charts
- Export collection data (CSV/PDF)
- Mobile app optimization

## Refactoring Notes
- server.py is monolithic (~1200 lines) - should split into APIRouter modules
