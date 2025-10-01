import pathlib, json, csv, time

AUDIT = pathlib.Path("audit")
DOCS  = pathlib.Path("docs"); DOCS.mkdir(exist_ok=True)
VAULT = DOCS / "VAULT.md"
FEAT  = DOCS / "FEATURES.md"
BUGS  = DOCS / "BUGFIXES.md"

def parse_events():
    events = []
    for fn in ["events.jsonl","mutations.jsonl","risk_index.jsonl"]:
        p = AUDIT / fn
        if not p.exists(): continue
        for line in p.read_text().splitlines():
            try: events.append(json.loads(line))
            except: pass
    return sorted(events, key=lambda x: x.get("ts",0))

def write_vault(ev):
    lines = ["# Knowledge Vault", ""]
    for e in ev:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(e.get("ts",0)))
        lines.append(f"- {ts} — `{e.get('event','mutation')}` — {json.dumps(e)[:180]}")
    VAULT.write_text("\n".join(lines)+"\n", encoding="utf-8")

def write_features(ev):
    lines = ["# Features", "", "| when | summary |", "|---|---|"]
    for e in ev:
        if e.get("event") == "mutation_committed" and e["payload"]["plan"]["kind"] in ("feature_seed","refactor"):
            ts = time.strftime("%Y-%m-%d", time.gmtime(e["ts"]))
            lines.append(f"| {ts} | {e['payload']['plan']['targets']} ({e['payload']['plan']['kind']}) |")
    FEAT.write_text("\n".join(lines)+"\n", encoding="utf-8")

def write_bugfixes(ev):
    lines = ["# Bug Fixes", "", "| when | detail |", "|---|---|"]
    for e in ev:
        if e.get("event") == "mutation_committed" and e["payload"]["plan"]["kind"] == "bugfix":
            ts = time.strftime("%Y-%m-%d", time.gmtime(e["ts"]))
            lines.append(f"| {ts} | {e['payload']['plan']['targets']} |")
    BUGS.write_text("\n".join(lines)+"\n", encoding="utf-8")

def main():
    ev = parse_events()
    write_vault(ev); write_features(ev); write_bugfixes(ev)

if __name__ == "__main__":
    main()