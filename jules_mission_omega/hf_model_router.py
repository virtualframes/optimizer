class LocalModel:
    def __init__(self, name, provider, confidence):
        self.name = name
        self.provider = provider
        self.confidence = confidence
        print(f"INFO: LocalModel '{self.name}' initialized.")

    def generate(self, prompt: str) -> str:
        """Generates a deterministic response from the local model."""
        print(f"INFO: Generating response with local model '{self.name}'...")
        return f"[{self.name}] deterministic response to: {prompt}"

def load_local_model(name: str) -> LocalModel:
    """Loads and returns a local model instance."""
    print(f"INFO: Loading local model '{name}'...")
    return LocalModel(name=name, provider="huggingface_local", confidence=0.85)