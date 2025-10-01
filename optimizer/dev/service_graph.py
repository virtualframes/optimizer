from __future__ import annotations
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "api"; DOCS.mkdir(parents=True, exist_ok=True)
OUT = DOCS / "service_graph.mmd"

def main():
    lines = [
        "graph TD",
        "  subgraph Services",
        "    API[FastAPI] --> Resilience[Entropy/Reroute]",
        "    API --> Context[Context Engine]",
        "    API --> Benchmark[Availability]",
        "    Resilience --> Audit[Audit Logs]",
        "    Context --> Docs[Docs & Graphs]",
        "  end"
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE", OUT)

if __name__ == "__main__":
    main()