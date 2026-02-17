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
- **Master Kit** (Reference): Club, Season, Type, Brand, Front Photo, Year
- **Version** (Child of Master Kit): Competition, Model, Gender, SKU, Photos
- **Item** (Child of Version, Phase 2): Printing, Condition, Size, Purchase info

## What's Been Implemented (Feb 17, 2026)

### MVP Features (Phase 1) - COMPLETE
- [x] Emergent Google OAuth authentication
- [x] Master Kit database with 24 seeded kits from popular teams
- [x] Version system (36 seeded versions) linked to Master Kits
- [x] Browse/Search page with filters (Club, Brand, Type, Year)
- [x] Grid/List view toggle
- [x] Kit Detail pages with version listings
- [x] Version Detail pages with full specs
- [x] Personal Collection management (add/remove, categories)
- [x] Rating & Review system (1-5 stars + comments)
- [x] Add Jersey form (multi-step: Master Kit -> Version)
- [x] User Profile page with collection stats
- [x] Dark "Stadium Night" theme
- [x] Responsive design
- [x] Landing page with stats

### Phase 2 Features (Feb 17, 2026) - COMPLETE
- [x] Collection item details (condition, size, value estimate, notes)
- [x] Contributions section with voting system (5 upvotes = auto-approved)
- [x] User profile settings (username, description, profile picture URL)
- [x] Collection privacy toggle (public/private)
- [x] Version estimation statistics (low/avg/high with bar chart)
- [x] Overall collection value estimation (low/avg/high)
- [x] Category-specific value estimations
- [x] Report & correct jerseys (with original vs proposed comparison, community re-voting)
- [x] Inline collection item editing (condition, size, value, notes)

### Test Results
- Backend: 100% (22/22 tests passed)
- Frontend: 95%

## Prioritized Backlog

### P0 (Next Sprint)
- Item-level tracking (Printing, Condition, Size, Purchase price/date, Signed status)
- Wishlist functionality with notifications
- Image upload (not just URL)

### P1
- Discussion forums
- Jersey Value Estimation (community voting)
- Notification system (wishlist updates, comment replies)
- User-to-user collection sharing

### P2
- Advanced search (fuzzy matching, multi-select filters)
- Collection statistics & analytics
- Export collection data
- 3D jersey viewer

## Next Tasks
1. Implement Item-level tracking (child of Version)
2. Add Wishlist feature
3. Build image upload functionality
4. Add discussion forums
5. Implement notification system
