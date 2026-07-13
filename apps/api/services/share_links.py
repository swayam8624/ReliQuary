"""Expiring share links for trust-gated secret handoff."""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ShareLink:
    token: str
    vault_id: str
    secret_name: str
    created_by: str
    expires_at: str
    max_views: int
    view_count: int = 0
    password_hash: Optional[str] = None


class ShareLinkStore:
    def __init__(self, path: str = "runtime/share_links.json"):
        self.path = Path(path)
        self.links: Dict[str, ShareLink] = {}
        self._load()

    def create(
        self,
        vault_id: str,
        secret_name: str,
        created_by: str,
        ttl_minutes: int = 60,
        max_views: int = 1,
        share_password: Optional[str] = None,
    ) -> ShareLink:
        token = secrets.token_urlsafe(32)
        link = ShareLink(
            token=token,
            vault_id=vault_id,
            secret_name=secret_name,
            created_by=created_by,
            expires_at=(datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).isoformat(),
            max_views=max(1, max_views),
            password_hash=self._hash_password(share_password) if share_password else None,
        )
        self.links[token] = link
        self._save()
        return link

    def consume(self, token: str, share_password: Optional[str] = None) -> ShareLink:
        link = self.links.get(token)
        if not link:
            raise ValueError("Share link not found")
        if datetime.now(timezone.utc) > datetime.fromisoformat(link.expires_at):
            raise ValueError("Share link expired")
        if link.view_count >= link.max_views:
            raise ValueError("Share link view limit reached")
        if link.password_hash and link.password_hash != self._hash_password(share_password):
            raise ValueError("Invalid share password")
        link.view_count += 1
        self._save()
        return link

    @staticmethod
    def _hash_password(password: Optional[str]) -> str:
        return hashlib.sha256((password or "").encode("utf-8")).hexdigest()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            self.links = {
                item["token"]: ShareLink(**item)
                for item in payload.get("links", [])
            }
        except (OSError, json.JSONDecodeError, TypeError):
            self.links = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"links": [asdict(link) for link in self.links.values()]}, indent=2, sort_keys=True),
            encoding="utf-8",
        )


share_link_store = ShareLinkStore()
