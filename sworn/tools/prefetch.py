"""analyze_prefetch — typed, read-only stub. reads a Windows Prefetch image and
returns (records, Receipt). no write counterpart exists."""
from __future__ import annotations
from dataclasses import dataclass
from ..receipt import Receipt

@dataclass
class PrefetchRecord:
    executable: str
    run_count: int
    last_run: str | None = None

def _parse(raw: bytes) -> list[PrefetchRecord]:
    return []

def analyze_prefetch(image_path: str) -> tuple[list[PrefetchRecord], Receipt]:
    raw = b""  # TODO(build): wire real tool
    records = _parse(raw)
    return records, Receipt.for_run(tool_name="analyze_prefetch",
                                    args={"image_path": image_path},
                                    file_path=image_path, raw_output=raw)
