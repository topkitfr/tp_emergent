#!/usr/bin/env python3
"""
Script de nettoyage de la base de données pour le déploiement
Supprime tous les maillots, collections, et images uploadées
Préserve les comptes utilisateurs
"""

import os
import shutil
from pymongo import MongoClient
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/app/backend/.env')

def clean_database():
    """Nettoie complètement la base de données des maillots"""
    
    # Connexion à MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url)
    db = client.topkit
    
    print("🧹 Nettoyage de la base de données pour le déploiement...")
    
    # 1. Supprimer tous les maillots
    jerseys_count = db.jerseys.count_documents({})
    if jerseys_count > 0:
        result = db.jerseys.delete_many({})
        print(f"✅ {result.deleted_count} maillots supprimés")
    else:
        print("✅ Aucun maillot à supprimer")
    
    # 2. Supprimer toutes les soumissions d'utilisateurs
    submissions_count = db.user_submissions.count_documents({})
    if submissions_count > 0:
        result = db.user_submissions.delete_many({})
        print(f"✅ {result.deleted_count} soumissions supprimées")
    else:
        print("✅ Aucune soumission à supprimer")
    
    # 3. Nettoyer les collections des utilisateurs (owned/wanted)
    users_with_collections = 0
    for user in db.users.find({}):
        user_updated = False
        
        if 'owned_jerseys' in user and len(user['owned_jerseys']) > 0:
            db.users.update_one(
                {'_id': user['_id']}, 
                {'$set': {'owned_jerseys': []}}
            )
            user_updated = True
            
        if 'wanted_jerseys' in user and len(user['wanted_jerseys']) > 0:
            db.users.update_one(
                {'_id': user['_id']}, 
                {'$set': {'wanted_jerseys': []}}
            )
            user_updated = True
            
        if user_updated:
            users_with_collections += 1
    
    if users_with_collections > 0:
        print(f"✅ Collections nettoyées pour {users_with_collections} utilisateurs")
    else:
        print("✅ Aucune collection utilisateur à nettoyer")
    
    # 4. Supprimer toutes les images uploadées
    uploads_dir = '/app/uploads'
    if os.path.exists(uploads_dir):
        try:
            # Lister tous les fichiers avant suppression
            files_to_delete = []
            for root, dirs, files in os.walk(uploads_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        files_to_delete.append(os.path.join(root, file))
            
            # Supprimer les fichiers
            deleted_count = 0
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️  Erreur lors de la suppression de {file_path}: {e}")
            
            print(f"✅ {deleted_count} images supprimées du dossier uploads")
            
        except Exception as e:
            print(f"⚠️  Erreur lors du nettoyage du dossier uploads: {e}")
    else:
        print("✅ Dossier uploads n'existe pas")
    
    # 5. Afficher le résumé des utilisateurs préservés
    users_count = db.users.count_documents({})
    print(f"✅ {users_count} comptes utilisateurs préservés")
    
    # 6. Afficher les statistiques finales
    print("\n📊 État final de la base de données:")
    print(f"   • Maillots: {db.jerseys.count_documents({})}")
    print(f"   • Soumissions: {db.user_submissions.count_documents({})}")
    print(f"   • Utilisateurs: {db.users.count_documents({})}")
    
    # Fermer la connexion
    client.close()
    
    print("\n🎉 Base de données nettoyée avec succès pour le déploiement!")
    print("🚀 L'application est prête à être déployée avec une base de données propre.")

if __name__ == "__main__":
    # Demander confirmation
    confirmation = input("⚠️  ATTENTION: Cette opération va supprimer TOUS les maillots et images.\n"
                        "Les comptes utilisateurs seront préservés.\n"
                        "Êtes-vous sûr de vouloir continuer? (oui/non): ")
    
    if confirmation.lower() in ['oui', 'o', 'yes', 'y']:
        clean_database()
    else:
        print("❌ Opération annulée.")