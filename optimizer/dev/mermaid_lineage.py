from __future__ import annotations
import json, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"; AUDIT.mkdir(parents=True, exist_ok=True)
MUT = AUDIT / "mutations.jsonl"
DOCS = ROOT / "docs" / "api"; DOCS.mkdir(parents=True, exist_ok=True)
OUT = DOCS / "lineage.mmd"

def main():
    events = []
    if MUT.exists():
        for l in MUT.read_text(encoding="utf-8").splitlines():
            if l.strip():
                try: events.append(json.loads(l))
                except Exception: pass
    lines = ["graph TD", f"  subgraph Lineage [{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}]"]
    ids = []
    for i, e in enumerate(events[:200]):
        nid = f"E{i}"
        ids.append(nid)
        label = (e.get("kind") or "event").replace('"', "'")
        lines.append(f'  {nid}["{label}"]')
    lines.append("  end")
    for i in range(len(ids)-1):
        lines.append(f"  {ids[i]} --> {ids[i+1]}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE", OUT)

if __name__ == "__main__":
    main()