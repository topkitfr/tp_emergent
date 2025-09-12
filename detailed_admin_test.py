#!/usr/bin/env python3
"""
Test détaillé pour analyser la structure complète des réponses admin
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"

# Credentials admin
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def detailed_admin_analysis():
    """Analyse détaillée des endpoints admin"""
    
    print("🔬 ANALYSE DÉTAILLÉE DES ENDPOINTS ADMIN")
    print("=" * 60)
    
    # Authentification
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Échec authentification: {response.text}")
        return
        
    auth_data = response.json()
    token = auth_data.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"✅ Authentifié en tant qu'admin")
    
    # 1. Analyse complète de /api/admin/beta/requests
    print("\n📋 ANALYSE COMPLÈTE /api/admin/beta/requests")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/beta/requests", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Structure complète de la réponse:")
            print(json.dumps(data, indent=2, default=str))
            
            # Vérification spécifique
            requests_list = data.get('requests', [])
            print(f"\n📈 Analyse des demandes:")
            print(f"   - Nombre total: {len(requests_list)}")
            print(f"   - Total indiqué: {data.get('total', 'N/A')}")
            print(f"   - Filtre appliqué: {data.get('filter', 'N/A')}")
            
            if len(requests_list) == 4:
                print(f"✅ Nombre correct de demandes beta (4)")
                
                # Analyser chaque demande
                for i, request in enumerate(requests_list, 1):
                    print(f"\n   📝 Demande {i}:")
                    print(f"      - ID: {request.get('id', 'N/A')}")
                    print(f"      - Email: {request.get('email', 'N/A')}")
                    print(f"      - Nom: {request.get('first_name', 'N/A')} {request.get('last_name', 'N/A')}")
                    print(f"      - Status: {request.get('status', 'N/A')}")
                    print(f"      - Date: {request.get('created_at', 'N/A')}")
                    
            else:
                print(f"⚠️  Nombre inattendu: {len(requests_list)} (attendu: 4)")
                
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 2. Investigation approfondie de /api/admin/jerseys/pending
    print("\n👕 INVESTIGATION /api/admin/jerseys/pending")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers de réponse: {dict(response.headers)}")
        print(f"Contenu de la réponse: {response.text}")
        
        # Test avec différentes variations d'headers
        print(f"\n🔧 Test avec headers alternatifs:")
        
        # Test 1: Sans Bearer prefix
        alt_headers1 = {"Authorization": token}
        response1 = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=alt_headers1)
        print(f"   Sans 'Bearer': {response1.status_code}")
        
        # Test 2: Avec Content-Type
        alt_headers2 = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response2 = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=alt_headers2)
        print(f"   Avec Content-Type: {response2.status_code}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 3. Test de tous les endpoints admin pour comparaison
    print("\n🔍 COMPARAISON TOUS LES ENDPOINTS ADMIN")
    print("-" * 50)
    
    admin_endpoints = [
        "/admin/beta/requests",
        "/admin/jerseys/pending", 
        "/admin/users",
        "/admin/traffic-stats",
        "/admin/activities"
    ]
    
    for endpoint in admin_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"{status_icon} {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Type: Liste avec {len(data)} éléments")
                    elif isinstance(data, dict):
                        print(f"   Type: Dict avec clés: {list(data.keys())}")
                    else:
                        print(f"   Type: {type(data)}")
                except:
                    print(f"   Réponse non-JSON")
            else:
                print(f"   Erreur: {response.text}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    # 4. Test du endpoint profile pour vérifier le token
    print("\n🔐 VÉRIFICATION TOKEN AVEC ENDPOINTS UTILISATEUR")
    print("-" * 50)
    
    user_endpoints = [
        "/users/profile",
        "/auth/profile", 
        "/users/me"
    ]
    
    for endpoint in user_endpoints:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"{status_icon} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                profile = response.json()
                print(f"   Rôle: {profile.get('role', 'N/A')}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 FIN DE L'ANALYSE DÉTAILLÉE")

if __name__ == "__main__":
    detailed_admin_analysis()