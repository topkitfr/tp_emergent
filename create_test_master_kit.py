#!/usr/bin/env python3
"""
Create test Master Kits for testing the Kit hierarchy system
"""

import requests
import json
from datetime import datetime

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
        return token
    else:
        print(f"Authentication failed: {response.status_code} - {response.text}")
        return None

def get_teams_and_brands(token):
    """Get available teams and brands"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get teams
    teams_response = requests.get(f"{BACKEND_URL}/teams", headers=headers)
    brands_response = requests.get(f"{BACKEND_URL}/brands", headers=headers)
    
    teams = teams_response.json() if teams_response.status_code == 200 else []
    brands = brands_response.json() if brands_response.status_code == 200 else []
    
    return teams, brands

def create_master_kit(token, team_id, brand_id):
    """Create a test Master Kit"""
    headers = {"Authorization": f"Bearer {token}"}
    
    master_kit_data = {
        "team_id": team_id,
        "brand_id": brand_id,
        "season": "2024-25",
        "kit_type": "home",
        "model": "authentic",
        "primary_color": "blue",
        "secondary_colors": ["white", "red"],
        "design_name": "Test Kit Design",
        "main_sponsor": "Test Sponsor"
    }
    
    response = requests.post(f"{BACKEND_URL}/master-kits", json=master_kit_data, headers=headers)
    
    if response.status_code == 200:
        master_kit = response.json()
        print(f"✅ Created Master Kit: {master_kit.get('topkit_reference')}")
        return master_kit
    else:
        print(f"❌ Failed to create Master Kit: {response.status_code} - {response.text}")
        return None

def main():
    print("🏗️  Creating test Master Kits...")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Get teams and brands
    teams, brands = get_teams_and_brands(token)
    
    print(f"Found {len(teams)} teams and {len(brands)} brands")
    
    if not teams or not brands:
        print("❌ Need at least one team and one brand to create Master Kits")
        return
    
    # Create a few test Master Kits
    created_kits = []
    
    # Use first available team and brand
    team = teams[0]
    brand = brands[0]
    
    print(f"Using Team: {team.get('name')} (ID: {team.get('id')})")
    print(f"Using Brand: {brand.get('name')} (ID: {brand.get('id')})")
    
    # Create Master Kit
    master_kit = create_master_kit(token, team['id'], brand['id'])
    if master_kit:
        created_kits.append(master_kit)
    
    print(f"\n✅ Created {len(created_kits)} Master Kit(s)")
    
    for kit in created_kits:
        print(f"   - {kit.get('topkit_reference')} ({kit.get('season')} {kit.get('kit_type')})")

if __name__ == "__main__":
    main()