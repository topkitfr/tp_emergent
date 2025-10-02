"""
Create sample data for the Edit Kit Form feature:
1. Players with aura ratings
2. Competitions/leagues for dropdowns
3. Additional teams if needed
"""
import asyncio
import os
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from collaborative_models import Player, Competition, Team, PlayerType

# Database setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'topkit')

async def create_sample_players():
    """Create sample players with aura ratings"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Sample players with aura ratings (influence_coefficient)
    players_data = [
        # Superstars (Aura 5.0)
        {"name": "Lionel Messi", "full_name": "Lionel Andrés Messi Cuccittini", "nationality": "Argentina", "position": "Forward", "influence_coefficient": 5.0, "player_type": PlayerType.SHOWDOWN_LEGEND},
        {"name": "Cristiano Ronaldo", "full_name": "Cristiano Ronaldo dos Santos Aveiro", "nationality": "Portugal", "position": "Forward", "influence_coefficient": 5.0, "player_type": PlayerType.SHOWDOWN_LEGEND},
        
        # Top Stars (Aura 4.6-4.8)
        {"name": "Kylian Mbappé", "full_name": "Kylian Mbappé Lottin", "nationality": "France", "position": "Forward", "influence_coefficient": 4.6, "player_type": PlayerType.SUPERSTAR},
        {"name": "Erling Haaland", "full_name": "Erling Braut Haaland", "nationality": "Norway", "position": "Forward", "influence_coefficient": 4.7, "player_type": PlayerType.SUPERSTAR},
        {"name": "Neymar Jr", "full_name": "Neymar da Silva Santos Júnior", "nationality": "Brazil", "position": "Forward", "influence_coefficient": 4.5, "player_type": PlayerType.SUPERSTAR},
        
        # Stars (Aura 4.0-4.4)
        {"name": "Kevin De Bruyne", "full_name": "Kevin De Bruyne", "nationality": "Belgium", "position": "Midfielder", "influence_coefficient": 4.2, "player_type": PlayerType.STAR},
        {"name": "Mohamed Salah", "full_name": "Mohamed Salah Hamed Mahrous Ghaly", "nationality": "Egypt", "position": "Forward", "influence_coefficient": 4.3, "player_type": PlayerType.STAR},
        {"name": "Robert Lewandowski", "full_name": "Robert Lewandowski", "nationality": "Poland", "position": "Forward", "influence_coefficient": 4.1, "player_type": PlayerType.STAR},
        {"name": "Luka Modrić", "full_name": "Luka Modrić", "nationality": "Croatia", "position": "Midfielder", "influence_coefficient": 4.0, "player_type": PlayerType.STAR},
        {"name": "Virgil van Dijk", "full_name": "Virgil van Dijk", "nationality": "Netherlands", "position": "Defender", "influence_coefficient": 3.9, "player_type": PlayerType.STAR},
        
        # Good Players (Aura 3.0-3.8)
        {"name": "Pedri", "full_name": "Pedro González López", "nationality": "Spain", "position": "Midfielder", "influence_coefficient": 3.5, "player_type": PlayerType.GOOD_PLAYER},
        {"name": "Gavi", "full_name": "Pablo Martín Páez Gavira", "nationality": "Spain", "position": "Midfielder", "influence_coefficient": 3.2, "player_type": PlayerType.GOOD_PLAYER},
        {"name": "Jamal Musiala", "full_name": "Jamal Musiala", "nationality": "Germany", "position": "Midfielder", "influence_coefficient": 3.4, "player_type": PlayerType.GOOD_PLAYER},
        {"name": "Eduardo Camavinga", "full_name": "Eduardo Camavinga", "nationality": "France", "position": "Midfielder", "influence_coefficient": 3.1, "player_type": PlayerType.GOOD_PLAYER},
        {"name": "Phil Foden", "full_name": "Philip Walter Foden", "nationality": "England", "position": "Midfielder", "influence_coefficient": 3.6, "player_type": PlayerType.GOOD_PLAYER},
        
        # Rising Stars (Aura 2.8-3.4)
        {"name": "Jude Bellingham", "full_name": "Jude Victor William Bellingham", "nationality": "England", "position": "Midfielder", "influence_coefficient": 3.8, "player_type": PlayerType.GOOD_PLAYER},
        {"name": "Aurélien Tchouaméni", "full_name": "Aurélien Djani Tchouaméni", "nationality": "France", "position": "Midfielder", "influence_coefficient": 3.0, "player_type": PlayerType.GOOD_PLAYER},
        {"name": "Ryan Gravenberch", "full_name": "Ryan Gravenberch", "nationality": "Netherlands", "position": "Midfielder", "influence_coefficient": 2.9, "player_type": PlayerType.GOOD_PLAYER},
        
        # Legends (Historical Aura 5.0)
        {"name": "Diego Maradona", "full_name": "Diego Armando Maradona", "nationality": "Argentina", "position": "Forward", "influence_coefficient": 5.0, "player_type": PlayerType.SHOWDOWN_LEGEND},
        {"name": "Pelé", "full_name": "Edson Arantes do Nascimento", "nationality": "Brazil", "position": "Forward", "influence_coefficient": 5.0, "player_type": PlayerType.SHOWDOWN_LEGEND},
        {"name": "Zinedine Zidane", "full_name": "Zinedine Yazid Zidane", "nationality": "France", "position": "Midfielder", "influence_coefficient": 4.8, "player_type": PlayerType.SHOWDOWN_LEGEND},
        {"name": "Ronaldinho", "full_name": "Ronaldo de Assis Moreira", "nationality": "Brazil", "position": "Forward", "influence_coefficient": 4.7, "player_type": PlayerType.SHOWDOWN_LEGEND},
    ]
    
    created_count = 0
    for player_data in players_data:
        # Check if player already exists
        existing = await db.players.find_one({"name": player_data["name"]})
        if not existing:
            player = Player(
                id=str(uuid.uuid4()),
                name=player_data["name"],
                full_name=player_data["full_name"],
                nationality=player_data["nationality"],
                position=player_data["position"],
                influence_coefficient=player_data["influence_coefficient"],
                player_type=player_data["player_type"],
                created_at=datetime.now(timezone.utc),
                created_by="system",
                topkit_reference=f"TK-PLAYER-{uuid.uuid4().hex[:6].upper()}"
            )
            await db.players.insert_one(player.dict())
            created_count += 1
            print(f"Created player: {player.name} (Aura: {player.influence_coefficient})")
    
    print(f"Total players created: {created_count}")
    client.close()

async def create_sample_competitions():
    """Create sample competitions/leagues for dropdowns"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    competitions_data = [
        # Major European Leagues
        {"competition_name": "La Liga", "short_name": "La Liga", "type": "League", "country": "Spain", "level": 1},
        {"competition_name": "Premier League", "short_name": "PL", "type": "League", "country": "England", "level": 1},
        {"competition_name": "Bundesliga", "short_name": "Bundesliga", "type": "League", "country": "Germany", "level": 1},
        {"competition_name": "Serie A", "short_name": "Serie A", "type": "League", "country": "Italy", "level": 1},
        {"competition_name": "Ligue 1", "short_name": "L1", "type": "League", "country": "France", "level": 1},
        
        # European Competitions
        {"competition_name": "UEFA Champions League", "short_name": "UCL", "type": "Cup", "country": "Europe", "level": 1},
        {"competition_name": "UEFA Europa League", "short_name": "UEL", "type": "Cup", "country": "Europe", "level": 2},
        {"competition_name": "UEFA Europa Conference League", "short_name": "UECL", "type": "Cup", "country": "Europe", "level": 3},
        
        # International Competitions
        {"competition_name": "FIFA World Cup", "short_name": "World Cup", "type": "Tournament", "country": "International", "level": 1},
        {"competition_name": "UEFA European Championship", "short_name": "Euro", "type": "Tournament", "country": "Europe", "level": 1},
        {"competition_name": "Copa América", "short_name": "Copa América", "type": "Tournament", "country": "South America", "level": 1},
        
        # Domestic Cups
        {"competition_name": "Copa del Rey", "short_name": "Copa del Rey", "type": "Cup", "country": "Spain", "level": 2},
        {"competition_name": "FA Cup", "short_name": "FA Cup", "type": "Cup", "country": "England", "level": 2},
        {"competition_name": "DFB-Pokal", "short_name": "DFB-Pokal", "type": "Cup", "country": "Germany", "level": 2},
        {"competition_name": "Coppa Italia", "short_name": "Coppa Italia", "type": "Cup", "country": "Italy", "level": 2},
        {"competition_name": "Coupe de France", "short_name": "Coupe de France", "type": "Cup", "country": "France", "level": 2},
    ]
    
    created_count = 0
    for comp_data in competitions_data:
        # Check if competition already exists
        existing = await db.competitions.find_one({"competition_name": comp_data["competition_name"]})
        if not existing:
            competition = Competition(
                id=str(uuid.uuid4()),
                competition_name=comp_data["competition_name"],
                short_name=comp_data["short_name"],
                type=comp_data["type"],
                country=comp_data["country"],
                level=comp_data["level"],
                created_at=datetime.now(timezone.utc),
                created_by="system",
                topkit_reference=f"TK-COMP-{uuid.uuid4().hex[:6].upper()}"
            )
            await db.competitions.insert_one(competition.dict())
            created_count += 1
            print(f"Created competition: {competition.competition_name}")
    
    print(f"Total competitions created: {created_count}")
    client.close()

async def main():
    """Create all sample data"""
    print("Creating sample data for Edit Kit Form...")
    print("\n1. Creating sample players with aura ratings...")
    await create_sample_players()
    
    print("\n2. Creating sample competitions...")
    await create_sample_competitions()
    
    print("\n✅ Sample data creation completed!")

if __name__ == "__main__":
    asyncio.run(main())