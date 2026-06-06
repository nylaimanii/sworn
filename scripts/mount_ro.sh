#!/usr/bin/env bash
#
# mount_ro.sh — guarantee 1 (cannot spoliate).
#
# Mounts a forensic disk image READ-ONLY at the OS layer so the agent is
# physically incapable of altering evidence. Read-only is not asserted by a
# prompt; it is enforced by the kernel and then PROVEN by attempting a write
# inside the mountpoint and confirming the write FAILS.
#
# This script NEVER writes to the source image. The only write it attempts is a
# probe file INSIDE the mountpoint, which must fail on a correct ro mount.
#
# Usage: mount_ro.sh <image_path> <mountpoint>
#   <image_path>  raw/dd image (e.g. evidence.dd, disk.raw, image.img)
#   <mountpoint>  directory to mount under (created if missing)
#
set -euo pipefail

die() { echo "ERROR: $*" >&2; exit 1; }

[ "$#" -eq 2 ] || die "usage: $0 <image_path> <mountpoint>"

IMAGE="$1"
MOUNTPOINT="$2"

[ -f "$IMAGE" ] || die "image not found: $IMAGE"

# E01/EWF images are containers, not raw block devices. They must be exposed as
# a raw device first (ewfmount/xmount), then THAT raw device is passed here.
case "$IMAGE" in
  *.e01|*.E01|*.Ex01|*.EX01)
    echo "ERROR: '$IMAGE' is an EWF/E01 container, not a raw image." >&2
    echo "       Expose it as a raw device first, then mount that raw file:" >&2
    echo "         mkdir -p /mnt/ewf" >&2
    echo "         ewfmount \"$IMAGE\" /mnt/ewf       # creates /mnt/ewf/ewf1 (raw)" >&2
    echo "         $0 /mnt/ewf/ewf1 \"$MOUNTPOINT\"" >&2
    exit 2
    ;;
esac

# Create the mountpoint (this is OUR directory, never the source image).
mkdir -p "$MOUNTPOINT"

# Mount strictly read-only.
#   ro     — read-only at the kernel level
#   loop   — treat the image file as a loop block device
#   noload — do not replay the ext3/ext4 journal (a journal replay is a WRITE);
#            harmless/ignored for non-journaled filesystems.
# NOTE: we never pass any flag that could write back to "$IMAGE".
echo "Mounting (ro,loop,noload): $IMAGE -> $MOUNTPOINT"
mount -o ro,loop,noload "$IMAGE" "$MOUNTPOINT"

# --- PROVE read-only: a write inside the mountpoint MUST fail. ---
PROBE="$MOUNTPOINT/.sworn_ro_probe_$$"
if touch "$PROBE" 2>/dev/null; then
  # Unexpected success: clean up the probe we created, unmount, and abort loudly.
  rm -f "$PROBE" 2>/dev/null || true
  umount "$MOUNTPOINT" 2>/dev/null || true
  die "WRITE SUCCEEDED on '$MOUNTPOINT' — mount is NOT read-only. ABORTING."
fi

echo "RO VERIFIED"
echo "Evidence mounted read-only at: $MOUNTPOINT"
echo "Unmount with: scripts/unmount_ro.sh \"$MOUNTPOINT\""
