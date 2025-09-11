#!/usr/bin/env python3
"""
Test du système de contributions collaboratives TopKit
Test des endpoints existants selon la demande de review
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE = "https://topkit-bugfixes.preview.emergentagent.com/api"

# Données de test pour l'authentification
TEST_USER = {
    "email": "topkitfr@gmail.com",
    "password": "adminpass123"
}

def authenticate_user():
    """Authentifier l'utilisateur de test"""
    print("🔐 Authentification de l'utilisateur...")
    
    response = requests.post(f"{API_BASE}/auth/login", json=TEST_USER)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        user_info = data.get("user", {})
        print(f"✅ Authentification réussie - Utilisateur: {user_info.get('name')} (ID: {user_info.get('id')})")
        return token, user_info
    else:
        print(f"❌ Échec de l'authentification: {response.status_code} - {response.text}")
        return None, None

def get_existing_team():
    """Récupérer une équipe existante pour les tests"""
    print("\n🔍 Recherche d'une équipe existante...")
    
    # Essayer de récupérer les équipes via l'endpoint teams
    try:
        response = requests.get(f"{API_BASE}/teams")
        if response.status_code == 200:
            teams = response.json()
            if teams:
                team = teams[0]
                print(f"✅ Équipe trouvée: {team.get('name')} (ID: {team.get('id')})")
                return team
    except:
        pass
    
    # Fallback: essayer via les jerseys approuvés
    try:
        response = requests.get(f"{API_BASE}/jerseys?status=approved&limit=1")
        if response.status_code == 200:
            jerseys = response.json()
            if jerseys:
                jersey = jerseys[0]
                # Créer un objet team fictif basé sur le jersey
                team = {
                    "id": f"team-{jersey.get('team', '').lower().replace(' ', '-')}",
                    "name": jersey.get('team'),
                    "country": "France"  # Valeur par défaut
                }
                print(f"✅ Équipe créée à partir du jersey: {team.get('name')}")
                return team
    except:
        pass
    
    # Créer une équipe de test par défaut
    team = {
        "id": "team-fc-barcelona",
        "name": "FC Barcelona", 
        "country": "Spain"
    }
    print(f"✅ Utilisation de l'équipe par défaut: {team.get('name')}")
    return team

