#!/usr/bin/env python3
"""
Gmail SMTP Email System Backend Testing
Test du système d'email Gmail SMTP nouvellement implémenté dans TopKit

Tests spécifiques:
1. GET /api/emails/health - Vérifier la santé du service d'email 
2. POST /api/emails/test - Envoyer un email de test (nécessite authentification admin)

Contexte:
- L'application utilise Gmail SMTP avec l'adresse topkitfr@gmail.com
- Le service d'email a été intégré dans les flux d'inscription et de demandes d'accès beta
- Authentification admin requise pour les tests d'email
- Les credentials Gmail SMTP sont configurés dans les variables d'environnement
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-admin.preview.emergentagent.com/api"

# Admin credentials for testing
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class GmailSMTPTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
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
            print(f"   📋 {details}")
        if error:
            print(f"   🚨 {error}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            print("🔐 Authenticating as admin...")
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {user_info.get('name', 'Admin')} (Role: {user_info.get('role', 'unknown')})"
                )
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
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
            self.log_test(
                "Admin Authentication",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_email_health_endpoint(self):
        """Test GET /api/emails/health endpoint"""
        try:
            print("🏥 Testing email service health endpoint...")
            
            response = self.session.get(f"{BACKEND_URL}/emails/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze health response
                status = data.get("status", "unknown")
                message = data.get("message", "No message")
                gmail_configured = data.get("gmail_configured", False)
                smtp_server = data.get("smtp_server", "N/A")
                smtp_port = data.get("smtp_port", "N/A")
                from_email = data.get("from_email", "N/A")
                
                # Determine if health check is successful
                is_healthy = status in ["healthy", "operational"]
                
                details = f"Status: {status}, Gmail Configured: {gmail_configured}"
                if smtp_server != "N/A":
                    details += f", SMTP: {smtp_server}:{smtp_port}, From: {from_email}"
                
                self.log_test(
                    "Email Service Health Check",
                    is_healthy,
                    details,
                    message if not is_healthy else ""
                )
                
                return is_healthy
            else:
                self.log_test(
                    "Email Service Health Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Email Service Health Check",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_email_test_endpoint(self):
        """Test POST /api/emails/test endpoint (requires admin auth)"""
        try:
            print("📧 Testing email test endpoint...")
            
            if not self.admin_token:
                self.log_test(
                    "Email Test Endpoint",
                    False,
                    "",
                    "Admin authentication required but not available"
                )
                return False
            
            response = self.session.post(f"{BACKEND_URL}/emails/test")
            
            if response.status_code == 200:
                data = response.json()
                
                message = data.get("message", "No message")
                status = data.get("status", "unknown")
                recipient = data.get("recipient", "N/A")
                
                success = status == "success"
                
                self.log_test(
                    "Email Test Endpoint",
                    success,
                    f"Status: {status}, Recipient: {recipient}, Message: {message}"
                )
                
                return success
            elif response.status_code == 403:
                self.log_test(
                    "Email Test Endpoint",
                    False,
                    "HTTP 403 - Access Forbidden",
                    "Admin authentication failed or insufficient privileges"
                )
                return False
            elif response.status_code == 401:
                self.log_test(
                    "Email Test Endpoint",
                    False,
                    "HTTP 401 - Unauthorized",
                    "Authentication token invalid or expired"
                )
                return False
            else:
                self.log_test(
                    "Email Test Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Email Test Endpoint",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_email_test_without_auth(self):
        """Test POST /api/emails/test without authentication (should fail)"""
        try:
            print("🔒 Testing email test endpoint without authentication...")
            
            # Temporarily remove auth header
            original_headers = self.session.headers.copy()
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]
            
            response = self.session.post(f"{BACKEND_URL}/emails/test")
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            # Should return 401 or 403
            if response.status_code in [401, 403]:
                self.log_test(
                    "Email Test Endpoint Security",
                    True,
                    f"Correctly rejected unauthenticated request with HTTP {response.status_code}"
                )
                return True
            else:
                self.log_test(
                    "Email Test Endpoint Security",
                    False,
                    f"Expected HTTP 401/403 but got {response.status_code}",
                    "Endpoint should require authentication"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Email Test Endpoint Security",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_email_service_configuration(self):
        """Test email service configuration validation"""
        try:
            print("⚙️ Testing email service configuration...")
            
            # Get health status to check configuration
            response = self.session.get(f"{BACKEND_URL}/emails/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required configuration fields
                required_fields = ["status", "gmail_configured"]
                optional_fields = ["smtp_server", "smtp_port", "from_email"]
                
                missing_fields = [field for field in required_fields if field not in data]
                present_optional = [field for field in optional_fields if field in data and data[field]]
                
                if not missing_fields:
                    details = f"All required fields present. Optional fields: {', '.join(present_optional)}"
                    self.log_test(
                        "Email Service Configuration",
                        True,
                        details
                    )
                    return True
                else:
                    self.log_test(
                        "Email Service Configuration",
                        False,
                        f"Missing required fields: {', '.join(missing_fields)}"
                    )
                    return False
            else:
                self.log_test(
                    "Email Service Configuration",
                    False,
                    f"HTTP {response.status_code}",
                    "Could not retrieve configuration status"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Email Service Configuration",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def run_comprehensive_tests(self):
        """Run all Gmail SMTP email system tests"""
        print("🚀 Starting Gmail SMTP Email System Testing")
        print("=" * 60)
        print()
        
        # Test sequence as requested
        tests = [
            ("Email Service Health Check", self.test_email_health_endpoint),
            ("Email Service Configuration", self.test_email_service_configuration),
            ("Admin Authentication", self.authenticate_admin),
            ("Email Test Endpoint Security", self.test_email_test_without_auth),
            ("Email Test Endpoint", self.test_email_test_endpoint),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ FAIL {test_name} - Exception: {str(e)}")
        
        # Summary
        print("=" * 60)
        print("📊 GMAIL SMTP EMAIL SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   📋 {result['details']}")
            if result["error"]:
                print(f"   🚨 {result['error']}")
        
        print()
        print("=" * 60)
        
        # Final assessment
        if success_rate >= 80:
            print("🎉 GMAIL SMTP EMAIL SYSTEM STATUS: EXCELLENT")
            print("✅ Email service is operational and ready for production")
        elif success_rate >= 60:
            print("⚠️ GMAIL SMTP EMAIL SYSTEM STATUS: GOOD")
            print("✅ Email service is mostly functional with minor issues")
        else:
            print("🚨 GMAIL SMTP EMAIL SYSTEM STATUS: NEEDS ATTENTION")
            print("❌ Email service has significant issues requiring fixes")
        
        print()
        
        # Specific findings
        health_test = next((r for r in self.test_results if "Health Check" in r["test"]), None)
        test_email = next((r for r in self.test_results if "Email Test Endpoint" in r["test"] and "Security" not in r["test"]), None)
        
        if health_test and health_test["success"]:
            print("✅ Email service health endpoint working correctly")
        
        if test_email and test_email["success"]:
            print("✅ Email test functionality working correctly")
            print("📧 Test email should have been sent to admin email")
        
        return success_rate

def main():
    """Main test execution"""
    print("Gmail SMTP Email System Backend Testing")
    print("Testing TopKit email functionality")
    print()
    
    tester = GmailSMTPTester()
    success_rate = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)

if __name__ == "__main__":
    main()