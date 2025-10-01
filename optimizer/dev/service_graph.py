import pathlib, json

OUT = pathlib.Path("docs/api/service_graph.mmd")
OUT.parent.mkdir(parents=True, exist_ok=True)

def build_graph():
    # Minimal topology; extend with introspection (FastAPI routes, CLI map, files)
    nodes = [
        ("Orchestrator","orchestrator"),
        ("ToolExecutor","tools"),
        ("AutoMutator","selflearning"),
        ("BenchmarkRunner","benchmark"),
        ("RiskScan","analytics"),
        ("CitationIngestor","scraper"),
        ("VaultUpdater","dev"),
    ]
    edges = [
        ("Orchestrator","ToolExecutor"),
        ("Orchestrator","AutoMutator"),
        ("AutoMutator","BenchmarkRunner"),
        ("BenchmarkRunner","RiskScan"),
        ("RiskScan","AutoMutator"),
        ("CitationIngestor","AutoMutator"),
        ("AutoMutator","VaultUpdater"),
    ]
    lines = ["```mermaid","graph TD"]
    for n,lab in nodes:
        lines.append(f'  {lab}["{n}"]')
    for a,b in edges:
        lines.append(f"  {a} --> {b}")
    lines.append("```")
    OUT.write_text("\n".join(lines)+"\n", encoding="utf-8")

def main(): build_graph()
if __name__ == "__main__": main()