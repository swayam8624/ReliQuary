import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vaults.storage import ArweaveStorageBackend, IPFSStorageBackend, StorageError


def test_ipfs_backend_fails_loudly_until_configured():
    with pytest.raises(StorageError, match="IPFS storage is not configured"):
        IPFSStorageBackend("http://127.0.0.1:5001")


def test_arweave_backend_fails_loudly_until_configured():
    with pytest.raises(StorageError, match="Arweave storage is not configured"):
        ArweaveStorageBackend("wallet.json")
