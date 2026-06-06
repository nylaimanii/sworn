"""list_memory_processes — typed, read-only stub. reads a memory image and returns
(records, Receipt). no write counterpart exists."""
from __future__ import annotations
from dataclasses import dataclass
from ..receipt import Receipt

@dataclass
class Process:
    pid: int
    ppid: int
    name: str
    create_time: str | None = None

def _parse(raw: bytes) -> list[Process]:
    return []

def list_memory_processes(mem_path: str) -> tuple[list[Process], Receipt]:
    raw = b""  # TODO(build): wire real tool
    records = _parse(raw)
    return records, Receipt.for_run(tool_name="list_memory_processes",
                                    args={"mem_path": mem_path},
                                    file_path=mem_path, raw_output=raw)
