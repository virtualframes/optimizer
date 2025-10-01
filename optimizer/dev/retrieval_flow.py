from __future__ import annotations
import pathlib, time
from optimizer.context_engine.context_db import load_all

OUT = pathlib.Path("docs/api/retrieval_flow.mmd")
OUT.parent.mkdir(parents=True, exist_ok=True)

def main():
    rows = load_all()
    lines = ["flowchart TD"," Q[Query]-->F[Filter Context]"," F-->R[Results]"]
    # lightweight mapping by tag → node
    buckets = {}
    for r in rows[:200]:
        tag = (r.get("tags") or ["misc"])[0]
        buckets.setdefault(tag, 0); buckets[tag]+=1
    for i, (tag, n) in enumerate(sorted(buckets.items(), key=lambda x:-x[1])[:10]):
        nid = f"T{i}"
        lines.append(f" F--> {nid}([{tag} x{n}])")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE", OUT)