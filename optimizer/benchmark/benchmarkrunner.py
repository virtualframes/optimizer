import time, csv, statistics as stats, pathlib, subprocess, json, random

AUDIT = pathlib.Path("audit"); AUDIT.mkdir(exist_ok=True)
CSV   = AUDIT / "availability.csv"
DOC   = pathlib.Path("docs/AVAILABILITY.md")

TASKS = {
  "echo": {"runner": lambda: _timed(lambda: "ok"), "slo_ms": 50},
  "cpu_spin": {"runner": lambda: _timed(cpu_spin), "slo_ms": 120},
  "mem_alloc": {"runner": lambda: _timed(mem_alloc), "slo_ms": 150},
  "disk_io": {"runner": lambda: _timed(disk_io), "slo_ms": 200},
}

def _timed(fn):
    t0 = time.perf_counter()
    out = fn()
    dt = int((time.perf_counter()-t0)*1000)
    return {"ok": True, "lat_ms": dt, "out": str(out)}

def cpu_spin(n=2_000_00):
    s=0
    for i in range(n): s += i*i
    return s

def mem_alloc(n=5_0000):
    x = [i for i in range(n)]
    return len(x)

def disk_io():
    p = pathlib.Path("._bench.tmp")
    p.write_text("x"*4096); _ = p.read_text(); p.unlink(missing_ok=True); return "ok"

def availability(lat_med, slo_ms, success_rate):
    penalty = max(0, (lat_med - slo_ms) / slo_ms)
    return max(0.0, min(1.0, success_rate * (1 - penalty)))

def run_suite(trials=5):
    rows = []
    for task, meta in TASKS.items():
        lats, succ = [], 0
        for _ in range(trials):
            r = meta["runner"]()
            lats.append(r["lat_ms"])
            succ += 1 if r["ok"] else 0
            rows.append({"task": task, "latency_ms": r["lat_ms"], "success": r["ok"], "strategy": "local"})
        sr = succ / trials
        lat_med = int(stats.median(lats))
        score = availability(lat_med, meta["slo_ms"], sr)
        rows.append({"task": task, "latency_ms": lat_med, "success": f"{succ}/{trials}", "strategy": f"score={score:.3f}"})
    write_csv(rows); write_doc(rows)

def write_csv(rows):
    fields = ["strategy","task","latency_ms","success","out"]
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            if "out" not in r: r["out"] = ""
            w.writerow(r)

def write_doc(rows):
    by_task = {}
    for r in rows:
        if r["strategy"].startswith("score"):
            by_task[r["task"]] = r["strategy"].split("=",1)[1]
    lines = ["# Availability (Stress)", ""]
    for t, s in by_task.items():
        lines.append(f"- **{t}** → score {s}")
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    run_suite(trials=int(pathlib.os.getenv("OMEGA_TRIALS","5")))

if __name__ == "__main__":
    main()