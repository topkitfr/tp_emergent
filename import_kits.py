import asyncio
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import re
import sys

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "topkit")

if len(sys.argv) > 1:
    CSV_PATH = sys.argv[1]
elif os.environ.get("CSV_PATH"):
    CSV_PATH = os.environ.get("CSV_PATH")
else:
    print("❌ Chemin CSV manquant.")
    print("   Usage : python import_kits.py /chemin/vers/fichier.csv")
    print("   Ou     : CSV_PATH=/chemin/vers/fichier.csv python import_kits.py")
    sys.exit(1)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


async def import_kits():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db["kits"]

    df = pd.read_csv(CSV_PATH)
    df = df.drop_duplicates(subset=["team", "season", "type", "brand"])
    df = df.where(pd.notna(df), None)

    print(f"📦 {len(df)} maillots uniques à importer...")

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        team = row["team"] or ""
        season = row["season"] or ""
        kit_type = row["type"] or ""
        brand = row["brand"] or ""

        slug = slugify(f"{team}-{season}-{kit_type}-{brand}")

        doc = {
            "slug": slug,
            "team": team,
            "season": season,
            "type": kit_type,
            "design": row["design"],
            "colors": [c.strip() for c in str(row["colors"]).split("/")] if pd.notna(row["colors"]) else [],
            "brand": brand,
            "sponsor": row["sponsor"],
            "league": row["league"],
            "release_date": row["release_date"],
            "img_url": row["img_url"],
            "source_url": row["source_url"],
            "status": "approved",
        }

        existing = await collection.find_one({"slug": slug})
        if existing:
            skipped += 1
            continue

        await collection.insert_one(doc)
        inserted += 1

    print(f"✅ {inserted} insérés, {skipped} doublons ignorés")
    client.close()


if __name__ == "__main__":
    asyncio.run(import_kits())
