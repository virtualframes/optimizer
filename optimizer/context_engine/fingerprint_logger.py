import hashlib, json

def fingerprint(payload: dict) -> str:
    b = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(b).hexdigest()