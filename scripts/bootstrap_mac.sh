#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if command -v cargo >/dev/null 2>&1; then
  scripts/build_rust_modules.sh
else
  echo "cargo is not installed; Python AES-GCM fallback will work, PQC Rust calls will be unavailable."
fi

python -m compileall apps auth core vaults agents zk scripts
pytest -q \
  tests/test_crypto.py \
  tests/api/test_vault_access.py \
  tests/api/test_research_surface.py \
  tests/test_vault_storage_persistence.py \
  tests/test_context_proof.py \
  tests/test_consensus_system.py

echo "Bootstrap complete."
