from __future__ import annotations
import argparse, json, re
from typing import List
from .context_db import scan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    args = ap.parse_args()
    rx = re.compile(re.escape(args.query), re.I)
    hits: List[dict] = []
    for rec in scan():
        if rx.search(json.dumps(rec, ensure_ascii=False)):
            hits.append(rec)
    print(json.dumps(hits[:50], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()