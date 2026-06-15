#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python}"

if [[ "$PYTHON_BIN" == */* ]]; then
  if [[ "$PYTHON_BIN" != /* ]]; then
    PYTHON_BIN="$ROOT_DIR/$PYTHON_BIN"
  fi
else
  PYTHON_BIN="$(command -v "$PYTHON_BIN")"
fi

if ! "$PYTHON_BIN" -m maturin --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m pip install maturin
fi

PYTHON_PREFIX="$("$PYTHON_BIN" -c 'import sys; print(sys.prefix)')"
PYTHON_BASE_PREFIX="$("$PYTHON_BIN" -c 'import sys; print(sys.base_prefix)')"

if [[ "$PYTHON_PREFIX" != "$PYTHON_BASE_PREFIX" ]]; then
  export VIRTUAL_ENV="$PYTHON_PREFIX"
  export PATH="$VIRTUAL_ENV/bin:$PATH"
fi

unset CONDA_DEFAULT_ENV CONDA_EXE CONDA_PREFIX CONDA_PROMPT_MODIFIER CONDA_PYTHON_EXE CONDA_SHLVL
export PYO3_PYTHON="$PYTHON_BIN"
export PYTHON_SYS_EXECUTABLE="$PYTHON_BIN"

RUST_TARGET="${RUST_TARGET:-$("$PYTHON_BIN" - <<'PY'
import platform
import sys

machine = platform.machine().lower()
if sys.platform == "darwin":
    if machine in {"arm64", "aarch64"}:
        print("aarch64-apple-darwin")
    elif machine in {"x86_64", "amd64"}:
        print("x86_64-apple-darwin")
PY
)}"

if [[ -n "$RUST_TARGET" ]] && command -v rustup >/dev/null 2>&1; then
  if ! rustup target list --installed | grep -qx "$RUST_TARGET"; then
    rustup target add "$RUST_TARGET"
  fi
fi

WHEEL_DIR="$(mktemp -d)"
trap 'rm -rf "$WHEEL_DIR"' EXIT

for crate in encryptor merkle; do
  (
    cd "$ROOT_DIR/rust_modules/$crate"
    if [[ -n "$RUST_TARGET" ]]; then
      "$PYTHON_BIN" -m maturin build --release --target "$RUST_TARGET" --out "$WHEEL_DIR"
    else
      "$PYTHON_BIN" -m maturin build --release --out "$WHEEL_DIR"
    fi
  )
done

"$PYTHON_BIN" -m pip install --force-reinstall --no-deps "$WHEEL_DIR"/*.whl
echo "Rust modules installed into $("$PYTHON_BIN" -c 'import sys; print(sys.executable)')"
