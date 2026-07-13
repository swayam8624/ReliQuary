"""Permissioned local file catalog for Brain Vault retrieval."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from apps.api.services.access_decision import AccessDecisionEngine, AccessResource, AccessSubject, Sensitivity


@dataclass
class CatalogEntry:
    entry_id: str
    vault_id: str
    owner_id: str
    name: str
    path: str
    resource_type: str
    sensitivity: Sensitivity
    size_bytes: int


class LocalFolderConnector:
    """Indexes filenames and paths from an explicitly selected local folder."""

    def scan(
        self,
        root_path: str,
        vault_id: str,
        owner_id: str,
        sensitivity: Sensitivity = "private",
        max_files: int = 500,
    ) -> List[CatalogEntry]:
        root = Path(root_path).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Local folder does not exist: {root}")

        entries: List[CatalogEntry] = []
        for path in self._walk(root):
            if len(entries) >= max_files:
                break
            try:
                stat = path.stat()
            except OSError:
                continue
            entries.append(
                CatalogEntry(
                    entry_id=f"file_{uuid.uuid4().hex[:16]}",
                    vault_id=vault_id,
                    owner_id=owner_id,
                    name=path.name,
                    path=str(path),
                    resource_type="file_path",
                    sensitivity=sensitivity,
                    size_bytes=stat.st_size,
                )
            )
        return entries

    @staticmethod
    def _walk(root: Path) -> Iterable[Path]:
        for current_root, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if not name.startswith(".")]
            for filename in sorted(filenames):
                if filename.startswith("."):
                    continue
                yield Path(current_root) / filename


class RetrievalCatalog:
    """Small JSON-backed catalog for local file metadata."""

    def __init__(self, path: str = "runtime/memory_catalog.json"):
        self.path = Path(path)
        self.entries: Dict[str, CatalogEntry] = {}
        self._load()

    def add_entries(self, entries: List[CatalogEntry]) -> None:
        for entry in entries:
            self.entries[entry.entry_id] = entry
        self._save()

    def search(self, query: str, limit: int = 20) -> List[CatalogEntry]:
        query_terms = [term.lower() for term in query.split() if term.strip()]
        if not query_terms:
            return []
        scored = []
        for entry in self.entries.values():
            haystack = f"{entry.name} {entry.path}".lower()
            score = sum(1 for term in query_terms if term in haystack)
            if score:
                scored.append((score, entry))
        scored.sort(key=lambda item: (-item[0], item[1].name))
        return [entry for _, entry in scored[:limit]]

    def query_with_policy(
        self,
        query: str,
        subject: AccessSubject,
        trust_score: int,
        limit: int = 10,
    ) -> List[dict]:
        engine = AccessDecisionEngine()
        results = []
        for entry in self.search(query, limit):
            decision = engine.evaluate(
                subject=subject,
                resource=AccessResource(
                    vault_id=entry.vault_id,
                    owner_id=entry.owner_id,
                    name=entry.name,
                    sensitivity=entry.sensitivity,
                    resource_type=entry.resource_type,
                    metadata={"path": entry.path, "size_bytes": entry.size_bytes},
                ),
                trust_score=trust_score,
                requested_detail="path",
            )
            result = {
                "entry_id": entry.entry_id,
                "name": entry.name,
                "resource_type": entry.resource_type,
                "sensitivity": entry.sensitivity,
                "decision": decision.decision,
                "visible_result": decision.visible_result,
                "reasons": decision.reasons,
                "trust_score": decision.trust_score,
                "required_score": decision.required_score,
            }
            if decision.decision == "allow":
                result["path"] = entry.path
                result["size_bytes"] = entry.size_bytes
            elif decision.decision == "redact":
                result["path"] = None
                result["size_bytes"] = entry.size_bytes
            results.append(result)
        return results

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            self.entries = {
                item["entry_id"]: CatalogEntry(**item)
                for item in payload.get("entries", [])
            }
        except (OSError, json.JSONDecodeError, TypeError):
            self.entries = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"entries": [asdict(entry) for entry in self.entries.values()]}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


retrieval_catalog = RetrievalCatalog()
