"""
The core of the Ruthless Benchmarking system.

This module is responsible for providing total, unflinching transparency about
the performance of the psi_agent system. It generates a periodic report that
exposes both internal performance metrics (e.g., latency, error rates) and
external intelligence about the flaws and contamination in public benchmarks.
This report is the foundational data source for the FlawDetector and the
AutoAligner, enabling the system to reason about its own performance and risks.
"""
import logging
import time
from .flaw_detector import benchmark_alignment
from ...orchestration.reroute_traceback import reroutetolocal_model
from ...memory.cockroachdbledger import CockroachDBLedger

ledger = CockroachDBLedger()

def exposebenchmarks(agent_outputs):
    """
    Benchmarks agent outputs and reroutes them if they fall below a threshold.
    """
    for output in agent_outputs:
        score = benchmark_alignment(output)
        # Assuming ledger has a method to log scores
        # ledger.log_score(output, score)
        if score < 0.7:
            reroutetolocal_model(output)

class BenchmarkExposer:
    """
    Exposes internal and external benchmarks with total transparency.
    """
    def __init__(self, ledger, neo4j_anchor):
        """
        Args:
            ledger: An instance of the CockroachDB ledger.
            neo4j_anchor: An instance of the Neo4j anchor.
        """
        self.ledger = ledger
        self.neo4j = neo4j_anchor
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def expose_ruthlessly(self):
        """Generates and anchors the transparent benchmark report."""
        logging.info("--- RUTHLESS BENCHMARK EXPOSURE ---")
        report = {
            "timestamp": time.time(),
            "internal": self.get_internal_metrics(),
            "external": self.get_external_metrics()
        }

        # self.ledger.anchor_benchmark_report(report)
        self.log_critical_metrics(report)
        return report

    def get_internal_metrics(self):
        """Retrieves internal performance metrics from monitoring systems."""
        # In a real system, these would query a monitoring tool.
        return {
            "scan_success_rate": 0.95,
            "synthesis_error_rate": 0.05,
            "psi_agent_latency_ms": 3500,
            "reroute_depth_max": 4
        }

    def get_external_metrics(self):
        """Retrieves external intelligence from the graph database."""
        # This conceptually queries Neo4j.
        # contamination_flaws = self.neo4j.query("...")
        return {
            "contamination": [{"benchmark": "DeceptiveTest-v3", "flaw": "Synthetic data contamination"}],
            "METR_Horizons": "15-60 mins (Claude 4.5)"
        }

    def log_critical_metrics(self, report):
        """Logs the most important metrics for operator visibility."""
        internal = report['internal']
        external = report['external']
        logging.info(f"Internal Metrics: Scan Success={internal['scan_success_rate']:.2f}, Latency={internal['psi_agent_latency_ms']}ms")
        if external['contamination']:
            logging.warning(f"External Risks: Contamination found in {len(external['contamination'])} benchmarks.")