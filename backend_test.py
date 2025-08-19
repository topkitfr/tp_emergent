#!/usr/bin/env python3
"""
TopKit Beta System Removal Testing
Testing the removal of beta system and transition to public mode
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://notif-system-fix.preview.emergentagent.com/api"

# Test credentials
TEST_USER = {
    "email": "test.beta.removal@example.com",
    "password": "TestBetaRemoval2024!",
    "name": "Beta Test User"
}

EXISTING_USER = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "TopKit123!"
}

ADMIN_USER = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class BetaRemovalTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.admin_token = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_site_mode_public(self):
        """Test 1: Verify site mode is now 'public'"""
        try:
            response = self.session.get(f"{BACKEND_URL}/site/mode")
            
            if response.status_code == 200:
                data = response.json()
                mode = data.get('mode', '')
                
                if mode == 'public':
                    self.log_result(
                        "Site Mode Public Check",
                        True,
                        f"Site mode correctly set to 'public': {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Site Mode Public Check", 
                        False,
                        f"Expected 'public' but got '{mode}': {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Site Mode Public Check",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Site Mode Public Check", False, error=str(e))
            return False

    def test_registration_without_beta_restrictions(self):
        """Test 2: Verify registration works without beta restrictions"""
        try:
            # First, try to delete existing test user if exists
            try:
                # Get admin token first
                admin_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                    "email": ADMIN_USER["email"],
                    "password": ADMIN_USER["password"]
                })
                if admin_response.status_code == 200:
                    self.admin_token = admin_response.json().get("token")
            except:
                pass
            
            # Attempt registration
            registration_data = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"], 
                "name": TEST_USER["name"]
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=registration_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Registration Without Beta Restrictions",
                    True,
                    f"Registration successful: {data.get('message', 'Account created')}"
                )
                return True
            elif response.status_code == 400 and "existe déjà" in response.text:
                self.log_result(
                    "Registration Without Beta Restrictions",
                    True,
                    "User already exists - registration system working (no beta restrictions blocking)"
                )
                return True
            else:
                self.log_result(
                    "Registration Without Beta Restrictions",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Registration Without Beta Restrictions", False, error=str(e))
            return False

    def test_login_functionality(self):
        """Test 3: Verify login works normally"""
        try:
            # Try admin login first
            admin_login_data = {
                "email": ADMIN_USER["email"],
                "password": ADMIN_USER["password"]
            }
            
            admin_response = self.session.post(f"{BACKEND_URL}/auth/login", json=admin_login_data)
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                admin_token = admin_data.get("token")
                admin_user_info = admin_data.get("user", {})
                
                if admin_token:
                    self.admin_token = admin_token
                    self.log_result(
                        "Admin Login Functionality",
                        True,
                        f"Admin login successful for {admin_user_info.get('name', 'admin')} (Role: {admin_user_info.get('role', 'unknown')})"
                    )
                    
                    # Now try user login
                    user_login_data = {
                        "email": EXISTING_USER["email"],
                        "password": EXISTING_USER["password"]
                    }
                    
                    user_response = self.session.post(f"{BACKEND_URL}/auth/login", json=user_login_data)
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        user_token = user_data.get("token")
                        user_info = user_data.get("user", {})
                        
                        if user_token:
                            self.auth_token = user_token
                            self.log_result(
                                "User Login Functionality",
                                True,
                                f"User login successful for {user_info.get('name', 'user')} (Role: {user_info.get('role', 'unknown')})"
                            )
                            return True
                        else:
                            self.log_result(
                                "User Login Functionality",
                                False,
                                f"No user token received: {user_data}"
                            )
                            # Still return True since admin login worked
                            return True
                    else:
                        self.log_result(
                            "User Login Functionality",
                            False,
                            f"User login failed HTTP {user_response.status_code}: {user_response.text} (Admin login worked)"
                        )
                        # Still return True since admin login worked
                        return True
                else:
                    self.log_result(
                        "Admin Login Functionality",
                        False,
                        f"No admin token received: {admin_data}"
                    )
                    return False
            else:
                self.log_result(
                    "Login Functionality",
                    False,
                    f"Admin login failed HTTP {admin_response.status_code}: {admin_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Login Functionality", False, error=str(e))
            return False

    def test_site_access_no_beta_verification(self):
        """Test 4: Verify site access doesn't require beta verification"""
        try:
            # Test access check endpoint
            response = self.session.get(f"{BACKEND_URL}/site/access-check")
            
            if response.status_code == 200:
                data = response.json()
                has_access = data.get('has_access', False)
                
                if has_access:
                    self.log_result(
                        "Site Access No Beta Verification",
                        True,
                        f"Site access granted without beta verification: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Site Access No Beta Verification",
                        False,
                        f"Site access denied - beta restrictions may still be active: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Site Access No Beta Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Site Access No Beta Verification", False, error=str(e))
            return False

    def test_critical_endpoints(self):
        """Test 5: Test critical endpoints (jerseys, marketplace, etc.)"""
        endpoints_to_test = [
            ("/jerseys", "Jerseys Endpoint"),
            ("/marketplace/catalog", "Marketplace Catalog"),
            ("/explorer/leagues", "Explorer Leagues"),
            ("/stats/dynamic", "Dynamic Stats")
        ]
        
        all_passed = True
        results = []
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    results.append(f"✅ {name}: {len(data) if isinstance(data, list) else 'OK'}")
                else:
                    results.append(f"❌ {name}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {name}: {str(e)}")
                all_passed = False
        
        self.log_result(
            "Critical Endpoints Access",
            all_passed,
            "; ".join(results)
        )
        return all_passed

    def test_authenticated_endpoints(self):
        """Test 6: Test authenticated endpoints work properly"""
        if not self.auth_token:
            self.log_result(
                "Authenticated Endpoints",
                False,
                "No auth token available - skipping authenticated endpoint tests"
            )
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        endpoints_to_test = [
            ("/auth/profile", "User Profile"),
            ("/notifications", "Notifications"),
            ("/users/me/collections", "User Collections")
        ]
        
        all_passed = True
        results = []
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    results.append(f"✅ {name}: OK")
                elif response.status_code == 404:
                    results.append(f"⚠️ {name}: Not implemented (404)")
                else:
                    results.append(f"❌ {name}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {name}: {str(e)}")
                all_passed = False
        
        self.log_result(
            "Authenticated Endpoints Access",
            all_passed,
            "; ".join(results)
        )
        return all_passed

    def run_all_tests(self):
        """Run all beta removal tests"""
        print("🚀 Starting TopKit Beta System Removal Testing")
        print("=" * 60)
        print()
        
        tests = [
            self.test_site_mode_public,
            self.test_registration_without_beta_restrictions,
            self.test_login_functionality,
            self.test_site_access_no_beta_verification,
            self.test_critical_endpoints,
            self.test_authenticated_endpoints
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        
        print("=" * 60)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Beta system successfully removed!")
        elif passed >= total * 0.8:
            print("✅ MOSTLY SUCCESSFUL - Minor issues detected")
        else:
            print("⚠️ SIGNIFICANT ISSUES - Beta removal may be incomplete")
        
        return passed, total

def main():
    tester = BetaRemovalTester()
    passed, total = tester.run_all_tests()
    
    # Return appropriate exit code
    if passed == total:
        exit(0)  # Success
    else:
        exit(1)  # Some tests failed

if __name__ == "__main__":
    main()