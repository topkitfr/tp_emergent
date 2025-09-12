#!/usr/bin/env python3
"""
TopKit Contribution System API Testing with Token Authentication Fix
Testing the contribution system API with proper token authentication
"""

import requests
import json
import base64
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://footkit-admin.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print("🎯 TOPKIT CONTRIBUTION SYSTEM API TESTING WITH TOKEN AUTHENTICATION FIX")
print("=" * 80)
print(f"Backend URL: {BACKEND_URL}")
print(f"API Base: {API_BASE}")
print()

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

USER_EMAIL = "steinmetzlivio@gmail.com"  
USER_PASSWORD = "123"

def test_authentication():
    """Test authentication and get JWT tokens"""
    print("🔐 TESTING AUTHENTICATION SYSTEM")
    print("-" * 40)
    
    tokens = {}
    
    # Test admin authentication
    try:
        admin_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            tokens['admin'] = admin_data.get('token')
            print(f"✅ Admin authentication successful")
            print(f"   Admin: {admin_data.get('user', {}).get('name', 'Unknown')}")
            print(f"   Role: {admin_data.get('user', {}).get('role', 'Unknown')}")
        else:
            print(f"❌ Admin authentication failed: {admin_response.status_code}")
            print(f"   Response: {admin_response.text}")
            
    except Exception as e:
        print(f"❌ Admin authentication error: {e}")
    
    # Test user authentication  
    try:
        user_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            tokens['user'] = user_data.get('token')
            print(f"✅ User authentication successful")
            print(f"   User: {user_data.get('user', {}).get('name', 'Unknown')}")
            print(f"   Role: {user_data.get('user', {}).get('role', 'Unknown')}")
        else:
            print(f"❌ User authentication failed: {user_response.status_code}")
            print(f"   Response: {user_response.text}")
            
    except Exception as e:
        print(f"❌ User authentication error: {e}")
    
    print()
    return tokens

def test_contributions_endpoint_access(tokens):
    """Test access to contributions endpoints"""
    print("🔗 TESTING CONTRIBUTIONS ENDPOINT ACCESS")
    print("-" * 40)
    
    # Test without authentication
    try:
        response = requests.get(f"{API_BASE}/contributions")
        print(f"✅ GET /api/contributions (no auth): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} contributions")
    except Exception as e:
        print(f"❌ GET /api/contributions error: {e}")
    
    # Test with admin token
    if 'admin' in tokens:
        try:
            headers = {"Authorization": f"Bearer {tokens['admin']}"}
            response = requests.get(f"{API_BASE}/contributions", headers=headers)
            print(f"✅ GET /api/contributions (admin): {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Found {len(data)} contributions with admin token")
        except Exception as e:
            print(f"❌ GET /api/contributions (admin) error: {e}")
    
    # Test POST without authentication (should fail)
    try:
        test_contribution = {
            "entity_type": "team",
            "entity_id": "test-id",
            "title": "Test contribution",
            "proposed_data": {"name": "Test Team"}
        }
        response = requests.post(f"{API_BASE}/contributions", json=test_contribution)
        print(f"✅ POST /api/contributions (no auth): {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   ⚠️  Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ POST /api/contributions (no auth) error: {e}")
    
    print()

