from __future__ import annotations
import argparse, json, requests
from optimizer.context_engine.context_db import append_item

def try_fetch(url: str) -> str | None:
    try:
        r = requests.get(url, headers={"User-Agent":"JulesAPIFinder/1.0"}, timeout=20)
        if r.ok:
            return r.text
    except Exception:
        return None
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="Base URL, e.g. https://example.com")
    args = ap.parse_args()
    findings = []
    for path in ("/openapi.json","/.well-known/agent.json","/swagger.json","/api","/docs"):
        txt = try_fetch(args.target.rstrip("/") + path)
        if txt:
            findings.append({"path": path, "size": len(txt)})
            append_item("api-probe", {"target": args.target, "path": path, "size": len(txt)}, ["api","probe"])
    print(json.dumps({"target": args.target, "hits": findings}, ensure_ascii=False))