#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "== health =="
curl -fsS "$BASE_URL/health"
echo

echo "== create vault =="
vault_json="$(
  curl -fsS -X POST "$BASE_URL/vaults/" \
    -H 'Content-Type: application/json' \
    -d '{"name":"container-vault","description":"Apple container Postgres smoke vault","owner_id":"alice"}'
)"
echo "$vault_json"
vault_id="$(python -c 'import json,sys; print(json.load(sys.stdin)["vault_id"])' <<<"$vault_json")"

echo "== store secret =="
curl -fsS -X POST "$BASE_URL/vaults/secrets?vault_id=$vault_id" \
  -H 'Content-Type: application/json' \
  -d '{"secret_name":"api-token","secret_value":"sk-container-smoke-secret","metadata":{"source":"container_smoke"}}'
echo

echo "== retrieve secret =="
curl -fsS "$BASE_URL/vaults/secrets/api-token?vault_id=$vault_id"
echo

echo "== context verify =="
curl -fsS -X POST "$BASE_URL/context/verify" \
  -H 'Content-Type: application/json' \
  -d "{\"user_id\":\"alice\",\"ip_address\":\"127.0.0.1\",\"user_agent\":\"reliquary-container-smoke/1.0\",\"timestamp\":\"$timestamp\",\"device_fingerprint\":\"local-container\"}"
echo
