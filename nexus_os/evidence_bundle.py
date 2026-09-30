from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(slots=True)
class EvidenceItem:
    kind: str
    source: str
    content: str
    sha256: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class EvidenceBundle:
    bundle_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    mission: str = ""
    created_at: float = field(default_factory=time.time)
    items: list[EvidenceItem] = field(default_factory=list)

    def add_text(
        self,
        kind: str,
        source: str,
        content: str,
        *,
        metadata: dict[str, str] | None = None,
    ) -> EvidenceItem:
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        item = EvidenceItem(
            kind=kind,
            source=source,
            content=content,
            sha256=digest,
            metadata=metadata or {},
        )
        self.items.append(item)
        return item

    def verify(self) -> bool:
        return all(
            hashlib.sha256(item.content.encode("utf-8")).hexdigest() == item.sha256
            for item in self.items
        )

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def read(cls, path: Path) -> EvidenceBundle:
        payload = json.loads(path.read_text(encoding="utf-8"))
        bundle = cls(
            bundle_id=payload["bundle_id"],
            mission=payload.get("mission", ""),
            created_at=float(payload["created_at"]),
        )
        bundle.items = [EvidenceItem(**item) for item in payload.get("items", [])]
        return bundle
