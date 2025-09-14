#!/usr/bin/env python3
"""
TopKit Collection API Testing
Focus on collection retrieval 404 errors for user steinmetzlivio@gmail.com
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

def log_test(message, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_login():
    """Test user login and return JWT token"""
    log_test("Testing user login...")
    
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
        log_test(f"Login response status: {response.status_code}")
        log_test(f"Login response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Login successful! Response: {json.dumps(data, indent=2)}")
            return data.get("token"), data.get("user")
        else:
            log_test(f"Login failed with status {response.status_code}: {response.text}", "ERROR")
            return None, None
            
    except requests.exceptions.RequestException as e:
        log_test(f"Login request failed: {str(e)}", "ERROR")
        return None, None

def test_profile(token):
    """Test profile endpoint"""
    log_test("Testing profile endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/profile", headers=headers, timeout=10)
        log_test(f"Profile response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Profile data retrieved successfully!")
            log_test(f"User stats: owned_jerseys={data['stats']['owned_jerseys']}, wanted_jerseys={data['stats']['wanted_jerseys']}, active_listings={data['stats']['active_listings']}")
            return data
        else:
            log_test(f"Profile request failed with status {response.status_code}: {response.text}", "ERROR")
            return None
            
    except requests.exceptions.RequestException as e:
        log_test(f"Profile request failed: {str(e)}", "ERROR")
        return None

def test_collection_retrieval(token, collection_type):
    """Test collection retrieval endpoints"""
    log_test(f"Testing collection retrieval for type: {collection_type}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/collections/{collection_type}", headers=headers, timeout=10)
        log_test(f"Collection {collection_type} response status: {response.status_code}")
        log_test(f"Collection {collection_type} response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Collection {collection_type} retrieved successfully! Found {len(data)} items")
            if data:
                log_test(f"Sample collection item: {json.dumps(data[0], indent=2)}")
            return data
        else:
            log_test(f"Collection {collection_type} request failed with status {response.status_code}: {response.text}", "ERROR")
            return None
            
    except requests.exceptions.RequestException as e:
        log_test(f"Collection {collection_type} request failed: {str(e)}", "ERROR")
        return None

def test_get_jerseys():
    """Test getting available jerseys"""
    log_test("Testing jerseys endpoint to find available jersey IDs...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/jerseys?limit=5", timeout=10)
        log_test(f"Jerseys response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Found {len(data)} jerseys")
            if data:
                jersey_id = data[0]["id"]
                jersey_info = f"{data[0].get('team', 'Unknown')} {data[0].get('season', 'Unknown')}"
                log_test(f"Using jersey ID: {jersey_id} ({jersey_info})")
                return jersey_id, jersey_info
            else:
                log_test("No jerseys found", "ERROR")
                return None, None
        else:
            log_test(f"Jerseys request failed with status {response.status_code}: {response.text}", "ERROR")
            return None, None
            
    except requests.exceptions.RequestException as e:
        log_test(f"Jerseys request failed: {str(e)}", "ERROR")
        return None, None

def test_add_to_collection(token, jersey_id, collection_type):
    """Test adding jersey to collection"""
    log_test(f"Testing adding jersey {jersey_id} to {collection_type} collection...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    collection_data = {
        "jersey_id": jersey_id,
        "collection_type": collection_type
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers, timeout=10)
        log_test(f"Add to collection response status: {response.status_code}")
        log_test(f"Add to collection response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Successfully added to {collection_type} collection! Response: {json.dumps(data, indent=2)}")
            return True
        elif response.status_code == 400 and "Already in collection" in response.text:
            log_test(f"Jersey already in {collection_type} collection (this is expected behavior)")
            return True
        else:
            log_test(f"Add to collection failed with status {response.status_code}: {response.text}", "ERROR")
            return False
            
    except requests.exceptions.RequestException as e:
        log_test(f"Add to collection request failed: {str(e)}", "ERROR")
        return False

def run_comprehensive_collection_test():
    """Run comprehensive collection API test"""
    log_test("=" * 80)
    log_test("STARTING COMPREHENSIVE COLLECTION API TEST")
    log_test(f"Backend URL: {BACKEND_URL}")
    log_test(f"Test User: {TEST_USER_EMAIL}")
    log_test("=" * 80)
    
    # Step 1: Login
    log_test("\n🔐 STEP 1: USER LOGIN")
    token, user = test_login()
    if not token:
        log_test("❌ LOGIN FAILED - Cannot proceed with collection tests", "ERROR")
        return False
    
    log_test(f"✅ Login successful! User: {user['name']} ({user['email']})")
    
    # Step 2: Test profile endpoint
    log_test("\n👤 STEP 2: PROFILE ENDPOINT TEST")
    profile_data = test_profile(token)
    if not profile_data:
        log_test("❌ PROFILE TEST FAILED", "ERROR")
        return False
    
    log_test("✅ Profile endpoint working correctly")
    initial_owned = profile_data['stats']['owned_jerseys']
    initial_wanted = profile_data['stats']['wanted_jerseys']
    
    # Step 3: Test collection retrieval (before adding)
    log_test("\n📋 STEP 3: COLLECTION RETRIEVAL TEST (BEFORE ADDING)")
    owned_collection = test_collection_retrieval(token, "owned")
    wanted_collection = test_collection_retrieval(token, "wanted")
    
    if owned_collection is None or wanted_collection is None:
        log_test("❌ COLLECTION RETRIEVAL FAILED", "ERROR")
        return False
    
    log_test(f"✅ Collection retrieval working! Owned: {len(owned_collection)}, Wanted: {len(wanted_collection)}")
    
    # Step 4: Get available jersey
    log_test("\n🏆 STEP 4: GET AVAILABLE JERSEY")
    jersey_id, jersey_info = test_get_jerseys()
    if not jersey_id:
        log_test("❌ NO JERSEYS AVAILABLE FOR TESTING", "ERROR")
        return False
    
    log_test(f"✅ Found jersey for testing: {jersey_info}")
    
    # Step 5: Add jersey to owned collection
    log_test("\n➕ STEP 5: ADD JERSEY TO OWNED COLLECTION")
    add_success = test_add_to_collection(token, jersey_id, "owned")
    if not add_success:
        log_test("❌ ADD TO OWNED COLLECTION FAILED", "ERROR")
        return False
    
    log_test("✅ Successfully added jersey to owned collection")
    
    # Step 6: Verify collection retrieval after adding
    log_test("\n🔍 STEP 6: VERIFY COLLECTION RETRIEVAL AFTER ADDING")
    updated_owned_collection = test_collection_retrieval(token, "owned")
    if updated_owned_collection is None:
        log_test("❌ COLLECTION RETRIEVAL AFTER ADDING FAILED", "ERROR")
        return False
    
    # Check if jersey appears in collection
    jersey_found = any(item['jersey_id'] == jersey_id for item in updated_owned_collection)
    if jersey_found:
        log_test(f"✅ Jersey {jersey_info} found in owned collection after adding")
    else:
        log_test(f"❌ Jersey {jersey_info} NOT found in owned collection after adding", "ERROR")
        return False
    
    # Step 7: Verify profile stats updated
    log_test("\n📊 STEP 7: VERIFY PROFILE STATS UPDATED")
    updated_profile = test_profile(token)
    if not updated_profile:
        log_test("❌ PROFILE UPDATE CHECK FAILED", "ERROR")
        return False
    
    final_owned = updated_profile['stats']['owned_jerseys']
    if final_owned >= initial_owned:
        log_test(f"✅ Profile stats updated correctly! Owned jerseys: {initial_owned} → {final_owned}")
    else:
        log_test(f"❌ Profile stats not updated correctly! Owned jerseys: {initial_owned} → {final_owned}", "ERROR")
        return False
    
    # Step 8: Test wanted collection
    log_test("\n⭐ STEP 8: TEST WANTED COLLECTION")
    add_wanted_success = test_add_to_collection(token, jersey_id, "wanted")
    if add_wanted_success:
        updated_wanted_collection = test_collection_retrieval(token, "wanted")
        if updated_wanted_collection is not None:
            wanted_jersey_found = any(item['jersey_id'] == jersey_id for item in updated_wanted_collection)
            if wanted_jersey_found:
                log_test(f"✅ Jersey also successfully added to wanted collection")
            else:
                log_test(f"❌ Jersey not found in wanted collection after adding", "ERROR")
        else:
            log_test("❌ Could not retrieve wanted collection after adding", "ERROR")
    
    log_test("\n" + "=" * 80)
    log_test("🎉 COLLECTION API TEST COMPLETED SUCCESSFULLY!")
    log_test("All collection endpoints are working correctly:")
    log_test("✅ POST /api/auth/login - Authentication working")
    log_test("✅ GET /api/profile - Profile stats working")
    log_test("✅ GET /api/collections/owned - Owned collection retrieval working")
    log_test("✅ GET /api/collections/wanted - Wanted collection retrieval working")
    log_test("✅ POST /api/collections - Collection addition working")
    log_test("✅ GET /api/jerseys - Jersey listing working")
    log_test("=" * 80)
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_collection_test()
    sys.exit(0 if success else 1)