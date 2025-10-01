from __future__ import annotations
import json, os, random, sys, time, pathlib
from typing import Dict, Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"; AUDIT.mkdir(parents=True, exist_ok=True)
MUTL = AUDIT / "mutations.jsonl"
WIN  = AUDIT / "entropy_injection.json"

def _write_jsonl(path: pathlib.Path, rec: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def _fallback_inject(prompt: str, level: float = 0.3) -> str:
    # simple token reversal fallback
    words = prompt.split()
    out = []
    for w in words:
        out.append(w[::-1] if random.random() < level else w)
    return " ".join(out)

def _inject(prompt: str, level: float) -> str:
    try:
        # prefer existing module if present (your repo already has this)
        from flaw_first_optimizer.entropy_injector import inject_entropy  # type: ignore
        return inject_entropy(prompt, level=level)
    except Exception:
        return _fallback_inject(prompt, level=level)

def main():
    seed = int(os.getenv("ENTROPYSEED", "1337")); random.seed(seed)
    level = float(os.getenv("OMEGA_LEVEL", "0.3"))
    prompt = os.getenv("OMEGA_PROMPT", "Demonstrate deterministic entropy collapse")
    ts = time.time()

    start = {"ts": ts, "kind": "entropy_start", "payload": {"prompt": prompt, "level": level, "seed": seed}}
    _write_jsonl(MUTL, start)

    mutated = _inject(prompt, level=level)

    winner = {
        "ts": time.time(),
        "kind": "entropy_result",
        "payload": {"prompt": prompt, "mutated": mutated, "level": level, "seed": seed},
        "event_id": f"omega-{int(ts)}"
    }
    _write_jsonl(MUTL, winner)
    WIN.write_text(json.dumps(winner, ensure_ascii=False, indent=2), encoding="utf-8")
    print(mutated)
    print(f"ANCHOREVENTID={winner['event_id']}")

if __name__ == "__main__":
    main()