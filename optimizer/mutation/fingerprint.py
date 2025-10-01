import hashlib
import json
from typing import Any

class Fingerprinter:
    def hash_any(self, payload: Any) -> str:
        """Creates a SHA256 hash of any JSON-serializable payload."""
        payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(payload_bytes).hexdigest()