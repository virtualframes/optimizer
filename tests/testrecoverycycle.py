# FLAWMODE: Test Recovery Cycle
# This test suite verifies the end-to-end functionality of the SelfHealingLoop.
# It ensures the agent can process a flaw, generate a patch, and approve it.

import unittest
from unittest.mock import MagicMock, patch
import sys

# Add the root directory to the path to allow importing the scripts
sys.path.append('.')

from scripts.selfhealingloop import SelfHealingLoop

class TestRecoveryCycle(unittest.TestCase):
    """
    Tests the full "trace, patch, benchmark, anchor" cycle.
    """

    def setUp(self):
        """Set up a mock flaw trace for use in all tests."""
        self.mock_trace = {
            "status": "triggered",
            "flaw_module": "optimizer.flaws.testflaw",
            "flaw_function": "some_broken_function",
            "result": "A simulated error occurred."
        }
        print("\nTEST: Setting up for TestRecoveryCycle...")

    def test_loop_initialization(self):
        """Ensures the SelfHealingLoop initializes correctly with a trace."""
        print("TEST: Running test_loop_initialization...")
        loop = SelfHealingLoop(self.mock_trace)
        self.assertEqual(loop.trace, self.mock_trace)
        self.assertIsNone(loop.patch)
        self.assertIsNone(loop.benchmark)
        print("PASS: test_loop_initialization")

    def test_successful_recovery_cycle(self):
        """
        Tests a complete, successful run of the healing loop.
        """
        print("TEST: Running test_successful_recovery_cycle...")
        loop = SelfHealingLoop(self.mock_trace)

        # Mock the internal methods to simulate a successful run
        loop.trace_failure = MagicMock(return_value={"diagnosis": "Found it!"})
        loop.generate_patch = MagicMock(return_value={"file_to_patch": "test.py"})
        loop.score_patch = MagicMock(return_value={"patch_approved": True})
        loop.anchor_memory = MagicMock(return_value=True)

        final_patch = loop.run()

        loop.trace_failure.assert_called_once()
        loop.generate_patch.assert_called_once()
        loop.score_patch.assert_called_once()
        loop.anchor_memory.assert_called_once()

        self.assertIsNotNone(final_patch, "Should return the final patch on success.")
        self.assertEqual(final_patch, {"file_to_patch": "test.py"})
        print("PASS: test_successful_recovery_cycle")

    def test_failed_benchmark_stops_cycle(self):
        """
        Ensures the cycle halts if the benchmark fails (patch is not approved).
        """
        print("TEST: Running test_failed_benchmark_stops_cycle...")
        loop = SelfHealingLoop(self.mock_trace)

        # Mock methods to simulate a failed benchmark
        loop.trace_failure = MagicMock(return_value={"diagnosis": "Found it!"})
        loop.generate_patch = MagicMock(return_value={"file_to_patch": "test.py"})
        loop.score_patch = MagicMock(return_value={"patch_approved": False}) # The key part
        loop.anchor_memory = MagicMock()

        final_patch = loop.run()

        loop.score_patch.assert_called_once()
        loop.anchor_memory.assert_not_called() # Should not anchor a failed patch

        self.assertIsNone(final_patch, "Should return None if patch is not approved.")
        print("PASS: test_failed_benchmark_stops_cycle")

if __name__ == "__main__":
    unittest.main()