import json, pathlib, time
ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "mutations.jsonl"
DOCS  = ROOT / "docs" / "api"; DOCS.mkdir(parents=True, exist_ok=True)
MMD   = DOCS / "lineage.mmd"

def load_events():
    if not AUDIT.exists(): return []
    lines = []
    for ln in AUDIT.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            try: lines.append(json.loads(ln))
            except Exception: pass
    return lines

def to_mermaid(events):
    nodes, edges = set(), set()
    for e in events:
        kind = e.get("kind","event")
        ts   = e.get("ts",0)
        ev   = e.get("event_id") or e.get("parent_id") or f"{kind}-{int(ts)}"
        nodes.add((ev, kind))
        parent = e.get("parent_id")
        if parent:
            edges.add((parent, ev, kind))
    out = ["flowchart TD"]
    for ev, kind in sorted(nodes):
        out.append(f'  "{ev}"["{kind}\\n{ev[:10]}"]')
    for a,b,k in sorted(edges):
        out.append(f'  "{a}" -->|{k}| "{b}"')
    out.append("classDef default fill:#eef,stroke:#112;")
    return "\n".join(out) + "\n"

def main():
    evs = load_events()
    MMD.write_text(to_mermaid(evs), encoding="utf-8")
    print("WROTE", MMD, f"({len(evs)} events)")

if __name__ == "__main__":
    main()
