#!/usr/bin/env python3
"""
Want List Fix Test - Testing potential solutions for the size requirement issue
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://mongodb-routing.preview.emergentagent.com/api"

# Test credentials
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

class WantListFixTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        
    def authenticate_user(self) -> bool:
        """Authenticate user and get JWT token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({"Authorization": f"Bearer {self.user_token}"})
                print(f"✅ Authenticated as: {user_info.get('name')} (ID: {self.user_id})")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_workaround_solutions(self, reference_kit_id: str):
        """Test potential workaround solutions"""
        
        print(f"\n🔧 TESTING WORKAROUND SOLUTIONS")
        print("=" * 50)
        
        # Solution 1: Use a default "Any" size for wanted collections
        print(f"\n1. Testing 'Any' size as default for wanted collections:")
        data1 = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "wanted",
            "size": "Any"
        }
        
        result1 = self.test_single_request(data1, "Default 'Any' size")
        
        # Solution 2: Use "TBD" (To Be Determined) size
        print(f"\n2. Testing 'TBD' size for wanted collections:")
        data2 = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "wanted", 
            "size": "TBD"
        }
        
        result2 = self.test_single_request(data2, "TBD size")
        
        # Solution 3: Use "Flexible" size
        print(f"\n3. Testing 'Flexible' size for wanted collections:")
        data3 = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "wanted",
            "size": "Flexible"
        }
        
        result3 = self.test_single_request(data3, "Flexible size")
        
        return [result1, result2, result3]
    
    def test_single_request(self, data: Dict, description: str) -> Dict:
        """Test a single request and return result"""
        try:
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=data)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                print(f"   ✅ SUCCESS: {description}")
                print(f"   Kit ID: {response_data.get('id')}")
                print(f"   Size stored: {response_data.get('size')}")
                return {"success": True, "data": response_data}
            elif response.status_code == 400:
                error_data = response.json()
                if "already in your collection" in error_data.get("detail", ""):
                    print(f"   ⚠️  DUPLICATE: {description} - Kit already in collection")
                    return {"success": True, "duplicate": True}
                else:
                    print(f"   ❌ FAILED: {description} - {error_data.get('detail')}")
                    return {"success": False, "error": error_data}
            else:
                error_data = response.json()
                print(f"   ❌ FAILED: {description} - HTTP {response.status_code}")
                print(f"   Error: {error_data}")
                return {"success": False, "error": error_data, "status_code": response.status_code}
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {description} - {str(e)}")
            return {"success": False, "exception": str(e)}
    
    def get_reference_kits(self) -> List[Dict]:
        """Get available reference kits"""
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def run_fix_tests(self):
        """Run all fix tests"""
        print("🔧 WANT LIST FIX TESTING - FINDING WORKAROUNDS FOR SIZE REQUIREMENT")
        print("=" * 80)
        
        # Authenticate
        if not self.authenticate_user():
            return
        
        # Get reference kits
        reference_kits = self.get_reference_kits()
        if not reference_kits:
            print("❌ No reference kits available")
            return
        
        # Use second kit for testing (first one might already be in collection)
        test_kit = reference_kits[1] if len(reference_kits) > 1 else reference_kits[0]
        reference_kit_id = test_kit.get("id")
        
        print(f"\n🎯 Testing with reference kit:")
        print(f"   ID: {reference_kit_id}")
        print(f"   Team: {test_kit.get('team_info', {}).get('name', 'Unknown')}")
        print(f"   Kit: {test_kit.get('master_kit_info', {}).get('kit_type', 'Unknown')} {test_kit.get('master_kit_info', {}).get('season', 'Unknown')}")
        
        # Test workaround solutions
        results = self.test_workaround_solutions(reference_kit_id)
        
        # Print summary
        print(f"\n📊 SUMMARY OF WORKAROUND TESTS:")
        print("=" * 50)
        successful_workarounds = [r for r in results if r.get('success')]
        print(f"Successful workarounds: {len(successful_workarounds)}/{len(results)}")
        
        if successful_workarounds:
            print(f"\n✅ RECOMMENDED FRONTEND FIX:")
            print(f"   When adding to wanted collection, always include a size field")
            print(f"   Suggested default values: 'Any', 'TBD', or 'Flexible'")
            print(f"   This will prevent the '[object Object]' error")
            print(f"\n🔧 IMPLEMENTATION SUGGESTION:")
            print(f"   In addToWantedDirectly function, modify the request to include:")
            print(f"   {{")
            print(f"     reference_kit_id: kitId,")
            print(f"     collection_type: 'wanted',")
            print(f"     size: 'Any'  // Add this line to prevent validation error")
            print(f"   }}")
        else:
            print(f"\n❌ NO WORKAROUNDS FOUND")
            print(f"   Backend modification required to make size optional for wanted collections")

def main():
    """Main function"""
    tester = WantListFixTester()
    tester.run_fix_tests()

if __name__ == "__main__":
    main()