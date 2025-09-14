#!/usr/bin/env python3
"""
Create test data (Teams, Brands, Master Kits) for testing the Kit hierarchy system
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"
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

def create_team(token, name, country, city):
    """Create a test team"""
    headers = {"Authorization": f"Bearer {token}"}
    
    team_data = {
        "name": name,
        "country": country,
        "city": city,
        "founded_year": 1900,
        "colors": ["blue", "white"]
    }
    
    response = requests.post(f"{BACKEND_URL}/teams", json=team_data, headers=headers)
    
    if response.status_code == 200:
        team = response.json()
        print(f"✅ Created Team: {team.get('name')} ({team.get('topkit_reference')})")
        return team
    else:
        print(f"❌ Failed to create team {name}: {response.status_code} - {response.text}")
        return None

def create_brand(token, name, country):
    """Create a test brand"""
    headers = {"Authorization": f"Bearer {token}"}
    
    brand_data = {
        "name": name,
        "country": country,
        "founded_year": 1970
    }
    
    response = requests.post(f"{BACKEND_URL}/brands", json=brand_data, headers=headers)
    
    if response.status_code == 200:
        brand = response.json()
        print(f"✅ Created Brand: {brand.get('name')} ({brand.get('topkit_reference')})")
        return brand
    else:
        print(f"❌ Failed to create brand {name}: {response.status_code} - {response.text}")
        return None

def create_master_kit(token, team_id, brand_id, season="2024-25", kit_type="home"):
    """Create a test Master Kit"""
    headers = {"Authorization": f"Bearer {token}"}
    
    master_kit_data = {
        "team_id": team_id,
        "brand_id": brand_id,
        "season": season,
        "kit_type": kit_type,
        "model": "authentic",
        "primary_color": "blue",
        "secondary_colors": ["white", "red"],
        "design_name": f"Test {kit_type.title()} Kit",
        "main_sponsor": "Test Sponsor"
    }
    
    response = requests.post(f"{BACKEND_URL}/master-kits", json=master_kit_data, headers=headers)
    
    if response.status_code == 200:
        master_kit = response.json()
        print(f"✅ Created Master Kit: {master_kit.get('topkit_reference')} ({season} {kit_type})")
        return master_kit
    else:
        print(f"❌ Failed to create Master Kit: {response.status_code} - {response.text}")
        return None

def main():
    print("🏗️  Creating test data for Kit hierarchy system...")
    print("=" * 60)
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Create test teams
    print("\n📍 Creating test teams...")
    teams = []
    
    team_data = [
        ("FC Barcelona", "Spain", "Barcelona"),
        ("Paris Saint-Germain", "France", "Paris"),
        ("Manchester United", "England", "Manchester")
    ]
    
    for name, country, city in team_data:
        team = create_team(token, name, country, city)
        if team:
            teams.append(team)
    
    # Create test brands
    print("\n🏷️  Creating test brands...")
    brands = []
    
    brand_data = [
        ("Nike", "USA"),
        ("Adidas", "Germany"),
        ("Puma", "Germany")
    ]
    
    for name, country in brand_data:
        brand = create_brand(token, name, country)
        if brand:
            brands.append(brand)
    
    # Create test Master Kits
    print("\n👕 Creating test Master Kits...")
    master_kits = []
    
    if teams and brands:
        # Create a few Master Kits with different combinations
        kit_combinations = [
            (teams[0], brands[0], "2024-25", "home"),
            (teams[0], brands[0], "2024-25", "away"),
            (teams[1], brands[1], "2024-25", "home"),
            (teams[2], brands[2], "2023-24", "home")
        ]
        
        for team, brand, season, kit_type in kit_combinations:
            master_kit = create_master_kit(token, team['id'], brand['id'], season, kit_type)
            if master_kit:
                master_kits.append(master_kit)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST DATA CREATION SUMMARY")
    print("=" * 60)
    print(f"✅ Created {len(teams)} team(s)")
    print(f"✅ Created {len(brands)} brand(s)")
    print(f"✅ Created {len(master_kits)} Master Kit(s)")
    
    if master_kits:
        print("\n🎯 Master Kits created:")
        for kit in master_kits:
            print(f"   - {kit.get('topkit_reference')}: {kit.get('season')} {kit.get('kit_type')}")
    
    print(f"\n🚀 Ready to test Kit hierarchy system with {len(master_kits)} Master Kit(s)!")

if __name__ == "__main__":
    main()