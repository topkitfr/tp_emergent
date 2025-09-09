#!/usr/bin/env python3
"""
Test image integration from contributions to main entities
"""

import requests
import base64
import os
import io
from PIL import Image

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-tracker.preview.emergentagent.com')
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
    # Create a 100x100 blue square image
    img = Image.new('RGB', (100, 100), color='blue')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_complete_image_workflow():
    """Test complete image workflow from contribution to entity"""
    print("🧪 Testing Complete Image Integration Workflow")
    
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
        "title": "Image Integration Test Team",
        "description": "Testing complete image integration workflow",
        "data": {
            "name": "Integration Test FC",
            "short_name": "ITC",
            "country": "France",
            "city": "Paris",
            "founded_year": 2024,
            "team_colors": ["Blue", "White"]
        },
        "source_urls": ["https://example.com/integration-test"]
    }
    
    print("Step 1: Creating contribution...")
    response = requests.post(f"{API_BASE}/contributions-v2/", json=contribution_data, headers=headers)
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create contribution: {response.status_code} - {response.text}")
        return False
    
    contrib_result = response.json()
    contribution_id = contrib_result.get('id')
    print(f"✅ Created contribution: {contribution_id}")
    
    # Step 2: Upload image to the contribution
    image_data = create_test_image()
    
    files = {
        'file': ('test_logo.png', image_data, 'image/png')
    }
    
    form_data = {
        'is_primary': 'true'
    }
    
    print("Step 2: Uploading image to contribution...")
    upload_response = requests.post(
        f"{API_BASE}/contributions-v2/{contribution_id}/upload-image", 
        files=files, 
        data=form_data, 
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if upload_response.status_code not in [200, 201]:
        print(f"❌ Failed to upload image: {upload_response.status_code} - {upload_response.text}")
        return False
    
    upload_result = upload_response.json()
    print(f"✅ Uploaded image: {upload_result}")
    
    # Step 3: Check if contribution now has image data
    print("Step 3: Checking contribution image data...")
    contrib_check = requests.get(f"{API_BASE}/contributions-v2/", headers=headers)
    
    if contrib_check.status_code == 200:
        contributions = contrib_check.json()
        target_contrib = next((c for c in contributions if c.get('id') == contribution_id), None)
        
        if target_contrib:
            images_count = target_contrib.get('images_count', 0)
            print(f"✅ Contribution has {images_count} images")
            
            if images_count > 0:
                print("✅ Image successfully associated with contribution")
            else:
                print("❌ Image not found in contribution")
                return False
        else:
            print("❌ Contribution not found")
            return False
    else:
        print(f"❌ Failed to check contributions: {contrib_check.status_code}")
        return False
    
    # Step 4: Approve the contribution (simulate auto-approval)
    print("Step 4: Checking auto-approval settings...")
    settings_response = requests.get(f"{API_BASE}/admin/settings", headers=headers)
    
    if settings_response.status_code == 200:
        settings = settings_response.json()
        auto_approval = settings.get("auto_approval_enabled", False)
        print(f"Auto-approval enabled: {auto_approval}")
        
        if not auto_approval:
            print("Enabling auto-approval for testing...")
            update_settings = {"auto_approval_enabled": True}
            requests.put(f"{API_BASE}/admin/settings", json=update_settings, headers=headers)
    
    # Step 5: Check if team appears in main catalogue with image
    print("Step 5: Checking team integration...")
    teams_response = requests.get(f"{API_BASE}/teams", headers=headers)
    
    if teams_response.status_code == 200:
        teams = teams_response.json()
        target_team = next((t for t in teams if t.get('name') == 'Integration Test FC'), None)
        
        if target_team:
            print(f"✅ Team found in catalogue: {target_team.get('name')}")
            
            # Check for image fields
            image_fields = ['logo_url', 'image_url', 'photo_url', 'images']
            has_images = any(target_team.get(field) for field in image_fields)
            
            if has_images:
                image_data = {field: target_team.get(field) for field in image_fields if target_team.get(field)}
                print(f"✅ Team has image data: {image_data}")
                return True
            else:
                print("❌ Team found but no image data")
                print(f"Team data: {target_team}")
                return False
        else:
            print("❌ Team not found in main catalogue")
            print(f"Available teams: {[t.get('name') for t in teams]}")
            return False
    else:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False

def check_image_processing_in_contributions():
    """Check how images are processed in the contribution system"""
    print("\n🔍 Investigating Image Processing in Contributions")
    
    # Authenticate
    token = authenticate_admin()
    if not token:
        print("❌ Failed to authenticate")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Get all contributions and check for images
    response = requests.get(f"{API_BASE}/contributions-v2/", headers=headers)
    
    if response.status_code == 200:
        contributions = response.json()
        print(f"✅ Found {len(contributions)} contributions")
        
        contributions_with_images = 0
        for contrib in contributions:
            contrib_id = contrib.get('id')
            images_count = contrib.get('images_count', 0)
            
            if images_count > 0:
                contributions_with_images += 1
                print(f"  ✅ {contrib.get('title', 'Unknown')} ({contrib_id}) - {images_count} images")
                
                # Get detailed contribution data
                detail_response = requests.get(f"{API_BASE}/contributions-v2/{contrib_id}", headers=headers)
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    images = detail_data.get('images', [])
                    print(f"    Images: {[img.get('url') for img in images]}")
            else:
                print(f"  ❌ {contrib.get('title', 'Unknown')} ({contrib_id}) - No images")
        
        print(f"\n📊 Summary: {contributions_with_images}/{len(contributions)} contributions have images")
        return contributions_with_images > 0
    else:
        print(f"❌ Failed to get contributions: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Image Integration Investigation")
    print("=" * 60)
    
    # Test 1: Complete image workflow
    workflow_success = test_complete_image_workflow()
    
    # Test 2: Check existing contributions for images
    existing_images = check_image_processing_in_contributions()
    
    print("\n" + "=" * 60)
    print("📊 IMAGE INTEGRATION INVESTIGATION SUMMARY")
    print("=" * 60)
    print(f"Complete Image Workflow: {'✅ Working' if workflow_success else '❌ Not Working'}")
    print(f"Existing Contributions with Images: {'✅ Found' if existing_images else '❌ None Found'}")
    
    if workflow_success:
        print("\n✅ Image integration system is working correctly!")
        print("   Images can be uploaded to contributions and integrated into main entities.")
    else:
        print("\n❌ Image integration system has issues!")
        print("   Images are not being properly integrated from contributions to main entities.")
        print("\n🔧 POTENTIAL ISSUES:")
        print("   • Auto-approval may not be transferring image data")
        print("   • Image integration logic may be missing in entity creation")
        print("   • Image URLs may not be properly mapped between contributions and entities")