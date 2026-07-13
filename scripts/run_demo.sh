#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

scripts/container_run_postgres.sh
scripts/container_build_api.sh
scripts/container_run_api.sh
scripts/container_smoke.sh

echo
echo "ReliQuary is running at http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
