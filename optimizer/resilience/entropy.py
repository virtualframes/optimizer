import json, os, pathlib, random, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
AUDIT.mkdir(parents=True, exist_ok=True)
MJSONL = AUDIT / "mutations.jsonl"
EOUT   = AUDIT / "entropy_injection.json"

def _anchor(event):
    MJSONL.parent.mkdir(parents=True, exist_ok=True)
    with MJSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def _ts(): return time.time()

def _provider_fail(name, prompt):
    raise TimeoutError(f"{name} timeout")

def _provider_local(name, prompt):
    return f"[LOCAL_OK:{name}] {prompt[:160]}"

def main():
    seed = int(os.getenv("ENTROPYSEED", "1337"))
    random.seed(seed)
    prompt = os.getenv("OMEGA_PROMPT", "Demonstrate Mission Ω entropy collapse.")
    providers = [
        ("claude",  _provider_fail),
        ("gpt",     _provider_fail),
        ("gemini",  _provider_fail),
        ("mixtral", _provider_local),
    ]
    parent_id = f"entropy-{int(_ts())}-{seed}"
    _anchor({"kind":"mission_omega_start","ts":_ts(),"parent_id":parent_id,"prompt":prompt})

    for i, (name, fn) in enumerate(providers, 1):
        ev_id = f"{parent_id}-{i}-{name}"
        try:
            _anchor({"kind":"provider_attempt","ts":_ts(),"event_id":ev_id,"provider":name})
            out = fn(name, prompt)
            _anchor({"kind":"provider_success","ts":_ts(),"event_id":ev_id,"provider":name,"output":out})
            _anchor({"kind":"mission_omega_success","ts":_ts(),"parent_id":ev_id,"output":out})
            EOUT.write_text(json.dumps({
                "seed": seed, "prompt": prompt, "winner": name, "output": out, "event_id": ev_id
            }, indent=2), encoding="utf-8")
            print(out)
            print(f"ANCHOR_EVENT_ID={ev_id}")
            return
        except Exception as e:
            _anchor({"kind":"provider_failure","ts":_ts(),"event_id":ev_id,"provider":name,"error":repr(e)})
            continue

    _anchor({"kind":"mission_omega_collapse","ts":_ts(),"parent_id":parent_id})
    raise RuntimeError("All providers failed")
