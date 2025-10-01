from psi_agent.mutation.mutation_engine import MutationEngine
from psi_agent.orchestration.pr_simulator import PRSimulator
from .flaw_detector import FlawDetector

class AutoAligner:
    def __init__(self, benchmark_report):
        self.report = benchmark_report
        self.detector = FlawDetector(benchmark_report)
        self.mutator = MutationEngine()
        self.pr_sim = PRSimulator()

    def analyze_and_mutate(self):
        """Detects flaws and proposes mutations to the architecture."""
        # Detect risks based on the ruthless benchmark report
        risks = self.detector.detect_entropy_risks()

        for risk in risks:
            if risk['type'] == "Infinite Reroute Recursion (T2)":
                # Internal reroute depth is too high
                mutation = self.mutator.generate_circuit_breaker("orchestration/fallback_router.py")
                self.propose_mutation(mutation, risk)

            elif risk['type'] == "Benchmark Overhead Collapse (T5)":
                # Internal latency is too high
                mutation = self.mutator.generate_throttle_fix("orchestration/psi_kernel.py")
                self.propose_mutation(mutation, risk)

            elif risk['type'] == "External Alignment Failure":
                # New intelligence suggests current agent (e.g., Claude) is deceptive
                mutation = self.mutator.adjust_agent_weights("orchestration/agent_router.py", risk['agent'], weight_penalty=0.5)
                self.propose_mutation(mutation, risk)

    def propose_mutation(self, mutation, risk):
        """Simulates and proposes the mutation via agentic PR."""
        rationale = f"Auto-Alignment: Mitigating {risk['type']} based on Alignment Monitor report."
        # Jules orchestrates the PR simulation and merge/fallback logic
        self.pr_sim.simulate(mutation, rationale)