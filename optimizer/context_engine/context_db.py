from __future__ import annotations
import json, pathlib, time
from typing import Dict, Any, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[2]
DB = ROOT / "context_db.jsonl"

def append(item: Dict[str, Any]) -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    with DB.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

def scan() -> Iterable[Dict[str, Any]]:
    if not DB.exists(): return []
    for l in DB.read_text(encoding="utf-8").splitlines():
        if l.strip():
            try: yield json.loads(l)
            except Exception: continue

def make_record(payload: Dict[str, Any], entropy: float, depth: int) -> Dict[str, Any]:
    return {"ts": time.time(), "payload": payload, "entropy": entropy, "reroute_depth": depth}