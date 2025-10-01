from __future__ import annotations
import json, time, pathlib
from typing import Dict, Any, Iterable

class ContextDB:
    def __init__(self, path: str = "context_db.jsonl"):
        self.path = pathlib.Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, obj: Dict[str, Any]) -> None:
        obj.setdefault("ts", time.time())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def query(self, predicate=lambda x: True, limit: int | None = None) -> Iterable[Dict[str, Any]]:
        if not self.path.exists():
            return []
        out = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if predicate(rec):
                        out.append(rec)
                    if limit and len(out) >= limit:
                        break
                except:  # noqa
                    continue
        return out