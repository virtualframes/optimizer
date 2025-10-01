import json, pathlib, time, csv, re, subprocess

AUDIT = pathlib.Path("audit"); AUDIT.mkdir(exist_ok=True)
RISK  = AUDIT / "risk_index.jsonl"
DOC   = pathlib.Path("docs/RISK.md")

def journal(unit="self_evolving_agent.service", since="2 hours ago"):
    # out = subprocess.run(["journalctl","-u",unit,"--since",since,"-o","cat","--no-pager"], capture_output=True, text=True).stdout
    # return out.splitlines()
    return []

def analyze():
    risks = []
    # availability
    try:
        with (pathlib.Path("audit/availability.csv")).open() as f:
            rows = list(csv.DictReader(f))
        bad = [r for r in rows if r["strategy"].startswith("score") and float(r["strategy"].split("=")[1]) < 0.6]
        if bad: risks.append({"type":"PerfDegradation","detail":bad})
    except FileNotFoundError:
        pass
    # logs
    lines = journal()
    if sum(1 for l in lines if "Starting Self-Evolving AI Agent" in l) >= 2:
        risks.append({"type":"CrashLoop"})
    if any(re.search(r"prompt injection|API key", l, re.I) for l in lines):
        risks.append({"type":"SecFinding"})
    write(risks); write_doc(risks)

def write(items):
    with RISK.open("a", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps({"ts": time.time(), **it})+"\n")

def write_doc(items):
    lines = ["# Risk Dashboard", ""]
    for it in items:
        lines.append(f"- **{it['type']}** — {json.dumps(it, ensure_ascii=False)[:200]}")
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main(): analyze()
if __name__ == "__main__": main()