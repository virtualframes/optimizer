# FLAWMODE: Jules Flaw Map Runner
# This script is the orchestrator for the FLAWMODE protocol.
# It selects a flaw from the bug injection matrix and executes it
# to trigger a failure that the Jules agent must then heal.

import importlib
import random
import sys

# Add the optimizer directory to the path to allow importing the flaws
sys.path.append('.')

from optimizer.flaws import buginjectionmatrix
# from optimizer.flaws import broken_imports # This is intentionally broken and should not be imported directly
from optimizer.flaws import infiniteloopsimulator
from optimizer.flaws import semanticdriftgenerator
from optimizer.flaws import memory_poisoner


class FlawRunner:
    """
    Selects and runs a flaw to test the self-healing capabilities of the agent.
    """

    def __init__(self, seed=None):
        self.seed = seed
        self.random = random.Random(seed)
        self.flaw_modules = [
            buginjectionmatrix,
            # broken_imports, # This would crash the runner itself
            infiniteloopsimulator,
            semanticdriftgenerator,
            memory_poisoner,
        ]

    def select_flaw(self):
        """Randomly selects a flaw module and a function from it."""
        chosen_module = self.random.choice(self.flaw_modules)
        flaw_functions = [
            (name, obj)
            for name, obj in vars(chosen_module).items()
            if callable(obj) and not name.startswith("__")
        ]
        if not flaw_functions:
            return None, None
        chosen_function_name, chosen_function = self.random.choice(flaw_functions)
        return chosen_module, chosen_function

    def run(self):
        """Selects and executes a flaw, returning a trace of the event."""
        module, flaw_func = self.select_flaw()
        if not module or not flaw_func:
            return {"status": "error", "message": "No flaw functions found."}

        print(f"FLAW RUNNER: Executing flaw '{flaw_func.__name__}' from module '{module.__name__}'")

        try:
            # This is a simulation. In a real scenario, the flaw would be
            # injected into a running application instance.
            # For now, we just call the function to log its simulated effect.
            result = flaw_func("dummy_input_for_testing")
            return {
                "status": "triggered",
                "flaw_module": module.__name__,
                "flaw_function": flaw_func.__name__,
                "result": str(result),
            }
        except Exception as e:
            return {
                "status": "error",
                "flaw_module": module.__name__,
                "flaw_function": flaw_func.__name__,
                "error": str(e),
            }


if __name__ == "__main__":
    runner = FlawRunner()
    trace = runner.run()
    print("--- FLAW TRACE ---")
    import json
    print(json.dumps(trace, indent=2))
    print("--------------------")
    # In a real run, this trace would be passed to the self-healing loop.