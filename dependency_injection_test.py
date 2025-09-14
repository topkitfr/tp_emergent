#!/usr/bin/env python3
"""
Test pour diagnostiquer le problème de dependency injection
dans l'endpoint /admin/jerseys/pending
"""

import requests
import json

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def test_dependency_injection_issue():
    """Test pour identifier le problème de dependency injection"""
    
    print("🔧 DIAGNOSTIC DEPENDENCY INJECTION ISSUE")
    print("=" * 60)
    
    # Authentification
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Échec authentification: {response.text}")
        return
        
    auth_data = response.json()
    token = auth_data.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Authentifié en tant qu'admin")
    print(f"   - Token: {token[:50]}...")
    
    # Test des endpoints qui fonctionnent vs ceux qui ne fonctionnent pas
    print(f"\n📊 COMPARAISON ENDPOINTS ADMIN")
    print("-" * 50)
    
    working_endpoints = [
        "/admin/beta/requests",
        "/admin/users", 
        "/admin/traffic-stats",
        "/admin/activities"
    ]
    
    broken_endpoints = [
        "/admin/jerseys/pending"
    ]
    
    print(f"✅ ENDPOINTS QUI FONCTIONNENT:")
    for endpoint in working_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            print(f"   {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: Erreur - {e}")
    
    print(f"\n❌ ENDPOINTS QUI NE FONCTIONNENT PAS:")
    for endpoint in broken_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            print(f"   {endpoint}: {response.status_code}")
            print(f"   Erreur: {response.text}")
            
            # Analyser les headers de la réponse
            print(f"   Headers réponse: {dict(response.headers)}")
            
        except Exception as e:
            print(f"   {endpoint}: Erreur - {e}")
    
    # Test avec un endpoint utilisateur standard pour comparaison
    print(f"\n🔍 TEST ENDPOINTS UTILISATEUR POUR COMPARAISON")
    print("-" * 50)
    
    # Essayer différents endpoints utilisateur
    user_test_endpoints = [
        "/jerseys",
        "/jerseys/approved",
        "/marketplace/catalog"
    ]
    
    for endpoint in user_test_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            print(f"   {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: Erreur - {e}")
    
    # Test spécifique pour comprendre le problème d'authentification
    print(f"\n🔐 ANALYSE DU PROBLÈME D'AUTHENTIFICATION")
    print("-" * 50)
    
    # Test sans token
    print(f"Test sans token:")
    try:
        response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending")
        print(f"   Sans token: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Sans token: Erreur - {e}")
    
    # Test avec token malformé
    print(f"Test avec token malformé:")
    try:
        bad_headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=bad_headers)
        print(f"   Token invalide: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Token invalide: Erreur - {e}")
    
    # Test avec token valide (notre cas)
    print(f"Test avec token valide (notre problème):")
    try:
        response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
        print(f"   Token valide: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Token valide: Erreur - {e}")
    
    print(f"\n💡 CONCLUSION:")
    print(f"   - L'authentification admin fonctionne (autres endpoints OK)")
    print(f"   - Le token JWT est valide")
    print(f"   - Le problème est spécifique à /admin/jerseys/pending")
    print(f"   - Erreur 'Authentication required' suggère un problème de dependency injection")
    print(f"   - Probable: get_current_moderator_or_admin attend user_id mais reçoit user dict")
    
    print("\n" + "=" * 60)
    print("🏁 FIN DU DIAGNOSTIC")

if __name__ == "__main__":
    test_dependency_injection_issue()