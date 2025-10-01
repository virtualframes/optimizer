from __future__ import annotations
import argparse, json, os
from optimizer.context_engine.context_db import append_item

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entropy", type=float, default=float(os.getenv("OMEGA_ENTROPY", "0.0")))
    ap.add_argument("--depth", type=int, default=int(os.getenv("OMEGA_DEPTH", "3")))
    ap.add_argument("--source", default="indexer")
    ap.add_argument("--payload", default='{"note":"spacetime index tick"}')
    ap.add_argument("--tags", default="index,spacetime")
    args = ap.parse_args()
    payload = json.loads(args.payload)
    item = append_item(args.source, payload, args.tags.split(","), reroute_depth=args.depth, entropy=args.entropy)
    print(json.dumps({"ok": True, "fingerprint": item.fingerprint}, ensure_ascii=False))