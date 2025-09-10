#!/usr/bin/env python3
"""
Create Master Kits using existing team and brand IDs
"""

import requests
import json

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"
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
    
    print(f"Found {len(teams)} teams and {len(brands)} brands")
    
    return teams, brands

def create_master_kit(token, team, brand, season="2024-25", kit_type="home"):
    """Create a Master Kit"""
    headers = {"Authorization": f"Bearer {token}"}
    
    master_kit_data = {
        "team_id": team['id'],
        "brand_id": brand['id'],
        "season": season,
        "kit_type": kit_type,
        "model": "authentic",
        "primary_color": "blue",
        "secondary_colors": ["white", "red"],
        "design_name": f"{team['name']} {kit_type.title()} Kit",
        "main_sponsor": "Test Sponsor"
    }
    
    print(f"Creating Master Kit for {team['name']} x {brand['name']} ({season} {kit_type})")
    
    response = requests.post(f"{BACKEND_URL}/master-kits", json=master_kit_data, headers=headers)
    
    if response.status_code == 200:
        master_kit = response.json()
        print(f"✅ Created Master Kit: {master_kit.get('topkit_reference')}")
        return master_kit
    else:
        print(f"❌ Failed to create Master Kit: {response.status_code} - {response.text}")
        return None

def main():
    print("🏗️  Creating Master Kits with existing team/brand data...")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        return
    
    # Get existing teams and brands
    teams, brands = get_teams_and_brands(token)
    
    if not teams or not brands:
        print("❌ No teams or brands found. Run create_test_data.py first.")
        return
    
    # Show available teams and brands
    print("\nAvailable teams:")
    for team in teams:
        print(f"  - {team['name']} (ID: {team['id']})")
    
    print("\nAvailable brands:")
    for brand in brands:
        print(f"  - {brand['name']} (ID: {brand['id']})")
    
    # Create Master Kits
    print("\n👕 Creating Master Kits...")
    master_kits = []
    
    # Create different combinations
    combinations = [
        (teams[0], brands[0], "2024-25", "home"),
        (teams[0], brands[0], "2024-25", "away"),
        (teams[1], brands[1], "2024-25", "home"),
    ]
    
    for team, brand, season, kit_type in combinations:
        master_kit = create_master_kit(token, team, brand, season, kit_type)
        if master_kit:
            master_kits.append(master_kit)
    
    print(f"\n✅ Successfully created {len(master_kits)} Master Kit(s)")
    
    for kit in master_kits:
        print(f"   - {kit.get('topkit_reference')}: {kit.get('season')} {kit.get('kit_type')}")

if __name__ == "__main__":
    main()