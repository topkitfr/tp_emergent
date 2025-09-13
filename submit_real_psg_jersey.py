#!/usr/bin/env python3
"""
Soumission d'un maillot PSG réel avec les photos uploadées par l'utilisateur
"""

import requests
import json
import os
from io import BytesIO

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"
USER_EMAIL = "testuser.images@gmail.com"
USER_PASSWORD = "SecureTestPass789!"

# URLs des images uploadées par l'utilisateur
FRONT_IMAGE_URL = "https://customer-assets.emergentagent.com/job_jersey-manager/artifacts/o1ynwavq_PXL_20250818_070741588.RAW-01.MP.COVER~2.jpg"
BACK_IMAGE_URL = "https://customer-assets.emergentagent.com/job_jersey-manager/artifacts/t3byno60_PXL_20250818_070807614.RAW-01.COVER.jpg"

class RealPSGJerseySubmitter:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        
    def authenticate_user(self):
        """Authentifier l'utilisateur"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_info = data.get('user', {})
                
                print(f"✅ Authentification réussie")
                print(f"   Utilisateur: {user_info.get('name')}")
                print(f"   Role: {user_info.get('role')}")
                print(f"   ID: {user_info.get('id')}")
                return True
            else:
                print(f"❌ Échec de l'authentification: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur d'authentification: {e}")
            return False
    
    def download_image(self, url, filename):
        """Télécharger une image depuis une URL"""
        try:
            print(f"📥 Téléchargement de {filename}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # Vérifier que c'est bien une image
                content_type = response.headers.get('content-type', '')
                if 'image/' in content_type:
                    print(f"   ✅ Image téléchargée: {len(response.content)} bytes ({content_type})")
                    return response.content
                else:
                    print(f"   ❌ Type de contenu invalide: {content_type}")
                    return None
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Erreur de téléchargement: {e}")
            return None
    
    def submit_psg_jersey(self):
        """Soumettre le maillot PSG avec les vraies photos"""
        try:
            print(f"\n🏃 Soumission du maillot PSG 24/25 Domicile Replica...")
            
            # Télécharger les images
            front_image_data = self.download_image(FRONT_IMAGE_URL, "face_psg.jpg")
            back_image_data = self.download_image(BACK_IMAGE_URL, "dos_psg.jpg")
            
            if not front_image_data or not back_image_data:
                print("❌ Impossible de télécharger les images")
                return None
            
            # Préparer les données du formulaire
            form_data = {
                'team': 'Paris Saint-Germain',
                'league': 'Ligue 1',
                'season': '2024/25',
                'manufacturer': 'Nike',
                'jersey_type': 'home',  # Correction: utiliser 'home' au lieu de 'domicile'
                'sku_code': 'PSG-DOM-2425-REP',
                'model': 'replica',
                'description': 'Maillot domicile PSG saison 2024/25 - Nike - Replica avec col rond et bande centrale rouge/bleue sur fond bleu marine'
            }
            
            # Préparer les fichiers
            files = {
                'front_photo': ('psg_front_real.jpg', front_image_data, 'image/jpeg'),
                'back_photo': ('psg_back_real.jpg', back_image_data, 'image/jpeg')
            }
            
            # Headers avec token d'authentification
            headers = {'Authorization': f'Bearer {self.user_token}'}
            
            print(f"📤 Envoi de la soumission...")
            response = requests.post(f"{BACKEND_URL}/jerseys", 
                                   data=form_data, 
                                   files=files, 
                                   headers=headers)
            
            if response.status_code == 200:
                jersey = response.json()
                
                print(f"\n🎉 MAILLOT PSG SOUMIS AVEC SUCCÈS!")
                print(f"   ID du maillot: {jersey.get('id')}")
                print(f"   Équipe: {jersey.get('team')}")
                print(f"   Référence: {jersey.get('reference_number')}")
                print(f"   Statut: {jersey.get('status')}")
                print(f"   Saison: {jersey.get('season')}")
                print(f"   Type: {jersey.get('jersey_type')}")
                print(f"   Modèle: {jersey.get('model')}")
                
                # Afficher les URLs des photos si disponibles
                if jersey.get('front_photo_url'):
                    print(f"   Photo face: /{jersey.get('front_photo_url')}")
                if jersey.get('back_photo_url'):
                    print(f"   Photo dos: /{jersey.get('back_photo_url')}")
                
                # Vérifier que les fichiers sont sauvegardés
                jersey_id = jersey.get('id')
                if jersey_id:
                    upload_dir = f"/app/frontend/public/uploads/jerseys/{jersey_id}"
                    if os.path.exists(upload_dir):
                        files_saved = os.listdir(upload_dir)
                        print(f"   Fichiers sauvegardés: {files_saved}")
                    else:
                        print(f"   ⚠️ Dossier non trouvé: {upload_dir}")
                
                return jersey
            else:
                print(f"❌ Échec de la soumission: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la soumission: {e}")
            return None
    
    def run(self):
        """Exécuter la soumission complète"""
        print("🚀 DÉMARRAGE DE LA SOUMISSION DU MAILLOT PSG RÉEL")
        print("=" * 55)
        
        # Authentification
        if not self.authenticate_user():
            return False
        
        # Soumission
        jersey = self.submit_psg_jersey()
        
        if jersey:
            print(f"\n✅ SOUMISSION TERMINÉE AVEC SUCCÈS!")
            print(f"Le maillot est maintenant en attente d'approbation admin.")
            print(f"Vous pouvez le voir dans l'interface admin pour correction et approbation.")
            return True
        else:
            print(f"\n❌ ÉCHEC DE LA SOUMISSION")
            return False

if __name__ == "__main__":
    submitter = RealPSGJerseySubmitter()
    submitter.run()