import pathlib, csv, time, json, difflib
from typing import List, Dict
import yaml

try:
    from optimizer.mutationanchor import MutationAnchor as _Anchor
except Exception:
    class _Anchor:
        def __init__(self): pass
        def record(self, kind, payload, parent_id=None):
            return type("Ev", (), {"event_id": f"noop-{int(time.time())}"})

ROOT = pathlib.Path(__file__).resolve().parents[2]
HIDDEN = ROOT / "docs" / "api" / "hidden.csv"
PLANDIR = ROOT / "docs" / "api" / "heal_plans"
PLANDIR.mkdir(parents=True, exist_ok=True)

def _load_hidden() -> List[Dict]:
    if not HIDDEN.exists(): return []
    rows = HIDDEN.read_text(encoding="utf-8").splitlines()[1:]
    out = []
    for r in rows:
        m, pth, reason, file, line = r.split(",", 4)
        out.append({"method": m, "path": pth, "reason": reason, "file": file, "line": int(line)})
    return out

def _suggest_include_in_schema(rec) -> Dict:
    f = pathlib.Path(rec["file"])
    lines = f.read_text(encoding="utf-8").splitlines()
    idx = rec["line"] - 1
    context = lines[max(0, idx-2):idx+3]
    new = []
    for ln in context:
        if "include_in_schema" in ln:
            ln = ln.replace("include_in_schema=False", "include_in_schema=True")
        new.append(ln)
    diff = "\n".join(difflib.unified_diff(context, new, fromfile="before", tofile="after", lineterm=""))
    return {"type": "include_in_schema_true", "file": rec["file"], "line": rec["line"], "diff_context": diff}

def _suggest_add_health_route() -> Dict:
    # propose a FastAPI health route stub in optimizer/services/api/ if missing
    target = ROOT / "optimizer" / "services" / "api" / "health_stub.py"
    stub = (
        "from fastapi import APIRouter\n\n"
        "router = APIRouter()\n\n"
        "@router.get('/health', include_in_schema=True)\n"
        "def health():\n"
        "    return {'ok': True}\n"
    )
    return {"type":"add_health_route_stub", "file": str(target), "content": stub}

def main():
    cfg = yaml.safe_load((ROOT / "optimizer" / "apiatlas" / "config.yaml").read_text(encoding="utf-8"))
    hidden = _load_hidden()
    plan = {"created": int(time.time()), "items": []}

    if cfg.get("heal",{}).get("suggest_include_in_schema_true", True):
        for rec in hidden:
            if rec["reason"] == "include_in_schema=False":
                plan["items"].append(_suggest_include_in_schema(rec))

    if cfg.get("heal",{}).get("suggest_add_health_route", True):
        plan["items"].append(_suggest_add_health_route())

    if cfg.get("heal",{}).get("suggest_documentation_gaps", True):
        undoc = [rec for rec in hidden if rec["reason"] in ("not_in_openapi","not_in_docs")]
        if undoc:
            plan["items"].append({
                "type":"documentation_todo",
                "count": len(undoc),
                "paths": sorted({(r["method"], r["path"]) for r in undoc})
            })

    out = PLANDIR / f"heal_plan_{plan['created']}.json"
    out.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    ev = _Anchor().record(kind="api_heal_plan", payload={"items": len(plan["items"])})
    print(f"Wrote heal plan with {len(plan['items'])} items -> {out}; event={ev.event_id}")

if __name__ == "__main__":
    main()