#!/usr/bin/env python3
"""
Detailed Jersey Release Collection Testing
Focus on the specific test flow mentioned in the review request
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://jersey-tracker.preview.emergentagent.com/api"
TEST_USER_EMAIL = "topkitfr@gmail.com"
TEST_USER_PASSWORD = "TopKitSecure789#"

def detailed_test():
    """Run detailed test following the exact review request flow"""
    session = requests.Session()
    
    print("🎯 DETAILED JERSEY RELEASE COLLECTION TESTING")
    print("=" * 60)
    
    # 1. Test authentication with existing user
    print("\n1️⃣ Testing Authentication:")
    response = session.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        user_id = data["user"]["id"]
        session.headers.update({"Authorization": f"Bearer {data['token']}"})
        print(f"✅ Authentication successful: {data['user']['name']} (Role: {data['user']['role']})")
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return
    
    # 2. Get current owned/wanted collections (should be empty initially)
    print("\n2️⃣ Getting Current Collections (should be empty initially):")
    
    owned_response = session.get(f"{BASE_URL}/users/{user_id}/collections/owned")
    wanted_response = session.get(f"{BASE_URL}/users/{user_id}/collections/wanted")
    
    if owned_response.status_code == 200:
        owned_collections = owned_response.json()
        print(f"✅ Owned collections: {len(owned_collections)} items")
        if owned_collections:
            print("   Existing owned items:")
            for item in owned_collections[:3]:  # Show first 3
                jersey_release = item.get('jersey_release', {})
                print(f"   - {jersey_release.get('player_name', 'Unknown')} #{jersey_release.get('player_number', 'N/A')}")
    else:
        print(f"❌ Failed to get owned collections: {owned_response.status_code}")
    
    if wanted_response.status_code == 200:
        wanted_collections = wanted_response.json()
        print(f"✅ Wanted collections: {len(wanted_collections)} items")
        if wanted_collections:
            print("   Existing wanted items:")
            for item in wanted_collections[:3]:  # Show first 3
                jersey_release = item.get('jersey_release', {})
                print(f"   - {jersey_release.get('player_name', 'Unknown')} #{jersey_release.get('player_number', 'N/A')}")
    else:
        print(f"❌ Failed to get wanted collections: {wanted_response.status_code}")
    
    # 3. Create test Jersey Release if needed (from existing master jerseys)
    print("\n3️⃣ Getting Available Jersey Releases:")
    
    releases_response = session.get(f"{BASE_URL}/jersey-releases")
    if releases_response.status_code == 200:
        releases = releases_response.json()
        print(f"✅ Found {len(releases)} jersey releases")
        
        if releases:
            test_release = releases[0]
            print(f"   Using test release: {test_release.get('player_name', 'Unknown')} #{test_release.get('player_number', 'N/A')}")
            print(f"   Release ID: {test_release['id']}")
            print(f"   Release Type: {test_release.get('release_type', 'Unknown')}")
            print(f"   Retail Price: €{test_release.get('retail_price', 'N/A')}")
        else:
            print("❌ No jersey releases available for testing")
            return
    else:
        print(f"❌ Failed to get jersey releases: {releases_response.status_code}")
        return
    
    jersey_release_id = test_release['id']
    
    # 4. Add Jersey Release to owned collection
    print("\n4️⃣ Adding Jersey Release to Owned Collection:")
    
    owned_data = {
        "jersey_release_id": jersey_release_id,
        "collection_type": "owned",
        "size": "L",
        "condition": "mint",
        "purchase_price": 89.99,
        "estimated_value": 95.00
    }
    
    add_owned_response = session.post(f"{BASE_URL}/users/{user_id}/collections", json=owned_data)
    
    if add_owned_response.status_code == 200:
        result = add_owned_response.json()
        owned_collection_id = result.get("collection_id")
        print(f"✅ Added to owned collection successfully")
        print(f"   Collection ID: {owned_collection_id}")
        print(f"   Message: {result.get('message')}")
    else:
        print(f"❌ Failed to add to owned collection: {add_owned_response.status_code} - {add_owned_response.text}")
        owned_collection_id = None
    
    # 5. Add Jersey Release to wanted collection
    print("\n5️⃣ Adding Jersey Release to Wanted Collection:")
    
    wanted_data = {
        "jersey_release_id": jersey_release_id,
        "collection_type": "wanted"
    }
    
    add_wanted_response = session.post(f"{BASE_URL}/users/{user_id}/collections", json=wanted_data)
    
    if add_wanted_response.status_code == 200:
        result = add_wanted_response.json()
        wanted_collection_id = result.get("collection_id")
        print(f"✅ Added to wanted collection successfully")
        print(f"   Collection ID: {wanted_collection_id}")
        print(f"   Message: {result.get('message')}")
    else:
        print(f"❌ Failed to add to wanted collection: {add_wanted_response.status_code} - {add_wanted_response.text}")
        wanted_collection_id = None
    
    # 6. Test updating collection item details
    print("\n6️⃣ Testing Collection Item Update:")
    
    if owned_collection_id:
        update_data = {
            "size": "XL",
            "condition": "near_mint",
            "purchase_price": 85.00,
            "estimated_value": 100.00
        }
        
        update_response = session.put(f"{BASE_URL}/users/{user_id}/collections/{owned_collection_id}", 
                                    json=update_data)
        
        if update_response.status_code == 200:
            result = update_response.json()
            print(f"✅ Collection item updated successfully")
            print(f"   Message: {result.get('message')}")
            print(f"   Updated: Size L→XL, Condition mint→near_mint, Price €89.99→€85.00")
        else:
            print(f"❌ Failed to update collection item: {update_response.status_code} - {update_response.text}")
    else:
        print("⚠️ Skipping update test - no owned collection item to update")
    
    # 7. Test removing from collection
    print("\n7️⃣ Testing Collection Item Removal:")
    
    if wanted_collection_id:
        remove_response = session.delete(f"{BASE_URL}/users/{user_id}/collections/{wanted_collection_id}")
        
        if remove_response.status_code == 200:
            result = remove_response.json()
            print(f"✅ Removed from wanted collection successfully")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Failed to remove from collection: {remove_response.status_code} - {remove_response.text}")
    else:
        print("⚠️ Skipping removal test - no wanted collection item to remove")
    
    # 8. Test vestiaire integration endpoint
    print("\n8️⃣ Testing Vestiaire Integration Endpoint:")
    
    vestiaire_data = {
        "jersey_release_id": jersey_release_id,
        "collection_type": "owned",
        "size": "M",
        "condition": "good",
        "purchase_price": 75.00
    }
    
    vestiaire_response = session.post(f"{BASE_URL}/vestiaire/add-to-collection", json=vestiaire_data)
    
    if vestiaire_response.status_code == 200:
        result = vestiaire_response.json()
        vestiaire_collection_id = result.get("collection_id")
        print(f"✅ Vestiaire integration successful")
        print(f"   Collection ID: {vestiaire_collection_id}")
        print(f"   Message: {result.get('message')}")
        
        # Clean up vestiaire item
        if vestiaire_collection_id:
            session.delete(f"{BASE_URL}/users/{user_id}/collections/{vestiaire_collection_id}")
            print("   ✅ Cleaned up vestiaire test item")
            
    else:
        print(f"❌ Vestiaire integration failed: {vestiaire_response.status_code} - {vestiaire_response.text}")
        if "already in collection" in vestiaire_response.text:
            print("   ℹ️ This is expected if the same jersey release is already in owned collection")
    
    # Final verification - check collections again
    print("\n9️⃣ Final Collections Verification:")
    
    final_owned = session.get(f"{BASE_URL}/users/{user_id}/collections/owned")
    final_wanted = session.get(f"{BASE_URL}/users/{user_id}/collections/wanted")
    
    if final_owned.status_code == 200:
        owned_items = final_owned.json()
        print(f"✅ Final owned collections: {len(owned_items)} items")
        
        if owned_items:
            print("   Current owned items:")
            for item in owned_items:
                jersey_release = item.get('jersey_release', {})
                master_jersey = item.get('master_jersey', {})
                team_info = master_jersey.get('team_info', {})
                print(f"   - {jersey_release.get('player_name', 'Unknown')} #{jersey_release.get('player_number', 'N/A')}")
                print(f"     Team: {team_info.get('name', 'Unknown')}")
                print(f"     Size: {item.get('size', 'N/A')}, Condition: {item.get('condition', 'N/A')}")
                print(f"     Purchase Price: €{item.get('purchase_price', 'N/A')}")
    
    if final_wanted.status_code == 200:
        wanted_items = final_wanted.json()
        print(f"✅ Final wanted collections: {len(wanted_items)} items")
    
    # Cleanup owned item
    if owned_collection_id:
        cleanup_response = session.delete(f"{BASE_URL}/users/{user_id}/collections/{owned_collection_id}")
        if cleanup_response.status_code == 200:
            print("\n🧹 Cleaned up test owned collection item")
    
    print(f"\n🎉 DETAILED TESTING COMPLETED")
    print(f"Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    detailed_test()