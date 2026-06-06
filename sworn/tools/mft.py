"""extract_mft_timeline — typed, read-only stub. reads an NTFS $MFT image and
returns (records, Receipt). no write counterpart exists."""
from __future__ import annotations
from dataclasses import dataclass
from ..receipt import Receipt

@dataclass
class MFTEntry:
    filename: str
    inode: int
    mtime: str
    atime: str
    ctime: str
    byte_offset: int | None = None

def _parse(raw: bytes) -> list[MFTEntry]:
    return []

def extract_mft_timeline(image_path: str) -> tuple[list[MFTEntry], Receipt]:
    raw = b""  # TODO(build): wire real tool
    records = _parse(raw)
    return records, Receipt.for_run(tool_name="extract_mft_timeline",
                                    args={"image_path": image_path},
                                    file_path=image_path, raw_output=raw)
