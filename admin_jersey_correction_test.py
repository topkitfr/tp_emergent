#!/usr/bin/env python3
"""
TopKit Admin Jersey Correction Endpoint Testing
Testing the fixed admin jersey correction bug functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class AdminJerseyCorrectionEndpointTester:
    def __init__(self):
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

    def authenticate_admin(self):
        """Test 1: Admin Authentication (topkitfr@gmail.com / TopKitSecure789#)"""
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

    def get_or_create_pending_jersey(self):
        """Test 2: Retrieve Pending Jersey for editing (or create one if needed)"""
        if not self.admin_token:
            self.log_result("Get/Create Pending Jersey", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First, try to get existing pending jerseys
            response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different possible response structures
                if isinstance(data, list):
                    pending_jerseys = data
                elif isinstance(data, dict):
                    pending_jerseys = data.get("jerseys", data.get("pending_jerseys", []))
                else:
                    pending_jerseys = []
                
                # Use existing pending jersey if available
                if pending_jerseys and len(pending_jerseys) > 0:
                    self.test_jersey_id = pending_jerseys[0].get("id")
                    jersey_info = pending_jerseys[0]
                    self.log_result(
                        "Get/Create Pending Jersey",
                        True,
                        f"Found existing pending jersey - ID: {self.test_jersey_id}, Team: {jersey_info.get('team')}, Reference: {jersey_info.get('reference_number')}"
                    )
                    return True
                else:
                    # Create a new test jersey if none exist
                    return self.create_test_jersey()
            else:
                self.log_result(
                    "Get/Create Pending Jersey",
                    False,
                    f"Failed to retrieve pending jerseys: HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Get/Create Pending Jersey", False, f"Exception: {str(e)}")
            return False

    def create_test_jersey(self):
        """Create a test jersey for correction testing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Use form data as the endpoint expects Form parameters
            form_data = {
                "team": "FC Barcelona",
                "league": "La Liga",
                "season": "23/24",
                "manufacturer": "Adidas",
                "jersey_type": "home",
                "sku_code": "ORIGINAL-BCN-23",
                "model": "replica",
                "description": "Original test jersey for admin correction validation"
            }
            
            response = requests.post(f"{BACKEND_URL}/jerseys", data=form_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.test_jersey_id = data.get("id")
                reference = data.get("reference_number")
                status = data.get("status")
                self.log_result(
                    "Create Test Jersey",
                    True,
                    f"Test jersey created - ID: {self.test_jersey_id}, Reference: {reference}, Status: {status}"
                )
                return True
            else:
                self.log_result(
                    "Create Test Jersey",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Create Test Jersey", False, f"Exception: {str(e)}")
            return False

    def test_jersey_edit_endpoint(self):
        """Test 3: Test Jersey Edit Endpoint - PUT /api/admin/jerseys/{jersey_id}/edit"""
        if not self.admin_token or not self.test_jersey_id:
            self.log_result("Jersey Edit Endpoint", False, "Missing admin token or jersey ID")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test data from review request with corrected data structure
            correction_data = {
                "team": "FC Barcelona",  # Modified from original
                "league": "La Liga",
                "season": "24/25",  # Modified season
                "manufacturer": "Nike",  # Modified from Adidas
                "jersey_type": "away",  # Modified from home
                "sku_code": "UPDATED-BCN-24",  # Modified SKU
                "model": "authentic",  # Modified from replica
                "description": "Updated test jersey for admin correction validation"  # Modified description
            }
            
            # Use the corrected URL from the review request
            response = requests.put(f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}/edit", 
                                  json=correction_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Jersey Edit Endpoint",
                    True,
                    f"Jersey updated successfully with corrected endpoint URL. Response: {data.get('message', 'Success')}",
                    data
                )
                return True
            else:
                self.log_result(
                    "Jersey Edit Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Jersey Edit Endpoint", False, f"Exception: {str(e)}")
            return False

    def validate_jersey_update(self):
        """Test 4: Validate Jersey Update - Verify modifications are saved correctly"""
        if not self.test_jersey_id:
            self.log_result("Validate Jersey Update", False, "No test jersey ID available")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys/{self.test_jersey_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if the modifications from the edit were saved
                expected_values = {
                    "team": "FC Barcelona",
                    "season": "24/25",
                    "manufacturer": "Nike",
                    "jersey_type": "away",
                    "sku_code": "UPDATED-BCN-24",
                    "model": "authentic"
                }
                
                validation_results = []
                all_correct = True
                
                for field, expected_value in expected_values.items():
                    actual_value = data.get(field)
                    is_correct = actual_value == expected_value
                    validation_results.append(f"{field}: {actual_value} {'✅' if is_correct else '❌ (expected: ' + expected_value + ')'}")
                    if not is_correct:
                        all_correct = False
                
                self.log_result(
                    "Validate Jersey Update",
                    all_correct,
                    f"Jersey validation results:\n   " + "\n   ".join(validation_results),
                    {"jersey_data": data, "validation_passed": all_correct}
                )
                return all_correct
            else:
                self.log_result(
                    "Validate Jersey Update",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Validate Jersey Update", False, f"Exception: {str(e)}")
            return False

    def check_notification_creation(self):
        """Test 5: Check Notification Creation - Confirm user receives notification about jersey update"""
        if not self.admin_token:
            self.log_result("Check Notification Creation", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get notifications to check if jersey update notification was created
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data if isinstance(data, list) else data.get("notifications", [])
                
                # Look for recent notifications related to jersey updates
                jersey_notifications = []
                for notification in notifications:
                    if (notification.get("related_id") == self.test_jersey_id or 
                        "jersey" in notification.get("message", "").lower() or
                        "maillot" in notification.get("message", "").lower()):
                        jersey_notifications.append(notification)
                
                if jersey_notifications:
                    latest_notification = jersey_notifications[0]  # Most recent
                    self.log_result(
                        "Check Notification Creation",
                        True,
                        f"Found {len(jersey_notifications)} jersey-related notifications. Latest: '{latest_notification.get('title')}' - '{latest_notification.get('message')}'",
                        {"notification_count": len(jersey_notifications), "latest": latest_notification}
                    )
                    return True
                else:
                    self.log_result(
                        "Check Notification Creation",
                        False,
                        f"No jersey-related notifications found. Total notifications: {len(notifications)}",
                        {"total_notifications": len(notifications)}
                    )
                    return False
            else:
                self.log_result(
                    "Check Notification Creation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Check Notification Creation", False, f"Exception: {str(e)}")
            return False

    def verify_workflow_status(self):
        """Test 6: Verify Workflow - Ensure jersey status remains 'pending' after edit for re-review"""
        if not self.test_jersey_id:
            self.log_result("Verify Workflow Status", False, "No test jersey ID available")
            return False
            
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys/{self.test_jersey_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                team = data.get("team")
                reference = data.get("reference_number")
                
                # After admin edit, jersey should remain pending for re-review
                if status == "pending":
                    self.log_result(
                        "Verify Workflow Status",
                        True,
                        f"Jersey {reference} ({team}) correctly remains in 'pending' status after admin edit for re-review"
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Workflow Status",
                        False,
                        f"Jersey status is '{status}', expected 'pending' after admin edit"
                    )
                    return False
            else:
                self.log_result(
                    "Verify Workflow Status",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Verify Workflow Status", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all admin jersey correction endpoint tests"""
        print("🎯 TOPKIT ADMIN JERSEY CORRECTION ENDPOINT TESTING")
        print("=" * 65)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin: {ADMIN_EMAIL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        print("TESTING OBJECTIVES:")
        print("1. Admin Authentication")
        print("2. Retrieve Pending Jersey for editing")
        print("3. Test Jersey Edit Endpoint: PUT /api/admin/jerseys/{jersey_id}/edit")
        print("4. Validate Jersey Update with new structure")
        print("5. Check Notification Creation")
        print("6. Verify Workflow Status")
        print()
        
        # Test sequence as per review request
        tests = [
            self.authenticate_admin,
            self.get_or_create_pending_jersey,
            self.test_jersey_edit_endpoint,
            self.validate_jersey_update,
            self.check_notification_creation,
            self.verify_workflow_status
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            success = test()
            if success:
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        print("=" * 65)
        print("🎯 ADMIN JERSEY CORRECTION ENDPOINT TESTING SUMMARY")
        print("=" * 65)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        if success_rate >= 90:
            print("✅ EXCELLENT: Admin jersey correction endpoint is working perfectly!")
        elif success_rate >= 75:
            print("⚠️  GOOD: Admin jersey correction endpoint is mostly working with minor issues.")
        elif success_rate >= 50:
            print("❌ ISSUES: Admin jersey correction endpoint has significant problems.")
        else:
            print("🚨 CRITICAL: Admin jersey correction endpoint is severely broken.")
        
        print()
        print("DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print()
        print("🔍 KEY FINDINGS:")
        
        # Analyze specific results
        auth_working = any("Admin Authentication" in r['test'] and "✅" in r['status'] for r in self.results)
        endpoint_working = any("Jersey Edit Endpoint" in r['test'] and "✅" in r['status'] for r in self.results)
        validation_working = any("Validate Jersey Update" in r['test'] and "✅" in r['status'] for r in self.results)
        notification_working = any("Check Notification Creation" in r['test'] and "✅" in r['status'] for r in self.results)
        workflow_working = any("Verify Workflow Status" in r['test'] and "✅" in r['status'] for r in self.results)
        
        if auth_working:
            print("✅ Admin authentication working perfectly")
        else:
            print("❌ Admin authentication has issues")
            
        if endpoint_working:
            print("✅ PUT /api/admin/jerseys/{jersey_id}/edit endpoint operational")
        else:
            print("❌ Jersey edit endpoint has problems")
            
        if validation_working:
            print("✅ Jersey update validation successful - modifications saved correctly")
        else:
            print("❌ Jersey update validation failed - modifications not saved properly")
            
        if notification_working:
            print("✅ Notification creation system working")
        else:
            print("❌ Notification creation system has issues")
            
        if workflow_working:
            print("✅ Workflow status management correct")
        else:
            print("❌ Workflow status management has problems")
        
        print()
        print("📋 ADMIN JERSEY CORRECTION WORKFLOW VERIFICATION:")
        print("1. Admin Authentication ✅" if auth_working else "1. Admin Authentication ❌")
        print("2. Retrieve Pending Jersey ✅" if any("Get/Create Pending Jersey" in r['test'] and "✅" in r['status'] for r in self.results) else "2. Retrieve Pending Jersey ❌")
        print("3. Jersey Edit Endpoint ✅" if endpoint_working else "3. Jersey Edit Endpoint ❌")
        print("4. Jersey Update Validation ✅" if validation_working else "4. Jersey Update Validation ❌")
        print("5. Notification Creation ✅" if notification_working else "5. Notification Creation ❌")
        print("6. Workflow Status ✅" if workflow_working else "6. Workflow Status ❌")
        
        print()
        print("🎯 REVIEW REQUEST VERIFICATION:")
        if endpoint_working and validation_working:
            print("✅ FIXED: Admin jersey correction bug resolved - endpoint URL corrected and data structure working")
        else:
            print("❌ ISSUE: Admin jersey correction bug still present")
            
        if not any("Erreur: Not Found" in str(r.get('response_data', '')) for r in self.results):
            print("✅ CONFIRMED: No 'Erreur: Not Found' errors detected")
        else:
            print("❌ ISSUE: 'Erreur: Not Found' errors still occurring")
        
        return success_rate

if __name__ == "__main__":
    tester = AdminJerseyCorrectionEndpointTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success_rate >= 75 else 1)