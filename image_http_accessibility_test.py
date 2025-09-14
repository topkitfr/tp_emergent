#!/usr/bin/env python3
"""
TEST D'ACCESSIBILITÉ HTTP DES IMAGES TOPKIT
==========================================

Test complet pour vérifier l'accessibilité HTTP de toutes les images
et identifier les patterns qui fonctionnent vs ceux qui ne fonctionnent pas.
"""

import requests
import json
from urllib.parse import urljoin

# Configuration
BACKEND_URL = "https://image-fix-10.preview.emergentagent.com/api"
FRONTEND_URL = "https://image-fix-10.preview.emergentagent.com"

class ImageAccessibilityTester:
    def __init__(self):
        self.session = requests.Session()
        self.accessible_images = []
        self.inaccessible_images = []
        self.url_patterns = {}
        
    def test_all_image_accessibility(self):
        """Tester l'accessibilité HTTP de toutes les images"""
        print("🌐 TEST D'ACCESSIBILITÉ HTTP DES IMAGES TOPKIT")
        print("=" * 50)
        
        # Récupérer tous les maillots avec images
        response = self.session.get(f"{BACKEND_URL}/jerseys/approved")
        if response.status_code != 200:
            print(f"❌ Erreur API: {response.status_code}")
            return
            
        jerseys = response.json()
        jerseys_with_images = []
        
        # Identifier les maillots avec images
        for jersey in jerseys:
            image_urls = []
            
            # Format "images" array
            if jersey.get('images'):
                for img in jersey['images']:
                    image_urls.append(('images_array', img))
                    
            # Format front_photo_url/back_photo_url
            if jersey.get('front_photo_url'):
                image_urls.append(('front_photo_url', jersey['front_photo_url']))
            if jersey.get('back_photo_url'):
                image_urls.append(('back_photo_url', jersey['back_photo_url']))
                
            if image_urls:
                jerseys_with_images.append({
                    'id': jersey['id'],
                    'team': jersey['team'],
                    'season': jersey.get('season', 'Unknown'),
                    'images': image_urls
                })
                
        print(f"📊 Maillots avec images trouvés: {len(jerseys_with_images)}")
        print()
        
        # Tester chaque image
        for jersey in jerseys_with_images:
            print(f"🏆 Test: {jersey['team']} ({jersey['season']})")
            print(f"   ID: {jersey['id'][:8]}...")
            
            for img_type, img_url in jersey['images']:
                self.test_image_url(img_url, img_type, jersey)
                
            print()
            
        # Générer le rapport
        self.generate_accessibility_report()
        
    def test_image_url(self, img_url, img_type, jersey):
        """Tester l'accessibilité d'une URL d'image spécifique"""
        if not img_url:
            return
            
        # Construire les différentes URLs possibles
        test_urls = []
        
        # URL directe (si relative)
        if not img_url.startswith('http'):
            # Essayer différents préfixes
            test_urls.extend([
                f"{FRONTEND_URL}/{img_url}",
                f"{FRONTEND_URL}/images/{img_url}",
                f"{FRONTEND_URL}/uploads/{img_url}",
                img_url if img_url.startswith('/') else f"{FRONTEND_URL}/{img_url}"
            ])
        else:
            test_urls.append(img_url)
            
        # Supprimer les doublons
        test_urls = list(set(test_urls))
        
        print(f"   🔍 {img_type}: {img_url}")
        
        accessible_url = None
        for test_url in test_urls:
            try:
                response = self.session.head(test_url, timeout=10)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    content_length = response.headers.get('content-length', '0')
                    
                    if 'image/' in content_type:
                        print(f"      ✅ ACCESSIBLE: {test_url}")
                        print(f"         Type: {content_type}, Taille: {content_length} bytes")
                        accessible_url = test_url
                        
                        self.accessible_images.append({
                            'original_url': img_url,
                            'accessible_url': test_url,
                            'img_type': img_type,
                            'jersey': jersey,
                            'content_type': content_type,
                            'content_length': content_length
                        })
                        break
                    else:
                        print(f"      ⚠️  MAUVAIS TYPE: {test_url} ({content_type})")
                else:
                    print(f"      ❌ HTTP {response.status_code}: {test_url}")
                    
            except Exception as e:
                print(f"      ❌ ERREUR: {test_url} - {e}")
                
        if not accessible_url:
            print(f"      🚫 AUCUNE URL ACCESSIBLE pour {img_url}")
            self.inaccessible_images.append({
                'original_url': img_url,
                'img_type': img_type,
                'jersey': jersey,
                'tested_urls': test_urls
            })
            
    def generate_accessibility_report(self):
        """Générer un rapport d'accessibilité complet"""
        print("\n" + "=" * 60)
        print("📊 RAPPORT D'ACCESSIBILITÉ HTTP DES IMAGES")
        print("=" * 60)
        
        total_images = len(self.accessible_images) + len(self.inaccessible_images)
        
        print(f"\n🔢 STATISTIQUES GLOBALES:")
        print(f"   📊 Total images testées: {total_images}")
        print(f"   ✅ Images accessibles: {len(self.accessible_images)} ({len(self.accessible_images)/total_images*100:.1f}%)" if total_images > 0 else "   ✅ Images accessibles: 0")
        print(f"   ❌ Images inaccessibles: {len(self.inaccessible_images)} ({len(self.inaccessible_images)/total_images*100:.1f}%)" if total_images > 0 else "   ❌ Images inaccessibles: 0")
        
        if self.accessible_images:
            print(f"\n✅ IMAGES ACCESSIBLES - DÉTAIL:")
            for img in self.accessible_images:
                print(f"   🏆 {img['jersey']['team']} - {img['img_type']}")
                print(f"      Original: {img['original_url']}")
                print(f"      Accessible: {img['accessible_url']}")
                print(f"      Type: {img['content_type']}, Taille: {img['content_length']} bytes")
                print()
                
        if self.inaccessible_images:
            print(f"\n❌ IMAGES INACCESSIBLES - DÉTAIL:")
            for img in self.inaccessible_images:
                print(f"   🏆 {img['jersey']['team']} - {img['img_type']}")
                print(f"      Original: {img['original_url']}")
                print(f"      URLs testées:")
                for url in img['tested_urls']:
                    print(f"         - {url}")
                print()
                
        # Analyser les patterns qui fonctionnent
        print(f"\n🔍 ANALYSE DES PATTERNS QUI FONCTIONNENT:")
        working_patterns = {}
        for img in self.accessible_images:
            original = img['original_url']
            accessible = img['accessible_url']
            
            # Identifier le pattern de transformation
            if original in accessible:
                if accessible.startswith(f"{FRONTEND_URL}/uploads/"):
                    pattern = "uploads_prefix"
                elif accessible.startswith(f"{FRONTEND_URL}/images/"):
                    pattern = "images_prefix"
                elif accessible.startswith(f"{FRONTEND_URL}/"):
                    pattern = "root_prefix"
                else:
                    pattern = "other"
            else:
                pattern = "transformed"
                
            if pattern not in working_patterns:
                working_patterns[pattern] = []
            working_patterns[pattern].append(img)
            
        for pattern, images in working_patterns.items():
            print(f"   📁 Pattern '{pattern}': {len(images)} images")
            for img in images[:2]:  # Montrer 2 exemples
                print(f"      - {img['original_url']} → {img['accessible_url']}")
                
        print(f"\n💡 RECOMMANDATIONS:")
        if len(self.accessible_images) > 0:
            print(f"   ✅ {len(self.accessible_images)} images sont accessibles via HTTP")
            print(f"   🔧 Patterns qui fonctionnent identifiés")
            print(f"   🚀 Utiliser les patterns fonctionnels pour l'affichage")
        else:
            print(f"   ❌ Aucune image accessible via HTTP")
            print(f"   🔧 Problème de configuration serveur statique")
            
        if len(self.inaccessible_images) > 0:
            print(f"   ⚠️  {len(self.inaccessible_images)} images nécessitent une correction")
            print(f"   🔧 Vérifier la configuration des routes statiques")
            
        print(f"\n🎯 CONCLUSION:")
        if len(self.accessible_images) == total_images and total_images > 0:
            print(f"   🎉 PARFAIT: Toutes les images sont accessibles!")
        elif len(self.accessible_images) > 0:
            print(f"   ⚠️  PARTIEL: {len(self.accessible_images)}/{total_images} images accessibles")
            print(f"   🔧 Solution partielle possible avec les patterns fonctionnels")
        else:
            print(f"   🚨 CRITIQUE: Aucune image accessible")
            print(f"   🔧 Configuration serveur statique requise")

def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE DU TEST D'ACCESSIBILITÉ HTTP")
    print("=" * 45)
    
    tester = ImageAccessibilityTester()
    tester.test_all_image_accessibility()
    
    print("\n✅ TEST TERMINÉ!")
    print("=" * 45)

if __name__ == "__main__":
    main()