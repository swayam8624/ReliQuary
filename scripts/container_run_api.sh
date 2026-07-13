#!/usr/bin/env bash
set -euo pipefail

container system start --enable-kernel-install --timeout 120
container network create reliquary-net >/dev/null 2>&1 || true
container delete --force reliquary-api >/dev/null 2>&1 || true

postgres_host="$(
  container inspect reliquary-postgres | python -c 'import json,sys
data=json.load(sys.stdin)
for network in data[0]["status"]["networks"]:
    if network["network"] == "reliquary-net":
        print(network["ipv4Address"].split("/")[0])
        break
else:
    raise SystemExit("reliquary-postgres is not attached to reliquary-net")'
)"

container run \
  --detach \
  --name reliquary-api \
  --network reliquary-net \
  --publish 8000:8000 \
  --env RELIQUARY_STORAGE_BACKEND=postgres \
  --env DATABASE_URL=postgresql://reliquary:reliquary-dev-password@"$postgres_host":5432/reliquary \
  --env RELIQUARY_DEV_SECRET_KEY=reliquary-local-container-secret \
  reliquary-api:local

echo "Waiting for ReliQuary API health..."
for _ in $(seq 1 90); do
  if curl -fsS http://localhost:8000/health >/dev/null 2>&1; then
    curl -fsS http://localhost:8000/health
    echo
    exit 0
  fi
  sleep 1
done

container logs -n 120 reliquary-api || true
echo "ReliQuary API did not become healthy." >&2
exit 1
