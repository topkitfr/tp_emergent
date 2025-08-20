#!/usr/bin/env python3
"""
Script de nettoyage des doublons TopKit
Détecte et supprime les équipes et compétitions en doublon
Conserve la version avec le plus de détails
"""

import asyncio
import aiohttp
import json
import sys
import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import motor.motor_asyncio
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitDuplicateCleaner:
    def __init__(self):
        self.session = None
        self.token = None
        self.mongo_client = None
        self.db = None
        self.stats = {
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'teams_processed': 0,
            'competitions_processed': 0,
            'errors': []
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        # Connexion MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'topkit')
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        self.db = self.mongo_client[db_name]
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.mongo_client:
            self.mongo_client.close()

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

    def normalize_team_name(self, name: str) -> str:
        """Normalise un nom d'équipe pour la comparaison"""
        # Remplacer les variantes communes
        name = name.lower().strip()
        
        # Remplacements standardisés
        replacements = {
            'fc barcelone': 'barcelona fc',
            'fc barcelona': 'barcelona fc',
            'real madrid cf': 'real madrid',
            'manchester united fc': 'manchester united',
            'ac milan': 'milan ac',
            'inter milan': 'inter',
            'fc': '',
            'cf': '',
            'sc': '',
            'ac': '',
        }
        
        for old, new in replacements.items():
            name = name.replace(old, new)
        
        # Supprimer espaces multiples et caractères spéciaux
        name = re.sub(r'\s+', ' ', name)
        name = re.sub(r'[^\w\s]', '', name)
        
        return name.strip()

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calcule la similarité entre deux noms"""
        norm1 = self.normalize_team_name(name1)
        norm2 = self.normalize_team_name(name2)
        return SequenceMatcher(None, norm1, norm2).ratio()

    def normalize_country(self, country: str) -> str:
        """Normalise un nom de pays"""
        country_map = {
            'espagne': 'spain',
            'angleterre': 'england',
            'allemagne': 'germany',
            'italie': 'italy',
            'france': 'france',
            'portugal': 'portugal',
            'pays-bas': 'netherlands',
            'belgique': 'belgium',
            'brésil': 'brazil',
            'argentine': 'argentina',
            'états-unis': 'usa',
            'japon': 'japan',
            'chine': 'china'
        }
        
        country_lower = country.lower().strip()
        return country_map.get(country_lower, country_lower)

    def calculate_team_score(self, team: Dict) -> int:
        """Calcule un score de qualité pour une équipe"""
        score = 0
        
        # Points pour les détails remplis
        if team.get('short_name'): score += 2
        if team.get('city'): score += 2
        if team.get('founded_year'): score += 3
        if team.get('colors') and len(team['colors']) > 0: score += 2
        if team.get('logo_url'): score += 5
        if team.get('common_names') and len(team['common_names']) > 0: score += 2
        if team.get('league_info'): score += 3
        
        # Points pour les maillots associés
        jersey_count = team.get('master_jerseys_count', 0)
        score += jersey_count * 2
        
        # Bonus pour ancienneté (données antérieures = mieux établies)
        ref_num = int(team.get('topkit_reference', 'TK-TEAM-999999').split('-')[-1])
        if ref_num < 50:  # Références antérieures
            score += 10
            
        return score

    async def get_all_teams(self) -> List[Dict]:
        """Récupère toutes les équipes"""
        async with self.session.get(f"{API_BASE_URL}/teams?limit=1000") as response:
            if response.status == 200:
                return await response.json()
            return []

    async def find_team_duplicates(self, teams: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """Trouve les équipes en doublon"""
        duplicates = []
        processed = set()
        
        for i, team1 in enumerate(teams):
            if i in processed:
                continue
                
            for j, team2 in enumerate(teams[i+1:], i+1):
                if j in processed:
                    continue
                
                # Vérifier similarité des noms
                similarity = self.calculate_similarity(team1['name'], team2['name'])
                
                # Vérifier pays (normalisé)
                country1 = self.normalize_country(team1.get('country', ''))
                country2 = self.normalize_country(team2.get('country', ''))
                
                # Conditions de doublon
                if similarity > 0.8 and country1 == country2:
                    print(f"🔍 Doublon détecté: '{team1['name']}' vs '{team2['name']}' (similarité: {similarity:.2f})")
                    
                    # Déterminer lequel garder (meilleur score)
                    score1 = self.calculate_team_score(team1)
                    score2 = self.calculate_team_score(team2)
                    
                    if score1 >= score2:
                        duplicates.append((team1, team2))  # Garder team1, supprimer team2
                    else:
                        duplicates.append((team2, team1))  # Garder team2, supprimer team1
                    
                    processed.add(j)
                    
        return duplicates

    async def delete_team_by_id(self, team_id: str, team_name: str) -> bool:
        """Supprime une équipe par son ID"""
        try:
            result = await self.db.teams.delete_one({"id": team_id})
            if result.deleted_count > 0:
                print(f"✅ Équipe supprimée: {team_name} (ID: {team_id})")
                return True
            else:
                print(f"❌ Équipe non trouvée pour suppression: {team_name}")
                return False
        except Exception as e:
            print(f"❌ Erreur suppression équipe {team_name}: {str(e)}")
            return False

    async def merge_team_data(self, keep_team: Dict, remove_team: Dict) -> bool:
        """Fusionne les données de deux équipes (garde la meilleure, enrichit si nécessaire)"""
        try:
            update_fields = {}
            
            # Enrichir avec des données manquantes
            if not keep_team.get('short_name') and remove_team.get('short_name'):
                update_fields['short_name'] = remove_team['short_name']
            
            if not keep_team.get('city') and remove_team.get('city'):
                update_fields['city'] = remove_team['city']
                
            if not keep_team.get('founded_year') and remove_team.get('founded_year'):
                update_fields['founded_year'] = remove_team['founded_year']
                
            if (not keep_team.get('colors') or len(keep_team['colors']) == 0) and remove_team.get('colors'):
                update_fields['colors'] = remove_team['colors']
                
            if not keep_team.get('logo_url') and remove_team.get('logo_url'):
                update_fields['logo_url'] = remove_team['logo_url']
            
            # Fusionner les noms communs
            if remove_team.get('common_names'):
                existing_common = keep_team.get('common_names', [])
                new_common = list(set(existing_common + remove_team['common_names'] + [remove_team['name']]))
                update_fields['common_names'] = new_common
            
            # Mettre à jour si nécessaire
            if update_fields:
                update_fields['last_modified_at'] = datetime.utcnow()
                update_fields['modification_count'] = keep_team.get('modification_count', 0) + 1
                
                result = await self.db.teams.update_one(
                    {"id": keep_team['id']}, 
                    {"$set": update_fields}
                )
                
                if result.modified_count > 0:
                    print(f"📝 Équipe enrichie: {keep_team['name']} avec données de {remove_team['name']}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Erreur fusion équipe: {str(e)}")
            return False

    async def cleanup_team_duplicates(self):
        """Nettoie les doublons d'équipes"""
        print("🔍 Recherche des doublons d'équipes...")
        
        teams = await self.get_all_teams()
        self.stats['teams_processed'] = len(teams)
        print(f"📊 {len(teams)} équipes à analyser")
        
        duplicates = await self.find_team_duplicates(teams)
        self.stats['duplicates_found'] = len(duplicates)
        
        if not duplicates:
            print("✅ Aucun doublon d'équipe trouvé")
            return True
            
        print(f"🎯 {len(duplicates)} doublons trouvés")
        
        for keep_team, remove_team in duplicates:
            print(f"\n🔄 Traitement doublon:")
            print(f"  📌 GARDER: {keep_team['name']} ({keep_team['topkit_reference']}) - Score: {self.calculate_team_score(keep_team)}")
            print(f"  🗑️ SUPPRIMER: {remove_team['name']} ({remove_team['topkit_reference']}) - Score: {self.calculate_team_score(remove_team)}")
            
            # Fusionner les données
            merge_success = await self.merge_team_data(keep_team, remove_team)
            
            if merge_success:
                # Supprimer le doublon
                delete_success = await self.delete_team_by_id(remove_team['id'], remove_team['name'])
                if delete_success:
                    self.stats['duplicates_removed'] += 1
                else:
                    self.stats['errors'].append(f"Échec suppression {remove_team['name']}")
            else:
                self.stats['errors'].append(f"Échec fusion données {remove_team['name']}")
                
        return True

    async def cleanup_all_duplicates(self):
        """Nettoie tous les types de doublons"""
        print("🚀 Début du nettoyage des doublons TopKit...")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Authentification
        if not await self.authenticate():
            return False
        
        # Nettoyage des équipes
        await self.cleanup_team_duplicates()
        
        return True

    def print_stats(self):
        """Affiche les statistiques de nettoyage"""
        print("\n" + "="*60)
        print("📊 STATISTIQUES DE NETTOYAGE DOUBLONS TOPKIT")
        print("="*60)
        print(f"⚽ Équipes analysées: {self.stats['teams_processed']}")
        print(f"🔍 Doublons trouvés: {self.stats['duplicates_found']}")
        print(f"🗑️ Doublons supprimés: {self.stats['duplicates_removed']}")
        print(f"❌ Erreurs: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print(f"\n🔍 Erreurs détectées:")
            for error in self.stats['errors']:
                print(f"  • {error}")
                
        success_rate = (self.stats['duplicates_removed'] / max(1, self.stats['duplicates_found'])) * 100
        print(f"\n🎯 Taux de succès: {success_rate:.1f}%")
        print("="*60)

async def main():
    """Fonction principale"""
    try:
        async with TopKitDuplicateCleaner() as cleaner:
            success = await cleaner.cleanup_all_duplicates()
            cleaner.print_stats()
            
            if success:
                print("\n🎉 Nettoyage des doublons terminé!")
                print("💡 Les doublons ont été supprimés et les données fusionnées")
                return 0
            else:
                print("\n❌ Nettoyage échoué")
                return 1
                
    except KeyboardInterrupt:
        print("\n⚠️ Nettoyage interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n💥 Erreur fatale: {str(e)}")
        return 1

if __name__ == "__main__":
    # Exécution du script
    exit_code = asyncio.run(main())
    sys.exit(exit_code)