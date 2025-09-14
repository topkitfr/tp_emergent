#!/usr/bin/env python3
"""
Test JWT validation specifically
"""

import requests

BASE_URL = "https://jersey-collab-1.preview.emergentagent.com/api"

def test_jwt_validation():
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    print("Testing profile endpoint without Authorization header...")
    response = session.get(f"{BASE_URL}/profile")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    print("\nTesting profile endpoint with invalid token...")
    session.headers.update({'Authorization': 'Bearer invalid_token_here'})
    response2 = session.get(f"{BASE_URL}/profile")
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text[:200]}")

if __name__ == "__main__":
    test_jwt_validation()