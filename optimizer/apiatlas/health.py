import os, json, time, pathlib, requests, yaml
from typing import List, Tuple
try:
    from optimizer.mutationanchor import MutationAnchor as _Anchor
except Exception:
    class _Anchor:
        def __init__(self): pass
        def record(self, kind, payload, parent_id=None):
            return type("Ev", (), {"event_id": f"noop-{int(time.time())}"})

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "api" / "health.csv"

def _load_endpoints() -> List[Tuple[str,str]]:
    p = ROOT / "docs" / "api" / "endpoints.jsonl"
    out = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            rec = json.loads(line)
            out.append((rec["method"], rec["path"]))
    return out

def main():
    cfg = yaml.safe_load((ROOT / "optimizer" / "apiatlas" / "config.yaml").read_text(encoding="utf-8"))
    base = os.getenv("API_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
    allow_external = os.getenv("ALLOW_EXTERNAL", "0") == "1"
    if not allow_external and not base.startswith("http://127.0.0.1") and not base.startswith("http://localhost"):
        print("Refusing external probing (set ALLOW_EXTERNAL=1 to override).")
        return

    endpoints = set(_load_endpoints())
    seeds = cfg.get("health_seeds", [])
    targets = sorted({("GET", s) for s in seeds if ( "{" not in s and "}" not in s )} & endpoints)

    rows = [("method","path","status","ms")]
    for m, pth in targets:
        url = f"{base}{pth}"
        t0 = time.time()
        try:
            r = requests.get(url, timeout=5)
            ms = int(1000*(time.time()-t0))
            rows.append((m, pth, str(r.status_code), str(ms)))
        except Exception as e:
            ms = int(1000*(time.time()-t0))
            rows.append((m, pth, f"ERR:{type(e).__name__}", str(ms)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join([",".join(r) for r in rows]) + "\n", encoding="utf-8")
    ev = _Anchor().record(kind="api_health", payload={"count": len(rows)-1})
    print(f"Health probed {len(rows)-1} endpoints; event={ev.event_id}")

if __name__ == "__main__":
    main()