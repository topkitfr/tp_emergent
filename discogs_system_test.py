#!/usr/bin/env python3
"""
TEST DU NOUVEAU SYSTÈME DISCOGS - BACKEND
Comprehensive testing of the new Discogs-like jersey validation system
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"

class DiscogsSystemTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.normal_user_token = None
        self.admin_user_token = None
        self.test_jersey_id = None
        self.test_jersey_id_2 = None
        self.results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def register_and_login_user(self, email, password, name):
        """Register and login a user, return token"""
        try:
            # Register user
            register_data = {
                "email": email,
                "password": password,
                "name": name
            }
            
            register_response = requests.post(
                f"{self.backend_url}/auth/register",
                json=register_data,
                timeout=10
            )
            
            if register_response.status_code == 200:
                token = register_response.json()["token"]
                return token
            elif register_response.status_code == 400 and "already exists" in register_response.text:
                # User exists, try login
                login_data = {
                    "email": email,
                    "password": password
                }
                
                login_response = requests.post(
                    f"{self.backend_url}/auth/login",
                    json=login_data,
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    token = login_response.json()["token"]
                    return token
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"Error in register_and_login_user: {e}")
            return None
    
    def test_1_normal_user_jersey_submission(self):
        """Test 1: Jersey submission by normal user should be pending"""
        print("\n=== TEST 1: SOUMISSION DE JERSEY (NORMAL USER) ===")
        
        # Create normal user
        self.normal_user_token = self.register_and_login_user(
            "normaluser@test.com", 
            "password123", 
            "Normal User"
        )
        
        if not self.normal_user_token:
            self.log_result("Normal User Creation", False, "Failed to create/login normal user")
            return False
        
        self.log_result("Normal User Creation", True, "Normal user created and logged in successfully")
        
        # Submit jersey
        jersey_data = {
            "team": "Manchester United",
            "season": "2023/24",
            "player": "Bruno Fernandes",
            "size": "L",
            "condition": "excellent",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "Premier League",
            "description": "Test jersey for Discogs validation system",
            "images": [],
            "reference_code": "MU2324BF10"
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.normal_user_token}"}
            response = requests.post(
                f"{self.backend_url}/jerseys",
                json=jersey_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                jersey = response.json()
                self.test_jersey_id = jersey["id"]
                
                if jersey["status"] == "pending":
                    self.log_result("Jersey Status Pending", True, f"Jersey created with status 'pending' as expected (ID: {self.test_jersey_id})")
                else:
                    self.log_result("Jersey Status Pending", False, f"Jersey status is '{jersey['status']}', expected 'pending'")
                    return False
            else:
                self.log_result("Jersey Creation", False, f"Failed to create jersey: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Jersey Creation", False, f"Exception during jersey creation: {e}")
            return False
        
        # Verify jersey does NOT appear in public GET /api/jerseys
        try:
            response = requests.get(f"{self.backend_url}/jerseys", timeout=10)
            
            if response.status_code == 200:
                jerseys = response.json()
                jersey_ids = [j["id"] for j in jerseys]
                
                if self.test_jersey_id not in jersey_ids:
                    self.log_result("Jersey Not Public", True, "Pending jersey correctly NOT visible in public jerseys list")
                else:
                    self.log_result("Jersey Not Public", False, "Pending jersey incorrectly visible in public jerseys list")
                    return False
            else:
                self.log_result("Public Jerseys Check", False, f"Failed to get public jerseys: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Public Jerseys Check", False, f"Exception checking public jerseys: {e}")
            return False
        
        return True
    
    def test_2_admin_access_success(self):
        """Test 2: Admin access with topkitfr@gmail.com should work"""
        print("\n=== TEST 2: ACCÈS ADMIN (topkitfr@gmail.com) ===")
        
        # Create admin user
        self.admin_user_token = self.register_and_login_user(
            "topkitfr@gmail.com", 
            "adminpass123", 
            "TopKit Admin"
        )
        
        if not self.admin_user_token:
            self.log_result("Admin User Creation", False, "Failed to create/login admin user")
            return False
        
        self.log_result("Admin User Creation", True, "Admin user created and logged in successfully")
        
        # Test admin endpoint access
        try:
            headers = {"Authorization": f"Bearer {self.admin_user_token}"}
            response = requests.get(
                f"{self.backend_url}/admin/jerseys/pending",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                self.log_result("Admin Endpoint Access", True, f"Admin successfully accessed pending jerseys endpoint")
                
                # Verify our test jersey is in the pending list
                pending_ids = [j["id"] for j in pending_jerseys]
                if self.test_jersey_id in pending_ids:
                    self.log_result("Pending Jersey Found", True, "Test jersey found in pending list")
                else:
                    self.log_result("Pending Jersey Found", False, "Test jersey not found in pending list")
                    return False
                    
            else:
                self.log_result("Admin Endpoint Access", False, f"Admin access failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Endpoint Access", False, f"Exception during admin access: {e}")
            return False
        
        return True
    
    def test_3_admin_access_denied(self):
        """Test 3: Non-admin user should be denied admin access"""
        print("\n=== TEST 3: ACCÈS ADMIN REFUSÉ (AUTRE USER) ===")
        
        if not self.normal_user_token:
            self.log_result("Normal User Token", False, "Normal user token not available")
            return False
        
        # Try to access admin endpoint with normal user token
        try:
            headers = {"Authorization": f"Bearer {self.normal_user_token}"}
            response = requests.get(
                f"{self.backend_url}/admin/jerseys/pending",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 403:
                self.log_result("Admin Access Denied", True, "Normal user correctly denied admin access (403)")
            else:
                self.log_result("Admin Access Denied", False, f"Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Admin Access Denied", False, f"Exception during access denial test: {e}")
            return False
        
        return True
    
    def test_4_jersey_approval(self):
        """Test 4: Admin jersey approval"""
        print("\n=== TEST 4: APPROBATION DE JERSEY ===")
        
        if not self.admin_user_token or not self.test_jersey_id:
            self.log_result("Prerequisites", False, "Admin token or test jersey ID not available")
            return False
        
        # Approve the jersey
        try:
            headers = {"Authorization": f"Bearer {self.admin_user_token}"}
            response = requests.post(
                f"{self.backend_url}/admin/jerseys/{self.test_jersey_id}/approve",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result("Jersey Approval", True, "Jersey approved successfully")
            else:
                self.log_result("Jersey Approval", False, f"Approval failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Jersey Approval", False, f"Exception during approval: {e}")
            return False
        
        # Verify jersey status changed to approved
        try:
            response = requests.get(f"{self.backend_url}/jerseys/{self.test_jersey_id}", timeout=10)
            
            if response.status_code == 200:
                jersey = response.json()
                if jersey["status"] == "approved":
                    self.log_result("Status Changed to Approved", True, "Jersey status correctly changed to 'approved'")
                else:
                    self.log_result("Status Changed to Approved", False, f"Jersey status is '{jersey['status']}', expected 'approved'")
                    return False
            else:
                self.log_result("Status Check", False, f"Failed to get jersey details: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Status Check", False, f"Exception checking jersey status: {e}")
            return False
        
        # Verify jersey now appears in public GET /api/jerseys
        try:
            response = requests.get(f"{self.backend_url}/jerseys", timeout=10)
            
            if response.status_code == 200:
                jerseys = response.json()
                jersey_ids = [j["id"] for j in jerseys]
                
                if self.test_jersey_id in jersey_ids:
                    self.log_result("Jersey Now Public", True, "Approved jersey now visible in public jerseys list")
                else:
                    self.log_result("Jersey Now Public", False, "Approved jersey still not visible in public jerseys list")
                    return False
            else:
                self.log_result("Public Jerseys Check", False, f"Failed to get public jerseys: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Public Jerseys Check", False, f"Exception checking public jerseys: {e}")
            return False
        
        return True
    
    def test_5_jersey_rejection(self):
        """Test 5: Admin jersey rejection"""
        print("\n=== TEST 5: REJET DE JERSEY ===")
        
        if not self.admin_user_token:
            self.log_result("Admin Token", False, "Admin token not available")
            return False
        
        # Create another test jersey for rejection
        jersey_data = {
            "team": "Liverpool",
            "season": "2023/24",
            "player": "Mohamed Salah",
            "size": "M",
            "condition": "good",
            "manufacturer": "Nike",
            "home_away": "away",
            "league": "Premier League",
            "description": "Test jersey for rejection",
            "images": [],
            "reference_code": "LIV2324MS11"
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.normal_user_token}"}
            response = requests.post(
                f"{self.backend_url}/jerseys",
                json=jersey_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                jersey = response.json()
                self.test_jersey_id_2 = jersey["id"]
                self.log_result("Second Jersey Creation", True, f"Second test jersey created (ID: {self.test_jersey_id_2})")
            else:
                self.log_result("Second Jersey Creation", False, f"Failed to create second jersey: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Second Jersey Creation", False, f"Exception creating second jersey: {e}")
            return False
        
        # Reject the jersey
        try:
            headers = {"Authorization": f"Bearer {self.admin_user_token}"}
            rejection_data = {
                "reason": "Jersey does not meet quality standards for the database"
            }
            response = requests.post(
                f"{self.backend_url}/admin/jerseys/{self.test_jersey_id_2}/reject",
                json=rejection_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result("Jersey Rejection", True, "Jersey rejected successfully")
            else:
                self.log_result("Jersey Rejection", False, f"Rejection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Jersey Rejection", False, f"Exception during rejection: {e}")
            return False
        
        # Verify jersey status changed to rejected
        try:
            response = requests.get(f"{self.backend_url}/jerseys/{self.test_jersey_id_2}", timeout=10)
            
            if response.status_code == 200:
                jersey = response.json()
                if jersey["status"] == "rejected":
                    self.log_result("Status Changed to Rejected", True, "Jersey status correctly changed to 'rejected'")
                else:
                    self.log_result("Status Changed to Rejected", False, f"Jersey status is '{jersey['status']}', expected 'rejected'")
                    return False
            else:
                self.log_result("Rejected Status Check", False, f"Failed to get rejected jersey details: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Rejected Status Check", False, f"Exception checking rejected jersey status: {e}")
            return False
        
        # Verify rejected jersey does NOT appear in public GET /api/jerseys
        try:
            response = requests.get(f"{self.backend_url}/jerseys", timeout=10)
            
            if response.status_code == 200:
                jerseys = response.json()
                jersey_ids = [j["id"] for j in jerseys]
                
                if self.test_jersey_id_2 not in jersey_ids:
                    self.log_result("Rejected Jersey Not Public", True, "Rejected jersey correctly NOT visible in public jerseys list")
                else:
                    self.log_result("Rejected Jersey Not Public", False, "Rejected jersey incorrectly visible in public jerseys list")
                    return False
            else:
                self.log_result("Public Jerseys Check", False, f"Failed to get public jerseys: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Public Jerseys Check", False, f"Exception checking public jerseys: {e}")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all Discogs system tests"""
        print("🎯 DÉBUT DES TESTS DU SYSTÈME DISCOGS - BACKEND")
        print("=" * 60)
        
        tests = [
            self.test_1_normal_user_jersey_submission,
            self.test_2_admin_access_success,
            self.test_3_admin_access_denied,
            self.test_4_jersey_approval,
            self.test_5_jersey_rejection
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test.__name__}: {e}")
        
        print("\n" + "=" * 60)
        print(f"🎯 RÉSULTATS FINAUX: {passed}/{total} tests réussis")
        
        if passed == total:
            print("🎉 SYSTÈME DISCOGS ENTIÈREMENT FONCTIONNEL!")
            print("✅ Seuls les jerseys approuvés sont visibles publiquement")
            print("✅ Système de validation admin opérationnel")
            print("✅ Contrôle d'accès admin fonctionnel")
        else:
            print("❌ PROBLÈMES DÉTECTÉS dans le système Discogs")
            print("🔧 Corrections nécessaires avant mise en production")
        
        return passed == total

if __name__ == "__main__":
    tester = DiscogsSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)