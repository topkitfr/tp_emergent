# KitLog - Football Jersey Catalog PRD

## Problem Statement
Create a web application for cataloging football jerseys, similar to Discogs.com but focused on football jerseys instead of music.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Auth**: Emergent-managed Google OAuth

## User Personas
1. **Jersey Collector** - Wants to catalog, organize, and showcase their collection
2. **Football Fan** - Wants to browse and discover jerseys from favorite teams
3. **Community Member** - Wants to rate, review, and discuss jerseys

## Core Data Model (Hierarchy)

### A. Master Kit (Reference)
- Team (club), Season, League, Type (Home/Away/Third/Fourth/GK/Special/Other)
- Brand, Sponsor, Gender (Man/Women/Kid)
- Photo Front (required)
- Legacy fields: year, design, colors, competition, source_url

### B. Version (Child of Master Kit)
- Competition (e.g., Champions League 2024/2025)
- Model (Authentic/Replica/Player Issue/Other)
- Code SKU, Code EAN
- Photos upload (front/back)

### C. Item (Version added to collection by users)
- Flocking: type (Name+Number/Name/Number), origin (Official/Perso), detail (text)
- Condition Origin: Club Stock/Match Prepared/Match Worn/Training
- Physical State: New with tag/Very good/Used/Damaged/Needs restoration
- Size, Purchase Cost, Price Estimate, Est. Value
- Signed (yes/no) + By Who (player name)
- Notes, Category

## What's Been Implemented

### MVP Features (Phase 1) - COMPLETE
- [x] Emergent Google OAuth authentication
- [x] Master Kit database with browsing and filtering
- [x] Version system linked to Master Kits
- [x] Browse/Search page with filters (Club, Brand, Type, Year, Design, League)
- [x] Grid/List view toggle
- [x] Kit Detail pages with version listings
- [x] Version Detail pages with full specs
- [x] Personal Collection management (add/remove, categories)
- [x] Rating & Review system (1-5 stars + comments)
- [x] User Profile page with collection stats
- [x] Dark "Stadium Night" theme
- [x] Responsive design
- [x] Landing page with stats

### Phase 2 Features - COMPLETE
- [x] Collection item details (condition, size, value estimate, notes)
- [x] Contributions section with voting system (5 upvotes = auto-approved)
- [x] User profile settings (username, description, profile picture URL)
- [x] Collection privacy toggle (public/private)
- [x] Value estimation statistics
- [x] Report & correct jerseys
- [x] Inline collection item editing

### Phase 3 Features - COMPLETE
- [x] Image upload endpoint with file validation
- [x] Reusable ImageUpload component
- [x] Multiple file upload support

### Phase 4 Features - COMPLETE
- [x] Correction Reports: Field-by-field comparison table
- [x] Pending Submissions: Expandable detailed cards
- [x] Button Management: "+ Add Jersey" moved from navbar to Contributions
- [x] Multi-step Add Jersey form creates submissions (pending review)
- [x] Jersey Hierarchy: "Printing/Player" field for collection items
- [x] MyCollection: Sheet panel for editing items with hierarchy summary

### Phase 5: Excel Import - COMPLETE
- [x] Cleared old seed data and imported 167 master kits from Excel file
- [x] Image proxy endpoint (/api/image-proxy) for footballkitarchive CDN images
- [x] proxyImageUrl utility for all frontend image rendering
- [x] Import endpoint (/api/import-excel) for re-importing data

### Phase 6: Schema Overhaul + Wishlist + Autocomplete (Feb 18, 2026) - COMPLETE
- [x] **Schema Updates - Master Kit**: Added `gender` (Man/Women/Kid) and `sponsor` fields
- [x] **Schema Updates - Version**: Added `ean_code` field, made `gender` optional (moved to Master Kit level)
- [x] **Schema Updates - Item/Collection**: New fields: `flocking_type`, `flocking_origin`, `flocking_detail`, `condition_origin`, `physical_state`, `purchase_cost`, `price_estimate`, `signed`, `signed_by`
- [x] **Wishlist Feature**: Full CRUD - POST/GET/DELETE /api/wishlist + GET /api/wishlist/check/{version_id}
- [x] **Wishlist UI**: Dedicated /wishlist page with grid/list view, toggle button on VersionDetail, navbar link
- [x] **Autocomplete**: GET /api/autocomplete endpoint supporting club, brand, sponsor, league, competition fields
- [x] **AutocompleteInput Component**: Reusable React component with debounced search and dropdown suggestions
- [x] **Updated AddJersey Form**: Team/Brand/Sponsor/League autocomplete, Gender dropdown, removed gender from Version step
- [x] **Updated VersionDetail**: Wishlist toggle button, new collection form with flocking/condition/physical_state/signed/purchase_cost/price_estimate
- [x] **Updated MyCollection Edit Sheet**: All new item fields with full edit capability
- [x] **Updated KitDetail**: Shows gender field when present
- [x] **Filters Endpoint**: Now returns sponsors and genders arrays

### Test Results (Phase 6)
- Backend: 100% (17/17 tests passed)
- Frontend: 100% (all features verified working)

## Prioritized Backlog

### P1
- Notification system (wishlist updates, comment replies, contribution votes)
- Discussion forums (posts, comments, voting)
- User-to-user collection sharing / public profile pages
- Advanced search (fuzzy matching, multi-select filters)

### P2
- Community voting on jersey value estimations
- Collection statistics & analytics dashboards
- Export collection data (CSV/PDF)
- Mobile app optimization

## Refactoring Notes
- server.py is monolithic (~1000 lines) - should split into APIRouter modules
