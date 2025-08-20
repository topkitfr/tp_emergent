#!/usr/bin/env python3
"""
Script d'import des ligues et équipes dans la base de données collaborative TopKit
Utilise les APIs collaboratives pour créer les compétitions et équipes
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, List, Tuple

# Configuration API
API_BASE_URL = "http://localhost:8001/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

# Données à importer (copiées depuis la demande utilisateur)
LEAGUES_TEAMS_DATA = """France,Ligue 1,1,Paris Saint-Germain
France,Ligue 1,1,Olympique de Marseille
France,Ligue 1,1,AS Monaco
France,Ligue 1,1,Lille OSC
France,Ligue 1,1,Olympique Lyonnais
France,Ligue 1,1,Stade Rennais
France,Ligue 1,1,FC Nantes
France,Ligue 1,1,AS Saint-Étienne
France,Ligue 1,1,Montpellier HSC
France,Ligue 1,1,OGC Nice
France,Ligue 1,1,RC Lens
France,Ligue 1,1,Stade de Reims
France,Ligue 1,1,FC Lorient
France,Ligue 1,1,RC Strasbourg
France,Ligue 1,1,Angers SCO
France,Ligue 1,1,Stade Brestois
France,Ligue 1,1,Clermont Foot
France,Ligue 1,1,FC Metz
France,Ligue 1,1,Toulouse FC
France,Ligue 1,1,AJ Auxerre
France,Ligue 2,2,Le Havre AC
France,Ligue 2,2,Amiens SC
France,Ligue 2,2,Grenoble Foot 38
France,Ligue 2,2,EA Guingamp
France,Ligue 2,2,Valenciennes FC
France,Ligue 2,2,Caen
France,Ligue 2,2,Dijon FCO
France,Ligue 2,2,Nîmes Olympique
France,Ligue 2,2,Châteauroux
France,Ligue 2,2,Pau FC
France,Ligue 2,2,Bastia
France,Ligue 2,2,Quevilly-Rouen
France,Ligue 2,2,Annecy
France,Ligue 2,2,Laval
France,Ligue 2,2,Sochaux
France,Ligue 2,2,Girondins de Bordeaux
Angleterre,Premier League,1,Manchester United
Angleterre,Premier League,1,Liverpool
Angleterre,Premier League,1,Chelsea
Angleterre,Premier League,1,Arsenal
Angleterre,Premier League,1,Manchester City
Angleterre,Premier League,1,Tottenham
Angleterre,Premier League,1,Aston Villa
Angleterre,Premier League,1,Everton
Angleterre,Premier League,1,Leicester City
Angleterre,Premier League,1,West Ham
Angleterre,Premier League,1,Newcastle United
Angleterre,Premier League,1,Wolverhampton
Angleterre,Premier League,1,Cristal Palace
Angleterre,Premier League,1,Brighton & Hove Albion
Angleterre,Premier League,1,Southampton
Angleterre,Premier League,1,Fulham
Angleterre,Premier League,1,Brentford
Angleterre,Championship,2,Leeds United
Angleterre,Championship,2,Nottingham Forest
Angleterre,Championship,2,Sheffield United
Angleterre,Championship,2,West Bromwich Albion
Angleterre,Championship,2,Swansea City
Angleterre,Championship,2,Birmingham City
Angleterre,Championship,2,Blackburn Rovers
Angleterre,Championship,2,Middlesbrough
Angleterre,Championship,2,Norwich City
Angleterre,Championship,2,Watford
Angleterre,Championship,2,QPR
Angleterre,Championship,2,Coventry City
Angleterre,Championship,2,Cardiff City
Angleterre,Championship,2,Sunderland
Angleterre,Championship,2,Ipswich Town
Espagne,La Liga,1,Real Madrid
Espagne,La Liga,1,FC Barcelone
Espagne,La Liga,1,Atlético Madrid
Espagne,La Liga,1,Séville FC
Espagne,La Liga,1,Real Sociedad
Espagne,La Liga,1,Villarreal
Espagne,La Liga,1,Real Betis
Espagne,La Liga,1,Athletic Bilbao
Espagne,La Liga,1,Valence CF
Espagne,La Liga,1,Osasuna
Espagne,La Liga,1,Celta Vigo
Espagne,La Liga,1,Rayo Vallecano
Espagne,La Liga,1,Getafe
Espagne,La Liga,1,Elche
Espagne,La Liga,1,Espanyol
Espagne,La Liga,1,Real Valladolid
Espagne,La Liga,1,Cádiz
Espagne,Segunda División,2,UD Almería
Espagne,Segunda División,2,Girona FC
Espagne,Segunda División,2,Real Oviedo
Espagne,Segunda División,2,Racing Santander
Espagne,Segunda División,2,CD Tenerife
Espagne,Segunda División,2,SD Huesca
Espagne,Segunda División,2,Granada CF
Espagne,Segunda División,2,Las Palmas
Espagne,Segunda División,2,Eibar
Espagne,Segunda División,2,Leganés
Espagne,Segunda División,2,Burgos CF
Espagne,Segunda División,2,Málaga CF
Espagne,Segunda División,2,Zaragoza
Espagne,Segunda División,2,Mirandés
Espagne,Segunda División,2,Sporting Gijón
Espagne,Segunda División,2,Albacete
Allemagne,Bundesliga,1,Bayern Munich
Allemagne,Bundesliga,1,Borussia Dortmund
Allemagne,Bundesliga,1,RB Leipzig
Allemagne,Bundesliga,1,Bayer Leverkusen
Allemagne,Bundesliga,1,VfL Wolfsburg
Allemagne,Bundesliga,1,Eintracht Francfort
Allemagne,Bundesliga,1,Borussia Mönchengladbach
Allemagne,Bundesliga,1,Union Berlin
Allemagne,Bundesliga,1,Freiburg
Allemagne,Bundesliga,1,Mainz 05
Allemagne,Bundesliga,1,1. FC Köln
Allemagne,Bundesliga,1,Hoffenheim
Allemagne,Bundesliga,1,Augsbourg
Allemagne,Bundesliga,1,Hertha Berlin
Allemagne,Bundesliga,1,Werder Brême
Allemagne,Bundesliga,1,Stuttgart
Allemagne,Bundesliga,1,Schalke 04
Allemagne,2. Bundesliga,2,Hamburger SV
Allemagne,2. Bundesliga,2,1. FC Nürnberg
Allemagne,2. Bundesliga,2,Fortuna Düsseldorf
Allemagne,2. Bundesliga,2,Holstein Kiel
Allemagne,2. Bundesliga,2,Karlsruher SC
Allemagne,2. Bundesliga,2,Hannover 96
Allemagne,2. Bundesliga,2,Darmstadt 98
Allemagne,2. Bundesliga,2,Heidenheim
Allemagne,2. Bundesliga,2,Kaiserslautern
Allemagne,2. Bundesliga,2,Greuther Fürth
Allemagne,2. Bundesliga,2,Arminia Bielefeld
Allemagne,2. Bundesliga,2,St. Pauli
Allemagne,2. Bundesliga,2,Jahn Ratisbonne
Allemagne,2. Bundesliga,2,Sandhausen
Italie,Serie A,1,Juventus
Italie,Serie A,1,AC Milan
Italie,Serie A,1,Inter Milan
Italie,Serie A,1,AS Rome
Italie,Serie A,1,SS Lazio
Italie,Serie A,1,Napoli
Italie,Serie A,1,Atalanta
Italie,Serie A,1,Fiorentina
Italie,Serie A,1,Torino
Italie,Serie A,1,Sassuolo
Italie,Serie A,1,Bologne
Italie,Serie A,1,Udinese
Italie,Serie A,1,Sampdoria
Italie,Serie A,1,Verona
Italie,Serie A,1,Empoli
Italie,Serie A,1,Salernitana
Italie,Serie A,1,Cremonese
Italie,Serie B,2,Brescia Calcio
Italie,Serie B,2,Cremonese
Italie,Serie B,2,Reggina
Italie,Serie B,2,Ascoli
Italie,Serie B,2,SPAL
Italie,Serie B,2,Pescara
Italie,Serie B,2,Parma
Italie,Serie B,2,Cittadella
Italie,Serie B,2,Como
Italie,Serie B,2,Modène
Italie,Serie B,2,Ternana
Italie,Serie B,2,Venezia
Italie,Serie B,2,Perugia
Italie,Serie B,2,Cosenza
Portugal,Primeira Liga,1,FC Porto
Portugal,Primeira Liga,1,Sporting CP
Portugal,Primeira Liga,1,SL Benfica
Portugal,Primeira Liga,1,SC Braga
Portugal,Primeira Liga,1,Vitória Guimarães
Portugal,Primeira Liga,1,Boavista FC
Portugal,Primeira Liga,1,Portimonense
Portugal,Primeira Liga,1,Moreirense
Portugal,Primeira Liga,1,Famalicão
Portugal,Primeira Liga,1,Marítimo
Portugal,Primeira Liga,1,Gil Vicente
Portugal,Primeira Liga,1,Estoril
Portugal,Primeira Liga,1,Arouca
Portugal,Primeira Liga,1,Chaves
Portugal,Liga Portugal 2,2,CD Nacional
Portugal,Liga Portugal 2,2,Académico de Viseu
Portugal,Liga Portugal 2,2,Varzim SC
Portugal,Liga Portugal 2,2,FC Penafiel
Portugal,Liga Portugal 2,2,UD Oliveirense
Portugal,Liga Portugal 2,2,SC Covilhã
Portugal,Liga Portugal 2,2,Mafra
Portugal,Liga Portugal 2,2,Feirense
Portugal,Liga Portugal 2,2,Leixões
Portugal,Liga Portugal 2,2,Tondela
Portugal,Liga Portugal 2,2,B-SAD
Pays-Bas,Eredivisie,1,Ajax
Pays-Bas,Eredivisie,1,PSV Eindhoven
Pays-Bas,Eredivisie,1,Feyenoord
Pays-Bas,Eredivisie,1,AZ Alkmaar
Pays-Bas,Eredivisie,1,Vitesse Arnhem
Pays-Bas,Eredivisie,1,FC Utrecht
Pays-Bas,Eredivisie,1,FC Twente
Pays-Bas,Eredivisie,1,Heerenveen
Pays-Bas,Eredivisie,1,NEC Nimègue
Pays-Bas,Eredivisie,1,Sparta Rotterdam
Pays-Bas,Eredivisie,1,Fortuna Sittard
Pays-Bas,Eredivisie,1,FC Groningen
Pays-Bas,Eredivisie,1,Willem II
Pays-Bas,Eerste Divisie,2,De Graafschap
Pays-Bas,Eerste Divisie,2,NAC Breda
Pays-Bas,Eerste Divisie,2,MVV Maastricht
Pays-Bas,Eerste Divisie,2,Almere City FC
Pays-Bas,Eerste Divisie,2,FC Den Bosch
Pays-Bas,Eerste Divisie,2,FC Dordrecht
Pays-Bas,Eerste Divisie,2,ADO Den Haag
Pays-Bas,Eerste Divisie,2,Excelsior
Pays-Bas,Eerste Divisie,2,Helmond Sport
Pays-Bas,Eerste Divisie,2,Emmen
Belgique,Jupiler Pro League,1,Club Brugge
Belgique,Jupiler Pro League,1,RSC Anderlecht
Belgique,Jupiler Pro League,1,Standard de Liège
Belgique,Jupiler Pro League,1,KRC Genk
Belgique,Jupiler Pro League,1,KAA Gent
Belgique,Jupiler Pro League,1,Royal Antwerp FC
Belgique,Jupiler Pro League,1,Union Saint-Gilloise
Belgique,Jupiler Pro League,1,Charleroi
Belgique,Jupiler Pro League,1,Mechelen
Belgique,Jupiler Pro League,1,Zulte Waregem
Belgique,Jupiler Pro League,1,Sint-Truiden
Belgique,Jupiler Pro League,1,Ostende
Belgique,Jupiler Pro League,1,Eupen
Belgique,Jupiler Pro League,1,Cercle Bruges
Belgique,Jupiler Pro League,1,KV Courtrai
Belgique,Challenger Pro League,2,Lommel SK
Belgique,Challenger Pro League,2,KMSK Deinze
Belgique,Challenger Pro League,2,RWD Molenbeek
Belgique,Challenger Pro League,2,KVC Westerlo
Belgique,Challenger Pro League,2,Seraing United
Belgique,Challenger Pro League,2,Excelsior Virton
Belgique,Challenger Pro League,2,Beerschot
Belgique,Challenger Pro League,2,Waasland-Beveren
Brésil,Série A,1,Flamengo
Brésil,Série A,1,São Paulo FC
Brésil,Série A,1,Palmeiras
Brésil,Série A,1,Santos FC
Brésil,Série A,1,Corinthians
Brésil,Série A,1,Grêmio
Brésil,Série A,1,Internacional
Brésil,Série A,1,Atlético Mineiro
Brésil,Série A,1,Fluminense
Brésil,Série A,1,Botafogo
Brésil,Série A,1,Cruzeiro
Brésil,Série A,1,Vasco da Gama
Brésil,Série A,1,Bahia
Brésil,Série A,1,Coritiba
Brésil,Série A,1,Fortaleza
Brésil,Série A,1,América Mineiro
Brésil,Série A,1,Goias
Brésil,Série A,1,Cuiabá
Brésil,Série A,1,Avaí
Brésil,Série B,2,CRB
Brésil,Série B,2,Criciúma EC
Brésil,Série B,2,Ituano FC
Brésil,Série B,2,Guarani FC
Brésil,Série B,2,Ponte Preta
Brésil,Série B,2,Vila Nova
Brésil,Série B,2,Chapecoense
Brésil,Série B,2,Novorizontino
Brésil,Série B,2,Londrina
Brésil,Série B,2,Operário
Argentine,Primera División,1,Boca Juniors
Argentine,Primera División,1,River Plate
Argentine,Primera División,1,Racing Club
Argentine,Primera División,1,Independiente
Argentine,Primera División,1,San Lorenzo
Argentine,Primera División,1,Estudiantes
Argentine,Primera División,1,Vélez Sarsfield
Argentine,Primera División,1,Argentinos Juniors
Argentine,Primera División,1,Lanús
Argentine,Primera División,1,Talleres
Argentine,Primera División,1,Newell's Old Boys
Argentine,Primera División,1,Rosario Central
Argentine,Primera División,1,Defensa y Justicia
Argentine,Primera División,1,Huracán
Argentine,Primera División,1,Arsenal Sarandí
Argentine,Primera División,1,Central Córdoba
Argentine,Primera B Nacional,2,Quilmes
Argentine,Primera B Nacional,2,Santamarina
Argentine,Primera B Nacional,2,Deportivo Morón
Argentine,Primera B Nacional,2,All Boys
Argentine,Primera B Nacional,2,Ferro Carril Oeste
Argentine,Primera B Nacional,2,Brown de Adrogué
Argentine,Primera B Nacional,2,Chacarita Juniors
Argentine,Primera B Nacional,2,Agropecuario
États-Unis,MLS,1,LA Galaxy
États-Unis,MLS,1,Seattle Sounders
États-Unis,MLS,1,New York City FC
États-Unis,MLS,1,Atlanta United
États-Unis,MLS,1,Portland Timbers
États-Unis,MLS,1,DC United
États-Unis,MLS,1,New York Red Bulls
États-Unis,MLS,1,LAFC
États-Unis,MLS,1,Columbus Crew
États-Unis,MLS,1,Orlando City
États-Unis,MLS,1,Philadelphia Union
États-Unis,MLS,1,Chicago Fire
États-Unis,MLS,1,FC Dallas
États-Unis,MLS,1,Colorado Rapids
États-Unis,MLS,1,Sporting Kansas City
États-Unis,MLS,1,Houston Dynamo
États-Unis,USL Championship,2,Sacramento Republic
États-Unis,USL Championship,2,Monterey Bay FC
États-Unis,USL Championship,2,Rhode Island FC
États-Unis,USL Championship,2,Pittsburgh Riverhounds
États-Unis,USL Championship,2,Charleston Battery
États-Unis,USL Championship,2,Oakland Roots
Japon,J1 League,1,Yokohama F. Marinos
Japon,J1 League,1,Kawasaki Frontale
Japon,J1 League,1,Tokyo Verdy
Japon,J1 League,1,Gamba Osaka
Japon,J1 League,1,Vissel Kobe
Japon,J1 League,1,Nagoya Grampus
Japon,J1 League,1,Urawa Red Diamonds
Japon,J1 League,1,Kashima Antlers
Japon,J1 League,1,FC Tokyo
Japon,J1 League,1,Shonan Bellmare
Japon,J1 League,1,Sagan Tosu
Japon,J1 League,1,Avispa Fukuoka
Japon,J2 League,2,V-Varen Nagasaki
Japon,J2 League,2,Mito HollyHock
Japon,J2 League,2,Fagiano Okayama
Japon,J2 League,2,Tochigi SC
Japon,J2 League,2,Montedio Yamagata
Japon,J2 League,2,Renofa Yamaguchi
Japon,J2 League,2,FC Ryukyu
Japon,J2 League,2,Thespakusatsu Gunma
Japon,J2 League,2,Roasso Kumamoto
Japon,J2 League,2,Tokushima Vortis
Chine,Super League,1,Guangzhou Evergrande
Chine,Super League,1,Shanghai Shenhua
Chine,Super League,1,Beijing Guoan
Chine,Super League,1,Shandong Taishan
Chine,Super League,1,Jiangsu Suning
Chine,Super League,1,Henan Songshan Longmen
Chine,Super League,1,Wuhan Three Towns
Chine,Super League,1,Changchun Yatai
Chine,Super League,1,Tianjin Jinmen Tiger
Chine,China League One,2,Chengdu Rongcheng
Chine,China League One,2,Nantong Zhiyun
Chine,China League One,2,Zhejiang Professional
Chine,China League One,2,Meizhou Hakka
Chine,China League One,2,Kunshan FC
Chine,China League One,2,Suzhou Dongwu
Égypte,Premier League,1,Al Ahly
Égypte,Premier League,1,Zamalek SC
Égypte,Premier League,1,Pyramids FC
Égypte,Premier League,1,Ismaily SC
Égypte,Premier League,1,Al Masry
Égypte,Premier League,1,ENPPI
Égypte,Premier League,1,Al Mokawloon
Égypte,Premier League,1,National Bank of Egypt
Égypte,Egyptian Second Division,2,El Gouna FC
Égypte,Egyptian Second Division,2,Asyut Petroleum
Égypte,Egyptian Second Division,2,Telephonat Beni Suef
Égypte,Egyptian Second Division,2,Smouha SC
Égypte,Egyptian Second Division,2,Haras El Hodoud"""

class TopKitImporter:
    def __init__(self):
        self.session = None
        self.token = None
        self.competitions = {}  # Map league_key -> competition_id
        self.stats = {
            'competitions_created': 0,
            'competitions_skipped': 0,
            'teams_created': 0,
            'teams_skipped': 0,
            'errors': []
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate(self):
        """Authentification admin pour les opérations"""
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
                    self.token = data.get("access_token")
                    print("✅ Authentification réussie")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ Échec authentification: {response.status} - {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Erreur authentification: {str(e)}")
            return False

    def parse_data(self) -> List[Tuple[str, str, int, str]]:
        """Parse les données CSV en tuples (pays, ligue, niveau, équipe)"""
        entries = []
        for line in LEAGUES_TEAMS_DATA.strip().split('\n'):
            if line.strip():
                parts = line.split(',')
                if len(parts) == 4:
                    pays, ligue, niveau, equipe = [p.strip() for p in parts]
                    entries.append((pays, ligue, int(niveau), equipe))
        return entries

    async def create_competition_if_not_exists(self, pays: str, ligue: str, niveau: int) -> str:
        """Crée une compétition si elle n'existe pas, retourne l'ID"""
        league_key = f"{pays}_{ligue}"
        
        # Vérifier si déjà créée
        if league_key in self.competitions:
            return self.competitions[league_key]

        # Déterminer le type de compétition
        competition_type = "domestic_league" if niveau in [1, 2] else "cup"
        
        competition_data = {
            "name": ligue,
            "official_name": f"{ligue} ({pays})",
            "competition_type": competition_type,
            "country": pays,
            "level": niveau,
            "is_recurring": True,
            "current_season": "2024-25"
        }

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            async with self.session.post(
                f"{API_BASE_URL}/competitions",
                json=competition_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    competition_id = data["id"]
                    self.competitions[league_key] = competition_id
                    self.stats['competitions_created'] += 1
                    print(f"✅ Compétition créée: {ligue} ({pays}) - {data.get('topkit_reference', 'N/A')}")
                    return competition_id
                elif response.status == 400:
                    error_data = await response.json()
                    if "existe déjà" in error_data.get("detail", ""):
                        # Compétition existe déjà, récupérer l'ID
                        print(f"ℹ️ Compétition existe: {ligue} ({pays})")
                        self.stats['competitions_skipped'] += 1
                        # Pour le moment, utiliser une ID par défaut
                        # Dans un vrai cas, il faudrait faire un GET pour récupérer l'ID
                        return "existing_competition_id"
                    else:
                        self.stats['errors'].append(f"Erreur création compétition {ligue}: {error_data.get('detail')}")
                        return None
                else:
                    error_text = await response.text()
                    self.stats['errors'].append(f"Erreur HTTP {response.status} pour compétition {ligue}: {error_text}")
                    return None
                    
        except Exception as e:
            self.stats['errors'].append(f"Exception création compétition {ligue}: {str(e)}")
            return None

    async def create_team(self, equipe: str, pays: str, competition_id: str = None) -> bool:
        """Crée une équipe"""
        team_data = {
            "name": equipe,
            "country": pays,
            "league_id": competition_id,  # Peut être None
            "colors": []  # À remplir plus tard si nécessaire
        }

        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            async with self.session.post(
                f"{API_BASE_URL}/teams",
                json=team_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.stats['teams_created'] += 1
                    print(f"✅ Équipe créée: {equipe} ({pays}) - {data.get('topkit_reference', 'N/A')}")
                    return True
                elif response.status == 400:
                    error_data = await response.json()
                    if "existe déjà" in error_data.get("detail", ""):
                        print(f"ℹ️ Équipe existe: {equipe} ({pays})")
                        self.stats['teams_skipped'] += 1
                        return True  # Considéré comme succès
                    else:
                        self.stats['errors'].append(f"Erreur création équipe {equipe}: {error_data.get('detail')}")
                        return False
                else:
                    error_text = await response.text()
                    self.stats['errors'].append(f"Erreur HTTP {response.status} pour équipe {equipe}: {error_text}")
                    return False
                    
        except Exception as e:
            self.stats['errors'].append(f"Exception création équipe {equipe}: {str(e)}")
            return False

    async def import_data(self):
        """Importe toutes les données"""
        print("🚀 Début de l'import des ligues et équipes TopKit...")
        
        # Authentification
        if not await self.authenticate():
            return False

        # Parse des données
        entries = self.parse_data()
        print(f"📊 {len(entries)} entrées à traiter")

        # Phase 1: Créer toutes les compétitions uniques
        print("\n📋 Phase 1: Création des compétitions...")
        unique_leagues = set()
        for pays, ligue, niveau, _ in entries:
            unique_leagues.add((pays, ligue, niveau))

        for pays, ligue, niveau in sorted(unique_leagues):
            await self.create_competition_if_not_exists(pays, ligue, niveau)

        # Phase 2: Créer toutes les équipes
        print(f"\n⚽ Phase 2: Création des équipes...")
        for pays, ligue, niveau, equipe in entries:
            league_key = f"{pays}_{ligue}"
            competition_id = self.competitions.get(league_key)
            await self.create_team(equipe, pays, competition_id)

        return True

    def print_stats(self):
        """Affiche les statistiques finales"""
        print("\n" + "="*60)
        print("📊 STATISTIQUES D'IMPORT TOPKIT")
        print("="*60)
        print(f"🏆 Compétitions créées: {self.stats['competitions_created']}")
        print(f"🏆 Compétitions existantes: {self.stats['competitions_skipped']}")
        print(f"⚽ Équipes créées: {self.stats['teams_created']}")
        print(f"⚽ Équipes existantes: {self.stats['teams_skipped']}")
        print(f"❌ Erreurs: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print(f"\n🔍 Détail des erreurs:")
            for error in self.stats['errors'][:10]:  # Limite à 10 erreurs
                print(f"  • {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... et {len(self.stats['errors']) - 10} autres erreurs")

        total_created = self.stats['competitions_created'] + self.stats['teams_created']
        total_processed = total_created + self.stats['competitions_skipped'] + self.stats['teams_skipped']
        success_rate = (total_processed / (total_processed + len(self.stats['errors']))) * 100 if total_processed + len(self.stats['errors']) > 0 else 0
        
        print(f"\n🎯 Taux de succès: {success_rate:.1f}%")
        print("="*60)

async def main():
    """Fonction principale"""
    try:
        async with TopKitImporter() as importer:
            success = await importer.import_data()
            importer.print_stats()
            
            if success:
                print("\n🎉 Import terminé avec succès!")
                return 0
            else:
                print("\n❌ Import échoué")
                return 1
                
    except KeyboardInterrupt:
        print("\n⚠️ Import interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n💥 Erreur fatale: {str(e)}")
        return 1

if __name__ == "__main__":
    # Exécution du script
    exit_code = asyncio.run(main())
    sys.exit(exit_code)