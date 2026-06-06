# sworn

An incident response agent architecturally incapable of lying.

`sworn` is a read-only forensic MCP server. Every typed tool **reads** evidence
(MFT, Amcache, Prefetch, memory) and returns `(records, Receipt)`. Receipts are
written to an append-only, hash-chained ledger, so no finding can be marked
*confirmed* without a verifiable receipt — and any tampering breaks the chain.

## Guarantees

1. **Cannot spoliate** — there is no write/shell tool anywhere; only readers exist.
2. **Cannot fabricate** — findings require a matching receipt in the hash-chained ledger.
3. **Cannot be hijacked** — `scan_for_injection` treats evidence as data, never instructions.

## Evidence integrity

This is the **architectural guardrail for guarantee 1 (cannot spoliate)**. Evidence
images are mounted **read-only at the OS layer**, so the agent is physically
incapable of altering them. Read-only is not asserted by a prompt — it is enforced
by the Linux kernel and then **proven by a failed write**.

> Linux mechanism. These commands run inside the **SIFT VM**; loop-mounting cannot
> be exercised on Windows.

**Raw / dd image:**

```bash
sudo scripts/mount_ro.sh /path/evidence.dd /mnt/evidence
# mounts with: mount -o ro,loop,noload ...
# prints "RO VERIFIED" — reached only because a probe write inside the
# mountpoint FAILED. If a write ever succeeds, the script aborts loudly.
```

**E01 / EWF image** (expose a raw device first, then mount that read-only):

```bash
mkdir -p /mnt/ewf
ewfmount /path/evidence.E01 /mnt/ewf      # creates /mnt/ewf/ewf1 (raw)
sudo scripts/mount_ro.sh /mnt/ewf/ewf1 /mnt/evidence
```

**Unmount:**

```bash
sudo scripts/unmount_ro.sh /mnt/evidence
```

The mount is verified read-only by the fact that **a write inside it fails**:
`mount_ro.sh` attempts to `touch` a probe file in the mountpoint and only prints
`RO VERIFIED` when that write is rejected. `sworn.mount.is_readonly()` provides a
software-side cross-check by parsing `/proc/mounts`. The source image is never
written to under any code path. See [docs/test_ro_mount.md](docs/test_ro_mount.md)
for the reproducible test.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    POSIX: source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m sworn.server      # prints: sworn mcp up
```

## Ledger self-check

```bash
python -c "import json,os,tempfile; from sworn import Receipt,Ledger; d=tempfile.mkdtemp(); p=os.path.join(d,'l.jsonl'); L=Ledger(p); r=Receipt.for_run(tool_name='t',args={},file_path='a',raw_output=b'orig'); L.append(r); print('clean:',L.verify()); ls=open(p).read().splitlines(); e=json.loads(ls[0]); e['receipt']['raw_output_sha256']='FORGED'; ls[0]=json.dumps(e); open(p,'w').write(chr(10).join(ls)+chr(10)); print('tampered:',L.verify())"
```

Expected:

```
clean: (True, None)
tampered: (False, 0)
```
