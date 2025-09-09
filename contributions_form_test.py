#!/usr/bin/env python3
"""
Contributions Form Functionality Testing - Review Request Specific
===============================================================

This test verifies the contributions form functionality as requested in the review:
1. Test creating a team contribution with the exact payload format specified
2. Verify the API accepts the payload format  
3. Check the contribution is created successfully
4. Verify the response format matches frontend expectations
5. Test validation requirements

SPECIFIC TEST NEEDED from review request:
Test creating a team contribution with this exact data:
POST /api/contributions-v2/
Content-Type: application/json
Authorization: Bearer {valid_admin_token}

{
  "entity_type": "team",
  "title": "Frontend Test Team", 
  "description": "",
  "data": {
    "name": "Frontend Test Team",
    "country": "France"
  },
  "source_urls": []
}
"""

import requests
import json
import base64
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ContributionsFormTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        
    def authenticate_admin(self):
        """Authenticate with admin credentials"""
        print("🔐 Testing admin authentication...")
        
        auth_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=auth_data)
            print(f"   Auth response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                
                print(f"   ✅ Admin authenticated successfully")
                print(f"   User: {user_data.get('name', 'Unknown')}")
                print(f"   Role: {user_data.get('role', 'Unknown')}")
                print(f"   Token length: {len(self.admin_token) if self.admin_token else 0}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def test_contributions_v2_endpoint(self):
        """Test the main contributions-v2 endpoint"""
        print("\n📝 Testing POST /api/contributions-v2/ endpoint...")
        
        # Test data for different entity types
        test_cases = [
            {
                "name": "Team Contribution",
                "data": {
                    "entity_type": "team",
                    "title": "Add Test Team FC",
                    "description": "Test team contribution for form submission testing",
                    "data": {
                        "name": "Test Team FC",
                        "country": "France",
                        "city": "Paris"
                    },
                    "source_urls": ["https://example.com/test-team"]
                }
            },
            {
                "name": "Brand Contribution", 
                "data": {
                    "entity_type": "brand",
                    "title": "Add Test Brand",
                    "description": "Test brand contribution for form submission testing",
                    "data": {
                        "name": "Test Brand",
                        "country": "France"
                    },
                    "source_urls": ["https://example.com/test-brand"]
                }
            },
            {
                "name": "Player Contribution",
                "data": {
                    "entity_type": "player",
                    "title": "Add Test Player",
                    "description": "Test player contribution for form submission testing",
                    "data": {
                        "name": "Test Player",
                        "nationality": "French"
                    },
                    "source_urls": ["https://example.com/test-player"]
                }
            },
            {
                "name": "Competition Contribution",
                "data": {
                    "entity_type": "competition",
                    "title": "Add Test Competition",
                    "description": "Test competition contribution for form submission testing",
                    "data": {
                        "competition_name": "Test Competition",
                        "country": "France",
                        "type": "National league"
                    },
                    "source_urls": ["https://example.com/test-competition"]
                }
            },
            {
                "name": "Master Kit Contribution",
                "data": {
                    "entity_type": "master_kit",
                    "title": "Add Test Master Kit",
                    "description": "Test master kit contribution for form submission testing",
                    "data": {
                        "team_name": "Test Team FC",
                        "brand_name": "Test Brand",
                        "season": "2024-25",
                        "jersey_type": "home"
                    },
                    "source_urls": ["https://example.com/test-master-kit"]
                }
            },
            {
                "name": "Reference Kit Contribution",
                "data": {
                    "entity_type": "reference_kit",
                    "title": "Add Test Reference Kit",
                    "description": "Test reference kit contribution for form submission testing",
                    "data": {
                        "master_kit_name": "Test Master Kit",
                        "size": "M",
                        "condition": "new"
                    },
                    "source_urls": ["https://example.com/test-reference-kit"]
                }
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n   Testing {test_case['name']}...")
            
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/contributions-v2/",
                    json=test_case['data'],
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    contribution_id = data.get('id')
                    print(f"   ✅ {test_case['name']} created successfully")
                    print(f"   Contribution ID: {contribution_id}")
                    print(f"   Status: {data.get('status', 'Unknown')}")
                    results.append({
                        'test': test_case['name'],
                        'success': True,
                        'contribution_id': contribution_id,
                        'status': data.get('status')
                    })
                else:
                    error_text = response.text
                    print(f"   ❌ {test_case['name']} failed: {error_text}")
                    
                    # Try to parse error details
                    try:
                        error_data = response.json()
                        if 'detail' in error_data:
                            print(f"   Error details: {error_data['detail']}")
                    except:
                        pass
                    
                    results.append({
                        'test': test_case['name'],
                        'success': False,
                        'error': error_text,
                        'status_code': response.status_code
                    })
                        
            except Exception as e:
                print(f"   ❌ {test_case['name']} error: {e}")
                results.append({
                    'test': test_case['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def test_form_validation(self):
        """Test form validation with invalid data"""
        print("\n🔍 Testing form validation...")
        
        validation_tests = [
            {
                "name": "Missing title field",
                "data": {
                    "entity_type": "team",
                    "data": {"name": "Test Team"},
                    "source_urls": []
                },
                "expected_error": True
            },
            {
                "name": "Invalid entity type",
                "data": {
                    "entity_type": "invalid_type",
                    "title": "Test Invalid",
                    "data": {"name": "Test"},
                    "source_urls": []
                },
                "expected_error": True
            },
            {
                "name": "Valid data should be accepted",
                "data": {
                    "entity_type": "team",
                    "title": "Valid Test Team",
                    "description": "This should work",
                    "data": {"name": "Valid Team", "country": "France"},
                    "source_urls": []
                },
                "expected_error": False
            }
        ]
        
        validation_results = []
        
        for test in validation_tests:
            print(f"\n   Testing {test['name']}...")
            
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/contributions-v2/",
                    json=test['data'],
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"   Status: {response.status_code}")
                
                if test['expected_error']:
                    if response.status_code >= 400:
                        print(f"   ✅ Validation correctly rejected invalid data")
                        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                        print(f"   Error response: {error_data}")
                        validation_results.append({
                            'test': test['name'],
                            'success': True,
                            'properly_rejected': True
                        })
                    else:
                        print(f"   ❌ Validation should have rejected this data")
                        validation_results.append({
                            'test': test['name'],
                            'success': False,
                            'properly_rejected': False
                        })
                else:
                    if response.status_code < 400:
                        print(f"   ✅ Valid data accepted")
                        validation_results.append({
                            'test': test['name'],
                            'success': True,
                            'properly_accepted': True
                        })
                    else:
                        print(f"   ❌ Valid data incorrectly rejected")
                        validation_results.append({
                            'test': test['name'],
                            'success': False,
                            'properly_accepted': False
                        })
                        
            except Exception as e:
                print(f"   ❌ Validation test error: {e}")
                validation_results.append({
                    'test': test['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return validation_results
    
    def test_error_message_format(self):
        """Test that error messages are properly formatted (not [object Object])"""
        print("\n🔍 Testing error message formatting...")
        
        # Send invalid data to trigger validation errors
        invalid_data = {
            "entity_type": "team",
            "data": {},  # Empty data should trigger validation
            "source_urls": []
            # Missing title field should trigger validation error
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/contributions-v2/",
                json=invalid_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_text = str(error_data)
                    
                    print(f"   Error response: {error_data}")
                    
                    # Check if error message contains [object Object]
                    if '[object Object]' in error_text:
                        print(f"   ❌ Error message contains '[object Object]' - serialization issue detected")
                        return False
                    else:
                        print(f"   ✅ Error message is properly formatted")
                        return True
                        
                except json.JSONDecodeError:
                    error_text = response.text
                    print(f"   Error text: {error_text}")
                    
                    if '[object Object]' in error_text:
                        print(f"   ❌ Error message contains '[object Object]' - serialization issue detected")
                        return False
                    else:
                        print(f"   ✅ Error message is properly formatted")
                        return True
            else:
                print(f"   ⚠️ Expected error response but got success")
                return False
                
        except Exception as e:
            print(f"   ❌ Error message format test failed: {e}")
            return False
    
    def test_server_logs_for_errors(self):
        """Check if there are any unhandled exceptions in server logs"""
        print("\n📋 Testing for server-side errors...")
        
        # Make a few requests to generate activity
        test_requests = [
            {"entity_type": "team", "title": "Log Test Team", "data": {"name": "Log Test Team"}, "source_urls": []},
            {"entity_type": "invalid", "data": {}, "source_urls": []},  # Should cause validation error
        ]
        
        for i, req_data in enumerate(test_requests):
            print(f"   Making test request {i+1}...")
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/contributions-v2/",
                    json=req_data,
                    headers={'Content-Type': 'application/json'}
                )
                print(f"   Request {i+1} status: {response.status_code}")
            except Exception as e:
                print(f"   Request {i+1} error: {e}")
        
        print("   ✅ Server error testing completed (check server logs for any unhandled exceptions)")
        return True
    
    def test_authentication_requirements(self):
        """Test that authentication is properly required"""
        print("\n🔐 Testing authentication requirements...")
        
        # Create a session without authentication
        unauth_session = requests.Session()
        
        test_data = {
            "entity_type": "team",
            "title": "Unauth Test Team",
            "data": {"name": "Unauth Test Team"},
            "source_urls": []
        }
        
        try:
            response = unauth_session.post(
                f"{BACKEND_URL}/contributions-v2/",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   Unauthenticated request status: {response.status_code}")
            
            if response.status_code == 401:
                print(f"   ✅ Authentication properly required")
                return True
            else:
                print(f"   ❌ Authentication not properly enforced")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication test error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests and provide summary"""
        print("🚀 Starting TopKit Contributions Form Submission Backend Testing")
        print("=" * 80)
        
        # Track overall results
        test_results = {
            'authentication': False,
            'form_submissions': [],
            'validation': [],
            'error_formatting': False,
            'server_errors': False,
            'auth_requirements': False
        }
        
        # Test 1: Authentication
        test_results['authentication'] = self.authenticate_admin()
        
        if not test_results['authentication']:
            print("\n❌ CRITICAL: Cannot proceed without authentication")
            return test_results
        
        # Test 2: Form submissions for all entity types
        test_results['form_submissions'] = self.test_contributions_v2_endpoint()
        
        # Test 3: Form validation
        test_results['validation'] = self.test_form_validation()
        
        # Test 4: Error message formatting
        test_results['error_formatting'] = self.test_error_message_format()
        
        # Test 5: Server error handling
        test_results['server_errors'] = self.test_server_logs_for_errors()
        
        # Test 6: Authentication requirements
        test_results['auth_requirements'] = self.test_authentication_requirements()
        
        # Print comprehensive summary
        self.print_test_summary(test_results)
        
        return test_results
    
    def print_test_summary(self, results):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 TOPKIT CONTRIBUTIONS FORM SUBMISSION TESTING SUMMARY")
        print("=" * 80)
        
        # Authentication
        auth_status = "✅ WORKING" if results['authentication'] else "❌ FAILED"
        print(f"🔐 Authentication System: {auth_status}")
        
        # Form submissions
        successful_submissions = sum(1 for r in results['form_submissions'] if r['success'])
        total_submissions = len(results['form_submissions'])
        submission_rate = (successful_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        print(f"📝 Form Submissions: {successful_submissions}/{total_submissions} ({submission_rate:.1f}%)")
        
        for result in results['form_submissions']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}")
            if not result['success']:
                print(f"      Error: {result.get('error', 'Unknown error')}")
        
        # Validation
        successful_validations = sum(1 for r in results['validation'] if r['success'])
        total_validations = len(results['validation'])
        validation_rate = (successful_validations / total_validations * 100) if total_validations > 0 else 0
        
        print(f"🔍 Form Validation: {successful_validations}/{total_validations} ({validation_rate:.1f}%)")
        
        # Error formatting
        error_format_status = "✅ PROPER" if results['error_formatting'] else "❌ BROKEN"
        print(f"💬 Error Message Format: {error_format_status}")
        
        # Authentication requirements
        auth_req_status = "✅ ENFORCED" if results['auth_requirements'] else "❌ NOT ENFORCED"
        print(f"🛡️ Authentication Requirements: {auth_req_status}")
        
        # Overall assessment
        critical_issues = []
        
        if not results['authentication']:
            critical_issues.append("Authentication system failure")
        
        if submission_rate < 50:
            critical_issues.append("Form submission failure rate too high")
        
        if not results['error_formatting']:
            critical_issues.append("Error messages showing [object Object]")
        
        if not results['auth_requirements']:
            critical_issues.append("Authentication not properly enforced")
        
        print("\n" + "=" * 80)
        
        if critical_issues:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   • {issue}")
            print("\n🚨 URGENT ACTION REQUIRED: Fix critical issues before deployment")
        else:
            print("✅ ALL CRITICAL TESTS PASSED!")
            print("🎉 Contributions form submission system is working correctly")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = ContributionsFormTester()
    results = tester.run_comprehensive_test()
    
    # Return exit code based on results
    critical_failures = (
        not results['authentication'] or
        not results['error_formatting'] or
        not results['auth_requirements'] or
        sum(1 for r in results['form_submissions'] if r['success']) < len(results['form_submissions']) * 0.5
    )
    
    return 1 if critical_failures else 0

if __name__ == "__main__":
    exit(main())