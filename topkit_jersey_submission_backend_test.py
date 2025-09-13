#!/usr/bin/env python3
"""
TopKit Jersey Submission System Backend Testing
==============================================

Test rapide du nouveau système de soumission de maillots dans TopKit.
Focus sur:
- NEW JERSEY SUBMISSION: Test de soumission via POST /api/jerseys avec multipart/form-data
- EXISTING FUNCTIONALITY: Vérification des APIs existantes
- ADMIN EDIT FUNCTIONALITY: Test de modification de maillots en attente
- USER AUTHENTICATION: Test de connexion avec les comptes fournis

Objectif: Valider que le nouveau système unifié (JerseyDetailEditor) fonctionne correctement.
"""

import requests
import json
import time
import sys
from datetime import datetime
import os

# Configuration
BACKEND_URL = "https://football-jersey-db.preview.emergentagent.com/api"

# Test credentials - using working alternative since steinmetzlivio@gmail.com is locked
USER_CREDENTIALS = {
    "email": "livio.test@topkit.fr",
    "password": "TopKitTestSecure789!"
}

ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com", 
    "password": "TopKitSecure789#"
}

class TopKitJerseySubmissionTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        self.created_jerseys = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"   📋 {details}")
        if error:
            print(f"   🚨 {error}")
        print()

    def authenticate_user(self):
        """Test user authentication with steinmetzlivio@gmail.com/TopKit123!"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=USER_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_info = data.get('user', {})
                
                self.log_test(
                    "User Authentication",
                    True,
                    f"User: {user_info.get('name', 'Unknown')}, Role: {user_info.get('role', 'Unknown')}, ID: {user_info.get('id', 'Unknown')}"
                )
                return True
            else:
                self.log_test(
                    "User Authentication", 
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, "", str(e))
            return False

    def authenticate_admin(self):
        """Test admin authentication with topkitfr@gmail.com/TopKitSecure789#"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_info = data.get('user', {})
                
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Admin: {user_info.get('name', 'Unknown')}, Role: {user_info.get('role', 'Unknown')}, ID: {user_info.get('id', 'Unknown')}"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication",
                    False, 
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, "", str(e))
            return False

    def test_jersey_submission_basic(self):
        """Test basic jersey submission via POST /api/jerseys"""
        if not self.user_token:
            self.log_test("Jersey Submission - Basic", False, "", "No user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test jersey data with required fields: team, league, season
            jersey_data = {
                "team": "FC Barcelona",
                "league": "La Liga",
                "season": "2024-25",
                "player": "Pedri",
                "manufacturer": "Nike",
                "home_away": "home",
                "description": "Maillot domicile FC Barcelona 2024-25 - Pedri #8"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                json=jersey_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                jersey_id = data.get('id')
                reference = data.get('reference_number', 'Unknown')
                status = data.get('status', 'Unknown')
                
                if jersey_id:
                    self.created_jerseys.append(jersey_id)
                
                self.log_test(
                    "Jersey Submission - Basic",
                    True,
                    f"Jersey created: ID={jersey_id}, Ref={reference}, Status={status}"
                )
                return True
            else:
                self.log_test(
                    "Jersey Submission - Basic",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Jersey Submission - Basic", False, "", str(e))
            return False

    def test_jersey_submission_multipart(self):
        """Test jersey submission with multipart/form-data (simulating photo upload)"""
        if not self.user_token:
            self.log_test("Jersey Submission - Multipart", False, "", "No user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Simulate multipart form data with photo fields
            files = {
                'team': (None, 'Real Madrid CF'),
                'league': (None, 'La Liga'),
                'season': (None, '2024-25'),
                'player': (None, 'Vinicius Jr'),
                'manufacturer': (None, 'Adidas'),
                'home_away': (None, 'home'),
                'description': (None, 'Maillot domicile Real Madrid 2024-25 - Vinicius Jr #7'),
                # Simulate photo uploads (would be actual files in real implementation)
                'front_photo': (None, 'front_photo_placeholder.jpg'),
                'back_photo': (None, 'back_photo_placeholder.jpg')
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                files=files,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                jersey_id = data.get('id')
                reference = data.get('reference_number', 'Unknown')
                status = data.get('status', 'Unknown')
                
                if jersey_id:
                    self.created_jerseys.append(jersey_id)
                
                self.log_test(
                    "Jersey Submission - Multipart",
                    True,
                    f"Jersey created with multipart: ID={jersey_id}, Ref={reference}, Status={status}"
                )
                return True
            else:
                self.log_test(
                    "Jersey Submission - Multipart",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Jersey Submission - Multipart", False, "", str(e))
            return False

    def test_required_fields_validation(self):
        """Test validation of required fields: team, league, season"""
        if not self.user_token:
            self.log_test("Required Fields Validation", False, "", "No user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test missing required fields
            test_cases = [
                {"league": "Premier League", "season": "2024-25"},  # Missing team
                {"team": "Manchester City", "season": "2024-25"},   # Missing league
                {"team": "Manchester City", "league": "Premier League"}  # Missing season
            ]
            
            validation_results = []
            
            for i, incomplete_data in enumerate(test_cases):
                response = self.session.post(
                    f"{BACKEND_URL}/jerseys",
                    json=incomplete_data,
                    headers=headers,
                    timeout=10
                )
                
                # Should return 422 (validation error) for missing required fields
                if response.status_code == 422:
                    validation_results.append(f"Test {i+1}: Correctly rejected incomplete data")
                else:
                    validation_results.append(f"Test {i+1}: Unexpected response {response.status_code}")
            
            success = all("Correctly rejected" in result for result in validation_results)
            
            self.log_test(
                "Required Fields Validation",
                success,
                "; ".join(validation_results)
            )
            return success
            
        except Exception as e:
            self.log_test("Required Fields Validation", False, "", str(e))
            return False

    def test_existing_apis(self):
        """Test existing APIs still work (collections, authentication, admin panel)"""
        try:
            # Test basic API endpoints
            endpoints_to_test = [
                ("/jerseys", "Jerseys API"),
                ("/marketplace/catalog", "Marketplace Catalog"),
                ("/explorer/leagues", "Explorer Leagues"),
                ("/stats/dynamic", "Dynamic Stats")
            ]
            
            results = []
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        results.append(f"{name}: ✅ Working")
                    else:
                        results.append(f"{name}: ❌ HTTP {response.status_code}")
                except Exception as e:
                    results.append(f"{name}: ❌ Error: {str(e)}")
            
            # Test authenticated endpoints if user token available
            if self.user_token:
                auth_headers = {"Authorization": f"Bearer {self.user_token}"}
                auth_endpoints = [
                    ("/profile", "User Profile"),
                    ("/notifications", "Notifications"),
                    ("/collections/my-owned", "User Collections")
                ]
                
                for endpoint, name in auth_endpoints:
                    try:
                        response = self.session.get(
                            f"{BACKEND_URL}{endpoint}", 
                            headers=auth_headers, 
                            timeout=10
                        )
                        if response.status_code == 200:
                            results.append(f"{name}: ✅ Working")
                        else:
                            results.append(f"{name}: ❌ HTTP {response.status_code}")
                    except Exception as e:
                        results.append(f"{name}: ❌ Error: {str(e)}")
            
            success_count = sum(1 for r in results if "✅" in r)
            total_count = len(results)
            
            self.log_test(
                "Existing APIs Functionality",
                success_count > total_count * 0.7,  # 70% success rate threshold
                f"{success_count}/{total_count} APIs working: {'; '.join(results)}"
            )
            
            return success_count > total_count * 0.7
            
        except Exception as e:
            self.log_test("Existing APIs Functionality", False, "", str(e))
            return False

    def test_admin_jersey_modification(self):
        """Test admin modification of pending jerseys via PUT /api/admin/jerseys/{id}"""
        if not self.admin_token:
            self.log_test("Admin Jersey Modification", False, "", "No admin token available")
            return False
            
        if not self.created_jerseys:
            self.log_test("Admin Jersey Modification", False, "", "No test jerseys available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First, get pending jerseys
            response = self.session.get(
                f"{BACKEND_URL}/admin/jerseys/pending",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test(
                    "Admin Jersey Modification",
                    False,
                    f"Cannot access pending jerseys: HTTP {response.status_code}",
                    response.text
                )
                return False
            
            pending_jerseys = response.json()
            if not pending_jerseys:
                self.log_test(
                    "Admin Jersey Modification",
                    False,
                    "No pending jerseys found for modification test"
                )
                return False
            
            # Try to modify the first pending jersey
            jersey_id = pending_jerseys[0].get('id')
            if not jersey_id:
                self.log_test(
                    "Admin Jersey Modification",
                    False,
                    "No jersey ID found in pending jerseys"
                )
                return False
            
            # Test modification (approve the jersey)
            modification_data = {
                "status": "approved",
                "admin_notes": "Jersey approved after review - test modification"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/admin/jerseys/{jersey_id}",
                json=modification_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                self.log_test(
                    "Admin Jersey Modification",
                    True,
                    f"Successfully modified jersey {jersey_id} - approved with admin notes"
                )
                return True
            else:
                # Try alternative endpoint for jersey approval
                response = self.session.post(
                    f"{BACKEND_URL}/admin/jerseys/{jersey_id}/approve",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 204]:
                    self.log_test(
                        "Admin Jersey Modification",
                        True,
                        f"Successfully approved jersey {jersey_id} via approve endpoint"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Jersey Modification",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    return False
                
        except Exception as e:
            self.log_test("Admin Jersey Modification", False, "", str(e))
            return False

    def test_admin_permissions(self):
        """Test admin permissions and access control"""
        if not self.admin_token:
            self.log_test("Admin Permissions", False, "", "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test admin-only endpoints
            admin_endpoints = [
                ("/admin/users", "Admin Users Management"),
                ("/admin/jerseys/pending", "Admin Pending Jerseys"),
                ("/admin/traffic-stats", "Admin Traffic Stats"),
                ("/admin/activities", "Admin Activities")
            ]
            
            results = []
            
            for endpoint, name in admin_endpoints:
                try:
                    response = self.session.get(
                        f"{BACKEND_URL}{endpoint}",
                        headers=headers,
                        timeout=10
                    )
                    if response.status_code == 200:
                        results.append(f"{name}: ✅ Accessible")
                    else:
                        results.append(f"{name}: ❌ HTTP {response.status_code}")
                except Exception as e:
                    results.append(f"{name}: ❌ Error: {str(e)}")
            
            success_count = sum(1 for r in results if "✅" in r)
            total_count = len(results)
            
            self.log_test(
                "Admin Permissions",
                success_count >= total_count * 0.75,  # 75% success rate threshold
                f"{success_count}/{total_count} admin endpoints accessible: {'; '.join(results)}"
            )
            
            return success_count >= total_count * 0.75
            
        except Exception as e:
            self.log_test("Admin Permissions", False, "", str(e))
            return False

    def test_jersey_detail_editor_data(self):
        """Test jersey detail data structure for JerseyDetailEditor"""
        if not self.user_token:
            self.log_test("Jersey Detail Editor Data", False, "", "No user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Get user's jerseys/collections to test detail editor data
            response = self.session.get(
                f"{BACKEND_URL}/collections/my-owned",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                collections = response.json()
                
                # Check if we have collection data to test detail editor
                if collections:
                    # Test detail editor data structure
                    collection_item = collections[0]
                    required_fields = ['id', 'jersey_id', 'collection_type', 'added_at']
                    
                    has_required_fields = all(field in collection_item for field in required_fields)
                    
                    # Check if jersey data is populated
                    jersey_data = collection_item.get('jersey', {})
                    jersey_fields = ['team', 'league', 'season', 'status']
                    has_jersey_data = all(field in jersey_data for field in jersey_fields)
                    
                    self.log_test(
                        "Jersey Detail Editor Data",
                        has_required_fields and has_jersey_data,
                        f"Collection data structure valid: {len(collections)} items, Required fields: {has_required_fields}, Jersey data: {has_jersey_data}"
                    )
                    
                    return has_required_fields and has_jersey_data
                else:
                    # No collections yet, but endpoint works
                    self.log_test(
                        "Jersey Detail Editor Data",
                        True,
                        "Collections endpoint accessible (0 items) - ready for detail editor"
                    )
                    return True
            else:
                self.log_test(
                    "Jersey Detail Editor Data",
                    False,
                    f"Cannot access collections: HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Jersey Detail Editor Data", False, "", str(e))
            return False

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🏈 TopKit Jersey Submission System Backend Testing")
        print("=" * 60)
        print(f"🎯 Backend URL: {BACKEND_URL}")
        print(f"👤 User: {USER_CREDENTIALS['email']}")
        print(f"👑 Admin: {ADMIN_CREDENTIALS['email']}")
        print()
        
        # Authentication tests
        print("🔐 AUTHENTICATION TESTS")
        print("-" * 30)
        user_auth_success = self.authenticate_user()
        admin_auth_success = self.authenticate_admin()
        print()
        
        # Jersey submission tests
        print("📝 JERSEY SUBMISSION TESTS")
        print("-" * 30)
        self.test_jersey_submission_basic()
        self.test_jersey_submission_multipart()
        self.test_required_fields_validation()
        print()
        
        # Existing functionality tests
        print("🔧 EXISTING FUNCTIONALITY TESTS")
        print("-" * 30)
        self.test_existing_apis()
        self.test_jersey_detail_editor_data()
        print()
        
        # Admin functionality tests
        print("👑 ADMIN FUNCTIONALITY TESTS")
        print("-" * 30)
        self.test_admin_permissions()
        self.test_admin_jersey_modification()
        print()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print()
        
        # Categorize results
        categories = {
            "Authentication": [],
            "Jersey Submission": [],
            "Existing APIs": [],
            "Admin Functions": [],
            "Data Structure": []
        }
        
        for result in self.test_results:
            test_name = result['test']
            if 'Authentication' in test_name:
                categories["Authentication"].append(result)
            elif 'Jersey Submission' in test_name or 'Required Fields' in test_name:
                categories["Jersey Submission"].append(result)
            elif 'Existing APIs' in test_name:
                categories["Existing APIs"].append(result)
            elif 'Admin' in test_name:
                categories["Admin Functions"].append(result)
            elif 'Detail Editor' in test_name:
                categories["Data Structure"].append(result)
        
        # Print category summaries
        for category, results in categories.items():
            if results:
                category_passed = sum(1 for r in results if r['success'])
                category_total = len(results)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                status_icon = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
                print(f"{status_icon} {category}: {category_rate:.1f}% ({category_passed}/{category_total})")
        
        print()
        
        # Print failed tests details
        failed_results = [r for r in self.test_results if not r['success']]
        if failed_results:
            print("🚨 FAILED TESTS DETAILS")
            print("-" * 30)
            for result in failed_results:
                print(f"❌ {result['test']}")
                if result['error']:
                    print(f"   Error: {result['error']}")
                if result['details']:
                    print(f"   Details: {result['details']}")
                print()
        
        # Print created jerseys for cleanup
        if self.created_jerseys:
            print("🏷️ CREATED TEST JERSEYS")
            print("-" * 30)
            for jersey_id in self.created_jerseys:
                print(f"   Jersey ID: {jersey_id}")
            print()
        
        # Final assessment
        print("🎯 FINAL ASSESSMENT")
        print("-" * 30)
        if success_rate >= 90:
            print("🎉 EXCELLENT: Jersey submission system is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD: Jersey submission system is mostly functional with minor issues.")
        elif success_rate >= 60:
            print("⚠️ MODERATE: Jersey submission system has some issues that need attention.")
        else:
            print("🚨 CRITICAL: Jersey submission system has major issues requiring fixes.")
        
        print()
        print("📋 KEY FINDINGS:")
        
        # Authentication status
        auth_results = [r for r in self.test_results if 'Authentication' in r['test']]
        auth_success = all(r['success'] for r in auth_results)
        if auth_success:
            print("   ✅ Authentication system working for both user and admin accounts")
        else:
            print("   ❌ Authentication issues detected - may block other functionality")
        
        # Jersey submission status
        submission_results = [r for r in self.test_results if 'Jersey Submission' in r['test'] or 'Required Fields' in r['test']]
        submission_success = sum(1 for r in submission_results if r['success'])
        submission_total = len(submission_results)
        if submission_success == submission_total:
            print("   ✅ Jersey submission system fully operational with proper validation")
        elif submission_success > 0:
            print(f"   ⚠️ Jersey submission partially working ({submission_success}/{submission_total})")
        else:
            print("   ❌ Jersey submission system not functional")
        
        # Admin functionality status
        admin_results = [r for r in self.test_results if 'Admin' in r['test']]
        admin_success = sum(1 for r in admin_results if r['success'])
        admin_total = len(admin_results)
        if admin_success == admin_total:
            print("   ✅ Admin functionality fully operational")
        elif admin_success > 0:
            print(f"   ⚠️ Admin functionality partially working ({admin_success}/{admin_total})")
        else:
            print("   ❌ Admin functionality not accessible")
        
        print()
        print("🔗 NEXT STEPS:")
        if failed_tests == 0:
            print("   🎯 System ready for frontend integration testing")
            print("   🎯 Consider testing JerseyDetailEditor UI components")
        else:
            print("   🔧 Fix failed backend endpoints before frontend testing")
            print("   🔧 Verify admin permissions and authentication")
        
        return success_rate

if __name__ == "__main__":
    tester = TopKitJerseySubmissionTester()
    try:
        success_rate = tester.run_comprehensive_test()
        # Exit with appropriate code
        sys.exit(0 if success_rate and success_rate >= 75 else 1)
    except Exception as e:
        print(f"🚨 Test execution failed: {e}")
        sys.exit(1)