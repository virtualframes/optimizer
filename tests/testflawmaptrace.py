# FLAWMODE: Test Flaw Map Trace
# This test suite verifies that the FlawRunner correctly selects,
# executes, and traces a flaw injection event.

import unittest
from unittest.mock import patch
import sys

# Add the root directory to the path to allow importing the scripts
sys.path.append('.')

from scripts.julesflawmaprunner import FlawRunner

class TestFlawMapTrace(unittest.TestCase):
    """
    Tests the functionality of the FlawRunner.
    """

    def test_flaw_selection(self):
        """
        Ensures the FlawRunner can select a flaw function without crashing.
        """
        print("\nTEST: Running test_flaw_selection...")
        runner = FlawRunner(seed=123)  # Use a seed for deterministic behavior
        module, flaw_func = runner.select_flaw()
        self.assertIsNotNone(module, "Should select a flaw module.")
        self.assertTrue(callable(flaw_func), "Should select a callable flaw function.")
        print("PASS: test_flaw_selection")

    def test_flaw_run_and_trace(self):
        """
        Ensures the FlawRunner can execute a flaw and return a valid trace dictionary.
        """
        print("\nTEST: Running test_flaw_run_and_trace...")
        runner = FlawRunner(seed=456)
        trace = runner.run()
        self.assertIsInstance(trace, dict, "Trace should be a dictionary.")
        self.assertIn("status", trace, "Trace should have a status.")
        self.assertEqual(trace["status"], "triggered", "Status should be 'triggered'.")
        self.assertIn("flaw_module", trace, "Trace should contain the flaw module.")
        self.assertIn("flaw_function", trace, "Trace should contain the flaw function.")
        print("PASS: test_flaw_run_and_trace")

    @patch('scripts.julesflawmaprunner.FlawRunner.select_flaw')
    def test_error_handling(self, mock_select_flaw):
        """
        Tests that the runner correctly handles an exception during flaw execution.
        """
        print("\nTEST: Running test_error_handling...")
        # Mock the choice to return a function that will raise an exception
        def faulty_flaw(input):
            raise ValueError("Intentional test error")

        # To mock a module and function, we need a bit more setup
        class MockModule:
            __name__ = "mock_module"

        # Make select_flaw return the module and the faulty function
        mock_select_flaw.return_value = (MockModule, faulty_flaw)

        runner = FlawRunner()
        trace = runner.run()

        self.assertEqual(trace["status"], "error", "Status should be 'error'.")
        self.assertIn("error", trace, "Trace should contain the error message.")
        self.assertEqual(trace["error"], "Intentional test error", "Error message should match.")
        print("PASS: test_error_handling")

if __name__ == "__main__":
    unittest.main()