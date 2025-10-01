from __future__ import annotations
import json, pathlib, sys
from typing import List, Dict

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "api"
BASE = DOCS / "service_graph.mmd"
ROUTES_JSON = DOCS / "routes.json"
ROUTEMAP_YAML = DOCS / "routemap.yaml"
OUT = DOCS / "service_graph_routes.mmd"

def _load_routes() -> List[Dict]:
    if ROUTES_JSON.exists():
        try:
            return json.loads(ROUTES_JSON.read_text(encoding="utf-8")).get("routes", [])
        except json.JSONDecodeError as e:
            print(f"Error: Could not decode {ROUTES_JSON}. Details: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: Could not read {ROUTES_JSON}. Details: {e}", file=sys.stderr)

    if ROUTEMAP_YAML.exists():
        try:
            import yaml
        except ImportError:
            print("Warning: PyYAML is not installed. Skipping routemap.yaml.", file=sys.stderr)
            return []

        try:
            y = yaml.safe_load(ROUTEMAP_YAML.read_text(encoding="utf-8"))
            if y and "routes" in y:
                return y.get("routes", [])
        except yaml.YAMLError as e:
            print(f"Error: Could not parse {ROUTEMAP_YAML}. Details: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error: Could not read {ROUTEMAP_YAML}. Details: {e}", file=sys.stderr)

    return []

def main():
    base = BASE.read_text(encoding="utf-8") if BASE.exists() else "graph TD\n A[service]-->B[service]"
    routes = _load_routes()
    lines = [l for l in base.splitlines() if l.strip()]
    lines.append("")
    lines.append("%% ---- Route overlays ----")
    if not routes:
        lines.append("%% (no routes.json / routemap.yaml found; overlay skipped)")
    else:
        lines.append("subgraph Routes")
        for i, r in enumerate(routes[:300]):
            path = r.get("path") or r.get("route") or "/"
            method = (r.get("method") or r.get("methods") or "GET")
            node = f"R{i}"
            lines.append(f'    {node}["{method} {path}"]')
        lines.append("end")
        # Optional: link common pairs
        for i in range(min(20,len(routes))):
            lines.append(f"    Services---R{i}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE", OUT)

if __name__ == "__main__":
    main()