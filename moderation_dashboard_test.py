#!/usr/bin/env python3
"""
TopKit Moderation Dashboard Testing Suite - CRITICAL FIXES VERIFICATION

**MODERATION DASHBOARD FIXES TESTING:**
User reported critical issue with moderation dashboard showing inconsistent data:
1. Overview tab shows '30 Pending Review'
2. Pending Review tab shows 'All Caught Up! No contributions pending review'
3. User created brand contribution but can't see it anywhere
4. Clear mismatch between stats and actual displayed data

**MAIN AGENT FIXES TO TEST:**
1. **Fixed Moderation Stats API** - GET /api/contributions-v2/admin/moderation-stats
   - Should now query contributions_v2 collection instead of contributions collection
   - Should return correct pending count from contributions_v2 collection
   
2. **Fixed Status Value Consistency** - Pending contributions API
   - Test GET /api/contributions-v2/?status=pending_review
   - Test GET /api/contributions-v2/?status=pending
   - Should identify which status value is actually used in database
   
3. **Collection Consistency Verification**
   - Confirm moderation stats API and contributions API use same collection
   - Check that 30 vs 0 discrepancy is resolved
   - Verify consistent counts across different endpoints

**TEST CREDENTIALS:**
- Admin: emergency.admin@topkit.test / EmergencyAdmin2025!

**EXPECTED RESULTS:**
- Moderation stats API should return consistent numbers with contributions API
- Should identify which status value ('pending' or 'pending_review') is actually used
- No more discrepancy between overview stats and pending review tab data
- Clear path to resolving the user's reported issue

**PRIORITY: CRITICAL** - This affects core moderation workflow.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration - Use environment variable with fallback
BACKEND_URL = os.environ.get('BACKEND_URL', os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')) + '/api'

# Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

# Rest of the file remains the same...
