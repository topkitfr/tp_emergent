#!/usr/bin/env python3
"""
Script pour lister tous les utilisateurs de la base de données TopKit
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime

def main():
    try:
        # Connexion à MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'topkit')
        
        print(f"Connexion à la base de données: {mongo_url}/{db_name}")
        
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Vérifier la connexion
        client.admin.command('ping')
        print("✅ Connexion à MongoDB réussie")
        
        # Récupérer tous les utilisateurs
        users_collection = db.users
        users = list(users_collection.find({}))
        
        print(f"\n📊 Total des utilisateurs: {len(users)}")
        print("=" * 80)
        
        if not users:
            print("Aucun utilisateur trouvé dans la base de données.")
            return
            
        # Afficher les informations de chaque utilisateur
        for i, user in enumerate(users, 1):
            print(f"\n👤 Utilisateur #{i}")
            print("-" * 40)
            
            # Informations de base
            print(f"ID: {user.get('user_id', 'N/A')}")
            print(f"Email: {user.get('email', 'N/A')}")
            print(f"Pseudo: {user.get('username', 'N/A')}")
            print(f"Nom: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
            
            # Statut du compte
            print(f"Vérifié: {'✅ Oui' if user.get('is_verified', False) else '❌ Non'}")
            print(f"Admin: {'✅ Oui' if user.get('is_admin', False) else '❌ Non'}")
            
            # Dates
            created_at = user.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    print(f"Créé le: {created_at}")
                else:
                    print(f"Créé le: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Sécurité
            print(f"2FA activé: {'✅ Oui' if user.get('twofa_enabled', False) else '❌ Non'}")
            
            # Collections et listes de souhaits
            collections = user.get('collections', [])
            wishlists = user.get('wishlists', [])
            print(f"Collections: {len(collections)} maillots")
            print(f"Liste de souhaits: {len(wishlists)} maillots")
            
            # Informations supplémentaires si disponibles
            if user.get('phone_number'):
                print(f"Téléphone: {user.get('phone_number')}")
            if user.get('country'):
                print(f"Pays: {user.get('country')}")
            if user.get('language'):
                print(f"Langue: {user.get('language')}")
                
        print("\n" + "=" * 80)
        print("📋 Résumé:")
        
        # Statistiques
        total_users = len(users)
        verified_users = len([u for u in users if u.get('is_verified', False)])
        admin_users = len([u for u in users if u.get('is_admin', False)])
        twofa_users = len([u for u in users if u.get('twofa_enabled', False)])
        
        print(f"Total utilisateurs: {total_users}")
        print(f"Utilisateurs vérifiés: {verified_users}")
        print(f"Administrateurs: {admin_users}")
        print(f"Utilisateurs avec 2FA: {twofa_users}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    # Charger les variables d'environnement depuis le fichier .env
    import sys
    sys.path.append('/app/backend')
    
    try:
        from dotenv import load_dotenv
        load_dotenv('/app/backend/.env')
    except ImportError:
        # Si dotenv n'est pas disponible, définir manuellement
        os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
        os.environ['DB_NAME'] = 'topkit'
    
    main()