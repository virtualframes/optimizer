import time


class TracebackLogger:
    def log(self, error, context):
        """
        Logs an error and its context.
        Placeholder for now. Prints to the console.
        """
        log_entry = {"timestamp": time.time(), "error": str(error), "context": context}
        print(f"TRACEBACK LOG: {log_entry}")
        # In a real implementation, this would write to a file or a logging service.
