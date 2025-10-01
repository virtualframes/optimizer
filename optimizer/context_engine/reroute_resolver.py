from __future__ import annotations
import argparse, json, pathlib
from typing import Dict, Any, List

ROOT = pathlib.Path(__file__).resolve().parents[2]
MJSONL = ROOT / "audit" / "mutations.jsonl"

def lineage(event_id: str) -> Dict[str, Any]:
    if not MJSONL.exists():
        return {"event_id": event_id, "lineage": []}
    lines = [json.loads(l) for l in MJSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_eid = {d.get("event_id", d.get("eventid")): d for d in lines if isinstance(d, dict)}
    chain: List[Dict[str, Any]] = []
    cur = by_eid.get(event_id)
    # walk parent_id → backwards
    while cur:
        chain.append(cur)
        pid = cur.get("parent_id") or cur.get("parentid")
        cur = by_eid.get(pid)
    return {"event_id": event_id, "lineage": chain}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="anchor/mission event id")
    args = ap.parse_args()
    print(json.dumps(lineage(args.id), indent=2, ensure_ascii=False))