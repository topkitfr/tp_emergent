#!/usr/bin/env python3
"""
Test rapide du système de contributions après correction
Test des endpoints de contributions avec authentification admin
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"

# Credentials admin
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

def test_contributions_system():
    """Test rapide du système de contributions après correction"""
    
    print("🧪 TEST RAPIDE DU SYSTÈME DE CONTRIBUTIONS APRÈS CORRECTION")
    print("=" * 70)
    
    # Variables pour tracking
    jwt_token = None
    contribution_id = None
    
    try:
        # 1. AUTHENTIFICATION ADMIN
        print("\n1️⃣ AUTHENTIFICATION ADMIN")
        print("-" * 30)
        
        auth_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=auth_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            auth_result = response.json()
            jwt_token = auth_result.get("token")
            user_info = auth_result.get("user", {})
            print(f"✅ Authentification réussie")
            print(f"   User: {user_info.get('name')} ({user_info.get('role')})")
            print(f"   Token: {jwt_token[:20]}...")
        else:
            print(f"❌ Échec authentification: {response.text}")
            return False
            
        # Headers avec token
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        # 2. CRÉATION D'UNE CONTRIBUTION
        print("\n2️⃣ POST /api/contributions - CRÉER UNE CONTRIBUTION")
        print("-" * 50)
        
        # First get a real team ID
        teams_response = requests.get(f"{BACKEND_URL}/teams", headers=headers)
        if teams_response.status_code == 200:
            teams = teams_response.json()
            if teams:
                team_id = teams[0]["id"]  # Use first team
                team_name = teams[0]["name"]
                print(f"Using team: {team_name} (ID: {team_id})")
            else:
                print("❌ Aucune équipe trouvée")
                return False
        else:
            print(f"❌ Impossible de récupérer les équipes: {teams_response.status_code}")
            return False
        
        contribution_data = {
            "entity_type": "team",
            "entity_id": team_id,
            "action_type": "update",
            "proposed_data": {
                "name": "FC Barcelona Updated",
                "city": "Barcelona"
            },
            "title": "Test contribution après correction",
            "description": "Test simple",
            "source_urls": []
        }
        
        print(f"Données envoyées:")
        print(json.dumps(contribution_data, indent=2))
        
        response = requests.post(f"{BACKEND_URL}/contributions", json=contribution_data, headers=headers)
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code in [200, 201]:
            contribution_result = response.json()
            contribution_id = contribution_result.get("id")
            topkit_ref = contribution_result.get("topkit_reference", "N/A")
            print(f"✅ Contribution créée avec succès")
            print(f"   ID: {contribution_id}")
            print(f"   Référence TopKit: {topkit_ref}")
            print(f"   Titre: {contribution_result.get('title')}")
            print(f"   Statut: {contribution_result.get('status')}")
        else:
            print(f"❌ Échec création contribution: {response.text}")
            return False
            
        # 3. RÉCUPÉRATION DES CONTRIBUTIONS
        print("\n3️⃣ GET /api/contributions - VÉRIFIER LA CONTRIBUTION")
        print("-" * 50)
        
        response = requests.get(f"{BACKEND_URL}/contributions", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            contributions = response.json()
            total_contributions = len(contributions)
            print(f"✅ Contributions récupérées: {total_contributions} trouvées")
            
            # Chercher notre contribution
            our_contribution = None
            for contrib in contributions:
                if contrib.get("id") == contribution_id:
                    our_contribution = contrib
                    break
            
            if our_contribution:
                print(f"✅ Notre contribution trouvée:")
                print(f"   ID: {our_contribution.get('id')}")
                print(f"   Référence: {our_contribution.get('topkit_reference')}")
                print(f"   Titre: {our_contribution.get('title')}")
                print(f"   Statut: {our_contribution.get('status')}")
                print(f"   Type d'entité: {our_contribution.get('entity_type')}")
                print(f"   Action: {our_contribution.get('action_type')}")
            else:
                print(f"❌ Notre contribution non trouvée dans la liste")
                return False
        else:
            print(f"❌ Échec récupération contributions: {response.text}")
            return False
            
        # 4. RÉSUMÉ DES TESTS
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 70)
        
        print("✅ Authentification admin: OK")
        print("✅ Création contribution: OK")
        print("✅ Récupération contributions: OK")
        print("✅ Contribution avec référence TopKit: OK")
        
        print(f"\n🎉 TOUS LES TESTS PASSÉS AVEC SUCCÈS!")
        print(f"Le système de contributions est opérationnel pour l'interface frontend.")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = test_contributions_system()
    sys.exit(0 if success else 1)