"""synthesizer: turns typed records + receipts into a structured investigative
narrative, not a raw log. every flagged finding carries its receipt id, so a
claim cannot appear in the narrative without tracing to a ledger entry."""
from __future__ import annotations
import re
from dataclasses import dataclass
from .tools.mft import MFTEntry
from .receipt import Receipt

# patterns a senior analyst would flag on a compromised web server
_SUSPICIOUS = [
    (r"\.(php|asp|aspx|jsp)$", "web-executable in filesystem (possible webshell)"),
    (r"(cmd|powershell|nc|netcat|mimikatz|psexec)\.exe$", "attacker tooling / lolbin"),
    (r"/(inetpub|wwwroot|htdocs|xampp)/", "file under web-served directory"),
    (r"\.(bat|vbs|ps1)$", "script artifact"),
    (r"(shell|backdoor|webshell|r57|c99)", "suspicious filename keyword"),
]

@dataclass
class Finding:
    claim: str
    why: str
    inode: str
    filename: str
    receipt_id: str
    confidence: str  # "confirmed" (traces to receipt) or "inference"

def synthesize(records: list[MFTEntry], receipt: Receipt) -> tuple[list[Finding], str]:
    findings: list[Finding] = []
    for r in records:
        for pat, why in _SUSPICIOUS:
            if re.search(pat, r.filename, re.IGNORECASE):
                findings.append(Finding(
                    claim=f"flagged: {r.filename}",
                    why=why, inode=r.inode, filename=r.filename,
                    receipt_id=receipt.receipt_id, confidence="confirmed",
                ))
                break
    # build the narrative
    lines = []
    lines.append("# sworn — investigative finding")
    lines.append("")
    lines.append("## summary")
    lines.append(f"analyzed {len(records):,} filesystem records from the mft timeline. "
                 f"flagged {len(findings)} entries of forensic interest on a windows web server. "
                 f"all findings trace to tool execution receipt `{receipt.receipt_id}`.")
    lines.append("")
    lines.append("## flagged findings (each traces to a receipt)")
    for f in findings[:40]:
        lines.append(f"- **{f.filename}** — {f.why}  ")
        lines.append(f"  inode `{f.inode}` · receipt `{f.receipt_id}` · {f.confidence}")
    if not findings:
        lines.append("- none matched the suspicious-pattern set; no confirmed findings to assert.")
    return findings, "\n".join(lines)
