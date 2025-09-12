#!/usr/bin/env python3
"""
TEST DE CONSTRUCTION D'URL FRONTEND VS BACKEND
==============================================

Vérifier si la logique de construction d'URL du frontend correspond
aux patterns qui fonctionnent réellement.
"""

import requests

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"
FRONTEND_URL = "https://kit-collection-5.preview.emergentagent.com"

def simulate_frontend_url_construction():
    """Simuler la logique de construction d'URL du frontend"""
    print("🔍 SIMULATION DE LA LOGIQUE FRONTEND DE CONSTRUCTION D'URL")
    print("=" * 60)
    
    # Récupérer les données comme le ferait le frontend
    response = requests.get(f"{BACKEND_URL}/jerseys/approved")
    if response.status_code != 200:
        print(f"❌ Erreur API: {response.status_code}")
        return
        
    jerseys = response.json()
    
    # Analyser chaque maillot avec images
    for jersey in jerseys:
        if not (jersey.get('images') or jersey.get('front_photo_url')):
            continue
            
        print(f"\n🏆 {jersey['team']} ({jersey.get('season', 'Unknown')})")
        print(f"   ID: {jersey['id'][:8]}...")
        
        # Simuler la logique frontend pour images array
        if jersey.get('images') and len(jersey['images']) > 0:
            original_url = jersey['images'][0]
            print(f"   📋 Format 'images' array: {original_url}")
            
            # Logique frontend actuelle (ligne 1236 App.js)
            if original_url.startswith('uploads/'):
                frontend_url = f"/{original_url}"
            else:
                frontend_url = f"/images/{original_url}"
                
            print(f"   🔧 URL construite par frontend: {frontend_url}")
            
            # Tester l'URL construite
            test_url = f"{FRONTEND_URL}{frontend_url}"
            test_accessibility(test_url, "Frontend Logic")
            
        # Simuler la logique frontend pour front_photo_url
        if jersey.get('front_photo_url'):
            original_url = jersey['front_photo_url']
            print(f"   📄 Format 'front_photo_url': {original_url}")
            
            # Logique frontend actuelle (ligne 1249 App.js)
            if original_url.startswith('uploads/'):
                frontend_url = f"/{original_url}"
            else:
                frontend_url = f"/images/{original_url}"
                
            print(f"   🔧 URL construite par frontend: {frontend_url}")
            
            # Tester l'URL construite
            test_url = f"{FRONTEND_URL}{frontend_url}"
            test_accessibility(test_url, "Frontend Logic")
            
        # Tester les patterns alternatifs qui fonctionnent
        print(f"   🧪 Test des patterns alternatifs:")
        
        # Pour images array, tester le pattern /images/ direct
        if jersey.get('images') and len(jersey['images']) > 0:
            alt_url = f"{FRONTEND_URL}/images/{jersey['images'][0]}"
            test_accessibility(alt_url, "Alternative /images/")
            
        # Pour front_photo_url, tester l'accès direct
        if jersey.get('front_photo_url'):
            alt_url = f"{FRONTEND_URL}/{jersey['front_photo_url']}"
            test_accessibility(alt_url, "Alternative direct")

def test_accessibility(url, method_name):
    """Tester l'accessibilité d'une URL"""
    try:
        response = requests.head(url, timeout=5)
        content_type = response.headers.get('content-type', '')
        
        if response.status_code == 200 and 'image/' in content_type:
            print(f"      ✅ {method_name}: ACCESSIBLE ({content_type})")
        elif response.status_code == 200:
            print(f"      ⚠️  {method_name}: HTTP 200 mais type incorrect ({content_type})")
        else:
            print(f"      ❌ {method_name}: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"      ❌ {method_name}: ERREUR - {e}")

def analyze_working_patterns():
    """Analyser les patterns qui fonctionnent réellement"""
    print(f"\n" + "=" * 60)
    print("📊 ANALYSE DES PATTERNS QUI FONCTIONNENT RÉELLEMENT")
    print("=" * 60)
    
    # Patterns identifiés comme fonctionnels
    working_examples = [
        {
            'original': 'jersey_4c6e5ec7-9851-4361-a0af-9dfb570e9037_front_1755648236.png',
            'working_url': '/images/jersey_4c6e5ec7-9851-4361-a0af-9dfb570e9037_front_1755648236.png',
            'type': 'images_array'
        },
        {
            'original': 'uploads/jerseys/ebd76b11-68c6-4f4f-9a2c-c94a2e022fa5/front_front_jersey.jpg',
            'working_url': '/uploads/jerseys/ebd76b11-68c6-4f4f-9a2c-c94a2e022fa5/front_front_jersey.jpg',
            'type': 'front_photo_url'
        },
        {
            'original': 'uploads/jerseys/8b83a4f0-2f42-4da5-acd9-f31210cbfa30/front_1000008367.jpg',
            'working_url': '/uploads/jerseys/8b83a4f0-2f42-4da5-acd9-f31210cbfa30/front_1000008367.jpg',
            'type': 'front_photo_url'
        }
    ]
    
    print(f"\n🔍 PATTERNS FONCTIONNELS IDENTIFIÉS:")
    for example in working_examples:
        print(f"   📁 Type: {example['type']}")
        print(f"      Original: {example['original']}")
        print(f"      Fonctionnel: {example['working_url']}")
        
        # Vérifier si la logique frontend produit la bonne URL
        if example['type'] == 'images_array':
            # Logique frontend pour images array
            if example['original'].startswith('uploads/'):
                frontend_constructed = f"/{example['original']}"
            else:
                frontend_constructed = f"/images/{example['original']}"
        else:
            # Logique frontend pour front_photo_url
            if example['original'].startswith('uploads/'):
                frontend_constructed = f"/{example['original']}"
            else:
                frontend_constructed = f"/images/{example['original']}"
                
        if frontend_constructed == example['working_url']:
            print(f"      ✅ Logique frontend CORRECTE")
        else:
            print(f"      ❌ Logique frontend INCORRECTE")
            print(f"         Frontend produit: {frontend_constructed}")
            print(f"         Devrait produire: {example['working_url']}")
        print()

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE DU TEST DE CONSTRUCTION D'URL FRONTEND")
    print("=" * 55)
    
    simulate_frontend_url_construction()
    analyze_working_patterns()
    
    print(f"\n💡 RECOMMANDATIONS FINALES:")
    print(f"   1. Vérifier que la logique frontend correspond aux patterns fonctionnels")
    print(f"   2. Corriger les URLs qui ne suivent pas les patterns qui marchent")
    print(f"   3. Implémenter une vérification d'existence avant affichage")
    print(f"   4. Ajouter un fallback robuste pour les images manquantes")
    
    print("\n✅ TEST TERMINÉ!")
    print("=" * 55)

if __name__ == "__main__":
    main()