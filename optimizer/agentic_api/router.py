from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
import time, os, random

app = FastAPI(title="Agentic API (dev)")

class Payload(BaseModel):
    data: dict

@app.get("/reroute/depth")
def reroute_depth() -> dict:
    return {"depth": int(os.getenv("OMEGA_DEPTH","3"))}

@app.post("/fingerprint")
def fingerprint(p: Payload) -> dict:
    import hashlib, json
    s = json.dumps(p.data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return {"fingerprint": hashlib.sha256(s).hexdigest(), "ts": time.time()}

@app.post("/entropy/inject")
def entropy_inject(p: Payload) -> dict:
    from optimizer.resilience.entropy import _inject  # reuse
    prompt = p.data.get("prompt","")
    level = float(os.getenv("OMEGA_LEVEL","0.3"))
    random.seed(int(os.getenv("ENTROPYSEED","1337")))
    return {"mutated": _inject(prompt, level), "level": level}

class Quorum(BaseModel):
    outputs: list[str]
    prefix: str = "ok:"
    threshold: int = 1

@app.post("/quorum/validate")
def quorum_validate(q: Quorum) -> dict:
    hits = sum(1 for o in q.outputs if o.startswith(q.prefix))
    return {"pass": hits >= q.threshold, "hits": hits, "threshold": q.threshold}