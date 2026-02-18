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
- Team (club), Season (YEAR/YEAR), League, Type (Home/Away/Third/Fourth/GK/Special/Other)
- Brand, Sponsor, Gender (Man/Woman/Kid)
- Photo Front (required)

### B. Version (Child of Master Kit)
- Competition (e.g., Champions League 2024/2025)
- Model (Authentic/Replica)
- Code SKU, Code EAN
- Photos upload (front/back)

### C. Item (Version added to collection by users)
- Flocking: type (Name+Number/Name/Number), origin (Official/Personalized), detail (text)
- Condition Origin: Club Stock/Match Prepared/Match Worn/Training/Shop
- Physical State: New with tag/Very good/Used/Damaged/Needs restoration
- Size, Purchase Cost
- Signed (yes/no) + By Who + Proof/Certificate
- Notes
- Estimated Price (auto-calculated by TopKit formula)

## Estimation System (TopKit)
**Formula**: `Estimated Price = Base Price × (1 + sum of coefficients)`

| Parameter | Value | Coefficient |
|-----------|-------|-------------|
| **Base - Authentic** | 140€ | — |
| **Base - Replica** | 90€ | — |
| Origin: Club Stock | | +0.2 |
| Origin: Match Prepared | | +0.5 |
| Origin: Match Worn | | +1.0 |
| Origin: Training | | +0.05 |
| Origin: Shop | | 0.0 |
| State: New with tag | | +0.3 |
| State: Very good | | +0.1 |
| State: Used | | 0.0 |
| State: Damaged | | -0.2 |
| State: Needs restoration | | -0.4 |
| Flocking: Official | | +0.15 |
| Flocking: Personalized | | 0.0 |
| Signed | | +1.0 |
| Proof/Certificate | | +1.0 |
| Age | | +0.05/year (max +1.0) |

## What's Been Implemented

### Phase 1-5: COMPLETE (see CHANGELOG.md for details)
- Full CRUD for Master Kits, Versions, Collection Items
- Google OAuth, Browse/Search, Ratings/Reviews
- Image proxy, Excel import (167 kits), Contributions/Submissions

### Phase 6: Schema + Wishlist + Autocomplete (Feb 18, 2026) - COMPLETE
- Schema updates: gender, sponsor on Master Kit; ean_code on Version; flocking/condition/physical_state/signed on Items
- Wishlist CRUD + UI page + toggle button on VersionDetail
- Autocomplete for Team, Brand, Sponsor, League, Competition fields

### Phase 7: Form Updates + Estimation System (Feb 18, 2026) - COMPLETE
- [x] All forms updated with correct enums: Gender (Man/Woman/Kid), Model (Authentic/Replica), Condition Origin (+Shop), Flocking Origin (Official/Personalized)
- [x] Backend estimation endpoint: POST /api/estimate with full coefficient breakdown
- [x] Frontend estimation utility (utils/estimation.js) matching backend formula exactly
- [x] EstimationBreakdown component with real-time dynamic calculation
- [x] Estimation integrated in VersionDetail Add-to-Collection form
- [x] Estimation integrated in MyCollection edit sheet
- [x] signed_proof field for Proof/Certificate bonus
- [x] estimated_price auto-stored on collection items
- [x] All estimation calculations verified (14/14 backend tests, 100% frontend)

### Test Results (Phase 7)
- Backend: 100% (14/14 estimation tests passed)
- Frontend: 100% (all features verified working)

## Prioritized Backlog

### P1
- Notification system (wishlist updates, contribution votes, comments)
- Discussion forums (posts, comments, voting)
- Public profile pages / collection sharing
- Advanced search (fuzzy matching, multi-select filters)

### P2
- Collection analytics dashboards with charts
- Export collection data (CSV/PDF)
- Mobile app optimization

## Refactoring Notes
- server.py is monolithic (~1100 lines) - should split into APIRouter modules
