"""extract_mft_timeline — typed, read-only forensic tool backed by The Sleuth Kit.

Shells out to `fls` (read-only) to produce a TSK body-file timeline of an NTFS
image, parses the pipe-delimited body format into typed MFTEntry records, and
returns (records, Receipt). The raw fls output is hashed into the Receipt and
preserved verbatim under raw/<sha256>.txt.

There is intentionally NO write counterpart and NO generic shell tool. This
function only READS image_path; it never writes to it.
"""
from __future__ import annotations
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ..receipt import Receipt


@dataclass
class MFTEntry:
    filename: str
    inode: str  # TSK NTFS inodes are compound strings, e.g. "16-128-1"
    mtime: str
    atime: str
    ctime: str
    byte_offset: int | None = None


def _epoch_to_iso(field: str) -> str:
    """Convert a body-file epoch-seconds field to an ISO-8601 UTC string.

    Empty, '0', or non-numeric fields become "" (no claimed time) rather than a
    fabricated timestamp.
    """
    field = field.strip()
    if not field:
        return ""
    try:
        secs = int(field)
    except ValueError:
        return ""
    if secs == 0:
        return ""
    return datetime.fromtimestamp(secs, tz=timezone.utc).isoformat()


def _parse(raw: bytes) -> list[MFTEntry]:
    """Parse TSK body-file bytes into typed MFTEntry records.

    Body format (pipe-delimited):
        MD5|name|inode|mode|UID|GID|size|atime|mtime|ctime|crtime
    """
    records: list[MFTEntry] = []
    text = raw.decode("utf-8", "replace")
    for line in text.splitlines():
        line = line.rstrip("\n")
        if not line.strip():
            continue
        fields = line.split("|")
        if len(fields) < 11:
            # not a well-formed body line; skip rather than guess
            continue
        name = fields[1]
        inode = fields[2]
        atime = _epoch_to_iso(fields[7])
        mtime = _epoch_to_iso(fields[8])
        ctime = _epoch_to_iso(fields[9])
        records.append(
            MFTEntry(
                filename=name,
                inode=inode,
                mtime=mtime,
                atime=atime,
                ctime=ctime,
                byte_offset=None,  # body format does not expose a byte offset
            )
        )
    return records


def extract_mft_timeline(image_path: str) -> tuple[list[MFTEntry], Receipt]:
    """Run fls (read-only) on image_path and return typed records + a Receipt.

    Raises RuntimeError if The Sleuth Kit (fls) is not installed.
    """
    if shutil.which("fls") is None:
        raise RuntimeError(
            "the sleuth kit (fls) not found — run inside the SIFT VM"
        )

    # Read-only: fls only reads the image. We never pass a write-capable flag and
    # never open image_path for writing anywhere in this module.
    proc = subprocess.run(
        ["fls", "-r", "-m", "C:/", image_path],
        capture_output=True,
        check=False,
    )
    raw = proc.stdout

    records = _parse(raw)

    receipt = Receipt.for_run(
        tool_name="extract_mft_timeline",
        args={"image_path": image_path},
        file_path=image_path,
        raw_output=raw,
    )

    # Preserve the raw evidence output verbatim, keyed by its hash. This writes
    # to OUR raw/ directory, never to image_path.
    raw_dir = Path("raw")
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / f"{receipt.raw_output_sha256}.txt").write_bytes(raw)

    return records, receipt
