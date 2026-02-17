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
- **Master Kit** (Reference): Club, Season, Type, Brand, Front Photo, Year, Design, Colors, Sponsor, League, Competition, Source URL
- **Version** (Child of Master Kit): Competition, Model, Gender, SKU, Photos
- **Item** (Child of Version): Printing/Player, Condition, Size, Value Estimate, Notes, Category

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

### Phase 4 Features (Feb 17, 2026) - COMPLETE
- [x] Correction Reports: Field-by-field comparison table
- [x] Pending Submissions: Expandable detailed cards
- [x] Button Management: "+ Add Jersey" moved from navbar to Contributions
- [x] Multi-step Add Jersey form creates submissions (pending review)
- [x] Jersey Hierarchy: "Printing/Player" field for collection items
- [x] MyCollection: Sheet panel for editing items with hierarchy summary

### Phase 5: Excel Import (Feb 17, 2026) - COMPLETE
- [x] Cleared old seed data (master_kits, versions, collections, reviews, reports, submissions)
- [x] Imported 167 master kits from Excel file (8 teams × 21 seasons 2005-2026)
- [x] 6 new fields added to master_kit schema: design, colors, sponsor, league, competition, source_url
- [x] Teams: PSG, Marseille, Bayern München, Borussia Dortmund, AC Milan, Inter Milan, FC Barcelona, Real Madrid
- [x] Image proxy endpoint (/api/image-proxy) for footballkitarchive CDN images
- [x] proxyImageUrl utility for all frontend image rendering
- [x] Design and League filter dropdowns added to Browse page
- [x] Colors displayed on jersey cards
- [x] Kit Detail page shows all new fields (design, colors, sponsor, league)
- [x] Import endpoint (/api/import-excel) for re-importing data

### Test Results (Phase 5)
- Backend: 100% (27/27 tests passed)
- Frontend: 100%

## Prioritized Backlog

### P0 (Next Sprint)
- Wishlist functionality with "Add to Wishlist" button on Version pages
- Notification system (wishlist updates, comment replies, contribution votes)

### P1
- Discussion forums (posts, comments, voting)
- User-to-user collection sharing / public profile pages
- Advanced search (fuzzy matching, multi-select filters)

### P2
- Community voting on jersey value estimations
- Collection statistics & analytics dashboards
- Export collection data (CSV/PDF)
- Mobile app optimization

## Refactoring Notes
- server.py is monolithic - should split into APIRouter modules
