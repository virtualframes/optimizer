import ast, pathlib, json, time
from typing import Dict, Set, List

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "optimizer"
DOCS = ROOT / "docs" / "graphs"; DOCS.mkdir(parents=True, exist_ok=True)

def py_modules(root: pathlib.Path) -> List[pathlib.Path]:
    return [p for p in root.rglob("*.py") if "tests/" not in str(p)]

def mod_name(path: pathlib.Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)

def build_graph() -> Dict[str, Set[str]]:
    edges: Dict[str, Set[str]] = {}
    for p in py_modules(SRC):
        src = p.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(src)
        except Exception:
            continue
        m = mod_name(p)
        edges.setdefault(m, set())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    if n.name.startswith("optimizer"):
                        edges[m].add(n.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("optimizer"):
                    edges[m].add(node.module)
    return edges

def detect_cycles(edges: Dict[str, Set[str]]) -> List[List[str]]:
    # simple DFS cycle finder
    cycles = []
    visiting, visited = set(), set()
    stack: List[str] = []

    def dfs(u: str):
        visiting.add(u); stack.append(u)
        for v in edges.get(u, set()):
            if v in visiting:
                # record cycle starting at v
                if v in stack:
                    i = stack.index(v)
                    cyc = stack[i:] + [v]
                    if cyc not in cycles:
                        cycles.append(cyc)
            elif v not in visited:
                dfs(v)
        visiting.remove(u); visited.add(u); stack.pop()

    for n in list(edges.keys()):
        if n not in visited:
            dfs(n)
    return cycles

def write_outputs(edges: Dict[str, Set[str]], cycles: List[List[str]]):
    (DOCS/"code_graph.json").write_text(
        json.dumps({
            "generated": int(time.time()),
            "edges": {k: sorted(list(v)) for k, v in edges.items()},
            "cycles": cycles
        }, indent=2), encoding="utf-8"
    )
    # Mermaid
    lines = ["flowchart TD"]
    for a, outs in edges.items():
        if not outs:
            lines.append(f'  "{a}"')
        for b in outs:
            lines.append(f'  "{a}" --> "{b}"')
    if cycles:
        lines.append("\n%% cycles:")
        for cyc in cycles:
            lines.append("%% " + " -> ".join(cyc))
    (DOCS/"code_graph.mmd").write_text("\n".join(lines)+"\n", encoding="utf-8")

def main():
    g = build_graph()
    c = detect_cycles(g)
    write_outputs(g, c)
    print(f"Wrote docs/graphs/code_graph.mmd and .json; cycles={len(c)}")

if __name__ == "__main__":
    main()