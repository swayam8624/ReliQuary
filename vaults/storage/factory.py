"""Storage backend selection for ReliQuary.

The backend is controlled by RELIQUARY_STORAGE_BACKEND:
- local or mac-folder: local filesystem path
- postgres: PostgreSQL DATABASE_URL
- s3: S3-compatible object storage
"""

from __future__ import annotations

import os
from pathlib import Path

from vaults.storage.base import StorageInterface
from vaults.storage.local import LocalStorage
from vaults.storage.postgres import PostgresStorage
from vaults.storage.s3 import S3Storage


def default_local_vault_path() -> str:
    return str(Path.home() / "ReliQuary Vaults")


def build_storage_from_env() -> StorageInterface:
    backend = os.environ.get("RELIQUARY_STORAGE_BACKEND", "local").lower().strip()

    if backend in {"local", "mac", "mac-folder", "folder", "harddrive", "hard-drive"}:
        path = os.environ.get("RELIQUARY_LOCAL_VAULT_PATH", default_local_vault_path())
        return LocalStorage(os.path.expanduser(path))

    if backend == "postgres":
        return PostgresStorage()

    if backend in {"s3", "aws-s3", "s3-compatible"}:
        bucket = os.environ.get("RELIQUARY_S3_BUCKET")
        if not bucket:
            raise ValueError("RELIQUARY_S3_BUCKET is required when RELIQUARY_STORAGE_BACKEND=s3")
        return S3Storage(
            bucket_name=bucket,
            region_name=os.environ.get("RELIQUARY_S3_REGION", "us-east-1"),
            prefix=os.environ.get("RELIQUARY_S3_PREFIX", "reliquary"),
            endpoint_url=os.environ.get("RELIQUARY_S3_ENDPOINT_URL"),
        )

    raise ValueError(
        "Unsupported RELIQUARY_STORAGE_BACKEND. Use local, mac-folder, postgres, or s3."
    )
