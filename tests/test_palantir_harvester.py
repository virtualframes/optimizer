import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from services.palantir_harvester.workflows.palantir_feature_harvester_workflow import (
    PalantirFeatureHarvesterWorkflow,
)
from services.palantir_harvester.activities.palantir_ingestion import (
    ingest_palantir_features,
)


@pytest.mark.asyncio
async def test_palantir_harvester_workflow():
    task_queue = "test-palantir-harvester-workflow"
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[PalantirFeatureHarvesterWorkflow],
            activities=[ingest_palantir_features],
        ):
            result = await env.client.execute_workflow(
                PalantirFeatureHarvesterWorkflow.run,
                id="test-palantir-harvester-workflow",
                task_queue=task_queue,
            )
            assert result == "Successfully ingested Palantir features."
