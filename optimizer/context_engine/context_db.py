from __future__ import annotations
import json, pathlib, time, hashlib
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional

ROOT = pathlib.Path(__file__).resolve().parents[2]
STORE = ROOT / "context_db.jsonl"
STORE.parent.mkdir(parents=True, exist_ok=True)

def _ts() -> float:
    return time.time()

def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

@dataclass(frozen=True)
class ContextItem:
    ts: float
    fingerprint: str
    source: str
    payload: Dict[str, Any]
    tags: List[str]
    reroute_depth: int = 0
    entropy: float = 0.0

def append_item(source: str, payload: Dict[str, Any], tags: Iterable[str], reroute_depth=0, entropy=0.0) -> ContextItem:
    item = ContextItem(ts=_ts(), fingerprint=_sha({"source":source,"payload":payload}), source=source, payload=payload, tags=list(tags), reroute_depth=reroute_depth, entropy=entropy)
    with STORE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")
    return item

def load_all() -> List[Dict[str, Any]]:
    if not STORE.exists():
        return []
    return [json.loads(l) for l in STORE.read_text(encoding="utf-8").splitlines() if l.strip()]