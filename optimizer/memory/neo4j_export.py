from __future__ import annotations
import argparse
import json
import os
import pathlib
import sys
from typing import Any, Dict, Iterable

ROOT = pathlib.Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "mutations.jsonl"
CTX = ROOT / "context_db.jsonl"


def _lines(p: pathlib.Path) -> Iterable[Dict[str, Any]]:
    if not p.exists():
        return []
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            try:
                yield json.loads(l)
            except Exception:
                continue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--uri", default=os.getenv("NEO4JURI", "bolt://localhost:7687")
    )
    ap.add_argument("--user", default=os.getenv("NEO4JUSER", "neo4j"))
    ap.add_argument("--password", default=os.getenv("NEO4JPASSWORD", "neo4j"))
    ap.add_argument(
        "--wipe", action="store_true", help="wipe previous Jules nodes/rels"
    )
    args = ap.parse_args()
    try:
        from neo4j import GraphDatabase  # type: ignore
    except Exception:
        print("neo4j driver not installed. pip install neo4j", file=sys.stderr)
        sys.exit(2)
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    muts = list(_lines(AUDIT))
    ctxs = list(_lines(CTX))
    with driver.session() as s:
        if args.wipe:
            s.run("MATCH (n:Jules) DETACH DELETE n")
        # export contexts
        for c in ctxs:
            s.run(
                """
MERGE (x:Jules:Context {fingerprint:$fp})
ON CREATE SET
    x.ts=$ts,
    x.source=$source,
    x.tags=$tags,
    x.entropy=$entropy,
    x.depth=$depth,
    x.payload=$payload
""",
                {
                    "fp": c.get("fingerprint") or c.get("payload", "") and c["payload"],
                    "ts": c.get("ts"),
                    "source": c.get("source", "context"),
                    "tags": c.get("tags", []),
                    "entropy": c.get("entropy", 0.0),
                    "depth": c.get("reroute_depth", 0),
                    "payload": c.get("payload", {}),
                },
            )
        # export mutations + lineage
        for m in muts:
            eid = m.get("event_id") or m.get("eventid")
            pid = m.get("parent_id") or m.get("parentid")
            if not eid:
                continue
            s.run(
                """
MERGE (e:Jules:Mutation {event_id:$eid})
ON CREATE SET
    e.ts=$ts,
    e.kind=$kind,
    e.payload=$payload,
    e.payloadhash=$hash
""",
                {
                    "eid": eid,
                    "ts": m.get("ts"),
                    "kind": m.get("kind"),
                    "payload": m.get("payload"),
                    "hash": m.get("payload_hash") or m.get("payloadhash"),
                },
            )
            if pid:
                s.run(
                    """
MERGE (p:Jules:Mutation {event_id:$pid})
MERGE (p)-[:CAUSES]->(e:Jules:Mutation {event_id:$eid})
""",
                    {"pid": pid, "eid": eid},
                )
    driver.close()
    print(f"exported {len(muts)} mutations, {len(ctxs)} context items to Neo4j")