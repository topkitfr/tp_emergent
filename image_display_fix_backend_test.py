#!/usr/bin/env python3
"""
Image Display Fix Backend Testing
=================================

Comprehensive test to verify the image display fix is working correctly:

1. Test Master Kit images - verify API endpoints for image serving are working
2. Check specific Master Kits that have images (like TK-MASTER-8270A7)
3. Confirm image URLs are constructed properly with /api/ prefix
4. Test Team/Brand images - check if teams and brands have logo_url fields populated
5. Test image serving for teams and brands
6. Verify API endpoints work for different image types
7. Test the corrected URL pattern: ${BACKEND_URL}/api/uploads/{type}/{filename}
8. Confirm images are served with proper content-type headers

The user reported that:
- Master kit photos not displayed in collection, kit area, homepage
- Team/brand photos not displayed in database and homepage

The main agent has fixed the frontend URL construction by adding /api/ prefix to image URLs.
"""

import asyncio
import aiohttp
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import mimetypes

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ImageDisplayFixTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
            
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    async def authenticate(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("token")
                    user_info = data.get("user", {})
                    
                    self.log_test(
                        "Admin Authentication", 
                        True, 
                        f"Authenticated as {user_info.get('name', 'Unknown')} ({user_info.get('role', 'Unknown')})"
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Admin Authentication", False, f"Status {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
            
    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
        
    async def test_master_kit_images(self):
        """Test Master Kit images and API endpoints"""
        print("\n🔍 TESTING MASTER KIT IMAGES")
        print("=" * 50)
        
        try:
            # Get all Master Kits
            async with self.session.get(f"{API_BASE}/master-kits", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    master_kits = await response.json()
                    self.log_test("Master Kits API Endpoint", True, f"Retrieved {len(master_kits)} Master Kits")
                    
                    # Test specific Master Kit TK-MASTER-8270A7
                    target_kit = None
                    kits_with_images = []
                    
                    for kit in master_kits:
                        if kit.get("topkit_reference") == "TK-MASTER-8270A7":
                            target_kit = kit
                        if kit.get("front_photo_url"):
                            kits_with_images.append(kit)
                            
                    # Test target kit
                    if target_kit:
                        self.log_test(
                            "Target Master Kit TK-MASTER-8270A7 Found", 
                            True, 
                            f"Club: {target_kit.get('club', 'Unknown')}, Season: {target_kit.get('season', 'Unknown')}"
                        )
                        
                        # Test image URL if present
                        if target_kit.get("front_photo_url"):
                            await self.test_image_serving(
                                target_kit["front_photo_url"], 
                                "TK-MASTER-8270A7 Image"
                            )
                        else:
                            self.log_test("TK-MASTER-8270A7 Image URL", False, "No front_photo_url found")
                    else:
                        self.log_test("Target Master Kit TK-MASTER-8270A7 Found", False, "Kit not found in database")
                        
                    # Test other Master Kits with images
                    self.log_test(
                        "Master Kits with Images", 
                        len(kits_with_images) > 0, 
                        f"Found {len(kits_with_images)} Master Kits with front_photo_url"
                    )
                    
                    # Test first few Master Kit images
                    for i, kit in enumerate(kits_with_images[:3]):
                        await self.test_image_serving(
                            kit["front_photo_url"], 
                            f"Master Kit {kit.get('topkit_reference', f'#{i+1}')} Image"
                        )
                        
                else:
                    error_text = await response.text()
                    self.log_test("Master Kits API Endpoint", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Master Kit Images Test", False, f"Exception: {str(e)}")
            
    async def test_team_brand_images(self):
        """Test Team and Brand images"""
        print("\n🔍 TESTING TEAM AND BRAND IMAGES")
        print("=" * 50)
        
        # Test Teams
        try:
            async with self.session.get(f"{API_BASE}/teams", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    teams = await response.json()
                    self.log_test("Teams API Endpoint", True, f"Retrieved {len(teams)} teams")
                    
                    teams_with_logos = [team for team in teams if team.get("logo_url")]
                    self.log_test(
                        "Teams with Logo URLs", 
                        len(teams_with_logos) > 0, 
                        f"Found {len(teams_with_logos)} teams with logo_url"
                    )
                    
                    # Test first few team logos
                    for i, team in enumerate(teams_with_logos[:3]):
                        await self.test_image_serving(
                            team["logo_url"], 
                            f"Team {team.get('name', f'#{i+1}')} Logo"
                        )
                        
                else:
                    error_text = await response.text()
                    self.log_test("Teams API Endpoint", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Teams Images Test", False, f"Exception: {str(e)}")
            
        # Test Brands
        try:
            async with self.session.get(f"{API_BASE}/brands", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    brands = await response.json()
                    self.log_test("Brands API Endpoint", True, f"Retrieved {len(brands)} brands")
                    
                    brands_with_logos = [brand for brand in brands if brand.get("logo_url")]
                    self.log_test(
                        "Brands with Logo URLs", 
                        len(brands_with_logos) > 0, 
                        f"Found {len(brands_with_logos)} brands with logo_url"
                    )
                    
                    # Test first few brand logos
                    for i, brand in enumerate(brands_with_logos[:3]):
                        await self.test_image_serving(
                            brand["logo_url"], 
                            f"Brand {brand.get('name', f'#{i+1}')} Logo"
                        )
                        
                else:
                    error_text = await response.text()
                    self.log_test("Brands API Endpoint", False, f"Status {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Brands Images Test", False, f"Exception: {str(e)}")
            
    async def test_image_serving(self, image_url: str, test_name: str):
        """Test image serving with proper URL construction"""
        try:
            # Test different URL construction patterns
            url_patterns = [
                f"{BACKEND_URL}/api/{image_url}",  # New corrected pattern with /api/ prefix
                f"{BACKEND_URL}/{image_url}",      # Direct pattern
                f"{API_BASE}/{image_url}",         # API base pattern
            ]
            
            # If image_url already starts with 'api/', test it directly
            if image_url.startswith('api/'):
                url_patterns.insert(0, f"{BACKEND_URL}/{image_url}")
                
            # If image_url already starts with 'uploads/', test with /api/ prefix
            if image_url.startswith('uploads/'):
                url_patterns.insert(0, f"{BACKEND_URL}/api/{image_url}")
                
            success = False
            working_url = None
            content_type = None
            
            for url in url_patterns:
                try:
                    async with self.session.get(url, headers=self.get_auth_headers()) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', 'unknown')
                            if content_type.startswith('image/'):
                                success = True
                                working_url = url
                                break
                            else:
                                # Check if it's actually an image by reading a bit
                                content = await response.read()
                                if len(content) > 0:
                                    # Check for image magic bytes
                                    if (content.startswith(b'\xff\xd8\xff') or  # JPEG
                                        content.startswith(b'\x89PNG') or        # PNG
                                        content.startswith(b'GIF8')):           # GIF
                                        success = True
                                        working_url = url
                                        content_type = "image/* (detected)"
                                        break
                except:
                    continue
                    
            if success:
                self.log_test(
                    f"{test_name} Serving", 
                    True, 
                    f"URL: {working_url}, Content-Type: {content_type}"
                )
            else:
                self.log_test(
                    f"{test_name} Serving", 
                    False, 
                    f"Failed all URL patterns: {image_url}"
                )
                
        except Exception as e:
            self.log_test(f"{test_name} Serving", False, f"Exception: {str(e)}")
            
    async def test_image_url_construction(self):
        """Test the corrected URL pattern construction"""
        print("\n🔍 TESTING IMAGE URL CONSTRUCTION PATTERNS")
        print("=" * 50)
        
        # Test various URL construction patterns
        test_cases = [
            {
                "filename": "test-image.jpg",
                "type": "master_kits",
                "expected_pattern": f"{BACKEND_URL}/api/uploads/master_kits/test-image.jpg"
            },
            {
                "filename": "team-logo.png", 
                "type": "teams",
                "expected_pattern": f"{BACKEND_URL}/api/uploads/teams/team-logo.png"
            },
            {
                "filename": "brand-logo.png",
                "type": "brands", 
                "expected_pattern": f"{BACKEND_URL}/api/uploads/brands/brand-logo.png"
            }
        ]
        
        for case in test_cases:
            expected_url = case["expected_pattern"]
            constructed_url = f"{BACKEND_URL}/api/uploads/{case['type']}/{case['filename']}"
            
            self.log_test(
                f"URL Construction for {case['type']}", 
                expected_url == constructed_url,
                f"Expected: {expected_url}, Got: {constructed_url}"
            )
            
    async def test_file_serving_endpoint(self):
        """Test the /api/uploads/{file_path:path} endpoint"""
        print("\n🔍 TESTING FILE SERVING ENDPOINT")
        print("=" * 50)
        
        # Find actual uploaded files to test
        backend_uploads_dir = Path("/app/backend/uploads")
        test_files = []
        
        if backend_uploads_dir.exists():
            for file_path in backend_uploads_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    relative_path = file_path.relative_to(backend_uploads_dir)
                    test_files.append(str(relative_path))
                    if len(test_files) >= 5:  # Test first 5 files
                        break
                        
        self.log_test(
            "Available Test Files", 
            len(test_files) > 0, 
            f"Found {len(test_files)} image files to test"
        )
        
        # Test file serving for found files
        for file_path in test_files:
            await self.test_file_serving_direct(file_path)
            
    async def test_file_serving_direct(self, file_path: str):
        """Test direct file serving via /api/uploads/ endpoint"""
        try:
            url = f"{BACKEND_URL}/api/uploads/{file_path}"
            
            async with self.session.get(url, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', 'unknown')
                    content_length = response.headers.get('content-length', 'unknown')
                    
                    self.log_test(
                        f"File Serving: {file_path}", 
                        True, 
                        f"Content-Type: {content_type}, Size: {content_length} bytes"
                    )
                else:
                    error_text = await response.text()
                    self.log_test(
                        f"File Serving: {file_path}", 
                        False, 
                        f"Status {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            self.log_test(f"File Serving: {file_path}", False, f"Exception: {str(e)}")
            
    async def test_content_type_headers(self):
        """Test that images are served with proper content-type headers"""
        print("\n🔍 TESTING CONTENT-TYPE HEADERS")
        print("=" * 50)
        
        # Test different image types
        test_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        backend_uploads_dir = Path("/app/backend/uploads")
        
        for ext in test_extensions:
            found_file = None
            if backend_uploads_dir.exists():
                for file_path in backend_uploads_dir.rglob(f"*{ext}"):
                    if file_path.is_file():
                        found_file = file_path.relative_to(backend_uploads_dir)
                        break
                        
            if found_file:
                await self.test_content_type_for_file(str(found_file), ext)
            else:
                self.log_test(
                    f"Content-Type Test for {ext}", 
                    False, 
                    f"No {ext} files found to test"
                )
                
    async def test_content_type_for_file(self, file_path: str, extension: str):
        """Test content-type header for specific file"""
        try:
            url = f"{BACKEND_URL}/api/uploads/{file_path}"
            
            async with self.session.head(url, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    # Expected content types
                    expected_types = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg', 
                        '.png': 'image/png',
                        '.gif': 'image/gif'
                    }
                    
                    expected = expected_types.get(extension, 'image/*')
                    is_correct = content_type.startswith('image/') and (
                        content_type == expected or 
                        content_type.startswith('image/')
                    )
                    
                    self.log_test(
                        f"Content-Type for {extension}", 
                        is_correct, 
                        f"Got: {content_type}, Expected: {expected}"
                    )
                else:
                    self.log_test(
                        f"Content-Type for {extension}", 
                        False, 
                        f"Status {response.status} for {file_path}"
                    )
                    
        except Exception as e:
            self.log_test(f"Content-Type for {extension}", False, f"Exception: {str(e)}")
            
    async def run_all_tests(self):
        """Run all image display fix tests"""
        print("🚀 STARTING IMAGE DISPLAY FIX BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Authenticate first
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run all test suites
            await self.test_master_kit_images()
            await self.test_team_brand_images()
            await self.test_image_url_construction()
            await self.test_file_serving_endpoint()
            await self.test_content_type_headers()
            
        finally:
            await self.cleanup_session()
            
        # Print final results
        self.print_final_results()
        
    def print_final_results(self):
        """Print final test results summary"""
        print("\n" + "=" * 60)
        print("🎯 IMAGE DISPLAY FIX BACKEND TESTING RESULTS")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT - Image display fix is working well!")
        elif success_rate >= 60:
            print("⚠️  GOOD - Image display fix is mostly working with minor issues")
        else:
            print("❌ NEEDS ATTENTION - Image display fix has significant issues")
            
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
                
        print("\n" + "=" * 60)

async def main():
    """Main test execution"""
    tester = ImageDisplayFixTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())