# Test: read-only mount, write-fails verification

This documents the reproducible check behind **guarantee 1 (cannot spoliate)**.
The mount is read-only because a write inside it *fails* — that failure is the proof.

> Environment: this runs inside the **SIFT VM (Linux)**. The loop mount is a Linux
> kernel mechanism and cannot be exercised on Windows.

## Steps (judge-reproducible)

1. Create a tiny throwaway raw image with a filesystem (no real evidence needed):

   ```bash
   dd if=/dev/zero of=/tmp/test.dd bs=1M count=8
   mkfs.ext4 -q /tmp/test.dd
   ```

2. Mount it read-only with the script:

   ```bash
   sudo scripts/mount_ro.sh /tmp/test.dd /mnt/sworn_test
   ```

   **Expected:** the script prints `RO VERIFIED`. It reaches that line only
   because its internal probe `touch "$MOUNTPOINT/.sworn_ro_probe_$$"` returned
   non-zero (the write was rejected by the kernel).

3. Confirm independently that a write fails:

   ```bash
   touch /mnt/sworn_test/should_fail        # expect: "Read-only file system"
   ```

   ```bash
   python -c "from sworn.mount import is_readonly; print(is_readonly('/mnt/sworn_test'))"
   # expect: True   (parses /proc/mounts and finds the 'ro' option)
   ```

4. Unmount:

   ```bash
   sudo scripts/unmount_ro.sh /mnt/sworn_test
   ```

## Pass criteria

- `mount_ro.sh` prints `RO VERIFIED` (probe write failed).
- A manual `touch` inside the mountpoint fails with `Read-only file system`.
- `is_readonly()` returns `True` on Linux for the mounted path.
- The source image (`/tmp/test.dd`) is never written to by any code path.

## Note on E01/EWF images

`mount_ro.sh` rejects `*.e01` inputs and instructs the user to expose the raw
device first with `ewfmount`, then mount that raw device read-only. EWF
containers are not raw block devices and cannot be loop-mounted directly.
