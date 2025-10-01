from psi_agent.orchestration.agent_router import route_task
from .prediction_parser import PredictionParser

class Synthesizer:
    def __init__(self):
        self.parser = PredictionParser()

    def process_findings(self, findings):
        """Processes raw findings using agentic LLMs."""
        processed_data = []
        for finding in findings:
            task = {
                "goal": "Analyze the following AI alignment content. Extract timelines, probabilities, benchmarks, citations, and novel techniques. Summarize the core argument.",
                "context": finding['data']['content']
            }

            # Route task (handles fallback if primary agent fails)
            result = route_task(task)

            if 'error' not in result:
                # Parse the structured output from the LLM
                intelligence = self.parser.parse(result['output'])
                intelligence['data_fp'] = finding['data_fp']
                processed_data.append(intelligence)
            else:
                logging.error(f"Synthesis failed for fingerprint {finding['data_fp']}. Error: {result['error']}")

        return processed_data