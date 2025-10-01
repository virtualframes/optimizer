from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from optimizer.context_engine.fingerprint_logger import fingerprint

router = APIRouter(prefix="", tags=["agentic"])

class FingerprintIn(BaseModel):
    payload: dict

@router.post("/fingerprint")
def post_fingerprint(body: FingerprintIn):
    return {"fingerprint": fingerprint(body.payload)}

class EntropyIn(BaseModel):
    prompt: str
    depth: int = 3
    quorum: int = 1

@router.post("/entropy/inject")
def post_entropy(body: EntropyIn):
    # call your existing omega injector via import
    from optimizer.resilience import entropy as inj
    import os
    os.environ["OMEGA_DEPTH"] = str(body.depth)
    os.environ["OMEGA_QUORUM"] = str(body.quorum)
    os.environ["OMEGA_MODE"] = "prefix"
    os.environ["OMEGA_PROMPT"] = body.prompt
    inj.main()
    return {"ok": True}

@router.get("/reroute/depth")
def get_reroute_depth():
    import os
    return {"depth": int(os.getenv("OMEGA_DEPTH","3"))}

class QuorumIn(BaseModel):
    output: str
    threshold: int = 1

@router.post("/quorum/validate")
def post_quorum(body: QuorumIn):
    from optimizer.resilience.quorum import prefix_validator, validate
    res = validate(body.output, body.threshold, [prefix_validator("[LOCAL_OK:")])
    return {"passed": res.passed, "witnesses": res.witnesses, "details": res.details}