"""
reset_versions.py
-----------------
1. Supprime toutes les versions existantes
2. Recrée les versions depuis les master_kits :
   - 1 version "authentic" pour TOUS les kits
   - 1 version "replica" uniquement pour les kits >= saison 2000
   - front_photo hérite du master_kit (jamais img_url externe)
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Chargement du .env (cherche dans plusieurs emplacements)
for env_path in [
    os.path.join(os.path.dirname(__file__), '..', '.env'),
    os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
    os.path.expanduser('~/tp_emergent/backend/.env'),
    os.path.expanduser('~/.env'),
]:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[OK] .env chargé depuis : {env_path}")
        break

MONGO_URL = os.environ.get("MONGO_URL") or os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME", "topkit")

if not MONGO_URL:
    print("[ERREUR] Variable MONGO_URL introuvable.")
    print("Lance : export MONGO_URL='mongodb+srv://...' puis relance le script.")
    sys.exit(1)

print(f"[OK] Connexion à MongoDB : {MONGO_URL[:40]}...")
client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=10000)

try:
    client.admin.command('ping')
    print("[OK] MongoDB connecté !")
except Exception as e:
    print(f"[ERREUR] Impossible de se connecter : {e}")
    sys.exit(1)

db = client[DB_NAME]

# --- Étape 1 : Suppression des versions existantes ---
print("\n[1/3] Suppression des versions existantes...")
result = db.versions.delete_many({})
print(f"      {result.deleted_count} versions supprimées.")

# --- Étape 2 : Récupération des master_kits ---
print("\n[2/3] Récupération des master_kits...")
master_kits = list(db.master_kits.find({}))
total = len(master_kits)
print(f"      {total} master_kits trouvés.")

if total == 0:
    print("[ERREUR] Aucun master_kit trouvé. Vérifie le nom de la collection.")
    sys.exit(1)

# --- Étape 3 : Génération des versions ---
print("\n[3/3] Génération des versions...")

versions = []
count_authentic = 0
count_replica = 0

for kit in master_kits:
    kit_id = kit['_id']

    # Récupère l'année depuis le champ season (ex: "2003-2004" → 2003, ou "2003" → 2003)
    season_raw = str(kit.get('season', '') or kit.get('year', '') or '1900')
    try:
        season_year = int(season_raw[:4])
    except ValueError:
        season_year = 1900

    # Photo : uniquement depuis le NAS, jamais img_url externe
    front_photo = kit.get('front_photo', '')

    # Champs communs
    base = {
        'master_kit_id': kit_id,
        'club_id': kit.get('club_id'),
        'season': kit.get('season'),
        'kit_type': kit.get('kit_type'),
        'brand': kit.get('brand'),
        'front_photo': front_photo,
        'back_photo': kit.get('back_photo', ''),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'user_id': None,  # Pas encore assignée à un user
    }

    # Version authentique (toujours)
    authentic = {**base, 'version_type': 'authentic'}
    versions.append(authentic)
    count_authentic += 1

    # Version replica (uniquement à partir de 2000)
    if season_year >= 2000:
        replica = {**base, 'version_type': 'replica'}
        versions.append(replica)
        count_replica += 1

# Insertion en batch
print(f"      Insertion de {len(versions)} versions ({count_authentic} authentiques + {count_replica} replicas)...")
if versions:
    result = db.versions.insert_many(versions)
    print(f"\n[DONE] {len(result.inserted_ids)} versions insérées avec succès !")
else:
    print("[WARN] Aucune version à insérer.")

print(f"\n--- Résumé ---")
print(f"  Master kits    : {total}")
print(f"  Authentiques   : {count_authentic}")
print(f"  Replicas       : {count_replica}")
print(f"  Total versions : {len(versions)}")
