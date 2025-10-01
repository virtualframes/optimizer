"""
Jules: An extremely skilled software engineer agent that learns and evolves.
"""
from .anti_slop_benchmark import AntiSlopBenchmark
from .consensus_engine import ConsensusEngine
from .patch_success_predictor import PatchSuccessPredictor
from .self_evolving_memory import SelfEvolvingMemory
from .symbolic_consistency_verifier import SymbolicConsistencyVerifier
from ..storage import neo4j_anchor as graph_db


class JulesAgent:
    def __init__(self):
        """Initializes the Jules agent with all its component modules."""
        print("Initializing Jules agent...")
        self.symbolic_verifier = SymbolicConsistencyVerifier()
        self.slop_benchmark = AntiSlopBenchmark()
        self.patch_predictor = PatchSuccessPredictor()
        self.memory = SelfEvolvingMemory()
        self.consensus_engine = ConsensusEngine()
        print("Jules agent initialized.")

    def _generate_patch(self, task: dict) -> dict:
        """
        Generates a patch for a given task, influenced by the current strategy.
        """
        strategy = self.memory.get_current_strategy()
        print(f"Generating patch using strategy: {strategy['name']} (confidence: {strategy['confidence']})")

        patch = {
            "id": f"patch_{task.get('id', 'unknown_task')}_{int(self.memory.memory.get('timestamp', 0))}",
            "type": strategy['name'],
            "description": f"A patch for task '{task.get('description', '')}' using the '{strategy['name']}' strategy.",
            "code_changes": "...",
        }
        return patch

    def work_on_task(self, task: dict):
        """
        Orchestrates the full workflow for processing a task, from analysis to evolution.

        :param task: A dictionary representing the task to be worked on.
        """
        task_id = task.get('id', 'unknown_task')
        print(f"\n--- Starting work on task: {task_id} ---")

        # 0. Anchor the initial task in the graph
        graph_db.anchor_jules_task(task_id, task.get("description", ""), task.get("concept"))

        # 1. Analyze the task input and anchor results
        print("\n[Step 1: Analyzing task input and anchoring reports]")
        slop_report = self.slop_benchmark.evaluate(task.get("description", ""))
        graph_db.anchor_benchmark_report(task_id, slop_report)
        print(f"Slop report: {slop_report}")

        if task.get("concept"):
            consistency_report = self.symbolic_verifier.verify(task["concept"])
            graph_db.anchor_symbolic_report(task_id, consistency_report)
            print(f"Symbolic consistency report: {consistency_report}")

        # 2. Generate a patch based on the current learned strategy
        print("\n[Step 2: Generating patch]")
        patch = self._generate_patch(task)
        print(f"Generated patch: {patch}")

        # 3. Predict the success of the generated patch
        print("\n[Step 3: Predicting patch success]")
        pr_data = {
            "id": task_id,
            "description": patch["description"],
            "diff_size": len(patch["code_changes"]),
        }
        prediction = self.patch_predictor.predict(pr_data)
        success_score = prediction.get("merge_likelihood", 0.0)
        print(f"Predicted success score: {success_score}")

        # Anchor the patch and its score
        graph_db.anchor_generated_patch(task_id, patch, success_score)

        # 4. Update memory with the outcome
        print("\n[Step 4: Updating self-evolving memory]")
        self.memory.update(task_id=task_id, patch=patch, score=success_score)
        print("Memory updated.")

        # 5. Trigger the evolution process and anchor the event
        print("\n[Step 5: Triggering memory evolution]")
        strategy_before = self.memory.get_current_strategy()
        self.memory.evolve()
        strategy_after = self.memory.get_current_strategy()

        if strategy_before != strategy_after:
            graph_db.anchor_memory_evolution(strategy_after)
            print("Anchored memory evolution event.")

        print(f"\n--- Finished work on task: {task_id} ---")
        return {"patch": patch, "predicted_score": success_score}