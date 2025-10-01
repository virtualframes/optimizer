class PolicyEvaluator:
    def evaluate(self, pr: dict) -> dict:
        """
        Simulates evaluating a pull request against OPA policies.
        In a real-world use case, this would involve a call to an OPA server.
        """
        print(f"PolicyEvaluator: Evaluating PR: {pr['url']}")
        # For simulation purposes, we'll assume the policy passes.
        return {
            "allow": True,
            "reason": "Policy check passed: PR is from an automated agent."
        }