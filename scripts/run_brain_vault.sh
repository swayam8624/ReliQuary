#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
python -m pip install -r requirements.txt >/dev/null

cleanup() {
  if [ -n "${API_PID:-}" ]; then
    kill "$API_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

python -m uvicorn apps.api.main:app --host "$API_HOST" --port "$API_PORT" >/tmp/reliquary-api.log 2>&1 &
API_PID=$!

echo "Starting ReliQuary API on http://$API_HOST:$API_PORT ..."
for _ in $(seq 1 40); do
  if curl -fsS "http://$API_HOST:$API_PORT/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

if ! curl -fsS "http://$API_HOST:$API_PORT/health" >/dev/null 2>&1; then
  echo "API did not become healthy. See /tmp/reliquary-api.log" >&2
  exit 1
fi

./scripts/build_vulkan_visualizer.sh >/tmp/reliquary-vulkan-build.log 2>&1
echo "Opening ReliQuary Brain Vault."
visualizer/vulkan/build/reliquary_vulkan_visualizer
