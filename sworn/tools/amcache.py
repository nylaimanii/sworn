"""get_amcache — typed, read-only stub. reads an Amcache.hve image and returns
(records, Receipt). no write counterpart exists."""
from __future__ import annotations
from dataclasses import dataclass
from ..receipt import Receipt

@dataclass
class ExecRecord:
    name: str
    path: str
    sha1: str | None = None
    first_run: str | None = None

def _parse(raw: bytes) -> list[ExecRecord]:
    return []

def get_amcache(image_path: str) -> tuple[list[ExecRecord], Receipt]:
    raw = b""  # TODO(build): wire real tool
    records = _parse(raw)
    return records, Receipt.for_run(tool_name="get_amcache",
                                    args={"image_path": image_path},
                                    file_path=image_path, raw_output=raw)
