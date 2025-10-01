from ..adapters.claude_adapter import ClaudeAdapter
from ..adapters.gemini_adapter import GeminiAdapter
from ..workflows import selfhealworkflow, validation_workflow
from ..storage.neo4j_anchor import anchor_event

class SentinelAgent:
    def __init__(self):
        self.claude = ClaudeAdapter()
        self.gemini = GeminiAdapter()

    def monitor(self, signal: dict):
        if signal["type"] == "failure":
            diagnosis = self.claude.debug_traceback(signal["traceback"])
            patch = self.gemini.suggest_patch(diagnosis)
            selfhealworkflow.run(diagnosis, patch)
            anchor_event(signal, diagnosis=diagnosis, patch=patch)

        elif signal["type"] == "validation":
            result = validation_workflow.run(signal["target"])
            anchor_event(signal, diagnosis=str(result))