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

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m uvicorn apps.api.main:app --reload
```

Open:

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Research surface: http://localhost:8000/

Run the in-process research flow without starting a server:

```bash
python scripts/research_flow.py
```

That prints a vault record, context verification result, trust evaluation, and
agent quorum decision. The default local context is intentionally incomplete,
so the strict security agent may drive a denied access decision.

## Local Postgres Vault Storage

ReliQuary can now persist vault records in a local PostgreSQL database. The
other storage backends remain research artifacts until they receive real
implementations.

Start Postgres:

```bash
docker compose -f docker/docker-compose.yml up -d postgres
```

Run the database-backed vault flow:

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

## Website

The website is intentionally minimal and has no pricing, Stripe, billing,
authentication shell, testimonials, or random marketing routes.

```bash
cd website
npm install
npm run dev
```

Open http://localhost:3000.

## Tests

```bash
pytest -q tests/test_crypto.py tests/api/test_vault_access.py tests/api/test_research_surface.py tests/test_vault_storage_persistence.py
```

Optional integration paths:

- Node SSS tests require `node_sss_service` to be running.
- Circom proof regeneration requires external Circom/SnarkJS tooling.
- Docker smoke requires a running Docker daemon.

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
