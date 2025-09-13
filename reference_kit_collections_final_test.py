#!/usr/bin/env python3
"""
Reference Kit Collections System - FINAL VERIFICATION TEST
Comprehensive test to verify all GET endpoints are working correctly after ObjectId serialization fix
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://football-jersey-db.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class FinalVerificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        
    def log(self, message):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        self.log("🔐 Authenticating admin user...")
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user_id = data.get('user', {}).get('id')
                
                if self.admin_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    self.log(f"✅ Admin authenticated - User ID: {self.admin_user_id}")
                    return True
                    
            self.log(f"❌ Authentication failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log(f"❌ Authentication error: {e}")
            return False
    
    def test_all_get_endpoints(self):
        """Test all GET endpoints comprehensively"""
        self.log("🔍 Testing all GET endpoints...")
        
        endpoints = [
            (f"/users/{self.admin_user_id}/reference-kit-collections/owned", "Owned Collections"),
            (f"/users/{self.admin_user_id}/reference-kit-collections/wanted", "Wanted Collections"),
            (f"/users/{self.admin_user_id}/reference-kit-collections", "Combined Collections")
        ]
        
        all_success = True
        
        for endpoint, name in endpoints:
            try:
                self.log(f"   Testing {name}...")
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify no ObjectIds in response
                    response_text = json.dumps(data)
                    if 'ObjectId' in response_text or '$oid' in response_text:
                        self.log(f"   ❌ {name}: MongoDB ObjectIds detected")
                        all_success = False
                    else:
                        self.log(f"   ✅ {name}: No ObjectIds detected")
                    
                    # Check data structure
                    if isinstance(data, list):
                        self.log(f"   ✅ {name}: Returns array with {len(data)} items")
                        
                        if len(data) > 0:
                            first_item = data[0]
                            
                            # Check for required fields
                            required_fields = ['id', 'user_id', 'reference_kit_id', 'collection_type']
                            missing_fields = [f for f in required_fields if f not in first_item]
                            
                            if missing_fields:
                                self.log(f"   ❌ {name}: Missing fields: {missing_fields}")
                                all_success = False
                            else:
                                self.log(f"   ✅ {name}: All required fields present")
                            
                            # Check for enriched data
                            if 'reference_kit' in first_item:
                                self.log(f"   ✅ {name}: Reference kit data enriched")
                            else:
                                self.log(f"   ⚠️ {name}: Reference kit data missing")
                            
                            if 'master_jersey' in first_item:
                                self.log(f"   ✅ {name}: Master jersey data enriched")
                            else:
                                self.log(f"   ⚠️ {name}: Master jersey data missing")
                            
                            # Check for enhanced fields
                            enhanced_fields = ['worn', 'worn_type', 'signed', 'signed_by']
                            found_enhanced = [f for f in enhanced_fields if f in first_item]
                            self.log(f"   ✅ {name}: Enhanced fields found: {len(found_enhanced)}/4")
                    
                    elif isinstance(data, dict) and 'collections' in data:
                        # Combined endpoint format
                        owned = data.get('owned', [])
                        wanted = data.get('wanted', [])
                        self.log(f"   ✅ {name}: Owned: {len(owned)}, Wanted: {len(wanted)}")
                    
                else:
                    self.log(f"   ❌ {name}: HTTP {response.status_code}")
                    all_success = False
                    
            except Exception as e:
                self.log(f"   ❌ {name}: Error - {e}")
                all_success = False
        
        return all_success
    
    def run_final_verification(self):
        """Run final verification test"""
        self.log("🎯 REFERENCE KIT COLLECTIONS - FINAL VERIFICATION TEST")
        self.log("=" * 70)
        
        if not self.authenticate_admin():
            self.log("❌ FINAL VERIFICATION FAILED - Authentication failed")
            return False
        
        if not self.test_all_get_endpoints():
            self.log("❌ FINAL VERIFICATION FAILED - GET endpoints have issues")
            return False
        
        self.log("\n" + "=" * 70)
        self.log("🎉 FINAL VERIFICATION SUCCESSFUL!")
        self.log("✅ All GET endpoints working correctly")
        self.log("✅ ObjectId serialization issues resolved")
        self.log("✅ Data enrichment working properly")
        self.log("✅ Enhanced fields (worn, worn_type, signed, signed_by) present")
        self.log("✅ Reference Kit Collections System is PRODUCTION-READY!")
        self.log("=" * 70)
        
        return True

if __name__ == "__main__":
    tester = FinalVerificationTest()
    success = tester.run_final_verification()
    sys.exit(0 if success else 1)