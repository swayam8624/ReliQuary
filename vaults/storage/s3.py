"""S3-compatible storage backend for ReliQuary vault and secret records."""

from __future__ import annotations

import json
from typing import List, Optional

from vaults.storage.base import StorageInterface

class S3Storage(StorageInterface):
    """Storage backend for AWS S3 or S3-compatible buckets.

    Credentials are resolved by boto3 from the normal AWS chain:
    environment variables, shared config files, IAM role, or SSO.
    """

    def __init__(
        self,
        bucket_name: str,
        region_name: str,
        prefix: str = "reliquary",
        endpoint_url: Optional[str] = None,
    ):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.prefix = prefix.strip("/")
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError(
                "S3Storage requires boto3. Install requirements.txt or add boto3 to your environment."
            ) from exc
        from botocore.exceptions import ClientError

        self._client_error = ClientError
        self.client = boto3.client("s3", region_name=region_name, endpoint_url=endpoint_url)

    def _key(self, *parts: str) -> str:
        clean_parts = [part.strip("/") for part in parts if part]
        return "/".join([self.prefix, *clean_parts])

    def _vault_key(self, vault_id: str) -> str:
        return self._key("vaults", f"{vault_id}.json")

    def _secret_key(self, vault_id: str, secret_name: str) -> str:
        safe_secret = secret_name.replace("/", "%2F")
        return self._key("secrets", vault_id, f"{safe_secret}.json")

    def save_vault(self, vault_id: str, data: bytes):
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=self._vault_key(vault_id),
            Body=data,
            ContentType="application/json",
            ServerSideEncryption="AES256",
        )

    def load_vault(self, vault_id: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=self._vault_key(vault_id))
        except self._client_error as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404", "NotFound"}:
                raise FileNotFoundError(f"Vault with ID '{vault_id}' not found in S3.") from exc
            raise
        return response["Body"].read()

    def delete_vault(self, vault_id: str):
        self.client.delete_object(Bucket=self.bucket_name, Key=self._vault_key(vault_id))
        prefix = self._key("secrets", vault_id) + "/"
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            objects = [{"Key": item["Key"]} for item in page.get("Contents", [])]
            if objects:
                self.client.delete_objects(Bucket=self.bucket_name, Delete={"Objects": objects})

    def list_vaults(self, owner_id: Optional[str] = None) -> List[bytes]:
        records = []
        prefix = self._key("vaults") + "/"
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            for item in page.get("Contents", []):
                body = self.client.get_object(Bucket=self.bucket_name, Key=item["Key"])["Body"].read()
                if owner_id:
                    payload = json.loads(body.decode("utf-8"))
                    payload_owner = payload.get("owner_id") or payload.get("metadata", {}).get("owner_did")
                    if payload_owner != owner_id:
                        continue
                records.append(body)
        return records

    def save_secret(self, secret_id: str, data: bytes):
        payload = json.loads(data.decode("utf-8"))
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=self._secret_key(payload["vault_id"], payload["secret_name"]),
            Body=data,
            ContentType="application/json",
            ServerSideEncryption="AES256",
        )

    def load_secret(self, vault_id: str, secret_name: str) -> bytes:
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=self._secret_key(vault_id, secret_name),
            )
        except self._client_error as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404", "NotFound"}:
                raise FileNotFoundError(f"Secret '{secret_name}' in vault '{vault_id}' not found in S3.") from exc
            raise
        return response["Body"].read()

    def list_secrets(self, vault_id: Optional[str] = None) -> List[bytes]:
        records = []
        prefix = self._key("secrets", vault_id or "") + "/"
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            for item in page.get("Contents", []):
                records.append(
                    self.client.get_object(Bucket=self.bucket_name, Key=item["Key"])["Body"].read()
                )
        return records


S3StorageBackend = S3Storage
