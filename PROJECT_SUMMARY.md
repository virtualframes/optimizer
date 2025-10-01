# Project Summary

## Problem
Agents drift, fail under entropy, and hide lineage. We make evolution auditable and resilient.

## Solution
- **Entropy injection** with deterministic replay
- **Lineage graphs** (Mermaid + Neo4j)
- **Self-healing** auto-mutations with sandboxed tests
- **Ruthless benchmarks** exposing availability under stress

## Subsystems
- **API**: FastAPI (`optimizer/api`)
- **CLI**: Typer (`optimizer/cli`)
- **Context Engine**: JSONL store, retrieval, spacetime indexing
- **Memory**: Neo4j lineage (`optimizer/memory/neo4j_anchor.py`)
- **Self-Learning**: `optimizer/selflearning/automutator.py`
- **Benchmarks**: `optimizer/benchmark/benchmarkrunner.py`
- **Dev graphs**: `optimizer/dev/service_graph.py`, Vault updater

## CI & Scripts
- `jules-benchmark`, `jules-risk-scan`, `jules-vault-update` on push & nightly
- Optional: Neo4j export (`jules-export-neo4j`)

## Roadmap
- Peer agent adapters for head-to-head
- Coverage-driven mutation targeting
- Neo4j live dashboards