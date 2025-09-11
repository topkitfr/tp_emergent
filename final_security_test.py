#!/usr/bin/env python3
"""
Final Comprehensive Security Test - All Enhanced Security Features
"""

import requests
import json
import uuid
from datetime import datetime

BASE_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"

def test_all_security_features():
    """Comprehensive test of all security features"""
    print("🔐 COMPREHENSIVE TOPKIT SECURITY FEATURES TEST")
    print("="*60)
    
    results = {
        "password_validation": False,
        "rate_limiting": False,
        "email_verification": False,
        "admin_bypass": False,
        "user_model_fields": False
    }
    
    session = requests.Session()
    
    # Test 1: Password Validation
    print("\n1️⃣ TESTING PASSWORD STRENGTH VALIDATION")
    weak_passwords = [
        ("123", "Too short"),
        ("password", "Common weak pattern"),
        ("abcdefgh", "Missing uppercase and numbers"),
        ("ABCDEFGH", "Missing lowercase and numbers"),
        ("Abcdefgh", "Missing numbers and special chars")
    ]
    
    validation_passed = 0
    for weak_pass, reason in weak_passwords:
        test_email = f"weakpass_{uuid.uuid4().hex[:6]}@test.com"
        response = session.post(f"{BASE_URL}/auth/register", json={
            "email": test_email,
            "password": weak_pass,
            "name": "Weak Password Test"
        })
        
        if response.status_code == 400:
            validation_passed += 1
            print(f"   ✅ Correctly rejected: {weak_pass} ({reason})")
        else:
            print(f"   ❌ Should have rejected: {weak_pass} ({reason})")
    
    # Test strong password
    strong_email = f"strongpass_{uuid.uuid4().hex[:6]}@test.com"
    strong_response = session.post(f"{BASE_URL}/auth/register", json={
        "email": strong_email,
        "password": "ValidPass456!",
        "name": "Strong Password Test"
    })
    
    if strong_response.status_code == 200:
        validation_passed += 1
        print(f"   ✅ Correctly accepted strong password")
    else:
        print(f"   ❌ Should have accepted strong password: {strong_response.text}")
    
    results["password_validation"] = validation_passed == 6
    print(f"   📊 Password Validation: {validation_passed}/6 tests passed")
    
    # Test 2: Rate Limiting
    print("\n2️⃣ TESTING RATE LIMITING")
    rate_session = requests.Session()  # Fresh session
    
    # Try to create accounts until rate limited
    accounts_created = 0
    rate_limited = False
    
    for i in range(5):
        rate_email = f"ratetest_{i}_{uuid.uuid4().hex[:6]}@test.com"
        response = rate_session.post(f"{BASE_URL}/auth/register", json={
            "email": rate_email,
            "password": "ValidPass456!",
            "name": f"Rate Test {i}"
        })
        
        if response.status_code == 200:
            accounts_created += 1
            print(f"   ✅ Account {i+1} created")
        elif response.status_code == 429:
            rate_limited = True
            print(f"   🚫 Rate limit triggered after {accounts_created} accounts")
            break
        else:
            print(f"   ❓ Unexpected response: {response.status_code}")
    
    results["rate_limiting"] = rate_limited and accounts_created <= 3
    print(f"   📊 Rate Limiting: {'✅ WORKING' if results['rate_limiting'] else '❌ NOT WORKING'}")
    
    # Test 3: Email Verification Workflow
    print("\n3️⃣ TESTING EMAIL VERIFICATION WORKFLOW")
    email_session = requests.Session()
    verify_email = f"emailverify_{uuid.uuid4().hex[:6]}@test.com"
    
    # Register account
    reg_response = email_session.post(f"{BASE_URL}/auth/register", json={
        "email": verify_email,
        "password": "ValidPass456!",
        "name": "Email Verify Test"
    })
    
    if reg_response.status_code == 200:
        reg_data = reg_response.json()
        user_data = reg_data.get("user", {})
        
        # Check email_verified is False
        if user_data.get("email_verified") == False:
            print("   ✅ Account created with email_verified=false")
            
            # Try login before verification
            login_before = email_session.post(f"{BASE_URL}/auth/login", json={
                "email": verify_email,
                "password": "ValidPass456!"
            })
            
            if login_before.status_code == 403:
                print("   ✅ Login blocked for unverified email")
                
                # Verify email if token available
                verification_link = reg_data.get("dev_verification_link")
                if verification_link and "token=" in verification_link:
                    token = verification_link.split("token=")[1]
                    
                    verify_response = email_session.post(f"{BASE_URL}/auth/verify-email", params={"token": token})
                    
                    if verify_response.status_code == 200:
                        print("   ✅ Email verification successful")
                        
                        # Try login after verification
                        login_after = email_session.post(f"{BASE_URL}/auth/login", json={
                            "email": verify_email,
                            "password": "ValidPass456!"
                        })
                        
                        if login_after.status_code == 200:
                            print("   ✅ Login successful after verification")
                            results["email_verification"] = True
                        else:
                            print("   ❌ Login failed after verification")
                    else:
                        print("   ❌ Email verification failed")
                else:
                    print("   ❌ No verification token available")
            else:
                print("   ❌ Login should be blocked for unverified email")
        else:
            print("   ❌ Account should have email_verified=false")
    else:
        print(f"   ❌ Account registration failed: {reg_response.status_code}")
    
    print(f"   📊 Email Verification: {'✅ WORKING' if results['email_verification'] else '❌ NOT WORKING'}")
    
    # Test 4: Admin Bypass
    print("\n4️⃣ TESTING ADMIN EMAIL VERIFICATION BYPASS")
    admin_session = requests.Session()
    
    admin_response = admin_session.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if admin_response.status_code == 200:
        admin_data = admin_response.json()
        admin_user = admin_data.get("user", {})
        
        if admin_user.get("role") == "admin":
            print("   ✅ Admin login successful (bypasses email verification)")
            results["admin_bypass"] = True
        else:
            print("   ❌ Admin role not properly set")
    else:
        print(f"   ❌ Admin login failed: {admin_response.status_code}")
    
    print(f"   📊 Admin Bypass: {'✅ WORKING' if results['admin_bypass'] else '❌ NOT WORKING'}")
    
    # Test 5: User Model Security Fields
    print("\n5️⃣ TESTING USER MODEL SECURITY FIELDS")
    if strong_response.status_code == 200:
        strong_data = strong_response.json()
        user_data = strong_data.get("user", {})
        
        required_fields = ["id", "email", "name", "role", "email_verified"]
        fields_present = 0
        
        for field in required_fields:
            if field in user_data:
                fields_present += 1
                print(f"   ✅ Field '{field}' present: {user_data[field]}")
            else:
                print(f"   ❌ Field '{field}' missing")
        
        results["user_model_fields"] = fields_present == len(required_fields)
        print(f"   📊 User Model Fields: {fields_present}/{len(required_fields)} present")
    else:
        print("   ❌ Cannot test user model fields - no successful registration")
    
    # Final Summary
    print("\n" + "="*60)
    print("🎯 COMPREHENSIVE SECURITY TEST SUMMARY")
    print("="*60)
    
    passed_features = sum(results.values())
    total_features = len(results)
    success_rate = (passed_features / total_features) * 100
    
    print(f"📊 OVERALL RESULTS:")
    print(f"   Features Tested: {total_features}")
    print(f"   Features Working: {passed_features}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print()
    
    print("📋 FEATURE BREAKDOWN:")
    for feature, working in results.items():
        status = "✅ WORKING" if working else "❌ NOT WORKING"
        feature_name = feature.replace("_", " ").title()
        print(f"   {status}: {feature_name}")
    
    print()
    if success_rate >= 90:
        print("🎉 EXCELLENT: TopKit security features are working excellently!")
    elif success_rate >= 75:
        print("✅ GOOD: TopKit security features are mostly working.")
    else:
        print("⚠️ NEEDS ATTENTION: Some security features need fixes.")
    
    print("="*60)
    
    return results, success_rate

if __name__ == "__main__":
    test_all_security_features()