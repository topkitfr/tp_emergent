#!/usr/bin/env python3
"""
Test spécifique pour les endpoints admin beta requests
Focus sur l'identification du problème d'accès aux demandes beta
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-tracker.preview.emergentagent.com/api"

# Credentials admin
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def test_admin_beta_requests():
    """Test complet des endpoints admin pour les demandes beta"""
    
    print("🔍 TEST ADMIN BETA REQUESTS - DIAGNOSTIC COMPLET")
    print("=" * 60)
    
    # 1. Test authentification admin
    print("\n1️⃣ TEST AUTHENTIFICATION ADMIN")
    print("-" * 40)
    
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("token")
            user_info = auth_data.get("user", {})
            
            print(f"✅ Authentification réussie")
            print(f"   - Nom: {user_info.get('name')}")
            print(f"   - Email: {user_info.get('email')}")
            print(f"   - Rôle: {user_info.get('role')}")
            print(f"   - ID: {user_info.get('id')}")
            print(f"   - Token: {token[:50]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
        else:
            print(f"❌ Échec authentification: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erreur authentification: {e}")
        return
    
    # 2. Test GET /api/admin/beta/requests
    print("\n2️⃣ TEST GET /api/admin/beta/requests")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/beta/requests", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            beta_requests = response.json()
            print(f"✅ Endpoint accessible")
            print(f"   - Type de réponse: {type(beta_requests)}")
            
            if isinstance(beta_requests, list):
                print(f"   - Nombre de demandes: {len(beta_requests)}")
                
                if len(beta_requests) > 0:
                    print(f"   - Structure première demande:")
                    first_request = beta_requests[0]
                    for key, value in first_request.items():
                        print(f"     * {key}: {value}")
                        
                    # Vérifier s'il y a 4 demandes comme attendu
                    if len(beta_requests) == 4:
                        print(f"✅ Nombre correct de demandes beta (4)")
                    else:
                        print(f"⚠️  Nombre inattendu de demandes: {len(beta_requests)} (attendu: 4)")
                        
                else:
                    print(f"⚠️  Aucune demande beta trouvée")
                    
            elif isinstance(beta_requests, dict):
                print(f"   - Clés de la réponse: {list(beta_requests.keys())}")
                if 'requests' in beta_requests:
                    requests_list = beta_requests['requests']
                    print(f"   - Nombre de demandes dans 'requests': {len(requests_list)}")
                    
        elif response.status_code == 403:
            print(f"❌ ERREUR 403 - Accès refusé")
            print(f"   - Message: {response.text}")
            print(f"   - Headers de la requête: {headers}")
            
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
    
    # 3. Test GET /api/admin/jerseys/pending
    print("\n3️⃣ TEST GET /api/admin/jerseys/pending")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            pending_jerseys = response.json()
            print(f"✅ Endpoint accessible")
            print(f"   - Type de réponse: {type(pending_jerseys)}")
            
            if isinstance(pending_jerseys, list):
                print(f"   - Nombre de maillots en attente: {len(pending_jerseys)}")
            elif isinstance(pending_jerseys, dict):
                print(f"   - Clés de la réponse: {list(pending_jerseys.keys())}")
                
        elif response.status_code == 403:
            print(f"❌ ERREUR 403 - Accès refusé (confirmé selon les logs)")
            print(f"   - Message: {response.text}")
            
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
    
    # 4. Test autres endpoints admin pour diagnostic complet
    print("\n4️⃣ TEST AUTRES ENDPOINTS ADMIN")
    print("-" * 40)
    
    admin_endpoints = [
        "/admin/users",
        "/admin/traffic-stats", 
        "/admin/activities"
    ]
    
    for endpoint in admin_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
            
            if response.status_code == 403:
                print(f"   - ERREUR 403: {response.text}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Erreur - {e}")
    
    # 5. Vérification du token JWT
    print("\n5️⃣ VÉRIFICATION TOKEN JWT")
    print("-" * 40)
    
    try:
        # Test avec endpoint profile pour vérifier le token
        response = requests.get(f"{BACKEND_URL}/users/profile", headers=headers)
        print(f"Profile endpoint: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Token valide")
            print(f"   - Rôle dans profile: {profile.get('role')}")
        else:
            print(f"❌ Token invalide: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur vérification token: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 FIN DU TEST DIAGNOSTIC")

if __name__ == "__main__":
    test_admin_beta_requests()