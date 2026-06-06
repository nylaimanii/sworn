# submission checklist - sworn

every box maps to a turn-in. each links to where the artifact lives.

- [x] public code repository - github.com/nylaimanii/sworn
- [x] open-source license (MIT), visible in About - LICENSE
- [x] README with setup instructions - README.md
- [x] run instructions (reproducible, fresh-clone verified) - docs/RUN.md
- [x] text description of features - README.md and docs/RUN.md
- [ ] demo video (under 5 min, live terminal, narration) - [YouTube link here]
- [x] architecture diagram (trust boundaries labelled) - docs/architecture.svg
- [x] evidence dataset documentation - docs/ACCURACY.md
- [x] accuracy report - docs/ACCURACY.md
- [x] agent execution logs (timestamped, traceable) - produced at ~/sworn_run/execution.log.jsonl by python -m sworn.run

## what sworn is
an incident response agent architecturally incapable of lying. three guarantees, proven live on verified ali hadi case 1 evidence:
1. cannot spoliate - evidence read-only at the os layer; no write function in the tool schema
2. cannot fabricate - every finding carries a receipt in an append-only hash-chained ledger
3. cannot be hijacked - evidence is data, never instructions; injection payloads are flagged, not obeyed

self-correction: a finding is corroborated against a second independent tool before being upgraded to confirmed.

## one-command reproduction
python -m sworn.run ~/evidence/Case1-Webserver.E01
