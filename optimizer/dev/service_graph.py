from __future__ import annotations
import pathlib

OUT = pathlib.Path("docs/api/service_graph.mmd")
OUT.parent.mkdir(parents=True, exist_ok=True)

def main():
    """Generates a simple static service graph."""
    lines = [
        "graph TD",
        "    subgraph Web Scrapers",
        "        A[jules-ingest-citations]",
        "        B[jules-scrape-forks]",
        "        C[jules-map-apis]",
        "    end",
        "    subgraph Context Engine",
        "        D[jules-index-context]",
        "        E[jules-retrieve-context]",
        "    end",
        "    subgraph Agentic API",
        "        F[agentic-api-dev]",
        "    end",
        "    A --> D",
        "    B --> D",
        "    C --> D",
        "    F --> E",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE", OUT)