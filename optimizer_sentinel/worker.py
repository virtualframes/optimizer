import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Import the workflow and the activities module
from .workflows.debugandpatch import DebugAndPatchWorkflow
from .agents import jules as jules_activities

async def main():
    # Connect to the Temporal server.
    client = await Client.connect("localhost:7233")

    # Create a worker that polls for tasks on the "jules-patch-queue"
    # and executes the workflow and its activities.
    worker = Worker(
        client,
        task_queue="jules-patch-queue",
        workflows=[DebugAndPatchWorkflow],
        activities=[
            jules_activities.diagnose,
            jules_activities.generate_patch,
            jules_activities.commit_and_create_pr,
            jules_activities.anchor_event_activity,
        ],
    )
    print("Starting Temporal worker with refactored activities...")
    await worker.run()
    print("Temporal worker stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWorker shutting down.")