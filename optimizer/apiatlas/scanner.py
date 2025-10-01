import json, os, re, time, pathlib, hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import yaml

# Mutation anchor: integrate if present, else no-op
try:
    from optimizer.mutationanchor import MutationAnchor as _Anchor
except Exception:
    class _Anchor:
        def __init__(self): pass
        def record(self, kind: str, payload: Dict, parent_id: Optional[str]=None):
            return type("Ev", (), {"event_id": f"noop-{int(time.time())}"})

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "docs" / "api"
OUTDIR.mkdir(parents=True, exist_ok=True)
ENDPOINTS = OUTDIR / "endpoints.jsonl"
HIDDEN = OUTDIR / "hidden.csv"
MAP = OUTDIR / "TREE.md"

@dataclass
class Endpoint:
    file: str
    line: int
    framework: str
    method: str
    path: str
    include_in_schema: Optional[bool]
    auth_hint: Optional[str]
    hash: str

def _sha(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

PY_PATTERNS = [
    # FastAPI / Starlette
    (r'@(?:app|router)\.(get|post|put|delete|patch|options|head)\(\s*["\']([^"\']+)["\']([^)]*)\)', "fastapi"),
    # Flask
    (r'@(?:app|bp)\.route\(\s*["\']([^"\']+)["\']\s*(?:,|\))', "flask"),  # method default GET
    (r'@(?:app|bp)\.route\(\s*["\']([^"\']+)["\'][^)]*methods\s*=\s*\[([^\]]+)\]\s*\)', "flask_multi"),
    # Django urls.py
    (r'path\(\s*["\']([^"\']+)["\']\s*,', "django"),
    (r're_path\(\s*["\']([^"\']+)["\']\s*,', "django_re"),
    # DRF router
    (r'router\.register\(\s*["\']([^"\']+)["\']', "drf"),
]

JS_PATTERNS = [
    # Express.js
    (r'(?:app|router)\.(get|post|put|delete|patch|options|head)\(\s*["\'`]([^"\'`]+)["\'`]', "express"),
]

def _iter_files(cfg: dict) -> List[pathlib.Path]:
    import fnmatch
    inc = cfg.get("include", ["**/*.py"])
    exc = cfg.get("exclude", [])
    files: List[pathlib.Path] = []
    for pat in inc:
        for p in ROOT.glob(pat):
            if not p.is_file(): continue
            skip = False
            for ex in exc:
                if fnmatch.fnmatch(str(p).replace("\\","/"), ex):
                    skip = True; break
            if not skip:
                files.append(p)
    return files

def _parse_py(file: pathlib.Path, text: str) -> List[Endpoint]:
    eps: List[Endpoint] = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        for pat, kind in PY_PATTERNS:
            for m in re.finditer(pat, line):
                include_flag = None
                auth_hint = None
                path_val, methods = None, None
                if kind == "fastapi":
                    method = m.group(1).upper()
                    path_val = m.group(2)
                    args = m.group(3) or ""
                    if "include_in_schema" in args:
                        include_flag = not re.search(r'include_in_schema\s*=\s*False', args)
                    if re.search(r"Depends\(", "\n".join(lines[max(1,i-5)-1:i+5])):
                        auth_hint = "Depends(...)"
                    eps.append(Endpoint(str(file), i, "fastapi", method, path_val, include_flag, auth_hint,
                                        _sha(f"{file}:{i}:{method}:{path_val}")))
                elif kind == "flask":
                    method = "GET"
                    path_val = m.group(1)
                    eps.append(Endpoint(str(file), i, "flask", method, path_val, None, None,
                                        _sha(f"{file}:{i}:{method}:{path_val}")))
                elif kind == "flask_multi":
                    path_val = m.group(1)
                    methods = [x.strip(" '\"") for x in (m.group(2) or "").split(",")]
                    for method in methods:
                        eps.append(Endpoint(str(file), i, "flask", method.upper(), path_val, None, None,
                                            _sha(f"{file}:{i}:{method}:{path_val}")))
                elif kind in ("django","django_re"):
                    # best-effort: assume GET
                    path_val = m.group(1)
                    method = "GET"
                    eps.append(Endpoint(str(file), i, "django", method, f"/{path_val}".replace("//","/"), None, None,
                                        _sha(f"{file}:{i}:{method}:{path_val}")))
                elif kind == "drf":
                    base = m.group(1).strip("/")
                    for method in ("GET","POST","PUT","DELETE","PATCH"):
                        eps.append(Endpoint(str(file), i, "drf", method, f"/{base}".replace("//","/"), None, None,
                                            _sha(f"{file}:{i}:{method}:{base}")))
    return eps

def _parse_js(file: pathlib.Path, text: str) -> List[Endpoint]:
    eps: List[Endpoint] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for pat, kind in JS_PATTERNS:
            for m in re.finditer(pat, line):
                method = m.group(1).upper()
                path_val = m.group(2)
                eps.append(Endpoint(str(file), i, "express", method, path_val, None, None,
                                    _sha(f"{file}:{i}:{method}:{path_val}")))
    return eps

def _load_openapi(cfg: dict) -> set:
    for cand in cfg.get("openapi_candidates", []):
        p = ROOT / cand
        if p.exists():
            try:
                doc = json.loads(p.read_text(encoding="utf-8"))
                paths = set()
                for k, v in (doc.get("paths") or {}).items():
                    for m in (v or {}).keys():
                        paths.add((m.upper(), k))
                return paths
            except Exception:
                pass
    return set()

def _doc_refs() -> set:
    # light doc URL/path references from README and docs/*.md
    import re
    refs = set()
    for p in ROOT.rglob("*.md"):
        if p.parts and "docs" in p.parts and p.name in ("daily.md","BENCHMARKS.md"): continue
        txt = p.read_text(errors="ignore")
        for m in re.finditer(r'(/\w[\/\w\-\{\}:]*)', txt):
            s = m.group(1)
            if len(s) < 2 or " " in s: continue
            refs.add(s)
    return refs

def scan(cfg: dict) -> List[Endpoint]:
    eps: List[Endpoint] = []
    for f in _iter_files(cfg):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if f.suffix == ".py":
            eps.extend(_parse_py(f, text))
        elif f.suffix in (".js",".ts"):
            eps.extend(_parse_js(f, text))
    return eps

def write_outputs(eps: List[Endpoint], cfg: dict) -> Dict:
    # endpoints.jsonl
    with ENDPOINTS.open("w", encoding="utf-8") as w:
        for e in eps:
            w.write(json.dumps(asdict(e)) + "\n")

    # TREE.md (API-focused)
    grouped: Dict[str, List[Endpoint]] = {}
    for e in eps:
        key = f"{e.method} {e.path}"
        grouped.setdefault(key, []).append(e)
    lines = ["# API Map", ""]
    for key in sorted(grouped.keys()):
        lines.append(f"- `{key}`  \n  " + ", ".join({f"{e.framework}@{pathlib.Path(e.file).name}:{e.line}" for e in grouped[key]}))
    MAP.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Hidden report
    openapi_paths = _load_openapi(cfg)
    docrefs = _doc_refs() if cfg.get("hidden",{}).get("unreferenced_in_docs",True) else set()
    hidden_rows = [("method","path","reason","file","line")]
    opts = cfg.get("hidden",{})
    for e in eps:
        reasons = []
        if opts.get("include_in_schema_false") and e.include_in_schema is False:
            reasons.append("include_in_schema=False")
        if opts.get("undocumented_vs_openapi") and (e.method, e.path) not in openapi_paths:
            reasons.append("not_in_openapi")
        if docrefs and e.path not in docrefs:
            reasons.append("not_in_docs")
        # allow per-line opt out
        try:
            line_txt = pathlib.Path(e.file).read_text(encoding="utf-8", errors="ignore").splitlines()[e.line-1]
            if "@private" in line_txt:
                reasons = []
        except Exception:
            pass
        for r in reasons:
            hidden_rows.append((e.method, e.path, r, e.file, str(e.line)))
    with HIDDEN.open("w", encoding="utf-8") as w:
        for row in hidden_rows:
            w.write(",".join(row) + "\n")

    return {"count": len(eps), "hidden": len(hidden_rows)-1}

def main():
    cfg = yaml.safe_load((ROOT / "optimizer" / "apiatlas" / "config.yaml").read_text(encoding="utf-8"))
    eps = scan(cfg)
    stats = write_outputs(eps, cfg)
    ev = _Anchor().record(kind="api_map", payload={"endpoints": stats["count"], "hidden": stats["hidden"]})
    print(f"API mapped: {stats['count']} endpoints; hidden flags: {stats['hidden']}; event={ev.event_id}")

if __name__ == "__main__":
    main()