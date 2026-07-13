#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v cmake >/dev/null 2>&1; then
  echo "cmake is required to build the Vulkan visualizer." >&2
  exit 1
fi

if [ -d "$HOME/VulkanSDK" ]; then
  latest_sdk="$(find "$HOME/VulkanSDK" -maxdepth 1 -mindepth 1 -type d | sort | tail -n 1)"
  if [ -n "$latest_sdk" ] && [ -f "$latest_sdk/setup-env.sh" ]; then
    # shellcheck disable=SC1090
    source "$latest_sdk/setup-env.sh"
  fi
fi

cmake -S visualizer/vulkan -B visualizer/vulkan/build
cmake --build visualizer/vulkan/build
echo "Run visualizer/vulkan/build/reliquary_vulkan_visualizer"
