from __future__ import annotations
from typing import Dict, List
import os, time
from neo4j import GraphDatabase

class Neo4jAnchor:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        pwd = os.getenv("NEO4J_PASSWORD", "password")
        self._driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        self._driver.close()

    def reinit_schema(self):
        q = """
        CREATE CONSTRAINT IF NOT EXISTS FOR (f:Fingerprint) REQUIRE f.hash IS UNIQUE;
        CREATE CONSTRAINT IF NOT EXISTS FOR (m:Mutation) REQUIRE m.id IS UNIQUE;
        CREATE CONSTRAINT IF NOT EXISTS FOR (e:EntropyRun) REQUIRE e.run_id IS UNIQUE;
        """
        with self._driver.session() as s:
            s.run(q)


    def anchor_mutation(self, hash: str, kind: str, meta: Dict):
        q = """
        MERGE (f:Fingerprint {hash:$hash}) ON CREATE SET f.ts=$ts
        MERGE (m:Mutation {id:$mid}) ON CREATE SET m.kind=$kind, m.ts=$ts, m.meta=$meta
        MERGE (m)-[:ANCHORS]->(f)
        """
        with self._driver.session() as s:
            s.run(q, hash=hash, mid=f"MUT_{hash[:10]}", kind=kind, meta=meta, ts=time.time())


    def anchor_entropy_event(self, run_id: str, winner: str, attempts: List[Dict]):
        q = """
        MERGE (r:EntropyRun {run_id:$run_id}) ON CREATE SET r.ts=$ts, r.winner=$winner
        WITH r
        UNWIND $attempts AS a
        MERGE (s:Source {path:a.provider, type:'provider'})
        MERGE (r)-[:TRIED {ok:a.ok, latency_ms:a.latency_ms}]->(s)
        """
        with self._driver.session() as s:
            s.run(q, run_id=run_id, ts=time.time(), winner=winner, attempts=attempts)


    def trace(self, anchor: str) -> Dict:
        q = """
        MATCH (f:Fingerprint {hash:$anchor})<-[:ANCHORS]-(m:Mutation)
        OPTIONAL MATCH (m)-[t:TOUCHED]->(mod:Module)
        RETURN m,f, collect({id:mod.path, rel:type(t)}) AS mods
        """
        nodes, edges = [], []
        with self._driver.session() as s:
            rec = s.run(q, anchor=anchor).single()
        if not rec:
            return {"nodes": [], "edges": []}
        m = rec["m"]; f = rec["f"]
        nodes += [
            {"id": m["id"], "label": m["id"], "kind":"Mutation", "ts": m.get("ts",0.0)},
            {"id": f["hash"], "label": f["hash"][:8], "kind":"Fingerprint", "ts": f.get("ts",0.0)}
        ]
        edges.append({"src": m["id"], "dst": f["hash"], "rel": "ANCHORS"})
        for mod in rec["mods"]:
            nodes.append({"id": mod["id"], "label": mod["id"], "kind": "Module", "ts": 0})
            edges.append({"src": m["id"], "dst": mod["id"], "rel": "TOUCHED"})
        return {"nodes": nodes, "edges": edges}

    # Optional bulk export hook for CLI
    def bulk_export(self):
        # Placeholder: pull recent audit events and upsert
        print("Mock bulk_export: In a real implementation, this would export audit data to Neo4j.")
        pass