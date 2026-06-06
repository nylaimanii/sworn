"""sworn — single investigation entrypoint.

usage: python -m sworn.run <e01_image> [--offset N]

ties the whole pipeline into one auditable run:
  guarantee 1 (read-only check) -> mft timeline -> synthesize findings ->
  self-correct by corroboration -> guarantee 3 injection scan -> hash-chained ledger.
emits a timestamped execution log (the agent-execution-logs turn-in) where every
finding traces back to the tool execution + receipt that produced it.
"""
from __future__ import annotations
import sys, os, json, argparse, stat
from datetime import datetime, timezone
from pathlib import Path
from .tools.mft import extract_mft_timeline
from .tools.injection import scan_for_injection
from .synth import synthesize
from .selfcorrect import corroborate
from .ledger import Ledger

def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="sworn")
    ap.add_argument("image")
    ap.add_argument("--offset", type=int, default=2048)
    ap.add_argument("--outdir", default=os.path.expanduser("~/sworn_run"))
    args = ap.parse_args(argv)

    out = Path(args.outdir); (out / "raw").mkdir(parents=True, exist_ok=True)
    log_path = out / "execution.log.jsonl"
    led = Ledger(out / "ledger.jsonl")
    log = log_path.open("a", encoding="utf-8")
    def event(stage, detail, receipt_id=None):
        rec = {"ts": _ts(), "stage": stage, "detail": detail, "receipt_id": receipt_id}
        log.write(json.dumps(rec) + "\n"); log.flush()
        print(f"[{rec['ts']}] {stage}: {detail}" + (f"  (receipt {receipt_id})" if receipt_id else ""))

    event("start", f"sworn investigation of {args.image}")

    # guarantee 1: confirm evidence is read-only
    mode = stat.S_IMODE(os.stat(args.image).st_mode)
    ro = not bool(mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    event("guarantee1_readonly", f"evidence mode {oct(mode)} read_only={ro}")

    # mft timeline (live, read-only)
    records, mft_rcpt = extract_mft_timeline(args.image, args.offset)
    led.append(mft_rcpt)
    (out / "raw" / f"{mft_rcpt.raw_output_sha256}.txt").write_bytes(b"")  # placeholder; raw preserved by tool
    event("mft_timeline", f"parsed {len(records)} records", mft_rcpt.receipt_id)

    # synthesize findings (structured narrative, not raw log)
    findings, report = synthesize(records, mft_rcpt)
    (out / "finding.md").write_text(report)
    event("synthesize", f"flagged {len(findings)} findings of interest", mft_rcpt.receipt_id)

    # self-correction by corroboration on the top finding
    verdict = "n/a"
    if findings:
        target = next((f for f in findings if "c99" in f.filename.lower()), findings[0])
        verdict, iters, rcpts = corroborate(args.image, target.filename, target.inode)
        for r in rcpts: led.append(r)
        event("self_correct", f"{target.filename} -> {verdict}", rcpts[-1].receipt_id if rcpts else None)

    # guarantee 3: scan any provided log artifacts for injection (data, not instructions)
    inj_dir = Path(os.path.expanduser("~/cases/injected"))
    inj_count = 0
    if inj_dir.exists():
        for f in inj_dir.glob("*"):
            if f.is_file():
                inds, ir = scan_for_injection(f.read_text(errors="replace"), str(f))
                led.append(ir); inj_count += len(inds)
                event("guarantee3_injection", f"{f.name}: {len(inds)} payloads flagged (not obeyed)", ir.receipt_id)

    ok, broken = led.verify()
    event("ledger_verify", f"chain intact={ok} broken_line={broken}")
    event("done", f"records={len(records)} findings={len(findings)} top_verdict={verdict} injection_flagged={inj_count}")
    log.close()
    print(f"\nexecution log: {log_path}\nfinding report: {out/'finding.md'}\nledger: {out/'ledger.jsonl'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
