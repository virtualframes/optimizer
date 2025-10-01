import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from services.xbow_validator.workflows.xbow_validation_workflow import XbowValidationWorkflow
from services.xbow_validator.activities.penetration_testing import simulate_penetration_test


@pytest.mark.asyncio
async def test_xbow_validation_workflow():
    task_queue = "test-xbow-validation-workflow"
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[XbowValidationWorkflow],
            activities=[simulate_penetration_test],
        ):
            result = await env.client.execute_workflow(
                XbowValidationWorkflow.run,
                "test-patch-id",
                id="test-xbow-validation-workflow",
                task_queue=task_queue,
            )
            assert result == "Successfully simulated penetration test for patch test-patch-id."