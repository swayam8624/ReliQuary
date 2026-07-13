#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/doctor_$(date +%Y%m%d_%H%M%S).log"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_WEBSITE=1
RUN_CONTAINER=0

for arg in "$@"; do
  case "$arg" in
    --skip-website) RUN_WEBSITE=0 ;;
    --container) RUN_CONTAINER=1 ;;
    -h|--help)
      echo "Usage: scripts/doctor_verbose.sh [--skip-website] [--container]"
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

exec > >(tee "$LOG_FILE") 2>&1

section() {
  printf '\n========== %s ==========\n' "$1"
}

run_step() {
  local label="$1"
  shift
  section "$label"
  printf '+'
  printf ' %q' "$@"
  printf '\n'
  "$@"
}

section "ReliQuary doctor"
echo "Root: $ROOT_DIR"
echo "Log:  $LOG_FILE"
echo "Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

section "Toolchain"
command -v "$PYTHON_BIN" && "$PYTHON_BIN" --version
command -v git && git --version
command -v cargo && cargo --version || echo "cargo not found; Rust-backed calls may be unavailable."
command -v node && node --version || echo "node not found; website build will be skipped unless installed."
command -v npm && npm --version || echo "npm not found; website build will be skipped unless installed."
command -v container && container --version || echo "Apple container CLI not found; container smoke is optional."

section "Git state"
git status --short

if [ ! -d ".venv" ]; then
  run_step "Create Python virtualenv" "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
run_step "Install Python dependencies" python -m pip install -r requirements.txt

if command -v cargo >/dev/null 2>&1; then
  run_step "Build Rust/PyO3 modules" scripts/build_rust_modules.sh
else
  section "Build Rust/PyO3 modules"
  echo "Skipped because cargo is not installed."
fi

run_step "Compile Python import surface" python -m compileall apps auth core vaults agents zk scripts
run_step "Run focused pytest matrix" pytest -q \
  tests/test_crypto.py \
  tests/api/test_access_decision.py \
  tests/api/test_memory_retrieval.py \
  tests/api/test_vault_access.py \
  tests/api/test_research_surface.py \
  tests/test_vault_storage_persistence.py \
  tests/test_context_proof.py \
  tests/test_consensus_system.py
run_step "Run in-process research flow" python scripts/research_flow.py

if [ "$RUN_WEBSITE" -eq 1 ] && command -v npm >/dev/null 2>&1; then
  run_step "Install website dependencies" npm --prefix website install
  run_step "Build website" npm --prefix website run build
else
  section "Website build"
  echo "Skipped."
fi

if [ "$RUN_CONTAINER" -eq 1 ]; then
  if command -v container >/dev/null 2>&1; then
    run_step "Build API image with Apple container" scripts/container_build_api.sh
    section "Apple container smoke"
    echo "Run scripts/container_run_postgres.sh and scripts/container_run_api.sh in separate terminals, then scripts/container_smoke.sh."
  else
    section "Apple container smoke"
    echo "Skipped because Apple container CLI is not installed."
  fi
fi

section "Storage modes"
cat <<'INFO'
Local Mac folder:
  RELIQUARY_STORAGE_BACKEND=local
  RELIQUARY_LOCAL_VAULT_PATH="$HOME/ReliQuary Vaults"

Postgres:
  RELIQUARY_STORAGE_BACKEND=postgres
  DATABASE_URL=postgresql://reliquary:reliquary@localhost:5432/reliquary

S3-compatible bucket:
  RELIQUARY_STORAGE_BACKEND=s3
  RELIQUARY_S3_BUCKET=your-bucket
  RELIQUARY_S3_REGION=us-east-1
  RELIQUARY_S3_PREFIX=reliquary
  RELIQUARY_S3_ENDPOINT_URL=https://optional-compatible-endpoint
INFO

section "Done"
echo "Doctor finished successfully. Full log: $LOG_FILE"
