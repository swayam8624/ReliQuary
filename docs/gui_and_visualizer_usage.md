# ReliQuary GUI, Website, and Visualizer Guide

This guide documents the user-facing surfaces that exist in the repository:

- `apps/desktop/reliquary_mac_gui.py`: native Tk Mac GUI that can operate directly on local folder, Postgres, or S3-compatible storage.
- `website/`: browser Brain Vault console that talks to the local FastAPI API.
- `visualizer/vulkan/`: Vulkan plus Dear ImGui console that renders the trust graph and calls the same API.

The backend remains the authority. The GUI, website, and Vulkan renderer do not decide whether a secret is safe to reveal. They collect inputs, send requests, and display the backend decision.

## Start the Local System

```bash
scripts/bootstrap_mac.sh
source .venv/bin/activate
python -m uvicorn apps.api.main:app --reload
```

Open:

- API docs: `http://localhost:8000/docs`
- Website console: run `npm --prefix website run dev`, then open `http://localhost:3000`
- Native Mac GUI: `scripts/run_mac_gui.sh`
- Vulkan ImGui console: `scripts/run_brain_vault.sh`

## Website Console

The website is a local browser console for a running ReliQuary API. It does not store data by itself and it is not a payment or marketing site.

### Top Bar

- `Local API URL`: FastAPI base URL. Default is `http://localhost:8000`.
- `Check API`: calls `/health` and prints the result in the log.

### Vault Setup

- `Name`: human-readable vault name.
- `Owner`: user id that owns the vault. Access requests from another user are capped to low trust unless the resource is public.
- `Description`: local note stored with the vault.
- `Active vault ID`: filled after pressing `Create`; can also be pasted manually.
- `Create`: sends `POST /vaults/`.

### Secret

- `Secret name`: lookup key inside the active vault.
- `Secret value`: text payload to store.
- `Sensitivity`: policy tier used during access decisions.
  - `public`: required trust `0`.
  - `private`: required trust `50`.
  - `sensitive`: required trust `75`.
  - `secret`: required trust `90`.
  - `sealed`: required trust `101`, so direct value reveal is never allowed.
- `Store`: sends `POST /vaults/secrets?vault_id=...`.

### Request Context

- `Requesting user`: identity asking for the secret.
- `Remote address`: request origin. `127.0.0.1`, `localhost`, and `::1` are treated as local.
- `Trust score`: caller score from `0` to `100`.
- `Device`: whether the device is verified.
- `Local`: whether the session is trusted local.
- `Biometric`: whether biometric or explicit high-trust confirmation is present.
- `Remote Deny`: fills the form with a low-trust remote attacker scenario.
- `Ask Brain Vault`: sends `POST /access/request-secret`.

### Decision Card

The backend returns:

- `allow`: full value can be disclosed.
- `redact`: only metadata or existence-level output can be shown.
- `deny`: no useful disclosure.

The card displays the decision, visible result, score, required score, and reasons. The graph above the forms changes color based on `allow`, `redact`, or `deny`.

## Native Mac GUI

Run:

```bash
scripts/run_mac_gui.sh
```

The native GUI is useful for storage setup because it can instantiate storage adapters directly.

### Storage Target

- `Local Mac folder`: writes vault records under the selected folder, defaulting to `~/ReliQuary Vaults`.
- `Choose Folder`: picks a folder or mounted external drive.
- `Postgres`: uses `DATABASE_URL`, for example `postgresql://reliquary:reliquary@localhost:5432/reliquary`.
- `S3-compatible bucket`: uses bucket, region, prefix, and optional endpoint URL.
- `Initialize Storage`: creates the selected storage adapter and binds the GUI to it.

### Vault

- `Name`: vault name.
- `Owner`: vault owner id.
- `Description`: vault description.
- `Current vault ID`: created vault id or an existing id pasted by the user.
- `Create Vault`: creates a vault in the initialized storage target.
- `List Vaults`: prints known vaults to the result log.

### Secret

- `Secret name`: name/key for the secret.
- `Secret value`: text value.
- `Store Secret`: stores the value in the current vault.
- `Retrieve Secret`: retrieves the value directly through the storage manager.

The Tk GUI currently stores text secrets. File/folder secret storage and share links are available in the API and Vulkan ImGui console.

### Trust Gate

