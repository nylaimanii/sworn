# running sworn (for judges)

sworn runs on the SANS SIFT Workstation or any linux with The Sleuth Kit + ewf-tools.
verified reproducible from a clean clone (see the fresh-clone test in the accuracy report).

## 1. prerequisites

    sudo apt update && sudo apt install -y sleuthkit ewf-tools p7zip-full python3-pip

## 2. clone + install

    git clone https://github.com/nylaimanii/sworn.git
    cd sworn
    pip install -r requirements.txt

## 3. get + verify the evidence (ali hadi case 1)

    mkdir -p ~/evidence && cd ~/evidence
    wget https://archive.org/download/dfir-case1/Case1-Webserver.E01
    wget https://archive.org/download/dfir-case1/Case1-Webserver.E01.txt
    ewfverify Case1-Webserver.E01
    # expect: ewfverify SUCCESS, md5 59c66fa4437123f020b91da5f15595b4

## 4. run the full investigation

    cd /path/to/sworn
    python -m sworn.run ~/evidence/Case1-Webserver.E01

expected (one auditable run):
- guarantee1_readonly: evidence read-only at the os layer
- mft_timeline: 134,075 records parsed (read-only)
- synthesize: findings of interest, including a c99 webshell
- self_correct: c99 upgraded to confirmed-high via istat corroboration
- guarantee3_injection: planted payloads flagged, host NOT marked clean
- ledger_verify: chain intact=True

## outputs
- ~/sworn_run/finding.md - structured investigative narrative
- ~/sworn_run/execution.log.jsonl - timestamped execution log (every finding traces to a receipt)
- ~/sworn_run/ledger.jsonl - hash-chained provenance ledger
