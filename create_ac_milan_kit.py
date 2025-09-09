#!/usr/bin/env python3
"""
Create AC Milan Kit with Uploaded Image
======================================

This script creates a complete AC Milan kit with the provided image:
1. Creates AC Milan team (if needed)
2. Creates Nike brand (if needed) 
3. Creates Master Kit for AC Milan Home 2025-2026
4. Creates Reference Kit with the provided image
"""

import requests
import json
import base64
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-tracker.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# AC Milan jersey image URL from assets
AC_MILAN_IMAGE_URL = "https://customer-assets.emergentagent.com/job_kit-collection-hub/artifacts/a0k1c60h_AC-Milan-2025-2026-maillot-de-foot-domicile.jpg"

class ACMilanKitCreator:
    def __init__(self):
        self.admin_token = None
        self.team_id = None
        self.brand_id = None
        self.master_kit_id = None
        self.reference_kit_id = None
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": "topkitfr@gmail.com", 
                "password": "TopKitSecure789#"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                print(f"✅ Admin authenticated successfully")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def download_and_encode_image(self):
        """Download AC Milan image and encode to base64"""
        try:
            response = requests.get(AC_MILAN_IMAGE_URL)
            if response.status_code == 200:
                image_data = response.content
                base64_image = base64.b64encode(image_data).decode('utf-8')
                # Add data URL prefix for JPEG
                return f"data:image/jpeg;base64,{base64_image}"
            else:
                print(f"❌ Failed to download image: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Image download error: {str(e)}")
            return None

    def create_or_find_team(self):
        """Create AC Milan team or find existing one"""
        headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
        
        # First check if AC Milan already exists
        try:
            response = requests.get(f"{API_BASE}/teams", headers=headers)
            if response.status_code == 200:
                teams = response.json()
                for team in teams:
                    if team.get('name', '').lower() == 'ac milan':
                        self.team_id = team['id']
                        print(f"✅ Found existing AC Milan team: {self.team_id}")
                        return True
        except Exception as e:
            print(f"⚠️ Error checking existing teams: {str(e)}")

        # Create new AC Milan team
        team_data = {
            "name": "AC Milan",
            "short_name": "ACM",
            "country": "Italy",
            "city": "Milan",
            "founded_year": 1899,
            "primary_color": "#cc0000",  # AC Milan red
            "secondary_color": "#000000"  # Black
        }
        
        try:
            response = requests.post(f"{API_BASE}/teams", json=team_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.team_id = result.get('id')
                print(f"✅ Created AC Milan team: {self.team_id}")
                return True
            else:
                print(f"❌ Failed to create team: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Team creation error: {str(e)}")
            return False

    def create_or_find_brand(self):
        """Create Nike brand or find existing one"""
        headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
        
        # First check if Nike already exists
        try:
            response = requests.get(f"{API_BASE}/brands", headers=headers)
            if response.status_code == 200:
                brands = response.json()
                for brand in brands:
                    if brand.get('name', '').lower() == 'nike':
                        self.brand_id = brand['id']
                        print(f"✅ Found existing Nike brand: {self.brand_id}")
                        return True
        except Exception as e:
            print(f"⚠️ Error checking existing brands: {str(e)}")

        # Create new Nike brand
        brand_data = {
            "name": "Nike",
            "country": "United States",
            "founded_year": 1964,
            "website": "https://www.nike.com"
        }
        
        try:
            response = requests.post(f"{API_BASE}/brands", json=brand_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.brand_id = result.get('id')
                print(f"✅ Created Nike brand: {self.brand_id}")
                return True
            else:
                print(f"❌ Failed to create brand: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Brand creation error: {str(e)}")
            return False

    def create_master_kit(self):
        """Create AC Milan Master Kit for 2025-2026 Home"""
        headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
        
        master_kit_data = {
            "team_id": self.team_id,
            "brand_id": self.brand_id,
            "season": "2025-26",
            "jersey_type": "home",
            "design_name": "Home Kit",
            "model": "Authentic",
            "primary_color": "#cc0000",  # AC Milan red
            "secondary_colors": ["#000000", "#ffffff"],  # Black and white
            "main_sponsor": "Emirates",
            "pattern_description": "Classic red and black stripes with modern Nike design elements"
        }
        
        try:
            response = requests.post(f"{API_BASE}/master-jerseys", json=master_kit_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.master_kit_id = result.get('id')
                print(f"✅ Created AC Milan Master Kit: {self.master_kit_id}")
                return True
            else:
                print(f"❌ Failed to create master kit: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Master kit creation error: {str(e)}")
            return False

    def create_reference_kit(self, main_photo_base64):
        """Create Reference Kit with the uploaded AC Milan image"""
        headers = {'Authorization': f'Bearer {self.admin_token}', 'Content-Type': 'application/json'}
        
        # Get competition (Serie A)
        try:
            response = requests.get(f"{API_BASE}/competitions", headers=headers)
            serie_a_id = None
            if response.status_code == 200:
                competitions = response.json()
                for comp in competitions:
                    if 'serie a' in comp.get('competition_name', '').lower():
                        serie_a_id = comp['id']
                        break
                
            if not serie_a_id:
                print("⚠️ Serie A not found, using first available competition")
                if competitions:
                    serie_a_id = competitions[0]['id']
                else:
                    print("❌ No competitions available")
                    return False
                    
        except Exception as e:
            print(f"⚠️ Error getting competitions: {str(e)}")
            return False

        reference_kit_data = {
            "master_kit_id": self.master_kit_id,
            "league_competition": serie_a_id,
            "model": "authentic",
            "is_limited_edition": False,
            "official_product_code": "DH6513-613",
            "barcode": "884726982742",
            "main_photo": main_photo_base64,
            "secondary_photos": []
        }
        
        try:
            response = requests.post(f"{API_BASE}/reference-kits", json=reference_kit_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                self.reference_kit_id = result.get('id')
                print(f"✅ Created AC Milan Reference Kit: {self.reference_kit_id}")
                return True
            else:
                print(f"❌ Failed to create reference kit: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Reference kit creation error: {str(e)}")
            return False

    def run(self):
        """Execute the complete AC Milan kit creation process"""
        print("🚀 Starting AC Milan Kit Creation Process")
        print("=" * 50)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            return False
            
        # Step 2: Download and encode image
        print("\n📥 Downloading AC Milan jersey image...")
        main_photo_base64 = self.download_and_encode_image()
        if not main_photo_base64:
            return False
        print(f"✅ Image encoded successfully ({len(main_photo_base64)} characters)")
        
        # Step 3: Create or find team
        print("\n🏟️ Creating/Finding AC Milan team...")
        if not self.create_or_find_team():
            return False
            
        # Step 4: Create or find brand
        print("\n👕 Creating/Finding Nike brand...")
        if not self.create_or_find_brand():
            return False
            
        # Step 5: Create master kit
        print("\n📋 Creating Master Kit...")
        if not self.create_master_kit():
            return False
            
        # Step 6: Create reference kit with image
        print("\n🖼️ Creating Reference Kit with image...")
        if not self.create_reference_kit(main_photo_base64):
            return False
            
        print("\n" + "=" * 50)
        print("🎉 AC MILAN KIT CREATION COMPLETED SUCCESSFULLY!")
        print(f"✅ Team ID: {self.team_id}")
        print(f"✅ Brand ID: {self.brand_id}")
        print(f"✅ Master Kit ID: {self.master_kit_id}")
        print(f"✅ Reference Kit ID: {self.reference_kit_id}")
        print("\nThe AC Milan 2025-2026 Home Kit is now available in the Kit Store!")
        return True

if __name__ == "__main__":
    creator = ACMilanKitCreator()
    success = creator.run()
    exit(0 if success else 1)