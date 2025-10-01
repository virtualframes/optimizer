import unittest
from optimizer_sentinel.workflows.schemamigrationguard import SchemaMigrationGuard

class TestSchemaMigrationGuard(unittest.TestCase):

    def setUp(self):
        self.guard = SchemaMigrationGuard()

    def test_validate_no_conflict(self):
        """
        Test that a low-risk migration passes validation.
        """
        target = {"name": "add_index_to_users", "migration_risk": "low"}
        self.assertTrue(self.guard.validate(target))

    def test_validate_with_conflict(self):
        """
        Test that a high-risk migration fails validation.
        """
        target = {"name": "drop_column_products", "migration_risk": "high"}
        self.assertFalse(self.guard.validate(target))

    def test_validate_no_risk_specified(self):
        """
        Test that a migration with no specified risk passes validation.
        """
        target = {"name": "add_table_audit_log"}
        self.assertTrue(self.guard.validate(target))

if __name__ == '__main__':
    unittest.main()