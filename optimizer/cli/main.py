import typer, json, sys
from typing import Optional

app = typer.Typer(help="Jules Mission Ω — command line")

@app.command("jules-run-agent")
def run_agent(role: str = typer.Option("editor"), prompt: str = typer.Option(..., prompt=True)):
    """
    Dispatch a role-based agent action (toy orchestrator hook).
    """
    from optimizer.selflearning.automutator import AutoMutator # placeholder: treat as fingerprint + emit event; in real impl, call agent router
    am = AutoMutator()
    am.emit_event("agent_run", {"role": role, "prompt": prompt})
    typer.echo(json.dumps({"ok": True, "role": role}))

@app.command("omega-stress")
def omega_stress(trials: int = typer.Option(5, help="Trials per task")):
    """
    Run availability stress suite and write audit/availability.csv + docs.
    """
    from optimizer.benchmark.benchmarkrunner import run_suite
    import os
    os.environ["OMEGA_TRIALS"] = str(trials)
    run_suite(trials=trials)
    typer.echo("stress complete → audit/availability.csv, docs/AVAILABILITY.md")

@app.command("jules-export-neo4j")
def export_neo4j(wipe: bool = typer.Option(False, help="Drop & re-create schema")):
    """
    Export lineage/context to Neo4j; optional full reinit.
    """
    from optimizer.memory.neo4j_anchor import Neo4jAnchor
    neo = Neo4jAnchor()
    if wipe:
        neo.reinit_schema()
    neo.bulk_export()
    typer.echo("exported to Neo4j")

# passthrough wrappers for convenience
@app.command("jules-benchmark")
def jules_benchmark(trials: int = 5):
    return omega_stress(trials)

@app.command("jules-risk-scan")
def jules_risk_scan():
    from optimizer.analytics.risk_classifiers import main as risk
    risk()
    typer.echo("risk scan done → audit/risk_index.jsonl, docs/RISK.md")

@app.command("jules-vault-update")
def jules_vault_update():
    from optimizer.dev.vault_updater import main as vault
    vault()
    typer.echo("vault updated")

@app.command("jules-auto-mutate")
def jules_auto_mutate():
    from optimizer.selflearning.automutator import main as auto_mutate
    auto_mutate()
    typer.echo("auto-mutate complete")

@app.command("jules-ingest-citations")
def jules_ingest_citations():
    from optimizer.scraper.citation_ingestor import main as ingest
    ingest()
    typer.echo("citation ingest complete")

@app.command("jules-service-graph")
def jules_service_graph():
    from optimizer.dev.service_graph import main as service_graph
    service_graph()
    typer.echo("service graph complete")

if __name__ == "__main__":
    app()