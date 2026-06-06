# running sworn (for judges)

sworn runs on the SANS SIFT Workstation or any linux with The Sleuth Kit + ewf-tools.
verified reproducible from a clean clone (see fresh-clone test in the accuracy report).

## 1. prerequisites




cd /workspaces/sworn && cat > docs/RUN.md << 'PYEOF'
# running sworn (for judges)

sworn runs on the SANS SIFT Workstation or any linux with The Sleuth Kit + ewf-tools.
verified reproducible from a clean clone (see fresh-clone test in the accuracy report).

## 1. prerequisites
## 2. clone + install
## 3. get + verify the evidence (ali hadi case 1)
## 4. run the full investigation
expected (one auditable run):
- guarantee1_readonly: evidence read-only at the os layer
- mft_timeline: 134,075 records parsed (read-only)
- synthesize: findings of interest, including a c99 webshell
- self_correct: c99 upgraded to confirmed-high via istat corroboration
- guarantee3_injection: planted payloads flagged, host NOT marked clean
- ledger_verify: chain intact=True

## outputs
- `~/sworn_run/finding.md` — structured investigative narrative
- `~/sworn_run/execution.log.jsonl` — timestamped execution log (every finding traces to a receipt)
- `~/sworn_run/ledger.jsonl` — hash-chained provenance ledger (run verify to confirm)
