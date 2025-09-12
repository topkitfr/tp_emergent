#!/usr/bin/env python3
"""
TopKit Email System Comprehensive Testing
=========================================

Tests the complete TopKit email system with ALL email types as requested:
1. GET /api/emails/health - Complete service health check
2. POST /api/emails/test-all-types - Test all email types (admin auth required)
3. POST /api/emails/password/reset - Password reset testing
4. POST /api/emails/newsletter/send - Newsletter sending (admin)

Email types tested:
- "basic" - Basic test email
- "jersey_submitted" - Jersey submission confirmation
- "password_reset" - Password reset
- "newsletter" - Weekly newsletter

Context: Complete Gmail SMTP email system with 27+ email types via EmailManager
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"

# Admin credentials as specified in the request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

# Test user for various scenarios
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "TopKit123!"

class TopKitEmailTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
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
                    f"Admin: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}"
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

    def authenticate_user(self):
        """Authenticate as regular user"""
        print("🔐 Authenticating as regular user...")
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.log_test(
                    "User Authentication", 
                    True, 
                    f"User: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}"
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

    def test_email_health_check(self):
        """Test GET /api/emails/health - Complete service health verification"""
        print("🏥 Testing email service health check...")
        try:
            response = requests.get(f"{BACKEND_URL}/emails/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                gmail_configured = data.get("gmail_configured", False)
                email_manager = data.get("email_manager", {})
                
                # Detailed health analysis
                health_details = []
                health_details.append(f"Status: {status}")
                health_details.append(f"Gmail Configured: {gmail_configured}")
                health_details.append(f"SMTP Server: {data.get('smtp_server')}")
                health_details.append(f"SMTP Port: {data.get('smtp_port')}")
                health_details.append(f"From Email: {data.get('from_email')}")
                
                # Email Manager status
                if email_manager:
                    health_details.append(f"Email Manager Status: {email_manager.get('status')}")
                    health_details.append(f"Total Services: {email_manager.get('total_services')}")
                    health_details.append(f"Basic Service: {email_manager.get('basic_service')}")
                    health_details.append(f"Extended Service: {email_manager.get('extended_service')}")
                    health_details.append(f"Community Service: {email_manager.get('community_service')}")
                    health_details.append(f"Marketing Service: {email_manager.get('marketing_service')}")
                
                success = status in ["healthy", "operational"] and gmail_configured
                self.log_test(
                    "Email Service Health Check",
                    success,
                    " | ".join(health_details)
                )
                return success
            else:
                self.log_test(
                    "Email Service Health Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Email Service Health Check", False, "", str(e))
            return False

    def test_all_email_types(self):
        """Test POST /api/emails/test-all-types - Test all email types with admin auth"""
        print("📧 Testing all email types...")
        
        if not self.admin_token:
            self.log_test("All Email Types Test", False, "", "Admin authentication required")
            return False
            
        try:
            # Test data for all email types
            test_data = {
                "recipient_email": ADMIN_EMAIL,  # Send to admin for testing
                "email_types": ["basic", "jersey_submitted", "password_reset", "newsletter"]
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/emails/test-all-types", 
                json=test_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", {})
                total_tests = data.get("total_tests", 0)
                successful = data.get("successful", 0)
                failed = data.get("failed", 0)
                
                # Analyze each email type result
                details = []
                details.append(f"Total Tests: {total_tests}")
                details.append(f"Successful: {successful}")
                details.append(f"Failed: {failed}")
                details.append(f"Recipient: {data.get('recipient')}")
                
                # Individual email type results
                for email_type, result in results.items():
                    status = "✅" if result.get("success") else "❌"
                    details.append(f"{email_type}: {status} {result.get('status')}")
                    if result.get("error"):
                        details.append(f"  Error: {result.get('error')}")
                
                success = successful > 0 and failed == 0
                self.log_test(
                    "All Email Types Test",
                    success,
                    " | ".join(details)
                )
                
                # Log individual email type tests
                for email_type, result in results.items():
                    self.log_test(
                        f"Email Type: {email_type}",
                        result.get("success", False),
                        f"Status: {result.get('status')}",
                        result.get("error", "")
                    )
                
                return success
            else:
                self.log_test(
                    "All Email Types Test",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("All Email Types Test", False, "", str(e))
            return False

    def test_password_reset_email(self):
        """Test POST /api/emails/password/reset - Password reset functionality"""
        print("🔑 Testing password reset email...")
        
        try:
            # Test with existing user email
            test_data = {
                "email": TEST_USER_EMAIL
            }
            
            response = requests.post(
                f"{BACKEND_URL}/emails/password/reset",
                json=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                self.log_test(
                    "Password Reset Email (Valid User)",
                    True,
                    f"Message: {message} | Email: {TEST_USER_EMAIL}"
                )
                
                # Test with non-existent email (should still return success for security)
                test_data_invalid = {
                    "email": "nonexistent@example.com"
                }
                
                response_invalid = requests.post(
                    f"{BACKEND_URL}/emails/password/reset",
                    json=test_data_invalid
                )
                
                if response_invalid.status_code == 200:
                    self.log_test(
                        "Password Reset Email (Invalid User)",
                        True,
                        "Security: No user existence disclosure"
                    )
                else:
                    self.log_test(
                        "Password Reset Email (Invalid User)",
                        False,
                        f"HTTP {response_invalid.status_code}",
                        response_invalid.text
                    )
                
                return True
            else:
                self.log_test(
                    "Password Reset Email",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Password Reset Email", False, "", str(e))
            return False

    def test_newsletter_send(self):
        """Test POST /api/emails/newsletter/send - Newsletter sending (admin only)"""
        print("📰 Testing newsletter sending...")
        
        if not self.admin_token:
            self.log_test("Newsletter Send Test", False, "", "Admin authentication required")
            return False
            
        try:
            # Newsletter data
            newsletter_data = {
                "recipient_email": ADMIN_EMAIL,  # Send to admin for testing
                "week_number": "42",
                "trend1": "Maillots rétro Manchester United en hausse",
                "trend2": "Nouveaux maillots PSG 2024/25 très demandés",
                "trend3": "Éditions limitées Real Madrid collectors",
                "new_jerseys": "156",
                "sales": "98",
                "new_members": "267",
                "football_news": "Le mercato d'hiver bat son plein avec de nombreux transferts surprenants."
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/emails/newsletter/send",
                json=newsletter_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                recipient = data.get("recipient", "")
                success = data.get("success", False)
                
                self.log_test(
                    "Newsletter Send (Individual)",
                    success,
                    f"Message: {message} | Recipient: {recipient}"
                )
                
                # Test mass newsletter (to all users) - commented out to avoid spam
                # newsletter_data_mass = newsletter_data.copy()
                # newsletter_data_mass.pop("recipient_email", None)  # Remove specific recipient
                
                return success
            else:
                self.log_test(
                    "Newsletter Send Test",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Newsletter Send Test", False, "", str(e))
            return False

    def test_jersey_submitted_email(self):
        """Test jersey submission confirmation email"""
        print("👕 Testing jersey submission email...")
        
        if not self.user_token:
            self.log_test("Jersey Submitted Email", False, "", "User authentication required")
            return False
            
        try:
            # Jersey submission data
            jersey_data = {
                "jersey_data": {
                    "team": "FC Barcelona",
                    "season": "2008-09",
                    "player": "Messi",
                    "size": "L",
                    "condition": "Excellent",
                    "description": "Maillot authentique de la saison historique du Barça"
                }
            }
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(
                f"{BACKEND_URL}/emails/jersey/submitted",
                json=jersey_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                status = data.get("status", "")
                
                self.log_test(
                    "Jersey Submitted Email",
                    True,
                    f"Message: {message} | Status: {status}"
                )
                return True
            else:
                self.log_test(
                    "Jersey Submitted Email",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Jersey Submitted Email", False, "", str(e))
            return False

    def test_individual_email_endpoints(self):
        """Test individual email endpoints"""
        print("🔍 Testing individual email endpoints...")
        
        # Test basic email sending (admin only)
        if self.admin_token:
            try:
                email_data = {
                    "to_email": ADMIN_EMAIL,
                    "subject": "Test Email TopKit",
                    "body": "Ceci est un test du système d'email TopKit.",
                    "html_body": "<h2>Test Email TopKit</h2><p>Ceci est un test du système d'email TopKit.</p>"
                }
                
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.post(
                    f"{BACKEND_URL}/emails/send",
                    json=email_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "General Email Send",
                        True,
                        f"Message: {data.get('message')} | Status: {data.get('status')}"
                    )
                else:
                    self.log_test(
                        "General Email Send",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test("General Email Send", False, "", str(e))
        
        # Test email service test endpoint (admin only)
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.post(
                    f"{BACKEND_URL}/emails/test",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Email Service Test",
                        True,
                        f"Message: {data.get('message')} | Recipient: {data.get('recipient')}"
                    )
                else:
                    self.log_test(
                        "Email Service Test",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test("Email Service Test", False, "", str(e))

    def test_different_user_scenarios(self):
        """Test with different users and scenarios"""
        print("👥 Testing different user scenarios...")
        
        # Test with different email types for different users
        if self.admin_token:
            # Test sending newsletter to specific user
            try:
                newsletter_data = {
                    "recipient_email": TEST_USER_EMAIL,
                    "week_number": "43",
                    "trend1": "Maillots vintage en forte demande",
                    "trend2": "Nouveautés Premier League",
                    "trend3": "Collections limitées disponibles",
                    "new_jerseys": "89",
                    "sales": "156",
                    "new_members": "198",
                    "football_news": "Les maillots de la Coupe du Monde deviennent des pièces de collection."
                }
                
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.post(
                    f"{BACKEND_URL}/emails/newsletter/send",
                    json=newsletter_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Newsletter to Specific User",
                        data.get("success", False),
                        f"Sent to: {data.get('recipient')}"
                    )
                else:
                    self.log_test(
                        "Newsletter to Specific User",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test("Newsletter to Specific User", False, "", str(e))

    def run_comprehensive_tests(self):
        """Run all comprehensive email system tests"""
        print("🚀 Starting TopKit Email System Comprehensive Testing")
        print("=" * 60)
        print()
        
        # Step 1: Test health check first (as requested)
        print("STEP 1: Email Service Health Check")
        print("-" * 40)
        health_ok = self.test_email_health_check()
        print()
        
        if not health_ok:
            print("⚠️  Email service health check failed. Continuing with other tests...")
            print()
        
        # Step 2: Authenticate as admin (as requested)
        print("STEP 2: Admin Authentication")
        print("-" * 40)
        admin_auth_ok = self.authenticate_admin()
        print()
        
        # Step 3: Authenticate as user for additional tests
        print("STEP 3: User Authentication")
        print("-" * 40)
        user_auth_ok = self.authenticate_user()
        print()
        
        # Step 4: Test all email types (as requested)
        print("STEP 4: Test All Email Types")
        print("-" * 40)
        if admin_auth_ok:
            self.test_all_email_types()
        else:
            self.log_test("All Email Types Test", False, "", "Admin authentication failed")
        print()
        
        # Step 5: Test individual endpoints (as requested)
        print("STEP 5: Individual Email Endpoints")
        print("-" * 40)
        self.test_password_reset_email()
        if admin_auth_ok:
            self.test_newsletter_send()
        else:
            self.log_test("Newsletter Send Test", False, "", "Admin authentication failed")
        print()
        
        # Step 6: Test jersey submission email
        print("STEP 6: Jersey Submission Email")
        print("-" * 40)
        if user_auth_ok:
            self.test_jersey_submitted_email()
        else:
            self.log_test("Jersey Submitted Email", False, "", "User authentication failed")
        print()
        
        # Step 7: Test additional email endpoints
        print("STEP 7: Additional Email Endpoints")
        print("-" * 40)
        self.test_individual_email_endpoints()
        print()
        
        # Step 8: Test different user scenarios (as requested)
        print("STEP 8: Different User Scenarios")
        print("-" * 40)
        self.test_different_user_scenarios()
        print()
        
        # Final Results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("=" * 60)
        print("🎯 TOPKIT EMAIL SYSTEM TEST RESULTS")
        print("=" * 60)
        print()
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   ✅ Passed: {self.passed_tests}")
        print(f"   ❌ Failed: {self.failed_tests}")
        print(f"   📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Group results by category
        categories = {
            "Authentication": [],
            "Health Check": [],
            "Email Types": [],
            "Individual Endpoints": [],
            "User Scenarios": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                categories["Authentication"].append(result)
            elif "Health" in test_name:
                categories["Health Check"].append(result)
            elif "Email Type" in test_name or "All Email Types" in test_name:
                categories["Email Types"].append(result)
            elif any(x in test_name for x in ["Password Reset", "Newsletter", "Jersey", "Email Send", "Email Service"]):
                categories["Individual Endpoints"].append(result)
            else:
                categories["User Scenarios"].append(result)
        
        for category, results in categories.items():
            if results:
                print(f"📋 {category.upper()}:")
                for result in results:
                    print(f"   {result['status']} {result['test']}")
                    if result['details']:
                        print(f"      Details: {result['details']}")
                    if result['error']:
                        print(f"      Error: {result['error']}")
                print()
        
        # Critical findings
        print("🔍 CRITICAL FINDINGS:")
        critical_tests = ["Email Service Health Check", "Admin Authentication", "All Email Types Test"]
        for test_name in critical_tests:
            result = next((r for r in self.test_results if r["test"] == test_name), None)
            if result:
                status = "✅ OPERATIONAL" if result["success"] else "❌ FAILED"
                print(f"   {test_name}: {status}")
        print()
        
        # Email types analysis
        email_type_results = [r for r in self.test_results if "Email Type:" in r["test"]]
        if email_type_results:
            print("📧 EMAIL TYPES ANALYSIS:")
            for result in email_type_results:
                email_type = result["test"].replace("Email Type: ", "")
                status = "✅" if result["success"] else "❌"
                print(f"   {email_type}: {status}")
            print()
        
        print("🏁 Testing completed!")
        print(f"📝 Full results logged with {len(self.test_results)} individual test cases")

def main():
    """Main testing function"""
    print("TopKit Email System Comprehensive Testing")
    print("Testing complete Gmail SMTP system with 27+ email types")
    print("Context: EmailManager with basic, extended, community, marketing services")
    print()
    
    tester = TopKitEmailTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()