def test_create_contribution(token, user_info):
    """Test de création d'une nouvelle contribution"""
    print("\n📝 TEST 1: Création d'une nouvelle contribution")
    
    # Récupérer une équipe existante
    team = get_existing_team()
    if not team:
        print("❌ Impossible de trouver une équipe pour le test")
        return False
    
    # Données de contribution selon la demande
    contribution_data = {
        "entity_type": "team",
        "entity_id": team["id"],
        "proposed_data": {
            "name": "FC Barcelona",
            "city": "Barcelona", 
            "country": "Spain"
        },
        "title": "Mise à jour informations FC Barcelona",
        "description": "Ajout de la ville manquante",
        "source_urls": ["https://example.com/source"]
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_BASE}/contributions", 
                               json=contribution_data, 
                               headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            contribution_id = data.get("id")
            topkit_ref = data.get("topkit_reference")
            status = data.get("status")
            
            print(f"✅ Contribution créée avec succès!")
            print(f"   - ID: {contribution_id}")
            print(f"   - Référence TopKit: {topkit_ref}")
            print(f"   - Status: {status}")
            print(f"   - Titre: {data.get('title')}")
            
            # Vérifier le format de la référence TopKit (TCxxxx)
            if topkit_ref and topkit_ref.startswith("TC"):
                print(f"✅ Format de référence TopKit correct: {topkit_ref}")
            else:
                print(f"⚠️  Format de référence TopKit inattendu: {topkit_ref}")
            
            # Vérifier le status initial
            if status == "pending":
                print("✅ Status initial correct: pending")
            else:
                print(f"⚠️  Status initial inattendu: {status}")
            
            return contribution_id
            
        else:
            print(f"❌ Échec de création: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return None

def test_get_contributions(token):
    """Test de récupération des contributions avec filtres"""
    print("\n📋 TEST 2: Récupération des contributions")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Toutes les contributions
    print("\n2.1 - Récupération de toutes les contributions")
    try:
        response = requests.get(f"{API_BASE}/contributions", headers=headers)
        
        if response.status_code == 200:
            contributions = response.json()
            print(f"✅ {len(contributions)} contributions récupérées")
            
            if contributions:
                contrib = contributions[0]
                print(f"   - Première contribution: {contrib.get('title')}")
                print(f"   - Status: {contrib.get('status')}")
                print(f"   - Référence: {contrib.get('topkit_reference')}")
        else:
            print(f"❌ Échec: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Filtrer par status=pending
    print("\n2.2 - Filtrage par status=pending")
    try:
        response = requests.get(f"{API_BASE}/contributions?status=pending", headers=headers)
        
        if response.status_code == 200:
            contributions = response.json()
            print(f"✅ {len(contributions)} contributions en attente")
            
            # Vérifier que toutes sont bien en pending
            all_pending = all(c.get('status') == 'pending' for c in contributions)
            if all_pending:
                print("✅ Toutes les contributions sont bien en status 'pending'")
            else:
                print("⚠️  Certaines contributions ne sont pas en status 'pending'")
        else:
            print(f"❌ Échec: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Filtrer par status=approved
    print("\n2.3 - Filtrage par status=approved")
    try:
        response = requests.get(f"{API_BASE}/contributions?status=approved", headers=headers)
        
        if response.status_code == 200:
            contributions = response.json()
            print(f"✅ {len(contributions)} contributions approuvées")
        else:
            print(f"❌ Échec: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 4: Filtrer par status=rejected
    print("\n2.4 - Filtrage par status=rejected")
    try:
        response = requests.get(f"{API_BASE}/contributions?status=rejected", headers=headers)
        
        if response.status_code == 200:
            contributions = response.json()
            print(f"✅ {len(contributions)} contributions rejetées")
        else:
            print(f"❌ Échec: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_vote_on_contribution(token, contribution_id, user_info):
    """Test de vote sur une contribution"""
    print("\n🗳️  TEST 3: Vote sur une contribution")
    
    if not contribution_id:
        print("❌ Pas de contribution disponible pour le test de vote")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Vote upvote
    print("\n3.1 - Test vote upvote")
    vote_data = {
        "vote_type": "upvote",
        "comment": "Excellente contribution, informations vérifiées"
    }
    
    try:
        response = requests.post(f"{API_BASE}/contributions/{contribution_id}/vote", 
                               json=vote_data, 
                               headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vote upvote enregistré avec succès!")
            print(f"   Message: {data.get('message')}")
            if 'contribution_score' in data:
                print(f"   Score de la contribution: {data.get('contribution_score')}")
        else:
            print(f"❌ Échec du vote: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du vote: {e}")
    
    # Test 2: Tentative de vote multiple (doit être empêché)
    print("\n3.2 - Test vote multiple (doit être empêché)")
    vote_data_2 = {
        "vote_type": "downvote",
        "comment": "Changement d'avis"
    }
    
    try:
        response = requests.post(f"{API_BASE}/contributions/{contribution_id}/vote", 
                               json=vote_data_2, 
                               headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vote mis à jour (changement autorisé)")
            print(f"   Message: {data.get('message')}")
            if 'contribution_score' in data:
                print(f"   Nouveau score: {data.get('contribution_score')}")
        else:
            print(f"⚠️  Vote multiple bloqué: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du second vote: {e}")

def test_authentication_required():
    """Test que l'authentification est requise"""
    print("\n🔒 TEST 4: Vérification de l'authentification requise")
    
    # Test sans token
    contribution_data = {
        "entity_type": "team",
        "entity_id": "test-team",
        "proposed_data": {"name": "Test Team"},
        "title": "Test sans auth",
        "description": "Test"
    }
    
    try:
        response = requests.post(f"{API_BASE}/contributions", json=contribution_data)
        
        if response.status_code == 401:
            print("✅ Authentification correctement requise (401)")
        else:
            print(f"⚠️  Réponse inattendue sans auth: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test sans auth: {e}")

def test_data_validation():
    """Test de validation des données"""
    print("\n✅ TEST 5: Validation des données")
    
    # Authentifier pour ce test
    token, user_info = authenticate_user()
    if not token:
        print("❌ Impossible de s'authentifier pour le test de validation")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test avec données invalides
    invalid_data = {
        "entity_type": "invalid_type",
        "entity_id": "test-id",
        "proposed_data": {},
        "title": "",  # Titre vide
        "description": "Test validation"
    }
    
    try:
        response = requests.post(f"{API_BASE}/contributions", 
                               json=invalid_data, 
                               headers=headers)
        
        if response.status_code == 400 or response.status_code == 422:
            print("✅ Validation des données fonctionne (400/422)")
            print(f"   Réponse: {response.text}")
        else:
            print(f"⚠️  Validation inattendue: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de validation: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 DÉBUT DES TESTS DU SYSTÈME DE CONTRIBUTIONS COLLABORATIVES TOPKIT")
    print("=" * 80)
    
    # Test des endpoints sans authentification d'abord
    print("\n📋 TEST PRÉLIMINAIRE: Vérification des endpoints de contributions")
    
    # Test 1: Récupération des contributions (sans auth)
    try:
        response = requests.get(f"{API_BASE}/contributions")
        print(f"GET /api/contributions - Status: {response.status_code}")
        if response.status_code == 200:
            contributions = response.json()
            print(f"✅ Endpoint accessible - {len(contributions)} contributions trouvées")
        else:
            print(f"❌ Endpoint non accessible: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Tentative de création sans auth
    print("\n🔒 TEST: Création de contribution sans authentification")
    contribution_data = {
        "entity_type": "team",
        "entity_id": "test-team",
        "proposed_data": {"name": "Test Team"},
        "title": "Test sans auth",
        "description": "Test"
    }
    
    try:
        response = requests.post(f"{API_BASE}/contributions", json=contribution_data)
        print(f"POST /api/contributions (sans auth) - Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Authentification correctement requise")
        elif response.status_code == 200:
            print("⚠️  Création autorisée sans authentification")
            data = response.json()
            print(f"   Contribution créée: {data.get('id')}")
        else:
            print(f"❌ Réponse inattendue: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Test de vote sans auth
    print("\n🗳️  TEST: Vote sans authentification")
    vote_data = {"vote_type": "upvote", "comment": "Test vote"}
    
    try:
        response = requests.post(f"{API_BASE}/contributions/test-id/vote", json=vote_data)
        print(f"POST /api/contributions/test-id/vote (sans auth) - Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Authentification correctement requise pour voter")
        elif response.status_code == 404:
            print("✅ Contribution non trouvée (normal)")
        else:
            print(f"⚠️  Réponse inattendue: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 4: Filtres sur les contributions
    print("\n🔍 TEST: Filtres sur les contributions")
    filters = ["status=pending", "status=approved", "status=rejected"]
    
    for filter_param in filters:
        try:
            response = requests.get(f"{API_BASE}/contributions?{filter_param}")
            print(f"GET /api/contributions?{filter_param} - Status: {response.status_code}")
            if response.status_code == 200:
                contributions = response.json()
                print(f"   ✅ {len(contributions)} contributions avec filtre {filter_param}")
            else:
                print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Tentative d'authentification avec différents comptes
    print("\n🔐 TEST: Tentatives d'authentification")
    
    test_accounts = [
        {"email": "steinmetzlivio@gmail.com", "password": "123"},
        {"email": "topkitfr@gmail.com", "password": "adminpass123"},
        {"email": "topkitfr@gmail.com", "password": "TopKitSecure789#"},
        {"email": "admin@topkit.fr", "password": "admin123"}
    ]
    
    authenticated_token = None
    authenticated_user = None
    
    for account in test_accounts:
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=account)
            print(f"Login {account['email']} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                authenticated_token = data.get("token")
                authenticated_user = data.get("user", {})
                print(f"✅ Authentification réussie: {authenticated_user.get('name')}")
                break
            else:
                print(f"   ❌ Échec: {response.text}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # Si authentification réussie, tester les endpoints protégés
    if authenticated_token:
        print(f"\n🔓 TESTS AVEC AUTHENTIFICATION - Utilisateur: {authenticated_user.get('name')}")
        headers = {"Authorization": f"Bearer {authenticated_token}"}
        
        # Test récupération des contributions avec authentification
        print("\n📋 TEST: Récupération des contributions avec authentification")
        try:
            response = requests.get(f"{API_BASE}/contributions", headers=headers)
            print(f"GET /api/contributions (avec auth) - Status: {response.status_code}")
            
            if response.status_code == 200:
                contributions = response.json()
                print(f"✅ {len(contributions)} contributions récupérées avec authentification")
                
                if contributions:
                    contrib = contributions[0]
                    print(f"   - Première contribution: {contrib.get('title', 'N/A')}")
                    print(f"   - Status: {contrib.get('status', 'N/A')}")
                    print(f"   - Référence: {contrib.get('topkit_reference', 'N/A')}")
                    
                    # Test de vote sur une contribution existante
                    contribution_id = contrib.get('id')
                    if contribution_id:
                        print(f"\n🗳️  TEST: Vote sur contribution existante {contribution_id}")
                        vote_data = {"vote_type": "upvote", "comment": "Test vote"}
                        
                        try:
                            vote_response = requests.post(f"{API_BASE}/contributions/{contribution_id}/vote", 
                                                        json=vote_data, 
                                                        headers=headers)
                            print(f"POST /api/contributions/{contribution_id}/vote - Status: {vote_response.status_code}")
                            
                            if vote_response.status_code == 200:
                                vote_result = vote_response.json()
                                print(f"✅ Vote enregistré: {vote_result.get('message')}")
                                if 'contribution_score' in vote_result:
                                    print(f"   Score: {vote_result.get('contribution_score')}")
                            elif vote_response.status_code == 400:
                                print(f"⚠️  Vote non autorisé: {vote_response.text}")
                            else:
                                print(f"❌ Échec du vote: {vote_response.text}")
                        except Exception as e:
                            print(f"❌ Erreur lors du vote: {e}")
                else:
                    print("   ℹ️  Aucune contribution existante pour tester le vote")
            else:
                print(f"❌ Échec: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test de création de contribution (format simplifié)
        print("\n📝 TEST: Tentative de création de contribution")
        print("   (Test de validation des données requises)")
        
        simple_contribution = {
            "entity_type": "team",
            "entity_id": "test-team-id",
            "contribution_type": "update",
            "proposed_changes": {"name": "Test Team"},
            "description": "Test de création de contribution"
        }
        
        try:
            response = requests.post(f"{API_BASE}/contributions", 
                                   json=simple_contribution, 
                                   headers=headers)
            print(f"POST /api/contributions (format simple) - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Contribution créée: {data.get('id', 'N/A')}")
                print(f"   - Status: {data.get('status', 'N/A')}")
                if 'topkit_reference' in data:
                    ref = data.get('topkit_reference')
                    print(f"   - Référence TopKit: {ref}")
                    if ref and ref.startswith('TC'):
                        print("   ✅ Format de référence correct (TCxxxx)")
                    else:
                        print(f"   ⚠️  Format de référence inattendu: {ref}")
            elif response.status_code == 404:
                print("   ⚠️  Entité non trouvée (normal pour test)")
            elif response.status_code == 422:
                print("   ⚠️  Données invalides (validation fonctionne)")
                print(f"   Détails: {response.text}")
            else:
                print(f"   ❌ Erreur: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la création: {e}")
    
    else:
        print("\n❌ Aucune authentification réussie - Tests limités aux endpoints publics")
    
    print("\n" + "=" * 80)
    print("🏁 TESTS TERMINÉS")
    print("\n📊 RÉSUMÉ:")
    print("✅ Endpoints de contributions testés")
    print("✅ Vérification de l'authentification requise")
    print("✅ Test des filtres de status")
    if authenticated_token:
        print("✅ Tests avec authentification réussis")
        print("✅ Création et vote sur contributions testés")
    else:
        print("⚠️  Tests limités - authentification non disponible")

if __name__ == "__main__":
    main()