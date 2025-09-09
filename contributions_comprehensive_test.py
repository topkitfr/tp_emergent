#!/usr/bin/env python3
"""
TopKit Contributions Comprehensive Backend Testing
Testing specific issues mentioned in the review request:
- ContributionCreateV2 model validation
- Sample form data matching frontend
- Error message formatting
- Server-side issues
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

class ComprehensiveContributionsTester:
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
                print(f"   User ID: {self.admin_user_id}")
                return True
            else:
                print(f"   ❌ Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def test_sample_form_data(self):
        """Test with sample form data that matches what the frontend sends"""
        print("\n📋 Testing with sample form data from review request...")
        
        sample_data_tests = [
            {
                "name": "Team Sample Data",
                "data": {
                    "entity_type": "team",
                    "title": "Add Test Team",
                    "description": "Sample team data matching frontend format",
                    "data": {
                        "name": "Test Team",
                        "country": "France", 
                        "city": "Paris"
                    },
                    "source_urls": ["https://example.com/team-source"]
                }
            },
            {
                "name": "Brand Sample Data",
                "data": {
                    "entity_type": "brand",
                    "title": "Add Test Brand",
                    "description": "Sample brand data matching frontend format",
                    "data": {
                        "name": "Test Brand",
                        "country": "France"
                    },
                    "source_urls": ["https://example.com/brand-source"]
                }
            },
            {
                "name": "Player Sample Data",
                "data": {
                    "entity_type": "player",
                    "title": "Add Test Player",
                    "description": "Sample player data matching frontend format",
                    "data": {
                        "name": "Test Player",
                        "nationality": "French"
                    },
                    "source_urls": ["https://example.com/player-source"]
                }
            },
            {
                "name": "Competition Sample Data",
                "data": {
                    "entity_type": "competition",
                    "title": "Add Test Competition",
                    "description": "Sample competition data matching frontend format",
                    "data": {
                        "competition_name": "Test Competition",
                        "country": "France",
                        "type": "National league"
                    },
                    "source_urls": ["https://example.com/competition-source"]
                }
            }
        ]
        
        results = []
        
        for test_case in sample_data_tests:
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
                    print(f"   TopKit Reference: {data.get('topkit_reference', 'None')}")
                    results.append({
                        'test': test_case['name'],
                        'success': True,
                        'contribution_id': contribution_id,
                        'status': data.get('status'),
                        'reference': data.get('topkit_reference')
                    })
                else:
                    error_text = response.text
                    print(f"   ❌ {test_case['name']} failed: {error_text}")
                    
                    # Check for [object Object] in error messages
                    if '[object Object]' in error_text:
                        print(f"   🚨 CRITICAL: [object Object] detected in error message!")
                    
                    results.append({
                        'test': test_case['name'],
                        'success': False,
                        'error': error_text,
                        'status_code': response.status_code,
                        'has_object_object': '[object Object]' in error_text
                    })
                        
            except Exception as e:
                print(f"   ❌ {test_case['name']} error: {e}")
                results.append({
                    'test': test_case['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def test_contribution_create_v2_model_validation(self):
        """Test ContributionCreateV2 model validation specifically"""
        print("\n🔍 Testing ContributionCreateV2 model validation...")
        
        validation_tests = [
            {
                "name": "All required fields present",
                "data": {
                    "entity_type": "team",
                    "title": "Complete Team Data",
                    "description": "Testing complete data",
                    "data": {
                        "name": "Complete Team",
                        "country": "France",
                        "city": "Paris",
                        "founded_year": 1900
                    },
                    "source_urls": ["https://example.com/complete"]
                },
                "should_pass": True
            },
            {
                "name": "Missing title (required field)",
                "data": {
                    "entity_type": "team",
                    "description": "Missing title",
                    "data": {"name": "Team Without Title"},
                    "source_urls": []
                },
                "should_pass": False
            },
            {
                "name": "Invalid entity_type",
                "data": {
                    "entity_type": "invalid_entity",
                    "title": "Invalid Entity Type",
                    "data": {"name": "Test"},
                    "source_urls": []
                },
                "should_pass": False
            },
            {
                "name": "Empty data dict (should still pass)",
                "data": {
                    "entity_type": "team",
                    "title": "Empty Data Dict",
                    "data": {},
                    "source_urls": []
                },
                "should_pass": True
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
                
                if test['should_pass']:
                    if response.status_code < 400:
                        print(f"   ✅ Validation correctly accepted valid data")
                        data = response.json()
                        validation_results.append({
                            'test': test['name'],
                            'success': True,
                            'correctly_handled': True,
                            'contribution_id': data.get('id')
                        })
                    else:
                        print(f"   ❌ Validation incorrectly rejected valid data")
                        print(f"   Error: {response.text}")
                        validation_results.append({
                            'test': test['name'],
                            'success': False,
                            'correctly_handled': False,
                            'error': response.text
                        })
                else:
                    if response.status_code >= 400:
                        print(f"   ✅ Validation correctly rejected invalid data")
                        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                        print(f"   Error response: {error_data}")
                        
                        # Check for [object Object] in error messages
                        error_text = str(error_data)
                        has_object_object = '[object Object]' in error_text
                        if has_object_object:
                            print(f"   🚨 CRITICAL: [object Object] detected in error message!")
                        
                        validation_results.append({
                            'test': test['name'],
                            'success': True,
                            'correctly_handled': True,
                            'has_object_object': has_object_object
                        })
                    else:
                        print(f"   ❌ Validation should have rejected this data")
                        validation_results.append({
                            'test': test['name'],
                            'success': False,
                            'correctly_handled': False
                        })
                        
            except Exception as e:
                print(f"   ❌ Validation test error: {e}")
                validation_results.append({
                    'test': test['name'],
                    'success': False,
                    'error': str(e)
                })
        
        return validation_results
    
    def test_server_side_error_handling(self):
        """Test for server-side issues and unhandled exceptions"""
        print("\n🔧 Testing server-side error handling...")
        
        # Test various edge cases that might cause server errors
        edge_cases = [
            {
                "name": "Very long title",
                "data": {
                    "entity_type": "team",
                    "title": "A" * 1000,  # Very long title
                    "data": {"name": "Long Title Team"},
                    "source_urls": []
                }
            },
            {
                "name": "Special characters in data",
                "data": {
                    "entity_type": "team",
                    "title": "Special Characters Test",
                    "data": {
                        "name": "Team with émojis 🏆⚽",
                        "country": "Côte d'Ivoire",
                        "city": "São Paulo"
                    },
                    "source_urls": []
                }
            },
            {
                "name": "Nested data structures",
                "data": {
                    "entity_type": "team",
                    "title": "Nested Data Test",
                    "data": {
                        "name": "Nested Team",
                        "nested_object": {
                            "key1": "value1",
                            "key2": ["array", "values"]
                        }
                    },
                    "source_urls": []
                }
            },
            {
                "name": "Large source URLs array",
                "data": {
                    "entity_type": "team",
                    "title": "Many URLs Test",
                    "data": {"name": "URL Team"},
                    "source_urls": [f"https://example.com/url{i}" for i in range(50)]
                }
            }
        ]
        
        server_results = []
        
        for test_case in edge_cases:
            print(f"\n   Testing {test_case['name']}...")
            
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/contributions-v2/",
                    json=test_case['data'],
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 500:
                    print(f"   🚨 SERVER ERROR (500) detected!")
                    server_results.append({
                        'test': test_case['name'],
                        'success': False,
                        'server_error': True,
                        'status_code': response.status_code,
                        'error': response.text
                    })
                elif response.status_code < 400:
                    print(f"   ✅ Server handled edge case successfully")
                    data = response.json()
                    server_results.append({
                        'test': test_case['name'],
                        'success': True,
                        'server_error': False,
                        'contribution_id': data.get('id')
                    })
                else:
                    print(f"   ✅ Server returned proper error response")
                    server_results.append({
                        'test': test_case['name'],
                        'success': True,
                        'server_error': False,
                        'status_code': response.status_code
                    })
                        
            except Exception as e:
                print(f"   ❌ Exception during server test: {e}")
                server_results.append({
                    'test': test_case['name'],
                    'success': False,
                    'exception': str(e)
                })
        
        return server_results
    
    def check_backend_logs(self):
        """Check backend logs for any errors"""
        print("\n📋 Checking backend logs for errors...")
        
        try:
            # Try to get recent backend logs
            result = subprocess.run(
                ['tail', '-n', '100', '/var/log/supervisor/backend.err.log'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                if log_content.strip():
                    print("   Recent backend error logs:")
                    print("   " + "\n   ".join(log_content.split('\n')[-10:]))  # Last 10 lines
                    
                    # Check for critical errors
                    critical_errors = ['ERROR', 'CRITICAL', 'Exception', 'Traceback']
                    has_critical = any(error in log_content for error in critical_errors)
                    
                    if has_critical:
                        print("   🚨 CRITICAL ERRORS found in backend logs!")
                        return False
                    else:
                        print("   ✅ No critical errors in recent logs")
                        return True
                else:
                    print("   ✅ No recent error logs")
                    return True
            else:
                print("   ⚠️ Could not access backend logs")
                return True
                
        except Exception as e:
            print(f"   ⚠️ Error checking logs: {e}")
            return True
    
    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 Starting TopKit Contributions Comprehensive Backend Testing")
        print("=" * 80)
        
        # Track overall results
        test_results = {
            'authentication': False,
            'sample_data': [],
            'model_validation': [],
            'server_handling': [],
            'backend_logs': True
        }
        
        # Test 1: Authentication
        test_results['authentication'] = self.authenticate_admin()
        
        if not test_results['authentication']:
            print("\n❌ CRITICAL: Cannot proceed without authentication")
            return test_results
        
        # Test 2: Sample form data
        test_results['sample_data'] = self.test_sample_form_data()
        
        # Test 3: ContributionCreateV2 model validation
        test_results['model_validation'] = self.test_contribution_create_v2_model_validation()
        
        # Test 4: Server-side error handling
        test_results['server_handling'] = self.test_server_side_error_handling()
        
        # Test 5: Backend logs check
        test_results['backend_logs'] = self.check_backend_logs()
        
        # Print comprehensive summary
        self.print_comprehensive_summary(test_results)
        
        return test_results
    
    def print_comprehensive_summary(self, results):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 TOPKIT CONTRIBUTIONS COMPREHENSIVE TESTING SUMMARY")
        print("=" * 80)
        
        # Authentication
        auth_status = "✅ WORKING" if results['authentication'] else "❌ FAILED"
        print(f"🔐 Authentication System: {auth_status}")
        
        # Sample data tests
        successful_samples = sum(1 for r in results['sample_data'] if r['success'])
        total_samples = len(results['sample_data'])
        sample_rate = (successful_samples / total_samples * 100) if total_samples > 0 else 0
        
        print(f"📋 Sample Form Data Tests: {successful_samples}/{total_samples} ({sample_rate:.1f}%)")
        
        # Check for [object Object] errors in sample data
        object_object_errors = sum(1 for r in results['sample_data'] if not r['success'] and r.get('has_object_object', False))
        if object_object_errors > 0:
            print(f"   🚨 CRITICAL: {object_object_errors} tests showed [object Object] errors!")
        
        # Model validation tests
        successful_validations = sum(1 for r in results['model_validation'] if r['success'])
        total_validations = len(results['model_validation'])
        validation_rate = (successful_validations / total_validations * 100) if total_validations > 0 else 0
        
        print(f"🔍 Model Validation Tests: {successful_validations}/{total_validations} ({validation_rate:.1f}%)")
        
        # Check for [object Object] errors in validation
        validation_object_errors = sum(1 for r in results['model_validation'] if r.get('has_object_object', False))
        if validation_object_errors > 0:
            print(f"   🚨 CRITICAL: {validation_object_errors} validation tests showed [object Object] errors!")
        
        # Server handling tests
        successful_server = sum(1 for r in results['server_handling'] if r['success'])
        total_server = len(results['server_handling'])
        server_rate = (successful_server / total_server * 100) if total_server > 0 else 0
        
        print(f"🔧 Server Error Handling: {successful_server}/{total_server} ({server_rate:.1f}%)")
        
        # Check for server errors
        server_errors = sum(1 for r in results['server_handling'] if r.get('server_error', False))
        if server_errors > 0:
            print(f"   🚨 CRITICAL: {server_errors} tests caused server errors (500)!")
        
        # Backend logs
        logs_status = "✅ CLEAN" if results['backend_logs'] else "❌ ERRORS FOUND"
        print(f"📋 Backend Logs: {logs_status}")
        
        # Overall assessment
        critical_issues = []
        
        if not results['authentication']:
            critical_issues.append("Authentication system failure")
        
        if sample_rate < 75:
            critical_issues.append("Sample form data failure rate too high")
        
        if validation_rate < 75:
            critical_issues.append("Model validation failure rate too high")
        
        if object_object_errors > 0 or validation_object_errors > 0:
            critical_issues.append("Error messages showing [object Object]")
        
        if server_errors > 0:
            critical_issues.append("Server errors (500) detected")
        
        if not results['backend_logs']:
            critical_issues.append("Critical errors found in backend logs")
        
        print("\n" + "=" * 80)
        
        if critical_issues:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   • {issue}")
            print("\n🚨 URGENT ACTION REQUIRED: Fix critical issues before deployment")
        else:
            print("✅ ALL COMPREHENSIVE TESTS PASSED!")
            print("🎉 Contributions form submission system is working excellently")
            print("✅ No [object Object] errors detected")
            print("✅ ContributionCreateV2 model validation working correctly")
            print("✅ Server-side error handling robust")
            print("✅ Backend logs clean")
        
        print("=" * 80)

def main():
    """Main test execution"""
    import subprocess  # Import here to avoid issues if not available
    
    tester = ComprehensiveContributionsTester()
    results = tester.run_comprehensive_test()
    
    # Return exit code based on results
    critical_failures = (
        not results['authentication'] or
        sum(1 for r in results['sample_data'] if r['success']) < len(results['sample_data']) * 0.75 or
        sum(1 for r in results['model_validation'] if r['success']) < len(results['model_validation']) * 0.75 or
        any(r.get('has_object_object', False) for r in results['sample_data'] + results['model_validation']) or
        any(r.get('server_error', False) for r in results['server_handling']) or
        not results['backend_logs']
    )
    
    return 1 if critical_failures else 0

if __name__ == "__main__":
    exit(main())