- `Requesting user`, `Trust score`, `Sensitivity`, `Remote address`, `Device`, `Local`, and `Biometric` map directly to the access decision engine.
- `Evaluate Trust Gate`: runs the access decision locally and writes an audit event to the access event log.
- Badge colors: green is allow, amber is redact, red is deny.

## Vulkan ImGui Console

Run:

```bash
scripts/run_brain_vault.sh
```

This is where Vulkan is used. The program in `visualizer/vulkan/src/main.cpp` creates a GLFW window, Vulkan instance/device/swapchain/render pass/framebuffers, and a Dear ImGui interface rendered through `ImGui_ImplVulkan_RenderDrawData`. On macOS it uses Vulkan through MoltenVK.

Vulkan is not the crypto engine and not the policy engine. It is the native visual computing layer for the Brain Vault: graph nodes, trust-gate colors, event playback, and a control console rendered by the GPU while the backend performs storage and access decisions.

### Left Panel: Storage, Vault, Secret

- `API URL`: local API base URL.
- `Owner`: owner id for new vaults.
- `Vault name`: name for `POST /vaults/`.
- `Create Vault`: creates a vault through the API and fills `Vault ID`.
- `Vault ID`: active vault id.
- `Secret name`: active secret name.
- `Secret value`: text payload.
- `Secret password`: per-secret access password. It is sent as `access_password`.
- `Store Text Secret`: stores a text secret with optional per-secret password.
- `File or folder path`: local file or directory path.
- `Store File/Folder Secret`: sends `POST /vaults/secrets/file`; files are base64 encoded and folders are packed as `.tar.gz` before storage.
- `Share password`: optional password protecting a share token. Minimum length is 8 characters.
- `Create Share Link`: sends `POST /share/create` with a 60 minute TTL and max 3 views.
- `Share token`: returned token. The API opens it through `POST /share/{token}`.

## How Secret Sharing Works

Share links are token based and local to the running backend storage:

1. Store a secret with `POST /vaults/secrets`.
2. Create a share token with `POST /share/create`.
3. Send the token or share URL to the recipient through your own channel.
4. Recipient calls `POST /share/{token}` with the share password and, if the secret was protected, the secret access password.

The share link enforces:

- expiry through `ttl_minutes`,
- view count through `max_views`,
- optional `share_password`,
- optional per-secret `access_password`.

It is not a global hosted relay yet. Cross-device use requires both devices to reach the same deployed API/storage instance.

## Where Data Is Stored

- Local folder vaults: selected folder in the Mac GUI or `RELIQUARY_LOCAL_STORAGE_PATH`.
- API local default: `runtime/vaults` unless overridden by environment.
- Postgres: tables managed by the storage adapter at `DATABASE_URL`.
- S3-compatible storage: configured bucket and prefix.
- Access event audit: `logs/access_events.jsonl` or `RELIQUARY_ACCESS_EVENT_LOG`.
- Trust history: `runtime/trust_history.json`.
- Share links: `runtime/share_links.json`.
- Security report output: `reports/security/`.

Generated runtime data is intentionally ignored by git.

## How Trust Is Calculated

ReliQuary has two related layers:

1. `core/trust/scorer.py` calculates a trust score from context and history. Default weights are context verification `0.30`, historical behavior `0.25`, risk assessment `0.20`, consistency `0.15`, and recency `0.10`.
2. `apps/api/services/access_decision.py` applies the score to a resource sensitivity threshold and request context.

The access decision engine clamps trust to `0..100`, applies sensitivity thresholds, and reduces trust for:

- non-owner access to non-public resources,
- remote origin without trusted local session,
- missing device verification for sensitive/secret/sealed data,
- missing biometric or explicit high-trust confirmation for secret/sealed data.

Outputs are deliberately conservative:

- `allow` means full disclosure is allowed by the current policy inputs.
- `redact` means the requester can see limited metadata or existence-level output.
- `deny` means the response should not disclose the secret.

## Production Notes

- Use the API docs before exposing a deployment: `http://localhost:8000/docs`.
- Do not rely on the website alone. It is a client surface; the API and storage backend must be configured.
- Do not treat deterministic development proof envelopes as real zero-knowledge proofs unless Circom/SnarkJS artifacts are configured and verified.
- Do not store real passwords in a public demo deployment.
- For cloud storage, use dedicated credentials, bucket policies, object encryption, and audit logs.
