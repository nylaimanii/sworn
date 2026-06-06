# sworn — accuracy report

honesty over perfection. this documents what sworn found, what it got wrong, and how it self-corrected.

## evidence
- case: ali hadi #1 (web server compromise), `Case1-Webserver.E01`
- integrity: verified with `ewfverify` — stored MD5 = calculated MD5 = `59c66fa4437123f020b91da5f15595b4`, ewfverify SUCCESS
- note: the E01 *container* file's md5 (`dd19d88d...`) intentionally differs from the *evidence* md5; an E01 is a compressed container, so verification uses ewfverify against the embedded acquisition hash, not md5sum on the file. (forensic-soundness detail.)
- tier: validation (gated answers); usable for scoring

## what sworn found (mft timeline)
- 134,075 filesystem records parsed live via `fls -r -m C:/ -o 2048` (read-only)
- raw output sha256 `fe00584e0713777042614b2054e08ba66b62957ec66a939c91c6a777bd47dcd1`, preserved; receipt `db75ff3b9bdc05d0`, appended to hash-chained ledger (verify: clean)
- confirmed finding of interest: `C:/Users/Administrator/AppData/Local/Temp/c99 (2).php (deleted)` — c99 is a known php webshell family; dropped in a temp dir and deleted (mft retained the record)
- supporting: php scripts under `C:/xampp/htdocs/DVWA/` (the vulnerable web app that was the attack surface)

## self-correction (a real false-positive pass we caught and fixed)
- **first synthesizer pass:** flagged 40,387 / 134,075 records. broad keyword match (any path containing "xampp") swept in tens of thousands of innocent files — e.g. legitimate XAMPP Start Menu shortcuts (`.lnk`, `.url`). this is over-calling: an agent flagging ~30% of a filesystem is noise, not analysis.
- **correction:** tightened to analyst-grade criteria — executable web scripts only when under a served web root, plus named attacker-tooling families; benign noise (Start Menu, .lnk/.url, $FILE_NAME, Uninstall) excluded.
- **second pass:** 477 flagged. surfaced the real c99 webshell instead of burying it under shortcut noise. ~99% reduction in false positives.

## known limitations (honest)
- 477 still over-includes: DVWA legitimately contains many `.php` files, so "executable script under web root" flags benign app files alongside the real webshell. a production pass would correlate with timeline anomalies / known-bad hashes to rank further. documented rather than hidden.
- findings asserted as "confirmed" trace to a tool-execution receipt; intent (malice vs. legitimate) is not over-claimed.

## self-correction by corroboration (live, on the c99 finding)
- iteration 1 (hypothesis): mft timeline flagged `C:/Users/Administrator/AppData/Local/Temp/c99 (2).php (deleted)` (inode 62338-128-4) as a webshell candidate.
- iteration 2 (corroboration): an independent second tool (`istat` on the inode) was run automatically. it confirmed a metadata entry consistent with a dropped-then-deleted file.
- verdict: **confirmed-high** (both sources agree). the corroboration step has its own receipt (`af45baa5f9e88403`) appended to the ledger; chain verifies clean.
- design: a finding that could NOT be corroborated would be downgraded to "weak" and not asserted as confirmed — over-assertion is treated as a failure. hard max-iterations cap prevents runaway loops.
