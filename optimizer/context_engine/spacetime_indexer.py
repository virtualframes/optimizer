from __future__ import annotations
import argparse, json
from .context_db import append, make_record
from .fingerprint_logger import fingerprint

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--entropy", type=float, default=0.3)
    ap.add_argument("--payload", type=str, default='{"note":"manual tick"}')
    args = ap.parse_args()
    payload = json.loads(args.payload)
    rec = make_record(payload, args.entropy, args.depth)
    rec["fingerprint"] = fingerprint({"payload": payload, "entropy": args.entropy, "depth": args.depth})
    append(rec)
    print(rec["fingerprint"])

if __name__ == "__main__":
    main()