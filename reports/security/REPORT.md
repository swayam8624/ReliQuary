# ReliQuary Security and Trust Report

Overall score: **69/100**

## Brutal Verdict

Promising but not production trustworthy.

This project is now more than a website: it has a real API surface, Rust crypto modules, a Postgres storage path, and runnable research flows. It is still not something I would trust with production secrets without hardening the mocked/prototype areas listed below.

## Metrics

### Runnable verification: 92/100
- Evidence: Focused pytest matrix passes
- Brutal note: This is the strongest part only after the current cleanup; full-suite health is still unknown.

### Rust crypto boundary: 82/100
- Evidence: Rust PyO3 modules imported and PQC tests ran
- Brutal note: Good direction. Needs audited algorithms, test vectors, and release builds in CI.

### Persistent storage: 72/100
- Evidence: Postgres backend, schema creation, and restart-style storage test exist
- Brutal note: Real Postgres exists now. Secret payloads use AES-GCM envelopes, but key management is still local/dev oriented.

### API research surface: 78/100
- Evidence: Auth, ZK, vault, context, trust, agents, and audit routers are exposed
- Brutal note: Breadth is good. Depth varies heavily across routers.

### Artifact hygiene: 95/100
- Evidence: 0 generated artifacts found outside ignored build dirs
- Brutal note: Much better after cleanup. Keep generated proof/log/database files out of git forever.

### Prototype debt: 23/100
- Evidence: 77 mock/TODO/placeholder/prototype markers found
- Brutal note: This is the ugly truth: the repo still contains lots of research scaffolding and simulated paths.

### Secure defaults: 25/100
- Evidence: 55 insecure-default markers found
- Brutal note: CORS wildcards, simulation modes, dev passwords, and legacy compatibility paths are not production security.

### Implementation density: 97/100
- Evidence: 887/910 Python functions have non-pass bodies
- Brutal note: Quantity is not quality, but it shows this is not just a website.

## Generated Graphs

- `reports/security/overall.svg`
- `reports/security/scorecard.svg`
