from __future__ import annotations
import csv, os, random, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"; AUDIT.mkdir(parents=True, exist_ok=True)
OUT = AUDIT / "availability.csv"

TASKS = [("ping","ping"), ("healthcheck","healthcheck"), ("echo","echo hello")]

def run_once(task: str, depth: int) -> tuple[int, bool, str]:
    t0 = time.time()
    # Simulate provider chain failures except final "local"
    providers = ["claude","gpt","gemini","local"][:max(1, depth)]
    for p in providers:
        time.sleep(0.02)  # tiny latency
        if p != "local":
            continue
        # local success
        out = f"ok:{task}"
        dt = int((time.time()-t0)*1000)
        return dt, True, out
    dt = int((time.time()-t0)*1000)
    return dt, False, "ERR: all providers failed"

def main():
    random.seed(int(os.getenv("ENTROPYSEED","1337")))
    depth = int(os.getenv("OMEGA_DEPTH","3"))
    trials = int(os.getenv("OMEGA_TRIALS","3"))
    rows = [("strategy","task","latency_ms","success","output")]
    for name in ("baseline","missionomega"):
        for task, prompt in TASKS:
            for _ in range(trials):
                d = 1 if name=="baseline" else depth
                dt, ok, out = run_once(task, d)
                rows.append((name, task, dt, int(ok), out))
    with OUT.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print(f"WROTE {OUT}")

if __name__ == "__main__":
    main()