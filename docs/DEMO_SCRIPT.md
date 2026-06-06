# sworn — demo video script (< 5 min, live terminal + narration)

rule: live terminal screencast, your voice, real evidence, includes a self-correction sequence. no slides.

## 0:00 — the hook (10s)
"every other incident-response agent asks you to trust it didn't lie.
sworn is built so it can't — and i'll prove three guarantees live against a real compromised web server."

## 0:10 — the evidence is real (35s)
- run: `ewfverify ~/evidence/Case1-Webserver.E01` (or show the tail you already have)
- say: "ali hadi case 1, a windows web server breach. verified with ewfverify — stored md5 equals calculated md5. this is real, intact evidence."

## 0:45 — guarantee 1: cannot spoliate (40s)
- run the guarantee-1 python block (file mode 444, write blocked, no write functions)
- say: "evidence is read-only at the os layer, and sworn's toolset exposes zero write functions.
  watch it try to write to the evidence — permission denied at the boundary. it's not a rule the agent follows; it's a capability that doesn't exist."

## 1:25 — find the evil (50s)
- run the mft + synthesize block; show records: 134,075 and the flagged list
- say: "sworn reads 134 thousand filesystem records read-only, then reasons like an analyst.
  it surfaces a c99 webshell — a known php backdoor — dropped in the administrator's temp folder and deleted."

## 2:15 — guarantee 2 + self-correction (the required sequence) (70s)
- run the corroborate block; show iter 1 -> iter 2 -> confirmed-high
- say: "here's the self-correction. iteration one: a hypothesis from the timeline.
  iteration two: sworn automatically corroborates it against a second independent tool, istat.
  both agree, so it upgrades to confirmed-high. if they hadn't, it would downgrade to weak rather than over-assert.
  every step gets a receipt."

## 3:25 — guarantee 2 proven: the ledger can't be faked (45s)
- show ledger.jsonl; run verify() -> (True, None); then tamper one line and re-verify -> (False, N)
- say: "every finding traces to a hash-chained receipt. the chain verifies clean.
  now i tamper one entry — and the chain breaks at that exact line. a finding cannot be fabricated or altered without sworn catching it."

## 4:10 — close (20s)
- say: "cannot spoliate, cannot fabricate, all traceable — demonstrated on real evidence, not promised.
  that's sworn."
