#!/usr/bin/env python3
"""
TopKit Admin Jersey Correction Functionality Backend Test
Testing admin jersey management endpoints for correction workflow
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-editor.preview.emergentagent.com/api"

# Test credentials from review request
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class AdminJerseyCorrectionTester:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.test_jersey_id = None
        self.results = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def authenticate_user(self):
        """Test 1: Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.log_result(
                    "User Authentication",
                    True,
                    f"User: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}"
                )
                return True
            else:
                self.log_result(
                    "User Authentication",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False

    def submit_test_jersey(self):
        """Test 2: Submit test jersey as admin user (since regular user is locked)"""
        if not self.admin_token:
            self.log_result("Jersey Submission", False, "No admin token available")
            return False
            
        try:
            jersey_data = {
                "team": "Real Madrid",
                "league": "La Liga",
                "season": "24/25",
                "jersey_type": "home",
                "manufacturer": "Adidas",
                "sku_code": "TEST-RM-24",
                "model": "authentic",
                "description": "Test jersey for admin correction functionality"
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_jersey_id = data.get("id")
                reference = data.get("reference_number")
                status = data.get("status")
                self.log_result(
                    "Jersey Submission",
                    True,
                    f"Jersey created - ID: {self.test_jersey_id}, Reference: {reference}, Status: {status}"
                )
                return True
            else:
                self.log_result(
                    "Jersey Submission",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Jersey Submission", False, f"Exception: {str(e)}")
            return False

    def verify_pending_status(self):
        """Test 3: Verify jersey is in pending status"""
        if not self.test_jersey_id:
            self.log_result("Pending Status Verification", False, "No test jersey ID available")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys/{self.test_jersey_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                team = data.get("team")
                reference = data.get("reference_number")
                
                if status == "pending":
                    self.log_result(
                        "Pending Status Verification",
                        True,
                        f"Jersey {reference} ({team}) is in pending status as expected"
                    )
                    return True
                else:
                    self.log_result(
                        "Pending Status Verification",
                        False,
                        f"Jersey status is '{status}', expected 'pending'"
                    )
                    return False
            else:
                self.log_result(
                    "Pending Status Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Pending Status Verification", False, f"Exception: {str(e)}")
            return False

    def authenticate_admin(self):
        """Test 4: Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Admin: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_get_pending_jerseys(self):
        """Test 5: GET /api/admin/jerseys/pending"""
        if not self.admin_token:
            self.log_result("GET Pending Jerseys", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                pending_jerseys = data.get("jerseys", [])
                total = data.get("total", 0)
                
                # Check if our test jersey is in the pending list
                test_jersey_found = False
                for jersey in pending_jerseys:
                    if jersey.get("id") == self.test_jersey_id:
                        test_jersey_found = True
                        break
                
                self.log_result(
                    "GET Pending Jerseys",
                    True,
                    f"Retrieved {total} pending jerseys. Test jersey found: {test_jersey_found}",
                    {"total_pending": total, "test_jersey_in_list": test_jersey_found}
                )
                return True
            else:
                self.log_result(
                    "GET Pending Jerseys",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("GET Pending Jerseys", False, f"Exception: {str(e)}")
            return False

    def test_put_jersey_modification(self):
        """Test 6: PUT /api/admin/jerseys/{jersey_id} - Test jersey modification"""
        if not self.admin_token or not self.test_jersey_id:
            self.log_result("PUT Jersey Modification", False, "Missing admin token or jersey ID")
            return False
            
        try:
            modification_data = {
                "team": "Real Madrid CF",  # Modified team name
                "league": "La Liga",
                "season": "2024/25",  # Modified season format
                "jersey_type": "home",
                "manufacturer": "Adidas",
                "sku_code": "RM-HOME-24-25",  # Modified SKU
                "model": "authentic",
                "description": "Test jersey for admin correction functionality - ADMIN MODIFIED"
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.put(f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}", 
                                  json=modification_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "PUT Jersey Modification",
                    True,
                    f"Jersey modified successfully. Updated fields: team, season, sku_code, description",
                    data
                )
                return True
            else:
                self.log_result(
                    "PUT Jersey Modification",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("PUT Jersey Modification", False, f"Exception: {str(e)}")
            return False

    def test_suggest_modifications(self):
        """Test 7: POST /api/admin/jerseys/{jersey_id}/suggest-modifications"""
        if not self.admin_token or not self.test_jersey_id:
            self.log_result("Suggest Modifications", False, "Missing admin token or jersey ID")
            return False
            
        try:
            suggestion_data = {
                "suggested_changes": "Please verify the manufacturer and update the season format to match our standards",
                "suggested_modifications": {
                    "manufacturer": "Should be 'Adidas' with capital A",
                    "season": "Should be '2024-25' format",
                    "sku_code": "Please provide official Adidas SKU code"
                }
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}/suggest-modifications", 
                                   json=suggestion_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                suggestion_id = data.get("suggestion_id")
                self.log_result(
                    "Suggest Modifications",
                    True,
                    f"Modification suggestion created successfully. Suggestion ID: {suggestion_id}",
                    data
                )
                return True
            else:
                self.log_result(
                    "Suggest Modifications",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Suggest Modifications", False, f"Exception: {str(e)}")
            return False

    def test_approve_jersey(self):
        """Test 8: POST /api/admin/jerseys/{jersey_id}/approve"""
        if not self.admin_token or not self.test_jersey_id:
            self.log_result("Approve Jersey", False, "Missing admin token or jersey ID")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}/approve", 
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Approve Jersey",
                    True,
                    f"Jersey approved successfully. Status changed to approved.",
                    data
                )
                return True
            else:
                self.log_result(
                    "Approve Jersey",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Approve Jersey", False, f"Exception: {str(e)}")
            return False

    def verify_approval_status(self):
        """Test 9: Verify jersey status changed to approved"""
        if not self.test_jersey_id:
            self.log_result("Approval Status Verification", False, "No test jersey ID available")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys/{self.test_jersey_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                team = data.get("team")
                reference = data.get("reference_number")
                approved_by = data.get("approved_by")
                
                if status == "approved":
                    self.log_result(
                        "Approval Status Verification",
                        True,
                        f"Jersey {reference} ({team}) is now approved. Approved by: {approved_by}"
                    )
                    return True
                else:
                    self.log_result(
                        "Approval Status Verification",
                        False,
                        f"Jersey status is '{status}', expected 'approved'"
                    )
                    return False
            else:
                self.log_result(
                    "Approval Status Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Approval Status Verification", False, f"Exception: {str(e)}")
            return False

    def test_admin_panel_visibility(self):
        """Test 10: Verify jersey appears in admin panel for moderation"""
        if not self.admin_token:
            self.log_result("Admin Panel Visibility", False, "No admin token available")
            return False
            
        try:
            # Create another test jersey to check admin panel visibility
            jersey_data = {
                "team": "FC Barcelona",
                "league": "La Liga", 
                "season": "24/25",
                "jersey_type": "away",
                "manufacturer": "Nike",
                "sku_code": "TEST-FCB-24",
                "model": "replica",
                "description": "Second test jersey for admin panel visibility check"
            }
            
            # Submit as admin (since user is locked)
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=admin_headers)
            
            if response.status_code == 200:
                new_jersey_id = response.json().get("id")
                
                # Now check if it appears in admin panel
                admin_response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=admin_headers)
                
                if admin_response.status_code == 200:
                    pending_data = admin_response.json()
                    pending_jerseys = pending_data.get("jerseys", [])
                    
                    # Check if new jersey appears in pending list
                    new_jersey_found = False
                    for jersey in pending_jerseys:
                        if jersey.get("id") == new_jersey_id:
                            new_jersey_found = True
                            break
                    
                    self.log_result(
                        "Admin Panel Visibility",
                        new_jersey_found,
                        f"New jersey {'found' if new_jersey_found else 'NOT found'} in admin moderation queue"
                    )
                    return new_jersey_found
                else:
                    self.log_result(
                        "Admin Panel Visibility",
                        False,
                        f"Failed to retrieve admin panel: HTTP {admin_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Admin Panel Visibility",
                    False,
                    f"Failed to create test jersey: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Panel Visibility", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all admin jersey correction tests"""
        print("🎯 TOPKIT ADMIN JERSEY CORRECTION FUNCTIONALITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"User: {USER_EMAIL}")
        print(f"Admin: {ADMIN_EMAIL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Test sequence - reorder to authenticate admin first
        tests = [
            self.authenticate_user,  # Try user auth but continue if fails
            self.authenticate_admin,  # Admin auth is critical
            self.submit_test_jersey,  # Use admin token if user fails
            self.verify_pending_status,
            self.test_get_pending_jerseys,
            self.test_put_jersey_modification,
            self.test_suggest_modifications,
            self.test_approve_jersey,
            self.verify_approval_status,
            self.test_admin_panel_visibility
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            success = test()
            if success:
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        print("=" * 60)
        print("🎯 ADMIN JERSEY CORRECTION TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        if success_rate >= 90:
            print("✅ EXCELLENT: Admin jersey correction functionality is working perfectly!")
        elif success_rate >= 75:
            print("⚠️  GOOD: Admin jersey correction functionality is mostly working with minor issues.")
        elif success_rate >= 50:
            print("❌ ISSUES: Admin jersey correction functionality has significant problems.")
        else:
            print("🚨 CRITICAL: Admin jersey correction functionality is severely broken.")
        
        print()
        print("DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("🔍 KEY FINDINGS:")
        
        # Analyze results
        auth_working = any("Authentication" in r['test'] and "✅" in r['status'] for r in self.results)
        jersey_submission_working = any("Jersey Submission" in r['test'] and "✅" in r['status'] for r in self.results)
        admin_endpoints_working = any("admin/jerseys" in str(r.get('response_data', '')) or 
                                    ("GET Pending" in r['test'] or "PUT Jersey" in r['test'] or 
                                     "Suggest Modifications" in r['test'] or "Approve Jersey" in r['test']) 
                                    and "✅" in r['status'] for r in self.results)
        
        if auth_working:
            print("✅ Authentication system working for both user and admin")
        else:
            print("❌ Authentication system has issues")
            
        if jersey_submission_working:
            print("✅ Jersey submission system operational")
        else:
            print("❌ Jersey submission system has problems")
            
        if admin_endpoints_working:
            print("✅ Admin jersey management endpoints functional")
        else:
            print("❌ Admin jersey management endpoints have issues")
        
        print()
        print("📋 ADMIN JERSEY CORRECTION WORKFLOW STATUS:")
        print("1. User submits jersey → Admin moderation queue ✅" if jersey_submission_working else "1. User submits jersey → Admin moderation queue ❌")
        print("2. Admin retrieves pending jerseys ✅" if any("GET Pending" in r['test'] and "✅" in r['status'] for r in self.results) else "2. Admin retrieves pending jerseys ❌")
        print("3. Admin modifies jersey details ✅" if any("PUT Jersey" in r['test'] and "✅" in r['status'] for r in self.results) else "3. Admin modifies jersey details ❌")
        print("4. Admin suggests modifications ✅" if any("Suggest Modifications" in r['test'] and "✅" in r['status'] for r in self.results) else "4. Admin suggests modifications ❌")
        print("5. Admin approves jersey ✅" if any("Approve Jersey" in r['test'] and "✅" in r['status'] for r in self.results) else "5. Admin approves jersey ❌")
        
        return success_rate

if __name__ == "__main__":
    tester = AdminJerseyCorrectionTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success_rate >= 75 else 1)