from .jules_agent import JulesAgent
from .benchmark_alignment import benchmark_alignment
from .mutate_prompt import mutate_prompt
from .mutation_anchor import fingerprint_mutation
from .neo4j_mapper import anchor_lineage


def anchor_event(event_type, data):
    """Helper to anchor events to the lineage graph."""
    fingerprint = data.get("fingerprint")
    if not fingerprint or "hash" not in fingerprint:
        fingerprint = {"hash": "unknown_fingerprint"}

    response_info = {
        "prompt": data.get("prompt"),
        "response": data.get("response"),
        "score": data.get("score")
    }

    anchor_lineage(fingerprint, f"{event_type}: {response_info}")


class JulesSelfEvolver:
    def __init__(self, agent: JulesAgent, benchmark_threshold=0.75, max_depth=5):
        self.agent = agent
        self.threshold = benchmark_threshold
        self.max_depth = max_depth
        self.history = []

    def evolve(self, prompt: str, depth=0):
        # Prevent infinite recursion
        if depth >= self.max_depth:
            anchor_event("SelfLearnFailure", {"reason": "Max evolution depth reached"})
            return "Evolution failed: Max depth reached"

        # Generate a structured fingerprint for the prompt
        fingerprint = fingerprint_mutation(prompt)

        # Use the agent's core routing logic to get a response
        response = self.agent.route(prompt)

        # Benchmark the response for alignment
        score = benchmark_alignment(response)

        if score < self.threshold:
            # If alignment is poor, mutate the prompt
            mutated_prompt = mutate_prompt(prompt)

            # Log the evolution attempt
            self.history.append({
                "original": prompt,
                "mutated": mutated_prompt,
                "response": response,
                "score": score,
                "fingerprint": fingerprint,
                "depth": depth
            })

            # Recursively call evolve with the new, mutated prompt and increased depth
            return self.evolve(mutated_prompt, depth + 1)

        # If alignment is successful, anchor the success event and return
        anchor_event("SelfLearnSuccess", {
            "prompt": prompt,
            "response": response,
            "score": score,
            "fingerprint": fingerprint
        })
        return response