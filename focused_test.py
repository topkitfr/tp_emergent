#!/usr/bin/env python3
"""
Focused test for the critical Edit Kit Details validation bug
Testing specifically the condition and physical_state enum field validation errors
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-catalog-app-1.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

def test_critical_enum_validation():
    """Test the critical enum validation bug"""
    session = requests.Session()
    
    # Authenticate
    print("🔐 Authenticating...")
    response = session.post(f"{BACKEND_URL}/auth/login", json=TEST_CREDENTIALS)
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return False
    
    data = response.json()
    session.headers.update({"Authorization": f"Bearer {data['token']}"})
    print(f"✅ Authenticated as {data['user']['email']}")
    
    # Get collection items
    print("\n📦 Getting collection items...")
    response = session.get(f"{BACKEND_URL}/my-collection")
    if response.status_code != 200:
        print(f"❌ Failed to get collection: {response.status_code}")
        return False
    
    collection_items = response.json()
    if not collection_items:
        print("❌ No collection items found")
        return False
    
    item_id = collection_items[0]["id"]
    print(f"✅ Using collection item: {item_id}")
    
    # CRITICAL TEST 1: Empty condition and physical_state (should be omitted)
    print("\n🎯 CRITICAL TEST 1: Empty condition and physical_state fields...")
    update_data = {
        "name_printing": "Test Player",
        "number_printing": "10",
        "is_signed": False,
        "personal_notes": "Testing empty enum fields - CRITICAL BUG FIX"
        # condition and physical_state intentionally omitted
    }
    
    response = session.put(f"{BACKEND_URL}/my-collection/{item_id}", json=update_data)
    
    if response.status_code == 200:
        print("✅ CRITICAL TEST 1 PASSED: Empty enum fields correctly handled - no 422 validation errors")
        result = response.json()
        print(f"   Saved personal_notes: {result.get('personal_notes')}")
    elif response.status_code == 422:
        error_data = response.json()
        print(f"❌ CRITICAL TEST 1 FAILED: 422 validation error still present")
        print(f"   Error details: {error_data}")
        
        # Check if it's specifically condition/physical_state errors
        error_details = error_data.get('detail', [])
        condition_error = any('condition' in str(err) for err in error_details)
        physical_state_error = any('physical_state' in str(err) for err in error_details)
        
        if condition_error:
            print("   🚨 CONDITION ENUM ERROR DETECTED")
        if physical_state_error:
            print("   🚨 PHYSICAL_STATE ENUM ERROR DETECTED")
            
        return False
    else:
        print(f"❌ CRITICAL TEST 1 FAILED: Unexpected response {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # CRITICAL TEST 2: Valid enum values
    print("\n🎯 CRITICAL TEST 2: Valid enum values...")
    update_data = {
        "condition": "match_worn",
        "physical_state": "very_good_condition",
        "is_signed": False,
        "personal_notes": "Testing valid enum values"
    }
    
    response = session.put(f"{BACKEND_URL}/my-collection/{item_id}", json=update_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("condition") == "match_worn" and result.get("physical_state") == "very_good_condition":
            print("✅ CRITICAL TEST 2 PASSED: Valid enum values saved correctly")
        else:
            print(f"❌ CRITICAL TEST 2 FAILED: Enum values not saved correctly")
            print(f"   Expected: condition=match_worn, physical_state=very_good_condition")
            print(f"   Got: condition={result.get('condition')}, physical_state={result.get('physical_state')}")
            return False
    else:
        print(f"❌ CRITICAL TEST 2 FAILED: {response.status_code} - {response.text}")
        return False
    
    # CRITICAL TEST 3: Mix of filled and empty fields
    print("\n🎯 CRITICAL TEST 3: Mix of filled and empty fields...")
    update_data = {
        "name_printing": "Neymar",
        "condition": "match_prepared",
        # physical_state omitted (empty)
        "patches": "Ligue 1",
        # signed_by omitted (empty)
        "is_signed": True,
        "purchase_price": 199.99,
        # purchase_date omitted (empty)
        "personal_notes": "Testing mixed filled/empty fields"
    }
    
    response = session.put(f"{BACKEND_URL}/my-collection/{item_id}", json=update_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ CRITICAL TEST 3 PASSED: Mixed filled/empty fields handled correctly")
        print(f"   Saved fields: name_printing={result.get('name_printing')}, condition={result.get('condition')}")
        print(f"   Purchase price: {result.get('purchase_price')}")
    else:
        print(f"❌ CRITICAL TEST 3 FAILED: {response.status_code} - {response.text}")
        return False
    
    print("\n🎉 ALL CRITICAL TESTS PASSED!")
    print("✅ The Edit Kit Details validation bug fix is working correctly")
    print("✅ Users should no longer get 422 validation errors for empty condition/physical_state fields")
    
    return True

if __name__ == "__main__":
    success = test_critical_enum_validation()
    exit(0 if success else 1)