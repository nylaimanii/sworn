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
