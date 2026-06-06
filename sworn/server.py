"""sworn mcp server entrypoint. run: python -m sworn.server -> prints "sworn mcp up".
registers ZERO tools at this stage. tools are wired in later, each a typed read-only
function returning (records, receipt). there is intentionally no generic shell/write tool."""
from __future__ import annotations

def main() -> None:
    print("sworn mcp up")

if __name__ == "__main__":
    main()
