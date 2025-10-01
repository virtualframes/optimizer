import unittest
from unittest.mock import MagicMock

# Since the modules are in the parent directory, we might need to adjust the Python path.
# For now, let's assume pytest handles it. If not, we'll fix it.
from optimizer_sentinel.agents.predictive_debug_engine import PredictiveDebugEngine
from optimizer_sentinel.adapters.risk_model import RiskModel
from optimizer_sentinel.agents.patch_engine import PatchEngine
from optimizer_sentinel.storage.neo4j_anchor import Neo4jAnchor

class TestPredictiveDebugEngine(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures, if any."""
        self.mock_risk_model = MagicMock(spec=RiskModel)
        self.mock_patch_engine = MagicMock(spec=PatchEngine)
        self.mock_neo4j_anchor = MagicMock(spec=Neo4jAnchor)

        self.engine = PredictiveDebugEngine(
            risk_model=self.mock_risk_model,
            patch_engine=self.mock_patch_engine,
            neo4j_anchor=self.mock_neo4j_anchor
        )

    def test_predict_failure_high_risk(self):
        """Test the predict_failure method with a high risk score."""
        directive = "test_directive"
        expected_patch = "mock_patch"

        self.mock_risk_model.score.return_value = 0.9
        self.mock_patch_engine.suggest.return_value = expected_patch

        patch = self.engine.predict_failure(directive)

        self.assertEqual(patch, expected_patch)
        self.mock_risk_model.score.assert_called_once()
        self.mock_patch_engine.suggest.assert_called_once()
        self.mock_neo4j_anchor.log_prediction.assert_called_once_with(directive, expected_patch)

    def test_predict_failure_low_risk(self):
        """Test the predict_failure method with a low risk score."""
        directive = "test_directive_low_risk"
        self.mock_risk_model.score.return_value = 0.5

        patch = self.engine.predict_failure(directive)

        self.assertIsNone(patch)
        self.mock_risk_model.score.assert_called_once()
        self.mock_patch_engine.suggest.assert_not_called()
        self.mock_neo4j_anchor.log_prediction.assert_not_called()

if __name__ == '__main__':
    unittest.main()