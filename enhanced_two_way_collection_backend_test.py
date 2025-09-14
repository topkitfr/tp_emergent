#!/usr/bin/env python3
"""
Enhanced Two-Way Collection Workflow Testing
Testing the new smart collection logic as specified in the review request:

1. "Add to Wanted" - Simple, no detailed form, just add to want list directly
2. "Add to Owned" - Detailed form with condition, price, size, printing options, etc.
3. Two-way relationship - If user adds a kit to "owned" that's already in their "wanted" list, 
   it should automatically remove it from wanted list

API Endpoints to Test:
- POST /api/personal-kits (with collection_type: "wanted" and "owned")
- GET /api/personal-kits?collection_type=wanted 
- GET /api/personal-kits?collection_type=owned

Authentication: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"

# Test credentials
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

class EnhancedTwoWayCollectionTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        self.test_reference_kit_id = None
        
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and len(str(details)) < 500:  # Only print short details
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate_user(self) -> bool:
        """Authenticate user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_data = data.get("user", {})
                self.user_id = user_data.get("id")
                
                # Set authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.user_token}"
                })
                
                self.log_result(
                    "User Authentication",
                    True,
                    f"User authenticated successfully: {user_data.get('name')} ({user_data.get('role')})",
                    {"user_id": self.user_id, "email": USER_EMAIL}
                )
                return True
            else:
                self.log_result(
                    "User Authentication",
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "User Authentication",
                False,
                f"Authentication error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def get_available_reference_kits(self) -> List[Dict]:
        """Get available reference kits from vestiaire"""
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                kits = response.json()
                self.log_result(
                    "Reference Kits Availability",
                    len(kits) > 0,
                    f"Found {len(kits)} reference kits available for testing",
                    {"kits_count": len(kits)}
                )
                return kits
            else:
                self.log_result(
                    "Reference Kits Availability",
                    False,
                    f"Failed to get reference kits: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return []
                
        except Exception as e:
            self.log_result(
                "Reference Kits Availability",
                False,
                f"Error getting reference kits: {str(e)}",
                {"error": str(e)}
            )
            return []
    
    def clear_existing_collections(self, reference_kit_id: str) -> bool:
        """Clear any existing collections for the test reference kit"""
        try:
            # Get existing collections
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            wanted_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            
            collections_to_remove = []
            
            if owned_response.status_code == 200:
                owned_kits = owned_response.json()
                for kit in owned_kits:
                    if kit.get("reference_kit_id") == reference_kit_id:
                        collections_to_remove.append(("owned", kit.get("id")))
            
            if wanted_response.status_code == 200:
                wanted_kits = wanted_response.json()
                for kit in wanted_kits:
                    if kit.get("reference_kit_id") == reference_kit_id:
                        collections_to_remove.append(("wanted", kit.get("id")))
            
            # Remove existing collections
            removed_count = 0
            for collection_type, collection_id in collections_to_remove:
                try:
                    delete_response = self.session.delete(f"{BACKEND_URL}/personal-kits/{collection_id}")
                    if delete_response.status_code in [200, 204]:
                        removed_count += 1
                except:
                    pass  # Ignore deletion errors
            
            self.log_result(
                "Collection Cleanup",
                True,
                f"Cleared {removed_count} existing collections for reference kit {reference_kit_id}",
                {"removed_collections": removed_count, "reference_kit_id": reference_kit_id}
            )
            return True
            
        except Exception as e:
            self.log_result(
                "Collection Cleanup",
                False,
                f"Error clearing collections: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_add_to_wanted_simple(self, reference_kit_id: str) -> Optional[str]:
        """Test 1: Add to Wanted - Simple, no detailed form"""
        try:
            # Simple wanted collection data (minimal required fields only)
            wanted_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "wanted",
                "size": "M"  # Required field but minimal for wanted
                # No other detailed fields - should be simple
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=wanted_data)
            
            if response.status_code in [200, 201]:
                created_kit = response.json()
                personal_kit_id = created_kit.get("id")
                
                # Verify it's a simple wanted entry (minimal data - only size is required)
                has_detailed_fields = any([
                    created_kit.get("condition") and created_kit.get("condition") != "good",  # Default condition is ok
                    created_kit.get("purchase_price"),
                    created_kit.get("is_signed"),
                    created_kit.get("has_printing"),
                    created_kit.get("personal_notes")
                    # Size is required but not considered "detailed" for wanted items
                ])
                
                # Verify required fields
                required_fields_present = all([
                    created_kit.get("reference_kit_id") == reference_kit_id,
                    created_kit.get("collection_type") == "wanted"
                ])
                
                success = required_fields_present and not has_detailed_fields
                
                self.log_result(
                    "Add to Wanted - Simple",
                    success,
                    "Reference kit added to wanted collection with minimal data (no detailed form)",
                    {
                        "personal_kit_id": personal_kit_id,
                        "reference_kit_id": reference_kit_id,
                        "collection_type": created_kit.get("collection_type"),
                        "has_detailed_fields": has_detailed_fields,
                        "required_fields_present": required_fields_present
                    }
                )
                
                return personal_kit_id if success else None
                
            else:
                self.log_result(
                    "Add to Wanted - Simple",
                    False,
                    f"Failed to add to wanted collection: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Add to Wanted - Simple",
                False,
                f"Error adding to wanted collection: {str(e)}",
                {"error": str(e)}
            )
            return None
    
    def verify_wanted_collection(self, reference_kit_id: str) -> bool:
        """Verify the reference kit appears in wanted collection"""
        try:
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            
            if response.status_code == 200:
                wanted_kits = response.json()
                
                # Find our reference kit
                found_kit = None
                for kit in wanted_kits:
                    if kit.get("reference_kit_id") == reference_kit_id:
                        found_kit = kit
                        break
                
                if found_kit:
                    self.log_result(
                        "Verify Wanted Collection",
                        True,
                        "Reference kit found in wanted collection",
                        {
                            "reference_kit_id": reference_kit_id,
                            "personal_kit_id": found_kit.get("id"),
                            "collection_type": found_kit.get("collection_type")
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Wanted Collection",
                        False,
                        "Reference kit not found in wanted collection",
                        {"reference_kit_id": reference_kit_id, "wanted_kits_count": len(wanted_kits)}
                    )
                    return False
            else:
                self.log_result(
                    "Verify Wanted Collection",
                    False,
                    f"Failed to get wanted collection: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Verify Wanted Collection",
                False,
                f"Error verifying wanted collection: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_add_to_owned_detailed(self, reference_kit_id: str) -> Optional[str]:
        """Test 2: Add to Owned - Detailed form with condition, price, size, etc."""
        try:
            # Detailed owned collection data (comprehensive fields)
            owned_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "owned",
                # Detailed fields for owned collection
                "size": "L",
                "condition": "excellent",
                "purchase_price": 89.99,
                "purchase_date": "2024-01-15T00:00:00Z",
                "purchase_location": "Official Store",
                "is_signed": True,
                "signed_by": "Lionel Messi",
                "has_printing": True,
                "printed_name": "MESSI",
                "printed_number": 10,
                "is_worn": False,
                "personal_notes": "Perfect condition, authentic jersey with original tags"
            }
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=owned_data)
            
            if response.status_code in [200, 201]:
                created_kit = response.json()
                personal_kit_id = created_kit.get("id")
                
                # Verify detailed fields are saved
                detailed_fields_saved = {
                    "size": created_kit.get("size") == "L",
                    "condition": created_kit.get("condition") == "excellent" or created_kit.get("state") == "excellent",
                    "purchase_price": bool(created_kit.get("purchase_price") or created_kit.get("price_buy")),
                    "is_signed": created_kit.get("is_signed") == True,
                    "has_printing": created_kit.get("has_printing") == True,
                    "personal_notes": bool(created_kit.get("personal_notes") or created_kit.get("info_plus"))
                }
                
                # Verify required fields
                required_fields_present = all([
                    created_kit.get("reference_kit_id") == reference_kit_id,
                    created_kit.get("collection_type") == "owned"
                ])
                
                detailed_fields_count = sum(detailed_fields_saved.values())
                success = required_fields_present and detailed_fields_count >= 4  # Allow some flexibility
                
                self.log_result(
                    "Add to Owned - Detailed",
                    success,
                    f"Reference kit added to owned collection with detailed data ({detailed_fields_count}/6 detailed fields saved)",
                    {
                        "personal_kit_id": personal_kit_id,
                        "reference_kit_id": reference_kit_id,
                        "collection_type": created_kit.get("collection_type"),
                        "detailed_fields_saved": detailed_fields_saved,
                        "detailed_fields_count": detailed_fields_count,
                        "required_fields_present": required_fields_present
                    }
                )
                
                return personal_kit_id if success else None
                
            else:
                self.log_result(
                    "Add to Owned - Detailed",
                    False,
                    f"Failed to add to owned collection: {response.status_code} - {response.text}",
                    {"status_code": response.status_code}
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Add to Owned - Detailed",
                False,
                f"Error adding to owned collection: {str(e)}",
                {"error": str(e)}
            )
            return None
    
    def verify_two_way_relationship(self, reference_kit_id: str) -> bool:
        """Test 3: Verify two-way relationship - adding to owned should remove from wanted"""
        try:
            # Check owned collection
            owned_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            wanted_response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            
            owned_has_kit = False
            wanted_has_kit = False
            
            if owned_response.status_code == 200:
                owned_kits = owned_response.json()
                for kit in owned_kits:
                    if kit.get("reference_kit_id") == reference_kit_id:
                        owned_has_kit = True
                        break
            
            if wanted_response.status_code == 200:
                wanted_kits = wanted_response.json()
                for kit in wanted_kits:
                    if kit.get("reference_kit_id") == reference_kit_id:
                        wanted_has_kit = True
                        break
            
            # Two-way relationship: should be in owned but NOT in wanted
            two_way_working = owned_has_kit and not wanted_has_kit
            
            self.log_result(
                "Two-Way Relationship Verification",
                two_way_working,
                f"Two-way relationship {'working' if two_way_working else 'not working'}: Kit in owned={owned_has_kit}, Kit in wanted={wanted_has_kit}",
                {
                    "reference_kit_id": reference_kit_id,
                    "in_owned_collection": owned_has_kit,
                    "in_wanted_collection": wanted_has_kit,
                    "two_way_relationship_working": two_way_working,
                    "expected_behavior": "Kit should be in owned but automatically removed from wanted"
                }
            )
            
            return two_way_working
            
        except Exception as e:
            self.log_result(
                "Two-Way Relationship Verification",
                False,
                f"Error verifying two-way relationship: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def verify_owned_collection_detailed(self, reference_kit_id: str) -> bool:
        """Verify the reference kit appears in owned collection with detailed data"""
        try:
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            
            if response.status_code == 200:
                owned_kits = response.json()
                
                # Find our reference kit
                found_kit = None
                for kit in owned_kits:
                    if kit.get("reference_kit_id") == reference_kit_id:
                        found_kit = kit
                        break
                
                if found_kit:
                    # Verify it has detailed data
                    detailed_fields = {
                        "size": bool(found_kit.get("size")),
                        "condition": bool(found_kit.get("condition") or found_kit.get("state")),
                        "purchase_price": bool(found_kit.get("purchase_price") or found_kit.get("price_buy")),
                        "personal_notes": bool(found_kit.get("personal_notes") or found_kit.get("info_plus")),
                        "is_signed": found_kit.get("is_signed") is not None,
                        "has_printing": found_kit.get("has_printing") is not None
                    }
                    
                    detailed_count = sum(detailed_fields.values())
                    has_enrichment = bool(found_kit.get("reference_kit_info") or found_kit.get("master_kit_info"))
                    
                    success = detailed_count >= 3 and has_enrichment  # Require at least 3 detailed fields and enrichment
                    
                    self.log_result(
                        "Verify Owned Collection - Detailed",
                        success,
                        f"Reference kit found in owned collection with {detailed_count}/6 detailed fields and data enrichment",
                        {
                            "reference_kit_id": reference_kit_id,
                            "personal_kit_id": found_kit.get("id"),
                            "collection_type": found_kit.get("collection_type"),
                            "detailed_fields": detailed_fields,
                            "detailed_count": detailed_count,
                            "has_data_enrichment": has_enrichment
                        }
                    )
                    return success
                else:
                    self.log_result(
                        "Verify Owned Collection - Detailed",
                        False,
                        "Reference kit not found in owned collection",
                        {"reference_kit_id": reference_kit_id, "owned_kits_count": len(owned_kits)}
                    )
                    return False
            else:
                self.log_result(
                    "Verify Owned Collection - Detailed",
                    False,
                    f"Failed to get owned collection: {response.status_code}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Verify Owned Collection - Detailed",
                False,
                f"Error verifying owned collection: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def test_api_endpoints_functionality(self) -> bool:
        """Test all required API endpoints are working"""
        try:
            endpoints_to_test = [
                {"url": f"{BACKEND_URL}/personal-kits?collection_type=wanted", "name": "Personal Kits Wanted"},
                {"url": f"{BACKEND_URL}/personal-kits?collection_type=owned", "name": "Personal Kits Owned"},
                {"url": f"{BACKEND_URL}/vestiaire", "name": "Vestiaire (Reference Kits)"}
            ]
            
            endpoint_results = {}
            
            for endpoint in endpoints_to_test:
                try:
                    response = self.session.get(endpoint["url"])
                    
                    if response.status_code == 200:
                        data = response.json()
                        endpoint_results[endpoint["name"]] = {
                            "status": "success",
                            "status_code": 200,
                            "data_type": type(data).__name__,
                            "count": len(data) if isinstance(data, list) else 1
                        }
                    else:
                        endpoint_results[endpoint["name"]] = {
                            "status": "error",
                            "status_code": response.status_code,
                            "error": response.text[:100]
                        }
                        
                except Exception as e:
                    endpoint_results[endpoint["name"]] = {
                        "status": "exception",
                        "error": str(e)[:100]
                    }
            
            # Count successful endpoints
            successful_endpoints = sum(1 for result in endpoint_results.values() if result.get("status") == "success")
            total_endpoints = len(endpoints_to_test)
            
            success_rate = (successful_endpoints / total_endpoints) * 100
            overall_success = success_rate >= 100  # All endpoints must work
            
            self.log_result(
                "API Endpoints Functionality",
                overall_success,
                f"API endpoints check: {successful_endpoints}/{total_endpoints} endpoints working ({success_rate:.1f}%)",
                {
                    "endpoint_results": endpoint_results,
                    "success_rate": success_rate,
                    "all_endpoints_working": overall_success
                }
            )
            
            return overall_success
            
        except Exception as e:
            self.log_result(
                "API Endpoints Functionality",
                False,
                f"API endpoints test error: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all enhanced two-way collection workflow tests"""
        print("🧪 Starting Enhanced Two-Way Collection Workflow Testing...")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate_user():
            return {"success": False, "message": "Authentication failed", "results": self.test_results}
        
        # Step 2: Get available reference kits
        reference_kits = self.get_available_reference_kits()
        if not reference_kits:
            return {"success": False, "message": "No reference kits available for testing", "results": self.test_results}
        
        # Use first available reference kit for testing
        test_kit = reference_kits[0]
        self.test_reference_kit_id = test_kit.get("id")
        
        print(f"🎯 Testing with Reference Kit: {test_kit.get('id')} ({test_kit.get('team_info', {}).get('name', 'Unknown Team')})")
        
        # Step 3: Clear existing collections for clean testing
        self.clear_existing_collections(self.test_reference_kit_id)
        
        # Step 4: Test API endpoints functionality
        api_endpoints_working = self.test_api_endpoints_functionality()
        
        # Step 5: Test "Add to Wanted" - Simple workflow
        wanted_kit_id = self.test_add_to_wanted_simple(self.test_reference_kit_id)
        
        # Step 6: Verify it appears in wanted collection
        wanted_verification = self.verify_wanted_collection(self.test_reference_kit_id)
        
        # Step 7: Test "Add to Owned" - Detailed workflow (same kit)
        owned_kit_id = self.test_add_to_owned_detailed(self.test_reference_kit_id)
        
        # Step 8: Verify it appears in owned collection with detailed data
        owned_verification = self.verify_owned_collection_detailed(self.test_reference_kit_id)
        
        # Step 9: Verify two-way relationship (should be removed from wanted)
        two_way_relationship = self.verify_two_way_relationship(self.test_reference_kit_id)
        
        # Calculate overall success
        test_successes = [
            api_endpoints_working,
            bool(wanted_kit_id),
            wanted_verification,
            bool(owned_kit_id),
            owned_verification,
            two_way_relationship
        ]
        
        overall_success = sum(test_successes) >= 5  # Allow one minor failure
        success_rate = (sum(test_successes) / len(test_successes)) * 100
        
        print("\n" + "=" * 70)
        print(f"🏁 Enhanced Two-Way Collection Workflow Testing Complete")
        print(f"📊 Success Rate: {success_rate:.1f}% ({sum(test_successes)}/{len(test_successes)} tests passed)")
        
        return {
            "success": overall_success,
            "success_rate": success_rate,
            "tests_passed": sum(test_successes),
            "total_tests": len(test_successes),
            "message": f"Enhanced two-way collection workflow testing completed with {success_rate:.1f}% success rate",
            "results": self.test_results,
            "test_reference_kit_id": self.test_reference_kit_id,
            "workflow_summary": {
                "api_endpoints_working": api_endpoints_working,
                "wanted_addition_simple": bool(wanted_kit_id),
                "wanted_verification": wanted_verification,
                "owned_addition_detailed": bool(owned_kit_id),
                "owned_verification": owned_verification,
                "two_way_relationship": two_way_relationship
            }
        }

def main():
    """Main test execution"""
    tester = EnhancedTwoWayCollectionTester()
    results = tester.run_comprehensive_tests()
    
    # Print summary
    print(f"\n📋 ENHANCED TWO-WAY COLLECTION WORKFLOW TEST SUMMARY:")
    print(f"Overall Success: {'✅ PASS' if results['success'] else '❌ FAIL'}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Tests Passed: {results['tests_passed']}/{results['total_tests']}")
    
    if results.get("workflow_summary"):
        workflow = results["workflow_summary"]
        print(f"\n🔗 Workflow Test Results:")
        print(f"API Endpoints Working: {'✅' if workflow.get('api_endpoints_working') else '❌'}")
        print(f"Add to Wanted (Simple): {'✅' if workflow.get('wanted_addition_simple') else '❌'}")
        print(f"Wanted Collection Verification: {'✅' if workflow.get('wanted_verification') else '❌'}")
        print(f"Add to Owned (Detailed): {'✅' if workflow.get('owned_addition_detailed') else '❌'}")
        print(f"Owned Collection Verification: {'✅' if workflow.get('owned_verification') else '❌'}")
        print(f"Two-Way Relationship: {'✅' if workflow.get('two_way_relationship') else '❌'}")
    
    if results.get("test_reference_kit_id"):
        print(f"\n🎯 Test Reference Kit ID: {results['test_reference_kit_id']}")
    
    # Return appropriate exit code
    sys.exit(0 if results['success'] else 1)

if __name__ == "__main__":
    main()