"""mount integrity helper for guarantee 1 (cannot spoliate).

`is_readonly(mountpoint)` confirms a mountpoint is actually mounted read-only by
parsing /proc/mounts on Linux. This is a software-side cross-check; the real
guardrail is the kernel ro,loop mount enforced by scripts/mount_ro.sh.
"""
from __future__ import annotations
import sys
from pathlib import Path


def is_readonly(mountpoint: str) -> bool:
    """Return True iff `mountpoint` is currently mounted read-only.

    Linux: parses /proc/mounts and checks the mount options contain 'ro'.
    Non-Linux: returns False (this is a Linux-only mechanism) and emits a clear
    'linux-only' note to stderr rather than crashing.
    """
    if not sys.platform.startswith("linux"):
        print(
            "is_readonly: linux-only check (ro loop-mount is a Linux mechanism); "
            f"returning False on platform '{sys.platform}'.",
            file=sys.stderr,
        )
        return False

    target = str(Path(mountpoint).resolve())
    try:
        with open("/proc/mounts", "r", encoding="utf-8") as fh:
            entries = fh.read().splitlines()
    except OSError as exc:
        print(f"is_readonly: cannot read /proc/mounts: {exc}", file=sys.stderr)
        return False

    for line in entries:
        parts = line.split()
        if len(parts) < 4:
            continue
        # fields: device mountpoint fstype options ...
        mp = parts[1]
        opts = parts[3].split(",")
        if mp == target or mp == mountpoint:
            return "ro" in opts
    return False
