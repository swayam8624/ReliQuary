#!/usr/bin/env bash
set -euo pipefail

container system start --enable-kernel-install --timeout 120
container network create reliquary-net >/dev/null 2>&1 || true
container delete --force reliquary-postgres >/dev/null 2>&1 || true

container run \
  --detach \
  --name reliquary-postgres \
  --network reliquary-net \
  --publish 5432:5432 \
  --env POSTGRES_DB=reliquary \
  --env POSTGRES_USER=reliquary \
  --env POSTGRES_PASSWORD=reliquary-dev-password \
  postgres:16-alpine

echo "Waiting for Postgres to accept connections..."
for _ in $(seq 1 60); do
  if container exec reliquary-postgres pg_isready -U reliquary -d reliquary >/dev/null 2>&1; then
    echo "Postgres is ready."
    exit 0
  fi
  sleep 1
done

container logs -n 80 reliquary-postgres || true
echo "Postgres did not become ready." >&2
exit 1
