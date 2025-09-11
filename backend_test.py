#!/usr/bin/env python3

"""
Enhanced Moderation Dashboard Backend Test
Testing the enhanced moderation dashboard backend functionality with new features.

Test Requirements from Review Request:
1. **Contributions API with Pagination**: Test the `/api/contributions-v2/` endpoint with different status filters (pending_review, approved, rejected) and pagination parameters (page, limit)
2. **Status-based Filtering**: Verify that the API correctly filters contributions by status for the new Approved and Rejected tabs
3. **Moderation Actions**: Test the `/api/contributions-v2/{contribution_id}/moderate` endpoint to ensure approve/reject/restore actions work correctly 
4. **Moderation Stats**: Test `/api/contributions-v2/admin/moderation-stats` to ensure stats are calculated correctly for all the different statuses
5. **Admin Authentication**: Verify that admin authentication works properly for accessing moderation features
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ModerationDashboardTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.test_contributions = []  # Store created test contributions
        
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
        """Test admin authentication"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        
        try:
            # Login with admin credentials
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                
                # Get user info from login response
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                user_role = user_data.get('role')
                
                if self.admin_token and self.admin_user_id:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    
                    if user_role == 'admin':
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Successfully authenticated as admin. User ID: {self.admin_user_id}, Role: {user_role}, Token length: {len(self.admin_token)}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Admin Authentication", 
                            False, 
                            f"User authenticated but role is '{user_role}', not 'admin'"
                        )
                        return False
                else:
                    self.log_test(
                        "Admin Authentication", 
                        False, 
                        f"Missing token or user ID in response. Token: {bool(self.admin_token)}, User ID: {bool(self.admin_user_id)}"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Login failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_moderation_stats(self):
        """Test moderation stats endpoint"""
        print("\n📊 TESTING MODERATION STATS")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/admin/moderation-stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Verify required fields are present
                required_fields = [
                    'pending_contributions', 'approved_today', 'rejected_today',
                    'total_votes_today', 'auto_approved_today', 'auto_rejected_today',
                    'contributions_by_type', 'top_contributors'
                ]
                
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    self.log_test(
                        "Moderation Stats API", 
                        True, 
                        f"Stats retrieved successfully. Pending: {stats['pending_contributions']}, "
                        f"Approved today: {stats['approved_today']}, Rejected today: {stats['rejected_today']}"
                    )
                    
                    # Test contributions by type
                    contrib_types = stats.get('contributions_by_type', {})
                    self.log_test(
                        "Contributions by Type Stats", 
                        True, 
                        f"Found {len(contrib_types)} contribution types: {list(contrib_types.keys())}"
                    )
                    
                    return True
                else:
                    self.log_test(
                        "Moderation Stats API", 
                        False, 
                        f"Missing required fields: {missing_fields}"
                    )
                    return False
            else:
                self.log_test(
                    "Moderation Stats API", 
                    False, 
                    f"Failed to get stats: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Moderation Stats API", False, f"Exception: {str(e)}")
            return False

    def test_contributions_pagination(self):
        """Test contributions API with pagination"""
        print("\n📄 TESTING CONTRIBUTIONS PAGINATION")
        
        try:
            # Test basic pagination
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/?page=1&limit=10")
            
            if response.status_code == 200:
                contributions = response.json()
                
                if isinstance(contributions, list):
                    self.log_test(
                        "Contributions Pagination - Basic", 
                        True, 
                        f"Retrieved {len(contributions)} contributions (max 10 requested)"
                    )
                    
                    # Test different page sizes
                    response_5 = self.session.get(f"{BACKEND_URL}/contributions-v2/?page=1&limit=5")
                    if response_5.status_code == 200:
                        contributions_5 = response_5.json()
                        if len(contributions_5) <= 5:
                            self.log_test(
                                "Contributions Pagination - Limit Control", 
                                True, 
                                f"Limit parameter working: requested 5, got {len(contributions_5)}"
                            )
                        else:
                            self.log_test(
                                "Contributions Pagination - Limit Control", 
                                False, 
                                f"Limit not respected: requested 5, got {len(contributions_5)}"
                            )
                    
                    # Test page 2 if we have enough contributions
                    if len(contributions) >= 10:
                        response_p2 = self.session.get(f"{BACKEND_URL}/contributions-v2/?page=2&limit=10")
                        if response_p2.status_code == 200:
                            contributions_p2 = response_p2.json()
                            self.log_test(
                                "Contributions Pagination - Page 2", 
                                True, 
                                f"Page 2 retrieved {len(contributions_p2)} contributions"
                            )
                    
                    return True
                else:
                    self.log_test(
                        "Contributions Pagination - Basic", 
                        False, 
                        f"Expected list, got {type(contributions)}"
                    )
                    return False
            else:
                self.log_test(
                    "Contributions Pagination - Basic", 
                    False, 
                    f"Failed to get contributions: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Contributions Pagination", False, f"Exception: {str(e)}")
            return False

    def test_status_filtering(self):
        """Test status-based filtering for contributions"""
        print("\n🔍 TESTING STATUS-BASED FILTERING")
        
        try:
            # Test different status filters
            statuses_to_test = ['pending_review', 'approved', 'rejected']
            
            for status in statuses_to_test:
                response = self.session.get(f"{BACKEND_URL}/contributions-v2/?status={status}&limit=20")
                
                if response.status_code == 200:
                    contributions = response.json()
                    
                    if isinstance(contributions, list):
                        # Verify all contributions have the requested status
                        status_match = all(contrib.get('status') == status for contrib in contributions)
                        
                        if status_match or len(contributions) == 0:
                            self.log_test(
                                f"Status Filter - {status}", 
                                True, 
                                f"Found {len(contributions)} contributions with status '{status}'"
                            )
                        else:
                            mismatched = [contrib.get('status') for contrib in contributions if contrib.get('status') != status]
                            self.log_test(
                                f"Status Filter - {status}", 
                                False, 
                                f"Status mismatch found: expected '{status}', found {set(mismatched)}"
                            )
                    else:
                        self.log_test(
                            f"Status Filter - {status}", 
                            False, 
                            f"Expected list, got {type(contributions)}"
                        )
                else:
                    self.log_test(
                        f"Status Filter - {status}", 
                        False, 
                        f"Failed to filter by status: {response.status_code} - {response.text}"
                    )
            
            # Test combined status and pagination
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/?status=approved&page=1&limit=5")
            if response.status_code == 200:
                contributions = response.json()
                self.log_test(
                    "Status + Pagination Combined", 
                    True, 
                    f"Combined filtering working: {len(contributions)} approved contributions (limit 5)"
                )
            
            return True
                
        except Exception as e:
            self.log_test("Status-based Filtering", False, f"Exception: {str(e)}")
            return False

    def create_test_contribution(self):
        """Create a test contribution for moderation testing"""
        try:
            # Create a test team contribution
            contribution_data = {
                "entity_type": "team",
                "title": "Test Team for Moderation",
                "description": "This is a test team contribution for moderation testing",
                "entity_data": {
                    "name": "Test Moderation Team",
                    "country": "France",
                    "city": "Paris",
                    "founded_year": 2024,
                    "colors": ["blue", "white"]
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/contributions-v2/", json=contribution_data)
            
            if response.status_code == 201:
                contribution = response.json()
                contribution_id = contribution.get('id')
                self.test_contributions.append(contribution_id)
                
                self.log_test(
                    "Test Contribution Creation", 
                    True, 
                    f"Created test contribution with ID: {contribution_id}"
                )
                return contribution_id
            else:
                self.log_test(
                    "Test Contribution Creation", 
                    False, 
                    f"Failed to create contribution: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Test Contribution Creation", False, f"Exception: {str(e)}")
            return None

    def test_moderation_actions(self):
        """Test moderation actions (approve/reject/restore)"""
        print("\n⚖️ TESTING MODERATION ACTIONS")
        
        try:
            # First, try to find an existing pending contribution
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/?status=pending_review&limit=5")
            
            contribution_id = None
            if response.status_code == 200:
                contributions = response.json()
                if contributions:
                    contribution_id = contributions[0].get('id')
                    self.log_test(
                        "Find Pending Contribution", 
                        True, 
                        f"Found existing pending contribution: {contribution_id}"
                    )
            
            # If no pending contribution found, create one
            if not contribution_id:
                contribution_id = self.create_test_contribution()
            
            if not contribution_id:
                self.log_test(
                    "Moderation Actions Setup", 
                    False, 
                    "Could not find or create a contribution to test moderation"
                )
                return False
            
            # Test APPROVE action
            approve_data = {
                "action": "approve",
                "reason": "Test approval - contribution meets quality standards",
                "internal_notes": "Automated test approval",
                "notify_contributor": False
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/{contribution_id}/moderate", 
                json=approve_data
            )
            
            if response.status_code == 200:
                result = response.json()
                new_status = result.get('status')
                
                if new_status == 'approved':
                    self.log_test(
                        "Moderation Action - Approve", 
                        True, 
                        f"Successfully approved contribution. New status: {new_status}"
                    )
                    
                    # Verify the contribution status was updated
                    verify_response = self.session.get(f"{BACKEND_URL}/contributions-v2/{contribution_id}")
                    if verify_response.status_code == 200:
                        contrib_data = verify_response.json()
                        if contrib_data.get('status') == 'approved':
                            self.log_test(
                                "Moderation Action - Status Verification", 
                                True, 
                                "Contribution status correctly updated to approved"
                            )
                        else:
                            self.log_test(
                                "Moderation Action - Status Verification", 
                                False, 
                                f"Status not updated correctly: {contrib_data.get('status')}"
                            )
                else:
                    self.log_test(
                        "Moderation Action - Approve", 
                        False, 
                        f"Unexpected status after approval: {new_status}"
                    )
            else:
                self.log_test(
                    "Moderation Action - Approve", 
                    False, 
                    f"Failed to approve contribution: {response.status_code} - {response.text}"
                )
            
            # Test REJECT action (create another test contribution first)
            reject_contribution_id = self.create_test_contribution()
            if reject_contribution_id:
                reject_data = {
                    "action": "reject",
                    "reason": "Test rejection - does not meet quality standards",
                    "internal_notes": "Automated test rejection",
                    "notify_contributor": False
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/contributions-v2/{reject_contribution_id}/moderate", 
                    json=reject_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    new_status = result.get('status')
                    
                    if new_status == 'rejected':
                        self.log_test(
                            "Moderation Action - Reject", 
                            True, 
                            f"Successfully rejected contribution. New status: {new_status}"
                        )
                    else:
                        self.log_test(
                            "Moderation Action - Reject", 
                            False, 
                            f"Unexpected status after rejection: {new_status}"
                        )
                else:
                    self.log_test(
                        "Moderation Action - Reject", 
                        False, 
                        f"Failed to reject contribution: {response.status_code} - {response.text}"
                    )
            
            # Test REQUEST_REVISION action
            revision_contribution_id = self.create_test_contribution()
            if revision_contribution_id:
                revision_data = {
                    "action": "request_revision",
                    "reason": "Test revision request - needs more information",
                    "internal_notes": "Automated test revision request",
                    "notify_contributor": False
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/contributions-v2/{revision_contribution_id}/moderate", 
                    json=revision_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    new_status = result.get('status')
                    
                    if new_status == 'needs_revision':
                        self.log_test(
                            "Moderation Action - Request Revision", 
                            True, 
                            f"Successfully requested revision. New status: {new_status}"
                        )
                    else:
                        self.log_test(
                            "Moderation Action - Request Revision", 
                            False, 
                            f"Unexpected status after revision request: {new_status}"
                        )
                else:
                    self.log_test(
                        "Moderation Action - Request Revision", 
                        False, 
                        f"Failed to request revision: {response.status_code} - {response.text}"
                    )
            
            return True
                
        except Exception as e:
            self.log_test("Moderation Actions", False, f"Exception: {str(e)}")
            return False

    def test_admin_access_control(self):
        """Test that moderation endpoints require admin access"""
        print("\n🔒 TESTING ADMIN ACCESS CONTROL")
        
        try:
            # Save current admin token
            admin_token = self.session.headers.get('Authorization')
            
            # Remove authorization header to test unauthorized access
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Test moderation stats without auth
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/admin/moderation-stats")
            
            if response.status_code == 401:
                self.log_test(
                    "Admin Access Control - Stats Unauthorized", 
                    True, 
                    "Correctly blocked unauthorized access to moderation stats"
                )
            else:
                self.log_test(
                    "Admin Access Control - Stats Unauthorized", 
                    False, 
                    f"Should have blocked unauthorized access, got: {response.status_code}"
                )
            
            # Test moderation action without auth
            if self.test_contributions:
                test_data = {
                    "action": "approve",
                    "reason": "Test",
                    "notify_contributor": False
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/contributions-v2/{self.test_contributions[0]}/moderate", 
                    json=test_data
                )
                
                if response.status_code == 401:
                    self.log_test(
                        "Admin Access Control - Moderation Unauthorized", 
                        True, 
                        "Correctly blocked unauthorized moderation action"
                    )
                else:
                    self.log_test(
                        "Admin Access Control - Moderation Unauthorized", 
                        False, 
                        f"Should have blocked unauthorized moderation, got: {response.status_code}"
                    )
            
            # Restore admin token
            self.session.headers['Authorization'] = admin_token
            
            # Verify admin access is restored
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/admin/moderation-stats")
            if response.status_code == 200:
                self.log_test(
                    "Admin Access Control - Restore Access", 
                    True, 
                    "Admin access correctly restored"
                )
            else:
                self.log_test(
                    "Admin Access Control - Restore Access", 
                    False, 
                    f"Failed to restore admin access: {response.status_code}"
                )
            
            return True
                
        except Exception as e:
            self.log_test("Admin Access Control", False, f"Exception: {str(e)}")
            return False

    def test_contribution_detail_access(self):
        """Test accessing individual contribution details"""
        print("\n📋 TESTING CONTRIBUTION DETAIL ACCESS")
        
        try:
            # Get a list of contributions first
            response = self.session.get(f"{BACKEND_URL}/contributions-v2/?limit=5")
            
            if response.status_code == 200:
                contributions = response.json()
                
                if contributions:
                    contribution_id = contributions[0].get('id')
                    
                    # Test getting contribution detail
                    detail_response = self.session.get(f"{BACKEND_URL}/contributions-v2/{contribution_id}")
                    
                    if detail_response.status_code == 200:
                        detail = detail_response.json()
                        
                        # Verify required fields are present
                        required_fields = ['id', 'entity_type', 'title', 'status', 'created_by', 'created_at']
                        missing_fields = [field for field in required_fields if field not in detail]
                        
                        if not missing_fields:
                            self.log_test(
                                "Contribution Detail Access", 
                                True, 
                                f"Successfully retrieved contribution detail for ID: {contribution_id}"
                            )
                            
                            # Check if history is present
                            if 'history' in detail:
                                self.log_test(
                                    "Contribution History Present", 
                                    True, 
                                    f"Contribution has {len(detail['history'])} history entries"
                                )
                            
                            return True
                        else:
                            self.log_test(
                                "Contribution Detail Access", 
                                False, 
                                f"Missing required fields in detail: {missing_fields}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Contribution Detail Access", 
                            False, 
                            f"Failed to get contribution detail: {detail_response.status_code}"
                        )
                        return False
                else:
                    self.log_test(
                        "Contribution Detail Access", 
                        False, 
                        "No contributions found to test detail access"
                    )
                    return False
            else:
                self.log_test(
                    "Contribution Detail Access", 
                    False, 
                    f"Failed to get contributions list: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Contribution Detail Access", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all moderation dashboard tests"""
        print("🚀 STARTING ENHANCED MODERATION DASHBOARD BACKEND TESTS")
        print("=" * 80)
        
        # Test 1: Admin Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with other tests.")
            return False
        
        # Test 2: Moderation Stats
        self.test_moderation_stats()
        
        # Test 3: Contributions Pagination
        self.test_contributions_pagination()
        
        # Test 4: Status-based Filtering
        self.test_status_filtering()
        
        # Test 5: Contribution Detail Access
        self.test_contribution_detail_access()
        
        # Test 6: Moderation Actions
        self.test_moderation_actions()
        
        # Test 7: Admin Access Control
        self.test_admin_access_control()
        
        # Print summary
        self.print_test_summary()
        
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 ENHANCED MODERATION DASHBOARD TEST SUMMARY")
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
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: Enhanced Moderation Dashboard backend is working excellently!")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: Enhanced Moderation Dashboard backend is working well with minor issues.")
        elif success_rate >= 50:
            print(f"\n⚠️ MODERATE: Enhanced Moderation Dashboard backend has some issues that need attention.")
        else:
            print(f"\n❌ CRITICAL: Enhanced Moderation Dashboard backend has significant issues requiring immediate attention.")

def main():
    """Main test execution"""
    tester = ModerationDashboardTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n🏁 TESTING COMPLETED")
        else:
            print(f"\n💥 TESTING FAILED - Critical authentication issue")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()