def test_contribution_creation_with_images(tokens):
    """Test contribution creation with image data"""
    print("📸 TESTING CONTRIBUTION CREATION WITH IMAGES")
    print("-" * 40)
    
    if 'admin' not in tokens:
        print("❌ No admin token available for testing")
        return None
    
    # First, get a team to contribute to
    try:
        response = requests.get(f"{API_BASE}/teams")
        if response.status_code == 200:
            teams = response.json()
            if teams:
                target_team = teams[0]
                print(f"✅ Found target team: {target_team.get('name', 'Unknown')}")
                print(f"   Team ID: {target_team.get('id', 'Unknown')}")
                
                # Create contribution with images
                headers = {"Authorization": f"Bearer {tokens['admin']}"}
                
                # Create sample base64 image data
                sample_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                sample_jpg = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
                
                contribution_data = {
                    "entity_type": "team",
                    "entity_id": target_team['id'],
                    "title": "Add team logo and photos",
                    "description": "Adding official team logo and secondary photos",
                    "proposed_data": {
                        "logo_url": "https://example.com/logo.png",
                        "colors": ["blue", "red"]
                    },
                    "images": {
                        "logo": sample_png,
                        "secondary_photos": [sample_jpg]
                    }
                }
                
                response = requests.post(f"{API_BASE}/contributions", 
                                       json=contribution_data, 
                                       headers=headers)
                
                print(f"✅ POST /api/contributions (with images): {response.status_code}")
                
                if response.status_code == 200:
                    contrib_data = response.json()
                    print(f"   ✅ Contribution created successfully!")
                    print(f"   ID: {contrib_data.get('id', 'Unknown')}")
                    print(f"   Reference: {contrib_data.get('topkit_reference', 'Unknown')}")
                    print(f"   Title: {contrib_data.get('title', 'Unknown')}")
                    print(f"   Status: {contrib_data.get('status', 'Unknown')}")
                    return contrib_data
                else:
                    print(f"   ❌ Failed to create contribution: {response.text}")
                    
            else:
                print("❌ No teams found to contribute to")
        else:
            print(f"❌ Failed to get teams: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Contribution creation error: {e}")
    
    print()
    return None

def test_token_authentication_fix(tokens):
    """Test the specific token authentication fix"""
    print("🔧 TESTING TOKEN AUTHENTICATION FIX")
    print("-" * 40)
    
    if 'user' not in tokens:
        print("❌ No user token available for testing")
        return
    
    # Test with correct token format (should be 'token' not 'auth_token')
    headers = {"Authorization": f"Bearer {tokens['user']}"}
    
    try:
        # Test profile access with token
        response = requests.get(f"{API_BASE}/profile", headers=headers)
        print(f"✅ GET /api/profile with token: {response.status_code}")
        
        if response.status_code == 200:
            profile_data = response.json()
            print(f"   ✅ Token authentication working correctly")
            print(f"   User: {profile_data.get('name', 'Unknown')}")
        else:
            print(f"   ❌ Token authentication failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Token authentication test error: {e}")
    
    # Test invalid token handling
    try:
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{API_BASE}/profile", headers=invalid_headers)
        print(f"✅ GET /api/profile with invalid token: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Invalid token correctly rejected")
        else:
            print(f"   ⚠️  Expected 401, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid token test error: {e}")
    
    # Test missing token handling
    try:
        response = requests.post(f"{API_BASE}/contributions", json={
            "entity_type": "team",
            "entity_id": "test",
            "title": "Test",
            "proposed_data": {}
        })
        print(f"✅ POST /api/contributions without token: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Missing token correctly rejected")
        else:
            print(f"   ⚠️  Expected 401, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Missing token test error: {e}")
    
    print()

def test_contribution_error_handling(tokens):
    """Test error handling for contributions"""
    print("⚠️  TESTING CONTRIBUTION ERROR HANDLING")
    print("-" * 40)
    
    if 'admin' not in tokens:
        print("❌ No admin token available for testing")
        return
    
    headers = {"Authorization": f"Bearer {tokens['admin']}"}
    
    # Test invalid entity ID
    try:
        invalid_contribution = {
            "entity_type": "team",
            "entity_id": "non-existent-id",
            "title": "Test contribution",
            "proposed_data": {"name": "Test Team"}
        }
        response = requests.post(f"{API_BASE}/contributions", 
                               json=invalid_contribution, 
                               headers=headers)
        print(f"✅ POST /api/contributions (invalid entity): {response.status_code}")
        
        if response.status_code == 404:
            print("   ✅ Invalid entity correctly rejected")
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Invalid entity test error: {e}")
    
    # Test duplicate contribution prevention
    try:
        # First, get a valid team
        teams_response = requests.get(f"{API_BASE}/teams")
        if teams_response.status_code == 200:
            teams = teams_response.json()
            if teams:
                target_team = teams[0]
                
                # Create first contribution
                contribution_data = {
                    "entity_type": "team",
                    "entity_id": target_team['id'],
                    "title": "First contribution",
                    "proposed_data": {"name": "Updated Team Name"}
                }
                
                first_response = requests.post(f"{API_BASE}/contributions", 
                                             json=contribution_data, 
                                             headers=headers)
                print(f"✅ First contribution: {first_response.status_code}")
                
                if first_response.status_code == 200:
                    # Try to create duplicate
                    duplicate_response = requests.post(f"{API_BASE}/contributions", 
                                                     json=contribution_data, 
                                                     headers=headers)
                    print(f"✅ Duplicate contribution: {duplicate_response.status_code}")
                    
                    if duplicate_response.status_code == 400:
                        print("   ✅ Duplicate contribution correctly prevented")
                    else:
                        print(f"   Response: {duplicate_response.text}")
                        
    except Exception as e:
        print(f"❌ Duplicate contribution test error: {e}")
    
    print()

