import unittest
from unittest.mock import patch, MagicMock, call
from flaw_first_optimizer.jules_agent import JulesAgent
from flaw_first_optimizer.julesselfevolver import JulesSelfEvolver, anchor_event

class TestJulesSelfEvolver(unittest.TestCase):

    def setUp(self):
        """Set up a mock agent for each test."""
        self.mock_agent = JulesAgent()

    @patch('flaw_first_optimizer.julesselfevolver.anchor_event')
    @patch('flaw_first_optimizer.julesselfevolver.benchmark_alignment')
    def test_evolve_loop_success_after_mutations(self, mock_benchmark, mock_anchor):
        """
        Test that the evolve loop mutates, reroutes, and eventually succeeds.
        """
        # Mock the agent's responses
        self.mock_agent.route = MagicMock(side_effect=[
            "Unaligned response 1", "Unaligned response 2", "aligned final response"
        ])
        # Configure the mock benchmark to fail twice, then succeed
        mock_benchmark.side_effect = [0.6, 0.7, 0.8]

        evolver = JulesSelfEvolver(agent=self.mock_agent, benchmark_threshold=0.75, max_depth=5)
        final_response = evolver.evolve("initial prompt")

        self.assertEqual(final_response, "aligned final response")
        self.assertEqual(mock_benchmark.call_count, 3)
        self.assertEqual(len(evolver.history), 2)
        mock_anchor.assert_called_once()
        args, _ = mock_anchor.call_args
        self.assertEqual(args[0], "SelfLearnSuccess")
        self.assertEqual(args[1]['score'], 0.8)

    @patch('flaw_first_optimizer.julesselfevolver.anchor_event')
    @patch('flaw_first_optimizer.julesselfevolver.benchmark_alignment')
    def test_evolve_fails_at_max_depth(self, mock_benchmark, mock_anchor):
        """
        Test that the evolution process stops and fails when max_depth is reached.
        """
        # Mock agent to always return the same unaligned response
        self.mock_agent.route = MagicMock(return_value="Unaligned response")
        # Mock benchmark to always fail
        mock_benchmark.return_value = 0.5

        # Set max_depth to 3 for this test
        evolver = JulesSelfEvolver(agent=self.mock_agent, benchmark_threshold=0.75, max_depth=3)
        final_response = evolver.evolve("initial prompt")

        # 1. Verify the final response indicates failure
        self.assertEqual(final_response, "Evolution failed: Max depth reached")

        # 2. Check that the agent's route method was called 3 times (the max_depth)
        self.assertEqual(self.mock_agent.route.call_count, 3)

        # 3. Ensure the history has 3 entries, one for each failed attempt
        self.assertEqual(len(evolver.history), 3)

        # 4. Check that the failure event was anchored once
        mock_anchor.assert_called_once()
        args, _ = mock_anchor.call_args
        self.assertEqual(args[0], "SelfLearnFailure")
        self.assertEqual(args[1]['reason'], "Max evolution depth reached")

if __name__ == '__main__':
    unittest.main()