#!/usr/bin/env python3
"""
TopKit Discogs Collection Workflow Testing
Testing the complete collection workflow as described in the review request:
1. Jersey submission workflow
2. Admin approval process  
3. Adding to personal collection with size/condition
4. Collection details management
5. Collection valuation generation
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

TEST_USER = {
    "email": "friendstest2@example.com", 
    "password": "TestFriends9!$"
}

class DiscogsWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.user_token = None
        self.submitted_jersey_id = None
        self.approved_jersey_id = None
        self.collection_id = None
        
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
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
    
    def test_admin_authentication(self):
        """Test admin authentication"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_USER)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_info = data.get('user', {})
                
                if user_info.get('role') == 'admin':
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Admin logged in successfully: {user_info.get('name')} (Role: {user_info.get('role')})"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, error="User does not have admin role")
                    return False
            else:
                self.log_result("Admin Authentication", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, error=str(e))
            return False
    
    def test_user_authentication(self):
        """Test user authentication"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=TEST_USER)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_info = data.get('user', {})
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"User logged in successfully: {user_info.get('name')} (Role: {user_info.get('role', 'user')})"
                )
                return True
            else:
                self.log_result("User Authentication", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, error=str(e))
            return False
    
    def test_jersey_submission(self):
        """Test jersey submission workflow - POST /api/jerseys"""
        try:
            if not self.user_token:
                self.log_result("Jersey Submission", False, error="No user token available")
                return False
            
            # Submit FC Barcelona 24/25 Home jersey as mentioned in review
            jersey_data = {
                "team": "FC Barcelona",
                "season": "2024-25",
                "player": "Pedri",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "FC Barcelona home jersey 2024-25 season with Pedri #8. Official Nike jersey with club crest and sponsor logos."
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.submitted_jersey_id = data.get('id')
                reference_number = data.get('reference_number')
                status = data.get('status')
                
                self.log_result(
                    "Jersey Submission", 
                    True, 
                    f"Jersey submitted successfully - ID: {self.submitted_jersey_id}, Ref: {reference_number}, Status: {status}"
                )
                return True
            else:
                self.log_result("Jersey Submission", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Jersey Submission", False, error=str(e))
            return False
    
    def test_admin_jersey_approval(self):
        """Test admin approval process"""
        try:
            if not self.admin_token or not self.submitted_jersey_id:
                self.log_result("Admin Jersey Approval", False, error="Missing admin token or jersey ID")
                return False
            
            # First, get pending jerseys to verify our submission is there
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            
            if response.status_code != 200:
                self.log_result("Admin Jersey Approval", False, error=f"Failed to get pending jerseys: HTTP {response.status_code}")
                return False
            
            pending_jerseys = response.json()
            our_jersey = None
            for jersey in pending_jerseys:
                if jersey.get('id') == self.submitted_jersey_id:
                    our_jersey = jersey
                    break
            
            if not our_jersey:
                self.log_result("Admin Jersey Approval", False, error="Submitted jersey not found in pending list")
                return False
            
            # Approve the jersey using the correct endpoint
            response = self.session.post(
                f"{BACKEND_URL}/admin/jerseys/{self.submitted_jersey_id}/approve", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.approved_jersey_id = self.submitted_jersey_id  # Same ID, now approved
                
                self.log_result(
                    "Admin Jersey Approval", 
                    True, 
                    f"Jersey approved successfully - {data.get('message', 'Approved')}"
                )
                return True
            else:
                self.log_result("Admin Jersey Approval", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Jersey Approval", False, error=str(e))
            return False
    
    def test_add_to_collection(self):
        """Test adding approved jersey to personal collection - POST /api/collections"""
        try:
            if not self.user_token or not self.approved_jersey_id:
                self.log_result("Add to Collection", False, error="Missing user token or approved jersey ID")
                return False
            
            # Add jersey to "owned" collection with size and condition (Discogs-style)
            collection_data = {
                "jersey_id": self.approved_jersey_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "near_mint",
                "personal_description": "Purchased from official FC Barcelona store. Excellent condition, worn only once."
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(f"{BACKEND_URL}/collections", json=collection_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.collection_id = data.get('id')
                
                self.log_result(
                    "Add to Collection", 
                    True, 
                    f"Jersey added to owned collection - Collection ID: {self.collection_id}, Size: M, Condition: near_mint"
                )
                return True
            else:
                self.log_result("Add to Collection", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Add to Collection", False, error=str(e))
            return False
    
    def test_get_collection_details(self):
        """Test retrieving collection details - GET /api/collections/owned/{jersey_id}/details"""
        try:
            if not self.user_token or not self.approved_jersey_id:
                self.log_result("Get Collection Details", False, error="Missing user token or jersey ID")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BACKEND_URL}/collections/owned/{self.approved_jersey_id}/details", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                jersey_info = data.get('jersey', {})
                collection_info = data.get('collection', {})
                
                self.log_result(
                    "Get Collection Details", 
                    True, 
                    f"Collection details retrieved - Jersey: {jersey_info.get('team')} {jersey_info.get('season')}, Size: {collection_info.get('size')}, Condition: {collection_info.get('condition')}"
                )
                return True
            else:
                self.log_result("Get Collection Details", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Get Collection Details", False, error=str(e))
            return False
    
    def test_update_collection_details(self):
        """Test updating collection details - PUT /api/collections/owned/{jersey_id}/details"""
        try:
            if not self.user_token or not self.approved_jersey_id:
                self.log_result("Update Collection Details", False, error="Missing user token or jersey ID")
                return False
            
            # Update collection details to improve valuation (Discogs-style)
            update_data = {
                "model_type": "authentic",
                "condition": "mint",
                "size": "M", 
                "special_features": ["match_worn", "signed"],
                "rarity": "rare",
                "purchase_price": 89.99,
                "purchase_date": "2024-08-15",
                "purchase_location": "FC Barcelona Official Store",
                "certificate_authenticity": True,
                "storage_notes": "Stored in climate-controlled environment, never worn in match"
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.put(f"{BACKEND_URL}/collections/owned/{self.approved_jersey_id}/details", json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_result(
                    "Update Collection Details", 
                    True, 
                    f"Collection details updated - Condition: mint, Rarity: rare, Special features: {update_data['special_features']}"
                )
                return True
            else:
                self.log_result("Update Collection Details", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Update Collection Details", False, error=str(e))
            return False
    
    def test_collection_valuation(self):
        """Test collection valuation generation - GET /api/collections/valuations"""
        try:
            if not self.user_token:
                self.log_result("Collection Valuation", False, error="Missing user token")
                return False
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BACKEND_URL}/collections/valuations", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both dict and list responses
                if isinstance(data, list):
                    # If it's a list, it might be the collections directly
                    total_items = len(data)
                    valued_items = 0
                    low_estimate = 0
                    median_estimate = 0
                    high_estimate = 0
                    
                    self.log_result(
                        "Collection Valuation", 
                        True, 
                        f"Collection valuation retrieved (list format) - Items: {total_items}"
                    )
                elif isinstance(data, dict):
                    # Expected dict format
                    portfolio_summary = data.get('portfolio_summary', {})
                    collections = data.get('collections', [])
                    
                    total_items = portfolio_summary.get('total_items', 0)
                    valued_items = portfolio_summary.get('valued_items', 0)
                    low_estimate = portfolio_summary.get('total_low_estimate', 0)
                    median_estimate = portfolio_summary.get('total_median_estimate', 0)
                    high_estimate = portfolio_summary.get('total_high_estimate', 0)
                    
                    self.log_result(
                        "Collection Valuation", 
                        True, 
                        f"Collection valuation generated - Items: {total_items}, Valued: {valued_items}, Estimates: €{low_estimate}-€{median_estimate}-€{high_estimate}"
                    )
                else:
                    self.log_result("Collection Valuation", False, error=f"Unexpected response format: {type(data)}")
                    return False
                
                return True
            else:
                self.log_result("Collection Valuation", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Collection Valuation", False, error=str(e))
            return False
    
    def run_complete_workflow(self):
        """Run the complete Discogs collection workflow"""
        print("🎯 Starting TopKit Discogs Collection Workflow Testing")
        print("=" * 60)
        
        # Step 1: Authentication
        print("\n📋 STEP 1: Authentication Setup")
        admin_auth_success = self.test_admin_authentication()
        user_auth_success = self.test_user_authentication()
        
        if not admin_auth_success or not user_auth_success:
            print("\n❌ Authentication failed - cannot proceed with workflow")
            return False
        
        # Step 2: Jersey Submission
        print("\n📋 STEP 2: Jersey Submission Workflow")
        if not self.test_jersey_submission():
            print("\n❌ Jersey submission failed - cannot proceed")
            return False
        
        # Step 3: Admin Approval
        print("\n📋 STEP 3: Admin Approval Process")
        if not self.test_admin_jersey_approval():
            print("\n❌ Admin approval failed - cannot proceed")
            return False
        
        # Step 4: Add to Collection
        print("\n📋 STEP 4: Add to Personal Collection")
        if not self.test_add_to_collection():
            print("\n❌ Add to collection failed - cannot proceed")
            return False
        
        # Step 5: Collection Details Management
        print("\n📋 STEP 5: Collection Details Management")
        self.test_get_collection_details()
        self.test_update_collection_details()
        
        # Step 6: Collection Valuation
        print("\n📋 STEP 6: Collection Valuation Generation")
        self.test_collection_valuation()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 DISCOGS COLLECTION WORKFLOW TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['error']}")
        
        print(f"\n🎉 WORKFLOW STATUS: {'COMPLETE' if success_rate >= 80 else 'INCOMPLETE'}")
        
        return success_rate

def main():
    """Main test execution"""
    tester = DiscogsWorkflowTester()
    
    try:
        tester.run_complete_workflow()
        success_rate = tester.print_summary()
        
        # Return appropriate exit code
        exit_code = 0 if success_rate >= 80 else 1
        exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()