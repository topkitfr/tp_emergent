#!/usr/bin/env python3
"""
Debug Master Kit creation data persistence
"""

import requests
import json

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
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

def get_teams_and_brands(token):
    """Get existing teams and brands"""
    headers = {"Authorization": f"Bearer {token}"}
    
    teams_response = requests.get(f"{BACKEND_URL}/teams", headers=headers)
    brands_response = requests.get(f"{BACKEND_URL}/brands", headers=headers)
    
    teams = teams_response.json() if teams_response.status_code == 200 else []
    brands = brands_response.json() if brands_response.status_code == 200 else []
    
    if teams and brands:
        print(f"Found {len(teams)} teams and {len(brands)} brands")
        print(f"First team: {teams[0]['name']} (ID: {teams[0]['id']})")
        print(f"First brand: {brands[0]['name']} (ID: {brands[0]['id']})")
        return teams[0], brands[0]
    else:
        print("❌ No teams or brands found")
        return None, None

def create_debug_master_kit(token, team, brand):
    """Create a Master Kit with explicit field values for debugging"""
    headers = {"Authorization": f"Bearer {token}"}
    
    master_kit_data = {
        "team_id": team['id'],
        "brand_id": brand['id'],
        "season": "2024-25",
        "kit_type": "home",
        "model": "authentic",
        "primary_color": "blue",
        "secondary_colors": ["white", "red"],
        "design_name": f"Debug Kit {team['name']} x {brand['name']}",
        "main_sponsor": "Debug Sponsor"
    }
    
    print(f"🔧 Creating DEBUG Master Kit with data:")
    print(f"   team_id: {master_kit_data['team_id']}")
    print(f"   brand_id: {master_kit_data['brand_id']}")
    print(f"   season: {master_kit_data['season']}")
    
    response = requests.post(f"{BACKEND_URL}/master-kits", json=master_kit_data, headers=headers)
    
    if response.status_code == 200:
        master_kit = response.json()
        print(f"✅ Created Master Kit: {master_kit.get('topkit_reference')}")
        print(f"   Returned team_id: {master_kit.get('team_id')}")
        print(f"   Returned brand_id: {master_kit.get('brand_id')}")
        return master_kit
    else:
        print(f"❌ Failed to create Master Kit: {response.status_code} - {response.text}")
        return None

def verify_master_kit_in_db(token, reference):
    """Verify the Master Kit was saved correctly in database"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BACKEND_URL}/master-kits", headers=headers)
    
    if response.status_code == 200:
        master_kits = response.json()
        for kit in master_kits:
            if kit.get('topkit_reference') == reference:
                print(f"🔍 Found Master Kit {reference} in database:")
                print(f"   DB team_id: {kit.get('team_id')}")
                print(f"   DB brand_id: {kit.get('brand_id')}")
                print(f"   DB season: {kit.get('season')}")
                print(f"   DB kit_type: {kit.get('kit_type')}")
                return kit
        print(f"❌ Master Kit {reference} not found in database")
        return None
    else:
        print(f"❌ Failed to get Master Kits: {response.status_code} - {response.text}")
        return None

def main():
    print("🔧 DEBUG: Master Kit Creation Data Persistence Test")
    print("=" * 60)
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        return
    
    # Get teams and brands
    team, brand = get_teams_and_brands(token)
    if not team or not brand:
        return
    
    # Create debug Master Kit
    master_kit = create_debug_master_kit(token, team, brand)
    if not master_kit:
        return
    
    # Verify in database
    db_kit = verify_master_kit_in_db(token, master_kit.get('topkit_reference'))
    
    if db_kit:
        # Compare created vs retrieved
        print("\n📊 DATA PERSISTENCE ANALYSIS:")
        print(f"   Created team_id: {team['id']}")
        print(f"   Retrieved team_id: {db_kit.get('team_id')}")
        print(f"   Match: {'✅' if team['id'] == db_kit.get('team_id') else '❌'}")
        
        print(f"   Created brand_id: {brand['id']}")
        print(f"   Retrieved brand_id: {db_kit.get('brand_id')}")
        print(f"   Match: {'✅' if brand['id'] == db_kit.get('brand_id') else '❌'}")

if __name__ == "__main__":
    main()