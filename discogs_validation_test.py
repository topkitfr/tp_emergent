#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Discogs-Style Validation System Testing
Testing the recent backend corrections for the Discogs-like jersey submission workflow
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://football-kit-ui.preview.emergentagent.com/api"

# Test accounts as specified in review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"
NORMAL_USER_EMAIL = "test@example.com"
NORMAL_USER_PASSWORD = "password123"

class DiscogsValidationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.admin_user_id = None
        self.normal_token = None
        self.normal_user_id = None
        self.test_jersey_id = None
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
    
    def setup_admin_user(self):
        """Setup admin user account"""
        try:
            # Try to login first
            login_payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.admin_user_id = data["user"]["id"]
                self.log_test("Admin User Setup (Login)", "PASS", f"Admin logged in: {ADMIN_EMAIL}")
                return True
            else:
                # Try to register admin user
                register_payload = {
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "name": "TopKit Admin"
                }
                
                register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
                
                if register_response.status_code == 200:
                    data = register_response.json()
                    self.admin_token = data["token"]
                    self.admin_user_id = data["user"]["id"]
                    self.log_test("Admin User Setup (Register)", "PASS", f"Admin registered: {ADMIN_EMAIL}")
                    return True
                else:
                    self.log_test("Admin User Setup", "FAIL", f"Could not setup admin user: {register_response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test("Admin User Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    def setup_normal_user(self):
        """Setup normal user account"""
        try:
            # Use unique email to avoid conflicts
            unique_email = f"testuser_{int(time.time())}@example.com"
            
            register_payload = {
                "email": unique_email,
                "password": NORMAL_USER_PASSWORD,
                "name": "Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if response.status_code == 200:
                data = response.json()
                self.normal_token = data["token"]
                self.normal_user_id = data["user"]["id"]
                self.log_test("Normal User Setup", "PASS", f"Normal user registered: {unique_email}")
                return True
            else:
                self.log_test("Normal User Setup", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Normal User Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_1_jersey_submission_fixed_validation(self):
        """PRIORITY 1: Test jersey submission with fixed validation (no 422 errors)"""
        try:
            if not self.normal_token:
                self.log_test("P1 - Jersey Submission Fixed Validation", "FAIL", "No normal user token")
                return False
            
            # Set auth header for normal user
            headers = {'Authorization': f'Bearer {self.normal_token}'}
            
            # Test jersey submission with comprehensive data (should not get 422 errors)
            jersey_payload = {
                "team": "Real Madrid",
                "season": "23/24",
                "player": "Benzema",
                "size": "L",
                "condition": "very_good",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for validation testing",
                "images": []
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("status") == "pending":
                    self.test_jersey_id = data["id"]
                    self.log_test("P1 - Jersey Submission Fixed Validation", "PASS", 
                                f"Jersey created successfully with 'pending' status (ID: {self.test_jersey_id})")
                    return True
                else:
                    self.log_test("P1 - Jersey Submission Fixed Validation", "FAIL", 
                                f"Jersey created but missing ID or wrong status: {data}")
                    return False
            elif response.status_code == 422:
                self.log_test("P1 - Jersey Submission Fixed Validation", "FAIL", 
                            f"422 validation error still occurring: {response.text}")
                return False
            else:
                self.log_test("P1 - Jersey Submission Fixed Validation", "FAIL", 
                            f"Unexpected status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("P1 - Jersey Submission Fixed Validation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_1_pending_jerseys_not_visible_public(self):
        """PRIORITY 1: Verify pending jerseys are NOT visible in public GET /api/jerseys"""
        try:
            # Get public jerseys (no auth required)
            response = self.session.get(f"{self.base_url}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Check if our test jersey (pending status) is in the public list
                test_jersey_found = any(jersey.get("id") == self.test_jersey_id for jersey in jerseys)
                
                if not test_jersey_found:
                    self.log_test("P1 - Pending Jerseys Not Public", "PASS", 
                                f"Pending jersey correctly hidden from public view (found {len(jerseys)} public jerseys)")
                    return True
                else:
                    self.log_test("P1 - Pending Jerseys Not Public", "FAIL", 
                                "Pending jersey incorrectly visible in public endpoint")
                    return False
            else:
                self.log_test("P1 - Pending Jerseys Not Public", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("P1 - Pending Jerseys Not Public", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_2_admin_access_pending_jerseys(self):
        """PRIORITY 2: Test admin user access to GET /api/admin/jerseys/pending"""
        try:
            if not self.admin_token:
                self.log_test("P2 - Admin Access Pending Jerseys", "FAIL", "No admin token")
                return False
            
            # Set auth header for admin user
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = self.session.get(f"{self.base_url}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                
                # Check if our test jersey is in the pending list
                test_jersey_found = any(jersey.get("id") == self.test_jersey_id for jersey in pending_jerseys)
                
                if test_jersey_found:
                    self.log_test("P2 - Admin Access Pending Jerseys", "PASS", 
                                f"Admin successfully accessed pending jerseys (found {len(pending_jerseys)} pending)")
                    return True
                else:
                    self.log_test("P2 - Admin Access Pending Jerseys", "PASS", 
                                f"Admin accessed pending endpoint (found {len(pending_jerseys)} pending, test jersey may have been processed)")
                    return True
            else:
                self.log_test("P2 - Admin Access Pending Jerseys", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("P2 - Admin Access Pending Jerseys", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_2_non_admin_access_denied(self):
        """PRIORITY 2: Verify non-admin users get 403 when accessing admin endpoints"""
        try:
            if not self.normal_token:
                self.log_test("P2 - Non-Admin Access Denied", "FAIL", "No normal user token")
                return False
            
            # Set auth header for normal user
            headers = {'Authorization': f'Bearer {self.normal_token}'}
            
            response = self.session.get(f"{self.base_url}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 403:
                self.log_test("P2 - Non-Admin Access Denied", "PASS", 
                            "Non-admin user correctly denied access with 403")
                return True
            else:
                self.log_test("P2 - Non-Admin Access Denied", "FAIL", 
                            f"Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("P2 - Non-Admin Access Denied", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_2_jersey_approval(self):
        """PRIORITY 2: Test jersey approval via POST /api/admin/jerseys/{id}/approve"""
        try:
            if not self.admin_token or not self.test_jersey_id:
                self.log_test("P2 - Jersey Approval", "FAIL", "Missing admin token or jersey ID")
                return False
            
            # Set auth header for admin user
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            response = self.session.post(f"{self.base_url}/admin/jerseys/{self.test_jersey_id}/approve", 
                                       headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "approved" in data["message"].lower():
                    self.log_test("P2 - Jersey Approval", "PASS", 
                                f"Jersey approved successfully: {data['message']}")
                    return True
                else:
                    self.log_test("P2 - Jersey Approval", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("P2 - Jersey Approval", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("P2 - Jersey Approval", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_2_jersey_rejection(self):
        """PRIORITY 2: Test jersey rejection via POST /api/admin/jerseys/{id}/reject"""
        try:
            if not self.admin_token:
                self.log_test("P2 - Jersey Rejection", "FAIL", "No admin token")
                return False
            
            # Create another jersey for rejection testing
            headers_normal = {'Authorization': f'Bearer {self.normal_token}'}
            
            jersey_payload = {
                "team": "Manchester City",
                "season": "23/24", 
                "player": "Haaland",
                "size": "M",
                "condition": "good",
                "manufacturer": "Puma",
                "home_away": "away",
                "league": "Premier League",
                "description": "Test jersey for rejection testing",
                "images": []
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload, 
                                              headers=headers_normal)
            
            if jersey_response.status_code != 200:
                self.log_test("P2 - Jersey Rejection", "FAIL", "Could not create jersey for rejection test")
                return False
            
            reject_jersey_id = jersey_response.json()["id"]
            
            # Now test rejection
            headers_admin = {'Authorization': f'Bearer {self.admin_token}'}
            rejection_data = {"reason": "Duplicate entry - similar jersey already exists"}
            
            response = self.session.post(f"{self.base_url}/admin/jerseys/{reject_jersey_id}/reject", 
                                       json=rejection_data, headers=headers_admin)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "rejected" in data["message"].lower():
                    self.log_test("P2 - Jersey Rejection", "PASS", 
                                f"Jersey rejected successfully: {data['message']}")
                    return True
                else:
                    self.log_test("P2 - Jersey Rejection", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("P2 - Jersey Rejection", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("P2 - Jersey Rejection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_3_user_pending_submissions(self):
        """PRIORITY 3: Test GET /api/collections/pending for authenticated users"""
        try:
            if not self.normal_token:
                self.log_test("P3 - User Pending Submissions", "FAIL", "No normal user token")
                return False
            
            # Set auth header for normal user
            headers = {'Authorization': f'Bearer {self.normal_token}'}
            
            response = self.session.get(f"{self.base_url}/collections/pending", headers=headers)
            
            if response.status_code == 200:
                pending_submissions = response.json()
                
                # Check if response is a list and contains proper data structure
                if isinstance(pending_submissions, list):
                    self.log_test("P3 - User Pending Submissions", "PASS", 
                                f"User pending submissions retrieved successfully ({len(pending_submissions)} items)")
                    return True
                else:
                    self.log_test("P3 - User Pending Submissions", "FAIL", 
                                f"Unexpected response format: {type(pending_submissions)}")
                    return False
            else:
                self.log_test("P3 - User Pending Submissions", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("P3 - User Pending Submissions", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_3_pending_submissions_authentication_required(self):
        """PRIORITY 3: Verify proper authentication requirement for pending submissions"""
        try:
            # Test without authentication
            response = self.session.get(f"{self.base_url}/collections/pending")
            
            if response.status_code in [401, 403]:
                self.log_test("P3 - Pending Submissions Auth Required", "PASS", 
                            f"Unauthenticated request correctly rejected with {response.status_code}")
                return True
            else:
                self.log_test("P3 - Pending Submissions Auth Required", "FAIL", 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("P3 - Pending Submissions Auth Required", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_4_approved_jersey_public_visibility(self):
        """PRIORITY 4: Verify approved jerseys appear in GET /api/jerseys"""
        try:
            # Get public jerseys after approval
            response = self.session.get(f"{self.base_url}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Check if our approved test jersey is now visible
                test_jersey_found = any(jersey.get("id") == self.test_jersey_id for jersey in jerseys)
                
                if test_jersey_found:
                    self.log_test("P4 - Approved Jersey Public Visibility", "PASS", 
                                f"Approved jersey now visible in public endpoint ({len(jerseys)} total jerseys)")
                    return True
                else:
                    self.log_test("P4 - Approved Jersey Public Visibility", "FAIL", 
                                "Approved jersey not found in public endpoint")
                    return False
            else:
                self.log_test("P4 - Approved Jersey Public Visibility", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("P4 - Approved Jersey Public Visibility", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_4_rejected_jerseys_remain_hidden(self):
        """PRIORITY 4: Verify rejected jerseys remain hidden from public view"""
        try:
            # Create and reject a jersey to test
            if not self.normal_token or not self.admin_token:
                self.log_test("P4 - Rejected Jerseys Hidden", "FAIL", "Missing tokens")
                return False
            
            # Create jersey as normal user
            headers_normal = {'Authorization': f'Bearer {self.normal_token}'}
            
            jersey_payload = {
                "team": "Chelsea FC",
                "season": "23/24",
                "player": "Sterling",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Nike",
                "home_away": "third",
                "league": "Premier League",
                "description": "Test jersey for rejection visibility test",
                "images": []
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload, 
                                              headers=headers_normal)
            
            if jersey_response.status_code != 200:
                self.log_test("P4 - Rejected Jerseys Hidden", "FAIL", "Could not create test jersey")
                return False
            
            rejected_jersey_id = jersey_response.json()["id"]
            
            # Reject the jersey as admin
            headers_admin = {'Authorization': f'Bearer {self.admin_token}'}
            rejection_data = {"reason": "Poor quality images"}
            
            reject_response = self.session.post(f"{self.base_url}/admin/jerseys/{rejected_jersey_id}/reject", 
                                              json=rejection_data, headers=headers_admin)
            
            if reject_response.status_code != 200:
                self.log_test("P4 - Rejected Jerseys Hidden", "FAIL", "Could not reject jersey")
                return False
            
            # Check public visibility
            public_response = self.session.get(f"{self.base_url}/jerseys")
            
            if public_response.status_code == 200:
                jerseys = public_response.json()
                rejected_jersey_found = any(jersey.get("id") == rejected_jersey_id for jersey in jerseys)
                
                if not rejected_jersey_found:
                    self.log_test("P4 - Rejected Jerseys Hidden", "PASS", 
                                "Rejected jersey correctly hidden from public view")
                    return True
                else:
                    self.log_test("P4 - Rejected Jerseys Hidden", "FAIL", 
                                "Rejected jersey incorrectly visible in public endpoint")
                    return False
            else:
                self.log_test("P4 - Rejected Jerseys Hidden", "FAIL", f"Status: {public_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("P4 - Rejected Jerseys Hidden", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_priority_4_end_to_end_workflow(self):
        """PRIORITY 4: Test complete end-to-end workflow: User submission → Admin approval → Public visibility"""
        try:
            if not self.normal_token or not self.admin_token:
                self.log_test("P4 - End-to-End Workflow", "FAIL", "Missing tokens")
                return False
            
            # Step 1: User submits jersey
            headers_normal = {'Authorization': f'Bearer {self.normal_token}'}
            
            jersey_payload = {
                "team": "Arsenal FC",
                "season": "23/24",
                "player": "Saka",
                "size": "M",
                "condition": "mint",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "End-to-end workflow test jersey",
                "images": []
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload, 
                                              headers=headers_normal)
            
            if jersey_response.status_code != 200:
                self.log_test("P4 - End-to-End Workflow", "FAIL", "Step 1: Jersey submission failed")
                return False
            
            workflow_jersey_id = jersey_response.json()["id"]
            
            # Step 2: Verify jersey is pending and not public
            public_check_1 = self.session.get(f"{self.base_url}/jerseys")
            if public_check_1.status_code == 200:
                jerseys_before = public_check_1.json()
                jersey_public_before = any(j.get("id") == workflow_jersey_id for j in jerseys_before)
                
                if jersey_public_before:
                    self.log_test("P4 - End-to-End Workflow", "FAIL", "Step 2: Jersey incorrectly public before approval")
                    return False
            
            # Step 3: Admin approves jersey
            headers_admin = {'Authorization': f'Bearer {self.admin_token}'}
            
            approve_response = self.session.post(f"{self.base_url}/admin/jerseys/{workflow_jersey_id}/approve", 
                                               headers=headers_admin)
            
            if approve_response.status_code != 200:
                self.log_test("P4 - End-to-End Workflow", "FAIL", "Step 3: Jersey approval failed")
                return False
            
            # Step 4: Verify jersey is now public
            public_check_2 = self.session.get(f"{self.base_url}/jerseys")
            if public_check_2.status_code == 200:
                jerseys_after = public_check_2.json()
                jersey_public_after = any(j.get("id") == workflow_jersey_id for j in jerseys_after)
                
                if jersey_public_after:
                    self.log_test("P4 - End-to-End Workflow", "PASS", 
                                "Complete workflow successful: Submission → Approval → Public visibility")
                    return True
                else:
                    self.log_test("P4 - End-to-End Workflow", "FAIL", "Step 4: Approved jersey not public")
                    return False
            else:
                self.log_test("P4 - End-to-End Workflow", "FAIL", "Step 4: Could not check public visibility")
                return False
                
        except Exception as e:
            self.log_test("P4 - End-to-End Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Discogs validation system tests"""
        print("🎯 TOPKIT DISCOGS-STYLE VALIDATION SYSTEM TESTING")
        print("=" * 60)
        print()
        
        # Setup phase
        print("📋 SETUP PHASE")
        print("-" * 30)
        
        if not self.setup_admin_user():
            print("❌ Cannot proceed without admin user")
            return False
        
        if not self.setup_normal_user():
            print("❌ Cannot proceed without normal user")
            return False
        
        print()
        
        # Priority 1 Tests
        print("🔥 PRIORITY 1 - Jersey Submission with Fixed Validation")
        print("-" * 50)
        
        p1_results = []
        p1_results.append(self.test_priority_1_jersey_submission_fixed_validation())
        p1_results.append(self.test_priority_1_pending_jerseys_not_visible_public())
        
        print()
        
        # Priority 2 Tests
        print("🔥 PRIORITY 2 - Admin Panel Backend Endpoints")
        print("-" * 45)
        
        p2_results = []
        p2_results.append(self.test_priority_2_admin_access_pending_jerseys())
        p2_results.append(self.test_priority_2_non_admin_access_denied())
        p2_results.append(self.test_priority_2_jersey_approval())
        p2_results.append(self.test_priority_2_jersey_rejection())
        
        print()
        
        # Priority 3 Tests
        print("🔥 PRIORITY 3 - User Pending Submissions Endpoint")
        print("-" * 48)
        
        p3_results = []
        p3_results.append(self.test_priority_3_user_pending_submissions())
        p3_results.append(self.test_priority_3_pending_submissions_authentication_required())
        
        print()
        
        # Priority 4 Tests
        print("🔥 PRIORITY 4 - Complete Workflow Integration")
        print("-" * 45)
        
        p4_results = []
        p4_results.append(self.test_priority_4_approved_jersey_public_visibility())
        p4_results.append(self.test_priority_4_rejected_jerseys_remain_hidden())
        p4_results.append(self.test_priority_4_end_to_end_workflow())
        
        print()
        
        # Summary
        print("📊 TEST SUMMARY")
        print("-" * 20)
        
        all_results = p1_results + p2_results + p3_results + p4_results
        passed = sum(1 for result in all_results if result)
        total = len(all_results)
        
        print(f"✅ PRIORITY 1: {sum(p1_results)}/{len(p1_results)} tests passed")
        print(f"✅ PRIORITY 2: {sum(p2_results)}/{len(p2_results)} tests passed")
        print(f"✅ PRIORITY 3: {sum(p3_results)}/{len(p3_results)} tests passed")
        print(f"✅ PRIORITY 4: {sum(p4_results)}/{len(p4_results)} tests passed")
        print()
        print(f"🎯 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Discogs validation system is fully functional!")
        else:
            print(f"⚠️  {total-passed} tests failed - Issues need attention")
        
        return passed == total

if __name__ == "__main__":
    tester = DiscogsValidationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)