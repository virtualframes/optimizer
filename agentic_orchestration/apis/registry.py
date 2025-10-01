# These imports will fail until the other API files are created.
from .openai import OpenAIModel
from .claude import ClaudeModel
from .gemini import GeminiModel


class APIRegistry:
    def __init__(self):
        # In a real implementation, these would be initialized with credentials.
        self.models = {
            "openai": OpenAIModel(),
            "claude": ClaudeModel(),
            "gemini": GeminiModel(),
        }

    def get_model(self, name):
        """
        Retrieves a model by name from the registry.
        """
        model = self.models.get(name)
        if not model:
            raise ValueError(f"Model '{name}' not found in registry.")
        return model
