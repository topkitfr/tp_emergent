#!/usr/bin/env python3
"""
TopKit Enhanced Features Comprehensive Testing
Testing all specific requirements from the review request
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"

class TopKitEnhancedFeaturesTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.admin_token = None
        self.admin_user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def setup_users(self):
        """Setup test users"""
        try:
            # Regular user
            unique_email = f"enhanced_test_{int(time.time())}@topkit.com"
            
            user_payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "Enhanced Features Test User"
            }
            
            user_response = self.session.post(f"{self.base_url}/auth/register", json=user_payload)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                self.auth_token = user_data["token"]
                self.user_id = user_data["user"]["id"]
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                
                # Admin user
                admin_payload = {
                    "email": "topkitfr@gmail.com",
                    "password": "adminpass123"
                }
                
                admin_response = self.session.post(f"{self.base_url}/auth/login", json=admin_payload)
                
                if admin_response.status_code == 200:
                    admin_data = admin_response.json()
                    self.admin_token = admin_data["token"]
                    self.admin_user_id = admin_data["user"]["id"]
                    
                    self.log_test("Setup Users", "PASS", f"Regular user and admin ready")
                    return True
                else:
                    self.log_test("Setup Users", "FAIL", f"Admin login failed")
                    return False
            else:
                self.log_test("Setup Users", "FAIL", f"User registration failed")
                return False
                
        except Exception as e:
            self.log_test("Setup Users", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_sequential_reference_generation(self):
        """Test creating multiple jerseys to verify TK-000001, TK-000002, TK-000003 format"""
        try:
            if not self.auth_token:
                self.log_test("Sequential Reference Generation", "FAIL", "No auth token")
                return False
            
            jerseys_data = [
                {
                    "team": "Arsenal FC",
                    "season": "2023-24",
                    "player": "Bukayo Saka",
                    "size": "L",
                    "condition": "excellent",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Arsenal home jersey with Saka #7"
                },
                {
                    "team": "Tottenham Hotspur",
                    "season": "2023-24",
                    "player": "Harry Kane",
                    "size": "M",
                    "condition": "very_good",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Tottenham home jersey with Kane #10"
                },
                {
                    "team": "West Ham United",
                    "season": "2023-24",
                    "player": "Declan Rice",
                    "size": "L",
                    "condition": "good",
                    "manufacturer": "Umbro",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "West Ham home jersey with Rice #41"
                }
            ]
            
            created_references = []
            
            for jersey_data in jerseys_data:
                response = self.session.post(f"{self.base_url}/jerseys", json=jersey_data)
                
                if response.status_code == 200:
                    jersey = response.json()
                    reference = jersey.get("reference_number")
                    if reference:
                        created_references.append(reference)
                else:
                    self.log_test("Sequential Reference Generation", "FAIL", f"Jersey creation failed: {response.status_code}")
                    return False
            
            if len(created_references) == 3:
                # Verify all references follow TK-XXXXXX format
                valid_format = all(ref.startswith("TK-") and len(ref) == 9 for ref in created_references)
                
                if valid_format:
                    # Verify sequential numbering
                    numbers = [int(ref.split("-")[1]) for ref in created_references]
                    is_sequential = all(numbers[i] < numbers[i+1] for i in range(len(numbers)-1))
                    
                    if is_sequential:
                        self.log_test("Sequential Reference Generation", "PASS", 
                                    f"Sequential references: {', '.join(created_references)}")
                        return True
                    else:
                        self.log_test("Sequential Reference Generation", "FAIL", "References not sequential")
                        return False
                else:
                    self.log_test("Sequential Reference Generation", "FAIL", "Invalid reference format")
                    return False
            else:
                self.log_test("Sequential Reference Generation", "FAIL", f"Expected 3 references, got {len(created_references)}")
                return False
                
        except Exception as e:
            self.log_test("Sequential Reference Generation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_complete_moderation_workflow(self):
        """Test complete workflow: submission → suggestion → resubmission → approval"""
        try:
            if not self.auth_token or not self.admin_token:
                self.log_test("Complete Moderation Workflow", "FAIL", "Missing auth tokens")
                return False
            
            # Step 1: Submit jersey
            jersey_payload = {
                "team": "Newcastle United",
                "season": "2023-24",
                "player": "Alexander Isak",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Castore",
                "home_away": "home",
                "league": "Premier League",
                "description": "Newcastle home jersey"
            }
            
            submission_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if submission_response.status_code != 200:
                self.log_test("Complete Moderation Workflow", "FAIL", "Jersey submission failed")
                return False
            
            jersey_data = submission_response.json()
            jersey_id = jersey_data["id"]
            original_reference = jersey_data.get("reference_number")
            
            # Step 2: Admin suggests modifications
            self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
            
            suggestion_payload = {
                "jersey_id": jersey_id,
                "suggested_changes": "Please add more details about the jersey condition and any special features."
            }
            
            suggestion_response = self.session.post(f"{self.base_url}/admin/jerseys/{jersey_id}/suggest-modifications", json=suggestion_payload)
            
            if suggestion_response.status_code != 200:
                self.log_test("Complete Moderation Workflow", "FAIL", "Suggestion failed")
                return False
            
            # Step 3: User resubmits with modifications
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            
            time.sleep(1)  # Wait for suggestion to be processed
            
            resubmission_payload = {
                "team": "Newcastle United",
                "season": "2023-24",
                "player": "Alexander Isak",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Castore",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Newcastle United home jersey with Alexander Isak #14. Excellent condition with no visible wear, all logos and prints intact. Features the distinctive black and white stripes and Castore branding."
            }
            
            resubmission_response = self.session.post(f"{self.base_url}/jerseys?resubmission_id={jersey_id}", json=resubmission_payload)
            
            if resubmission_response.status_code != 200:
                self.log_test("Complete Moderation Workflow", "FAIL", "Resubmission failed")
                return False
            
            resubmitted_jersey = resubmission_response.json()
            resubmitted_id = resubmitted_jersey["id"]
            resubmitted_reference = resubmitted_jersey.get("reference_number")
            
            # Verify reference preserved
            if original_reference != resubmitted_reference:
                self.log_test("Complete Moderation Workflow", "FAIL", "Reference not preserved in resubmission")
                return False
            
            # Step 4: Admin approves resubmission
            self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
            
            approval_response = self.session.post(f"{self.base_url}/admin/jerseys/{resubmitted_id}/approve")
            
            if approval_response.status_code != 200:
                self.log_test("Complete Moderation Workflow", "FAIL", "Approval failed")
                return False
            
            # Step 5: Verify jersey is now public
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            
            public_jerseys_response = self.session.get(f"{self.base_url}/jerseys")
            
            if public_jerseys_response.status_code == 200:
                public_jerseys = public_jerseys_response.json()
                approved_jersey = None
                
                for jersey in public_jerseys:
                    if jersey.get("id") == resubmitted_id:
                        approved_jersey = jersey
                        break
                
                if approved_jersey:
                    self.log_test("Complete Moderation Workflow", "PASS", 
                                f"Complete workflow successful: {original_reference} preserved through resubmission and approval")
                    return True
                else:
                    self.log_test("Complete Moderation Workflow", "FAIL", "Approved jersey not found in public list")
                    return False
            else:
                self.log_test("Complete Moderation Workflow", "FAIL", "Could not get public jerseys")
                return False
                
        except Exception as e:
            self.log_test("Complete Moderation Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_notification_content_verification(self):
        """Test that notifications contain reference numbers in messages"""
        try:
            if not self.auth_token:
                self.log_test("Notification Content Verification", "FAIL", "No auth token")
                return False
            
            # Create a jersey to trigger notifications
            jersey_payload = {
                "team": "Brighton & Hove Albion",
                "season": "2023-24",
                "player": "Alexis Mac Allister",
                "size": "M",
                "condition": "mint",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Brighton home jersey with Mac Allister #10"
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if response.status_code == 200:
                jersey_data = response.json()
                reference_number = jersey_data.get("reference_number")
                
                time.sleep(1)  # Wait for notification
                
                # Get notifications
                notifications_response = self.session.get(f"{self.base_url}/notifications")
                
                if notifications_response.status_code == 200:
                    notifications_data = notifications_response.json()
                    notifications = notifications_data.get("notifications", [])
                    
                    # Find submission notification
                    submission_notification = None
                    for notification in notifications:
                        if "Jersey Submitted Successfully!" in notification.get("title", ""):
                            submission_notification = notification
                            break
                    
                    if submission_notification:
                        message = submission_notification.get("message", "")
                        
                        # Verify reference number is in message
                        if reference_number and reference_number in message:
                            # Verify message format
                            expected_elements = [
                                jersey_data.get("team", ""),
                                jersey_data.get("season", ""),
                                reference_number,
                                "submitted",
                                "reviewed"
                            ]
                            
                            message_complete = all(element.lower() in message.lower() for element in expected_elements if element)
                            
                            if message_complete:
                                self.log_test("Notification Content Verification", "PASS", 
                                            f"Notification contains reference {reference_number} and complete details")
                                return True
                            else:
                                self.log_test("Notification Content Verification", "FAIL", "Notification missing expected content")
                                return False
                        else:
                            self.log_test("Notification Content Verification", "FAIL", "Reference number not in notification message")
                            return False
                    else:
                        self.log_test("Notification Content Verification", "FAIL", "No submission notification found")
                        return False
                else:
                    self.log_test("Notification Content Verification", "FAIL", "Could not get notifications")
                    return False
            else:
                self.log_test("Notification Content Verification", "FAIL", "Jersey creation failed")
                return False
                
        except Exception as e:
            self.log_test("Notification Content Verification", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_database_integrity_with_references(self):
        """Test that all jersey operations work correctly with reference_number field"""
        try:
            if not self.auth_token:
                self.log_test("Database Integrity with References", "FAIL", "No auth token")
                return False
            
            # Create jersey
            jersey_payload = {
                "team": "Crystal Palace",
                "season": "2023-24",
                "player": "Wilfried Zaha",
                "size": "L",
                "condition": "very_good",
                "manufacturer": "Macron",
                "home_away": "home",
                "league": "Premier League",
                "description": "Crystal Palace home jersey with Zaha #11"
            }
            
            create_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if create_response.status_code != 200:
                self.log_test("Database Integrity with References", "FAIL", "Jersey creation failed")
                return False
            
            jersey_data = create_response.json()
            jersey_id = jersey_data["id"]
            reference_number = jersey_data.get("reference_number")
            
            # Test 1: Get specific jersey
            get_response = self.session.get(f"{self.base_url}/jerseys/{jersey_id}")
            
            if get_response.status_code == 200:
                retrieved_jersey = get_response.json()
                if retrieved_jersey.get("reference_number") != reference_number:
                    self.log_test("Database Integrity with References", "FAIL", "Reference number not preserved in GET")
                    return False
            else:
                self.log_test("Database Integrity with References", "FAIL", "Could not retrieve jersey")
                return False
            
            # Test 2: Add to collection
            collection_payload = {
                "jersey_id": jersey_id,
                "collection_type": "owned"
            }
            
            collection_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
            
            if collection_response.status_code != 200:
                self.log_test("Database Integrity with References", "FAIL", "Collection add failed")
                return False
            
            # Test 3: Get collection
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if owned_response.status_code == 200:
                owned_collection = owned_response.json()
                jersey_in_collection = None
                
                for item in owned_collection:
                    if item.get("jersey_id") == jersey_id:
                        jersey_in_collection = item
                        break
                
                if jersey_in_collection and "jersey" in jersey_in_collection:
                    collection_jersey = jersey_in_collection["jersey"]
                    if collection_jersey.get("reference_number") != reference_number:
                        self.log_test("Database Integrity with References", "FAIL", "Reference number not in collection jersey")
                        return False
                else:
                    self.log_test("Database Integrity with References", "FAIL", "Jersey not found in collection")
                    return False
            else:
                self.log_test("Database Integrity with References", "FAIL", "Could not get collection")
                return False
            
            # Test 4: Create listing
            listing_payload = {
                "jersey_id": jersey_id,
                "price": 89.99,
                "description": "Crystal Palace jersey from my collection",
                "images": []
            }
            
            listing_response = self.session.post(f"{self.base_url}/listings", json=listing_payload)
            
            if listing_response.status_code == 200:
                listing_data = listing_response.json()
                listing_id = listing_data["id"]
                
                # Test 5: Get listing with jersey details
                listing_detail_response = self.session.get(f"{self.base_url}/listings/{listing_id}")
                
                if listing_detail_response.status_code == 200:
                    listing_detail = listing_detail_response.json()
                    
                    if "jersey" in listing_detail:
                        listing_jersey = listing_detail["jersey"]
                        if listing_jersey.get("reference_number") == reference_number:
                            self.log_test("Database Integrity with References", "PASS", 
                                        f"All operations work correctly with reference {reference_number}")
                            return True
                        else:
                            self.log_test("Database Integrity with References", "FAIL", "Reference number not in listing jersey")
                            return False
                    else:
                        self.log_test("Database Integrity with References", "FAIL", "No jersey data in listing")
                        return False
                else:
                    self.log_test("Database Integrity with References", "FAIL", "Could not get listing details")
                    return False
            else:
                self.log_test("Database Integrity with References", "FAIL", "Listing creation failed")
                return False
                
        except Exception as e:
            self.log_test("Database Integrity with References", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all enhanced features tests"""
        print("🚀 Starting TopKit Enhanced Features Comprehensive Testing")
        print("Testing all specific requirements from the review request")
        print("=" * 80)
        
        tests = [
            self.setup_users,
            self.test_sequential_reference_generation,
            self.test_complete_moderation_workflow,
            self.test_notification_content_verification,
            self.test_database_integrity_with_references
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ {test.__name__}: FAIL - Exception: {str(e)}")
                failed += 1
        
        print("=" * 80)
        print(f"🏁 Testing Complete: {passed} PASSED, {failed} FAILED")
        
        if failed == 0:
            print("🎉 ALL ENHANCED FEATURES WORKING PERFECTLY!")
            print("✅ Jersey Reference System (TK-000001 format)")
            print("✅ Enhanced Notifications with Reference Numbers")
            print("✅ Reference Preservation in Resubmissions")
            print("✅ Complete Moderation Workflow")
            print("✅ Database Integrity with New Fields")
        else:
            print(f"⚠️  {failed} tests failed. Please review the issues above.")
        
        return failed == 0

if __name__ == "__main__":
    tester = TopKitEnhancedFeaturesTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)