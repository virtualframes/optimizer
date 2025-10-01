from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from ..activities.penetration_testing import simulate_penetration_test


@workflow.defn
class XbowValidationWorkflow:
    @workflow.run
    async def run(self, patch_id: str):
        return await workflow.execute_activity(
            simulate_penetration_test,
            patch_id,
            start_to_close_timeout=timedelta(hours=1),
        )
