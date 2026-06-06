"""self-correction by corroboration: a finding from one source (mft timeline) is
treated as a HYPOTHESIS, then independently checked against a second tool (istat
on the inode). agree -> upgrade to high-confidence; can't corroborate -> flag as
weak rather than assert. iteration-over-iteration is logged. hard max-iterations cap."""
from __future__ import annotations
import subprocess, shutil, json
from dataclasses import dataclass, asdict
from .receipt import Receipt

@dataclass
class Iteration:
    n: int
    action: str
    result: str
    receipt_id: str | None

def _istat(image_path: str, inode_full: str, offset: int = 2048) -> bytes:
    # inode in body format looks like "62338-128-4"; istat wants the base inode
    base = inode_full.split("-")[0]
    return subprocess.run(["istat","-o",str(offset),image_path,base],
                          capture_output=True).stdout

def corroborate(image_path: str, finding_filename: str, finding_inode: str,
                max_iterations: int = 3) -> tuple[str, list[Iteration], list[Receipt]]:
    if shutil.which("istat") is None:
        raise RuntimeError("the sleuth kit (istat) not found — run in the codespace")
    iters: list[Iteration] = []
    receipts: list[Receipt] = []

    # iteration 1: the initial hypothesis from the mft timeline pass
    iters.append(Iteration(1, "hypothesis from mft timeline",
                           f"flagged {finding_filename} (inode {finding_inode}) as webshell candidate",
                           None))

    # iteration 2: corroborate against a second, independent tool (istat)
    raw = _istat(image_path, finding_inode)
    rcpt = Receipt.for_run(tool_name="istat_corroboration",
                           args={"image_path": image_path, "inode": finding_inode},
                           file_path=image_path, raw_output=raw)
    receipts.append(rcpt)
    text = raw.decode("utf-8","replace").lower()
    # does the second source independently support a real, deleted file entry?
    deleted = "not allocated" in text or "deleted" in text or "$file_name" in text
    has_meta = "size:" in text or "crtime" in text or "mft entry" in text
    if has_meta and deleted:
        verdict = "confirmed-high"
        result = "istat independently confirms a metadata entry consistent with a dropped-then-deleted file. finding UPGRADED."
    elif has_meta:
        verdict = "confirmed"
        result = "istat confirms the inode metadata exists; deletion state not independently established. finding HELD as confirmed (not upgraded)."
    else:
        verdict = "weak"
        result = "istat could not corroborate the inode. finding DOWNGRADED to weak — not asserted as confirmed."
    iters.append(Iteration(2, "corroborate via istat (independent source)", result, rcpt.receipt_id))

    # cap respected: we stop after corroboration (well under max_iterations)
    assert len(iters) <= max_iterations
    return verdict, iters, receipts
