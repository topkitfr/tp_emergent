#!/usr/bin/env bash
# Backup MongoDB Atlas → /mnt/Freebox-1/backups/mongo/ (NAS Freebox).
# Lancé via cron tp_admin (3h du matin). Rétention 30j rolling.
#
# Prérequis : mongodb-database-tools installé sur l'hôte.
# Pas de Docker ici : l'image mongo:7 ne tourne pas sur le CPU ARM
# de la Freebox (< ARMv8.2-A).
#
# Install (déjà fait, mai 2026) :
#   curl -fsSL -A 'Mozilla/5.0' -o /tmp/mt.deb \
#     https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2204-arm64-100.13.0.deb
#   sudo dpkg -i /tmp/mt.deb && rm /tmp/mt.deb
#
# Restore manuel :
#   mongorestore --uri="<MONGO_URL>" --gzip \
#     --archive=/mnt/Freebox-1/backups/mongo/topkit-YYYYMMDD-HHMMSS.archive.gz [--drop]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env.backend"
BACKUP_DIR="/mnt/Freebox-1/backups/mongo"
RETENTION_DAYS=30

if ! command -v mongodump >/dev/null; then
  echo "ERR: mongodump introuvable (cf. en-tête du script pour install)" >&2
  exit 1
fi

if [[ ! -r "$ENV_FILE" ]]; then
  echo "ERR: $ENV_FILE introuvable ou non lisible" >&2
  exit 1
fi

MONGO_URL=$(grep -E '^MONGO_URL=' "$ENV_FILE" | cut -d= -f2-)
if [[ -z "${MONGO_URL:-}" ]]; then
  echo "ERR: MONGO_URL absent de $ENV_FILE" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

TS=$(date +%Y%m%d-%H%M%S)
ARCHIVE="$BACKUP_DIR/topkit-$TS.archive.gz"

mongodump --uri="$MONGO_URL" --gzip --archive="$ARCHIVE" --quiet

if [[ ! -s "$ARCHIVE" ]]; then
  echo "ERR: archive vide ou absente ($ARCHIVE)" >&2
  exit 2
fi

SIZE=$(du -h "$ARCHIVE" | cut -f1)
echo "[$(date -Iseconds)] backup OK : $ARCHIVE ($SIZE)"

# Rétention : supprime les dumps > RETENTION_DAYS jours
DELETED=$(find "$BACKUP_DIR" -maxdepth 1 -name 'topkit-*.archive.gz' -mtime "+$RETENTION_DAYS" -print -delete | wc -l)
[[ "$DELETED" -gt 0 ]] && echo "[$(date -Iseconds)] rétention : $DELETED dump(s) > ${RETENTION_DAYS}j supprimé(s)"

exit 0
