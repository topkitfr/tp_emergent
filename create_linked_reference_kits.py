#!/usr/bin/env python3
"""
Create new reference kits properly linked to existing master jerseys
"""

import requests
import json
import os
import uuid
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "topkitfr@gmail.com"  
ADMIN_PASSWORD = "TopKitSecure789#"

def authenticate_admin():
    """Authenticate and get token"""
    try:
        auth_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✅ Admin authenticated")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def get_current_master_jerseys(token):
    """Get current master jerseys"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_BASE}/master-jerseys", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Found {len(data)} master jerseys")
            return data
        else:
            print(f"❌ Failed to get master jerseys")
            return []
            
    except Exception as e:
        print(f"❌ Error getting master jerseys: {e}")
        return []

def create_reference_kit(token, kit_data):
    """Create a reference kit"""
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response = requests.post(f"{API_BASE}/reference-kits", json=kit_data, headers=headers)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Created reference kit: {kit_data.get('topkit_reference')}")
            return True, data
        else:
            print(f"❌ Failed to create reference kit: {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error creating reference kit: {e}")
        return False, None

def main():
    print("🚀 Creating Reference Kits Linked to Existing Master Jerseys")
    print("="*60)
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        return
    
    # Get current master jerseys
    master_jerseys = get_current_master_jerseys(token)
    
    if not master_jerseys:
        print("❌ No master jerseys found")
        return
    
    # Select first 2 master jerseys to create versions for
    target_masters = master_jerseys[:2]
    
    created_count = 0
    
    for i, master in enumerate(target_masters):
        master_id = master['id']
        team_name = master.get('team_info', {}).get('name', 'Unknown Team')
        season = master.get('season', '2024-25')
        jersey_type = master.get('jersey_type', 'home')
        
        print(f"\n📋 Creating reference kits for: {team_name} {season} {jersey_type}")
        print(f"   Master ID: {master_id}")
        
        # Create 2-3 reference kits for this master
        reference_kits = [
            {
                "id": str(uuid.uuid4()),
                "master_kit_id": master_id,
                "available_sizes": ["S", "M", "L", "XL"],
                "available_prints": [
                    {"player_name": "Messi", "number": "10", "price": 15.00},
                    {"player_name": "Ronaldo", "number": "7", "price": 15.00}
                ],
                "original_retail_price": 140.00,
                "current_market_estimate": 160.00,
                "price_range_min": 120.00,
                "price_range_max": 180.00,
                "is_limited_edition": False,
                "topkit_reference": f"TK-REF-NEW{i+1:02d}A",
                "verified_level": "unverified"
            },
            {
                "id": str(uuid.uuid4()),
                "master_kit_id": master_id,
                "available_sizes": ["S", "M", "L", "XL", "XXL"],
                "available_prints": [
                    {"player_name": "Mbappé", "number": "7", "price": 18.00}
                ],
                "original_retail_price": 89.99,
                "current_market_estimate": 95.00,
                "price_range_min": 75.00,
                "price_range_max": 110.00,
                "is_limited_edition": False,
                "topkit_reference": f"TK-REF-NEW{i+1:02d}B",
                "verified_level": "unverified"
            }
        ]
        
        # Add a third kit for the first master jersey
        if i == 0:
            reference_kits.append({
                "id": str(uuid.uuid4()),
                "master_kit_id": master_id,
                "available_sizes": ["M", "L", "XL"],
                "available_prints": [
                    {"player_name": "Benzema", "number": "9", "price": 20.00},
                    {"player_name": "Neymar", "number": "11", "price": 20.00}
                ],
                "original_retail_price": 199.99,
                "current_market_estimate": 220.00,
                "price_range_min": 180.00,
                "price_range_max": 250.00,
                "is_limited_edition": True,
                "topkit_reference": f"TK-REF-NEW{i+1:02d}C", 
                "verified_level": "unverified"
            })
        
        # Create each reference kit
        for kit_data in reference_kits:
            success, created_kit = create_reference_kit(token, kit_data)
            if success:
                created_count += 1
    
    print(f"\n🎉 Successfully created {created_count} reference kits!")
    
    # Test the created reference kits
    if created_count > 0:
        print(f"\n🔍 Testing reference kits for first master jersey...")
        try:
            first_master_id = target_masters[0]['id']
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f"{API_BASE}/reference-kits?master_kit_id={first_master_id}", headers=headers)
            
            if response.status_code == 200:
                linked_kits = response.json()
                print(f"✅ Found {len(linked_kits)} reference kits linked to first master jersey")
                
                if linked_kits:
                    print(f"\n📋 Reference kits for {target_masters[0].get('team_info', {}).get('name', 'Master Jersey')}:")
                    for kit in linked_kits:
                        prints = kit.get('available_prints', [])
                        player_names = [p.get('player_name', 'Unknown') for p in prints]
                        reference = kit.get('topkit_reference', 'No Reference')
                        price = kit.get('original_retail_price', 'No Price')
                        print(f"   - {reference}: {', '.join(player_names)} - ${price}")
            else:
                print(f"❌ Failed to test reference kits: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing reference kits: {e}")
    
    print(f"\n🎉 Reference kits creation completed!")
    print("Now you can test the complete Discogs-like workflow:")
    print("1. Go to Kit Area")
    print("2. Click on the first master jersey")
    print("3. You should see 'Other Versions' section with 3 reference kits")
    print("4. Test 'View All Versions' link")
    print("5. Click on individual versions for detailed view")

if __name__ == "__main__":
    main()