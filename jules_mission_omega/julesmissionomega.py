from jules_mission_omega.psi_kernel import detect_vendor_failure, activate_circuit_breaker
from jules_mission_omega.hf_model_router import load_local_model
from jules_mission_omega.dry_run_harness import run_heuristics
from jules_mission_omega.reroute_traceback import log_failure
from jules_mission_omega.mutation_anchor import anchor_event
from jules_mission_omega.benchmark_runner import benchmark_degraded_response

class JulesMissionOmega:
    def __init__(self, prompt: str):
        """Initializes the mission with a given prompt."""
        print("INFO: Jules Mission Ω initialized.")
        self.prompt = prompt
        self.incident_id = None
        self.fingerprint = None
        self.response = None

    def execute(self):
        """Executes the full failure simulation and recovery stack."""
        print("\n" + "="*50)
        print("========= EXECUTING JULES MISSION OMEGA =========")
        print("="*50 + "\n")

        # Step 1: Detect and log the failure
        failure_details = detect_vendor_failure(self.prompt)
        self.fingerprint = failure_details["fingerprint"]
        self.incident_id = failure_details["incident_id"]
        log_failure(failure_details)

        # Step 2: Activate circuit breaker
        activate_circuit_breaker()

        # Step 3: Failover to local model and run heuristics
        local_model = load_local_model("mixtral-8x7b-instruct-v0.1")
        heuristics = run_heuristics(self.prompt)

        # Step 4: Generate deterministic response if heuristics pass
        if heuristics["quorum_passed"]:
            print("INFO: Heuristic quorum passed. Generating deterministic response.")
            self.response = {
                "text": local_model.generate(self.prompt),
                "confidence": heuristics["confidence"],
                "method": "local_model_with_heuristic_quorum",
                "deterministic": True,
                "seed": 42,
                "entropy_budget": 0.0
            }
        else:
            print("ERROR: Heuristic quorum failed. Cannot generate response.")
            self.response = {"text": "Error: Could not generate a reliable response.", "confidence": 0.0}

        # Step 5: Anchor the entire event and benchmark the outcome
        anchor_event(self.incident_id, self.fingerprint, self.response)
        benchmark_degraded_response(self.response)

        print("\n" + "="*50)
        print("============== MISSION OMEGA COMPLETE ==============")
        print("="*50 + "\n")

        return self.response