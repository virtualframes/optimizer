# Jules Mission Ω • Working Memory (Source of Truth for Agents + Humans)

**Last Updated**: 2025-10-01 09:33:43 UTC
**Maintainer**: diegocortes3211-design
**Repository**: virtualframes/optimizer

## Culture & Process
- **Spec-driven development**: docs-as-code; every feature starts with a spec PR and ships with docs and tests
- **Mutation anchoring**: All changes fingerprinted and stored in Neo4j lineage graph
- **Living documentation**: Auto-generated from code, version-controlled with source
- **Self-healing protocols**: Automated conflict detection and resolution

## Core Stack (must stay consistent)
- **API**: FastAPI with modular routers/services/schemas; WebSockets for live state
- **CLI**: Typer (type-hinted commands, auto-help)
- **Lineage**: Neo4j property-graph (commits, AST, actions); Cypher for impact analysis
- **Vector memory**: Postgres + PGVector for embeddings/semantic recall
- **Realtime state/cache**: Redis
- **Sandboxing**: Docker + epicbox for untrusted code
- **CI/CD**: GitHub Actions; systemd for HA in prod

## Multi-MCP & Integrations
- **Providers**: OpenAI, Anthropic, Google, Local (Ollama/etc.)
- **Routing**: capability-aware selection + fallback; log tokens/latency/cost
- **Web Search**: Bing/Google/SERP where allowed; ingest via `citation_ingestor.py`
- **Intelligent fallback**: Automatic server selection based on capabilities and load

## VM/RDP + Orchestration
- **VM providers**: Docker first; Hyper-V/VirtualBox/libvirt optional
- **RDP defaults**: TLS on; clipboard allowed; drive redirection on; session TTL 3600s
- **Container orchestration**: Resource limits, health checks, auto-restart
- **Repository cloning**: Automated deployment with dependency analysis

## Security Defaults
- **Env-only secrets**: OAuth2/JWT; rate limits; TLS everywhere
- **Sandbox all code paths**: In benchmarks/mutation replay
- **Pydantic validation**: Type-safe configuration management
- **systemd hardening**: NoNewPrivileges, ProtectSystem, resource limits

## Canonical CLI Entry Points
```bash
# Core Agentic Scripts
jules-run-agent        = "optimizer.cli.main:run"
omega-inject           = "optimizer.resilience.entropy:main"
omega-stress           = "optimizer.benchmark.availability_stress:main"
jules-index-context    = "optimizer.contextengine.spacetimeindexer:main"
jules-retrieve-context = "optimizer.contextengine.contextretriever:main"
jules-auto-mutate      = "optimizer.selflearning.automutator:main"

# Delta Pack Scripts
jules-export-neo4j     = "optimizer.memory.neo4j_export:main"
jules-service-overlay  = "optimizer.dev.servicerouteoverlay:main"
jules-risk-scan        = "optimizer.analytics.risk_classifiers:main"
jules-generate-dashboard = "optimizer.dev.dashboard_generator:main"
```

## Docs/CI Rules
- **PRs must update specs + docs**: auto-build docs on merge; fail CI if docs drift
- **Mutation tracking**: All changes logged to vault/mutations.jsonl
- **Conflict resolution**: Automated detection and resolution protocols
- **Health monitoring**: Continuous service health checks and alerting

## Recent Resolutions (PR #49)
- **Conflict Type**: pyproject.toml CLI entry points collision
- **Resolution**: Manual merge of all unique entry points
- **Status**: ✅ Resolved - unified [project.scripts] block implemented
- **Verification**: All CLI commands tested and functional