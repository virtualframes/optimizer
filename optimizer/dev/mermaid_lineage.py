from __future__ import annotations
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
MJSONL = ROOT / "audit" / "mutations.jsonl"
OUT = ROOT / "docs/api/lineage.mmd"
OUT.parent.mkdir(parents=True, exist_ok=True)

def main():
    """Generates a basic Mermaid lineage graph."""
    lines = ["graph TD"]
    if not MJSONL.exists():
        lines.append("    A[No mutations found] --> B[No lineage to render]")
        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("WROTE", OUT)
        return

    mutations = [json.loads(line) for line in MJSONL.read_text(encoding="utf-8").splitlines() if line]

    if not mutations:
        lines.append("    A[No mutations found] --> B[No lineage to render]")
        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("WROTE", OUT)
        return

    for m in mutations:
        event_id = m.get("event_id") or m.get("eventid", "UnknownID")
        parent_id = m.get("parent_id") or m.get("parentid")

        if parent_id:
            lines.append(f"    {parent_id} --> {event_id}")
        else:
            lines.append(f"    {event_id}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE", OUT)