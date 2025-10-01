from fastapi import FastAPI, HTTPException
from .models import (
    FingerprintRequest, FingerprintResponse,
    EntropyInjectRequest, EntropyInjectResponse, ProviderAttempt,
    LineageTraceRequest, LineageTraceResponse, LineageNode, LineageEdge
)
from .deps import get_neo4j, get_context, get_fingerprinter, get_entropy
import time

tags = [
    {"name": "health"},
    {"name": "fingerprint"},
    {"name": "entropy"},
    {"name": "lineage"}
]

app = FastAPI(title="Jules Mission Ω API", version="1.0.0", openapi_tags=tags)

@app.get("/healthz", tags=["health"])
def healthz():
    return {"ok": True, "ts": time.time()}

@app.post("/fingerprint", response_model=FingerprintResponse, tags=["fingerprint"])
def fingerprint(req: FingerprintRequest):
    fp = get_fingerprinter().hash_any(req.payload)
    # anchor to context + graph
    get_context().append({"ts": time.time(), "kind": req.kind, "hash": fp, "meta": req.meta})
    get_neo4j().anchor_mutation(hash=fp, kind=req.kind, meta=req.meta)
    return FingerprintResponse(ts=time.time(), hash=fp, kind=req.kind, meta=req.meta)

@app.post("/entropy/inject", response_model=EntropyInjectResponse, tags=["entropy"])
def entropy_inject(req: EntropyInjectRequest):
    try:
        result = get_entropy().inject(prompt=req.prompt, level=req.level, depth=req.depth, seed=req.seed, mode=req.mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # anchor winner + attempts
    get_neo4j().anchor_entropy_event(result["run_id"], result["winner"], result["attempts"])
    attempts = [ProviderAttempt(**a) for a in result["attempts"]]
    return EntropyInjectResponse(
        ts=time.time(),
        run_id=result["run_id"],
        mutated=result["mutated"],
        winner=result["winner"],
        attempts=attempts
    )

@app.post("/lineage/trace", response_model=LineageTraceResponse, tags=["lineage"])
def lineage_trace(req: LineageTraceRequest):
    g = get_neo4j().trace(req.anchor)
    # returns {nodes:[...], edges:[...]}
    nodes = [LineageNode(**n) for n in g["nodes"]]
    edges = [LineageEdge(**e) for e in g["edges"]]
    return LineageTraceResponse(anchor=req.anchor, nodes=nodes, edges=edges)