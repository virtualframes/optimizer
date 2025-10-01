# central dependency factory; real modules are imported lazily to keep API thin
from functools import lru_cache

@lru_cache(maxsize=1)
def get_neo4j():
    from optimizer.memory.neo4j_anchor import Neo4jAnchor
    return Neo4jAnchor() # reads NEO4J_* env vars

@lru_cache(maxsize=1)
def get_context():
    from optimizer.context_engine.context_db import ContextDB
    return ContextDB("context_db.jsonl")

@lru_cache(maxsize=1)
def get_entropy():
    from optimizer.resilience.entropy import EntropyEngine
    return EntropyEngine()

@lru_cache(maxsize=1)
def get_fingerprinter():
    from optimizer.mutation.fingerprint import Fingerprinter
    return Fingerprinter()