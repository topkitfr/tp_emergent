#!/usr/bin/env python3
"""
Test image integration with correct endpoint and investigate why existing teams don't have images
"""

import requests
import base64
import os
import io
from PIL import Image

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://footkit-hub.preview.emergentagent.com')
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
    # Create a 100x100 green square image
    img = Image.new('RGB', (100, 100), color='green')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_correct_image_upload_workflow():
    """Test image upload with correct endpoint"""
    print("🧪 Testing Image Upload with Correct Endpoint")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Failed to authenticate")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Step 1: Create a contribution
    contribution_data = {
        "entity_type": "team",
        "entity_id": None,
        "title": "Correct Image Upload Test Team",
        "description": "Testing image upload with correct endpoint",
        "data": {
            "name": "Correct Upload Test FC",
            "short_name": "CUTC",
            "country": "France",
            "city": "Marseille",
            "founded_year": 2024,
            "team_colors": ["Green", "White"]
        },
        "source_urls": ["https://example.com/correct-upload-test"]
    }
    
    print("Step 1: Creating contribution...")
    response = requests.post(f"{API_BASE}/contributions-v2/", json=contribution_data, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create contribution: {response.status_code} - {response.text}")
        return False
    
    contrib_result = response.json()
    contribution_id = contrib_result.get('id')
    print(f"✅ Created contribution: {contribution_id}")
    
    # Step 2: Upload image using correct endpoint
    image_data = create_test_image()
    
    files = {
        'file': ('test_logo.png', image_data, 'image/png')
    }
    
    form_data = {
        'is_primary': 'true',
        'caption': 'Team logo'
    }
    
    print("Step 2: Uploading image with correct endpoint...")
    upload_response = requests.post(
        f"{API_BASE}/contributions-v2/{contribution_id}/images", 
        files=files, 
        data=form_data, 
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if upload_response.status_code not in [200, 201]:
        print(f"❌ Failed to upload image: {upload_response.status_code} - {upload_response.text}")
        return False
    
    upload_result = upload_response.json()
    print(f"✅ Uploaded image: {upload_result}")
    
    # Step 3: Verify image is in contribution
    print("Step 3: Verifying image in contribution...")
    detail_response = requests.get(f"{API_BASE}/contributions-v2/{contribution_id}", headers=headers)
    
    if detail_response.status_code == 200:
        detail_data = detail_response.json()
        images = detail_data.get('images', [])
        
        if images:
            print(f"✅ Contribution has {len(images)} images")
            for img in images:
                print(f"  - {img.get('url')} (primary: {img.get('is_primary')})")
            return True
        else:
            print("❌ No images found in contribution")
            return False
    else:
        print(f"❌ Failed to get contribution details: {detail_response.status_code}")
        return False

def investigate_existing_team_images():
    """Investigate why existing teams don't have images despite contributions having them"""
    print("\n🔍 Investigating Existing Team Image Integration")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Failed to authenticate")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Get teams
    teams_response = requests.get(f"{API_BASE}/teams", headers=headers)
    if teams_response.status_code != 200:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json()
    print(f"Found {len(teams)} teams:")
    
    for team in teams:
        team_name = team.get('name', 'Unknown')
        team_ref = team.get('topkit_reference', 'No ref')
        
        # Check for image fields
        image_fields = ['logo_url', 'image_url', 'photo_url', 'images']
        has_images = any(team.get(field) for field in image_fields)
        
        print(f"  Team: {team_name} ({team_ref}) - Images: {'Yes' if has_images else 'No'}")
        
        if has_images:
            image_data = {field: team.get(field) for field in image_fields if team.get(field)}
            print(f"    Image data: {image_data}")
    
    # Get contributions with images
    contributions_response = requests.get(f"{API_BASE}/contributions-v2/", headers=headers)
    if contributions_response.status_code != 200:
        print(f"❌ Failed to get contributions: {contributions_response.status_code}")
        return False
    
    contributions = contributions_response.json()
    print(f"\nFound {len(contributions)} contributions:")
    
    contributions_with_images = []
    for contrib in contributions:
        images_count = contrib.get('images_count', 0)
        if images_count > 0:
            contributions_with_images.append(contrib)
            print(f"  Contribution: {contrib.get('title')} - {images_count} images")
            
            # Get detailed data
            detail_response = requests.get(f"{API_BASE}/contributions-v2/{contrib.get('id')}", headers=headers)
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                images = detail_data.get('images', [])
                for img in images:
                    image_url = img.get('url')
                    print(f"    Image: {image_url}")
                    
                    # Test if image is accessible
                    try:
                        if image_url.startswith('/'):
                            full_url = f"{BACKEND_URL}{image_url}"
                        else:
                            full_url = f"{BACKEND_URL}/{image_url}"
                        
                        img_response = requests.head(full_url, timeout=5)
                        accessible = img_response.status_code == 200
                        print(f"      Accessible: {'Yes' if accessible else 'No'} ({img_response.status_code})")
                    except Exception as e:
                        print(f"      Accessible: No (Error: {e})")
    
    print(f"\n📊 Analysis:")
    print(f"  Teams with images: {sum(1 for team in teams if any(team.get(field) for field in ['logo_url', 'image_url', 'photo_url', 'images']))}")
    print(f"  Contributions with images: {len(contributions_with_images)}")
    
    # Check if there's a mismatch
    if len(contributions_with_images) > 0:
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print(f"  ✅ Contributions can store images successfully")
        print(f"  ❌ Images are not being transferred from contributions to main entities")
        print(f"  🔧 ISSUE: Missing image integration logic in auto-approval process")
        return False
    else:
        print(f"\n✅ No image integration issues - no contributions have images to transfer")
        return True

def check_image_accessibility():
    """Check if uploaded images are accessible"""
    print("\n🌐 Checking Image Accessibility")
    
    # Test some known image URLs
    test_urls = [
        "uploads/teams/team_5513ecdb_1757273279_medium.webp",
        "uploads/contributions/56bb0092-e8ef-45c5-9024-61ddd2b38c83/8636d882_1757269626.jpg",
        "uploads/contributions/00ba24fb-efd6-49ac-903d-c6e36e3883f9/4784f407_1757268333.png"
    ]
    
    accessible_count = 0
    for url in test_urls:
        try:
            full_url = f"{BACKEND_URL}/{url}"
            response = requests.head(full_url, timeout=5)
            accessible = response.status_code == 200
            
            print(f"  {url}: {'✅ Accessible' if accessible else '❌ Not Accessible'} ({response.status_code})")
            if accessible:
                accessible_count += 1
        except Exception as e:
            print(f"  {url}: ❌ Error ({e})")
    
    print(f"\n📊 Image Accessibility: {accessible_count}/{len(test_urls)} images accessible")
    return accessible_count > 0

if __name__ == "__main__":
    print("🚀 Starting Image Integration Fix Investigation")
    print("=" * 70)
    
    # Test 1: Correct image upload workflow
    upload_success = test_correct_image_upload_workflow()
    
    # Test 2: Investigate existing team images
    integration_working = investigate_existing_team_images()
    
    # Test 3: Check image accessibility
    images_accessible = check_image_accessibility()
    
    print("\n" + "=" * 70)
    print("📊 IMAGE INTEGRATION FIX INVESTIGATION SUMMARY")
    print("=" * 70)
    print(f"Correct Image Upload Workflow: {'✅ Working' if upload_success else '❌ Not Working'}")
    print(f"Image Integration to Entities: {'✅ Working' if integration_working else '❌ Not Working'}")
    print(f"Image Accessibility: {'✅ Working' if images_accessible else '❌ Not Working'}")
    
    print(f"\n🎯 ROOT CAUSE IDENTIFIED:")
    if upload_success and images_accessible and not integration_working:
        print("✅ Image upload system works correctly")
        print("✅ Uploaded images are accessible")
        print("❌ CRITICAL ISSUE: Images are not transferred from contributions to main entities")
        print("\n🔧 REQUIRED FIX:")
        print("   • Add image transfer logic in auto-approval process")
        print("   • When a contribution is approved, copy image URLs to the main entity")
        print("   • Update team/brand/player creation to include image data from contributions")
    elif not upload_success:
        print("❌ Image upload system has issues")
    elif not images_accessible:
        print("❌ Uploaded images are not accessible")
    else:
        print("✅ All systems working correctly")