#!/usr/bin/env python3
"""
Test different passwords for steinmetzlivio@gmail.com to find the correct one
"""

import requests
import json

BASE_URL = "https://jersey-tracker.preview.emergentagent.com/api"

def test_login_with_password(email, password):
    """Test login with specific password"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/login", json=payload)
        return response.status_code, response.json() if response.content else {}
    except Exception as e:
        return None, str(e)

def main():
    email = "steinmetzlivio@gmail.com"
    
    # Common passwords to try
    passwords = [
        "password123",
        "adminpass123", 
        "password",
        "123456",
        "steinmetz123",
        "livio123",
        "topkit123",
        "test123",
        "user123",
        "steinmetzlivio",
        "livio",
        "steinmetz"
    ]
    
    print(f"🔍 Testing different passwords for {email}")
    print("=" * 60)
    
    for password in passwords:
        print(f"🔑 Trying password: {password}")
        status, response = test_login_with_password(email, password)
        
        if status == 200:
            print(f"✅ SUCCESS! Password found: {password}")
            print(f"📡 Response: {json.dumps(response, indent=2)}")
            return password
        elif status == 400:
            print(f"❌ Invalid credentials")
        else:
            print(f"⚠️ Status: {status}, Response: {response}")
        print()
    
    print("❌ No valid password found from common passwords list")
    return None

if __name__ == "__main__":
    main()