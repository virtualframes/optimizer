from __future__ import annotations
import argparse, json
from optimizer.context_engine.context_db import load_all

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    args = ap.parse_args()
    q = args.query.lower()
    hits = [r for r in load_all() if q in json.dumps(r, ensure_ascii=False).lower()]
    print(json.dumps({"count": len(hits), "results": hits[:25]}, ensure_ascii=False))