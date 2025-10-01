from __future__ import annotations
import hashlib, json

def fingerprint(payload) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()