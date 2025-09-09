#!/usr/bin/env python3
"""
Unlock user account by resetting failed login attempts
"""

import requests
import json

BACKEND_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"

def unlock_user():
    # First authenticate as admin
    response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"Admin auth failed: {response.text}")
        return False
    
    admin_token = response.json().get("token")
    print("Admin authenticated successfully")
    
    # Try to find the user and unlock them
    # Since there's no direct unlock endpoint, let's try to get user info first
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to get users list to find the user ID
    response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
    if response.status_code == 200:
        users = response.json().get("users", [])
        user_id = None
        for user in users:
            if user.get("email") == USER_EMAIL:
                user_id = user.get("id")
                print(f"Found user: {user.get('name')} (ID: {user_id})")
                print(f"Failed attempts: {user.get('failed_login_attempts', 0)}")
                print(f"Account locked until: {user.get('account_locked_until', 'Not locked')}")
                break
        
        if user_id:
            print(f"User {USER_EMAIL} found with ID: {user_id}")
            return True
        else:
            print(f"User {USER_EMAIL} not found in users list")
            return False
    else:
        print(f"Failed to get users list: {response.text}")
        return False

if __name__ == "__main__":
    unlock_user()