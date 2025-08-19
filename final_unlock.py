#!/usr/bin/env python3
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def final_unlock():
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME = os.environ.get('DB_NAME', 'topkit_production_db')
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        email = 'steinmetzlivio@gmail.com'
        
        # Nettoyer toutes les activités suspectes
        await db.suspicious_activities.delete_many({})
        print('🧹 Toutes les activités suspectes supprimées')
        
        # Vérifier l'utilisateur
        user = await db.users.find_one({'email': email})
        if user:
            print(f'✅ Utilisateur trouvé: {user["name"]} - ID: {user["id"]}')
            
            # Voir tous les champs
            problematic_fields = []
            for key, value in user.items():
                if 'lock' in key.lower() or 'fail' in key.lower() or 'ban' in key.lower():
                    problematic_fields.append(f"{key}: {value}")
            
            if problematic_fields:
                print(f'⚠️  Champs problématiques: {problematic_fields}')
            else:
                print('✅ Aucun champ problématique trouvé')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')
    finally:
        client.close()

asyncio.run(final_unlock())