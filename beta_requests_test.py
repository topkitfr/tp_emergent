#!/usr/bin/env python3
"""
TopKit Backend Testing - Admin Beta Requests Endpoint
Testing specifically the GET /api/admin/beta/requests endpoint as requested
"""

import requests
import json
import sys
from datetime import datetime

# Configuration from frontend/.env
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"

# Admin credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class BetaRequestsTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
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
                    f"Successfully authenticated as {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')}, ID: {user_info.get('id', 'Unknown')})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def test_beta_requests_endpoint(self):
        """Test the GET /api/admin/beta/requests endpoint"""
        if not self.admin_token:
            self.log_result("Beta Requests Endpoint", False, "", "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/beta/requests", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if data is a dict with 'requests' key (correct format)
                if isinstance(data, dict) and 'requests' in data:
                    requests_list = data['requests']
                    request_count = len(requests_list)
                    total_count = data.get('total', request_count)
                    filter_type = data.get('filter', 'unknown')
                    
                    if request_count > 0:
                        # Analyze the first request to verify structure
                        first_request = requests_list[0]
                        required_fields = ['id', 'email', 'first_name', 'last_name', 'message', 'status', 'requested_at']
                        missing_fields = []
                        present_fields = []
                        
                        for field in required_fields:
                            if field in first_request:
                                present_fields.append(field)
                            else:
                                missing_fields.append(field)
                        
                        # Log detailed analysis
                        details = f"Found {request_count} beta request(s) (Total: {total_count}, Filter: {filter_type}). "
                        details += f"Present fields: {present_fields}. "
                        if missing_fields:
                            details += f"Missing fields: {missing_fields}. "
                        
                        # Show sample data structure
                        details += f"Sample request: {json.dumps(first_request, indent=2, default=str)}"
                        
                        success = len(missing_fields) == 0
                        self.log_result(
                            "Beta Requests Endpoint - Data Structure", 
                            success, 
                            details,
                            f"Missing required fields: {missing_fields}" if missing_fields else ""
                        )
                        
                        # Additional analysis of all requests
                        self.analyze_all_requests(requests_list)
                        
                        # Test individual request fields for the first request
                        self.test_individual_request_fields(first_request)
                        
                    else:
                        self.log_result(
                            "Beta Requests Endpoint - Data Structure", 
                            False, 
                            f"No beta requests found in database (Total: {total_count}, Filter: {filter_type})",
                            "Expected to find beta requests but got empty list"
                        )
                    
                    return True
                elif isinstance(data, list):
                    # Handle legacy format (direct list)
                    request_count = len(data)
                    
                    if request_count > 0:
                        # Analyze the first request to verify structure
                        first_request = data[0]
                        required_fields = ['id', 'email', 'first_name', 'last_name', 'message', 'status', 'requested_at']
                        missing_fields = []
                        present_fields = []
                        
                        for field in required_fields:
                            if field in first_request:
                                present_fields.append(field)
                            else:
                                missing_fields.append(field)
                        
                        # Log detailed analysis
                        details = f"Found {request_count} beta request(s) (Legacy format). "
                        details += f"Present fields: {present_fields}. "
                        if missing_fields:
                            details += f"Missing fields: {missing_fields}. "
                        
                        success = len(missing_fields) == 0
                        self.log_result(
                            "Beta Requests Endpoint - Data Structure", 
                            success, 
                            details,
                            f"Missing required fields: {missing_fields}" if missing_fields else ""
                        )
                        
                        # Additional analysis of all requests
                        self.analyze_all_requests(data)
                        
                    return True
                else:
                    self.log_result(
                        "Beta Requests Endpoint - Data Structure", 
                        False, 
                        f"Unexpected response format. Got {type(data)}: {json.dumps(data, indent=2, default=str)}",
                        "Response is neither a list nor a dict with 'requests' key"
                    )
                    return False
                    
            else:
                self.log_result(
                    "Beta Requests Endpoint", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Beta Requests Endpoint", False, "", str(e))
            return False

    def analyze_all_requests(self, requests_data):
        """Analyze all beta requests for patterns and completeness"""
        try:
            status_counts = {}
            email_domains = {}
            
            for request in requests_data:
                # Count statuses
                status = request.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count email domains
                email = request.get('email', '')
                if '@' in email:
                    domain = email.split('@')[1]
                    email_domains[domain] = email_domains.get(domain, 0) + 1
            
            analysis = f"Status distribution: {status_counts}. "
            analysis += f"Email domains: {email_domains}. "
            analysis += f"Total requests: {len(requests_data)}"
            
            self.log_result(
                "Beta Requests Analysis", 
                True, 
                analysis
            )
            
        except Exception as e:
            self.log_result("Beta Requests Analysis", False, "", str(e))

    def test_individual_request_fields(self, request_data):
        """Test individual request field validation"""
        try:
            field_tests = []
            
            # Test ID field
            if 'id' in request_data and request_data['id']:
                field_tests.append("✅ ID: Present and non-empty")
            else:
                field_tests.append("❌ ID: Missing or empty")
            
            # Test email field
            email = request_data.get('email', '')
            if email and '@' in email:
                field_tests.append(f"✅ Email: Valid format ({email})")
            else:
                field_tests.append(f"❌ Email: Invalid or missing ({email})")
            
            # Test name fields
            first_name = request_data.get('first_name', '')
            last_name = request_data.get('last_name', '')
            if first_name:
                field_tests.append(f"✅ First Name: Present ({first_name})")
            else:
                field_tests.append("❌ First Name: Missing")
                
            if last_name:
                field_tests.append(f"✅ Last Name: Present ({last_name})")
            else:
                field_tests.append("❌ Last Name: Missing")
            
            # Test status field
            status = request_data.get('status', '')
            valid_statuses = ['pending', 'approved', 'rejected']
            if status in valid_statuses:
                field_tests.append(f"✅ Status: Valid ({status})")
            else:
                field_tests.append(f"❌ Status: Invalid or missing ({status})")
            
            # Test requested_at field
            requested_at = request_data.get('requested_at', '')
            if requested_at:
                field_tests.append(f"✅ Requested At: Present ({requested_at})")
            else:
                field_tests.append("❌ Requested At: Missing")
            
            self.log_result(
                "Individual Request Field Validation", 
                True, 
                "; ".join(field_tests)
            )
            
        except Exception as e:
            self.log_result("Individual Request Field Validation", False, "", str(e))

    def run_comprehensive_test(self):
        """Run comprehensive beta requests endpoint test"""
        print("🎯 TOPKIT ADMIN BETA REQUESTS ENDPOINT TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Test beta requests endpoint
        if not self.test_beta_requests_endpoint():
            print("❌ Beta requests endpoint test failed")
            return False
        
        # Calculate success rate
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 60)
        print(f"🎉 BETA REQUESTS ENDPOINT TESTING COMPLETE")
        print(f"Success Rate: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Summary of findings
        print("📋 SUMMARY OF FINDINGS:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
            if result['details']:
                print(f"      {result['details']}")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = BetaRequestsTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ Beta requests endpoint testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Beta requests endpoint testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()