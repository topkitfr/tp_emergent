#!/usr/bin/env python3

"""
Update Endpoint Debug Test

This test specifically debugs the PUT /api/personal-kits/{kit_id} endpoint
to identify why it's returning a 500 error.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "T0p_Mdp_1288*"

class UpdateEndpointDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        
    def authenticate_user(self):
        """Authenticate test user"""
        print("🔐 AUTHENTICATING USER...")
        
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.user_token}"
                })
                
                print(f"✅ Successfully authenticated: {user_info.get('name')} (ID: {self.user_id})")
                return True
            else:
                print(f"❌ Authentication failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def test_update_endpoint_detailed(self):
        """Test update endpoint with detailed debugging"""
        print("\n🔍 TESTING UPDATE ENDPOINT WITH DETAILED DEBUGGING...")
        
        try:
            # Get existing kit
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code != 200:
                print(f"❌ Failed to get owned kits: {response.status_code}")
                return False
            
            owned_kits = response.json()
            if not owned_kits:
                print("❌ No owned kits found")
                return False
            
            kit = owned_kits[0]
            kit_id = kit["id"]
            
            print(f"📋 Testing with kit ID: {kit_id}")
            print(f"📋 Current kit data keys: {list(kit.keys())}")
            
            # Test different update payloads to isolate the issue
            test_payloads = [
                {
                    "name": "minimal_update",
                    "data": {"personal_notes": "Test update"}
                },
                {
                    "name": "single_field_update", 
                    "data": {"condition": "good"}
                },
                {
                    "name": "boolean_field_update",
                    "data": {"is_signed": False}
                },
                {
                    "name": "numeric_field_update",
                    "data": {"purchase_price": 100.0}
                },
                {
                    "name": "multiple_fields_update",
                    "data": {
                        "personal_notes": "Updated notes",
                        "condition": "good",
                        "purchase_price": 95.0
                    }
                }
            ]
            
            for test_case in test_payloads:
                print(f"\n🧪 Testing {test_case['name']}...")
                print(f"   Payload: {test_case['data']}")
                
                try:
                    response = self.session.put(
                        f"{BACKEND_URL}/personal-kits/{kit_id}", 
                        json=test_case['data']
                    )
                    
                    print(f"   Status: {response.status_code}")
                    print(f"   Response: {response.text[:500]}")
                    
                    if response.status_code == 200:
                        print(f"   ✅ {test_case['name']} SUCCESS")
                        
                        # Verify the update worked
                        verify_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
                        if verify_response.status_code == 200:
                            updated_kits = verify_response.json()
                            updated_kit = next((k for k in updated_kits if k["id"] == kit_id), None)
                            if updated_kit:
                                print(f"   ✅ Update verified in database")
                                for field, expected_value in test_case['data'].items():
                                    actual_value = updated_kit.get(field)
                                    if actual_value == expected_value:
                                        print(f"   ✅ {field}: {actual_value} (matches expected)")
                                    else:
                                        print(f"   ❌ {field}: {actual_value} (expected {expected_value})")
                            else:
                                print(f"   ❌ Updated kit not found in verification")
                        break  # Stop on first success
                    else:
                        print(f"   ❌ {test_case['name']} FAILED")
                        
                except Exception as e:
                    print(f"   ❌ {test_case['name']} ERROR: {str(e)}")
            
            return True
                
        except Exception as e:
            print(f"❌ Error in update endpoint testing: {str(e)}")
            return False

    def test_individual_field_updates(self):
        """Test updating individual fields to identify problematic ones"""
        print("\n🔬 TESTING INDIVIDUAL FIELD UPDATES...")
        
        try:
            # Get existing kit
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            owned_kits = response.json()
            kit = owned_kits[0]
            kit_id = kit["id"]
            
            # Test each field individually
            individual_tests = [
                {"size": "M"},
                {"condition": "good"},
                {"purchase_price": 75.0},
                {"is_signed": False},
                {"signed_by": "Test Player"},
                {"has_printing": False},
                {"printed_name": "TEST"},
                {"printed_number": 7},
                {"is_worn": True},
                {"personal_notes": "Individual field test"}
            ]
            
            successful_updates = []
            failed_updates = []
            
            for field_update in individual_tests:
                field_name = list(field_update.keys())[0]
                field_value = list(field_update.values())[0]
                
                print(f"\n   Testing {field_name}: {field_value}")
                
                try:
                    response = self.session.put(
                        f"{BACKEND_URL}/personal-kits/{kit_id}",
                        json=field_update
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ {field_name} update SUCCESS")
                        successful_updates.append(field_name)
                    else:
                        print(f"   ❌ {field_name} update FAILED: {response.status_code}")
                        print(f"      Response: {response.text[:200]}")
                        failed_updates.append({
                            "field": field_name,
                            "status": response.status_code,
                            "error": response.text[:200]
                        })
                        
                except Exception as e:
                    print(f"   ❌ {field_name} update ERROR: {str(e)}")
                    failed_updates.append({
                        "field": field_name,
                        "status": "exception",
                        "error": str(e)
                    })
            
            print(f"\n📊 INDIVIDUAL FIELD UPDATE RESULTS:")
            print(f"   Successful updates: {len(successful_updates)}")
            print(f"   Failed updates: {len(failed_updates)}")
            
            if successful_updates:
                print(f"   ✅ Working fields: {', '.join(successful_updates)}")
            
            if failed_updates:
                print(f"   ❌ Problematic fields:")
                for failure in failed_updates:
                    print(f"      - {failure['field']}: {failure['status']} - {failure['error']}")
            
            return len(failed_updates) == 0
            
        except Exception as e:
            print(f"❌ Error in individual field testing: {str(e)}")
            return False

    def run_debug_test(self):
        """Run the complete debug test"""
        print("🚀 STARTING UPDATE ENDPOINT DEBUG TEST")
        print("=" * 80)
        
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed.")
            return False
        
        # Test update endpoint with detailed debugging
        update_test_ok = self.test_update_endpoint_detailed()
        
        # Test individual field updates
        individual_test_ok = self.test_individual_field_updates()
        
        print("\n" + "=" * 80)
        print("📊 DEBUG TEST SUMMARY")
        print("=" * 80)
        
        if update_test_ok and individual_test_ok:
            print("✅ UPDATE ENDPOINT IS WORKING: All tests passed")
        elif update_test_ok:
            print("⚠️ UPDATE ENDPOINT PARTIALLY WORKING: Some individual fields have issues")
        else:
            print("❌ UPDATE ENDPOINT HAS CRITICAL ISSUES: Basic update functionality failing")
        
        return update_test_ok

if __name__ == "__main__":
    debugger = UpdateEndpointDebugger()
    success = debugger.run_debug_test()
    sys.exit(0 if success else 1)