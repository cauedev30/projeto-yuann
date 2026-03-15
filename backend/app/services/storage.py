from __future__ import annotations

from pathlib import Path
from uuid import uuid4


class LocalStorageService:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def store_bytes(self, filename: str, content: bytes) -> str:
        storage_key = f"{uuid4()}-{filename}"
        target = self.root / storage_key
        target.write_bytes(content)
        return storage_key

    def read_bytes(self, storage_key: str) -> bytes:
        return (self.root / storage_key).read_bytes()
