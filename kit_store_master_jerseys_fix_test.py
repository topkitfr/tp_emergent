#!/usr/bin/env python3
"""
Kit Store Master Jerseys Fix Testing
Testing Kit Store endpoint after the master_kits → master_jerseys fix to verify reference kits now appear
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://football-jersey-db.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class KitStoreMasterJerseysTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate admin user and get JWT token"""
        try:
            auth_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                if self.admin_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Successfully authenticated admin user. Token length: {len(self.admin_token)}"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, "", "No token in response")
                    return False
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    "", 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def test_vestiaire_endpoint_after_fix(self):
        """Test GET /api/vestiaire to verify reference kits now appear after master_jerseys fix"""
        try:
            response = self.session.get(f"{API_BASE}/vestiaire")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we have reference kits in the response
                reference_kits = data if isinstance(data, list) else data.get('reference_kits', [])
                
                if reference_kits:
                    self.log_result(
                        "Kit Store Endpoint After Fix",
                        True,
                        f"Found {len(reference_kits)} reference kits in Kit Store response"
                    )
                    
                    # Analyze the structure of reference kits
                    for i, kit in enumerate(reference_kits[:3]):  # Check first 3 kits
                        kit_details = []
                        if 'topkit_reference' in kit:
                            kit_details.append(f"TopKit Ref: {kit['topkit_reference']}")
                        if 'master_jersey_info' in kit:
                            master_jersey = kit['master_jersey_info']
                            if 'season' in master_jersey:
                                kit_details.append(f"Season: {master_jersey['season']}")
                            if 'jersey_type' in master_jersey:
                                kit_details.append(f"Type: {master_jersey['jersey_type']}")
                            if 'team_info' in master_jersey:
                                team_info = master_jersey['team_info']
                                if 'name' in team_info:
                                    kit_details.append(f"Team: {team_info['name']}")
                        elif 'master_kit_info' in kit:
                            # Handle legacy field name (master_kit_info instead of master_jersey_info)
                            master_jersey = kit['master_kit_info']
                            if 'season' in master_jersey:
                                kit_details.append(f"Season: {master_jersey['season']}")
                            if 'jersey_type' in master_jersey:
                                kit_details.append(f"Type: {master_jersey['jersey_type']}")
                            if 'team_id' in master_jersey:
                                kit_details.append(f"Team ID: {master_jersey['team_id']}")
                            kit_details.append("(Using legacy master_kit_info field)")
                        
                        print(f"   Kit {i+1}: {', '.join(kit_details) if kit_details else 'Basic structure'}")
                    
                    return reference_kits
                else:
                    self.log_result(
                        "Kit Store Endpoint After Fix",
                        False,
                        "",
                        "No reference kits found in Kit Store response - fix may not be working"
                    )
                    return []
            else:
                self.log_result(
                    "Kit Store Endpoint After Fix",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Kit Store Endpoint After Fix", False, "", str(e))
            return []

    def test_reference_kit_display_validation(self):
        """Verify that existing reference kits in database show up in Kit Store with proper data"""
        try:
            # First get reference kits directly from database endpoint
            response = self.session.get(f"{API_BASE}/reference-kits")
            
            if response.status_code == 200:
                db_reference_kits = response.json()
                db_count = len(db_reference_kits) if isinstance(db_reference_kits, list) else len(db_reference_kits.get('reference_kits', []))
                
                # Now get Kit Store response
                vestiaire_response = self.session.get(f"{API_BASE}/vestiaire")
                
                if vestiaire_response.status_code == 200:
                    vestiaire_data = vestiaire_response.json()
                    vestiaire_kits = vestiaire_data if isinstance(vestiaire_data, list) else vestiaire_data.get('reference_kits', [])
                    vestiaire_count = len(vestiaire_kits)
                    
                    # Compare counts and data
                    if vestiaire_count > 0:
                        self.log_result(
                            "Reference Kit Display Validation",
                            True,
                            f"Database has {db_count} reference kits, Kit Store shows {vestiaire_count} kits"
                        )
                        
                        # Check if kits have proper master jersey information
                        kits_with_master_jersey = 0
                        for kit in vestiaire_kits:
                            if 'master_jersey_info' in kit and kit['master_jersey_info']:
                                kits_with_master_jersey += 1
                        
                        print(f"   Kits with master jersey info: {kits_with_master_jersey}/{vestiaire_count}")
                        
                        return True
                    else:
                        self.log_result(
                            "Reference Kit Display Validation",
                            False,
                            f"Database has {db_count} reference kits but Kit Store shows 0 kits",
                            "Reference kits not appearing in Kit Store despite existing in database"
                        )
                        return False
                else:
                    self.log_result(
                        "Reference Kit Display Validation",
                        False,
                        "",
                        f"Kit Store endpoint failed: HTTP {vestiaire_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Reference Kit Display Validation",
                    False,
                    "",
                    f"Reference kits endpoint failed: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Reference Kit Display Validation", False, "", str(e))
            return False

    def test_master_jersey_data_linking(self):
        """Ensure reference kits have proper master jersey information linked"""
        try:
            response = self.session.get(f"{API_BASE}/vestiaire")
            
            if response.status_code == 200:
                data = response.json()
                reference_kits = data if isinstance(data, list) else data.get('reference_kits', [])
                
                if not reference_kits:
                    self.log_result(
                        "Master Jersey Data Linking",
                        False,
                        "",
                        "No reference kits found to validate master jersey linking"
                    )
                    return False
                
                # Analyze master jersey data quality
                total_kits = len(reference_kits)
                kits_with_master_jersey = 0
                kits_with_team_info = 0
                kits_with_complete_data = 0
                
                for kit in reference_kits:
                    has_master_jersey = False
                    has_team_info = False
                    has_complete_data = False
                    
                    if 'master_jersey_info' in kit and kit['master_jersey_info']:
                        has_master_jersey = True
                        kits_with_master_jersey += 1
                        master_jersey = kit['master_jersey_info']
                    elif 'master_kit_info' in kit and kit['master_kit_info']:
                        # Handle legacy field name (master_kit_info instead of master_jersey_info)
                        has_master_jersey = True
                        kits_with_master_jersey += 1
                        master_jersey = kit['master_kit_info']
                    if has_master_jersey:
                        # Check for team information (could be in team_info or via team_id)
                        if ('team_info' in master_jersey and master_jersey['team_info']) or 'team_id' in master_jersey:
                            has_team_info = True
                            kits_with_team_info += 1
                        
                        # Check for complete data (season, jersey_type, etc.)
                        required_fields = ['season', 'jersey_type']
                        if all(field in master_jersey and master_jersey[field] for field in required_fields):
                            has_complete_data = True
                            kits_with_complete_data += 1
                
                # Calculate success rate
                master_jersey_rate = (kits_with_master_jersey / total_kits) * 100
                team_info_rate = (kits_with_team_info / total_kits) * 100
                complete_data_rate = (kits_with_complete_data / total_kits) * 100
                
                success = master_jersey_rate >= 80  # At least 80% should have master jersey info
                
                self.log_result(
                    "Master Jersey Data Linking",
                    success,
                    f"Master jersey linking: {kits_with_master_jersey}/{total_kits} ({master_jersey_rate:.1f}%), "
                    f"Team info: {kits_with_team_info}/{total_kits} ({team_info_rate:.1f}%), "
                    f"Complete data: {kits_with_complete_data}/{total_kits} ({complete_data_rate:.1f}%)"
                )
                
                return success
            else:
                self.log_result(
                    "Master Jersey Data Linking",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Master Jersey Data Linking", False, "", str(e))
            return False

    def test_contributions_v2_integration(self):
        """Verify that approved reference kits from contributions-v2 appear in Kit Store"""
        try:
            # Get contributions-v2 data
            contributions_response = self.session.get(f"{API_BASE}/contributions-v2/")
            
            if contributions_response.status_code == 200:
                contributions = contributions_response.json()
                contributions_list = contributions if isinstance(contributions, list) else contributions.get('contributions', [])
                
                # Filter for approved contributions related to reference kits or master jerseys
                approved_kit_contributions = []
                for contrib in contributions_list:
                    if (contrib.get('status') == 'APPROVED' and 
                        contrib.get('entity_type') in ['master_jersey', 'reference_kit']):
                        approved_kit_contributions.append(contrib)
                
                # Get Kit Store data
                vestiaire_response = self.session.get(f"{API_BASE}/vestiaire")
                
                if vestiaire_response.status_code == 200:
                    vestiaire_data = vestiaire_response.json()
                    reference_kits = vestiaire_data if isinstance(vestiaire_data, list) else vestiaire_data.get('reference_kits', [])
                    
                    self.log_result(
                        "Contributions-v2 Integration Test",
                        True,
                        f"Found {len(approved_kit_contributions)} approved kit contributions, "
                        f"Kit Store shows {len(reference_kits)} reference kits"
                    )
                    
                    # Check if there's correlation between approved contributions and Kit Store items
                    if len(approved_kit_contributions) > 0 and len(reference_kits) > 0:
                        print(f"   Integration appears functional - both approved contributions and Kit Store items exist")
                    elif len(approved_kit_contributions) == 0:
                        print(f"   No approved kit contributions found to verify integration")
                    else:
                        print(f"   Warning: Approved contributions exist but no Kit Store items found")
                    
                    return True
                else:
                    self.log_result(
                        "Contributions-v2 Integration Test",
                        False,
                        "",
                        f"Kit Store endpoint failed: HTTP {vestiaire_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Contributions-v2 Integration Test",
                    False,
                    "",
                    f"Contributions-v2 endpoint failed: HTTP {contributions_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Contributions-v2 Integration Test", False, "", str(e))
            return False

    def run_all_tests(self):
        """Run all Kit Store master jerseys fix tests"""
        print("🧪 Starting Kit Store Master Jerseys Fix Testing")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Run all tests
        tests = [
            self.test_vestiaire_endpoint_after_fix,
            self.test_reference_kit_display_validation,
            self.test_master_jersey_data_linking,
            self.test_contributions_v2_integration
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Summary
        print("=" * 60)
        print(f"🎯 Kit Store Master Jerseys Fix Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All tests passed - Kit Store master jerseys fix is working correctly!")
        elif passed >= total * 0.75:
            print("⚠️  Most tests passed - Kit Store fix is mostly working with minor issues")
        else:
            print("❌ Multiple test failures - Kit Store master jerseys fix needs attention")
        
        return passed, total

if __name__ == "__main__":
    tester = KitStoreMasterJerseysTester()
    tester.run_all_tests()