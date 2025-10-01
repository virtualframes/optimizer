import json, pathlib, re, time
from collections import defaultdict
try:
    from optimizer.mutationanchor import MutationAnchor as _Anchor
except Exception:
    class _Anchor:
        def __init__(self): pass
        def record(self, kind, payload, parent_id=None):
            return type("Ev", (), {"event_id": f"noop-{int(time.time())}"})

ROOT = pathlib.Path(__file__).resolve().parents[2]
ENDPOINTS = ROOT / "docs" / "api" / "endpoints.jsonl"
REPORT = ROOT / "docs" / "api" / "debug_report.json"

def main():
    eps = []
    if ENDPOINTS.exists():
        for line in ENDPOINTS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                eps.append(json.loads(line))
    collisions = defaultdict(list)
    for e in eps:
        key = (e["method"], e["path"])
        collisions[key].append((e["framework"], e["file"], e["line"]))
    dupes = {k:v for k,v in collisions.items() if len(v) > 1}

    # Weak auth hints: FastAPI route without Depends(...) nearby
    weak_auth = []
    for e in eps:
        if e["framework"] == "fastapi":
            txt = pathlib.Path(e["file"]).read_text(encoding="utf-8", errors="ignore")
            win = "\n".join(txt.splitlines()[max(0,e["line"]-6):e["line"]+5])
            if "Depends(" not in win and not re.search(r"@router\.(get|post|put|delete|patch).*\[auth", win, flags=re.I):
                weak_auth.append(e)

    report = {
        "generated": int(time.time()),
        "endpoint_count": len(eps),
        "duplicate_routes": {f"{m} {p}": v for (m,p), v in dupes.items()},
        "weak_auth_hints": [{"method": x["method"], "path": x["path"], "file": x["file"], "line": x["line"]} for x in weak_auth],
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    ev = _Anchor().record(kind="api_debug", payload={"dupes": len(dupes), "weak_auth": len(weak_auth)})
    print(f"Debug report -> {REPORT} (dupes={len(dupes)}, weak_auth={len(weak_auth)}); event={ev.event_id}")

if __name__ == "__main__":
    main()