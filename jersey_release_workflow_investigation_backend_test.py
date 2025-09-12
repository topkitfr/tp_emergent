#!/usr/bin/env python3
"""
JERSEY RELEASE WORKFLOW INVESTIGATION - BACKEND TEST
===================================================

INVESTIGATION CRITIQUE - RESTAURER LE WORKFLOW JERSEY RELEASE

This test investigates why Jersey Releases no longer exist in the database 
and restores the complete workflow as requested.

PRIORITÉ ABSOLUE:
1. **Vérifier les Master Jerseys disponibles** - List all Master Jerseys in database
2. **Tester la création de Jersey Release** - Create new Jersey Release with existing Master Jersey
3. **Vérifier l'endpoint Vestiaire** - Test GET /api/vestiaire for Jersey Releases
4. **Tester le workflow complet** - Master Jersey -> Jersey Release -> Vestiaire -> Collections

Authentication:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- User: steinmetzlivio@gmail.com / T0p_Mdp_1288*

Objectif: Identifier pourquoi les Jersey Releases ont disparu et restaurer le workflow fonctionnel.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class JerseyReleaseWorkflowInvestigator:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = []
        self.master_jerseys = []
        self.jersey_releases = []
        self.created_jersey_release_id = None
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_data = data.get("user", {})
                self.admin_user_id = user_data.get("id")
                
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Admin authenticated successfully - Name: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.admin_user_id}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_data = data.get("user", {})
                self.user_user_id = user_data.get("id")
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"User authenticated successfully - Name: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.user_user_id}"
                )
                return True
            else:
                self.log_result(
                    "User Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False

    def verify_master_jerseys_available(self):
        """PRIORITÉ 1: Vérifier les Master Jerseys disponibles"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/master-jerseys", headers=headers)
            
            if response.status_code == 200:
                master_jerseys = response.json()
                self.master_jerseys = master_jerseys
                
                if isinstance(master_jerseys, list) and len(master_jerseys) > 0:
                    # Look for FC Barcelona specifically
                    fc_barcelona_jerseys = [mj for mj in master_jerseys if 'barcelona' in mj.get('team', {}).get('name', '').lower()]
                    
                    details = f"Found {len(master_jerseys)} Master Jerseys total"
                    if fc_barcelona_jerseys:
                        details += f", including {len(fc_barcelona_jerseys)} FC Barcelona jerseys"
                        details += f". First FC Barcelona jersey: {fc_barcelona_jerseys[0].get('team', {}).get('name')} - {fc_barcelona_jerseys[0].get('season')} - {fc_barcelona_jerseys[0].get('jersey_type')}"
                    
                    self.log_result(
                        "Master Jerseys Availability Check", 
                        True, 
                        details
                    )
                    return True
                else:
                    self.log_result(
                        "Master Jerseys Availability Check", 
                        False, 
                        f"No Master Jerseys found in database - Response: {master_jerseys}"
                    )
                    return False
            else:
                self.log_result(
                    "Master Jerseys Availability Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Master Jerseys Availability Check", False, f"Exception: {str(e)}")
            return False

    def test_jersey_release_creation(self):
        """PRIORITÉ 2: Tester la création de Jersey Release"""
        if not self.master_jerseys:
            self.log_result(
                "Jersey Release Creation Test", 
                False, 
                "Cannot test Jersey Release creation - no Master Jerseys available"
            )
            return False
            
        try:
            # Use first available Master Jersey (preferably FC Barcelona)
            fc_barcelona_jerseys = [mj for mj in self.master_jerseys if 'barcelona' in mj.get('team', {}).get('name', '').lower()]
            target_master_jersey = fc_barcelona_jerseys[0] if fc_barcelona_jerseys else self.master_jerseys[0]
            
            # Create Jersey Release data with required release_type field
            jersey_release_data = {
                "master_jersey_id": target_master_jersey.get("id"),
                "release_type": "player_version",  # Required field: "player_version", "fan_version", "authentic", "replica"
                "player_name": "Test Player Investigation",
                "player_number": 10,
                "retail_price": 89.99,
                "size_range": ["S", "M", "L", "XL"],
                "product_images": []
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/jersey-releases", json=jersey_release_data, headers=headers)
            
            if response.status_code in [200, 201]:
                created_jersey_release = response.json()
                self.created_jersey_release_id = created_jersey_release.get("id")
                
                self.log_result(
                    "Jersey Release Creation Test", 
                    True, 
                    f"Jersey Release created successfully - ID: {self.created_jersey_release_id}, Master Jersey: {target_master_jersey.get('team', {}).get('name')} {target_master_jersey.get('season')}, Player: {jersey_release_data['player_name']}"
                )
                return True
            else:
                self.log_result(
                    "Jersey Release Creation Test", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Jersey Release Creation Test", False, f"Exception: {str(e)}")
            return False

    def verify_jersey_release_in_database(self):
        """Verify the created Jersey Release exists in database"""
        if not self.created_jersey_release_id:
            self.log_result(
                "Jersey Release Database Verification", 
                False, 
                "Cannot verify - no Jersey Release was created"
            )
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/jersey-releases/{self.created_jersey_release_id}", headers=headers)
            
            if response.status_code == 200:
                jersey_release = response.json()
                self.log_result(
                    "Jersey Release Database Verification", 
                    True, 
                    f"Jersey Release found in database - Player: {jersey_release.get('player_name')}, Size: {jersey_release.get('size')}, Price: €{jersey_release.get('price')}"
                )
                return True
            else:
                self.log_result(
                    "Jersey Release Database Verification", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Jersey Release Database Verification", False, f"Exception: {str(e)}")
            return False

    def verify_vestiaire_endpoint(self):
        """PRIORITÉ 3: Vérifier l'endpoint Vestiaire"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if response.status_code == 200:
                vestiaire_data = response.json()
                
                if isinstance(vestiaire_data, list):
                    jersey_releases_count = len(vestiaire_data)
                    
                    # Check if our created Jersey Release appears
                    created_release_found = False
                    if self.created_jersey_release_id:
                        created_release_found = any(
                            jr.get("id") == self.created_jersey_release_id 
                            for jr in vestiaire_data
                        )
                    
                    details = f"Vestiaire endpoint returned {jersey_releases_count} Jersey Releases"
                    if created_release_found:
                        details += f". ✅ Our created Jersey Release (ID: {self.created_jersey_release_id}) appears in Vestiaire"
                    elif self.created_jersey_release_id:
                        details += f". ❌ Our created Jersey Release (ID: {self.created_jersey_release_id}) NOT found in Vestiaire"
                    
                    if jersey_releases_count > 0:
                        sample_release = vestiaire_data[0]
                        details += f". Sample release: Player '{sample_release.get('player_name')}', Price €{sample_release.get('price')}"
                    
                    self.log_result(
                        "Vestiaire Endpoint Verification", 
                        jersey_releases_count > 0, 
                        details
                    )
                    
                    self.jersey_releases = vestiaire_data
                    return jersey_releases_count > 0
                else:
                    self.log_result(
                        "Vestiaire Endpoint Verification", 
                        False, 
                        f"Vestiaire endpoint returned non-array data: {type(vestiaire_data)} - {vestiaire_data}"
                    )
                    return False
            else:
                self.log_result(
                    "Vestiaire Endpoint Verification", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Vestiaire Endpoint Verification", False, f"Exception: {str(e)}")
            return False

    def test_complete_workflow_add_to_collection(self):
        """PRIORITÉ 4: Tester le workflow complet - Ajout aux collections"""
        if not self.jersey_releases:
            self.log_result(
                "Complete Workflow - Add to Collection", 
                False, 
                "Cannot test collection workflow - no Jersey Releases available in Vestiaire"
            )
            return False
            
        try:
            # Use our created Jersey Release if available, otherwise use first available
            target_release = None
            if self.created_jersey_release_id:
                target_release = next(
                    (jr for jr in self.jersey_releases if jr.get("id") == self.created_jersey_release_id), 
                    None
                )
            
            if not target_release:
                target_release = self.jersey_releases[0]
            
            # Test adding to "owned" collection
            collection_data = {
                "jersey_release_id": target_release.get("id"),
                "collection_type": "owned",
                "size": target_release.get("size", "L"),
                "condition": target_release.get("condition", "mint"),
                "personal_description": f"Added during workflow investigation - {datetime.now().isoformat()}"
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/users/{self.user_user_id}/collections", json=collection_data, headers=headers)
            
            if response.status_code in [200, 201]:
                collection_result = response.json()
                collection_id = collection_result.get("collection_id") or collection_result.get("id")
                
                self.log_result(
                    "Complete Workflow - Add to Collection", 
                    True, 
                    f"Jersey Release successfully added to owned collection - Collection ID: {collection_id}, Jersey Release: {target_release.get('player_name')} (ID: {target_release.get('id')})"
                )
                return True
            elif response.status_code == 400 and "already in collection" in response.text.lower():
                self.log_result(
                    "Complete Workflow - Add to Collection", 
                    True, 
                    f"Jersey Release already in collection (expected behavior for duplicate prevention) - Jersey Release: {target_release.get('player_name')} (ID: {target_release.get('id')})"
                )
                return True
            else:
                self.log_result(
                    "Complete Workflow - Add to Collection", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Complete Workflow - Add to Collection", False, f"Exception: {str(e)}")
            return False

    def verify_collection_data_quality(self):
        """Verify collection data quality and aggregation"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                
                if isinstance(collections, list) and len(collections) > 0:
                    # Check data quality
                    enriched_collections = 0
                    empty_jersey_release_data = 0
                    
                    for collection in collections:
                        jersey_release_data = collection.get("jersey_release", {})
                        master_jersey_data = collection.get("master_jersey", {})
                        
                        if jersey_release_data and len(jersey_release_data) > 0:
                            enriched_collections += 1
                        else:
                            empty_jersey_release_data += 1
                    
                    data_quality_percentage = (enriched_collections / len(collections)) * 100 if collections else 0
                    
                    details = f"Found {len(collections)} collections total. Data quality: {data_quality_percentage:.1f}% ({enriched_collections}/{len(collections)} properly enriched)"
                    if empty_jersey_release_data > 0:
                        details += f". ❌ {empty_jersey_release_data} collections have empty jersey_release data"
                    
                    self.log_result(
                        "Collection Data Quality Verification", 
                        data_quality_percentage > 50, 
                        details
                    )
                    return data_quality_percentage > 50
                else:
                    self.log_result(
                        "Collection Data Quality Verification", 
                        False, 
                        f"No collections found for user - Response: {collections}"
                    )
                    return False
            else:
                self.log_result(
                    "Collection Data Quality Verification", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Collection Data Quality Verification", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_investigation(self):
        """Run complete Jersey Release workflow investigation"""
        print("🔍 JERSEY RELEASE WORKFLOW INVESTIGATION - BACKEND TEST")
        print("=" * 60)
        print("INVESTIGATION CRITIQUE - RESTAURER LE WORKFLOW JERSEY RELEASE")
        print()
        
        # Phase 1: Authentication
        print("📋 PHASE 1: AUTHENTICATION")
        print("-" * 30)
        admin_auth_success = self.authenticate_admin()
        user_auth_success = self.authenticate_user()
        
        if not admin_auth_success or not user_auth_success:
            print("❌ CRITICAL: Authentication failed - cannot proceed with investigation")
            return False
        
        print()
        
        # Phase 2: Master Jerseys Investigation
        print("📋 PHASE 2: MASTER JERSEYS INVESTIGATION")
        print("-" * 40)
        master_jerseys_available = self.verify_master_jerseys_available()
        
        print()
        
        # Phase 3: Jersey Release Creation Test
        print("📋 PHASE 3: JERSEY RELEASE CREATION TEST")
        print("-" * 40)
        jersey_release_created = self.test_jersey_release_creation()
        
        if jersey_release_created:
            self.verify_jersey_release_in_database()
        
        print()
        
        # Phase 4: Vestiaire Endpoint Verification
        print("📋 PHASE 4: VESTIAIRE ENDPOINT VERIFICATION")
        print("-" * 42)
        vestiaire_working = self.verify_vestiaire_endpoint()
        
        print()
        
        # Phase 5: Complete Workflow Test
        print("📋 PHASE 5: COMPLETE WORKFLOW TEST")
        print("-" * 35)
        workflow_success = self.test_complete_workflow_add_to_collection()
        
        print()
        
        # Phase 6: Collection Data Quality Check
        print("📋 PHASE 6: COLLECTION DATA QUALITY CHECK")
        print("-" * 40)
        collection_quality = self.verify_collection_data_quality()
        
        print()
        
        # Summary
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 25)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical Analysis
        print("🔍 CRITICAL ANALYSIS")
        print("-" * 20)
        
        if not master_jerseys_available:
            print("❌ ROOT CAUSE IDENTIFIED: No Master Jerseys available in database")
            print("   → Cannot create Jersey Releases without Master Jerseys")
            print("   → This explains why Jersey Releases have disappeared")
        elif not jersey_release_created:
            print("❌ ROOT CAUSE IDENTIFIED: Jersey Release creation endpoint not working")
            print("   → Master Jerseys exist but cannot create Jersey Releases")
        elif not vestiaire_working:
            print("❌ ROOT CAUSE IDENTIFIED: Vestiaire endpoint not returning Jersey Releases")
            print("   → Jersey Releases may exist but not appearing in Vestiaire")
        elif not workflow_success:
            print("❌ ROOT CAUSE IDENTIFIED: Collection workflow broken")
            print("   → Jersey Releases exist but cannot be added to collections")
        elif not collection_quality:
            print("❌ ROOT CAUSE IDENTIFIED: Collection data aggregation issues")
            print("   → Collections exist but data not properly enriched")
        else:
            print("✅ WORKFLOW INVESTIGATION COMPLETE: All systems operational")
            print("   → Jersey Release workflow is functional")
        
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS")
        print("-" * 18)
        
        if not master_jerseys_available:
            print("1. Create Master Jerseys (FC Barcelona, etc.) in database")
            print("2. Ensure Master Jersey creation endpoints are functional")
        
        if master_jerseys_available and not jersey_release_created:
            print("1. Fix Jersey Release creation endpoint (/api/jersey-releases)")
            print("2. Verify Master Jersey ID references are correct")
        
        if jersey_release_created and not vestiaire_working:
            print("1. Fix Vestiaire endpoint aggregation pipeline")
            print("2. Ensure Jersey Releases are properly linked to Master Jerseys")
        
        if vestiaire_working and not workflow_success:
            print("1. Fix collection addition endpoints")
            print("2. Verify Jersey Release ID references in collection system")
        
        if workflow_success and not collection_quality:
            print("1. Fix collection data aggregation pipeline")
            print("2. Ensure proper Jersey Release and Master Jersey data enrichment")
        
        print()
        print("🎯 INVESTIGATION COMPLETE")
        print(f"Overall System Health: {success_rate:.1f}%")
        
        return success_rate > 80

def main():
    """Main test execution"""
    investigator = JerseyReleaseWorkflowInvestigator()
    success = investigator.run_comprehensive_investigation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()