import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from .workflows.xbow_validation_workflow import XbowValidationWorkflow
from .activities.penetration_testing import simulate_penetration_test


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="xbow-validator-task-queue",
        workflows=[XbowValidationWorkflow],
        activities=[simulate_penetration_test],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
