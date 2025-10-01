# Jules Mission Ω — Self-Evolving Agent Stack

Mutation-aware agents with entropy injection, lineage graphs, and ruthless benchmarking.

**Key modules:** `optimizer/api`, `optimizer/cli`, `optimizer/context_engine`, `optimizer/memory`, `optimizer/selflearning`, `optimizer/benchmark`, `optimizer/dev`.

## Quickstart

```bash
# 1) install
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev,neo4j]

# 2) run API
uvicorn optimizer.api.main:app --host 0.0.0.0 --port 8080

# 3) run CLI
jules-benchmark
jules-risk-scan
jules-vault-update
```
## Features

*   Entropy collapse injector (omega-inject)
*   Availability benchmarks (jules-benchmark)
*   Lineage + service graphs (Mermaid)
*   Neo4j lineage export (jules-export-neo4j)
*   Auto-mutation sandbox (jules-auto-mutate)

## Architecture

*   **API**: FastAPI (`optimizer/api`)
*   **CLI**: Typer (`optimizer/cli`)
*   **Context Engine**: JSONL append-only, retrieval tools
*   **Memory**: Neo4j graph lineage
*   **Self-learning**: AST transforms + sandbox validation
*   **Benchmarking**: Stress + availability scoring

## Development

```bash
ruff check .
pytest -q
mypy optimizer
```

## Contributing

See CONTRIBUTING.md and PROJECT_SUMMARY.md.

## Security

Never commit secrets. Report vulnerabilities via Security Policy.

## License

Apache-2.0