# ReliQuary

ReliQuary is a research prototype for context-bound cryptographic memory:
secret vaults, policy/context checks, multi-agent access decisions, Merkle audit
trails, zero-knowledge context verification hooks, and Rust-backed crypto
extensions.

The core idea is simple: sensitive data should not be released only because a
caller knows an ID. Access should depend on the vault owner, current context,
trust score, agent quorum decision, and an auditable trail of what happened.

## What This Project Is

ReliQuary is not a static website and not a payment SaaS shell. The website is
only a small companion surface. The real project is the backend and research
runtime:

- `apps/api/` exposes the runnable FastAPI research API.
- `vaults/` stores vault and secret records through a storage adapter.
- `core/crypto/` selects Python or Rust crypto backends.
- `rust_modules/` contains PyO3 extensions for AES-GCM, Kyber, Falcon, and
  Merkle primitives.
- `agents/` contains multi-agent decision and consensus work.
- `core/trust/` and `apps/api/services/` contain dynamic trust scoring and
  context-verification plumbing.
- `zk/` contains Circom-oriented context verification circuits and FastAPI
  routes.
- `auth/` contains OAuth/WebAuthn/DID/RBAC-oriented authentication work.

Some research modules are still prototypes, but they are kept because they are
part of the actual direction of the system. Generated artifacts, marketplace
packaging, stale deployment manifests, logs, local databases, benchmark images,
and proving outputs are intentionally removed from git.

## What Works Now

- FastAPI app at `apps.api.main:app`.
- Active API routers for auth, ZK, vaults, context, trust, agents, and audit.
- Local vault creation, listing, secret storage, and retrieval.
- Trust-gated access decisions that return `allow`, `redact`, or `deny` with
  required trust scores and audit events.
- Native Mac GUI for vault creation, local folder storage, Postgres storage, and
  S3-compatible bucket storage, including a visual trust gate.
- Browser Brain Vault console that shows whether requested knowledge is
  revealed, redacted, or denied.
- Vulkan/MoltenVK visualizer scaffold for the secured brain graph.
- AES-GCM and Merkle helpers.
- Rust/PyO3 build path for native crypto modules.
- Rust-backed Kyber/Falcon tests when the extensions are installed.
- Minimal website that explains and drives the local research API.
- Focused pytest coverage for crypto, vault behavior, and exposed research API
  surface.

## Quickstart

```bash
git clone https://github.com/SwayamSingal/ReliQuary.git
cd ReliQuary

scripts/bootstrap_mac.sh
```

For a verbose run that shows every stage, tool version, command, and log path:

```bash
scripts/doctor_verbose.sh
```

For a native GUI on macOS:

```bash
scripts/run_brain_vault.sh
```

Run the local in-process research flow without starting a server:

```bash
source .venv/bin/activate
python scripts/research_flow.py
```

Run the API directly:

```bash
source .venv/bin/activate
python -m uvicorn apps.api.main:app --reload
```

Open:

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Research surface: http://localhost:8000/

That prints a vault record, context verification result, trust evaluation, and
agent quorum decision. The default local context is intentionally incomplete,
so the strict security agent may drive a denied access decision.

## Storage and GUI

ReliQuary can persist vault and secret records in three practical ways:

- Local Mac folder or external drive through `RELIQUARY_STORAGE_BACKEND=local`.
- Local or hosted PostgreSQL through `RELIQUARY_STORAGE_BACKEND=postgres`.
- AWS S3 or S3-compatible object storage through `RELIQUARY_STORAGE_BACKEND=s3`.

The native GUI supports all three modes:

```bash
scripts/run_mac_gui.sh
```

More detail is in `docs/storage_and_gui.md`.

## Brain Vault Access Decisions

The vault APIs store encrypted records. The access APIs decide what can be
shown to a requester:

```bash
curl -s -X POST http://localhost:8000/access/request-secret \
  -H 'Content-Type: application/json' \
  -d '{
    "vault_id": "replace-with-vault-id",
    "resource_name": "database-password",
    "sensitivity": "secret",
    "trust_score": 95,
    "subject": {
      "user_id": "alice",
      "device_verified": true,
      "local_session": true,
      "biometric_verified": true,
      "remote_address": "127.0.0.1"
    }
  }'
```

The same request with a different user, remote address, unverified device, or
low trust score returns `redact` or `deny` instead of the secret value. Recent
decisions are exposed at `/access/events` and `/access/stream` for dashboards
and visualizers.

ReliQuary can also index user-selected local folders as permissioned memory:

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

Then query:

```bash
curl -s -X POST http://localhost:8000/memory/query \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "passport",
    "trust_score": 95,
    "subject": {
      "user_id": "alice",
      "device_verified": true,
      "local_session": true,
      "biometric_verified": true,
      "remote_address": "127.0.0.1"
    }
  }'
```

See `docs/brain_vault_visualizer.md`.

## Local Postgres Vault Storage

On macOS, the first-class container path uses Apple's `container` CLI, not
Docker Desktop. `scripts/run_demo.sh` starts Postgres, builds the ReliQuary API
image from `Containerfile`, starts the API, and runs a smoke test that creates a
vault, stores a secret, retrieves it, and verifies context.

