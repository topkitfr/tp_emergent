#!/usr/bin/env python3
"""
Admin Check - Verify pending jerseys and admin functionality
"""

import requests
import json

BASE_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"

def authenticate_admin():
    """Authenticate as admin user"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Try to login as admin
    payload = {
        "email": "topkitfr@gmail.com",
        "password": "adminpass123"
    }
    
    response = session.post(f"{BASE_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if "token" in data:
            session.headers.update({'Authorization': f'Bearer {data["token"]}'})
            print(f"✅ Admin authenticated: {data['user']['email']} (role: {data['user'].get('role', 'unknown')})")
            return session
    
    print(f"❌ Admin authentication failed: {response.status_code}")
    return None

def check_pending_jerseys(session):
    """Check for pending jerseys"""
    response = session.get(f"{BASE_URL}/admin/jerseys/pending")
    
    if response.status_code == 200:
        pending = response.json()
        print(f"📝 Found {len(pending)} pending jerseys")
        
        for jersey in pending:
            print(f"   - {jersey.get('team', 'Unknown')} {jersey.get('season', '')} "
                  f"({jersey.get('reference_number', 'No ref')}) - Status: {jersey.get('status', 'unknown')}")
        
        return pending
    else:
        print(f"❌ Could not get pending jerseys: {response.status_code}")
        return []

def approve_pending_jerseys(session, pending_jerseys):
    """Approve all pending jerseys"""
    approved_count = 0
    
    for jersey in pending_jerseys:
        if jersey.get('status') == 'pending':
            jersey_id = jersey.get('id')
            response = session.post(f"{BASE_URL}/admin/jerseys/{jersey_id}/approve")
            
            if response.status_code == 200:
                approved_count += 1
                print(f"✅ Approved: {jersey.get('team', 'Unknown')} {jersey.get('season', '')} "
                      f"({jersey.get('reference_number', 'No ref')})")
            else:
                print(f"❌ Failed to approve {jersey_id}: {response.status_code}")
    
    print(f"📊 Approved {approved_count} jerseys")
    return approved_count

def check_approved_jerseys():
    """Check approved jerseys visible to public"""
    session = requests.Session()
    response = session.get(f"{BASE_URL}/jerseys")
    
    if response.status_code == 200:
        jerseys = response.json()
        print(f"🌍 Public jerseys visible: {len(jerseys)}")
        
        for jersey in jerseys:
            print(f"   - {jersey.get('team', 'Unknown')} {jersey.get('season', '')} "
                  f"({jersey.get('reference_number', 'No ref')}) - Player: {jersey.get('player', 'N/A')}")
        
        return jerseys
    else:
        print(f"❌ Could not get public jerseys: {response.status_code}")
        return []

def main():
    print("🔍 ADMIN CHECK - PENDING JERSEYS AND APPROVAL SYSTEM")
    print("=" * 60)
    
    # Step 1: Authenticate as admin
    admin_session = authenticate_admin()
    if not admin_session:
        print("Cannot proceed without admin authentication")
        return
    
    # Step 2: Check pending jerseys
    pending_jerseys = check_pending_jerseys(admin_session)
    
    # Step 3: Check current public jerseys
    print("\n📋 Current public jerseys:")
    public_jerseys = check_approved_jerseys()
    
    # Step 4: If there are pending jerseys, approve them
    if pending_jerseys:
        print(f"\n🚀 Approving {len(pending_jerseys)} pending jerseys...")
        approved_count = approve_pending_jerseys(admin_session, pending_jerseys)
        
        if approved_count > 0:
            print("\n📋 Public jerseys after approval:")
            check_approved_jerseys()
    else:
        print("\n✅ No pending jerseys to approve")
    
    print("\n" + "=" * 60)
    print("🏁 ADMIN CHECK COMPLETE")

if __name__ == "__main__":
    main()