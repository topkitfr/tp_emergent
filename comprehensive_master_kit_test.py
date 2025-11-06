#!/usr/bin/env python3
"""
Comprehensive Master Kit FormData Submission Test
Testing all requirements from the review request:

1. Login with emergency.admin@topkit.test / EmergencyAdmin2025!
2. Test Master Kit creation via POST /api/master-kits with FormData:
   - kit_type: "authentic" 
   - club_id: (use an existing club ID from /api/form-data/clubs)
   - kit_style: "home"
   - season: "2024/2025"
   - brand_id: (use existing brand from /api/form-data/brands) 
   - front_photo: test image file
   - back_photo: test image file
3. Verify the endpoint now accepts FormData without UnicodeDecodeError
4. Check that contribution entries are created for moderation dashboard
5. Confirm success response includes topkit_reference and proper message
"""

import requests
import json
import sys
from datetime import datetime
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://kitauth-fix.preview.emergentagent.com/api"

# Test Admin Credentials
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

def create_test_image(width=800, height=600):
    """Create a test image for upload"""
    img = Image.new('RGB', (width, height), color='blue')
    img_buffer = BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    return img_buffer

def main():
    print("🧪 COMPREHENSIVE MASTER KIT FORMDATA SUBMISSION TEST")
    print("=" * 70)
    
    session = requests.Session()
    
    # Step 1: Login with emergency.admin@topkit.test / EmergencyAdmin2025!
    print("\n1️⃣ AUTHENTICATION TEST")
    print("-" * 30)
    print(f"Testing login with: {ADMIN_CREDENTIALS['email']} / {ADMIN_CREDENTIALS['password']}")
    
    response = session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get("token")
        user_data = data.get('user', {})
        session.headers.update({"Authorization": f"Bearer {auth_token}"})
        
        print(f"✅ Authentication successful!")
        print(f"   User ID: {user_data.get('id')}")
        print(f"   Name: {user_data.get('name')}")
        print(f"   Role: {user_data.get('role')}")
    else:
        print(f"❌ Authentication failed - Status {response.status_code}")
        print(f"   Error: {response.text}")
        return False
    
    # Step 2: Get form data (clubs and brands)
    print("\n2️⃣ FORM DATA RETRIEVAL TEST")
    print("-" * 30)
    
    clubs_response = session.get(f"{BACKEND_URL}/form-data/clubs", timeout=10)
    brands_response = session.get(f"{BACKEND_URL}/form-data/brands", timeout=10)
    
    if clubs_response.status_code == 200 and brands_response.status_code == 200:
        clubs = clubs_response.json()
        brands = brands_response.json()
        
        print(f"✅ Form data retrieved successfully!")
        print(f"   Clubs available: {len(clubs)}")
        print(f"   Brands available: {len(brands)}")
        
        if not clubs or not brands:
            print("❌ Insufficient form data for testing")
            return False
            
        # Select first club and brand
        selected_club = clubs[0]
        selected_brand = brands[0]
        
        print(f"   Selected Club: {selected_club['name']} ({selected_club['id']})")
        print(f"   Selected Brand: {selected_brand['name']} ({selected_brand['id']})")
    else:
        print(f"❌ Form data retrieval failed")
        print(f"   Clubs status: {clubs_response.status_code}")
        print(f"   Brands status: {brands_response.status_code}")
        return False
    
    # Step 3: Test Master Kit creation with FormData
    print("\n3️⃣ MASTER KIT FORMDATA CREATION TEST")
    print("-" * 30)
    
    # Create test images
    front_image = create_test_image(800, 600)
    back_image = create_test_image(800, 600)
    
    # Prepare FormData as specified in review request
    form_data = {
        'kit_type': 'authentic',
        'club_id': selected_club['id'],
        'kit_style': 'home',
        'season': '2024/2025',
        'brand_id': selected_brand['id']
    }
    
    # Prepare files
    files = {
        'front_photo': ('front_test.jpg', front_image, 'image/jpeg'),
        'back_photo': ('back_test.jpg', back_image, 'image/jpeg')
    }
    
    print(f"Creating Master Kit with FormData:")
    print(f"   kit_type: {form_data['kit_type']}")
    print(f"   club_id: {form_data['club_id']}")
    print(f"   kit_style: {form_data['kit_style']}")
    print(f"   season: {form_data['season']}")
    print(f"   brand_id: {form_data['brand_id']}")
    print(f"   front_photo: test image file")
    print(f"   back_photo: test image file")
    
    response = session.post(
        f"{BACKEND_URL}/master-kits",
        data=form_data,
        files=files,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        master_kit_id = data.get('id')
        
        print(f"✅ Master Kit created successfully!")
        print(f"   Master Kit ID: {master_kit_id}")
        print(f"   TopKit Reference: {data.get('topkit_reference')}")
        print(f"   Status: {data.get('status')}")
        print(f"   Message: {data.get('message')}")
        
        # Verify no UnicodeDecodeError
        if "UnicodeDecodeError" not in response.text:
            print(f"✅ No UnicodeDecodeError - bug fix successful!")
        else:
            print(f"❌ UnicodeDecodeError still present!")
            return False
            
        # Verify response includes topkit_reference and proper message
        if data.get('topkit_reference') and data.get('message'):
            print(f"✅ Response includes topkit_reference and proper message!")
        else:
            print(f"❌ Response missing topkit_reference or message")
            return False
    else:
        error_text = response.text
        print(f"❌ Master Kit creation failed - Status {response.status_code}")
        print(f"   Error: {error_text}")
        
        # Check specifically for UnicodeDecodeError
        if "UnicodeDecodeError" in error_text:
            print(f"❌ UnicodeDecodeError detected - bug not fixed!")
        
        return False
    
    # Step 4: Check contribution entries are created for moderation dashboard
    print("\n4️⃣ MODERATION DASHBOARD INTEGRATION TEST")
    print("-" * 30)
    
    response = session.get(f"{BACKEND_URL}/contributions-v2/", timeout=10)
    
    if response.status_code == 200:
        contributions = response.json()
        
        print(f"✅ Contributions endpoint accessible!")
        print(f"   Total contributions: {len(contributions)}")
        
        # Look for our Master Kit contribution
        master_kit_contributions = [
            c for c in contributions 
            if c.get('entity_type') == 'master_kit' and 
               c.get('entity_id') == master_kit_id
        ]
        
        if master_kit_contributions:
            contribution = master_kit_contributions[0]
            print(f"✅ Master Kit contribution found in moderation dashboard!")
            print(f"   Contribution ID: {contribution.get('id')}")
            print(f"   Entity Type: {contribution.get('entity_type')}")
            print(f"   Status: {contribution.get('status')}")
            print(f"   TopKit Reference: {contribution.get('topkit_reference')}")
        else:
            print(f"❌ Master Kit contribution not found in moderation dashboard")
            print(f"   Looking for Master Kit ID: {master_kit_id}")
            
            # Show available contributions for debugging
            master_kit_contribs = [c for c in contributions if c.get('entity_type') == 'master_kit']
            print(f"   Available master_kit contributions: {len(master_kit_contribs)}")
            for i, contrib in enumerate(master_kit_contribs[:3]):
                print(f"     {i+1}. ID: {contrib.get('id')} - Entity ID: {contrib.get('entity_id')}")
            
            return False
    else:
        print(f"❌ Contributions endpoint failed - Status {response.status_code}")
        return False
    
    # Final Summary
    print("\n🎉 COMPREHENSIVE TEST RESULTS")
    print("=" * 70)
    print("✅ ALL REQUIREMENTS SUCCESSFULLY TESTED:")
    print("   1. ✅ Login with emergency.admin@topkit.test / EmergencyAdmin2025!")
    print("   2. ✅ Master Kit creation via POST /api/master-kits with FormData")
    print("      - kit_type: 'authentic' ✅")
    print("      - club_id: from /api/form-data/clubs ✅")
    print("      - kit_style: 'home' ✅")
    print("      - season: '2024/2025' ✅")
    print("      - brand_id: from /api/form-data/brands ✅")
    print("      - front_photo: test image file ✅")
    print("      - back_photo: test image file ✅")
    print("   3. ✅ FormData endpoint accepts data without UnicodeDecodeError")
    print("   4. ✅ Contribution entries created for moderation dashboard")
    print("   5. ✅ Success response includes topkit_reference and proper message")
    print("\n🚀 MASTER KIT FORMDATA SUBMISSION BUG FIX: FULLY OPERATIONAL!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)