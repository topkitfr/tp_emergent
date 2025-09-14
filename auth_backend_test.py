#!/usr/bin/env python3
"""
TopKit Authentication Backend Testing - Post Modifications
Testing authentication system after recent modifications as requested in review
"""

import requests
import json
import uuid
from datetime import datetime
import time
import jwt

# Configuration - Using correct backend URL from frontend .env
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"

class AuthenticationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.test_jersey_id = None
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
    
    def test_registration(self):
        """Test d'inscription (POST /api/auth/register)"""
        try:
            # Use the exact credentials from review request
            payload = {
                "email": "test@example.com",
                "password": "password123",
                "name": "Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
                    # Verify JWT token structure
                    try:
                        # Decode without verification to check structure
                        decoded = jwt.decode(self.auth_token, options={"verify_signature": False})
                        if "user_id" in decoded and "exp" in decoded:
                            self.log_test("Test d'inscription (POST /api/auth/register)", "PASS", 
                                        f"User registered successfully with valid JWT token. User ID: {self.user_id}")
                            return True
                        else:
                            self.log_test("Test d'inscription (POST /api/auth/register)", "FAIL", 
                                        "JWT token missing required fields")
                            return False
                    except Exception as jwt_error:
                        self.log_test("Test d'inscription (POST /api/auth/register)", "FAIL", 
                                    f"Invalid JWT token structure: {jwt_error}")
                        return False
                else:
                    self.log_test("Test d'inscription (POST /api/auth/register)", "FAIL", 
                                "Missing token or user in response")
                    return False
            elif response.status_code == 400:
                # User might already exist, try with unique email
                unique_email = f"test_{int(time.time())}@example.com"
                payload["email"] = unique_email
                
                retry_response = self.session.post(f"{self.base_url}/auth/register", json=payload)
                if retry_response.status_code == 200:
                    data = retry_response.json()
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("Test d'inscription (POST /api/auth/register)", "PASS", 
                                f"User registered with unique email: {unique_email}")
                    return True
                else:
                    self.log_test("Test d'inscription (POST /api/auth/register)", "FAIL", 
                                f"Retry failed. Status: {retry_response.status_code}, Response: {retry_response.text}")
                    return False
            else:
                self.log_test("Test d'inscription (POST /api/auth/register)", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test d'inscription (POST /api/auth/register)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_login(self):
        """Test de connexion (POST /api/auth/login)"""
        try:
            # First register a user for login test
            unique_email = f"logintest_{int(time.time())}@example.com"
            
            # Register
            register_payload = {
                "email": unique_email,
                "password": "password123",
                "name": "Test User"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code != 200:
                self.log_test("Test de connexion (POST /api/auth/login)", "FAIL", 
                            "Could not register test user for login test")
                return False
            
            # Now test login with same credentials
            login_payload = {
                "email": unique_email,
                "password": "password123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    # Verify token is valid JWT
                    try:
                        decoded = jwt.decode(data["token"], options={"verify_signature": False})
                        if "user_id" in decoded and "exp" in decoded:
                            self.log_test("Test de connexion (POST /api/auth/login)", "PASS", 
                                        f"Login successful with valid JWT token. User: {data['user']['email']}")
                            return True
                        else:
                            self.log_test("Test de connexion (POST /api/auth/login)", "FAIL", 
                                        "JWT token missing required fields")
                            return False
                    except Exception as jwt_error:
                        self.log_test("Test de connexion (POST /api/auth/login)", "FAIL", 
                                    f"Invalid JWT token: {jwt_error}")
                        return False
                else:
                    self.log_test("Test de connexion (POST /api/auth/login)", "FAIL", 
                                "Missing token or user in response")
                    return False
            else:
                self.log_test("Test de connexion (POST /api/auth/login)", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test de connexion (POST /api/auth/login)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_profile(self):
        """Test du profil (GET /api/profile)"""
        try:
            if not self.auth_token:
                self.log_test("Test du profil (GET /api/profile)", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                if "user" in profile and "stats" in profile:
                    user_data = profile["user"]
                    stats_data = profile["stats"]
                    
                    # Verify required user fields
                    required_user_fields = ["id", "email", "name", "provider", "created_at"]
                    required_stats_fields = ["owned_jerseys", "wanted_jerseys", "active_listings"]
                    
                    user_valid = all(field in user_data for field in required_user_fields)
                    stats_valid = all(field in stats_data for field in required_stats_fields)
                    
                    if user_valid and stats_valid:
                        # Verify data consistency
                        if user_data["id"] == self.user_id:
                            self.log_test("Test du profil (GET /api/profile)", "PASS", 
                                        f"Profile retrieved successfully. Stats: {stats_data}")
                            return True
                        else:
                            self.log_test("Test du profil (GET /api/profile)", "FAIL", 
                                        "User ID mismatch in profile")
                            return False
                    else:
                        self.log_test("Test du profil (GET /api/profile)", "FAIL", 
                                    "Missing required fields in profile or stats")
                        return False
                else:
                    self.log_test("Test du profil (GET /api/profile)", "FAIL", 
                                "Missing user or stats in response")
                    return False
            else:
                self.log_test("Test du profil (GET /api/profile)", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test du profil (GET /api/profile)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collections_owned(self):
        """Test des collections (GET /api/collections/owned)"""
        try:
            if not self.auth_token:
                self.log_test("Test des collections owned (GET /api/collections/owned)", "FAIL", 
                            "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/collections/owned")
            
            if response.status_code == 200:
                owned_collection = response.json()
                # Even if empty, endpoint should be accessible
                self.log_test("Test des collections owned (GET /api/collections/owned)", "PASS", 
                            f"Owned collection accessible. Items: {len(owned_collection)}")
                return True
            else:
                self.log_test("Test des collections owned (GET /api/collections/owned)", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test des collections owned (GET /api/collections/owned)", "FAIL", 
                        f"Exception: {str(e)}")
            return False
    
    def test_collections_wanted(self):
        """Test des collections (GET /api/collections/wanted)"""
        try:
            if not self.auth_token:
                self.log_test("Test des collections wanted (GET /api/collections/wanted)", "FAIL", 
                            "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if response.status_code == 200:
                wanted_collection = response.json()
                # Even if empty, endpoint should be accessible
                self.log_test("Test des collections wanted (GET /api/collections/wanted)", "PASS", 
                            f"Wanted collection accessible. Items: {len(wanted_collection)}")
                return True
            else:
                self.log_test("Test des collections wanted (GET /api/collections/wanted)", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test des collections wanted (GET /api/collections/wanted)", "FAIL", 
                        f"Exception: {str(e)}")
            return False
    
    def test_remove_button_endpoint(self):
        """Test du bouton Remove (DELETE /api/collections/{jersey_id})"""
        try:
            if not self.auth_token:
                self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "FAIL", 
                            "No auth token available")
                return False
            
            # First create a jersey to add to collection
            jersey_payload = {
                "team": "Manchester United",
                "season": "2023-24",
                "player": "Bruno Fernandes",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Test jersey for remove functionality",
                "images": []
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if jersey_response.status_code != 200:
                self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "FAIL", 
                            "Could not create test jersey")
                return False
            
            jersey_data = jersey_response.json()
            self.test_jersey_id = jersey_data["id"]
            
            # Add jersey to collection
            collection_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
            
            if add_response.status_code != 200:
                self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "FAIL", 
                            "Could not add jersey to collection")
                return False
            
            # Now test the remove functionality
            remove_response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            if remove_response.status_code == 200:
                data = remove_response.json()
                if "message" in data and "removed" in data["message"].lower():
                    # Verify jersey was actually removed by checking collection
                    verify_response = self.session.get(f"{self.base_url}/collections/owned")
                    if verify_response.status_code == 200:
                        collection = verify_response.json()
                        jersey_still_in_collection = any(item.get('jersey_id') == self.test_jersey_id for item in collection)
                        
                        if not jersey_still_in_collection:
                            self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "PASS", 
                                        "Jersey successfully removed from collection")
                            return True
                        else:
                            self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "FAIL", 
                                        "Jersey still in collection after removal")
                            return False
                    else:
                        self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "FAIL", 
                                    "Could not verify removal")
                        return False
                else:
                    self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "FAIL", 
                                "Unexpected response message")
                    return False
            else:
                self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "FAIL", 
                            f"Status: {remove_response.status_code}, Response: {remove_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test du bouton Remove (DELETE /api/collections/{jersey_id})", "FAIL", 
                        f"Exception: {str(e)}")
            return False
    
    def test_remove_button_error_handling(self):
        """Test gestion d'erreur pour des IDs inexistants"""
        try:
            if not self.auth_token:
                self.log_test("Test gestion d'erreur IDs inexistants", "FAIL", "No auth token available")
                return False
            
            # Test with non-existent jersey ID
            fake_jersey_id = str(uuid.uuid4())
            
            response = self.session.delete(f"{self.base_url}/collections/{fake_jersey_id}")
            
            if response.status_code == 404:
                self.log_test("Test gestion d'erreur IDs inexistants", "PASS", 
                            "Correctly returned 404 for non-existent jersey ID")
                return True
            else:
                self.log_test("Test gestion d'erreur IDs inexistants", "FAIL", 
                            f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test gestion d'erreur IDs inexistants", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests as specified in review request"""
        print("🔐 TOPKIT AUTHENTICATION BACKEND TESTING - POST MODIFICATIONS")
        print("=" * 70)
        print()
        
        tests = [
            self.test_registration,
            self.test_login,
            self.test_profile,
            self.test_collections_owned,
            self.test_collections_wanted,
            self.test_remove_button_endpoint,
            self.test_remove_button_error_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("=" * 70)
        print(f"🎯 RÉSULTATS FINAUX: {passed}/{total} tests réussis")
        
        if passed == total:
            print("✅ TOUS LES TESTS D'AUTHENTIFICATION SONT PASSÉS!")
            print("Le backend d'authentification fonctionne correctement après les modifications récentes.")
        else:
            print(f"❌ {total - passed} test(s) ont échoué.")
            print("Des problèmes ont été détectés dans le système d'authentification.")
        
        return passed == total

if __name__ == "__main__":
    tester = AuthenticationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)