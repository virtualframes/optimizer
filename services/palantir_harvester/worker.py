import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from .workflows.palantir_feature_harvester_workflow import (
    PalantirFeatureHarvesterWorkflow,
)
from .activities.palantir_ingestion import ingest_palantir_features


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="palantir-harvester-task-queue",
        workflows=[PalantirFeatureHarvesterWorkflow],
        activities=[ingest_palantir_features],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
