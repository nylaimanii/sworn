#!/usr/bin/env bash
#
# unmount_ro.sh — safely unmount an evidence mountpoint created by mount_ro.sh.
#
# Usage: unmount_ro.sh <mountpoint>
#
set -euo pipefail

die() { echo "ERROR: $*" >&2; exit 1; }

[ "$#" -eq 1 ] || die "usage: $0 <mountpoint>"

MOUNTPOINT="$1"

[ -d "$MOUNTPOINT" ] || die "mountpoint not found: $MOUNTPOINT"

# Only act if it is actually a mount; mountpoint(1) is the safe check.
if command -v mountpoint >/dev/null 2>&1; then
  if ! mountpoint -q "$MOUNTPOINT"; then
    echo "Nothing mounted at: $MOUNTPOINT (no action taken)."
    exit 0
  fi
fi

echo "Unmounting: $MOUNTPOINT"
# Try a clean unmount first; fall back to lazy unmount if busy.
if ! umount "$MOUNTPOINT" 2>/dev/null; then
  echo "Busy — retrying with lazy unmount (-l)..."
  umount -l "$MOUNTPOINT"
fi

echo "Unmounted: $MOUNTPOINT"
