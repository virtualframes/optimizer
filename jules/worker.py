import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Import the workflow from the orchestration layer
from services.synapse_cortex.workflows.orchestration_workflow import OrchestrationWorkflow

# Import activities that the workflow will use
from services.synapse_cortex.activities.diagnostics_activity import diagnose_issue

async def main():
    """
    Main function to start the Temporal worker.
    """
    client = await Client.connect("localhost:7233")

    # Create a worker that connects to the "syzygy-synapse" task queue
    worker = Worker(
        client,
        task_queue="syzygy-synapse-task-queue",
        workflows=[OrchestrationWorkflow],
        activities=[diagnose_issue],
    )
    print("Starting Jules worker...")
    await worker.run()
    print("Jules worker stopped.")

if __name__ == "__main__":
    asyncio.run(main())