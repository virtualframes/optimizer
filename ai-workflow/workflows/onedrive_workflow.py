from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports():
    from activities.onedrive_sync import sync_onenote

@workflow.defn
class OneDriveSyncWorkflow:
    @workflow.run
    async def run(self):
        """Orchestrates the OneNote data synchronization."""
        workflow.logger.info("Starting OneDrive/OneNote sync workflow.")

        # It's best practice to define a retry policy for activities
        # that make network calls.
        retry_policy = RetryPolicy(
            maximum_attempts=5,
            # Add specific non-retryable error types if needed
            # non_retryable_error_types=["YourApplicationError"],
        )

        result = await workflow.execute_activity(
            sync_onenote,
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=retry_policy,
        )

        workflow.logger.info("OneDrive/OneNote sync workflow completed successfully.")
        return result

"""
-- How to run this workflow --

This workflow needs a Temporal Worker to execute it and a client to start it.

1. Worker (worker.py):

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows.onedrive_workflow import OneDriveSyncWorkflow
from activities.onedrive_sync import sync_onenote

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="onedrive-sync-queue",
        workflows=[OneDriveSyncWorkflow],
        activities=[sync_onenote],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())


2. Client to start the workflow (run_workflow.py):

import asyncio
from temporalio.client import Client
from workflows.onedrive_workflow import OneDriveSyncWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        OneDriveSyncWorkflow.run,
        id="onedrive-sync-workflow",
        task_queue="onedrive-sync-queue",
    )
    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
"""