```bash
scripts/run_demo.sh
```

Run only the database-backed vault flow against any existing local Postgres:

```bash
export RELIQUARY_STORAGE_BACKEND=postgres
export DATABASE_URL=postgresql://reliquary:reliquary-dev-password@localhost:5432/reliquary
python scripts/postgres_vault_flow.py
```

Run the API against Postgres:

```bash
RELIQUARY_STORAGE_BACKEND=postgres \
DATABASE_URL=postgresql://reliquary:reliquary-dev-password@localhost:5432/reliquary \
python -m uvicorn apps.api.main:app --reload
```

The Postgres backend creates:

- `reliquary_vaults`
- `reliquary_secrets`

Secret values are persisted as AES-GCM envelopes. Production runs must set a
32-byte base64 key in `RELIQUARY_SECRET_KEY_B64`; local development uses
`RELIQUARY_DEV_SECRET_KEY` so the clone-run path remains usable.

## S3-Compatible Bucket Storage

Use this mode for AWS S3, MinIO, Cloudflare R2, or another compatible provider:

```bash
export RELIQUARY_STORAGE_BACKEND=s3
export RELIQUARY_S3_BUCKET=your-bucket
export RELIQUARY_S3_REGION=us-east-1
export RELIQUARY_S3_PREFIX=reliquary
# Optional for non-AWS providers:
export RELIQUARY_S3_ENDPOINT_URL=https://your-s3-compatible-endpoint
python -m uvicorn apps.api.main:app --reload
```

Credentials are resolved by the normal boto3 chain: AWS SSO, shared credentials,
environment variables, IAM role, or the compatible provider's equivalent. Never
commit bucket credentials.

Create a vault:

```bash
curl -s -X POST http://localhost:8000/vaults/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"research-vault","description":"local ReliQuary research vault","owner_id":"alice"}'
```

Evaluate context:

```bash
curl -s -X POST http://localhost:8000/context/verify \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "alice",
    "ip_address": "127.0.0.1",
    "user_agent": "reliquary-research-client/1.0",
    "timestamp": "2026-06-14T00:00:00Z",
    "device_fingerprint": "local-device"
  }'
```

Evaluate trust:

```bash
curl -s -X POST http://localhost:8000/trust/evaluate \
  -H 'Content-Type: application/json' \
  -d '{
    "request_id": "trust-local-1",
    "user_id": "alice",
    "context_data": {"verified": true, "confidence_score": 0.92}
  }'
```

## Rust Crypto Modules

Rust is the right choice for ReliQuary's crypto boundary. Python is useful for
orchestration, API work, and research iteration; Rust is better for native
cryptographic primitives, memory-sensitive code, and packaging small extension
modules. Rewriting the whole project in C++ would increase build complexity
without improving the current product path.

Build and install the PyO3 modules into the active Python environment:

```bash
source .venv/bin/activate
scripts/build_rust_modules.sh
```

That installs:

- `reliquary_encryptor`
- `reliquary_merkle`

Without these modules, AES-GCM and Merkle flows have Python fallbacks, but
Kyber/Falcon operations do not fake post-quantum behavior.

## Vulkan Brain Visualizer

On macOS, Vulkan runs through MoltenVK. Install the Vulkan SDK, then:

```bash
scripts/build_vulkan_visualizer.sh
visualizer/vulkan/build/reliquary_vulkan_visualizer
```

The current visualizer is a real Vulkan swapchain with Dear ImGui controls for
API configuration, vaults, text secrets, file/folder secrets, specific secret
passwords, share links, a trust-gate graph, and a chat-style command panel.

Run the full local console:

```bash
scripts/run_brain_vault.sh
```

## Website

The website is a control console for a local API, not a billing or marketing
shell. The root `vercel.json` builds `website/` directly so a Vercel production
deployment does not 404 when the project root is selected.

```bash
npm --prefix website install
npm --prefix website run dev
```

Open http://localhost:3000.

## Tests

```bash
pytest -q tests/test_crypto.py tests/api/test_vault_access.py tests/api/test_research_surface.py tests/test_vault_storage_persistence.py
```

Optional integration paths:

- Node SSS tests require `node_sss_service` to be running.
- Circom proof regeneration requires external Circom/SnarkJS tooling.
- Apple container smoke requires `container` CLI on macOS.

## Brutal Security / Trust Scorecard

Generate the current security and trust report:

```bash
python scripts/security_metrics.py
```

Outputs:

- `reports/security/REPORT.md`
- `reports/security/metrics.json`
- `reports/security/overall.svg`
- `reports/security/scorecard.svg`

The report is intentionally harsh. It penalizes mocked code paths, insecure
defaults, dev credentials, simulation modes, and placeholder storage/security
claims.

## Circom / ZK

The repo keeps ReliQuary circuits and ZK API hooks. It does not vendor the
Circom compiler as a broken submodule. Install Circom/SnarkJS externally when
you need to regenerate proving artifacts.

```bash
npm install -g snarkjs
```

Generated proving files such as `.zkey`, `.wtns`, `.ptau`, and proof JSON files
are runtime artifacts and should not be committed.
