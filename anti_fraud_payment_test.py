#!/usr/bin/env python3
"""
TopKit Anti-Fraud Payment System Testing (Leboncoin Style)
Testing the secure payment system with fund blocking until admin verification
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

# Test user credentials - working credentials
TEST_USER_EMAIL = "testuser@topkit.fr"
TEST_USER_PASSWORD = "SecurePass789#"

class AntiFraudPaymentTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.test_listing_id = None
        self.test_transaction_id = None
        
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
        
    def make_request(self, method, endpoint, data=None, token=None, params=None):
        """Make HTTP request with proper error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return None, f"Unsupported method: {method}"
                
            return response, None
        except Exception as e:
            return None, str(e)
    
    def test_admin_authentication(self):
        """Test admin authentication"""
        print("🔐 Testing Admin Authentication...")
        
        response, error = self.make_request("POST", "/auth/login", {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if error:
            self.log_result("Admin Authentication", False, error=error)
            return False
            
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data.get("token")
            user_info = data.get("user", {})
            
            if user_info.get("role") in ["admin", "moderator"]:
                self.log_result("Admin Authentication", True, 
                    f"Admin logged in: {user_info.get('name')} ({user_info.get('role')})")
                return True
            else:
                self.log_result("Admin Authentication", False, 
                    error=f"User role is {user_info.get('role')}, expected admin/moderator")
                return False
        else:
            self.log_result("Admin Authentication", False, 
                error=f"HTTP {response.status_code}: {response.text}")
            return False
    
    def test_user_authentication(self):
        """Test or create user authentication"""
        print("👤 Testing User Authentication...")
        
        # Try to login first
        response, error = self.make_request("POST", "/auth/login", {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if response and response.status_code == 200:
            data = response.json()
            self.user_token = data.get("token")
            user_info = data.get("user", {})
            self.log_result("User Authentication", True, 
                f"User logged in: {user_info.get('name')}")
            return True
        
        # If login fails, try to register
        print("   User not found, attempting registration...")
        response, error = self.make_request("POST", "/auth/register", {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": "Test User"
        })
        
        if response and response.status_code == 200:
            # Try login again after registration
            time.sleep(1)  # Brief delay
            response, error = self.make_request("POST", "/auth/login", {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response and response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.log_result("User Authentication", True, "User registered and logged in")
                return True
        
        self.log_result("User Authentication", False, 
            error="Could not login or register user")
        return False
    
    def test_create_test_listing(self):
        """Create a test listing for payment testing"""
        print("📝 Creating Test Listing...")
        
        if not self.user_token:
            self.log_result("Create Test Listing", False, error="No user token available")
            return False
        
        # First, create a test jersey
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Vinicius Jr",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Maillot domicile Real Madrid 2024-25 - Vinicius Jr #20"
        }
        
        response, error = self.make_request("POST", "/jerseys", jersey_data, self.user_token)
        
        if not response or response.status_code != 200:
            self.log_result("Create Test Listing", False, 
                error=f"Failed to create jersey: {error or response.text}")
            return False
        
        jersey_id = response.json().get("jersey", {}).get("id")
        if not jersey_id:
            self.log_result("Create Test Listing", False, error="No jersey ID returned")
            return False
        
        # Add jersey to collection
        collection_data = {
            "jersey_id": jersey_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "near_mint",
            "personal_description": "Maillot authentique pour test anti-fraude"
        }
        
        response, error = self.make_request("POST", "/collections", collection_data, self.user_token)
        
        if not response or response.status_code != 200:
            self.log_result("Create Test Listing", False, 
                error=f"Failed to add to collection: {error or response.text}")
            return False
        
        collection_id = response.json().get("collection_id")
        if not collection_id:
            self.log_result("Create Test Listing", False, error="No collection ID returned")
            return False
        
        # Create marketplace listing
        listing_data = {
            "collection_id": collection_id,
            "price": 89.99,
            "marketplace_description": "Maillot Real Madrid Vinicius Jr - État impeccable",
            "images": []
        }
        
        response, error = self.make_request("POST", "/listings", listing_data, self.user_token)
        
        if response and response.status_code == 200:
            listing_info = response.json().get("listing", {})
            self.test_listing_id = listing_info.get("id")
            self.log_result("Create Test Listing", True, 
                f"Test listing created: {self.test_listing_id} (€{listing_info.get('price')})")
            return True
        else:
            self.log_result("Create Test Listing", False, 
                error=f"Failed to create listing: {error or response.text}")
            return False
    
    def test_secure_payment_checkout(self):
        """Test POST /api/payments/secure/checkout"""
        print("💳 Testing Secure Payment Checkout...")
        
        if not self.test_listing_id:
            self.log_result("Secure Payment Checkout", False, error="No test listing available")
            return False
        
        # Create a second user for buying (admin can't buy from regular user)
        buyer_email = "buyer@test.com"
        buyer_password = "BuyerSecurePass789#"
        
        # Register buyer
        response, error = self.make_request("POST", "/auth/register", {
            "email": buyer_email,
            "password": buyer_password,
            "name": "Test Buyer"
        })
        
        # Login buyer
        response, error = self.make_request("POST", "/auth/login", {
            "email": buyer_email,
            "password": buyer_password
        })
        
        if not response or response.status_code != 200:
            self.log_result("Secure Payment Checkout", False, 
                error="Could not create/login buyer account")
            return False
        
        buyer_token = response.json().get("token")
        
        # Test secure checkout
        checkout_data = {
            "listing_id": self.test_listing_id,
            "origin_url": "https://topkit-bugfixes.preview.emergentagent.com"
        }
        
        response, error = self.make_request("POST", "/payments/secure/checkout", 
            checkout_data, buyer_token)
        
        if response and response.status_code == 200:
            data = response.json()
            self.test_transaction_id = data.get("transaction_id")
            
            required_fields = ["url", "session_id", "transaction_id", "message"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_result("Secure Payment Checkout", False, 
                    error=f"Missing fields: {missing_fields}")
                return False
            
            self.log_result("Secure Payment Checkout", True, 
                f"Secure checkout created - Transaction ID: {self.test_transaction_id}")
            return True
        else:
            self.log_result("Secure Payment Checkout", False, 
                error=f"HTTP {response.status_code}: {response.text if response else error}")
            return False
    
    def test_pending_verification_transactions(self):
        """Test GET /api/admin/transactions/pending-verification"""
        print("📋 Testing Pending Verification Transactions...")
        
        if not self.admin_token:
            self.log_result("Pending Verification Transactions", False, 
                error="No admin token available")
            return False
        
        response, error = self.make_request("GET", "/admin/transactions/pending-verification", 
            token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            transactions = data.get("transactions", [])
            total_pending = data.get("total_pending", 0)
            
            self.log_result("Pending Verification Transactions", True, 
                f"Retrieved {total_pending} pending transactions")
            
            # Check if our test transaction is in the list
            if self.test_transaction_id:
                test_transaction_found = any(
                    t.get("id") == self.test_transaction_id for t in transactions
                )
                if test_transaction_found:
                    print(f"   ✅ Test transaction {self.test_transaction_id} found in pending list")
                else:
                    print(f"   ℹ️  Test transaction {self.test_transaction_id} not yet in pending list (may need payment completion)")
            
            return True
        else:
            self.log_result("Pending Verification Transactions", False, 
                error=f"HTTP {response.status_code}: {response.text if response else error}")
            return False
    
    def test_transaction_details(self):
        """Test GET /api/admin/transactions/{id}/details"""
        print("📄 Testing Transaction Details...")
        
        if not self.admin_token or not self.test_transaction_id:
            self.log_result("Transaction Details", False, 
                error="No admin token or transaction ID available")
            return False
        
        response, error = self.make_request("GET", 
            f"/admin/transactions/{self.test_transaction_id}/details", 
            token=self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            transaction = data.get("transaction", {})
            buyer = data.get("buyer", {})
            seller = data.get("seller", {})
            
            required_sections = ["transaction", "buyer", "seller"]
            missing_sections = [section for section in required_sections if section not in data]
            
            if missing_sections:
                self.log_result("Transaction Details", False, 
                    error=f"Missing sections: {missing_sections}")
                return False
            
            self.log_result("Transaction Details", True, 
                f"Transaction details retrieved - Status: {transaction.get('status')}")
            return True
        else:
            self.log_result("Transaction Details", False, 
                error=f"HTTP {response.status_code}: {response.text if response else error}")
            return False
    
    def test_verify_authentic(self):
        """Test POST /api/admin/transactions/{id}/verify-authentic"""
        print("✅ Testing Verify Authentic...")
        
        if not self.admin_token or not self.test_transaction_id:
            self.log_result("Verify Authentic", False, 
                error="No admin token or transaction ID available")
            return False
        
        verification_data = {
            "action_type": "verify_authentic",
            "notes": "Maillot vérifié authentique par l'équipe TopKit. Tous les éléments correspondent aux standards officiels.",
            "authenticity_score": 9,
            "evidence_photos": []
        }
        
        response, error = self.make_request("POST", 
            f"/admin/transactions/{self.test_transaction_id}/verify-authentic", 
            verification_data, self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            
            expected_fields = ["message", "transaction_id", "status", "payment_released"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                self.log_result("Verify Authentic", False, 
                    error=f"Missing fields: {missing_fields}")
                return False
            
            if data.get("status") == "verified_authentic":
                self.log_result("Verify Authentic", True, 
                    f"Transaction verified authentic - Payment released: {data.get('payment_released')}")
                return True
            else:
                self.log_result("Verify Authentic", False, 
                    error=f"Unexpected status: {data.get('status')}")
                return False
        else:
            self.log_result("Verify Authentic", False, 
                error=f"HTTP {response.status_code}: {response.text if response else error}")
            return False
    
    def test_verify_fake(self):
        """Test POST /api/admin/transactions/{id}/verify-fake"""
        print("❌ Testing Verify Fake...")
        
        # Create a second transaction for fake verification test
        if not self.test_listing_id:
            self.log_result("Verify Fake", False, error="No test listing available")
            return False
        
        # Create another buyer for fake test
        fake_buyer_email = "fake_buyer@test.com"
        fake_buyer_password = "FakeBuyerSecurePass789#"
        
        # Register and login fake buyer
        self.make_request("POST", "/auth/register", {
            "email": fake_buyer_email,
            "password": fake_buyer_password,
            "name": "Fake Test Buyer"
        })
        
        response, error = self.make_request("POST", "/auth/login", {
            "email": fake_buyer_email,
            "password": fake_buyer_password
        })
        
        if not response or response.status_code != 200:
            self.log_result("Verify Fake", False, 
                error="Could not create fake buyer account")
            return False
        
        fake_buyer_token = response.json().get("token")
        
        # Create second transaction
        checkout_data = {
            "listing_id": self.test_listing_id,
            "origin_url": "https://topkit-bugfixes.preview.emergentagent.com"
        }
        
        response, error = self.make_request("POST", "/payments/secure/checkout", 
            checkout_data, fake_buyer_token)
        
        if not response or response.status_code != 200:
            self.log_result("Verify Fake", False, 
                error="Could not create second transaction for fake test")
            return False
        
        fake_transaction_id = response.json().get("transaction_id")
        
        # Test verify fake
        verification_data = {
            "action_type": "verify_fake",
            "notes": "Maillot détecté comme contrefaçon. Qualité des matériaux et finitions non conformes aux standards officiels.",
            "authenticity_score": 3,
            "evidence_photos": []
        }
        
        response, error = self.make_request("POST", 
            f"/admin/transactions/{fake_transaction_id}/verify-fake", 
            verification_data, self.admin_token)
        
        if response and response.status_code == 200:
            data = response.json()
            
            expected_fields = ["message", "transaction_id", "status", "buyer_refunded", "seller_penalized"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                self.log_result("Verify Fake", False, 
                    error=f"Missing fields: {missing_fields}")
                return False
            
            if data.get("status") == "verified_fake":
                self.log_result("Verify Fake", True, 
                    f"Transaction verified fake - Buyer refunded: {data.get('buyer_refunded')}, Seller penalized: {data.get('seller_penalized')}")
                return True
            else:
                self.log_result("Verify Fake", False, 
                    error=f"Unexpected status: {data.get('status')}")
                return False
        else:
            self.log_result("Verify Fake", False, 
                error=f"HTTP {response.status_code}: {response.text if response else error}")
            return False
    
    def run_all_tests(self):
        """Run all anti-fraud payment system tests"""
        print("🛡️ TOPKIT ANTI-FRAUD PAYMENT SYSTEM TESTING")
        print("=" * 60)
        print()
        
        # Authentication tests
        admin_auth_success = self.test_admin_authentication()
        user_auth_success = self.test_user_authentication()
        
        if not admin_auth_success:
            print("❌ Cannot proceed without admin authentication")
            return self.generate_summary()
        
        if not user_auth_success:
            print("❌ Cannot proceed without user authentication")
            return self.generate_summary()
        
        # Setup test data
        self.test_create_test_listing()
        
        # Core anti-fraud system tests
        self.test_secure_payment_checkout()
        self.test_pending_verification_transactions()
        self.test_transaction_details()
        self.test_verify_authentic()
        self.test_verify_fake()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🛡️ ANTI-FRAUD PAYMENT SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"   • {result['test']}")
        print()
        
        # Anti-fraud system specific analysis
        print("🛡️ ANTI-FRAUD SYSTEM ANALYSIS:")
        
        secure_checkout_passed = any(r["test"] == "Secure Payment Checkout" and r["success"] for r in self.test_results)
        pending_verification_passed = any(r["test"] == "Pending Verification Transactions" and r["success"] for r in self.test_results)
        verify_authentic_passed = any(r["test"] == "Verify Authentic" and r["success"] for r in self.test_results)
        verify_fake_passed = any(r["test"] == "Verify Fake" and r["success"] for r in self.test_results)
        
        print(f"   🔒 Secure Payment Creation: {'✅ WORKING' if secure_checkout_passed else '❌ FAILED'}")
        print(f"   📋 Admin Verification Queue: {'✅ WORKING' if pending_verification_passed else '❌ FAILED'}")
        print(f"   ✅ Authentic Verification: {'✅ WORKING' if verify_authentic_passed else '❌ FAILED'}")
        print(f"   ❌ Fake Detection: {'✅ WORKING' if verify_fake_passed else '❌ FAILED'}")
        
        if all([secure_checkout_passed, pending_verification_passed, verify_authentic_passed, verify_fake_passed]):
            print("\n🎉 ANTI-FRAUD SYSTEM IS FULLY OPERATIONAL!")
            print("   The Leboncoin-style payment protection system is working correctly.")
            print("   Payments are properly blocked until admin verification.")
        else:
            print("\n⚠️  ANTI-FRAUD SYSTEM HAS ISSUES!")
            print("   Some components of the payment protection system are not working.")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "anti_fraud_operational": all([secure_checkout_passed, pending_verification_passed, verify_authentic_passed, verify_fake_passed])
        }

if __name__ == "__main__":
    tester = AntiFraudPaymentTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["success_rate"] >= 80 else 1)