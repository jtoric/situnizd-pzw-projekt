#!/usr/bin/env bash
# Kopija baze produkcijskog stoga (docker-compose.prod.yml) i provjera da se kopija može vratiti.
#
#   bash scripts/backup.sh                 # iz korijena repozitorija
#
# Kopija se sprema u backups/ (ili BACKUP_DIR), a zatim vraća u privremenu bazu na istom
# poslužitelju baze. Kopija koja se nikad nije vratila nije provjerena kopija: pogreška u
# naredbi, prazna datoteka ili pogrešna baza vide se tek kad kopija zatreba.
set -euo pipefail

COMPOSE=(docker compose -f docker-compose.prod.yml --env-file .env.prod)
DIR="${BACKUP_DIR:-backups}"
CHECK_DB=pl_reg_provjera

mkdir -p "$DIR"
FILE="$DIR/pl_reg-$(date +%Y%m%d-%H%M%S).sql.gz"

# -T: bez terminala, da izlaz naredbe ide u cijev, a ne na zaslon
"${COMPOSE[@]}" exec -T db pg_dump -U pl_user pl_reg | gzip > "$FILE"

# Provjera vraćanja u privremenu bazu; ON_ERROR_STOP prekida na prvoj pogrešci u kopiji
"${COMPOSE[@]}" exec -T db dropdb -U pl_user --if-exists "$CHECK_DB"
"${COMPOSE[@]}" exec -T db createdb -U pl_user "$CHECK_DB"
gunzip -c "$FILE" | "${COMPOSE[@]}" exec -T db psql -q -v ON_ERROR_STOP=1 -U pl_user -d "$CHECK_DB" > /dev/null
USERS=$("${COMPOSE[@]}" exec -T db psql -tA -U pl_user -d "$CHECK_DB" -c "SELECT count(*) FROM users")
"${COMPOSE[@]}" exec -T db dropdb -U pl_user "$CHECK_DB"

if [ "${USERS//[[:space:]]/}" -lt 1 ]; then
  echo "Vraćena kopija nema nijednog korisnika: $FILE" >&2
  exit 1
fi
echo "Kopija $FILE je vraćena u privremenu bazu: korisnika ${USERS//[[:space:]]/}."
