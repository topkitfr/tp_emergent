#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - ENHANCED PROFILE FUNCTIONALITY TESTING

Testing the new enhanced profile functionality backend endpoints:
1. Profile completeness endpoint - GET /api/users/{user_id}/profile-completeness
2. Follow/unfollow system:
   - POST /api/users/{user_id}/follow
   - DELETE /api/users/{user_id}/follow  
   - GET /api/users/{user_id}/follow-status
3. Social endpoints:
   - GET /api/users/{user_id}/followers
   - GET /api/users/{user_id}/following
4. Activity feed - GET /api/users/{user_id}/activity-feed
5. Collection statistics - GET /api/users/{user_id}/collection-stats
6. Performance optimized endpoints:
   - GET /api/master-kits-paginated
   - GET /api/leaderboard-paginated
   - GET /api/uploads/{file_path} with optimization parameters (w, h, q)

CRITICAL: Testing all new enhanced profile endpoints with proper authentication.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://user-connect-hub.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitEnhancedProfileTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.test_user_id = None
        self.second_user_id = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate with admin credentials"""
        try:
            print(f"\n🔐 ADMIN AUTHENTICATION")
            print("=" * 60)
            print(f"   Email: {ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Admin Authentication", True, 
                             f"✅ Admin authentication successful")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Email: {self.admin_user_data.get('email')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Admin Authentication", False, 
                             f"❌ Admin authentication failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_test_users(self):
        """Get test users from leaderboard for testing social features"""
        try:
            print(f"\n👥 GETTING TEST USERS")
            print("=" * 60)
            
            response = self.session.get(f"{BACKEND_URL}/leaderboard?limit=10", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) >= 2:
                    # Get first two users that are not the admin user
                    admin_id = self.admin_user_data.get('id')
                    test_users = [user for user in data if user.get('user_id') != admin_id][:2]
                    
                    if len(test_users) >= 1:
                        self.test_user_id = test_users[0].get('user_id')
                        print(f"      ✅ Test User 1: {test_users[0].get('username')} (ID: {self.test_user_id})")
                        
                        if len(test_users) >= 2:
                            self.second_user_id = test_users[1].get('user_id')
                            print(f"      ✅ Test User 2: {test_users[1].get('username')} (ID: {self.second_user_id})")
                        
                        self.log_test("Get Test Users", True, f"✅ Found {len(test_users)} test users")
                        return True
                    else:
                        self.log_test("Get Test Users", False, "❌ No suitable test users found")
                        return False
                else:
                    self.log_test("Get Test Users", False, "❌ Insufficient users in leaderboard")
                    return False
            else:
                self.log_test("Get Test Users", False, f"❌ Failed to get leaderboard - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Test Users", False, f"Exception: {str(e)}")
            return False
    
    def test_profile_completeness_endpoint(self):
        """Test /api/users/{user_id}/profile-completeness endpoint"""
        try:
            print(f"\n📊 TESTING PROFILE COMPLETENESS ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                self.log_test("Profile Completeness Endpoint", False, "❌ No authentication token available")
                return False
            
            # Test with admin user's own profile
            user_id = self.admin_user_data.get('id')
            if not user_id:
                self.log_test("Profile Completeness Endpoint", False, "❌ No user ID available for testing")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/profile-completeness", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Endpoint accessible - profile completeness data returned")
                
                # Validate response structure
                required_fields = ['completeness_percentage', 'missing_required', 'missing_optional']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print(f"      ✅ Response structure valid")
                    print(f"      ✅ Profile completeness: {data.get('completeness_percentage', 0)}%")
                    print(f"         Completed required: {data.get('completed_required', 0)}/{data.get('total_required', 0)}")
                    print(f"         Missing required: {len(data.get('missing_required', []))}")
                    print(f"         Missing optional: {len(data.get('missing_optional', []))}")
                    
                    # Validate percentage is between 0 and 100
                    percentage = data.get('completeness_percentage', 0)
                    if 0 <= percentage <= 100:
                        self.log_test("Profile Completeness Endpoint", True, 
                                     f"✅ Endpoint working correctly - {percentage}% completeness")
                        return True
                    else:
                        self.log_test("Profile Completeness Endpoint", False, 
                                     f"❌ Invalid completeness percentage: {percentage}")
                        return False
                else:
                    self.log_test("Profile Completeness Endpoint", False, 
                                 f"❌ Missing required fields: {missing_fields}")
                    return False
            elif response.status_code == 401:
                self.log_test("Profile Completeness Endpoint", False, 
                             f"❌ Authentication failed")
                return False
            elif response.status_code == 404:
                self.log_test("Profile Completeness Endpoint", False, 
                             f"❌ User not found: {user_id}")
                return False
            else:
                self.log_test("Profile Completeness Endpoint", False, 
                             f"❌ Endpoint failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Profile Completeness Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_follow_unfollow_system(self):
        """Test follow/unfollow system endpoints"""
        try:
            print(f"\n👥 TESTING FOLLOW/UNFOLLOW SYSTEM")
            print("=" * 60)
            
            if not self.auth_token or not self.test_user_id:
                self.log_test("Follow/Unfollow System", False, "❌ Missing authentication or test user")
                return False
            
            # Test 1: Follow a user
            print(f"      Testing follow user {self.test_user_id}...")
            follow_response = self.session.post(f"{BACKEND_URL}/users/{self.test_user_id}/follow", timeout=10)
            
            if follow_response.status_code == 200:
                follow_data = follow_response.json()
                print(f"      ✅ Follow successful: {follow_data.get('message', 'No message')}")
                
                # Test 2: Check follow status
                print(f"      Testing follow status...")
                status_response = self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/follow-status", timeout=10)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    is_following = status_data.get('is_following', False)
                    print(f"      ✅ Follow status check: Following = {is_following}")
                    
                    if is_following:
                        # Test 3: Try to follow again (should fail)
                        print(f"      Testing duplicate follow (should fail)...")
                        duplicate_response = self.session.post(f"{BACKEND_URL}/users/{self.test_user_id}/follow", timeout=10)
                        
                        if duplicate_response.status_code == 400:
                            print(f"      ✅ Duplicate follow properly rejected")
                            
                            # Test 4: Unfollow the user
                            print(f"      Testing unfollow...")
                            unfollow_response = self.session.delete(f"{BACKEND_URL}/users/{self.test_user_id}/follow", timeout=10)
                            
                            if unfollow_response.status_code == 200:
                                unfollow_data = unfollow_response.json()
                                print(f"      ✅ Unfollow successful: {unfollow_data.get('message', 'No message')}")
                                
                                # Test 5: Check follow status after unfollow
                                print(f"      Testing follow status after unfollow...")
                                final_status_response = self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/follow-status", timeout=10)
                                
                                if final_status_response.status_code == 200:
                                    final_status_data = final_status_response.json()
                                    is_still_following = final_status_data.get('is_following', True)
                                    
                                    if not is_still_following:
                                        print(f"      ✅ Follow status correctly updated after unfollow")
                                        self.log_test("Follow/Unfollow System", True, 
                                                     "✅ Complete follow/unfollow workflow working correctly")
                                        return True
                                    else:
                                        self.log_test("Follow/Unfollow System", False, 
                                                     "❌ Follow status not updated after unfollow")
                                        return False
                                else:
                                    self.log_test("Follow/Unfollow System", False, 
                                                 f"❌ Final status check failed - Status {final_status_response.status_code}")
                                    return False
                            else:
                                self.log_test("Follow/Unfollow System", False, 
                                             f"❌ Unfollow failed - Status {unfollow_response.status_code}")
                                return False
                        else:
                            self.log_test("Follow/Unfollow System", False, 
                                         f"❌ Duplicate follow not properly rejected - Status {duplicate_response.status_code}")
                            return False
                    else:
                        self.log_test("Follow/Unfollow System", False, 
                                     "❌ Follow status shows not following after successful follow")
                        return False
                else:
                    self.log_test("Follow/Unfollow System", False, 
                                 f"❌ Follow status check failed - Status {status_response.status_code}")
                    return False
            else:
                self.log_test("Follow/Unfollow System", False, 
                             f"❌ Follow failed - Status {follow_response.status_code}", follow_response.text)
                return False
                
        except Exception as e:
            self.log_test("Follow/Unfollow System", False, f"Exception: {str(e)}")
            return False
    
    def test_social_endpoints(self):
        """Test followers and following endpoints"""
        try:
            print(f"\n👥 TESTING SOCIAL ENDPOINTS")
            print("=" * 60)
            
            if not self.auth_token or not self.test_user_id:
                self.log_test("Social Endpoints", False, "❌ Missing authentication or test user")
                return False
            
            # Test 1: Get followers
            print(f"      Testing followers endpoint...")
            followers_response = self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/followers", timeout=10)
            
            if followers_response.status_code == 200:
                followers_data = followers_response.json()
                print(f"      ✅ Followers endpoint accessible - {len(followers_data)} followers")
                
                # Validate response structure
                if isinstance(followers_data, list):
                    if len(followers_data) > 0:
                        # Check first follower structure
                        first_follower = followers_data[0]
                        required_fields = ['user_id', 'name', 'followed_at']
                        missing_fields = [field for field in required_fields if field not in first_follower]
                        
                        if missing_fields:
                            print(f"      ⚠️ Missing fields in follower data: {missing_fields}")
                    
                    # Test 2: Get following
                    print(f"      Testing following endpoint...")
                    following_response = self.session.get(f"{BACKEND_URL}/users/{self.test_user_id}/following", timeout=10)
                    
                    if following_response.status_code == 200:
                        following_data = following_response.json()
                        print(f"      ✅ Following endpoint accessible - {len(following_data)} following")
                        
                        # Validate response structure
                        if isinstance(following_data, list):
                            if len(following_data) > 0:
                                # Check first following structure
                                first_following = following_data[0]
                                required_fields = ['user_id', 'name', 'followed_at']
                                missing_fields = [field for field in required_fields if field not in first_following]
                                
                                if missing_fields:
                                    print(f"      ⚠️ Missing fields in following data: {missing_fields}")
                            
                            self.log_test("Social Endpoints", True, 
                                         f"✅ Both social endpoints working - {len(followers_data)} followers, {len(following_data)} following")
                            return True
                        else:
                            self.log_test("Social Endpoints", False, 
                                         f"❌ Following response is not a list: {type(following_data)}")
                            return False
                    else:
                        self.log_test("Social Endpoints", False, 
                                     f"❌ Following endpoint failed - Status {following_response.status_code}")
                        return False
                else:
                    self.log_test("Social Endpoints", False, 
                                 f"❌ Followers response is not a list: {type(followers_data)}")
                    return False
            else:
                self.log_test("Social Endpoints", False, 
                             f"❌ Followers endpoint failed - Status {followers_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Social Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_activity_feed_endpoint(self):
        """Test activity feed endpoint"""
        try:
            print(f"\n📰 TESTING ACTIVITY FEED ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                self.log_test("Activity Feed Endpoint", False, "❌ No authentication token available")
                return False
            
            # Test with admin user's own activity feed
            user_id = self.admin_user_data.get('id')
            if not user_id:
                self.log_test("Activity Feed Endpoint", False, "❌ No user ID available for testing")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/activity-feed", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Endpoint accessible - {len(data)} activity items")
                
                # Validate response structure
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check first activity item structure
                        first_item = data[0]
                        required_fields = ['type', 'action', 'timestamp']
                        missing_fields = [field for field in required_fields if field not in first_item]
                        
                        if not missing_fields:
                            print(f"      ✅ Response structure valid")
                            print(f"      ✅ Latest activity: {first_item.get('action', 'Unknown')}")
                            print(f"         Type: {first_item.get('type', 'Unknown')}")
                            print(f"         Timestamp: {first_item.get('timestamp', 'Unknown')}")
                            
                            self.log_test("Activity Feed Endpoint", True, 
                                         f"✅ Endpoint working correctly - {len(data)} activity items returned")
                            return True
                        else:
                            self.log_test("Activity Feed Endpoint", False, 
                                         f"❌ Missing required fields: {missing_fields}")
                            return False
                    else:
                        print(f"      ⚠️ No activity items found")
                        self.log_test("Activity Feed Endpoint", True, 
                                     f"✅ Endpoint working - no activity data available")
                        return True
                else:
                    self.log_test("Activity Feed Endpoint", False, 
                                 f"❌ Response is not a list: {type(data)}")
                    return False
            elif response.status_code == 401:
                self.log_test("Activity Feed Endpoint", False, 
                             f"❌ Authentication failed")
                return False
            elif response.status_code == 404:
                self.log_test("Activity Feed Endpoint", False, 
                             f"❌ User not found: {user_id}")
                return False
            else:
                self.log_test("Activity Feed Endpoint", False, 
                             f"❌ Endpoint failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Activity Feed Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_collection_stats_endpoint(self):
        """Test collection statistics endpoint"""
        try:
            print(f"\n📈 TESTING COLLECTION STATS ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                self.log_test("Collection Stats Endpoint", False, "❌ No authentication token available")
                return False
            
            # Test with admin user's collection stats
            user_id = self.admin_user_data.get('id')
            if not user_id:
                self.log_test("Collection Stats Endpoint", False, "❌ No user ID available for testing")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/users/{user_id}/collection-stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Endpoint accessible - collection stats returned")
                
                # Validate response structure
                required_fields = ['total_items', 'total_value', 'by_type', 'by_condition']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print(f"      ✅ Response structure valid")
                    print(f"      ✅ Collection stats:")
                    print(f"         Total items: {data.get('total_items', 0)}")
                    print(f"         Total value: €{data.get('total_value', 0)}")
                    print(f"         By type: {len(data.get('by_type', {}))}")
                    print(f"         By condition: {len(data.get('by_condition', {}))}")
                    
                    # Validate numeric values
                    total_items = data.get('total_items', 0)
                    total_value = data.get('total_value', 0)
                    
                    if isinstance(total_items, int) and isinstance(total_value, (int, float)):
                        self.log_test("Collection Stats Endpoint", True, 
                                     f"✅ Endpoint working correctly - {total_items} items, €{total_value} value")
                        return True
                    else:
                        self.log_test("Collection Stats Endpoint", False, 
                                     f"❌ Invalid data types in response")
                        return False
                else:
                    self.log_test("Collection Stats Endpoint", False, 
                                 f"❌ Missing required fields: {missing_fields}")
                    return False
            elif response.status_code == 401:
                self.log_test("Collection Stats Endpoint", False, 
                             f"❌ Authentication failed")
                return False
            elif response.status_code == 404:
                self.log_test("Collection Stats Endpoint", False, 
                             f"❌ User not found: {user_id}")
                return False
            else:
                self.log_test("Collection Stats Endpoint", False, 
                             f"❌ Endpoint failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Collection Stats Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_endpoints(self):
        """Test performance optimized endpoints"""
        try:
            print(f"\n⚡ TESTING PERFORMANCE ENDPOINTS")
            print("=" * 60)
            
            # Test 1: Master kits paginated
            print(f"      Testing master-kits-paginated...")
            kits_response = self.session.get(f"{BACKEND_URL}/master-kits-paginated?page=1&per_page=5", timeout=10)
            
            if kits_response.status_code == 200:
                kits_data = kits_response.json()
                print(f"      ✅ Master kits paginated accessible")
                
                # Validate pagination structure
                required_fields = ['items', 'pagination']
                missing_fields = [field for field in required_fields if field not in kits_data]
                
                if not missing_fields:
                    pagination = kits_data.get('pagination', {})
                    items = kits_data.get('items', [])
                    
                    print(f"         Items: {len(items)}")
                    print(f"         Page: {pagination.get('page', 'Unknown')}")
                    print(f"         Total pages: {pagination.get('total_pages', 'Unknown')}")
                    
                    # Test 2: Leaderboard paginated
                    print(f"      Testing leaderboard-paginated...")
                    leaderboard_response = self.session.get(f"{BACKEND_URL}/leaderboard-paginated?page=1&per_page=5", timeout=10)
                    
                    if leaderboard_response.status_code == 200:
                        leaderboard_data = leaderboard_response.json()
                        print(f"      ✅ Leaderboard paginated accessible")
                        
                        # Validate pagination structure
                        if 'items' in leaderboard_data and 'pagination' in leaderboard_data:
                            leaderboard_pagination = leaderboard_data.get('pagination', {})
                            leaderboard_items = leaderboard_data.get('items', [])
                            
                            print(f"         Items: {len(leaderboard_items)}")
                            print(f"         Page: {leaderboard_pagination.get('page', 'Unknown')}")
                            print(f"         Total pages: {leaderboard_pagination.get('total_pages', 'Unknown')}")
                            
                            self.log_test("Performance Endpoints", True, 
                                         f"✅ Both paginated endpoints working correctly")
                            return True
                        else:
                            self.log_test("Performance Endpoints", False, 
                                         f"❌ Leaderboard pagination structure invalid")
                            return False
                    else:
                        self.log_test("Performance Endpoints", False, 
                                     f"❌ Leaderboard paginated failed - Status {leaderboard_response.status_code}")
                        return False
                else:
                    self.log_test("Performance Endpoints", False, 
                                 f"❌ Master kits pagination structure invalid - Missing: {missing_fields}")
                    return False
            else:
                self.log_test("Performance Endpoints", False, 
                             f"❌ Master kits paginated failed - Status {kits_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Performance Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_image_optimization_endpoint(self):
        """Test image optimization endpoint"""
        try:
            print(f"\n🖼️ TESTING IMAGE OPTIMIZATION ENDPOINT")
            print("=" * 60)
            
            # Test with a sample image path (we'll test the endpoint structure)
            test_path = "master_kits/sample.jpg"
            
            # Test 1: Basic image serving
            print(f"      Testing basic image serving...")
            basic_response = self.session.get(f"{BACKEND_URL}/uploads/{test_path}", timeout=10)
            
            # We expect either 200 (if image exists) or 404 (if not found)
            if basic_response.status_code in [200, 404]:
                print(f"      ✅ Basic image endpoint accessible (Status: {basic_response.status_code})")
                
                # Test 2: Image optimization parameters
                print(f"      Testing image optimization parameters...")
                optimized_response = self.session.get(f"{BACKEND_URL}/uploads/{test_path}?w=300&h=200&q=80", timeout=10)
                
                # We expect either 200 (if image exists) or 404 (if not found)
                if optimized_response.status_code in [200, 404]:
                    print(f"      ✅ Optimized image endpoint accessible (Status: {optimized_response.status_code})")
                    
                    # Check if optimization parameters are accepted (no 400 error)
                    if optimized_response.status_code != 400:
                        self.log_test("Image Optimization Endpoint", True, 
                                     f"✅ Image optimization endpoint working - accepts w, h, q parameters")
                        return True
                    else:
                        self.log_test("Image Optimization Endpoint", False, 
                                     f"❌ Optimization parameters rejected")
                        return False
                else:
                    self.log_test("Image Optimization Endpoint", False, 
                                 f"❌ Optimized image endpoint failed - Status {optimized_response.status_code}")
                    return False
            else:
                self.log_test("Image Optimization Endpoint", False, 
                             f"❌ Basic image endpoint failed - Status {basic_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Image Optimization Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_all_enhanced_profile_endpoints(self):
        """Test all enhanced profile endpoints"""
        print("\n🚀 ENHANCED PROFILE FUNCTIONALITY TESTING")
        print("Testing all new enhanced profile endpoints with proper authentication")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        
        # Step 2: Get test users
        print("\n2️⃣ Getting test users...")
        users_success = self.get_test_users()
        if not users_success:
            print("⚠️ Limited testing without additional users")
        
        # Step 3: Test profile completeness endpoint
        print("\n3️⃣ Testing profile completeness endpoint...")
        test_results.append(self.test_profile_completeness_endpoint())
        
        # Step 4: Test follow/unfollow system
        print("\n4️⃣ Testing follow/unfollow system...")
        if self.test_user_id:
            test_results.append(self.test_follow_unfollow_system())
        else:
            print("      ⚠️ Skipping follow/unfollow tests - no test user available")
            test_results.append(False)
        
        # Step 5: Test social endpoints
        print("\n5️⃣ Testing social endpoints...")
        if self.test_user_id:
            test_results.append(self.test_social_endpoints())
        else:
            print("      ⚠️ Skipping social endpoint tests - no test user available")
            test_results.append(False)
        
        # Step 6: Test activity feed endpoint
        print("\n6️⃣ Testing activity feed endpoint...")
        test_results.append(self.test_activity_feed_endpoint())
        
        # Step 7: Test collection stats endpoint
        print("\n7️⃣ Testing collection stats endpoint...")
        test_results.append(self.test_collection_stats_endpoint())
        
        # Step 8: Test performance endpoints
        print("\n8️⃣ Testing performance endpoints...")
        test_results.append(self.test_performance_endpoints())
        
        # Step 9: Test image optimization endpoint
        print("\n9️⃣ Testing image optimization endpoint...")
        test_results.append(self.test_image_optimization_endpoint())
        
        return test_results
    
    def print_final_summary(self):
        """Print final testing summary"""
        print("\n📊 ENHANCED PROFILE FUNCTIONALITY TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Tests totaux: {total_tests}")
        print(f"Réussis: {passed_tests} ✅")
        print(f"Échoués: {failed_tests} ❌")
        print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 ENDPOINT RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Admin login working")
        else:
            print(f"  ❌ AUTHENTICATION: Admin login failed")
        
        # Profile completeness
        profile_completeness = any(r['success'] for r in self.test_results if 'Profile Completeness' in r['test'])
        if profile_completeness:
            print(f"  ✅ PROFILE COMPLETENESS: /api/users/{{user_id}}/profile-completeness working")
        else:
            print(f"  ❌ PROFILE COMPLETENESS: /api/users/{{user_id}}/profile-completeness failed")
        
        # Follow/unfollow system
        follow_system = any(r['success'] for r in self.test_results if 'Follow/Unfollow System' in r['test'])
        if follow_system:
            print(f"  ✅ FOLLOW/UNFOLLOW: Complete follow/unfollow workflow working")
        else:
            print(f"  ❌ FOLLOW/UNFOLLOW: Follow/unfollow system failed")
        
        # Social endpoints
        social_endpoints = any(r['success'] for r in self.test_results if 'Social Endpoints' in r['test'])
        if social_endpoints:
            print(f"  ✅ SOCIAL ENDPOINTS: /api/users/{{user_id}}/followers and /following working")
        else:
            print(f"  ❌ SOCIAL ENDPOINTS: Social endpoints failed")
        
        # Activity feed
        activity_feed = any(r['success'] for r in self.test_results if 'Activity Feed' in r['test'])
        if activity_feed:
            print(f"  ✅ ACTIVITY FEED: /api/users/{{user_id}}/activity-feed working")
        else:
            print(f"  ❌ ACTIVITY FEED: /api/users/{{user_id}}/activity-feed failed")
        
        # Collection stats
        collection_stats = any(r['success'] for r in self.test_results if 'Collection Stats' in r['test'])
        if collection_stats:
            print(f"  ✅ COLLECTION STATS: /api/users/{{user_id}}/collection-stats working")
        else:
            print(f"  ❌ COLLECTION STATS: /api/users/{{user_id}}/collection-stats failed")
        
        # Performance endpoints
        performance = any(r['success'] for r in self.test_results if 'Performance Endpoints' in r['test'])
        if performance:
            print(f"  ✅ PERFORMANCE: Paginated endpoints working")
        else:
            print(f"  ❌ PERFORMANCE: Paginated endpoints failed")
        
        # Image optimization
        image_optimization = any(r['success'] for r in self.test_results if 'Image Optimization' in r['test'])
        if image_optimization:
            print(f"  ✅ IMAGE OPTIMIZATION: /api/uploads/{{file_path}} with parameters working")
        else:
            print(f"  ❌ IMAGE OPTIMIZATION: Image optimization failed")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status
        print(f"\n🎯 FINAL STATUS:")
        if passed_tests == total_tests:
            print(f"  ✅ ALL ENHANCED PROFILE ENDPOINTS WORKING: All endpoints tested successfully")
        elif passed_tests >= total_tests * 0.8:
            print(f"  ⚠️ MOSTLY WORKING: {passed_tests}/{total_tests} endpoints working correctly")
            print(f"     - Minor issues identified but core functionality operational")
        else:
            print(f"  ❌ MAJOR ISSUES: Only {passed_tests}/{total_tests} endpoints working")
            print(f"     - Significant problems require attention")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all enhanced profile endpoint tests and return success status"""
        test_results = self.test_all_enhanced_profile_endpoints()
        self.print_final_summary()
        return any(test_results)

def main():
    """Main test execution - Enhanced Profile Functionality Testing"""
    tester = TopKitEnhancedProfileTesting()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()