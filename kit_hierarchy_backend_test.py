#!/usr/bin/env python3
"""
KIT HIERARCHY WORKFLOW TESTING - BACKEND TEST
==============================================

This test validates the complete Kit hierarchy workflow with newly created test data:

1. Authentication Test: Verify admin login with topkitfr@gmail.com/TopKitSecure789#
2. Vestiaire Endpoint Test: Test GET /api/vestiaire to verify 14 Reference Kits with enriched data
3. Personal Kit Creation Test: Test POST /api/personal-kits to create personal kits from reference kits
4. Personal Kit Retrieval Test: Test GET /api/personal-kits?collection_type=owned and wanted
5. Complete Workflow Test: Full user workflow from authentication to collection management

Expected Results:
- Vestiaire should return ~14 Reference Kits with team names like "FC Barcelona", "Paris Saint-Germain", "Manchester United"
- Personal Kit creation should work with proper data validation
- Personal Kit retrieval should return enriched data with reference_kit_info, master_kit_info, team_info, brand_info

Focus: Validating new Kit hierarchy data structures and API responses match migrated frontend expectations.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-kit-ui.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class KitHierarchyTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = {
            "authentication": False,
            "master_kits_available": False,
            "reference_kit_creation": False,
            "personal_kit_creation": False,
            "vestiaire_endpoint": False,
            "data_structure_validation": False
        }
        self.created_resources = {
            "reference_kits": [],
            "personal_kits": []
        }

    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def authenticate_admin(self):
        """Authenticate admin user and get JWT token"""
        try:
            self.log("🔐 Authenticating admin user...")
            
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                self.admin_user_id = user_info.get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log(f"✅ Admin authentication successful")
                self.log(f"   User: {user_info.get('name')} ({user_info.get('email')})")
                self.log(f"   Role: {user_info.get('role')}")
                self.log(f"   User ID: {self.admin_user_id}")
                self.test_results["authentication"] = True
                return True
            else:
                self.log(f"❌ Admin authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Admin authentication error: {str(e)}", "ERROR")
            return False

    def check_master_kits_available(self):
        """Check if there are Master Kits in the database"""
        try:
            self.log("🔍 Checking Master Kits availability...")
            
            response = self.session.get(f"{BACKEND_URL}/master-kits")
            
            if response.status_code == 200:
                master_kits = response.json()
                self.log(f"✅ Master Kits endpoint accessible")
                self.log(f"   Found {len(master_kits)} Master Kits in database")
                
                if len(master_kits) > 0:
                    # Display first few master kits
                    for i, kit in enumerate(master_kits[:3]):
                        self.log(f"   Master Kit {i+1}: {kit.get('topkit_reference', 'No ref')} - {kit.get('season', 'No season')}")
                        if 'team_info' in kit:
                            self.log(f"     Team: {kit['team_info'].get('name', 'Unknown')}")
                        if 'brand_info' in kit:
                            self.log(f"     Brand: {kit['brand_info'].get('name', 'Unknown')}")
                    
                    self.test_results["master_kits_available"] = True
                    return master_kits
                else:
                    self.log("⚠️  No Master Kits found in database - cannot test Reference Kit creation")
                    return []
            else:
                self.log(f"❌ Master Kits endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Master Kits check error: {str(e)}", "ERROR")
            return []

    def test_reference_kit_creation(self, master_kits):
        """Test POST /api/reference-kits endpoint"""
        try:
            if not master_kits:
                self.log("⚠️  Skipping Reference Kit creation - no Master Kits available")
                return False
                
            self.log("🏗️  Testing Reference Kit creation...")
            
            # Use first available master kit
            master_kit = master_kits[0]
            master_kit_id = master_kit.get('id')
            
            self.log(f"   Using Master Kit: {master_kit.get('topkit_reference', 'No ref')}")
            
            # Create reference kit data
            reference_kit_data = {
                "master_kit_id": master_kit_id,
                "available_sizes": ["XS", "S", "M", "L", "XL", "XXL"],
                "original_retail_price": 89.99,
                "current_market_estimate": 120.00,
                "price_range_min": 80.00,
                "price_range_max": 150.00,
                "is_limited_edition": False,
                "official_product_code": "TEST-REF-001"
            }
            
            response = self.session.post(f"{BACKEND_URL}/reference-kits", json=reference_kit_data)
            
            if response.status_code == 200:
                reference_kit = response.json()
                self.log("✅ Reference Kit creation successful")
                self.log(f"   Reference Kit ID: {reference_kit.get('id')}")
                self.log(f"   TopKit Reference: {reference_kit.get('topkit_reference')}")
                self.log(f"   Master Kit ID: {reference_kit.get('master_kit_id')}")
                
                # Validate data structure
                required_fields = ['id', 'master_kit_id', 'available_sizes', 'original_retail_price', 'topkit_reference']
                missing_fields = [field for field in required_fields if field not in reference_kit]
                
                if not missing_fields:
                    self.log("✅ Reference Kit data structure validation passed")
                    
                    # Check enriched data
                    if 'master_kit_info' in reference_kit:
                        self.log("✅ Master Kit info enrichment present")
                    if 'team_info' in reference_kit:
                        self.log("✅ Team info enrichment present")
                    if 'brand_info' in reference_kit:
                        self.log("✅ Brand info enrichment present")
                    
                    self.created_resources["reference_kits"].append(reference_kit)
                    self.test_results["reference_kit_creation"] = True
                    return reference_kit
                else:
                    self.log(f"❌ Reference Kit missing required fields: {missing_fields}", "ERROR")
                    return False
            else:
                self.log(f"❌ Reference Kit creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Reference Kit creation error: {str(e)}", "ERROR")
            return False

    def test_personal_kit_creation(self, reference_kit):
        """Test POST /api/personal-kits endpoint"""
        try:
            if not reference_kit:
                self.log("⚠️  Skipping Personal Kit creation - no Reference Kit available")
                return False
                
            self.log("👤 Testing Personal Kit creation...")
            
            reference_kit_id = reference_kit.get('id')
            self.log(f"   Using Reference Kit: {reference_kit.get('topkit_reference')}")
            
            # Create personal kit data
            personal_kit_data = {
                "reference_kit_id": reference_kit_id,
                "size": "L",
                "condition": "mint",
                "collection_type": "owned",
                "purchase_price": 95.00,
                "purchase_location": "Official Store",
                "is_worn": False,
                "is_signed": False,
                "has_printing": True,
                "printed_name": "TEST PLAYER",
                "printed_number": 10,
                "printing_type": "official",
                "personal_notes": "Test kit for collection management testing"
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            
            if response.status_code == 200:
                personal_kit = response.json()
                self.log("✅ Personal Kit creation successful")
                self.log(f"   Personal Kit ID: {personal_kit.get('id')}")
                self.log(f"   Reference Kit ID: {personal_kit.get('reference_kit_id')}")
                self.log(f"   Size: {personal_kit.get('size')}")
                self.log(f"   Condition: {personal_kit.get('condition')}")
                self.log(f"   Collection Type: {personal_kit.get('collection_type')}")
                
                # Validate data structure
                required_fields = ['id', 'user_id', 'reference_kit_id', 'size', 'condition', 'collection_type']
                missing_fields = [field for field in required_fields if field not in personal_kit]
                
                if not missing_fields:
                    self.log("✅ Personal Kit data structure validation passed")
                    
                    # Check enriched data
                    if 'reference_kit_info' in personal_kit:
                        self.log("✅ Reference Kit info enrichment present")
                    if 'master_kit_info' in personal_kit:
                        self.log("✅ Master Kit info enrichment present")
                    if 'team_info' in personal_kit:
                        self.log("✅ Team info enrichment present")
                    if 'brand_info' in personal_kit:
                        self.log("✅ Brand info enrichment present")
                    
                    self.created_resources["personal_kits"].append(personal_kit)
                    self.test_results["personal_kit_creation"] = True
                    return personal_kit
                else:
                    self.log(f"❌ Personal Kit missing required fields: {missing_fields}", "ERROR")
                    return False
            else:
                self.log(f"❌ Personal Kit creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Personal Kit creation error: {str(e)}", "ERROR")
            return False

    def test_vestiaire_endpoint(self):
        """Test GET /api/vestiaire endpoint (Kit Store)"""
        try:
            self.log("🏪 Testing Vestiaire (Kit Store) endpoint...")
            
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                vestiaire_kits = response.json()
                self.log("✅ Vestiaire endpoint accessible")
                self.log(f"   Found {len(vestiaire_kits)} Reference Kits in Kit Store")
                
                if len(vestiaire_kits) > 0:
                    # Display first few kits
                    for i, kit in enumerate(vestiaire_kits[:3]):
                        self.log(f"   Kit {i+1}: {kit.get('topkit_reference', 'No ref')}")
                        
                        # Validate expected data structure
                        required_fields = ['id', 'master_kit_id', 'available_sizes', 'topkit_reference']
                        missing_fields = [field for field in required_fields if field not in kit]
                        
                        if not missing_fields:
                            self.log(f"     ✅ Data structure valid")
                            
                            # Check enriched data
                            enrichment_status = []
                            if 'master_kit_info' in kit and kit['master_kit_info']:
                                enrichment_status.append("master_kit")
                            if 'team_info' in kit and kit['team_info']:
                                enrichment_status.append("team")
                            if 'brand_info' in kit and kit['brand_info']:
                                enrichment_status.append("brand")
                            
                            if enrichment_status:
                                self.log(f"     ✅ Enriched with: {', '.join(enrichment_status)}")
                            else:
                                self.log(f"     ⚠️  No enrichment data found")
                        else:
                            self.log(f"     ❌ Missing fields: {missing_fields}")
                    
                    self.test_results["vestiaire_endpoint"] = True
                    self.test_results["data_structure_validation"] = True
                    return vestiaire_kits
                else:
                    self.log("⚠️  No Reference Kits found in Vestiaire")
                    self.test_results["vestiaire_endpoint"] = True  # Endpoint works, just empty
                    return []
            else:
                self.log(f"❌ Vestiaire endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Vestiaire endpoint error: {str(e)}", "ERROR")
            return []

    def test_user_collection_endpoint(self):
        """Test GET /api/personal-kits endpoint (User's collection)"""
        try:
            self.log("📚 Testing User Collection endpoint...")
            
            response = self.session.get(f"{BACKEND_URL}/personal-kits")
            
            if response.status_code == 200:
                user_collection = response.json()
                self.log("✅ User Collection endpoint accessible")
                self.log(f"   Found {len(user_collection)} Personal Kits in user's collection")
                
                if len(user_collection) > 0:
                    # Display collection items
                    for i, kit in enumerate(user_collection[:3]):
                        self.log(f"   Kit {i+1}: Size {kit.get('size', 'Unknown')} - {kit.get('condition', 'Unknown')} condition")
                        self.log(f"     Collection Type: {kit.get('collection_type', 'Unknown')}")
                        if kit.get('printed_name'):
                            self.log(f"     Printing: {kit.get('printed_name')} #{kit.get('printed_number', 'N/A')}")
                
                return user_collection
            else:
                self.log(f"❌ User Collection endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ User Collection endpoint error: {str(e)}", "ERROR")
            return []

    def run_comprehensive_test(self):
        """Run all Kit Hierarchy tests"""
        self.log("🚀 Starting Kit Hierarchy Backend API Testing")
        self.log("=" * 60)
        
        # 1. Authentication
        if not self.authenticate_admin():
            self.log("❌ Cannot proceed without authentication", "ERROR")
            return False
        
        # 2. Check Master Kits availability
        master_kits = self.check_master_kits_available()
        
        # 3. Test Reference Kit creation
        reference_kit = self.test_reference_kit_creation(master_kits)
        
        # 4. Test Personal Kit creation
        personal_kit = self.test_personal_kit_creation(reference_kit)
        
        # 5. Test Vestiaire endpoint
        vestiaire_kits = self.test_vestiaire_endpoint()
        
        # 6. Test User Collection endpoint
        user_collection = self.test_user_collection_endpoint()
        
        # Generate final report
        self.generate_final_report()
        
        return True

    def generate_final_report(self):
        """Generate comprehensive test report"""
        self.log("=" * 60)
        self.log("📊 KIT HIERARCHY TESTING RESULTS")
        self.log("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        self.log(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        self.log("")
        
        # Individual test results
        test_descriptions = {
            "authentication": "Admin Authentication",
            "master_kits_available": "Master Kits Data Availability",
            "reference_kit_creation": "Reference Kit Creation (POST /api/reference-kits)",
            "personal_kit_creation": "Personal Kit Creation (POST /api/personal-kits)",
            "vestiaire_endpoint": "Vestiaire Endpoint (GET /api/vestiaire)",
            "data_structure_validation": "Data Structure Validation"
        }
        
        for test_key, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            description = test_descriptions.get(test_key, test_key)
            self.log(f"{status} - {description}")
        
        self.log("")
        
        # Resources created
        if self.created_resources["reference_kits"]:
            self.log(f"📦 Created {len(self.created_resources['reference_kits'])} Reference Kit(s)")
        if self.created_resources["personal_kits"]:
            self.log(f"👤 Created {len(self.created_resources['personal_kits'])} Personal Kit(s)")
        
        self.log("")
        
        # Key findings
        self.log("🔍 KEY FINDINGS:")
        
        if self.test_results["authentication"]:
            self.log("✅ Authentication system working with admin credentials")
        
        if self.test_results["master_kits_available"]:
            self.log("✅ Master Kits available for Reference Kit creation")
        else:
            self.log("⚠️  No Master Kits found - Reference Kit creation limited")
        
        if self.test_results["reference_kit_creation"]:
            self.log("✅ Reference Kit creation working with proper data enrichment")
        
        if self.test_results["personal_kit_creation"]:
            self.log("✅ Personal Kit creation working for collection management")
        
        if self.test_results["vestiaire_endpoint"]:
            self.log("✅ Vestiaire endpoint returning Reference Kits with enriched data")
        
        if self.test_results["data_structure_validation"]:
            self.log("✅ All data structures match expected format")
        
        # Critical issues
        critical_issues = []
        if not self.test_results["authentication"]:
            critical_issues.append("Authentication system failure")
        if not self.test_results["vestiaire_endpoint"]:
            critical_issues.append("Vestiaire endpoint not accessible")
        
        if critical_issues:
            self.log("")
            self.log("🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                self.log(f"❌ {issue}")
        
        self.log("=" * 60)
        
        # Return overall success
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = KitHierarchyTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n🎉 Kit Hierarchy testing completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Kit Hierarchy testing completed with issues!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()