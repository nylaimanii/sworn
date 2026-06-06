"""append-only, hash-chained record of every tool execution. each line hashes the
previous line, so tampering breaks the chain and verify() catches it. opened in
append mode only; no rewrite path is exposed."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
from .receipt import Receipt

GENESIS_PREV = "0" * 64

def _hash_entry(prev_hash: str, payload: dict[str, Any]) -> str:
    basis = prev_hash + json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(basis.encode()).hexdigest()

class Ledger:
    def __init__(self, path: str | Path = "ledger.jsonl") -> None:
        self.path = Path(path)
        self.path.touch(exist_ok=True)

    def _last_hash(self) -> str:
        last = GENESIS_PREV
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    last = json.loads(line)["entry_hash"]
        return last

    def append(self, receipt: Receipt) -> str:
        prev = self._last_hash()
        payload = {"prev_hash": prev, "receipt": receipt.to_dict(), "receipt_id": receipt.receipt_id}
        entry_hash = _hash_entry(prev, payload)
        payload["entry_hash"] = entry_hash
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
        return entry_hash

    def verify(self) -> tuple[bool, int | None]:
        prev = GENESIS_PREV
        with self.path.open("r", encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                payload = {k: entry[k] for k in ("prev_hash", "receipt", "receipt_id")}
                if entry["prev_hash"] != prev:
                    return False, i
                if _hash_entry(prev, payload) != entry["entry_hash"]:
                    return False, i
                prev = entry["entry_hash"]
        return True, None

    def has_receipt(self, receipt_id: str) -> bool:
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and json.loads(line).get("receipt_id") == receipt_id:
                    return True
        return False
