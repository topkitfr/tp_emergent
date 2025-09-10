#!/usr/bin/env python3
"""
Want List "[object Object]" Error Investigation
Testing the POST /api/personal-kits endpoint with collection_type: "wanted" 
to identify the root cause of the "[object Object]" error when users try to add items to their want list.

Investigation Focus:
1. Test POST /api/personal-kits endpoint with collection_type: "wanted"
2. Check actual error response from backend
3. Identify if error is backend validation, authentication, database, or frontend handling
4. Test with user credentials: steinmetzlivio@gmail.com / T0p_Mdp_1288*
5. Test with minimal data for wanted collection
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"

# Test credentials
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

class WantListErrorInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate_user(self) -> bool:
        """Authenticate user and get JWT token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"Successfully authenticated user: {user_info.get('name', 'Unknown')} (ID: {self.user_id})",
                    {"user_info": user_info, "token_length": len(self.user_token) if self.user_token else 0}
                )
                
                # Set authorization header for future requests
                self.session.headers.update({"Authorization": f"Bearer {self.user_token}"})
                return True
            else:
                self.log_result(
                    "User Authentication", 
                    False, 
                    f"Authentication failed with status {response.status_code}",
                    {"response": response.text, "status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_available_reference_kits(self) -> List[Dict]:
        """Get available reference kits from vestiaire"""
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                kits = response.json()
                self.log_result(
                    "Get Available Reference Kits", 
                    True, 
                    f"Found {len(kits)} reference kits available",
                    {"kit_count": len(kits), "first_kit": kits[0] if kits else None}
                )
                return kits
            else:
                self.log_result(
                    "Get Available Reference Kits", 
                    False, 
                    f"Failed to get reference kits: {response.status_code}",
                    {"response": response.text}
                )
                return []
                
        except Exception as e:
            self.log_result("Get Available Reference Kits", False, f"Error: {str(e)}")
            return []
    
    def test_add_to_wanted_minimal_data(self, reference_kit_id: str) -> Dict:
        """Test adding to wanted collection with minimal data"""
        try:
            # Test with minimal data as specified in review request
            minimal_data = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "wanted"
            }
            
            print(f"\n🔍 Testing POST /api/personal-kits with minimal data:")
            print(f"   Data: {json.dumps(minimal_data, indent=2)}")
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=minimal_data)
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"   Response Body: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response Body (raw): {response.text}")
                response_data = {"raw_response": response.text}
            
            if response.status_code == 200 or response.status_code == 201:
                self.log_result(
                    "Add to Wanted - Minimal Data", 
                    True, 
                    "Successfully added to wanted collection with minimal data",
                    {"request_data": minimal_data, "response": response_data}
                )
                return {"success": True, "data": response_data}
            else:
                self.log_result(
                    "Add to Wanted - Minimal Data", 
                    False, 
                    f"Failed to add to wanted collection: HTTP {response.status_code}",
                    {
                        "request_data": minimal_data, 
                        "response": response_data,
                        "status_code": response.status_code,
                        "error_analysis": self.analyze_error_response(response_data)
                    }
                )
                return {"success": False, "error": response_data, "status_code": response.status_code}
                
        except Exception as e:
            error_details = {
                "exception": str(e),
                "exception_type": type(e).__name__,
                "request_data": minimal_data
            }
            self.log_result("Add to Wanted - Minimal Data", False, f"Exception occurred: {str(e)}", error_details)
            return {"success": False, "exception": str(e)}
    
    def test_add_to_wanted_with_size(self, reference_kit_id: str) -> Dict:
        """Test adding to wanted collection with size field"""
        try:
            # Test with size field added
            data_with_size = {
                "reference_kit_id": reference_kit_id,
                "collection_type": "wanted",
                "size": "M"
            }
            
            print(f"\n🔍 Testing POST /api/personal-kits with size field:")
            print(f"   Data: {json.dumps(data_with_size, indent=2)}")
            
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=data_with_size)
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            if response.status_code == 200 or response.status_code == 201:
                self.log_result(
                    "Add to Wanted - With Size", 
                    True, 
                    "Successfully added to wanted collection with size",
                    {"request_data": data_with_size, "response": response_data}
                )
                return {"success": True, "data": response_data}
            else:
                self.log_result(
                    "Add to Wanted - With Size", 
                    False, 
                    f"Failed to add to wanted collection: HTTP {response.status_code}",
                    {
                        "request_data": data_with_size, 
                        "response": response_data,
                        "status_code": response.status_code
                    }
                )
                return {"success": False, "error": response_data, "status_code": response.status_code}
                
        except Exception as e:
            self.log_result("Add to Wanted - With Size", False, f"Exception occurred: {str(e)}")
            return {"success": False, "exception": str(e)}
    
    def analyze_error_response(self, response_data: Dict) -> Dict:
        """Analyze error response to identify the root cause"""
        analysis = {
            "error_type": "unknown",
            "likely_cause": "unknown",
            "frontend_serialization_issue": False
        }
        
        if isinstance(response_data, dict):
            # Check for validation errors
            if "detail" in response_data:
                detail = response_data["detail"]
                if isinstance(detail, list):
                    analysis["error_type"] = "validation_error"
                    analysis["likely_cause"] = "Pydantic validation failed - missing required fields"
                    analysis["validation_errors"] = detail
                elif isinstance(detail, str):
                    analysis["error_type"] = "string_error"
                    analysis["likely_cause"] = detail
                else:
                    analysis["error_type"] = "object_error"
                    analysis["likely_cause"] = "Backend returning object that frontend can't serialize"
                    analysis["frontend_serialization_issue"] = True
            
            # Check for authentication errors
            if response_data.get("detail") == "Authentication required":
                analysis["error_type"] = "authentication_error"
                analysis["likely_cause"] = "Invalid or missing JWT token"
            
            # Check for database errors
            if "database" in str(response_data).lower() or "mongo" in str(response_data).lower():
                analysis["error_type"] = "database_error"
                analysis["likely_cause"] = "Database connection or query issue"
        
        return analysis
    
    def test_get_wanted_collections(self) -> Dict:
        """Test getting user's wanted collections"""
        try:
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=wanted")
            
            if response.status_code == 200:
                collections = response.json()
                self.log_result(
                    "Get Wanted Collections", 
                    True, 
                    f"Successfully retrieved {len(collections)} wanted items",
                    {"collection_count": len(collections), "collections": collections[:2]}  # Show first 2
                )
                return {"success": True, "collections": collections}
            else:
                try:
                    error_data = response.json()
                except:
                    error_data = {"raw_response": response.text}
                
                self.log_result(
                    "Get Wanted Collections", 
                    False, 
                    f"Failed to get wanted collections: HTTP {response.status_code}",
                    {"response": error_data, "status_code": response.status_code}
                )
                return {"success": False, "error": error_data}
                
        except Exception as e:
            self.log_result("Get Wanted Collections", False, f"Exception occurred: {str(e)}")
            return {"success": False, "exception": str(e)}
    
    def test_authentication_validity(self) -> bool:
        """Test if authentication token is still valid"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/profile/public-info")
            
            if response.status_code == 200:
                profile = response.json()
                self.log_result(
                    "Authentication Validity Check", 
                    True, 
                    "JWT token is valid and working",
                    {"profile": profile}
                )
                return True
            else:
                self.log_result(
                    "Authentication Validity Check", 
                    False, 
                    f"Token validation failed: HTTP {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication Validity Check", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_investigation(self):
        """Run comprehensive investigation of the want list error"""
        print("🚨 WANT LIST '[object Object]' ERROR INVESTIGATION STARTING")
        print("=" * 80)
        
        # Step 1: Authenticate user
        if not self.authenticate_user():
            print("❌ Cannot proceed without authentication")
            return
        
        # Step 2: Verify token is working
        if not self.test_authentication_validity():
            print("❌ Token validation failed")
            return
        
        # Step 3: Get available reference kits
        reference_kits = self.get_available_reference_kits()
        if not reference_kits:
            print("❌ No reference kits available for testing")
            return
        
        # Use first available reference kit for testing
        test_kit = reference_kits[0]
        reference_kit_id = test_kit.get("id")
        
        print(f"\n🎯 Using reference kit for testing:")
        print(f"   ID: {reference_kit_id}")
        print(f"   Kit Info: {test_kit.get('master_jersey_info', {})}")
        
        # Step 4: Test adding to wanted with minimal data (as per review request)
        print(f"\n📝 TESTING MINIMAL DATA (as specified in review request)")
        minimal_result = self.test_add_to_wanted_minimal_data(reference_kit_id)
        
        # Step 5: Test adding to wanted with size field
        print(f"\n📝 TESTING WITH SIZE FIELD")
        size_result = self.test_add_to_wanted_with_size(reference_kit_id)
        
        # Step 6: Check current wanted collections
        print(f"\n📝 CHECKING CURRENT WANTED COLLECTIONS")
        collections_result = self.test_get_wanted_collections()
        
        # Step 7: Summary and analysis
        self.print_investigation_summary(minimal_result, size_result, collections_result)
    
    def print_investigation_summary(self, minimal_result: Dict, size_result: Dict, collections_result: Dict):
        """Print comprehensive investigation summary"""
        print("\n" + "=" * 80)
        print("🔍 INVESTIGATION SUMMARY - '[object Object]' ERROR ANALYSIS")
        print("=" * 80)
        
        # Authentication Status
        auth_status = "✅ WORKING" if self.user_token else "❌ FAILED"
        print(f"Authentication: {auth_status}")
        if self.user_token:
            print(f"   User ID: {self.user_id}")
            print(f"   Token Length: {len(self.user_token)} characters")
        
        # API Endpoint Tests
        print(f"\nAPI Endpoint Tests:")
        print(f"   Minimal Data Test: {'✅ SUCCESS' if minimal_result.get('success') else '❌ FAILED'}")
        print(f"   With Size Test: {'✅ SUCCESS' if size_result.get('success') else '❌ FAILED'}")
        print(f"   Get Collections Test: {'✅ SUCCESS' if collections_result.get('success') else '❌ FAILED'}")
        
        # Error Analysis
        print(f"\nError Analysis:")
        if not minimal_result.get('success'):
            error_info = minimal_result.get('error', {})
            status_code = minimal_result.get('status_code', 'Unknown')
            print(f"   HTTP Status Code: {status_code}")
            print(f"   Error Response: {json.dumps(error_info, indent=4)}")
            
            if 'error_analysis' in minimal_result.get('details', {}):
                analysis = minimal_result['details']['error_analysis']
                print(f"   Error Type: {analysis.get('error_type', 'unknown')}")
                print(f"   Likely Cause: {analysis.get('likely_cause', 'unknown')}")
                print(f"   Frontend Serialization Issue: {analysis.get('frontend_serialization_issue', False)}")
        
        # Root Cause Identification
        print(f"\n🎯 ROOT CAUSE IDENTIFICATION:")
        if minimal_result.get('success'):
            print("   ✅ Backend API is working correctly")
            print("   ✅ No '[object Object]' error detected in backend")
            print("   🔍 Issue is likely in frontend error handling")
        else:
            status_code = minimal_result.get('status_code')
            if status_code == 400:
                print("   🚨 Backend validation error (400 Bad Request)")
                print("   🔍 Missing required fields or invalid data format")
            elif status_code == 401:
                print("   🚨 Authentication error (401 Unauthorized)")
                print("   🔍 Invalid or expired JWT token")
            elif status_code == 422:
                print("   🚨 Pydantic validation error (422 Unprocessable Entity)")
                print("   🔍 Data doesn't match expected model schema")
            elif status_code == 500:
                print("   🚨 Server error (500 Internal Server Error)")
                print("   🔍 Database or backend processing issue")
            else:
                print(f"   🚨 Unexpected error (HTTP {status_code})")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if minimal_result.get('success'):
            print("   1. Check frontend addToWantedDirectly function error handling")
            print("   2. Verify frontend properly displays backend success responses")
            print("   3. Check if frontend is trying to serialize response objects incorrectly")
        else:
            error_details = minimal_result.get('details', {})
            if 'validation_errors' in error_details.get('error_analysis', {}):
                print("   1. Fix missing required fields in frontend request")
                print("   2. Check PersonalKit model requirements in backend")
                print("   3. Ensure frontend sends all required fields for 'wanted' collection")
            else:
                print("   1. Check backend logs for detailed error information")
                print("   2. Verify database connectivity and data integrity")
                print("   3. Test with different reference kit IDs")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the investigation"""
    investigator = WantListErrorInvestigator()
    investigator.run_comprehensive_investigation()
    
    # Print final test results summary
    print(f"\n📊 FINAL TEST RESULTS:")
    passed = sum(1 for result in investigator.test_results if result['success'])
    total = len(investigator.test_results)
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total*100):.1f}%" if total > 0 else "   No tests run")
    
    # Return exit code based on results
    if total == 0:
        return 1  # No tests run
    elif passed == total:
        return 0  # All tests passed
    else:
        return 1  # Some tests failed

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)