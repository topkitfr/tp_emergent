#!/usr/bin/env python3
"""
Test Team and Brand Logo URLs
=============================

Test the actual team and brand logo URLs to see which pattern works.
"""

import asyncio
import aiohttp
import os

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jersey-collab-1.preview.emergentagent.com')

async def test_logo_urls():
    """Test team and brand logo URLs"""
    
    # Test URLs from investigation
    test_urls = [
        # PSG Logo
        f"{BACKEND_URL}/api/image_uploaded_1757682307853",
        f"{BACKEND_URL}/api/uploads/image_uploaded_1757682307853", 
        f"{BACKEND_URL}/image_uploaded_1757682307853",
        f"{BACKEND_URL}/api/uploads/teams/image_uploaded_1757682307853",
        
        # AC Milan Logo
        f"{BACKEND_URL}/api/image_uploaded_1757775656853",
        f"{BACKEND_URL}/api/uploads/image_uploaded_1757775656853",
        f"{BACKEND_URL}/image_uploaded_1757775656853",
        f"{BACKEND_URL}/api/uploads/teams/image_uploaded_1757775656853",
        
        # Qatar Airways Logo
        f"{BACKEND_URL}/api/image_uploaded_1757683563379",
        f"{BACKEND_URL}/api/uploads/image_uploaded_1757683563379",
        f"{BACKEND_URL}/image_uploaded_1757683563379",
        f"{BACKEND_URL}/api/uploads/brands/image_uploaded_1757683563379",
        
        # Nike Logo
        f"{BACKEND_URL}/api/image_uploaded_1757683514243",
        f"{BACKEND_URL}/api/uploads/image_uploaded_1757683514243",
        f"{BACKEND_URL}/image_uploaded_1757683514243",
        f"{BACKEND_URL}/api/uploads/brands/image_uploaded_1757683514243",
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in test_urls:
            try:
                async with session.get(url) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', 'unknown')
                    
                    if status == 200 and content_type.startswith('image/'):
                        print(f"✅ WORKING: {url}")
                        print(f"   Status: {status}, Content-Type: {content_type}")
                    elif status == 200:
                        print(f"⚠️  RESPONSE: {url}")
                        print(f"   Status: {status}, Content-Type: {content_type}")
                    else:
                        print(f"❌ FAILED: {url}")
                        print(f"   Status: {status}")
                        
            except Exception as e:
                print(f"❌ ERROR: {url}")
                print(f"   Exception: {str(e)}")
                
            print()

if __name__ == "__main__":
    asyncio.run(test_logo_urls())