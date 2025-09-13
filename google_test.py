#!/usr/bin/env python3
"""
Test Google OAuth specifically
"""

import requests

BASE_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"

def test_google_oauth():
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    print("Testing Google OAuth redirect...")
    response = session.get(f"{BASE_URL}/auth/google", allow_redirects=False)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    if response.status_code == 302:
        print(f"Redirect URL: {response.headers.get('location', 'No location header')}")
        print("✅ Google OAuth redirect working")
    else:
        print(f"Response: {response.text[:200]}")

if __name__ == "__main__":
    test_google_oauth()