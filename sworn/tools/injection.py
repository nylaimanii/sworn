"""scan_for_injection — guarantee 3 (cannot be hijacked). scans evidence TEXT for
prompt-injection patterns and returns an INDICATOR (a finding) — it never acts on
the content. evidence is data, never instructions."""
from __future__ import annotations
import re
from dataclasses import dataclass
from ..receipt import Receipt

_PATTERNS = [
    r"ignore (all )?(prior|previous) instructions",
    r"system\s*:",
    r"mark (the )?host clean",
    r"you are now",
    r"disregard .* rules",
]

@dataclass
class InjectionIndicator:
    matched_pattern: str
    excerpt: str
    location: str

def scan_for_injection(artifact_text: str, location: str) -> tuple[list[InjectionIndicator], Receipt]:
    indicators: list[InjectionIndicator] = []
    for pat in _PATTERNS:
        for m in re.finditer(pat, artifact_text, re.IGNORECASE):
            start = max(0, m.start() - 30)
            end = min(len(artifact_text), m.end() + 30)
            indicators.append(InjectionIndicator(matched_pattern=pat, excerpt=artifact_text[start:end], location=location))
    receipt = Receipt.for_run(tool_name="scan_for_injection", args={"location": location},
                              file_path=location, raw_output=artifact_text.encode("utf-8", "replace"))
    return indicators, receipt
