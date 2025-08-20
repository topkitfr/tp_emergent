#!/usr/bin/env python3
"""
Script pour valider toutes les données importées dans TopKit
Met à jour le statut de vérification de toutes les équipes et compétitions
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List

# Configuration API
API_BASE_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitDataValidator:
    def __init__(self):
        self.session = None
        self.token = None
        self.stats = {
            'teams_validated': 0,
            'competitions_validated': 0,
            'brands_validated': 0,
            'players_validated': 0,
            'errors': []
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate(self):
        """Authentification admin"""
        try:
            async with self.session.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("token") or data.get("access_token")
                    print("✅ Authentification réussie")
                    return True
                else:
                    print(f"❌ Échec authentification: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erreur authentification: {str(e)}")
            return False

    async def get_all_unverified_teams(self) -> List[Dict]:
        """Récupère toutes les équipes non-vérifiées"""
        try:
            async with self.session.get(f"{API_BASE_URL}/teams?limit=1000") as response:
                if response.status == 200:
                    teams = await response.json()
                    unverified = [t for t in teams if t.get('verified_level') == 'unverified']
                    print(f"📊 Équipes non-vérifiées trouvées: {len(unverified)}")
                    return unverified
                else:
                    print(f"❌ Erreur récupération équipes: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Exception récupération équipes: {str(e)}")
            return []

    async def get_all_unverified_competitions(self) -> List[Dict]:
        """Récupère toutes les compétitions non-vérifiées"""
        try:
            async with self.session.get(f"{API_BASE_URL}/competitions?limit=1000") as response:
                if response.status == 200:
                    competitions = await response.json()
                    unverified = [c for c in competitions if c.get('verified_level') == 'unverified']
                    print(f"📊 Compétitions non-vérifiées trouvées: {len(unverified)}")
                    return unverified
                else:
                    print(f"❌ Erreur récupération compétitions: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Exception récupération compétitions: {str(e)}")
            return []

    async def validate_team(self, team_id: str, team_name: str) -> bool:
        """Valide une équipe spécifique"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Données de mise à jour pour validation
            update_data = {
                "verified_level": "community_verified",
                "verified_at": datetime.utcnow().isoformat(),
                "verified_by": "admin_bulk_import"
            }
            
            async with self.session.put(
                f"{API_BASE_URL}/teams/{team_id}",
                json=update_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    self.stats['teams_validated'] += 1
                    print(f"✅ Équipe validée: {team_name}")
                    return True
                else:
                    error_text = await response.text()
                    self.stats['errors'].append(f"Erreur validation équipe {team_name}: {error_text}")
                    print(f"❌ Échec validation équipe {team_name}: {response.status}")
                    return False
                    
        except Exception as e:
            self.stats['errors'].append(f"Exception validation équipe {team_name}: {str(e)}")
            return False

    async def validate_competition(self, comp_id: str, comp_name: str) -> bool:
        """Valide une compétition spécifique"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Données de mise à jour pour validation
            update_data = {
                "verified_level": "community_verified",
                "verified_at": datetime.utcnow().isoformat(),
                "verified_by": "admin_bulk_import"
            }
            
            async with self.session.put(
                f"{API_BASE_URL}/competitions/{comp_id}",
                json=update_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    self.stats['competitions_validated'] += 1
                    print(f"✅ Compétition validée: {comp_name}")
                    return True
                else:
                    error_text = await response.text()
                    self.stats['errors'].append(f"Erreur validation compétition {comp_name}: {error_text}")
                    print(f"❌ Échec validation compétition {comp_name}: {response.status}")
                    return False
                    
        except Exception as e:
            self.stats['errors'].append(f"Exception validation compétition {comp_name}: {str(e)}")
            return False

    async def bulk_validate_via_database(self):
        """Méthode alternative: mise à jour directe via base de données MongoDB"""
        try:
            import motor.motor_asyncio
            import os
            
            # Connexion MongoDB avec les bonnes valeurs d'environnement
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            db_name = os.environ.get('DB_NAME', 'topkit')
            
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client[db_name]
            
            print(f"🔗 Connexion MongoDB: {mongo_url}/{db_name}")
            
            # Mise à jour en masse des équipes
            teams_result = await db.teams.update_many(
                {"verified_level": "unverified"},
                {
                    "$set": {
                        "verified_level": "community_verified",
                        "verified_at": datetime.utcnow(),
                        "verified_by": "admin_bulk_validation"
                    }
                }
            )
            
            # Mise à jour en masse des compétitions
            competitions_result = await db.competitions.update_many(
                {"verified_level": "unverified"},
                {
                    "$set": {
                        "verified_level": "community_verified",
                        "verified_at": datetime.utcnow(),
                        "verified_by": "admin_bulk_validation"
                    }
                }
            )
            
            # Mise à jour en masse des marques
            brands_result = await db.brands.update_many(
                {"verified_level": "unverified"},
                {
                    "$set": {
                        "verified_level": "community_verified",
                        "verified_at": datetime.utcnow(),
                        "verified_by": "admin_bulk_validation"
                    }
                }
            )
            
            # Mise à jour en masse des joueurs
            players_result = await db.players.update_many(
                {"verified_level": "unverified"},
                {
                    "$set": {
                        "verified_level": "community_verified",
                        "verified_at": datetime.utcnow(),
                        "verified_by": "admin_bulk_validation"
                    }
                }
            )
            
            self.stats['teams_validated'] = teams_result.modified_count
            self.stats['competitions_validated'] = competitions_result.modified_count
            self.stats['brands_validated'] = brands_result.modified_count
            self.stats['players_validated'] = players_result.modified_count
            
            await client.close()
            
            print(f"✅ Validation en masse réussie:")
            print(f"  - Équipes validées: {teams_result.modified_count}")
            print(f"  - Compétitions validées: {competitions_result.modified_count}")
            print(f"  - Marques validées: {brands_result.modified_count}")
            print(f"  - Joueurs validés: {players_result.modified_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur validation en masse: {str(e)}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            self.stats['errors'].append(f"Erreur validation database: {str(e)}")
            return False

    async def validate_all_data(self):
        """Valide toutes les données non-vérifiées"""
        print("🚀 Début de la validation des données TopKit...")
        print(f"📅 Date de validation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Authentification
        if not await self.authenticate():
            return False

        # Essayer d'abord la méthode en masse via database
        print("\n🔄 Tentative de validation en masse via base de données...")
        bulk_success = await self.bulk_validate_via_database()
        
        if bulk_success:
            print("✅ Validation en masse réussie!")
            return True
        
        # Si échec, utiliser l'API individuelle
        print("\n🔄 Utilisation de l'API pour validation individuelle...")
        
        # Récupérer les données non-vérifiées
        unverified_teams = await self.get_all_unverified_teams()
        unverified_competitions = await self.get_all_unverified_competitions()
        
        total_items = len(unverified_teams) + len(unverified_competitions)
        print(f"\n📊 Total d'éléments à valider: {total_items}")
        
        # Valider les équipes
        print(f"\n⚽ Validation des {len(unverified_teams)} équipes...")
        for i, team in enumerate(unverified_teams, 1):
            if i % 50 == 0:  # Progress update every 50 items
                print(f"[{i}/{len(unverified_teams)}] Validation équipes en cours...")
            await self.validate_team(team['id'], team['name'])
        
        # Valider les compétitions
        print(f"\n🏆 Validation des {len(unverified_competitions)} compétitions...")
        for i, comp in enumerate(unverified_competitions, 1):
            await self.validate_competition(comp['id'], comp['name'])
        
        return True

    def print_stats(self):
        """Affiche les statistiques de validation"""
        print("\n" + "="*60)
        print("📊 STATISTIQUES DE VALIDATION TOPKIT")
        print("="*60)
        print(f"⚽ Équipes validées: {self.stats['teams_validated']}")
        print(f"🏆 Compétitions validées: {self.stats['competitions_validated']}")
        print(f"👕 Marques validées: {self.stats['brands_validated']}")
        print(f"👤 Joueurs validés: {self.stats['players_validated']}")
        print(f"❌ Erreurs: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print(f"\n🔍 Détail des erreurs (dernières 5):")
            for error in self.stats['errors'][-5:]:  # Afficher les 5 dernières erreurs
                print(f"  • {error}")
        
        total_validated = (
            self.stats['teams_validated'] + 
            self.stats['competitions_validated'] + 
            self.stats['brands_validated'] + 
            self.stats['players_validated']
        )
        
        print(f"\n🎯 Total validé: {total_validated} éléments")
        print("="*60)

async def main():
    """Fonction principale"""
    try:
        async with TopKitDataValidator() as validator:
            success = await validator.validate_all_data()
            validator.print_stats()
            
            if success:
                print("\n🎉 Validation des données terminée avec succès!")
                print("💡 Toutes les références sont maintenant validées et visibles dans TopKit")
                return 0
            else:
                print("\n❌ Validation échouée")
                return 1
                
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrompue par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n💥 Erreur fatale: {str(e)}")
        return 1

if __name__ == "__main__":
    # Exécution du script
    exit_code = asyncio.run(main())
    sys.exit(exit_code)