import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from .workflows.self_healing_workflow import SelfHealingWorkflow
from .activities.bug_bounty_ingestion import ingest_bug_bounty_data


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="self-healing-task-queue",
        workflows=[SelfHealingWorkflow],
        activities=[ingest_bug_bounty_data],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())