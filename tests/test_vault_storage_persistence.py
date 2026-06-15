import json

from vaults.manager import VaultManager


class QueryableMemoryStorage:
    def __init__(self):
        self.vaults = {}
        self.secrets = {}

    def save_vault(self, vault_id: str, data: bytes):
        self.vaults[vault_id] = data

    def load_vault(self, vault_id: str) -> bytes:
        if vault_id not in self.vaults:
            raise FileNotFoundError(vault_id)
        return self.vaults[vault_id]

    def list_vaults(self, owner_id=None):
        records = []
        for data in self.vaults.values():
            payload = json.loads(data)
            if owner_id is None or payload["owner_id"] == owner_id:
                records.append(data)
        return records

    def delete_vault(self, vault_id: str):
        self.vaults.pop(vault_id, None)

    def save_secret(self, secret_id: str, data: bytes):
        payload = json.loads(data)
        self.secrets[(payload["vault_id"], payload["secret_name"])] = data

    def load_secret(self, vault_id: str, secret_name: str) -> bytes:
        key = (vault_id, secret_name)
        if key not in self.secrets:
            raise FileNotFoundError(secret_name)
        return self.secrets[key]


def test_queryable_storage_survives_manager_restart():
    storage = QueryableMemoryStorage()
    manager = VaultManager(storage)

    vault = manager.create_vault(
        name="persistent-vault",
        description="stored through queryable backend",
        owner_id="alice",
    )
    manager.store_secret(vault.vault_id, "api-token", "sk-real-secret")

    fresh_manager = VaultManager(storage)
    loaded_vault = fresh_manager.get_vault(vault.vault_id)
    loaded_secret = fresh_manager.retrieve_secret(vault.vault_id, "api-token")
    listed_vaults = fresh_manager.list_vaults(owner_id="alice")

    assert loaded_vault.vault_id == vault.vault_id
    assert loaded_secret.secret_value == "sk-real-secret"
    assert [item.vault_id for item in listed_vaults] == [vault.vault_id]
