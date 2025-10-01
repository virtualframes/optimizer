import json
import os
import time
from collections import Counter

class SelfEvolvingMemory:
    def __init__(self, path="/opt/jules/memory.json"):
        """Initializes the SelfEvolvingMemory."""
        self.path = path
        self.cache = {}
        self.current_strategy = {"name": "default", "confidence": 0.5}
        self.load()

    def load(self):
        """Loads the memory cache and strategy from a file."""
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    data = json.load(f)
                    self.cache = data.get("cache", {})
                    self.current_strategy = data.get("strategy", {"name": "default", "confidence": 0.5})
            except (json.JSONDecodeError, IOError):
                self.cache = {}
                self.current_strategy = {"name": "default", "confidence": 0.5}
        else:
            self.cache = {}
            self.current_strategy = {"name": "default", "confidence": 0.5}

    def update(self, task_id: str, patch: dict, score: float):
        """
        Updates the memory with the outcome of a task.

        :param task_id: The ID of the task.
        :param patch: The patch that was generated, should contain a 'type' key.
        :param score: The success score of the patch.
        """
        self.cache[task_id] = {
            "patch": patch,
            "score": score,
            "timestamp": time.time()
        }
        self.persist()

    def evolve(self):
        """
        Evolves the agent's patching strategy based on historical data.
        It identifies the most successful 'type' of patch and updates the strategy.
        """
        print("Evolving based on past performance...")

        if len(self.cache) < 10: # Don't evolve without enough data
            print("Not enough data to evolve. Need at least 10 entries.")
            return

        high_score_patches = [
            v["patch"] for v in self.cache.values() if v.get("score", 0) > 0.8
        ]

        if not high_score_patches:
            print("No high-scoring patches found to learn from.")
            return

        # Assumes patches have a 'type' for strategy analysis
        patch_types = [p.get("type", "unknown") for p in high_score_patches]
        most_common_type = Counter(patch_types).most_common(1)[0]

        new_strategy_name = most_common_type[0]
        confidence = round(most_common_type[1] / len(high_score_patches), 2)

        print(f"New winning strategy identified: '{new_strategy_name}' with confidence {confidence}.")
        self.current_strategy = {"name": new_strategy_name, "confidence": confidence}
        self.persist()

    def get_current_strategy(self) -> dict:
        """Returns the current best strategy."""
        return self.current_strategy

    def persist(self):
        """Persists the memory cache and strategy to a file."""
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.path, 'w') as f:
            data_to_persist = {
                "cache": self.cache,
                "strategy": self.current_strategy,
            }
            json.dump(data_to_persist, f, indent=2)