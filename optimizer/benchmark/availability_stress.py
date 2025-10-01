import csv, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"; AUDIT.mkdir(parents=True, exist_ok=True)
CSV   = AUDIT / "availability.csv"
OUTMD = ROOT / "docs" / "AVAILABILITY.md"; OUTMD.parent.mkdir(parents=True, exist_ok=True)

def _fail(_): raise TimeoutError("upstream timeout")
def _ok(p):   return "ok:" + p[:24]

TASKS = [("ping","ping"),("health","healthcheck"),("echo","echo hello")]
STRATS = {
    "baseline": [_fail],
    "mission_omega": [_fail, _fail, _ok],
}

def run():
    rows = [("strategy","task","latency_ms","success","output")]
    for sname, chain in STRATS.items():
        for tname, prompt in TASKS:
            t0 = time.time()
            out, success = "ERR", False
            for fn in chain:
                try:
                    out = fn(prompt)
                    success = out.startswith("ok:")
                    break
                except Exception:
                    continue
            dt = int(1000*(time.time()-t0))
            rows.append((sname, tname, dt, int(success), out))
    with CSV.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    # quick human page
    total = len(rows)-1
    succ  = sum(int(r[3]) for r in rows[1:])
    OUTMD.write_text(
        "# Availability (mini-bench)\n\n"
        f"- samples: {total}\n"
        f"- success: {succ}/{total}\n"
        f"- file: `audit/availability.csv`\n", encoding="utf-8"
    )
    print("WROTE", CSV, "and", OUTMD)

def main(): run()
