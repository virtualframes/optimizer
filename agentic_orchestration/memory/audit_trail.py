import time


class AuditTrail:
    def __init__(self):
        self.trail = []

    def record(self, event, data):
        """
        Records an audit event.
        Placeholder for now. Appends to a list.
        """
        entry = {"timestamp": time.time(), "event": event, "data": data}
        self.trail.append(entry)
        print(f"AUDIT TRAIL: {entry}")
        # In a real implementation, this would write to a secure, append-only log.