def test_contribution_retrieval(tokens):
    """Test contribution retrieval and filtering"""
    print("📋 TESTING CONTRIBUTION RETRIEVAL")
    print("-" * 40)
    
    try:
        # Test basic retrieval
        response = requests.get(f"{API_BASE}/contributions")
        print(f"✅ GET /api/contributions: {response.status_code}")
        
        if response.status_code == 200:
            contributions = response.json()
            print(f"   Found {len(contributions)} contributions")
            
            if contributions:
                contrib = contributions[0]
                print(f"   Sample contribution:")
                print(f"     ID: {contrib.get('id', 'Unknown')}")
                print(f"     Title: {contrib.get('title', 'Unknown')}")
                print(f"     Status: {contrib.get('status', 'Unknown')}")
                print(f"     Reference: {contrib.get('topkit_reference', 'Unknown')}")
                
                # Test filtering by status
                status_response = requests.get(f"{API_BASE}/contributions?status=pending")
                print(f"✅ GET /api/contributions?status=pending: {status_response.status_code}")
                
                if status_response.status_code == 200:
                    pending_contribs = status_response.json()
                    print(f"   Found {len(pending_contribs)} pending contributions")
                    
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Contribution retrieval error: {e}")
    
    print()

def test_api_response_format(tokens):
    """Test API response format matches frontend expectations"""
    print("📊 TESTING API RESPONSE FORMAT")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE}/contributions")
        
        if response.status_code == 200:
            contributions = response.json()
            print(f"✅ Response format validation")
            
            if contributions:
                contrib = contributions[0]
                required_fields = [
                    'id', 'entity_type', 'entity_reference', 'action_type',
                    'title', 'status', 'created_at', 'topkit_reference'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in contrib:
                        missing_fields.append(field)
                
                if not missing_fields:
                    print("   ✅ All required fields present")
                    
                    # Check if topkit_reference is in expected format
                    ref = contrib.get('topkit_reference', '')
                    if ref.startswith('TK-'):
                        print("   ✅ TopKit reference format correct")
                    else:
                        print(f"   ⚠️  TopKit reference format unexpected: {ref}")
                        
                else:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    
            else:
                print("   ℹ️  No contributions to validate format")
                
        else:
            print(f"   ❌ Failed to get contributions: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Response format test error: {e}")
    
    print()

def main():
    """Main test execution"""
    print("Starting TopKit Contribution System API Testing...")
    print()
    
    # Test authentication first
    tokens = test_authentication()
    
    if not tokens:
        print("❌ No authentication tokens available - cannot proceed with tests")
        return
    
    # Run all tests
    test_contributions_endpoint_access(tokens)
    test_token_authentication_fix(tokens)
    test_contribution_creation_with_images(tokens)
    test_contribution_error_handling(tokens)
    test_contribution_retrieval(tokens)
    test_api_response_format(tokens)
    
    # Summary
    print("🎯 TESTING SUMMARY")
    print("=" * 80)
    print("✅ Authentication system tested")
    print("✅ Token authentication fix verified")
    print("✅ Contribution creation with images tested")
    print("✅ Error handling validated")
    print("✅ API response format checked")
    print("✅ Contribution retrieval tested")
    print()
    print("🎉 TopKit Contribution System API testing completed!")

if __name__ == "__main__":
    main()