import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "api"; DOCS.mkdir(parents=True, exist_ok=True)
MMD  = DOCS / "service_graph.mmd"

GROUPS = {
  "agentkits": ["optimizer/agentkits"],
  "orchestration": ["optimizer/orchestration"],
  "api": ["optimizer/api"],
  "memory": ["optimizer/memory"],
  "benchmark": ["optimizer/benchmark"],
  "research": ["optimizer/research"],
  "resilience": ["optimizer/resilience"],
}

def main():
    lines = ["flowchart LR"]
    for k, roots in GROUPS.items():
        lines.append(f'  subgraph {k}')
        for r in roots:
            p = ROOT / r
            if not p.exists(): continue
            for f in p.rglob("*.py"):
                nid = f.as_posix()
                lines.append(f'    "{nid}"["{f.name}"]')
        lines.append("  end")
    # simple cross-edges
    edges = [
        ("optimizer/api","optimizer/orchestration"),
        ("optimizer/orchestration","optimizer/agentkits"),
        ("optimizer/agentkits","optimizer/memory"),
        ("optimizer/benchmark","optimizer/resilience"),
    ]
    for a,b in edges:
        lines.append(f'  "{a}" --> "{b}"')
    MMD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE", MMD)

if __name__ == "__main__":
    main()
