# Brain Vault Visualizer

ReliQuary now exposes trust-gated access decisions as first-class API events.
That is the data source for the web console, Mac GUI, and Vulkan visualizer.

## Decision API

```bash
POST /access/evaluate
POST /access/request-secret
GET  /access/events
GET  /access/stream
POST /memory/index/local-folder
POST /memory/query
```

Decision outcomes:

- `allow`: full value/path may be shown.
- `redact`: only metadata or existence may be shown.
- `deny`: no resource details are disclosed.

Sensitivity thresholds:

- `public`: 0
- `private`: 50
- `sensitive`: 75
- `secret`: 90
- `sealed`: never directly reveals values

## Vulkan Visualizer

On macOS this uses Vulkan through MoltenVK. Install the Vulkan SDK first, then:

```bash
./scripts/build_vulkan_visualizer.sh
visualizer/vulkan/build/reliquary_vulkan_visualizer
```

The current executable creates a real Vulkan instance and replays access events
as a terminal-rendered brain-vault graph. The next graphics step is a swapchain,
graph node renderer, and ImGui side panel that subscribes to `/access/stream`.

## Permissioned Local Memory

The first real connector is a local Mac folder connector. It indexes filenames,
paths, sizes, owner, vault ID, and sensitivity. It does not copy file contents.

```bash
curl -s -X POST http://localhost:8000/memory/index/local-folder \
  -H 'Content-Type: application/json' \
  -d '{
    "root_path": "/Users/me/Documents",
    "vault_id": "replace-with-vault-id",
    "owner_id": "alice",
    "sensitivity": "sensitive"
  }'
```

Queries are policy-gated. A trusted local owner can receive paths; a low-trust
remote caller receives redacted or denied results.
