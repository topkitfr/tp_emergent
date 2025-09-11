#!/usr/bin/env python3
"""
Test image upload endpoint with correct format
"""

import requests
import base64
import os
import io
from PIL import Image

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://topkit-bugfixes.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def authenticate_admin():
    """Authenticate admin user and get JWT token"""
    try:
        auth_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            return token
        else:
            print(f"Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def create_test_image():
    """Create a small test image"""
    # Create a 100x100 red square image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_image_upload():
    """Test the image upload endpoint with correct format"""
    print("🧪 Testing Image Upload Endpoint")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Failed to authenticate")
        return False
    
    print("✅ Authentication successful")
    
    # Create test image
    image_data = create_test_image()
    print(f"✅ Created test image ({len(image_data)} bytes)")
    
    # Prepare multipart form data
    files = {
        'file': ('test_image.png', image_data, 'image/png')
    }
    
    data = {
        'entity_type': 'team',
        'generate_variants': 'true'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        # Test image upload
        response = requests.post(f"{API_BASE}/upload/image", files=files, data=data, headers=headers)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Image upload successful!")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Image upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image upload error: {e}")
        return False

def test_contribution_with_image():
    """Test creating a contribution with image data"""
    print("\n🧪 Testing Contribution with Image")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Failed to authenticate")
        return False
    
    # Create test image as base64
    image_data = create_test_image()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Create contribution with image
    contribution_data = {
        "entity_type": "team",
        "entity_id": None,
        "title": "Test Team with Image Upload",
        "description": "Testing image upload in contribution",
        "changes": {
            "name": "Image Upload Test FC",
            "short_name": "IUTC",
            "country": "France",
            "city": "Lyon",
            "founded_year": 2024,
            "team_colors": ["Red", "Blue"]
        },
        "images": [
            {
                "type": "logo",
                "data": image_base64,
                "filename": "test_logo.png"
            }
        ]
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(f"{API_BASE}/contributions-v2/", json=contribution_data, headers=headers)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Contribution with image created successfully!")
            print(f"   Contribution ID: {result.get('id')}")
            
            # Check if the contribution has image data
            contrib_id = result.get('id')
            if contrib_id:
                # Get the contribution back to check image data
                get_response = requests.get(f"{API_BASE}/contributions-v2/", headers=headers)
                if get_response.status_code == 200:
                    contributions = get_response.json()
                    target_contrib = next((c for c in contributions if c.get('id') == contrib_id), None)
                    
                    if target_contrib:
                        has_images = any(target_contrib.get(field) for field in ['images', 'image_urls', 'logo_url'])
                        print(f"   Image data in contribution: {'Yes' if has_images else 'No'}")
                        if has_images:
                            print(f"   Image fields found: {[field for field in ['images', 'image_urls', 'logo_url'] if target_contrib.get(field)]}")
                    else:
                        print("   ⚠️ Could not retrieve created contribution")
            
            return True
        else:
            print(f"❌ Contribution creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Contribution creation error: {e}")
        return False

def check_team_images():
    """Check if teams have image data"""
    print("\n🧪 Checking Team Image Data")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Failed to authenticate")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f"{API_BASE}/teams", headers=headers)
        
        if response.status_code == 200:
            teams = response.json()
            print(f"✅ Found {len(teams)} teams")
            
            teams_with_images = 0
            for team in teams:
                team_name = team.get('name', 'Unknown')
                team_ref = team.get('topkit_reference', 'No ref')
                
                # Check for image fields
                image_fields = ['logo_url', 'image_url', 'photo_url', 'images']
                has_images = any(team.get(field) for field in image_fields)
                
                if has_images:
                    teams_with_images += 1
                    image_data = {field: team.get(field) for field in image_fields if team.get(field)}
                    print(f"   ✅ {team_name} ({team_ref}) - Has images: {image_data}")
                else:
                    print(f"   ❌ {team_name} ({team_ref}) - No images")
            
            print(f"\n📊 Summary: {teams_with_images}/{len(teams)} teams have image data")
            return teams_with_images > 0
        else:
            print(f"❌ Failed to get teams: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking teams: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Image Upload Investigation")
    print("=" * 50)
    
    # Test 1: Direct image upload endpoint
    upload_success = test_image_upload()
    
    # Test 2: Contribution with image
    contrib_success = test_contribution_with_image()
    
    # Test 3: Check existing team images
    team_images = check_team_images()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Image Upload Endpoint: {'✅ Working' if upload_success else '❌ Not Working'}")
    print(f"Contribution with Image: {'✅ Working' if contrib_success else '❌ Not Working'}")
    print(f"Teams with Images: {'✅ Found' if team_images else '❌ None Found'}")
    
    if upload_success and contrib_success:
        print("\n✅ Image upload system is working correctly!")
        print("   The issue may be in the frontend display or image URL generation.")
    elif contrib_success:
        print("\n⚠️ Contribution image upload works, but direct upload endpoint has issues.")
        print("   Images can be uploaded via contributions but may not be processed correctly.")
    else:
        print("\n❌ Image upload system has critical issues!")
        print("   Both direct upload and contribution image upload are not working properly.")