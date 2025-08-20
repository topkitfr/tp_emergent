#!/usr/bin/env python3
"""
Créer des images de test pour les maillots manquants
"""

import os
from PIL import Image, ImageDraw, ImageFont
import requests

def create_jersey_image(team_name, season, color=(33, 150, 243), size=(300, 300)):
    """Créer une image de maillot avec le nom de l'équipe"""
    # Créer une image de base
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    
    # Ajouter du texte
    try:
        # Essayer d'utiliser une police système
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        # Fallback vers police par défaut
        font = ImageFont.load_default()
    
    # Texte principal
    text = team_name
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2 - 20
    
    # Dessiner le texte avec un contour
    draw.text((x-1, y-1), text, font=font, fill='white')
    draw.text((x+1, y-1), text, font=font, fill='white')
    draw.text((x-1, y+1), text, font=font, fill='white')
    draw.text((x+1, y+1), text, font=font, fill='white')
    draw.text((x, y), text, font=font, fill='black')
    
    # Saison
    season_text = f"Season {season}"
    bbox2 = draw.textbbox((0, 0), season_text, font=font)
    season_width = bbox2[2] - bbox2[0]
    season_x = (size[0] - season_width) // 2
    season_y = y + 40
    
    draw.text((season_x-1, season_y-1), season_text, font=font, fill='white')
    draw.text((season_x+1, season_y-1), season_text, font=font, fill='white')
    draw.text((season_x-1, season_y+1), season_text, font=font, fill='white')
    draw.text((season_x+1, season_y+1), season_text, font=font, fill='white')
    draw.text((season_x, season_y), season_text, font=font, fill='black')
    
    return img

def create_missing_images():
    """Créer les images manquantes identifiées par l'analyse"""
    # Images manquantes identifiées
    missing_files = [
        {
            'path': '/app/frontend/public/images/jersey_4c6e5ec7-9851-4361-a0af-9dfb570e9037_front_1755648236.png',
            'team': 'FC Barcelona',
            'season': '2024-25',
            'color': (196, 30, 58)  # Rouge Barcelona
        },
        {
            'path': '/app/frontend/public/uploads/jerseys/ebd76b11-68c6-4f4f-9a2c-c94a2e022fa5/front_front_jersey.jpg',
            'team': 'Paris Saint-Germain',
            'season': '2024-25',
            'color': (0, 51, 160)  # Bleu PSG
        },
        {
            'path': '/app/frontend/public/uploads/jerseys/8b83a4f0-2f42-4da5-acd9-f31210cbfa30/front_1000008367.jpg',
            'team': 'tr frhb',
            'season': '2024-25',
            'color': (76, 175, 80)  # Vert
        },
        {
            'path': '/app/frontend/public/uploads/jerseys/32a362b6-cf2e-4914-b131-9ee7f3195986/front_1000008367.jpg',
            'team': 'PSG Photo',
            'season': '2024-25',
            'color': (255, 87, 34)  # Orange
        }
    ]
    
    print("🎨 CRÉATION D'IMAGES DE TEST POUR LES MAILLOTS MANQUANTS")
    print("=" * 60)
    
    for file_info in missing_files:
        try:
            # Créer le dossier parent si nécessaire
            os.makedirs(os.path.dirname(file_info['path']), exist_ok=True)
            
            # Créer l'image
            img = create_jersey_image(
                file_info['team'], 
                file_info['season'], 
                file_info['color']
            )
            
            # Sauvegarder l'image
            img.save(file_info['path'], 'JPEG', quality=85)
            
            # Vérifier que le fichier existe
            if os.path.exists(file_info['path']):
                file_size = os.path.getsize(file_info['path'])
                print(f"✅ {file_info['team']}: {file_info['path']} ({file_size} bytes)")
            else:
                print(f"❌ {file_info['team']}: Échec de création")
                
        except Exception as e:
            print(f"❌ {file_info['team']}: Erreur - {e}")
    
    print(f"\n🏁 Création terminée!")

if __name__ == "__main__":
    create_missing_images()