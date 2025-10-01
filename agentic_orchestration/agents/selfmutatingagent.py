class SelfMutatingAgent:
    def __init__(self, source_path):
        self.source_path = source_path

    def mutate(self, cycle):
        with open(self.source_path) as f:
            code = f.read()
        injection = f"\n# Cycle {cycle}: Self-evolving directive\n"
        mutated = code + injection
        with open(self.source_path, "w") as f:
            f.write(mutated)
        return mutated
# Cycle 1: Self-evolving directive

# Cycle 2: Self-evolving directive

# Cycle 3: Self-evolving directive

# Cycle 4: Self-evolving directive

# Cycle 5: Self-evolving directive
