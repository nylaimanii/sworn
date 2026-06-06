"""the receipt: the unit of truth in sworn. every typed tool returns (records, receipt).
no finding may be marked 'confirmed' without a matching receipt in the ledger."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Receipt:
    tool_name: str
    args: dict[str, Any]
    file_path: str
    raw_output_sha256: str
    timestamp_utc: str = field(default_factory=_now_utc)
    byte_offset: int | None = None

    @classmethod
    def for_run(cls, *, tool_name: str, args: dict[str, Any], file_path: str,
                raw_output: bytes, byte_offset: int | None = None) -> "Receipt":
        return cls(tool_name=tool_name, args=args, file_path=file_path,
                   raw_output_sha256=_sha256(raw_output), byte_offset=byte_offset)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def receipt_id(self) -> str:
        basis = f"{self.tool_name}|{self.file_path}|{self.raw_output_sha256}|{self.byte_offset}"
        return _sha256(basis.encode())[:16]
