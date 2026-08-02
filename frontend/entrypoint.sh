#!/bin/sh
# The named node_modules volume survives container rebuilds. Keep it aligned with
# the lockfile so new imports are available immediately after a dependency change.
set -eu

LOCKFILE_STAMP="/app/node_modules/.hotelapp-package-lock.json"

if ! cmp -s /app/package-lock.json "$LOCKFILE_STAMP"; then
    npm ci
    cp /app/package-lock.json "$LOCKFILE_STAMP"
fi

exec "$@"
