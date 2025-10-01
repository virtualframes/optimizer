def score_agent(response, original_prompt):
    # Simple semantic similarity mock
    return 0.8 if original_prompt in response else 0.5