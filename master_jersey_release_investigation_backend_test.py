#!/usr/bin/env python3
"""
MASTER JERSEY / JERSEY RELEASE LOGIC INVESTIGATION - BACKEND TEST
================================================================

Investigation requise pour comprendre le vrai problème dans la logique Master Jersey / Jersey Release:

1. **Vérifier la logique Vestiaire:**
   - Tester `/api/vestiaire` - Est-ce que ça retourne les Jersey Releases correctement?
   - Vérifier que chaque Jersey Release a un `master_jersey_id` qui pointe vers un Master Jersey
   - Confirmer que les Jersey Releases sont enrichis avec les données Master Jersey

2. **Tester l'ajout à collection avec Jersey Releases:**
   - Utiliser l'utilisateur steinmetzlivio@gmail.com/T0p_Mdp_1288*
   - Tester l'ajout d'un Jersey Release à sa collection avec POST `/api/users/{user_id}/collections`
   - Vérifier que le `jersey_release_id` est correctement utilisé (pas `jersey_id`)

3. **Vérifier la structure des données:**
   - Confirmer que les collections utilisent `jersey_release_id` pour pointer vers les Jersey Releases
   - Vérifier que les Jersey Releases ont bien `master_jersey_id` pour pointer vers les Master Jerseys
   - S'assurer que cette chaîne de données est cohérente

4. **Tester le workflow complet:**
   - Utilisateur voit Jersey Releases dans vestiaire
   - Utilisateur peut ajouter Jersey Release à owned/wanted
   - Utilisateur peut voir ses collections avec les Jersey Releases ajoutés

**Authentification:**
- Utilisateur: steinmetzlivio@gmail.com / T0p_Mdp_1288*

**Focus:** Identifier si le problème vient de la logique Master Jersey / Jersey Release ou d'autre chose dans cette chaîne de données.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class MasterJerseyReleaseInvestigator:
    def __init__(self):
        self.user_token = None
        self.user_user_id = None
        self.test_results = []
        self.vestiaire_data = None
        self.jersey_releases = []
        self.master_jerseys = []
        
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

    def authenticate_user(self):
        """Authenticate user and get token"""
        print("🔐 PHASE 1: USER AUTHENTICATION")
        print("=" * 50)
        
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
                    f"User: {user_data.get('name')}, ID: {self.user_user_id}, Role: {user_data.get('role')}"
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

    def test_vestiaire_endpoint(self):
        """Test /api/vestiaire endpoint and analyze Jersey Release structure"""
        print("🏪 PHASE 2: VESTIAIRE ENDPOINT ANALYSIS")
        print("=" * 50)
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if response.status_code == 200:
                self.vestiaire_data = response.json()
                
                # Check if it's an array
                if isinstance(self.vestiaire_data, list):
                    jersey_count = len(self.vestiaire_data)
                    self.jersey_releases = self.vestiaire_data
                    
                    self.log_result(
                        "Vestiaire Endpoint Response", 
                        True, 
                        f"Returns array with {jersey_count} Jersey Releases"
                    )
                    
                    # Analyze first Jersey Release structure
                    if jersey_count > 0:
                        first_jersey = self.vestiaire_data[0]
                        self.analyze_jersey_release_structure(first_jersey)
                        
                        # Check all Jersey Releases for master_jersey_id
                        self.verify_master_jersey_links()
                    else:
                        self.log_result(
                            "Jersey Release Data", 
                            False, 
                            "No Jersey Releases found in vestiaire"
                        )
                        
                else:
                    self.log_result(
                        "Vestiaire Endpoint Response", 
                        False, 
                        f"Expected array, got: {type(self.vestiaire_data)}"
                    )
                    
            else:
                self.log_result(
                    "Vestiaire Endpoint Response", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Vestiaire Endpoint Response", False, f"Exception: {str(e)}")

    def analyze_jersey_release_structure(self, jersey_release):
        """Analyze the structure of a Jersey Release"""
        print("🔍 JERSEY RELEASE STRUCTURE ANALYSIS")
        print("-" * 40)
        
        # Check for required fields
        required_fields = ['id', 'master_jersey_id']
        missing_fields = []
        
        for field in required_fields:
            if field not in jersey_release:
                missing_fields.append(field)
        
        if missing_fields:
            self.log_result(
                "Jersey Release Required Fields", 
                False, 
                f"Missing fields: {missing_fields}"
            )
        else:
            self.log_result(
                "Jersey Release Required Fields", 
                True, 
                f"All required fields present: {required_fields}"
            )
        
        # Check for master_jersey_info (enriched data)
        if 'master_jersey_info' in jersey_release:
            master_info = jersey_release['master_jersey_info']
            self.log_result(
                "Master Jersey Enrichment", 
                True, 
                f"Master Jersey data: Team={master_info.get('team')}, Season={master_info.get('season')}, Brand={master_info.get('brand')}"
            )
        else:
            self.log_result(
                "Master Jersey Enrichment", 
                False, 
                "No master_jersey_info found - Jersey Releases not enriched with Master Jersey data"
            )
        
        # Print full structure for analysis
        print("📋 COMPLETE JERSEY RELEASE STRUCTURE:")
        print(json.dumps(jersey_release, indent=2, default=str))
        print()

    def verify_master_jersey_links(self):
        """Verify that all Jersey Releases have valid master_jersey_id links"""
        print("🔗 MASTER JERSEY LINKS VERIFICATION")
        print("-" * 40)
        
        valid_links = 0
        invalid_links = 0
        
        for jersey_release in self.jersey_releases:
            jersey_id = jersey_release.get('id', 'Unknown')
            master_jersey_id = jersey_release.get('master_jersey_id')
            
            if master_jersey_id:
                valid_links += 1
                print(f"✅ Jersey Release {jersey_id} → Master Jersey {master_jersey_id}")
            else:
                invalid_links += 1
                print(f"❌ Jersey Release {jersey_id} → No master_jersey_id")
        
        success = invalid_links == 0
        self.log_result(
            "Master Jersey ID Links", 
            success, 
            f"Valid links: {valid_links}, Invalid links: {invalid_links}"
        )

    def test_collection_addition(self):
        """Test adding Jersey Releases to user collection"""
        print("📦 PHASE 3: COLLECTION ADDITION TESTING")
        print("=" * 50)
        
        if not self.jersey_releases:
            self.log_result(
                "Collection Addition Test", 
                False, 
                "No Jersey Releases available for testing"
            )
            return
        
        # Test adding first Jersey Release to owned collection
        test_jersey = self.jersey_releases[0]
        jersey_release_id = test_jersey.get('id')
        
        if not jersey_release_id:
            self.log_result(
                "Collection Addition Test", 
                False, 
                "Jersey Release has no ID"
            )
            return
        
        # Test owned collection
        self.test_add_to_collection(jersey_release_id, "owned")
        
        # Test wanted collection (if we have more than one Jersey Release)
        if len(self.jersey_releases) > 1:
            second_jersey = self.jersey_releases[1]
            second_jersey_id = second_jersey.get('id')
            if second_jersey_id:
                self.test_add_to_collection(second_jersey_id, "wanted")

    def test_add_to_collection(self, jersey_release_id, collection_type):
        """Test adding a specific Jersey Release to collection"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            payload = {
                "jersey_release_id": jersey_release_id,  # Using jersey_release_id, not jersey_id
                "collection_type": collection_type
            }
            
            response = requests.post(
                f"{BACKEND_URL}/users/{self.user_user_id}/collections", 
                headers=headers, 
                json=payload
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                collection_id = data.get('collection_id', 'Unknown')
                
                self.log_result(
                    f"Add to {collection_type.title()} Collection", 
                    True, 
                    f"Jersey Release {jersey_release_id} added successfully (Collection ID: {collection_id})"
                )
                
                # Verify the collection was created correctly
                self.verify_collection_structure(collection_id, jersey_release_id, collection_type)
                
            elif response.status_code == 400:
                # Check if it's a duplicate error (expected behavior)
                error_message = response.text
                if "already in collection" in error_message.lower():
                    self.log_result(
                        f"Add to {collection_type.title()} Collection", 
                        True, 
                        f"Duplicate prevention working: {error_message}"
                    )
                else:
                    self.log_result(
                        f"Add to {collection_type.title()} Collection", 
                        False, 
                        f"HTTP 400: {error_message}"
                    )
            else:
                self.log_result(
                    f"Add to {collection_type.title()} Collection", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result(f"Add to {collection_type.title()} Collection", False, f"Exception: {str(e)}")

    def verify_collection_structure(self, collection_id, jersey_release_id, collection_type):
        """Verify that the collection was created with correct structure"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/{collection_type}", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                
                # Find our collection
                target_collection = None
                for collection in collections:
                    if collection.get('id') == collection_id:
                        target_collection = collection
                        break
                
                if target_collection:
                    # Check structure
                    has_jersey_release_id = 'jersey_release_id' in target_collection
                    has_jersey_release_data = 'jersey_release' in target_collection
                    has_master_jersey_data = 'master_jersey' in target_collection
                    
                    structure_details = []
                    if has_jersey_release_id:
                        structure_details.append(f"jersey_release_id: {target_collection['jersey_release_id']}")
                    if has_jersey_release_data:
                        structure_details.append("jersey_release data: ✅")
                    if has_master_jersey_data:
                        structure_details.append("master_jersey data: ✅")
                    
                    success = has_jersey_release_id and has_jersey_release_data
                    self.log_result(
                        f"{collection_type.title()} Collection Structure", 
                        success, 
                        "; ".join(structure_details) if structure_details else "No expected fields found"
                    )
                    
                    # Print full collection structure for analysis
                    print(f"📋 COLLECTION STRUCTURE ({collection_type.upper()}):")
                    print(json.dumps(target_collection, indent=2, default=str))
                    print()
                    
                else:
                    self.log_result(
                        f"{collection_type.title()} Collection Structure", 
                        False, 
                        f"Collection {collection_id} not found in user's {collection_type} collections"
                    )
            else:
                self.log_result(
                    f"{collection_type.title()} Collection Structure", 
                    False, 
                    f"Failed to retrieve collections: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(f"{collection_type.title()} Collection Structure", False, f"Exception: {str(e)}")

    def test_complete_workflow(self):
        """Test the complete user workflow"""
        print("🔄 PHASE 4: COMPLETE WORKFLOW TESTING")
        print("=" * 50)
        
        # Test user's existing collections
        self.test_user_collections()
        
        # Test general collections endpoint
        self.test_general_collections_endpoint()

    def test_user_collections(self):
        """Test user's owned and wanted collections"""
        for collection_type in ['owned', 'wanted']:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/{collection_type}", headers=headers)
                
                if response.status_code == 200:
                    collections = response.json()
                    count = len(collections)
                    
                    self.log_result(
                        f"User {collection_type.title()} Collections", 
                        True, 
                        f"Retrieved {count} {collection_type} collections"
                    )
                    
                    # Analyze first collection if exists
                    if count > 0:
                        first_collection = collections[0]
                        print(f"📋 SAMPLE {collection_type.upper()} COLLECTION:")
                        print(json.dumps(first_collection, indent=2, default=str))
                        print()
                        
                else:
                    self.log_result(
                        f"User {collection_type.title()} Collections", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(f"User {collection_type.title()} Collections", False, f"Exception: {str(e)}")

    def test_general_collections_endpoint(self):
        """Test the general collections endpoint that was reported as problematic"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                count = len(collections)
                
                success = count > 0
                self.log_result(
                    "General Collections Endpoint", 
                    success, 
                    f"Retrieved {count} total collections" + (" (ISSUE: Should show user's collections)" if count == 0 else "")
                )
                
                if count > 0:
                    print("📋 SAMPLE GENERAL COLLECTION:")
                    print(json.dumps(collections[0], indent=2, default=str))
                    print()
                    
            else:
                self.log_result(
                    "General Collections Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("General Collections Endpoint", False, f"Exception: {str(e)}")

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize issues
        critical_issues = []
        data_structure_issues = []
        workflow_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                test_name = result["test"]
                details = result["details"]
                
                if "Authentication" in test_name:
                    critical_issues.append(f"🚨 {test_name}: {details}")
                elif "Structure" in test_name or "Links" in test_name or "Enrichment" in test_name:
                    data_structure_issues.append(f"📊 {test_name}: {details}")
                else:
                    workflow_issues.append(f"🔄 {test_name}: {details}")
        
        # Print issues by category
        if critical_issues:
            print("🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"   {issue}")
            print()
        
        if data_structure_issues:
            print("📊 DATA STRUCTURE ISSUES:")
            for issue in data_structure_issues:
                print(f"   {issue}")
            print()
        
        if workflow_issues:
            print("🔄 WORKFLOW ISSUES:")
            for issue in workflow_issues:
                print(f"   {issue}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        if self.vestiaire_data:
            jersey_count = len(self.jersey_releases)
            print(f"   • Vestiaire contains {jersey_count} Jersey Releases")
            
            if jersey_count > 0:
                first_jersey = self.jersey_releases[0]
                has_master_id = 'master_jersey_id' in first_jersey
                has_enrichment = 'master_jersey_info' in first_jersey
                
                print(f"   • Jersey Releases have master_jersey_id: {'✅' if has_master_id else '❌'}")
                print(f"   • Jersey Releases are enriched with Master Jersey data: {'✅' if has_enrichment else '❌'}")
        
        # Recommendations
        print()
        print("💡 RECOMMENDATIONS:")
        
        if failed_tests == 0:
            print("   • All tests passed - Master Jersey / Jersey Release logic appears to be working correctly")
            print("   • If users are experiencing issues, the problem may be in the frontend or user experience")
        else:
            print("   • Focus on fixing the failed tests identified above")
            print("   • Verify the data chain: Master Jersey → Jersey Release → Collection")
            print("   • Check if the issue is in data structure, API endpoints, or frontend integration")
        
        return success_rate

    def run_investigation(self):
        """Run the complete Master Jersey / Jersey Release investigation"""
        print("🔍 MASTER JERSEY / JERSEY RELEASE LOGIC INVESTIGATION")
        print("=" * 70)
        print("Focus: Identifier si le problème vient de la logique Master Jersey / Jersey Release")
        print("User: steinmetzlivio@gmail.com")
        print()
        
        # Phase 1: Authentication
        if not self.authenticate_user():
            print("❌ Cannot proceed without authentication")
            return 0
        
        # Phase 2: Vestiaire Analysis
        self.test_vestiaire_endpoint()
        
        # Phase 3: Collection Testing
        self.test_collection_addition()
        
        # Phase 4: Complete Workflow
        self.test_complete_workflow()
        
        # Generate Summary
        success_rate = self.generate_summary()
        
        return success_rate

def main():
    """Main execution function"""
    investigator = MasterJerseyReleaseInvestigator()
    success_rate = investigator.run_investigation()
    
    # Exit with appropriate code
    if success_rate >= 90:
        print("🎉 Investigation completed successfully!")
        sys.exit(0)
    elif success_rate >= 70:
        print("⚠️  Investigation completed with some issues")
        sys.exit(1)
    else:
        print("❌ Investigation revealed significant problems")
        sys.exit(2)

if __name__ == "__main__":
    main()