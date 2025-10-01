from __future__ import annotations
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CTX = ROOT / "context_db.jsonl"
DOCS = ROOT / "docs" / "api"; DOCS.mkdir(parents=True, exist_ok=True)
OUT = DOCS / "retrieval_flow.mmd"

def main():
    n = 0
    if CTX.exists():
        for _ in CTX.read_text(encoding="utf-8").splitlines():
            n += 1
    mmd = "\n".join([
        "graph TD",
        "  Q[Query] -->|search| Retriever",
        "  Retriever -->|hits| Render",
        f"  classDef dim fill:#eee;",
        f"  Note((context items: {n})):::dim"
    ]) + "\n"
    OUT.write_text(mmd, encoding="utf-8")
    print("WROTE", OUT)

if __name__ == "__main__":
    main()