"""synthesizer: turns typed records + receipts into a structured investigative
narrative, not a raw log. every flagged finding carries its receipt id, so a
claim cannot appear in the narrative without tracing to a ledger entry.

patterns are deliberately TIGHT: a senior analyst flags attacker artifacts,
not every innocent file whose path happens to contain a keyword. over-flagging
is itself a failure mode (see accuracy report)."""
from __future__ import annotations
import re
from dataclasses import dataclass
from .tools.mft import MFTEntry
from .receipt import Receipt

# web-served roots where a dropped executable script is genuinely suspicious
_WEBROOT = re.compile(r"/(inetpub/wwwroot|htdocs|www|webapps)/", re.IGNORECASE)
# executable web scripts (webshell candidates) ONLY when under a web root
_WEBSCRIPT = re.compile(r"\.(php|asp|aspx|jsp|jspx)$", re.IGNORECASE)
# named attacker tooling / known webshell families
_TOOLING = re.compile(r"(mimikatz|psexec|\bnc\.exe$|netcat|r57|c99|b374k|webshell|backdoor)", re.IGNORECASE)
# skip obvious benign noise so we don't re-introduce false positives
_BENIGN = re.compile(r"(\$FILE_NAME\)|/Start Menu/|\.lnk$|\.url$|Uninstall)", re.IGNORECASE)

@dataclass
class Finding:
    filename: str
    why: str
    inode: str
    receipt_id: str
    confidence: str

def synthesize(records: list[MFTEntry], receipt: Receipt) -> tuple[list[Finding], str]:
    findings: list[Finding] = []
    for r in records:
        name = r.filename
        if _BENIGN.search(name):
            continue
        why = None
        if _WEBSCRIPT.search(name) and _WEBROOT.search(name):
            why = "executable web script under a served web root (webshell candidate)"
        elif _TOOLING.search(name):
            why = "named attacker tooling / known webshell family"
        if why:
            findings.append(Finding(filename=name, why=why, inode=r.inode,
                                    receipt_id=receipt.receipt_id, confidence="confirmed"))
    lines = ["# sworn — investigative finding", "",
             "## summary",
             f"analyzed {len(records):,} filesystem records from the mft timeline. "
             f"flagged {len(findings)} entries of forensic interest under tight, analyst-style criteria "
             f"(web-served executable scripts and named attacker tooling only). "
             f"all findings trace to tool execution receipt `{receipt.receipt_id}`.", "",
             "## flagged findings (each traces to a receipt)"]
    for f in findings[:40]:
        lines.append(f"- **{f.filename}** — {f.why}  ")
        lines.append(f"  inode `{f.inode}` · receipt `{f.receipt_id}` · {f.confidence}")
    if not findings:
        lines.append("- none matched the tight criteria; no confirmed findings asserted on this pass.")
    return findings, "\n".join(lines)
