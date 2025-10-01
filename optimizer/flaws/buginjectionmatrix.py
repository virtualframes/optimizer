# FLAWMODE: Bug Injection Matrix
# This module defines the programmable flaws that Jules can inject into the system.
# Each function represents a specific type of failure, designed to be traced and healed.

import random

class BugInjectionMatrix:
    """
    A matrix of controlled bug injections.
    Each method introduces a specific, traceable flaw.
    """

    def __init__(self, seed=None):
        self.random = random.Random(seed)

    def cause_null_pointer_exception(self, target_object):
        """Injects a flaw that leads to a NoneType error."""
        target_object.attribute = None
        # The next access to target_object.attribute will likely fail.
        return None

    def introduce_infinite_loop(self, condition):
        """A placeholder for a flaw that causes an infinite loop."""
        # This is a dangerous operation, implemented as a placeholder.
        # In a real scenario, this would be a more subtle logic flaw.
        print("FLAW INJECTED: Infinite Loop (Simulated)")
        # while True:
        #     pass
        return False

    def corrupt_data(self, data_structure):
        """Injects a flaw by corrupting a data structure."""
        if isinstance(data_structure, list) and data_structure:
            index_to_corrupt = self.random.randint(0, len(data_structure) - 1)
            data_structure[index_to_corrupt] = "CORRUPTED_BY_JULES"
        elif isinstance(data_structure, dict) and data_structure:
            key_to_corrupt = self.random.choice(list(data_structure.keys()))
            data_structure[key_to_corrupt] = "CORRUPTED_BY_JULES"
        return data_structure

    def simulate_semantic_drift(self, text):
        """Injects a flaw by altering the meaning of a text string."""
        replacements = {"success": "failure", "complete": "incomplete", "stable": "unstable"}
        for old, new in replacements.items():
            if old in text:
                return text.replace(old, new)
        return "semantically_drifted_by_jules"