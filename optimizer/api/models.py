from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import time

# /fingerprint
class FingerprintRequest(BaseModel):
    payload: Any
    kind: str = Field("generic", description="mutation/event/category")
    meta: Dict[str, Any] = {}

class FingerprintResponse(BaseModel):
    ts: float
    hash: str
    kind: str
    meta: Dict[str, Any]

# /entropy/inject
class EntropyInjectRequest(BaseModel):
    prompt: str
    level: float = Field(0.3, ge=0, le=1)
    depth: int = Field(1, ge=1, le=8)
    seed: Optional[int] = None
    mode: str = Field("prefix", description="validator mode (prefix/json)")

class ProviderAttempt(BaseModel):
    provider: str
    ok: bool
    latency_ms: int
    note: Optional[str] = None

class EntropyInjectResponse(BaseModel):
    ts: float
    run_id: str
    mutated: str
    winner: str
    attempts: List[ProviderAttempt]

# /lineage/trace
class LineageTraceRequest(BaseModel):
    anchor: str = Field(..., description="hash/anchor id")

class LineageNode(BaseModel):
    id: str
    label: str
    kind: str
    ts: float

class LineageEdge(BaseModel):
    src: str
    dst: str
    rel: str

class LineageTraceResponse(BaseModel):
    anchor: str
    nodes: List[LineageNode]
    edges: List[LineageEdge]