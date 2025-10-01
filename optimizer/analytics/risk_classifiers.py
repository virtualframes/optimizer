from __future__ import annotations
import csv
import json
import pathlib
import re
import time
from typing import Dict, Any, List

ROOT = pathlib.Path(__file__).resolve().parents[2]
CTX = ROOT / "context_db.jsonl"
AVAIL = ROOT / "audit" / "availability.csv"
RISKJ = ROOT / "audit" / "risk_index.jsonl"
RISKM = ROOT / "docs" / "RISK.md"
RISKJ.parent.mkdir(parents=True, exist_ok=True)
RISKM.parent.mkdir(parents=True, exist_ok=True)

KEYWORDS = {
    "prompt_injection": re.compile(
        r"(ignore previous|override|system prompt|jailbreak)", re.I
    ),
    "pii_leak": re.compile(r"(ssn|social security|credit card|passport)", re.I),
    "model_failure": re.compile(
        r"(timeout|rate.?limit|upstream fail|provider fail)", re.I
    ),
}
LATENCY_WARN_MS = 3000


def _load_jsonl(p: pathlib.Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    return [
        json.loads(l)
        for l in p.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]


def _load_availability() -> List[Dict[str, Any]]:
    if not AVAIL.exists():
        return []
    rows = []
    with AVAIL.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def classify():
    risks = []
    for rec in _load_jsonl(CTX):
        text = json.dumps(rec, ensure_ascii=False)
        labels = []
        for name, rx in KEYWORDS.items():
            if rx.search(text):
                labels.append(name)
        if rec.get("entropy", 0) > 0.7:
            labels.append("high_entropy")
        if rec.get("reroute_depth", 0) >= 4:
            labels.append("deep_reroute")
        if labels:
            risks.append(
                {
                    "ts": rec.get("ts"),
                    "fingerprint": rec.get("fingerprint"),
                    "labels": labels,
                }
            )
    # latency spikes
    for row in _load_availability():
        try:
            lat = int(row.get("latency_ms", "0"))
            ok = int(row.get("success", "0"))
        except Exception:
            continue
        if lat >= LATENCY_WARN_MS or not ok:
            risks.append(
                {
                    "ts": time.time(),
                    "fingerprint": f"avail:{row.get('task')}",
                    "labels": ["latency_spike" if lat >= LATENCY_WARN_MS else "failure"],
                }
            )
    return risks


def write_outputs(risks: List[Dict[str, Any]]):
    with RISKJ.open("w", encoding="utf-8") as f:
        for r in risks:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # simple markdown summary
    counts: Dict[str, int] = {}
    for r in risks:
        for l in r["labels"]:
            counts[l] = counts.get(l, 0) + 1
    lines = [
        "# Risk Dashboard",
        "",
        f"- items: {len(risks)}",
        "",
        "## Counts",
        "",
        "| label | count |",
        "|---|---:|",
    ]
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {k} | {v} |")
    RISKM.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {RISKJ} and {RISKM}")


def main():
    write_outputs(classify())


if __name__ == "__main__":
    main()