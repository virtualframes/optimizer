class FallbackRouter:
    def route(self, task):
        """
        Routes a failed task to a fallback mechanism.
        Placeholder for now. Returns a fixed error message.
        """
        print(f"Routing failed task: {task.get('goal')}")
        return {"error": "Task failed and fallback was triggered."}
