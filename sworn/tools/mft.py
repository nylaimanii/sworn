"""extract_mft_timeline — typed read-only NTFS MFT timeline via The Sleuth Kit.

live-tested against ali hadi case1 (Case1-Webserver.E01, ntfs partition at sector 2048).
runs `fls -r -m C:/ -o <offset> <image>` read-only and parses the body timeline.
NO write counterpart exists. no generic shell passthrough is exposed to the model.
"""
from __future__ import annotations
import subprocess
import shutil
from dataclasses import dataclass
from ..receipt import Receipt


@dataclass
class MFTEntry:
    filename: str
    inode: str
    mtime: str
    atime: str
    ctime: str
    byte_offset: int | None = None


def _epoch_to_iso(v: str) -> str:
    from datetime import datetime, timezone
    try:
        n = int(v)
        return "" if n == 0 else datetime.fromtimestamp(n, timezone.utc).isoformat()
    except (ValueError, OverflowError, OSError):
        return ""


def _parse(raw: bytes) -> list[MFTEntry]:
    out: list[MFTEntry] = []
    for line in raw.decode("utf-8", "replace").splitlines():
        parts = line.split("|")
        if len(parts) < 11:
            continue
        # body format: MD5|name|inode|mode|UID|GID|size|atime|mtime|ctime|crtime
        out.append(MFTEntry(
            filename=parts[1], inode=parts[2],
            atime=_epoch_to_iso(parts[7]),
            mtime=_epoch_to_iso(parts[8]),
            ctime=_epoch_to_iso(parts[9]),
        ))
    return out


def extract_mft_timeline(image_path: str, offset: int = 2048) -> tuple[list[MFTEntry], Receipt]:
    """parse the NTFS MFT timeline from a disk image (read-only)."""
    if shutil.which("fls") is None:
        raise RuntimeError("the sleuth kit (fls) not found — run inside the SIFT VM / codespace")
    args = {"image_path": image_path, "offset": offset}
    raw = subprocess.run(
        ["fls", "-r", "-m", "C:/", "-o", str(offset), image_path],
        capture_output=True,
    ).stdout
    records = _parse(raw)
    receipt = Receipt.for_run(
        tool_name="extract_mft_timeline",
        args=args,
        file_path=image_path,
        raw_output=raw,
    )
    return records, receipt
