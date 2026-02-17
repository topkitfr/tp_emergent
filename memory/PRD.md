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
- **Item** (Child of Version): Printing/Player, Condition, Size, Value Estimate, Notes, Category

## What's Been Implemented

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

### Phase 2 Features - COMPLETE
- [x] Collection item details (condition, size, value estimate, notes)
- [x] Contributions section with voting system (5 upvotes = auto-approved)
- [x] User profile settings (username, description, profile picture URL)
- [x] Collection privacy toggle (public/private)
- [x] Version estimation statistics (low/avg/high with bar chart)
- [x] Overall collection value estimation (low/avg/high)
- [x] Category-specific value estimations
- [x] Report & correct jerseys (with original vs proposed comparison, community re-voting)
- [x] Inline collection item editing (condition, size, value, notes)

### Phase 3 Features - COMPLETE
- [x] Image upload endpoint (POST /api/upload) with file validation (JPG/PNG/WebP/GIF, max 10MB)
- [x] Static file serving at /api/uploads/ for uploaded images
- [x] Reusable ImageUpload component with dual modes: file upload (click/drag-drop) and URL input
- [x] Add Jersey form updated with ImageUpload
- [x] Contributions submission form updated with ImageUpload
- [x] Image preview with replace/clear overlay on hover
- [x] Multiple file upload endpoint (POST /api/upload/multiple)

### Phase 4 Features (Feb 17, 2026) - COMPLETE
- [x] Correction Reports: Field-by-field comparison table (Field | Current | Proposed) replacing raw JSON
- [x] Pending Submissions: Expandable cards showing all submission fields when clicked
- [x] Button Management: Removed "+ Add Jersey" from header navbar; moved to Contributions page
- [x] Add Jersey form on Contributions creates submissions (pending review) not direct records
- [x] Multi-step Add Jersey form (Step 1: Master Kit, Step 2: Version) with "Use Existing Kit" option
- [x] Jersey Hierarchy: Collection items now have "Printing / Player" field for item-level tracking
- [x] MyCollection: Sheet panel for editing items (replaces inline editing in grid view)
- [x] Jersey Hierarchy summary displayed in edit panel (Master → Version → Item)
- [x] Grid & list views show printing/player info

### Test Results (Phase 4)
- Backend: 100% (9/9 tests passed)
- Frontend: 100% (all features working correctly)

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
- 3D jersey viewer
- Mobile app optimization

## Refactoring Notes
- server.py is monolithic - should split into APIRouter modules (kits, users, submissions, etc.)
