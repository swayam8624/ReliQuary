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

## One GUI

Run the full local product surface with one command:

```bash
./scripts/run_brain_vault.sh
```

That starts the local API, builds the Vulkan/ImGui client if needed, and opens
the Brain Vault window.

## Vulkan ImGui Visualizer

On macOS this uses Vulkan through MoltenVK. Manual build:

```bash
./scripts/build_vulkan_visualizer.sh
visualizer/vulkan/build/reliquary_vulkan_visualizer
```

The executable now owns a real Vulkan swapchain and Dear ImGui UI. It includes:

- API URL configuration.
- Vault creation.
- Text secret storage.
- File/folder secret storage.
- Per-secret password field.
- Share-link creation.
- Trust-gated graph nodes for storage, gate, and answer.
- Chat-style command panel that routes intent to the correct control surface.

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

## Share Links

Share links are expiring token links with optional share password and max-view
limits:

```bash
curl -s -X POST http://localhost:8000/share/create \
  -H 'Content-Type: application/json' \
  -d '{
    "vault_id": "replace-with-vault-id",
    "secret_name": "recovery-file",
    "created_by": "alice",
    "ttl_minutes": 60,
    "max_views": 1,
    "share_password": "share-pass"
  }'
```
