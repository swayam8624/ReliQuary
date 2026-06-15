#!/usr/bin/env python
"""Exercise ReliQuary vaults against a real PostgreSQL database.

Set DATABASE_URL to an existing Postgres database, or run:

    docker compose -f docker/docker-compose.yml up -d postgres

Then:

    RELIQUARY_STORAGE_BACKEND=postgres \
    DATABASE_URL=postgresql://reliquary:reliquary-dev-password@localhost:5432/reliquary \
    python scripts/postgres_vault_flow.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from vaults.manager import VaultManager
from vaults.storage.postgres import PostgresStorage


def print_step(title: str, payload: dict | list) -> None:
    print(f"\n== {title} ==")
    print(json.dumps(payload, indent=2, default=str))


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "DATABASE_URL is required. Example: "
            "postgresql://reliquary:reliquary-dev-password@localhost:5432/reliquary"
        )

    storage = PostgresStorage(database_url)
    manager = VaultManager(storage)

    vault = manager.create_vault(
        name="postgres-research-vault",
        description="Vault persisted in PostgreSQL",
        owner_id="alice",
    )
    print_step("created postgres vault", {
        "vault_id": vault.vault_id,
        "owner_id": vault.owner_id,
        "name": vault.name,
        "status": vault.status,
    })

    secret = manager.store_secret(
        vault_id=vault.vault_id,
        secret_name="api-token",
        secret_value="sk-postgres-backed-secret",
        metadata={"storage": "postgres"},
    )
    print_step("stored secret metadata", {
        "secret_id": secret.secret_id,
        "vault_id": secret.vault_id,
        "secret_name": secret.secret_name,
        "metadata": secret.metadata,
    })

    fresh_manager = VaultManager(PostgresStorage(database_url))
    loaded_vault = fresh_manager.get_vault(vault.vault_id)
    loaded_secret = fresh_manager.retrieve_secret(vault.vault_id, "api-token")
    listed_vaults = fresh_manager.list_vaults(owner_id="alice")

    print_step("loaded after fresh manager", {
        "vault_id": loaded_vault.vault_id,
        "secret_name": loaded_secret.secret_name,
        "secret_value": loaded_secret.secret_value,
        "alice_vault_count": len(listed_vaults),
    })


if __name__ == "__main__":
    main()
