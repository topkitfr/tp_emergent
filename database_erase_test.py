#!/usr/bin/env python3
"""
TopKit Database Erasure Testing
VIDAGE COMPLET DE LA BASE DE DONNÉES - Testing complete database wipe functionality
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"admin_test_{int(time.time())}@topkit.com"
TEST_USER_PASSWORD = "admin123"
TEST_USER_NAME = "Admin Test User"

class DatabaseEraseTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def setup_authentication(self):
        """Setup authentication for admin operations"""
        try:
            # Register a test user for authentication
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("Authentication Setup", "PASS", f"Admin user registered with ID: {self.user_id}")
                    return True
                else:
                    self.log_test("Authentication Setup", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Authentication Setup", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    def check_database_state_before_erase(self):
        """Check current database state before erasure"""
        try:
            # Check jerseys
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=100")
            jerseys_count = 0
            if jerseys_response.status_code == 200:
                jerseys = jerseys_response.json()
                jerseys_count = len(jerseys)
            
            # Check listings
            listings_response = self.session.get(f"{self.base_url}/listings?limit=100")
            listings_count = 0
            if listings_response.status_code == 200:
                listings = listings_response.json()
                listings_count = len(listings)
            
            self.log_test("Database State Before Erase", "INFO", 
                         f"Found {jerseys_count} jerseys and {listings_count} listings before erasure")
            
            return {
                "jerseys_count": jerseys_count,
                "listings_count": listings_count
            }
            
        except Exception as e:
            self.log_test("Database State Before Erase", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_database_erase_endpoint(self):
        """Test DELETE /api/admin/database/erase endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Database Erase Endpoint", "FAIL", "No authentication token available")
                return False
            
            # Call the database erase endpoint
            response = self.session.delete(f"{self.base_url}/admin/database/erase")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "success" in data.get("status", ""):
                    self.log_test("Database Erase Endpoint", "PASS", 
                                f"Database erase successful: {data['message']}")
                    return True
                else:
                    self.log_test("Database Erase Endpoint", "FAIL", 
                                f"Unexpected response format: {data}")
                    return False
            elif response.status_code == 403:
                self.log_test("Database Erase Endpoint", "FAIL", 
                            "Access denied - endpoint requires proper authentication")
                return False
            else:
                self.log_test("Database Erase Endpoint", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Erase Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def verify_jerseys_empty_after_erase(self):
        """Verify GET /api/jerseys returns empty list after erase"""
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=100")
            
            if response.status_code == 200:
                jerseys = response.json()
                if len(jerseys) == 0:
                    self.log_test("Jerseys Empty After Erase", "PASS", 
                                "GET /api/jerseys returns empty list []")
                    return True
                else:
                    self.log_test("Jerseys Empty After Erase", "FAIL", 
                                f"Expected empty list, found {len(jerseys)} jerseys")
                    return False
            else:
                self.log_test("Jerseys Empty After Erase", "FAIL", 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jerseys Empty After Erase", "FAIL", f"Exception: {str(e)}")
            return False
    
    def verify_listings_empty_after_erase(self):
        """Verify GET /api/listings returns empty list after erase"""
        try:
            response = self.session.get(f"{self.base_url}/listings?limit=100")
            
            if response.status_code == 200:
                listings = response.json()
                if len(listings) == 0:
                    self.log_test("Listings Empty After Erase", "PASS", 
                                "GET /api/listings returns empty list []")
                    return True
                else:
                    self.log_test("Listings Empty After Erase", "FAIL", 
                                f"Expected empty list, found {len(listings)} listings")
                    return False
            else:
                self.log_test("Listings Empty After Erase", "FAIL", 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Listings Empty After Erase", "FAIL", f"Exception: {str(e)}")
            return False
    
    def verify_old_account_login_fails(self):
        """Verify that login with old account fails after database erase"""
        try:
            # Try to login with the account we created before erase
            # (This should fail since all users were deleted)
            login_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            # Remove current auth header for this test
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code == 400:
                # Login should fail with "Invalid credentials" since user was deleted
                self.log_test("Old Account Login Fails", "PASS", 
                            "Login with old account correctly fails after database erase")
                return True
            elif response.status_code == 200:
                self.log_test("Old Account Login Fails", "FAIL", 
                            "Old account still exists - database erase may not have worked completely")
                return False
            else:
                self.log_test("Old Account Login Fails", "FAIL", 
                            f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Old Account Login Fails", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_alternative_clear_listings_endpoint(self):
        """Test DELETE /api/admin/database/clear-listings as alternative"""
        try:
            # First create some test data to clear
            if not self.auth_token:
                self.log_test("Alternative Clear Listings", "FAIL", "No authentication token")
                return False
            
            # Create a test jersey and listing
            jersey_payload = {
                "team": "Test Team",
                "season": "2024-25",
                "player": "Test Player",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Test Brand",
                "home_away": "home",
                "league": "Test League",
                "description": "Test jersey for clear listings test",
                "images": []
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            if jersey_response.status_code != 200:
                self.log_test("Alternative Clear Listings", "FAIL", "Could not create test jersey")
                return False
            
            jersey_id = jersey_response.json()["id"]
            
            # Create a test listing
            listing_payload = {
                "jersey_id": jersey_id,
                "price": 99.99,
                "description": "Test listing for clear test",
                "images": []
            }
            
            listing_response = self.session.post(f"{self.base_url}/listings", json=listing_payload)
            if listing_response.status_code != 200:
                self.log_test("Alternative Clear Listings", "FAIL", "Could not create test listing")
                return False
            
            # Now test the clear-listings endpoint
            response = self.session.delete(f"{self.base_url}/admin/database/clear-listings")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "success" in data.get("status", ""):
                    self.log_test("Alternative Clear Listings", "PASS", 
                                f"Clear listings successful: {data['message']}")
                    return True
                else:
                    self.log_test("Alternative Clear Listings", "FAIL", 
                                f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Alternative Clear Listings", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Alternative Clear Listings", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_database_erase_without_authentication(self):
        """Test that database erase requires authentication"""
        try:
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.delete(f"{self.base_url}/admin/database/erase")
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                self.log_test("Database Erase Authentication Required", "PASS", 
                            f"Correctly requires authentication (status: {response.status_code})")
                return True
            else:
                self.log_test("Database Erase Authentication Required", "FAIL", 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Erase Authentication Required", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_complete_database_erase_test(self):
        """Run the complete database erasure test sequence"""
        print("🎯 TOPKIT DATABASE ERASURE TESTING - VIDAGE COMPLET DE LA BASE DE DONNÉES")
        print("=" * 80)
        print()
        
        # Step 1: Setup authentication
        if not self.setup_authentication():
            print("❌ CRITICAL: Could not setup authentication. Aborting test.")
            return False
        
        # Step 2: Check database state before erase
        initial_state = self.check_database_state_before_erase()
        
        # Step 3: Test authentication requirement
        self.test_database_erase_without_authentication()
        
        # Step 4: Test the main database erase endpoint
        erase_success = self.test_database_erase_endpoint()
        
        if erase_success:
            print("⏳ Waiting 3 seconds for database operations to complete...")
            time.sleep(3)
            
            # Step 5: Verify erasure worked
            jerseys_empty = self.verify_jerseys_empty_after_erase()
            listings_empty = self.verify_listings_empty_after_erase()
            old_login_fails = self.verify_old_account_login_fails()
            
            # Summary
            print("=" * 80)
            print("🎯 DATABASE ERASURE TEST SUMMARY:")
            print("=" * 80)
            
            if jerseys_empty and listings_empty and old_login_fails:
                print("✅ SUCCESS: Database completely erased!")
                print("   - All jerseys removed ✅")
                print("   - All listings removed ✅") 
                print("   - All users removed ✅")
                print("   - Database is completely clean and ready for restructuring")
                return True
            else:
                print("❌ PARTIAL SUCCESS: Database erase had issues")
                print(f"   - Jerseys empty: {'✅' if jerseys_empty else '❌'}")
                print(f"   - Listings empty: {'✅' if listings_empty else '❌'}")
                print(f"   - Users removed: {'✅' if old_login_fails else '❌'}")
                return False
        else:
            print("❌ CRITICAL: Database erase endpoint failed")
            print("🔄 Testing alternative clear-listings endpoint...")
            
            # Test alternative endpoint
            clear_success = self.test_alternative_clear_listings_endpoint()
            
            if clear_success:
                print("⚠️  Alternative endpoint worked, but manual cleanup may be needed")
                print("   Recommendation: Use clear-listings + manual user/jersey cleanup")
                return False
            else:
                print("❌ Both erase endpoints failed")
                return False

def main():
    """Main test execution"""
    tester = DatabaseEraseTest()
    success = tester.run_complete_database_erase_test()
    
    if success:
        print("\n🎉 VIDAGE COMPLET RÉUSSI - Database completely wiped and ready!")
        print("   The TopKit database is now completely empty and ready for restructuring.")
    else:
        print("\n⚠️  VIDAGE PARTIEL - Some issues encountered during database erasure.")
        print("   Manual intervention may be required to complete the cleanup.")

if __name__ == "__main__":
    main()