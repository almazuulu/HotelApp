#!/bin/sh
# Wait for PostgreSQL, apply migrations, then hand over to the container command.
#
# Compose already gates startup on the `db` healthcheck; this loop is the second
# guard, because a healthy server still rejects connections for a short window
# while it finishes initialising the database.
set -eu

POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT} ..."
attempt=0
until pg_isready \
    --host="${POSTGRES_HOST}" \
    --port="${POSTGRES_PORT}" \
    --username="${POSTGRES_USER:-postgres}" \
    --dbname="${POSTGRES_DB:-postgres}" \
    --quiet; do
    attempt=$((attempt + 1))
    if [ "${attempt}" -ge 60 ]; then
        echo "PostgreSQL is still unreachable after ${attempt} attempts. Giving up." >&2
        exit 1
    fi
    sleep 1
done
echo "PostgreSQL is ready."

python manage.py migrate --noinput

exec "$@"
