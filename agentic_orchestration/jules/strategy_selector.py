class StrategySelector:
    def select(self, task):
        """
        Selects a strategy based on the task.
        Placeholder for now. Returns a fixed strategy.
        """
        print(f"Selecting strategy for task: {task.get('goal')}")
        return "openai"  # Default to openai for now
