#!/usr/bin/env bash
# Backup MongoDB Atlas → /mnt/Freebox-1/backups/mongo/ (NAS Freebox).
# Lancé via cron tp_admin (3h du matin). Rétention 30j rolling.
#
# Restore manuel :
#   docker run --rm -v /mnt/Freebox-1/backups/mongo:/backup mongo:7 \
#     mongorestore --uri="<MONGO_URL>" --gzip --archive=/backup/topkit-YYYYMMDD-HHMMSS.archive.gz [--drop]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env.backend"
BACKUP_DIR="/mnt/Freebox-1/backups/mongo"
RETENTION_DAYS=30

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
ARCHIVE_HOST="$BACKUP_DIR/topkit-$TS.archive.gz"

# mongodump via image one-shot (pas d'install mongo sur la VM)
docker run --rm \
  -v "$BACKUP_DIR:/backup" \
  mongo:7 \
  mongodump --uri="$MONGO_URL" --gzip --archive="/backup/topkit-$TS.archive.gz" --quiet

if [[ ! -s "$ARCHIVE_HOST" ]]; then
  echo "ERR: archive vide ou absente ($ARCHIVE_HOST)" >&2
  exit 2
fi

SIZE=$(du -h "$ARCHIVE_HOST" | cut -f1)
echo "[$(date -Iseconds)] backup OK : $ARCHIVE_HOST ($SIZE)"

# Rétention : supprime les dumps > RETENTION_DAYS jours
DELETED=$(find "$BACKUP_DIR" -maxdepth 1 -name 'topkit-*.archive.gz' -mtime "+$RETENTION_DAYS" -print -delete | wc -l)
[[ "$DELETED" -gt 0 ]] && echo "[$(date -Iseconds)] rétention : $DELETED dump(s) > ${RETENTION_DAYS}j supprimé(s)"

exit 0
