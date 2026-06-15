import json
import os
from typing import List, Optional

from vaults.storage.base import StorageInterface


class PostgresStorage(StorageInterface):
    """PostgreSQL storage backend for ReliQuary vault and secret records."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL is required for PostgresStorage")

        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError(
                "PostgresStorage requires psycopg. Install requirements.txt first."
            ) from exc

        self._psycopg = psycopg
        self._ensure_schema()

    def _connect(self):
        return self._psycopg.connect(self.database_url)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reliquary_vaults (
                        vault_id TEXT PRIMARY KEY,
                        owner_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'active',
                        payload JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_reliquary_vaults_owner_id
                    ON reliquary_vaults(owner_id)
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reliquary_secrets (
                        secret_id TEXT PRIMARY KEY,
                        vault_id TEXT NOT NULL REFERENCES reliquary_vaults(vault_id)
                            ON DELETE CASCADE,
                        secret_name TEXT NOT NULL,
                        payload JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        UNIQUE(vault_id, secret_name)
                    )
                    """
                )

    def save_vault(self, vault_id: str, data: bytes):
        payload = json.loads(data.decode("utf-8"))
        owner_id = payload.get("owner_id") or payload.get("metadata", {}).get("owner_did") or ""
        name = payload.get("name") or f"vault_{vault_id[:8]}"
        status = payload.get("status") or "active"

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO reliquary_vaults (vault_id, owner_id, name, status, payload)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (vault_id) DO UPDATE SET
                        owner_id = EXCLUDED.owner_id,
                        name = EXCLUDED.name,
                        status = EXCLUDED.status,
                        payload = EXCLUDED.payload,
                        updated_at = NOW()
                    """,
                    (vault_id, owner_id, name, status, json.dumps(payload)),
                )

    def load_vault(self, vault_id: str) -> bytes:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT payload FROM reliquary_vaults WHERE vault_id = %s",
                    (vault_id,),
                )
                row = cur.fetchone()
                if row is None:
                    raise FileNotFoundError(f"Vault with ID '{vault_id}' not found.")
                return json.dumps(row[0], default=str).encode("utf-8")

    def list_vaults(self, owner_id: Optional[str] = None) -> List[bytes]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                if owner_id:
                    cur.execute(
                        """
                        SELECT payload FROM reliquary_vaults
                        WHERE owner_id = %s
                        ORDER BY created_at, vault_id
                        """,
                        (owner_id,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT payload FROM reliquary_vaults
                        ORDER BY created_at, vault_id
                        """
                    )
                return [json.dumps(row[0], default=str).encode("utf-8") for row in cur.fetchall()]

    def delete_vault(self, vault_id: str):
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM reliquary_vaults WHERE vault_id = %s", (vault_id,))

    def save_secret(self, secret_id: str, data: bytes):
        payload = json.loads(data.decode("utf-8"))
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO reliquary_secrets (secret_id, vault_id, secret_name, payload)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (vault_id, secret_name) DO UPDATE SET
                        secret_id = EXCLUDED.secret_id,
                        payload = EXCLUDED.payload,
                        updated_at = NOW()
                    """,
                    (
                        secret_id,
                        payload["vault_id"],
                        payload["secret_name"],
                        json.dumps(payload),
                    ),
                )

    def load_secret(self, vault_id: str, secret_name: str) -> bytes:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT payload FROM reliquary_secrets
                    WHERE vault_id = %s AND secret_name = %s
                    """,
                    (vault_id, secret_name),
                )
                row = cur.fetchone()
                if row is None:
                    raise FileNotFoundError(
                        f"Secret '{secret_name}' in vault '{vault_id}' not found."
                    )
                return json.dumps(row[0], default=str).encode("utf-8")

    def list_secrets(self, vault_id: Optional[str] = None) -> List[bytes]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                if vault_id:
                    cur.execute(
                        """
                        SELECT payload FROM reliquary_secrets
                        WHERE vault_id = %s
                        ORDER BY created_at, secret_id
                        """,
                        (vault_id,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT payload FROM reliquary_secrets
                        ORDER BY created_at, secret_id
                        """
                    )
                return [json.dumps(row[0], default=str).encode("utf-8") for row in cur.fetchall()]
