#!/usr/bin/env python3

"""
Moderation Dashboard Authentication Issues Test
Testing for intermittent authentication issues when navigating between tabs.

This test specifically addresses the reported issue:
"intermittent authentication issues on the Moderation Dashboard when navigating between tabs"
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ModerationAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} - {test_name}: {details}")

    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                user_role = user_data.get('role')
                
                if self.admin_token and user_role == 'admin':
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    self.log_test(
                        "Initial Admin Authentication", 
                        True, 
                        f"Successfully authenticated. Token: {len(self.admin_token)} chars, Role: {user_role}"
                    )
                    return True
                    
            self.log_test("Initial Admin Authentication", False, f"Login failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_test("Initial Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_token_persistence(self):
        """Test if token remains valid across multiple requests"""
        print("\n🔄 TESTING TOKEN PERSISTENCE")
        
        try:
            # Make multiple requests to different endpoints to simulate tab navigation
            endpoints_to_test = [
                ("/contributions-v2/admin/moderation-stats", "Moderation Stats"),
                ("/contributions-v2/?status=pending_review&page=1&limit=25", "Pending Contributions"),
                ("/contributions-v2/?status=approved&page=1&limit=25", "Approved Contributions"),
                ("/contributions-v2/?status=rejected&page=1&limit=25", "Rejected Contributions"),
                ("/contributions-v2/admin/moderation-stats", "Stats Again")
            ]
            
            for endpoint, description in endpoints_to_test:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    self.log_test(
                        f"Token Persistence - {description}", 
                        True, 
                        f"Successfully accessed {endpoint}"
                    )
                elif response.status_code == 401:
                    self.log_test(
                        f"Token Persistence - {description}", 
                        False, 
                        f"Authentication failed for {endpoint} - token may have expired"
                    )
                    return False
                else:
                    self.log_test(
                        f"Token Persistence - {description}", 
                        False, 
                        f"Unexpected status {response.status_code} for {endpoint}"
                    )
                
                # Small delay to simulate user navigation
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.log_test("Token Persistence", False, f"Exception: {str(e)}")
            return False

    def test_rapid_tab_switching(self):
        """Test rapid switching between different moderation tabs"""
        print("\n⚡ TESTING RAPID TAB SWITCHING")
        
        try:
            # Simulate rapid tab switching by making quick successive requests
            for i in range(10):
                # Alternate between different endpoints rapidly
                endpoints = [
                    "/contributions-v2/?status=pending_review&limit=10",
                    "/contributions-v2/?status=approved&limit=10", 
                    "/contributions-v2/?status=rejected&limit=10",
                    "/contributions-v2/admin/moderation-stats"
                ]
                
                endpoint = endpoints[i % len(endpoints)]
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code != 200:
                    self.log_test(
                        f"Rapid Tab Switch - Request {i+1}", 
                        False, 
                        f"Failed on request {i+1} to {endpoint}: {response.status_code}"
                    )
                    return False
                
                # No delay - simulate very rapid switching
            
            self.log_test(
                "Rapid Tab Switching", 
                True, 
                "Successfully handled 10 rapid successive requests without authentication issues"
            )
            return True
            
        except Exception as e:
            self.log_test("Rapid Tab Switching", False, f"Exception: {str(e)}")
            return False

    def test_session_timeout_handling(self):
        """Test how the system handles potential session timeouts"""
        print("\n⏰ TESTING SESSION TIMEOUT HANDLING")
        
        try:
            # First, verify current token works
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/admin/moderation-stats")
            if response.status_code != 200:
                self.log_test(
                    "Session Timeout - Initial Check", 
                    False, 
                    f"Token not working initially: {response.status_code}"
                )
                return False
            
            self.log_test(
                "Session Timeout - Initial Check", 
                True, 
                "Token working correctly before timeout test"
            )
            
            # Test with a potentially expired/invalid token
            original_token = self.session.headers.get('Authorization')
            
            # Modify token slightly to simulate corruption/expiration
            corrupted_token = original_token[:-5] + "XXXXX"
            self.session.headers['Authorization'] = corrupted_token
            
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/admin/moderation-stats")
            
            if response.status_code == 401:
                self.log_test(
                    "Session Timeout - Invalid Token Handling", 
                    True, 
                    "System correctly rejected invalid/corrupted token"
                )
            else:
                self.log_test(
                    "Session Timeout - Invalid Token Handling", 
                    False, 
                    f"System should have rejected invalid token, got: {response.status_code}"
                )
            
            # Restore original token
            self.session.headers['Authorization'] = original_token
            
            # Verify restoration works
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/admin/moderation-stats")
            if response.status_code == 200:
                self.log_test(
                    "Session Timeout - Token Restoration", 
                    True, 
                    "Successfully restored valid token"
                )
                return True
            else:
                self.log_test(
                    "Session Timeout - Token Restoration", 
                    False, 
                    f"Failed to restore token: {response.status_code}"
                )
                return False
            
        except Exception as e:
            self.log_test("Session Timeout Handling", False, f"Exception: {str(e)}")
            return False

    def test_concurrent_requests(self):
        """Test handling of concurrent requests that might happen during tab navigation"""
        print("\n🔀 TESTING CONCURRENT REQUEST HANDLING")
        
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def make_request(endpoint, request_id):
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    results_queue.put({
                        'id': request_id,
                        'status': response.status_code,
                        'endpoint': endpoint,
                        'success': response.status_code == 200
                    })
                except Exception as e:
                    results_queue.put({
                        'id': request_id,
                        'status': 'error',
                        'endpoint': endpoint,
                        'success': False,
                        'error': str(e)
                    })
            
            # Create multiple threads to simulate concurrent requests
            threads = []
            endpoints = [
                "/contributions-v2/?status=pending_review&limit=5",
                "/contributions-v2/?status=approved&limit=5",
                "/contributions-v2/?status=rejected&limit=5",
                "/contributions-v2/admin/moderation-stats",
                "/contributions-v2/?page=1&limit=10"
            ]
            
            for i, endpoint in enumerate(endpoints):
                thread = threading.Thread(target=make_request, args=(endpoint, i))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=10)
            
            # Collect results
            results = []
            while not results_queue.empty():
                results.append(results_queue.get())
            
            successful_requests = sum(1 for r in results if r['success'])
            total_requests = len(results)
            
            if successful_requests == total_requests:
                self.log_test(
                    "Concurrent Request Handling", 
                    True, 
                    f"All {total_requests} concurrent requests succeeded"
                )
                return True
            else:
                failed_requests = [r for r in results if not r['success']]
                self.log_test(
                    "Concurrent Request Handling", 
                    False, 
                    f"Only {successful_requests}/{total_requests} requests succeeded. Failed: {failed_requests}"
                )
                return False
            
        except Exception as e:
            self.log_test("Concurrent Request Handling", False, f"Exception: {str(e)}")
            return False

    def test_moderation_action_with_navigation(self):
        """Test moderation actions while simulating navigation between tabs"""
        print("\n⚖️ TESTING MODERATION ACTIONS WITH TAB NAVIGATION")
        
        try:
            # Create a test contribution
            contribution_data = {
                "entity_type": "team",
                "title": "Test Team for Navigation Auth",
                "description": "Testing authentication during navigation",
                "entity_data": {
                    "name": "Navigation Test Team",
                    "country": "France",
                    "city": "Paris",
                    "founded_year": 2024,
                    "colors": ["red", "blue"]
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/contributions-v2/", json=contribution_data)
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Moderation Action - Create Test Contribution", 
                    False, 
                    f"Failed to create test contribution: {response.status_code}"
                )
                return False
            
            contribution = response.json()
            contribution_id = contribution.get('id')
            
            self.log_test(
                "Moderation Action - Create Test Contribution", 
                True, 
                f"Created test contribution: {contribution_id}"
            )
            
            # Simulate navigation between tabs before moderation action
            navigation_endpoints = [
                "/contributions-v2/?status=pending_review&limit=10",
                "/contributions-v2/?status=approved&limit=10",
                "/contributions-v2/admin/moderation-stats",
                "/contributions-v2/?status=rejected&limit=10"
            ]
            
            for endpoint in navigation_endpoints:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code != 200:
                    self.log_test(
                        "Moderation Action - Navigation Before Action", 
                        False, 
                        f"Navigation failed at {endpoint}: {response.status_code}"
                    )
                    return False
            
            self.log_test(
                "Moderation Action - Navigation Before Action", 
                True, 
                "Successfully navigated between tabs before moderation action"
            )
            
            # Now perform moderation action
            moderate_data = {
                "action": "approve",
                "reason": "Test approval after navigation",
                "internal_notes": "Testing auth persistence during navigation",
                "notify_contributor": False
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/{contribution_id}/moderate", 
                json=moderate_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'approved':
                    self.log_test(
                        "Moderation Action - Approve After Navigation", 
                        True, 
                        "Successfully approved contribution after tab navigation"
                    )
                    return True
                else:
                    self.log_test(
                        "Moderation Action - Approve After Navigation", 
                        False, 
                        f"Unexpected status after approval: {result.get('status')}"
                    )
                    return False
            else:
                self.log_test(
                    "Moderation Action - Approve After Navigation", 
                    False, 
                    f"Moderation action failed: {response.status_code} - {response.text}"
                )
                return False
            
        except Exception as e:
            self.log_test("Moderation Action with Navigation", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all authentication-focused tests"""
        print("🚀 STARTING MODERATION DASHBOARD AUTHENTICATION TESTS")
        print("=" * 80)
        
        # Test 1: Initial Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with other tests.")
            return False
        
        # Test 2: Token Persistence
        self.test_token_persistence()
        
        # Test 3: Rapid Tab Switching
        self.test_rapid_tab_switching()
        
        # Test 4: Session Timeout Handling
        self.test_session_timeout_handling()
        
        # Test 5: Concurrent Request Handling
        self.test_concurrent_requests()
        
        # Test 6: Moderation Action with Navigation
        self.test_moderation_action_with_navigation()
        
        # Print summary
        self.print_test_summary()
        
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 MODERATION AUTHENTICATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        
        # Assessment for authentication issues
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT: No authentication issues detected during tab navigation!")
        elif success_rate >= 80:
            print(f"\n✅ GOOD: Minor authentication issues detected, but system is stable.")
        elif success_rate >= 60:
            print(f"\n⚠️ MODERATE: Some authentication issues detected during navigation.")
        else:
            print(f"\n❌ CRITICAL: Significant authentication issues detected - intermittent auth problems confirmed!")

def main():
    """Main test execution"""
    tester = ModerationAuthTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n🏁 AUTHENTICATION TESTING COMPLETED")
        else:
            print(f"\n💥 AUTHENTICATION TESTING FAILED")
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {str(e)}")

if __name__ == "__main__":
    main()