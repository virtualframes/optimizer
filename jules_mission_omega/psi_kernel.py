import hashlib
import datetime

# Placeholder for a global vendor registry
VENDOR_REGISTRY = {
    "Claude": {"state": "ACTIVE", "circuit_open": False},
    "GPT": {"state": "ACTIVE", "circuit_open": False},
    "Gemini": {"state": "ACTIVE", "circuit_open": False},
}

def get_timestamp():
    """Returns a string timestamp."""
    return datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def hash_prompt(prompt: str) -> str:
    """Generates a SHA256 hash of the prompt."""
    return hashlib.sha256(prompt.encode()).hexdigest()

def detect_vendor_failure(prompt: str):
    """Simulates the detection of a multi-vendor failure."""
    print("INFO: Detecting vendor failure...")
    vendors = {
        "Claude": {"latency": 30000, "error": 503, "status": "TIMEOUT"},
        "GPT": {"latency": 28000, "error": 504, "status": "TIMEOUT"},
        "Gemini": {"latency": 32000, "error": 502, "status": "TIMEOUT"}
    }
    fingerprint = hash_prompt(prompt)
    incident_id = f"VENDOR_BLACKOUT_{get_timestamp()}"
    print(f"INFO: Failure detected. Incident ID: {incident_id}, Fingerprint: {fingerprint}")
    return {
        "vendors": vendors,
        "fingerprint": fingerprint,
        "incident_id": incident_id
    }

def activate_circuit_breaker():
    """Activates the circuit breaker for all vendors."""
    print("INFO: Activating circuit breaker...")
    for vendor in ["Claude", "GPT", "Gemini"]:
        if vendor in VENDOR_REGISTRY:
            VENDOR_REGISTRY[vendor]["state"] = "DEGRADED"
            VENDOR_REGISTRY[vendor]["circuit_open"] = True
    print(f"INFO: Circuit breaker is OPEN. Vendor states: {VENDOR_REGISTRY}")