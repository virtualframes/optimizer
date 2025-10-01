from __future__ import annotations
import os
import json
import time
import random
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = AUDIT_DIR / "entropy_injection.json"

def main():
    """
    Simulates entropy injection based on environment variables.
    This function mimics a multi-provider fallback scenario.
    """
    depth = int(os.getenv("OMEGA_DEPTH", "3"))
    timeout_ms = int(os.getenv("OMEGA_TIMEOUT_MS", "100"))
    quorum = int(os.getenv("OMEGA_QUORUM", "1"))
    mode = os.getenv("OMEGA_MODE", "prefix")
    prompt = os.getenv("OMEGA_PROMPT", "default prompt")
    seed = int(os.getenv("ENTROPYSEED", time.time()))

    random.seed(seed)

    results = {
        "timestamp": time.time(),
        "seed": seed,
        "config": {
            "depth": depth,
            "timeout_ms": timeout_ms,
            "quorum": quorum,
            "mode": mode,
            "prompt": prompt,
        },
        "trace": [],
    }

    providers = [f"provider_{i}" for i in range(depth)]
    random.shuffle(providers)

    successes = 0
    for provider in providers:
        latency = random.randint(10, timeout_ms * 2)
        is_success = latency <= timeout_ms and random.random() > 0.2 # 80% success rate if within timeout

        if is_success:
            successes += 1
            response = f"[LOCAL_OK:{provider}] response to '{prompt}'"
        else:
            response = f"[FAIL:{provider}] timeout or error"

        results["trace"].append({
            "provider": provider,
            "latency_ms": latency,
            "success": is_success,
            "response": response,
        })

        if successes >= quorum:
            break

    with OUT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(results, ensure_ascii=False) + "\n")

    print(f"Entropy injection simulation complete. Results logged to {OUT_FILE}")
    print(json.dumps(results, indent=2))