#!/usr/bin/env python3
"""
Create Reference Kits from existing Master Kits
"""

import requests
import json

# Configuration
BACKEND_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def authenticate_admin():
    """Authenticate admin user and get JWT token"""
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        print(f"✅ Admin authenticated successfully")
        return token
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        return None

def get_master_kits(token):
    """Get existing master kits"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BACKEND_URL}/master-kits", headers=headers)
    
    if response.status_code == 200:
        master_kits = response.json()
        print(f"Found {len(master_kits)} Master Kits")
        return master_kits
    else:
        print(f"❌ Failed to get Master Kits: {response.status_code} - {response.text}")
        return []

def create_reference_kit(token, master_kit):
    """Create a Reference Kit from a Master Kit"""
    headers = {"Authorization": f"Bearer {token}"}
    
    reference_kit_data = {
        "master_kit_id": master_kit['id'],
        "available_sizes": ["S", "M", "L", "XL"],
        "original_retail_price": 89.99,
        "current_market_estimate": 120.00,
        "is_limited_edition": False,
        "official_product_code": f"SKU-{master_kit['topkit_reference']}"
    }
    
    print(f"Creating Reference Kit for Master Kit: {master_kit['topkit_reference']}")
    
    response = requests.post(f"{BACKEND_URL}/reference-kits", json=reference_kit_data, headers=headers)
    
    if response.status_code == 200:
        reference_kit = response.json()
        print(f"✅ Created Reference Kit: {reference_kit.get('topkit_reference')}")
        return reference_kit
    else:
        print(f"❌ Failed to create Reference Kit: {response.status_code} - {response.text}")
        return None

def main():
    print("🏗️  Creating Reference Kits from Master Kits...")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        return
    
    # Get existing Master Kits
    master_kits = get_master_kits(token)
    
    if not master_kits:
        print("❌ No Master Kits found.")
        return
    
    # Show available Master Kits
    print("\nAvailable Master Kits:")
    for kit in master_kits:
        team_name = kit.get('team_info', {}).get('name', 'Unknown Team')
        brand_name = kit.get('brand_info', {}).get('name', 'Unknown Brand')
        print(f"  - {kit['topkit_reference']}: {team_name} x {brand_name} ({kit['season']} {kit['kit_type']})")
    
    # Create Reference Kits
    print("\n👕 Creating Reference Kits...")
    reference_kits = []
    
    for master_kit in master_kits:
        reference_kit = create_reference_kit(token, master_kit)
        if reference_kit:
            reference_kits.append(reference_kit)
    
    print(f"\n✅ Successfully created {len(reference_kits)} Reference Kit(s)")
    
    for kit in reference_kits:
        print(f"   - {kit.get('topkit_reference')}")

if __name__ == "__main__":
    main()