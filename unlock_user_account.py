#!/usr/bin/env python3
"""
Script pour déverrouiller le compte steinmetzlivio@gmail.com
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Configuration MongoDB
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'topkit_production_db')

async def unlock_user_account():
    """Déverrouiller le compte steinmetzlivio@gmail.com"""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    email = "steinmetzlivio@gmail.com"
    
    try:
        # Trouver l'utilisateur
        user = await db.users.find_one({"email": email})
        
        if not user:
            print(f"❌ Utilisateur {email} non trouvé")
            return
        
        print(f"✅ Utilisateur trouvé: {user.get('name', 'Unknown')} - Role: {user.get('role', 'user')}")
        
        # Vérifier l'état actuel
        locked_until = user.get('account_locked_until')
        failed_attempts = user.get('failed_login_attempts', 0)
        
        print(f"📊 État actuel:")
        print(f"   - Tentatives échouées: {failed_attempts}")
        print(f"   - Verrouillé jusqu'à: {locked_until}")
        
        # Déverrouiller le compte
        update_result = await db.users.update_one(
            {"email": email},
            {
                "$unset": {
                    "account_locked_until": "",
                },
                "$set": {
                    "failed_login_attempts": 0,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if update_result.modified_count > 0:
            print(f"🔓 Compte {email} déverrouillé avec succès!")
            print("   - Tentatives échouées remises à 0")
            print("   - Verrouillage supprimé")
        else:
            print(f"⚠️  Aucune modification effectuée pour {email}")
            
    except Exception as e:
        print(f"❌ Erreur lors du déverrouillage: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(unlock_user_account())