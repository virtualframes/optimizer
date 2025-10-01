import json
import datetime
import os

class JulesMemoryAnchor:
    """
    Anchors the results of a recovery or rewrite cycle into a persistent
    memory format (JSON files in the memory/ directory).
    """
    def __init__(self, memory_dir="memory"):
        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)

    def store(self, directive_id, context, result, benchmark):
        """
        Stores a memory node as a JSON file.
        """
        memory_node = {
            "id": directive_id,
            "context": context,
            "result": result,
            "benchmark": benchmark,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        file_path = os.path.join(self.memory_dir, f"{directive_id}.json")
        with open(file_path, "w") as f:
            json.dump(memory_node, f, indent=2)

        print(f"MEMORY ANCHOR: Stored memory node to {file_path}")
        return file_path