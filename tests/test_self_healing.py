import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from services.self_healing.workflows.self_healing_workflow import SelfHealingWorkflow
from services.self_healing.activities.bug_bounty_ingestion import ingest_bug_bounty_data


@pytest.mark.asyncio
async def test_self_healing_workflow():
    task_queue = "test-self-healing-workflow"
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[SelfHealingWorkflow],
            activities=[ingest_bug_bounty_data],
        ):
            result = await env.client.execute_workflow(
                SelfHealingWorkflow.run,
                id="test-self-healing-workflow",
                task_queue=task_queue,
            )
            assert result == "Successfully ingested bug bounty data."