#!/usr/bin/env python3
"""
ANALYSE COMPLÈTE DES FORMATS D'IMAGES TOPKIT - DIAGNOSTIC APPROFONDI
=================================================================

OBJECTIF: Analyser TOUS les formats d'images existants dans la base de données 
pour comprendre pourquoi l'affichage ne fonctionne pas.

TESTS À EFFECTUER:
1. GET /api/jerseys/approved - Analyser TOUS les maillots et leurs formats d'images
2. Identifier tous les patterns différents :
   - Format "images" array
   - Format "front_photo_url" / "back_photo_url" 
   - Différents types d'extensions (.jpg, .png, .jpeg, .webp, etc.)
   - Différents chemins (uploads/, images/, relatifs, absolus)
3. Lister les formats d'images réels vs attendus
4. Vérifier si les fichiers existent physiquement pour chaque format

FOCUS: Identifier TOUS les formats et patterns d'images pour construire une solution universelle.
"""

import requests
import json
import os
from pathlib import Path
from collections import defaultdict
import re

# Configuration
BACKEND_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"

class ImageFormatAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.image_patterns = defaultdict(list)
        self.file_extensions = defaultdict(int)
        self.path_patterns = defaultdict(int)
        self.jerseys_with_images = []
        self.jerseys_without_images = []
        
    def analyze_all_jerseys(self):
        """Analyser tous les maillots approuvés et leurs formats d'images"""
        print("🔍 ANALYSE COMPLÈTE DES FORMATS D'IMAGES DANS LA BASE DE DONNÉES")
        print("=" * 70)
        
        try:
            # Récupérer tous les maillots approuvés
            response = self.session.get(f"{BACKEND_URL}/jerseys/approved")
            
            if response.status_code != 200:
                print(f"❌ Erreur lors de la récupération des maillots: {response.status_code}")
                return
                
            jerseys = response.json()
            print(f"📊 TOTAL MAILLOTS ANALYSÉS: {len(jerseys)}")
            print()
            
            # Analyser chaque maillot
            for i, jersey in enumerate(jerseys, 1):
                self.analyze_jersey_images(jersey, i)
                
            # Générer le rapport complet
            self.generate_comprehensive_report()
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")
            
    def analyze_jersey_images(self, jersey, index):
        """Analyser les formats d'images d'un maillot spécifique"""
        jersey_id = jersey.get('id', 'unknown')
        team = jersey.get('team', 'Unknown Team')
        
        print(f"🔍 [{index:2d}] Analyse: {team} (ID: {jersey_id[:8]}...)")
        
        # Vérifier tous les champs d'images possibles
        image_fields = {
            'images': jersey.get('images'),
            'front_photo_url': jersey.get('front_photo_url'),
            'back_photo_url': jersey.get('back_photo_url'),
            'front_photo': jersey.get('front_photo'),
            'back_photo': jersey.get('back_photo'),
            'photo_urls': jersey.get('photo_urls'),
            'image_urls': jersey.get('image_urls')
        }
        
        has_images = False
        jersey_analysis = {
            'id': jersey_id,
            'team': team,
            'season': jersey.get('season', 'Unknown'),
            'image_fields': {},
            'patterns': [],
            'extensions': [],
            'paths': []
        }
        
        for field_name, field_value in image_fields.items():
            if field_value:
                has_images = True
                jersey_analysis['image_fields'][field_name] = field_value
                
                # Analyser selon le type de données
                if isinstance(field_value, list):
                    print(f"   📋 {field_name}: Array avec {len(field_value)} éléments")
                    for img_url in field_value:
                        self.analyze_image_url(img_url, field_name, jersey_analysis)
                        
                elif isinstance(field_value, str):
                    print(f"   📄 {field_name}: String - {field_value}")
                    self.analyze_image_url(field_value, field_name, jersey_analysis)
                    
                else:
                    print(f"   ❓ {field_name}: Type inconnu - {type(field_value)} - {field_value}")
        
        if has_images:
            self.jerseys_with_images.append(jersey_analysis)
            print(f"   ✅ Maillot AVEC images ({len(jersey_analysis['image_fields'])} champs)")
        else:
            self.jerseys_without_images.append(jersey_analysis)
            print(f"   ❌ Maillot SANS images")
            
        print()
        
    def analyze_image_url(self, url, field_name, jersey_analysis):
        """Analyser une URL d'image spécifique"""
        if not url or not isinstance(url, str):
            return
            
        # Nettoyer l'URL
        clean_url = url.strip()
        
        # Extraire l'extension
        extension_match = re.search(r'\.([a-zA-Z0-9]+)(?:\?|$)', clean_url)
        if extension_match:
            extension = extension_match.group(1).lower()
            self.file_extensions[extension] += 1
            jersey_analysis['extensions'].append(extension)
            print(f"      🔗 Extension: .{extension}")
        
        # Analyser le pattern de chemin
        path_patterns = []
        
        if clean_url.startswith('/'):
            path_patterns.append('absolute_path')
            print(f"      📁 Chemin absolu: {clean_url}")
        elif clean_url.startswith('http'):
            path_patterns.append('full_url')
            print(f"      🌐 URL complète: {clean_url}")
        else:
            path_patterns.append('relative_path')
            print(f"      📂 Chemin relatif: {clean_url}")
            
        # Identifier les patterns de dossiers
        if '/uploads/' in clean_url:
            path_patterns.append('uploads_folder')
            self.path_patterns['uploads_folder'] += 1
            print(f"      📁 Pattern: uploads/")
            
        if '/images/' in clean_url:
            path_patterns.append('images_folder')
            self.path_patterns['images_folder'] += 1
            print(f"      📁 Pattern: images/")
            
        if '/jerseys/' in clean_url:
            path_patterns.append('jerseys_subfolder')
            self.path_patterns['jerseys_subfolder'] += 1
            print(f"      📁 Pattern: jerseys/")
            
        # Identifier les patterns de nommage
        if 'front' in clean_url.lower():
            path_patterns.append('front_photo')
            print(f"      🔍 Type: Photo avant")
            
        if 'back' in clean_url.lower():
            path_patterns.append('back_photo')
            print(f"      🔍 Type: Photo arrière")
            
        jersey_analysis['patterns'].extend(path_patterns)
        jersey_analysis['paths'].append(clean_url)
        
        # Enregistrer le pattern global
        pattern_key = f"{field_name}_{'+'.join(sorted(path_patterns))}"
        self.image_patterns[pattern_key].append({
            'url': clean_url,
            'jersey_id': jersey_analysis['id'],
            'team': jersey_analysis['team']
        })
        
    def check_physical_files(self):
        """Vérifier si les fichiers existent physiquement"""
        print("🔍 VÉRIFICATION DE L'EXISTENCE PHYSIQUE DES FICHIERS")
        print("=" * 55)
        
        base_paths = [
            '/app/frontend/public',
            '/app/backend',
            '/app'
        ]
        
        files_found = 0
        files_missing = 0
        
        for jersey in self.jerseys_with_images:
            print(f"\n📁 Vérification: {jersey['team']} (ID: {jersey['id'][:8]}...)")
            
            for path in jersey['paths']:
                file_found = False
                
                for base_path in base_paths:
                    # Construire le chemin complet
                    if path.startswith('/'):
                        full_path = base_path + path
                    else:
                        full_path = os.path.join(base_path, path)
                        
                    if os.path.exists(full_path):
                        file_size = os.path.getsize(full_path)
                        print(f"   ✅ TROUVÉ: {full_path} ({file_size} bytes)")
                        files_found += 1
                        file_found = True
                        break
                        
                if not file_found:
                    print(f"   ❌ MANQUANT: {path}")
                    files_missing += 1
                    
        print(f"\n📊 RÉSUMÉ FICHIERS:")
        print(f"   ✅ Fichiers trouvés: {files_found}")
        print(f"   ❌ Fichiers manquants: {files_missing}")
        print(f"   📈 Taux de réussite: {files_found/(files_found+files_missing)*100:.1f}%" if (files_found+files_missing) > 0 else "   📈 Aucun fichier à vérifier")
        
    def generate_comprehensive_report(self):
        """Générer un rapport complet de l'analyse"""
        print("\n" + "=" * 70)
        print("📊 RAPPORT COMPLET D'ANALYSE DES FORMATS D'IMAGES")
        print("=" * 70)
        
        # Statistiques générales
        total_jerseys = len(self.jerseys_with_images) + len(self.jerseys_without_images)
        print(f"\n🔢 STATISTIQUES GÉNÉRALES:")
        print(f"   📊 Total maillots: {total_jerseys}")
        print(f"   ✅ Maillots avec images: {len(self.jerseys_with_images)} ({len(self.jerseys_with_images)/total_jerseys*100:.1f}%)")
        print(f"   ❌ Maillots sans images: {len(self.jerseys_without_images)} ({len(self.jerseys_without_images)/total_jerseys*100:.1f}%)")
        
        # Extensions de fichiers
        print(f"\n📁 EXTENSIONS DE FICHIERS DÉTECTÉES:")
        for ext, count in sorted(self.file_extensions.items(), key=lambda x: x[1], reverse=True):
            print(f"   .{ext}: {count} fichiers")
            
        # Patterns de chemins
        print(f"\n📂 PATTERNS DE CHEMINS DÉTECTÉS:")
        for pattern, count in sorted(self.path_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"   {pattern}: {count} occurrences")
            
        # Patterns d'images détaillés
        print(f"\n🔍 PATTERNS D'IMAGES DÉTAILLÉS:")
        for pattern, examples in self.image_patterns.items():
            print(f"   {pattern}: {len(examples)} exemples")
            for example in examples[:3]:  # Montrer 3 exemples max
                print(f"      - {example['url']} ({example['team']})")
            if len(examples) > 3:
                print(f"      ... et {len(examples) - 3} autres")
                
        # Maillots avec images - détail
        print(f"\n✅ MAILLOTS AVEC IMAGES - DÉTAIL:")
        for jersey in self.jerseys_with_images:
            print(f"   🏆 {jersey['team']} ({jersey['season']})")
            print(f"      ID: {jersey['id']}")
            print(f"      Champs d'images: {list(jersey['image_fields'].keys())}")
            print(f"      Extensions: {list(set(jersey['extensions']))}")
            print(f"      Chemins: {len(jersey['paths'])} fichiers")
            for path in jersey['paths']:
                print(f"         - {path}")
            print()
            
        # Vérification des fichiers physiques
        self.check_physical_files()
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS POUR SOLUTION UNIVERSELLE:")
        print(f"   1. Supporter les formats: {', '.join(self.file_extensions.keys())}")
        print(f"   2. Gérer les chemins: uploads/, images/, relatifs et absolus")
        print(f"   3. Traiter les formats: arrays et strings")
        print(f"   4. Vérifier l'existence des fichiers avant affichage")
        print(f"   5. Implémenter un fallback pour les images manquantes")
        
        print(f"\n🎯 CONCLUSION:")
        if len(self.jerseys_with_images) > 0:
            print(f"   ✅ {len(self.jerseys_with_images)} maillots ont des données d'images")
            print(f"   🔍 {len(self.image_patterns)} patterns différents détectés")
            print(f"   📁 {len(self.file_extensions)} types d'extensions trouvés")
            print(f"   🚀 Solution universelle nécessaire pour supporter tous les formats")
        else:
            print(f"   ❌ Aucun maillot avec images trouvé dans la base de données")
            print(f"   🔍 Problème potentiel de données ou de structure")

def main():
    """Fonction principale d'analyse"""
    print("🚀 DÉMARRAGE DE L'ANALYSE COMPLÈTE DES FORMATS D'IMAGES")
    print("=" * 60)
    
    analyzer = ImageFormatAnalyzer()
    analyzer.analyze_all_jerseys()
    
    print("\n✅ ANALYSE TERMINÉE!")
    print("=" * 60)

if __name__ == "__main__":
    main()